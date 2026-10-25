---
type: Geography
title: Census tracts, 2020 (Cleveland)
description: 2020 census tracts with most of their area inside the City of Cleveland.
resource: https://www2.census.gov/geo/tiger/GENZ2020/shp/cb_2020_39_tract_500k.zip
status: draft
tags: [census, boundaries]

id_field: GEOID
name_field: NAMELSAD
within: cle_city
within_rule: majority_area
census_unit: tract
---

# About

Census tracts drawn for the 2020 census, from the Census Bureau's 2020 **cartographic boundary file** for Ohio (1:500,000), the same kind of file as `bg_2020`. Cartographic boundaries are clipped to the shoreline, so tracts along Lake Erie don't extend over the water, as they do in TIGER/Line.

The file covers all of Ohio: 3,162 tracts, coordinate system EPSG:4269 (NAD83). It is fetched automatically from the URL above into a snapshot under `data/raw/`.

Fields used: `GEOID` (11 digits: state, county, tract) and `NAMELSAD` (display name, e.g. `Census Tract 1114.01`).

`GEOID` matches the Census Data API's tract codes (`census_unit: tract`), so Census data for these units is requested for the states and counties their GEOIDs fall in.

# Which units are included

**Majority-area rule:** a tract is in `tract_2020` if more than 50% of its area is inside `cle_city`. Areas are measured in EPSG:3734. The same rule as `bg_2020`, so both keep the city's units whole.

Tracts are larger than block groups, so the rule moves more area in or out of the city at the boundary, and totals built from tracts differ more from totals for the city's exact boundary.

# Notes

- Water-only tracts (e.g. Lake Erie, `39035990000`) aren't in the cartographic file.
- Tracts with zero population are kept. Their values are handled by the Indicator.
- Area is measured from the clipped cartographic shapes, so water doesn't count toward a tract's area.
