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

**Renderer and performance impact** (Android emulator x86_64; logs in `docs/benchmarks/2026-11-10-helix-sliceA/`; not representative of phone GPUs):

| Build | Renderer | fps | Draw calls | Video memory | Viewport CPU render | Worst frame, breach scenario | Restart |
|---|---|---|---|---|---|---|---|
| greybox `503347c` | Compatibility | 55-60 | ~120 | 35-37 MB | 2-3.7 ms | 38 ms | 32-63 ms |
| slice A `4e2798a` | Compatibility | 45-53 | ~1,800 | 94-96 MB | 9-13 ms | 1,739 ms (damage-state meshes compiled mid-play) | 630-950 ms |
| slice A `4e2798a` | Mobile | 48-55 | ~184 | 141-155 MB | ~4 ms | 660 ms | 210-345 ms |
| slice A + batching `88e3ce6` | Compatibility | 48-55 | ~540-690 | 94-96 MB | 7.4-8.4 ms | **66 ms** | 550-800 ms |

Initial load (first frame) is 9-10 s on the emulator. APK 74.5 MB (only integrated assets). Open performance work for slice E: keep the set across restarts (instancing ~70 models costs ~650 ms per restart), fewer component surfaces/shadow casters, physical-device numbers.

**Missing dependencies.** Operative and weapon meshes: the library now contains weapon models (`OPR-WPN-*`) but no operative model; both are for slice C. Debris sets, damage overlays and VFX: slice B (below).

**Rights / release blockers.** All integrated entries are `pending_review`; rights notes say AI-assisted or AI-generated work is not commercially cleared. Commercial release needs the owner's review of each entry. `assets/audio/music/gameplay_bed.ogg` rights remain unverified (existing blocker).

## Slice B: debris sets, damage overlays and gameplay VFX

**Implemented in a session without Godot; verified 2026-11-10** (import clean, 199 tests pass, captures `docs/images/assets/sliceB_*`). Textures now import VRAM-compressed; emulator Compatibility at `b649204`: 52-55 fps, 610-690 draw calls, video memory 93-97 MB, worst breach frame 68 ms, restarts 720-820 ms, eval APK 126 MB.

- **Debris** (`HLX-DEB-{AI_CORE-A, BLAST_WALL-A, CORE_SHIELD-A, POWER_CELL-A, RELAY_DISH-A, RELAY_MAST-B, SERVER_RACK-B, SERVICE_DECK-B, SUPPORT_COLUMN-B}`, 4-7 fragments each): `AssetLibrary.instance_debris` picks the set by kind and size like components; `DebrisSet` places it in the destroyed body's last pose and animates the fragments (seeded throw, gravity, floor bounce, shrink after 2.2 s). Contract 8 allows visual-only rigid bodies or particles; a scripted throw was chosen so no 3D physics is added.
- **Damage overlays** (`SHR-DMG-<MATERIAL>-LIGHT/HEAVY` for ai_core_module, composite, electronic_module, energy_component, glass_polymer, lightweight_alloy, reinforced_steel): surfaces in `mat_<material>_<ch>[_zone]` slots get a darkened copy (×0.85 damaged, ×0.72 critical) with the overlay as a transparent object-space triplanar `next_pass`, one tile per metre. Materials are shared per source surface and level. The overlay is chosen by the component's physics material.
- **VFX presets** (ui-vfx, `assets/vfx/godot/presets/`): `breach_explosion`, `impact_metal/glass/electric/concrete` (by physics material), `kinetic_impact`, `kinetic_muzzle`, `component_collapse`, `critical_core_destroyed`, `critical_core_idle`. Pools of 1-3 per preset, restarted on use; every preset and debris set is drawn once under the floor during load. Textures integrated: `OPR-VFX-BREACH_{ACTIVATION,DEBRIS,EXPLOSION,SHOCKWAVE}-A`, `OPR-VFX-KINETIC_{IMPACT,MUZZLE}-A`, `SHR-VFX-{CRITICAL_CORE_DESTRUCTION, CRITICAL_CORE_IDLE, DEBRIS_CHIP_SMALL, DUST_COLLAPSE, DUST_CONCRETE, ENERGY_DISCHARGE, IMPACT_ELECTRIC, IMPACT_GLASS, IMPACT_METAL, PARTICLE_SPARK, SMOKE_PUFF}-A`.
- **Performance risk to measure:** the overlay `next_pass` adds a transparent draw per damaged main surface; particle quads are alpha-blended or additive. Measure with `mission_benchmark` (breach scenario) on the emulator and a physical device before approving.
- **Deferred:** CRITICAL sparking loops from `fx_spark_*` empties, emission flicker, projectile trails, upgrade-tier VFX.

