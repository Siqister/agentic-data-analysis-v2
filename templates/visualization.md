---
# VISUALIZATION: one map (for now, always a choropleth with tooltips).
# Copy to specs/visualizations/<id>.md (the file name is the ID).
# Delete fields marked (optional) when they don't apply.

type: Visualization
title: Households with housing cost burden, 2019–2023   # shown on the map, descriptive only
description: Choropleth of housing cost burden by Cleveland neighborhood.
status: draft                                # draft | stable (only the expert sets stable)

indicator: housing_cost_burden_pct           # sets the color
geography: cle_neighborhoods                 # must be one the indicator is reported at
classification: quantile                     # quantile | equal_interval | natural_breaks | manual
classes: 5
breaks: []                                   # (manual only) break values, lowest to highest
colors: YlOrRd                               # a d3-scale-chromatic scheme name
also_show: []                                # (optional) other Indicators to add to the tooltip
---

# What this map shows

What is measured, and at what geography. No patterns or findings.

# Design choices

Why this classification, number of classes, and color scheme.

# Source note

(Optional) Extra text for the map's footer. Data sources are added automatically.
