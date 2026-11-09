# vfx/

Gameplay visual effects: flipbook sprite sheets, particle textures, upgrade-tier variants and Godot CPUParticles3D presets.

- `shared/`: weapon (OPR) and shared (SHR) effects; `shared/particles/` single particle textures; `shared/tiers/` upgrade-tier variants.
- `helix/`, `vita/`, `nova_grid/`, `civitas/`, `meridian/`: chapter effects.
- `vfx_index.json`: manifest entries (frames, grid, fps, loop, blend, pivot) for every sheet; `upgrade_tiers.json`: tier and tint mapping.
- `godot/presets/`: 11 ready-made CPUParticles3D scenes (validated with Godot 4.7.2); `godot/tools/`: build, load and render scripts.
- `previews/`: contact sheets, animated WebP previews and in-engine renders.
- `_build/`: the generators (`build_all.sh`).

See `PRODUCTION_NOTES.md` for the table of every sheet, how to set them up in Godot, the validation log and rights notes.

## render_type

`sprite` (flipbooks and variant atlases) and `texture` (trails, particle textures, threshold line).
