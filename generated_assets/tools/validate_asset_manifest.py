#!/usr/bin/env python3
"""Merge and validate the Temporal: First Jump asset manifest.

Sources:
  generated_assets/asset_manifest.json          base manifest (schema, integration-owned entries, planned[])
  generated_assets/manifest_parts/<stream>.json  one fragment per production stream:
                                                 {"stream": "...", "updated": "YYYY-MM-DD", "entries": [...]}

Modes:
  (default)   validate the base manifest plus every fragment in memory; nothing is written.
  --merge     as default, then write the merged result into asset_manifest.json. Entries that came
              from fragments carry "merged_from": "<stream>" and are replaced on every merge, so the
              merge is repeatable. Base-owned entries (no merged_from) are kept as they are.
  --check     fail if asset_manifest.json is not identical to a fresh merge (CI style).
  --report P  also write a JSON report (counts, per-entry facts, problems) to P.
  --loudness  measure integrated loudness of audio entries with ffmpeg ebur128 (slow).
  --strict    treat warnings as failures.

Checks:
  Structure: schema block, required fields, allowed category / render_type / approval_status /
    chapter values, unique ids and paths across the base and ALL fragments, a fragment's entries
    must not shadow base entries, planned[] statuses, "levels" values 1-100.
  Files: every path exists (relative to the repo root).
  Images (png, webp, jpg): real dimensions equal "dimensions" when given; alpha channel present for
    VFX, decals, damage overlays, icons and other sprite/ui transparency assets; not fully transparent;
    power-of-two sizes for textures; sprite-sheet divisibility (width % columns, height % rows,
    frames <= columns*rows) for entries with an "animation" block; 9-slice margins fit the image.
  Meshes (glb, gltf): parses the glTF container without third-party libraries; reports node, mesh,
    material and triangle counts and the world-space bounds (from accessor min/max and node
    transforms); contract checks for destructible components (origin at the centre of the
    collision rectangle, front face inside reference_size_px, depth centred on z = 0 and within
    depth_m), triangle budgets, material slot naming, embedded image count.
  Audio (ogg, wav, flac, mp3): duration and sample rate via soundfile, falling back to ffprobe;
    "duration_seconds" and "sample_rate" must match; optional loudness.
  Video (webm, ogv, mp4): duration via ffprobe.
  Fonts (ttf, otf, woff2): file signature, and a licence file (OFL.txt, LICENSE*) in the same folder.
  Rights: rights_status must never claim commercial clearance for AI-generated output.

Exit code is non-zero on any failure.

Usage (any cwd):
  python3 generated_assets/tools/validate_asset_manifest.py [--merge] [--check] [--report out.json]
"""

from __future__ import annotations

import argparse
import copy
import json
import math
import re
import shutil
import struct
import subprocess
import sys
from pathlib import Path

SCRIPT = Path(__file__).resolve()
GEN_ROOT = SCRIPT.parents[1]
REPO_ROOT = SCRIPT.parents[2]
MANIFEST = GEN_ROOT / "asset_manifest.json"
PARTS_DIR = GEN_ROOT / "manifest_parts"

CHAPTERS = {"helix", "vita", "nova_grid", "civitas", "meridian", "shared"}
IMAGE_EXT = {"png", "webp", "jpg", "jpeg"}
MESH_EXT = {"glb", "gltf"}
AUDIO_EXT = {"ogg", "wav", "flac", "mp3"}
VIDEO_EXT = {"webm", "ogv", "mp4"}
FONT_EXT = {"ttf", "otf", "woff2", "woff"}
# Component depth per kind (metres) from scripts/mission/view/mission_view.gd KINDS.
CODE_KIND_DEPTH = {
    "server_rack": 0.8, "support_column": 0.5, "service_deck": 1.4, "ai_core": 0.7,
    "core_shield": 0.9, "power_cell": 0.5, "blast_wall": 1.2, "relay_mast": 0.3, "relay_dish": 0.8,
}
PX_PER_METRE = 100.0
# Tolerances for contract geometry checks (metres).
DAMAGE_BULGE_TOL = 0.10
SILHOUETTE_TOL = 0.011
ORIGIN_TOL = 0.02
TRIS_STANDARD = 1500
TRIS_HERO = 3000
ID_RE = re.compile(r"^[A-Z0-9]+(-[A-Z0-9_]+)+$")
MATERIAL_NAME_RE = re.compile(r"^(mat|trim|emit|glass|fx|dmg|env|bg|chr|wpn|prj|ui)_[a-z0-9_]+$")


class Problems:
    def __init__(self) -> None:
        self.errors: list[str] = []
        self.warnings: list[str] = []

    def error(self, msg: str) -> None:
        self.errors.append(msg)

    def warn(self, msg: str) -> None:
        self.warnings.append(msg)


# ---------------------------------------------------------------- loading and merging

def load_json(path: Path, problems: Problems):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        problems.error(f"{rel(path)}: not found")
    except json.JSONDecodeError as exc:
        problems.error(f"{rel(path)}: invalid JSON: {exc}")
    return None


