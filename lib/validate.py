"""Spec validation (tests/validation.md § 1).

    uv run python -m lib.validate [--network]

--network adds the author-mode data field check against the source's own field list.
"""

import argparse
import re
import subprocess
import sys
from dataclasses import dataclass, field

import requests

from lib import ROOT
from lib.compiled import code_path, code_status, read_header
from lib.specs import FOLDERS, SPECS, Spec, dependencies, dependents, load_all

COMMON = ["type", "title", "description", "status"]
REQUIRED = {
    "Resource": ["resource"],
    "Geography": ["resource", "id_field"],
    "Crosswalk": ["from", "to", "method"],
    "Indicator": ["measure", "geography", "data"],
    "Visualization": ["indicator", "geography", "classification", "classes", "colors"],
}
CHOICES = {
    "status": {"draft", "stable", "deprecated"},
    "method": {"population_weighted", "areal", "centroid", "nested"},
    "weights": {"total_population", "households", "housing_units"},
    "measure": {"percent", "rate", "count", "median", "index"},
    "unit": {"count", "dollars"},
    "within_rule": {"majority_area", "centroid", "any"},
    "census_unit": {"block group", "tract"},
    "classification": {"quantile", "equal_interval", "natural_breaks", "manual"},
}


@dataclass
class Report:
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    info: list[str] = field(default_factory=list)

    def text(self) -> str:
        out = []
        for title, items in (("Errors", self.errors), ("Warnings", self.warnings), ("Data fields", self.info)):
            if title == "Data fields" and not items:
                continue
            out.append(f"{title} ({len(items)})")
            out += [f"  {i}" for i in items] or ["  none"]
        return "\n".join(out)


def run(specs: dict[str, Spec] | None = None, network: bool = False) -> Report:
    specs = specs if specs is not None else load_all()
    r = Report()
    err, warn = r.errors.append, r.warnings.append
    secrets = _env_values()

    for s in specs.values():
        f = s.rel
        if "#dup:" in s.id:
            err(f"{f} — file name {s.path.stem} is already used by another spec; IDs must be unique")
        if not s.meta:
            err(f"{f} — no YAML frontmatter")
            continue
        if s.type not in FOLDERS:
            err(f"{f} — type must be one of {', '.join(FOLDERS)} (found {s.type!r})")
            continue
        if s.path.parent.name != FOLDERS[s.type]:
            err(f"{f} — a {s.type} belongs in specs/{FOLDERS[s.type]}/")
        for k in COMMON + REQUIRED[s.type]:
            if s.meta.get(k) in (None, "", []):
                err(f"{f} — missing required field `{k}`")
        if "\n" in str(s.meta.get("description", "")):
            err(f"{f} — `description` must be one line")
        for k, allowed in CHOICES.items():
            if k in s.meta and s.meta[k] not in allowed:
                err(f"{f} — `{k}: {s.meta[k]}` is not allowed; use one of {', '.join(sorted(allowed))}")
        rel = s.meta.get("reliability")
        if rel is not None and (not isinstance(rel, dict) or rel.get("low") not in ("flag", "suppress")):
            err(f"{f} — `reliability.low` must be flag or suppress")
        if any(v and v in s.text for v in secrets) or re.search(r"\b[0-9a-f]{40}\b", s.text):
            err(f"{f} — contains what looks like an API key; refer to keys by their .env variable name only")

        for fld, ref, want in s.refs():
            if ref not in specs:
                err(f"{f} — `{fld}` refers to {ref!r}, which has no spec")
            elif specs[ref].type != want:
                err(f"{f} — `{fld}` refers to {ref!r}, which is a {specs[ref].type}, not a {want}")

        m = s.meta
        if s.type == "Geography" and bool(m.get("within")) != bool(m.get("within_rule")):
            err(f"{f} — `within` and `within_rule` must both be present or both missing")
        if s.type == "Crosswalk":
            pw = m.get("method") == "population_weighted"
            has = [k for k in ("weights", "weights_source") if m.get(k)]
            if pw and len(has) < 2:
                err(f"{f} — population_weighted needs both `weights` and `weights_source`")
            if not pw and has:
                err(f"{f} — `{'`, `'.join(has)}` only apply to population_weighted; remove them")
            frm = specs.get(m.get("from"))
            if m.get("method") == "nested" and frm and frm.meta.get("within") and frm.meta["within"] != m.get("to"):
                err(f"{f} — nested from {frm.id}, which is limited to {frm.meta['within']}, so `to` must be {frm.meta['within']}")
        if s.type == "Indicator":
            for cw in m.get("crosswalks") or []:
                c = specs.get(cw)
                if c and c.meta.get("from") != m.get("geography"):
                    err(f"{f} — crosswalk {cw!r} starts from {c.meta.get('from')}, but this indicator is calculated at {m.get('geography')}")
            for entry in m.get("data") or []:
                res = specs.get(entry.get("resource"))
                if res and res.meta.get("datasets") is not None:
                    approved = {(d.get("dataset"), d.get("vintage")) for d in res.meta["datasets"]}
                    if (entry.get("dataset"), entry.get("vintage")) not in approved:
                        err(f"{f} — {entry.get('dataset')} {entry.get('vintage')} is not on {res.id}'s approved `datasets` list")
                if not entry.get("fields"):
                    err(f"{f} — a `data` entry has no `fields`")
                geo = specs.get(m.get("geography"))
                if _is_census(res) and geo and not geo.meta.get("census_unit"):
                    err(f"{f} — uses Census data, but its geography {geo.id} has no `census_unit`")
            if m.get("measure") in ("median", "index") and m.get("crosswalks") and "Aggregation" not in s.sections():
                err(f"{f} — a {m['measure']} with crosswalks needs an `# Aggregation` section")
        if s.type == "Visualization":
            ind = specs.get(m.get("indicator"))
            if ind and ind.type == "Indicator":
                at = [ind.meta.get("geography")] + [specs[c].meta.get("to") for c in ind.meta.get("crosswalks") or [] if c in specs]
                if m.get("geography") not in at:
                    err(f"{f} — {ind.id} is not reported at {m.get('geography')} (it is at {', '.join(map(str, at))})")
            if m.get("classification") == "manual":
                b = m.get("breaks") or []
                if len(b) != (m.get("classes") or 0) - 1 or b != sorted(b):
                    err(f"{f} — manual `breaks` needs classes − 1 values in increasing order")
            elif m.get("breaks"):
                err(f"{f} — `breaks` only applies to manual classification")

    for s in specs.values():
        try:
            dependencies(s, specs)
        except ValueError as e:
            err(f"{s.rel} — {e}")

    _check_stable_edits(specs, warn)
    _check_indexes(specs, err)
    _check_code(specs, err, warn)
    _check_tests(specs, err)
    if network:
        _check_fields(specs, r)
    return r


