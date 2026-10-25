---
type: Indicator
title: Total population by census tract, 2006–2010
description: Number of people, from the ACS 2006–2010 5-year estimates.
status: stable
tags: [demographics]

measure: count
geography: tract_2010
crosswalks:
  - tract_2010__to__tract_2020

data:
  - resource: census_api
    dataset: acs/acs5
    vintage: 2010
    fields:
      B01003_001E: Total population

reliability:
  cv_threshold: 0.30
  low: flag
---

# Definition

The estimated number of people living in each unit, from the ACS 2006–2010 5-year estimates, table B01003.

- **Universe:** total population
- **Count:** B01003_001E, with its margin of error B01003_001M
- **Exclusions:** none

# Computation

1. **Annotations** are handled as in [census_api § Notes](../resources/census_api.md#notes).
2. Otherwise, `estimate` = B01003_001E and `moe` = B01003_001M.

Moving the count to other geographies and reliability follow [architecture.md § 12](../../architecture.md#uncertainty-acs).

# Caveats

- ACS estimates come from a sample. Estimates for small units often have large MOEs.
- The 2006–2010 estimates were controlled to the population estimates of the time, not to the 2010 census counts.
- Through a matched crosswalk, a unit's value is its matched source unit's. Their land areas differ by up to `1 − min_overlap` of either unit, and land area isn't the same as where people live.
- Units without a match are blank in the table and gray on the map.
- A map of counts partly reflects how large each unit is.
