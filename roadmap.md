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
- ☑ Invocation tests (chunk 1; `inv_001` and `inv_002` passed from the plain prompt in fresh sessions, 2026-10-24; `inv_001`–`inv_003` passed after approval in chunk 2; `inv_001`–`inv_005` in chunk 3)

**Resources & geographies**
- ☑ API resource (Census Data API) (chunk 1)
- ☑ Local file resource (chunk 3: `cle_crime` GeoPackage, named fields only, offline field check)
- ☑ Point dataset (chunk 3: incident points, EPSG:3857 → 3734, clipped to a Geography)
- ☑ Geography from Census boundary files (chunk 1: cartographic boundary file, fetched by URL)
- ☑ Geography from a local file (chunk 1: city GeoPackage; neighborhoods not yet)
- ☑ Geography selection rule (`within`, `majority_area`) (chunk 1)
- ☑ Census request extent derived from the Geography (`census_unit`) (chunk 2)

**Indicators**
- ☑ Count, with margin of error (chunk 1)
- ☐ Percent or rate (counts first, then rate)
- ☑ Reliability flag (chunk 1); suppress not yet
- ☐ Median or other custom aggregation
- ☐ Indicator that builds on other Indicators
- ☑ Selection of points (`measure: points`, `window` in local dates) (chunk 3)
- ☐ Point aggregation

**Crosswalks**
- ☑ `nested` (chunk 1: only `from.within == to` with one target unit)
- ☐ `population_weighted`
- ☐ `areal` / `centroid`

**Visualizations**
- ☑ Choropleth with tooltips (chunk 1)
- ☑ Hexbin heat map, 250 m privacy floor (chunk 3)

---

## Current chunk

### Chunk 4a — 2010 tract median household income, matched to 2020 tracts

**Analysis question (chunks 4a + 4b):** how has median household income changed at the census tract level between 2010 (ACS 2006–2010) and 2024 (ACS 2020–2024)? 4a puts both medians on 2020 tracts. 4b computes the change.

