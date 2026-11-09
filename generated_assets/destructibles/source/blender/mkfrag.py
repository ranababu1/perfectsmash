"""Write generated_assets/manifest_parts/3d-kits.json from build stats (destructibles) plus
extra entry files (environments, weapons, characters, previews) in /workspace/tfj-masters/3d-kits/extra/."""
import json, glob, os, datetime

REPO = "/workspace/tfj-3d-kits"
STATS = "/workspace/tfj-masters/3d-kits/stats"
EXTRA = "/workspace/tfj-masters/3d-kits/extra"
CH_CODE = {"helix": "HLX", "vita": "VTA", "nova_grid": "NVG", "civitas": "CVT", "meridian": "MRD", "shared": "SHR"}
LEVELS = {"helix": [1, 20], "vita": [21, 40], "nova_grid": [41, 60], "civitas": [61, 80], "meridian": [81, 100],
          "shared": [1, 100]}
SRC = ("Scripted Blender 5.2.3 (bpy) procedural modelling by the 3d-kits stream; source: "
       "generated_assets/destructibles/source/blender/ (tfjkit, tfjdamage, kits/{kit}.py)")
MATNOTE = ("Colour lives in each slot's baseColorFactor, no COLOR_0 (ASSET_CONTRACT 7, v1.4). mat_<material>_<ch> is "
           "the main physics-material surface; mat_<material>_<ch>_<zone> are other finishes of the same material (bind the "
           "same material set and damage overlay by prefix); trim_<zone>_<ch> are paint, rubber, cable, internals and burnt "
           "metal; emit_ and glass_ as named. UV0 is world-scale box projection, 1 UV unit = 1 m, so tileable sets and "
           "the 1 tile/m damage overlays line up.")
PREMIUM = {"helix"}  # chapters rebuilt in the premium uplift pass (textured slots)
MATNOTE_TEX = ("Premium pass (2026-11-10): every slot is textured from the surfaces stream library. The glb references "
               "the textures by relative URI (../../materials/<ch>/... and ../../materials/shared/...), it does not embed "
               "them: Godot resolves them to the res:// library PNGs on import and through runtime GLTFDocument (both "
               "tested). baseColorFactor is a palette tint over the library albedo, metallicFactor is set per zone, "
               "emissive textures are masks (EMISSION_OP_MULTIPLY). COLOR_0 carries baked ambient occlusion only "
               "(valid since v1.7; multiply it with albedo). Slots: mat_<material>_<ch>[_<zone>] main and zone finishes, "
               "trim_edge_<ch> is the worn edge highlight on bevels, trim_module_<ch> uses fitted UVs (one rack unit per "
               "blade) with the electronic_module emission mask, trim_<zone>_<ch> paint, rubber, cable, internals, burnt "
               "metal; emit_ and glass_ as named. UV0 is world-scale box projection (1 UV unit = 1 m) except fitted module "
               "faces. Per v1.9, keep emission enabled on every loader-built surface (black when unlit).")


def matnote(ch):
    return MATNOTE_TEX if ch in PREMIUM else MATNOTE


RIGHTS = ("original procedural work: scripted Blender (bpy) code written by the 3d-kits asset agent (AI-assisted "
          "authorship); no third-party meshes, textures or concept pixels; ownership not legally settled for AI-assisted "
          "work; not marked commercially cleared. Premium-pass textures come from the surfaces stream library in this repo "
          "(see generated_assets/materials/PRODUCTION_NOTES.md for their rights note)")


def rel(p):
    return os.path.relpath(p, REPO)