## Slice D: Helix music, ambience and sound effects

**Implemented and verified** (`91d1967`): tests, windowed run, Android emulator install and play. Not yet reviewed by ear.

- **Source:** the audio already on `main` (identical to the latest `assets` delivery, checked by file hash). 90 files, slice `D_helix_audio` in `data/integrated_assets.json`.
- **Music cues:** `helix_prep` (`HLX-MUS-GAMEPLAY-PREP`), `helix_gameplay` (`HLX-MUS-GAMEPLAY-TENSION`), `helix_combat` (`HLX-MUS-COMBAT-01`), `helix_critical_layer` (`HLX-MUS-CRITICAL_LAYER-01`), `victory_mission` / `defeat_mission` (`GAM-MUS-VICTORY-MISSION`, `GAM-MUS-DEFEAT-MISSION`), `menu` (`GAM-MUS-MENU-01`), `cinematic` (`GAM-MUS-OPENING-01`), `legacy_bed` (unchanged legacy file).
- **Ambience:** `helix_server_hall`, `helix_core`, `helix_cooling` (`HLX-AMB-*-01`); helix_01 plays the server hall.
- **Sound effects:** `OPR-SFX-KINETIC_FIRE-01..05`, `OPR-SFX-BREACH_LAUNCH-01..04`, `OPR-SFX-BREACH_EXPLOSION-01..05`, `OPR-SFX-WEAPON_SWITCH-01..03`, `OPR-SFX-RELOAD_READY-01..03`, `SHR-SFX-IMPACT_{METAL,GLASS,COMPOSITE,CONCRETE}-*`, `SHR-SFX-ELECTRIC_SHORT-*`, `SHR-SFX-{STRUCTURE_COLLAPSE,MACHINE_FAILURE,ENERGY_DISCHARGE,SECONDARY_BLAST}-*`, `HLX-SFX-CORE_DESTROYED-01..03`, `SHR-SFX-ALARM_PULSE-01`, `GAM-SFX-UI_{CLICK,CONFIRM,BACK,OBJECTIVE_COMPLETE,VICTORY,DEFEAT}-*`.
- **Scripts:** `scripts/core/audio_catalog.gd`, `scripts/services/audio_service.gd`, `scripts/services/music_director.gd`, new `scripts/mission/mission_audio.gd`, `scripts/mission/mission_screen.gd`, `scripts/main.gd`; `default_bus_layout.tres`; loop flags in 8 Ogg imports.
- **Rights:** all `pending_review`; the asset notes describe original synthesised and algorithmic work, not commercially cleared until reviewed. `gameplay_bed.ogg` remains unverified.

## Slice C: HUD, typography, operative and weapons

**Implemented and verified** (tests, captures; emulator run pending with slice E).

- **Asset ids:** `GAM-UI-THEME-A` (+ fonts `GAM-FNT-CHAKRA_PETCH-*`, `GAM-FNT-BARLOW-*`, UI kit textures as dependencies), icons `GAM-ICN-{OBJECTIVE_PRIMARY,OBJECTIVE_OPTIONAL,OBJECTIVE_COMPLETE,OBJECTIVE_FAILED,CRITICAL_ASSET,SHOTS_FIRED,TIME_LIMIT,AMMO,PAUSE,RETRY,WEAPON_KINETIC_ACCELERATOR,WEAPON_BREACH_CHARGE}-A`, `OPR-CHR-OPERATIVE-A`, `OPR-WPN-KINETIC_ACCELERATOR-A`, `OPR-WPN-BREACH_CHARGE-A`, `OPR-PRJ-KINETIC_SLUG-A`, `OPR-PRJ-BREACH_CANISTER-A`.
- **Scripts:** `scripts/mission/mission_hud.gd`, `scripts/mission/view/operative_rig.gd`, `scripts/mission/view/mission_view.gd`, `scripts/mission/view/asset_library.gd`, `scripts/mission/mission_screen.gd`; tools `build_integration_manifest.py`, `export_filter.py`.
- **Visible:** themed panels, chips and buttons; weapon buttons with icons and live ammunition; objective state icons; red critical-asset marker over the core; hooded operative aiming, recoiling, reloading and switching weapons; slug and canister projectiles.
- **Rights:** fonts SIL OFL 1.1 (cleared for embedding, licences shipped); everything else `pending_review`, not commercially cleared.
