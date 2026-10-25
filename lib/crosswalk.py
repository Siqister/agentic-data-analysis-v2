"""Build and apply crosswalks (architecture.md § 4.3). Crosswalks move counts only,
except `matched`, which copies values unchanged."""

import numpy as np
import pandas as pd

from lib import ROOT, geography
from lib.moe import sum_moe
from lib.snapshot import Snapshot
from lib.specs import Spec

MATCHED_FIELDS = ("from_id", "to_id", "from_area", "to_area", "shared_area")

BUILD = ROOT / "build" / "crosswalks"


def build(spec: Spec, source, target, specs: dict[str, Spec], snaps: list[Snapshot] | None = None) -> pd.DataFrame:
    """Weights table: from_id, to_id, weight. `source` and `target` are loaded Geographies.
    For `matched`, the matched pairs (from_id, to_id) instead; see `build_matched`."""
    method = spec.meta["method"]
    if method == "matched":
        return build_matched(spec, source, target, specs, snaps)
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


def build_matched(spec: Spec, source, target, specs: dict[str, Spec],
                  snaps: list[Snapshot] | None = None) -> pd.DataFrame:
    """Pairs that match by reciprocal land-area overlap (architecture.md § 4.3, matched):
    shared ≥ min_overlap × the source unit's land area and ≥ min_overlap × the target's.

    Writes every pair that touches a source or target unit to the build file, with both
    shares, whether it matched, and whether each unit is in its Geography. Returns the
    matched pairs whose units are both in their Geographies: from_id, to_id."""
    res = specs[spec.meta["weights_source"]]
    snap = geography.snapshot(res)
    if snaps is not None:
        snaps.append(snap)
    f = spec.meta["fields"]
    rel = read_delimited(snap.path, [f[k] for k in MATCHED_FIELDS])
    pairs = pd.DataFrame({"from_id": rel[f["from_id"]], "to_id": rel[f["to_id"]]})
    from_area, to_area, shared = (pd.to_numeric(rel[f[k]], errors="raise")
                                  for k in ("from_area", "to_area", "shared_area"))
    # A unit with no land area has no overlap share, so it never matches.
    pairs["from_share"] = (shared / from_area).where(from_area > 0)
    pairs["to_share"] = (shared / to_area).where(to_area > 0)
    m = spec.meta["min_overlap"]
    pairs["matched"] = (pairs["from_share"] >= m) & (pairs["to_share"] >= m)
    pairs["from_in_geography"] = pairs["from_id"].isin(source["geography_id"])
    pairs["to_in_geography"] = pairs["to_id"].isin(target["geography_id"])
    pairs = pairs[pairs["from_in_geography"] | pairs["to_in_geography"]].reset_index(drop=True)
    BUILD.mkdir(parents=True, exist_ok=True)
    pairs.to_csv(BUILD / f"{spec.id}.csv", index=False)

    out = pairs.loc[pairs["matched"] & pairs["from_in_geography"] & pairs["to_in_geography"], ["from_id", "to_id"]]
    for col in ("from_id", "to_id"):
        if out[col].duplicated().any():
            raise ValueError(f"{spec.id}: a unit has more than one match; min_overlap must be above 0.5")
    return out.reset_index(drop=True)


def read_delimited(path, columns: list[str]) -> pd.DataFrame:
    """Only the named columns of a delimited text file, all as text, byte-order mark removed
    (architecture.md § 10). The delimiter is the first of | tab , found in the header."""
    with open(path, encoding="utf-8-sig") as fh:
        header = fh.readline()
    sep = next((c for c in ("|", "\t", ",") if c in header), None)
    if sep is None:
        raise ValueError(f"{path}: can't tell the delimiter from the header")
    have = header.rstrip("\r\n").split(sep)
    missing = [c for c in columns if c not in have]
    if missing:
        raise ValueError(f"{path}: no column {', '.join(missing)}")
    return pd.read_csv(path, sep=sep, usecols=columns, dtype=str, encoding="utf-8-sig", keep_default_na=False)


def apply_matched(table: pd.DataFrame, pairs: pd.DataFrame, target_ids, label: str) -> pd.DataFrame:
    """Copy estimate, moe and note from each target unit's matched source unit, unchanged.
    A target unit with no match is blank, with note "no matching <label>" (e.g. "2010 tract")."""
    t = pd.DataFrame({"geography_id": list(target_ids)})
    t = t.merge(pairs, left_on="geography_id", right_on="to_id", how="left")
    t = t.merge(table[["geography_id", "estimate", "moe", "note"]].rename(columns={"geography_id": "from_id"}),
                on="from_id", how="left")
    none = t["from_id"].isna()
    t.loc[none, ["estimate", "moe"]] = np.nan
    t.loc[none, "note"] = f"no matching {label}"
    return t[["geography_id", "estimate", "moe", "note"]]


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
