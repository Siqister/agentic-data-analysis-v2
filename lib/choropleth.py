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
         source_note: str, out: Path, inflation: bool = False) -> list[float]:
    """Write the map. Returns the class breaks used. For a percent_change map, `unit` is the
    inputs' unit, and `inflation` says whether the start is in end-year dollars."""
    t = table.drop(columns=["geography_name"], errors="ignore")
    merged = geo.merge(t, on="geography_id", how="left")
    if merged["estimate"].notna().sum() == 0:
        raise ValueError("no values to map")
    b = breaks(merged["estimate"], spec_meta["classification"], spec_meta["classes"], spec_meta.get("breaks"))
    change = measure == "percent_change"
    keep = ["geography_id", "geography_name", "estimate", "moe", "reliability", "note", "geometry"]
    if change:
        keep[3:5] = ["start", "end"]   # no MOE or reliability for a change (§ 4.5)
    merged = merged[keep].replace({np.nan: None})
    config = {
        "title": spec_meta["title"],
        "colors": spec_meta["colors"],
        "classes": spec_meta["classes"],
        "breaks": b,
        "format": "signed_percent" if change else "percent" if measure == "percent" else unit,
        "noValue": NO_VALUE,
    }
    page = TEMPLATE.format(
        title=html.escape(spec_meta["title"]),
        source=html.escape(source_note),
        d3=D3.read_text(),
        config=json.dumps(config),
        # Only a percent_change map adds these, so other maps' pages are unchanged.
        change_format=CHANGE_FORMAT if change else "",
        change_lines=_change_lines(unit, inflation) if change else "",
        data=json.dumps(_geojson(gpd.GeoDataFrame(merged, geometry="geometry", crs=geo.crs))),
    )
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(page)
    return b


CHANGE_FORMAT = """
  : config.format === "signed_percent" ? (v => d3.format("+.1f")(v) + "%")"""
CHANGE_LINES = """const {unit} = v => v == null ? "no value" : d3.format("{format}")(v);
    lines.splice(1, 3, "Change: " + (p.estimate == null ? "no value" : fmt(p.estimate)),
      "{start}: " + {unit}(p.start), "End: " + {unit}(p.end));
    """
INPUT_FORMATS = {"dollars": "$,.0f", "count": ",.0f"}


def _change_lines(unit: str, inflation: bool) -> str:
    """Tooltip lines for start and end, formatted by the inputs' unit."""
    if unit not in INPUT_FORMATS:
        raise ValueError(f"a change map of `unit: {unit}` inputs isn't built yet")
    start = "Start, in end-year dollars" if inflation else "Start"
    return CHANGE_LINES.format(unit=unit, format=INPUT_FORMATS[unit], start=start)

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
const fmt = config.format === "percent" ? (v => d3.format(".1f")(v) + "%"){change_format}
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
    {change_lines}if (p.note) lines.push("Note: " + p.note);
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


def draw_categorical(spec_meta: dict, inputs: list, census_unit: str | None, table: pd.DataFrame,
                     clusters: dict, geo: gpd.GeoDataFrame, source_note: str, out: Path) -> None:
    """Write a cluster map (architecture.md § 4.5): cluster n in the scheme's nth color, units not
    clustered in light gray. The tooltip and legend show each input, formatted by its measure and unit.
    `inputs` are the cluster Indicator's builds_on specs; `clusters` its manifest's `clusters` block."""
    ids = [i.id for i in inputs]
    t = table.drop(columns=["geography_name"], errors="ignore")
    merged = geo.merge(t, on="geography_id", how="left")
    if merged["estimate"].notna().sum() == 0:
        raise ValueError("no values to map")
    merged = merged[["geography_id", "geography_name", "estimate", *ids, "note", "geometry"]].replace({np.nan: None})
    units = (census_unit or "unit") + "s"
    config = {
        "colors": spec_meta["colors"],
        "classes": spec_meta["classes"],
        "inputs": [{"id": i.id, "title": i.meta["title"], **_input_format(i)} for i in inputs],
        "clusters": clusters["clusters"],
        "units": units[0].upper() + units[1:],
        "noValue": NO_VALUE,
    }
    page = CATEGORICAL_TEMPLATE.format(
        title=html.escape(spec_meta["title"]),
        source=html.escape(source_note),
        d3=D3.read_text(),
        config=json.dumps(config),
        data=json.dumps(_geojson(gpd.GeoDataFrame(merged, geometry="geometry", crs=geo.crs))),
    )
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(page)


