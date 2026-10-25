---
type: Indicator
title: Median household income by census tract, 2006–2010
description: Median household income in the past 12 months, in 2010 dollars, from the ACS 2006–2010 5-year estimates.
status: draft
tags: [income]

measure: median
unit: dollars
geography: tract_2010
crosswalks:
  - tract_2010__to__tract_2020

data:
  - resource: census_api
    dataset: acs/acs5
    vintage: 2010
    fields:
      B19013_001E: Median household income in the past 12 months (in 2010 inflation-adjusted dollars)

reliability:
  cv_threshold: 0.30
  low: flag
---

# Definition

The median income of households in each unit over the past 12 months, in 2010 inflation-adjusted dollars, from the ACS 2006–2010 5-year estimates, table B19013. The Census Bureau publishes it directly, so nothing is derived here.

- **Universe:** households
- **Value:** B19013_001E, with its margin of error B19013_001M
- **Exclusions:** none

# Computation

1. **Annotations** are handled as in [census_api § Notes](../resources/census_api.md#notes).
2. **Top- and bottom-coded values** ([census_api § Notes](../resources/census_api.md#notes), B19013): an estimate of `250001` or `2499` is a placeholder. `estimate` and `moe` are blank, and `note` reads "top-coded: $250,000 or more" or "bottom-coded: under $2,500". This step overrides step 1: their MOE is the annotation `-333333333`, but both `estimate` and `moe` are blank, and the note gives the coded meaning instead of the annotation code.
3. Otherwise, `estimate` = B19013_001E and `moe` = B19013_001M.

Reliability follows [architecture.md § 12](../../architecture.md#uncertainty-acs).

# Aggregation

A median can't be split or summed, so it moves only through a crosswalk that pairs units one to one (`matched`, [architecture.md § 4.3](../../architecture.md#matched)). The value at the target unit is the source unit's published median, with its MOE and note, unchanged. Target units without a pair are blank, with the crosswalk's note. Reliability is computed again from the copied values, so it's the same as the source unit's.

# Caveats

- Values are in 2010 inflation-adjusted dollars. They are not comparable with later years until adjusted for inflation.
- The 2006–2010 estimates were controlled to the population estimates of the time, not to the 2010 census counts.
- Through a matched crosswalk, a unit's value is its matched source unit's. Their land areas differ by up to `1 − min_overlap` of either unit, and land area isn't the same as where households are.
- Units with too few sample cases have no published median, a few may be coded below $2,500 or at $250,000 or more, and units without a match are blank. They are blank in the table and gray on the map.
- The top and bottom codes are in 2010 dollars, so they don't stand for the same real income as later years' codes.
- ACS medians for small units often have large MOEs.
