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

1. Pull `B01003_001E` and `B01003_001M` for every block group in Cuyahoga County, Ohio (state `39`, county `035`), which contains all of Cleveland.
2. Build each block group's `GEOID` (state + county + tract + block group) and keep the block groups in `bg_2020`. Every `bg_2020` unit must have a **row**. A missing row is an error. A blank value with a note is allowed.
3. Annotation values ([census_api § Notes](../resources/census_api.md#notes)) are not numbers. If the estimate is an annotation, `estimate` and `moe` are blank. If only the MOE is an annotation, the estimate is kept and `moe` is blank. Either way, the annotation goes in `note`.
4. **Block groups:** `estimate` = B01003_001E, `moe` = B01003_001M.
5. **City** (through `bg_2020__to__cle_city`): `estimate` = sum of the block group estimates. `moe` = √(sum of squared block group MOEs). If some block groups have a blank estimate or MOE, the sums use the block groups that have one, and `note` says how many were left out of each, e.g. "estimate excludes 2 block groups with no value; MOE excludes 3 block groups with no MOE".
6. **Reliability**, at every geography: CV = (MOE ÷ 1.645) ÷ estimate. `reliability` is `low` if CV > 0.30, otherwise `ok`. Low values are flagged and kept.
7. An estimate of 0 has no CV: `cv` is blank, `reliability` is `low`, and `note` says "estimate is 0; CV undefined".
8. A blank `estimate` or `moe` has no CV: `cv` and `reliability` are blank.

# Caveats

- ACS estimates come from a sample. Block group estimates often have large MOEs.
- The city total is built from whole block groups (majority-area rule), so it can differ from the Census Bureau's published figure for Cleveland city. That figure is a known-answer check (`kat_001`), not the reported value.
- A map of counts partly reflects how large each block group is.
