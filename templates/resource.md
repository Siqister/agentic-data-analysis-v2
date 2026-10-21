---
# RESOURCE: one API, one file, or one dataset we're allowed to use.
# Copy to specs/resources/<id>.md (the file name is the ID).
# Delete fields marked (optional) or (APIs only) when they don't apply.

type: Resource
title: U.S. Census Bureau Data API
description: Census Bureau API serving ACS and decennial census tables.
resource: https://api.census.gov/data        # URL or project-relative path of the asset
status: draft                                # draft | stable (only the expert sets stable)
tags: [census]                               # (optional)

auth: CENSUS_API_KEY                         # (optional) NAME of the .env variable, never the key
datasets:                                    # (APIs only) the only dataset + vintage combinations indicators may use
  - { dataset: acs/acs5, vintage: 2023 }
  - { dataset: dec/dhc, vintage: 2020 }
---

# About

Who publishes it, what it covers, how often it's updated, and the license.

# Access

How to get data from it. For an API: how to build a request, geography syntax, authentication, and request limits. For a file: where it lives and what format it's in.

# Schema

For a dataset: the columns, with plain meanings (at least the ones we use). For an API: how fields are named (e.g. Census `_E` = estimate, `_M` = margin of error) and where the official field list lives.

# Notes

Pitfalls to know about. For an API, add notes on specific tables, e.g. "B25070: exclude `_011` (not computed) from denominators." Indicators link here instead of repeating them.
