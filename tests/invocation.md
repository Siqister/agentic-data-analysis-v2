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
