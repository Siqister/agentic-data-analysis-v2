---
type: Geography
title: City of Cleveland boundary
description: The City of Cleveland's official municipal boundary, as published by the City.
resource: data/static/cle_city/City_Boundary_-6607456956089209299.gpkg
status: draft
tags: [boundaries, city]

id_field: NAME
name_field: NAME
---

# About

One unit: the City of Cleveland, Ohio. A GeoPackage with one layer (`City_Boundary`) holding one multipolygon, coordinate system EPSG:3734 (NAD83 / Ohio North, US feet) embedded in the file. About 78.4 square miles.

Fields: `NAME` (`Cleveland`), plus `CREATEDBY`, `DATECREATED`, `MODIFIEDBY`, `DATEMODIFIED`, `MAINTENANCEID` and `GLOBALID`. The file has no Census code, so `id_field` is `NAME`, and the unit code is `Cleveland`.

Source: City of Cleveland Open Data, City Boundary dataset — <https://data.clevelandohio.gov/datasets/fa8ba3c00cf842fd8dd49e8d9e80e268_0>. Downloaded by the expert as a GeoPackage on 2026-10-21.

# Which units are included

The single feature in the file. No `within` rule.

# Notes

- This is the City's boundary, not the Census Bureau's "Cleveland city" place boundary (place `3916000`). The two may differ slightly, which is one reason `kat_001` has a tolerance.
- Local file: hashed in place for manifests. It lives in `data/static/`, which is not committed.
