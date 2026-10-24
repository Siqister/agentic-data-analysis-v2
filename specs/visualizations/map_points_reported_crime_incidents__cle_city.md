---
type: Visualization
title: Reported crime incidents, 30 Nov 2025 – 30 Sep 2026
description: Hexbin heat map of reported crime incidents (NIBRS Group A) in the City of Cleveland.
status: stable

map: hexbin
indicator: points_reported_crime_incidents
geography: cle_city
hex_size_m: 500
classification: quantile
classes: 5
colors: Purples
---

# What this map shows

Reported crime incidents with at least one NIBRS Group A offense, with offense dates from 30 November 2025 to 30 September 2026, counted in 500 m hexagons across the City of Cleveland. Each hexagon is shaded by its class, from lowest to highest; the tooltip shows the class ("2 of 5"). No counts are shown. Hexagons with no incidents are gray.

# Design choices

- **500 m hexagons** (width across flats): the starting size agreed with the expert, to be tuned at Stop C. It is twice the 250 m privacy floor.
- **The pattern depends on hex size and grid origin.** A different size, or a shifted grid, moves incidents between hexagons. The origin is fixed in `lib/`, so reruns and other hexbin maps share the grid.
- **Edge hexagons are clipped** to the city outline. A clipped hexagon covers less area, so it tends to fall in a lower class.
- **Quantile, 5 classes:** each class holds about the same number of hexagons that have at least one incident. Gray hexagons don't count toward the classes. Classes are relative to this map, and no counts are shown.
- **Purples:** a single-hue sequential scheme, distinct from the existing `Blues` and `Greens`, and without the alarm of reds.

# Source note

Crimes reported to police, not all crimes. Points are aggregated into hexagons; no individual locations are shown.
