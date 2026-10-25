---
type: Visualization
title: Median household income by block group, 2020–2024
description: Choropleth of median household income by 2020 census block group in Cleveland.
status: draft

indicator: median_household_income_2024
geography: bg_2020
classification: quantile
classes: 5
colors: Greens
---

# What this map shows

The median household income of each 2020 census block group in Cleveland, from the ACS 2020–2024 5-year estimates, in 2024 inflation-adjusted dollars. The tooltip shows the block group's code, the estimate, its margin of error, and its reliability, in dollars. Block groups with no published value, or a coded one, are gray.

# Design choices

- **Quantile, 5 classes:** each class holds about the same number of block groups that have a value. Gray block groups don't count toward the classes.
- **Greens:** a single-hue sequential scheme for a value that runs from low to high, distinct from the population map's `Blues`.

# Source note

None.
