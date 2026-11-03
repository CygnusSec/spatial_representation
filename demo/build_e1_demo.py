#!/usr/bin/env python3
"""Build a self-contained HTML page comparing the four E1 shared-boundary scenarios.

Reads stored E1 results and draws them; no experiment is run and no network is used.
Usage: python demo/build_e1_demo.py [--results experiments/results_group]
"""
import argparse
import html
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
WIDTH, HEIGHT = 420, 300
BOUNDARY_X = 105.76
CASES = (
    ("exact_shared_boundary", "exact_shared_boundary",
     "1. Exact shared boundary", "Both polygons use the same coordinates.", 3e-4),
    ("gap_1e-6_degree", "gap_1e-6_degree",
     "2. Gap of 10⁻⁶ degrees", "Converting to TopoJSON creates no shared arc and keeps the gap.", 3e-6),
    ("independent_geojson_edit", "independent_geojson_edit_plus_1e-4_degree",
     "3. Edit A alone in GeoJSON", "A moves; B keeps its own copy of the boundary, so they overlap.", 3e-4),
    ("shared_topojson_edit", "shared_topojson_edit_plus_1e-4_degree",
     "4. Edit the shared arc in TopoJSON", "One arc is edited, so both polygons change together.", 3e-4),
)
STYLE = """
body{font:15px/1.45 system-ui,sans-serif;color:#1d2c35;background:#fff;margin:0 auto;max-width:960px;padding:24px}
h1{font-size:24px;margin:0 0 6px}p{margin:0 0 12px}.note{color:#566570;font-size:13px}
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(400px,1fr));gap:18px;margin-top:18px}
figure{margin:0;border:1px solid #d9dee0;border-radius:6px;padding:12px}
h2{font-size:16px;margin:0 0 2px}svg{display:block;width:100%;height:auto;background:#f6f8f8;margin:8px 0}
dl{display:grid;grid-template-columns:auto 1fr;gap:2px 12px;margin:0;font-size:13px}dt{color:#566570}dd{margin:0;font-variant-numeric:tabular-nums}
.bad{color:#a23f2b;font-weight:600}.good{color:#1f6b69;font-weight:600}
"""


def draw(features, half_width):
    """Draw both polygons around the boundary; x is stretched, y keeps the full 0.01 degrees."""
    y0, y1 = 21.0, 21.01
    x0 = BOUNDARY_X - half_width
    def px(point):
        return (WIDTH * (point[0] - x0) / (2 * half_width), HEIGHT * (y1 - point[1]) / (y1 - y0))
    parts = [f'<svg viewBox="0 0 {WIDTH} {HEIGHT}" role="img" aria-label="Polygons A and B around their boundary">']
    for feature, name, color in zip(features, "AB", ("#2a7977", "#b68a3b")):
        ring = [px(p) for p in feature["geometry"]["coordinates"][0]]
        points = " ".join(f"{x:.2f},{y:.2f}" for x, y in ring)
        parts.append(f'<polygon points="{points}" fill="{color}" fill-opacity=".38" stroke="{color}" stroke-width="2"/>')
        for x, y in ring[:-1]:
            if 0 <= x <= WIDTH:
                parts.append(f'<circle cx="{x:.2f}" cy="{y:.2f}" r="3.5" fill="{color}" stroke="#fff"/>')
    parts.append(f'<text x="{WIDTH * .12:.0f}" y="{HEIGHT * .54:.0f}" font-size="24" font-weight="700" fill="#2a7977">A</text>')
    parts.append(f'<text x="{WIDTH * .84:.0f}" y="{HEIGHT * .54:.0f}" font-size="24" font-weight="700" fill="#8c692b">B</text>')
    parts.append("</svg>")
    return "".join(parts)


def row(term, value, css=""):
    attribute = f' class="{css}"' if css else ""
    return f"<dt>{html.escape(term)}</dt><dd{attribute}>{html.escape(value)}</dd>"


def panel(data_dir, stored, stem, case, title, caption, half_width):
    metrics = stored[case]["decoded_metrics"]
    topology = stored[case].get("topology")
    features = json.loads((data_dir / f"{stem}.geojson").read_text(encoding="utf-8"))["features"]
    overlap = metrics["overlap_area_utm_m2"]
    arcs = f'{topology["shared_arcs"]} of {topology["arcs"]}' if topology else "none (stored separately)"
    rows = [
        row("Shared arcs", arcs),
        row("Touching", "yes" if metrics["touches"] else "no", "good" if metrics["touches"] else "bad"),
        row("Each polygon valid", "yes" if metrics["all_valid"] else "no"),
        row("Gap distance", f'{metrics["distance_utm_m"]:,.6f} m', "bad" if metrics["distance_utm_m"] > 0 else ""),
        row("Overlap area", f"{overlap:,.3f} m²", "bad" if overlap > 0.001 else "good"),
    ]
    return (f"<figure><h2>{html.escape(title)}</h2><p class=note>{html.escape(caption)}</p>"
            f"{draw(features, half_width)}<p class=note>Width shown: {2 * half_width:.0e} degrees.</p>"
            f"<dl>{''.join(rows)}</dl></figure>")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--results", type=Path, default=HERE.parent / "experiments" / "results_group")
    parser.add_argument("--output", type=Path, default=HERE / "e1_compare.html")
    args = parser.parse_args()
    stored = {r["case"]: r for r in json.loads((args.results / "e1_topology.json").read_text(encoding="utf-8"))}
    panels = "".join(panel(args.results / "data" / "e1", stored, *case) for case in CASES)
    page = ("<!DOCTYPE html><html lang=en><head><meta charset=utf-8>"
            "<meta name=viewport content='width=device-width,initial-scale=1'>"
            f"<title>E1 shared-boundary comparison</title><style>{STYLE}</style></head><body>"
            "<h1>E1: shared boundaries, gaps and updates</h1>"
            "<p>Spaghetti storage keeps two copies of a shared boundary; topological storage keeps one arc. "
            "These panels draw the stored E1 files for two adjacent polygons on synthetic data.</p>"
            "<p class=note>Each panel shows the full 0.01-degree height, but its width is stretched around the shared "
            "boundary so that small differences are visible. Horizontal and vertical scales therefore differ, and "
            "panel 2 uses a much narrower width. Distances and areas are computed in UTM 48N (EPSG:32648).</p>"
            f"<div class=grid>{panels}</div></body></html>\n")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(page, encoding="utf-8")
    print(args.output)


if __name__ == "__main__":
    main()
