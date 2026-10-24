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
- ☑ Invocation tests (chunk 1; `inv_001` and `inv_002` passed from the plain prompt in fresh sessions, 2026-10-24; `inv_001`–`inv_003` passed after approval in chunk 2)

**Resources & geographies**
- ☑ API resource (Census Data API) (chunk 1)
- ☐ Local file resource (local-file snapshotting exercised through the `cle_city` Geography in chunk 1; no local-file Resource spec yet)
- ☐ Point dataset
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
- ☐ Point aggregation

**Crosswalks**
- ☑ `nested` (chunk 1: only `from.within == to` with one target unit)
- ☐ `population_weighted`
- ☐ `areal` / `centroid`

**Visualizations**
- ☑ Choropleth with tooltips (chunk 1)

---

## Current chunk

### Chunk 3 — Spatial distribution of reported crime incidents

**Analysis question:** where were reported crime incidents located over a set time window? This chunk shows the spatial distribution as a hexbin heat map. Counts ("how many") come in a later chunk that builds on this one.

**Brief:** the first point dataset and the first map that isn't a choropleth.
- The crime incidents file becomes a local-file Resource.
- A new kind of Indicator, a reviewed **selection** of points (`measure: points`), does all the filtering: time window, offense types, incident rule, city clip.
- A hexbin Visualization draws it.
- The heat map embeds only hexes and their classes, never points.

**Branch:** `chunk/03-crime-heatmap`

**Status:** ✅ Stop A passed 2026-10-24: requirements approved by the expert, including the proposed fixes for design issues 1–10 (5 dropped) and the agent's defaults for the Stop A questions (decisions 18–21). Tasks 1–5 done 2026-10-24 (✅ Stop B passed). 🛑 **Stop C:** the expert reviews the outputs, code and `lib/` changes, answers the Stop C questions, tunes `hex_size_m` if wanted, and runs `inv_001`–`inv_005` in fresh sessions. Then task 6 (retro).

**Exercises (capability checklist):**
- Existing items: local file resource, point dataset.
- New items to add: selection Indicator (`measure: points`), hexbin Visualization.
- Point aggregation stays ☐ until the counts chunk.

_Place and unit words in this section are requirements. They do not go into the Indicator body (chunk 2, design issue 5)._

#### Requirements

**Specs to draft** (all `status: draft`)

| ID | Type | Settings |
|---|---|---|
| `cle_crime` | Resource | `resource: data/static/cle_crime/Crime_Incidents_P1RMS_-6429680527207168309.gpkg`; no `auth`, no `datasets`. Body: About (City of Cleveland, Division of Police; portal link; daily updates; downloaded by the expert as a GeoPackage on 2026-10-24), Access (GeoPackage, one layer `Crime_Incidents`, geometry column `SHAPE`, points in EPSG:3857; times stored in UTC), Schema (fields used, with plain meanings, plus the NIBRS Group A/B list of `IncidentDesc` values), Notes (below). |
| `points_reported_crime_incidents` | Indicator | `measure: points`; `geography: cle_city` (clip extent); no `crosswalks`, `reliability` or `unit`; `window: { field: OffenseDate, from: 2025-11-30, to: 2026-09-30 }`; `data`: `cle_crime`, fields `CaseNumber`, `IncidentDesc`, `OffenseDate`, `SHAPE`. |
| `map_points_reported_crime_incidents__cle_city` | Visualization | `map: hexbin`; `indicator: points_reported_crime_incidents`; `geography: cle_city`; `hex_size_m: 500`; `classification: quantile`; `classes: 5`; `colors: Purples` (agent's proposal, see Stop A question 4). |

Used unchanged: `cle_city`. Not used: `census_api`, `bg_2020`, `bg_2020__to__cle_city`.

**Computation** (to be written into the Indicator body, without place names)

1. Read the named fields from the Resource.
2. Keep rows whose `IncidentDesc` is a NIBRS Group A offense type, per the Resource's list. Exclude Group B, rows with no `IncidentDesc`, and Justifiable Homicide (a Group A code that isn't a crime).
3. Keep rows whose `OffenseDate`, converted from UTC to Eastern time (America/New_York), falls on a date in the window, both dates inclusive.
4. One point per incident: group the kept rows by `CaseNumber`. All rows in a case share one location and date (checked: none differ), so take the first.
5. Apply the point rules below.
6. Output: `CaseNumber`, `OffenseDate`, point (EPSG:3734). Record the number excluded at each step, by reason.

