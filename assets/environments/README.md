# environments/

Chapter environment kits, backdrop plates and set dressing.

## Intended contents

- Helix Systems server-hall modular kit (floors, back walls, distant racks as low-contrast cards).
- Later: VITA, Nova Grid, Civitas, Meridian kits with distinct palettes.
- Cinematic environment plates used as stills live under `../cinematics/`; this folder is for gameplay-plane and parallax set pieces.

## Godot use

3D modular pieces and textured cards parented under the mission presentation root. Keep low contrast behind destructible gameplay components. Parallax / depth is visual only; no depth-axis collision.

## render_type

- Near/mid architecture: `mesh`.
- Far background cards and matte plates: textured quads (`mesh` + 2D texture) or 2D layers as the coding agent prefers.
