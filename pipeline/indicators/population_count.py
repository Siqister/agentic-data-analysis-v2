# spec: specs/indicators/population_count.md
# spec_hash: sha256:dfca17a449b8099123f3060bf23da2420c2bf7daea133db620245c4f5533e139
# generated: { by: claude-code, at: 2026-10-21T17:08:51-04:00 }
# verified: { by: human:siqi, at: 2026-10-21T17:51:45-04:00 }
"""Total population (B01003_001), by block group and for the city. Steps follow the spec's # Computation."""

import pandas as pd

from lib import crosswalk, moe

E, M = "B01003_001E", "B01003_001M"


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

    # 3–4. Estimate and MOE; annotation values are already blank, named in `note`.
    t = pd.DataFrame({"geography_id": t["geography_id"], "geography_name": t["geography_name"],
                      "estimate": t[E], "moe": t[M], "note": t["annotation"]})

    # 5. City: sum of block group estimates, MOE = √(sum of squared MOEs).
    city = crosswalk.apply_count(t, ctx.crosswalk("bg_2020__to__cle_city"))
    city = city.merge(ctx.geography("cle_city")[["geography_id", "geography_name"]], on="geography_id")

    # 6–7. Reliability at every geography.
    return {
        "bg_2020": moe.reliability(t, rel["cv_threshold"], rel["low"]),
        "cle_city": moe.reliability(city, rel["cv_threshold"], rel["low"]),
    }