**Point rules** (Indicator `# Point rules`, § 4.4)
- **Outside the clip extent:** points outside the `geography` boundary are excluded. Tested against the boundary in EPSG:3734, not the `City` field.
- **On the boundary:** a point on the boundary line counts as inside.
- **Accepted geocodes:** any row with a point. Rows with no point ("Not Located") are excluded.
- **Denominator:** none. This is a selection, not a rate.

**Expected size** (sanity check at Stop C, not a known-answer test)
- About 31,594 incidents before the point rules (Eastern dates; it would be 31,582 if the UTC dates were used).
- 106 have no point.
- 129 have a `City` other than Cleveland.
- So expect roughly 31,360 points.

**Caveats** (Indicator `# Caveats`, without place names)
- These are crimes **reported to police**. Many crimes are never reported, and reporting rates differ by offense type and by community.
- Incidents, not offenses or victims: an incident with several offenses or several victims is one point.
- Located where the incident happened, not where victims or residents live. Places with many visitors and few residents look dense.
- Some Group A offenses (drug, weapon law violations) mostly reflect police activity, not underlying crime levels.
- All Group A offense types are pooled, so the pattern mixes very different crimes.
- Not comparable with figures from the FBI's old Summary Reporting System (hierarchy rule) or with the City's legacy pre-2025-11-11 dataset.
- Late reports: offenses near the end of the window may still be reported after the download.
- Excluded rows are listed by reason in the manifest.

**Design choices** (Visualization `# Design choices`)
- Why 500 m, and that it's at or above the 250 m floor.
- The pattern depends on hex size and grid origin.
- Classes are relative (quantiles), and no counts are shown.

**Outputs** (each with its manifest)

- `build/points/points_reported_crime_incidents__cle_city.gpkg`: the selection. Intermediate, not committed, never published (design issue 3).
- `outputs/visualizations/map_points_reported_crime_incidents__cle_city.html`

No table in `outputs/tables/`.

**Tests**

- **Spec validation** passes for the whole project, including the new checks (design issues 1, 2, 6, 8).
- **No known-answer test** (decision 9). The expected size above is checked by eye at Stop C.
- **`inv_004`: plain-language heat map.** Prompt: "Show me a heat map of reported crime in Cleveland." Expected: `runs`, `spec: map_points_reported_crime_incidents__cle_city`.
- **`inv_005`: counts aren't available yet.** Prompt: "How many crimes were reported in each block group?" Expected: `not_available`. The agent must not count points from the selection outside a spec.
- Existing `inv_001`–`inv_003` still pass (run at least once this chunk).

**Not in this chunk:** counts, block groups, crosswalks, neighborhoods, wards, rates, breakdowns by offense type, other time windows, continuous (kernel density) surfaces.

#### Design issues

Found by checking the requirements against architecture.md, AGENTS.md, validation.md, the templates and `lib/`. Proposed fixes:

1. **`measure: points` Indicator.**
   - Changes: § 4.4, the Indicator template, AGENTS.md glossary ("Indicator: one measure, or a reviewed selection of data"), validation.md choices, and `lib/validate.py`.
   - A `points` Indicator has `geography` (its clip extent) and an optional `window`. It has no `crosswalks`, `reliability` or `unit`.
   - § 4.4 *Separation of concerns*: its body may name its Resource's fields, but still no place names.
   - Naming table (§ 12): Indicator IDs for selections start with `points_`.
2. **`window` field.** `{ field, from, to }` with ISO dates, both inclusive. The validator checks that `field` is one of the Indicator's `data` fields and that `from` ≤ `to`.
   - The file stores times in UTC (`Z`). Its own `HourofDay`, `OffenseDay`, `OffenseMonth` and `OffenseYear` fields match the times converted to Eastern time (checked: 69,732 of 69,735 rows), not the stored values.
   - Proposed § 12 convention: dates are local dates in America/New_York. A UTC time is converted before its date is taken. `lib/` does this for `window`, so compiled code doesn't repeat it.
