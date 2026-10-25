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

- A request is a plain-language prompt naming an Indicator or Visualization, e.g. "show me population by block group." The agent maps it to **one spec ID**. If more than one spec could match, it asks which one, naming what tells them apart (e.g. the available years and units), and runs nothing until answered. It never defaults to the latest year (chunk 4a).
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
| **Crosswalk** | Moves data between two Geographies | `specs/crosswalks/` | `from`, `to`, `method`, `weights`, `weights_source`, `min_overlap`, `fields` |
| **Indicator** | One measure, or a reviewed selection of points | `specs/indicators/` | `measure`, `unit`, `geography`, `crosswalks`, `data`, `builds_on`, `reliability`, `window`, `inflation`, `cluster` |
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
- **APIs list their approved datasets.** `datasets` is the short, expert-controlled list of dataset + vintage combinations that Indicators may use, e.g. `acs/acs5` 2023. This keeps Indicators on releases the expert chose. A second vintage is added only for a comparison over time ([§ 4.4](#vintages-and-change-over-time)).
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
- **`GEO_ID` instead of `GEOID`.** Census 2010 cartographic files have no `GEOID` field. Their `GEO_ID` is the summary level, `US`, and the GEOID, e.g. `1400000US39035101101` for a tract. With `census_unit` and `id_field: GEO_ID`, `lib/` keeps the part after `US` as the unit's code. Use cartographic files, not TIGER/Line, for both boundary years: TIGER/Line shapes extend into Lake Erie, which changes the majority-area rule for lakeshore units (chunk 4a).

### 4.3 Crosswalk

Moves data from one Geography (`from`) to another (`to`) by producing a **weights table**: for each source unit, the share that goes to each target unit.

> Example: block group X is 70% in Neighborhood A and 30% in Neighborhood B, so 70% of its counts go to A.

| `method` | How a unit is split | When to use it |
|---|---|---|
| `population_weighted` | By where people, households, or housing units are (`weights`), using census block counts (`weights_source`) | **Default** |
| `areal` | By share of land area | Only when nothing better exists |
| `centroid` | The whole unit goes to the target containing its center | Rough approximation |
| `nested` | Each unit is entirely inside one target (all weights 1) | Block groups → tracts |
| `matched` | Not split: a target unit takes the value of the one source unit it overlaps almost completely, both ways; other target units are blank | The same kind of unit across boundary years, e.g. 2010 tracts → 2020 tracts |

- `nested` is also valid when the `from` Geography's `within` equals `to`: the `within` filter already assigned every unit to that one target, e.g. `bg_2020` → `cle_city`.
- Crosswalks move **counts only**, never percentages or medians, **except `matched`**, which copies each value unchanged ([below](#matched)).

#### `matched`

Pairs units one to one across boundary years, from a Census relationship file (land area from full-resolution TIGER). Decided in chunk 4a.

- **Fields.** `weights_source` is the relationship-file Resource. `min_overlap` (above 0.5, at most 1) is the threshold. `fields` names the file's columns: `from_id`, `to_id`, `from_area`, `to_area`, `shared_area`. No `weights`.
- **Rule.** Source unit *a* and target unit *b* **match** when their shared land area is at least `min_overlap` of *a*'s land area **and** at least `min_overlap` of *b*'s. With `min_overlap` above 0.5, each unit has at most one match. A unit with no land area never matches.
- **Values.** A target unit with a match takes its source unit's `estimate`, `moe` and `note` unchanged. A target unit with no match, or whose match isn't in the `from` Geography, is blank, with `note` "no matching 2010 tract" (built from the `from` Geography's `census_unit` and the boundary year at the end of its ID, [§ 12](#naming); so `from` needs a `census_unit`). Reliability is computed again at the target from the copied values.
- **Any measure** can use it, because nothing is split or summed. A `median` or `index` Indicator still explains it in `# Aggregation`.
- **Build file.** `build/crosswalks/<id>.csv` lists every overlapping pair with both overlap shares and whether it matched, so the expert can review the threshold. Changing `min_overlap` is a frontmatter change: results rerun, no recompile.
- Census blocks are used here to build weights. They are never reported.

### 4.4 Indicator

One measure, such as "% of households with housing cost burden", or a reviewed selection of points ([below](#selections-measure-points)).

- **`geography`** is where it's calculated, usually `bg_2020`. It's also reported there.
- **`crosswalks`** lists the extra geographies it's reported at. Each crosswalk's `to` is an output geography, and its `from` must equal the Indicator's `geography`.
- **`data`** names exactly what to pull (an Indicator has `data`, `builds_on`, or both): Resource, dataset, vintage, and each field with its plain meaning. For Census data, the matching `_M` (margin of error) field is pulled automatically for every `_E` field. For a file Resource (no `datasets`), an entry has `resource` and `fields` only, and `lib/` reads only those fields.
- **`measure`** decides how values move to other geographies:
  - `percent`, `rate`, `count`: move the counts, then compute ([§ 12](#12-conventions)).
  - `median`, `index`: with crosswalks, the body needs an `# Aggregation` section explaining a valid method.
  - `percent_change`: the change from one Indicator's value to another's, in percent ([below](#vintages-and-change-over-time)). Never moved through a crosswalk.
  - `cluster`: a cluster number from several Indicators' values ([below](#clusters-measure-cluster)). Never moved through a crosswalk.
- **`unit`** (optional): what the values are in, for display. `count` (the default) or `dollars`. Percentages come from `measure: percent`, not `unit`.
- **`reliability`** (survey data only) sets the CV threshold, and whether low-reliability values are flagged or suppressed.
- **`builds_on`** (optional) lists Indicators whose results this one uses. Each must be reported at this Indicator's `geography`. The runner runs them first, as dependencies; compiled code reads their tables at this `geography` with `ctx.indicator(id)` (from `outputs/tables/`, never recomputed). Their snapshots count as this Indicator's data, so a new snapshot below reruns it.
- **Body:** `# Definition` (universe, numerator, denominator, exclusions), `# Computation` (steps), `# Caveats`. Add `# Point rules` for point data: outside-city points, boundary points, accepted geocodes, and denominator.
- **The body is about the measure, not the place** ([Separation of concerns](#separation-of-concerns)). Steps that are the same for every Indicator are done by `lib/` and aren't repeated: pulling the fields for the geography's units, joining them to the units (§ 12), applying the listed crosswalks, and computing reliability at every geography. The compiled code returns one table at the Indicator's `geography`; the runner does the rest.

#### Vintages and change over time

One Indicator has one vintage, fixed in its `data`. The year is **never a run-time parameter**: it decides the Geography (ACS 2010–2019 is published on 2010 census geography, 2020 onward on 2020 geography), the units available (the Census API serves block groups only from vintage 2013), the crosswalks, and sometimes the field codes, and those are reviewed parts of the graph. Rejected: one Indicator whose year is taken from the prompt (unreviewed combinations, colliding outputs). Decided in chunk 4.

- **Each vintage is its own Indicator**, with the ACS end year at the end of its ID ([§ 12](#naming)), e.g. `median_household_income_tract_2010` beside `median_household_income_tract_2024`. It reports published values in that year's dollars; inflation adjustment belongs to the comparison.
- **The same published value at a second Census unit** is its own Indicator too, because a median can't move from block groups to tracts. For a unit other than the block group, the unit goes before the year: `median_household_income_tract_2024`. The block group is the default unit and isn't named (`median_household_income_2024`). Decided in chunk 4a; an alternative is in [§ 13](#13-deferred) (*Published values at other units*).
- **A change Indicator** `builds_on` two vintage Indicators reported at the same geography. Its ID names both years, e.g. `median_household_income_tract_pct_change_2010_2024`.
  - `measure: percent_change`; `builds_on` has exactly two Indicators, **start first, then end**, with the same `unit` (none means `count`). No `data`, `crosswalks`, `reliability` or `unit`.
  - `estimate` = (end ÷ start − 1) × 100. **No MOE for the change** (decided in chunk 4b, a proof of concept): `moe`, `cv` and `reliability` are blank, and the table carries the inputs in `start`, `start_moe`, `end`, `end_moe` ([§ 12](#output-tables-csv)). If either input is blank, so is the change, and `note` says which input and why.
  - **`inflation`** (optional): `{ index, from: { year, value }, to: { year, value }, source, retrieved }`, both values from the same published table. Only when both inputs have `unit: dollars`. `start` and `start_moe` are multiplied by `to.value ÷ from.value`, so both inputs are in the end year's dollars. Without `inflation`, `start` and `start_moe` are the start Indicator's values as published. The index values are written in the spec with their source instead of coming from a Resource: the one exception to AGENTS.md rule 3 (expert's decision, chunk 4b).
  - Its `# Caveats` are copied into its output manifests ([§ 8](#8-manifests)).
- **The change math lives in `lib/`**, so a change Indicator's compiled code is a few lines. A new pair of years is a copied spec with new `builds_on` and a quick review; the agent may draft it from a prompt in author mode.
- When a third vintage of one measure is needed, revisit *Non-expert parameters* ([§ 13](#13-deferred)).

#### Clusters (`measure: cluster`)

A cluster Indicator groups units by several Indicators' values at once: each unit's inputs form one feature vector, and k-means gives it a cluster number. More inputs are added by editing `builds_on`. Decided in chunk 6a.

- **ID** names what it combines, then `cluster`, the unit and both years, like a change Indicator ([§ 12](#naming)): `income_population_cluster_tract_2010_2024`.
- **`builds_on`** has two or more Indicators, each reported at this `geography`. The first input sets the numbering. No `data`, `crosswalks`, `reliability`, `unit` or `inflation`.
- **`cluster`**: `{ method, k, seed, log }`. `method` is `kmeans` (the only one for now); `k`, the number of clusters, from 2 to 10; `seed`, a whole number; `log` (optional), inputs to take the natural log of, each in `builds_on`.
- **Computation**, all in `lib/` (the compiled code is a few lines):
  1. Read each input's `estimate`, in `builds_on` order. A unit with any blank input is not clustered: its `estimate` is blank, and `note` lists each blank input by ID with that input's note.
  2. Take the log of each input in `log`. Each must have only positive values (checked at run time).
  3. Scale each input to z-scores over the clustered units (population SD, ddof 0). **No clipping or trimming.**
  4. k-means: scikit-learn `KMeans`, `n_clusters` = `k`, `random_state` = `seed`, `n_init` = 50 (fixed in `lib/`), Lloyd algorithm.
  5. Number the clusters 1 … k in ascending order of their members' median of the first input (as published, before the log); ties go by the next input.
  6. `estimate` = the cluster number; `moe`, `cv` and `reliability` are blank. The table also carries each input's `estimate` ([§ 12](#output-tables-csv)).
- **Run-time checks** (structural, so a failure stops the run): `k` ≤ the number of clustered units; every cluster has at least one unit; each clustered unit is nearest its own cluster's center in z-score space.
- **Diagnostics.** `build/clusters/<id>__<geography>__diagnostics.csv`, never published: one row for each k from 2 to 8, with the spec's other settings: inertia, mean silhouette, stability (mean adjusted Rand index over 50 seeded bootstrap resamples) and cluster sizes; the spec's `k` is marked. The expert uses it to choose `k`.
- **Changing `k`, `seed` or `log`** changes the spec, so the code is stale ([§ 6](#6-compiled-code-and-staleness)): recompile and review.
- **Clusters are numbered, never named.** The agent doesn't name, rank or describe them (AGENTS.md rule 4). Names are the expert's and will go in a spec.
- Its `# Caveats` are copied into its output manifests ([§ 8](#8-manifests)).

#### Selections (`measure: points`)

A selection is a reviewed set of points, e.g. the reported crime incidents in a time window. Later Indicators can build on it (`builds_on`), e.g. to count points per unit. A different selection (say, property crimes only) is a new Indicator, not a parameter.

- **ID** starts with `points_` ([§ 12](#naming)). The time window doesn't go in the ID.
- **`geography`** is the clip extent: points outside its boundary are excluded. There are no `crosswalks`, `reliability` or `unit`.
- **`window`** (optional): `{ field, from, to }`, ISO dates, both inclusive. `field` is one of the Indicator's `data` fields. Dates are local dates ([§ 12](#dates-and-times)); `lib/` converts the times before comparing, so compiled code doesn't repeat it. Changing the window changes the spec, so the code is stale.
- **The Indicator does all the filtering**, so its body may name its Resource's fields. Still no place names. Such an Indicator is tied to one Resource by nature, so it's less reusable than a Census Indicator.
- **Body:** `# Definition`, `# Computation`, `# Point rules`, `# Caveats`.
- **Compiled code** returns a point table (the fields the body names, geometry in EPSG:3734) plus the number of rows excluded at each step, by reason. The runner writes it to `build/points/<id>__<geography>.gpkg` with a manifest ([§ 8](#8-manifests)). It skips the per-unit table checks and reliability. A selection is never published: it stays in `build/`, and maps embed only aggregated hexes ([§ 12](#privacy)).

### 4.5 Visualization

One map. **`map`** (optional) sets the kind: `choropleth` (the default) or `hexbin`.

- Classification (`classification`, `classes`, `breaks`) and `colors` are always set in the spec, **never chosen by the agent**.
- Output: a self-contained HTML file using D3 v7 (pinned version), with its data embedded.
- The page's source note lists the Resource and Geography titles (for an Indicator with only `builds_on`, those of its inputs; plus "Margins of error at 90% confidence." when any data is from the Census), then the spec's `# Source note` text unless it is "None.".

**Choropleth.** Its `indicator` is not a `points` Indicator.
- **`indicator`** sets the color. **`geography`** must be one the Indicator is reported at.
- The tooltip shows the unit's name, the estimate, the margin of error, and the reliability. It also shows any `also_show` Indicators.
- **`percent_change`:** the tooltip and legend show a signed percent ("+12.3%"); the tooltip adds `start` and `end`, formatted by the inputs' `unit` ("Start, in end-year dollars" only with `inflation`), and leaves out the blank MOE and reliability. It's drawn with `manual` breaks around 0 and a diverging scheme.
- **`cluster`** (chunk 6a): `classification: categorical`, which is only for a `cluster` Indicator and the only classification it takes. `classes` equals the Indicator's `k`; `colors` is a d3 categorical scheme with at least `k` colors (e.g. `Tableau10`); no `breaks`. Cluster n takes the scheme's nth color. Units not clustered are light gray, labelled "not clustered". The tooltip shows the unit's name, "Cluster 3", and each input formatted by its `unit` and `measure` ("$41,743", "−12.0%"), with no MOE or reliability. The legend has one row per cluster: its color, "Cluster n", the number of units, and the median of each input.

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

Known gap, accepted by the expert (chunk 3): a Visualization's `# Source note` text is body, so editing it doesn't redraw the map. Redraw with `run <id> --mode author --force`.

"Rerun" means running already-reviewed code again. "Recompile" means generating new code, which then needs the expert's review.

Compiled code is tracked in git.

---

## 7. Shared helper library

`lib/` holds the operations that repeat across specs. The expert reviews them once, tests confirm them, and they change only with review.

| Helper | What it does |
|---|---|
| Fetch & load | Fetch a request from a Resource into a snapshot; load snapshots and Geographies; read only the named fields of a file Resource |
| Runner | Walk the graph from a requested spec, check staleness, fetch, run `builds_on` Indicators first, compute, apply crosswalks and reliability, test, and write outputs ([§ 2](#invocation)) |
| Selection | For a `points` Indicator: apply the `window` in local dates, then write the compiled code's points and exclusion counts to `build/points/` |
| Build crosswalk | Build a weights table using one of the allowed methods, or the pairs table for `matched` |
| Apply crosswalk | Move counts and their margins of error between geographies, or copy matched values unchanged |
| Rate from counts | Percentage or rate from numerator and denominator counts, with margin of error |
| Change | Percent change from a start and an end Indicator's tables, with an inflation factor when there is one; carries the inputs and their MOEs |
| Cluster | For a `cluster` Indicator: build the input table from `builds_on` with blank handling and notes, log, z-scores, k-means, numbering, the run-time checks, the diagnostics file, and per-cluster medians |
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

An Indicator that `builds_on` others lists their snapshots in `data` (taken from their manifests) and adds an `indicator_inputs` block: each input table's path and fingerprint. The output is stale when an input's fingerprint changes, like a map's `indicator_output`.

A `percent_change` or `cluster` Indicator's table manifest, and its map's manifest, also have a `caveats` list: the bullets of its `# Caveats`, copied. Other Indicators keep their caveats in the spec only (chunks 4b, 6a).

A `cluster` Indicator's table and map manifests also have a `clusters` block: `method`, `k`, `seed`, `log`, the number of units clustered and not, and for each cluster its number, size, and the median of each input in its own unit.

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
- **Delimited text files** (e.g. a Census relationship file): `lib/` reads only the named columns, all as text so codes keep their leading zeros, with any byte-order mark removed. Numbers are converted where they're used.
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
│   ├── points/             selections from points Indicators + manifest (never published)
│   └── clusters/           diagnostics for cluster Indicators (never published)
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
  | Indicator | what it measures, not where; Census data ends with the ACS end year, after the unit if it isn't the block group ([§ 4.4](#vintages-and-change-over-time)) | `housing_cost_burden_pct_2024`, `median_household_income_tract_2024` |
  | Indicator (cluster) | what it combines, then `cluster`, the unit and both years | `income_population_cluster_tract_2010_2024` |
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
- **Medians** can't be moved by allocation. Use a valid method described in `# Aggregation` (e.g. a `matched` crosswalk, [§ 4.3](#matched)), or report at the native geography only.
- **Citywide values** are aggregated from the native geography like any other output. The Census Bureau's published value for Cleveland city is a **known-answer check**, not the reported figure.

### Uncertainty (ACS)

- Carry margins of error (90% confidence) through every step, using Census Bureau formulas. For example, the margin of error of a sum is √(sum of squared MOEs).
- CV = (MOE ÷ 1.645) ÷ estimate. A suggested threshold is 0.30, set per Indicator. `reliability` is `low` above it, otherwise `ok`, at every geography the Indicator is reported at.
- An estimate of 0 has no CV: `cv` is blank, `reliability` is `low`, and `note` says "estimate is 0; CV undefined".
- A blank `estimate` or `moe` has no CV: `cv` and `reliability` are blank.
- **Counts through a crosswalk:** estimate = Σ weight × estimate, MOE = √Σ (weight × MOE)². If some units have a blank estimate or MOE, the sums use the units that have one, and `note` says how many were left out of each. Through a `matched` crosswalk, a count is copied unchanged with its MOE and note, as for any measure ([§ 4.3](#matched)).

### Output tables (CSV)

| Column | Meaning |
|---|---|
| `geography_id` | Unit code (text) |
| `geography_name` | Display name, if any |
| `estimate` | The value |
| `moe`, `cv` | Margin of error and CV (blank if not applicable) |
| `reliability` | `ok` or `low` |
| `numerator`, `numerator_moe`, `denominator`, `denominator_moe` | For percentages and rates |
| `start`, `start_moe`, `end`, `end_moe` | For `percent_change` only, after `reliability`: the two inputs; `start` and `start_moe` multiplied by the inflation factor when there is one, otherwise as published |
| one column per input, named by its Indicator ID | For `cluster` only, after `reliability`: each input's `estimate` as published (before log and scaling). `estimate` is the cluster number, a whole number 1 … k, shown as "Cluster 3"; `moe`, `cv` and `reliability` are blank |
| `note` | Anything unusual, e.g. "suppressed: low reliability" |

- Values are stored at full precision and rounded only for display: percentages to 1 decimal place (a percent change with its sign, e.g. "+12.3%"), counts and dollars to whole numbers (dollars with a `$`).
- **Missing or suppressed values are left blank, never 0**, with the reason in `note`.
- **Compute with flagged uncertainty rather than stop.** When some inputs are blank, compute from the ones that have values and say what was left out in `note`. Stop only for structural problems (a missing unit, a broken join, a spec that doesn't say what to do), never because data is incomplete. (Expert's principle, chunk 2.)
- **Not published at a level:** the Census Data API returns `null` for a field that isn't published at a geography's `census_unit`. If every unit is `null`, the run stops (structural). If only some are, those values are blank with "not published" in `note`.
- **A missing unit is an error; a blank value is not.** Every unit of the geography gets a row. A unit with no row in the source stops the run. A unit whose value is blank (an annotation, a coded value, suppression), with its reason in `note`, is a normal result, and its `reliability` is blank.

### Maps

- Units with no value are drawn light gray (`#d9d9d9`). On a cluster map they're labelled "not clustered".
- **Hexbin maps:** hexes inside the geography with no points are drawn light gray (`#d9d9d9`) and labelled as having none (e.g. "no incidents"); classes are computed over hexes with at least one point. Edge hexes are clipped to the geography's outline, so they cover less area and tend to fall in a lower class.
- Titles describe what is measured, never what it shows.

### Tech stack

- Python 3.11 or newer: pandas, geopandas, shapely, pyyaml, requests, scikit-learn (k-means and its diagnostics; pinned so clusters are reproducible).
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
| **Non-expert parameters** | Pre-approved settings run-mode users may change, e.g. survey year. Trigger for survey year: a third vintage of one measure ([§ 4.4](#vintages-and-change-over-time)); then an approved list of years, with the year in output names. |
| **Data-source proposals log** | A place for the agent's suggested new sources. For now, they're raised in conversation. |
| **More OKF features** | `sources`, `stale_after`, attested computation, `log.md`. |
| **Packaging as a skill** | After the Cleveland study works end to end. AGENTS.md rule 1 (route every request through the runner) moves into the skill, with a description that matches plain-language requests. |
| **Shared Visualization defaults** | One Visualization spec per map stays the rule: each map keeps its own ID, approval, and `# Design choices`. Once house style repeats across many maps, make `classification` and `classes` optional, with defaults in `lib/`; changing a default is then a reviewed `lib/` change that reruns all results. Triggers: one setting changed across every map, shared color scales across related maps (*Visualization rules*), or `# Design choices` sections that are only boilerplate. Rejected: one generic `choropleth` spec that takes its indicator at run time (unreviewed combinations; see *Non-expert parameters*), and map settings inside Indicators (a color change would make compiled code stale). Raised in chunk 2. |
| **Published values at other units** | An `# Aggregation` method "use the published value at the target unit", through a block group → tract crosswalk, so one Indicator covers both units instead of one Indicator per unit ([§ 4.4](#vintages-and-change-over-time)). More general, more `lib/` work. Trigger: many measures needed at tracts. Raised in chunk 4a. |
| **GeoPackage layers** | A `layer` field on Geography, for multi-layer files. Not needed while every file has one layer. |
