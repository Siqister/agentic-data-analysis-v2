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
- ☑ Invocation tests (chunk 1; `inv_001` and `inv_002` passed from the plain prompt in fresh sessions, 2026-10-24; `inv_001`–`inv_003` passed after approval in chunk 2; `inv_001`–`inv_005` in chunk 3; `inv_001`–`inv_008` in chunk 4a; `inv_001`–`inv_010` in chunk 4b)

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
- ☑ Indicator that builds on other Indicators (chunk 4b: `builds_on` start and end, `ctx.indicator`, `indicator_inputs` staleness)
- ☑ Percent change over time, with an inflation factor (chunk 4b: `measure: percent_change`, `inflation`, no MOE)
- ☑ Caveats in manifests (chunk 4b: `percent_change` tables and their maps)
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
- ☑ Manual classification with a diverging scheme (chunk 4b: breaks around 0, `RdBu`, signed percents)

---

## Current chunk

### Chunk 5 — Change in tract population, 2006–2010 to 2020–2024

**Analysis question:** what is the population count by census tract in 2006–2010 and in 2020–2024, and what is the percent change? The change is reported on 2020 tracts.

**Brief:** chunk 4a–4b's pattern, repeated for a count. No new kind of capability.
- Three Indicators: the 2006–2010 tract count (moved to 2020 tracts by 4a's `matched` crosswalk), the 2020–2024 tract count, and a `percent_change` Indicator that `builds_on` both.
- It bends "one chunk, one analysis question" slightly (three Indicators), accepted by the expert because each is a copy of an approved pattern.
- What's new is small: the first count through a `matched` crosswalk, and the first `percent_change` with no `inflation` and inputs that aren't dollars.

**Branch:** `chunk/05-tract-population-change`

**Status:** ✅ Stop A passed 2026-10-25. Tasks 1–4 done in Claude Code. 🛑 **Stop B:** the expert reviews the four draft specs, `kat_006`, `kat_007`, `inv_011`, `inv_012`, and the *Stop B notes* below. Next: task 5.

**Exercises (capability checklist):** no new items. Extends `matched` (first count), `percent_change` (no `inflation`, `unit: count`) and the change choropleth (count formatting).

_Place and unit words in this section are requirements. They do not go into the Indicator body (chunk 2, design issue 5)._

#### Requirements

**Specs to draft** (all `status: draft`)

| ID | Type | Settings |
|---|---|---|
| `population_count_tract_2010` | Indicator | Copy of `population_count_2024`'s body with the period changed. `measure: count`; `geography: tract_2010`; `crosswalks: [tract_2010__to__tract_2020]`; `data`: `census_api`, `acs/acs5`, vintage 2010, `B01003_001E` Total population; `reliability` 0.30, flag. Caveats as `median_household_income_tract_2010`'s that apply to a count (controls of the time, matched by land area). |
| `population_count_tract_2024` | Indicator | Same as `population_count_2024` with `geography: tract_2020` and no `crosswalks` (like `median_household_income_tract_2024`). |
| `population_count_tract_pct_change_2010_2024` | Indicator | `measure: percent_change`; `geography: tract_2020`; `builds_on: [population_count_tract_2010, population_count_tract_2024]` (start first, end second); no `data`, `crosswalks`, `reliability`, `unit` or `inflation`. |
| `map_population_count_tract_pct_change_2010_2024__tract_2020` | Visualization | `indicator`: the change Indicator; `geography: tract_2020`; `classification: manual`; `classes: 10`; `breaks: [-20, -15, -10, -5, 0, 5, 10, 15, 20]` (decision 3; tunable at Stop C); `colors: RdBu` (`d3.schemeRdBu[10]`), red for decline to blue for increase. `# Source note`: "Change is not tested for statistical significance." |

Used unchanged: `census_api` (2010 and 2024 vintages already approved), `tract_2010`, `tract_2020`, `tract_2010__to__tract_2020`, `census_tract_relationship_2020_2010`, `cle_city`.

**Computation** (change Indicator body, without place names): as `median_household_income_tract_pct_change_2010_2024` steps 1 and 3–6, with no inflation step. `start` is the start Indicator's count as published.

**Caveats** (change Indicator `# Caveats`, without place names; copied into its manifests)
- **Not tested for statistical significance, and no MOE** (chunk 4b decision 8 carried). The inputs' MOEs are in `start_moe` and `end_moe`.
- Only units matched one to one between the two boundary vintages have a value. The match is by land area, not by where people live: people in the up to `1 − min_overlap` of land the two units don't share count in one period and not the other.
- The 2006–2010 estimates were controlled to the population estimates of the time, not to the 2010 census counts; the 2020–2024 estimates to estimates based on the 2020 census. Part of a change can come from the controls, not from people moving.
- The 2020–2024 period includes 2020, when ACS data collection was disrupted.
- A start of 0 gives no change (`lib/change.py` already notes it).

**Outputs** (each with its manifest)
- `outputs/tables/population_count_tract_2010__tract_2010.csv`, `…_tract_2010__tract_2020.csv`
- `outputs/tables/population_count_tract_2024__tract_2020.csv`
- `outputs/tables/population_count_tract_pct_change_2010_2024__tract_2020.csv`
- `outputs/visualizations/map_population_count_tract_pct_change_2010_2024__tract_2020.html`

**Expected size** (sanity check at Stop C, not a known-answer test)
- 177 rows at `tract_2010`; 159 at `tract_2020` for each of the other tables.
- **136 values** for the 2006–2010 count at `tract_2020` and for the change: the matched 2020 tracts (4a build file), unless a 2010 count is blank or 0. More than the income change's 130, because counts aren't suppressed or top-coded.
- Of the 136 matched pairs, 93 share at least 99.9% of both tracts' land, 114 at least 99%; 5 are below 95% and 2 below 90% (the lowest, 83.1%, is the `kat_003` tract). So the land-area caveat bears on a handful of tracts.
- The 2020–2024 tract counts add up to roughly the block group city total (366,340), not exactly: the majority-area rule keeps different units at each level.

**Tests**
- **Spec validation** passes for the whole project, including design issue 2's checks.
- **`kat_006`**: `population_count_tract_2010` at `tract_2020` for `39035197400` (the `kat_003` tract, matched to 2010 tract 106300, the only in-city pair whose GEOIDs differ). Expected: the published 2006–2010 B01003 value and MOE for tract 106300, read in task 4. `tolerance: exact`. A trusted published value, through the matched path.
- **`kat_007`**: the change Indicator at the same tract, computed by hand from the two input tables; `tolerance: absolute 0.01`. Not a trusted published value (like `kat_005`, an accepted exception to validation.md § 2).
- Both break if `min_overlap` rises above 0.83, like `kat_003` and `kat_005`.
- `kat_001`–`kat_005` still pass. The income change table and map stay byte-identical apart from `created` and `lib_hash`.
- **Invocation** (run after approval, validation.md § 3):
  - `inv_011`, change runs. Prompt: "How has population changed by census tract since 2010?" `expected: runs`, `spec: population_count_tract_pct_change_2010_2024`. Reports the table without describing or ranking places.
  - `inv_012`, no period named. Prompt: "What is the population of each census tract in Cleveland?" `expected: asks`. Two Indicators match (2006–2010 and 2020–2024); the agent names both periods and runs nothing until answered. It doesn't default to the latest.
  - Existing `inv_001`–`inv_010` still pass.

**Not in this chunk:** maps of the two vintage counts; an MOE or significance test for the change; block groups (no 2006–2010 data); a city total from tracts; a `population_weighted` crosswalk.

#### Design issues

Found by checking the requirements against architecture.md, the templates and `lib/`. `lib/change.py` already treats a missing `inflation` as a factor of 1, so the change math needs no change.

1. **`percent_change` beyond dollars** (§§ 4.4, 4.5, 12 *Output tables*; Indicator template).
   - Docs say `start` is "in the end year's dollars". Reword: `start` and `start_moe` are multiplied by the inflation factor when there is one; otherwise they're the start Indicator's values as published.
   - `lib/choropleth.py` (the change map is in, decision 3): the change tooltip hard-codes dollars and "Start, in end-year dollars". Format `start` and `end` by the inputs' `unit` (count: "12,345"), and say "in end-year dollars" only with `inflation`. The income change map's page must not change.
   - New compiled code reads `inflation` with `.get`; the 4b code is pinned and left alone.
2. **Validator** (`lib/validate.py`, validation.md): a `percent_change` Indicator's two `builds_on` Indicators have the same `unit` (missing = `count`); `inflation` only when that unit is `dollars`. Small; it catches a copied spec that keeps the income factor.
3. **Counts through `matched`** (§ 12 *Uncertainty*, docs only): the "counts through a crosswalk" bullet gives the weighted-sum formula. Add that through `matched` a count is copied unchanged, with its MOE, as § 4.3 says for any measure. `lib/` already does this.

Proposed: apply 1–3 after task 2, before drafting specs.

#### Stop A questions

Answered 2026-10-25. Recorded as decisions 3–5.

#### Tasks

1. Commit the chunk 5 plan (this roadmap) on `main`, then create `chunk/05-tract-population-change` from `main`.
2. **Source check** (network): `B01003_001E` and `_001M` exist in `acs/acs5` 2010 and 2024 at tract level; the 2010 tract codes in the city match `tract_2010`'s GEOIDs, as they did for B19013. 🛑 Stop if not.
3. Apply design issues 1–3. Check existing outputs are unchanged apart from `created` and `lib_hash`, and `kat_001`–`kat_005` pass.
4. Draft the specs, update each folder's `index.md`, add `kat_006`, `kat_007`, `inv_011`, `inv_012`. 🛑 **Stop B.**
5. Compile the three Indicators (`population_count_tract_2024.py` may share `population_count_2024.py`'s reviewed body, as the income tract code did). Build design issue 1's tooltip change.
6. Run validation and known-answer tests; produce the outputs; check the expected size; tune the breaks with the expert. 🛑 **Stop C:** the expert reviews and approves; then the invocation tests in fresh sessions.
7. Retro per the working method.

#### Stop B notes

Results of tasks 2–4 (2026-10-25):
- **Source check passed.** `B01003_001E` exists in `acs/acs5` 2010 and 2024 with `_001M` as an attribute; every `tract_2010` and `tract_2020` GEOID is in the API's Cuyahoga tract list; no in-city row has a null or annotation. In-city sums: 409,357 (2006–2010, 177 tracts) and 366,340 (2020–2024, 159 tracts).
- **Design issues 1–3 applied** to architecture.md §§ 4.4, 4.5, 7, 12, the Indicator template, validation.md, `lib/change.py` (docstring) and `lib/validate.py` (unit check). The tooltip change in `lib/choropleth.py` is task 5. Every existing table, map and build file is byte-identical; manifests differ only in `created`, `lib_hash` and `fingerprint` (which includes `lib_hash`). `kat_001`–`kat_005` pass. A negative test of the new check (mixed units; `inflation` on counts) gives both errors.
- **Validation:** 0 errors apart from the three "no compiled code" errors expected before task 5; the `--network` field check is clean.

Questions (recommendation first):
1. **Expected size: 134 changes, not 136.** Two matched 2010 tracts (980100, 980500) have a count of 0, so their change is blank with "2006–2010: estimate is 0". The 2006–2010 count at `tract_2020` still has 136 values. The plan's "unless a 2010 count is blank or 0" covers it; recorded so Stop C checks 134.
2. **`kat_007` is near 0** (3,805 ÷ 3,809 − 1 = −0.105%). It still tells start from end (swapped gives +0.105%, outside the 0.01 tolerance) and goes through the only in-city pair whose GEOIDs differ. Recommend keep.
3. **Titles** name the unit, like the income tract specs: "Total population by census tract, 2006–2010" etc. The block group count keeps "Total population, 2020–2024". Recommend keep.
4. **`population_count_tract_2010` caveats:** sample/MOE, controls of the time, matched by land area (people, not households), unmatched units blank, counts reflect size. Left out the income spec's coding and too-few-cases caveats, which don't apply to B01003.

#### Decisions (expert, 2026-10-25)

Carried from chunks 4a–4b: one Indicator per vintage (§ 4.4); the tract unit before the year in IDs; `matched` at `min_overlap` 0.80; `percent_change` with no MOE or significance test; caveats in the change Indicator's manifests; "take the simpler option when in doubt".

From the chunk 5 brief:
1. **Three Indicators in one chunk** is acceptable: each is a copy of an approved pattern.
2. **The change is reported on 2020 tracts.**

Stop A (2026-10-25):
3. **Change map:** yes. Manual breaks at −20, −15, −10, −5, 0, +5, +10, +15, +20 % (10 classes), `RdBu`, red for decline to blue for increase. Tunable at Stop C.
4. **Counts through the `matched` crosswalk at `min_overlap` 0.80:** accepted, with the land-area caveat. No higher threshold, no `population_weighted` crosswalk.
5. **Known-answer tests:** `kat_006` (published, exact) and `kat_007` (by hand, an accepted exception to validation.md § 2). Not answered separately; taken as approved with Stop A, as recommended.

---

## Completed chunks

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