def rel(path: Path) -> str:
    try:
        return str(path.relative_to(REPO_ROOT))
    except ValueError:
        return str(path)


def load_fragments(problems: Problems) -> list[tuple[str, Path, list[dict]]]:
    out = []
    if not PARTS_DIR.is_dir():
        return out
    for path in sorted(PARTS_DIR.glob("*.json")):
        data = load_json(path, problems)
        if data is None:
            continue
        if isinstance(data, list):
            stream, entries = path.stem, data
        elif isinstance(data, dict):
            stream = data.get("stream") or path.stem
            entries = data.get("entries", [])
            if stream != path.stem:
                problems.warn(f"{rel(path)}: stream {stream!r} differs from file name; using {path.stem!r}")
                stream = path.stem
        else:
            problems.error(f"{rel(path)}: fragment must be an object or a list")
            continue
        if not isinstance(entries, list):
            problems.error(f"{rel(path)}: entries must be a list")
            continue
        out.append((stream, path, entries))
    return out


def merged_manifest(base: dict, fragments: list[tuple[str, Path, list[dict]]]) -> dict:
    merged = copy.deepcopy(base)
    own = [e for e in merged.get("entries", []) if isinstance(e, dict) and not e.get("merged_from")]
    for stream, _path, entries in fragments:
        for entry in entries:
            if isinstance(entry, dict):
                item = dict(entry)
                item["merged_from"] = stream
                own.append(item)
            else:
                own.append(entry)
    merged["entries"] = own
    merged["fragments"] = [
        {"stream": s, "path": rel(p), "entries": len(e)} for s, p, e in fragments
    ]
    return merged


# ---------------------------------------------------------------- structural checks

def check_structure(data: dict, problems: Problems) -> None:
    schema = data.get("schema")
    if not isinstance(schema, dict):
        problems.error("manifest has no schema block")
        return

    def allowed(key: str) -> set[str]:
        values = schema.get(key)
        if not isinstance(values, list) or not values:
            problems.error(f"schema.{key} is missing or empty")
            return set()
        return set(values)

    categories = allowed("categories")
    render_types = allowed("render_types")
    approvals = allowed("approval_statuses")
    planned_statuses = allowed("planned_statuses")
    chapters = set(schema.get("chapters") or CHAPTERS)
    entry_required = schema.get("entry_fields_required") or []
    planned_required = schema.get("planned_fields_required") or []

    entries = data.get("entries")
    planned = data.get("planned", [])
    if not isinstance(entries, list):
        problems.error("entries must be a list")
        entries = []
    if not isinstance(planned, list):
        problems.error("planned must be a list")
        planned = []

    seen_ids: dict[str, str] = {}
    seen_paths: dict[str, str] = {}

    def where_of(item: dict, kind: str, index: int) -> str:
        src = item.get("merged_from") or "base"
        return f"{kind}[{index}] {item.get('id', '?')} ({src})"

    for index, item in enumerate(entries):
        if not isinstance(item, dict):
            problems.error(f"entries[{index}]: not an object")
            continue
        where = where_of(item, "entries", index)
        for field in entry_required:
            value = item.get(field)
            if value is None or (isinstance(value, str) and not value.strip()):
                problems.error(f"{where}: missing required field {field!r}")
        item_id = item.get("id")
        if item_id:
            if item_id in seen_ids:
                problems.error(f"{where}: duplicate id {item_id!r} (also {seen_ids[item_id]})")
            else:
                seen_ids[item_id] = where
            if item.get("merged_from") and not ID_RE.match(item_id):
                problems.warn(f"{where}: id does not follow <CH>-<TYPE>-<NAME>-<VARIANT> (ASSET_CONTRACT 6)")
        if item.get("category") not in categories:
            problems.error(f"{where}: invalid category {item.get('category')!r}")
        if item.get("render_type") not in render_types:
            problems.error(f"{where}: invalid render_type {item.get('render_type')!r}")
        if item.get("approval_status") not in approvals:
            problems.error(f"{where}: invalid approval_status {item.get('approval_status')!r}")
        if item.get("merged_from") and item.get("approval_status") == "approved":
            problems.warn(f"{where}: fragment entry marked approved; new work should be pending_review")
        chapter = item.get("chapter")
        if chapter is not None and chapter not in chapters:
            problems.error(f"{where}: invalid chapter {chapter!r} (allowed {sorted(chapters)})")
        levels = item.get("levels")
        if levels is not None:
            if not isinstance(levels, list) or not all(isinstance(n, int) and 1 <= n <= 100 for n in levels):
                problems.error(f"{where}: levels must be a list of integers 1-100")
        rights = str(item.get("rights_status", "")).lower()
        if re.search(r"commercial(ly)?[ _-]?clear", rights) and not re.search(r"\bnot\b", rights):
            source = str(item.get("source", "")).lower()
            if any(k in source + rights for k in ("ai", "generat", "suno", "udio", "elevenlabs", "image", "model")):
                problems.error(f"{where}: AI or generated output must not be marked commercially cleared")
        path = item.get("path")
        if path:
            if path in seen_paths:
                problems.error(f"{where}: path listed twice: {path} (also {seen_paths[path]})")
            else:
                seen_paths[path] = where
            if not (REPO_ROOT / path).is_file():
                problems.error(f"{where}: file missing on disk: {path}")

    for index, item in enumerate(planned):
        if not isinstance(item, dict):
            problems.error(f"planned[{index}]: not an object")
            continue
        where = where_of(item, "planned", index)
        for field in planned_required:
            value = item.get(field)
            if value is None or (isinstance(value, str) and not value.strip()):
                problems.error(f"{where}: missing required field {field!r}")
        item_id = item.get("id")
        if item_id:
            if item_id in seen_ids:
                problems.error(f"{where}: duplicate id {item_id!r} (also {seen_ids[item_id]})")
            else:
                seen_ids[item_id] = where
        if item.get("category") not in categories:
            problems.error(f"{where}: invalid category {item.get('category')!r}")
        if item.get("render_type") not in render_types:
            problems.error(f"{where}: invalid render_type {item.get('render_type')!r}")
        if item.get("status") not in planned_statuses:
            problems.error(f"{where}: invalid status {item.get('status')!r}")
        path = item.get("path")
        if path and (REPO_ROOT / path).exists():
            problems.warn(f"{where}: planned item points at an existing file: {path}")


