"""Read Census Data API snapshots into tables (census_api spec, § Schema and § Notes)."""

import json

import numpy as np
import pandas as pd

from lib.snapshot import Snapshot

# Annotation values: codes, not numbers. They must never enter a calculation.
ANNOTATIONS = {-999999999, -888888888, -666666666, -555555555, -333333333, -222222222}

GEO_PARTS = ["state", "county", "tract", "block group"]


def read(snap: Snapshot, fields: list[str]) -> pd.DataFrame:
    """One row per unit: GEOID (text), each field as a number (NaN for annotations),
    and `annotation`, which names any field that held an annotation value."""
    rows = json.loads(snap.path.read_text())
    df = pd.DataFrame(rows[1:], columns=rows[0], dtype=str)
    parts = [p for p in GEO_PARTS if p in df.columns]
    df["GEOID"] = df[parts].agg("".join, axis=1)
    notes = pd.Series("", index=df.index)
    for f in fields:
        values = pd.to_numeric(df[f], errors="raise").astype(float)
        is_annotation = values.isin(ANNOTATIONS)
        notes[is_annotation] += f + "=" + values[is_annotation].astype(int).astype(str) + "; "
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
