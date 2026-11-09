#!/usr/bin/env python3
"""Build the 100-level asset coverage matrix from the merged manifest.

Inputs:
  docs/level-design-spec.md                 level numbers, names, puzzle notes, shot budgets (parsed)
  generated_assets/asset_manifest.json      merged manifest (run validate_asset_manifest.py --merge first)
  this file                                 level archetypes, chapter role->kind tables, landmark props,
                                            music/ambience/cinematic/VFX requirements (the design layer)
Outputs:
  generated_assets/docs/coverage_matrix.json
  generated_assets/docs/coverage_matrix.md

Every requirement is resolved against the manifest at run time, so re-running after streams push
updates availability automatically. Status per requirement:
  available  a matching manifest entry exists (file validated by the manifest validator)
  fallback   only a shared/generic substitute exists (playable, less chapter identity)
  missing    nothing in the manifest matches yet
A level is "fully covered" when every hard requirement is available, "covered with fallbacks" when
nothing is missing but some use fallbacks, otherwise "missing".

Usage: python3 generated_assets/tools/build_coverage_matrix.py [--check]
"""

from __future__ import annotations

import argparse
import datetime
import json
import re
import sys
from pathlib import Path

SCRIPT = Path(__file__).resolve()
GEN = SCRIPT.parents[1]
REPO = SCRIPT.parents[2]
MANIFEST = GEN / "asset_manifest.json"
SPEC = REPO / "docs" / "level-design-spec.md"
NARRATIVE = REPO / "docs" / "narrative-bible.md"
OUT_JSON = GEN / "docs" / "coverage_matrix.json"
OUT_MD = GEN / "docs" / "coverage_matrix.md"

CHAPTERS = [
    # key, code, number, organisation, first level, title
    ("helix", "HLX", 1, "Helix Systems", 1, "The Machine That Decided"),
    ("vita", "VTA", 2, "VITA Genomics", 21, "The Price of Perfection"),
    ("nova_grid", "NVG", 3, "Nova Grid", 41, "The Energy Beneath"),
    ("civitas", "CVT", 4, "Civitas", 61, "The Quiet Cage"),
    ("meridian", "MRD", 5, "Meridian", 81, "The Convergence"),
]

# Structural roles -> chapter component kind (ASSET_CONTRACT section 5). "SHR:" = shared generic kind.
ROLE_KIND = {
    "helix": {"column": "support_column", "deck": "service_deck", "rack": "server_rack", "shield": "core_shield",
              "wall": "blast_wall", "glass": "control_pod_glass", "cap": "SHR:generic_block_concrete",
              "crate": "data_crate", "cell": "power_cell", "mast": "relay_mast", "dish": "relay_dish",
              "core": "ai_core", "ring": "logistics_gantry", "tower": "cooling_stack"},
    "vita": {"column": "lab_column", "deck": "lab_deck", "rack": "specimen_rack", "shield": "SHR:generic_block_steel",
             "wall": "containment_cap", "glass": "cleanroom_panel", "cap": "containment_cap",
             "crate": "SHR:generic_block_alloy", "cell": "cryo_cell", "mast": "lab_column", "dish": "bioreactor",
             "core": "gene_vault_core", "ring": "bioreactor", "tower": "bioreactor"},
    "nova_grid": {"column": "grid_pylon", "deck": "cable_bridge", "rack": "transformer", "shield": "containment_wall",
                  "wall": "containment_wall", "glass": "SHR:generic_panel_glass", "cap": "SHR:generic_block_concrete",
                  "crate": "SHR:generic_block_steel", "cell": "capacitor_cell", "mast": "grid_pylon",
                  "dish": "cooling_tower_segment", "core": "reactor_core", "ring": "containment_ring_segment",
                  "tower": "cooling_tower_segment"},
    "civitas": {"column": "civic_column", "deck": "relay_bridge", "rack": "data_exchange_rack", "shield": "security_wall",
                "wall": "security_wall", "glass": "civic_screen", "cap": "SHR:generic_block_concrete",
                "crate": "SHR:generic_block_alloy", "cell": "data_exchange_rack", "mast": "sensor_mast",
                "dish": "sensor_array", "core": "surveillance_core", "ring": "relay_bridge", "tower": "sensor_mast"},
    "meridian": {"column": "anchor_column", "deck": "convergence_deck", "rack": "quantum_stabilizer",
                 "shield": "monolith_slab", "wall": "monolith_slab", "glass": "phase_shield", "cap": "monolith_slab",
                 "crate": "SHR:generic_block_steel", "cell": "temporal_cell", "mast": "timeline_relay",
                 "dish": "phase_shield", "core": "convergence_core", "ring": "timeline_relay", "tower": "anchor_column"},
}
# Physics material per kind (ASSET_CONTRACT section 5, data/materials.json ids).
KIND_MATERIAL = {
    "server_rack": "electronic_module", "support_column": "lightweight_alloy", "service_deck": "composite",
    "ai_core": "ai_core_module", "core_shield": "reinforced_steel", "power_cell": "energy_component",
    "blast_wall": "reinforced_steel", "relay_mast": "lightweight_alloy", "relay_dish": "glass_polymer",
    "control_pod_glass": "glass_polymer", "logistics_gantry": "lightweight_alloy", "cooling_stack": "composite",
    "data_crate": "composite",
    "lab_column": "lightweight_alloy", "lab_deck": "composite", "cleanroom_panel": "glass_polymer",
    "specimen_rack": "electronic_module", "bioreactor": "glass_polymer", "containment_cap": "concrete",
    "cryo_cell": "energy_component", "gene_vault_core": "ai_core_module",
    "grid_pylon": "reinforced_steel", "cable_bridge": "composite", "transformer": "electronic_module",
    "cooling_tower_segment": "concrete", "containment_ring_segment": "reinforced_steel",
    "capacitor_cell": "energy_component", "containment_wall": "concrete", "reactor_core": "energy_component",
    "civic_column": "concrete", "relay_bridge": "composite", "sensor_mast": "lightweight_alloy",
    "sensor_array": "glass_polymer", "civic_screen": "glass_polymer", "data_exchange_rack": "electronic_module",
    "security_wall": "reinforced_steel", "surveillance_core": "ai_core_module",
    "anchor_column": "reinforced_steel", "convergence_deck": "composite", "phase_shield": "glass_polymer",
    "quantum_stabilizer": "electronic_module", "temporal_cell": "energy_component", "monolith_slab": "concrete",
    "timeline_relay": "lightweight_alloy", "convergence_core": "energy_component",
    "generic_block_alloy": "lightweight_alloy", "generic_block_steel": "reinforced_steel",
    "generic_block_concrete": "concrete", "generic_panel_glass": "glass_polymer", "generic_beam_composite": "composite",
}
# Shared fallback kind per physics material.
GENERIC_FOR_MATERIAL = {
    "lightweight_alloy": "generic_block_alloy", "reinforced_steel": "generic_block_steel", "concrete": "generic_block_concrete",
    "glass_polymer": "generic_panel_glass", "composite": "generic_beam_composite",
    "electronic_module": "generic_block_alloy", "energy_component": "generic_block_alloy",
    "ai_core_module": "generic_block_alloy",
}
# Physics materials without their own texture set or damage overlay yet borrow a related one
# (counted as fallback): the critical core housing reads as an electronic module.
MATERIAL_FALLBACK = {"ai_core_module": "electronic_module"}

