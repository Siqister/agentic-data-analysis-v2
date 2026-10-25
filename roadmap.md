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
- ☑ Invocation tests (chunk 1; `inv_001` and `inv_002` passed from the plain prompt in fresh sessions, 2026-10-24; `inv_001`–`inv_003` passed after approval in chunk 2; `inv_001`–`inv_005` in chunk 3; `inv_001`–`inv_008` in chunk 4a)

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
- ☑ Count, with margin of error (chunk 1)
- ☐ Percent or rate (counts first, then rate)
- ☑ Reliability flag (chunk 1); suppress not yet
- ☑ Median or other custom aggregation (chunk 4a: a median through a `matched` crosswalk, `# Aggregation`)
- ☐ Indicator that builds on other Indicators
- ☑ Selection of points (`measure: points`, `window` in local dates) (chunk 3)
- ☐ Point aggregation

**Crosswalks**
- ☑ `nested` (chunk 1: only `from.within == to` with one target unit)
- ☑ `matched` (chunk 4a: 2010 → 2020 tracts, reciprocal land-area overlap, `min_overlap` 0.80)
- ☐ `population_weighted`
- ☐ `areal` / `centroid`

**Visualizations**
- ☑ Choropleth with tooltips (chunk 1)
- ☑ Hexbin heat map, 250 m privacy floor (chunk 3)

---

## Current chunk

### Chunk 4b — Change in tract median household income, 2010 → 2024

**Analysis question:** how has median household income changed at the census tract level between 2010 (ACS 2006–2010) and 2024 (ACS 2020–2024)? Percent change, in constant 2024 dollars.

