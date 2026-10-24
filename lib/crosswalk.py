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


def apply_count(table: pd.DataFrame, weights: pd.DataFrame, label: str = "source unit") -> pd.DataFrame:
    """Move a count and its MOE: estimate = Σ w·e, MOE = √Σ (w·m)².

    Blank source values are left out of the sums, and `note` says how many were left out
    (architecture.md § 12: compute with flagged uncertainty rather than stop).
    A target with no values at all is blank."""
    t = weights.merge(table[["geography_id", "estimate", "moe"]],
                      left_on="from_id", right_on="geography_id", how="left")
    t["e"] = t["weight"] * t["estimate"]
    t["m"] = t["weight"] * t["moe"]
    out = t.groupby("to_id").agg(
        estimate=("e", lambda s: s.sum(min_count=1)),
        moe=("m", lambda s: sum_moe(s.dropna()) if s.notna().any() else float("nan")),
        no_estimate=("e", lambda s: int(s.isna().sum())),
        no_moe=("m", lambda s: int(s.isna().sum())),
    ).reset_index()
    out["note"] = out.apply(_partial_note, axis=1, label=label)
    out = out.rename(columns={"to_id": "geography_id"})
    return out[["geography_id", "estimate", "moe", "note"]]


def _partial_note(row, label: str) -> str:
    """`label` is the source unit's name, singular (e.g. "block group")."""
    def n(k):
        return f"{k} {label}" + ("" if k == 1 else "s")
    parts = []
    if row["no_estimate"]:
        parts.append(f"estimate excludes {n(row['no_estimate'])} with no value")
    if row["no_moe"]:
        parts.append(f"MOE excludes {n(row['no_moe'])} with no MOE")
    return "; ".join(parts)
