#!/usr/bin/env python3
"""Compare the deterministic output of a quick run with a stored result set.

Timings are not compared because they depend on the machine.
Usage: verify_quick_run.py QUICK_DIR BASELINE_DIR
"""
import json
import math
import sys
from pathlib import Path


def load(directory, name):
    return json.loads((Path(directory) / name).read_text(encoding="utf-8"))


def close(a, b, path="e1"):
    """Exact for structure and text; relative tolerance for floats across CPUs."""
    if isinstance(a, dict) and isinstance(b, dict) and a.keys() == b.keys():
        return [p for k in a for p in close(a[k], b[k], f"{path}.{k}")]
    if isinstance(a, list) and isinstance(b, list) and len(a) == len(b):
        return [p for i, pair in enumerate(zip(a, b)) for p in close(*pair, f"{path}[{i}]")]
    if isinstance(a, float) and isinstance(b, float):
        return [] if math.isclose(a, b, rel_tol=1e-9, abs_tol=1e-9) else [path]
    return [] if a == b else [path]


quick, baseline = sys.argv[1:3]
problems = close(load(quick, "e1_topology.json"), load(baseline, "e1_topology.json"))

stored = {(r["n"], r["profile"]): r for r in load(baseline, "e2_summary.json")}
new = load(quick, "e2_summary.json")
for row in new:
    key = (row["n"], row["profile"])
    if not row["validation"]["passed"]:
        problems.append(f"validation failed: {key}")
    if key not in stored:
        problems.append(f"no stored result: {key}")
    elif row["sha256"] != stored[key]["sha256"]:
        problems.append(f"file bytes differ: {key}")

if not load(quick, "e3_summary.json"):
    problems.append("E3 produced no result")

if problems:
    print("\n".join(problems))
    sys.exit(1)
print(f"Quick run matches {baseline}: E1 and {len(new)} E2 files")
