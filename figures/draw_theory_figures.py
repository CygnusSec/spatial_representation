#!/usr/bin/env python3
"""Draw the report's original, deterministic mathematical illustrations.

Run with Python containing NumPy and Matplotlib. No external image assets are used.
All coordinates and examples were constructed for this report.
"""

from pathlib import Path
import os
import tempfile

os.environ.setdefault("MPLCONFIGDIR", str(Path(tempfile.gettempdir()) / "spatial_report_mpl"))
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.tri as mtri
from matplotlib.colors import LinearSegmentedColormap, Normalize
from matplotlib.patches import Polygon, Rectangle
from matplotlib.transforms import ScaledTranslation
import numpy as np


HERE = Path(__file__).resolve().parent
TEAL = "#2A7977"
BLUE = "#476F9B"
OCHRE = "#B68A3B"
RED = "#AB5C4B"
INK = "#1D2C35"
GRAY = "#65727B"
LIGHT = "#E3E8E9"
PURPLE = "#786589"
FIELD = LinearSegmentedColormap.from_list("muted_field", ["#E6E2C4", "#91B7AA", "#287573"])

plt.rcParams.update({
    "font.family": "DejaVu Sans",
    "font.size": 11,
    "axes.titlesize": 12,
    "axes.titleweight": "bold",
    "axes.titlecolor": "black",
    "axes.labelcolor": INK,
    "text.color": INK,
    "xtick.color": GRAY,
    "ytick.color": GRAY,
    "xtick.labelsize": 10,
    "ytick.labelsize": 10,
    "axes.edgecolor": "#A6B0B5",
    "axes.linewidth": .7,
    "svg.fonttype": "path",
    "savefig.facecolor": "white",
})


def save(fig, stem):
    fig.savefig(HERE / f"{stem}.png", dpi=300)
    fig.savefig(HERE / f"{stem}.svg")
    plt.close(fig)


def f(x, y):
    return 10 + 5 * np.sin(x / 3) * np.cos(y / 4)


def domain_axes(ax):
    ax.set(xlim=(0, 10), ylim=(0, 10), aspect="equal")
    ax.set_xticks([0, 5, 10])
    ax.set_yticks([0, 5, 10])
    ax.set_xlabel("x", labelpad=1)
    ax.set_ylabel("y", rotation=0, labelpad=8)


def panel_title(ax, title, subtitle):
    ax.set_title(title, pad=27)
    ax.text(.5, 1.025, subtitle, transform=ax.transAxes, ha="center", va="bottom",
            fontsize=10.5, color=GRAY)


