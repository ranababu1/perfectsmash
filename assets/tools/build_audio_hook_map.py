#!/usr/bin/env python3
"""Map the game's sound and music ids (data/audio.json on main) to delivered audio files.

Reads data/audio.json and the merged assets/asset_manifest.json and writes
assets/docs/audio_hook_map.json and .md: for every code sound id, the manifest
entries whose `sound_id` matches (or a documented stand-in), ready-to-paste `files` lists of
res:// paths, music cues, ambience cues the code does not have yet, and delivered sound ids the
code does not use. Proposal only: data/audio.json stays untouched until the owner approves the
assets and their licence records. Usage: python3 assets/tools/build_audio_hook_map.py [--check]
"""
from __future__ import annotations

import collections
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CODE = ROOT / "data" / "audio.json"
MANIFEST = ROOT / "assets" / "asset_manifest.json"
OUT_JSON = ROOT / "assets" / "docs" / "audio_hook_map.json"
OUT_MD = ROOT / "assets" / "docs" / "audio_hook_map.md"

# Code ids with no delivered sound_id of their own, and the delivered ids that can stand in.
STAND_INS = {"impact_generic": ["impact_composite", "impact_concrete"]}
# Delivered sound ids that would let impact_by_material be more specific (proposed code change).
PROPOSED_IMPACT_BY_MATERIAL = {"composite": "impact_composite", "concrete": "impact_concrete"}
CHAPTER_CODES = ["HLX", "VTA", "NVG", "CVT", "MRD"]


