"""Environment kits for all five chapters: floors, walls, pillars, catwalks, trusses, massing, statics,
props and the four band landmarks per chapter (contract sections 10 and 19)."""
import env_common as E
import env_landmarks as L

CODE = {"helix": "HLX", "vita": "VTA", "nova_grid": "NVG", "civitas": "CVT", "meridian": "MRD"}
EMIT = {"helix": ("cyan", "orange"), "vita": ("green", "white"), "nova_grid": ("amber", "blue"),
        "civitas": ("blue", "red"), "meridian": ("violet", "cyan")}

LANDMARKS = {
    "helix": [("RELAY_ARRAY", L.hlx_relay_array), ("LOGISTICS_CRANE", L.hlx_logistics_crane),
              ("COOLING_TOWER", L.hlx_cooling_tower), ("AURA_CORE_CHAMBER", L.hlx_aura_core_chamber)],
    "vita": [("CLEANROOM_AIRLOCK", L.vta_cleanroom_airlock), ("BIOREACTOR_BANK", L.vta_bioreactor_bank),
             ("ARCHIVE_VAULT", L.vta_archive_vault), ("GROWTH_CHAMBER", L.vta_growth_chamber)],
    "nova_grid": [("INTAKE_TURBINE", L.nvg_intake_turbine), ("COOLING_TOWER", L.nvg_cooling_tower),
                  ("TRANSFORMER_YARD", L.nvg_transformer_yard), ("REACTOR_RING", L.nvg_reactor_ring)],
    "civitas": [("SENSOR_TOWER", L.cvt_sensor_tower), ("SCREEN_WALL", L.cvt_screen_wall),
                ("PREDICTION_ROOM", L.cvt_prediction_room), ("RELAY_SPIRE", L.cvt_relay_spire)],
    "meridian": [("HYBRID_STACK", L.mrd_hybrid_stack), ("FOUNDATION_PILLARS", L.mrd_foundation_pillars),
                 ("TEMPORAL_ANCHOR", L.mrd_temporal_anchor), ("CONVERGENCE_CHAMBER", L.mrd_convergence_chamber)],
}


def _spec(ch, typ, name, fn, mat, layer, origin, purpose, **kw):
    e, e2 = EMIT[ch]
    d = dict(id=f"{CODE[ch]}-{typ}-{name}-A" if not name[-2:-1] == "-" else f"{CODE[ch]}-{typ}-{name}",
             chapter=ch, material=mat, category="environments", build=fn, emit=e, emit2=e2, layer=layer,
             origin=origin, purpose=purpose, kind=name.split("-")[0].lower(), value={"floor": 0.27, "near": 0.5, "mid": 0.38, "static": 1.0, "landmark": 0.48}[layer] * ({"vita": 0.55, "meridian": 0.62}.get(ch, 1.0) if layer in ("floor", "mid", "landmark") else 1.0),
             ao_dist={"floor": 0.15, "near": 0.25, "mid": 0.6, "static": 0.12, "landmark": 0.6}[layer])
    d.update(kw)
    return d


