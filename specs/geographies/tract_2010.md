---
type: Geography
title: Census tracts, 2010 (Cleveland)
description: 2010 census tracts with most of their area inside the City of Cleveland.
resource: https://www2.census.gov/geo/tiger/GENZ2010/gz_2010_39_140_00_500k.zip
status: stable
tags: [census, boundaries]

id_field: GEO_ID
name_field: NAME
within: cle_city
within_rule: majority_area
census_unit: tract
---

# About

Census tracts drawn for the 2010 census, from the Census Bureau's 2010 **cartographic boundary file** for Ohio (1:500,000), the same kind of file as `tract_2020`. ACS 5-year estimates from 2010 through 2019 are published on these tracts.

The file covers all of Ohio: 2,948 tracts, coordinate system EPSG:4269 (NAD83). It is fetched automatically from the URL above into a snapshot under `data/raw/`.

Fields used:
- `GEO_ID`: the summary level, `US`, and the 11-digit tract GEOID, e.g. `1400000US39035111401`. The 2010 file has no `GEOID` field; `lib/` keeps the part after `US` as the unit's code ([architecture.md § 4.2](../../architecture.md#42-geography)).
- `NAME`: the tract number only, e.g. `1114.01` (no "Census Tract" prefix, unlike `tract_2020`).

The 11-digit code matches the Census Data API's tract codes (`census_unit: tract`).

**Not TIGER/Line:** its tract shapes extend into Lake Erie, which would change the majority-area rule for lakeshore tracts, and it wouldn't match how `tract_2020` is drawn.

# Which units are included

**Majority-area rule:** a tract is in `tract_2010` if more than 50% of its area is inside `cle_city`. Areas are measured in EPSG:3734. The same rule as `tract_2020`.

The city boundary is today's (`cle_city`), not the 2010 one. Tracts are larger than block groups, so the rule moves more area in or out of the city at the boundary.

# Notes

- Water-only tracts (e.g. Lake Erie, `39035990000`) aren't in the cartographic file.
- Tracts with zero population are kept. Their values are handled by the Indicator.
- The 2010 and 2020 cartographic files are generalized separately, so a tract that didn't change can have slightly different shapes in the two. Matching across years uses the relationship file's land areas, not these shapes.