ARCHETYPE_ROLES = {
    "exposed_target": ["deck", "core"],
    "tall_mast": ["mast", "dish", "core"],
    "support_bridge": ["column", "deck", "core"],
    "stack_tower": ["crate", "rack", "core"],
    "glass_screen": ["glass", "column", "deck", "core"],
    "chain_towers": ["rack", "column", "core"],
    "heavy_cap": ["cap", "column", "core"],
    "domino_row": ["column", "deck", "core"],
    "topple_line": ["crate", "column", "deck"],
    "twin_towers": ["rack", "column", "deck", "core"],
    "arc_over_wall": ["static", "wall", "deck", "core"],
    "pyramid": ["crate", "deck", "core"],
    "glass_roof": ["glass", "column", "core"],
    "indirect_shield": ["shield", "column", "crate", "core"],
    "ledges": ["static", "crate", "core"],
    "linked_bridge": ["column", "deck", "mast", "core"],
    "multi_tier": ["column", "deck", "rack", "core"],
    "frame": ["column", "deck", "shield", "core"],
    "ring": ["ring", "column", "deck", "core"],
    "wide_platform": ["deck", "rack", "column", "mast", "core"],
    "mixed_material": ["crate", "glass", "cap", "column", "core"],
    "chain_cell": ["cell"],
    "finale": ["column", "deck", "rack", "shield", "wall", "glass", "cell", "mast", "dish", "tower", "core"],
}