# ---------------------------------------------------------------- images

def parse_dimensions(value) -> tuple[int, int] | None:
    if isinstance(value, str):
        m = re.match(r"^\s*(\d+)\s*[xX]\s*(\d+)", value)
        if m:
            return int(m.group(1)), int(m.group(2))
    if isinstance(value, (list, tuple)) and len(value) >= 2 and all(isinstance(v, (int, float)) for v in value[:2]):
        return int(value[0]), int(value[1])
    if isinstance(value, dict) and "width" in value and "height" in value:
        return int(value["width"]), int(value["height"])
    return None


def is_pow2(n: int) -> bool:
    return n > 0 and (n & (n - 1)) == 0


def needs_alpha(item: dict) -> bool:
    if item.get("requires_alpha") is not None:
        return bool(item["requires_alpha"])
    text = " ".join(str(item.get(k, "")) for k in ("id", "path")).upper()
    if item.get("category") == "vfx" and item.get("render_type") == "sprite":
        return True
    if any(tag in text for tag in ("-DCL-", "-DMG-", "-ICN-", "/ICONS/", "/DECALS/", "/DAMAGE/")):
        return True
    if item.get("nine_slice"):
        return True
    return False


def check_image(item: dict, full: Path, where: str, problems: Problems, facts: dict) -> None:
    try:
        from PIL import Image
    except ImportError:
        problems.warn(f"{where}: Pillow not installed; image checks skipped")
        return
    try:
        with Image.open(full) as img:
            img.load()
            width, height = img.size
            mode = img.mode
            has_alpha = mode in ("RGBA", "LA", "PA") or (mode == "P" and "transparency" in img.info)
            facts.update({"width": width, "height": height, "mode": mode, "alpha": has_alpha})
            if has_alpha:
                alpha = img.convert("RGBA").getchannel("A")
                lo, hi = alpha.getextrema()
                facts["alpha_range"] = [lo, hi]
                if hi == 0:
                    problems.error(f"{where}: image is fully transparent")
            else:
                lo, hi = img.convert("L").getextrema()
                if lo == hi:
                    problems.warn(f"{where}: image is a single flat colour")
    except Exception as exc:  # noqa: BLE001
        problems.error(f"{where}: cannot decode image: {exc}")
        return
    expected = parse_dimensions(item.get("dimensions"))
    if expected and expected != (width, height):
        problems.error(f"{where}: dimensions {width}x{height} differ from manifest {expected[0]}x{expected[1]}")
    if not expected and item.get("merged_from"):
        problems.warn(f"{where}: no dimensions recorded (actual {width}x{height})")
    if needs_alpha(item) and not has_alpha:
        problems.error(f"{where}: expected an alpha channel (mode {mode})")
    if item.get("render_type") == "texture" and not (is_pow2(width) and is_pow2(height)):
        problems.warn(f"{where}: texture {width}x{height} is not a power of two (ASSET_CONTRACT 7)")
    if item.get("render_type") == "texture" and max(width, height) > 2048:
        problems.warn(f"{where}: texture larger than 2048 px")
    anim = item.get("animation")
    if isinstance(anim, dict) and ("columns" in anim or "rows" in anim):
        cols = int(anim.get("columns") or 1)
        rows = int(anim.get("rows") or 1)
        frames = int(anim.get("frames") or cols * rows)
        if cols <= 0 or rows <= 0:
            problems.error(f"{where}: animation columns/rows must be positive")
        else:
            if width % cols:
                problems.error(f"{where}: sheet width {width} not divisible by {cols} columns")
            if height % rows:
                problems.error(f"{where}: sheet height {height} not divisible by {rows} rows")
            if frames > cols * rows:
                problems.error(f"{where}: {frames} frames exceed {cols}x{rows} grid")
            fw, fh = width // cols, height // rows
            facts["frame_size"] = [fw, fh]
            if max(width, height) > 2048:
                problems.warn(f"{where}: sprite sheet larger than 2048 px")
            if not anim.get("fps"):
                problems.warn(f"{where}: animation has no fps")
            if has_alpha and cols * rows > 1:
                _check_frames_not_empty(full, cols, rows, frames, where, problems, facts)
    ns = item.get("nine_slice")
    if isinstance(ns, dict):
        try:
            left, right = int(ns.get("left", 0)), int(ns.get("right", 0))
            top, bottom = int(ns.get("top", 0)), int(ns.get("bottom", 0))
            if left + right >= width or top + bottom >= height:
                problems.error(f"{where}: 9-slice margins {ns} leave no centre in {width}x{height}")
        except (TypeError, ValueError):
            problems.error(f"{where}: nine_slice margins must be integers")


