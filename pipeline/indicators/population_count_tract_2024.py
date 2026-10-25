# spec: specs/indicators/population_count_tract_2024.md
# spec_hash: sha256:5547421c37669bb55016be2b6e2cae7516fb1e13ba8b5e5006e0e80b97779f6c
# generated: { by: claude-code, at: 2026-10-25T12:05:47-04:00 }
# verified: { by: human:siqi, at: 2026-10-25T12:14:45-04:00 }
"""Total population (B01003_001). Steps follow the spec's # Computation.

Returns one table at the Indicator's geography; the runner applies reliability."""

import pandas as pd

from lib import census

E = "B01003_001E"


def compute(ctx) -> pd.DataFrame:
    t = ctx.acs(ctx.spec.meta["data"][0])

    # 1–2. Annotations as in census_api § Notes; otherwise the published estimate and MOE.
    est, err = census.estimate_moe(t, E)
    return pd.DataFrame({"geography_id": t["geography_id"], "geography_name": t["geography_name"],
                         "estimate": est, "moe": err, "note": t["annotation"]})