# Level -> archetypes, from the puzzle notes in docs/level-design-spec.md section 4.
LEVEL_ARCHETYPES = {
    1: ["exposed_target"], 2: ["tall_mast"], 3: ["support_bridge"], 4: ["stack_tower"], 5: ["glass_screen"],
    6: ["chain_towers", "chain_cell"], 7: ["heavy_cap"], 8: ["domino_row"], 9: ["topple_line"], 10: ["twin_towers"],
    11: ["arc_over_wall"], 12: ["pyramid"], 13: ["glass_roof"], 14: ["indirect_shield"], 15: ["twin_towers", "glass_screen"],
    16: ["ledges"], 17: ["topple_line"], 18: ["arc_over_wall"], 19: ["domino_row", "ledges", "chain_cell"], 20: ["finale"],
    21: ["glass_screen"], 22: ["glass_screen", "chain_towers"], 23: ["stack_tower"], 24: ["heavy_cap", "glass_roof"], 25: ["twin_towers"],
    26: ["multi_tier"], 27: ["support_bridge", "heavy_cap"], 28: ["indirect_shield"], 29: ["linked_bridge", "chain_cell"], 30: ["glass_screen"],
    31: ["arc_over_wall"], 32: ["heavy_cap"], 33: ["mixed_material"], 34: ["heavy_cap"], 35: ["frame"],
    36: ["glass_roof", "arc_over_wall"], 37: ["multi_tier"], 38: ["twin_towers"], 39: ["linked_bridge", "chain_cell"], 40: ["finale"],
    41: ["support_bridge"], 42: ["frame"], 43: ["ring"], 44: ["chain_towers"], 45: ["arc_over_wall"],
    46: ["support_bridge"], 47: ["stack_tower"], 48: ["linked_bridge", "chain_cell"], 49: ["mixed_material"], 50: ["ring", "chain_cell"],
    51: ["arc_over_wall"], 52: ["ledges", "twin_towers"], 53: ["heavy_cap"], 54: ["linked_bridge"], 55: ["domino_row", "multi_tier", "chain_cell"],
    56: ["glass_roof", "arc_over_wall"], 57: ["indirect_shield"], 58: ["frame"], 59: ["wide_platform", "chain_cell"], 60: ["finale", "ring"],
    61: ["tall_mast"], 62: ["tall_mast"], 63: ["arc_over_wall"], 64: ["glass_screen"], 65: ["domino_row", "arc_over_wall"],
    66: ["wide_platform"], 67: ["support_bridge"], 68: ["topple_line"], 69: ["linked_bridge", "chain_cell"], 70: ["frame"],
    71: ["multi_tier"], 72: ["arc_over_wall"], 73: ["linked_bridge", "chain_cell"], 74: ["wide_platform"], 75: ["mixed_material"],
    76: ["heavy_cap", "topple_line"], 77: ["twin_towers"], 78: ["arc_over_wall", "ledges"], 79: ["multi_tier"], 80: ["finale"],
    81: ["exposed_target"], 82: ["multi_tier"], 83: ["wide_platform"], 84: ["arc_over_wall", "ledges"], 85: ["heavy_cap"],
    86: ["domino_row", "ledges"], 87: ["frame"], 88: ["multi_tier"], 89: ["linked_bridge"], 90: ["linked_bridge", "ledges", "chain_cell"],
    91: ["ring", "chain_cell"], 92: ["topple_line", "mixed_material"], 93: ["heavy_cap", "frame"], 94: ["domino_row", "chain_cell"], 95: ["multi_tier"],
    96: ["arc_over_wall"], 97: ["linked_bridge", "chain_cell"], 98: ["mixed_material"], 99: ["multi_tier", "wide_platform"], 100: ["finale", "ring"],
}
# Pure topple objectives without a critical target core (spec section 4).
NO_CRITICAL = {9, 17, 68, 92}

