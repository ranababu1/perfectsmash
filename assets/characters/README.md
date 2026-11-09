# characters/

Operative design and later character packs for Temporal: First Jump.

## Intended contents

- Concept sheets (orthographic and three-quarter views) for the anonymous hooded operative.
- Greybox / placeholder mesh or primitive stand-in used until the Batch 3 visual test is approved.
- Later: gameplay-scale mesh, simple animation set (idle, ready, aim, fire/recoil, reload/cooldown, reaction), chapter suit trim variants.

## Godot use

Attached as a 3D presentation node driven by the operative's 2D physics / mission position. Collision stays in the 2D plane. The coding agent owns the scene wiring.

## render_type

- Concepts and sheets: reference images (not imported as gameplay sprites).
- Placeholder and final body: `mesh`.
- Optional silhouette icons for UI: `ui`.

## Milestone note

Do not commit expensive character modelling yet. Owner decision: final representation after the Helix greybox visual test.
