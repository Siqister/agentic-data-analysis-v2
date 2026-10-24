"""Draw a choropleth from a Visualization spec as a self-contained HTML file (architecture.md § 4.5).

D3 v7.9.0 is embedded from lib/vendor/, so the page works offline and the version is pinned.
"""

import html
import json
from pathlib import Path

import geopandas as gpd
import numpy as np
import pandas as pd
import shapely
from shapely.geometry.polygon import orient

from lib import ROOT
from lib.geography import WEB_CRS

D3 = ROOT / "lib" / "vendor" / "d3.v7.9.0.min.js"
NO_VALUE = "#d9d9d9"


def breaks(values: pd.Series, classification: str, classes: int, manual: list | None = None) -> list[float]:
    """The classes − 1 thresholds between classes. A value equal to a threshold goes to the higher class."""
    v = values.dropna().astype(float).to_numpy()
    if classification == "quantile":
        # Same as d3.scaleQuantile (R-7 quantiles).
        return [float(np.quantile(v, i / classes)) for i in range(1, classes)]
    if classification == "equal_interval":
        lo, hi = v.min(), v.max()
        return [float(lo + (hi - lo) * i / classes) for i in range(1, classes)]
    if classification == "manual":
        return [float(b) for b in manual]
    raise NotImplementedError(f"classification {classification} isn't built yet")


def _geojson(gdf: gpd.GeoDataFrame) -> dict:
    g = gdf.to_crs(WEB_CRS)
    # D3 expects polygon exteriors wound clockwise (the reverse of RFC 7946).
    geoms = shapely.set_precision(g.geometry.values, 1e-6)
    g = g.set_geometry(gpd.GeoSeries([orient(p, sign=-1.0) if p.geom_type == "Polygon" else
                                      shapely.MultiPolygon([orient(q, sign=-1.0) for q in p.geoms])
                                      for p in geoms], crs=WEB_CRS))
    return json.loads(g.to_json(drop_id=True))


def draw(spec_meta: dict, measure: str, unit: str, table: pd.DataFrame, geo: gpd.GeoDataFrame,
         source_note: str, out: Path) -> list[float]:
    """Write the map. Returns the class breaks used."""
    t = table.drop(columns=["geography_name"], errors="ignore")
    merged = geo.merge(t, on="geography_id", how="left")
    if merged["estimate"].notna().sum() == 0:
        raise ValueError("no values to map")
    b = breaks(merged["estimate"], spec_meta["classification"], spec_meta["classes"], spec_meta.get("breaks"))
    keep = ["geography_id", "geography_name", "estimate", "moe", "reliability", "note", "geometry"]
    merged = merged[keep].replace({np.nan: None})
    config = {
        "title": spec_meta["title"],
        "colors": spec_meta["colors"],
        "classes": spec_meta["classes"],
        "breaks": b,
        "format": "percent" if measure == "percent" else unit,
        "noValue": NO_VALUE,
    }
    page = TEMPLATE.format(
        title=html.escape(spec_meta["title"]),
        source=html.escape(source_note),
        d3=D3.read_text(),
        config=json.dumps(config),
        data=json.dumps(_geojson(gpd.GeoDataFrame(merged, geometry="geometry", crs=geo.crs))),
    )
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(page)
    return b


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
  #map path {{ stroke: #fff; stroke-width: 0.4; }}
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
const color = d3.scaleThreshold().domain(config.breaks).range(scheme[config.classes]);
const fmt = config.format === "percent" ? (v => d3.format(".1f")(v) + "%")
  : config.format === "dollars" ? d3.format("$,.0f") : d3.format(",.0f");
const fill = v => v == null ? config.noValue : color(v);

const svg = d3.select("#map");
const projection = d3.geoMercator().fitSize([900, 700], data);
const path = d3.geoPath(projection);
const tip = d3.select("#tip");
svg.selectAll("path").data(data.features).join("path")
  .attr("d", path)
  .attr("fill", d => fill(d.properties.estimate))
  .on("mousemove", (event, d) => {{
    const p = d.properties;
    const lines = [
      "<b>" + (p.geography_name || p.geography_id) + "</b>" + (p.geography_name ? " (" + p.geography_id + ")" : ""),
      "Estimate: " + (p.estimate == null ? "no value" : fmt(p.estimate)),
      "Margin of error: " + (p.moe == null ? "—" : "±" + fmt(p.moe)),
      "Reliability: " + (p.reliability || "—"),
    ];
    if (p.note) lines.push("Note: " + p.note);
    tip.html(lines.join("<br>")).style("display", "block")
      .style("left", Math.min(event.clientX + 12, window.innerWidth - 220) + "px")
      .style("top", (event.clientY + 12) + "px");
  }})
  .on("mouseleave", () => tip.style("display", "none"));

const edges = [null, ...config.breaks, null];
const legend = d3.select("#legend");
scheme[config.classes].forEach((c, i) => {{
  const lo = edges[i], hi = edges[i + 1];
  const label = lo == null ? "under " + fmt(hi) : hi == null ? fmt(lo) + " and over" : fmt(lo) + " to under " + fmt(hi);
  legend.append("span").html('<i style="background:' + c + '"></i>' + label);
}});
legend.append("span").html('<i style="background:' + config.noValue + '"></i>No value');
</script>
</body>
</html>
"""
