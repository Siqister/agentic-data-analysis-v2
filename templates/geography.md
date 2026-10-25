---
# GEOGRAPHY: one boundary file we report on.
# Copy to specs/geographies/<id>.md (the file name is the ID).
# Delete fields marked (optional) when they don't apply.

type: Geography
title: Census block groups, 2020 (Cleveland)
description: 2020 census block groups within the City of Cleveland.
resource: https://www2.census.gov/geo/tiger/TIGER2020/BG/tl_2020_39_bg.zip   # URL or project-relative path
status: draft                                # draft | stable (only the expert sets stable)
tags: [census, boundaries]                   # (optional)

id_field: GEOID                              # unique code for each unit (always read as text); GEO_ID for Census 2010 cartographic files
name_field: NAMELSAD                         # (optional) display name
within: cle_city                             # (optional) keep only units inside this Geography
within_rule: majority_area                   # (required with within) majority_area | centroid | any
census_unit: block group                     # (optional) block group | tract: the Census API unit id_field's GEOIDs match
---

# About

What the units are, roughly how many there are, who draws them, and the boundary year.

# Which units are included

Why the `within_rule` was chosen, and what it means for units that straddle the line. For a local file, also give the source URL it was downloaded from.

# Notes

Pitfalls, e.g. water-only units, units with zero population, boundary corrections.
