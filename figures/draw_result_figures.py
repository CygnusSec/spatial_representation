#!/usr/bin/env python3
"""Draw the report's measured-result figures from the experiment CSV files.

Usage:
    python draw_result_figures.py
    python draw_result_figures.py --results ../experiments/results --output .

Requires Matplotlib (created with 3.10.8) and NumPy. No benchmark is executed.
PNG files have an exact width of 9 inches at 300 dpi; SVG files retain vectors.
Source data and metric definitions remain in experiments/results and README.md.
"""

from __future__ import annotations

import argparse
import csv
import os
import tempfile
from pathlib import Path

os.environ.setdefault("MPLCONFIGDIR", str(Path(tempfile.gettempdir()) / "spatial_report_mpl"))
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import FixedLocator, FuncFormatter, NullFormatter, NullLocator
import numpy as np


HERE = Path(__file__).resolve().parent
INK = "#1D2C35"
GRAY = "#65727B"
GRID = "#E3E8E9"
TEAL = "#2A7977"
BLUE = "#476F9B"
OCHRE = "#B68A3B"
RED = "#AB5C4B"
PURPLE = "#786589"
PROFILES = ["GeoJSON", "TopoJSON", "KML", "GeoParquet-NONE", "GeoParquet-ZSTD"]
COLORS = [BLUE, TEAL, OCHRE, PURPLE, RED]
MARKERS = ["o", "s", "^", "D", "v"]
LABELS = ["GeoJSON", "TopoJSON", "KML", "GeoParquet NONE", "GeoParquet ZSTD"]


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as stream:
        return list(csv.DictReader(stream))


def style() -> None:
    plt.rcParams.update({
        "font.family": "DejaVu Sans",
        "font.size": 11.5,
        "axes.titlesize": 12,
        "axes.titleweight": "bold",
        "axes.titlecolor": "black",
        "axes.labelsize": 11.5,
        "axes.labelcolor": INK,
        "text.color": INK,
        "xtick.color": GRAY,
        "ytick.color": GRAY,
        "xtick.labelsize": 11.2,
        "ytick.labelsize": 11.2,
        "axes.edgecolor": "#A6B0B5",
        "axes.linewidth": 0.75,
        "svg.fonttype": "path",
        "savefig.facecolor": "white",
        "figure.facecolor": "white",
    })


def tidy_axis(ax, *, grid_axis: str = "y") -> None:
    ax.spines[["top", "right"]].set_visible(False)
    ax.set_axisbelow(True)
    ax.grid(axis=grid_axis, which="major", color=GRID, linewidth=0.8)
    ax.tick_params(length=3.5, width=0.7)


def save(fig, output: Path, stem: str) -> None:
    # Deliberately do not use bbox_inches="tight": keep the requested 9-inch width.
    output.mkdir(parents=True, exist_ok=True)
    fig.savefig(output / f"{stem}.png", dpi=300)
    fig.savefig(output / f"{stem}.svg", metadata={
        "Creator": "draw_result_figures.py; measured experiment CSV files",
        "Description": "Original scientific figure for the spatial-representation report",
    })
    plt.close(fig)


def fmt_decimal(value: float, decimals: int = 2) -> str:
    return f"{value:.{decimals}f}"