def main() -> int:
    check = "--check" in sys.argv
    code = json.loads(CODE.read_text())
    manifest = json.loads(MANIFEST.read_text())
    audio = [e for e in manifest.get("entries", []) if e.get("category") in ("audio", "music")]
    by_sound = collections.defaultdict(list)
    by_music = collections.defaultdict(list)
    by_amb = collections.defaultdict(list)
    for e in audio:
        if e.get("sound_id"):
            by_sound[e["sound_id"]].append(e)
        if e.get("music_cue"):
            by_music[e["music_cue"]].append(e)
        if e.get("ambience_cue"):
            by_amb[e["ambience_cue"]].append(e)

    # Files data/audio.json already wires directly (code-side integration), by repo path.
    by_path = {e["path"]: e for e in manifest.get("entries", [])}

    def wired(paths):
        return sorted((by_path[p[len("res://"):]] for p in paths if p.startswith("res://") and p[len("res://"):] in by_path), key=lambda e: e["id"])

    sounds = []
    for sid, spec in code.get("sounds", {}).items():
        own = sorted(by_sound.get(sid, []), key=lambda e: e["id"])
        via = []
        entries = own
        if not own and sid in STAND_INS:
            via = STAND_INS[sid]
            entries = sorted([e for s in via for e in by_sound.get(s, [])], key=lambda e: e["id"])
        code_wired = [] if own or entries else wired(spec.get("files", []))
        if code_wired:
            entries = code_wired
        row = {
            "sound_id": sid,
            "fallback": spec.get("fallback", ""),
            "status": "delivered" if own else ("stand_in" if via and entries else ("wired_in_code" if code_wired else "missing")),
            "stand_in_ids": via,
            "files": ["res://" + e["path"] for e in entries],
            "asset_ids": [e["id"] for e in entries],
            "pending_approval": sum(1 for e in entries if e.get("approval_status") != "approved"),
        }
        chapters = {c: [e["id"] for e in entries if e["id"].startswith(c + "-")] for c in CHAPTER_CODES}
        if any(chapters.values()):
            row["per_chapter"] = {c: v for c, v in chapters.items() if v}
        sounds.append(row)

    music = []
    for cue, spec in code.get("music", {}).items():
        files = sorted(by_music.get(cue, []), key=lambda e: e["id"])
        status = "delivered" if files else "missing"
        if not files and spec.get("file"):
            files = wired([spec["file"]])
            status = "wired_in_code" if files else "code_file_only"
        music.append({"music_cue": cue, "code_file": spec.get("file", ""),
                      "status": status,
                      "files": ["res://" + e["path"] for e in files], "asset_ids": [e["id"] for e in files]})
    new_music = sorted(c for c in by_music if c not in code.get("music", {}))
    ambience = [{"ambience_cue": cue, "files": ["res://" + e["path"] for e in sorted(v, key=lambda e: e["id"])],
                 "asset_ids": [e["id"] for e in sorted(v, key=lambda e: e["id"])]} for cue, v in sorted(by_amb.items())]
    extra = sorted(s for s in by_sound if s not in code.get("sounds", {}))
    unhooked = sorted(e["id"] for e in audio if not (e.get("sound_id") or e.get("music_cue") or e.get("ambience_cue")))

    data = {
        "generated_from": {"code": "data/audio.json", "manifest_updated": manifest.get("updated", "")},
        "note": "Proposal for the coding agent. Paste a row's files into data/audio.json only after the owner approves the assets and their licence records.",
        "sounds": sounds,
        "music": music,
        "music_cues_delivered_not_in_code": new_music,
        "ambience_cues_not_in_code": ambience,
        "sound_ids_delivered_not_in_code": {s: [e["id"] for e in by_sound[s]] for s in extra},
        "proposed_impact_by_material": {m: s for m, s in PROPOSED_IMPACT_BY_MATERIAL.items() if by_sound.get(s)},
        "audio_entries_without_hook_id": unhooked,
    }
    text_json = json.dumps(data, indent=1) + "\n"

    n_del = sum(1 for s in sounds if s["status"] in ("delivered", "wired_in_code"))
    n_si = sum(1 for s in sounds if s["status"] == "stand_in")
    md = ["# Audio hook map (code sound ids to delivered files)", "",
          f"Generated by `assets/tools/build_audio_hook_map.py` from `data/audio.json` and the merged manifest (updated {manifest.get('updated', '')}). Do not edit by hand. Owner approval for integration: 2026-11-10. `wired_in_code` means `data/audio.json` already lists the delivered files itself.", "",
          f"- Code sound ids: {len(sounds)}; with delivered files: {n_del}; covered by a stand-in: {n_si}; missing: {len(sounds) - n_del - n_si}.",
          f"- Music cues in code: {len(music)}; delivered or wired in code: {sum(1 for m in music if m['status'] in ('delivered', 'wired_in_code'))}. Ambience cues delivered (no ambience hook in code yet): {len(ambience)}.",
          f"- Audio entries with no hook id: {len(unhooked)} (layers and variants for future hooks).", "",
          "| Code sound id | Procedural fallback | Status | Files | Assets |", "|---|---|---|---:|---|"]
    for s in sounds:
        status = s["status"] + (f" ({', '.join(s['stand_in_ids'])})" if s["stand_in_ids"] else "")
        md.append(f"| `{s['sound_id']}` | {s['fallback']} | {status} | {len(s['files'])} | {', '.join(s['asset_ids'][:4])}{' ...' if len(s['asset_ids']) > 4 else ''} |")
    md += ["", "| Music cue | Code file | Status | Delivered |", "|---|---|---|---|"]
    for m in music:
        md.append(f"| `{m['music_cue']}` | {m['code_file'] or '-'} | {m['status']} | {', '.join(m['asset_ids']) or '-'} |")
    if new_music:
        md += ["", "Music cues delivered but not in code: " + ", ".join(f"`{c}`" for c in new_music) + "."]
    md += ["", "Ambience cues delivered (proposed new `ambience` block in `data/audio.json`): " + ", ".join(f"`{a['ambience_cue']}`" for a in ambience) + "."]
    if extra:
        md += ["", "Sound ids delivered but not used by code yet: " + ", ".join(f"`{s}` ({len(by_sound[s])})" for s in extra) + "."]
    per = [s for s in sounds if len(s.get("per_chapter", {})) > 1]
    for s in per:
        md += ["", f"`{s['sound_id']}` has chapter-specific variants ({', '.join(f'{c} {len(v)}' for c, v in s['per_chapter'].items())}); the code plays one id everywhere, so either pick per chapter (proposed: `{s['sound_id']}_<chapter>` ids) or use all variants as one pool."]
    if data["proposed_impact_by_material"]:
        md += ["", "Proposed `impact_by_material` refinement: " + ", ".join(f"`{m}` -> `{s}`" for m, s in data["proposed_impact_by_material"].items()) + " (code maps both to `impact_generic` today)."]
    text_md = "\n".join(md) + "\n"

    if check:
        ok = OUT_JSON.exists() and OUT_JSON.read_text() == text_json and OUT_MD.exists() and OUT_MD.read_text() == text_md
        print("PASS: audio hook map current" if ok else "FAIL: audio hook map out of date")
        return 0 if ok else 1
    OUT_JSON.write_text(text_json)
    OUT_MD.write_text(text_md)
    print(f"audio hooks: {len(sounds)} code ids, {n_del} delivered, {n_si} stand-in, {len(sounds) - n_del - n_si} missing; music {len(music)} cues; ambience {len(ambience)} cues; extra ids {len(extra)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
