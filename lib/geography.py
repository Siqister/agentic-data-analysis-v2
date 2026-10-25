"""Load Geographies, applying their `within` rule (architecture.md § 4.2)."""

import geopandas as gpd

from lib.snapshot import Snapshot, local_file, url_file
from lib.specs import Spec

AREA_CRS = 3734   # NAD83 / Ohio North, for areas and distances
WEB_CRS = 4326    # WGS84, for web maps


def snapshot(spec: Spec) -> Snapshot:
    res = spec.meta["resource"]
    if res.startswith(("http://", "https://")):
        return url_file(spec.id, res)
    return local_file(spec.id, res)


def load(spec: Spec, specs: dict[str, Spec], snaps: list[Snapshot] | None = None) -> gpd.GeoDataFrame:
    """Columns: geography_id (text), geography_name, geometry (in the file's own CRS).
    Snapshots used (this one and any `within` parent) are appended to `snaps`."""
    snap = snapshot(spec)
    if snaps is not None:
        snaps.append(snap)
    id_field = spec.meta["id_field"]
    name_field = spec.meta.get("name_field")
    path = f"/vsizip/{snap.path}" if snap.path.suffix == ".zip" else str(snap.path)
    gdf = gpd.read_file(path, columns=[c for c in (id_field, name_field) if c])
    if gdf.crs is None:
        raise ValueError(f"{spec.id}: file has no coordinate system")
    gdf["geography_name"] = gdf[name_field].astype(str) if name_field else ""
    gdf["geography_id"] = gdf[id_field].astype(str)
    if spec.meta.get("census_unit") and id_field == "GEO_ID":
        # Census 2010 cartographic files: <summary level>US<GEOID>; keep the GEOID (§ 4.2).
        if not gdf["geography_id"].str.contains("US", regex=False).all():
            raise ValueError(f"{spec.id}: some GEO_ID values have no 'US' before the GEOID")
        gdf["geography_id"] = gdf["geography_id"].str.split("US", n=1).str[1]
    gdf = gdf[["geography_id", "geography_name", "geometry"]]
    if gdf["geography_id"].duplicated().any():
        raise ValueError(f"{spec.id}: {id_field} is not unique")

    within = spec.meta.get("within")
    if within:
        parent = load(specs[within], specs, snaps)
        gdf = gdf[_keep(gdf, parent, spec.meta["within_rule"])]
        if gdf.empty:
            raise ValueError(f"{spec.id}: no units are within {within}")
    return gdf.reset_index(drop=True)


def _keep(units: gpd.GeoDataFrame, parent: gpd.GeoDataFrame, rule: str):
    """Boolean mask of units kept by the within rule. Areas are measured in EPSG:3734."""
    u = units.geometry.to_crs(AREA_CRS)
    p = parent.geometry.to_crs(AREA_CRS).union_all()
    if rule == "majority_area":
        candidates = u.intersects(p)
        share = u[candidates].intersection(p).area / u[candidates].area
        mask = candidates.copy()
        mask[candidates] = share > 0.5
        return mask.values
    if rule == "centroid":
        return u.centroid.within(p).values
    if rule == "any":
        return (u.intersects(p) & ~u.touches(p)).values
    raise ValueError(f"unknown within_rule: {rule}")
