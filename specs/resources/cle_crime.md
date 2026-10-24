---
type: Resource
title: Cleveland Police crime incidents
description: Offenses reported to the Cleveland Division of Police, one row per offense, with point locations.
resource: data/static/cle_crime/Crime_Incidents_P1RMS_-6429680527207168309.gpkg
status: stable
tags: [crime, police]
---

# About

Published by the City of Cleveland, Division of Police, on the City's open data portal: <https://data.clevelandohio.gov/datasets/e15e8989c83e4cbd841fb171a6c62f68_0/about>. The live layer is updated daily. Offenses are classified by NIBRS (the FBI's National Incident-Based Reporting System) offense type.

Downloaded by the expert as a GeoPackage on 2026-10-24. It is a local file, hashed in place for manifests, in `data/static/`, which is not committed.

# Access

- A GeoPackage with one layer, `Crime_Incidents`. Geometry column `SHAPE`: points in EPSG:3857 (Web Mercator), embedded in the file.
- `ReportedDate` and `OffenseDate` are datetimes stored in UTC.
- Read only the fields an Indicator names.

# Schema

Fields used by Indicators:

| Field | Meaning |
|---|---|
| `CaseNumber` | Police case number. One case is one incident; it can have several rows, one per offense. |
| `IncidentDesc` | NIBRS offense type of the row's offense. Blank for records that aren't NIBRS offenses or aren't classified yet. |
| `OffenseDate` | Date and time the offense occurred (UTC). |
| `SHAPE` | Point location of the incident. Empty for incidents that couldn't be located. |

Other fields include `ReportedDate`, `Statute` and `StatDesc` (the Ohio Revised Code or Cleveland Codified Ordinance section, and the City's label for it), `Address_Public` (masked to the block, e.g. "40XX Arnold Ct"), `City`, precomputed `NEIGHBORHOOD`, `WARD`, tract, block group and block GEOIDs, `LAT`/`LON`, and Eastern-time date parts (`OffenseYear`, `OffenseMonth`, `OffenseDay`, `HourofDay`, `DOW`, `TimeBlock`). There are no victim, offender or arrest fields.

## NIBRS offense types

`IncidentDesc` values, as spelled in the file, by NIBRS group (FBI, *NIBRS User Manual*). Group A offenses are crimes reported in full incident detail; Group B offenses are reported only when an arrest is made.

**Group A**

Aggravated Assault · All Other Larceny · Animal Cruelty · Arson · Assisting or Promoting Prostitution · Bribery · Burglary/Breaking and Entering · Counterfeiting/Forgery · Credit Card/Automatic Teller Fraud · Destruction/Damage/Vandalism of Property · Drug Equipment Violations · Drug/narcotic Violations · Embezzlement · Extortion/Blackmail · False Pretenses/Swindle/Confidence Game · Forcible Fondling · Forcible Rape · Forcible Sodomy · Gambling Equipment Violations · Hacking/Computer Invasion · Human Trafficking Commercial Sex Acts · Human Trafficking Involuntary Servitude · Identity Theft · Impersonation · Incest · Intimidation · Justifiable Homicide · Kidnaping/Abduction · Motor Vehicle Theft · Murder and Nonnegligent Manslaughter · Negligent Manslaughter · Pocket-Picking · Pornography/Obscene Material · Purse-Snatching · Robbery · Sexual Assault With an Object · Shoplifting · Simple Assault · Statutory Rape · Stolen Property Offenses · Theft From Building · Theft From Coin Operated Machine or Device · Theft From Motor Vehicle · Theft of Motor Vehicle Parts/Accessories · Weapon Law Violations · Welfare Fraud · Wire Fraud

Justifiable Homicide is a Group A code but not a crime: NIBRS records it for completeness.

**Group B**

All Other Offenses · Bad Checks · Disorderly Conduct · Driving Under the Influence · Drunkenness · Family Offenses (Nonviolent) · Liquor Law Violations · Peeping · Runaway · Trespass of Real Property

These lists hold the values present in the 2026-10-24 download. A later download may add values; each new value must be added to one list before an Indicator can use it.

# Notes

- **Coverage starts 2025-11-11.** Earlier rows are a sparse subset (old cases touched in the new system), not a history. They are not comparable with the City's legacy 2016–2025 dataset, which used a different data model.
- **One row is one offense.** Several rows can share a `CaseNumber`; rows in one case share location and time and differ by `Statute`. `PrimaryKey` is not a key, and `OBJECTID` changes between exports.
- **`IncidentDesc` holds NIBRS offense types**, grouped [above](#nibrs-offense-types). Rows without it are non-crime or non-NIBRS records (e.g. "NO CRIME", hit-skip traffic, emergency hospitalization, protection orders), or not yet classified. On a later download, some unclassified rows may gain a classification.
- **No victim data,** so the NIBRS rule "one offense per victim" for crimes against persons can't be applied.
- **`DaysAgo`** depends on the export date. Never use it.
- **Times are stored in UTC.** The derived date parts are in Eastern time. Convert before taking a date: an evening incident has the next day's UTC date ([architecture.md § 12](../../architecture.md#dates-and-times)).
- **Points are more precise than the block-masked address.** Never publish raw points; maps embed only aggregated surfaces at or above the privacy floor ([architecture.md § 12](../../architecture.md#privacy)).
- **Late reports:** counts for recent months grow on later downloads. Most offenses are reported within 30 days, but some are reported a year or more later.
- **Geometry is EPSG:3857.** Clipping and any area or distance work use EPSG:3734 ([architecture.md § 12](../../architecture.md#geography)).
- **`City`** is a field on each row, not a clip: some located points fall outside the city boundary. Clip against a Geography instead.
