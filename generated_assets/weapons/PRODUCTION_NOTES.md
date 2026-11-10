# Weapons: production notes (3d-kits stream)

The weapon set lives in `weapons/shared/` and is built by `destructibles/source/blender/kits/weapons.py` through `runenv.py`. The material palette is "arsenal" (gunmetal, cyan and amber).

| Id | Notes |
|---|---|
| `OPR-WPN-KINETIC_ACCELERATOR-A/B/C` | Three upgrade tiers. Follows the SV-02 concept: angular shell, ribbed coil accelerator, ported muzzle, skeletal stock and cyan lines. |
| `OPR-WPN-BREACH_CHARGE-A/B/C` | Three upgrade tiers. Follows the SV-03 concept: blocky launcher body, octagonal side drum with an amber ring, front loop bracket and a hazard panel. |
| `OPR-PRJ-KINETIC_SLUG-A` | Projectile, centred, travels along +X. |
| `OPR-PRJ-BREACH_CANISTER-A` | Projectile, centred, travels along +X. |
| `OPR-WPN-PENETRATOR-A`, `-PULSE_CANNON-A`, `-DISRUPTOR-A`, `-TEMPORAL_LANCE-A` | Future weapons. Concept-level blockouts only, not production art. |

## Conventions

- **Origin.** The origin is the grip (hand contact point), with the barrel along +X and up +Y. A `muzzle` empty marks the bore exit.
- **Mounting.** Mount the weapon on the operative's `weapon_socket` with no offset.
- **Budget.** At most 2,500 tris. Actual counts are 896 to 1,760 for the tiers, 152 to 582 for the projectiles and 152 to 640 for the blockouts.
- **Materials.** Slots follow the kit convention (`mat_lightweight_alloy_opr[_<zone>]`, `trim_*_opr`, `emit_*_opr`). Colour is in the material, with no `COLOR_0`.

## Commands

    cd generated_assets/destructibles/source/blender
    TFJ_SAMPLES=32 blender -b --factory-startup --python runenv.py -- kits.weapons [--no-render]
    python3 sheets.py grid ../../../weapons/previews/opr_weapons_sheet.webp "/workspace/tfj-masters/3d-kits/stats_env/OPR-*.json" "<title>" 4

The Godot mount check is `characters/PRODUCTION_NOTES.md` (`char_check.gd`).

## Rights

This is original procedural work. The scripted Blender code was written by the 3d-kits asset agent (AI-assisted authorship). The form language follows the project concept frames SV-02 and SV-03; no concept pixels are used. Ownership is not legally settled, and nothing is marked commercially cleared.

## Premium uplift pass (2026-11-10)

All 12 weapon and projectile files were rebuilt in place. Ids and file names are unchanged.

- **Kinetic Accelerator A to C (SV-02).** A coilgun silhouette rather than a rifle:
  - a sweeping upper spine with a receiver hump, an optic block and a side ammo readout;
  - an exposed, larger ribbed coil stack between collars, with a glowing feed ring;
  - a lower rail with a cyan line, a forward bracket and a thicker ported muzzle;
  - a thumbhole stock with a real triangular opening.
  - Tier B adds a capacitor pack and cable. Tier C adds heat sinks, a third rail and a second capacitor.
- **Breach Charge A to C (SV-03).**
  - Layered gunmetal plates, an octagonal side drum with a bolted bezel and an amber-ringed core, and a loop bracket with amber slots.
  - The muted hazard inlay is shorter, and there is a carry handle and belly louvres.
  - Amber is limited to slots, rings and small lights.
  - The canister has dark end caps with panel blocks, three muted diagonal hazard bands and two amber ring slits.
- **Grip.** One shared grip on every weapon: raked, with finger ridges, a trigger guard, a trigger and a thumb rest. The grip origin is unchanged, so weapon_socket mounting is the same.
- **Materials.**
  - Each file embeds one baked set (512 for weapons, 256 for projectiles) in a single slot, `wpn_<stem>`.
  - The bake routes base colour and metallic through emission bakes, because Cycles' diffuse colour pass darkens metals. AO is baked at an asset-scaled distance.
  - The palette was tuned against the Godot MissionView frame, not the Cycles preview. Godot shows these greys lighter than Cycles does.
- **Budgets.** Every file is within budget: KA 1,460 / 1,664 / 1,916 tris, Breach 1,064 / 1,088 / 1,208, canister 582, slug 152. The glbs are 0.1 to 0.9 MB.
- **Checks.** The Godot 4.7.2 GL Compatibility lineup loads 12 of 12 files.
- **Previews.**
  - `previews/opr_weapons_showcase_missionview.webp`: MissionView lighting, the honest in-game read.
  - `previews/opr_weapons_showcase_graded.webp`: the showcase grade. Its reflection sky lifts the metals.
  - `previews/opr_weapons_sheet.webp`: Cycles.
  - The layout is `environments/showcase/weapons_showcase_layout.json`.
- **Limit.** The self-bake keeps the zone surfaces but not the library normal detail: the normal map is close to flat. Real normal detail would need a high-poly sculpt pass.

## Kinetic Accelerator premium pass 2 (2026-11-10, after owner review)

Review note: the first SV-02 pass still read as a stocked rifle. Rebuilt in `kits/weapons.py`; the Breach launcher and canister are unchanged (kept after review).

- Silhouette: an open electromagnetic coil and rail accelerator. A compact wedge receiver over the shared grip slopes down to the rear; the rifle stock is gone, replaced by a small angled energy cell with a short rubber brace.
- Coils dominate: a large exposed stack of dark ribbed windings carried between two heavy rails, with a cyan energy band in every gap and a cyan core, cyan strips on the rail inner faces, a forward bracket tying the rails and a ported muzzle projector.
- Tiers differ in coil count and shroud: A has 4 coils, fully open. B has 6 coils, a vented top shroud over the rear half of the stack and a capacitor pack. C has 8 coils, a full-length armoured top shroud, three shroud bands, heat-sink fins, a cyan side rail and twin capacitors.
- Tris: A 1,456, B 1,876, C 2,388 (budget 2,500, no decimation). One 512 baked set each.
- Godot showcase: `emission_scale` (graded frames only, layout opt-in) trims emission so the cyan bands do not clip to white under ACES; the MissionView frame is untouched.
- Previews (after): `previews/opr_weapons_showcase_graded.webp`, `previews/opr_weapons_showcase_missionview.webp`, `previews/opr_weapons_sheet.webp`. Before: the same paths at commit `218ced4`.

## Future-weapon blockouts re-render (2026-11-10)
- Penetrator, Pulse Cannon, Disruptor and Temporal Lance rebuilt with the current pipeline (240, 664, 248 and 728 tris). They remain blockouts for scale and silhouette only, not final art. Godot lineup: all weapons/shared files load. Sheet: weapons/previews/opr_weapons_sheet.webp.
