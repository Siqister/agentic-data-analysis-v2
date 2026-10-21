---
type: Visualization
title: Total population by block group, 2020–2024
description: Choropleth of total population by 2020 census block group in Cleveland.
status: stable

indicator: population_count
geography: bg_2020
classification: quantile
classes: 5
colors: Blues
---

# What this map shows

The estimated total population of each 2020 census block group in Cleveland, from the ACS 2020–2024 5-year estimates. The tooltip shows the block group's code, the estimate, its margin of error, and its reliability.

# Design choices

- **Quantile, 5 classes:** each class holds about the same number of block groups.
- **Blues:** a single-hue sequential scheme suits a count that runs from low to high.
- The map shows raw counts, so it partly reflects how large each block group is. That's accepted for chunk 1.

# Source note

None.
