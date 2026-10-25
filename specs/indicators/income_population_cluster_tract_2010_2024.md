---
type: Indicator
title: Income and population clusters by census tract, 2006–2010 to 2020–2024
description: k-means cluster number from 2020–2024 median household income, its percent change from 2006–2010, and the percent change in population over the same periods.
status: draft
tags: [demographics, income, change, cluster]

measure: cluster
geography: tract_2020
builds_on:
  - median_household_income_tract_2024
  - median_household_income_tract_pct_change_2010_2024
  - population_count_tract_pct_change_2010_2024
cluster:
  method: kmeans
  k: 5
  seed: 0
  log: [median_household_income_tract_2024]
---

# Definition

A cluster number for each unit, from k-means on three inputs taken together: median household income in 2020–2024, the percent change in median household income from 2006–2010 to 2020–2024 (in 2024 dollars), and the percent change in total population over the same periods. Units in the same cluster have similar values on all three inputs at once. Clusters are numbered, not named.

- **Universe:** units with a value for every input
- **Inputs:** each `builds_on` Indicator's `estimate`, as published
- **Exclusions:** units where any input is blank

# Computation

1. Read each `builds_on` Indicator's `estimate` at this geography: one input per Indicator, in `builds_on` order.
2. A unit with any blank input is not clustered. Its `estimate` is blank, and `note` lists each blank input by ID with that input's note, e.g. "median_household_income_tract_pct_change_2010_2024: 2006–2010: no matching 2010 tract".
3. Take the natural log of each input listed in `cluster.log`. Each must have only positive values (checked at run time).
4. Scale each input to z-scores over the clustered units: (value − mean) ÷ standard deviation, population SD (ddof 0). No clipping or trimming: extreme values are kept.
5. k-means: scikit-learn `KMeans`, `n_clusters` = `cluster.k`, `random_state` = `cluster.seed`, `n_init` = 50 (fixed in `lib/`), Lloyd algorithm.
6. Number the clusters 1 … k in ascending order of their members' median of the first input (as published, before the log). Ties go by the next input.
7. `estimate` = the cluster number. `moe`, `cv` and `reliability` are blank.
8. The table also has one column per input, named by its Indicator ID, with that input's `estimate` as published (before log and scaling).

# Caveats

- **Clusters divide a continuous spread of units; they aren't distinct groups found in the data.** A unit near the edge of a cluster may differ little from units in the next one.
- **Not tested for statistical significance.** The inputs have sampling error (the changes have no MOE), so membership near cluster edges may not hold. The diagnostics file reports stability.
- Results depend on the inputs, `k`, the log, the scaling and the seed. A new input, a new snapshot or a change in which units have values can change the clusters and their numbers.
- Each input counts equally after scaling. Inputs that measure similar things carry more weight together.
- Extreme values are kept: one unit can form a cluster of its own, or pull a cluster's center.
- Only units with every input have a cluster. For the change inputs, that means units matched one to one across boundary vintages.
- Cluster numbers follow the first input's median. They are an order, not a ranking or a name.
- Each input's own caveats apply.
