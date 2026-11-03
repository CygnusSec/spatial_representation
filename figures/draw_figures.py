#!/usr/bin/env python3
"""Draw report Figures 1-5 as PDF. Figures 4 and 5 read a stored result set.

Usage (requires matplotlib and numpy; no benchmark is executed):
    python draw_figures.py --results ../experiments/results_group --output ../experiments/results_group/figures

The TIN sample coordinates and object positions in Figure 1 are illustrative.
"""
import argparse
import csv
from pathlib import Path

import matplotlib

matplotlib.use("pdf")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.tri import Triangulation
from matplotlib.colors import LinearSegmentedColormap, to_rgba
from matplotlib.patches import FancyArrowPatch, Polygon, Rectangle
from matplotlib.ticker import FixedLocator, FuncFormatter, NullFormatter, NullLocator

HERE = Path(__file__).resolve().parent
OUT = HERE
RESULTS = HERE.parent / "experiments" / "results_group"
TEAL, OCHRE, BLUE, PURPLE, RED = "#2a7a78", "#b88a3a", "#4a6f9c", "#76608a", "#b05a45"
INK, GREY, GRID = "#2f3a45", "#6b7680", "#e4e7ea"

plt.rcParams.update({
    "font.family": "DejaVu Sans", "font.size": 9, "axes.edgecolor": "#9aa3ab",
    "axes.linewidth": 0.7, "xtick.color": GREY, "ytick.color": GREY,
    "axes.labelcolor": INK, "axes.titlesize": 10, "axes.titleweight": "bold",
    "pdf.fonttype": 42,
})


def fixed(value, digits=2):
    return f"{value:.{digits}f}"


def thousands(value, _pos=None):
    return f"{int(round(value)):,}"


def titled(ax, title, sub=None):
    ax.set_title(title, pad=16 if sub else 6)
    if sub:
        ax.text(0.5, 1.015, sub, transform=ax.transAxes, ha="center", va="bottom", color=GREY, fontsize=8)


