---
type: Indicator
title: Change in total population by census tract, 2006–2010 to 2020–2024 (%)
description: Percent change in the number of people from the ACS 2006–2010 to the 2020–2024 5-year estimates.
status: draft
tags: [demographics, change]

measure: percent_change
geography: tract_2020
builds_on:
  - population_count_tract_2010
  - population_count_tract_2024
---

# Definition

The percent change in each unit's estimated number of people, from the ACS 2006–2010 5-year estimate (the start) to the ACS 2020–2024 5-year estimate (the end). The two periods don't overlap, as the Census Bureau requires for comparing 5-year estimates.

- **Universe:** total population
- **Start:** the start Indicator's count, as published
- **End:** the end Indicator's count, as published
- **Exclusions:** units where either count is blank, or the start is 0

# Computation

1. `start` = the start Indicator's value at this geography; `end` = the end Indicator's value. Each comes with its MOE and note.
2. `estimate` = (`end` ÷ `start` − 1) × 100.
3. `moe` is blank: the change has no MOE. `cv` and `reliability` are blank too.
4. If either value is blank, `estimate` and `moe` are blank, and `note` says which input is blank and why, with the input's period first, e.g. "2006–2010: no matching 2010 tract". A start of 0 gives no change either, and `note` says so.
5. The table also has `start`, `start_moe`, `end` and `end_moe`.

# Caveats

- **Not tested for statistical significance, and no MOE.** The inputs' MOEs are in `start_moe` and `end_moe`.
- Only units matched one to one between the two boundary vintages have a value. The match is by land area, not by where people live: people in the up to `1 − min_overlap` of land the two units don't share count in one period and not the other.
- The 2006–2010 estimates were controlled to the population estimates of the time, not to the 2010 census counts; the 2020–2024 estimates to estimates based on the 2020 census. Part of a change can come from the controls, not from people moving.
- The 2020–2024 period includes 2020, when ACS data collection was disrupted.
- A start of 0 gives no change.
