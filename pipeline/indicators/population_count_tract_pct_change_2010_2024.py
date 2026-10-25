# spec: specs/indicators/population_count_tract_pct_change_2010_2024.md
# spec_hash: sha256:5a5d267d828260219d2c4227fc6c10b59ee4bdadb25b5413ddfebeec2f87dd66
# generated: { by: claude-code, at: 2026-10-25T12:05:47-04:00 }
# verified: { by: human:siqi, at: 2026-10-25T12:14:45-04:00 }
"""Percent change in total population, start to end. Steps follow the spec's # Computation;
the arithmetic, blanks and notes are in lib/change.py.

Returns one table at the Indicator's geography; there are no crosswalks or reliability."""

import pandas as pd

from lib import change


def compute(ctx) -> pd.DataFrame:
    # 1. The start and end Indicators' values at this geography (builds_on: start, then end).
    start_id, end_id = ctx.spec.meta["builds_on"]
    start, end = ctx.indicator(start_id), ctx.indicator(end_id)

    # No `inflation`: the factor is 1, so start and start_moe are as published.
    factor = change.inflation_factor(ctx.spec.meta.get("inflation"))

    # 2–5. Percent change; moe blank; blank inputs or a start of 0 give a blank change with a note
    # naming the input's period; start, start_moe, end and end_moe kept.
    labels = (change.period(ctx.specs[start_id]), change.period(ctx.specs[end_id]))
    return change.percent_change(start, end, factor, labels)
