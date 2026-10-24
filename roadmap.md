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
- ☑ Invocation tests (chunk 1; `inv_001` and `inv_002` passed from the plain prompt in fresh sessions, 2026-10-24)

**Resources & geographies**
- ☑ API resource (Census Data API) (chunk 1)
- ☐ Local file resource (local-file snapshotting exercised through the `cle_city` Geography in chunk 1; no local-file Resource spec yet)
- ☐ Point dataset
- ☑ Geography from Census boundary files (chunk 1: cartographic boundary file, fetched by URL)
- ☑ Geography from a local file (chunk 1: city GeoPackage; neighborhoods not yet)
- ☑ Geography selection rule (`within`, `majority_area`) (chunk 1)

**Indicators**
- ☑ Count, with margin of error (chunk 1)
- ☐ Percent or rate (counts first, then rate)
- ☑ Reliability flag (chunk 1); suppress not yet
- ☐ Median or other custom aggregation
- ☐ Indicator that builds on other Indicators
- ☐ Point aggregation

**Crosswalks**
- ☑ `nested` (chunk 1: only `from.within == to` with one target unit)
- ☐ `population_weighted`
- ☐ `areal` / `centroid`

**Visualizations**
- ☑ Choropleth with tooltips (chunk 1)

---

## Current chunk

### Chunk 2 — Block group median household income

**Analysis question:** What is the block group level income?

**Brief:** One published median, reported only at its native geography (block groups). Like chunk 1, the value comes straight from a Census table with no derivation, so this chunk adds no new capability from the checklist. "Median or other custom aggregation" stays ☐ until a chunk aggregates a median to another geography: a citywide median, which would need interpolation from the B19001 income brackets and a derived MOE, is deferred to a later chunk.

**Branch:** `chunk/02-bg-median-income`

