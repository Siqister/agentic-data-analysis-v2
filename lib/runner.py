"""Run a requested Indicator or Visualization (architecture.md § 2, Invocation).

Walks down the graph from the requested spec, checks staleness, fetches missing
snapshots, computes through reviewed code, runs known-answer tests, and writes
outputs with manifests.

    uv run python -m lib.runner list
    uv run python -m lib.runner status
    uv run python -m lib.runner run <spec id> [--mode author|run]
"""

import argparse
import dataclasses
import importlib.util
import re
import sys

import yaml

import geopandas as gpd
import pandas as pd

from lib import ROOT, census, crosswalk, geography, heatmap, known_answers, moe, output, points
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

    def acs(self, entry: dict) -> pd.DataFrame:
        """Census API fields named in one `data` entry (with _M fields), for every unit of the
        Indicator's geography: geography_id, geography_name, the fields, and `annotation`.

        The request extent comes from the units' GEOIDs (architecture.md § 4.2). A unit with
        no row, or a field not published for any unit, stops the run (§ 12)."""
        resource = self.specs[entry["resource"]].meta
        approved = {(d["dataset"], d["vintage"]) for d in resource.get("datasets", [])}
        if (entry["dataset"], entry["vintage"]) not in approved:
            raise Stop(f"{entry['dataset']} {entry['vintage']} is not on {entry['resource']}'s approved list")
        geo_spec = self.specs[self.spec.meta["geography"]]
        unit = geo_spec.meta.get("census_unit")
        if not unit:
            raise Stop(f"{geo_spec.id} has no census_unit, so Census data can't be requested for it")
        units = self.geography(geo_spec.id)[["geography_id", "geography_name"]]
        fields = census.with_moe(list(entry["fields"]))
        raw = []
        for for_, in_ in census.requests_for(units["geography_id"], unit):
            snap = census_api(resource, entry["dataset"], entry["vintage"], fields, for_, in_)
            self.snaps.append(snap)
            raw.append(census.read(snap, fields))
        t = units.merge(pd.concat(raw), left_on="geography_id", right_on="GEOID", how="left")
        missing = t.loc[t["GEOID"].isna(), "geography_id"]
        if len(missing):
            raise Stop(f"no {entry['dataset']} row for {geo_spec.id} units: {', '.join(missing[:10])}")
        for f in fields:
            if t["annotation"].str.contains(f"{f} not published", regex=False).all():
                raise Stop(f"{f} is not published at {unit} level")
        return t.drop(columns="GEOID").reset_index(drop=True)

    def features(self, entry: dict) -> pd.DataFrame:
        """Only the fields named in one `data` entry for a file Resource, read through a snapshot.
        Geometry, if named, is in EPSG:3734 (architecture.md § 4.4)."""
        res = self.specs[entry["resource"]]
        fields = list(entry["fields"])
        snap = geography.snapshot(res)
        self.snaps.append(dataclasses.replace(snap, request=f"{snap.request} · {', '.join(fields)}"))
        try:
            return points.read(snap.path, fields)
        except ValueError as e:
            raise Stop(f"{res.id}: {e}")

    def in_window(self, t: pd.DataFrame) -> pd.Series:
        """True for rows in the Indicator's `window`, in local dates (architecture.md § 12)."""
        try:
            return points.in_window(t, self.spec.meta["window"])
        except ValueError as e:
            raise Stop(f"{self.spec.id}: {e}")

    def inside(self, t: gpd.GeoDataFrame) -> pd.Series:
        """True for points inside the Indicator's geography or on its boundary."""
        return points.inside(t.geometry, self.geography(self.spec.meta["geography"]))

    def indicator(self, ind_id: str) -> pd.DataFrame:
        """A `builds_on` Indicator's table at this Indicator's geography, read from outputs/tables/
        (the runner has already run it)."""
        if ind_id not in (self.spec.meta.get("builds_on") or []):
            raise Stop(f"{self.spec.id}: {ind_id} is not in its builds_on")
        return output.read_table(indicator_outputs(self.specs[ind_id], self.specs)[self.spec.meta["geography"]])

    def stop(self, message: str):
        """Stop the run from compiled code, e.g. for a value the spec doesn't cover."""
        raise Stop(f"{self.spec.id}: {message}")

    def geography(self, geo_id: str):
        if geo_id not in self._geo:
            self._geo[geo_id] = geography.load(self.specs[geo_id], self.specs, self.snaps)
        return self._geo[geo_id]

    def crosswalk(self, cw_id: str):
        cw = self.specs[cw_id]
        return crosswalk.build(cw, self.geography(cw.meta["from"]), self.geography(cw.meta["to"]), self.specs, self.snaps)


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
        for k in ("method", "min_overlap", "within", "within_rule", "census_unit"):
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


def indicator_outputs(ind: Spec, specs: dict[str, Spec]) -> dict:
    """Output path at each geography: a table, or for a selection, a GeoPackage in build/points/."""
    if ind.meta["measure"] == "points":
        g = ind.meta["geography"]
        return {g: output.POINTS / f"{ind.id}__{g}.gpkg"}
    return {g: output.TABLES / f"{ind.id}__{g}.csv" for g in reported_at(ind, specs)}