def figure1():
    field = lambda x, y: 10 + 5 * np.sin(x / 3) * np.cos(y / 4)
    cmap = LinearSegmentedColormap.from_list("field", ["#e3dfb8", "#9ebfa8", "#2a7a78"])
    norm = dict(cmap=cmap, vmin=5, vmax=15)
    fig, axes = plt.subplots(2, 2, figsize=(6.6, 6.9))
    (a, b), (c, d) = axes

    xs, ys = np.meshgrid(np.linspace(0, 10, 300), np.linspace(0, 10, 300))
    image = a.pcolormesh(xs, ys, field(xs, ys), shading="auto", rasterized=True, **norm)
    a.contour(xs, ys, field(xs, ys), levels=[7, 9, 11, 13], colors="white", linewidths=0.8)
    for level in (7, 9, 11, 13):
        # Label each contour where it crosses x = 4.7, on the field color of that level.
        label_y = 4 * np.arccos((level - 10) / (5 * np.sin(4.7 / 3)))
        a.text(4.7, label_y, str(level), fontsize=7.5, color=INK, ha="center", va="center",
               bbox=dict(facecolor=cmap((level - 5) / 10), edgecolor="none", pad=0.8))
    titled(a, "(a) Field on a continuous domain", "f(x, y) = 10 + 5 sin(x/3) cos(y/4)")

    edges = np.arange(0, 11)
    cx, cy = np.meshgrid(edges[:-1] + 0.5, edges[:-1] + 0.5)
    b.pcolormesh(edges, edges, field(cx, cy), edgecolors="white", linewidth=0.5, **norm)
    b.scatter(cx, cy, s=1, color=INK)
    titled(b, "(b) Raster 10 × 10", "Sampled at centers; constant within a cell")

    pts = np.array([
        (0, 0), (10, 0), (10, 10), (0, 10), (1.6, 9.6), (4.3, 9.5), (5.3, 9.5), (5.2, 9.2),
        (6.2, 9.5), (7.1, 9.3), (6.6, 8.6), (8.0, 8.6), (8.0, 8.1), (5.9, 7.7), (4.8, 6.3),
        (1.3, 5.4), (4.8, 5.4), (6.5, 5.0), (9.1, 4.9), (6.7, 4.3), (7.8, 3.6), (8.2, 3.2),
        (2.4, 2.6), (2.6, 1.8), (4.0, 2.1), (5.4, 2.1), (1.8, 0.8),
    ])
    tri = Triangulation(pts[:, 0], pts[:, 1]).triangles
    c.tripcolor(pts[:, 0], pts[:, 1], tri, field(pts[:, 0], pts[:, 1]), shading="gouraud", rasterized=True, **norm)
    c.triplot(pts[:, 0], pts[:, 1], tri, color=INK, linewidth=0.55)
    c.scatter(pts[:, 0], pts[:, 1], s=6, color="white", edgecolors=INK, linewidths=0.5, zorder=3)
    titled(c, "(c) TIN from irregular samples", "f values at vertices; linear interpolation")

    for name, verts, color, label in (
        ("R1", [(0.9, 6.0), (3.6, 6.5), (3.9, 9.1), (1.1, 8.8)], TEAL, (2.4, 7.6)),
        ("R2", [(5.6, 5.6), (8.9, 5.2), (9.2, 8.8), (6.0, 9.2)], BLUE, (7.4, 7.3)),
        ("R3", [(1.0, 1.0), (3.8, 1.3), (3.4, 3.8), (0.8, 3.5)], OCHRE, (2.2, 2.4)),
    ):
        d.add_patch(Polygon(verts, facecolor=to_rgba(color, 0.18), edgecolor=color, linewidth=1.1))
        d.text(*label, name, ha="center", va="center", weight="bold", color=INK)
    d.plot([0, 3.8, 5.0, 8.0, 10], [4.6, 4.8, 3.4, 3.1, 1.6], color="#5d6873", linewidth=1.6)
    d.text(6.8, 3.6, "L1", color=INK, ha="center", va="bottom", fontsize=8.5)
    for name, (x, y) in {"P1": (5.1, 1.4), "P2": (8.4, 4.1)}.items():
        d.scatter([x], [y], s=16, color=RED, zorder=3)
        d.text(x + 0.3, y, name, va="center", color=INK, fontsize=8.5)
    d.grid(color=GRID, linewidth=0.5)
    d.set_axisbelow(True)
    titled(d, "(d) Set of identified entities", "Separate example: regions, line, points")

    for ax in axes.flat:
        ax.set(xlim=(0, 10), ylim=(0, 10), aspect="equal", xlabel="x", ylabel="y", xticks=[0, 5, 10], yticks=[0, 5, 10])
    fig.subplots_adjust(left=0.08, right=0.97, top=0.93, bottom=0.17, hspace=0.42, wspace=0.28)
    bar_ax = fig.add_axes([0.24, 0.075, 0.54, 0.018])
    bar = fig.colorbar(image, cax=bar_ax, orientation="horizontal", ticks=[5, 7.5, 10, 12.5, 15])
    bar.ax.set_xticklabels(["5.0", "7.5", "10.0", "12.5", "15.0"])
    bar.set_label("Value of f — shared by panels (a), (b), (c)", fontsize=8, color=GREY)
    fig.savefig(OUT / "figure1_entity_field.pdf", dpi=220)
    plt.close(fig)


def annotate(ax, text, point, at, color):
    ax.annotate(text, point, xytext=at, color=color, fontsize=8, ha="center", va="center",
                arrowprops=dict(arrowstyle="-", color=color, linewidth=0.7, shrinkB=2))