def comp_entries(st):
    ch = st["chapter"]
    lv = LEVELS[ch]
    levels = list(range(lv[0], lv[1] + 1))
    kit = st.get("kit", ch)
    t = st["tris"]
    common = dict(category="destructibles", render_type="mesh", format="glb", source=SRC.format(kit=kit),
                  rights_status=RIGHTS, approval_status="pending_review", chapter=ch,
                  material=st["material"], component_kind=st["kind"], levels=levels)
    e1 = dict(id=st["id"], path=rel(st["file"]), purpose=st.get("purpose") or
              f"{st['kind'].replace('_', ' ')} destructible component mesh with progressive damage geometry", **common)
    e1.update(
        used_by="MissionView component mesh (proposed loader, ASSET_CONTRACT 17); nodes mesh_intact / mesh_light / mesh_heavy",
        pivot="centre of the collision rectangle, z = 0 (front +Z)",
        reference_size_px=st["reference_size_px"], depth_m=st["depth_m"], scale_range=st["scale_range"],
        tris=t["intact"] + t["light"] + t["heavy"], states=["intact", "light", "heavy", "destroyed"],
        critical=bool(st.get("critical")),
        dimensions=f"{st['reference_size_px'][0] / 100:.2f} x {st['reference_size_px'][1] / 100:.2f} x {st['depth_m']} m",
        notes=(f"Nodes: mesh_intact ({t['intact']} tris), mesh_light ({t['light']}), mesh_heavy ({t['heavy']}); show one "
               f"at a time (all three import visible: hide mesh_light and mesh_heavy on instancing). Marker empties: "
               f"{', '.join(st['fx'])}. Material slots: {', '.join(st['materials'])}. " + matnote(st["chapter"]) + " Heavy state switches "
               f"some compute light to the warning colour and turns others off (malfunction read); fx_spark_* mark exposed "
               f"internals for spark VFX. Destroyed state: see "
               f"{st['debris_id']}. glb {st['bytes'] / 1024:.0f} KB."))
    e2 = dict(id=st["debris_id"], path=rel(st["debris_file"]),
              purpose=f"Destroyed state for {st['id']}: collapsed husk plus loose fragments (visual only, no collision)",
              **common)
    e2.update(
        used_by="MissionView destroyed state (proposed: spawn at the removed body; fragments as short-lived visual-only bodies)",
        pivot="each node at its own centre, laid out around the component centre in intact positions; husk rests on the bottom edge of the rectangle",
        reference_size_px=st["reference_size_px"], depth_m=st["depth_m"], tris=t["debris"], states=["destroyed"],
        notes=(f"Nodes: husk + frag_01..frag_{st['fragments'] - 1:02d} ({st['fragments']} meshes, {t['debris']} tris "
               f"total, <= 1.5x intact). Same material slot convention as the component. "
               f"glb {st['debris_bytes'] / 1024:.0f} KB."))
    return [e1, e2]


ENV_SRC = ("Scripted Blender 5.2.3 (bpy) procedural modelling by the 3d-kits stream; source: "
           "generated_assets/destructibles/source/blender/ ({mod}, tfjenv.py)")
DESIGN = ("Form language follows the project concept frames SV-01 to SV-07 (see their manifest entries); "
          "no concept pixels are used in the mesh.")
STATS_ENV = "/workspace/tfj-masters/3d-kits/stats_env"
STATS_CHR = "/workspace/tfj-masters/3d-kits/stats_char.json"
LANDMARK_KEYS = {
    "helix": ["RELAY_ARRAY", "LOGISTICS_CRANE", "COOLING_TOWER", "AURA_CORE_CHAMBER"],
    "vita": ["CLEANROOM_AIRLOCK", "BIOREACTOR_BANK", "ARCHIVE_VAULT", "GROWTH_CHAMBER"],
    "nova_grid": ["INTAKE_TURBINE", "COOLING_TOWER", "TRANSFORMER_YARD", "REACTOR_RING"],
    "civitas": ["SENSOR_TOWER", "SCREEN_WALL", "PREDICTION_ROOM", "RELAY_SPIRE"],
    "meridian": ["HYBRID_STACK", "FOUNDATION_PILLARS", "TEMPORAL_ANCHOR", "CONVERGENCE_CHAMBER"],
}
ORIGIN_TEXT = {
    "floor": "top face at y = 0, left edge at x = 0, depth centred on z = 0 (tiles along +x and in z)",
    "bottom_centre": "bottom centre (x and z centred, lowest point at y = 0)",
    "centre": "centre of the collision rectangle, z = 0 (front +Z), like components",
    "grip": "weapon grip (hand contact); barrel along +X; muzzle empty at the bore exit",
}
LAYER_USE = {
    "floor": "MissionView floor layer (proposed kit loader, ASSET_CONTRACT 10): top at y = 0, z -9 .. +5",
    "near": "MissionView near-back layer, z -2.5 .. -4 (props, no collision; never taller than 3 m behind a critical asset)",
    "mid": "MissionView mid-back layer, z -4 .. -8 (facility walls, gantries, massing)",
    "static": "MissionView statics (fixed ledges and plinths), gameplay band, depth 1.6 m",
    "landmark": "MissionView mid-back band landmark, z -4 .. -8, one per five levels (ASSET_CONTRACT 19)",
}


