#!/usr/bin/env python3
"""Reproduce the theory examples without GIS libraries.

Only Python's standard library is required. Input assumptions are deliberately
explicit: half-planes form a nonempty full-dimensional convex polygon; polygon
boundaries are valid, oriented, exactly coincident where shared, and fully noded.
This script does not claim to validate or repair arbitrary geometry.

Besides the half-plane and shared-edge examples, it covers the network model and
TIGER/Line record linkage of Chapter 2 (Rigaux, Scholl and Voisard, 2002).
"""

from pathlib import Path
import heapq
import json
import math


def convex_classify(point, constraints, epsilon=0.0):
    """Return INSIDE, BOUNDARY or OUTSIDE using normalized signed distances.

    Positive epsilon defines a boundary tolerance band in coordinate units.
    That band may include points slightly outside the mathematical polygon.
    Nonzero normals and the stated geometric input assumptions are required.
    """
    if epsilon < 0 or not math.isfinite(epsilon):
        raise ValueError("epsilon must be a finite nonnegative number")
    if not constraints:
        raise ValueError("a polygon requires half-plane constraints")
    near_boundary = False
    x, y = point
    for a, b, c in constraints:
        normal = math.hypot(a, b)
        if normal == 0:
            raise ValueError("zero normal is not a valid input constraint")
        distance = (a * x + b * y + c) / normal
        if distance > epsilon:
            return "OUTSIDE"
        if abs(distance) <= epsilon:
            near_boundary = True
    return "BOUNDARY" if near_boundary else "INSIDE"


def build_shared_edges(polygons):
    """Build canonical atomic edges with left/right faces and ring references.

    polygons maps face ID to a list of rings. Rings may be closed or unclosed.
    Outer rings are CCW; hole rings are CW. Edges are oriented from the
    lexicographically smaller vertex to the larger. An unassigned side stays None:
    distinguishing complementary faces requires a separate construction, because
    an uncovered hole need not belong to the unbounded exterior face.
    This produces a preliminary edge/face table, not complete DCEL next/prev links.
    """
    edges = {}
    ring_references = {}
    for face, rings in polygons.items():
        ring_references[face] = []
        for ring in rings:
            vertices = [tuple(p) for p in ring]
            if len(vertices) > 1 and vertices[0] == vertices[-1]:
                vertices.pop()
            if len(vertices) < 3:
                raise ValueError("a ring needs at least three vertices")
            refs = []
            for index, u in enumerate(vertices):
                v = vertices[(index + 1) % len(vertices)]
                if u == v:
                    raise ValueError("zero-length edge")
                key = (min(u, v), max(u, v))
                if key not in edges:
                    edges[key] = {"start": key[0], "end": key[1], "left": None, "right": None}
                side = "left" if (u, v) == key else "right"
                if edges[key][side] is not None:
                    raise ValueError("inconsistent or duplicate face incidence")
                edges[key][side] = face
                refs.append({"edge": key, "orientation": 1 if side == "left" else -1})
            ring_references[face].append(refs)
    return edges, ring_references


def segments_cross(p, q, r, s):
    """Return True when segments pq and rs cross at a single interior point."""
    def side(a, b, c):
        return (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0])
    return side(p, q, r) * side(p, q, s) < 0 and side(r, s, p) * side(r, s, q) < 0


def shortest_path(arcs, start, goal):
    """Dijkstra over undirected arcs given as {name: (node, node, length)}.

    Returns (length, node list), or None when the goal is not connected.
    """
    neighbors = {}
    for u, v, length in arcs.values():
        neighbors.setdefault(u, []).append((v, length))
        neighbors.setdefault(v, []).append((u, length))
    queue = [(0.0, start, [start])]
    settled = set()
    while queue:
        distance, node, path = heapq.heappop(queue)
        if node == goal:
            return distance, path
        if node in settled:
            continue
        settled.add(node)
        for neighbor, length in neighbors.get(node, []):
            if neighbor not in settled:
                heapq.heappush(queue, (distance + length, neighbor, path + [neighbor]))
    return None