def figure_e2(rows: list[dict[str, str]], output: Path) -> None:
    fig, (a, b) = plt.subplots(
        1, 2, figsize=(9, 6.05), gridspec_kw={"width_ratios": [1.0, 1.08]}
    )
    fig.subplots_adjust(left=0.155, right=0.98, bottom=0.335, top=0.86, wspace=0.56)

    # (a) Byte measurements at a fixed feature count. "File" is not synonymous
    # with "uncompressed": the ZSTD profile already has Parquet compression.
    at_n = {r["profile"]: r for r in rows if int(r["n"]) == 10000}
    assert set(at_n) == set(PROFILES), "Expected all five measured N=10,000 profiles"
    raw = np.array([int(at_n[p]["raw_bytes"]) for p in PROFILES]) / (1024 ** 2)
    gz = np.array([int(at_n[p]["gzip6_bytes"]) for p in PROFILES]) / (1024 ** 2)
    y = np.arange(len(PROFILES))
    bar_h = 0.32
    a.barh(y - bar_h / 2, raw, height=bar_h, color=TEAL, label="Raw file", zorder=3)
    a.barh(y + bar_h / 2, gz, height=bar_h, color=OCHRE, label="After gzip6", zorder=3)
    a.set_yticks(y, ["GeoJSON", "TopoJSON", "KML", "GeoParquet\nNONE", "GeoParquet\nZSTD"])
    a.invert_yaxis()
    a.set_xlim(0, 6.8)
    a.set_xticks([0, 2, 4, 6])
    a.set_xlabel("Size (MiB)", labelpad=9)
    a.set_title("(a) Size • N = 10,000\nRaw file and external gzip6", pad=18)
    a.tick_params(axis="y", length=0, pad=8)
    tidy_axis(a, grid_axis="x")
    # Label the raw file bars; exact gzip byte counts are in the adjacent report
    # table/CSV, avoiding dense labels on very short bars.
    for yi, value in zip(y, raw):
        a.text(value + 0.10, yi - bar_h / 2, fmt_decimal(value), va="center", ha="left", fontsize=11.2)
    a.legend(loc="upper left", bbox_to_anchor=(-0.03, -0.20), ncol=2,
             frameon=False, fontsize=11.2, handlelength=1.25,
             handletextpad=0.45, columnspacing=1.0, borderaxespad=0)

    # (b) Median plus interquartile range (five measured repetitions); the end
    # state is a list of equal id/class attributes and Shapely geometries.
    for profile, label, color, marker in zip(PROFILES, LABELS, COLORS, MARKERS):
        subset = sorted((r for r in rows if r["profile"] == profile), key=lambda r: int(r["n"]))
        ns = np.array([int(r["n"]) for r in subset])
        med = np.array([float(r["read_median_ms"]) for r in subset])
        q1 = np.array([float(r["read_q1_ms"]) for r in subset])
        q3 = np.array([float(r["read_q3_ms"]) for r in subset])
        assert np.all(q1 <= med) and np.all(med <= q3)
        b.errorbar(ns, med, yerr=np.vstack([med - q1, q3 - med]), label=label,
                   color=color, marker=marker, markersize=5.3, linewidth=1.6,
                   capsize=3.2, capthick=1.1, elinewidth=1.15,
                   linestyle="--" if profile == "GeoParquet-ZSTD" else "-",
                   zorder=4)
    b.set_xscale("log")
    b.set_yscale("log")
    b.set_xlim(78, 13000)
    b.set_ylim(1.6, 850)
    b.xaxis.set_major_locator(FixedLocator([100, 1000, 10000]))
    b.xaxis.set_major_formatter(FuncFormatter(lambda value, _: f"{int(value):,}"))
    b.yaxis.set_major_locator(FixedLocator([2, 5, 10, 20, 50, 100, 200, 500]))
    b.yaxis.set_major_formatter(FuncFormatter(lambda value, _: str(int(value))))
    b.xaxis.set_minor_locator(NullLocator())
    b.yaxis.set_minor_formatter(NullFormatter())
    b.yaxis.set_minor_locator(NullLocator())
    b.set_xlabel("Number of polygons N (log scale)", labelpad=9)
    b.set_ylabel("Read time (ms; log scale)", labelpad=7)
    b.set_title("(b) Read to Shapely geometry\nMedian and Q1–Q3 range", pad=18)
    tidy_axis(b, grid_axis="both")
    b.legend(loc="upper left", bbox_to_anchor=(-0.20, -0.20), ncol=2,
             frameon=False, fontsize=11.2, handlelength=1.65,
             handletextpad=0.4, columnspacing=0.8, labelspacing=0.65,
             borderaxespad=0)

    fig.text(0.035, 0.073,
             "GeoParquet ZSTD is already compressed internally; gzip6 measures an extra outer layer.",
             ha="left", va="bottom", fontsize=11.2, color=GRAY)
    fig.text(0.035, 0.027,
             "5 repetitions after warm-up, warm cache; the read result includes id, class and geometry.",
             ha="left", va="bottom", fontsize=11.2, color=GRAY)
    save(fig, output, "fig04_results_e2")


