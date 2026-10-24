---
# INDICATOR: one measure, or a reviewed selection of points (measure: points).
# Copy to specs/indicators/<id>.md (the file name is the ID).
# Delete fields marked (optional) when they don't apply.

type: Indicator
title: Households with housing cost burden (%)
description: Share of households spending 30% or more of income on housing costs.
status: draft                                # draft | stable (only the expert sets stable)
tags: [housing]                              # (optional)

measure: percent                             # percent | rate | count | median | index | points
unit: count                                  # (optional) count (default) | dollars; for display only; not for points
geography: bg_2020                           # calculated (and reported) here; for points, the clip extent
crosswalks:                                  # (optional) also reported at each crosswalk's target; not for points
  - bg_2020__to__tract_2020
  - bg_2020__to__cle_neighborhoods
  - bg_2020__to__cle_city

data:                                        # exactly what to pull, and from where (file Resource: resource + fields only)
  - resource: census_api
    dataset: acs/acs5                        # must be on the Resource's approved list
    vintage: 2023
    fields:                                  # code: plain meaning (Census _M fields are pulled automatically)
      B25070_001E: Renter households, total
      B25070_007E: Gross rent 30.0–34.9% of income
      B25070_008E: Gross rent 35.0–39.9% of income
      B25070_009E: Gross rent 40.0–49.9% of income
      B25070_010E: Gross rent 50.0% or more of income
      B25070_011E: Not computed
      # … plus the owner-cost fields from B25091 (example only — not vetted)

builds_on: []                                # (optional) other Indicators this one uses
reliability:                                 # (optional) survey data only; not for points
  cv_threshold: 0.30                         # CV above this = low reliability
  low: flag                                  # flag (keep and mark) | suppress (leave blank)
window:                                      # (optional, points only) ISO dates, both inclusive, local (America/New_York)
  field: OffenseDate                         # one of the data fields
  from: 2025-11-30
  to: 2026-09-30
---

<!-- The body is about the measure, not the place: no place names, unit types, or Geography or
     Crosswalk IDs. Fetching, joining, crosswalks and reliability are done by lib/.
     A points Indicator (ID starts with points_) may name its Resource's fields, and needs # Point rules.
     lib/ applies its window, so the body doesn't repeat the date conversion. -->

# Definition

One plain-language paragraph, then:

- **Universe:** who or what is counted
- **Numerator:**
- **Denominator:**
- **Exclusions:** what is removed, and from where

# Computation

Numbered steps the compiled code must follow, in plain language.

1. …

# Caveats

Known limits, e.g. small samples in some block groups, or differences from other published figures.

<!-- Add only if needed:
# Point rules       (point data) points outside the clip extent, on boundaries, geocoding accepted, denominator
# Aggregation       (median or index with crosswalks) how values are produced at other geographies
-->
