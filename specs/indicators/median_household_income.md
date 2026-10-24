---
type: Indicator
title: Median household income
description: Median household income in the past 12 months, in 2024 dollars, from the ACS 5-year estimates.
status: draft
tags: [income]

measure: median
unit: dollars
geography: bg_2020

data:
  - resource: census_api
    dataset: acs/acs5
    vintage: 2024
    fields:
      B19013_001E: Median household income in the past 12 months (in 2024 inflation-adjusted dollars)

reliability:
  cv_threshold: 0.30
  low: flag
---

# Definition

The median income of households in each block group over the past 12 months, in 2024 inflation-adjusted dollars, from the ACS 2020–2024 5-year estimates, table B19013. The Census Bureau publishes it directly, so nothing is derived here.

- **Universe:** households
- **Value:** B19013_001E, with its margin of error B19013_001M
- **Exclusions:** none

# Computation

1. Pull `B19013_001E` and `B19013_001M` for every block group in Cuyahoga County, Ohio (state `39`, county `035`), which contains all of Cleveland.
2. Build each block group's `GEOID` (state + county + tract + block group) and keep the block groups in `bg_2020`. Every `bg_2020` unit must have a **row**. A missing row is an error. A blank **value** with a note is allowed.
3. **Annotations** ([census_api § Notes](../resources/census_api.md#notes)) are not numbers. If the estimate is an annotation, `estimate` and `moe` are blank. If only the MOE is an annotation, the estimate is kept and `moe` is blank. Either way, the annotation goes in `note`.
4. **Top- and bottom-coded values** ([census_api § Notes](../resources/census_api.md#notes), B19013): an estimate of `250001` or `2499` is a placeholder. `estimate` and `moe` are blank, and `note` reads "top-coded: $250,000 or more" or "bottom-coded: under $2,500". This step overrides step 3: their MOE is the annotation `-333333333`, but both `estimate` and `moe` are blank, and the note gives the coded meaning instead of the annotation code.
5. Otherwise, `estimate` = B19013_001E and `moe` = B19013_001M.
6. **Reliability**: CV = (MOE ÷ 1.645) ÷ estimate. `reliability` is `low` if CV > 0.30, otherwise `ok`. Low values are flagged and kept. A blank `estimate` or `moe` has no CV: `cv` and `reliability` are blank.

# Caveats

- Values are in 2024 inflation-adjusted dollars.
- A median can't be summed or averaged across block groups, so there is no citywide value. That needs a separate method (e.g. interpolation from the B19001 income brackets), deferred to a later chunk.
- Many block groups have no published median (too few sample cases), and a few are coded below $2,500. They are blank in the table and gray on the map.
- ACS medians for block groups often have large MOEs.