def figure_mvt(rows: list[dict[str, str]], output: Path) -> None:
    rows = sorted(rows, key=lambda r: int(r["zoom"]))
    zooms = np.array([int(r["zoom"]) for r in rows])
    assert list(zooms) == [11, 13, 15]
    assert all(int(r["n_source_features"]) == 10000 for r in rows)
    assert all(r["all_source_ids_present"] == "True" for r in rows)

    fig, axes = plt.subplots(1, 3, figsize=(9, 6.05),
                              gridspec_kw={"width_ratios": [1.10, 1.0, 1.0]})
    fig.subplots_adjust(left=0.085, right=0.98, bottom=0.34, top=0.86, wspace=0.64)
    a, b, c = axes

    # (a) Actual gzip6 byte sizes of encoded tile payloads, not HTTP traffic.
    locs = np.arange(len(zooms))
    all_kib = np.array([int(r["gzip6_bytes_all"]) for r in rows]) / 1024
    view_kib = np.array([int(r["gzip6_bytes_view"]) for r in rows]) / 1024
    bars_all = a.bar(locs - 0.18, all_kib, width=0.34, color=TEAL, label="Full domain", zorder=3)
    bars_view = a.bar(locs + 0.18, view_kib, width=0.34, color=OCHRE, label="Tiles intersecting viewport", zorder=3)
    a.set_xticks(locs, zooms)
    a.set_xlim(-0.65, 2.65)
    a.set_ylim(0, 350)
    a.set_yticks([0, 100, 200, 300])
    a.set_ylabel("Size (KiB)", labelpad=6)
    a.set_title("(a) Tile size\nAfter gzip6", pad=18)
    for bars, x_offset in ((bars_all, -4), (bars_view, 4)):
        for rect in bars:
            a.annotate(f"{rect.get_height():.0f}",
                       (rect.get_x() + rect.get_width() / 2, rect.get_height() + 6),
                       xytext=(x_offset, 0), textcoords="offset points",
                       ha="center", va="bottom", fontsize=11.2)

    # (b) Maximum, over source-feature IDs, of GEOS discrete Hausdorff distance.
    hausdorff = np.array([float(r["max_hausdorff_mercator_m"]) for r in rows])
    b.plot(zooms, hausdorff, color=BLUE, marker="o", markersize=6, linewidth=1.8, zorder=4)
    b.set_title("(b) Discrete Hausdorff\nMaximum", pad=18)
    b.set_ylabel("Distance (m, Mercator)", labelpad=5)
    b.set_xlim(10.45, 15.55)
    b.set_ylim(0, 4.05)
    b.set_yticks([0, 1, 2, 3, 4])
    b.set_xticks(zooms)
    for z, value in zip(zooms, hausdorff):
        b.annotate(fmt_decimal(value), (z, value), xytext=(0, 9), textcoords="offset points",
                   ha="center", va="bottom", fontsize=11.2)

    # (c) Sum of per-feature symmetric differences / total source feature area.
    # This is intentionally NOT the symmetric difference of whole-coverage unions.
    area_pct = np.array([float(r["relative_symmetric_difference_area"]) for r in rows]) * 100
    c.plot(zooms, area_pct, color=PURPLE, marker="s", markersize=6, linewidth=1.8, zorder=4)
    c.set_title("(c) Area difference\nPer feature (%)", pad=18)
    c.set_ylabel("Relative area difference (%)", labelpad=5)
    c.set_xlim(10.45, 15.55)
    c.set_ylim(0, 3.3)
    c.set_yticks([0, 1, 2, 3])
    c.set_xticks(zooms)
    for z, value in zip(zooms, area_pct):
        c.annotate(fmt_decimal(value, 3), (z, value), xytext=(0, 9), textcoords="offset points",
                   ha="center", va="bottom", fontsize=11.2)

    for ax in axes:
        tidy_axis(ax)
        ax.set_xlabel("Zoom level", labelpad=8)

    fig.legend(handles=[bars_all, bars_view], labels=["Full domain", "Tiles intersecting viewport"],
               loc="upper left", bbox_to_anchor=(0.07, 0.245), ncol=2,
               frameon=False, fontsize=11.2, columnspacing=1.7,
               handlelength=1.5, handletextpad=0.5)
    fig.text(0.035, 0.161,
             "N = 10,000; XYZ Web Mercator, extent 4,096, buffer 0; viewport = 1/16 of the domain area.",
             ha="left", va="bottom", fontsize=11.2, color=GRAY)
    fig.text(0.035, 0.108,
             "Discrete Hausdorff without densification; distance in the Mercator plane.",
             ha="left", va="bottom", fontsize=11.2, color=GRAY)
    fig.text(0.035, 0.055,
             "Symmetric difference area summed per feature, divided by the total source area.",
             ha="left", va="bottom", fontsize=11.2, color=GRAY)
    save(fig, output, "fig05_results_mvt")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--results", type=Path, default=HERE.parent / "experiments" / "results")
    parser.add_argument("--output", type=Path, default=HERE)
    args = parser.parse_args()
    style()
    figure_e2(read_csv(args.results / "e2_summary.csv"), args.output)
    figure_mvt(read_csv(args.results / "e3_summary.csv"), args.output)
    print(f"Created fig04_results_e2 and fig05_results_mvt (PNG + SVG) in {args.output}")


if __name__ == "__main__":
    main()
