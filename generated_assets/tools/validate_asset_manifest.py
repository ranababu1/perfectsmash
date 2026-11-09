#!/usr/bin/env python3
"""Validate generated_assets/asset_manifest.json against its schema and the repository.

Checks:
  - Manifest JSON parses and has a schema block.
  - Every entry and planned item has its required fields, non-empty.
  - IDs are unique across entries[] and planned[].
  - category, render_type and approval_status values are in the schema's allowed lists.
  - Planned items use an allowed planned status.
  - Every entries[].path exists relative to the repo root, and no path is listed twice.
  - Planned items must not carry a 'path' that points at an existing file (warning).

Exit code is non-zero on any failure.

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
        return 1
    try:
        data = json.loads(MANIFEST.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        print(f"FAIL: manifest is not valid JSON: {exc}", file=sys.stderr)
        return 1

    errors: list[str] = []
    warnings: list[str] = []

    schema = data.get("schema")
    if not isinstance(schema, dict):
        print("FAIL: manifest has no schema block", file=sys.stderr)
        return 1

    def allowed(key: str) -> set[str]:
        values = schema.get(key)
        if not isinstance(values, list) or not values:
            errors.append(f"schema.{key} is missing or empty")
            return set()
        return set(values)

    categories = allowed("categories")
    render_types = allowed("render_types")
    approvals = allowed("approval_statuses")
    planned_statuses = allowed("planned_statuses")
    entry_required = schema.get("entry_fields_required") or []
    planned_required = schema.get("planned_fields_required") or []

    entries = data.get("entries")
    planned = data.get("planned", [])
    if not isinstance(entries, list):
        errors.append("entries must be a list")
        entries = []
    if not isinstance(planned, list):
        errors.append("planned must be a list")
        planned = []

    seen_ids: dict[str, str] = {}
    seen_paths: set[str] = set()

    def check_id(item: dict, where: str) -> None:
        item_id = item.get("id")
        if not item_id:
            return
        if item_id in seen_ids:
            errors.append(f"{where}: duplicate id {item_id!r} (also in {seen_ids[item_id]})")
        else:
            seen_ids[item_id] = where

    def check_required(item: dict, fields: list[str], where: str) -> None:
        for field in fields:
            value = item.get(field)
            if value is None or (isinstance(value, str) and not value.strip()):
                errors.append(f"{where}: missing required field {field!r}")

    present = 0
    for index, item in enumerate(entries):
        where = f"entries[{index}] ({item.get('id', '?')})"
        if not isinstance(item, dict):
            errors.append(f"{where}: not an object")
            continue
        check_required(item, entry_required, where)
        check_id(item, where)
        if item.get("category") not in categories:
            errors.append(f"{where}: invalid category {item.get('category')!r}")
        if item.get("render_type") not in render_types:
            errors.append(f"{where}: invalid render_type {item.get('render_type')!r}")
        if item.get("approval_status") not in approvals:
            errors.append(f"{where}: invalid approval_status {item.get('approval_status')!r}")
        path = item.get("path")
        if path:
            if path in seen_paths:
                errors.append(f"{where}: path listed twice: {path}")
            seen_paths.add(path)
            if (REPO_ROOT / path).is_file():
                present += 1
            else:
                errors.append(f"{where}: file missing on disk: {path}")

    for index, item in enumerate(planned):
        where = f"planned[{index}] ({item.get('id', '?')})"
        if not isinstance(item, dict):
            errors.append(f"{where}: not an object")
            continue
        check_required(item, planned_required, where)
        check_id(item, where)
        if item.get("category") not in categories:
            errors.append(f"{where}: invalid category {item.get('category')!r}")
        if item.get("render_type") not in render_types:
            errors.append(f"{where}: invalid render_type {item.get('render_type')!r}")
        if item.get("status") not in planned_statuses:
            errors.append(f"{where}: invalid status {item.get('status')!r}")
        path = item.get("path")
        if path and (REPO_ROOT / path).exists():
            warnings.append(f"{where}: planned item points at an existing file: {path}")

    print(f"entries: {len(entries)} checked, {present} present")
    print(f"planned: {len(planned)} listed")
    for message in warnings:
        print(f"WARN: {message}")
    if errors:
        for message in errors:
            print(f"FAIL: {message}", file=sys.stderr)
        print(f"FAIL: {len(errors)} problem(s)", file=sys.stderr)
        return 1
    print("PASS: schema, unique ids, allowed values and file paths all valid")
    return 0


if __name__ == "__main__":
    sys.exit(main())
