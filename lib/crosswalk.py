"""Build and apply crosswalks (architecture.md § 4.3). Crosswalks move counts only."""

import pandas as pd

from lib import ROOT
from lib.moe import sum_moe
from lib.specs import Spec

BUILD = ROOT / "build" / "crosswalks"


def build(spec: Spec, source, target, specs: dict[str, Spec]) -> pd.DataFrame:
    """Weights table: from_id, to_id, weight. `source` and `target` are loaded Geographies."""
    method = spec.meta["method"]
    if method == "nested":
        frm = specs[spec.meta["from"]]
        if frm.meta.get("within") == spec.meta["to"] and len(target) == 1:
            # The within filter already put every source unit in the one target unit.
            weights = pd.DataFrame({"from_id": source["geography_id"],
                                    "to_id": target["geography_id"].iloc[0], "weight": 1.0})
        else:
            raise NotImplementedError(
                f"{spec.id}: nested crosswalks other than '<from>.within == to' (one target unit) "
                "aren't built yet; generalize lib/crosswalk.py with review")
    else:
        raise NotImplementedError(f"{spec.id}: method {method} isn't built yet")
    BUILD.mkdir(parents=True, exist_ok=True)
    weights.to_csv(BUILD / f"{spec.id}.csv", index=False)
    return weights


def apply_count(table: pd.DataFrame, weights: pd.DataFrame) -> pd.DataFrame:
    """Move a count and its MOE: estimate = Σ w·e, MOE = √Σ (w·m)².

    Every source unit must have a value; a blank one stops the run, because the spec
    doesn't say how a target total with missing parts should be reported."""
    t = weights.merge(table[["geography_id", "estimate", "moe"]],
                      left_on="from_id", right_on="geography_id", how="left")
    missing = t[t["estimate"].isna() | t["moe"].isna()]
    if len(missing):
        raise ValueError(f"crosswalk source units without a value: {', '.join(missing['from_id'][:10])}")
    t["e"] = t["weight"] * t["estimate"]
    t["m"] = t["weight"] * t["moe"]
    out = t.groupby("to_id").agg(estimate=("e", "sum"), moe=("m", sum_moe)).reset_index()
    out = out.rename(columns={"to_id": "geography_id"})
    out["note"] = ""
    return out
