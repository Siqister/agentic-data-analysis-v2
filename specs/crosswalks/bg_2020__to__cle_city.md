---
type: Crosswalk
title: Block groups (2020) → City of Cleveland
description: Assigns every Cleveland block group, whole, to the city.
status: stable

from: bg_2020
to: cle_city
method: nested
---

# How it works

Every block group in `bg_2020` goes entirely to `cle_city` (weight 1). A city count is the sum of the block group counts, and its MOE is combined with the Census Bureau's formula for sums.

# Why this method

`bg_2020` is already limited to block groups inside `cle_city` (`within: cle_city`, majority-area rule). Every unit therefore belongs to the one target, so splitting them would add nothing.

# Edge cases

Block groups that straddle the city line are counted fully in or fully out, as decided by `bg_2020`'s majority-area rule. The resulting city total can differ from published "Cleveland city" figures.
