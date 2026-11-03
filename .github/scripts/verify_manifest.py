#!/usr/bin/env python3
"""Check MANIFEST_SHA256.json against the files package_report_sources.py would ship."""
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.dont_write_bytecode = True
sys.path.insert(0, str(ROOT))
import package_report_sources as package  # noqa: E402

records = json.loads(package.MANIFEST_FILE.read_text(encoding="utf-8"))["files"]
listed = {record["path"]: record for record in records}
on_disk = {p.relative_to(ROOT).as_posix() for p in ROOT.rglob("*") if package.include(p)}

problems = [f"missing from disk: {path}" for path in sorted(listed.keys() - on_disk)]
problems += [f"not in manifest: {path}" for path in sorted(on_disk - listed.keys())]
for path in sorted(on_disk & listed.keys()):
    content = (ROOT / path).read_bytes()
    record = listed[path]
    if len(content) != record["bytes"] or hashlib.sha256(content).hexdigest() != record["sha256"]:
        problems.append(f"content differs: {path}")

if problems:
    print("\n".join(problems))
    print("Regenerate MANIFEST_SHA256.json after changing packaged files.")
    sys.exit(1)
print(f"Manifest OK: {len(listed)} files")
