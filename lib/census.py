"""Read Census Data API snapshots into tables (census_api spec, § Schema and § Notes)."""

import json

import numpy as np
import pandas as pd

from lib.snapshot import Snapshot

# Annotation values: codes, not numbers. They must never enter a calculation.
ANNOTATIONS = {-999999999, -888888888, -666666666, -555555555, -333333333, -222222222}

GEO_PARTS = ["state", "county", "tract", "block group"]

# census_unit → GEOID length. Units are requested inside their state and counties.
UNITS = {"block group": 12, "tract": 11}


def requests_for(geo_ids, census_unit: str) -> list[tuple[str, list[str]]]:
    """(for, in) for each API request that covers these units: one per state, listing
    the counties their GEOIDs fall in. The extent comes from the units, never from a spec."""
    if census_unit not in UNITS:
        raise ValueError(f"unknown census_unit: {census_unit}")
    ids = pd.Series(list(geo_ids), dtype=str)
    bad = ids[ids.str.len() != UNITS[census_unit]]
    if len(bad):
        raise ValueError(f"not {census_unit} GEOIDs: {', '.join(bad[:5])}")
    out = []
    for state, counties in ids.str[2:5].groupby(ids.str[:2]):
        in_ = [f"state:{state}", f"county:{','.join(sorted(set(counties)))}"]
        if census_unit == "block group":
            out.append(("block group:*", in_ + ["tract:*"]))
        else:
            out.append(("tract:*", in_))
    return out


def read(snap: Snapshot, fields: list[str]) -> pd.DataFrame:
    """One row per unit: GEOID (text), each field as a number (NaN for annotations and nulls),
    and `annotation`, which names any field that held an annotation value or was not published."""
    rows = json.loads(snap.path.read_text())
    df = pd.DataFrame(rows[1:], columns=rows[0], dtype=object)
    parts = [p for p in GEO_PARTS if p in df.columns]
    df["GEOID"] = df[parts].astype(str).agg("".join, axis=1)
    notes = pd.Series("", index=df.index)
    for f in fields:
        values = pd.to_numeric(df[f], errors="raise").astype(float)
        is_null = values.isna()
        is_annotation = values.isin(ANNOTATIONS)
        notes[is_annotation] += f + "=" + values[is_annotation].astype(int).astype(str) + "; "
        notes[is_null] += f + " not published; "
        df[f] = values.mask(is_annotation, np.nan)
    df["annotation"] = notes.str.rstrip("; ")
    return df[["GEOID", *fields, "annotation"]]


def estimate_moe(table: pd.DataFrame, field: str) -> tuple[pd.Series, pd.Series]:
    """Estimate and MOE for one _E field, after `read`. An annotated estimate blanks both;
    an annotated MOE alone blanks only the MOE. `annotation` already names what was annotated."""
    est = table[field]
    moe = table[field[:-1] + "M"].where(est.notna())
    return est, moe


def with_moe(fields: list[str]) -> list[str]:
    """Every _E field followed by its _M field (pulled automatically)."""
    out = []
    for f in fields:
        out.append(f)
        if f.endswith("E"):
            out.append(f[:-1] + "M")
    return out