def _check_frames_not_empty(full: Path, cols: int, rows: int, frames: int, where: str, problems: Problems, facts: dict) -> None:
    from PIL import Image
    with Image.open(full) as img:
        alpha = img.convert("RGBA").getchannel("A")
        fw, fh = img.width // cols, img.height // rows
        empty = []
        edge_bleed = 0
        for i in range(frames):
            cx, cy = (i % cols) * fw, (i // cols) * fh
            cell = alpha.crop((cx, cy, cx + fw, cy + fh))
            if cell.getextrema()[1] == 0:
                empty.append(i)
            # 2 px margin rule: count frames whose border pixels are not transparent.
            border = [cell.crop((0, 0, fw, 2)), cell.crop((0, fh - 2, fw, fh)), cell.crop((0, 0, 2, fh)), cell.crop((fw - 2, 0, fw, fh))]
            if any(b.getextrema()[1] > 8 for b in border):
                edge_bleed += 1
        facts["empty_frames"] = empty
        if empty:
            problems.error(f"{where}: empty frames {empty[:8]}{'...' if len(empty) > 8 else ''}")
        if edge_bleed:
            problems.warn(f"{where}: {edge_bleed} frame(s) touch the 2 px frame margin (filter bleed risk)")


# ---------------------------------------------------------------- glTF

def read_gltf(full: Path) -> tuple[dict, bytes | None]:
    raw = full.read_bytes()
    if full.suffix.lower() == ".gltf":
        doc = json.loads(raw.decode("utf-8"))
        return doc, None
    if len(raw) < 20:
        raise ValueError("file too small for glb")
    magic, version, length = struct.unpack_from("<4sII", raw, 0)
    if magic != b"glTF":
        raise ValueError("bad glb magic")
    if version != 2:
        raise ValueError(f"glb version {version}, expected 2")
    if length != len(raw):
        raise ValueError(f"glb length header {length} != file size {len(raw)}")
    offset = 12
    doc = None
    binary = None
    while offset + 8 <= len(raw):
        chunk_len, chunk_type = struct.unpack_from("<II", raw, offset)
        data = raw[offset + 8: offset + 8 + chunk_len]
        if chunk_type == 0x4E4F534A:
            doc = json.loads(data.decode("utf-8"))
        elif chunk_type == 0x004E4942:
            binary = data
        offset += 8 + chunk_len
    if doc is None:
        raise ValueError("glb has no JSON chunk")
    return doc, binary


def mat_mul(a: list[float], b: list[float]) -> list[float]:
    # Column-major 4x4 like glTF.
    out = [0.0] * 16
    for c in range(4):
        for r in range(4):
            out[c * 4 + r] = sum(a[k * 4 + r] * b[c * 4 + k] for k in range(4))
    return out


def node_matrix(node: dict) -> list[float]:
    if "matrix" in node:
        return [float(v) for v in node["matrix"]]
    tx, ty, tz = node.get("translation", [0, 0, 0])
    qx, qy, qz, qw = node.get("rotation", [0, 0, 0, 1])
    sx, sy, sz = node.get("scale", [1, 1, 1])
    r = [
        1 - 2 * (qy * qy + qz * qz), 2 * (qx * qy + qz * qw), 2 * (qx * qz - qy * qw), 0,
        2 * (qx * qy - qz * qw), 1 - 2 * (qx * qx + qz * qz), 2 * (qy * qz + qx * qw), 0,
        2 * (qx * qz + qy * qw), 2 * (qy * qz - qx * qw), 1 - 2 * (qx * qx + qy * qy), 0,
        0, 0, 0, 1,
    ]
    s = [sx, 0, 0, 0, 0, sy, 0, 0, 0, 0, sz, 0, 0, 0, 0, 1]
    t = [1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, tx, ty, tz, 1]
    return mat_mul(t, mat_mul(r, s))


def transform_point(m: list[float], p: tuple[float, float, float]) -> tuple[float, float, float]:
    x, y, z = p
    return (
        m[0] * x + m[4] * y + m[8] * z + m[12],
        m[1] * x + m[5] * y + m[9] * z + m[13],
        m[2] * x + m[6] * y + m[10] * z + m[14],
    )


def gltf_facts(doc: dict, include_names: tuple[str, ...] = ()) -> dict:
    nodes = doc.get("nodes", [])
    meshes = doc.get("meshes", [])
    accessors = doc.get("accessors", [])
    materials = [m.get("name", f"material_{i}") for i, m in enumerate(doc.get("materials", []))]
    scenes = doc.get("scenes", [])
    scene_index = doc.get("scene", 0)
    roots = scenes[scene_index].get("nodes", []) if scenes else list(range(len(nodes)))
    tris_total = 0
    per_node_tris: dict[str, int] = {}
    lo = [math.inf] * 3
    hi = [-math.inf] * 3
    lo_named = {name: [math.inf] * 3 for name in include_names}
    hi_named = {name: [-math.inf] * 3 for name in include_names}
    node_names: list[str] = []

    def mesh_tris(mesh: dict) -> int:
        count = 0
        for prim in mesh.get("primitives", []):
            mode = prim.get("mode", 4)
            if "indices" in prim:
                n = accessors[prim["indices"]]["count"]
            else:
                n = accessors[prim["attributes"]["POSITION"]]["count"]
            if mode == 4:
                count += n // 3
            elif mode in (5, 6):
                count += max(0, n - 2)
        return count

    def visit(index: int, parent: list[float], top: str | None) -> None:
        node = nodes[index]
        name = node.get("name", f"node_{index}")
        node_names.append(name)
        m = mat_mul(parent, node_matrix(node))
        group = top
        if name in include_names:
            group = name
        if "mesh" in node:
            mesh = meshes[node["mesh"]]
            t = mesh_tris(mesh)
            tris_total_add(t)
            per_node_tris[name] = per_node_tris.get(name, 0) + t
            for prim in mesh.get("primitives", []):
                acc = accessors[prim["attributes"]["POSITION"]]
                mn, mx = acc.get("min"), acc.get("max")
                if not mn or not mx:
                    continue
                for cx in (mn[0], mx[0]):
                    for cy in (mn[1], mx[1]):
                        for cz in (mn[2], mx[2]):
                            p = transform_point(m, (cx, cy, cz))
                            for k in range(3):
                                lo[k] = min(lo[k], p[k])
                                hi[k] = max(hi[k], p[k])
                                if group in lo_named:
                                    lo_named[group][k] = min(lo_named[group][k], p[k])
                                    hi_named[group][k] = max(hi_named[group][k], p[k])
        for child in node.get("children", []):
            visit(child, m, group)

    totals = {"tris": 0}

    def tris_total_add(t: int) -> None:
        totals["tris"] += t

    identity = [1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1]
    for root in roots:
        visit(root, identity, None)
    tris_total = totals["tris"]
    bounds = None if lo[0] == math.inf else {"min": [round(v, 4) for v in lo], "max": [round(v, 4) for v in hi]}
    named = {}
    for name in include_names:
        if lo_named[name][0] != math.inf:
            named[name] = {"min": [round(v, 4) for v in lo_named[name]], "max": [round(v, 4) for v in hi_named[name]]}
    return {
        "nodes": len(nodes),
        "node_names": node_names,
        "root_nodes": [nodes[i].get("name", f"node_{i}") for i in roots],
        "meshes": len(meshes),
        "materials": materials,
        "tris": tris_total,
        "tris_per_node": per_node_tris,
        "bounds": bounds,
        "named_bounds": named,
        "images": len(doc.get("images", [])),
        "animations": [a.get("name", f"anim_{i}") for i, a in enumerate(doc.get("animations", []))],
        "skins": len(doc.get("skins", [])),
    }


def check_mesh(item: dict, full: Path, where: str, problems: Problems, facts: dict) -> None:
    try:
        doc, _binary = read_gltf(full)
    except Exception as exc:  # noqa: BLE001
        problems.error(f"{where}: cannot parse glTF: {exc}")
        return
    asset = doc.get("asset", {})
    if str(asset.get("version")) != "2.0":
        problems.error(f"{where}: glTF asset.version {asset.get('version')!r}, expected 2.0")
    try:
        info = gltf_facts(doc, ("mesh_intact", "mesh_light", "mesh_heavy"))
    except (KeyError, IndexError, TypeError) as exc:
        problems.error(f"{where}: malformed glTF structure: {exc}")
        return
    facts.update({k: v for k, v in info.items() if k != "node_names"})
    if info["meshes"] == 0:
        problems.error(f"{where}: glTF contains no meshes")
        return
    if info["bounds"] is None:
        problems.error(f"{where}: no POSITION min/max, cannot compute bounds")
        return
    if doc.get("cameras") or (doc.get("extensions", {}) or {}).get("KHR_lights_punctual"):
        problems.warn(f"{where}: kit file contains cameras or lights (ASSET_CONTRACT 2)")
    for name in info["materials"]:
        if not MATERIAL_NAME_RE.match(name):
            problems.warn(f"{where}: material slot {name!r} does not follow mat_/trim_/emit_/glass_ naming (ASSET_CONTRACT 7)")
    mats = doc.get("materials", [])
    vc_slots = sorted({
        mats[prim["material"]].get("name", "")
        for mesh in doc.get("meshes", []) for prim in mesh.get("primitives", [])
        if "COLOR_0" in prim.get("attributes", {}) and isinstance(prim.get("material"), int)
        and prim["material"] < len(mats) and str(mats[prim["material"]].get("name", "")).startswith(("mat_", "trim_"))
    })
    if vc_slots:
        problems.warn(f"{where}: COLOR_0 vertex colours on {', '.join(vc_slots)}; Godot 4.7 import does not reliably use them as albedo, "
                      "so bake the intended colour into baseColorFactor or an albedo texture (ASSET_CONTRACT 7)")
    if item.get("tris") is not None and int(item["tris"]) != info["tris"]:
        problems.warn(f"{where}: manifest tris {item['tris']} differ from file {info['tris']}")

    is_component = item.get("category") == "destructibles" and item.get("component_kind") and "-DEB-" not in str(item.get("id", ""))
    hero = bool(item.get("critical") or str(item.get("component_kind", "")).endswith("_core"))
    budget = TRIS_HERO if hero else TRIS_STANDARD
    if is_component:
        intact_tris = info["tris_per_node"].get("mesh_intact", info["tris"])
        if intact_tris > budget:
            problems.warn(f"{where}: {intact_tris} tris over the {budget} budget (ASSET_CONTRACT 12)")
        if "mesh_intact" not in info["node_names"]:
            problems.warn(f"{where}: no node named mesh_intact (ASSET_CONTRACT 6)")
        b = info["named_bounds"].get("mesh_intact") or info["bounds"]
        lo, hi = b["min"], b["max"]
        cx, cy, cz = [(lo[k] + hi[k]) / 2 for k in range(3)]
        size = [hi[k] - lo[k] for k in range(3)]
        facts["intact_size_m"] = [round(v, 4) for v in size]
        if abs(cx) > ORIGIN_TOL or abs(cy) > ORIGIN_TOL:
            problems.error(f"{where}: origin not at the rectangle centre (bounds centre x={cx:.3f}, y={cy:.3f}) (ASSET_CONTRACT 4)")
        if abs(cz) > ORIGIN_TOL + 0.05:
            problems.warn(f"{where}: depth not centred on z = 0 (centre z={cz:.3f}) (ASSET_CONTRACT 3)")
        for alt in ("mesh_light", "mesh_heavy"):
            ab = info["named_bounds"].get(alt)
            if ab:
                over = max(max(lo[k] - ab["min"][k], ab["max"][k] - hi[k]) for k in range(3))
                if over > DAMAGE_BULGE_TOL:
                    problems.warn(f"{where}: {alt} reaches {over:.3f} m outside mesh_intact bounds (limit {DAMAGE_BULGE_TOL} m, ASSET_CONTRACT 8)")
        ref = item.get("reference_size_px")
        if isinstance(ref, (list, tuple)) and len(ref) == 2:
            w, h = ref[0] / PX_PER_METRE, ref[1] / PX_PER_METRE
            if size[0] > w + 2 * SILHOUETTE_TOL or size[1] > h + 2 * SILHOUETTE_TOL:
                problems.error(f"{where}: front silhouette {size[0]:.3f}x{size[1]:.3f} m exceeds collision rectangle {w:.2f}x{h:.2f} m")
            if size[0] < w * 0.85 or size[1] < h * 0.85:
                problems.warn(f"{where}: silhouette {size[0]:.3f}x{size[1]:.3f} m is much smaller than the rectangle {w:.2f}x{h:.2f} m")
        else:
            problems.warn(f"{where}: component without reference_size_px (ASSET_CONTRACT 5)")
        depth = item.get("depth_m") or CODE_KIND_DEPTH.get(item.get("component_kind"))
        if depth:
            if size[2] > depth + 0.02:
                problems.error(f"{where}: depth {size[2]:.3f} m exceeds kind depth {depth} m")
            code_depth = CODE_KIND_DEPTH.get(item.get("component_kind"))
            if code_depth and item.get("depth_m") and abs(item["depth_m"] - code_depth) > 1e-6:
                problems.warn(f"{where}: depth_m {item['depth_m']} differs from MissionView depth {code_depth}")
    elif info["tris"] > 20000:
        problems.warn(f"{where}: {info['tris']} tris is heavy for mobile")


# ---------------------------------------------------------------- audio, video, fonts

def probe_audio(full: Path) -> dict:
    try:
        import soundfile as sf  # type: ignore
        info = sf.info(str(full))
        return {"duration": info.frames / info.samplerate, "sample_rate": info.samplerate, "channels": info.channels, "via": "soundfile"}
    except Exception:  # noqa: BLE001
        pass
    return probe_ffprobe(full)


def probe_ffprobe(full: Path) -> dict:
    if not shutil.which("ffprobe"):
        raise RuntimeError("neither soundfile nor ffprobe could read the file")
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration:stream=sample_rate,channels,codec_type,width,height,r_frame_rate",
         "-of", "json", str(full)], capture_output=True, text=True, check=True).stdout
    data = json.loads(out)
    res = {"duration": float(data.get("format", {}).get("duration", 0.0)), "via": "ffprobe"}
    for s in data.get("streams", []):
        if s.get("codec_type") == "audio":
            res["sample_rate"] = int(s.get("sample_rate", 0))
            res["channels"] = int(s.get("channels", 0))
        if s.get("codec_type") == "video":
            res["width"], res["height"] = s.get("width"), s.get("height")
            res["fps"] = s.get("r_frame_rate")
    return res


