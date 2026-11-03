"""Package reproducible report sources, figures, and experiment data.

The delivered Word and PDF are distributed separately. Each source ZIP includes
a SHA-256 manifest to allow independent verification of every included file.
"""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile


PACKAGE_NAME = "Spatial_Representation_Sources_and_Data"
SOURCE_DIR = Path(__file__).resolve().parent
PACKAGE_FILE = SOURCE_DIR.parent / f"{PACKAGE_NAME}.zip"
MANIFEST_FILE = SOURCE_DIR / "MANIFEST_SHA256.json"


def include(path: Path) -> bool:
    if not path.is_file():
        return False
    if any(part == "__pycache__" or part.startswith(".") for part in path.relative_to(SOURCE_DIR).parts):
        return False
    if path.suffix.lower() in {".docx", ".pdf", ".pyc"}:
        return False
    return path != MANIFEST_FILE


def main() -> None:
    files = sorted(
        (p for p in SOURCE_DIR.rglob("*") if include(p)),
        key=lambda path: path.relative_to(SOURCE_DIR).as_posix(),
    )
    records = []
    for path in files:
        content = path.read_bytes()
        records.append(
            {
                "path": path.relative_to(SOURCE_DIR).as_posix(),
                "bytes": len(content),
                "sha256": hashlib.sha256(content).hexdigest(),
            }
        )
    manifest = {"package": PACKAGE_NAME, "files": records}
    MANIFEST_FILE.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    temporary_file = PACKAGE_FILE.with_suffix(".zip.part")
    try:
        with ZipFile(temporary_file, "w", compression=ZIP_DEFLATED, compresslevel=6) as zf:
            for path in files:
                relative = path.relative_to(SOURCE_DIR).as_posix()
                zf.write(path, f"{PACKAGE_NAME}/{relative}")
            zf.write(MANIFEST_FILE, f"{PACKAGE_NAME}/{MANIFEST_FILE.name}")
        with ZipFile(temporary_file) as check:
            if check.testzip() is not None:
                raise RuntimeError("ZIP CRC verification failed")
            if len(check.namelist()) != len(files) + 1:
                raise RuntimeError("ZIP file count mismatch")
        os.replace(temporary_file, PACKAGE_FILE)
    finally:
        temporary_file.unlink(missing_ok=True)
    print(f"Archive: {PACKAGE_FILE}")
    print(f"Files: {len(files) + 1}")
    print(f"Bytes: {PACKAGE_FILE.stat().st_size}")


if __name__ == "__main__":
    main()
