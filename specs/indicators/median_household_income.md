---
type: Indicator
title: Median household income
description: Median household income in the past 12 months, in 2024 dollars, from the ACS 5-year estimates.
status: stable
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

The median income of households in each unit over the past 12 months, in 2024 inflation-adjusted dollars, from the ACS 2020–2024 5-year estimates, table B19013. The Census Bureau publishes it directly, so nothing is derived here.

- **Universe:** households
- **Value:** B19013_001E, with its margin of error B19013_001M
- **Exclusions:** none

# Computation

1. **Annotations** are handled as in [census_api § Notes](../resources/census_api.md#notes).
2. **Top- and bottom-coded values** ([census_api § Notes](../resources/census_api.md#notes), B19013): an estimate of `250001` or `2499` is a placeholder. `estimate` and `moe` are blank, and `note` reads "top-coded: $250,000 or more" or "bottom-coded: under $2,500". This step overrides step 1: their MOE is the annotation `-333333333`, but both `estimate` and `moe` are blank, and the note gives the coded meaning instead of the annotation code.
3. Otherwise, `estimate` = B19013_001E and `moe` = B19013_001M.

Reliability follows [architecture.md § 12](../../architecture.md#uncertainty-acs).

# Caveats

- Values are in 2024 inflation-adjusted dollars.
- A median can't be summed or averaged across units, so it is reported only where it's published. Other geographies need a separate method (e.g. interpolation from the B19001 income brackets) in an `# Aggregation` section.
- Units with too few sample cases have no published median, and a few are coded below $2,500 or at $250,000 or more. They are blank in the table and gray on the map.
- ACS medians for small units often have large MOEs.