def loudness(full: Path) -> dict | None:
    if not shutil.which("ffmpeg"):
        return None
    proc = subprocess.run(["ffmpeg", "-nostats", "-hide_banner", "-i", str(full), "-af", "ebur128=peak=true", "-f", "null", "-"],
                          capture_output=True, text=True)
    text = proc.stderr
    i = re.findall(r"I:\s+(-?[\d.]+) LUFS", text)
    tp = re.findall(r"Peak:\s+(-?[\d.]+) dBFS", text)
    return {"integrated_lufs": float(i[-1]) if i else None, "true_peak_dbfs": float(tp[-1]) if tp else None}


def check_audio(item: dict, full: Path, where: str, problems: Problems, facts: dict, do_loudness: bool) -> None:
    try:
        info = probe_audio(full)
    except Exception as exc:  # noqa: BLE001
        problems.error(f"{where}: cannot read audio: {exc}")
        return
    facts.update({k: (round(v, 3) if isinstance(v, float) else v) for k, v in info.items()})
    dur = info.get("duration", 0.0)
    if dur <= 0:
        problems.error(f"{where}: zero-length audio")
    expected = item.get("duration_seconds")
    if isinstance(expected, (int, float)):
        if abs(expected - dur) > max(0.1, 0.01 * dur):
            problems.error(f"{where}: duration {dur:.2f} s differs from manifest {expected} s")
    elif item.get("merged_from"):
        problems.warn(f"{where}: no duration_seconds recorded (actual {dur:.2f} s)")
    sr = item.get("sample_rate")
    if sr and info.get("sample_rate") and int(sr) != int(info["sample_rate"]):
        problems.error(f"{where}: sample rate {info['sample_rate']} differs from manifest {sr}")
    if info.get("sample_rate") and info["sample_rate"] not in (22050, 32000, 44100, 48000):
        problems.warn(f"{where}: unusual sample rate {info['sample_rate']}")
    ch = item.get("channels")
    if ch and info.get("channels") and int(ch) != int(info["channels"]):
        problems.error(f"{where}: channels {info['channels']} differ from manifest {ch}")
    if do_loudness:
        lu = loudness(full)
        if lu:
            facts.update(lu)


