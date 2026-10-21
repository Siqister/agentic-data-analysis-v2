"""Known-answer tests (tests/validation.md § 2). The YAML blocks in tests/known_answers.md are the contract."""

import math
import re

import pandas as pd
import yaml

from lib import ROOT

FILE = ROOT / "tests" / "known_answers.md"


def load() -> dict[str, dict]:
    text = FILE.read_text()
    tests = {}
    for m in re.finditer(r"^## (kat_\d+)\b.*?```yaml\n(.*?)```", text, re.S | re.M):
        tests[m.group(1)] = yaml.safe_load(m.group(2))
    return tests


def evaluate(test: dict, table: pd.DataFrame) -> dict:
    """Compare one computed unit with the published value. Returns a result dict with `status`."""
    row = table[table["geography_id"] == str(test["unit"])]
    if row.empty or pd.isna(row["estimate"].iloc[0]):
        return {"status": "fail", "reason": f"no value for unit {test['unit']}"}
    actual = float(row["estimate"].iloc[0])
    expected = float(test["expected"])
    diff = actual - expected
    tol = str(test["tolerance"]).strip()
    if tol == "exact":
        decimals = len(str(test["expected"]).partition(".")[2])
        allowed, ok = 0.0, round(actual, decimals) == expected
    elif m := re.fullmatch(r"absolute ([\d.]+)", tol):
        allowed = float(m.group(1))
        ok = abs(diff) <= allowed
    elif m := re.fullmatch(r"relative ([\d.]+)%", tol):
        allowed = float(m.group(1)) / 100 * abs(expected)
        ok = abs(diff) <= allowed
    elif tol == "within_moe":
        allowed = math.sqrt(float(row["moe"].iloc[0]) ** 2 + float(test.get("expected_moe") or 0) ** 2)
        ok = abs(diff) <= allowed
    else:
        raise ValueError(f"unknown tolerance: {tol}")
    return {"status": "pass" if ok else "fail", "expected": expected, "actual": actual,
            "difference": diff, "relative_difference": diff / expected if expected else None,
            "tolerance": tol, "allowed": allowed}
