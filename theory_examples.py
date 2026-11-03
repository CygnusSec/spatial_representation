#!/usr/bin/env python3
"""Reproduce the two theory examples without GIS libraries.

Only Python's standard library is required. Input assumptions are deliberately
explicit: half-planes form a nonempty full-dimensional convex polygon; polygon
boundaries are valid, oriented, exactly coincident where shared, and fully noded.
This script does not claim to validate or repair arbitrary geometry.
"""

from pathlib import Path
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
        "scope": "No input repair, automatic noding, general validity test, or complete DCEL construction.",
    }
    destination = Path(__file__).resolve().with_name("theory_examples_results.json")
    destination.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": result["status"], "results": str(destination)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