**Brief:** the first Indicator that `builds_on` other Indicators, and the first diverging map.
- A new `measure: percent_change` Indicator on 2020 tracts. It builds on the 2006–2010 tract median (moved to 2020 tracts by 4a's matched crosswalk) and the 2020–2024 tract median.
- The 2010 values are adjusted to 2024 dollars with a factor written in the spec (decision 3).
- A proof of concept: no significance test and no MOE for the change. Caveats are recorded in the change Indicator's manifests (decisions 2, 8, 11).
- A choropleth with manual breaks around 0 and a diverging color scheme.

**Branch:** `chunk/04b-tract-income-change`

**Status:** ✅ Stop A passed 2026-10-25. Tasks 1–4 done. 🛑 **Stop B:** the expert reviews the drafted specs and *Stop B notes*.

**Exercises (capability checklist):**
- New items to add: Indicator that builds on other Indicators; `percent_change` measure; manual classification with a diverging scheme; caveats in manifests.

_Place and unit words in this section are requirements. They do not go into the Indicator body (chunk 2, design issue 5)._

#### Requirements

**Specs to draft** (all `status: draft`)

| ID | Type | Settings |
|---|---|---|
| `median_household_income_tract_pct_change_2010_2024` | Indicator | `measure: percent_change`; `geography: tract_2020`; `builds_on: [median_household_income_tract_2010, median_household_income_tract_2024]` (start first, end second); no `data`, `crosswalks`, `reliability` or `unit`; `inflation` (design issue 3): index R-CPI-U-RS, 2010 and 2024 annual averages, source URL and retrieval date (task 2). |
| `map_median_household_income_tract_pct_change_2010_2024__tract_2020` | Visualization | `indicator`: the change Indicator; `geography: tract_2020`; `classification: manual`; `classes: 8`; `breaks: [-15, -10, -5, 0, 5, 10, 15]`; `colors: RdBu`, red for decline to blue for increase (decision 9). `# Source note`: "Change is not tested for statistical significance." |

Used unchanged: `median_household_income_tract_2010`, `median_household_income_tract_2024`, `tract_2010`, `tract_2020`, `tract_2010__to__tract_2020`, `census_api`, `census_tract_relationship_2020_2010`, `cle_city`.

**Computation** (Indicator body, without place names)
1. `start` = the start Indicator's value at this geography; `end` = the end Indicator's value. Each comes with its MOE and note.
2. Inflation factor = `inflation.to.value` ÷ `inflation.from.value`. `start` and its MOE are multiplied by it, so both values are in the end year's dollars.
3. `estimate` = (`end` ÷ `start` − 1) × 100.
4. `moe` is blank: the change has no MOE (decision 8). `cv` and `reliability` are blank too.
5. If either value is blank, `estimate` and `moe` are blank, and `note` says which input is blank and why, e.g. "2006–2010: no matching 2010 tract".
6. The table also has `start` (in the end year's dollars), `start_moe`, `end`, `end_moe` (design issue 5).

**Caveats** (Indicator `# Caveats`, without place names; copied into its output manifests, design issue 6)
- **Not tested for statistical significance, and no MOE.** Both medians have large MOEs (in `start_moe` and `end_moe`), so many changes may be within sampling error.
- The 2010 values are adjusted with a national price index (R-CPI-U-RS), which doesn't reflect local prices.
- A change in a unit's median isn't a change in any household's income: households move in and out, and who lives there changes.
- Only units matched one to one between the two boundary vintages have a value. The match is by land area, not by where households are.
- The 2006–2010 estimates were controlled to the population estimates of the time, not to the 2010 census counts. The 2020–2024 period includes 2020, when ACS data collection was disrupted.
- Top- and bottom-coded inputs are blank, and the codes stand for different real incomes in each year.

**Outputs** (each with its manifest)
- `outputs/tables/median_household_income_tract_pct_change_2010_2024__tract_2020.csv`
- `outputs/visualizations/map_median_household_income_tract_pct_change_2010_2024__tract_2020.html`

**Expected size** (sanity check at Stop C, not a known-answer test)
- 159 rows; **130 with a value** (both inputs present, from 4a's go/no-go).
- The median ratio of 2020–2024 to 2006–2010 values, before adjustment, is about 1.38. With a factor of about 1.44, the median change is a few percent below 0. Before adjustment, the range runs from 0.61 to 3.18.

**Tests**
- **Spec validation** passes for the whole project, including the checks from design issues 1–3.
- **`kat_005`**: the change Indicator at `tract_2020` for one tract, computed by hand from the two input tables and the factor; `tolerance: absolute 0.01` (percentage points). This isn't a trusted published value. It checks the joins and arithmetic, not the factor; an exception to validation.md § 2, which the expert accepts at Stop A.
- `kat_001`–`kat_004` still pass.
- **Invocation:**
  - `inv_008` changes from `not_available` to `runs`. Prompt (unchanged): "How has median household income changed by census tract since 2010?" `spec: median_household_income_tract_pct_change_2010_2024`. The agent reports the table without describing or ranking places.
  - `inv_009`, block groups aren't available. Prompt: "Map the change in median household income by block group since 2010." Expected: `not_available`.
  - `inv_010`, other years aren't available. Prompt: "How has median household income changed by census tract between 2015 and 2024?" Expected: `not_available`. The agent must not change the years itself (architecture.md § 4.4 *Vintages and change over time*).
  - Existing `inv_001`–`inv_007` still pass. Invocation tests run after approval (validation.md § 3).

**Not in this chunk:** significance tests or flags; change in dollars; other pairs of years; block groups; change at the city level; a 2020–2024 tract map.

#### Design issues

Found by checking the requirements against architecture.md, AGENTS.md, validation.md, the templates and `lib/`. Proposed fixes:

1. **`measure: percent_change`** (§ 4.4 `measure`, Indicator template, validation.md choices, `lib/validate.py`).
   - Values are percent changes, signed. Displayed to 1 decimal place with a sign, e.g. "+12.3%".
   - It has `builds_on` with exactly two Indicators (start, then end), no `crosswalks` (a percent change can't be moved), no `reliability` (a CV is meaningless for a change near 0), and no `unit`.
2. **`builds_on` in the runner** (§§ 4.4, 7, 8; `lib/runner.py`, `lib/validate.py`).
   - The runner runs each `builds_on` Indicator first, as a dependency (staleness as usual). A new `ctx.indicator(id)` returns that Indicator's table at this Indicator's `geography`, read from `outputs/tables/`.
   - Validator: each `builds_on` Indicator is reported at this Indicator's `geography`. An Indicator needs `data`, `builds_on`, or both, so `data` is no longer always required.
   - Manifest: `data` includes the inputs' snapshots (from their manifests), so a new snapshot below reruns this Indicator. A new `indicator_inputs` block records each input table's path and fingerprint, and the output is stale when one changes, like a Visualization's `indicator_output`.
   - Source note: Resources and Geographies come from the `builds_on` Indicators' `data` when the Indicator has none.
3. **`inflation` field** (§ 4.4, Indicator template, AGENTS.md rule 3, `lib/validate.py`).
   - `inflation: { index, from: { year, value }, to: { year, value }, source, retrieved }`, with both values from the same table. Optional; only for a change Indicator whose inputs are in different years' dollars.
   - AGENTS.md rule 3 gains one exception, from the expert: an inflation index value may be written in an Indicator's `inflation` field with its source, instead of coming from a Resource.
4. **`lib/change.py`** (new, needs review; § 7 helper table): percent change from start and end values and a factor, carrying the inputs' MOEs into `start_moe` and `end_moe` (start's multiplied by the factor), with the blank and note rules in Computation steps 4–5. No MOE for the change (decision 8). Compiled code is a few lines (§ 4.4).
5. **Start and end columns** (§ 12 *Output tables*, `lib/output.py`): `start`, `start_moe`, `end`, `end_moe`, for `percent_change` only, after `reliability` and before `note`. `start` is in the end year's dollars.
6. **Caveats in manifests** (§ 8, `lib/output.py`, `lib/runner.py`): a `percent_change` Indicator's table manifest gets a `caveats` list, copied from its `# Caveats` bullets, and so does its map's manifest. Other Indicators keep their caveats in the spec only (decision 11). This is a `lib/` change, so all results rerun; existing CSVs, maps and manifests stay the same apart from `created` and `lib_hash`.
7. **Choropleth for `percent_change`** (§ 4.5, `lib/choropleth.py`):
   - Signed percent in the tooltip and the legend.
   - Manual breaks with a diverging scheme. Manual classification is in the validator but has never been drawn.
   - The tooltip also shows `start` and `end`, in dollars (decision 10).
   - `reliability` is blank, so the tooltip leaves it out.

Proposed: apply 1–7 after task 2, before drafting specs.

#### Stop A questions

Answered 2026-10-25. Recorded as decisions 7–12.

#### Tasks

1. Commit the chunk 4b plan (this roadmap) on `main`, then create `chunk/04b-tract-income-change` from `main`.
2. **Look up the inflation factor** (network needed). Read the R-CPI-U-RS **2010 and 2024 annual averages from BLS's current all-items file** (<https://www.bls.gov/cpi/research-series/r-cpi-u-rs-home.htm>), both from the same file. 320.4 for 2010 came from an older PDF, and BLS reissued the series with corrections in April 2026. Record the values, the file and the retrieval date. 🛑 Stop and discuss if they can't be read.
3. Apply design issues 1–7. Check that existing outputs are unchanged apart from `created` and `lib_hash` in manifests, and `kat_001`–`kat_004` pass.
4. Draft both specs, update each folder's `index.md`, add `kat_005`, update `inv_008`, and add `inv_009` and `inv_010`. 🛑 **Stop B.**
5. Build the `lib/` changes. Compile `pipeline/indicators/median_household_income_tract_pct_change_2010_2024.py`.
6. Run validation and known-answer tests, and produce the outputs. Check the expected size. Tune the breaks with the expert by editing frontmatter. 🛑 **Stop C:** the expert reviews and approves; then the invocation tests run in fresh sessions.
7. Retro per the working method. Remove *Change over time* from architecture.md § 13.

#### Stop B notes (2026-10-25)

**Task 3 (docs only; `lib/` is task 5, after Stop B, as in 4a):** design issues 1–7 written into AGENTS.md rule 3 (the `inflation` exception), architecture.md §§ 4 (fields), 4.4 (`percent_change`, `builds_on`, `data` optional, change Indicators and `inflation` under *Vintages and change over time*), 4.5 (source note and tooltip for `percent_change`), 7 (Change helper, runner), 8 (`indicator_inputs`, `caveats`), 12 (start/end columns, signed display); the Indicator template; validation.md (three new Indicator checks). The check that existing outputs are unchanged moves to task 5, when `lib/` changes.

**Task 4 drafts** (both `draft`): `median_household_income_tract_pct_change_2010_2024`, `map_median_household_income_tract_pct_change_2010_2024__tract_2020`; both `index.md` files; `kat_005` (tract `39035197400`, the `kat_003` tract: 43913 ÷ (36591 × 1.44625) − 1 = **−17.02%**); `inv_008` changed to `runs`; `inv_009`, `inv_010` added. Validation has 3 errors, all expected until task 5 (`percent_change` unknown, `data` still required, no compiled code).

**Questions for the expert**

1. **2024 index value:** 462.511 (three decimals, like the monthly values), or the table's stored 462.51116666666667? It changes any percent change by under 0.0001 points.
2. **Period in the blank-input note** ("2006–2010: no matching 2010 tract"): proposed, `lib/change.py` derives it from each input's ACS 5-year vintage (vintage − 4 to vintage). Alternative: from the end of the input Indicator's title. When both inputs are blank, the note gives both, start first, joined by "; ".
3. **`inv_009`** also says the agent must not run the tract map instead without asking. OK?
4. **Indicator title:** "Change in median household income by census tract, 2006–2010 to 2020–2024 (%)", with "(%)" as in the template's example; the map's title has no "(%)".

#### Task 2 findings (2026-10-25)

✅ **R-CPI-U-RS read from BLS's current all-items file**, `https://www.bls.gov/cpi/research-series/r-cpi-u-rs-allitems.xlsx` ("Consumer Price Index Retroactive Series (R-CPI-U-RS), U.S. city average, All items, Not Seasonally Adjusted, December 1977=100", 1977–2025), linked from the R-CPI-U-RS home page (last modified 2026-04-03, after the corrections of 2026-03-31 to 04-03). Retrieved 2026-10-25; file SHA-256 `355ea8a1…2544d8`.
- **2010 annual average (`AVG`): 319.8.** Not 320.4: that is the September 2010 monthly value. The cell is a stored value at one decimal (the monthly mean is 319.83).
- **2024 annual average: 462.51116666666667**, stored as the unrounded mean of the twelve monthly values, which have three decimals from 2023 on. Proposed for the spec: **462.511** (three decimals, like the monthly values); the difference in any percent change is under 0.0001 points.
- **Factor: 462.511 ÷ 319.8 = 1.44625.** The plan's "about 1.44" holds; with the median ratio of about 1.38, the median change is about −4.6%.
- Access: BLS refuses scripted downloads (HTTP 403). The page and the file were read with the agent's web fetch tool; the agent didn't disguise a script as a browser. A rerun of this lookup needs the same route, or the expert downloading the file.

#### Decisions (expert, 2026-10-25)

Carried from chunk 4 planning and 4a:
1. **Approach A** (architecture.md § 4.4 *Vintages and change over time*): the change Indicator `builds_on` the two vintage Indicators, the change math lives in `lib/`, and a new pair of years is a new spec.
2. **Proof of concept:** results first; no significance test. Caveats go in the manifest.
3. **Inflation factor** looked up and written into the change Indicator's spec, not a new Resource (an exception to AGENTS.md rule 3).
4. **Diverging color scheme** for the change map.
5. **Accepted caveats:** coded values that don't line up across years; 2006–2010 controls to population estimates, not census counts.
6. **Tracts, `min_overlap` 0.80:** 4a's go/no-go gave 130 of 159 2020 tracts with both values; 4b goes ahead.

Stop A (2026-10-25):
7. **`measure: percent_change`**, not a generic `change` with a unit.
8. **No MOE for the change:** `moe`, `cv` and `reliability` are blank. The inputs' MOEs stay in `start_moe` and `end_moe`.
9. **Map classes:** manual breaks at −15, −10, −5, 0, +5, +10, +15 % (8 classes), `RdBu`, red for decline to blue for increase. Tunable at Stop C.
10. **Tooltip** shows the start (in 2024 dollars) and end values as well as the change.
11. **Caveats in manifests for the change Indicator only** (and its map).
12. **`kat_005`** is computed by hand, an accepted exception to validation.md § 2.

---

## Completed chunks

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
| 2026-10-25 | Chat | Wrote chunk 4b requirements into Current chunk: change Indicator (`percent_change`, `builds_on`, `inflation`), diverging map, design issues 1–7, Stop A questions 1–6, `kat_005`, `inv_008`–`inv_010`. Fixed the order of two chat rows in this log. | 🛑 Stop A: expert approves requirements and design issues, answers Stop A questions. Then Claude Code: task 1. |
| 2026-10-25 | Chat | ✅ Stop A passed: expert approved chunk 4b requirements and design issues 1–7. Decisions 7–12: `percent_change`; no MOE for the change; breaks ±5/10/15 % (8 classes, `RdBu`); start and end in the tooltip; manifest caveats for the change Indicator only; `kat_005` by hand. | Claude Code: task 1 (commit the plan on `main`, create the branch), then task 2 (inflation factor). Stop B after specs are drafted. |
