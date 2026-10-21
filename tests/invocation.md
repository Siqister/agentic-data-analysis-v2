# Invocation Tests

Each test gives the agent a plain-language prompt and checks how it responds. The format is in [validation.md](validation.md#3-invocation-tests).

## inv_001 — Unknown indicator

```yaml
prompt: "Show me median household income by block group."
expected: not_available
spec: null
```

No Indicator or Visualization covers median household income. The agent says it isn't available and lists the available Indicators and Visualizations. It creates, drafts, and fetches nothing: no new files in `specs/`, `pipeline/`, `data/`, or `outputs/`.
