"""Margin-of-error math (Census Bureau formulas, 90% confidence) and reliability."""

import numpy as np
import pandas as pd

Z90 = 1.645


def sum_moe(moes) -> float:
    """MOE of a sum: √(sum of squared MOEs)."""
    m = np.asarray(moes, dtype=float)
    return float(np.sqrt(np.sum(m ** 2)))


def reliability(table: pd.DataFrame, cv_threshold: float, low: str) -> pd.DataFrame:
    """Add `cv` and `reliability` columns per the Indicator's settings.

    CV = (MOE ÷ 1.645) ÷ estimate. CV above the threshold is `low`.
    An estimate of 0 has no CV: `cv` blank, `reliability` low, with a note.
    `low: suppress` blanks the estimate and MOE of low-reliability units.
    """
    t = table.copy()
    est, moe = t["estimate"], t["moe"]
    has_value = est.notna() & moe.notna()
    zero = has_value & (est == 0)
    t["cv"] = np.where(has_value & ~zero, (moe / Z90) / est.where(est != 0), np.nan)
    t["reliability"] = np.where(~has_value, "", np.where(zero | (t["cv"] > cv_threshold), "low", "ok"))
    t.loc[zero, "note"] = _append(t.loc[zero, "note"], "estimate is 0; CV undefined")
    if low == "suppress":
        lowmask = t["reliability"] == "low"
        t.loc[lowmask, ["estimate", "moe"]] = np.nan
        t.loc[lowmask, "note"] = _append(t.loc[lowmask, "note"], "suppressed: low reliability")
    elif low != "flag":
        raise ValueError(f"unknown reliability.low: {low}")
    return t


def _append(notes: pd.Series, text: str) -> pd.Series:
    return notes.fillna("").map(lambda n: f"{n}; {text}" if n else text)
