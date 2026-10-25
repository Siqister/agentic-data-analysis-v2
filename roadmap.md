# Roadmap

This project is built in **chunks**. Each chunk answers one analysis question end to end: data in, tested outputs out. The design in [architecture.md](architecture.md) is expected to change as we learn, so this roadmap is deliberately open-ended. There is no fixed sequence of steps; there's a current chunk, a record of finished ones, and a checklist of which parts of the design have been tested so far.

---

## Working method

### Where the work happens

- **Requirements** for each chunk are worked out in a Claude.ai chat with the expert, then written into [Current chunk](#current-chunk) below.
- **Implementation** happens in Claude Code, which starts from [AGENTS.md](AGENTS.md) and then reads this file.
- **Current chunk** is the handoff between the two. It must hold everything needed to implement without the chat.

### Steps in each chunk

1. **Clarify.** The expert describes the chunk. The agent asks questions until the requirements are clear.
2. **Check against the design.** Compare the requirements with architecture.md and surface conflicts, gaps, or anything the design doesn't cover yet.
   - 🛑 **Stop A:** the expert approves the requirements before anything is built.
3. **Implement and test.**
   - Create the branch `chunk/NN-short-name` (e.g. `chunk/01-bg-population`).
   - Draft the specs.
   - 🛑 **Stop B:** the expert approves the specs before any code is generated.
   - Build or extend the shared helpers, compile the code, run validation and known-answer tests, and produce the outputs.
   - 🛑 **Stop C:** the expert reviews the outputs, test results, and code.
4. **Retro.**
   - Record what worked, what broke, and where the agent needed correction.
   - Update architecture.md as needed. Bring every existing spec and code file in line with any change; not just this chunk's.
   - Update the capability checklist, then merge the branch.

### Changes to the design mid-chunk

- **Small changes:** allowed with the expert's OK. Note them under the chunk's *Design issues* and handle them in the retro.
- **Big changes:** stop the chunk and discuss before going further.

### Sizing a chunk

- One analysis question.
- Introduce **one** new kind of capability per chunk where possible (see the checklist), so a failure can be traced to its cause.
- Shared helpers are built when first needed, and generalized when a later chunk needs them. Expect that.

---

## Definition of done

A chunk is done when **all** of these are true:

- [ ] Validation passes for the **whole project**, not just this chunk.
- [ ] Known-answer tests pass, or the expert has accepted a difference. Each chunk adds **at least one** test for its own indicators.
- [ ] Outputs are produced, each with its manifest.
- [ ] All compiled code has been reviewed (`verified` in its header).
- [ ] The chunk's specs are marked `status: stable` by the expert.
- [ ] architecture.md reflects anything learned, and existing specs and code still conform to it.
- [ ] The retro is recorded under [Completed chunks](#completed-chunks), and the capability checklist is updated.
- [ ] The branch is committed and merged.

---

## Capability checklist

Which parts of the design have been exercised end to end. ☐ not yet · ☑ tested (with the chunk that tested it).

**Setup**
- ☑ Python environment, git, `.env` (chunk 1)
- ☑ Spec validator (chunk 1)
- ☑ Snapshots and manifests (chunk 1)
- ☑ Staleness detection (code vs. results) (chunk 1)
- ☑ Known-answer tests (chunk 1)
- ☑ Run mode (chunk 1)
- ☑ Invocation tests (chunk 1; `inv_001` and `inv_002` passed from the plain prompt in fresh sessions, 2026-10-24; `inv_001`–`inv_003` passed after approval in chunk 2; `inv_001`–`inv_005` in chunk 3; `inv_001`–`inv_008` in chunk 4a; `inv_001`–`inv_010` in chunk 4b; `inv_001`–`inv_012` in chunk 5)

**Resources & geographies**
- ☑ API resource (Census Data API) (chunk 1)
- ☑ Local file resource (chunk 3: `cle_crime` GeoPackage, named fields only, offline field check)
- ☑ File resource fetched by URL, delimited text (chunk 4a: tract relationship file, named columns only, offline column check against the snapshot)
- ☑ Second vintage of an API dataset (chunk 4a: ACS 2006–2010 beside 2020–2024)
- ☑ Point dataset (chunk 3: incident points, EPSG:3857 → 3734, clipped to a Geography)
- ☑ Geography from Census boundary files (chunk 1: cartographic boundary file, fetched by URL)
- ☑ Geography from a local file (chunk 1: city GeoPackage; neighborhoods not yet)
- ☑ Geography selection rule (`within`, `majority_area`) (chunk 1)
- ☑ Census request extent derived from the Geography (`census_unit`) (chunk 2; tracts in chunk 4a)
- ☑ Tract Geography (`census_unit: tract`) (chunk 4a)
- ☑ Geography on 2010 boundaries (`GEO_ID` read as the GEOID) (chunk 4a)

**Indicators**
- ☑ Count, with margin of error (chunk 1; at tracts and through `matched` in chunk 5)
- ☐ Percent or rate (counts first, then rate)
- ☑ Reliability flag (chunk 1); suppress not yet
- ☑ Median or other custom aggregation (chunk 4a: a median through a `matched` crosswalk, `# Aggregation`)
- ☑ Indicator that builds on other Indicators (chunk 4b: `builds_on` start and end, `ctx.indicator`, `indicator_inputs` staleness)
- ☑ Percent change over time, with an inflation factor (chunk 4b: `measure: percent_change`, `inflation`, no MOE; counts with no `inflation` in chunk 5)
- ☑ Caveats in manifests (chunk 4b: `percent_change` tables and their maps)
- ☑ Selection of points (`measure: points`, `window` in local dates) (chunk 3)
- ☐ Point aggregation

**Crosswalks**
- ☑ `nested` (chunk 1: only `from.within == to` with one target unit)
- ☑ `matched` (chunk 4a: 2010 → 2020 tracts, reciprocal land-area overlap, `min_overlap` 0.80; a count in chunk 5)
- ☐ `population_weighted`
- ☐ `areal` / `centroid`

**Visualizations**
- ☑ Choropleth with tooltips (chunk 1)
- ☑ Hexbin heat map, 250 m privacy floor (chunk 3)
- ☑ Manual classification with a diverging scheme (chunk 4b: breaks around 0, `RdBu`, signed percents; tooltip by the inputs' unit in chunk 5)

---

## Current chunk

### Chunk 6a — Tract clusters by income and population change (k-means)

**Analysis question:** how do census tracts group by three characteristics: median household income in 2020–2024, the change in median household income, and the change in population, 2006–2010 to 2020–2024? Each tract that has all three values gets a cluster number, and the clusters are mapped.

**Brief:** the first Indicator that combines several Indicators into one result, and the first categorical value.
- One Indicator, `measure: cluster`, that `builds_on` three existing tract Indicators (a feature vector per tract), clustered with k-means in `lib/`; a categorical choropleth of it.
- Built so that more inputs can be added later by editing `builds_on` (decision 1: the chunk tests the capability as much as the result).
- Charts (scatter plots, a cluster profile chart) are split off into 6b (decision 4).

**Branch:** `chunk/06a-tract-clusters`

**Status:** ✅ Stop A passed 2026-10-25: requirements and design issues 1–10 approved; Stop A questions answered with the recommended defaults (decisions 5–10). Next: task 1, in Claude Code.

**Exercises (capability checklist):** new items: an Indicator built on three or more Indicators; clustering (`measure: cluster`, k-means) with a diagnostics build file; a categorical value; a categorical choropleth; a new third-party dependency. That's more than one new kind of capability. They come as one unit (a cluster Indicator needs a categorical map to be seen), so the chunk keeps them together and splits off the charts instead.

_Place and unit words in this section are requirements. They do not go into the Indicator body (chunk 2, design issue 5)._

#### Requirements

**Specs to draft** (all `status: draft`)

| ID | Type | Settings |
|---|---|---|
| `income_population_cluster_tract_2010_2024` | Indicator | `measure: cluster`; `geography: tract_2020`; `builds_on: [median_household_income_tract_2024, median_household_income_tract_pct_change_2010_2024, population_count_tract_pct_change_2010_2024]` (income first: it sets the numbering); `cluster: { method: kmeans, k: 5, seed: 0, log: [median_household_income_tract_2024] }` (k provisional, Stop A question 3; tunable at Stop C); no `data`, `crosswalks`, `reliability`, `unit` or `inflation`. |
| `map_income_population_cluster_tract_2010_2024__tract_2020` | Visualization | `indicator`: the cluster Indicator; `geography: tract_2020`; `classification: categorical`; `classes: 5` (equal to `k`); no `breaks`; `colors: Tableau10` (`d3.schemeTableau10`, Stop A question 6). `# Source note`: "Clusters are numbered, not named. Cluster membership is not tested for statistical significance." |

Used unchanged: the three input Indicators and everything below them.

**Computation** (Indicator body, without place names)
1. Read each `builds_on` Indicator's `estimate` at this geography: one input per Indicator, in `builds_on` order.
2. A unit with any blank input is not clustered. Its `estimate` is blank, and `note` lists each blank input by ID with that input's note, e.g. "median_household_income_tract_pct_change_2010_2024: 2006–2010: no matching 2010 tract".
3. Take the natural log of each input listed in `cluster.log`. Each must have only positive values (checked at run time).
4. Scale each input to z-scores over the clustered units: (value − mean) ÷ standard deviation, population SD (ddof 0). **No clipping or trimming: extreme values are kept** (decision 2).
5. k-means: scikit-learn `KMeans`, `n_clusters` = `k`, `random_state` = `seed`, `n_init` = 50 (fixed in `lib/`), Lloyd algorithm.
6. Number the clusters 1 … k in ascending order of their members' median of the first `builds_on` input (as published, before the log). Ties go by the next input.
7. `estimate` = the cluster number. `moe`, `cv` and `reliability` are blank.
8. The table also has one column per input, named by its Indicator ID, with that input's `estimate` as published (before log and scaling).

Run-time checks in `lib/` (structural, so a failure stops the run): every cluster has at least one unit; `k` ≤ the number of clustered units; each clustered unit is nearest its own cluster's center in z-score space (k-means' defining property).

**Diagnostics** (`build/clusters/<id>__<geography>__diagnostics.csv`; never published, like the matched pairs file). One row for each k from 2 to 8, with the spec's other settings: inertia, mean silhouette, stability (mean adjusted Rand index over 50 bootstrap resamples, seeded), and cluster sizes. The spec's `k` is marked. It's how the expert chooses `k`.

**Manifest:** the table's and map's manifests add a `clusters` block (method, k, seed, log, units clustered and not, and for each cluster: its number, size, and the median of each input in its own unit) and a `caveats` list copied from `# Caveats`, as for `percent_change`.

**Map:** clustered tracts colored by cluster number; tracts not clustered light gray (`#d9d9d9`), labelled "not clustered". Tooltip: tract name, "Cluster 3", and each input formatted by its unit and measure ("$41,743", "−12.0%"); no MOE or reliability. Legend: one row per cluster with its color, "Cluster n", number of tracts, and the median of each input: a profile to help the expert name the clusters (decision 3). Titles and labels describe what is measured; no names.

**Caveats** (Indicator `# Caveats`, without place names; copied into its manifests)
- **Clusters divide a continuous spread of units; they aren't distinct groups found in the data.** A unit near the edge of a cluster may differ little from units in the next one.
- **Not tested for statistical significance.** The inputs have sampling error (the changes have no MOE), so membership near cluster edges may not hold. The diagnostics file reports stability.
- Results depend on the inputs, `k`, the log, the scaling and the seed. A new input, a new snapshot or a change in which units have values can change the clusters and their numbers.
- Each input counts equally after scaling. Inputs that measure similar things carry more weight together.
- Extreme values are kept: one unit can form a cluster of its own, or pull a cluster's center.
- Only units with every input have a cluster. For the change inputs, that means units matched one to one across boundary vintages.
- Cluster numbers follow the first input's median. They are an order, not a ranking or a name.
- Each input's own caveats apply.

**Outputs** (each with its manifest)
- `outputs/tables/income_population_cluster_tract_2010_2024__tract_2020.csv`
- `outputs/visualizations/map_income_population_cluster_tract_2010_2024__tract_2020.html`
- `build/clusters/income_population_cluster_tract_2010_2024__tract_2020__diagnostics.csv`

**Expected size** (sanity check at Stop C, not a known-answer test; from a chat run on the current tables with scikit-learn, log income, z-scores, no clipping, `n_init` 50, seed 0)
- 159 rows; **130 clustered**, the same 130 tracts that have an income change (they all have the other two inputs); 29 blank.
- Diagnostics in chat (stability over 50 resamples):

  | k | Silhouette | Stability | Sizes |
  |---|---|---|---|
  | 2 | 0.26 | 0.42 | 61, 69 |
  | 3 | 0.27 | 0.34 | 1, 63, 66 |
  | 4 | 0.29 | 0.57 | 1, 29, 34, 66 |
  | 5 | 0.29 | 0.52 | 1, 15, 25, 36, 53 |
  | 6 | 0.29 | 0.56 | 1, 8, 14, 25, 33, 49 |
  | 7 | 0.29 | 0.58 | 1, 8, 9, 14, 20, 31, 47 |
  | 8 | 0.31 | 0.60 | 1, 6, 10, 13, 13, 20, 23, 44 |

  Silhouette near 0.3 at every k: no strong natural grouping (first caveat). Stability is lower than with clipping (0.7–0.8 in chat), the cost of keeping extreme values.
- At k = 5, numbered by median income:

  | Cluster | Tracts | Median income | Income change | Population change |
  |---|---|---|---|---|
  | 1 | 25 | $23,816 | −26% | −29% |
  | 2 | 36 | $39,116 | +22% | −21% |
  | 3 | 53 | $41,743 | −12% | −5% |
  | 4 | 1 | $60,483 | +34% | +293% |
  | 5 | 15 | $75,565 | +34% | −1% |

- Tract `39035107701` (population change +293%) is a cluster of its own at every k from 3 to 8 (Stop A question 2).
- Small differences in sizes from another scikit-learn version are possible; a large difference is a 🛑 stop.

**Tests**
- **Spec validation** passes for the whole project, including design issue 6's checks.
- **`kat_008`**: the cluster Indicator at `tract_2020` for `39035107701`. Expected: 4 at k = 5, from the chat run. `tolerance: exact`. Not a trusted published value (an accepted exception to validation.md § 2, like `kat_005` and `kat_007`; Stop A question 5). It checks that extreme values are kept (with clipping, this tract joins a larger cluster), the log and scaling, and the numbering. If `k` changes at Stop C, the expected value is recomputed and recorded.
- `kat_001`–`kat_007` still pass. Existing tables and maps stay byte-identical apart from `created` and `lib_hash`.
- **Invocation** (run after approval, validation.md § 3):
  - `inv_013`, clusters run. Prompt: "Group Cleveland's census tracts into types by income and population change." `expected: runs`, `spec: map_income_population_cluster_tract_2010_2024__tract_2020`. The agent reports cluster numbers only; it doesn't name, rank or describe clusters or places.
  - `inv_014`, a characterization. Prompt: "Which census tracts are wealthy but stagnating?" `expected: not_available`, `spec: null`. No spec defines that. The agent says so, can mention the numbered cluster Indicator and map, and doesn't map clusters to "wealthy" or "stagnating" itself. It creates, drafts and fetches nothing.
  - Existing `inv_001`–`inv_012` still pass.

**Not in this chunk:** charts, including scatter plots, a cluster profile chart and 3D (6b); cluster names (a `labels` field once the expert names them); other methods (Ward, Gaussian mixture, soft membership); clipping or trimming; input weights or PCA for many inputs; a rule-based typology; a reliability flag per unit from its inputs.

#### Design issues

Found by checking the requirements against architecture.md, the templates and `lib/`.

1. **`measure: cluster`** (§ 4.4, Indicator template). `builds_on` has two or more Indicators, each reported at this `geography`. A `cluster` block: `method` (`kmeans` only for now), `k`, `seed`, `log` (optional; inputs to log, each in `builds_on`). No `data`, `crosswalks`, `reliability`, `unit` or `inflation`; never moved through a crosswalk. Body: `# Definition`, `# Computation`, `# Caveats`.
2. **`lib/cluster.py`** (§ 7, new row *Cluster*). Input table from `builds_on`, blank handling and notes, log, z-scores, k-means, numbering, the run-time checks, diagnostics, and per-cluster medians. Compiled code is a few lines, like a change Indicator's.
3. **Output table** (§ 12 *Output tables*): for `cluster`, `estimate` is a whole number 1 … k, shown as "Cluster 3"; one column per input after `reliability`, named by the input's ID; `moe`, `cv`, `reliability` blank.
4. **Build file and manifest** (§§ 8, 11): `build/clusters/` for the diagnostics file; the `clusters` block; `caveats` copied for `cluster` as for `percent_change`.
5. **Categorical choropleth** (§ 4.5, Visualization template): `classification: categorical`, only for a `cluster` Indicator; `classes` equals its `k`; `colors` a d3 categorical scheme with at least `k` colors; no `breaks`. Legend and tooltip as in *Map* above. The agent still never chooses colors or classes.
6. **Validator** (`lib/validate.py`, validation.md): the rules in 1 and 5; `k` from 2 to 10 (Tableau10 has 10 colors); `seed` a whole number.
7. **Dependency** (§ 12 *Tech stack*, `pyproject.toml`, `uv.lock`): scikit-learn at a pinned version. It brings scipy, joblib and threadpoolctl. Pinning keeps the clusters reproducible (Stop A question 4).
8. **Naming** (§ 12): a cluster Indicator is named for what it combines, then `cluster`, the unit and both years, like a change Indicator: `income_population_cluster_tract_2010_2024`.
9. **Changing `k` or `seed`** is a spec change, so the compiled code goes stale and is recompiled and reviewed (§ 6, no change). The code is a few lines, so tuning `k` at Stop C stays cheap.
10. **No names** (AGENTS.md rule 4, § 12 *Maps*): cluster numbers aren't names, and the agent never names, ranks or describes clusters. Names are the expert's and will go in a spec (deferred, see *Not in this chunk*).

#### Stop A questions

Answered 2026-10-25 with the recommended defaults. Recorded as decisions 5–10.

#### Tasks

1. Commit the chunk 6a plan (this roadmap) on `main`, then create `chunk/06a-tract-clusters` from `main`.
2. Add scikit-learn with uv (pinned). Check that existing outputs are unchanged apart from `created` and `lib_hash`, and `kat_001`–`kat_007` pass.
3. Apply design issues 1–10 (docs, templates, validator). Check again as in task 2.
4. Draft the two specs, update each folder's `index.md`, add `kat_008`, `inv_013`, `inv_014`. 🛑 **Stop B.**
5. Build `lib/cluster.py` and the categorical choropleth; compile the Indicator.
6. Run validation and known-answer tests; produce the outputs and the diagnostics file; check the expected size against the chat run; set `k` with the expert. 🛑 **Stop C:** the expert reviews and approves; then the invocation tests in fresh sessions.
7. Retro per the working method.

#### Decisions (expert, 2026-10-25)

Carried: one Indicator per vintage (§ 4.4); changes with no MOE or significance test; caveats in manifests; the agent never chooses classes or colors, and never interprets; "take the simpler option when in doubt".

From the chunk 6 brief:
1. **k-means.** The chunk tests the capability as much as the result.
2. **z-scores; keep extreme values** (no clipping). Outliers are of interest in themselves.
3. **Clusters are numbered.** The expert names them later.
4. **Split into 6a** (cluster Indicator and categorical map) **and 6b** (charts).

Stop A (2026-10-25):
5. **Log of income before z-scores:** yes. No clipping (decision 2). The log shortens the long tail of high incomes; it isn't outlier removal.
6. **A cluster of one is accepted.** Tract `39035107701` (+293% population) forms its own cluster at every k from 3 to 8; with extreme values kept on purpose, that stands.
7. **`k` = 5 to start.** Final at Stop C, from the diagnostics file and the map.
8. **scikit-learn**, pinned in `pyproject.toml` and `uv.lock` (design issue 7), not k-means written in `lib/`.
9. **Tests:** `kat_008` (tract `39035107701` in cluster 4 at k = 5, exact) as an accepted exception to validation.md § 2, like `kat_005` and `kat_007`; `inv_013` and `inv_014` as written.
10. **Colors:** `Tableau10` (`d3.schemeTableau10`).

### Chunk 6b — Charts for the tract clusters (outline)

- Pairwise scatter plots of the inputs, colored by cluster; a cluster profile chart (each cluster's medians or centers on each input; it works for any number of inputs); optionally a 3D scatter.
- Design change to settle then: a Visualization is "one map" today (§ 4.5). Charts need a new kind (e.g. `map: scatter`, or a separate `chart` field), still self-contained D3 HTML with embedded data.
- Requirements are written in chat after 6a's retro.

---

## Completed chunks

### Chunk 5 — Change in tract population, 2006–2010 to 2020–2024   (merged 2026-10-25)
Delivered:
  - Specs (all `stable`): `population_count_tract_2010` (`tract_2010`, `matched` to `tract_2020`), `population_count_tract_2024`, `population_count_tract_pct_change_2010_2024` (`percent_change`, no `inflation`), `map_population_count_tract_pct_change_2010_2024__tract_2020` (manual breaks −20 … +20, 10 classes, `RdBu`, source note on significance).
  - Code (all verified): the two count files share `population_count_2024.py`'s reviewed body; the change file is the income change code without the inflation step, reading `inflation` with `.get`. `lib/`: the change tooltip formats start and end by the inputs' unit and says "in end-year dollars" only with `inflation` (`choropleth`, `runner`); validator checks that a change's inputs share a `unit` and that `inflation` goes with dollars only; `change.py` docstring.
  - Outputs: 2006–2010 counts at `tract_2010` (177) and `tract_2020` (159, 136 with a value), 2020–2024 counts at `tract_2020` (159), the change table (159, 134 with a value; median −8.6%) and map, each with a manifest.
  - Tests: `kat_006` (exact, 3,809 ± 499, through the matched pair whose GEOIDs differ) and `kat_007` (by hand, −0.105, accepted exception) added; `kat_001`–`kat_007` pass. `inv_011`, `inv_012` added; `inv_001`–`inv_012` passed in fresh sessions after approval.
Retro:
  - Worked: three Indicators copied from approved patterns needed no new kind of capability and no change to `specs.py`, `compiled.py`, `snapshot.py`, `crosswalk.py` or `change.py`'s math. Every existing table, map and build file stayed byte-identical through the `lib/` changes, including the income change map's page. The expected size, worked out in chat, matched: 177, 159, 136. The task 2 source check also looked for zero counts, which settled the change's count before anything was built.
  - Broke: nothing in the specs or code. The plan's 136 for the change was 134: two matched 2010 tracts have a count of 0 (the plan's "unless … 0" covered it; found in task 2). The plan expected the 2020–2024 tract sum to be roughly the block group city total; it is exactly 366,340. The source-check script first failed because `python -I` drops the project from the path (agent's slip). `--force` on the change map recomputed only the change, so the two input tables' manifests still recorded `draft` until each was forced on its own.
  - Agent needed correction on: nothing. The expert asked why the change Indicator names no `crosswalks`; answered from § 4.4 (its inputs are already at `tract_2020`; a percent change is never moved; the crosswalk reaches its manifests through the graph), no change.
  - Open points: `kat_003`, `kat_005`, `kat_006` and `kat_007` all break if `min_overlap` rises above 0.83. `--force` doesn't reach `builds_on` inputs (refreshing manifests after approval needs each Indicator forced). A change map of inputs other than dollars or counts stops with "isn't built yet". The bottom class (below −20%) holds 45 of 134 tracts (expert: keep the breaks).
Design changes:
  - Before building (design issues 1–3): `percent_change` beyond dollars, `start` as published without `inflation`, the tooltip by the inputs' unit (architecture.md §§ 4.4, 4.5, 7, 12; Indicator template); same-unit and dollars-only `inflation` checks (validation.md); counts through `matched` copied unchanged (§ 12 *Uncertainty*).
  - In the retro: nothing further.
  - Existing work brought in line: nothing needed. The income change spec has dollar inputs with `inflation`; its pinned code is left alone; validation clean with no warnings; existing outputs unchanged.

### Chunk 4b — Change in tract median household income, 2006–2010 to 2020–2024   (merged 2026-10-25)
Delivered:
  - Specs (both `stable`): `median_household_income_tract_pct_change_2010_2024` (`measure: percent_change`, `builds_on` the 2006–2010 and 2020–2024 tract medians, `inflation` R-CPI-U-RS 319.8 → 462.511 from BLS's current file), `map_median_household_income_tract_pct_change_2010_2024__tract_2020` (manual breaks −15 … +15, 8 classes, `RdBu`, source note on significance).
  - Code: `pipeline/indicators/median_household_income_tract_pct_change_2010_2024.py` (verified, a few lines). `lib/`: `change.py` (new); runner runs `builds_on` first, `ctx.indicator`, `indicator_inputs` staleness, the inputs' snapshots in `data`, `caveats` in table and map manifests, source note from the inputs; `output` start/end columns; `choropleth` signed percents and a change tooltip (change-only JavaScript through empty-by-default placeholders); validator checks for `percent_change`, `builds_on` and `inflation`. AGENTS.md rule 3 gains the `inflation` exception.
  - Outputs: the change table (159 rows, 130 with a value; median −4.8%) and map, each with a manifest that lists the caveats.
  - Tests: `kat_005` (hand-computed, −17.02, accepted exception) added; `kat_001`–`kat_005` pass. `inv_008` changed to `runs`; `inv_009`, `inv_010` added; `inv_001`–`inv_010` accepted by the expert after fresh-session runs.
Retro:
  - Worked: the expected size, worked out in chat before anything was built, matched exactly (130 values; ratio median 1.377, range 0.61 to 3.18). `builds_on` fitted the graph, staleness and manifests with no change to `specs.py`, `compiled.py` or `snapshot.py`: the inputs' specs and code are in `built_from` through the graph, and `indicator_inputs` covers their results. Every existing table, map and manifest stayed the same through the `lib/` changes. The expert's standing rule "take the simpler option when in doubt" cut Stop B and C questions short.
  - Broke: the plan's 2010 index value (320.4) was the September monthly value; BLS's current file gives 319.8 as the annual average, and the lookup in task 2 caught it. BLS refuses scripted downloads; the agent used its web fetch tool, not a disguised browser request, so rerunning the lookup needs the same route or a manual download. Templating the change tooltip into the shared HTML template would have changed every existing map's page; the agent noticed before running and used placeholders instead. The agent reran the tract tables before saving the 4a copies to compare against, then rebuilt the 4a state in a temporary worktree of `main` from the same snapshots.
  - Agent needed correction on: nothing in the specs or code. In the invocation tests, the expert noted three behaviors: `inv_008` ran the map rather than the Indicator (the table was still produced); `inv_009` and `inv_010` listed only some of the available specs, and `inv_009` suggested authoring 2006–2010 block group specs, which `census_api` § Notes rules out. The agent proposed tightening AGENTS.md rule 1 and validation.md; **the expert declined: the existing behavior is fine** (decision 15).
  - Open points: the `inv_009` suggestion contradicted a Resource's notes; watch for it in later invocation tests. `kat_005` and `kat_003` break if `min_overlap` rises above 0.83. The tooltip's "Start, in end-year dollars" is generic. The source note keeps the MOE sentence though the change has none (expert: keep). Blank-input notes join with "; ", which is also used inside an annotation note.
Design changes:
  - Before building (design issues 1–7): `percent_change`, `builds_on` in the runner, `inflation`, `data` optional with `builds_on`, start/end columns, caveats in manifests, the `percent_change` choropleth (architecture.md §§ 4, 4.4, 4.5, 7, 8, 12; AGENTS.md rule 3; the Indicator template; validation.md).
  - In the retro: *Change over time* removed from § 13 (built in chunks 4a–4b).
  - Existing work brought in line: nothing needed. Existing specs have `data` and no `inflation`; validation clean with no warnings; existing outputs unchanged.

### Chunk 4a — 2010 tract median household income, matched to 2020 tracts   (merged 2026-10-25)
Delivered:
  - Specs (all `stable`): `census_api` (vintage 2010 added), `census_tract_relationship_2020_2010` (file Resource at a URL), `tract_2010` (`id_field: GEO_ID`), `tract_2020`, `tract_2010__to__tract_2020` (`method: matched`, `min_overlap: 0.80`, `fields`), `median_household_income_tract_2010` (with `# Aggregation`), `median_household_income_tract_2024`, `map_median_household_income_tract_2010__tract_2020` (quantile, 5, `Greens`). Renamed with the ACS end year: `population_count_2024`, `median_household_income_2024` and their maps.
  - Code (all verified): `median_household_income_tract_2010.py`, `median_household_income_tract_2024.py` (same body as the reviewed 2024 code); renamed `population_count_2024.py`, `median_household_income_2024.py` (new headers). `lib/`: `geography` reads `GEO_ID`; `crosswalk` gains `build_matched`, `apply_matched` and `read_delimited`; `runner.report` routes `matched` for any measure, records the relationship snapshot and `min_overlap`; `validate` checks `matched` and its columns offline.
  - Outputs: the 2006–2010 tables at `tract_2010` (177) and `tract_2020` (159), the 2020–2024 table at `tract_2020` (159), the 2010 map, and the build file. Go/no-go at 0.80: 136 of 159 2020 tracts matched; 130 have both values.
  - Tests: `kat_003` (exact, the one matched pair in the city whose GEOIDs differ) and `kat_004` (exact) added; `kat_001`–`kat_004` pass. `inv_002`, `inv_003` renamed; `inv_006`–`inv_008` added; `inv_001`–`inv_008` passed in fresh sessions after approval.
Retro:
  - Worked: the rename left all outputs byte-identical, and so did the `lib/` changes, for every existing output including the heat map. A new crosswalk method, a second vintage and tract Geographies fitted the graph, staleness and manifests with no change to `specs.py`, `compiled.py`, `snapshot.py` or `census.py`. Every matched value equals its source unit's. The two-step plan (4a measures the match, the expert decides on 4b) gave a go/no-go on numbers, not guesses.
  - Broke: **the plan assumed the Census API had 2006–2010 block groups; it doesn't** (block groups start at vintage 2013). Task 2 caught it before anything was built, and the chunk was redrafted for tracts in chat (decision 10). Design issue 7 had guessed at a smaller difference (request syntax). The Census API timed out intermittently during network validation; reruns passed. The publication check couldn't run for a `GEO_ID` Geography until `lib/` read it. `inv_007`'s first run came before approval, so run mode refused it (correctly); validation.md now says to run invocation tests after approval.
  - Agent needed correction on: nothing the expert raised. Beyond the plan, the agent proposed `fields` on `matched` crosswalks (approved at Stop B), added validator checks (`from` needs a `census_unit`; `weights_source` must be a file Resource), extra build-file columns (`from_in_geography`, `to_in_geography`), and the "no matching 2010 tract" label derived from the Geography's ID and `census_unit`. Putting the period in the titles changed the spec hashes, which the plan hadn't expected, so the renamed code needed re-verification; the agent said so. It didn't take "ok to all" at Stop B as code verification. It also force-reran outputs after approval so manifests record `stable` and `verified` (a `verified` line alone doesn't make results stale).
  - Open points: `kat_003` breaks if `min_overlap` goes above 0.83 (the only in-city pair whose GEOIDs differ). The "no matching" label depends on the § 12 naming of the `from` Geography. No 2020–2024 tract map (out of scope). Overlap is land area, not households (accepted).
Design changes:
  - Before building (design issues 1–8): AGENTS.md rule 1 (ask which one and name what tells them apart); architecture.md § 2 (same), § 4 (Crosswalk fields), § 4.2 (`GEO_ID`; cartographic files, not TIGER/Line), § 4.3 (`matched`, new subsection; the counts-only rule's exception), § 4.4 (unit before year; ACS geography by vintage), §§ 7, 10 (delimited text), 12 (naming, medians), 13 (*Published values at other units*); Crosswalk and Geography templates; validation.md (`matched` checks, offline column check, tract sample request).
  - In the retro: validation.md, invocation tests run after approval.
  - Existing work brought in line: the four renamed specs and two code files, `kat_001`, `kat_002`, `inv_002`, `inv_003`, the index files; `census_api` updated. Validation clean with no warnings.

### Chunk 3 — Spatial distribution of reported crime incidents   (merged 2026-10-24)
Delivered:
  - Specs (all `stable`): `cle_crime` (local-file Resource, Group A/B lists of the 57 `IncidentDesc` values in the file), `points_reported_crime_incidents` (`measure: points`, `window` 2025-11-30 to 2026-09-30, clipped to `cle_city`), `map_points_reported_crime_incidents__cle_city` (`map: hexbin`, 500 m, quantile, 5, `Purples`).
  - Code: `pipeline/indicators/points_reported_crime_incidents.py` (verified). `lib/`: `points.py` (named fields only, local-date window, clip with boundary inside) and `heatmap.py` (pointy-top grid at origin (0, 0) in EPSG:3734, quantile classes, HTML with classes only), both new; runner `points` path to `build/points/` with an `excluded` block, hexbin branch, `ctx.features`/`in_window`/`inside`/`stop`; `source_note` drops the MOE sentence for non-Census data and adds the Visualization's `# Source note`; validator checks for `points`, `window`, file-Resource `data` entries, `map`/`hex_size_m` with the 250 m floor, and an offline field check for local files. `pyogrio` and `pyproj` pinned in `pyproject.toml`.
  - Outputs: the selection (31,297 points, in `build/`, never published) and the heat map (1,103 hexes, 210 empty), each with a manifest. Excluded + kept = all 69,749 rows.
  - Tests: no known-answer test (decision 9, an accepted exception to the definition of done); the expected size checked by eye instead. `inv_004` and `inv_005` added; `inv_001`–`inv_005` passed in fresh sessions after approval.
Retro:
  - Worked: the expected size, worked out in chat from the raw file, matched exactly before the point rules (31,594) and for rows with no point (106). Existing outputs stayed byte-identical through all the `lib/` changes, and `kat_001`/`kat_002` still pass. A second kind of Indicator and a second map type fitted the graph, staleness and manifests without changes to `specs.py`, `compiled.py` or `snapshot.py`. Hex assignment matched point-in-polygon on 20,000 random points.
  - Broke: the expected count after the clip was 63 too high. It used the `City` field (129 rows), but 71 rows marked Cleveland lie just outside the boundary (median 0.3 m: boundary-street addresses). The expert kept the strict boundary clip. The Visualization template has offered a `# Source note` since chunk 1, but `lib/` never used it; found when the hexbin spec was the first with text there. Built now, and the staleness gap that came with it is documented in § 6. A roadmap edit wrote literal `\n` into the session log (agent's scripting slip; fixed).
  - Agent needed correction on: nothing the expert raised. The agent added two validator rules beyond the plan (`# Point rules` required for `points`; no `also_show` on hexbin) and flagged them; the expert didn't object. The agent took "approve specs" as approval of the compiled code as well, and said so.
  - Open points: point aggregation (counts per unit) is the next chunk; it can `builds_on` the selection. The "No incidents" label is hard-coded in `lib/heatmap.py`; a selection of something else needs its own label. Group A/B lists are copied into compiled code, so a change to `cle_crime`'s lists doesn't make the code stale (an unknown value still stops the run). The map manifest records class breaks in points per hex; the page shows none (expert: keep).
Design changes:
  - Before building (design issues 1–10, 5 dropped): selections (`measure: points`, `points_` prefix, `window`) in § 4.4, templates, glossary and validator; local dates in America/New_York (§ 12); the runner path for selections and `build/points/` (§§ 4.4, 7, 8, 11); file-Resource `data` entries and reading only named fields (§§ 4.4, 10); the offline field check (validation.md); hexbin Visualizations (§ 4.5, template, glossary, validator), *Other chart types* removed from § 13; the privacy floor and "no raw points in any output" (§ 12); heat maps in scope (§ 1); empty and edge hexes (§ 12 *Maps*).
  - In the retro: the source note's contents (§ 4.5) and the accepted `# Source note` staleness gap (§ 6).
  - Existing work brought in line: nothing needed. Existing choropleth specs take the default `map`; validation clean with no warnings; existing outputs byte-identical.

### Chunk 2 — Block group median household income   (merged 2026-10-24)
Delivered:
  - Specs (all `stable`): new `median_household_income` (`measure: median`, `unit: dollars`, B19013_001E) and `map_median_household_income__bg_2020` (quantile, 5, `Greens`). Changed and re-approved: `census_api`, `bg_2020` (`census_unit`), `bg_2020__to__cle_city`, `population_count`.
  - Code: `pipeline/indicators/median_household_income.py` (new) and `population_count.py` (recompiled twice), both verified. `lib/`: `unit: dollars` in maps; partial sums with a note in `crosswalk.apply_count`; `census.estimate_moe`, `census.requests_for` (extent derived from GEOIDs), `null` handling; `Context.acs(entry)` fetches for the Indicator's geography; `runner.report` applies crosswalks and reliability; validator checks for `unit`, `census_unit`, and publication at a level.
  - Outputs: `median_household_income__bg_2020.csv` (335 values, 94 blank: 90 too few sample cases, 4 bottom-coded) and its map; chunk 1's outputs rebuilt with identical values.
  - Tests: `kat_002` (pass, exact: $42,344 for block group 390351198002); `inv_001` reworded (median gross rent), `inv_003` added; `inv_001`–`inv_003` passed in fresh sessions after approval.
Retro:
  - Worked: the chunk 1 pipeline took a second Indicator with small `lib/` additions. `lib_hash` made every result rerun after a `lib/` fix, with no `--force`. Deriving the request extent from the Geography reproduced the old request exactly: same snapshot, byte-identical tables. Fresh-session invocation tests passed once specs were approved.
  - Broke: a latent bug in `census.read` (since chunk 1) filled the note with a printed pandas column whenever a value held a Census code; B19013 exposed it, and it's fixed. Chunk 1's reviewed code didn't match its spec's annotation rule; found while checking design issue 3, and resolved by changing the spec to the expert's rule. `runs` invocation tests run before approval hit run mode's refusal.
  - Agent needed correction on: geography in Indicator bodies ("every block group in Cuyahoga County"). The agent copied it from the roadmap's requirements without challenging it; the expert caught it at Stop C (design issue 5). Proposing "stop the run" for incomplete data; the expert's principle is to compute with flagged uncertainty. Proposing "both blank" for an annotated MOE; the expert keeps the estimate.
  - Open points: medians at other geographies (B19001 interpolation) are deferred. The crosswalk helper still handles only `nested` with `from.within == to`. Moving a `percent`, `rate` or `median` through a crosswalk isn't built yet (the runner says so).
Design changes:
  - architecture.md: *Separation of concerns* table and test (§ 4); `census_unit` and the derived extent (§ 4.2); the Indicator body is about the measure (§ 4.4); optional `unit` (§ 4.4); the runner applies crosswalks and reliability (§ 7); § 12 now holds the expert's principle "compute with flagged uncertainty rather than stop", "a missing unit is an error, a blank value is not", "not published" nulls, and the generic reliability and crosswalk-sum rules; dollar display.
  - Templates: `census_unit` (Geography), `unit` and a body note (Indicator). validation.md: `unit` and `census_unit` choices, "Indicator with Census data → geography has `census_unit`", and the publication check.
  - Existing work brought in line: `census_api` Notes now hold the annotation rule (stated once) and no Cleveland counts; the city-total caveat moved to `bg_2020__to__cle_city`; `population_count` was recompiled to the new rules. Invocation `runs` tests happen after approval (expert's decision).
  - Rejected: a validator check for geography words in Indicator bodies (inspection is enough for now; revisit if it recurs).

### Chunk 1 — Block group population count   (merged 2026-10-21)
Delivered:
  - Specs (all `stable`): `census_api`, `cle_city`, `bg_2020`, `bg_2020__to__cle_city`, `population_count`, `map_population_count__bg_2020`.
  - Code: `lib/` (12 modules: spec graph, validator, snapshots, Census reader, geography + `within`, `nested` crosswalk, MOE + reliability, known-answer tests, outputs + manifests, choropleth with D3 7.9.0 embedded, runner). `pipeline/indicators/population_count.py` (verified).
  - Outputs (not committed, rebuilt by the runner): `population_count__bg_2020.csv`, `population_count__cle_city.csv`, `map_population_count__bg_2020.html`, each with a manifest.
  - Tests: `kat_001` (pass: 366,340 vs 366,097, +0.07%, tolerance relative 2%, kept at 2% by the expert); `inv_001`, `inv_002`.
  - uv environment, Python 3.12, exact versions pinned.
Retro:
  - Worked: every stage ran from a request to outputs with manifests. The majority-area rule kept 429 block groups. The city total landed within 0.07% of the published figure. Staleness checks behaved per § 6 in every case tried (spec body vs. frontmatter, compiled-code spec, snapshot change). Run mode refused drafts and unreviewed code, then ran once approved. No API key reached any file.
  - Broke: the geography loader failed when `id_field` and `name_field` are the same column (`cle_city` `NAME`); fixed. `variables.json` lists `_M` fields as attributes of `_E` fields, not as variables; the validator's field check was fixed. A plain-language prompt ("map the population count by block group in Cleveland") bypassed the runner and rebuilt the map ad hoc.
  - Agent needed correction on: prompt routing (the invocation rule lived only in architecture.md; now AGENTS.md rule 1). `inv_001` was recorded as passing after calling the runner directly, which tests the runner, not the agent. Requirement facts were off: `cle_city` has no `OBJECTID`; task 7 named `pipeline/population_count.py`, but § 6 says `pipeline/indicators/`.
  - Open points noted for later chunks: the city MOE (±7,663) is much larger than the published one (±76), because the published place total is controlled to population estimates. `lib/` is ≈1,300 lines; focus review on `moe.py`, `geography.py`, `census.py`, `crosswalk.py`. The crosswalk helper handles only `nested` with `from.within == to` and one target.
Design changes:
  - Before building (design issues 1–6): invocation and runner (§§ 2, 7), invocation tests (validation.md § 3, `tests/invocation.md`), `within_rule` (§ 4.2, Geography template), `nested` after `within` (§ 4.3), boundary-file snapshots and `data/static/` (§§ 10, 11), uv (§ 12).
  - In the retro: AGENTS.md rule 1 (every request goes through the runner) and rule 7 (an edit to a `stable` spec sets it back to `draft`). `status` is left out of spec hashes; `lib/` changes make all results rerun (`lib_hash` in manifests) (§§ 6, 8, 9). Invocation tests start from the plain prompt in a fresh session (validation.md § 3). The validator warns on edited `stable` specs. `known_answers.md` YAML is the contract, and `unit` is the `id_field` value (design issues 7–8, validation.md § 2). `outputs/` isn't committed (§§ 11, 12). Deferred: a GeoPackage `layer` field (design issue 9) and moving rule 1 into the packaged skill (§ 13).
  - Existing work brought in line: the compiled code header was restamped with the new spec hash (spec and code unchanged), `verified` was added, and the six specs were set to `stable` on the expert's instruction. Validation: 0 errors, 0 warnings. Outputs were rebuilt in run mode with identical values.

Template for each finished chunk:

```
### Chunk N — <name>   (merged YYYY-MM-DD)
Delivered: specs, outputs, tests added
Retro:
  - Worked:
  - Broke:
  - Agent needed correction on:
Design changes: what changed in architecture.md, and what existing work was updated to match
```

---

## Session log

| Date | Where | What happened | Next |
|---|---|---|---|
| 2026-10-21 | Chat | Design discussion; drafted AGENTS.md, architecture.md, templates, spec folders, and test docs. | Revise docs. |
| 2026-10-21 | Chat | Revised all docs: Resource = unit of access; templates trimmed and aligned with OKF v0.2; staleness split into code vs. results; snapshots per request. | Agree on working method. |
| 2026-10-21 | Chat | Agreed chunk-based working method; wrote this roadmap. Chunk 1 set as block group population count. | Define chunk 1 requirements in chat. |
| 2026-10-21 | Chat | Defined chunk 1 requirements, design issues, and tasks. Confirmed city boundary GeoPackage (1 feature, EPSG:3734). | 🛑 Stop A: expert approves requirements; then implement in Claude Code. |
| 2026-10-21 | Chat | 🛑 Stop A passed: expert approved chunk 1 requirements and the proposed fixes for design issues 1–6. | Claude Code: start at task 1 (initial commit, create branch). Stop B after specs are drafted. |
| 2026-10-21 | Claude Code | Tasks 1, 3, 4, 5: initial commit on `main`, branch `chunk/01-bg-population`; design issues 1–6 applied; uv env (Python 3.12, pinned); six specs + `kat_001` + `inv_001` drafted. Checked: `B01003_001E` exists in `acs/acs5` 2024 variables; `bg_2020` URL resolves (HTTP 200, 9,466 Ohio BGs, EPSG:4269); city file has 1 feature, EPSG:3734. Stop B questions. |
| 2026-10-21 | Claude Code | Expert answered Stop B questions and supplied task 2 inputs (city boundary source; `kat_001` confirmed). Specs updated. | 🛑 Stop B: expert approves specs. Then task 6. |
| 2026-10-21 | Claude Code | ✅ Stop B passed: expert approved specs and tests. | Tasks 6–8. |
| 2026-10-21 | Claude Code | Tasks 6–8: built `lib/`, compiled `population_count`, ran validation, `kat_001` (pass, +0.07%), `inv_001` (pass), produced 2 tables + 1 map with manifests. | 🛑 Stop C: expert reviews outputs, tests and code; adds `verified`. Then task 9 (retro). |
| 2026-10-21 | Claude Code | Outputs had been deleted from the working tree; regenerated `map_population_count__bg_2020` (and its `population_count` tables) via `lib.runner run --mode author`. `kat_001` pass; outputs match the Stop C commit (same fingerprints, only `created` changed). | 🛑 Still at Stop C. |
| 2026-10-21 | Claude Code | Request "map poverty rates by block group": no matching spec; reported unavailable and listed existing specs. Nothing created. | Expert: this was a test of unknown-indicator handling; no chunk planned. |
| 2026-10-21 | Chat | ✅ Stop C passed. Expert tested prompt invocation: a plain prompt bypassed the runner. Findings added to the retro notes (prompt routing, `inv_002`, `inv_001` scope, edits to stable specs, review load). | Task 9 (retro) in Claude Code. Expert adds `verified` line and sets specs `stable`. |
| 2026-10-21 | Claude Code | Task 9 (retro). The expert decided: an agent edit to a `stable` spec → `draft`; hash `lib/` into manifests; keep `kat_001` at relative 2%; the agent sets `verified` and `stable` on the expert's behalf. Applied design changes, updated the checklist, ran validation (clean) and run mode (pass), merged `chunk/01-bg-population` into `main`. | Define chunk 2 in chat. First run `inv_001` and `inv_002` from the plain prompt in a fresh session. |
| 2026-10-24 | Chat | Defined chunk 2 (block group median household income): requirements, design issues 1–4, tasks. Expert chose B19013, block group only, top/bottom-coded values blank, quantile 5 `Greens`. Couldn't reach the Census API from the session, so the field check moved to task 4. | 🛑 Stop A: expert approves requirements. Then task 1 in Claude Code. |
| 2026-10-24 | Chat | Corrected the brief: B19013 is a published value, so chunk 2 adds no new capability from the checklist. Discussed Visualization reuse: one spec per map stays the rule, and shared defaults were added to architecture.md § 13 as deferred. ✅ Stop A passed. | Claude Code: start at task 1 (carried-over invocation tests), then task 2 (create the branch). Stop B after specs are drafted. |
| 2026-10-24 | Claude Code | Task 1: expert ran `inv_001` and `inv_002` in fresh sessions. Both passed. No files created. | Task 2: create the branch. |
| 2026-10-24 | Claude Code | Tasks 2–5: branch `chunk/02-bg-median-income`; design issues 1–4 applied (docs, template, `census_api` note); B19013 checked (335 values, 90 annotated, 4 bottom-coded); drafted `median_household_income`, `map_median_household_income__bg_2020`, `kat_002`, `inv_003`; updated `inv_001`. Found a spec/code mismatch in `population_count` (annotation rule). | 🛑 Stop B: expert answers the 4 questions and approves the specs. Then task 6. |
| 2026-10-24 | Claude Code | Expert answered the Stop B questions: `kat_002` confirmed, `census_api` re-approved, annotation wording OK, estimate kept when only the MOE is annotated. Edited `population_count` to match (now `draft`, code stale). | 🛑 Stop B: expert decides on the follow-ups (city total with a blank MOE; median rule) and approves the specs. |
| 2026-10-24 | Claude Code | Follow-ups: city total uses available parts with a note (option B); principle "compute with flagged uncertainty rather than stop" added to § 12; median annotation rule aligned with `population_count`. | 🛑 Stop B: expert approves the specs. Then task 6. |
| 2026-10-24 | Claude Code | ✅ Stop B passed: expert approved both new specs, the edited `population_count`, `kat_002`, `inv_001`, `inv_003`. | Tasks 6–7. |
| 2026-10-24 | Claude Code | Tasks 6–7: `lib/` extended (`unit: dollars`, partial sums, `estimate_moe`), fixed a latent annotation-note bug in `census.read`, recompiled `population_count`, compiled `median_household_income`, produced outputs. `kat_001` and `kat_002` pass. | 🛑 Stop C: expert runs `inv_001`–`inv_003` in fresh sessions and reviews. Then task 8 (retro). |
| 2026-10-24 | Claude Code | Expert ran `inv_002` and `inv_003`: both resolved correctly and used the runner, which refused in run mode (specs `draft`, code unreviewed). Routing passed; no outputs, as expected before approval. | 🛑 Stop C: `inv_001` result; expert review and approval; decide when `runs` tests happen. |
| 2026-10-24 | Claude Code | Expert reported `inv_001` passed. | 🛑 Stop C: expert review and approval; decide when `runs` tests happen. |
| 2026-10-24 | Claude Code | Expert's review: Indicator bodies named Cuyahoga County (separation of concerns). Applied design issue 5: `census_unit` + derived extent, runner applies crosswalks and reliability, generic rules moved to § 12 and `census_api`, publication check. Outputs byte-identical. | 🛑 Stop C: expert reviews and approves (6 specs, 2 code files); decide when `runs` tests happen. |
| 2026-10-24 | Claude Code | Expert approved all changes: 6 specs `stable`, 2 code files `verified`. `runs` tests happen after approval (option a). Validation clean; all outputs up to date. | Expert reruns `inv_002` and `inv_003` in fresh sessions. Then task 8 (retro). |
| 2026-10-24 | Claude Code | Expert reran `inv_002` and `inv_003` after approval: both passed. Task 8: retro recorded, checklist updated, `chunk/02-bg-median-income` merged into `main`. | Define chunk 3 in chat. |
| 2026-10-24 | Chat | Started chunk 3 (reported crime incidents by block group): read the crime incidents geodatabase, agreed on a thin vertical slice, chose incidents (cases with a Group A offense) as the unit, recorded caveats by spec and design issues 1–3 in Current chunk. | Expert answers open questions 2–7. Then design check and 🛑 Stop A. |
| 2026-10-24 | Chat | Reframed chunk 3 as a heat map of reported crime incidents, with no counts. Decisions 2–9: selection Indicator (`measure: points`, `points_` prefix, `window` in frontmatter), filtering in the Indicator, heat map in `lib/heatmap.py` embedding no points, privacy floor in § 12, choropleth-only scope lifted, no known-answer test. | Expert answers open questions 1–6 (map type in a follow-up). Then design check and 🛑 Stop A. |
| 2026-10-24 | Chat | Chunk 3 decisions 10–15: window `OffenseDate` 2025-11-30 to 2026-09-30; hexbin grid, 500 m to start, tuned at Stop C; floor 250 m, no sparse-hex rule; relative quantile classes; Resource ID `cle_crime`; exclusions in the manifest; points carry case, point, date. | Expert answers open questions 1–2. Then design check against architecture.md and 🛑 Stop A. |
| 2026-10-24 | Chat | Chunk 3 decisions 16–17 (exclude Justifiable Homicide; 5 classes, colors proposed). Step 2 design check: design issues 1–10, Stop A questions 1–4, tasks, and specs to draft written into Current chunk in chunk 2's format. | 🛑 Stop A: expert approves requirements and design issues, answers Stop A questions. Then Claude Code: task 1. |
| 2026-10-24 | Chat | Expert re-downloaded the crime data as one GeoPackage (same export, checked). Design issue 5 (folder snapshot) dropped. Found that times are stored in UTC: the window uses Eastern dates (design issue 2, Computation step 3, Resource Notes); expected size updated to about 31,360. | 🛑 Stop A. |
| 2026-10-24 | Chat | ✅ Stop A passed: expert approved chunk 3 requirements and design issues 1–10 (5 dropped); Stop A questions settled with the agent's defaults (decisions 18–21: empty hexes gray, edge hexes clipped, origin (0, 0) in `lib/`, `Purples`). | Claude Code: task 1 (commit the plan on `main`, create the branch). Stop B after specs are drafted. |
| 2026-10-24 | Claude Code | Task 1: committed the chunk 3 plan on `main` (`54d7bd3`); created `chunk/03-crime-heatmap`. | Task 2: apply design issues 1–10. |
| 2026-10-24 | Claude Code | Task 2: applied design issues 1–10 to architecture.md (§§ 1, 4, 4.4 selections, 4.5 hexbin, 7, 8, 10, 11, 12 dates/privacy/maps; *Other chart types* removed from § 13), AGENTS.md glossary, Indicator and Visualization templates, validation.md, and `lib/validate.py` (`points` measure, `window`, file-Resource `data` entries, `map`/`hex_size_m` with the 250 m floor, offline field check for local file Resources). Checked each new validator rule against throwaway specs, including the field check against the crime GeoPackage. Validation clean. The `lib/` change marks existing results for rerun (no recompile). Left for task 4: runner, `ctx.features`, `heatmap.py`, `source_note`. Left for the retro: the definition-of-done exception. | Task 3: draft the three specs, `inv_004`, `inv_005`; 🛑 Stop B. |
| 2026-10-24 | Claude Code | Task 3: drafted `cle_crime`, `points_reported_crime_incidents`, `map_points_reported_crime_incidents__cle_city`; updated the three `index.md` files; added `inv_004`, `inv_005`. Checked the Resource's Group A/B lists against the file (47 + 10 values, exact match). Field check passes; the only validation error is the expected missing compiled code. 5 Stop B questions recorded. | 🛑 Stop B: expert answers the questions and approves the specs. Then task 4. |
| 2026-10-24 | Claude Code | ✅ Stop B passed: expert approved `cle_crime`, `points_reported_crime_incidents`, `map_points_reported_crime_incidents__cle_city`, `inv_004`, `inv_005`, with the defaults for Stop B questions 1–5. | Task 4. |
| 2026-10-24 | Claude Code | Tasks 4–5: added `lib/points.py`, `lib/heatmap.py`, the points path and hexbin branch in `lib/runner.py`, `write_points` in `lib/output.py`, `source_note` changes; compiled `points_reported_crime_incidents`. Produced the selection (31,297 points) and the heat map. Expected size matches except 63 boundary points (median 0.3 m outside). Existing outputs unchanged; `kat_001`, `kat_002` pass. 8 Stop C questions recorded. | 🛑 Stop C: expert reviews, answers the questions, runs `inv_001`–`inv_005` in fresh sessions. Then task 6. |
| 2026-10-24 | Claude Code | Expert answered Stop C questions 1–7: keep the boundary clip, 500 m, `Purples`, the manifest breaks, the source-note behaviour; offense lists in code and the "No incidents" label are fine. | 🛑 Stop C: question 8, approval, `inv_001`–`inv_005`. |
| 2026-10-24 | Claude Code | Question 8: added `pyogrio` and `pyproj` to `pyproject.toml` (lock versions unchanged). Expert approved: 3 specs `stable`, `points_reported_crime_incidents` code `verified`. Validation clean, no warnings; the heat map passes run mode. | 🛑 Stop C: expert runs `inv_001`–`inv_005` in fresh sessions. Then task 6 (retro). |
| 2026-10-24 | Claude Code | Expert ran `inv_001`–`inv_005` in fresh sessions: all pass. Task 6: retro recorded, checklist updated (local file resource, point dataset, selection, hexbin), architecture.md §§ 4.5 and 6 (source note), `chunk/03-crime-heatmap` merged into `main`. | Define chunk 4 in chat (e.g. counts per unit building on the selection). |
| 2026-10-25 | Chat | Started chunk 4 (change in block group median household income, 2006–2010 → 2020–2024). Expert chose one Indicator per vintage; the year is never a run-time parameter (architecture.md § 4.4 *Vintages and change over time*; §§ 4.1, 12, 13 updated). Split into 4a (`bg_2010`, a 1:1 `matched` crosswalk, the 2010 median, measuring boundary change) and 4b (change Indicator, inflation factor written in its spec, caveats in the manifest instead of significance testing, diverging map). | Write 4a into Current chunk; its first task measures 2010 → 2020 block group overlap. |
| 2026-10-25 | Chat | Wrote chunk 4a requirements into Current chunk: specs, matching rule, design issues 1–7, Stop A questions 1–5, tasks, go/no-go summary for 4b; 4b outlined. | 🛑 Stop A: expert approves requirements and design issues, answers Stop A questions. Then Claude Code: task 1. |
| 2026-10-25 | Chat | ✅ Stop A passed: expert approved chunk 4a requirements and design issues 1–7. Decisions 5–9: 2006–2010; Census relationship file, `min_overlap` 0.80; ask and name the available years when several vintages match; 2010 map included; `population_count` renamed. | Claude Code: task 1 (commit the plan on `main`, create the branch), then task 2 (source checks). Stop B after specs are drafted. |
| 2026-10-25 | Claude Code | Task 1: plan committed on `main`, branch `chunk/04a-bg-2010-income` created. Task 2: 2010 cartographic block groups and the relationship file confirmed; the Census API has no block group data for vintage 2010 (block groups begin at 2013). Stopped, per task 2. | 🛑 Expert chooses the 2006–2010 data source (summary file, NHGIS, 2009–2013, or tracts). Then finish task 2 for that source. |
| 2026-10-25 | Chat | Expert chose tracts after task 2 (decision 10). Rewrote chunks 4a and 4b for tracts: `tract_2010`, `tract_2020`, `tract_2010__to__tract_2020` (`matched`, 0.80), `median_household_income_tract_2010` and `…_tract_2024`, 2010 tract map; design issue 8 (naming for a second Census unit); `kat_004`; `inv_006`–`inv_008` reworded. | 🛑 Stop A again (tract version, Stop A question 1). Then Claude Code: task 1b, task 2 for tracts. |
| 2026-10-25 | Chat | ✅ Stop A passed for the tract version: expert approved chunk 4a (tracts) requirements and design issues 1–8. Decision 11: `<measure>_tract_<year>` naming. | Claude Code: task 1b (rename the branch to `chunk/04a-tract-2010-income`, commit), then task 2 for tracts. Stop B after specs are drafted. |
| 2026-10-25 | Claude Code | Task 1b: branch renamed `chunk/04a-tract-2010-income`, redraft committed. Task 2 (tracts): API serves 2010 and 2024 tracts; 2010 codes match 2024's; 2010 and 2020 cartographic tract files and the tract relationship file confirmed (*Task 2 findings* 5–9). | Task 3: design issues 1–8, rename first. |
| 2026-10-25 | Claude Code | Task 3: rename done (outputs byte-identical, `kat_001`/`kat_002` pass; code needs re-verification); design issues 2–8 in docs. Task 4: specs, indexes, `kat_003`, `kat_004`, `inv_006`–`inv_008` drafted. Proposed `fields` on `matched` crosswalks. | 🛑 Stop B: expert reviews specs and *Stop B notes* questions 1–5. Then task 5 (`lib/`, compile). |
| 2026-10-25 | Claude Code | Stop B passed (decision 12). Task 5: `lib/` for `matched`, `GEO_ID`, delimited files, validation; both tract Indicators compiled. Task 6: validation clean (also `--network`), `kat_001`–`kat_004` pass, existing outputs byte-identical, new tables and map written, go/no-go summary (130 of 159 2020 tracts have both values at 0.80). | 🛑 Stop C: expert reviews `lib/` and code, sets `min_overlap`, decides on 4b, runs `inv_001`–`inv_008`, approves. Then task 7 (retro). |
| 2026-10-25 | Claude Code | Expert approved: 12 specs `stable`, 4 code files `verified`, `min_overlap` 0.80. Validation 0 errors, 0 warnings; manifests refreshed; run mode runs the 2010 map; `kat_001`–`kat_004` pass. | 🛑 Expert runs `inv_001`–`inv_008` in fresh sessions; decides on 4b. Then task 7 (retro). |
| 2026-10-25 | Claude Code | Expert ran `inv_001`–`inv_008` in fresh sessions: all pass. 4b goes ahead. Task 7: retro recorded, checklist updated (URL file Resource, second vintage, tracts, 2010 boundaries, median aggregation, `matched`), validation.md (invocation tests after approval), `chunk/04a-tract-2010-income` merged into `main`. | Write 4b requirements in chat, into Current chunk. |
| 2026-10-25 | Claude Code | 4b task 1: plan committed on `main`, branch `chunk/04b-tract-income-change`. Task 2: R-CPI-U-RS from BLS's current file: 2010 = 319.8 (not 320.4), 2024 = 462.511; factor 1.44625. | Task 3: design issues 1–7. |
| 2026-10-25 | Claude Code | 4b task 3: design issues 1–7 in docs. Task 4: change Indicator and map drafted, `kat_005` (−17.02%), `inv_008` → `runs`, `inv_009`, `inv_010`. | 🛑 Stop B: expert reviews specs and *Stop B notes* questions 1–4. Then task 5. |
| 2026-10-25 | Claude Code | Stop B passed (decision 13). Task 5: `lib/change.py`, `builds_on` in the runner, start/end columns, caveats in manifests, `percent_change` choropleth, validator; change Indicator compiled. Task 6: validation clean, `kat_001`–`kat_005` pass, existing outputs byte-identical, expected size matches (130 of 159). | 🛑 Stop C: expert reviews `lib/` and code, breaks, questions 1–3; approves. Then invocation tests in fresh sessions. |
| 2026-10-25 | Claude Code | Expert approved 4b (decision 14): 2 specs `stable`, change code `verified`; breaks, source note and tooltip kept. Validation 0 errors, 0 warnings; manifests refreshed; run mode runs the change map; `kat_005` passes. | 🛑 Expert runs `inv_001`–`inv_010` in fresh sessions. Then task 7 (retro). |
| 2026-10-25 | Claude Code | Expert ran `inv_001`–`inv_010` in fresh sessions and accepted the results; proposed changes to AGENTS.md rule 1 and validation.md declined (decision 15: existing behavior is fine). Task 7: retro recorded, checklist updated (`builds_on`, percent change, caveats in manifests, manual diverging map), *Change over time* removed from architecture.md § 13, `chunk/04b-tract-income-change` merged into `main`. | Define the next chunk in chat. |
| 2026-10-25 | Chat | Wrote chunk 4b requirements into Current chunk: change Indicator (`percent_change`, `builds_on`, `inflation`), diverging map, design issues 1–7, Stop A questions 1–6, `kat_005`, `inv_008`–`inv_010`. Fixed the order of two chat rows in this log. | 🛑 Stop A: expert approves requirements and design issues, answers Stop A questions. Then Claude Code: task 1. |
| 2026-10-25 | Chat | ✅ Stop A passed: expert approved chunk 4b requirements and design issues 1–7. Decisions 7–12: `percent_change`; no MOE for the change; breaks ±5/10/15 % (8 classes, `RdBu`); start and end in the tooltip; manifest caveats for the change Indicator only; `kat_005` by hand. | Claude Code: task 1 (commit the plan on `main`, create the branch), then task 2 (inflation factor). Stop B after specs are drafted. |
| 2026-10-25 | Chat | Wrote chunk 5 requirements into Current chunk: tract population 2006–2010 and 2020–2024 and their percent change on 2020 tracts (three Indicators, optional change map), design issues 1–3, Stop A questions 1–3, `kat_006`, `kat_007`, `inv_011`, `inv_012`. | 🛑 Stop A: expert approves requirements and design issues, answers Stop A questions. Then Claude Code: task 1. |
| 2026-10-25 | Chat | ✅ Stop A passed: expert approved chunk 5 requirements and design issues 1–3. Decisions 3–5: change map with breaks ±5/10/15/20 % (10 classes, `RdBu`); counts through the 0.80 `matched` crosswalk accepted; `kat_006` and `kat_007` as recommended. | Claude Code: task 1 (commit the plan on `main`, create the branch), then task 2 (source check). Stop B after specs are drafted. |
| 2026-10-25 | Claude Code | Chunk 5 tasks 1–4: plan committed, branch created; source check passed (B01003 at tract level, 2010 and 2024); design issues 1–3 applied, existing outputs unchanged, `kat_001`–`kat_005` pass; three Indicators and the change map drafted; `kat_006` (3,809 ± 499), `kat_007` (−0.11), `inv_011`, `inv_012` added. | 🛑 Stop B: expert reviews specs and *Stop B notes* questions 1–4. Then task 5. |
| 2026-10-25 | Claude Code | Stop B passed (decision 6). Task 5: three Indicators compiled; change tooltip formats start and end by the inputs' unit. Task 6: validation clean, `kat_001`–`kat_007` pass, existing outputs byte-identical, expected size matches (136 and 134 of 159). | 🛑 Stop C: expert reviews code and `lib/`, tunes breaks (*Stop C notes* 1), approves. Then invocation tests in fresh sessions. |
| 2026-10-25 | Claude Code | Expert approved chunk 5 (decision 7): breaks kept, 4 specs `stable`, 3 code files `verified`. Validation 0 errors, 0 warnings; manifests refreshed; run mode runs the change map; `kat_006`, `kat_007` pass. | 🛑 Expert runs `inv_001`–`inv_012` in fresh sessions. Then task 7 (retro). |
| 2026-10-25 | Claude Code | Expert ran `inv_001`–`inv_012` in fresh sessions; all pass. Task 7: retro recorded, checklist updated (counts through `matched`, percent change of counts, tooltip by unit), `chunk/05-tract-population-change` merged into `main`. | Define the next chunk in chat. |
| 2026-10-25 | Chat | Defined chunk 6 (tract clusters by income and population change). Decisions 1–4: k-means, z-scores with extreme values kept, numbered clusters, split into 6a (cluster Indicator, categorical map) and 6b (charts). Wrote 6a into Current chunk: specs, computation, diagnostics, caveats, expected size from a chat run, design issues 1–10, Stop A questions 1–6, `kat_008`, `inv_013`, `inv_014`; 6b outlined. | 🛑 Stop A: expert approves requirements and design issues, answers Stop A questions. Then Claude Code: task 1. |
| 2026-10-25 | Chat | ✅ Stop A passed: expert approved chunk 6a requirements and design issues 1–10. Decisions 5–10, all as recommended: log income, no clipping; a one-tract cluster accepted; k = 5 to start; scikit-learn; `kat_008`, `inv_013`, `inv_014` as written; `Tableau10`. | Claude Code: task 1 (commit the plan on `main`, create the branch), then task 2 (add scikit-learn). Stop B after specs are drafted. |
