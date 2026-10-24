---
# VISUALIZATION: one map: a choropleth with tooltips, or a hexbin heat map of a points Indicator.
# Copy to specs/visualizations/<id>.md (the file name is the ID).
# Delete fields marked (optional) when they don't apply.

type: Visualization
title: Households with housing cost burden, 2019–2023   # shown on the map, descriptive only
description: Choropleth of housing cost burden by Cleveland neighborhood.
status: draft                                # draft | stable (only the expert sets stable)

map: choropleth                              # (optional) choropleth (default) | hexbin
indicator: housing_cost_burden_pct           # sets the color; hexbin: a points Indicator
geography: cle_neighborhoods                 # must be one the indicator is reported at; hexbin: its clip extent
classification: quantile                     # quantile | equal_interval | natural_breaks | manual
classes: 5
breaks: []                                   # (manual only) break values, lowest to highest
colors: YlOrRd                               # a d3-scale-chromatic scheme name
also_show: []                                # (optional, choropleth only) other Indicators to add to the tooltip
hex_size_m: 500                              # (hexbin only) hex width across flats in metres; at least 250
---

# What this map shows

What is measured, and at what geography. No patterns or findings.

# Design choices

Why this classification, number of classes, and color scheme. For a hexbin map: why this hex size, and that the pattern depends on hex size and grid origin and the classes are relative.

# Source note

(Optional) Extra text for the map's footer. Data sources are added automatically.