def run_indicator(ind: Spec, specs: dict[str, Spec], force: bool = False) -> None:
    inputs = {}
    for dep in ind.meta.get("builds_on") or []:
        # Inputs run first, as dependencies; their tables are read, never recomputed here.
        run_indicator(specs[dep], specs)
        path = indicator_outputs(specs[dep], specs)[ind.meta["geography"]]
        inputs[dep] = yaml.safe_load(output.manifest_path(path).read_text())
    bf = built_from(ind, specs)
    outputs = indicator_outputs(ind, specs)
    reasons = {g: output.stale_reason(p, bf) or _inputs_changed(p, inputs) for g, p in outputs.items()}
    if not force and not any(reasons.values()):
        print(f"{ind.id}: up to date")
        return
    print(f"{ind.id}: computing ({'; '.join(sorted({r for r in reasons.values() if r})) or 'forced'})")

    ctx = Context(ind, specs)
    module = _import(code_path(ind))
    if ind.meta["measure"] == "points":
        selected, excluded = selection(ind, module.compute(ctx))
        path = outputs[ind.meta["geography"]]
        output.write_points(selected, path, bf, _dedupe([s.record() for s in ctx.snaps]), excluded)
        print(f"  {len(selected)} points; excluded: " + ", ".join(f"{k} {v}" for k, v in excluded.items()))
        print(f"  wrote {path.relative_to(ROOT)}")
        return
    tables = report(ind, specs, ctx, module.compute(ctx))

    results = {}
    for test_id, test in known_answers.load().items():
        if test["indicator"] == ind.id:
            r = known_answers.evaluate(test, tables[test["geography"]])
            results[test_id] = r
            print(f"  {test_id}: {r['status']}  expected {r.get('expected')}  actual {r.get('actual')}  "
                  f"difference {r.get('difference')} ({_pct(r.get('relative_difference'))})  tolerance {r.get('tolerance')}")
    if any(r["status"] != "pass" for r in results.values()):
        raise Stop(f"{ind.id}: a known-answer test failed; outputs not delivered. The expert decides: fix, or accept the difference.")

    data = _dedupe([d for m in inputs.values() for d in m["data"]] + [s.record() for s in ctx.snaps])
    tests = {k: v["status"] for k, v in results.items()}
    for g, path in outputs.items():
        m = output.write_table(tables[g], path, bf, data, tests)
        if inputs:
            m["indicator_inputs"] = [{"path": v["output"], "fingerprint": v["fingerprint"]} for v in inputs.values()]
        if ind.meta["measure"] == "percent_change":
            m["caveats"] = caveats(ind)
        if inputs or "caveats" in m:
            output.manifest_path(path).write_text(yaml.safe_dump(m, sort_keys=False, allow_unicode=True))
        print(f"  wrote {path.relative_to(ROOT)}")


def report(ind: Spec, specs: dict[str, Spec], ctx: Context, native: pd.DataFrame) -> dict[str, pd.DataFrame]:
    """From the compiled code's table at the Indicator's geography, the table at every geography
    it's reported at: crosswalks applied per `measure`, then reliability (architecture.md § 12)."""
    geo = ind.meta["geography"]
    cols = {"geography_id", "estimate", "moe", "note"}
    if not cols <= set(native.columns):
        raise Stop(f"{ind.id}: code must return columns {sorted(cols)}")
    if set(native["geography_id"]) != set(ctx.geography(geo)["geography_id"]):
        raise Stop(f"{ind.id}: code must return one row per {geo} unit")
    tables = {geo: native}
    label = specs[geo].meta.get("census_unit", "unit")
    for cw_id in ind.meta.get("crosswalks") or []:
        to = specs[cw_id].meta["to"]
        if specs[cw_id].meta["method"] == "matched":
            # Copies values unchanged, so any measure can use it (architecture.md § 4.3).
            moved = crosswalk.apply_matched(native, ctx.crosswalk(cw_id), ctx.geography(to)["geography_id"],
                                            label=_matched_label(specs[geo]))
        elif ind.meta["measure"] != "count":
            raise Stop(f"{ind.id}: moving a {ind.meta['measure']} through a crosswalk isn't built yet")
        else:
            moved = crosswalk.apply_count(native, ctx.crosswalk(cw_id), label=label)
        tables[to] = moved.merge(ctx.geography(to)[["geography_id", "geography_name"]], on="geography_id")
    rel = ind.meta.get("reliability")
    for g, t in tables.items():
        if "geography_name" not in t.columns:
            t = t.merge(ctx.geography(g)[["geography_id", "geography_name"]], on="geography_id")
        tables[g] = (moe.reliability(t, rel["cv_threshold"], rel["low"]) if rel
                     else t.assign(cv=float("nan"), reliability=""))
    return tables


def _matched_label(geo: Spec) -> str:
    """E.g. "2010 tract": the boundary year at the end of the Geography's ID (§ 12) and its census_unit."""
    year = re.search(r"_(\d{4})$", geo.id)
    if not year or not geo.meta.get("census_unit"):
        raise Stop(f"{geo.id}: a matched crosswalk's `from` needs a census_unit and a boundary year in its ID")
    return f"{year.group(1)} {geo.meta['census_unit']}"