# Landmark (non-collision, mid-back layer) per chapter band of five levels: gives each band an
# intentional identity. Regex keywords match PRP or ENV ids of that chapter.
LANDMARKS = {
    "helix": [("RELAY_ARRAY", "Relay uplink array and antenna field (New Avalon edge nodes)"),
              ("LOGISTICS_CRANE", "Robotic logistics gantry crane and drone racks"),
              ("COOLING_TOWER", "Server-hall cooling stacks with vapour vents"),
              ("AURA_CORE_CHAMBER", "AURA central logic chamber: ring of server monoliths")],
    "vita": [("CLEANROOM_AIRLOCK", "Clean-room airlock gates and decontamination arches"),
             ("BIOREACTOR_BANK", "Bank of tall bioreactor tanks with green culture light"),
             ("ARCHIVE_VAULT", "Genetic archive vault door and sample shelving (Patent Wall, Black Archive)"),
             ("GROWTH_CHAMBER", "Central growth chamber with glass containment shell")],
    "nova_grid": [("INTAKE_TURBINE", "Intake turbine housings and cable conduits"),
                  ("COOLING_TOWER", "Hyperboloid cooling towers venting steam"),
                  ("TRANSFORMER_YARD", "Transformer yard with insulator stacks and arcing busbars"),
                  ("REACTOR_RING", "Reactor containment ring over the signal chamber")],
    "civitas": [("SENSOR_TOWER", "City sensor towers and camera clusters"),
                ("SCREEN_WALL", "Civic screen wall of public notices (no readable text)"),
                ("PREDICTION_ROOM", "Prediction room with forecast projection table"),
                ("RELAY_SPIRE", "Central civic relay spire and sky bridges")],
    "meridian": [("HYBRID_STACK", "Hybrid server-lab-reactor stacks in the excavated facility"),
                 ("FOUNDATION_PILLARS", "Monumental foundation pillars of the convergence cavern"),
                 ("TEMPORAL_ANCHOR", "Temporal anchor pylons with violet field distortion"),
                 ("CONVERGENCE_CHAMBER", "Convergence core chamber, culmination of all four institutions")],
}
AMBIENCE_BANDS = {
    "helix": ["SERVER_HALL", "LOGISTICS", "COOLING", "CORE"],
    "vita": ["CLEANROOM", "BIOREACTOR", "ARCHIVE", "GROWTH"],
    "nova_grid": ["INTAKE", "COOLING", "TRANSFORMER", "REACTOR"],
    "civitas": ["STREET", "PLAZA", "CONTROL", "SPIRE"],
    "meridian": ["EXCAVATION", "CAVERN", "ANCHOR", "CONVERGENCE"],
}
MATERIAL_VFX = {
    "glass_polymer": ("glass shards", r"-VFX-.*(GLASS|SHARD)"),
    "electronic_module": ("electrical arcs", r"-VFX-.*(ARC|ELECTRIC)"),
    "ai_core_module": ("electrical arcs", r"-VFX-.*(ARC|ELECTRIC)"),
    "energy_component": ("energy discharge", r"-VFX-.*(ENERGY|DISCHARGE|PLASMA)"),
    "concrete": ("concrete dust", r"-VFX-.*(DUST|CONCRETE)"),
    "reinforced_steel": ("metal sparks", r"-VFX-.*SPARK"),
    "lightweight_alloy": ("metal sparks", r"-VFX-.*SPARK"),
    "composite": ("debris chips", r"-VFX-.*(DEBRIS|CHIP|FRAGMENT)"),
}
WEAPON_VFX = [
    ("kinetic muzzle flash", r"-VFX-.*(MUZZLE|KINETIC)"),
    ("impact sparks", r"-VFX-.*(IMPACT|SPARK)"),
    ("breach blast", r"-VFX-.*(BLAST|EXPLOSION|BREACH)"),
    ("smoke", r"-VFX-.*SMOKE"),
]
GAME_WIDE = [
    # (label, id regex, category, accept reference/mock entries)
    ("Operative character mesh", r"^OPR-CHR-OPERATIVE", "characters", False),
    ("Operative animations", r"^OPR-(ANM|CHR)-OPERATIVE.*", "characters", False),
    ("Kinetic Accelerator weapon", r"^OPR-WPN-KINETIC", "weapons", False),
    ("Breach Charge launcher", r"^OPR-WPN-BREACH", "weapons", False),
    ("Kinetic projectile", r"^OPR-PRJ-KINETIC", "weapons", False),
    ("Breach canister projectile", r"^OPR-PRJ-BREACH", "weapons", False),
    ("HUD elements (weapon slots, ammo, cooldown, reticle, trajectory)", r"-UI-(WEAPON_SLOT|AMMO_PIP|COOLDOWN_RING|AIM_RETICLE|TRAJECTORY_DOT|HUD)", "ui", False),
    ("Critical asset target marker", r"-UI-CRITICAL_MARKER", "ui", False),
    ("Objective markers", r"-UI-OBJECTIVE_MARKER", "ui", False),
    ("Weapon icons", r"-ICN-.*(KINETIC|BREACH|WEAPON)", "ui", False),
    ("Objective icons", r"-ICN-.*(OBJECTIVE|TARGET|CORE)", "ui", False),
    ("Panels and buttons (9-slice kit)", r"-UI-(PANEL|BUTTON)", "ui", False),
    ("Main menu backdrop", r"-BG-.*MAIN_MENU", "ui", False),
    ("Loading backdrop", r"-BG-.*LOADING", "ui", False),
    ("Chapter cards and upgrade tier badges", r"-UI-(CARD_CHAPTER|TIER_BADGE|PROGRESS)", "ui", False),
    ("Chapter title treatments", r"-UI-CHAPTER_TITLE_DECO", "ui", False),
    ("Screen layout references (menus, HUD, results, map, upgrades)", r"-UI-SCREEN_.*MOCK", "ui", True),
    ("Godot theme spec", r"-UI-THEME", "ui", False),
    ("Topple threshold marker", r"-(UI|VFX)-.*(THRESHOLD|TOPPLE)", "ui", False),
    ("Game logo", r"^GAM-LOGO-(?!APP_ICON)", "ui", False),
    ("App icon", r"(APP_ICON|-ICN-APP)", "ui", False),
    ("Splash screen", r"SPLASH", "ui", False),
    ("UI font", r"-FNT-", "fonts", False),
    ("Menu music", r"^GAM-MUS-(MENU|TITLE|MAIN)", "audio", False),
    ("Victory stinger", r"-(MUS|SFX)-.*(VICTORY|SUCCESS|WIN)", "audio", False),
    ("Defeat stinger", r"-(MUS|SFX)-.*(DEFEAT|FAIL|LOSE)", "audio", False),
    ("Ending music", r"^GAM-MUS-(ENDING|CREDITS)", "audio", False),
    ("Kinetic fire SFX", r"-SFX-.*KINETIC", "audio", False),
    ("Breach launch / detonation SFX", r"-SFX-.*(BREACH|EXPLOSION|BLAST)", "audio", False),
    ("Metal impact SFX", r"-SFX-.*METAL", "audio", False),
    ("Glass break SFX", r"-SFX-.*GLASS", "audio", False),
    ("Concrete break SFX", r"-SFX-.*(CONCRETE|STONE|RUBBLE)", "audio", False),
    ("Electrical / machinery SFX", r"-SFX-.*(ELECTRIC|ARC|MACHINE|SERVO|HUM)", "audio", False),
    ("UI SFX", r"-SFX-.*(UI|CLICK|CONFIRM|SELECT)", "audio", False),
    ("Alarm SFX", r"-SFX-.*ALARM", "audio", False),
    ("Opening cinematic", r"^GAM-CIN-.*OPENING|-CIN-OPENING", "cinematics", False),
]


def parse_spec() -> dict[int, dict]:
    levels: dict[int, dict] = {}
    if not SPEC.is_file():
        return levels
    for line in SPEC.read_text(encoding="utf-8").splitlines():
        m = re.match(r"^\|\s*(\d{2,3})\s*\|\s*([^|]+?)\s*\|\s*([^|]+?)\s*\|\s*([^|]+?)\s*\|\s*(\d+)\s*\|", line)
        if m:
            n = int(m.group(1))
            if 1 <= n <= 100 and n not in levels:
                levels[n] = {"name": m.group(2), "layout": m.group(3), "skill": m.group(4), "shots": int(m.group(5))}
    return levels


