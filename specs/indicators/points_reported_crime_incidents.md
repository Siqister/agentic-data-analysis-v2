---
type: Indicator
title: Reported crime incidents (NIBRS Group A)
description: Locations of reported crime incidents with at least one NIBRS Group A offense, one point per incident, in a set time window.
status: draft
tags: [crime, points]

measure: points
geography: cle_city

data:
  - resource: cle_crime
    fields:
      CaseNumber: Police case number; one per incident
      IncidentDesc: NIBRS offense type of the row's offense
      OffenseDate: Date and time the offense occurred
      SHAPE: Point location of the incident

window:
  field: OffenseDate
  from: 2025-11-30
  to: 2026-09-30
---

# Definition

The locations of crime incidents reported to police, one point per incident. An incident is one `CaseNumber` with at least one NIBRS Group A offense, following the NIBRS incident definition (FBI, *A Guide to Understanding NIBRS*).

- **Universe:** reported incidents whose offense date falls in the window
- **Selected:** incidents with at least one Group A offense ([cle_crime § NIBRS offense types](../resources/cle_crime.md#nibrs-offense-types)), excluding Justifiable Homicide
- **Exclusions:** Group B offenses, rows with no `IncidentDesc`, Justifiable Homicide, incidents with no point, and points outside the clip extent

# Computation

1. Read the named fields.
2. **Offense type.** Keep rows whose `IncidentDesc` is on the Group A list. Exclude, each as its own reason: rows with no `IncidentDesc`; Group B rows; Justifiable Homicide (a Group A code that isn't a crime). A value on neither list stops the run: the Resource's lists must be updated first.
3. **Window.** Keep rows whose `OffenseDate` falls in the frontmatter `window`, both dates inclusive. `lib/` applies the window in local dates ([architecture.md § 12](../../architecture.md#dates-and-times)). A row with no `OffenseDate` is excluded as "no offense date".
4. **One point per incident.** A row with no `CaseNumber` is excluded as "no case number". Group the kept rows by `CaseNumber` and keep the first. All rows in a case share one location and date, so which row is kept doesn't matter. The extra rows are recorded as "additional offense in the same incident".
5. Apply the point rules below.
6. **Output:** `CaseNumber`, `OffenseDate`, and the point in EPSG:3734. Record the number of rows excluded at each step, by reason.

# Point rules

- **Outside the clip extent:** points outside the geography's boundary are excluded, tested against the boundary in EPSG:3734. The `City` field is not used.
- **On the boundary:** a point on the boundary line counts as inside.
- **Accepted geocodes:** any row with a point. Rows with no point ("Not Located") are excluded.
- **Denominator:** none. This is a selection, not a rate.

# Caveats

- These are crimes **reported to police**. Many crimes are never reported, and reporting rates differ by offense type and by community.
- **Incidents, not offenses or victims:** an incident with several offenses or several victims is one point.
- **Located where the incident happened,** not where victims or residents live. Places with many visitors and few residents look dense.
- Some Group A offenses (drug and weapon law violations) mostly reflect **police activity**, not underlying crime levels.
- **All Group A offense types are pooled,** so the pattern mixes very different crimes.
- **Not comparable** with figures from the FBI's old Summary Reporting System (hierarchy rule) or with the City's legacy pre-2025-11-11 dataset.
- **Late reports:** offenses near the end of the window may still be reported after the download.
- Excluded rows are listed by reason in the selection's manifest.
