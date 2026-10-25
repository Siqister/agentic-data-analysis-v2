# spec: specs/indicators/population_count_2024.md
# spec_hash: sha256:bff8441d9998b0ab58a7e2c8d5ef5034632f6881c3e2ec48cf94147fff7b5b91
# generated: { by: claude-code, at: 2026-10-25T10:42:11-04:00 }
"""Total population (B01003_001). Steps follow the spec's # Computation.

Returns one table at the Indicator's geography; the runner applies crosswalks and reliability."""

import pandas as pd

from lib import census

E = "B01003_001E"


def compute(ctx) -> pd.DataFrame:
    t = ctx.acs(ctx.spec.meta["data"][0])

    # 1–2. Annotations as in census_api § Notes; otherwise the published estimate and MOE.
    est, err = census.estimate_moe(t, E)
    return pd.DataFrame({"geography_id": t["geography_id"], "geography_name": t["geography_name"],
                         "estimate": est, "moe": err, "note": t["annotation"]})
