"""Write outputs with manifests, and check whether results are stale (architecture.md §§ 6, 8, 12)."""

import json
from datetime import datetime
from pathlib import Path

import pandas as pd
import yaml

from lib import ROOT
from lib.specs import file_hash, sha256

TABLES = ROOT / "outputs" / "tables"
MAPS = ROOT / "outputs" / "visualizations"

COLUMNS = ["geography_id", "geography_name", "estimate", "moe", "cv", "reliability"]
RATE_COLUMNS = ["numerator", "numerator_moe", "denominator", "denominator_moe"]


def manifest_path(output: Path) -> Path:
    return output.with_name(output.name + ".manifest.yaml")


def lib_hash() -> str:
    """One hash of the shared helpers (Python files and vendored assets)."""
    files = sorted(p for p in (ROOT / "lib").rglob("*") if p.is_file() and "__pycache__" not in p.parts)
    return sha256(json.dumps([[str(p.relative_to(ROOT)), file_hash(p)] for p in files]).encode())


def fingerprint(built_from: list[dict], data: list[dict]) -> str:
    keys = [{k: b.get(k) for k in ("id", "spec_hash", "code_hash")} for b in built_from]
    return sha256(json.dumps([keys, [d["hash"] for d in data], lib_hash()], sort_keys=True).encode())


def write_manifest(output: Path, built_from: list[dict], data: list[dict], tests: dict) -> dict:
    manifest = {
        "output": str(output.relative_to(ROOT)),
        "created": datetime.now().astimezone().isoformat(timespec="seconds"),
        "fingerprint": fingerprint(built_from, data),
        "lib_hash": lib_hash(),
        "built_from": built_from,
        "data": data,
        "known_answer_tests": tests,
    }
    manifest_path(output).write_text(yaml.safe_dump(manifest, sort_keys=False, allow_unicode=True))
    return manifest


def write_table(table: pd.DataFrame, path: Path, built_from, data, tests) -> dict:
    """CSV with the standard columns (§ 12). Values at full precision; blanks stay blank."""
    cols = COLUMNS + [c for c in RATE_COLUMNS if c in table.columns] + ["note"]
    path.parent.mkdir(parents=True, exist_ok=True)
    table[cols].to_csv(path, index=False)
    return write_manifest(path, built_from, data, tests)


def read_table(path: Path) -> pd.DataFrame:
    return pd.read_csv(path, dtype={"geography_id": str, "geography_name": str, "note": str,
                                    "reliability": str}, keep_default_na=False,
                       na_values={c: [""] for c in ["estimate", "moe", "cv", *RATE_COLUMNS]})


def stale_reason(output: Path, built_from: list[dict]) -> str | None:
    """Why `output` must be rebuilt, or None if it's up to date."""
    mp = manifest_path(output)
    if not output.exists() or not mp.exists():
        return "no output yet"
    m = yaml.safe_load(mp.read_text())
    if [b.get("id") for b in m["built_from"]] != [b["id"] for b in built_from]:
        return "the specs it depends on changed"
    for old, new in zip(m["built_from"], built_from):
        for k in ("spec_hash", "code_hash"):
            if old.get(k) != new.get(k):
                return f"{new['id']} {k.replace('_hash', '')} changed"
    for d in m["data"]:
        p = ROOT / d["path"]
        if not p.exists():
            return f"snapshot {d['path']} is missing"
        if file_hash(p) != d["hash"]:
            return f"data {d['path']} changed"
    if m.get("lib_hash") != lib_hash():
        return "lib/ changed"
    if any(v != "pass" for v in (m.get("known_answer_tests") or {}).values()):
        return "a known-answer test did not pass"
    return None