def figure2():
    fig, (a, b) = plt.subplots(1, 2, figsize=(6.6, 3.5))
    a.add_patch(Polygon([(0, 0), (2, 0), (0, 2)], facecolor=to_rgba(TEAL, 0.17), edgecolor=TEAL, linewidth=1.4))
    a.text(1.52, 0.76, "x + y = 2", rotation=-45, color=GREY, fontsize=7.5, ha="center", va="center")
    for point, color in (((0.5, 0.5), BLUE), ((1, 1), OCHRE), ((1.5, 1), RED)):
        a.scatter(*point, s=18, color=color, zorder=3)
    annotate(a, "P (0.5, 0.5)\ninside", (0.5, 0.5), (0.55, -0.27), BLUE)
    annotate(a, "Q (1, 1)\non boundary", (1, 1), (0.42, 2.2), OCHRE)
    annotate(a, "R (1.5, 1)\noutside", (1.5, 1), (1.5, 1.72), RED)
    titled(a, "(a) Intersection of half-planes", "x ≥ 0; y ≥ 0; x + y ≤ 2")
    a.text(0.5, -0.27, "P: INSIDE; Q: BOUNDARY; R: OUTSIDE\nIllustrative classification with ε = 0.",
           transform=a.transAxes, ha="center", va="top", color=GREY, fontsize=7.5)

    b.add_patch(Rectangle((0, 0), 2, 1, facecolor=TEAL, alpha=0.17, linewidth=0))
    b.add_patch(Rectangle((0, 1), 1, 1, facecolor=BLUE, alpha=0.17, linewidth=0))
    b.plot([0, 2, 2, 1, 1, 0, 0], [0, 0, 1, 1, 2, 2, 0], color=TEAL, linewidth=1.4)
    b.plot([0, 1], [1, 1], color=OCHRE, linewidth=1.3, linestyle="--")
    b.text(1.6, 0.3, "C₁", color=TEAL, fontsize=10)
    b.text(0.05, 1.8, "C₂", color=BLUE, fontsize=10)
    b.scatter(0.5, 1, s=18, color=PURPLE, zorder=3)
    b.scatter(1.5, 1.5, s=18, color=RED, zorder=3)
    annotate(b, "S (0.5, 1)\nin the union", (0.5, 1), (0.5, 1.45), PURPLE)
    annotate(b, "T (1.5, 1.5)\noutside", (1.5, 1.5), (1.55, 2.05), RED)
    titled(b, "(b) Union of two convex pieces", "[0, 2] × [0, 1] ∪ [0, 1] × [1, 2]")
    b.text(0.5, -0.27, "The dashed line separates the two pieces.\nS is not on the outer boundary of the union.",
           transform=b.transAxes, ha="center", va="top", color=GREY, fontsize=7.5)

    for ax in (a, b):
        ax.set(xlim=(-0.3, 2.4), ylim=(-0.5, 2.5), aspect="equal", xlabel="x", ylabel="y", xticks=[0, 1, 2], yticks=[0, 1, 2])
        ax.grid(color=GRID, linewidth=0.5)
        ax.set_axisbelow(True)
    fig.subplots_adjust(left=0.08, right=0.98, top=0.86, bottom=0.25, wspace=0.25)
    fig.savefig(OUT / "figure2_half_planes.pdf")
    plt.close(fig)


def figure3():
    fig, axes = plt.subplots(1, 3, figsize=(6.6, 3.15))
    a, b, c = axes
    for ax in axes:
        ax.set(xlim=(-0.2, 2.45), ylim=(-1.05, 1.45), aspect="equal")
        ax.axis("off")
    titles = (
        (a, "(a) Spaghetti", "Separate geometry for A and B\n2 copies of the shared edge", "8 stored segments",
         "Shared edge drawn offset to show both\ncopies; both have x = 1."),
        (b, "(b) Network", "Nodes and edges; no faces assigned\n", "V = 6; E = 7",
         "Nodes record edge connectivity;\nleft and right faces are not stored."),
        (c, "(c) Topology", "One edge, two incident faces\n", "V = 6; E = 7; F = 3",
         "F counts A, B and the outer face.\nEdge e runs from (1, 0) to (1, 1)."),
    )
    for ax, title, sub, summary, note in titles:
        ax.set_title(title, pad=24)
        ax.text(0.5, 1.0, sub, transform=ax.transAxes, ha="center", va="bottom", color=GREY, fontsize=7.2)
        ax.text(1, -0.42, summary, ha="center", va="center", weight="bold", color=INK, fontsize=8.5)
        ax.text(1, -0.8, note, ha="center", va="center", color=GREY, fontsize=6.5)

    a.add_patch(Rectangle((0, 0), 0.98, 1, facecolor=to_rgba(TEAL, 0.13), edgecolor=TEAL, linewidth=1.2))
    a.add_patch(Rectangle((1.02, 0), 0.98, 1, facecolor=to_rgba(BLUE, 0.13), edgecolor=BLUE, linewidth=1.2))
    a.text(0.49, 0.5, "A", ha="center", va="center", weight="bold", color=TEAL, fontsize=12)
    a.text(1.51, 0.5, "B", ha="center", va="center", weight="bold", color=BLUE, fontsize=12)

    xs, ys = [0, 2, 2, 0, 0], [0, 0, 1, 1, 0]
    for ax in (b, c):
        ax.plot(xs, ys, color=INK, linewidth=1.2)
        ax.plot([1, 1], [0, 1], color=INK, linewidth=1.2, zorder=1)
    nodes = {"v1": (0, 0), "v2": (1, 0), "v3": (2, 0), "v4": (0, 1), "v5": (1, 1), "v6": (2, 1)}
    for name, (x, y) in nodes.items():
        b.scatter(x, y, s=12, color=OCHRE, zorder=3)
        b.text(x, y + (0.13 if y else -0.13), name, ha="center", va="center", color=INK, fontsize=7)
        c.scatter(x, y, s=5, color=INK, zorder=3)
    c.add_patch(Rectangle((0, 0), 1, 1, facecolor=TEAL, alpha=0.13, linewidth=0))
    c.add_patch(Rectangle((1, 0), 1, 1, facecolor=BLUE, alpha=0.13, linewidth=0))
    c.plot([1, 1], [0, 1], color=TEAL, linewidth=1.5, zorder=2)
    c.add_patch(FancyArrowPatch((1, 0.3), (1, 0.72), arrowstyle="-|>", mutation_scale=13, color=TEAL, linewidth=0, zorder=4))
    c.text(1.1, 0.55, "e", color=TEAL, style="italic", fontsize=8)
    c.text(0.5, 0.45, "A", ha="center", va="center", weight="bold", color=TEAL, fontsize=12)
    c.text(1.5, 0.45, "B", ha="center", va="center", weight="bold", color=BLUE, fontsize=12)
    c.text(0.5, 1.13, "left: A", ha="center", color=INK, fontsize=7)
    c.text(1.5, 1.13, "right: B", ha="center", color=INK, fontsize=7)
    c.text(2.12, 1.0, "∞", ha="left", va="center", color=GREY, fontsize=9)
    fig.text(0.5, 0.025, "Connected planar partition: V − E + F = 6 − 7 + 3 = 2", ha="center", color=INK, fontsize=8)
    fig.subplots_adjust(left=0.01, right=0.99, top=0.84, bottom=0.05, wspace=0.05)
    fig.savefig(OUT / "figure3_collections.pdf")
    plt.close(fig)