def parse_narrative() -> dict[int, dict]:
    """Section 9 mission map: level, mission name, destructible set / visual target, story breadcrumb."""
    out: dict[int, dict] = {}
    if not NARRATIVE.is_file():
        return out
    for line in NARRATIVE.read_text(encoding="utf-8").splitlines():
        m = re.match(r"^\|\s*(\d{2,3})\s*\|\s*([^|]+?)\s*\|\s*([^|]+?)\s*\|\s*([^|]+?)\s*\|\s*$", line)
        if m and 1 <= int(m.group(1)) <= 100:
            out.setdefault(int(m.group(1)), {"story_target": m.group(3), "breadcrumb": m.group(4)})
    return out


REFERENCE_RE = re.compile(r"(MOCK|CONCEPT|EDITABLE_SOURCE|STYLEFRAME|^SV-)")


def is_reference(e: dict) -> bool:
    """Concepts, mock layouts and editable sources do not count as production coverage."""
    return e.get("render_type") == "reference" or bool(REFERENCE_RE.search(str(e.get("id", ""))))


class Index:
    def __init__(self, entries: list[dict]) -> None:
        self.all = [e for e in entries if isinstance(e, dict) and e.get("path") and (REPO / e["path"]).is_file()]
        self.entries = [e for e in self.all if not is_reference(e)]

    def by_regex(self, pattern: str, codes: list[str] | None = None, include_refs: bool = False) -> list[str]:
        rx = re.compile(pattern)
        out = []
        for e in (self.all if include_refs else self.entries):
            eid = str(e.get("id", ""))
            if codes and not any(eid.startswith(c + "-") for c in codes):
                continue
            if rx.search(eid):
                out.append(eid)
        return sorted(out)

    def kind(self, chapter: str, kind: str) -> list[str]:
        out = []
        for e in self.entries:
            if e.get("category") != "destructibles" or e.get("component_kind") != kind:
                continue
            if str(e.get("chapter", "")) != chapter or "-DEB-" in str(e.get("id", "")):
                continue
            if not str(e.get("path", "")).endswith((".glb", ".gltf")):
                continue
            out.append(e["id"])
        return sorted(out)

    def debris(self, chapter: str, kind: str) -> list[str]:
        return sorted(e["id"] for e in self.entries if e.get("component_kind") == kind and str(e.get("chapter", "")) == chapter and "-DEB-" in str(e.get("id", "")))


def req(label: str, ids: list[str], fallback: list[str] | None = None, wanted: str = "") -> dict:
    if ids:
        return {"label": label, "status": "available", "assets": ids[:6]}
    if fallback:
        return {"label": label, "status": "fallback", "assets": fallback[:6], "wanted": wanted}
    return {"label": label, "status": "missing", "assets": [], "wanted": wanted}


def resolve_kind(idx: Index, chapter: str, role: str) -> dict:
    target = ROLE_KIND[chapter][role]
    if target.startswith("SHR:"):
        kind = target[4:]
        ids = idx.kind("shared", kind)
        return dict(req(f"{role}: {kind} (shared)", ids, wanted=f"SHR-CMP-{kind.upper()}-A"), role=role, kind=kind, material=KIND_MATERIAL[kind])
    material = KIND_MATERIAL[target]
    code = next(c for k, c, *_ in CHAPTERS if k == chapter)
    ids = idx.kind(chapter, target)
    fb = idx.kind("shared", GENERIC_FOR_MATERIAL[material]) if not ids else []
    return dict(req(f"{role}: {target}", ids, fb, wanted=f"{code}-CMP-{target.upper()}-A"), role=role, kind=target, material=material)


