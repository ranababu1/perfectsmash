"""mk_ch_showcase3.py <chapter>: review pass 3 back band. Keeps the chapter's gameplay band (components,
operative) and grade keys from the current layout, replaces the environment back band with a chapter-specific
composition (distinct walls, landmark silhouettes, massing) and chapter accent lights and grade."""
import json, sys
ch = sys.argv[1]
GA = "/workspace/tfj-3d-kits/generated_assets"
P = f"{GA}/environments/showcase/{ch}_showcase_layout.json"
L = json.load(open(P))
C = {"vita": "vta", "nova_grid": "nvg", "civitas": "cvt", "meridian": "mrd"}[ch]
e = lambda n: f"environments/{ch}/{C}_{n}.glb"
keep = [it for it in L["items"] if not it["f"].startswith("environments/")]
items = []
for z, kind in ((3, "floor_tile_b"), (-1, None), (-5, "floor_tile_a")):
    for x in (-10, -6, -2, 2, 6, 10, 14):
        k = kind or ("floor_trench_a" if x in (-6, 6) else "floor_tile_b")
        items.append(dict(f=e("env_" + k), p=[x, 0, z]))
W = lambda k, x, z=-6.6: dict(f=e("env_back_wall_" + k), p=[x, 0, z])
if ch == "nova_grid":
    back = [W("b", -6), W("a", -2), W("b", 2), W("a", -10),
            dict(f=e("prp_transformer_yard_a"), p=[9.2, 0, -6.6]),
            dict(f=e("env_massing_block_a"), p=[1.5, 0, -11.5]),
            dict(f=e("env_massing_tower_b"), p=[-8.5, 0, -12.5]), dict(f=e("env_massing_tower_b"), p=[16.5, 0, -11.0]),
            dict(f=e("env_massing_tower_b"), p=[6.2, 0, -13.5], s=0.85),
            dict(f=e("prp_pipe_run_a"), p=[-4.8, 0, -3.6]), dict(f=e("prp_tank_a"), p=[1.3, 0, -3.8]),
            dict(f=e("prp_crate_stack_a"), p=[13.6, 0, -3.4]), dict(f=e("env_ceiling_truss_a"), p=[-2.0, 5.2, -4.2])]
    lights = [dict(p=[-2.0, 1.0, -5.3], c="ffae42", e=1.6, r=3.5), dict(p=[2.0, 2.8, -5.0], c="ffae42", e=1.2, r=3.5),
              dict(p=[-6.0, 2.8, -5.0], c="ffae42", e=1.0, r=3.5), dict(p=[-1.0, 5.0, -5.7], c="4aa8ff", e=2.4, r=3.5),
              dict(p=[9.2, 2.0, -4.0], c="ffae42", e=1.2, r=5.0), dict(p=[11.5, 4.5, -4.6], c="4aa8ff", e=1.2, r=4.0),
              dict(p=[3.0, 1.5, 1.0], c="ffcf8a", e=0.5, r=4.0),
              dict(type="spot", p=[-0.6, 4.0, 4.0], look=[-1.4, 0.8, 0.7], c="ffe6c8", e=1.4, r=8.0, angle=25)]
    grade = dict(ambient_color="8c8478", horizon_color="8a7c68", fog_color="241c14", sun_color="ffe8cc", rim_color="7fb0ff")
elif ch == "civitas":
    back = [W("a", -6), W("b", -2), W("a", 2), W("b", 6), W("b", -10),
            dict(f=e("prp_screen_wall_a"), p=[13.0, 0, -6.6]),
            dict(f=e("prp_sensor_tower_a"), p=[9.4, 0, -4.8]),
            dict(f=e("env_massing_block_a"), p=[-1.0, 0, -11.5]),
            dict(f=e("prp_relay_spire_a"), p=[5.0, 0, -11.0]),
            dict(f=e("env_massing_tower_b"), p=[-9.0, 0, -12.0]), dict(f=e("env_massing_tower_b"), p=[17.5, 0, -11.5]),
            dict(f=e("env_low_wall_a"), p=[-3.6, 0, -3.4]), dict(f=e("prp_console_a"), p=[3.4, 0, -3.2])]
    lights = [dict(p=[-2.0, 3.0, -5.2], c="8ab4ff", e=1.4, r=5.0), dict(p=[6.0, 3.0, -5.2], c="8ab4ff", e=1.2, r=5.0),
              dict(p=[-7.0, 5.0, -5.8], c="ff3b4e", e=0.9, r=2.2), dict(p=[1.0, 5.0, -5.8], c="ff3b4e", e=0.9, r=2.2),
              dict(p=[9.4, 9.0, -3.6], c="ff3b4e", e=0.8, r=2.5), dict(p=[13.0, 3.0, -5.0], c="8ab4ff", e=1.4, r=5.0),
              dict(p=[3.0, 1.5, 1.0], c="9fc0ff", e=0.5, r=4.0),
              dict(type="spot", p=[-0.6, 4.0, 4.0], look=[-1.4, 0.8, 0.7], c="d8e6ff", e=1.5, r=8.0, angle=25)]
    grade = dict(ambient_color="6f86ae", horizon_color="6c8cb8", fog_color="141e2c", sun_color="d0e0ff", rim_color="8fb4ff",
                 saturation=1.0)
