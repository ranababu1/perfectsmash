#!/usr/bin/env python3
"""Validate generated_assets/asset_manifest.json against the repository.

Checks:
  - Manifest JSON parses.
  - Every entries[].path exists relative to the repo root.
  - planned[] paths (if any full path field is present) do NOT need to exist;
    proposed_path_prefix directories are optional.
  - No entries[] path is missing; fail non-zero if so.
  - Warn if a planned item accidentally points at an existing file using a 'path' key.

Usage (from repo root or any cwd):
  python3 generated_assets/tools/validate_asset_manifest.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

SCRIPT = Path(__file__).resolve()
GEN_ROOT = SCRIPT.parents[1]
REPO_ROOT = SCRIPT.parents[2]
MANIFEST = GEN_ROOT / "asset_manifest.json"


def main() -> int:
    if not MANIFEST.is_file():
        print(f"FAIL: manifest not found: {MANIFEST}", file=sys.stderr)
        return 2

    data = json.loads(MANIFEST.read_text(encoding="utf-8"))
    entries = data.get("entries") or []
    planned = data.get("planned") or []

    missing: list[str] = []
    present = 0
    for entry in entries:
        rel = entry.get("path")
        eid = entry.get("id", "<no-id>")
        if not rel:
            missing.append(f"{eid}: entries item missing 'path'")
            continue
        full = REPO_ROOT / rel
        if full.is_file():
            present += 1
            print(f"OK   {eid}: {rel}")
        else:
            missing.append(f"{eid}: missing file {rel}")
            print(f"MISS {eid}: {rel}", file=sys.stderr)

    planned_warnings = 0
    for item in planned:
        pid = item.get("id", "<no-id>")
        # Planned inventory must not claim a real path unless explicitly testing.
        if "path" in item and item["path"]:
            full = REPO_ROOT / item["path"]
            if full.is_file():
                print(f"WARN {pid}: planned item has existing path {item['path']} (move to entries?)")
                planned_warnings += 1
            else:
                print(f"PLAN {pid}: path listed but not on disk (ok for planned)")
        else:
            prefix = item.get("proposed_path_prefix", "")
            print(f"PLAN {pid}: {prefix or '(no prefix)'} [{item.get('status', '')}]")

    print("---")
    print(f"entries: {len(entries)} checked, {present} present, {len(missing)} missing")
    print(f"planned: {len(planned)} listed, {planned_warnings} warnings")

    if missing:
        print("FAIL: one or more manifest entries are missing on disk", file=sys.stderr)
        for line in missing:
            print(f"  {line}", file=sys.stderr)
        return 1

    print("PASS: all manifest entries exist on disk")
    return 0


if __name__ == "__main__":
    sys.exit(main())
