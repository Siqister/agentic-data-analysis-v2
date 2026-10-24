"""Draw a hexbin heat map of a selection as a self-contained HTML file (architecture.md §§ 4.5, 12).

Pointy-top hexes in EPSG:3734 on a grid with its origin at (0, 0), so every hexbin map shares
the grid. The page embeds only hex shapes and class labels: no points and no counts.
"""

import html
import json
import math
from pathlib import Path

import geopandas as gpd
import numpy as np
import pandas as pd
import pyproj
import shapely

from lib.choropleth import D3, NO_VALUE, _geojson, breaks
from lib.geography import AREA_CRS

SQRT3 = math.sqrt(3)
# Metres per unit of EPSG:3734 (US survey feet).
UNIT_M = pyproj.CRS(AREA_CRS).axis_info[0].unit_conversion_factor


def axial(x: np.ndarray, y: np.ndarray, width: float) -> tuple[np.ndarray, np.ndarray]:
    """Axial (q, r) of the hex containing each point, for pointy-top hexes `width` across flats."""
    size = width / SQRT3   # centre to corner
    qf = (SQRT3 / 3 * x - y / 3) / size
    rf = (2 / 3 * y) / size
    # Cube rounding: round all three cube coordinates, then fix the one that moved most.
    sf = -qf - rf
    q, r, s = np.round(qf), np.round(rf), np.round(sf)
    dq, dr, ds = abs(q - qf), abs(r - rf), abs(s - sf)
    fix_q = (dq > dr) & (dq > ds)
    fix_r = ~fix_q & (dr > ds)
    q = np.where(fix_q, -r - s, q)
    r = np.where(fix_r, -q - s, r)
    return q.astype(int), r.astype(int)


def hexagon(q: int, r: int, width: float) -> shapely.Polygon:
    size = width / SQRT3
    cx, cy = width * (q + r / 2), 1.5 * size * r
    return shapely.Polygon([(cx + size * math.cos(math.radians(a)), cy + size * math.sin(math.radians(a)))
                            for a in range(30, 360, 60)])


def grid(area, width: float) -> gpd.GeoDataFrame:
    """Every hex that overlaps `area` (in EPSG:3734), clipped to it: columns q, r, geometry."""
    size = width / SQRT3
    minx, miny, maxx, maxy = area.bounds
    cells = []
    for r in range(math.floor(miny / (1.5 * size)) - 1, math.ceil(maxy / (1.5 * size)) + 2):
        for q in range(math.floor(minx / width - r / 2) - 1, math.ceil(maxx / width - r / 2) + 2):
            cells.append((q, r))
    g = gpd.GeoDataFrame(cells, columns=["q", "r"],
                         geometry=[hexagon(q, r, width) for q, r in cells], crs=AREA_CRS)
    g = g[g.intersects(area)].copy()
    g["geometry"] = [_polygonal(p) for p in g.intersection(area)]
    return g[~g.geometry.is_empty & (g.area > 0)].reset_index(drop=True)


def _polygonal(geom):
    """Only the polygon parts of a clipped hex (a clip can leave stray lines or points)."""
    if geom.geom_type in ("Polygon", "MultiPolygon"):
        return geom
    parts = [p for p in getattr(geom, "geoms", []) if p.geom_type == "Polygon"]
    parts += [q for p in getattr(geom, "geoms", []) if p.geom_type == "MultiPolygon" for q in p.geoms]
    return shapely.MultiPolygon(parts) if parts else shapely.Polygon()


