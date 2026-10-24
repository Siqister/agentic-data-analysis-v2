"""Read file Resources and select points (architecture.md §§ 4.4, 12).

A selection reads only the fields its Indicator names, takes dates as local dates in
America/New_York, and clips to its geography with boundary points counted as inside.
"""

import warnings
from datetime import date, timedelta
from pathlib import Path

import geopandas as gpd
import pandas as pd
import pyogrio

from lib.geography import AREA_CRS

LOCAL_TZ = "America/New_York"


def read(path: Path, fields: list[str]) -> pd.DataFrame:
    """The named fields of a one-layer file. If the geometry column is named, a GeoDataFrame
    with geometry in EPSG:3734; otherwise a DataFrame."""
    info = pyogrio.read_info(path)
    geom = info.get("geometry_name") or ""
    missing = [f for f in fields if f not in set(info["fields"]) | {geom}]
    if missing:
        raise ValueError(f"{path.name} has no field {', '.join(missing)}")
    with warnings.catch_warnings():
        # GDAL notes ISO times with a trailing ".0Z" as non-conformant, then parses them correctly.
        warnings.filterwarnings("ignore", message="Non-conformant content", category=RuntimeWarning)
        t = pyogrio.read_dataframe(path, columns=[f for f in fields if f != geom],
                                   read_geometry=bool(geom) and geom in fields)
    if isinstance(t, gpd.GeoDataFrame):
        if t.crs is None:
            raise ValueError(f"{path.name} has no coordinate system")
        t = t.to_crs(AREA_CRS)
    return t


def in_window(t: pd.DataFrame, window: dict) -> pd.Series:
    """True where the local date of `window.field` is from `from` to `to`, both inclusive.
    Times without a time zone stop the run: their local date can't be known. Blank times are False."""
    times = t[window["field"]]
    if times.dt.tz is None:
        raise ValueError(f"{window['field']} has no time zone, so its local date can't be taken")
    local = times.dt.tz_convert(LOCAL_TZ)
    lo = pd.Timestamp(_date(window["from"]), tz=LOCAL_TZ)
    hi = pd.Timestamp(_date(window["to"]) + timedelta(days=1), tz=LOCAL_TZ)
    return (local >= lo) & (local < hi)


def inside(points: gpd.GeoSeries, area: gpd.GeoDataFrame) -> pd.Series:
    """True where a point is inside `area` or on its boundary, tested in EPSG:3734.
    Blank geometries are False."""
    return points.to_crs(AREA_CRS).covered_by(area.geometry.to_crs(AREA_CRS).union_all())


def _date(d) -> date:
    return d if isinstance(d, date) else date.fromisoformat(str(d))
