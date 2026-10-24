# spec: specs/indicators/population_count.md
# spec_hash: sha256:29a8e3906988e73df6a568c2adac699531a0718105befb42005f4c303edf6552
# generated: { by: claude-code, at: 2026-10-24T15:23:00-04:00 }
# verified: { by: human:siqi, at: 2026-10-24T15:27:40-04:00 }
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