def read_rows(name):
    with (RESULTS / name).open(encoding="utf-8", newline="") as stream:
        return list(csv.DictReader(stream))


def clean(ax, axis="y"):
    ax.spines[["top", "right"]].set_visible(False)
    ax.grid(axis=axis, color=GRID, linewidth=0.5)
    ax.set_axisbelow(True)


def figure4():
    names = ["GeoJSON", "TopoJSON", "KML", "GeoParquet\nNONE", "GeoParquet\nZSTD"]
    profiles = ["GeoJSON", "TopoJSON", "KML", "GeoParquet-NONE", "GeoParquet-ZSTD"]
    rows = read_rows("e2_summary.csv")
    largest = {r["profile"]: r for r in rows if int(r["n"]) == 10000}
    raw = np.array([int(largest[p]["raw_bytes"]) for p in profiles]) / 2**20
    gzip = np.array([int(largest[p]["gzip6_bytes"]) for p in profiles]) / 2**20
    fig, (a, b) = plt.subplots(1, 2, figsize=(6.6, 3.9), gridspec_kw={"width_ratios": [1.05, 1]})
    y = np.arange(5)
    a.barh(y - 0.17, raw, 0.34, color=TEAL, label="Raw file")
    a.barh(y + 0.17, gzip, 0.34, color=OCHRE, label="After gzip6")
    for pos, value in zip(y, raw):
        a.text(value + 0.08, pos - 0.17, fixed(value), va="center", fontsize=8, color=INK)
    a.set(yticks=y, yticklabels=names, xlabel="Size (MiB)", xlim=(0, 7.3))
    a.invert_yaxis()
    a.set_title("(a) Size • N = 10,000\nRaw file and external gzip6", fontsize=9)
    clean(a, "x")
    a.legend(frameon=False, loc="upper center", bbox_to_anchor=(0.45, -0.17), ncol=2, fontsize=8)

    sizes = [100, 1000, 10000]
    styles = (("GeoJSON", BLUE, "o", "-"), ("TopoJSON", TEAL, "s", "-"), ("KML", OCHRE, "^", "-"),
              ("GeoParquet-NONE", PURPLE, "D", "-"), ("GeoParquet-ZSTD", RED, "v", "--"))
    for profile, color, marker, style in styles:
        subset = {int(r["n"]): r for r in rows if r["profile"] == profile}
        medians = np.array([float(subset[n]["read_median_ms"]) for n in sizes])
        q1 = np.array([float(subset[n]["read_q1_ms"]) for n in sizes])
        q3 = np.array([float(subset[n]["read_q3_ms"]) for n in sizes])
        b.errorbar(sizes, medians, yerr=[medians - q1, q3 - medians], color=color, marker=marker, markersize=4,
                   linestyle=style, linewidth=1.2, elinewidth=0.9, capsize=3, label=profile.replace("-", " "))
    b.set(xscale="log", yscale="log", xlabel="Number of polygons N (log scale)", ylabel="Read time (ms; log scale)", ylim=(1.7, 800))
    b.xaxis.set_major_locator(FixedLocator(sizes))
    b.xaxis.set_major_formatter(FuncFormatter(thousands))
    b.xaxis.set_minor_locator(NullLocator())
    b.yaxis.set_major_locator(FixedLocator([2, 5, 10, 20, 50, 100, 200, 500]))
    b.yaxis.set_major_formatter(FuncFormatter(lambda v, _p: f"{v:g}"))
    b.yaxis.set_minor_formatter(NullFormatter())
    b.set_title("(b) Read to Shapely geometry\nMedian and Q1–Q3 range", fontsize=9)
    clean(b, "both")
    b.legend(frameon=False, loc="upper center", bbox_to_anchor=(0.45, -0.17), ncol=2, fontsize=7.5)
    fig.text(0.5, 0.015, "GeoParquet ZSTD is already compressed internally; gzip6 measures an extra outer layer.\n"
             "5 repetitions after warm-up, warm cache; the read result includes id, class and geometry.",
             ha="center", color=GREY, fontsize=6.8)
    fig.subplots_adjust(left=0.15, right=0.97, top=0.87, bottom=0.34, wspace=0.36)
    fig.savefig(OUT / "figure4_e2_size_read.pdf")
    plt.close(fig)


