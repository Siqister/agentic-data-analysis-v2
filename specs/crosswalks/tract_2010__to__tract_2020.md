---
type: Crosswalk
title: Census tracts (2010) → census tracts (2020), matched
description: Gives a 2020 tract the value of the 2010 tract it overlaps almost completely, both ways; other 2020 tracts are blank.
status: draft

from: tract_2010
to: tract_2020
method: matched
weights_source: census_tract_relationship_2020_2010
min_overlap: 0.80
fields:
  from_id: GEOID_TRACT_10
  to_id: GEOID_TRACT_20
  from_area: AREALAND_TRACT_10
  to_area: AREALAND_TRACT_20
  shared_area: AREALAND_PART
---

# How it works

For each pair of a 2010 tract *a* and a 2020 tract *b* in the relationship file, the shared land area is `AREALAND_PART`. They **match** when the shared land area is at least `min_overlap` (80%) of *a*'s land area **and** at least 80% of *b*'s ([architecture.md § 4.3](../../architecture.md#matched)).

Example: 2010 tract A has 1.00 km² of land and 2020 tract B has 0.95 km². They share 0.93 km²: 93% of A and 98% of B, so they match, and B takes A's estimate, margin of error and note unchanged. If A had been split into two 2020 tracts of about half each, neither half would reach 80% of A, so both would be blank.

A 2020 tract with no match, or whose match isn't in `tract_2010`, is blank, with `note` "no matching 2010 tract".

# Why this method

Values like medians can't be split or summed, so they can only move between boundary years where a unit stayed essentially the same. Requiring the overlap both ways means neither tract gained or lost much land. The relationship file's land areas come from full-resolution TIGER shapes, which are the same in both years where a boundary didn't move; intersecting the two cartographic files would add differences from generalization (expert's decision 6, chunk 4a).

`min_overlap` starts at 0.80 and is reviewed at Stop C against the build file `build/crosswalks/tract_2010__to__tract_2020.csv`, which lists every pair with both overlap shares and whether it matched. Changing it is a frontmatter change: results rerun, nothing is recompiled.

# Edge cases

- **Split and merged tracts** don't match and are blank.
- **Tracts that straddle the city line differently** in the two years: a 2020 tract in `tract_2020` whose matched 2010 tract isn't in `tract_2010` is blank. 2010 tracts with no 2020 tract in `tract_2020` are dropped.
- **Water-only tracts** have no land area and never match. They aren't in either Geography.
- **Land area isn't population.** Two tracts that share most of their land can still differ in where households are, e.g. if the land they don't share is densely built.