def tiger_chain(tlid, record_1, record_2, record_i):
    """Join record types 1, 2 and I on TLID into one complete-chain description.

    Shape records are ordered by RTSQ and a (0, 0) pair is a NULL coordinate.
    """
    main_record = next(r for r in record_1 if r["TLID"] == tlid)
    shapes = sorted((r for r in record_2 if r["TLID"] == tlid), key=lambda r: r["RTSQ"])
    points = [p for r in shapes for p in r["points"] if p != (0, 0)]
    link = next((r for r in record_i if r["TLID"] == tlid), None)
    return {
        "tlid": tlid,
        "start": (main_record["FRLONG"], main_record["FRLAT"]),
        "end": (main_record["TOLONG"], main_record["TOLAT"]),
        "shape_points": points,
        "left": (link["CENIDL"], link["POLYIDL"]) if link else None,
        "right": (link["CENIDR"], link["POLYIDR"]) if link else None,
    }


def gt_polygon_boundary(polygon, chains):
    """Rebuild one polygon ring from the chains that name it on either side.

    Follows the two steps of Section 2.4.2: select the chains sharing the polygon
    identifier, then connect them by comparing end coordinates, because TIGER gives
    nodes no identifier. Each chain is oriented so that the polygon lies on its left.
    Handles a single closed ring; holes and multiple rings are out of scope.
    """
    oriented = []
    for chain in chains.values():
        if chain["left"] == polygon and chain["right"] == polygon:
            continue
        line = [chain["start"], *chain.get("shape_points", []), chain["end"]]
        if chain["left"] == polygon:
            oriented.append(line)
        elif chain["right"] == polygon:
            oriented.append(line[::-1])
    if not oriented:
        raise ValueError("no chain references this polygon")
    ring = list(oriented.pop(0))
    while oriented:
        following = next((line for line in oriented if line[0] == ring[-1]), None)
        if following is None:
            raise ValueError("chains do not form one connected ring")
        oriented.remove(following)
        ring.extend(following[1:])
    if ring[0] != ring[-1]:
        raise ValueError("chains do not close the ring")
    return ring


def signed_area(ring):
    """Shoelace area of a closed ring; positive when counterclockwise."""
    return sum(a[0] * b[1] - b[0] * a[1] for a, b in zip(ring, ring[1:])) / 2