def draw(spec_meta: dict, points: gpd.GeoDataFrame, geo: gpd.GeoDataFrame, source_note: str, out: Path) -> dict:
    """Write the map. Returns a summary for the manifest: hex size, number of hexes, empty hexes,
    hexes per class, and the class breaks (in points per hex)."""
    area = geo.geometry.to_crs(AREA_CRS).union_all()
    width = spec_meta["hex_size_m"] / UNIT_M
    hexes = grid(area, width)

    pts = points.geometry.to_crs(AREA_CRS)
    q, r = axial(pts.x.to_numpy(), pts.y.to_numpy(), width)
    counts = pd.Series(1, index=pd.MultiIndex.from_arrays([q, r], names=["q", "r"])).groupby(level=[0, 1]).sum()
    hexes["count"] = hexes.set_index(["q", "r"]).index.map(counts).fillna(0).astype(int)
    if hexes["count"].sum() != len(points):
        raise ValueError(f"{len(points) - hexes['count'].sum()} points fall in no hex of the geography")

    occupied = hexes["count"] > 0
    if not occupied.any():
        raise ValueError("no points to map")
    k = spec_meta["classes"]
    b = breaks(hexes.loc[occupied, "count"], spec_meta["classification"], k, spec_meta.get("breaks"))
    # A count equal to a break goes to the higher class, as in the choropleth.
    hexes["cls"] = None
    hexes.loc[occupied, "cls"] = np.searchsorted(b, hexes.loc[occupied, "count"], side="right") + 1

    config = {"title": spec_meta["title"], "colors": spec_meta["colors"], "classes": k, "noValue": NO_VALUE}
    page = TEMPLATE.format(
        title=html.escape(spec_meta["title"]),
        source=html.escape(source_note),
        d3=D3.read_text(),
        config=json.dumps(config),
        data=json.dumps(_geojson(hexes[["cls", "geometry"]])),   # classes only: no counts, no points
    )
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(page)
    per_class = hexes.loc[occupied, "cls"].value_counts()
    return {"hex_size_m": spec_meta["hex_size_m"], "hexes": len(hexes), "empty": int((~occupied).sum()),
            "per_class": {int(c): int(per_class.get(c, 0)) for c in range(1, k + 1)}, "breaks": b}


TEMPLATE = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<style>
  body {{ margin: 0; padding: 16px; font: 14px/1.4 system-ui, -apple-system, sans-serif; color: #1a1a1a; background: #fff; }}
  h1 {{ font-size: 18px; margin: 0 0 12px; }}
  #map {{ width: 100%; max-width: 900px; height: auto; display: block; }}
  #map path {{ stroke: #fff; stroke-width: 0.3; }}
  #map path:hover {{ stroke: #1a1a1a; stroke-width: 1.2; }}
  .legend {{ display: flex; flex-wrap: wrap; gap: 4px 12px; margin: 12px 0; font-size: 12px; }}
  .legend span {{ display: inline-flex; align-items: center; gap: 4px; }}
  .legend i {{ width: 14px; height: 14px; display: inline-block; border: 1px solid #ccc; }}
  #tip {{ position: fixed; pointer-events: none; background: #fff; border: 1px solid #999; padding: 6px 8px;
          font-size: 12px; display: none; box-shadow: 0 1px 4px rgba(0,0,0,.2); }}
  .source {{ font-size: 11px; color: #555; max-width: 900px; margin-top: 8px; }}
</style>
</head>
<body>
<h1>{title}</h1>
<div class="legend" id="legend"></div>
<svg id="map" viewBox="0 0 900 700"></svg>
<div id="tip"></div>
<p class="source">{source}</p>
<script>{d3}</script>
<script>
const config = {config};
const data = {data};
const scheme = d3["scheme" + config.colors];
if (!scheme || !scheme[config.classes]) throw new Error("unknown color scheme " + config.colors);
const colors = scheme[config.classes];
const fill = c => c == null ? config.noValue : colors[c - 1];
const label = c => c == null ? "No incidents" : "Class " + c + " of " + config.classes;

const svg = d3.select("#map");
const projection = d3.geoMercator().fitSize([900, 700], data);
const path = d3.geoPath(projection);
const tip = d3.select("#tip");
svg.selectAll("path").data(data.features).join("path")
  .attr("d", path)
  .attr("fill", d => fill(d.properties.cls))
  .on("mousemove", (event, d) => {{
    tip.html(label(d.properties.cls)).style("display", "block")
      .style("left", Math.min(event.clientX + 12, window.innerWidth - 160) + "px")
      .style("top", (event.clientY + 12) + "px");
  }})
  .on("mouseleave", () => tip.style("display", "none"));

const legend = d3.select("#legend");
colors.forEach((c, i) => {{
  const n = i + 1;
  const end = n === 1 ? " (lowest)" : n === config.classes ? " (highest)" : "";
  legend.append("span").html('<i style="background:' + c + '"></i>' + n + " of " + config.classes + end);
}});
legend.append("span").html('<i style="background:' + config.noValue + '"></i>No incidents');
</script>
</body>
</html>
"""