def draw_models():
    fig, axes = plt.subplots(2, 2, figsize=(9, 8.4))
    fig.subplots_adjust(left=.08, right=.95, top=.91, bottom=.16, hspace=.53, wspace=.30)
    norm = Normalize(vmin=5, vmax=15)

    # (a) A dense rendering of the analytic field, not a claim of infinite sampling.
    x = np.linspace(0, 10, 451)
    xx, yy = np.meshgrid(x, x)
    image = axes[0, 0].imshow(f(xx, yy), origin="lower", extent=(0, 10, 0, 10),
                            interpolation="bilinear", cmap=FIELD, norm=norm)
    contour = axes[0, 0].contour(xx, yy, f(xx, yy), levels=[7, 9, 11, 13],
                                 colors="white", linewidths=.65, alpha=.8)
    axes[0, 0].clabel(contour, fmt="%g", fontsize=9, colors=INK,
                      manual=[(4.2, 9.4), (4.2, 7.1), (4.2, 5.4), (4.2, 3.7)])
    panel_title(axes[0, 0], "(a) Field on a continuous domain", "f(x, y) = 10 + 5 sin(x/3) cos(y/4)")

    # (b) Exactly 10 x 10 cells; each cell stores the value at its center.
    edges = np.arange(11, dtype=float)
    centers = edges[:-1] + .5
    cx, cy = np.meshgrid(centers, centers)
    axes[0, 1].pcolormesh(edges, edges, f(cx, cy), cmap=FIELD, norm=norm,
                          shading="flat", edgecolors="#F8FAF9", linewidth=.45)
    axes[0, 1].scatter(cx, cy, s=2, c=INK, alpha=.38, linewidths=0)
    panel_title(axes[0, 1], "(b) Raster 10 × 10", "Sampled at centers; constant within a cell")

    # (c) Deterministic irregular samples, including the four domain corners.
    rng = np.random.default_rng(20261102)
    samples = np.vstack(([[0, 0], [10, 0], [10, 10], [0, 10]],
                         rng.uniform(.35, 9.65, size=(23, 2))))
    tri = mtri.Triangulation(samples[:, 0], samples[:, 1])
    interpolator = mtri.LinearTriInterpolator(tri, f(samples[:, 0], samples[:, 1]))
    axes[1, 0].imshow(interpolator(xx, yy), origin="lower", extent=(0, 10, 0, 10),
                      interpolation="bilinear", cmap=FIELD, norm=norm)
    axes[1, 0].triplot(tri, color=INK, linewidth=.65, alpha=.75)
    axes[1, 0].scatter(samples[:, 0], samples[:, 1], s=13, c=INK,
                       edgecolors="white", linewidths=.35, zorder=4)
    panel_title(axes[1, 0], "(c) TIN from irregular samples", "f values at vertices; linear interpolation")

    # (d) A different illustrative phenomenon: individual identified entities.
    regions = [
        ([(.8, 6.1), (4.1, 6.6), (3.7, 9.1), (1.0, 8.8)], TEAL, "R1", (2.4, 7.65)),
        ([(5.2, 5.7), (8.9, 5.2), (9.3, 8.7), (6.0, 9.0)], BLUE, "R2", (7.4, 7.1)),
        ([(1.1, .9), (4.4, 1.2), (3.3, 3.8), (.8, 3.5)], OCHRE, "R3", (2.5, 2.35)),
    ]
    for points, color, label, xy in regions:
        axes[1, 1].add_patch(Polygon(points, closed=True, facecolor=color, alpha=.18,
                                     edgecolor=color, linewidth=1.8))
        axes[1, 1].text(*xy, label, color=INK, weight="bold", ha="center", va="center")
    route = np.array([[0, 4.6], [3.9, 4.8], [5.2, 3.4], [8.0, 3.1], [10, 1.6]])
    axes[1, 1].plot(route[:, 0], route[:, 1], color=GRAY, linewidth=2)
    axes[1, 1].text(6.6, 3.65, "L1", fontsize=11, color=INK)
    axes[1, 1].scatter([5.1, 8.5], [1.4, 4.15], s=34, c=RED, edgecolors="white", linewidths=.6)
    axes[1, 1].text(5.45, 1.35, "P1", fontsize=11, va="center")
    axes[1, 1].text(8.85, 4.15, "P2", fontsize=11, va="center")
    panel_title(axes[1, 1], "(d) Set of identified entities", "Separate example: regions, line, points")

    for ax in axes.flat:
        domain_axes(ax)
    cax = fig.add_axes([.25, .065, .5, .017])
    cbar = fig.colorbar(image, cax=cax, orientation="horizontal", ticks=[5, 7.5, 10, 12.5, 15])
    cbar.set_label("Value of f — shared by panels (a), (b), (c)", fontsize=11, labelpad=5)
    save(fig, "fig01_models")


def square_axes(ax):
    ax.set_xlim(-.22, 2.22)
    ax.set_ylim(-.22, 1.40)
    ax.set_aspect("equal")
    ax.axis("off")


def draw_base_edges(ax, color=INK, linewidth=1.5, shared=True):
    segments = [((0, 0), (1, 0)), ((1, 0), (2, 0)),
                ((0, 1), (1, 1)), ((1, 1), (2, 1)),
                ((0, 0), (0, 1)), ((2, 0), (2, 1))]
    if shared:
        segments.append(((1, 0), (1, 1)))
    for a, b in segments:
        ax.plot([a[0], b[0]], [a[1], b[1]], color=color, lw=linewidth, zorder=2)


def draw_faces(ax):
    ax.add_patch(Rectangle((0, 0), 1, 1, color=TEAL, alpha=.11, zorder=0))
    ax.add_patch(Rectangle((1, 0), 1, 1, color=BLUE, alpha=.11, zorder=0))
    ax.text(.45, .48, "A", fontsize=18, color=TEAL, ha="center", va="center", weight="bold")
    ax.text(1.55, .48, "B", fontsize=18, color=BLUE, ha="center", va="center", weight="bold")