def check_video(item: dict, full: Path, where: str, problems: Problems, facts: dict) -> None:
    try:
        info = probe_ffprobe(full)
    except Exception as exc:  # noqa: BLE001
        problems.error(f"{where}: cannot read video: {exc}")
        return
    facts.update(info)
    expected = item.get("duration_seconds")
    if isinstance(expected, (int, float)) and abs(expected - info["duration"]) > max(0.1, 0.02 * info["duration"]):
        problems.error(f"{where}: duration {info['duration']:.2f} s differs from manifest {expected} s")


FONT_MAGIC = {b"\x00\x01\x00\x00", b"OTTO", b"true", b"wOF2", b"wOFF", b"ttcf"}


def check_font(item: dict, full: Path, where: str, problems: Problems, facts: dict) -> None:
    head = full.read_bytes()[:4]
    if head not in FONT_MAGIC:
        problems.error(f"{where}: not a TrueType/OpenType/WOFF font (magic {head!r})")
    folder = full.parent
    licences = [p.name for p in folder.iterdir() if re.match(r"(?i)^(ofl|license|licence|copying)", p.name)]
    if not licences and folder.parent != folder:
        licences = [p.name for p in folder.parent.iterdir() if re.match(r"(?i)^(ofl|license|licence)", p.name)]
    facts["licence_files"] = licences
    if not licences:
        problems.error(f"{where}: no licence file (OFL.txt or LICENSE) beside the font")


