# materials/

Tileable texture sets, ORM maps and decals for the seven gameplay materials in `data/materials.json`.

## Intended contents

Per material (`lightweight_alloy`, `reinforced_steel`, `composite`, `glass_polymer`, `concrete`, `electronic_module`, `energy_component`, and `ai_core_module` for Helix, VITA and Civitas):

- Albedo (tileable, flat-lit, no baked shadows).
- Normal.
- Roughness / metallic or packed ORM.
- Damage overlays (damaged, critical).
- Shared decals: scorch, impact crack, warning stripe, panel seam.

Resolutions: 512² standard, 1024² hero (AI core). Mobile-compressed on Godot import (ETC2/ASTC).

## Godot use

Applied to destructible and environment meshes. Visuals stay separate from physical material stats in `MaterialCatalog`.

## render_type

2D texture art consumed by `mesh` materials. Decals may also be `sprite`-style transparent PNGs.