3. **The runner for `points` Indicators** (`lib/runner.py`, `lib/output.py`, § 7, § 8, § 11):
   - Compiled code returns a point GeoDataFrame (`CaseNumber`, `OffenseDate`, geometry in EPSG:3734), plus exclusion counts.
   - The runner skips the per-unit table checks and reliability.
   - It writes `build/points/<id>__<geography>.gpkg` with a manifest next to it. The manifest uses the same `fingerprint` and `lib_hash` staleness as now, plus an `excluded` block (reason → count).
   - `run_visualization` reads from there.
   - `build/` isn't committed, so the points never reach `outputs/`.
4. **Reading a file Resource** (`lib/runner.py` `Context`):
   - A new `ctx.features(entry)` reads the Resource's layer through a snapshot and returns only the fields named in `data`, as AGENTS.md rule 3 requires.
   - The geometry is converted to EPSG:3734.
   - A `data` entry for a file Resource has `resource` and `fields` only. The validator already skips the approved-list check when a Resource has no `datasets`.
   - A GeoPackage with one layer, like `cle_city`, so the existing local-file snapshot (hashed in place) and geopandas/pyogrio reading work as they are.
5. ~~A snapshot of a folder~~ **Dropped.** The expert re-downloaded the data as a single GeoPackage, so the existing one-file snapshot works. The number is kept so later references stay stable.
6. **Field check for file Resources** (validation.md *Data fields*, `lib/validate.py`):
   - The current check is Census-only and needs network access.
   - Add an offline check: every field named in a file Resource's `data` entry exists in the layer.
7. **Hexbin Visualization** (§ 4.5, Visualization template, AGENTS.md glossary, validation.md, `lib/validate.py`):
   - New optional `map` field: `choropleth` (default) or `hexbin`.
   - `hexbin` requires `hex_size_m`, `classification`, `classes` and `colors`, and its `indicator` must be `measure: points`. `choropleth` keeps its current fields and requires a non-`points` Indicator.
   - § 2 diagram unchanged.
   - Move *Other chart types* out of § 13.
8. **Privacy floor** (§ 12, `lib/validate.py`): hex size at least **250 m** across flats. No output may contain raw points: maps embed hexes only, and the selection stays in `build/`.
9. **`lib/heatmap.py`** (new, needs review), alongside `choropleth.py` and using the same pinned D3:
   - Builds a pointy-top hex grid in EPSG:3734. Size is converted from metres; the origin is fixed in `lib/` at (0, 0), so reruns and any future map share the grid.
   - Keeps the hexes that intersect the clip geography, clipped to its outline.
   - Counts points per hex and assigns quantile classes.
   - Embeds only hex shapes (EPSG:4326) and class labels.
   - The tooltip shows the class ("2 of 5"). The legend runs low to high with no counts.
   - The source note comes from the Resource and Geography titles. `runner.source_note` drops the "Margins of error at 90% confidence." sentence when no data is from the Census.
10. **Scope and conventions:**
    - § 1: map types beyond choropleths are in scope; a heat map shows patterns below block-group level, aggregated above the floor.
    - § 12 *Maps*: how empty and edge hexes look (Stop A questions 1–2).
    - § 7 helper table: add selection and heat map helpers.
    - Definition of done: record the chunk 3 exception (no known-answer test) in the retro.

Proposed: apply 1–10 before drafting specs.

#### Stop A questions

Answered 2026-10-24: the expert accepted the agent's suggested default for each. Recorded as decisions 18–21.

#### Stop B questions

Raised 2026-10-24 when drafting the specs. Answered 2026-10-24: the expert accepted each default as written.

