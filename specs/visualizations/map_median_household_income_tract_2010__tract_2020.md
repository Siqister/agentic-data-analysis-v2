---
type: Visualization
title: Median household income by census tract, 2006–2010
description: Choropleth of 2006–2010 median household income on 2020 census tracts in Cleveland, where a 2010 tract matches.
status: draft

indicator: median_household_income_tract_2010
geography: tract_2020
classification: quantile
classes: 5
colors: Greens
---

# What this map shows

The median household income from the ACS 2006–2010 5-year estimates, in 2010 inflation-adjusted dollars, drawn on 2020 census tracts in Cleveland. Each 2020 tract shows the value of the 2010 tract it matches: their land areas overlap almost completely, both ways ([tract_2010__to__tract_2020](../crosswalks/tract_2010__to__tract_2020.md)). The tooltip shows the tract's name, the estimate, its margin of error, and its reliability, in dollars. Tracts with no match, no published value, or a coded one are gray.

# Design choices

- **Quantile, 5 classes:** each class holds about the same number of tracts that have a value. Gray tracts don't count toward the classes.
- **Greens:** the same scheme as the 2020–2024 block group income map, for the same measure. Its classes aren't comparable with that map's: the dollars are from different years and the units are different (decision 8, chunk 4a).
- **Drawn on 2020 tracts,** so it lines up with the 2020–2024 maps and with the change map planned for chunk 4b.

# Source note

None.
