# Architecture & Requirements

This file holds every requirement for building the project. [AGENTS.md](AGENTS.md) holds the short rules; this file explains how everything works and why.

**Guiding principle: minimalism.** Every field, file, and step has to earn its place. If something can be derived, don't write it down twice.

**Contents**

1. [Goals and scope](#1-goals-and-scope)
2. [How it works](#2-how-it-works)
3. [Specs and the Open Knowledge Format](#3-specs-and-the-open-knowledge-format)
4. [The five node types](#4-the-five-node-types)
5. [The dependency graph](#5-the-dependency-graph)
6. [Compiled code and staleness](#6-compiled-code-and-staleness)
7. [Shared helper library](#7-shared-helper-library)
8. [Manifests](#8-manifests)
9. [Modes: author and run](#9-modes-author-and-run)
10. [Getting data](#10-getting-data)
11. [Project layout](#11-project-layout)
12. [Conventions](#12-conventions)
13. [Deferred](#13-deferred)

---

## 1. Goals and scope

**Primary goal:** a repeatable, agent-driven workflow for geospatial indicators and maps. The expert decides the methodology. The agent handles the mechanics: API calls, joins, spatial operations, and charting.

**Secondary goal:** learn the limits of agentic work. Note where the agent needed correction.

**Long-term:** package this as a reusable skill for others.

**In scope now**

- A **one-time study** of Cleveland, Ohio.
- Geographies: **city, neighborhoods** (from a shapefile), **census tracts**, and **census block groups**. Block groups are the smallest unit we report.
- Outputs: **CSV tables**, plus **interactive maps** as self-contained D3 HTML files: choropleths with tooltips, and hexbin heat maps.
- A **heat map** shows a pattern below block-group level, aggregated into hexes no smaller than the privacy floor ([§ 12](#privacy)). It shows relative classes, not values.
- Code runs **locally** through Claude Code on the expert's computer.
- Evaluation: **known-answer tests** only ([tests/validation.md](tests/validation.md)).

**Not in scope now:**
- Interpreting results.
- Reporting values below block-group level.
- Running in the cloud or on Claude.ai.

---

## 2. How it works

```
 Resource ──────────────┐
 (API, file, dataset)   │
                        ▼
 Geography ──► Crosswalk ──► Indicator ──► Visualization ──► CSV + HTML + manifests
 (boundaries)  (geo → geo)   (a measure)   (a map)
                               ▲   │
                               └───┘ can build on other Indicators
```

**A typical run:**

1. Someone asks for a map, e.g. "housing cost burden by neighborhood."
2. The agent finds that map's Visualization spec, then follows its references down through the Indicator, Crosswalks, Geographies, and Resources.
3. It checks what's missing or stale ([§ 6](#6-compiled-code-and-staleness)).
4. It fetches any data it doesn't have yet, then computes stale items from the bottom of the graph up.
5. It runs the known-answer tests.
6. It writes the tables and the map, each with a manifest.

### Invocation

- A request is a plain-language prompt naming an Indicator or Visualization, e.g. "show me population by block group." The agent maps it to **one spec ID**. If more than one spec could match, it asks.
- The agent carries out the request **only through reviewed code** in `lib/` and `pipeline/`. It never re-derives a computation for a single request. This holds even when the prompt doesn't mention specs; [AGENTS.md](AGENTS.md) rule 1 states it as the agent's first rule, because putting it only here wasn't enough (chunk 1).
- Commands: `uv run python -m lib.runner list` (what's available), `run <id> [--mode author|run]`, `status` (code and results staleness); `uv run python -m lib.validate [--network]`.
- The **runner** in `lib/` does steps 2–6 above. It is generic, so it lives in `lib/`, not `pipeline/`. Graph traversal is automatic: it reads the reference fields in frontmatter ([§ 5](#5-the-dependency-graph)) and walks down from the requested spec.
- If no spec matches, the agent says the item isn't available and lists the Indicators and Visualizations that are. It creates, drafts, and fetches nothing.
- How the agent responds to prompts is checked by **invocation tests** ([tests/validation.md § 3](tests/validation.md#3-invocation-tests)).

---

## 3. Specs and the Open Knowledge Format

`specs/` is a bundle in the **Open Knowledge Format (OKF), version 0.2**:
<https://github.com/GoogleCloudPlatform/open-knowledge-format/blob/main/SPEC.md>

OKF is a minimal standard for knowledge stored as Markdown files with YAML frontmatter. It's designed to be read by agents and people alike. We follow it wherever it fits and add our own fields only where we need them. OKF explicitly allows this.

### What we use from OKF

| OKF element | How we use it |
|---|---|
| **One concept = one Markdown file** | One spec = one node (Resource, Geography, …). |
| **Concept ID** = file path without `.md` | Our ID is the **file name** without `.md`. File names are unique across `specs/`, so the short name is enough to refer to any spec. |
| **`type`** (the only field OKF requires) | One of `Resource`, `Geography`, `Crosswalk`, `Indicator`, `Visualization`. |
| **`title`, `description`** | Required for us. `description` is one line. |
| **`resource`** (URI of the underlying asset) | Where a Resource or Geography lives: a URL or a project-relative path. |
| **`tags`** | Optional. |
| **`status`** (`draft` / `stable` / `deprecated`) | **Required for us.** New specs start as `draft`, and only the expert sets `stable`. OKF treats a missing status as `stable`, so we require the field: an AI-drafted spec must never pass as approved. |
| **`index.md`** in each folder | Lists the specs in that folder as `* [Title](file.md) - description`. No frontmatter. |
| **Root `index.md`** with `okf_version: "0.2"` | `specs/index.md` declares the bundle's OKF version. |
| **`# Schema`** body heading | The columns of a dataset. |
| **`# Computation`** body heading | An Indicator's calculation steps. |
| **`generated` / `verified`** | Their vocabulary is reused in compiled code headers ([§ 6](#6-compiled-code-and-staleness)). |
| **Markdown links in the body** | For readers only. OKF links carry no type, so dependencies come from frontmatter fields ([§ 5](#5-the-dependency-graph)). |

### What we don't use (yet)

`sources` / `usage_window`, `stale_after`, the attested-computation fields (`runtime`, `parameters`, `computation`, `executor`, `attester`), and `log.md`. [roadmap.md](roadmap.md)'s session log covers what `log.md` would do. Revisit these if a real need appears.

### Body layout

OKF requires no body sections. Our templates use a few short `#` headings so that every spec of a type reads the same way. Body text is for people, and it's also what the agent reads to compile code. That's why the body of an Indicator matters as much as its frontmatter.

---

## 4. The five node types

Fields are defined in [templates/](templates/). The lists below show only what each type adds to the shared fields (`type`, `title`, `description`, `status`, `tags`).

| Type | What it is | Folder | Adds these fields |
|---|---|---|---|
| **Resource** | One API, file, or dataset | `specs/resources/` | `resource`, `auth`, `datasets` |
| **Geography** | One boundary file | `specs/geographies/` | `resource`, `id_field`, `name_field`, `within`, `within_rule`, `census_unit` |
| **Crosswalk** | Moves data between two Geographies | `specs/crosswalks/` | `from`, `to`, `method`, `weights`, `weights_source` |
| **Indicator** | One measure, or a reviewed selection of points | `specs/indicators/` | `measure`, `unit`, `geography`, `crosswalks`, `data`, `builds_on`, `reliability`, `window` |
| **Visualization** | One map | `specs/visualizations/` | `map`, `indicator`, `geography`, `classification`, `classes`, `breaks`, `colors`, `also_show`, `hex_size_m` |

### Separation of concerns

Each type says one kind of thing. Specs point to each other only through frontmatter fields ([§ 5](#5-the-dependency-graph)).

| Type | Says | Never says |
|---|---|---|
| Resource | How to access the data: request syntax, auth, approved datasets, what table codes mean | Places, or observations from one pull |
| Geography | What the units are, the file, which units are in (`within`), and how its units match a source's units (`census_unit`) | Measures |
| Crosswalk | How values move from one Geography to another, and the boundary effects (e.g. straddling units) | Specific measures |
| Indicator | What is measured (or selected), and how it's computed from the named fields, at any geography | Place names, unit types, county codes, or Geography and Crosswalk IDs in the body |
| Visualization | How one Indicator at one Geography is drawn | Computation |

Test for an Indicator: changing its `geography` or `crosswalks` must not require editing its body. Checked by inspection, not by the validator.

### 4.1 Resource: the unit of access

> **A Resource tells you how to get data from somewhere. An Indicator tells you exactly what to pull and how to use it.**

- **One Resource = one API, one file, or one dataset.** The whole Census Data API is a single Resource (`census_api`). Its spec explains how to use the API. Which tables and fields to pull is a methodology choice, so that belongs in each Indicator.
- **APIs list their approved datasets.** `datasets` is the short, expert-controlled list of dataset + vintage combinations that Indicators may use, e.g. `acs/acs5` 2023. This keeps every Indicator on the same survey release.
- **Borderline case, data portals** (e.g. Cleveland Open Data). Use this test:
  - *If choosing what to pull from it is a methodology decision* → one Resource (like the Census API).
  - *If deciding whether to trust it is itself a decision* → one Resource per dataset.

  Portal datasets have different publishers, schemas, and reliability, so each one is its own Resource.
- **Table-specific notes** (e.g. "B25070 has a 'not computed' category") go in the Resource body under `# Notes`. Indicators link to them instead of repeating them.
- API keys are referred to by their `.env` variable **name** (`auth`), never their value.

### 4.2 Geography

One boundary file = one Geography: `bg_2020`, `tract_2020`, `cle_city`, `cle_neighborhoods`.

- `id_field`: the unique code for each unit, always read as text.
- `within` (optional): keep only units inside another Geography.
- `within_rule` (required with `within`): how units that straddle the boundary are decided, so helpers can apply it from frontmatter. Areas are measured in EPSG:3734.

  | `within_rule` | A unit is kept when |
  |---|---|
  | `majority_area` | More than 50% of its area is inside |
  | `centroid` | Its centroid is inside |
  | `any` | Any part of it overlaps, beyond touching edges |

  The body explains why the rule was chosen.
- The coordinate system is read from the file itself ([§ 12](#12-conventions)).
- Boundary files are snapshotted like Resources ([§ 10](#10-getting-data)).
- `census_unit` (optional): the Census Data API unit its units match, `block group` or `tract`, with `id_field` holding the Census `GEOID`. Required for a Geography that an Indicator with Census data is calculated at. The request extent is **derived, never written down**: `lib/` reads the kept units' GEOIDs (after `within`) and requests those units' states and counties, so it can't disagree with the boundary file.

### 4.3 Crosswalk

Moves data from one Geography (`from`) to another (`to`) by producing a **weights table**: for each source unit, the share that goes to each target unit.

> Example: block group X is 70% in Neighborhood A and 30% in Neighborhood B, so 70% of its counts go to A.

| `method` | How a unit is split | When to use it |
|---|---|---|
| `population_weighted` | By where people, households, or housing units are (`weights`), using census block counts (`weights_source`) | **Default** |
| `areal` | By share of land area | Only when nothing better exists |
| `centroid` | The whole unit goes to the target containing its center | Rough approximation |
| `nested` | Each unit is entirely inside one target (all weights 1) | Block groups → tracts |

- `nested` is also valid when the `from` Geography's `within` equals `to`: the `within` filter already assigned every unit to that one target, e.g. `bg_2020` → `cle_city`.
- Crosswalks move **counts only**, never percentages or medians.
- Census blocks are used here to build weights. They are never reported.

### 4.4 Indicator

One measure, such as "% of households with housing cost burden", or a reviewed selection of points ([below](#selections-measure-points)).

- **`geography`** is where it's calculated, usually `bg_2020`. It's also reported there.
- **`crosswalks`** lists the extra geographies it's reported at. Each crosswalk's `to` is an output geography, and its `from` must equal the Indicator's `geography`.
- **`data`** names exactly what to pull: Resource, dataset, vintage, and each field with its plain meaning. For Census data, the matching `_M` (margin of error) field is pulled automatically for every `_E` field. For a file Resource (no `datasets`), an entry has `resource` and `fields` only, and `lib/` reads only those fields.
- **`measure`** decides how values move to other geographies:
  - `percent`, `rate`, `count`: move the counts, then compute ([§ 12](#12-conventions)).
  - `median`, `index`: with crosswalks, the body needs an `# Aggregation` section explaining a valid method.
- **`unit`** (optional): what the values are in, for display. `count` (the default) or `dollars`. Percentages come from `measure: percent`, not `unit`.
- **`reliability`** (survey data only) sets the CV threshold, and whether low-reliability values are flagged or suppressed.
- **Body:** `# Definition` (universe, numerator, denominator, exclusions), `# Computation` (steps), `# Caveats`. Add `# Point rules` for point data: outside-city points, boundary points, accepted geocodes, and denominator.
- **The body is about the measure, not the place** ([Separation of concerns](#separation-of-concerns)). Steps that are the same for every Indicator are done by `lib/` and aren't repeated: pulling the fields for the geography's units, joining them to the units (§ 12), applying the listed crosswalks, and computing reliability at every geography. The compiled code returns one table at the Indicator's `geography`; the runner does the rest.

#### Selections (`measure: points`)

A selection is a reviewed set of points, e.g. the reported crime incidents in a time window. Later Indicators can build on it (`builds_on`), e.g. to count points per unit. A different selection (say, property crimes only) is a new Indicator, not a parameter.

- **ID** starts with `points_` ([§ 12](#naming)). The time window doesn't go in the ID, the way the ACS vintage doesn't.
- **`geography`** is the clip extent: points outside its boundary are excluded. There are no `crosswalks`, `reliability` or `unit`.
- **`window`** (optional): `{ field, from, to }`, ISO dates, both inclusive. `field` is one of the Indicator's `data` fields. Dates are local dates ([§ 12](#dates-and-times)); `lib/` converts the times before comparing, so compiled code doesn't repeat it. Changing the window changes the spec, so the code is stale.
- **The Indicator does all the filtering**, so its body may name its Resource's fields. Still no place names. Such an Indicator is tied to one Resource by nature, so it's less reusable than a Census Indicator.
- **Body:** `# Definition`, `# Computation`, `# Point rules`, `# Caveats`.
- **Compiled code** returns a point table (the fields the body names, geometry in EPSG:3734) plus the number of rows excluded at each step, by reason. The runner writes it to `build/points/<id>__<geography>.gpkg` with a manifest ([§ 8](#8-manifests)). It skips the per-unit table checks and reliability. A selection is never published: it stays in `build/`, and maps embed only aggregated hexes ([§ 12](#privacy)).

### 4.5 Visualization

One map. **`map`** (optional) sets the kind: `choropleth` (the default) or `hexbin`.

- Classification (`classification`, `classes`, `breaks`) and `colors` are always set in the spec, **never chosen by the agent**.
- Output: a self-contained HTML file using D3 v7 (pinned version), with its data embedded.

**Choropleth.** Its `indicator` is not a `points` Indicator.
- **`indicator`** sets the color. **`geography`** must be one the Indicator is reported at.
- The tooltip shows the unit's name, the estimate, the margin of error, and the reliability. It also shows any `also_show` Indicators.

**Hexbin heat map.** Its `indicator` is a `points` Indicator, and `geography` is that Indicator's `geography`.
- **`hex_size_m`** (required): hex width across flats, in metres, at least the privacy floor ([§ 12](#privacy)).
- Pointy-top hexes in EPSG:3734, on a grid whose origin is fixed in `lib/` at (0, 0), so reruns and every hexbin map share the grid. Hexes that intersect the geography are kept and clipped to its outline.
- Points are counted per hex, and hexes are classed by `classification` over the hexes with at least one point.
- The HTML embeds only hex shapes (EPSG:4326) and their class labels, never points or counts. The tooltip shows the class ("2 of 5"); the legend runs low to high with no counts.
- `# Design choices` explains the hex size, and says that the pattern depends on hex size and grid origin and that classes are relative.

---

## 5. The dependency graph

Specs reference each other by ID in specific frontmatter fields. The validator builds the graph from these fields alone, so there's no separate list of dependencies to keep in sync.

| Type | Fields that point to other specs |
|---|---|
| Resource | none |
| Geography | `within` |
| Crosswalk | `from`, `to`, `weights_source` |
| Indicator | `geography`, `crosswalks`, `data[].resource`, `builds_on` |
| Visualization | `indicator`, `geography`, `also_show` |

- The graph must not loop.
- The graph gives three things: **build order**, **what's stale**, and **manifests** (everything an output was built from).
- The project has tens of nodes, so frontmatter plus a small script is enough.

---

## 6. Compiled code and staleness

**The spec is the source of truth. Code is compiled from it.**

### Which specs get compiled code

| Type | How it runs |
|---|---|
| **Indicator** | Always has compiled code: `pipeline/indicators/<id>.py` |
| **Crosswalk, Visualization** | Built by shared helpers ([§ 7](#7-shared-helper-library)) straight from frontmatter. They get compiled code only if a spec needs something the helpers can't do. |
| **Resource, Geography** | Fetched and loaded by shared helpers. No compiled code. |

### Compile → review → pin

The agent compiles the code. The expert reviews it. The code's header then records where it came from, using OKF's `generated` / `verified` vocabulary:

```python
# spec: specs/indicators/housing_cost_burden_pct.md
# spec_hash: sha256:3f9a…
# generated: { by: claude-code, at: 2026-11-02T14:00:00-05:00 }
# verified: { by: human:siqi, at: 2026-11-02T16:30:00-05:00 }
```

Code without a `verified` line is unreviewed and can't run in run mode.

### Staleness: code follows its spec, results follow the data

| What changed | What happens |
|---|---|
| A spec that has compiled code (any part, body included) | That **code is stale**: recompile and review again (author mode only). Its results, and everything above it, rerun. |
| The frontmatter of a spec without compiled code | Results of everything above it **rerun**. No review is needed. |
| Only the body of a spec without compiled code (documentation) | **Nothing.** |
| A new data snapshot | Results of everything above it **rerun**. |
| Any file in `lib/` | **All** results rerun. `lib/` changes are reviewed, so no recompile is needed. |
| Only a spec's `status` | **Nothing.** `status` records approval, not content, so it's left out of spec hashes. |

"Rerun" means running already-reviewed code again. "Recompile" means generating new code, which then needs the expert's review.

Compiled code is tracked in git.

---

## 7. Shared helper library

`lib/` holds the operations that repeat across specs. The expert reviews them once, tests confirm them, and they change only with review.

| Helper | What it does |
|---|---|
| Fetch & load | Fetch a request from a Resource into a snapshot; load snapshots and Geographies; read only the named fields of a file Resource |
| Runner | Walk the graph from a requested spec, check staleness, fetch, compute, apply crosswalks and reliability, test, and write outputs ([§ 2](#invocation)) |
| Selection | For a `points` Indicator: apply the `window` in local dates, then write the compiled code's points and exclusion counts to `build/points/` |
| Build crosswalk | Build a weights table using one of the allowed methods |
| Apply crosswalk | Move counts and their margins of error between geographies |
| Rate from counts | Percentage or rate from numerator and denominator counts, with margin of error |
| Margin-of-error math | Census Bureau formulas for sums, ratios, and proportions |
| Reliability | Compute CV and flag or suppress values per the Indicator's settings |
| Point aggregation | Count points within polygons, following the Indicator's point rules |
| Draw choropleth | Produce the HTML map from a Visualization spec |
| Draw heat map | Build the hex grid, count a selection's points per hex, class the hexes, and produce the HTML map |
| Write output | Write a CSV or HTML file together with its manifest |

Compiled Indicator code should be **short**: mostly calls to these helpers.

---

## 8. Manifests

Every output gets a manifest saved next to it, with the same name plus `.manifest.yaml`. It's generated by walking down the graph.

```yaml
output: outputs/tables/housing_cost_burden_pct__cle_neighborhoods.csv
created: 2026-11-02T14:10:00-05:00

built_from:
  - housing_cost_burden_pct (Indicator)
      spec_hash: sha256:3f9a…
      code_hash: sha256:81c2…
      verified: human:siqi, 2026-11-02
  - bg_2020__to__cle_neighborhoods (Crosswalk)
      method: population_weighted (housing_units)

data:
  - census_api: acs/acs5 2023, B25070_001E … B25070_011E (+ _M)
      retrieved: 2026-11-01
      snapshot_hash: sha256:5be1…

known_answer_tests:
  kat_003: pass
```

The manifest also records `lib_hash` (one hash of everything in `lib/`) and a `fingerprint` of all the hashes above. The runner compares them with the current state to decide whether the output is stale.

A selection's manifest (`build/points/…gpkg.manifest.yaml`) works the same way and adds an `excluded` block: each reason, with the number of rows it removed.

```yaml
excluded:
  not a Group A offense: …     # example reasons
  outside the window: …
  no point: …
```

HTML maps also show a short source note on the page, generated from the manifest.

---

## 9. Modes: author and run

| | **Author mode** | **Run mode** |
|---|---|---|
| **Who** | Domain expert, working with the agent | Anyone |
| **Specs & templates** | Draft (agent helps), edit, validate, set `status: stable` | Read only |
| **Code** | Compile, review, pin | Read only |
| **`lib/`** | Edit, with review | Read only |
| **What can run** | Anything | Only `stable` specs with reviewed, up-to-date code |
| **When something is wrong** | Fix it | Stop and refer to an expert |

**Author mode in practice:**
1. The expert describes an indicator.
2. The agent drafts the spec from the template.
3. The agent checks every field code against the API's own field list (for Census, `variables.json` for that dataset and vintage).
4. The agent compiles the code; the expert reviews it.
5. Tests run, and the expert marks the spec `stable`.

**Editing a `stable` spec.** When the agent edits a `stable` spec (anything but `status`), it sets `status` back to `draft` in the same edit, so the expert approves the change. The validator warns about any `stable` spec whose content differs from the last commit.

---

## 10. Getting data

- **API keys** live in `.env`, which is never committed. Example: `CENSUS_API_KEY=...`.
- **Snapshots are stored per request.** A request is one specific pull: Resource + dataset + vintage + fields + geography. Each one is saved once in `data/raw/<resource>/<request-hash>/`, with a `snapshot.yaml`:

  ```yaml
  resource: census_api
  request: acs/acs5 2023 · B25070_001E…B25070_011E (+ _M) · block group, Cuyahoga County OH
  url: https://api.census.gov/data/2023/acs/acs5?get=...   # key removed
  retrieved: 2026-11-01T09:12:00-04:00
  hash: sha256:5be1…
  ```

  A file Resource at a URL is snapshotted the same way, as one request for the whole file. One whose `resource` is a local file is hashed in place, like a local Geography (below).
- **Geography boundary files are snapshotted too.**
  - A Geography whose `resource` is a **URL** is fetched once into `data/raw/<geography id>/<hash>/`, with a `snapshot.yaml` recording the URL, retrieval time, and hash.
  - A Geography whose `resource` is a **local file** is hashed in place; it is not copied.
  - Both hashes go in manifests, like Resource snapshots.
- **Static local files** live in `data/static/<id>/`, e.g. a boundary file the expert downloaded by hand. Like the rest of `data/`, they're not committed. The spec records where the file came from (source URL in its body), and manifests record the file's hash.
- **All computation reads snapshots, never a live source.** To refresh, fetch a new snapshot on purpose. Its hash changes, and everything above it reruns.
- `data/` is not committed. Manifests record snapshot hashes.

---

## 11. Project layout

```
cleveland-analysis/
├── CLAUDE.md               points Claude Code to AGENTS.md
├── AGENTS.md               start here: rules, read order, glossary
├── architecture.md         this file
├── roadmap.md              implementation steps and session log
├── .env                    API keys (never committed)
├── .gitignore
├── templates/              one template per node type
├── specs/                  OKF bundle — the source of truth
│   ├── index.md            declares okf_version "0.2"
│   ├── resources/
│   ├── geographies/
│   ├── crosswalks/
│   ├── indicators/
│   └── visualizations/
├── lib/                    shared helpers (reviewed)
├── pipeline/               compiled code (reviewed, pinned)
├── pyproject.toml, uv.lock Python environment (uv, versions pinned)
├── data/raw/               snapshots (not committed)
├── data/static/            local files added by hand, e.g. boundary files (not committed)
├── build/                  intermediate results, e.g. crosswalk weights (not committed)
│   └── points/             selections from points Indicators + manifest (never published)
├── outputs/                (not committed)
│   ├── tables/             CSV + manifest
│   └── visualizations/     HTML + manifest
└── tests/
    ├── validation.md       validator checks + known-answer and invocation test formats
    ├── known_answers.md    the known-answer tests
    └── invocation.md       the invocation tests
```

`lib/`, `pipeline/`, `data/`, `build/` and `outputs/` are created during implementation.

---

## 12. Conventions

### Naming

- **File name = ID**, unique across `specs/`. Lowercase `snake_case`, except official codes keep their case.

  | Type | Pattern | Example |
  |---|---|---|
  | Resource | `<publisher>_<name>` | `census_api`, `cle_311_calls` |
  | Geography | `<unit>_<boundary year>`, or a `cle_` prefix for city-specific ones | `bg_2020`, `cle_neighborhoods` |
  | Crosswalk | `<from>__to__<to>` | `bg_2020__to__cle_neighborhoods` |
  | Indicator | what it measures, not where | `housing_cost_burden_pct` |
  | Indicator (selection) | `points_<what it selects>` | `points_reported_crime_incidents` |
  | Visualization | `map_<indicator>__<geography>` | `map_housing_cost_burden_pct__cle_neighborhoods` |

- Output files: `outputs/tables/<indicator>__<geography>.csv` and `outputs/visualizations/<visualization id>.html`.

### Geography

- Block groups are the smallest reporting unit. 2020 census boundaries are the default.
- `GEOID`s and other unit codes are always **text**, so leading zeros are kept.
- **Coordinate systems** are read from each file. A file with no coordinate system is an error, never a guess. Area and distance calculations use NAD83 / Ohio North (EPSG:3734). Web maps use WGS84 (EPSG:4326).

### Dates and times

- Dates are **local dates in America/New_York**. A time stored in UTC is converted before its date is taken: an evening incident has the next day's UTC date. `lib/` does this for `window`.

### Privacy

- **Hex floor:** a hexbin map's `hex_size_m` is at least **250 m** across flats. Checked by the validator. Sparse hexes are not suppressed.
- **No raw points in any output.** Maps embed only aggregated hexes and their classes. Selections stay in `build/`, which is never committed or published.

### Counts first, then rates

- **Never average percentages.** Move numerator and denominator **counts** through the crosswalk, add them up, then divide.
- **Medians** can't be moved by allocation. Use a valid method described in `# Aggregation`, or report at the native geography only.
- **Citywide values** are aggregated from the native geography like any other output. The Census Bureau's published value for Cleveland city is a **known-answer check**, not the reported figure.

### Uncertainty (ACS)

- Carry margins of error (90% confidence) through every step, using Census Bureau formulas. For example, the margin of error of a sum is √(sum of squared MOEs).
- CV = (MOE ÷ 1.645) ÷ estimate. A suggested threshold is 0.30, set per Indicator. `reliability` is `low` above it, otherwise `ok`, at every geography the Indicator is reported at.
- An estimate of 0 has no CV: `cv` is blank, `reliability` is `low`, and `note` says "estimate is 0; CV undefined".
- A blank `estimate` or `moe` has no CV: `cv` and `reliability` are blank.
- **Counts through a crosswalk:** estimate = Σ weight × estimate, MOE = √Σ (weight × MOE)². If some units have a blank estimate or MOE, the sums use the units that have one, and `note` says how many were left out of each.

### Output tables (CSV)

| Column | Meaning |
|---|---|
| `geography_id` | Unit code (text) |
| `geography_name` | Display name, if any |
| `estimate` | The value |
| `moe`, `cv` | Margin of error and CV (blank if not applicable) |
| `reliability` | `ok` or `low` |
| `numerator`, `numerator_moe`, `denominator`, `denominator_moe` | For percentages and rates |
| `note` | Anything unusual, e.g. "suppressed: low reliability" |

- Values are stored at full precision and rounded only for display: percentages to 1 decimal place, counts and dollars to whole numbers (dollars with a `$`).
- **Missing or suppressed values are left blank, never 0**, with the reason in `note`.
- **Compute with flagged uncertainty rather than stop.** When some inputs are blank, compute from the ones that have values and say what was left out in `note`. Stop only for structural problems (a missing unit, a broken join, a spec that doesn't say what to do), never because data is incomplete. (Expert's principle, chunk 2.)
- **Not published at a level:** the Census Data API returns `null` for a field that isn't published at a geography's `census_unit`. If every unit is `null`, the run stops (structural). If only some are, those values are blank with "not published" in `note`.
- **A missing unit is an error; a blank value is not.** Every unit of the geography gets a row. A unit with no row in the source stops the run. A unit whose value is blank (an annotation, a coded value, suppression), with its reason in `note`, is a normal result, and its `reliability` is blank.

### Maps

- Units with no value are drawn light gray (`#d9d9d9`).
- **Hexbin maps:** hexes inside the geography with no points are drawn light gray (`#d9d9d9`) and labelled as having none (e.g. "no incidents"); classes are computed over hexes with at least one point. Edge hexes are clipped to the geography's outline, so they cover less area and tend to fall in a lower class.
- Titles describe what is measured, never what it shows.

### Tech stack

- Python 3.11 or newer: pandas, geopandas, shapely, pyyaml, requests.
- Environment manager: uv. Exact versions are pinned in `pyproject.toml` and `uv.lock`.
- D3 v7 at a pinned version.
- git. `.env`, `data/`, `build/` and `outputs/` are not committed.

---

## 13. Deferred

Agreed during design, but not part of the first build.

| Item | What it means |
|---|---|
| **Cloud portability** | Run compute from a bundle of snapshots, with an environment check at start-up. On Claude.ai, code runs in a temporary cloud sandbox, and network access depends on the plan and admin settings. |
| **Other evaluation layers** | Invariant checks (percentages between 0 and 100, numerator ≤ denominator, parts add up to the city total). Independent re-implementation. Map checks. A log of human corrections. A second-city test. |
| **Golden indicator set** | 5–10 indicators with trusted published values to anchor the known-answer tests. |
| **Visualization rules** | Data-quality notes on maps, how unreliable values look, shared color scales across related maps. |
| **Non-expert parameters** | Pre-approved settings run-mode users may change, e.g. survey year. |
| **Data-source proposals log** | A place for the agent's suggested new sources. For now, they're raised in conversation. |
| **More OKF features** | `sources`, `stale_after`, attested computation, `log.md`. |
| **Change over time** | Comparisons across years, including converting 2010 boundaries to 2020. |
| **Packaging as a skill** | After the Cleveland study works end to end. AGENTS.md rule 1 (route every request through the runner) moves into the skill, with a description that matches plain-language requests. |
| **Shared Visualization defaults** | One Visualization spec per map stays the rule: each map keeps its own ID, approval, and `# Design choices`. Once house style repeats across many maps, make `classification` and `classes` optional, with defaults in `lib/`; changing a default is then a reviewed `lib/` change that reruns all results. Triggers: one setting changed across every map, shared color scales across related maps (*Visualization rules*), or `# Design choices` sections that are only boilerplate. Rejected: one generic `choropleth` spec that takes its indicator at run time (unreviewed combinations; see *Non-expert parameters*), and map settings inside Indicators (a color change would make compiled code stale). Raised in chunk 2. |
| **GeoPackage layers** | A `layer` field on Geography, for multi-layer files. Not needed while every file has one layer. |
