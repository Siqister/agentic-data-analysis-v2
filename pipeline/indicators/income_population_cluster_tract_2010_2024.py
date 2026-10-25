# spec: specs/indicators/income_population_cluster_tract_2010_2024.md
# spec_hash: sha256:11b9520e86f61c06b0ae69673edbbb23b666e8a8961e20f7259480ca7ab2bdfe
# generated: { by: claude-code, at: 2026-10-25T12:57:00-04:00 }
# verified: { by: human:siqi, at: 2026-10-25T13:04:06-04:00 }
"""k-means clusters from median household income and the change in income and population.
Steps follow the spec's # Computation; the log, scaling, k-means, numbering, notes and run-time
checks are in lib/cluster.py.

Returns one table at the Indicator's geography; there are no crosswalks or reliability."""

import pandas as pd

from lib import cluster


def compute(ctx) -> pd.DataFrame:
    # 1. Each builds_on Indicator's values at this geography, in builds_on order (the first sets the numbering).
    tables = {i: ctx.indicator(i) for i in ctx.spec.meta["builds_on"]}

    # 2–8. Units with a blank input aren't clustered (note names each blank input); log per cluster.log;
    # z-scores, no clipping; k-means (k, seed); clusters numbered by the first input's median;
    # moe blank; one column per input, as published.
    return cluster.assign(tables, ctx.spec.meta["cluster"])
