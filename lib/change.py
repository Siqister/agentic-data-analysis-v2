"""Percent change between two Indicators' tables (architecture.md § 4.4, Vintages and change over time).

No MOE for the change (chunk 4b): the inputs' MOEs are carried in start_moe and end_moe."""

import numpy as np
import pandas as pd

from lib.specs import Spec


def inflation_factor(inflation: dict | None) -> float:
    """to.value ÷ from.value, or 1 with no `inflation`."""
    if not inflation:
        return 1.0
    return float(inflation["to"]["value"]) / float(inflation["from"]["value"])


def period(ind: Spec) -> str:
    """An input's period for notes, from its ACS 5-year vintage V: "V−4–V", e.g. "2006–2010"."""
    entries = [e for e in ind.meta.get("data") or [] if e.get("dataset") == "acs/acs5"]
    if len(entries) != 1:
        raise ValueError(f"{ind.id}: can't tell its period (needs one acs/acs5 data entry)")
    v = int(entries[0]["vintage"])
    return f"{v - 4}–{v}"


def percent_change(start: pd.DataFrame, end: pd.DataFrame, factor: float,
                   labels: tuple[str, str]) -> pd.DataFrame:
    """One row per unit of `end`: estimate = (end ÷ (start × factor) − 1) × 100, moe blank,
    start and start_moe times the inflation factor (1 without `inflation`), end and end_moe as published.

    If either input is blank, so is the change, and `note` gives each blank input's period
    and note, start first, e.g. "2006–2010: no matching 2010 tract"."""
    s = start[["geography_id", "estimate", "moe", "note"]]
    e = end[["geography_id", "geography_name", "estimate", "moe", "note"]]
    if set(s["geography_id"]) != set(e["geography_id"]):
        raise ValueError("the start and end tables must have the same units")
    t = e.merge(s, on="geography_id", suffixes=("_end", "_start"))
    out = pd.DataFrame({
        "geography_id": t["geography_id"],
        "geography_name": t["geography_name"],
        "start": t["estimate_start"] * factor,
        "start_moe": t["moe_start"] * factor,
        "end": t["estimate_end"],
        "end_moe": t["moe_end"],
    })
    ok = out["start"].notna() & out["end"].notna() & (out["start"] != 0)
    out["estimate"] = np.where(ok, (out["end"] / out["start"].where(ok) - 1) * 100, np.nan)
    out["moe"] = np.nan
    out["note"] = [_note(r, labels) for r in t.itertuples()]
    return out


def _note(r, labels: tuple[str, str]) -> str:
    parts = []
    for label, est, note in ((labels[0], r.estimate_start, r.note_start), (labels[1], r.estimate_end, r.note_end)):
        if pd.isna(est):
            parts.append(f"{label}: {note if isinstance(note, str) and note else 'no value'}")
        elif est == 0 and label == labels[0]:
            parts.append(f"{label}: estimate is 0")
    return "; ".join(parts)