def specs_for(ch):
    st = E.STYLE[ch]
    mf, mw = st["mat_floor"], st["mat_wall"]
    out = [
        _spec(ch, "ENV", "FLOOR_TILE-A", lambda B, r, s: E.floor_tile(B, s["chapter"], 1.0, 1.0), mf, "floor", "floor",
              "Floor module 1 x 1 m, top at y 0, left edge at x 0, depth centred", dims_m=[1.0, 0.3, 1.0]),
        _spec(ch, "ENV", "FLOOR_TILE-B", lambda B, r, s: E.floor_tile(B, s["chapter"], 4.0, 4.0), mf, "floor", "floor",
              "Floor module 4 x 4 m, top at y 0, left edge at x 0, depth centred", dims_m=[4.0, 0.3, 4.0]),
        _spec(ch, "ENV", "FLOOR_TRENCH-A", lambda B, r, s: E.floor_tile(B, s["chapter"], 4.0, 4.0, "trench"), mf, "floor",
              "floor", "Floor module 4 x 4 m with a covered service trench along x", dims_m=[4.0, 0.3, 4.0]),
        _spec(ch, "ENV", "BACK_WALL-A", lambda B, r, s: E.wall(B, s["chapter"]), mw, "mid", "bottom_centre",
              "Mid-back facility wall module 4 m wide, 6 m tall, 0.5 m thick", dims_m=[4.0, 6.0, 0.6]),
        _spec(ch, "ENV", "BACK_WALL-B", lambda B, r, s: E.wall(B, s["chapter"], kind="window"), mw, "mid", "bottom_centre",
              "Mid-back wall module with an observation window", dims_m=[4.0, 6.0, 0.6]),
        _spec(ch, "ENV", "LOW_WALL-A", lambda B, r, s: E.low_wall(B, s["chapter"]), mw, "near", "bottom_centre",
              "Near-back low wall with railing and console faces, 1.1 m tall", dims_m=[4.0, 1.1, 0.46]),
        _spec(ch, "ENV", "PILLAR-A", lambda B, r, s: E.pillar(B, s["chapter"]), mw, "mid", "bottom_centre",
              "Structural pillar 0.8 m, 6 m tall", dims_m=[0.96, 6.0, 0.96]),
        _spec(ch, "ENV", "CATWALK-A", lambda B, r, s: E.catwalk(B, s["chapter"]), "reinforced_steel", "mid", "bottom_centre",
              "Raised catwalk module 4 m long, deck top at 0.6 m, rail at 1.6 m", dims_m=[4.0, 1.6, 1.2]),
        _spec(ch, "ENV", "CEILING_TRUSS-A", lambda B, r, s: E.truss(B, s["chapter"]), "reinforced_steel", "mid",
              "bottom_centre", "Ceiling truss 8 m long with light fittings below (origin at the fittings' underside)",
              dims_m=[8.0, 0.88, 0.8]),
        _spec(ch, "ENV", "MASSING_BLOCK-A", lambda B, r, s: E.massing(B, s["chapter"]), mw, "mid", "bottom_centre",
              "Mid/background facility block 6 x 8 x 4 m with stepped tiers and window bands", dims_m=[6.0, 10.0, 4.0]),
        _spec(ch, "ENV", "MASSING_TOWER-B", lambda B, r, s: E.massing(B, s["chapter"], 3.0, 12.0, 3.0, 4), mw, "mid",
              "bottom_centre", "Background tower 3 x 12 x 3 m", dims_m=[3.0, 14.0, 3.0]),
        _spec(ch, "ENV", "LEDGE_STATIC-A", lambda B, r, s: E.static_ledge(B, s["chapter"], 2.0, 0.3), mf, "static", "centre",
              "Static ledge, collision rect 200 x 30 px, depth 1.6 m", fit=(2.0, 0.3, 1.6), reference_size_px=[200, 30],
              depth_m=1.6, frame=1.1),
        _spec(ch, "ENV", "PLINTH_STATIC-A", lambda B, r, s: E.static_plinth(B, s["chapter"], 1.0, 0.6), mf, "static",
              "centre", "Static plinth, collision rect 100 x 60 px, depth 1.6 m", fit=(1.0, 0.6, 1.6),
              reference_size_px=[100, 60], depth_m=1.6),
        _spec(ch, "PRP", "CRATE_STACK-A", lambda B, r, s: E.prop_crates(B, s["chapter"], r), "composite", "near",
              "bottom_centre", "Near-back dressing: stacked equipment crates", dims_m=[2.2, 1.4, 0.9]),
        _spec(ch, "PRP", "PIPE_RUN-A", lambda B, r, s: E.prop_pipes(B, s["chapter"]), "reinforced_steel", "near",
              "bottom_centre", "Near-back dressing: 3 m pipe run on stands", dims_m=[3.0, 1.2, 0.5]),
        _spec(ch, "PRP", "CONSOLE-A", lambda B, r, s: E.prop_console(B, s["chapter"]), "electronic_module", "near",
              "bottom_centre", "Near-back dressing: operator console with three screens", dims_m=[1.6, 1.35, 0.8]),
        _spec(ch, "PRP", "TANK-A", lambda B, r, s: E.prop_tank(B, s["chapter"]), "reinforced_steel", "near",
              "bottom_centre", "Near-back dressing: vertical service tank 2.2 m", dims_m=[1.3, 2.2, 1.3]),
    ]
    for key, fn in LANDMARKS[ch]:
        out.append(_spec(ch, "PRP", key, fn, mw, "landmark", "bottom_centre",
                         f"Band landmark {key} (mid-back layer, z -4 .. -8)", budget=3000, landmark=True))
    return out


SPECS = [s for ch in CODE for s in specs_for(ch)]
