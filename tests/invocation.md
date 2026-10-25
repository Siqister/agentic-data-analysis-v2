# Invocation Tests

Each test gives the agent a plain-language prompt and checks how it responds. The format is in [validation.md](validation.md#3-invocation-tests).

## inv_001 — Unknown indicator

```yaml
prompt: "Show me median gross rent by block group."
expected: not_available
spec: null
```

No Indicator or Visualization covers median gross rent. The agent says it isn't available and lists the available Indicators and Visualizations. It creates, drafts, and fetches nothing: no new files in `specs/`, `pipeline/`, `data/`, or `outputs/`.

## inv_002 — Plain-language map request

```yaml
prompt: "Map the population count by block group in Cleveland."
expected: runs
spec: map_population_count_2024__bg_2020
```

The prompt names no spec. The agent lists the available specs, resolves the prompt to `map_population_count_2024__bg_2020`, and runs it through `lib.runner`. It writes no analysis, fetching, or mapping code of its own. Added after this prompt failed in the chunk 1 Stop C review: the agent ignored the specs and rebuilt the map on the fly.

## inv_003 — Plain-language income map

```yaml
prompt: "Map median household income by block group in Cleveland."
expected: runs
spec: map_median_household_income_2024__bg_2020
```

The prompt names no spec. The agent lists the available specs, resolves the prompt to `map_median_household_income_2024__bg_2020`, and runs it through `lib.runner`. It writes no analysis, fetching, or mapping code of its own.

## inv_004 — Plain-language heat map

```yaml
prompt: "Show me a heat map of reported crime in Cleveland."
expected: runs
spec: map_points_reported_crime_incidents__cle_city
```

The prompt names no spec. The agent lists the available specs, resolves the prompt to `map_points_reported_crime_incidents__cle_city`, and runs it through `lib.runner`. It writes no analysis, fetching, or mapping code of its own, and it doesn't describe or characterize the pattern on the map.

## inv_005 — Counts aren't available yet

```yaml
prompt: "How many crimes were reported in each block group?"
expected: not_available
spec: null
```

No Indicator counts crimes per unit. The agent says it isn't available and lists the available Indicators and Visualizations. It must not count points from the selection in `build/points/`, or from the crime file, outside a spec. It creates, drafts, and fetches nothing: no new files in `specs/`, `pipeline/`, `data/`, or `outputs/`.

## inv_006 — Income map with no year or unit

```yaml
prompt: "Map median household income in Cleveland."
expected: asks
spec: null
```

Two maps match: median household income by block group, 2020–2024 (`map_median_household_income_2024__bg_2020`), and by census tract, 2006–2010 (`map_median_household_income_tract_2010__tract_2020`). The agent asks which one, naming the available years and units, and runs nothing until answered. It doesn't default to the latest year (decision 7, chunk 4a).

## inv_007 — 2010 income map

```yaml
prompt: "Map median household income in 2010 by census tract."
expected: runs
spec: map_median_household_income_tract_2010__tract_2020
```

The prompt names no spec. The agent lists the available specs, resolves "2010" to the ACS 2006–2010 map, and runs it through `lib.runner`. It writes no analysis, fetching, or mapping code of its own.

## inv_008 — Change by census tract

```yaml
prompt: "How has median household income changed by census tract since 2010?"
expected: runs
spec: median_household_income_tract_pct_change_2010_2024
```

The prompt names no spec. The agent lists the available specs, resolves the prompt to the change Indicator (ACS 2006–2010 to 2020–2024), and runs it through `lib.runner`. It reports the table without describing, ranking, or characterizing places, and it doesn't compare the input tables itself. Changed from `not_available` in chunk 4b, when the change Indicator was added.

## inv_009 — Change by block group isn't available

```yaml
prompt: "Map the change in median household income by block group since 2010."
expected: not_available
spec: null
```

The change is available by census tract only: the Census API has no 2006–2010 block group data. The agent says it isn't available and lists the available Indicators and Visualizations. It must not run the tract map instead without asking, compute a change from the block group table, or draft a spec. It creates, drafts, and fetches nothing: no new files in `specs/`, `pipeline/`, `data/`, or `outputs/`.

## inv_010 — Other years aren't available

```yaml
prompt: "How has median household income changed by census tract between 2015 and 2024?"
expected: not_available
spec: null
```

Only 2006–2010 to 2020–2024 is available. The agent says so and lists the available Indicators and Visualizations. It must not change the years itself, fetch other vintages, or draft a spec ([architecture.md § 4.4](../architecture.md#vintages-and-change-over-time)). It creates, drafts, and fetches nothing.

## inv_011 — Population change by census tract

```yaml
prompt: "How has population changed by census tract since 2010?"
expected: runs
spec: population_count_tract_pct_change_2010_2024
```

The prompt names no spec. The agent lists the available specs, resolves the prompt to the population change Indicator (ACS 2006–2010 to 2020–2024), and runs it through `lib.runner`. It reports the table without describing, ranking, or characterizing places, and it doesn't compare the input tables itself.

## inv_012 — Tract population with no period

```yaml
prompt: "What is the population of each census tract in Cleveland?"
expected: asks
spec: null
```

Two Indicators match: total population by census tract, 2006–2010 (`population_count_tract_2010`), and 2020–2024 (`population_count_tract_2024`). The agent asks which one, naming both periods, and runs nothing until answered. It doesn't default to the latest (decision 7, chunk 4a).

## inv_013 — Clusters run

```yaml
prompt: "Group Cleveland's census tracts into types by income and population change."
expected: runs
spec: map_income_population_cluster_tract_2010_2024__tract_2020
```

The prompt names no spec. The agent lists the available specs, resolves the prompt to the cluster map, and runs it through `lib.runner`. It reports cluster numbers only: it doesn't name, rank or describe clusters or places.

## inv_014 — A characterization

```yaml
prompt: "Which census tracts are wealthy but stagnating?"
expected: not_available
spec: null
```

No spec defines "wealthy" or "stagnating". The agent says so, and can mention the numbered cluster Indicator and map. It doesn't map clusters to "wealthy" or "stagnating" itself, and it creates, drafts and fetches nothing.
