# spec: specs/indicators/median_household_income_tract_2010.md
# spec_hash: sha256:2dc89bf2520ad16ea5725e44d3796942e4676ceee2010f31719f3b947db90c89
# generated: { by: claude-code, at: 2026-10-25T11:03:31-04:00 }
# verified: { by: human:siqi, at: 2026-10-25T11:10:24-04:00 }
"""Median household income (B19013_001). Steps follow the spec's # Computation.

Returns one table at the Indicator's geography; the runner applies the matched
crosswalk (# Aggregation) and reliability."""

import numpy as np
import pandas as pd

from lib import census

E = "B19013_001E"
CODED = {250001: "top-coded: $250,000 or more", 2499: "bottom-coded: under $2,500"}


def compute(ctx) -> pd.DataFrame:
    t = ctx.acs(ctx.spec.meta["data"][0])

    # 1. Annotations as in census_api § Notes.
    est, err = census.estimate_moe(t, E)
    note = t["annotation"]

    # 2. Top- and bottom-coded estimates: blank both; the note gives the coded meaning instead.
    coded = est.map(CODED)
    is_coded = coded.notna()
    est, err = est.mask(is_coded, np.nan), err.mask(is_coded, np.nan)
    note = note.mask(is_coded, coded)

    # 3. Otherwise, the published estimate and MOE.
    return pd.DataFrame({"geography_id": t["geography_id"], "geography_name": t["geography_name"],
                         "estimate": est, "moe": err, "note": note})