def main():
    constraints = [(-1.0, 0.0, 0.0), (0.0, -1.0, 0.0), (1.0, 1.0, -2.0)]
    points = {"P": (.5, .5), "Q": (1.0, 1.0), "R": (1.5, 1.0)}
    expected = {"P": "INSIDE", "Q": "BOUNDARY", "R": "OUTSIDE"}
    observed = {name: convex_classify(point, constraints) for name, point in points.items()}
    assert observed == expected

    # Positive rescaling must not alter epsilon's geometric meaning.
    tolerance = 1e-8
    tolerance_points = list(points.values()) + [(1 + 1e-9, 1), (-1e-9, .5), (1 + 1e-5, 1)]
    scales = [1e-9, .001, 1.0, 17.0, 1e9]
    rescale_checks = 0
    for point in tolerance_points:
        base = convex_classify(point, constraints, tolerance)
        for scale in scales:
            rescaled = [(a * scale, b * scale, c * scale) for a, b, c in constraints]
            assert convex_classify(point, rescaled, tolerance) == base
            # Also scale each constraint differently.
            mixed = [(a * scales[i], b * scales[i], c * scales[i])
                     for i, (a, b, c) in enumerate(constraints)]
            assert convex_classify(point, mixed, tolerance) == base
            rescale_checks += 2
    assert convex_classify((1 + 1e-9, 1), constraints, tolerance) == "BOUNDARY"
    assert convex_classify((1 + 1e-9, 1), constraints, 0) == "OUTSIDE"

    polygons = {
        "A": [[(0, 0), (1, 0), (1, 1), (0, 1)]],
        "B": [[(1, 0), (2, 0), (2, 1), (1, 1)]],
    }
    edges, refs = build_shared_edges(polygons)
    vertices = {p for key in edges for p in key}
    shared = edges[((1, 0), (1, 1))]
    assert len(edges) == 7
    assert len(vertices) == 6
    assert shared["left"] == "A" and shared["right"] == "B"
    assert sum(len(ring) for face in refs.values() for ring in face) == 8
    assert len(vertices) - len(edges) + 3 == 2

    # This particular union is the single rectangle [0,2] x [0,1], with no holes.
    # Only for this hand-verified example do all unassigned sides share one
    # unbounded exterior face. This is not a general complementary-face builder.
    for edge in edges.values():
        for side in ("left", "right"):
            if edge[side] is None:
                edge[side] = "OUTER"

    # A partition edge can be interior to a union, despite bounding each piece.
    c1 = [(-1, 0, 0), (1, 0, -2), (0, -1, 0), (0, 1, -1)]
    c2 = [(-1, 0, 0), (1, 0, -1), (0, -1, 1), (0, 1, -2)]
    assert convex_classify((.5, 1), c1) == "BOUNDARY"
    assert convex_classify((.5, 1), c2) == "BOUNDARY"
    assert convex_classify((1.5, 1.5), c1) == "OUTSIDE"
    assert convex_classify((1.5, 1.5), c2) == "OUTSIDE"

    # Network model: a crossing in projection is a connection only if it is a node.
    west, east, south, north, crossing = (0, 1), (2, 1), (1, 0), (1, 2), (1, 1)
    assert segments_cross(west, east, south, north)
    nonplanar = {"road": ("W", "E", 2.0), "overpass": ("S", "N", 2.0)}
    planar = {"WX": ("W", "X", 1.0), "XE": ("X", "E", 1.0), "SX": ("S", "X", 1.0), "XN": ("X", "N", 1.0)}
    assert shortest_path(nonplanar, "S", "E") is None
    planar_length, planar_path = shortest_path(planar, "S", "E")
    assert planar_length == 2.0 and planar_path == ["S", "X", "E"]

    # TIGER/Line: chain 8086 as printed in Tables 2.1-2.3 of the book. LONG2-LAT9 of
    # the first shape record are elided in Table 2.2, so only printed points appear.
    record_1 = [
        {"TLID": 8086, "FRLONG": -72156546, "FRLAT": 41957498, "TOLONG": -72161936, "TOLAT": 41958117},
        {"TLID": 8087, "FRLONG": -72197129, "FRLAT": 41957206, "TOLONG": -72197197, "TOLAT": 41957669},
    ]
    record_2 = [
        {"TLID": 8086, "RTSQ": 2, "points": [(-72161599, 41958117), (0, 0)]},
        {"TLID": 8086, "RTSQ": 1, "points": [(-72156638, 41957658), (-72157985, 41958184)]},
    ]
    record_i = [{"TLID": 8086, "CENIDL": "PO123", "POLYIDL": 1, "CENIDR": "PO1987", "POLYIDR": 1}]
    chain_8086 = tiger_chain(8086, record_1, record_2, record_i)
    assert chain_8086["shape_points"][0] == (-72156638, 41957658)
    assert chain_8086["shape_points"][-1] == (-72161599, 41958117)
    assert chain_8086["left"] == ("PO123", 1) and chain_8086["right"] == ("PO1987", 1)
    chain_8087 = tiger_chain(8087, record_1, record_2, record_i)
    assert chain_8087["shape_points"] == [] and chain_8087["left"] is None

    # Figure 2.14 expressed as chains. The book fixes f = [N1, N2, P1, P2, <>]; the
    # direction of the other arcs is chosen here and verified by the areas below.
    n1, n2 = (3, 0), (2, 2)
    figure_chains = {
        "a": {"start": (0, 2), "end": n1, "left": "P1", "right": "OUTER"},
        "b": {"start": n2, "end": (0, 2), "left": "P1", "right": "OUTER"},
        "c": {"start": n2, "end": (4, 4), "left": "OUTER", "right": "P2"},
        "d": {"start": (4, 4), "end": (6, 1), "left": "OUTER", "right": "P2"},
        "e": {"start": (6, 1), "end": n1, "left": "OUTER", "right": "P2"},
        "f": {"start": n1, "end": n2, "left": "P1", "right": "P2"},
    }
    ring_p1 = gt_polygon_boundary("P1", figure_chains)
    ring_p2 = gt_polygon_boundary("P2", figure_chains)
    assert {n for n, c in figure_chains.items() if "P1" in (c["left"], c["right"])} == {"a", "b", "f"}
    assert {n for n, c in figure_chains.items() if "P2" in (c["left"], c["right"])} == {"c", "d", "e", "f"}
    assert {n for n, c in figure_chains.items() if n1 in (c["start"], c["end"])} == {"a", "e", "f"}
    assert signed_area(ring_p1) == 2.0 and signed_area(ring_p2) == 8.5
    polygon_p = [(4, 4), (6, 1), (3, 0), (0, 2), (2, 2), (4, 4)]
    assert abs(signed_area(polygon_p)) == signed_area(ring_p1) + signed_area(ring_p2)
    adjacent_to_p1 = sorted({side for c in figure_chains.values() if "P1" in (c["left"], c["right"])
                             for side in (c["left"], c["right"])} - {"P1"})
    assert adjacent_to_p1 == ["OUTER", "P2"]
    figure_vertices = {p for c in figure_chains.values() for p in (c["start"], c["end"])}
    assert len(figure_vertices) - len(figure_chains) + 3 == 2

    result = {
        "status": "all assertions passed",
        "coordinates": "dimensionless synthetic examples",
        "halfplanes": {
            "constraints_ax_by_c_le_0": constraints,
            "epsilon_exact_example": 0,
            "classifications": [{"id": name, "point": point, "classification": observed[name]}
                                for name, point in points.items()],
            "rescaling_checks_passed": rescale_checks,
            "rescaling_epsilon": tolerance,
            "positive_scales": scales,
            "boundary_band_example": {"point": [1 + 1e-9, 1], "epsilon_0": "OUTSIDE",
                                      "epsilon_1e_minus_8": "BOUNDARY"},
        },
        "shared_edges": {
            "exterior_assignment": "OUTER is assigned only for the verified two-square example; the general function leaves unassigned sides as None.",
            "input_boundary_segment_occurrences": 8,
            "unique_vertices": len(vertices), "unique_edges": len(edges),
            "faces_including_exterior": 3, "euler_V_minus_E_plus_F": 2,
            "common_edge": shared,
            "all_edges": [edges[key] for key in sorted(edges)],
            "face_ring_references": refs,
        },
        "union_counterexample": {
            "point": [.5, 1], "C1": "BOUNDARY", "C2": "BOUNDARY",
            "union": "INSIDE",
            "reason": "A small disk around (0.5,1) is contained in the union of the two rectangles.",
        },
        "network": {
            "example": "Illustrative two roads crossing at (1, 1); not taken from the book.",
            "segments_cross_in_projection": True,
            "nonplanar_arcs": sorted(nonplanar),
            "nonplanar_path_S_to_E": None,
            "planar_arcs": sorted(planar),
            "planar_path_S_to_E": planar_path,
            "planar_length": planar_length,
        },
        "tiger_line": {
            "chain_from_book_tables_2_1_to_2_3": chain_8086,
            "shape_points_elided_in_table_2_2": 8,
            "chain_8087_without_shape_or_link_records": chain_8087,
            "figure_2_14": {
                "direction_of_arcs_other_than_f": "Chosen for this example; the book only fixes arc f.",
                "ring_P1": ring_p1,
                "ring_P2": ring_p2,
                "area_P1": signed_area(ring_p1),
                "area_P2": signed_area(ring_p2),
                "area_polygon_P_of_figure_2_6": abs(signed_area(polygon_p)),
                "polygons_adjacent_to_P1": adjacent_to_p1,
                "euler_V_minus_E_plus_F": 2,
            },
        },
        "scope": "No input repair, automatic noding, general validity test, or complete DCEL construction.",
    }
    destination = Path(__file__).resolve().with_name("theory_examples_results.json")
    destination.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": result["status"], "results": str(destination)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
