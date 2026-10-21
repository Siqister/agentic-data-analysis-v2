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
- ☐ Python environment, git, `.env`
- ☐ Spec validator
- ☐ Snapshots and manifests
- ☐ Staleness detection (code vs. results)
- ☐ Known-answer tests
- ☐ Run mode

**Resources & geographies**
- ☐ API resource (Census Data API)
- ☐ Local file resource
- ☐ Point dataset
- ☐ Geography from Census TIGER/Line
- ☐ Geography from a local shapefile (neighborhoods)
- ☐ Geography selection rule (`within`)

**Indicators**
- ☐ Count, with margin of error
- ☐ Percent or rate (counts first, then rate)
- ☐ Reliability flag / suppress
- ☐ Median or other custom aggregation
- ☐ Indicator that builds on other Indicators
- ☐ Point aggregation

**Crosswalks**
- ☐ `nested`
- ☐ `population_weighted`
- ☐ `areal` / `centroid`

**Visualizations**
- ☐ Choropleth with tooltips

---

## Current chunk

### Chunk 1 — Block group population count

**Analysis question:** Show me population by block group.

**Brief:** Kept deliberately thin: one count, no percentages. Its purpose is to run every stage of the system once, from start to finish.

**Branch:** `chunk/01-bg-population`

**Status:** 🛑 **At Stop B** (2026-10-21). Tasks 1–5 done. The expert answered all Stop B questions and the specs were updated to match; waiting for the expert's explicit approval of the specs before any code is generated (task 6).

**Exercises (capability checklist):** Python environment, git, `.env` · spec validator · snapshots and manifests · staleness detection · known-answer tests · run mode · API resource · local file resource · geography from Census boundary files · geography from a local file · `within` · count with margin of error · reliability flag · `nested` · choropleth with tooltips

#### Requirements

**Invocation**

