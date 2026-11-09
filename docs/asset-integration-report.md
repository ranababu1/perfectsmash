# Asset Integration Report: Helix prototype

Development integration of the production asset library into the playable Helix mission. Owner approval 2026-11-10 covers **development use only**; it is not commercial release clearance. Rights and approval fields are copied unchanged from the library manifest.

- **Library:** `assets/` on `main` (moved from `generated_assets/` by the owner's PRs #2/#3), manifest `assets/asset_manifest.json`, stream fragments `assets/manifest_parts/`. Validator: `python assets/tools/validate_asset_manifest.py` → 1439 entries present, PASS; `--check` 0 warnings (2026-11-10).
- **What the game uses:** `data/integrated_assets.json`, built by `tools/assets/build_integration_manifest.py` from the ids in `tools/assets/integration_selection.json`. Textures that an integrated model references are added automatically (`slice: "dependency"`, `required_by`).
- **What builds ship:** only integrated files. `tools/assets/export_filter.py` turns the integration manifest into the export exclude filter (`--apply export_presets.cfg`; `make_eval_project.py` uses it). Without it the Android APK was 245 MB; with it 74 MB.
- **Contract:** `assets/docs/ASSET_CONTRACT.md` (v1.7) is binding: 100 px = 1 m, front face = physics rectangle, mesh centred on z = 0, depth per kind, centre pivots, one damage-state node visible at a time, material slot naming.

## Slice A: Helix structures, environment and materials

**Implemented.**
- `AssetLibrary` (`scripts/mission/view/asset_library.gd`): indexes the integration manifest; picks the component variant whose `reference_size_px` needs the least stretch; scales X/Y to the physics rectangle (depth unchanged); shows one of `mesh_intact` / `mesh_light` / `mesh_heavy`; binds chapter normal/ORM maps by slot name only where a surface has no texture of its own (the current kit exports bind their texture sets themselves).
- `ComponentVisual` (`scripts/mission/view/component_visual.gd`): one per component; production model, or the greybox box when no model exists (missing art never breaks a level). Follows its physics body every frame; switches damage-state nodes with `DamageableComponent` states; draws every state node during the first frames so their shaders compile at load.
- Set dressing from `data/environments/helix_01.json` (pieces, repeats, shadows), statics from the kit ledge/plinth scaled to the static rectangle. Repeated pieces are drawn as one MultiMesh per mesh.
- Lighting for the textured kit: graphite fill (ambient `#6c7a88` at 0.42), sun 1.0, reflection-only procedural sky (contract §9 proposed source), depth fog `#121820` density 0.035.

**Asset ids integrated (55 selected + 21 texture dependencies).**
- Components: `HLX-CMP-AI_CORE-A`, `HLX-CMP-BLAST_WALL-A`, `HLX-CMP-CORE_SHIELD-A`, `HLX-CMP-POWER_CELL-A`, `HLX-CMP-RELAY_DISH-A`, `HLX-CMP-RELAY_MAST-B`, `HLX-CMP-SERVER_RACK-B`, `HLX-CMP-SERVICE_DECK-B`, `HLX-CMP-SUPPORT_COLUMN-B`.
- Environment: `HLX-ENV-BACK_WALL-A/-B`, `HLX-ENV-CATWALK-A`, `HLX-ENV-CEILING_TRUSS-A`, `HLX-ENV-FLOOR_TILE-A/-B`, `HLX-ENV-FLOOR_TRENCH-A`, `HLX-ENV-LEDGE_STATIC-A`, `HLX-ENV-PLINTH_STATIC-A`, `HLX-ENV-LOW_WALL-A`, `HLX-ENV-MASSING_BLOCK-A`, `HLX-ENV-MASSING_TOWER-B`, `HLX-ENV-PILLAR-A`; props `HLX-PRP-CONSOLE-A`, `HLX-PRP-PIPE_RUN-A`, `HLX-PRP-TANK-A`, `HLX-PRP-CRATE_STACK-A`, `HLX-PRP-COOLING_TOWER-A`, `HLX-PRP-RELAY_ARRAY-A` (band-1 landmark).
- Materials: `HLX-MAT-{COMPOSITE,CONCRETE,ELECTRONIC_MODULE,ENERGY_COMPONENT,FLOOR,GLASS_POLYMER,LIGHTWEIGHT_ALLOY,REINFORCED_STEEL}-A` (albedo, normal, ORM, emission where delivered); dependencies `SHR-MAT-{BRUSHED_STEEL,CABLE_BUNDLE,CARBON_COMPOSITE,FROSTED_POLYMER,GUNMETAL,PAINTED_PANEL,RUBBER}-A` (+ normal, ORM).

**Scenes and scripts changed.** `scripts/mission/view/mission_view.gd`, new `asset_library.gd`, `component_visual.gd`; data `data/integrated_assets.json`, `data/environments/helix_01.json`; tools `tools/assets/*`, `tools/capture_helix.gd`; tests `tests/test_assets.gd`.

**Visible in gameplay.** A dark graphite server hall: tiled floor with cyan trench lines, back walls with windows and vents, pillars, catwalk, ceiling truss, cooling tower and the relay array behind the structure, consoles, pipes and tanks in the near back; the real blast wall, columns, deck, racks, power cell, relay mast and dish, steel shield and the white/red AI core under its marker. Damage states switch on the models (after a column breach the core shows its heavy-damage geometry). The operative and weapons are still the deliberate placeholder (see dependencies).

**Screenshots** (`docs/images/assets/`, 1280 × 720, same camera): before `sliceA_before_greybox_start.webp`; after `sliceA_after_1_start`, `_2_aim_kinetic`, `_4_breach_detonation`, `_5_core_exposed`, `_6_aim_finish`, `_8_result`; Android emulator `sliceA_emulator_start.webp` (2856 × 1280).

**Tests and import.** Godot import of the whole library: no errors (33 s). `tests/test_assets.gd`: every integrated file loads; rights fields present and not marked cleared; best variant per kind; front face inside the physics rectangle for every helix_01 component; state nodes; slot binding; model texture dependencies integrated; the view uses models and the set.

**Missing dependencies.** Operative and weapon meshes: the library now contains weapon models (`OPR-WPN-*`) but no operative model; both are for slice C. Debris sets, damage overlays and VFX: slice B.

**Rights / release blockers.** All integrated entries are `pending_review`; rights notes say AI-assisted or AI-generated work is not commercially cleared. Commercial release needs the owner's review of each entry. `assets/audio/music/gameplay_bed.ogg` rights remain unverified (existing blocker).