def build(manifest: dict) -> dict:
    idx = Index(manifest.get("entries", []))
    spec = parse_spec()
    story = parse_narrative()
    levels = []
    for key, code, number, org, first, title in CHAPTERS:
        for rel_n in range(1, 21):
            n = first + rel_n - 1
            band = (rel_n - 1) // 5
            info = spec.get(n, {})
            archetypes = LEVEL_ARCHETYPES[n]
            roles: list[str] = []
            for a in archetypes:
                for r in ARCHETYPE_ROLES[a]:
                    if r not in roles:
                        roles.append(r)
            if n in NO_CRITICAL and "core" in roles:
                roles.remove("core")
            structural = []
            materials: list[str] = []
            static_req = None
            for r in roles:
                if r == "core":
                    continue
                if r == "static":
                    static_req = req("static ledge / barrier", idx.by_regex(r"-ENV-.*(STATIC|LEDGE|PLINTH|BARRIER|PLATFORM)", [code]),
                                     idx.by_regex(r"-ENV-.*(STATIC|LEDGE|PLINTH|BARRIER|PLATFORM)", ["SHR"]), wanted=f"{code}-ENV-STATIC_LEDGE-A")
                    continue
                k = resolve_kind(idx, key, r)
                structural.append(k)
                if k["material"] not in materials:
                    materials.append(k["material"])
            if static_req:
                structural.append(dict(static_req, role="static", kind="static", material="static"))
            critical = None
            if "core" in roles:
                ck = resolve_kind(idx, key, "core")
                deb = idx.debris(key, ck["kind"])
                critical = dict(ck, debris=req("critical debris set", deb, wanted=f"{code}-DEB-{ck['kind'].upper()}-A"))
                if ck["material"] not in materials:
                    materials.append(ck["material"])
            mats = []
            for m in materials:
                alt = MATERIAL_FALLBACK.get(m)
                fb = idx.by_regex(rf"-MAT-{m.upper()}", ["SHR"])
                if alt:
                    fb = fb + idx.by_regex(rf"-MAT-{alt.upper()}", [code, "SHR"])
                mats.append(dict(req(f"{m} texture set", idx.by_regex(rf"-MAT-{m.upper()}", [code]), fb,
                                     wanted=f"{code}-MAT-{m.upper()}-A"), material=m))
                for state in ("LIGHT", "HEAVY"):
                    fb_dmg = idx.by_regex(rf"-DMG-{alt.upper()}-{state}", [code, "SHR"]) if alt else None
                    mats.append(dict(req(f"{m} damage {state.lower()}", idx.by_regex(rf"-DMG-{m.upper()}-{state}", [code, "SHR"]), fb_dmg,
                                         wanted=f"SHR-DMG-{m.upper()}-{state}"), material=m))
            vfx = [req(label, idx.by_regex(rx, [code, "SHR", "OPR"]), wanted=f"SHR-VFX-{label.upper().replace(' ', '_')}-A") for label, rx in WEAPON_VFX]
            seen_vfx = set()
            for m in materials:
                label, rx = MATERIAL_VFX[m]
                if label in seen_vfx:
                    continue
                seen_vfx.add(label)
                vfx.append(req(label, idx.by_regex(rx, [code, "SHR"]), wanted=f"SHR-VFX-{label.upper().replace(' ', '_')}-A"))
            if critical:
                vfx.append(req("critical asset destruction", idx.by_regex(r"-VFX-.*(CORE|CRITICAL)", [code, "SHR"]), wanted=f"{code}-VFX-CORE_DESTRUCTION-A"))
            env = {
                "floor": req("floor kit", idx.by_regex(r"-ENV-.*FLOOR", [code]), wanted=f"{code}-ENV-FLOOR-A"),
                "back_wall": req("back wall kit", idx.by_regex(r"-ENV-.*(WALL|BACK)", [code]), wanted=f"{code}-ENV-BACK_WALL-A"),
                "structures": req("mid-back structures", [i for i in idx.by_regex(r"-ENV-", [code]) if not re.search(r"FLOOR|WALL|BACK|STATIC|LEDGE|PLINTH|BARRIER|PLATFORM", i)], wanted=f"{code}-ENV-<STRUCTURE>-A"),
            }
            bgs = idx.by_regex(r"-BG-", [code])
            bg = req("far background layer", [bgs[band % len(bgs)]] if bgs else [], wanted=f"{code}-BG-FAR-{'ABCD'[band]}")
            lm_key, lm_desc = LANDMARKS[key][band]
            landmark = dict(req(f"band landmark: {lm_desc}", idx.by_regex(rf"-(PRP|ENV)-.*{lm_key}", [code]), wanted=f"{code}-PRP-{lm_key}-A"), key=lm_key)
            landmark_keys = [k for k, _ in LANDMARKS[key]]
            pool = [i for i in idx.by_regex(r"-PRP-", [code]) if not any(k in i for k in landmark_keys)]
            dressing = [pool[(n * 2 + j) % len(pool)] for j in range(min(2, len(pool)))] if pool else []
            if rel_n == 20 and n != 100:
                music = req("chapter finale / boss theme", idx.by_regex(r"-MUS-.*(BOSS|FINALE)", [code]), wanted=f"{code}-MUS-BOSS-01")
            elif n == 100:
                music = req("final boss theme", idx.by_regex(r"-MUS-.*(BOSS|FINALE)", [code]), wanted=f"{code}-MUS-BOSS-01")
            elif band == 3:
                music = req("combat / escalation theme", idx.by_regex(r"-MUS-.*(COMBAT|TENSION|ESCALAT)", [code]), wanted=f"{code}-MUS-COMBAT-01")
            else:
                music = req("chapter gameplay theme", idx.by_regex(r"-MUS-.*(GAMEPLAY|THEME|EXPLORE)", [code]), wanted=f"{code}-MUS-GAMEPLAY-01")
            amb_key = AMBIENCE_BANDS[key][band]
            amb_band = idx.by_regex(rf"-AMB-.*{amb_key}", [code])
            ambience = req(f"ambience bed ({amb_key.lower()})", amb_band, idx.by_regex(r"-AMB-", [code]), wanted=f"{code}-AMB-{amb_key}-01")
            cinematics = []
            if n == 1:
                cinematics.append(req("opening cinematic", idx.by_regex(r"-CIN-.*OPENING", ["GAM", code]), wanted="GAM-CIN-OPENING-01"))
            if rel_n == 1:
                cinematics.append(req("chapter intro cinematic", idx.by_regex(r"-CIN-.*INTRO", [code]), wanted=f"{code}-CIN-INTRO-01"))
                cinematics.append(req("chapter transition music", idx.by_regex(r"-MUS-.*(TRANSITION|INTRO)", [code, "GAM"]), wanted=f"{code}-MUS-TRANSITION-01"))
            if rel_n == 20 and n != 100:
                cinematics.append(req("chapter outro cinematic", idx.by_regex(r"-CIN-.*OUTRO", [code]), wanted=f"{code}-CIN-OUTRO-01"))
            if n == 100:
                cinematics.append(req("finale cinematic", idx.by_regex(r"-CIN-.*FINALE", ["GAM", code]), wanted="GAM-CIN-FINALE-01"))
                cinematics.append(req("ending music", idx.by_regex(r"-MUS-.*(ENDING|CREDITS)", ["GAM"]), wanted="GAM-MUS-ENDING-01"))
            hard = [*structural, *( [critical, critical["debris"]] if critical else []), *mats, *vfx, *env.values(), bg, landmark, music, ambience, *cinematics]
            missing = sorted({h.get("wanted") or h["label"] for h in hard if h["status"] == "missing"})
            fallbacks = sorted({h["label"] for h in hard if h["status"] == "fallback"})
            status = "missing" if missing else ("fallback" if fallbacks else "full")
            levels.append({
                "level": n, "chapter": key, "chapter_number": number, "organisation": org, "band": band + 1,
                "name": info.get("name", ""), "shots": info.get("shots"), "layout_notes": info.get("layout", ""),
                "story_target": story.get(n, {}).get("story_target", ""), "story_breadcrumb": story.get(n, {}).get("breadcrumb", ""),
                "archetypes": archetypes, "environment_kit": env, "background_layers": [bg], "structural_components": structural,
                "critical_asset": critical, "materials": mats, "vfx": vfx, "music": music, "ambience": ambience,
                "cinematics": cinematics, "unique_props": {"landmark": landmark, "dressing": dressing},
                "status": status, "missing": missing, "fallbacks": fallbacks,
                "requirements": len(hard), "available": sum(1 for h in hard if h["status"] == "available"),
            })
    game_wide = [dict(req(label, idx.by_regex(rx, include_refs=refs)), category=cat) for label, rx, cat, refs in GAME_WIDE]
    miss_count: dict[str, list[int]] = {}
    for lv in levels:
        for m in lv["missing"]:
            miss_count.setdefault(m, []).append(lv["level"])
    ranked = sorted(({"asset": k, "levels": len(v), "first_level": min(v)} for k, v in miss_count.items()), key=lambda x: (-x["levels"], x["first_level"], x["asset"]))
    per_chapter = {}
    for key, *_ in CHAPTERS:
        lv = [x for x in levels if x["chapter"] == key]
        per_chapter[key] = {s: sum(1 for x in lv if x["status"] == s) for s in ("full", "fallback", "missing")}
    archetype_use: dict[str, int] = {}
    for lv in levels:
        for a in lv["archetypes"]:
            archetype_use[a] = archetype_use.get(a, 0) + 1
    return {
        "generated": datetime.date.today().isoformat(),
        "manifest_updated": manifest.get("updated"),
        "manifest_entries": len(idx.all), "production_entries": len(idx.entries),
        "summary": {
            "levels": len(levels),
            "fully_covered": sum(1 for x in levels if x["status"] == "full"),
            "covered_with_fallbacks": sum(1 for x in levels if x["status"] == "fallback"),
            "missing_assets": sum(1 for x in levels if x["status"] == "missing"),
            "requirements_total": sum(x["requirements"] for x in levels),
            "requirements_available": sum(x["available"] for x in levels),
            "per_chapter": per_chapter,
            "game_wide_available": sum(1 for g in game_wide if g["status"] == "available"),
            "game_wide_total": len(game_wide),
            "archetype_use": dict(sorted(archetype_use.items(), key=lambda kv: -kv[1])),
        },
        "game_wide": game_wide,
        "missing_ranked": ranked,
        "levels": levels,
    }


