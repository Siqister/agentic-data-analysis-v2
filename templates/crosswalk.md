---
# CROSSWALK: how to move data from one Geography to another.
# Copy to specs/crosswalks/<from>__to__<to>.md (the file name is the ID).
# Delete the weights fields unless method is population_weighted.

type: Crosswalk
title: Block groups (2020) → Cleveland neighborhoods
description: Splits each block group among neighborhoods by where its housing units are.
status: draft                                # draft | stable (only the expert sets stable)

from: bg_2020                                # source Geography
to: cle_neighborhoods                        # target Geography
method: population_weighted                  # population_weighted | areal | centroid | nested
weights: housing_units                       # what is counted: total_population | households | housing_units
weights_source: census_blocks_2020           # Resource with block-level counts and boundaries
---

# How it works

Plain-language description with a small worked example, e.g. "Block group X is 70% in A and 30% in B, so 70% of its counts go to A."

# Why this method

Why this method and weighting basis fit the indicators that will use it.

# Edge cases

Units partly outside the target area, units with zero population, slivers from boundaries that almost line up.
