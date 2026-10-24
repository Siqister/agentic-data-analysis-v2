"""Run a requested Indicator or Visualization (architecture.md § 2, Invocation).

Walks down the graph from the requested spec, checks staleness, fetches missing
snapshots, computes through reviewed code, runs known-answer tests, and writes
outputs with manifests.

    uv run python -m lib.runner list
    uv run python -m lib.runner status
    uv run python -m lib.runner run <spec id> [--mode author|run]
"""

import argparse
import importlib.util
import sys

import yaml

from lib import ROOT, census, crosswalk, geography, known_answers, output
from lib import validate
from lib.choropleth import draw
from lib.compiled import code_hash, code_path, code_status, read_header
from lib.snapshot import Snapshot, census_api
from lib.specs import Spec, dependencies, load_all


class Stop(Exception):
    """The run can't go on; the message says why and what to do."""


class Context:
    """What compiled Indicator code may use. Every data read goes through a snapshot."""

    def __init__(self, spec: Spec, specs: dict[str, Spec]):
        self.spec = spec
        self.specs = specs
        self.snaps: list[Snapshot] = []
        self._geo: dict = {}

    def acs(self, entry: dict, for_: str, in_: list[str]):
        """Census API fields named in one `data` entry (with _M fields), as a table keyed by GEOID."""
        resource = self.specs[entry["resource"]].meta
        approved = {(d["dataset"], d["vintage"]) for d in resource.get("datasets", [])}
        if (entry["dataset"], entry["vintage"]) not in approved:
            raise Stop(f"{entry['dataset']} {entry['vintage']} is not on {entry['resource']}'s approved list")
        fields = census.with_moe(list(entry["fields"]))
        snap = census_api(resource, entry["dataset"], entry["vintage"], fields, for_, in_)
        self.snaps.append(snap)
        return census.read(snap, fields)

    def geography(self, geo_id: str):
        if geo_id not in self._geo:
            self._geo[geo_id] = geography.load(self.specs[geo_id], self.specs, self.snaps)
        return self._geo[geo_id]

    def crosswalk(self, cw_id: str):
        cw = self.specs[cw_id]
        return crosswalk.build(cw, self.geography(cw.meta["from"]), self.geography(cw.meta["to"]), self.specs)


def available(specs: dict[str, Spec]) -> str:
    lines = []
    for t in ("Indicator", "Visualization"):
        lines.append(f"{t}s:")
        for s in specs.values():
            if s.type == t:
                lines.append(f"  {s.id} — {s.meta.get('title')} ({s.meta.get('status')})")
    return "\n".join(lines)


def built_from(spec: Spec, specs: dict[str, Spec]) -> list[dict]:
    """The spec and everything below it, top first, with the hashes that decide staleness."""
    out = []
    for s in [spec, *reversed(dependencies(spec, specs))]:
        entry = {"id": s.id, "type": s.type, "status": s.meta.get("status")}
        path = code_path(s)
        if path:
            header = read_header(path) if path.exists() else None
            entry["spec_hash"] = s.hash
            entry["code"] = str(path.relative_to(ROOT))
            entry["code_hash"] = code_hash(path) if path.exists() else None
            entry["verified"] = header.verified if header else None
        else:
            entry["spec_hash"] = s.meta_hash   # frontmatter only: body edits don't rerun
        for k in ("method", "within", "within_rule"):
            if k in s.meta:
                entry[k] = s.meta[k]
        out.append(entry)
    return out


def check_ready(spec: Spec, specs: dict[str, Spec], mode: str):
    problems = []
    for s in [spec, *dependencies(spec, specs)]:
        status = code_status(s)
        if status in ("missing", "stale"):
            problems.append(f"{s.id}: compiled code is {status}" + (" (recompile and review in author mode)" if mode == "run" else ""))
        if mode == "run":
            if s.meta.get("status") != "stable":
                problems.append(f"{s.id}: spec is {s.meta.get('status')}, not stable")
            if status == "unverified":
                problems.append(f"{s.id}: compiled code has not been reviewed")
    if problems:
        raise Stop("can't run:\n  " + "\n  ".join(problems) + ("\nRefer to an expert." if mode == "run" else ""))


def reported_at(ind: Spec, specs: dict[str, Spec]) -> list[str]:
    return [ind.meta["geography"]] + [specs[c].meta["to"] for c in ind.meta.get("crosswalks") or []]


def run_indicator(ind: Spec, specs: dict[str, Spec], force: bool = False) -> None:
    bf = built_from(ind, specs)
    outputs = {g: output.TABLES / f"{ind.id}__{g}.csv" for g in reported_at(ind, specs)}
    reasons = {g: output.stale_reason(p, bf) for g, p in outputs.items()}
    if not force and not any(reasons.values()):
        print(f"{ind.id}: up to date")
        return
    print(f"{ind.id}: computing ({'; '.join(sorted({r for r in reasons.values() if r})) or 'forced'})")

    ctx = Context(ind, specs)
    module = _import(code_path(ind))
    tables = module.compute(ctx)
    if set(tables) != set(outputs):
        raise Stop(f"{ind.id}: code returned {sorted(tables)}, expected {sorted(outputs)}")

    results = {}
    for test_id, test in known_answers.load().items():
        if test["indicator"] == ind.id:
            r = known_answers.evaluate(test, tables[test["geography"]])
            results[test_id] = r
            print(f"  {test_id}: {r['status']}  expected {r.get('expected')}  actual {r.get('actual')}  "
                  f"difference {r.get('difference')} ({_pct(r.get('relative_difference'))})  tolerance {r.get('tolerance')}")
    if any(r["status"] != "pass" for r in results.values()):
        raise Stop(f"{ind.id}: a known-answer test failed; outputs not delivered. The expert decides: fix, or accept the difference.")

    data = _dedupe([s.record() for s in ctx.snaps])
    tests = {k: v["status"] for k, v in results.items()}
    for g, path in outputs.items():
        output.write_table(tables[g], path, bf, data, tests)
        print(f"  wrote {path.relative_to(ROOT)}")