def env_entries(st):
    ch = st["chapter"]
    cat = st["category"]
    t = st["tris"]["intact"]
    lv = LEVELS.get(ch, [1, 100])
    levels = list(range(lv[0], lv[1] + 1))
    if st.get("landmark"):
        key = st["id"].split("-")[2]
        i = LANDMARK_KEYS[ch].index(key)
        levels = list(range(lv[0] + 5 * i, lv[0] + 5 * i + 5))
    mod = "kits/weapons.py" if cat == "weapons" else "kits/env_kits.py, env_common.py, env_landmarks.py"
    e = dict(id=st["id"], path=rel(st["file"]), category=cat, render_type="mesh", format="glb",
             purpose=st["purpose"], source=ENV_SRC.format(mod=mod), rights_status=RIGHTS,
             approval_status="pending_review", used_by=LAYER_USE.get(st.get("layer"), "OperativeRig weapon_socket (proposed, ASSET_CONTRACT 11)"),
             chapter=ch if ch in LEVELS else "shared", levels=levels if cat != "weapons" else list(range(1, 101)),
             pivot=ORIGIN_TEXT.get(st.get("origin"), st.get("origin")), material=st["material"], tris=t)
    if st.get("dims_m"):
        e["dimensions"] = " x ".join(f"{v:g}" for v in st["dims_m"]) + " m (w x h x d)"
    else:
        mn, mx = st["bounds_m"]
        e["dimensions"] = f"{mx[0] - mn[0]:.2f} x {mx[2] - mn[2]:.2f} x {mx[1] - mn[1]:.2f} m (w x h x d)"
    if st.get("reference_size_px"):
        e["reference_size_px"] = st["reference_size_px"]
        e["depth_m"] = st["depth_m"]
    notes = [f"Single node mesh_intact ({t} tris) under a root named after the file.",
             f"Material slots: {', '.join(st['materials'])}.",
             matnote(ch), "Background layers are pre-darkened in baseColorFactor so they sit 30-50% below gameplay pieces.",
             DESIGN]
    if st.get("fx"):
        notes.insert(1, f"Marker empties: {', '.join(st['fx'])}.")
    if st.get("blockout"):
        e["approval_status"] = "pending_review"
        notes.insert(0, "CONCEPT-LEVEL BLOCKOUT ONLY (future weapon, not production art).")
    if cat == "weapons" and "-PRJ-" in st["id"]:
        e["used_by"] = "Projectile visual (proposed replacement for the code's primitive projectile, ASSET_CONTRACT 11)"
        e["pivot"] = "centre of the projectile, travel along +X"
    e["notes"] = " ".join(notes) + f" glb {st['bytes'] / 1024:.0f} KB."
    return [e]


