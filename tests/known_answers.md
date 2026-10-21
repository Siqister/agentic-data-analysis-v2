# Known-Answer Tests

Each test checks one computed value against a trusted published value. The format and tolerance rules are in [validation.md](validation.md#2-known-answer-tests).

The expert will choose the "golden" indicators later.

## kat_001 — Total population, Cleveland city

```yaml
indicator: population_count
geography: cle_city
unit: "Cleveland"                # cle_city's id_field is NAME
expected: 366097
expected_moe: 76
tolerance: relative 2%
source: ACS 2020–2024 5-year, B01003_001, Cleveland city, Ohio (place 3916000) — https://data.census.gov/table/ACSDT5Y2024.B01003?g=160XX00US3916000 (accessed 2026-10-21)
```

Value retrieved by the agent from the Census Data API (`acs/acs5` 2024, `B01003_001E` and `_001M`, `for=place:16000&in=state:39`); confirmed by the expert 2026-10-21. Ours is the sum of whole block groups inside the City's own boundary, so a gap is expected from straddling block groups and from differences between the City's boundary and the Census place boundary. Tighten the tolerance once the actual gap is known.
