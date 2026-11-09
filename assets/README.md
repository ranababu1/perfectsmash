# Generated assets

Working tree for Temporal: First Jump art, animation, audio and related production files produced by the asset agent.

This folder is the staging area for new visual and audio work. It sits alongside the existing shipped paths under `assets/` (app icons and the current gameplay music bed). Nothing here is claimed as integrated into Godot until the coding agent imports it and the asset manifest marks it as such.

## Layout

| Folder | Contents | Typical `render_type` |
|---|---|---|
| `characters/` | Operative concepts, placeholders, later character packs | `mesh` (placeholder first), concept `sprite` sheets |
| `weapons/` | Kinetic Accelerator, Breach Charge and later weapons | `mesh` + projectile/VFX `sprite` |
| `environments/` | Chapter kits, backgrounds, set dressing | `mesh` + textured cards |
| `destructibles/` | Modular gameplay components and damage variants | `mesh` |
| `materials/` | Tileable texture sets, ORM maps, decals | texture (2D art on meshes) |
| `vfx/` | Flipbooks, particles, sparks, blast flashes | `sprite` / particles |
| `ui/` | HUD, icons, branding (replacing Perfect Smash icons later) | `ui` |
| `cinematics/` | Narrated stills and short accent clips | stills (2D) / occasional `video` |
| `audio/` | Music masters (when licensed), SFX, ambience, VO exports | `audio` |
| `fonts/` | Licensed UI fonts only | font |
| `tools/` | Manifest validation and asset-side helpers | n/a |
| `docs/` | References index and notes that must not edit `docs/` on main | n/a |

## Key files

- `asset-production-plan.md` - first-response production plan (brief §26), updated for Option B rendering.
- `asset_manifest.json` - machine-readable inventory. **Existing** entries list real repo paths. **Planned** entries are not present on disk.

## Rules

- Prefer simple modular 3D geometry with 2D textures over heavy character modelling.
- Do not mark AI-generated work as commercially cleared.
- Do not commit unlicensed music. Do not touch `assets/music/` or `assets/audio/music/gameplay_bed.ogg` from this tree.
- Keep the first milestone to a small Helix Systems prototype, gated on the coding agent's Batch 3 greybox.