def char_entries():
    if not os.path.exists(STATS_CHR):
        return []
    st = json.load(open(STATS_CHR))
    t = st["tris"]["intact"]
    base = dict(category="characters", render_type="mesh", format="glb", rights_status=RIGHTS,
                approval_status="pending_review", chapter="shared", levels=list(range(1, 101)),
                source=ENV_SRC.format(mod="runchar.py"))
    anims = st["animations"]
    e = dict(id=st["id"], path=rel(st["file"]), purpose="Operative: stylised low-mid poly hooded faceless operative (SV-01, shorter cape) with a rigid node rig and nine animations",
             used_by="OperativeRig replacement (proposed, ASSET_CONTRACT 11): drive torso, arm_weapon, head, legs like the primitive placeholder",
             pivot="between the feet at floor level, facing +X", tris=t, dimensions="about 0.55 x 1.84 x 0.5 m (w x h x d)",
             animation=sorted(anims), **base)
    e["notes"] = (f"Node rig (no skin): hips > torso > head > hood, torso > arm_weapon > forearm_weapon > weapon_socket, "
                  f"torso > arm_support > forearm_support, hips > leg_r/leg_l > shin_r/shin_l. arm_weapon pivots at the "
                  f"right (camera-side) shoulder; rotation 0 aims along +X and the aim angle is a rotation about +Z, as "
                  f"in OperativeRig. Mount the weapon glb on weapon_socket with no offset (weapon origin = grip). "
                  f"The support arm is separate; copy a share of the arm_weapon rotation to arm_support if the far hand "
                  f"should follow the aim. Head carries the emissive visor slits (emit_cyan_opr). Animations are node "
                  f"TRS clips at 30 fps, in place, every node keyed in every clip so clips can be switched cleanly. "
                  f"Material slots: {', '.join(st['materials'])}. Slot convention as the kit (colour in baseColorFactor, no COLOR_0). Quality: stylised production candidate built procedurally; it reads "
                  f"well at game distance but is not a sculpted hero character. {DESIGN} glb {st['bytes'] / 1024:.0f} KB.")
    out = [e]
    for name, a in sorted(anims.items()):
        out.append(dict(id=f"OPR-ANM-OPERATIVE-{name.upper()}", path=rel(st["file"]),
                        purpose=f"Operative animation clip '{name}' ({a['frames']} frames at 30 fps)",
                        used_by="AnimationPlayer on the imported operative scene (proposed, ASSET_CONTRACT 11)",
                        animation=name, loop=bool(a["loop"]), duration_seconds=a["seconds"],
                        notes=f"Clip '{name}' inside {os.path.basename(st['file'])}; {'loops' if a['loop'] else 'plays once and holds the last frame'}. In place, no root motion.",
                        **base))
    return out


def main():
    entries = []
    for p in sorted(glob.glob(f"{STATS_ENV}/*.json")):
        st = json.load(open(p))
        if os.path.exists(st["file"]) and st["file"].startswith(REPO):
            entries += env_entries(st)
    entries += char_entries()
    for p in sorted(glob.glob(f"{STATS}/*.json")):
        st = json.load(open(p))
        if not os.path.exists(st["file"]) or not st["file"].startswith(REPO):
            continue
        entries += comp_entries(st)
    for p in sorted(glob.glob(f"{EXTRA}/*.json")):
        for e in json.load(open(p)):
            if os.path.exists(os.path.join(REPO, e["path"])):
                entries.append(e)
    from PIL import Image
    CH_BY = {"hlx": "helix", "vta": "vita", "nvg": "nova_grid", "cvt": "civitas", "mrd": "meridian", "shr": "shared", "opr": "shared"}
    for cat in ("destructibles", "environments", "weapons", "characters"):
        for p in sorted(glob.glob(f"{REPO}/generated_assets/{cat}/previews/*.webp")):
            b = os.path.basename(p)[:-5]
            if not (b.endswith(("_components_sheet", "_environment_sheet", "_godot_test_frame")) or b.startswith("opr_")
                    or "_showcase" in b):
                continue  # other streams' previews share these folders
            ch = CH_BY.get(b.split("_")[0], "shared")
            w, h = Image.open(p).size
            godot = "godot" in b or "_showcase" in b
            entries.append(dict(
                id=f"{b.split('_')[0].upper()}-PRV-{cat.upper()}-{b.upper()}", path=rel(p), category=cat,
                render_type="reference", format="webp",
                purpose=("Godot 4.7.2 GL Compatibility check frame (runtime GLTFDocument load, MissionView camera, sun and environment)"
                         if godot else "Contact sheet rendered in Blender Cycles at the game camera angle"),
                source=("generated_assets/destructibles/source/godot/" + ("showcase.gd" if "_showcase" in b else "char_check.gd" if cat == "characters" else "kit_scene.gd")
                        if godot else "generated_assets/destructibles/source/blender/sheets.py from build tiles (tfjrender.py)"),
                rights_status=RIGHTS, used_by="review only", chapter=ch, dimensions=f"{w}x{h}",
                approval_status="pending_review"))
    import sys
    only = sys.argv[1:]  # optional: chapters and/or categories to include (batches committed so far)
    if only:
        entries = [e for e in entries if e.get("chapter") in only or e.get("category") in only
                   or f"{e.get('category')}:{e.get('chapter')}" in only]
    frag = {"stream": "3d-kits", "updated": datetime.date.today().isoformat(), "entries": entries}
    out = f"{REPO}/generated_assets/manifest_parts/3d-kits.json"
    json.dump(frag, open(out, "w"), indent=1)
    print(out, len(entries), "entries")


if __name__ == "__main__":
    main()
