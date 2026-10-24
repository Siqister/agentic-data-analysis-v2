# spec: specs/indicators/median_household_income.md
# spec_hash: sha256:dffec5cac2d6d2c060f1b32d70ae129c634a2155e17b31d08799c309d80bd94f
# generated: { by: claude-code, at: 2026-10-24T14:56:45-04:00 }
"""Median household income (B19013_001), by block group. Steps follow the spec's # Computation."""

import numpy as np
import pandas as pd

from lib import census, moe

E = "B19013_001E"
CODED = {250001: "top-coded: $250,000 or more", 2499: "bottom-coded: under $2,500"}


def compute(ctx) -> dict[str, pd.DataFrame]:
    rel = ctx.spec.meta["reliability"]

    # 1. Every block group in Cuyahoga County, Ohio.
    raw = ctx.acs(ctx.spec.meta["data"][0], for_="block group:*", in_=["state:39", "county:035", "tract:*"])

    # 2. Keep the block groups in bg_2020; every one must have a row.
    bg = ctx.geography("bg_2020")[["geography_id", "geography_name"]]
    t = bg.merge(raw, left_on="geography_id", right_on="GEOID", how="left")
    missing = t.loc[t["GEOID"].isna(), "geography_id"]
    if len(missing):
        raise ValueError(f"no ACS row for block groups: {', '.join(missing)}")

    # 3. Annotations: an annotated estimate blanks both, an annotated MOE only the MOE.
    est, err = census.estimate_moe(t, E)
    note = t["annotation"]

    # 4. Top- and bottom-coded estimates: blank both; the note gives the coded meaning instead.
    coded = est.map(CODED)
    is_coded = coded.notna()
    est, err = est.mask(is_coded, np.nan), err.mask(is_coded, np.nan)
    note = note.mask(is_coded, coded)

    # 5. Otherwise, the published estimate and MOE.
    t = pd.DataFrame({"geography_id": t["geography_id"], "geography_name": t["geography_name"],
                      "estimate": est, "moe": err, "note": note})

    # 6. Reliability.
    return {"bg_2020": moe.reliability(t, rel["cv_threshold"], rel["low"])}