1. **Unknown offense type.** An `IncidentDesc` value on neither the Group A nor the Group B list stops the run until the Resource's lists are updated (Computation step 2). The lists hold exactly the 57 values in the 2026-10-24 file. Alternative: exclude unknown values with their own reason and continue.
2. **Missing case number or offense date.** A kept row with no `OffenseDate` is excluded as "no offense date"; one with no `CaseNumber` as "no case number". In this file, all 15 such rows also have no `IncidentDesc`, so neither reason removes anything now.
3. **Extra rows in an incident** are recorded in the manifest as "additional offense in the same incident", so the `excluded` block accounts for every row read.
4. **Source note** on the map: "Crimes reported to police, not all crimes. Points are aggregated into hexagons; no individual locations are shown." Data sources are added automatically.
5. **Order of steps** (for the exclusion counts): offense type, then window, then one point per incident, then point rules. `lib/` applies the window, but at step 3 of this order.

#### Stop C results and questions

**Results** (2026-10-24, author mode)
- Selection: **31,297 points**. Excluded rows: no `IncidentDesc` 18,507 · Group B 5,722 · Justifiable Homicide 1 · no offense date 0 · outside the window 8,896 · no case number 0 · additional offense in the same incident 5,029 · no point 106 · outside the clip extent 191. Excluded + kept = 69,749, every row in the file.
- Against the expected size: 31,594 before the point rules (exact match); 106 with no point (exact match); 191 outside the boundary vs about 129 by the `City` field, so 63 fewer points than the expected ~31,360 (question 1).
- Map: 1,103 hexes at 500 m, 210 empty; 173–185 hexes per class. The HTML embeds only hex shapes and `cls`; no points, counts or case fields.
- Hex assignment checked against point-in-polygon (20,000 random points, 0 misassigned); hex width is exactly 500 m.
- Existing outputs: `median_household_income` table and map byte-identical after the `lib/` changes; `kat_001` pass (+0.07%), `kat_002` pass (exact). `population_count` outputs regenerated (they were missing).
- Spec validation: no errors. Warnings only for draft specs and unreviewed code.
- To review: `lib/points.py` and `lib/heatmap.py` (new); `lib/runner.py`, `lib/output.py`, `lib/validate.py`; `pipeline/indicators/points_reported_crime_incidents.py`.

