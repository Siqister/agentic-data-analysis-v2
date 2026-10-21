# Cleveland Analysis — Start Here

This is the entry point for any AI agent (or person) working in this project. Read it fully before doing anything else.

## What this project is

A spec-driven workflow for geospatial data analysis and visualization, tested on a citywide plan for Cleveland, Ohio. It covers demographics, economy, and neighborhood health.

A domain expert writes plain-language **specs**: which data to use, how each measure is calculated, and how it should be mapped. The agent turns those specs into code, runs it, and produces **CSV tables** and **interactive maps**. Each output records exactly what it was built from.

Specs follow the **Open Knowledge Format (OKF) v0.2** ([architecture.md § 3](architecture.md#3-specs-and-the-open-knowledge-format)). Guiding principle: **minimalism**. No field, file, or step that doesn't earn its place.

## Read in this order

1. **This file**: the rules.
2. **[architecture.md](architecture.md)**: the full requirements. If something here seems to conflict with it, architecture.md wins.
3. **[roadmap.md](roadmap.md)**: what's done, what's next, and notes from earlier sessions.
4. **[templates/](templates/)**: open the matching template whenever you write or check a spec.
5. **[tests/validation.md](tests/validation.md)**: read before building or running checks.

## Rules

1. **Specs are the source of truth.** Compute only what a spec describes. If a spec is unclear, incomplete, or seems wrong, stop and ask the expert. Never guess.
2. **Pull only what a spec names.** Data may come only from a Resource or Geography that has a spec, and only the specific datasets and fields named in an Indicator or Crosswalk. If you think more data is needed, tell the expert and suggest sources. Never write a Resource spec on your own.
3. **Do not interpret.** Produce indicators and maps, not findings. Don't describe, rank, or characterize places. Titles describe what is measured, never what it shows.
4. **Leave pinned code alone.** Regenerate compiled code only when its spec has changed or the expert asks.
5. **Use the shared helpers.** Crosswalks, margin-of-error math, rates, point aggregation, and maps go through `lib/`. Don't reimplement them. Changes to `lib/` need the expert's review.
6. **Only the expert approves.** New specs start as `status: draft`. Only the expert sets `stable` or marks code as reviewed.
7. **Protect secrets and data.** Never commit `.env` or `data/`. Never print or log an API key.
8. **Keep the roadmap current.** Before ending a session, or when stopping partway through, update [roadmap.md](roadmap.md).

## Two modes

Ask which mode applies at the start of a session if it isn't clear.

| Mode | Who | Can do | Cannot do |
|---|---|---|---|
| **Author** | Domain expert, working with the agent | Write and edit specs, compile and review code, edit `lib/`, run tests, produce outputs | — |
| **Run** | Anyone | Choose which existing indicators and maps to produce, and run them | Change anything. Only `stable` specs with reviewed, up-to-date code can run. |

## Glossary

| Term | Meaning |
|---|---|
| **Resource** | One API, file, or dataset we're allowed to use, e.g. the Census Data API. It explains *how to access* the data. |
| **Geography** | One boundary file we report on: city, neighborhoods, census tracts, or block groups. |
| **Crosswalk** | How to move data from one geography to another, e.g. block groups → neighborhoods. |
| **Indicator** | One measure, e.g. "% of households with housing cost burden." It names *exactly what data to pull* and how to compute with it. |
| **Visualization** | One map. For now, a choropleth with tooltips. |
| **Spec** | A Markdown file describing one of the five items above. Its file name is its ID. |
| **OKF** | Open Knowledge Format, the minimal Markdown + YAML standard our specs follow. |
| **Status** | `draft` (not yet approved) or `stable` (approved by the expert). |
| **Compiled code** | The script the agent generates from a spec. It's reviewed once, then pinned. |
| **Stale** | Out of date. *Code* is stale when its spec changed: recompile and review. *Results* are stale when their data changed: rerun. |
| **Snapshot** | A saved copy of one data pull. All computation reads snapshots, never live sources. |
| **Manifest** | A small file next to each output listing everything it was built from. |
| **MOE / CV** | Margin of error (ACS, 90% confidence) and coefficient of variation (error relative to the estimate; higher means less reliable). |
