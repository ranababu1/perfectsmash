# destructibles/

Modular gameplay components whose front face matches the 2D physics rectangle.

## Intended contents (Helix prototype kinds from `data/missions/helix_01.json`)

| kind | Approx. front face (px) | Material id |
|---|---|---|
| `blast_wall` | 30 × 140 | reinforced_steel |
| `server_rack` | 40 × 100 | electronic_module |
| `support_column` | 26 × 160 | lightweight_alloy |
| `service_deck` | 200 × 24 | composite |
| `ai_core` | 60 × 60 | electronic_module (critical) |
| `power_cell` | 36 × 40 | energy_component |
| `relay_mast` | 22 × 220 | lightweight_alloy |
| `relay_dish` | 70 × 24 | glass_polymer |

Plus damage-state treatment (material/decal swaps first; optional pre-fractured meshes later).

## Godot use

One glTF / mesh per kind. Scale: 100 physics px = 1 m. Pivot at geometric centre. Depth per kind (e.g. rack ~0.8 m). Coding agent maps mesh to each `DamageableComponent` body.

## render_type

`mesh`. Damage overlays and decals are 2D textures from `../materials/`. Destruction particles from `../vfx/`.
