#!/usr/bin/env python3
"""Chapter II-V preview layouts for asset-integration screenshots (tools only, not game levels).

The game ships one authored mission (data/missions/helix_01.json). Chapters II to V have no
missions yet, so their delivered kits cannot be seen in the real MissionScreen. This tool writes
one preview mission and set per chapter by recasting helix_01 role for role onto the chapter's
proposed kinds (ASSET_CONTRACT section 5), with each kind's default physics material, and the
helix_01 set dressing onto the chapter's environment kit and landmarks. Component ids,
positions, sizes, supports and objectives are unchanged, so the layouts are a like-for-like
look at each kit, not designed levels. Output: tools/chapter_preview/<chapter>_preview.json
(mission) and tools/chapter_preview/environments/<chapter>_preview.json (set).

    python3 tools/chapter_preview/build_chapter_previews.py
"""

import json
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
OUT = REPO / "tools/chapter_preview"

# helix_01 kind -> (chapter kind, default physics material from the contract catalogue)
ROLES = {
    "vita": {
        "server_rack": ("specimen_rack", "electronic_module"), "support_column": ("lab_column", "lightweight_alloy"),
        "service_deck": ("lab_deck", "composite"), "ai_core": ("gene_vault_core", "ai_core_module"),
        "core_shield": ("cleanroom_panel", "glass_polymer"), "power_cell": ("cryo_cell", "energy_component"),
        "blast_wall": ("cleanroom_panel", "glass_polymer"), "relay_mast": ("lab_column", "lightweight_alloy"),
        "relay_dish": ("containment_cap", "concrete"),
    },
    "nova_grid": {
        "server_rack": ("transformer", "electronic_module"), "support_column": ("grid_pylon", "reinforced_steel"),
        "service_deck": ("cable_bridge", "composite"), "ai_core": ("reactor_core", "energy_component"),
        "core_shield": ("containment_wall", "concrete"), "power_cell": ("capacitor_cell", "energy_component"),
        "blast_wall": ("containment_wall", "concrete"), "relay_mast": ("grid_pylon", "reinforced_steel"),
        "relay_dish": ("containment_ring_segment", "reinforced_steel"),
    },
    "civitas": {
        "server_rack": ("data_exchange_rack", "electronic_module"), "support_column": ("civic_column", "concrete"),
        "service_deck": ("relay_bridge", "composite"), "ai_core": ("surveillance_core", "ai_core_module"),
        "core_shield": ("security_wall", "reinforced_steel"), "power_cell": ("sensor_array", "glass_polymer"),
        "blast_wall": ("security_wall", "reinforced_steel"), "relay_mast": ("sensor_mast", "lightweight_alloy"),
        "relay_dish": ("civic_screen", "glass_polymer"),
    },
    "meridian": {
        "server_rack": ("quantum_stabilizer", "electronic_module"), "support_column": ("anchor_column", "reinforced_steel"),
        "service_deck": ("convergence_deck", "composite"), "ai_core": ("convergence_core", "energy_component"),
        "core_shield": ("phase_shield", "glass_polymer"), "power_cell": ("temporal_cell", "energy_component"),
        "blast_wall": ("monolith_slab", "concrete"), "relay_mast": ("timeline_relay", "lightweight_alloy"),
        "relay_dish": ("monolith_slab", "concrete"),
    },
}
CODES = {"vita": "VTA", "nova_grid": "NVG", "civitas": "CVT", "meridian": "MRD"}
NUMBERS = {"vita": 2, "nova_grid": 3, "civitas": 4, "meridian": 5}
CORES = {"vita": "gene vault core", "nova_grid": "reactor core", "civitas": "surveillance core", "meridian": "convergence core"}
NAMES = {"vita": "VITA kit preview", "nova_grid": "Nova Grid kit preview", "civitas": "Civitas kit preview", "meridian": "Meridian kit preview"}
# helix_01 landmark props -> chapter landmarks (band 1 and the left-hand feature)
LANDMARKS = {
    "vita": {"HLX-PRP-RELAY_ARRAY-A": "VTA-PRP-GROWTH_CHAMBER-A", "HLX-PRP-COOLING_TOWER-A": "VTA-PRP-BIOREACTOR_BANK-A"},
    "nova_grid": {"HLX-PRP-RELAY_ARRAY-A": "NVG-PRP-REACTOR_RING-A", "HLX-PRP-COOLING_TOWER-A": "NVG-PRP-COOLING_TOWER-A"},
    "civitas": {"HLX-PRP-RELAY_ARRAY-A": "CVT-PRP-SENSOR_TOWER-A", "HLX-PRP-COOLING_TOWER-A": "CVT-PRP-RELAY_SPIRE-A"},
    "meridian": {"HLX-PRP-RELAY_ARRAY-A": "MRD-PRP-TEMPORAL_ANCHOR-A", "HLX-PRP-COOLING_TOWER-A": "MRD-PRP-HYBRID_STACK-A"},
}


def main():
    mission = json.loads((REPO / "data/missions/helix_01.json").read_text(encoding="utf-8"))
    env = json.loads((REPO / "data/environments/helix_01.json").read_text(encoding="utf-8"))
    manifest = {e["id"] for e in json.loads((REPO / "assets/asset_manifest.json").read_text(encoding="utf-8"))["entries"]}
    (OUT / "environments").mkdir(parents=True, exist_ok=True)
    for chapter, roles in ROLES.items():
        mid = f"{chapter}_preview"
        m = json.loads(json.dumps(mission))
        m["_note"] = f"TOOLS ONLY, not a game level: helix_01 recast onto the {chapter} kit for asset screenshots (tools/chapter_preview/build_chapter_previews.py)."
        m["id"], m["name"], m["chapter"] = mid, NAMES[chapter], NUMBERS[chapter]
        for c in m["components"]:
            c["kind"], c["material"] = roles[c["kind"]]
        m["briefing"] = f"Preview of the {chapter} kit on the helix_01 layout. Destroy the {CORES[chapter]}."
        for o in m["objectives"]:
            o["label"] = o["label"].replace("the AURA core", "the " + CORES[chapter]).replace("server racks", "racks").replace("relay uplink", "top link")
        e = json.loads(json.dumps(env))
        e["_note"] = f"TOOLS ONLY: helix_01 set dressing recast onto the {chapter} environment kit."
        e["chapter"] = chapter
        code = CODES[chapter]
        e["statics"] = {k: (v.replace("HLX-", code + "-") if isinstance(v, str) else v) for k, v in e["statics"].items()}
        for piece in e["pieces"]:
            piece["id"] = LANDMARKS[chapter].get(piece["id"], piece["id"].replace("HLX-", code + "-"))
        missing = [p["id"] for p in e["pieces"] if p["id"] not in manifest]
        if missing:
            raise SystemExit(f"{chapter}: pieces not in the library: {missing}")
        (OUT / f"{mid}.json").write_text(json.dumps(m, indent="\t", ensure_ascii=False) + "\n", encoding="utf-8")
        (OUT / "environments" / f"{mid}.json").write_text(json.dumps(e, indent="\t", ensure_ascii=False) + "\n", encoding="utf-8")
        print("wrote", mid)


if __name__ == "__main__":
    main()