**Status:** 🛑 **At Stop C** (2026-10-24). Tasks 6–7 done; see [Stop C review](#stop-c-review-chunk-2). Waiting for the expert to run `inv_001`–`inv_003` in fresh sessions and review outputs, tests and code. Then task 8 (retro).

**Exercises (capability checklist):** no new item; it reuses API resource, `within`, reliability flag and choropleth. New smaller cases, below the level of the checklist: `measure: median` with no crosswalks, blank values that are expected rather than errors, table-specific top- and bottom-coded values, and a dollar format on the map.

**Carried over from chunk 1:** run `inv_001` and `inv_002` from the plain prompt in a fresh session. Do this **before** design issue 1 changes `inv_001`, so the result is recorded against the chunk 1 version.

**Task 1 results (2026-10-24, fresh sessions, run by the expert; working tree checked afterwards: no files created or changed):**

- `inv_001` ("Show me median household income by block group."): ✅ **pass.** The agent said there's no spec for median household income, listed the available Indicators and Visualizations, and created nothing.
- `inv_002` ("Map the population count by block group in Cleveland."): ✅ **pass.** It went through `lib.runner`, which reported both specs up to date, so nothing was rebuilt.

#### Requirements

**Specs to draft** (all `status: draft`)

| ID | Type | Settings |
|---|---|---|
| `median_household_income` | Indicator | `measure: median`; `geography: bg_2020`; no `crosswalks`; `data`: `census_api`, `acs/acs5` 2024, `B19013_001E` (Median household income in the past 12 months, in 2024 inflation-adjusted dollars; `_M` pulled automatically); `reliability: {cv_threshold: 0.30, low: flag}`; `unit: dollars` (design issue 4) |
| `map_median_household_income__bg_2020` | Visualization | `indicator: median_household_income`; `geography: bg_2020`; `classification: quantile`; `classes: 5`; `colors: Greens`; tooltip shows the standard fields only (name, estimate, MOE, reliability), in dollars |

Used unchanged: `census_api`, `cle_city`, `bg_2020`. This chunk doesn't use `bg_2020__to__cle_city`.

**Computation** (to be written into the Indicator body)

1. Pull `B19013_001E` and `B19013_001M` for every block group in Cuyahoga County (state `39`, county `035`).
2. Keep the block groups in `bg_2020`. Every `bg_2020` unit must have a **row**. A missing row is an error. A blank **value** with a note is allowed (design issue 3).
3. **Annotations**: same rule as `population_count`. If the estimate or the MOE is an annotation, the value is blank and the annotation goes in `note`. Medians are often `-666666666` (too few sample cases) at block group level.
4. **Top- and bottom-coded values**: an estimate of `250001` ("$250,000 or more") or `2499` ("under $2,500") is a placeholder, not a measured value. The value is blank, and `note` reads "top-coded: $250,000 or more" or "bottom-coded: under $2,500" (design issue 2).
5. `estimate` = B19013_001E, `moe` = B19013_001M.
6. **Reliability**: CV = (MOE ÷ 1.645) ÷ estimate. `low` if CV > 0.30, otherwise `ok`. Low values are flagged and kept.

**Caveats** (to be written into the Indicator body): values are in 2024 inflation-adjusted dollars. A median can't be summed or averaged across block groups, so there's no citywide value in this chunk. Blank block groups appear gray on the map.

**Outputs** (each with its manifest)

- `outputs/tables/median_household_income__bg_2020.csv`
- `outputs/visualizations/map_median_household_income__bg_2020.html`

No city table.

**Tests**

- **Spec validation** passes for the whole project.
- **`kat_002`: Median household income, one block group.** Compares one `bg_2020` value with its published ACS 2020–2024 5-year `B19013_001` value on data.census.gov. Tolerance: `exact`, because the value comes from the same source with no computation. This tests fetching, the GEOID join, and the output, not the method. The agent proposes a block group with a non-blank, non-coded value and a link, and the expert confirms it.
- **`inv_001`**: new prompt (design issue 1).
- **`inv_003`: Plain-language income map.** Prompt: "Map median household income by block group in Cleveland." Expected: `runs`, `spec: map_median_household_income__bg_2020`.

**Not in this chunk:** a citywide median, B19001 income brackets, per capita or mean income, poverty (`C17002`), tracts, neighborhoods.

#### Design issues

1. **`inv_001` stops being an unknown indicator.** Its prompt is "Show me median household income by block group," which this chunk makes available. Proposed new prompt: "Show me median gross rent by block group." Keep the test's ID and intent.
2. **Top and bottom coding aren't annotations.** `lib/census.py` treats only negative codes as annotations, so `250001` and `2499` would pass through as real values. The placeholder values are specific to each table (other medians use other caps), so they don't belong in `lib/`. Proposed: add a `B19013` note under `census_api` `# Notes` (§ 4.1, table-specific notes), and blank these values in the Indicator's compiled code, as in Computation step 4. No `lib/` change. Editing `census_api` sets it back to `draft` (rule 7).
3. **Expected blanks.** `population_count` treats a missing value as an error. For medians, blanks are normal. Proposed: § 12 *Output tables* says "a missing unit (row) is an error; a blank value with its reason in `note` is allowed." Confirm that no `lib/` check treats blank values as an error. (`output.py` already keeps blanks blank.)
4. **Dollar format.** `choropleth.py` formats values as either counts (`,.0f`) or percents. Proposed: add an optional `unit` field to Indicator (`count` by default, or `dollars`; percent still comes from `measure`). Update § 4.4, the Indicator template, the validator, and the tooltip and legend formats (`$,.0f`). This is a `lib/` change, so it needs review, and every result reruns.

Not issues (checked in the code): the validator requires `# Aggregation` only for a median *with* crosswalks; the runner handles an Indicator with no `crosswalks`; `exact` tolerance already exists in `known_answers.py`.

Proposed: apply 1–4 before drafting specs.

Applied 1–4 on 2026-10-24: `inv_001` prompt → "Show me median gross rent by block group."; `census_api` `# Notes` B19013 (now `draft` again, per rule 7); architecture.md § 12 *Output tables* (a missing unit is an error, a blank value isn't, and its `reliability` is blank); `unit` field in § 4 and § 4.4, the Indicator template, and validation.md's list of fields with fixed choices. Issue 3 check: no `lib/` check treats a blank value as an error (`moe.reliability` leaves `reliability` blank, `choropleth` draws gray and leaves blanks out of the breaks, `output` keeps blanks blank; `crosswalk.apply_count` stops on blanks, but only for counts moved through a crosswalk).

**Task 4 findings (2026-10-24):** `B19013_001E` = "Median household income in the past 12 months (in 2024 inflation-adjusted dollars)", `_M` listed. Published at block group level: all 429 `bg_2020` units have a row. Codes, per the Census Bureau's annotation notes: `2499` = "2,500-" and `250001` = "250,000+", each with MOE `-333333333` ("median falls in the lowest or highest interval of an open-ended distribution"). In Cleveland: 90 block groups have estimate `-666666666` (MOE `-222222222`), 4 are bottom-coded, 0 are top-coded (9 elsewhere in the county). That leaves **335** block groups with a value and **94** blank.

#### Stop B questions (chunk 2) — answered 2026-10-24

1. **`kat_002`:** the agent proposes block group `390351198002` (Block Group 2, Tract 1198): **$42,344 ± $13,701**, near the middle of Cleveland's values, published and uncoded. Confirm on <https://data.census.gov/table/ACSDT5Y2024.B19013?g=1500000US390351198002>. → **Confirmed.**
2. **`census_api` re-approval:** it went back to `draft` when the B19013 note was added. Until you approve it again, chunk 1's outputs can't run in run mode. → **Approved;** `census_api` is `stable` again.
3. **Annotation rule wording** (Computation steps 3–4): drafted so that if the estimate *or* the MOE is an annotation, **both** `estimate` and `moe` are blank. Coded values (whose MOE is `-333333333`) get only the coded note ("bottom-coded: under $2,500"), not the annotation code. OK? → **OK.**
4. **A mismatch found in chunk 1's reviewed code:** `population_count`'s spec (step 3) says a block group whose estimate *or* MOE is an annotation gets a blank value. Its code blanks only the field that holds the annotation, so an annotated MOE would leave the estimate in place. This has no effect on current data (no B01003 block group has an annotation). Proposed: add one shared helper in `lib/census.py` (estimate + MOE + note, with the both-blank rule), use it in both Indicators, and recompile `population_count` for your review. Its results would rerun with the same values. Or leave `population_count` alone and note it. → **Expert: if only the MOE is an annotation, the estimate stays.** So the spec changes, not the helper: `population_count` step 3 now says an annotated estimate blanks both, and an annotated MOE alone blanks only `moe`. Step 8 was added (blank estimate or MOE → blank `cv` and `reliability`), and step 2 now says *row*, matching § 12. The spec is `draft` again (rule 7) and its code is stale. The code needs one change, recompiled in task 6: blank `moe` when the estimate is an annotation (it currently keeps it).

**Follow-ups (answered 2026-10-24):**

- **City total with blank parts → option B.** The sums use the block groups that have a value, and `note` says how many were left out. Written into `population_count` step 5. Needs a `lib/` change in task 6: `crosswalk.apply_count` currently stops on any blank.
- **General principle (expert):** compute with flagged uncertainty rather than stop. Stop only for structural problems. Added to architecture.md § 12 *Output tables*.
- **Consistency:** `median_household_income` step 3 now uses the same annotation rule as `population_count` (an annotated estimate blanks both; an annotated MOE alone blanks only `moe`). Step 4 (coded values) overrides it. Step 6 matches `population_count` step 8.

#### Stop C review (chunk 2)

**Results**

- `median_household_income__bg_2020`: 429 rows. **335** have a value ($6,130–$158,438). **94** are blank: 90 with `B19013_001E=-666666666; B19013_001M=-222222222` and 4 `bottom-coded: under $2,500`. Reliability: 198 `ok`, 137 `low` (CV max 0.60), 94 blank. Every blank value has blank `moe`, `cv` and `reliability`.
- Map: quantile breaks $27,071 / $38,494 / $47,276 / $59,577 (from the 335 values); legend and tooltip in dollars; blanks gray.
- `kat_002`: **pass** (42,344 = 42,344, exact). `kat_001`: **pass** (366,340, +0.07%), unchanged.
- `population_count` (recompiled): same values as chunk 1 (429 block groups, city 366,340 ± 7,663, 292 `ok` / 137 `low`). No block group has a blank estimate or MOE, so the new partial-sum note doesn't appear.
- Spec validation: 0 errors. Warnings are only "draft / unreviewed" (expected). Field check: B19013_001E label matches.
- A `lib/` change made every result rerun on its own (`lib_hash`, from the chunk 1 retro), with no `--force`.
- No API key in `data/`, `outputs/`, `build/`, code, or specs.

**Invocation tests (expert, fresh sessions, plain prompts, 2026-10-24):**

- `inv_001` ("Show me median gross rent by block group."): ✅ **pass** (reported by the expert).
- `inv_002` ("Map the population count by block group in Cleveland."): resolved to `map_population_count__bg_2020` and went through `lib.runner`. The runner, in run mode (the default), refused: `population_count` is `draft` with unreviewed code. **Routing passed; no output**, as run mode requires.
- `inv_003` ("Map median household income by block group in Cleveland."): resolved to `map_median_household_income__bg_2020` and went through `lib.runner`. Run mode refused: the map and Indicator are `draft`, and the code is unreviewed. **Routing passed; no output**, as run mode requires.
- **Retro note:** `runs` tests run before approval always hit run mode's refusal, so they test routing but not the run itself. Options: (a) at Stop C, approve first (`verified`, `stable`), then run the invocation tests; (b) define `runs` as "resolves to `spec` and invokes the runner", and accept a readiness refusal as a pass while specs are `draft`.

**To review**

- `lib/` changes: `census.py` (new `estimate_moe` helper; **bug fix** in `read`: the annotation note was filled with a printed copy of a whole pandas column, an f-string bug latent since chunk 1 that B19013 exposed); `crosswalk.py` (`apply_count` sums the values it has and notes what's missing, with a `label` for the unit name, instead of stopping); `choropleth.py` + `runner.py` (`unit: dollars` → `$,.0f`); `validate.py` (`unit` choices).
- `pipeline/indicators/population_count.py` (recompiled: uses `estimate_moe`, city note label) and `pipeline/indicators/median_household_income.py` (new). Each needs a `verified` line.
- Specs to set `stable`: `population_count`, `median_household_income`, `map_median_household_income__bg_2020`.

#### Tasks

1. Run the carried-over invocation tests (`inv_001`, `inv_002`) from the plain prompt in a fresh session, and record the results.
2. Create `chunk/02-bg-median-income` from `main`.
3. Apply design issues 1–4.
4. Check `B19013_001E` against `variables.json` for `acs/acs5` 2024. Confirm that B19013 is published at block group level, and record the top- and bottom-code values it uses.
5. Draft the two specs, update each folder's `index.md`, add `kat_002` (with a proposed block group) and `inv_003`, and update `inv_001`. 🛑 **Stop B.**
6. Extend `lib/` for `unit: dollars`. Compile `pipeline/indicators/median_household_income.py`.
7. Run validation, `kat_001`, `kat_002` and the invocation tests, then produce the outputs. 🛑 **Stop C.**
8. Retro per the working method.

#### Decisions (2026-10-24)

- **Indicator:** median household income, `B19013_001E`, ACS 2020–2024 5-year.
- **Geography:** block group only. The citywide median is deferred.
- **Top- and bottom-coded values:** blank, with a note.
- **Reliability:** CV 0.30, flag.
- **Map:** quantile, 5 classes, `Greens`.
- **Visualization reuse:** keep one Visualization spec per map, even though this map's settings nearly match chunk 1's. Shared defaults are recorded as future scope in [architecture.md § 13](architecture.md#13-deferred) (*Shared Visualization defaults*), with the triggers for revisiting them.

**Other income variables considered (for later chunks):** B19001 households by income bracket (16 brackets, `percent`, aggregates to the city through `nested`, and is the basis for a citywide median); B19301 per capita income, or B19313 aggregate income ÷ B01003 population (a ratio that could build on `population_count`); B19025 aggregate household income ÷ households (mean household income); C17002 ratio of income to poverty level (the block-group-level poverty table, because B17001 isn't published for block groups).

---

## Completed chunks

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
