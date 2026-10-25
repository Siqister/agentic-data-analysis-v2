# Validation

There are three kinds of checks:

1. **Spec validation**: are the specs well-formed and consistent with each other? Runs before anything is computed.
2. **Known-answer tests**: do our calculations reproduce numbers we already trust? Runs after Indicators are computed.
3. **Invocation tests**: does the agent respond to a prompt the way it should? Checked by giving the agent the prompt.

Other evaluation layers are deferred ([architecture.md § 13](../architecture.md#13-deferred)).

---

## 1. Spec validation

A small script, built during implementation, reads every spec in `specs/` and checks it against its template and against the other specs.

### Each spec

- [ ] Has frontmatter with `type` set to `Resource`, `Geography`, `Crosswalk`, `Indicator`, or `Visualization`, and sits in that type's folder.
- [ ] File name is unique across `specs/`.
- [ ] Has every field its template requires: `title`, a one-line `description`, `status`, plus the type's own fields. Fields marked *(optional)* may be missing.
- [ ] Fields with a fixed set of choices hold an allowed value: `status`, `method`, `weights`, `measure`, `unit`, `within_rule`, `census_unit`, `map`, `classification`, `reliability.low`.
- [ ] Contains no API key values. Only `.env` variable names are allowed.

### How specs fit together

- [ ] Every ID in a reference field ([architecture.md § 5](../architecture.md#5-the-dependency-graph)) exists and has the right type.
- [ ] The graph has no loops.
- [ ] **Geography:** `within` and `within_rule` are both present or both missing.
- [ ] **Crosswalk:** `population_weighted` has `weights` and `weights_source`. `matched` has `weights_source`, `min_overlap` (above 0.5, at most 1) and `fields` (`from_id`, `to_id`, `from_area`, `to_area`, `shared_area`), and no `weights`. Other methods have none of these.
- [ ] **Crosswalk:** `matched` has a `from` Geography with a `census_unit`, and a `weights_source` that is a file Resource (no `datasets`).
- [ ] **Crosswalk:** `nested` with a `from` Geography that has `within` requires that `within` equals `to`. (Other `nested` crosswalks are checked when they're built: every unit must fall in exactly one target.)
- [ ] **Indicator:** every listed crosswalk's `from` equals the Indicator's `geography`.
- [ ] **Indicator:** with Census data, its `geography` has a `census_unit`.
- [ ] **Indicator:** every `data` entry uses a dataset and vintage on its Resource's approved `datasets` list. An entry for a Resource with no `datasets` (a file) has no `dataset` or `vintage`.
- [ ] **Indicator:** a `points` measure has no `crosswalks`, `reliability` or `unit`, and has a `# Point rules` section. Only a `points` measure has a `window`.
- [ ] **Indicator:** `window` has `field`, `from` and `to`; `field` is one of its `data` fields; `from` and `to` are dates and `from` ≤ `to`.
- [ ] **Indicator:** a `median` or `index` measure that has crosswalks has an `# Aggregation` section.
- [ ] **Visualization:** `geography` is the Indicator's geography or the target of one of its crosswalks. With `manual` classification, `breaks` has `classes − 1` values in increasing order.
- [ ] **Visualization:** a `choropleth` (the default) has a non-`points` Indicator and no `hex_size_m`. A `hexbin` has a `points` Indicator, no `also_show`, and `hex_size_m` of at least 250 (the privacy floor, [architecture.md § 12](../architecture.md#privacy)).
- [ ] **Indexes:** each folder's `index.md` lists exactly the specs in that folder. `specs/index.md` declares `okf_version: "0.2"`.

### Data fields

**File Resources** (always; no network needed):

- [ ] Every field in an Indicator's `data` entry for a local file Resource exists in the file's layer (the geometry column counts as a field). A missing file is an error.
- [ ] Every column in a `matched` Crosswalk's `fields` exists in its `weights_source` file. For a file at a URL, this reads the snapshot; with no snapshot yet, it's a warning (it's checked when the crosswalk is built).

**Census** (author mode; needs network access, `--network`):

- [ ] Every field code in an Indicator's `data` exists in the source's own field list for that dataset and vintage (for Census, `variables.json`). Its official label is shown next to the spec's plain meaning so the expert can confirm they match.
- [ ] Every field is published at the Indicator's geography's `census_unit`: a sample request (one tract's block groups, or one county's tracts) doesn't return `null` for every unit.

### Code and status

- [ ] Every Indicator has compiled code in `pipeline/` whose header gives its spec, spec hash, and `generated` info.
- [ ] **Stale code:** the stored spec hash doesn't match the current spec. Listed along with everything above it in the graph.
- [ ] **Unreviewed code:** no `verified` line. Listed; it can't run in run mode.
- [ ] **Edited stable spec:** a `stable` spec whose content (anything but `status`) differs from the last commit. Warning: if the agent edited it, it goes back to `draft`.
- [ ] **Run-mode readiness:** lists anything a requested output depends on that is still `draft`, stale, or unreviewed.

### Known-answer tests

- [ ] Each test refers to an existing Indicator, and to a geography that Indicator is reported at.

### Report

Plain language, in two sections: **Errors** (must fix before anything runs) and **Warnings** (worth a look). Each line names the file and says what to fix, for example:
`specs/indicators/housing_cost_burden_pct.md — crosswalk "tract_2020__to__cle_city" starts from tract_2020, but this indicator is calculated at bg_2020.`

---

## 2. Known-answer tests

A known-answer test compares a value we computed with a **trusted published value**. If the pipeline reproduces numbers we already know are right, we can trust it more on numbers we don't.

Good sources include Census Bureau published figures for the City of Cleveland (a Census "place"), published figures for a few spot-check tracts, and other sources the expert trusts.

### Format

All tests live in [known_answers.md](known_answers.md), one section per test:

````markdown
## kat_001 — Housing cost burden, Cleveland city

```yaml
indicator: housing_cost_burden_pct
geography: cle_city
unit: "Cleveland"                # the unit's id_field value (text), e.g. NAME for cle_city, GEOID for Census units
expected: 0.000                  # published value (placeholder)
expected_moe: 0.000              # (optional) published margin of error
tolerance: within_moe            # exact | absolute 0.5 | relative 2% | within_moe
source: ACS 2019–2023 5-year, B25070 + B25091, Cleveland city — https://data.census.gov/... (accessed 2026-11-01)
```

Optional note, e.g. "Ours is aggregated from block groups, so a small gap is expected."
````

The heading gives the test ID (`kat_001`, `kat_002`, …). The YAML block is the contract: `lib/known_answers.py` reads only that. The prose under it is for people.

### Tolerance

Results rarely match exactly: published figures are rounded, and we aggregate from smaller units. Every test states how close counts as a pass.

| Tolerance | Passes when | Use for |
|---|---|---|
| `exact` | Equal once rounded to the published precision | Values computed the same way as the source |
| `absolute N` | Difference ≤ N, e.g. `absolute 0.5` percentage points | Percentages |
| `relative N%` | Difference ≤ N% of the expected value | Counts and dollar values |
| `within_moe` | Difference ≤ √(our MOE² + published MOE²) | Our aggregate compared with a published ACS figure |

### When tests run and what failure means

- Tests run after any Indicator is computed or recomputed, and before dependent outputs are delivered.
- A failure **blocks delivery** of every output that depends on that Indicator. The report shows expected, actual, difference, and tolerance.
- The expert decides: fix the spec or code, or accept the difference. An accepted difference is noted under the test and recorded in affected manifests.

---

## 3. Invocation tests

An invocation test checks how the agent responds to a plain-language prompt ([architecture.md § 2](../architecture.md#invocation)): whether it maps the prompt to the right spec, asks when the prompt is ambiguous, and refuses to improvise when nothing matches. Unlike known-answer tests, they test the agent's behavior, not a number.

### Format

All tests live in [invocation.md](invocation.md), one section per test:

````markdown
## inv_001 — Unknown indicator

```yaml
prompt: "Show me median household income by block group."
expected: not_available          # runs | asks | not_available
spec: null                       # (runs only) the spec ID the prompt should resolve to
```

What the agent should do, in plain language, including what it must not do.
````

The heading gives the test ID (`inv_001`, `inv_002`, …).

| `expected` | Passes when the agent |
|---|---|
| `runs` | Resolves the prompt to `spec` and runs it through the runner |
| `asks` | Asks which spec is meant, and runs nothing until answered |
| `not_available` | Says the item isn't available and lists the available Indicators and Visualizations; creates, drafts, and fetches nothing (no new files in `specs/`, `pipeline/`, `data/`, or `outputs/`) |

### When they run

In author mode, when the runner, the agent's instructions, or the set of specs changes, and at least once per chunk. Each test starts from the **plain prompt, in a fresh agent session**: calling `lib.runner` directly tests the runner, not the agent. The expert (or a check of the working tree) confirms the behavior. A failure is a bug in the agent's instructions or the runner, not in an Indicator.
