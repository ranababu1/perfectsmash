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