**Why tracts:** the Census API has no 2006–2010 block group data ([Task 2 findings](#task-2-findings-2026-10-25)). Decision 10.

**Brief:** the first tract Geographies, the first Indicator on an older boundary vintage, and the first crosswalk that can carry a median.
- Two new Geographies, `tract_2010` and `tract_2020`.
- A second ACS vintage (2006–2010) at tract level, and the 2020–2024 median at tract level.
- A new crosswalk method, `matched`. It copies a value 1:1 from a 2010 tract to a 2020 tract only when their land areas overlap almost completely, both ways. Every other 2020 tract is blank, with a note.
- Existing Census Indicators are renamed with their ACS end year (architecture.md § 4.4 *Vintages and change over time*).
- **Go/no-go gate for 4b.** At Stop C, the expert sees how many 2020 tracts have both values, then decides whether 4b goes ahead.

**Branch:** `chunk/04a-tract-2010-income` (renamed from `chunk/04a-bg-2010-income` in task 1b).

**Status:** ✅ Stop A passed 2026-10-25 for the tract version: requirements and design issues 1–8 approved, Stop A question 1 answered (decision 11). ✅ Stop B passed 2026-10-25 (decision 12). Tasks 5–6 done. Expert approved 2026-10-25 (decision 13). 🛑 **Stop C, remaining:** the expert runs `inv_001`–`inv_008` in fresh sessions and decides on 4b.

**Exercises (capability checklist):**
- New items to add: tract Geography (`census_unit: tract`); file Resource fetched by URL (delimited text); a Geography on 2010 boundaries; `matched` crosswalk; a median moved through a crosswalk (`# Aggregation`).
- *Indicator that builds on other Indicators* stays ☐ until 4b.

_Place and unit words in this section are requirements. They do not go into the Indicator body (chunk 2, design issue 5)._

#### Requirements

**Specs to draft or change** (all `status: draft`)

| ID | Type | Settings |
|---|---|---|
| `census_api` (changed) | Resource | Add `{ dataset: acs/acs5, vintage: 2010 }` to `datasets`. About: vintage 2010 is the 2006–2010 5-year estimate, on 2010 census geography, published down to tracts (block groups start at vintage 2013). Notes: anything about 2010 found in task 2 (annotation codes, coded values). |
| `census_tract_relationship_2020_2010` | Resource | The Census Bureau's 2020 ↔ 2010 census tract relationship file, Ohio state file. A file Resource at a URL; no `auth`, no `datasets`. Body: About (publisher, URL, one row per 2020 × 2010 tract pair that overlaps), Schema (the GEOID and land-area fields used), Notes (land area only, from full-resolution TIGER; no population or housing counts; UTF-8 with BOM if, like the block group file, it has one). URL and field names confirmed in task 2. |
| `tract_2010` | Geography | Census 2010 cartographic boundary file for Ohio tracts (1:500,000, the same kind as `bg_2020`); `id_field: GEO_ID`, read as the 11-digit tract GEOID (design issue 6); `within: cle_city`; `within_rule: majority_area`; `census_unit: tract`. |
| `tract_2020` | Geography | Census 2020 cartographic boundary file for Ohio tracts (1:500,000); `id_field: GEOID`; `within: cle_city`; `within_rule: majority_area`; `census_unit: tract`. |
| `tract_2010__to__tract_2020` | Crosswalk | `method: matched`; `weights_source: census_tract_relationship_2020_2010`; `min_overlap: 0.80` (decision 6). |
| `median_household_income_tract_2010` | Indicator | `measure: median`; `unit: dollars`; `geography: tract_2010`; `crosswalks: [tract_2010__to__tract_2020]`; `data`: `census_api`, `acs/acs5` 2010, `B19013_001E` "Median household income in the past 12 months (in 2010 inflation-adjusted dollars)"; `reliability: { cv_threshold: 0.30, low: flag }`. Body follows `median_household_income_2024`, plus `# Aggregation`. |
| `median_household_income_tract_2024` | Indicator | As `median_household_income_2024`, with `geography: tract_2020` and no crosswalks (design issue 8). |
| `map_median_household_income_tract_2010__tract_2020` | Visualization | `indicator: median_household_income_tract_2010`; `geography: tract_2020`; `classification: quantile`; `classes: 5`; `colors: Greens` (decision 8). |
| Renamed (design issue 1) | Indicator, Visualization | `population_count` → `population_count_2024`, `median_household_income` → `median_household_income_2024`, and their maps → `map_population_count_2024__bg_2020`, `map_median_household_income_2024__bg_2020`. Titles name the ACS period and the unit (e.g. "Median household income by block group, 2020–2024"), because the agent matches prompts against titles. |

Used unchanged: `cle_city`, `bg_2020`, `bg_2020__to__cle_city`.

**Matching rule** (Crosswalk body and `lib/crosswalk.py`)
- For each pair of a 2010 tract *a* and a 2020 tract *b* in the relationship file, the shared land area is `AREALAND_PART`.
- *a* and *b* **match** when the shared land area is at least `min_overlap` of *a*'s land area **and** at least `min_overlap` of *b*'s. With `min_overlap` above 0.5, each unit has at most one match.
- A 2020 tract with a match takes its 2010 tract's `estimate`, `moe` and `note` unchanged.
- A 2020 tract with no match, or whose match isn't in `tract_2010` (e.g. it straddles the city line differently), is blank, with `note` "no matching 2010 tract".
- The build file `build/crosswalks/tract_2010__to__tract_2020.csv` lists every overlapping pair with both overlap shares and whether it matched, so the threshold can be reviewed and tuned at Stop C by editing frontmatter (no recompile).

**Computation** (both new Indicator bodies, without place names): the same as `median_household_income_2024`.
1. Annotations as in `census_api` § Notes.
2. Top- and bottom-coded values blank, with the coded meaning in `note` (codes for 2010 confirmed in task 2).
3. Otherwise, `estimate` and `moe` are the published values.

**`# Aggregation`** (2010 Indicator body): a median can't be split or summed, so it moves only through a crosswalk that pairs units one to one. The value is the source unit's published median, unchanged; units without a pair are blank.

**Caveats** (2010 Indicator `# Caveats`, without place names)
- Values are in 2010 inflation-adjusted dollars. They are not comparable with later years until adjusted (chunk 4b).
- The 2006–2010 estimates were controlled to the population estimates of the time, not to the 2010 census counts.
- Through a matched crosswalk, a unit's value is its matched source unit's: their land areas differ by up to `1 − min_overlap`, and land area isn't the same as where households are.
- Units with too few sample cases, coded values, or no match are blank.

Geography caveat (`tract_2010` and `tract_2020` bodies): tracts are larger than block groups, so the majority-area rule moves more area in or out of the city at the boundary, and tract totals differ more from the city's exact boundary.

**Outputs** (each with its manifest)
- `outputs/tables/median_household_income_tract_2010__tract_2010.csv` and `…__tract_2020.csv`
- `outputs/tables/median_household_income_tract_2024__tract_2020.csv`
- `outputs/visualizations/map_median_household_income_tract_2010__tract_2020.html`
- The renamed outputs of the four renamed specs. Values unchanged; the old files are removed from `outputs/`.
- `build/crosswalks/tract_2010__to__tract_2020.csv` (not committed)

**Go/no-go summary** (in Stop C's notes, from the build file and the tables; no new spec)
- 2020 tracts with a 2010 match, at `min_overlap` 0.80, 0.90 and 0.95.
- Of those, how many have both a 2010 and a 2020–2024 value, so a change can be computed in 4b.
- The map, to see where the blanks fall.

**Tests**
- **Spec validation** passes for the whole project, including the checks from design issues 3, 4 and 8.
- **`kat_003`** (exact): `median_household_income_tract_2010` at `tract_2020`, for a 2020 tract whose matched 2010 tract has a **different** GEOID if one exists, so the test covers the match and not only the fetch. Value from the Census API, confirmed by the expert.
- **`kat_004`** (exact): `median_household_income_tract_2024` at `tract_2020`, one tract. Value from the Census API, confirmed by the expert.
- `kat_001` and `kat_002` still pass under their renamed Indicators.
- **Invocation:**
  - `inv_002`, `inv_003`: specs renamed; prompts unchanged (they name block groups, so only one spec matches).
  - `inv_006`, income map with no year or unit. Prompt: "Map median household income in Cleveland." Expected: `asks`: the agent asks which one, names the available years and units (2020–2024 by block group; 2006–2010 by tract), and runs nothing until answered (decision 7).
  - `inv_007`, 2010 map. Prompt: "Map median household income in 2010 by census tract." Expected: `runs`, `spec: map_median_household_income_tract_2010__tract_2020`.
  - `inv_008`, change isn't available yet. Prompt: "How has median household income changed by census tract since 2010?" Expected: `not_available`. The agent must not compare the tables outside a spec.
  - Existing `inv_001`, `inv_004`, `inv_005` still pass.

**Not in this chunk:** change or percent change, inflation adjustment, `builds_on`, diverging maps (all 4b); block groups for 2006–2010; household-weighted overlap; other vintages; a 2020–2024 tract map.

#### Design issues

Found by checking the requirements against architecture.md, AGENTS.md, validation.md, the templates and `lib/`. Proposed fixes:

1. **Rename Census Indicators with their ACS end year** (§ 12 naming, already in architecture.md).
   - Move the two Indicator specs and their compiled code; update the code's `# spec:` path. The spec hash is unchanged (the ID isn't in the text), but the code hash changes, so the expert re-verifies and results rerun.
   - Rename both maps; update `indicator:`, `kat_001`, `kat_002`, `inv_002`, `inv_003` and the `index.md` files.
   - Every edited `stable` spec goes back to `draft`. Outputs must be byte-identical apart from names and `created`.
2. **Prompts that match several specs.** AGENTS.md rule 1 already says to ask. Extend it: when several match, ask which one, listing the matching specs and what tells them apart (e.g. the available years and units). Add `inv_006`.
3. **`matched` crosswalk method** (§ 4.3 table, § 12 *Counts first*, Crosswalk template, validation.md, `lib/validate.py`):
   - New method: pairs units one to one by reciprocal land-area overlap (rule above). New Crosswalk field `min_overlap` (above 0.5 and at most 1), required for `matched` only. `matched` requires `weights_source` (the relationship Resource) and has no `weights`.
   - § 12: "Crosswalks move counts only, never percentages or medians", **except `matched`**, which copies a value unchanged. A `median` or `index` still needs `# Aggregation` to use it.
4. **`lib/` for `matched`:**
   - `crosswalk.build` reads the relationship file through a snapshot and writes the build file with both overlap shares.
   - New `crosswalk.apply_matched` copies `estimate`, `moe` and `note`, and writes the "no matching" note.
   - `runner.report` uses it for any `measure` when the method is `matched`; other methods still move counts only.
5. **A file Resource at a URL, as delimited text** (§ 10 already allows a file at a URL). Snapshot the whole file once; read only the named columns, with GEOIDs as text and the BOM removed. The offline field check (validation.md) covers it.
6. **GEOID for `tract_2010`.** The 2010 cartographic files have `GEO_ID` (`1400000US` + the 11-digit tract GEOID for tracts; confirmed for block groups in task 2). `lib/geography` reads a Census `GEO_ID` as its GEOID for a Geography with `census_unit`, documented in § 4.2. Not TIGER/Line: its shapes extend into Lake Erie, which would change the majority-area rule for lakeshore units.
7. **Tract requests and 2010 data** (`lib/census`): check that `requests_for` handles `census_unit: tract` (unused so far) for vintages 2010 and 2024, and record 2010 annotation codes and coded values in `census_api` § Notes.
8. **The same published value at a second Census unit** (§ 12 naming, § 4.4).
   - A median can't move from block groups to tracts, so the tract median is pulled at tract level. That makes it a separate Indicator.
   - Proposed naming: for a Census unit other than the block group, the ID puts the unit before the year: `median_household_income_tract_2024`, `median_household_income_tract_2010`. Block group stays unnamed, as the default unit.
   - Alternative, not proposed for a proof of concept: an `# Aggregation` method "use the published value at the target unit" through a block group → tract crosswalk, so one Indicator covers both units. More general, more `lib/` work. Revisit if many measures need tracts.

Proposed: apply 1–8 after task 2's checks, before drafting specs.

#### Stop A questions

Answered 2026-10-25. Block group version: decisions 5–9. Tract version: decision 11.

#### Tasks

1. ✅ Commit the chunk 4a plan on `main`, then create the branch. (Done 2026-10-25, as `chunk/04a-bg-2010-income`.)
   - 1b. Rename the branch to `chunk/04a-tract-2010-income` and commit this rewrite and the task 2 findings.
2. **Check the sources for tracts** (network needed). 🛑 **Stop and discuss if any check fails.**
   - The Census API serves `acs/acs5` 2010 and 2024 `B19013_001E`/`_001M` at tract level for Cuyahoga County. Record the request syntax, annotation codes, and top- and bottom-coded values for 2010.
   - The 2010 cartographic tract file for Ohio (expected `…/GENZ2010/gz_2010_39_140_00_500k.zip`): URL, fields, coordinate system.
   - The 2020 cartographic tract file for Ohio (expected `…/GENZ2020/shp/cb_2020_39_tract_500k.zip`): URL, fields, coordinate system.
   - The tract relationship file for Ohio (expected `…/rel2020/tract/tab20_tract20_tract10_st39.txt`): URL, fields, and the land-area columns.
3. Apply design issues 1–8. Do the rename (issue 1) first and confirm outputs are unchanged and `kat_001`/`kat_002` pass.
4. Draft the new specs, update `census_api` and each folder's `index.md`, and add `kat_003`, `kat_004` and `inv_006`–`inv_008`. 🛑 **Stop B.**
5. Build the `lib/` changes (issues 3–7). Compile `pipeline/indicators/median_household_income_tract_2010.py` and `…_tract_2024.py`.
6. Run validation, known-answer tests and invocation tests, and produce the outputs. Write the go/no-go summary. 🛑 **Stop C:** the expert reviews, sets `min_overlap`, and decides on 4b.
7. Retro per the working method.

#### Stop C notes (2026-10-25)

**`lib/` changes (design issues 3–7; need the expert's review):**
- `geography.load`: for a Geography with `census_unit` and `id_field: GEO_ID`, keeps the part after `US`.
- `crosswalk`: `build` dispatches `matched` to new `build_matched` (reads the relationship file through a snapshot, writes the build file with `from_share`, `to_share`, `matched`, `from_in_geography`, `to_in_geography`, for pairs that touch either Geography; returns the matched pairs inside both; stops if a unit has two matches). New `read_delimited` (named columns only, all text, BOM removed, delimiter from the header). New `apply_matched` (copies `estimate`, `moe`, `note`; blank with "no matching 2010 tract" otherwise).
- `runner.report`: a `matched` crosswalk uses `apply_matched` for any measure; the note label comes from the `from` Geography's boundary year and `census_unit`. The relationship snapshot goes into `data` in the manifest, and `min_overlap` into `built_from`.
- `validate`: `matched` allowed; checks its fields (`weights_source`, `min_overlap` in (0.5, 1], the five `fields`, a `from` with `census_unit`, a file Resource as `weights_source`); offline check that `fields` columns exist in the snapshotted file.
- `census.requests_for` needed no change: tract requests work for vintages 2010 and 2024.

**Compiled code (unreviewed):** `median_household_income_tract_2010.py` and `median_household_income_tract_2024.py`. Their `# Computation` is word-for-word the same as `median_household_income_2024`'s, so the body is the reviewed 2024 code (the 2010 docstring also mentions the matched crosswalk). Also to re-verify: `population_count_2024.py`, `median_household_income_2024.py` (headers only changed).

**Results:**
- Validation: 0 errors offline and with `--network`; the official labels of all four field codes match the specs. Remaining warnings: unreviewed code and `draft` specs.
- Known-answer tests: `kat_001`, `kat_002`, `kat_003`, `kat_004` pass (the last three exact).
- Existing outputs: after the `lib/` changes, the five renamed outputs and the crime heat map are byte-identical to the pre-chunk files.
- Matched values: in all 136 matched pairs, the 2020 tract's `estimate`, `moe`, `note`, `cv` and `reliability` equal its 2010 tract's.
- New outputs: `outputs/tables/median_household_income_tract_2010__tract_2010.csv` (177 tracts), `…__tract_2020.csv` (159), `outputs/tables/median_household_income_tract_2024__tract_2020.csv` (159), `outputs/visualizations/map_median_household_income_tract_2010__tract_2020.html`, and `build/crosswalks/tract_2010__to__tract_2020.csv`.

**Go/no-go summary for 4b** (159 2020 tracts in the city; 177 2010 tracts):

| `min_overlap` | 2020 tracts matched | matched, but 2010 tract not in `tract_2010` | with a 2010 value | with both a 2010 and a 2020–2024 value |
|---|---|---|---|---|
| 0.80 | 136 (86%) | 0 | 134 | 130 (82%) |
| 0.90 | 134 (84%) | 0 | 132 | 128 (81%) |
| 0.95 | 131 (82%) | 0 | 129 | 125 (79%) |

At 0.80: 23 2020 tracts have no match; 2 matched tracts have no 2010 value (too few sample cases); 8 tracts have no 2020–2024 value (too few sample cases). No 2010 or 2020–2024 tract in the city is top- or bottom-coded. At 0.90 or above, `kat_003`'s tract no longer matches (its overlap is 83.1%), so the test would need replacing. The map shows where the blanks fall.

#### Stop B notes (2026-10-25)

**Task 3 done.** Rename (design issue 1): the four specs and two code files moved, titles name the ACS period, all four back to `draft`. The titles changed the spec hashes, so both code headers were regenerated (body unchanged, no `verified` line): **the expert re-verifies `population_count_2024` and `median_household_income_2024`.** The five renamed tables and maps are byte-identical to the old ones; `kat_001` and `kat_002` pass. Design issues 2–8 written into AGENTS.md rule 1, architecture.md §§ 2, 4, 4.2, 4.3 (new *matched* subsection), 4.4, 7, 10, 12, 13, the Crosswalk and Geography templates, and validation.md. `lib/` is task 5.

**Task 4 drafts** (all `draft`): `census_api` (vintage 2010 added; About and Notes for 2010; back to `draft`), `census_tract_relationship_2020_2010`, `tract_2010`, `tract_2020`, `tract_2010__to__tract_2020`, `median_household_income_tract_2010`, `median_household_income_tract_2024`, `map_median_household_income_tract_2010__tract_2020`; every `index.md`; `kat_003`, `kat_004`, `inv_006`–`inv_008`. Validation now has 4 errors, all expected until task 5: `matched` isn't a known method yet, and the two new Indicators have no compiled code. With `--network`: the official labels of all three `B19013_001E` fields match the specs. The publication check for `median_household_income_tract_2010` can't run until `lib/` reads `GEO_ID` (task 5). Other publication and `variables.json` checks failed only intermittently, because the Census API was timing out on 2026-10-25; the direct requests in task 2 show both vintages are published at tract level. Rerun at Stop C.

**Questions for the expert**

1. **`fields` on a `matched` Crosswalk (new, not in the approved design).** The builder has to know which relationship-file columns to read, and the tract and block group files name them differently (`GEOID_TRACT_20` vs `GEOID_BLKGRP_20`). Proposed: the Crosswalk names them in `fields: { from_id, to_id, from_area, to_area, shared_area }`, which keeps rule 3 (fields are named in an Indicator or Crosswalk) and lets the offline field check cover them. Alternative: `lib/` derives them from the `census_unit`; less to write, but hidden.
2. **Title of `population_count_2024`:** "Total population, 2020–2024", without "by block group", because it's also reported for the city. The income Indicators name their unit.
3. **Name fields:** `tract_2020` uses `NAMELSAD` ("Census Tract 1114.01"); `tract_2010` uses `NAME` ("1114.01"; the 2010 file has no `NAMELSAD`). Only the 2020 names appear on the map.
4. **`kat_003`:** in the city, only one matched 2020 tract has a different GEOID from its 2010 tract: `39035197400` ← `39035106300`, overlap 99.99% / 83.1%. It only matches at `min_overlap` below 0.83, so it has to be replaced if the threshold goes up. Expected values for `kat_003` (36591 ± 5794) and `kat_004` (38083 ± 13217) were read by the agent from the Census API; please confirm.
5. **Early look for the go/no-go** (from the agent's checks of the source files, not from the pipeline; the formal summary is at Stop C): about 159 2020 tracts and 177 2010 tracts are inside the city by the majority-area rule, and about 136 2020 tracts match at 0.80.

#### Task 2 findings (2026-10-25)

1. ❌ **Census API, `acs/acs5` 2010, block groups: not served.** `geography.json` for vintages 2009–2012 lists `tract` but not `block group`. A block group request returns HTTP 400 "unknown/unsupported geography hierarchy", with `in=tract:*` or a single tract. Block groups start at vintage 2013 (2009–2013). The field exists: `B19013_001E` "Median household income in the past 12 months (in 2010 inflation-adjusted dollars)", with attributes `_001EA`, `_001M`, `_001MA`. Annotation and coded values for 2010 were not checked, since there was no block group data to check.
2. ✅ **2010 cartographic block groups, Ohio.** `https://www2.census.gov/geo/tiger/GENZ2010/gz_2010_39_150_00_500k.zip`: 9,234 block groups, EPSG:4269. Fields `GEO_ID` (`1500000US` + 12-digit GEOID; design issue 6 confirmed), `STATE`, `COUNTY`, `TRACT`, `BLKGRP`, `NAME`, `LSAD`, `CENSUSAREA`.
3. ✅ **Relationship file, Ohio.** `https://www2.census.gov/geo/docs/maps-data/data/rel2020/blkgrp/tab20_blkgrp20_blkgrp10_st39.txt`: pipe-delimited, UTF-8 with BOM, 12,710 pairs (1,996 with a Cuyahoga 2020 block group). Fields used: `GEOID_BLKGRP_20`, `GEOID_BLKGRP_10`, `AREALAND_BLKGRP_20`, `AREALAND_BLKGRP_10`, `AREALAND_PART`. No blank GEOIDs.
4. **Alternatives for 2006–2010 block group data** (each one needs the expert):
   - **Census Bureau ACS 2006–2010 summary file**, Ohio, `Tracts_Block_Groups_Only` (`https://www2.census.gov/acs2010_5yr/summaryfile/…/Ohio/Tracts_Block_Groups_Only/`). Same publisher as the API. Zipped sequence files plus a geography file and a sequence-to-table lookup: a new file Resource, with more parsing than the relationship file.
   - **NHGIS** (the roadmap's fallback): the same data, cleaner extracts, but needs an account and a manual or API extract. A new Resource.
   - **Vintage 2013 (2009–2013) from the API**, on 2010 block groups. It doesn't overlap 2020–2024, so a comparison is still allowed, but it changes decision 5 and the analysis question.
   - **Tracts, 2006–2010, from the API.** Changes the geography for 4a and 4b (decision 3 named tracts as a fallback).

**Resolved:** the expert chose tracts (decision 10). Items 2–3 (block group files) are no longer used.

**Tract checks (2026-10-25): all pass.**

5. ✅ **Census API, tracts, vintages 2010 and 2024.** `for=tract:*&in=state:39&in=county:035` returns HTTP 200 for both; a county list (`county:035,093`) works too. Cuyahoga: 447 tracts (2010), 428 (2024). Same field codes in both vintages.
   - **2010 annotation and coded values match 2024's.** Annotations seen: estimate `-666666666` with MOE `-222222222` (too few sample cases). Coded values: `2499` (bottom-coded) and `250001` (top-coded), each with MOE `-333333333`. In Cuyahoga 2010, 4 annotated and none coded. Coded values confirmed from Ohio, New York, California and New Jersey 2010 tracts. 2024 Cuyahoga: 13 annotated, 2 top-coded.
6. ✅ **2010 cartographic tracts, Ohio.** `https://www2.census.gov/geo/tiger/GENZ2010/gz_2010_39_140_00_500k.zip`: 2,948 tracts, EPSG:4269. Fields `GEO_ID` (all `1400000US` + 11 digits; design issue 6 holds), `STATE`, `COUNTY`, `TRACT`, `NAME` (tract number, e.g. `1114.01`), `LSAD`, `CENSUSAREA`.
7. ✅ **2020 cartographic tracts, Ohio.** `https://www2.census.gov/geo/tiger/GENZ2020/shp/cb_2020_39_tract_500k.zip`: 3,162 tracts, EPSG:4269. Fields include `GEOID` (11 digits), `NAME` (tract number), `NAMELSAD`, `ALAND`, `AWATER`.
8. ✅ **Tract relationship file, Ohio.** `https://www2.census.gov/geo/docs/maps-data/data/rel2020/tract/tab20_tract20_tract10_st39.txt`: pipe-delimited, UTF-8 with BOM, 4,301 pairs (631 with a Cuyahoga 2020 tract). Fields used: `GEOID_TRACT_20`, `GEOID_TRACT_10`, `AREALAND_TRACT_20`, `AREALAND_TRACT_10`, `AREALAND_PART`. No blank GEOIDs.
9. **Joins.** API tract GEOIDs (state + county + tract) match the boundary IDs, except tract `39035990000` (Lake Erie, water only, annotated in both vintages), which isn't in either cartographic file. The relationship file rows whose IDs aren't in the boundary files are water-only tracts (`…99xxxx`, land area 0) and one Ohio–Pennsylvania pair. **For `lib/`:** units with zero land area can't have an overlap share, so they never match (no division by zero).

#### Decisions (expert, 2026-10-25)

1. **Approach A:** each vintage is its own Indicator, and the year is never a run-time parameter. Recorded in architecture.md § 4.4 *Vintages and change over time*, §§ 4.1, 12, 13.
2. **Split chunk 4** into 4a (this chunk) and 4b (below). 4b is written in detail after 4a's retro.
3. **Boundary match:** one to one, with units that don't match left blank with a note (compute with flagged uncertainty). If too few units match, rethink or stop.
4. **Accepted caveats:** coded values that don't line up across years after adjustment; possible differences in 2010 annotation codes; 2006–2010 controls to population estimates, not census counts.
5. **"2010" is the ACS 2006–2010 5-year estimate**, compared with 2020–2024 in 4b. The periods don't overlap, as the Census Bureau requires for comparing 5-year estimates.
6. **Overlap source: the Census relationship file** (land area from full-resolution TIGER), not an intersection of the cartographic files, whose 1:500,000 shapes are generalized differently in each vintage. **`min_overlap` starts at 0.80**, tuned at Stop C.
7. **A prompt that matches several specs:** the agent asks which one and names what tells them apart, e.g. the available years and units (AGENTS.md rule 1, design issue 2). No default to the latest.
8. **2010 map included:** `Greens`, quantile, 5 classes. Its classes aren't comparable with the 2024 maps' (different dollars, different units).
9. **`population_count` is renamed too** (`population_count_2024`), so every Census Indicator follows one naming rule.
10. **Tracts, not block groups** (after task 2): the Census API has no 2006–2010 block group data. Chunk 4 uses ACS 2006–2010 tracts from the API, on 2010 tracts matched to 2020 tracts. Not chosen: the 2006–2010 summary file, NHGIS, or 2009–2013 block groups.
11. **Naming for a second Census unit:** the unit goes before the year, e.g. `median_household_income_tract_2024`; block group stays unnamed as the default unit (design issue 8). The `# Aggregation` alternative (published value at the target unit) is not built now; revisit if many measures need tracts.
12. **Stop B (2026-10-25):** drafted specs approved for compiling. Stop B questions 1–5 accepted: `fields` on `matched` crosswalks; "Total population, 2020–2024"; `NAMELSAD` / `NAME`; `kat_003` (36591 ± 5794) and `kat_004` (38083 ± 13217) confirmed. Specs stay `draft` until Stop C.
13. **Stop C approval (2026-10-25):** `lib/` changes and the four code files reviewed; all 12 chunk specs set `stable`, the four code files `verified`. `min_overlap` stays 0.80. Earlier runs of `inv_007` (blocked: specs were still `draft`, so run mode refused; the right behavior, rerun after approval) and `inv_008` (pass) came before approval.

### Chunk 4b — Change in tract median household income, 2010 → 2024 (planned; detailed after 4a's retro)

Only if 4a's go/no-go says so.
- `median_household_income_tract_pct_change_2010_2024` at `tract_2020`: `builds_on` `median_household_income_tract_2010` (reported at `tract_2020` through the matched crosswalk) and `median_household_income_tract_2024`. New `measure: change`; the change math in a `lib/` helper; first runner support for `builds_on`.
- **Inflation:** R-CPI-U-RS (the index the Census Bureau uses for ACS), 2024 annual average ÷ 2010 annual average (320.4), written in the change Indicator's spec with its source. An expert-approved exception to AGENTS.md rule 3 (no Resource for one constant). Read the 2024 value from BLS's current file (BLS reissued the series with corrections in April 2026).
- **Proof of concept:** no significance test. Caveats go in the manifest (a new manifest field), e.g. that MOEs are large and some changes may not be statistically significant.
- Diverging color scheme with fixed breaks around 0.
- Possibly CSV columns for the start and end values.

---

## Completed chunks

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
| 2026-10-25 | Claude Code | Task 1b: branch renamed `chunk/04a-tract-2010-income`, redraft committed. Task 2 (tracts): API serves 2010 and 2024 tracts; 2010 codes match 2024's; 2010 and 2020 cartographic tract files and the tract relationship file confirmed (*Task 2 findings* 5–9). | Task 3: design issues 1–8, rename first. |
| 2026-10-25 | Claude Code | Task 3: rename done (outputs byte-identical, `kat_001`/`kat_002` pass; code needs re-verification); design issues 2–8 in docs. Task 4: specs, indexes, `kat_003`, `kat_004`, `inv_006`–`inv_008` drafted. Proposed `fields` on `matched` crosswalks. | 🛑 Stop B: expert reviews specs and *Stop B notes* questions 1–5. Then task 5 (`lib/`, compile). |
| 2026-10-25 | Claude Code | Stop B passed (decision 12). Task 5: `lib/` for `matched`, `GEO_ID`, delimited files, validation; both tract Indicators compiled. Task 6: validation clean (also `--network`), `kat_001`–`kat_004` pass, existing outputs byte-identical, new tables and map written, go/no-go summary (130 of 159 2020 tracts have both values at 0.80). | 🛑 Stop C: expert reviews `lib/` and code, sets `min_overlap`, decides on 4b, runs `inv_001`–`inv_008`, approves. Then task 7 (retro). |
| 2026-10-25 | Claude Code | Expert approved: 12 specs `stable`, 4 code files `verified`, `min_overlap` 0.80. Validation 0 errors, 0 warnings; manifests refreshed; run mode runs the 2010 map; `kat_001`–`kat_004` pass. | 🛑 Expert runs `inv_001`–`inv_008` in fresh sessions; decides on 4b. Then task 7 (retro). |
| 2026-10-25 | Chat | Expert chose tracts after task 2 (decision 10). Rewrote chunks 4a and 4b for tracts: `tract_2010`, `tract_2020`, `tract_2010__to__tract_2020` (`matched`, 0.80), `median_household_income_tract_2010` and `…_tract_2024`, 2010 tract map; design issue 8 (naming for a second Census unit); `kat_004`; `inv_006`–`inv_008` reworded. | 🛑 Stop A again (tract version, Stop A question 1). Then Claude Code: task 1b, task 2 for tracts. |
| 2026-10-25 | Chat | ✅ Stop A passed for the tract version: expert approved chunk 4a (tracts) requirements and design issues 1–8. Decision 11: `<measure>_tract_<year>` naming. | Claude Code: task 1b (rename the branch to `chunk/04a-tract-2010-income`, commit), then task 2 for tracts. Stop B after specs are drafted. |
