# weapons/

Weapon meshes, projectiles and related presentation for Chapter I weapons first.

## Intended contents

- Kinetic Accelerator: distinctive electromagnetic precision launcher (not a conventional assault rifle). Clean isolated views, placeholder mesh, later gameplay mesh.
- Breach Charge: launcher that fires lobbed canisters (matches `data/weapons.json` delivery = lobbed). Canister projectile mesh/sprite, arming cue art.
- Projectile and muzzle/impact presentation assets (simple meshes and/or VFX textures).
- Later chapters: Penetrator, Pulse Cannon, Disruptor, Temporal Lance (design only until mechanics are validated).

## Godot use

Presentation meshes and VFX attached to weapon / projectile nodes. Physics, ammunition, cooldown and delivery curves stay in `WeaponCatalog` / `WeaponState`.

## render_type

- Weapon bodies: `mesh` (placeholder primitives acceptable for Helix prototype).
- Projectiles: simple `mesh` and/or `sprite`.
- Muzzle, trail, impact: mostly `sprite` / particles under `../vfx/`.
- HUD weapon icons: `ui`.

## Design constraints

- Reserve orange/amber for weapon energy and danger cues; do not flood every surface with glow.
- Kinetic = sharp, linear, cyan/blue energy language. Breach = radial blast, hazard striping, clearly different silhouette.
