---
type: Visualization
title: Census tracts clustered by income, income change, and population change
description: Categorical choropleth of k-means clusters from median household income and the change in income and population, on 2020 census tracts in Cleveland.
status: draft

indicator: income_population_cluster_tract_2010_2024
geography: tract_2020
classification: categorical
classes: 5
colors: Tableau10
---

# What this map shows

The cluster number of each 2020 census tract in Cleveland, from k-means on 2020–2024 median household income, the percent change in median household income from 2006–2010 to 2020–2024, and the percent change in total population over the same periods. The tooltip shows the tract's name, its cluster, and its three input values. The legend lists each cluster with its number of tracts and the median of each input. Tracts without all three inputs, including those with no matching 2010 tract, are gray and labelled "not clustered".

# Design choices

- **Categorical, 5 classes:** one color per cluster; `classes` equals the Indicator's `k`. `k` is provisional and set at Stop C from the diagnostics file and the map (decision 7, chunk 6a).
- **`Tableau10`:** a categorical scheme with distinct, unordered colors, since cluster numbers are not a scale (decision 10, chunk 6a).
- **Cluster profiles in the legend:** the median of each input per cluster helps the expert name the clusters later (decision 3, chunk 6a). Clusters stay numbered until then.

# Source note

Clusters are numbered, not named. Cluster membership is not tested for statistical significance.
