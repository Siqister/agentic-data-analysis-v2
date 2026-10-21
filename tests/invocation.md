# Invocation Tests

Each test gives the agent a plain-language prompt and checks how it responds. The format is in [validation.md](validation.md#3-invocation-tests).

## inv_001 — Unknown indicator

```yaml
prompt: "Show me median household income by block group."
expected: not_available
spec: null
```

No Indicator or Visualization covers median household income. The agent says it isn't available and lists the available Indicators and Visualizations. It creates, drafts, and fetches nothing: no new files in `specs/`, `pipeline/`, `data/`, or `outputs/`.

## inv_002 — Plain-language map request

```yaml
prompt: "Map the population count by block group in Cleveland."
expected: runs
spec: map_population_count__bg_2020
```

The prompt names no spec. The agent lists the available specs, resolves the prompt to `map_population_count__bg_2020`, and runs it through `lib.runner`. It writes no analysis, fetching, or mapping code of its own. Added after this prompt failed in the chunk 1 Stop C review: the agent ignored the specs and rebuilt the map on the fly.
