---
type: Indicator
title: Change in median household income by census tract, 2006–2010 to 2020–2024 (%)
description: Percent change in median household income from the ACS 2006–2010 to the 2020–2024 5-year estimates, in 2024 dollars.
status: stable
tags: [income, change]

measure: percent_change
geography: tract_2020
builds_on:
  - median_household_income_tract_2010
  - median_household_income_tract_2024

inflation:
  index: R-CPI-U-RS
  from: { year: 2010, value: 319.8 }
  to: { year: 2024, value: 462.511 }
  source: https://www.bls.gov/cpi/research-series/r-cpi-u-rs-allitems.xlsx
  retrieved: 2026-10-25
---

# Definition

The percent change in each unit's median household income, from the ACS 2006–2010 5-year estimate (the start) to the ACS 2020–2024 5-year estimate (the end), with the start adjusted to 2024 dollars. The two periods don't overlap, as the Census Bureau requires for comparing 5-year estimates.

- **Universe:** households
- **Start:** the start Indicator's median, in 2010 inflation-adjusted dollars, adjusted to 2024 dollars
- **End:** the end Indicator's median, in 2024 inflation-adjusted dollars
- **Exclusions:** units where either median is blank

**Inflation:** the Census Bureau adjusts ACS dollar values with the R-CPI-U-RS, so the start is adjusted with the same index: the end year's annual average ÷ the start year's, both from BLS's current all-items table (`inflation`, above). The table stores the 2024 annual average unrounded (462.51116…); it's written to three decimals, like the table's monthly values.

# Computation

1. `start` = the start Indicator's value at this geography; `end` = the end Indicator's value. Each comes with its MOE and note.
2. Inflation factor = `inflation.to.value` ÷ `inflation.from.value`. `start` and its MOE are multiplied by it, so both values are in the end year's dollars.
3. `estimate` = (`end` ÷ `start` − 1) × 100.
4. `moe` is blank: the change has no MOE. `cv` and `reliability` are blank too.
5. If either value is blank, `estimate` and `moe` are blank, and `note` says which input is blank and why, with the input's period first, e.g. "2006–2010: no matching 2010 tract".
6. The table also has `start` (in the end year's dollars), `start_moe`, `end` and `end_moe`.

# Caveats

- **Not tested for statistical significance, and no MOE.** Both medians have large MOEs (in `start_moe` and `end_moe`), so many changes may be within sampling error.
- The 2010 values are adjusted with a national price index (R-CPI-U-RS), which doesn't reflect local prices.
- A change in a unit's median isn't a change in any household's income: households move in and out, and who lives there changes.
- Only units matched one to one between the two boundary vintages have a value. The match is by land area, not by where households are.
- The 2006–2010 estimates were controlled to the population estimates of the time, not to the 2010 census counts. The 2020–2024 period includes 2020, when ACS data collection was disrupted.
- Top- and bottom-coded inputs are blank, and the codes stand for different real incomes in each year.
