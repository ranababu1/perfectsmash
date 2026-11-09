#!/usr/bin/env python3
"""Print (or apply) the export exclude filter that ships only the assets the game uses.

The production library under assets/ holds every chapter (about 370 MB). Builds should carry
only what data/integrated_assets.json lists plus the game's own assets (KEEP below). Godot export
filters cannot whitelist (exclude wins over include), so this tool computes exclusions: every
directory under assets/ with nothing kept in it becomes "dir/*", and in mixed directories each
unused file is excluded by path. Rerun after every integration slice.

    python tools/assets/export_filter.py                  # print the filter
    python tools/assets/export_filter.py --apply FILE     # rewrite exclude_filter lines in an
                                                          # export_presets.cfg (local, gitignored)
"""

import argparse
import json
import re
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
ASSETS = REPO / "assets"
BASE_EXCLUDE = ["tests/*", "tools/*", "docs/*"]
## Game files under assets/ that are not part of the production library manifest.
KEEP = ["assets/icon", "assets/audio/music/gameplay_bed.ogg"]


def kept_paths():
    data = json.loads((REPO / "data/integrated_assets.json").read_text(encoding="utf-8"))
    return {e["path"] for e in data["entries"]} | set(data.get("presets", {}).values())


def is_kept(rel, kept):
    return rel in kept or any(rel == k or rel.startswith(k + "/") for k in KEEP)


def subtree_has_kept(rel_dir, kept):
    prefix = rel_dir + "/"
    return any(k.startswith(prefix) for k in kept) or any(k == rel_dir or k.startswith(prefix) or rel_dir.startswith(k + "/") for k in KEEP)


def exclusions():
    kept = kept_paths()
    out = []

    def walk(directory):
        rel = directory.relative_to(REPO).as_posix()
        if not subtree_has_kept(rel, kept):
            out.append(rel + "/*")
            return
        for child in sorted(directory.iterdir()):
            crel = child.relative_to(REPO).as_posix()
            if child.is_dir():
                walk(child)
            elif not child.name.endswith(".import") and not is_kept(crel, kept):
                out.append(crel)

    walk(ASSETS)
    return out


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--apply", type=Path, help="export_presets.cfg to update in place")
    args = parser.parse_args()
    value = ", ".join(BASE_EXCLUDE + exclusions())
    if args.apply:
        text = args.apply.read_text(encoding="utf-8")
        text = re.sub(r'^exclude_filter=".*"$', lambda m: f'exclude_filter="{value}"', text, flags=re.M)
        args.apply.write_text(text, encoding="utf-8", newline="\n")
        print(f"applied {len(value.split(', '))} exclusions to {args.apply}")
    else:
        print(value)


if __name__ == "__main__":
    main()