**Questions** (expert's answers 2026-10-24: 1 keep the strict boundary clip; 2 keep 500 m; 3 keep `Purples` as is; 4 keep the breaks in the manifest; 5 no change for now, the staleness gap is accepted; 6 fine; 7 fine; 8 yes: added to `pyproject.toml` with the versions already in `uv.lock`)

1. **Boundary points.** 71 points with `City` = Cleveland fall outside the boundary, median 0.3 m (75% within 0.4 m, max 91 m): addresses on boundary streets. 9 points with another `City` fall inside. The spec clips strictly against the boundary, so the 71 are excluded. Keep it, or add a tolerance (a spec change)?
2. **Hex size.** 500 m now. Tune by editing `hex_size_m` and rerunning (no recompile).
3. **Lightest class.** `Purples` class 1 (`#f2f0f7`) is close to the white page and to the gray of empty hexes in tone. Keep, or change `colors` or the page background?
4. **Counts in the map manifest.** The HTML has no counts, but its manifest records the class breaks in points per hex (8, 19, 37, 58) and hexes per class, as the choropleth manifest records its breaks. Keep, or drop the breaks?
5. **Source note staleness.** The Visualization's `# Source note` text now goes into the HTML (it was never used before; chunks 1–2 said "None."). But § 6 says a body-only change to a spec without compiled code triggers nothing, so editing that text wouldn't redraw the map. Fix by including that section in the Visualization's hash, or move the text to frontmatter?
6. **Group lists in compiled code.** The Group A/B lists are copied from `cle_crime` into the compiled code (like chunk 2's coded values from `census_api`). A change to the Resource's lists doesn't make the code stale; an unknown value still stops the run.
7. **"No incidents"** is hard-coded in `lib/heatmap.py` (decision 18). A later selection of something other than incidents would need its own label.
8. **Dependencies.** `lib/` now imports `pyogrio` and `pyproj` directly. Both are geopandas dependencies pinned in `uv.lock`, but not listed in `pyproject.toml`. Add them?

#### Tasks

1. Commit the chunk 3 plan (this roadmap) on `main`, then create `chunk/03-crime-heatmap` from `main`.
2. Apply design issues 1–10 (docs, templates, validator). `lib/` changes are reviewed at Stop C.
3. Draft `cle_crime`, `points_reported_crime_incidents` and `map_points_reported_crime_incidents__cle_city`, update each folder's `index.md`, and add `inv_004` and `inv_005`. Run the new field check against the geodatabase. 🛑 **Stop B.**
4. Build the `lib/` changes (`ctx.features`, Eastern dates for `window`, the `points` runner path, `heatmap.py`). Compile `pipeline/indicators/points_reported_crime_incidents.py`.
5. Run validation and the invocation tests (`inv_001`–`inv_005`), and produce the outputs. Check the point count against the expected size and the exclusion counts in the manifest. Tune `hex_size_m` with the expert by editing frontmatter and rerunning. 🛑 **Stop C.**
6. Retro per the working method.

#### Decisions (expert, 2026-10-24)

1. **One point = one incident:** a distinct `CaseNumber` with at least one NIBRS Group A offense. Group B offenses, rows with no NIBRS offense, and rows with no classification are excluded. This follows the NIBRS incident definition (FBI, *A Guide to Understanding NIBRS*).
2. **Selections are Indicators.** An Indicator can be "a reviewed selection of data", not only a measure.
   - Marked by `measure: points` and the ID prefix `points_`.
   - The window doesn't go in the ID, the way the ACS vintage doesn't.
   - A later count Indicator `builds_on` it.
   - A different selection (e.g. property crimes only) is a new Indicator, not a parameter.
3. **The Indicator does all filtering**, including the city clip, which comes from `geography`, not the body. Such an Indicator is tied to one Resource's fields by nature, so it's less reusable than the Census Indicators.
4. **The window goes in frontmatter**: more readable and checkable. Changing it makes the code stale (recompile and review).
5. **All Group A offense types**, sex offenses included. No type filter.
6. **The Visualization only draws.** Map type, hex size, classes and colors are set in the spec, never chosen by the agent.
7. **Privacy:**
   - A project-wide floor of 250 m across flats (§ 12, checked by the validator). No suppression of sparse hexes.
   - The HTML embeds only hexes and classes.
   - The selection stays in `build/`.
8. **Map types beyond choropleths are in scope.**
9. **No known-answer test for this chunk.** The expert accepts this as an exception to the definition of done.
10. **Window:** `OffenseDate`, 2025-11-30 to 2026-09-30, both inclusive. The expert chose 30 November over the 11 November coverage start. Offense dates 1–10 Nov 2025 are about 75% missing, so the window starts after them either way.
11. **Hexbin grid:** size is the width across flats, in metres. Start at 500 m; tune at Stop C by editing frontmatter and rerunning (no recompile).
12. **Legend and tooltip:** relative quantile classes, low to high. No counts shown.
13. **Resource ID: `cle_crime`.**
14. **Exclusions** are recorded by reason in the selection's manifest.
15. **Each point carries** `CaseNumber`, its point, and `OffenseDate`. Nothing else.
16. **Justifiable Homicide is excluded** and recorded in the manifest.
17. **5 classes.**
18. **Empty hexes** (inside the city, no incidents): drawn light gray (`#d9d9d9`), labelled "no incidents". Quantile classes are computed over hexes with at least one incident.
19. **Edge hexes** are clipped to the city outline. A clipped hex covers less area and tends to fall in a lower class, so `# Design choices` says so.
20. **Grid origin** is fixed in `lib/` at (0, 0) in EPSG:3734, not a spec field. Every hexbin map shares the grid.
21. **Colors: `Purples`.** Sequential, distinct from the existing `Blues` and `Greens`, and avoids the alarm of reds for crime.

**The file** (expert's download, read by the agent 2026-10-24)
- `data/static/cle_crime/Crime_Incidents_P1RMS_-6429680527207168309.gpkg`: a GeoPackage.
  - One layer, `Crime_Incidents`, geometry column `SHAPE`: 69,749 points in EPSG:3857 (Web Mercator), plus `LAT`/`LON` fields.
  - Downloaded 2026-10-24. It replaces an earlier File Geodatabase download of the same export: same rows, fields and values (checked).
  - Source: <https://data.clevelandohio.gov/datasets/e15e8989c83e4cbd841fb171a6c62f68_0/about>. The live layer updates daily.
- **Coverage starts 2025-11-11**, matching the portal's cutover note ("data from before 11/11/25" lives in a separate legacy dataset).
  - 6,377 rows were reported earlier, back to 1983, at tens to a few hundred per year.
  - Their case numbers carry their own years: old cases touched in the new system, not a history.
- **One row = one offense.**
  - Since 2025-11-11: 63,372 rows in 54,708 cases. 7,039 cases have 2–11 rows.
  - Rows in one case share location and time and differ by `Statute`.
  - `CaseNumber` + `Statute` appears unique.
  - `PrimaryKey` is not a key (`2147483647` on about half the rows).
  - `OBJECTID` is assigned per export.
- **Offense fields:**
  - `IncidentDesc` is the NIBRS offense type.
  - `StatDesc` is the city's statute label.
  - `Statute` is the Ohio Revised Code or Cleveland Codified Ordinance section.
  - 15,794 rows since 2025-11-11 have no `IncidentDesc`. Of these, 11,198 have no classification at all. The rest are non-crime or non-NIBRS records: "NO CRIME", hit-skip traffic, emergency hospitalization, protection orders.
- **Group A vs B as they appear in the file:**
  - 42,224 Group A rows in 36,428 cases. 86% of those cases have one offense.
  - 5,354 Group B rows. Group B values present: All Other Offenses, Disorderly Conduct, Driving Under the Influence, Drunkenness, Family Offenses (Nonviolent), Liquor Law Violations, Peeping, Runaway, Trespass of Real Property, Bad Checks.
- **Location:**
  - 270 rows have no point ("Not Located").
  - 327 rows have `City` other than Cleveland. Clip against the city boundary, not this field.
  - Precomputed fields: `NEIGHBORHOOD` (34 + "Not Located"), `WARD` (= `WARD_2026`, 15 wards), `WARD_2014`, and 2020 tract, block group and block GEOIDs.
  - Points are more precise than `Address_Public`, which is masked to the block ("40XX Arnold Ct"): 28,172 distinct points vs 13,320 addresses.
- **Time fields:**
  - `ReportedDate` and `OffenseDate` (datetimes, stored in UTC), plus derived parts (`OffenseYear`, `OffenseMonth`, `OffenseDay`, `HourofDay`, `DOW`, `TimeBlock`) in Eastern time.
  - `DaysAgo` is counted from the export date. Never use it in a measure.
  - Reporting lag: 97% of rows are reported within 30 days of the offense, but about 600 are reported a year or more later.
- **No victim, offender or arrest fields.**

**Resource `# Notes`** (facts about the dataset, true for any pull)
- Coverage starts 2025-11-11. Earlier rows are a sparse subset, not a history, and are not comparable with the legacy 2016–2025 dataset, which used a different data model.
- One row is one offense. Several rows can share a `CaseNumber`. `PrimaryKey` is not a key, and `OBJECTID` changes between exports.
- `IncidentDesc` holds NIBRS offense types. The list of which values are Group A and which are Group B belongs here, so Indicators can link to it.
- Rows without `IncidentDesc` are non-crime or non-NIBRS records, or not yet classified. On a later download, some unclassified rows may gain a classification.
- No victim data, so the NIBRS rule "one offense per victim" for crimes against persons can't be applied.
- `DaysAgo` depends on the export date. Never use it.
- `ReportedDate` and `OffenseDate` are stored in UTC. The derived fields (`OffenseDay`, `HourofDay`, and so on) are in Eastern time. Convert before taking a date: an evening incident has the next day's UTC date.
- Points are more precise than the block-masked address. Never publish raw points; maps embed only aggregated surfaces at or above the § 12 floor.
- Late reports: counts for recent months grow on later downloads.
- Geometry is EPSG:3857. The clip and any area or distance work use EPSG:3734 (§ 12).

---

## Completed chunks

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