def _check_stable_edits(specs, warn):
    """A `stable` spec whose content (anything but `status`) changed since the last commit
    may have been edited without re-approval."""
    for s in specs.values():
        if s.meta.get("status") != "stable":
            continue
        try:
            committed = subprocess.run(["git", "show", f"HEAD:{s.rel}"], cwd=ROOT,
                                       capture_output=True, text=True, check=True).stdout
        except (OSError, subprocess.CalledProcessError):
            continue   # not committed yet, or no git
        if Spec(s.id, s.path, {}, "", committed).hash != s.hash:
            warn(f"{s.rel} — stable, but changed since the last commit. If the agent edited it, "
                 "set it back to draft for the expert to re-approve")


def _env_values() -> list[str]:
    env = ROOT / ".env"
    if not env.exists():
        return []
    return [line.partition("=")[2].strip() for line in env.read_text().splitlines() if "=" in line]


def _check_indexes(specs, err):
    from lib.specs import split_frontmatter
    meta, _ = split_frontmatter((SPECS / "index.md").read_text()) if (SPECS / "index.md").exists() else (None, "")
    if not meta or str(meta.get("okf_version")) != "0.2":
        err('specs/index.md — must declare okf_version: "0.2"')
    for folder in FOLDERS.values():
        idx = SPECS / folder / "index.md"
        if not idx.exists():
            err(f"specs/{folder}/index.md — missing")
            continue
        listed = set(re.findall(r"^\* \[[^\]]+\]\(([^)]+)\.md\) - ", idx.read_text(), re.M))
        actual = {p.stem for p in (SPECS / folder).glob("*.md") if p.name != "index.md"}
        for x in sorted(actual - listed):
            err(f"specs/{folder}/index.md — doesn't list {x}.md")
        for x in sorted(listed - actual):
            err(f"specs/{folder}/index.md — lists {x}.md, which doesn't exist")


