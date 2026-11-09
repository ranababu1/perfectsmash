# Godot validation harness (Godot 4.7.2 stable)

| Script | What it does | Needs |
|---|---|---|
| `run_import_check.sh [report.json]` | Copies the working tree (no `.git`) to `/tmp/tfj-godot-check/project`, runs `godot --headless --import`, then `load_check.gd`, which loads every glb, png, webp, ogg, wav and font in `generated_assets/asset_manifest.json` and records type, size, tris, AABB, materials, animation names and audio length. Non-zero exit on any failure. | Godot only (headless) |
| `render_previews.sh [out_dir] [--only=helix,vita]` | Renders, under the exact MissionView camera, sun, ambient, floor, back wall and seeded backdrop blocks: `mission_<chapter>.png` (the `helix_01` layout with each chapter's kit mapped onto its roles, greybox boxes where a mesh is missing), `kit_<chapter>.png`, `props_<chapter>.png`, `states_<chapter>.png` (intact, light, heavy, debris using the contract's damage hook). | Xvfb + software OpenGL (llvmpipe). `--headless` cannot render. Run `run_import_check.sh` first |

Calibration (2026-11-09): the harness render of the greybox `helix_01` differs from the game's own `tools/capture_mission.gd` frame in 2.8% of pixels (HUD and operative arm pose only); geometry and framing match. See `../../docs/previews/baseline_*.webp`.

Binaries: `/opt/tfj-tools/bin/godot` (override with `GODOT=`), temp project `TFJ_GODOT_WORK=`.
