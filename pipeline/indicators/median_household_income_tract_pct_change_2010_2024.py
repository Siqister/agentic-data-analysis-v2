# spec: specs/indicators/median_household_income_tract_pct_change_2010_2024.md
# spec_hash: sha256:8d3a37723bfd4f929d2ba5b55f6bd68e69907e1d09f7921c99a1a092956599f6
# generated: { by: claude-code, at: 2026-10-25T11:31:17-04:00 }
# verified: { by: human:siqi, at: 2026-10-25T11:35:10-04:00 }
"""Percent change in median household income, start to end. Steps follow the spec's # Computation;
the arithmetic, blanks and notes are in lib/change.py.

Returns one table at the Indicator's geography; there are no crosswalks or reliability."""

import pandas as pd

from lib import change


def compute(ctx) -> pd.DataFrame:
    # 1. The start and end Indicators' values at this geography (builds_on: start, then end).
    start_id, end_id = ctx.spec.meta["builds_on"]
    start, end = ctx.indicator(start_id), ctx.indicator(end_id)

    # 2. Inflation factor = to.value ÷ from.value; start and its MOE are multiplied by it.
    factor = change.inflation_factor(ctx.spec.meta["inflation"])

    # 3–6. Percent change; moe blank; blank inputs give a blank change with a note naming the
    # input's period; start, start_moe, end and end_moe kept.
    labels = (change.period(ctx.specs[start_id]), change.period(ctx.specs[end_id]))
    return change.percent_change(start, end, factor, labels)