def _check_code(specs, err, warn):
    for s in specs.values():
        status = code_status(s)
        if status == "none":
            continue
        path = code_path(s)
        rel = path.relative_to(ROOT)
        if status == "missing":
            err(f"{s.rel} — no compiled code at {rel}")
            continue
        h = read_header(path)
        if h.spec != s.rel or not h.spec_hash or not h.generated:
            err(f"{rel} — header must give spec ({s.rel}), spec_hash and generated")
        if status == "stale":
            above = dependents(s.id, specs)
            warn(f"{rel} — stale: {s.rel} changed since the code was compiled; recompile and review."
                 + (f" Also affects: {', '.join(above)}" if above else ""))
        elif status == "unverified":
            warn(f"{rel} — not reviewed (no `verified` line); can't run in run mode")
    for s in specs.values():
        if s.type in ("Indicator", "Visualization"):
            blockers = [d.id for d in [s, *_safe_deps(s, specs)]
                        if d.meta.get("status") != "stable" or code_status(d) in ("missing", "stale", "unverified")]
            if blockers:
                warn(f"{s.rel} — not ready for run mode: {', '.join(blockers)} draft, stale, or unreviewed")


def _safe_deps(s, specs):
    try:
        return dependencies(s, specs)
    except ValueError:
        return []


def _check_tests(specs, err):
    from lib import known_answers
    for test_id, t in known_answers.load().items():
        ind = specs.get(t.get("indicator"))
        if not ind or ind.type != "Indicator":
            err(f"tests/known_answers.md — {test_id}: indicator {t.get('indicator')!r} has no spec")
            continue
        at = [ind.meta.get("geography")] + [specs[c].meta.get("to") for c in ind.meta.get("crosswalks") or [] if c in specs]
        if t.get("geography") not in at:
            err(f"tests/known_answers.md — {test_id}: {ind.id} is not reported at {t.get('geography')}")


def _is_census(res) -> bool:
    return bool(res) and str(res.meta.get("resource", "")).startswith("https://api.census.gov")


def _check_fields(specs, r: Report):
    for s in specs.values():
        if s.type != "Indicator":
            continue
        for entry in s.meta.get("data") or []:
            res = specs.get(entry.get("resource"))
            if not _is_census(res):
                continue
            _check_published(s, entry, res, specs, r)
            url = f"{res.meta['resource']}/{entry['vintage']}/{entry['dataset']}/variables.json"
            try:
                variables = requests.get(url, timeout=120).json()["variables"]
            except Exception as e:
                r.errors.append(f"{s.rel} — couldn't read {url}: {e}")
                continue
            for code, meaning in entry["fields"].items():
                v = variables.get(code)
                if v is None:
                    r.errors.append(f"{s.rel} — field {code} is not in {entry['dataset']} {entry['vintage']}")
                    continue
                # _M fields are listed as attributes of their _E field, not as variables.
                moe = code[:-1] + "M"
                if code.endswith("E") and moe not in (v.get("attributes") or "").split(","):
                    r.errors.append(f"{s.rel} — {code} has no margin of error field {moe}")
                r.info.append(f"{s.rel} — {code}: spec says {meaning!r}; official label "
                              f"{v['label']!r} ({v.get('concept')})")


def _check_published(s, entry, res, specs, r: Report):
    """A sample request for one tract's units: a field that comes back null for every unit
    isn't published at the geography's census_unit (architecture.md § 12)."""
    from lib import geography
    from lib.snapshot import _env
    geo = specs.get(s.meta.get("geography"))
    unit = geo.meta.get("census_unit") if geo else None
    if not unit:
        return
    try:
        gid = geography.load(geo, specs)["geography_id"].iloc[0]
    except Exception as e:
        r.errors.append(f"{s.rel} — couldn't load {geo.id} to check publication: {e}")
        return
    state, county, tract = gid[:2], gid[2:5], gid[5:11]
    params = [("get", ",".join(entry["fields"]))]
    if unit == "block group":
        params += [("for", "block group:*"), ("in", f"state:{state}"), ("in", f"county:{county}"), ("in", f"tract:{tract}")]
    else:
        params += [("for", f"tract:{tract}"), ("in", f"state:{state}"), ("in", f"county:{county}")]
    key = _env(res.meta.get("auth"))
    url = f"{res.meta['resource']}/{entry['vintage']}/{entry['dataset']}"
    try:
        rows = requests.get(url, params=params + ([("key", key)] if key else []), timeout=120).json()
    except Exception:
        r.errors.append(f"{s.rel} — couldn't check whether its fields are published at {unit} level")
        return
    header, values = rows[0], rows[1:]
    for code in entry["fields"]:
        i = header.index(code)
        if all(v[i] is None for v in values):
            r.errors.append(f"{s.rel} — {code} is not published at {unit} level ({geo.id})")


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--network", action="store_true")
    args = p.parse_args(argv)
    report = run(network=args.network)
    print(report.text())
    return 1 if report.errors else 0


if __name__ == "__main__":
    sys.exit(main())
