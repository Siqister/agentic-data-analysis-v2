---
type: Indicator
title: Total population
description: Number of people, from the ACS 5-year estimates.
status: draft
tags: [demographics]

measure: count
geography: bg_2020
crosswalks:
  - bg_2020__to__cle_city

data:
  - resource: census_api
    dataset: acs/acs5
    vintage: 2024
    fields:
      B01003_001E: Total population

reliability:
  cv_threshold: 0.30
  low: flag
---

# Definition

The estimated number of people living in each unit, from the ACS 2020–2024 5-year estimates, table B01003.

- **Universe:** total population
- **Count:** B01003_001E, with its margin of error B01003_001M
- **Exclusions:** none

# Computation

1. **Annotations** are handled as in [census_api § Notes](../resources/census_api.md#notes).
2. Otherwise, `estimate` = B01003_001E and `moe` = B01003_001M.

Moving the count to other geographies and reliability follow [architecture.md § 12](../../architecture.md#uncertainty-acs).

# Caveats

- ACS estimates come from a sample. Estimates for small units often have large MOEs.
- A map of counts partly reflects how large each unit is.