def figure5():
    zooms = ["11", "13", "15"]
    x = np.arange(3)
    rows = sorted(read_rows("e3_summary.csv"), key=lambda r: int(r["zoom"]))
    assert [r["zoom"] for r in rows] == zooms
    whole = np.array([int(r["gzip6_bytes_all"]) for r in rows]) / 1024
    view = np.array([int(r["gzip6_bytes_view"]) for r in rows]) / 1024
    hausdorff = [float(r["max_hausdorff_mercator_m"]) for r in rows]
    area_pct = [100 * float(r["relative_symmetric_difference_area"]) for r in rows]
    fig, (a, b, c) = plt.subplots(1, 3, figsize=(6.6, 3.5))
    bars_whole = a.bar(x - 0.19, whole, 0.38, color=TEAL, label="Full domain")
    bars_view = a.bar(x + 0.19, view, 0.38, color=OCHRE, label="Tiles intersecting viewport")
    a.bar_label(bars_whole, fmt="%.0f", fontsize=7.5, padding=1)
    a.bar_label(bars_view, fmt="%.0f", fontsize=7.5, padding=1)
    a.set(xticks=x, xticklabels=zooms, xlabel="Zoom level", ylabel="Size (KiB)", ylim=(0, 350))
    a.set_title("(a) Tile size\nAfter gzip6", fontsize=9)
    clean(a)
    a.legend(frameon=False, loc="upper left", bbox_to_anchor=(-0.2, -0.17), ncol=2, fontsize=7.5)

    for ax, values, color, marker, label, digits, title, top in (
        (b, hausdorff, BLUE, "o", "Distance (m, Mercator)", 2, "(b) Discrete Hausdorff\nMaximum", 4),
        (c, area_pct, PURPLE, "s", "Relative area difference (%)", 3, "(c) Area difference\nPer feature (%)", 3.3),
    ):
        ax.plot(x, values, color=color, marker=marker, markersize=4.5, linewidth=1.3)
        for pos, value in zip(x, values):
            ax.annotate(fixed(value, digits), (pos, value), xytext=(6, 6), textcoords="offset points", fontsize=7.5, color=INK)
        ax.set(xticks=x, xticklabels=zooms, xlabel="Zoom level", ylabel=label, ylim=(0, top), xlim=(-0.25, 2.75))
        ax.set_title(title, fontsize=9)
        ax.yaxis.label.set_size(8)
        clean(ax)
    fig.text(0.5, 0.02, "N = 10,000; XYZ Web Mercator, extent 4,096, buffer 0; viewport = 1/16 of the domain area.\n"
             "Discrete Hausdorff without densification; distance in the Mercator plane.\n"
             "Symmetric difference area summed per feature, divided by the total source area.",
             ha="center", va="bottom", color=GREY, fontsize=6.8)
    fig.subplots_adjust(left=0.09, right=0.98, top=0.87, bottom=0.34, wspace=0.42)
    fig.savefig(OUT / "figure5_e3_mvt.pdf")
    plt.close(fig)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--results", type=Path, default=RESULTS)
    parser.add_argument("--output", type=Path, default=RESULTS / "figures")
    args = parser.parse_args()
    RESULTS, OUT = args.results, args.output
    OUT.mkdir(parents=True, exist_ok=True)
    figure1()
    figure2()
    figure3()
    figure4()
    figure5()
