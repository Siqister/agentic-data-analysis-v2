---
# CROSSWALK: how to move data from one Geography to another.
# Copy to specs/crosswalks/<from>__to__<to>.md (the file name is the ID).
# Delete weights unless method is population_weighted; delete min_overlap and fields unless it is matched.
# weights_source is required for population_weighted and matched.

type: Crosswalk
title: Block groups (2020) → Cleveland neighborhoods
description: Splits each block group among neighborhoods by where its housing units are.
status: draft                                # draft | stable (only the expert sets stable)

from: bg_2020                                # source Geography
to: cle_neighborhoods                        # target Geography
method: population_weighted                  # population_weighted | areal | centroid | nested | matched
weights: housing_units                       # what is counted: total_population | households | housing_units
weights_source: census_blocks_2020           # Resource with block-level counts and boundaries; for matched, a relationship file
min_overlap: 0.80                            # (matched only) above 0.5, at most 1: shared land area as a share of each unit's
fields:                                      # (matched only) the relationship file's columns
  from_id: GEOID_TRACT_10
  to_id: GEOID_TRACT_20
  from_area: AREALAND_TRACT_10
  to_area: AREALAND_TRACT_20
  shared_area: AREALAND_PART
---

# How it works

Plain-language description with a small worked example, e.g. "Block group X is 70% in A and 30% in B, so 70% of its counts go to A."

# Why this method

Why this method and weighting basis fit the indicators that will use it.

# Edge cases

Units partly outside the target area, units with zero population, slivers from boundaries that almost line up.
