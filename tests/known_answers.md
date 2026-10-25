# Known-Answer Tests

Each test checks one computed value against a trusted published value. The format and tolerance rules are in [validation.md](validation.md#2-known-answer-tests).

The expert will choose the "golden" indicators later.

## kat_001 — Total population, Cleveland city

```yaml
indicator: population_count_2024
geography: cle_city
unit: "Cleveland"                # cle_city's id_field is NAME
expected: 366097
expected_moe: 76
tolerance: relative 2%
source: ACS 2020–2024 5-year, B01003_001, Cleveland city, Ohio (place 3916000) — https://data.census.gov/table/ACSDT5Y2024.B01003?g=160XX00US3916000 (accessed 2026-10-21)
```

Value retrieved by the agent from the Census Data API (`acs/acs5` 2024, `B01003_001E` and `_001M`, `for=place:16000&in=state:39`); confirmed by the expert 2026-10-21. Ours is the sum of whole block groups inside the City's own boundary, so a gap is expected from straddling block groups and from differences between the City's boundary and the Census place boundary. Tighten the tolerance once the actual gap is known.

## kat_002 — Median household income, one block group

```yaml
indicator: median_household_income_2024
geography: bg_2020
unit: "390351198002"             # Block Group 2, Census Tract 1198.00, Cuyahoga County
expected: 42344
expected_moe: 13701
tolerance: exact
source: ACS 2020–2024 5-year, B19013_001, Block Group 2, Census Tract 1198, Cuyahoga County, Ohio — https://data.census.gov/table/ACSDT5Y2024.B19013?g=1500000US390351198002 (accessed 2026-10-24)
```

Value proposed by the agent from the Census Data API (`acs/acs5` 2024, `B19013_001E` and `_001M`), chosen as a block group near the middle of Cleveland's values with a published, uncoded estimate and MOE. Confirmed by the expert 2026-10-24. The value is passed through unchanged, so this tests fetching, the GEOID join and the output, not a method.


## kat_003 — Median household income 2006–2010, one matched 2020 tract

```yaml
indicator: median_household_income_tract_2010
geography: tract_2020
unit: "39035197400"              # Census Tract 1974 (2020), matched to 2010 Census Tract 1063 (39035106300)
expected: 36591
expected_moe: 5794
tolerance: exact
source: ACS 2006–2010 5-year, B19013_001, Census Tract 1063, Cuyahoga County, Ohio — https://data.census.gov/table/ACSDT5Y2010.B19013?g=1400000US39035106300 (accessed 2026-10-25)
```

Value proposed by the agent from the Census Data API (`acs/acs5` 2010, `B19013_001E` and `_001M`, tract `106300`). Awaiting the expert's confirmation. In the tract relationship file, the two tracts share 99.99% of the 2010 tract's land area and 83.1% of the 2020 tract's, so they match at `min_overlap` 0.80 but not at 0.90. It's the only matched pair inside the city whose GEOIDs differ, so this test covers the match, not only the fetch. At a `min_overlap` above 0.83 the tract is blank, and this test has to be replaced.

## kat_004 — Median household income 2020–2024, one tract

```yaml
indicator: median_household_income_tract_2024
geography: tract_2020
unit: "39035198500"              # Census Tract 1985, Cuyahoga County
expected: 38083
expected_moe: 13217
tolerance: exact
source: ACS 2020–2024 5-year, B19013_001, Census Tract 1985, Cuyahoga County, Ohio — https://data.census.gov/table/ACSDT5Y2024.B19013?g=1400000US39035198500 (accessed 2026-10-25)
```

Value proposed by the agent from the Census Data API (`acs/acs5` 2024, `B19013_001E` and `_001M`, tract `198500`), chosen as the tract nearest the middle of Cleveland's tract values with a published, uncoded estimate and MOE. Awaiting the expert's confirmation. The value is passed through unchanged, so this tests the tract fetch, the GEOID join and the output.

## kat_005 — Change in median household income, one matched tract

```yaml
indicator: median_household_income_tract_pct_change_2010_2024
geography: tract_2020
unit: "39035197400"              # Census Tract 1974 (2020), matched to 2010 Census Tract 1063; the kat_003 tract
expected: -17.02
tolerance: absolute 0.01
source: Computed by hand from median_household_income_tract_2010__tract_2020.csv (36591) and median_household_income_tract_2024__tract_2020.csv (43913), factor 462.511 ÷ 319.8 (2026-10-25)
```

**Not a trusted published value** (decision 12, chunk 4b; an accepted exception to [validation.md § 2](validation.md#2-known-answer-tests)). It checks the joins, the order of start and end, and the arithmetic, not the inflation factor: 43913 ÷ (36591 × 462.511 ÷ 319.8) − 1 = −17.0197%. The start comes through the matched crosswalk, so the test covers that path too. If `min_overlap` rises above 0.83, this tract has no value and the test must be replaced, like `kat_003`.

## kat_006 — Total population 2006–2010, one matched 2020 tract

```yaml
indicator: population_count_tract_2010
geography: tract_2020
unit: "39035197400"              # Census Tract 1974 (2020), matched to 2010 Census Tract 1063 (39035106300); the kat_003 tract
expected: 3809
expected_moe: 499
tolerance: exact
source: ACS 2006–2010 5-year, B01003_001, Census Tract 1063, Cuyahoga County, Ohio — https://data.census.gov/table/ACSDT5Y2010.B01003?g=1400000US39035106300 (accessed 2026-10-25)
```

Value proposed by the agent from the Census Data API (`acs/acs5` 2010, `B01003_001E` and `_001M`, tract `106300`). Awaiting the expert's confirmation. The first count through the `matched` crosswalk: the value and MOE are the 2010 tract's, copied unchanged. It's the only matched pair inside the city whose GEOIDs differ, so this test covers the match, not only the fetch. At a `min_overlap` above 0.83 the tract is blank, and this test has to be replaced, like `kat_003`.

## kat_007 — Change in total population, one matched tract

```yaml
indicator: population_count_tract_pct_change_2010_2024
geography: tract_2020
unit: "39035197400"              # Census Tract 1974 (2020), matched to 2010 Census Tract 1063; the kat_003 tract
expected: -0.11
tolerance: absolute 0.01
source: Computed by hand from the published counts, 3809 (ACS 2006–2010, tract 106300) and 3805 (ACS 2020–2024, tract 197400), from the Census Data API (2026-10-25); to be checked against population_count_tract_2010__tract_2020.csv and population_count_tract_2024__tract_2020.csv once built
```

**Not a trusted published value** (decision 5, chunk 5; an accepted exception to [validation.md § 2](validation.md#2-known-answer-tests), like `kat_005`). It checks the joins, the order of start and end, and the arithmetic with no inflation factor: 3805 ÷ 3809 − 1 = −0.1050%. Swapping start and end gives +0.1051%, outside the tolerance. The start comes through the matched crosswalk, so the test covers that path too. If `min_overlap` rises above 0.83, this tract has no value and the test must be replaced, like `kat_003`.