def selection(ind: Spec, result) -> tuple[gpd.GeoDataFrame, dict]:
    """Check what a points Indicator's code returns: points in EPSG:3734, and rows excluded by reason."""
    if not (isinstance(result, tuple) and len(result) == 2 and isinstance(result[0], gpd.GeoDataFrame)
            and isinstance(result[1], dict)):
        raise Stop(f"{ind.id}: code must return (points GeoDataFrame, excluded dict)")
    selected, excluded = result
    if selected.crs is None or selected.crs.to_epsg() != geography.AREA_CRS:
        raise Stop(f"{ind.id}: points must be in EPSG:{geography.AREA_CRS}")
    if selected.geometry.isna().any() or not (selected.geom_type == "Point").all():
        raise Stop(f"{ind.id}: every row must have a point")
    return selected, excluded


def run_visualization(viz: Spec, specs: dict[str, Spec], force: bool = False) -> None:
    ind = specs[viz.meta["indicator"]]
    geo_id = viz.meta["geography"]
    run_indicator(ind, specs, force)
    table_path = indicator_outputs(ind, specs)[geo_id]
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
    note = source_note(ind, specs, data, viz)
    if viz.meta.get("map") == "hexbin":
        classes = heatmap.draw(viz.meta, output.read_points(table_path), geo, note, out)
    else:
        classes = {"breaks": draw(viz.meta, ind.meta["measure"], ind.meta.get("unit", "count"),
                                  output.read_table(table_path), geo, note, out)}
    m = output.write_manifest(out, bf, data, ind_manifest["known_answer_tests"])
    m["indicator_output"] = {"path": ind_manifest["output"], "fingerprint": ind_manifest["fingerprint"]}
    m["classes"] = {"classification": viz.meta["classification"], **classes}
    if ind_manifest.get("caveats"):
        m["caveats"] = ind_manifest["caveats"]
    output.manifest_path(out).write_text(yaml.safe_dump(m, sort_keys=False, allow_unicode=True))
    print(f"  wrote {out.relative_to(ROOT)}")


def source_note(ind: Spec, specs: dict[str, Spec], data: list[dict], viz: Spec | None = None) -> str:
    """Data sources from the Resource and Geography titles, the MOE sentence only when some data
    is from the Census, then the Visualization's own `# Source note` text, if any."""
    parts, census_data = [], False
    for entry in _data_entries(ind, specs):
        res = specs[entry["resource"]]
        fields = ", ".join(entry["fields"])
        if entry.get("dataset"):
            parts.append(f"{res.meta['title']}, {entry['dataset']} {entry['vintage']}: {fields}")
        else:
            parts.append(f"{res.meta['title']}: {fields}")
        census_data = census_data or validate._is_census(res)
    geos = [specs[d["source"]].meta["title"] for d in data
            if d["source"] in specs and specs[d["source"]].type == "Geography"]
    if geos:
        parts.append("Boundaries: " + "; ".join(dict.fromkeys(geos)))
    note = "Source: " + " · ".join(parts) + "."
    if census_data:
        note += " Margins of error at 90% confidence."
    extra = _section(viz.body, "Source note") if viz else ""
    if extra and extra != "None.":
        note += " " + extra
    return note


def _data_entries(ind: Spec, specs: dict[str, Spec]) -> list[dict]:
    """The Indicator's `data`, or with none, its `builds_on` Indicators' (architecture.md § 4.5)."""
    if ind.meta.get("data"):
        return list(ind.meta["data"])
    return [e for dep in ind.meta.get("builds_on") or [] for e in _data_entries(specs[dep], specs)]


def caveats(ind: Spec) -> list[str]:
    """The bullets under the Indicator's `# Caveats`, copied (architecture.md § 8)."""
    out, inside = [], False
    for line in ind.body.splitlines():
        if line.startswith("# "):
            inside = line[2:].strip() == "Caveats"
        elif inside and line.startswith("- "):
            out.append(line[2:].strip())
        elif inside and line.startswith("  ") and out:
            out[-1] += " " + line.strip()
    return out


def _inputs_changed(path, inputs: dict) -> str | None:
    """An input table was rewritten since this output was built (like a map's indicator_output)."""
    mp = output.manifest_path(path)
    if not inputs or not mp.exists():
        return None
    recorded = {i["path"]: i["fingerprint"] for i in yaml.safe_load(mp.read_text()).get("indicator_inputs") or []}
    for dep, m in inputs.items():
        if recorded.get(m["output"]) != m["fingerprint"]:
            return f"{dep} results changed"
    return None


def _section(body: str, heading: str) -> str:
    """Text under a `# heading` in a spec body, up to the next `# ` heading, on one line."""
    lines, inside = [], False
    for line in body.splitlines():
        if line.startswith("# "):
            inside = line[2:].strip() == heading
        elif inside:
            lines.append(line.strip())
    return " ".join(l for l in lines if l)


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
            for g, path in indicator_outputs(s, specs).items():
                r = output.stale_reason(path, bf)
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