ICON = {"available": "ok", "fallback": "fb", "missing": "--"}


def cell(r: dict | None) -> str:
    if r is None:
        return "n/a"
    return ICON[r["status"]]


def group_cell(items: list[dict]) -> str:
    if not items:
        return "n/a"
    a = sum(1 for i in items if i["status"] == "available")
    f = sum(1 for i in items if i["status"] == "fallback")
    return f"{a}/{len(items)}" + (f" ({f} fb)" if f else "")


def to_md(data: dict) -> str:
    s = data["summary"]
    lines = [
        "# 100-level asset coverage matrix",
        "",
        f"Generated {data['generated']} by `generated_assets/tools/build_coverage_matrix.py` from the merged manifest "
        f"(updated {data['manifest_updated']}, {data['manifest_entries']} entries on disk, {data['production_entries']} production entries; concepts and mock layouts do not count). Do not edit by hand; re-run the script.",
        "",
        "Status: `ok` available, `fb` shared fallback only, `--` missing. Group columns show available/required.",
        "A level is **full** when every requirement is available, **fallback** when nothing is missing but shared substitutes are used.",
        "",
        "## Summary",
        "",
        f"- Levels fully covered: **{s['fully_covered']} / {s['levels']}**; covered with fallbacks: {s['covered_with_fallbacks']}; with missing assets: {s['missing_assets']}.",
        f"- Requirements available: {s['requirements_available']} / {s['requirements_total']} level-requirement slots.",
        f"- Game-wide requirements available: {s['game_wide_available']} / {s['game_wide_total']}.",
        "",
        "| Chapter | Full | Fallback | Missing |",
        "|---|---:|---:|---:|",
    ]
    for k, v in s["per_chapter"].items():
        lines.append(f"| {k} | {v['full']} | {v['fallback']} | {v['missing']} |")
    lines += ["", "Layout archetype use across the campaign (variety check): " + ", ".join(f"{k} {v}" for k, v in s["archetype_use"].items()) + ".", ""]
    lines += ["## Game-wide", "", "| Requirement | Status | Assets |", "|---|---|---|"]
    for g in data["game_wide"]:
        lines.append(f"| {g['label']} | {cell(g)} | {', '.join(g['assets'][:3])} |")
    for key, code, number, org, first, title in CHAPTERS:
        lines += ["", f"## Chapter {number}: {org} ({title}), levels {first}-{first + 19}", "",
                  "| L | Name | Story target | Archetypes | Struct | Core | Mat+dmg | VFX | Env | BG | Landmark | Music | Amb | Cine | Status |",
                  "|---:|---|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
        for lv in [x for x in data["levels"] if x["chapter"] == key]:
            env = list(lv["environment_kit"].values())
            lines.append("| {level} | {name} | {story} | {arch} | {st} | {core} | {mat} | {vfx} | {env} | {bg} | {lm} | {mus} | {amb} | {cin} | {status} |".format(
                level=lv["level"], name=lv["name"], story=lv["story_target"], arch=", ".join(lv["archetypes"]), st=group_cell(lv["structural_components"]),
                core=cell(lv["critical_asset"]), mat=group_cell(lv["materials"]), vfx=group_cell(lv["vfx"]), env=group_cell(env),
                bg=cell(lv["background_layers"][0]), lm=cell(lv["unique_props"]["landmark"]) + " " + lv["unique_props"]["landmark"]["key"].lower(),
                mus=cell(lv["music"]), amb=cell(lv["ambience"]), cin=group_cell(lv["cinematics"]), status=lv["status"]))
    lines += ["", "## Missing assets ranked by levels affected", "", "| Wanted asset (id pattern) | Levels | First level |", "|---|---:|---:|"]
    for m in data["missing_ranked"][:120]:
        lines.append(f"| `{m['asset']}` | {m['levels']} | {m['first_level']} |")
    if len(data["missing_ranked"]) > 120:
        lines.append(f"| ... {len(data['missing_ranked']) - 120} more in coverage_matrix.json | | |")
    lines += ["", "## How requirements are derived", "",
              "- Structural components: each level's layout archetypes (from the puzzle notes in `docs/level-design-spec.md`) give structural roles; each chapter maps roles to its component kinds (ASSET_CONTRACT section 5). A chapter kind with only a shared generic block of the same physics material counts as fallback.",
              "- Critical asset: the chapter core kind plus its debris set, except pure topple levels 9, 17, 68 and 92.",
              "- Materials: a texture set per physics material used (chapter set, or shared as fallback) plus light and heavy damage overlays.",
              "- VFX: weapon effects for every level plus material-specific destruction effects and the critical destruction effect.",
              "- Environment: chapter floor, back wall and mid-back structures; a far background layer rotated by band.",
              "- Story targets and breadcrumbs come from the mission map in `docs/narrative-bible.md` section 9; they steer dressing and landmark choice per level.",
              "- Variety: one landmark prop per band of five levels (four per chapter, 20 in total) and two dressing props rotated from the chapter prop pool.",
              "- Music: chapter gameplay theme for bands 1-3, combat theme for band 4, boss or finale theme on levels 20/40/60/80/100. Ambience by band with the chapter bed as fallback. Cinematics on chapter intros, outros, the opening (level 1) and the finale (level 100).",
              ""]
    return "\n".join(lines)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true", help="fail if the committed matrix differs from a fresh build (ignores the date)")
    args = ap.parse_args()
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    data = build(manifest)
    # One level per line keeps the file small and diffs readable.
    head = {k: v for k, v in data.items() if k != "levels"}
    body = ",\n".join("  " + json.dumps(lv, ensure_ascii=False, separators=(",", ":")) for lv in data["levels"])
    text_json = json.dumps(head, indent=1, ensure_ascii=False)[:-2] + ',\n "levels": [\n' + body + "\n ]\n}\n"
    text_md = to_md(data) + "\n"
    if args.check:
        old = json.loads(OUT_JSON.read_text(encoding="utf-8")) if OUT_JSON.is_file() else {}
        old["generated"] = data["generated"]
        if json.dumps(old, sort_keys=True) != json.dumps(data, sort_keys=True):
            print("FAIL: coverage matrix out of date", file=sys.stderr)
            return 1
        print("PASS: coverage matrix current")
        return 0
    OUT_JSON.write_text(text_json, encoding="utf-8")
    OUT_MD.write_text(text_md, encoding="utf-8")
    s = data["summary"]
    print(f"levels: {s['levels']}, full {s['fully_covered']}, fallback {s['covered_with_fallbacks']}, missing {s['missing_assets']}; "
          f"requirements {s['requirements_available']}/{s['requirements_total']}; game-wide {s['game_wide_available']}/{s['game_wide_total']}")
    print(f"distinct missing assets: {len(data['missing_ranked'])}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