- The work is invoked by a plain-language prompt naming an Indicator or Visualization, e.g. "show me population by block group." The agent maps the prompt to a spec ID. If more than one spec could match, it asks.
- The agent carries out the request **only through reviewed code** in `lib/` and `pipeline/`. It never re-derives a computation for a single request.
- **Graph traversal is automatic.** A runner in `lib/` reads the reference fields in spec frontmatter ([architecture.md § 5](architecture.md#5-the-dependency-graph)) and walks down from the requested spec. It then checks staleness, fetches any missing snapshots, computes from the bottom up, runs the tests, and writes outputs with manifests.
- If no spec matches the request, the agent says it isn't available and lists the Indicators and Visualizations that are. It creates, drafts, and fetches nothing.

**Specs to draft** (all `status: draft`)

| ID | Type | Settings |
|---|---|---|
| `census_api` | Resource | `https://api.census.gov/data`; `auth: CENSUS_API_KEY`; `datasets`: `acs/acs5` 2024 (the 2020–2024 5-year) |
| `cle_city` | Geography | `resource: data/static/cle_city/City_Boundary_-6607456956089209299.gpkg`, the City of Cleveland's own boundary, downloaded by the expert. One layer (`City_Boundary`), one multipolygon, EPSG:3734 embedded. Fields: `OBJECTID`, `NAME`, no Census code. `id_field` is decided at Stop B. |
| `bg_2020` | Geography | Census 2020 cartographic boundary file, Ohio block groups (`cb_2020_39_bg_500k`, clipped to the shoreline). `resource: https://www2.census.gov/geo/tiger/GENZ2020/shp/cb_2020_39_bg_500k.zip`, a fixed download URL, not an API. **The agent fetches it automatically** into a snapshot under `data/raw/`; the expert downloads nothing. The agent confirms the URL resolves at Stop B. `id_field: GEOID`; `within: cle_city` with the **majority-area rule**: a block group is in the city if more than 50% of its area is inside `cle_city`, measured in EPSG:3734 |
| `bg_2020__to__cle_city` | Crosswalk | `method: nested`. Valid because `bg_2020` is already limited to block groups in `cle_city`. |
| `population_count` | Indicator | `measure: count`; `geography: bg_2020`; `crosswalks: [bg_2020__to__cle_city]`; `data`: `census_api`, `acs/acs5` 2024, `B01003_001E` (Total population; `_M` pulled automatically); `reliability: {cv_threshold: 0.30, low: flag}` |
| `map_population_count__bg_2020` | Visualization | `indicator: population_count`; `geography: bg_2020`; `classification: quantile`; `classes: 5`; `colors: Blues`; tooltip shows the standard fields only (name, estimate, MOE, reliability) |

**Outputs** (each with its manifest)

- `outputs/tables/population_count__bg_2020.csv`
- `outputs/tables/population_count__cle_city.csv`
- `outputs/visualizations/map_population_count__bg_2020.html`

**Tests**

- **Spec validation** passes for the whole project.
- **`kat_001`: Total population, Cleveland city.** Compares the `cle_city` total (the sum of the included block groups) with the published ACS 2020–2024 5-year `B01003_001` for Cleveland city, Ohio (Census place `3916000`). Tolerance: `relative 2%`. The expert supplies the expected value from data.census.gov, or the agent proposes it with a link and the expert confirms. A gap is expected from two sources: straddling block groups, and differences between the City's boundary and the Census place boundary.
- **`inv_001`: Unknown indicator.** A prompt asks for an indicator that has no spec, e.g. "median household income by block group." Expected behavior: the agent says it isn't available, lists the available Indicators, and creates or fetches nothing.

**Not in this chunk:** tracts, neighborhoods, percentages or rates, census blocks, `population_weighted` crosswalks.

**Accepted limitation:** a choropleth of raw counts partly reflects how large each block group is. That's acceptable here, because the chunk exists to exercise every stage.

#### Design issues

1. **Invocation isn't in architecture.md.** Add: prompt → spec ID → reviewed runner in `lib/`. The runner is generic, so it lives in `lib/`, not `pipeline/`.
2. **Invocation tests are a new kind of test.** Add a short section to `tests/validation.md` defining them (prompt in, expected agent behavior out). The tests themselves go in `tests/invocation.md`.
3. **The `within` rule isn't machine-readable.** Geographies are loaded by helpers from frontmatter, so the rule needs a field, e.g. `within_rule: majority_area | centroid | any`. Update the Geography template.
4. **"Nested" after a `within` filter.** §4.3 should say `nested` is valid when the `from` Geography's `within` equals `to`.
5. **Boundary files aren't snapshotted.** §10 covers Resources only. Geography files need the same treatment. A URL (like `bg_2020`) is fetched once into `data/raw/`, with a `snapshot.yaml` recording the URL, retrieval time, and hash. A local file (like `cle_city`) is hashed in place. Both hashes go in manifests.
6. **Static local files.** `data/static/` isn't in the §11 layout. Add it: not committed, source URL recorded in the spec, file hash recorded in manifests.
7. **`known_answers.md` must be machine-readable.** State that the YAML blocks are the contract and the prose is for people.
8. **Unit codes without a Census code.** `cle_city` has no GEOID, so a known-answer test's `unit` uses whatever `id_field` is chosen.
9. **GeoPackage layers.** The city file has a single layer. If a multi-layer file appears, Geography will need a `layer` field. Not needed now.

Proposed: apply 1–6 before drafting specs, because the build depends on them. Handle 7, 8 and 9 in the retro.

Applied 1–6 on 2026-10-21 (architecture.md §§ 2, 4.2, 4.3, 7, 10, 11, 12; `templates/geography.md`; `tests/validation.md` § 1 and new § 3; new `tests/invocation.md`).

10. **`cle_city` fields differ from the requirements.** The file has `NAME`, `GLOBALID`, `MAINTENANCEID`, `CREATEDBY`, `DATECREATED`, `MODIFIEDBY`, `DATEMODIFIED`; there is no `OBJECTID`. Drafted with `id_field: NAME` (unit code `Cleveland`).

#### Stop B questions (answered 2026-10-21)

1. **`cle_city` `id_field`:** `NAME` (unit code `Cleveland`) as drafted, or `GLOBALID`? → **`NAME`.**
2. **`cle_city` source URL** (task 2): needed for the spec body. → **<https://data.clevelandohio.gov/datasets/fa8ba3c00cf842fd8dd49e8d9e80e268_0>**, added to `cle_city`.
3. **`kat_001` expected value:** the agent proposes 366,097 ± 76 (API, `acs/acs5` 2024, place `3916000`). Confirm on data.census.gov. → **Confirmed.**
4. **Block group names:** the boundary file's name fields hold only "Block Group 2", so `bg_2020` has no `name_field` and the tooltip shows the GEOID. OK? → **OK.**
5. **Zero estimates:** a block group with estimate 0 has no CV. Drafted as `cv` blank, `reliability: low`, note "estimate is 0; CV undefined". OK? → **OK.**
6. **City MOE:** drafted as √(sum of squared MOEs) over all block groups. The Census Bureau's ACS handbook suggests that when several estimates are 0, only the largest of their MOEs is included. Which? → **Expert: whichever is easier.** Kept the plain √(sum of squares) as drafted: simpler, and slightly conservative (larger MOE).
7. **Fetch extent:** the Indicator pulls all Cuyahoga County block groups (state 39, county 035) and keeps those in `bg_2020`. OK? → **OK.**

#### Tasks

1. Make an initial commit on `main` (the repo has no commits yet), then create `chunk/01-bg-population`.
2. Expert: add the source URL for the city boundary file, and the published value and MOE for `kat_001`.
3. Apply design issues 1–6 to architecture.md, the templates, and `tests/validation.md`.
4. Set up uv: Python ≥ 3.11 with pandas, geopandas, shapely, pyyaml and requests, versions pinned.
5. Draft the six specs, update each folder's `index.md`, and add `kat_001` and `inv_001`. 🛑 **Stop B.**
6. Build `lib/`: spec graph and validator, fetch and snapshot (API and local file), load geographies with the `within` rule, apply crosswalk with MOE, reliability, write output with manifest, choropleth (D3 v7, pinned), and the runner.
7. Compile `pipeline/population_count.py`.
8. Run validation, `kat_001` and `inv_001`, then produce the outputs. 🛑 **Stop C.**
9. Retro per the working method.

#### Decisions (2026-10-21)

- **Data:** ACS 2020–2024 5-year, `B01003_001E`.
- **Block group boundaries:** Census 2020 cartographic boundary file, not TIGER/Line, to avoid lake water. The agent fetches it by URL; no manual download.
- **City boundary:** the City of Cleveland's own file, as a GeoPackage (single file, CRS embedded), not the Census place boundary.
- **Straddling block groups:** majority-area rule.
- **City total:** reported through a `nested` crosswalk.
- **Reliability:** CV 0.30, flag.
- **Map:** quantile, 5 classes, `Blues`.
- **`kat_001` tolerance:** relative 2%. Tighten once the actual gap is known.
- **Unknown indicator:** say it isn't available, list what exists, create nothing.
- **Invocation:** by prompt; execution only through reviewed code.
- **Environment:** uv.

---

## Completed chunks

_None yet._

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