def draw_topology():
    fig, axes = plt.subplots(1, 3, figsize=(9, 4.6))
    fig.subplots_adjust(left=.035, right=.985, bottom=.28, top=.84, wspace=.17)
    titles = [("(a) Spaghetti", "Separate geometry for A and B"),
              ("(b) Network", "Nodes and edges; no faces assigned"),
              ("(c) Topology", "One edge, two incident faces")]
    for ax, (title, subtitle) in zip(axes, titles):
        square_axes(ax)
        panel_title(ax, title, subtitle)

    draw_faces(axes[0])
    # Both stored edges are x=1. Their display transforms separate the strokes.
    for xvals, yvals, color in [([0, 1], [0, 0], TEAL), ([0, 1], [1, 1], TEAL),
                                ([0, 0], [0, 1], TEAL), ([1, 2], [0, 0], BLUE),
                                ([1, 2], [1, 1], BLUE), ([2, 2], [0, 1], BLUE)]:
        axes[0].plot(xvals, yvals, color=color, lw=1.8)
    for shift, color in [(-1.6, TEAL), (1.6, BLUE)]:
        transform = axes[0].transData + ScaledTranslation(shift / 72, 0, fig.dpi_scale_trans)
        axes[0].plot([1, 1], [0, 1], color=color, lw=1.7, transform=transform)
    axes[0].text(1, 1.16, "2 copies of the shared edge", fontsize=10.5, ha="center", color=GRAY)

    draw_base_edges(axes[1])
    nodes = [(0, 0), (1, 0), (2, 0), (0, 1), (1, 1), (2, 1)]
    for i, (x, y) in enumerate(nodes, start=1):
        axes[1].scatter([x], [y], s=43, color=OCHRE, edgecolors="white", linewidths=.6, zorder=3)
        axes[1].text(x, y + (.14 if y else -.16), f"v{i}", ha="center", va="center", fontsize=10.5)

    draw_faces(axes[2])
    draw_base_edges(axes[2], shared=False)
    axes[2].plot([1, 1], [0, 1], color=TEAL, lw=2.0)
    axes[2].annotate("", xy=(1, .86), xytext=(1, .15),
                     arrowprops={"arrowstyle": "-|>", "color": TEAL, "lw": 2.3, "mutation_scale": 15})
    axes[2].text(1.10, .68, "e", color=TEAL, fontsize=12, style="italic")
    axes[2].text(.43, 1.16, "left: A", fontsize=10.5, ha="center")
    axes[2].text(1.58, 1.16, "right: B", fontsize=10.5, ha="center")
    axes[2].text(2.10, .95, "∞", fontsize=14, color=GRAY, ha="left")
    for x, y in nodes:
        axes[2].scatter([x], [y], s=20, color=INK, edgecolors="white", linewidths=.4, zorder=4)

    notes = [
        ("8 stored segments", "Shared edge drawn offset to show both\ncopies; both have x = 1."),
        ("V = 6; E = 7", "Nodes record edge connectivity;\nleft and right faces are not stored."),
        ("V = 6; E = 7; F = 3", "F counts A, B and the outer face.\nEdge e runs from (1, 0) to (1, 1)."),
    ]
    for ax, (count, note) in zip(axes, notes):
        ax.text(.5, -.18, count, transform=ax.transAxes, ha="center", va="top", fontsize=11.5, weight="bold")
        ax.text(.5, -.37, note, transform=ax.transAxes, ha="center", va="top", fontsize=10.5,
                color=GRAY, linespacing=1.4)
    fig.text(.5, .055, "Connected planar partition: V − E + F = 6 − 7 + 3 = 2", ha="center",
             fontsize=11, color=INK)
    save(fig, "fig02_spaghetti_network_topology")


def geometry_axes(ax):
    ax.set_xlim(-.35, 2.55)
    ax.set_ylim(-.35, 2.55)
    ax.set_aspect("equal")
    ax.set_xticks([0, 1, 2])
    ax.set_yticks([0, 1, 2])
    ax.grid(color=LIGHT, linewidth=.6, zorder=-2)
    ax.set_xlabel("x", labelpad=1)
    ax.set_ylabel("y", rotation=0, labelpad=9)


def point(ax, xy, color):
    ax.scatter([xy[0]], [xy[1]], s=42, color=color, edgecolors="white", linewidths=.7, zorder=7)