def _input_format(ind) -> dict:
    """A d3-format specifier and suffix for one input: signed percent for a change, percent, or by `unit`.
    (d3's own `%` type multiplies by 100, so the sign is added as a suffix.)"""
    measure = ind.meta["measure"]
    if measure == "percent_change":
        return {"format": "+.1f", "suffix": "%"}
    if measure == "percent":
        return {"format": ".1f", "suffix": "%"}
    unit = ind.meta.get("unit", "count")
    if unit not in INPUT_FORMATS:
        raise ValueError(f"a cluster map input of `unit: {unit}` isn't built yet")
    return {"format": INPUT_FORMATS[unit], "suffix": ""}


CATEGORICAL_TEMPLATE = """<!doctype html>
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
  .legend {{ border-collapse: collapse; margin: 12px 0; font-size: 12px; max-width: 900px; }}
  .legend th, .legend td {{ padding: 2px 8px; text-align: right; vertical-align: bottom; }}
  .legend th:first-child, .legend td:first-child {{ text-align: left; white-space: nowrap; }}
  .legend th {{ font-weight: 600; border-bottom: 1px solid #ccc; }}
  .legend i {{ width: 14px; height: 14px; display: inline-block; border: 1px solid #ccc; vertical-align: -2px; margin-right: 4px; }}
  #tip {{ position: fixed; pointer-events: none; background: #fff; border: 1px solid #999; padding: 6px 8px;
          font-size: 12px; display: none; box-shadow: 0 1px 4px rgba(0,0,0,.2); max-width: 320px; }}
  .source {{ font-size: 11px; color: #555; max-width: 900px; margin-top: 8px; }}
</style>
</head>
<body>
<h1>{title}</h1>
<table class="legend" id="legend"></table>
<svg id="map" viewBox="0 0 900 700"></svg>
<div id="tip"></div>
<p class="source">{source}</p>
<script>{d3}</script>
<script>
const config = {config};
const data = {data};
const scheme = d3["scheme" + config.colors];
if (!scheme || scheme.length < config.classes || !Array.isArray(scheme) || Array.isArray(scheme[0]))
  throw new Error("not a categorical scheme with " + config.classes + " colors: " + config.colors);
const fill = n => n == null ? config.noValue : scheme[n - 1];
const fmts = config.inputs.map(i => d3.format(i.format));
const value = (k, v) => v == null ? "no value" : fmts[k](v) + config.inputs[k].suffix;

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
      p.estimate == null ? "Not clustered" : "Cluster " + p.estimate,
      ...config.inputs.map((i, k) => i.title + ": " + value(k, p[i.id])),
    ];
    if (p.note) lines.push("Note: " + p.note);
    tip.html(lines.join("<br>")).style("display", "block")
      .style("left", Math.min(event.clientX + 12, window.innerWidth - 340) + "px")
      .style("top", (event.clientY + 12) + "px");
  }})
  .on("mouseleave", () => tip.style("display", "none"));

// One row per cluster: color, number, size, and the median of each input.
const legend = d3.select("#legend");
legend.append("tr").html("<th>Cluster</th><th>" + config.units + "</th>" +
  config.inputs.map(i => "<th>Median: " + i.title + "</th>").join(""));
config.clusters.forEach(c => legend.append("tr").html(
  '<td><i style="background:' + fill(c.cluster) + '"></i>Cluster ' + c.cluster + "</td><td>" + c.size + "</td>" +
  config.inputs.map((i, k) => "<td>" + value(k, c.medians[i.id]) + "</td>").join("")));
const none = data.features.filter(f => f.properties.estimate == null).length;
legend.append("tr").html('<td><i style="background:' + config.noValue + '"></i>Not clustered</td><td>' + none +
  "</td>" + config.inputs.map(() => "<td></td>").join(""));
</script>
</body>
</html>
"""