def run_visualization(viz: Spec, specs: dict[str, Spec], force: bool = False) -> None:
    ind = specs[viz.meta["indicator"]]
    geo_id = viz.meta["geography"]
    run_indicator(ind, specs, force)
    table_path = output.TABLES / f"{ind.id}__{geo_id}.csv"
    ind_manifest = yaml.safe_load(output.manifest_path(table_path).read_text())

    bf = built_from(viz, specs)
    out = output.MAPS / f"{viz.id}.html"
    reason = output.stale_reason(out, bf)
    if not force and not reason and _fresh_against(out, ind_manifest):
        print(f"{viz.id}: up to date")
        return
    print(f"{viz.id}: drawing ({reason or 'indicator results changed'})")
    snaps: list[Snapshot] = []
    geo = geography.load(specs[geo_id], specs, snaps)
    data = _dedupe(ind_manifest["data"] + [s.record() for s in snaps])
    breaks = draw(viz.meta, ind.meta["measure"], ind.meta.get("unit", "count"), output.read_table(table_path), geo,
                  source_note(ind, specs, data), out)
    m = output.write_manifest(out, bf, data, ind_manifest["known_answer_tests"])
    m["indicator_output"] = {"path": ind_manifest["output"], "fingerprint": ind_manifest["fingerprint"]}
    m["classes"] = {"classification": viz.meta["classification"], "breaks": breaks}
    output.manifest_path(out).write_text(yaml.safe_dump(m, sort_keys=False, allow_unicode=True))
    print(f"  wrote {out.relative_to(ROOT)}")


def source_note(ind: Spec, specs: dict[str, Spec], data: list[dict]) -> str:
    parts = []
    for entry in ind.meta.get("data") or []:
        res = specs[entry["resource"]].meta
        fields = ", ".join(entry["fields"])
        parts.append(f"{res['title']}, {entry['dataset']} {entry['vintage']}: {fields}")
    geos = [specs[d["source"]].meta["title"] for d in data
            if d["source"] in specs and specs[d["source"]].type == "Geography"]
    if geos:
        parts.append("Boundaries: " + "; ".join(dict.fromkeys(geos)))
    return "Source: " + " · ".join(parts) + ". Margins of error at 90% confidence."


def _fresh_against(out, ind_manifest) -> bool:
    mp = output.manifest_path(out)
    if not mp.exists():
        return False
    m = yaml.safe_load(mp.read_text())
    return (m.get("indicator_output") or {}).get("fingerprint") == ind_manifest["fingerprint"]


def _dedupe(records: list[dict]) -> list[dict]:
    return list({r["path"]: r for r in records}.values())


def _pct(x):
    return "—" if x is None else f"{x:+.2%}"


def _import(path):
    spec = importlib.util.spec_from_file_location(path.stem, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def status(specs: dict[str, Spec]) -> None:
    for s in specs.values():
        line = f"{s.id} ({s.type}, {s.meta.get('status')})"
        cs = code_status(s)
        if cs != "none":
            line += f" · code: {cs}"
        if s.type == "Indicator":
            bf = built_from(s, specs)
            for g in reported_at(s, specs):
                r = output.stale_reason(output.TABLES / f"{s.id}__{g}.csv", bf)
                line += f" · {g}: {r or 'up to date'}"
        if s.type == "Visualization":
            r = output.stale_reason(output.MAPS / f"{s.id}.html", built_from(s, specs))
            line += f" · map: {r or 'up to date'}"
        print(line)


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("list")
    sub.add_parser("status")
    r = sub.add_parser("run")
    r.add_argument("spec_id")
    r.add_argument("--mode", choices=["author", "run"], default="run")
    r.add_argument("--force", action="store_true", help="recompute even if up to date (author mode)")
    args = p.parse_args(argv)

    specs = load_all()
    if args.cmd == "list":
        print(available(specs))
        return 0
    if args.cmd == "status":
        status(specs)
        return 0

    report = validate.run(specs, network=False)
    if report.errors:
        print(report.text())
        print("\nSpec validation has errors; nothing was run.")
        return 1
    spec = specs.get(args.spec_id)
    if spec is None or spec.type not in ("Indicator", "Visualization"):
        print(f'"{args.spec_id}" is not available.\n\n{available(specs)}')
        return 1
    try:
        check_ready(spec, specs, args.mode)
        if args.force and args.mode != "author":
            raise Stop("--force is for author mode only")
        if spec.type == "Indicator":
            run_indicator(spec, specs, args.force)
        else:
            run_visualization(spec, specs, args.force)
    except Stop as e:
        print(f"Stopped: {e}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
