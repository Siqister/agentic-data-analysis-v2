---
type: Visualization
title: Change in total population by census tract, 2006–2010 to 2020–2024
description: Choropleth of the percent change in total population on 2020 census tracts in Cleveland.
status: stable

indicator: population_count_tract_pct_change_2010_2024
geography: tract_2020
classification: manual
classes: 10
breaks: [-20, -15, -10, -5, 0, 5, 10, 15, 20]
colors: RdBu
---

# What this map shows

The percent change in total population on each 2020 census tract in Cleveland, from the ACS 2006–2010 to the 2020–2024 5-year estimates. The tooltip shows the tract's name, the change, and both counts. Tracts without both counts, including those with no matching 2010 tract, and tracts with a start of 0 are gray.

# Design choices

- **Manual breaks at −20, −15, −10, −5, 0, +5, +10, +15, +20 %, 10 classes:** fixed breaks keep 0 as a class boundary, so decline and increase are never in the same class. Tunable at Stop C (decision 3, chunk 5).
- **`RdBu`:** a diverging scheme, red for decline to blue for increase, with the lightest colors on either side of 0.
- **No significance shown:** the change has no MOE (decision 8, chunk 4b), so classes don't say whether a change is beyond sampling error. The source note says so.

# Source note

Change is not tested for statistical significance.
