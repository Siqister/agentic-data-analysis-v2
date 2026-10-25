---
type: Resource
title: Census tract relationship file, 2020 ↔ 2010 (Ohio)
description: Census Bureau table of every overlapping pair of a 2020 and a 2010 census tract in Ohio, with their shared land area.
resource: https://www2.census.gov/geo/docs/maps-data/data/rel2020/tract/tab20_tract20_tract10_st39.txt
status: draft
tags: [census, boundaries]
---

# About

Published by the U.S. Census Bureau, Geography Division, as part of the 2020 relationship files. Public domain. A one-time release: it doesn't change between ACS vintages.

One row per pair of a 2020 census tract and a 2010 census tract whose areas overlap, for tracts in Ohio (4,301 rows in the version checked on 2026-10-25). A tract that didn't change appears once, paired with itself. A tract that was split or merged appears once per piece.

# Access

- A pipe-delimited (`|`) text file at the URL above, UTF-8 with a byte-order mark. No authentication.
- Fetched once into a snapshot under `data/raw/`, as one request for the whole file.
- Read only the columns a Crosswalk names, all as text.

# Schema

Columns used:

| Column | Meaning |
|---|---|
| `GEOID_TRACT_20` | 2020 tract GEOID (11 digits: state, county, tract) |
| `GEOID_TRACT_10` | 2010 tract GEOID (11 digits) |
| `AREALAND_TRACT_20` | Land area of the whole 2020 tract, in square metres |
| `AREALAND_TRACT_10` | Land area of the whole 2010 tract, in square metres |
| `AREALAND_PART` | Land area the two tracts share, in square metres |

Other columns: the tracts' `OID`, `NAMELSAD`, `MTFCC` and `FUNCSTAT` codes, `AREAWATER_TRACT_20`, `AREAWATER_TRACT_10` and `AREAWATER_PART`. Layout: <https://www.census.gov/geographies/reference-files/time-series/geo/relationship-files.2020.html>.

# Notes

- **Land area only**, measured on the full-resolution TIGER shapes, not the generalized cartographic boundaries. There are no population or housing counts, so overlap measures land, not where people live.
- **Water-only tracts** (`99xxxx`) have land area 0, so no overlap share can be computed for them.
- Pairs that cross a state line are included, so a few 2010 GEOIDs belong to a neighboring state.