# ---------------------------------------------------------------- deep checks driver

def deep_checks(data: dict, problems: Problems, do_loudness: bool) -> dict:
    per_entry: dict[str, dict] = {}
    for index, item in enumerate(data.get("entries", [])):
        if not isinstance(item, dict) or not item.get("path"):
            continue
        full = REPO_ROOT / item["path"]
        if not full.is_file():
            continue
        where = f"{item.get('id', '?')} ({item.get('merged_from') or 'base'})"
        ext = full.suffix.lower().lstrip(".")
        facts: dict = {"bytes": full.stat().st_size}
        fmt = str(item.get("format", "")).lower()
        if fmt and fmt not in (ext, "jpeg" if ext == "jpg" else ext) and not (fmt == "jpg" and ext == "jpeg"):
            problems.warn(f"{where}: format {fmt!r} but file extension .{ext}")
        if ext in IMAGE_EXT:
            check_image(item, full, where, problems, facts)
        elif ext in MESH_EXT:
            check_mesh(item, full, where, problems, facts)
        elif ext in AUDIO_EXT:
            check_audio(item, full, where, problems, facts, do_loudness)
        elif ext in VIDEO_EXT:
            check_video(item, full, where, problems, facts)
        elif ext in FONT_EXT:
            check_font(item, full, where, problems, facts)
        per_entry[item.get("id", f"entry_{index}")] = facts
    return per_entry


