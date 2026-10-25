---
type: Visualization
title: Change in median household income by census tract, 2006–2010 to 2020–2024
description: Choropleth of the percent change in median household income, in 2024 dollars, on 2020 census tracts in Cleveland.
status: stable

indicator: median_household_income_tract_pct_change_2010_2024
geography: tract_2020
classification: manual
classes: 8
breaks: [-15, -10, -5, 0, 5, 10, 15]
colors: RdBu
---

# What this map shows

The percent change in median household income on each 2020 census tract in Cleveland, from the ACS 2006–2010 to the 2020–2024 5-year estimates, with the 2006–2010 values adjusted to 2024 dollars. The tooltip shows the tract's name, the change, and both medians in 2024 dollars. Tracts without both medians, including those with no matching 2010 tract, are gray.

# Design choices

- **Manual breaks at −15, −10, −5, 0, +5, +10, +15 %, 8 classes:** fixed breaks keep 0 as a class boundary, so decline and increase are never in the same class. The same breaks would apply to another pair of years. Tunable at Stop C (decision 9, chunk 4b).
- **`RdBu`:** a diverging scheme, red for decline to blue for increase, with the lightest colors on either side of 0.
- **No significance shown:** the change has no MOE (decision 8, chunk 4b), so classes don't say whether a change is beyond sampling error. The source note says so.

# Source note

Change is not tested for statistical significance.