def draw_halfplanes():
    fig, axes = plt.subplots(1, 2, figsize=(9, 5.2))
    fig.subplots_adjust(left=.075, right=.975, top=.82, bottom=.25, wspace=.22)
    for ax in axes:
        geometry_axes(ax)
    axes[0].set_title("(a) Intersection of half-planes", pad=23)
    axes[1].set_title("(b) Union of two convex pieces", pad=23)
    axes[0].text(.5, 1.025, "x ≥ 0; y ≥ 0; x + y ≤ 2", transform=axes[0].transAxes,
                 ha="center", va="bottom", fontsize=11, color=GRAY)
    axes[1].text(.5, 1.025, "[0, 2] × [0, 1] ∪ [0, 1] × [1, 2]", transform=axes[1].transAxes,
                 ha="center", va="bottom", fontsize=11, color=GRAY)

    axes[0].add_patch(Polygon([(0, 0), (2, 0), (0, 2)], closed=True, facecolor=TEAL,
                              edgecolor=TEAL, linewidth=1.8, alpha=.17, zorder=1))
    axes[0].plot([0, 2, 0, 0], [0, 0, 2, 0], color=TEAL, linewidth=1.7, zorder=2)
    axes[0].text(1.57, .58, "x + y = 2", rotation=-45, fontsize=10, color=GRAY,
                 rotation_mode="anchor", ha="center")
    for xy, color in [((.5, .5), BLUE), ((1, 1), OCHRE), ((1.5, 1), RED)]:
        point(axes[0], xy, color)
    axes[0].annotate("P (0.5, 0.5)\ninside", xy=(.5, .5), xytext=(.23, -.03), fontsize=10.5,
                     ha="left", va="top", color=BLUE,
                     arrowprops={"arrowstyle": "-", "color": BLUE, "lw": .7})
    axes[0].annotate("Q (1, 1)\non boundary", xy=(1, 1), xytext=(.07, 2.28), fontsize=10.5,
                     ha="left", va="center", color="#8C692B",
                     arrowprops={"arrowstyle": "-", "color": OCHRE, "lw": .7})
    axes[0].annotate("R (1.5, 1)\noutside", xy=(1.5, 1), xytext=(1.35, 1.75), fontsize=10.5,
                     ha="left", va="center", color=RED,
                     arrowprops={"arrowstyle": "-", "color": RED, "lw": .7})

    axes[1].add_patch(Rectangle((0, 0), 2, 1, facecolor=TEAL, alpha=.17, edgecolor="none"))
    axes[1].add_patch(Rectangle((0, 1), 1, 1, facecolor=BLUE, alpha=.17, edgecolor="none"))
    outline = np.array([[0, 0], [2, 0], [2, 1], [1, 1], [1, 2], [0, 2], [0, 0]])
    axes[1].plot(outline[:, 0], outline[:, 1], color=TEAL, lw=1.8, zorder=2)
    axes[1].plot([0, 1], [1, 1], linestyle=(0, (4, 2.5)), color=OCHRE, lw=1.8, zorder=3)
    axes[1].text(1.65, .22, "C₁", fontsize=14, color=TEAL, ha="center")
    axes[1].text(.16, 1.83, "C₂", fontsize=14, color=BLUE, ha="center")
    point(axes[1], (.5, 1), PURPLE)
    point(axes[1], (1.5, 1.5), RED)
    axes[1].annotate("S (0.5, 1)\nin the union", xy=(.5, 1), xytext=(.13, 1.43), fontsize=10.5,
                     ha="left", va="center", color=PURPLE,
                     arrowprops={"arrowstyle": "-", "color": PURPLE, "lw": .7})
    axes[1].annotate("T (1.5, 1.5)\noutside", xy=(1.5, 1.5), xytext=(1.13, 2.10), fontsize=10.5,
                     ha="left", va="center", color=RED,
                     arrowprops={"arrowstyle": "-", "color": RED, "lw": .7})
    axes[0].text(.5, -.25, "P: INSIDE; Q: BOUNDARY; R: OUTSIDE\nIllustrative classification with ε = 0.",
                 transform=axes[0].transAxes, ha="center", va="top", fontsize=10.5,
                 color=GRAY, linespacing=1.5)
    axes[1].text(.5, -.25, "The dashed line separates the two pieces.\nS is not on the outer boundary of the union.",
                 transform=axes[1].transAxes, ha="center", va="top", fontsize=10.5,
                 color=GRAY, linespacing=1.5)
    save(fig, "fig03_halfplanes")


if __name__ == "__main__":
    draw_models()
    draw_topology()
    draw_halfplanes()
    print("Created 3 original figures as PNG (300 dpi) and SVG in", HERE)
