#!/usr/bin/env python3
"""Build data/integrated_assets.json: the production assets the game actually uses.

The production library lives under assets/ on main (owner PRs #2/#3, 2026-11-10), with its
manifest at assets/asset_manifest.json and stream fragments in assets/manifest_parts/. Paths
were rewritten from the delivery root `generated_assets/` to `assets/` after the move; any
entry still using the old root is mapped to `assets/` here.

Only ids listed in tools/assets/integration_selection.json (per vertical slice) are
integrated. Each entry is copied verbatim (source, rights_status, approval_status, contract
fields), with:
- `path`: the file's location in this repository (assets/...);
- `slice`: the vertical slice that integrated it;
- `albedo_mean_linear` for texture-set albedo maps;
- `required_by`: for files pulled in automatically because an integrated glb (glTF external
  image URIs) or Godot text resource (.tres/.tscn ext_resources) references them, the ids of
  those assets; UI kit 1x files carry their 2x entry's metadata with `variant`.
Godot particle presets (`godot_presets` in the selection: name -> .tscn under assets/) are
listed under `presets`; every texture a preset references must itself be integrated, so a build
never ships a preset without its sheets. The preset files carry no rights of their own beyond
those textures (scene text written by the ui-vfx stream).
Nothing here changes rights or approval status: development integration is not clearance.

    python tools/assets/build_integration_manifest.py
"""

import json
import posixpath
import re
import struct
import subprocess
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
LIBRARY = REPO / "assets"
SELECTION = REPO / "tools/assets/integration_selection.json"
OUT = REPO / "data/integrated_assets.json"
FRAGMENTS = ["3d-kits", "surfaces", "ui-vfx", "audio"]
DELIVERY_ROOT = "generated_assets/"


def srgb_to_linear(c):
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def albedo_mean_linear(path):
    from PIL import Image
    img = Image.open(path).convert("RGB").resize((64, 64))
    pixels = list(img.get_flattened_data()) if hasattr(img, "get_flattened_data") else list(img.getdata())
    return [round(sum(srgb_to_linear(p[i] / 255.0) for p in pixels) / len(pixels), 4) for i in range(3)]


def repo_path(delivered):
    return "assets/" + delivered[len(DELIVERY_ROOT):] if delivered.startswith(DELIVERY_ROOT) else delivered


def glb_image_paths(repo_rel):
    """Repository paths of the external images a .glb references."""
    data = (REPO / repo_rel).read_bytes()
    length = struct.unpack("<I", data[12:16])[0]
    gltf = json.loads(data[20:20 + length])
    base = posixpath.dirname(repo_rel)
    return [posixpath.normpath(posixpath.join(base, image["uri"])) for image in gltf.get("images", []) if image.get("uri")]


def preset_texture_paths(repo_rel):
    """Repository paths of the res:// resources a .tscn preset references."""
    text = (REPO / repo_rel).read_text(encoding="utf-8")
    return [m[len("res://"):] for m in re.findall(r'path="(res://[^"]+)"', text)]


def text_resource_paths(repo_rel):
    """Repository paths of the ext_resources a Godot text resource (.tres/.tscn) references."""
    text = (REPO / repo_rel).read_text(encoding="utf-8")
    return [m for m in re.findall(r'path="res://([^"]+)"', text)]


def main():
    by_id = {}
    for name in FRAGMENTS:
        fragment = LIBRARY / "manifest_parts" / f"{name}.json"
        if fragment.exists():
            for entry in json.loads(fragment.read_text(encoding="utf-8")).get("entries", []):
                by_id[entry["id"]] = entry
    for entry in json.loads((LIBRARY / "asset_manifest.json").read_text(encoding="utf-8"))["entries"]:
        by_id[entry["id"]] = entry  # the merged manifest wins over fragments
    selection_data = json.loads(SELECTION.read_text(encoding="utf-8"))
    selection = selection_data["slices"]
    preset_selection = {k: v for k, v in selection_data.get("godot_presets", {}).items() if not k.startswith("_")}
    library_commit = subprocess.run(["git", "log", "-1", "--format=%h", "--", "assets/asset_manifest.json"],
                                    cwd=REPO, capture_output=True, text=True).stdout.strip()
    entries, problems = [], []
    for slice_name, ids in selection.items():
        for asset_id in ids:
            entry = by_id.get(asset_id)
            if entry is None:
                problems.append(f"{asset_id}: not in the library manifest")
                continue
            entry = dict(entry)
            entry["path"] = repo_path(entry["path"])
            entry["slice"] = slice_name
            if not (REPO / entry["path"]).exists():
                problems.append(f"{asset_id}: file missing at {entry['path']}")
                continue
            if "-MAT-" in asset_id and entry["path"].endswith("_albedo.png"):
                entry["albedo_mean_linear"] = albedo_mean_linear(REPO / entry["path"])
            entries.append(entry)
    # Dependencies: textures the integrated glbs reference must ship with them.
    by_path = {repo_path(e["path"]): e for e in by_id.values()}
    integrated = {e["path"]: e for e in entries}
    for entry in list(entries):
        if entry["path"].endswith(".glb"):
            deps = glb_image_paths(entry["path"])
        elif entry["path"].endswith((".tres", ".tscn")):
            deps = text_resource_paths(entry["path"])
        else:
            continue
        for dep in deps:
            if dep in integrated:
                integrated[dep].setdefault("required_by", [])
                if entry["id"] not in integrated[dep]["required_by"] and integrated[dep].get("slice") == "dependency":
                    integrated[dep]["required_by"].append(entry["id"])
                continue
            source = by_path.get(dep)
            variant_of = None
            if source is None and "/png_1x/" in dep:
                # UI kit 1x files are recorded in the notes of their 2x entry (same id).
                source = by_path.get(dep.replace("/png_1x/", "/png_2x/"))
                variant_of = "1x of " + source["path"] if source else None
            if source is None:
                problems.append(f"{entry['id']}: references {dep}, which has no manifest entry")
                continue
            dep_entry = dict(source)
            dep_entry["path"] = dep
            dep_entry["slice"] = "dependency"
            dep_entry["required_by"] = [entry["id"]]
            if variant_of:
                dep_entry["variant"] = variant_of
            if not (REPO / dep).exists():
                problems.append(f"{entry['id']}: references missing file {dep}")
                continue
            entries.append(dep_entry)
            integrated[dep] = dep_entry
    presets = {}
    for name, path in preset_selection.items():
        if not (REPO / path).exists():
            problems.append(f"preset {name}: file missing at {path}")
            continue
        missing = [dep for dep in preset_texture_paths(path) if dep not in integrated]
        if missing:
            problems.append(f"preset {name}: references files that are not integrated: {', '.join(missing)}")
            continue
        presets[name] = path
    out = {
        "_note": "Production assets the game uses, for development (owner approval 2026-11-10). Entries are copied verbatim from assets/asset_manifest.json (and stream fragments); rights_status and approval_status are unchanged: this is not commercial release clearance. Generated by tools/assets/build_integration_manifest.py from tools/assets/integration_selection.json.",
        "library": "assets/asset_manifest.json",
        "library_commit": library_commit,
        "entries": entries,
        "presets": presets,
    }
    OUT.write_text(json.dumps(out, indent="\t", ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    print(f"{len(entries)} entries, {len(presets)} presets ({', '.join(f'{k}: {len(v)}' for k, v in selection.items())}) -> {OUT.relative_to(REPO)}")
    if problems:
        print("NOT INTEGRATED:", *problems, sep="\n  ")
        raise SystemExit(1)


if __name__ == "__main__":
    main()
