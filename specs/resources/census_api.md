---
type: Resource
title: U.S. Census Bureau Data API
description: Census Bureau API serving American Community Survey (ACS) tables.
resource: https://api.census.gov/data
status: stable
tags: [census]

auth: CENSUS_API_KEY
datasets:
  - { dataset: acs/acs5, vintage: 2024 }
---

# About

Published by the U.S. Census Bureau. Serves ACS and decennial census tables as JSON. Public domain. The ACS 5-year release is updated once a year; vintage 2024 is the 2020–2024 5-year estimate, published on 2020 census geography.

# Access

- Request: `https://api.census.gov/data/<vintage>/<dataset>?get=<fields>&for=<geography>&in=<parent>&key=<key>`.
- Block groups must be requested inside a county: `for=block group:*&in=state:39&in=county:035&in=tract:*` (Ohio, Cuyahoga County, all tracts).
- The key is read from `.env` (`CENSUS_API_KEY`) and is removed from any URL saved in a snapshot or manifest.
- At most 50 fields per request.

# Schema

- Field codes are `<table>_<line><suffix>`: `_E` = estimate, `_M` = margin of error (90% confidence).
- Every value arrives as text and is converted to a number after the annotation values below are handled.
- Block group units are identified by `state` + `county` + `tract` + `block group`, which concatenate to the 12-digit `GEOID` used in the boundary files.
- Official field list for each dataset and vintage: `https://api.census.gov/data/<vintage>/<dataset>/variables.json`.

# Notes

- **Annotation values.** Negative codes such as `-666666666`, `-555555555`, `-333333333` and `-222222222` are annotations, not numbers. They must never enter a calculation as values. See the Census Bureau's [ACS notes on estimate and MOE annotations](https://www.census.gov/data/developers/data-sets/acs-1year/notes-on-acs-estimate-and-annotation-values.html).
- **B01003 (Total population).** At block group level, the estimate has a sampling MOE.