elif ch == "meridian":
    back = [W("a", -6), W("b", -2), W("a", 2), W("b", -10),
            dict(f=e("prp_temporal_anchor_a"), p=[6.4, 0, -6.0]),
            dict(f=e("prp_convergence_chamber_a"), p=[12.6, 0, -6.6]),
            dict(f=e("env_massing_block_a"), p=[6.2, 0, -11.5]),
            dict(f=e("env_massing_tower_b"), p=[-8.0, 0, -11.5]), dict(f=e("env_massing_tower_b"), p=[18.0, 0, -12.0]),
            dict(f=e("env_massing_tower_b"), p=[0.0, 0, -13.0], s=0.85),
            dict(f=e("env_low_wall_a"), p=[-4.6, 0, -3.4]), dict(f=e("prp_crate_stack_a"), p=[1.2, 0, -3.4])]
    lights = [dict(p=[-6.0, 2.6, -5.4], c="8f7cff", e=1.6, r=4.0), dict(p=[2.0, 2.6, -5.4], c="8f7cff", e=1.4, r=4.0),
              dict(p=[-2.0, 3.0, -5.5], c="7fe8ff", e=1.1, r=3.0), dict(p=[6.4, 4.5, -4.6], c="7fe8ff", e=1.4, r=4.0),
              dict(p=[12.6, 5.0, -5.0], c="8f7cff", e=1.8, r=6.0), dict(p=[3.0, 1.5, 1.0], c="b4a8ff", e=0.5, r=4.0),
              dict(type="spot", p=[-0.6, 4.0, 4.0], look=[-1.4, 0.8, 0.7], c="e4e0ff", e=1.5, r=8.0, angle=25)]
    grade = dict(ambient_color="7e78a0", horizon_color="7a70a8", fog_color="1a1628", sun_color="e6e2ff", rim_color="a090ff")
else:  # vita
    back = [W("a", -6), W("b", -2), W("a", 2), W("b", 6), W("a", 10), W("b", 14), W("b", -10),
            dict(f=e("prp_growth_chamber_a"), p=[10.6, 0, -4.2]),
            dict(f=e("env_massing_block_a"), p=[1.0, 0, -11.5]),
            dict(f=e("env_massing_tower_b"), p=[-8.0, 0, -11.5]), dict(f=e("env_massing_tower_b"), p=[17.0, 0, -12.0]),
            dict(f=e("prp_console_a"), p=[-4.2, 0, -3.2]), dict(f=e("prp_tank_a"), p=[1.4, 0, -3.6])]
    lights = [dict(p=[10.6, 2.2, -3.0], c="62e3a4", e=1.2, r=5.0), dict(p=[-2.0, 2.0, -5.3], c="62e3a4", e=0.9, r=3.5),
              dict(p=[6.0, 2.0, -5.3], c="62e3a4", e=0.9, r=3.5), dict(p=[2.0, 3.5, -5.0], c="e8fff4", e=0.8, r=4.0),
              dict(p=[3.0, 1.5, 1.0], c="d8fff0", e=0.4, r=4.0),
              dict(type="spot", p=[-0.6, 4.0, 4.0], look=[-1.4, 0.8, 0.7], c="eef8f4", e=1.4, r=8.0, angle=25)]
    grade = dict(ambient_color="90a6a0", horizon_color="a0b8b0", fog_color="1a2624", sun_color="eef8f4", rim_color="a8e8d0")
for k in ("ambient_color", "horizon_color", "fog_color", "sun_color", "rim_color", "saturation"):
    L.pop(k, None)
L.update(grade)
L["lights"] = lights
L["items"] = items + back + keep
json.dump(L, open(P, "w"), indent=1)
print("LAYOUT3", ch, len(L["items"]), "focus", L["focus"])