def summary(data: dict, per_entry: dict) -> dict:
    by_cat: dict[str, int] = {}
    by_stream: dict[str, int] = {}
    total = 0
    for item in data.get("entries", []):
        if not isinstance(item, dict):
            continue
        by_cat[item.get("category", "?")] = by_cat.get(item.get("category", "?"), 0) + 1
        src = item.get("merged_from") or "base"
        by_stream[src] = by_stream.get(src, 0) + 1
        total += per_entry.get(item.get("id"), {}).get("bytes", 0)
    return {"by_category": dict(sorted(by_cat.items())), "by_stream": dict(sorted(by_stream.items())), "bytes": total}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--merge", action="store_true", help="write merged fragments into asset_manifest.json")
    parser.add_argument("--check", action="store_true", help="fail if asset_manifest.json is not up to date with fragments")
    parser.add_argument("--report", type=Path, help="write a JSON report")
    parser.add_argument("--loudness", action="store_true", help="measure audio loudness with ffmpeg")
    parser.add_argument("--strict", action="store_true", help="warnings fail too")
    parser.add_argument("--quiet", action="store_true", help="print only the summary and failures")
    args = parser.parse_args()

    problems = Problems()
    base = load_json(MANIFEST, problems)
    if not isinstance(base, dict):
        for m in problems.errors:
            print(f"FAIL: {m}", file=sys.stderr)
        return 1
    fragments = load_fragments(problems)
    base_ids = {e.get("id") for e in base.get("entries", []) if isinstance(e, dict) and not e.get("merged_from")}
    for stream, path, entries in fragments:
        for e in entries:
            if isinstance(e, dict) and e.get("id") in base_ids:
                problems.error(f"{rel(path)}: id {e.get('id')!r} shadows a base-owned entry")
    data = merged_manifest(base, fragments)

    check_structure(data, problems)
    per_entry = deep_checks(data, problems, args.loudness)
    summ = summary(data, per_entry)

    if args.check:
        current = json.dumps(base, sort_keys=True)
        fresh = json.dumps(data, sort_keys=True)
        if current != fresh:
            problems.error("asset_manifest.json is out of date with manifest_parts (run with --merge)")

    entries = [e for e in data.get("entries", []) if isinstance(e, dict)]
    print(f"fragments: {len(fragments)} ({', '.join(f'{s}={len(e)}' for s, _p, e in fragments) or 'none'})")
    print(f"entries: {len(entries)} checked, {sum(1 for e in entries if e.get('path') and (REPO_ROOT / e['path']).is_file())} present, {summ['bytes'] / 1e6:.1f} MB")
    print(f"by category: {summ['by_category']}")
    print(f"planned: {len(data.get('planned', []))} listed")
    if not args.quiet:
        for m in problems.warnings:
            print(f"WARN: {m}")
    else:
        print(f"warnings: {len(problems.warnings)}")

    if args.report:
        report = {"summary": summ, "errors": problems.errors, "warnings": problems.warnings, "entries": per_entry}
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(report, indent=1, sort_keys=True) + "\n", encoding="utf-8")

    failed = bool(problems.errors) or (args.strict and problems.warnings)
    if problems.errors:
        for m in problems.errors:
            print(f"FAIL: {m}", file=sys.stderr)
        print(f"FAIL: {len(problems.errors)} problem(s)", file=sys.stderr)
    if args.merge and not problems.errors:
        data["updated"] = __import__("datetime").date.today().isoformat()
        MANIFEST.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print(f"merged {sum(len(e) for _s, _p, e in fragments)} fragment entries into {rel(MANIFEST)}")
    elif args.merge:
        print("not merged: fix the failures first", file=sys.stderr)
    if failed:
        return 1
    print("PASS: structure, ids, paths and deep file checks valid")
    return 0


if __name__ == "__main__":
    sys.exit(main())
