# VFX library: production notes (stream ui-vfx)

Branch `assets` only. Staging work under `assets/vfx/`; nothing is wired into the game. Approval status of every file: `pending_review`.

## Summary

- 39 base sheets and textures: 32 animated or variant sprite sheets plus 7 static textures (trails, particle textures, threshold line), and 12 upgrade-tier variants (`shared/tiers/`). 51 manifest entries in `vfx_index.json`, merged into `manifest_parts/ui-vfx.json`.
- 11 Godot `CPUParticles3D` preset scenes (`godot/presets/*.tscn`) built, loaded and rendered with Godot 4.7.2 (see "Godot validation").
- Previews: `previews/vfx_contact_sheet.webp`, `previews/vfx_upgrade_tiers_contact_sheet.webp`, `previews/vfx_godot_render_contact_sheet.webp`, an animated WebP for every base sheet in `previews/anim/`, and in-engine animated renders in `previews/godot/`.
- Everything is procedural (Python numpy / scipy / Pillow, `_build/`); `_build/build_all.sh` regenerates the library from scratch (about 6 minutes, single-threaded, low memory).

## Format (ASSET_CONTRACT section 13)

- PNG RGBA, straight alpha, sRGB. Frames are square (128, 256 or 512 px), grids read left to right, top to bottom; every sheet is a power of two and at most 2048 px.
- Every frame has at least 3 px of fully empty border plus a soft fade window, so linear filtering and mipmaps cannot bleed between frames. The builder logs, per sheet, the maximum alpha on the outer 2 px (always 0) and the pre-window alpha in the outer ring (clipping check); sheets where sparks or smoke would have reached the frame edge were re-tuned until anything that reaches the ring is already fading out.
- Additive sheets (`"blend": "add"`): rgb is the emitted colour, alpha the intensity; hot cores go to white. They are designed to read on the game background `#15191E` without glow or bloom.
- Alpha-blended sheets (`"blend": "mix"`): smoke, dust and debris, lit from the upper left like the MissionView sun, with self-shadowing.
- Quantised with 1 LSB triangular dither, so soft gradients do not band.
- Amber is used only for weapon energy (Breach Charge), blasts, fire and danger; red only for the critical asset. Purple only in Meridian.

## Library

| Id | File | Frame / size | Frames (grid) | fps | Loop | Blend | Pivot [u, v] |
|---|---|---|---|---|---|---|---|
| CVT-VFX-SENSOR_DISRUPTION-A | `civitas/cvt_vfx_sensor_disruption_a.png` | 256 px | 16 (4x4) | 16 | yes | add | [0.5, 0.5] |
| HLX-VFX-DATA_CORRUPTION-A | `helix/hlx_vfx_data_corruption_a.png` | 256 px | 16 (4x4) | 15 | yes | add | [0.5, 0.5] |
| HLX-VFX-ELECTRICAL_OVERLOAD-A | `helix/hlx_vfx_electrical_overload_a.png` | 256 px | 16 (4x4) | 20 | no | add | [0.5, 0.5] |
| MRD-VFX-QUANTUM_INSTABILITY-A | `meridian/mrd_vfx_quantum_instability_a.png` | 256 px | 16 (4x4) | 16 | yes | add | [0.5, 0.5] |
| MRD-VFX-TEMPORAL_DISTORTION-A | `meridian/mrd_vfx_temporal_distortion_a.png` | 512 px | 16 (4x4) | 16 | yes | add | [0.5, 0.5] |
| NVG-VFX-ENERGY_OVERLOAD-A | `nova_grid/nvg_vfx_energy_overload_a.png` | 512 px | 16 (4x4) | 20 | no | add | [0.5, 0.5] |
| OPR-VFX-BREACH_ACTIVATION-A | `shared/opr_vfx_breach_activation_a.png` | 256 px | 8 (4x2) | 30 | no | add | [0.5, 0.5] |
| OPR-VFX-BREACH_ARMING-A | `shared/opr_vfx_breach_arming_a.png` | 256 px | 16 (4x4) | 16 | yes | add | [0.5, 0.5] |
| OPR-VFX-BREACH_DEBRIS-A | `shared/opr_vfx_breach_debris_a.png` | 512 px | 16 (4x4) | 24 | no | mix | [0.5, 0.5] |
| OPR-VFX-BREACH_EXPLOSION-A | `shared/opr_vfx_breach_explosion_a.png` | 512 px | 16 (4x4) | 24 | no | add | [0.5, 0.5] |
| OPR-VFX-BREACH_SHOCKWAVE-A | `shared/opr_vfx_breach_shockwave_a.png` | 512 px | 16 (4x4) | 30 | no | add | [0.5, 0.5] |
| OPR-VFX-BREACH_TRAIL-A | `shared/opr_vfx_breach_trail_a.png` | 512x128 texture | - | - | - | add | [1.0, 0.5] |
| OPR-VFX-KINETIC_IMPACT-A | `shared/opr_vfx_kinetic_impact_a.png` | 256 px | 16 (4x4) | 30 | no | add | [0.5, 0.5] |
| OPR-VFX-KINETIC_MUZZLE-A | `shared/opr_vfx_kinetic_muzzle_a.png` | 256 px | 8 (4x2) | 30 | no | add | [0.16, 0.5] |
| OPR-VFX-KINETIC_TRAIL-A | `shared/opr_vfx_kinetic_trail_a.png` | 512x64 texture | - | - | - | add | [1.0, 0.5] |
| OPR-VFX-WEAPON_COOLDOWN_CHARGE-A | `shared/opr_vfx_weapon_cooldown_charge_a.png` | 256 px | 16 (4x4) | 20 | yes | add | [0.5, 0.5] |
| OPR-VFX-WEAPON_COOLDOWN_READY-A | `shared/opr_vfx_weapon_cooldown_ready_a.png` | 256 px | 8 (4x2) | 24 | no | add | [0.5, 0.5] |
| SHR-VFX-ARC_ELECTRIC_LOOP-A | `shared/shr_vfx_arc_electric_loop_a.png` | 256 px | 16 (4x4) | 24 | yes | add | [0.5, 0.5] |
| SHR-VFX-CRITICAL_CORE_DESTRUCTION-A | `shared/shr_vfx_critical_core_destruction_a.png` | 512 px | 16 (4x4) | 24 | no | add | [0.5, 0.5] |
| SHR-VFX-CRITICAL_CORE_IDLE-A | `shared/shr_vfx_critical_core_idle_a.png` | 256 px | 16 (4x4) | 16 | yes | add | [0.5, 0.5] |
| SHR-VFX-DEBRIS_CHIP_SMALL-A | `shared/shr_vfx_debris_chip_small_a.png` | 128 px | 16 (4x4) | 1 | no | mix | [0.5, 0.5] |
| SHR-VFX-DEBRIS_FRAGMENT_LARGE-A | `shared/shr_vfx_debris_fragment_large_a.png` | 256 px | 16 (4x4) | 1 | no | mix | [0.5, 0.5] |
| SHR-VFX-DUST_COLLAPSE-A | `shared/shr_vfx_dust_collapse_a.png` | 512 px | 16 (4x4) | 16 | no | mix | [0.5, 0.86] |
| SHR-VFX-DUST_CONCRETE-A | `shared/shr_vfx_dust_concrete_a.png` | 256 px | 16 (4x4) | 20 | no | mix | [0.5, 0.5] |
| SHR-VFX-ENERGY_DISCHARGE-A | `shared/shr_vfx_energy_discharge_a.png` | 256 px | 16 (4x4) | 24 | no | add | [0.5, 0.5] |
| SHR-VFX-FIRE_LOOP-A | `shared/shr_vfx_fire_loop_a.png` | 256 px | 16 (4x4) | 20 | yes | add | [0.5, 0.94] |
| SHR-VFX-GLASS_SHARD-A | `shared/shr_vfx_glass_shard_a.png` | 128 px | 16 (4x4) | 1 | no | mix | [0.5, 0.5] |
| SHR-VFX-IMPACT_ELECTRIC-A | `shared/shr_vfx_impact_electric_a.png` | 256 px | 16 (4x4) | 30 | no | add | [0.5, 0.5] |
| SHR-VFX-IMPACT_GLASS-A | `shared/shr_vfx_impact_glass_a.png` | 256 px | 16 (4x4) | 30 | no | add | [0.5, 0.5] |
| SHR-VFX-IMPACT_METAL-A | `shared/shr_vfx_impact_metal_a.png` | 256 px | 16 (4x4) | 30 | no | add | [0.5, 0.65] |
| SHR-VFX-PARTICLE_GLOW-A | `shared/particles/shr_vfx_particle_glow_a.png` | 128x128 texture | - | - | - | add | [0.5, 0.5] |
| SHR-VFX-PARTICLE_RING-A | `shared/particles/shr_vfx_particle_ring_a.png` | 128x128 texture | - | - | - | add | [0.5, 0.5] |
| SHR-VFX-PARTICLE_SMOKE-A | `shared/particles/shr_vfx_particle_smoke_a.png` | 128x128 texture | - | - | - | mix | [0.5, 0.5] |
| SHR-VFX-PARTICLE_SPARK-A | `shared/particles/shr_vfx_particle_spark_a.png` | 128x32 texture | - | - | - | add | [0.5, 0.5] |
| SHR-VFX-SMOKE_LOOP-A | `shared/shr_vfx_smoke_loop_a.png` | 256 px | 16 (4x4) | 12 | yes | mix | [0.5, 0.95] |
| SHR-VFX-SMOKE_PUFF-A | `shared/shr_vfx_smoke_puff_a.png` | 256 px | 16 (4x4) | 16 | no | mix | [0.5, 0.5] |
| SHR-VFX-SPARK_BURST-A | `shared/shr_vfx_spark_burst_a.png` | 256 px | 16 (4x4) | 30 | no | add | [0.5, 0.5] |
| SHR-VFX-THRESHOLD_LINE-A | `shared/shr_vfx_threshold_line_a.png` | 512x64 texture | - | - | - | add | [0.5, 0.5] |
| VTA-VFX-CONTAINMENT_LEAK-A | `vita/vta_vfx_containment_leak_a.png` | 256 px | 16 (4x4) | 16 | yes | mix | [0.1, 0.5] |

Variant atlases (`DEBRIS_CHIP_SMALL`, `DEBRIS_FRAGMENT_LARGE`, `GLASS_SHARD`) are not animations: each cell is a different piece. In Godot set `anim_speed_min = anim_speed_max = 0`, `anim_offset_min = 0`, `anim_offset_max = 1` so every particle picks a random cell.

Seamless loops (`ARMING`, `COOLDOWN_CHARGE`, `SMOKE_LOOP`, `FIRE_LOOP`, `CONTAINMENT_LEAK`, `CRITICAL_CORE_IDLE`, `TEMPORAL_DISTORTION`, `QUANTUM_INSTABILITY`) loop without a seam: the smoke, fire and vapour loops scroll a noise field that tiles exactly once per cycle. `ARC_ELECTRIC_LOOP`, `DATA_CORRUPTION` and `SENSOR_DISRUPTION` are flicker loops (independent frames); start them on a random frame.

## Upgrade tiers

`upgrade_tiers.json` maps weapon upgrade tiers to sheets and scales. Base and Mk I use the `-A` sheets (Mk I adds 8% scale); Mk II and Mk III use the `-T2` / `-T3` sheets in `shared/tiers/`, which are gradient remaps of the base sheets (same frames, timing and pivot) to the HUD tier colours (Mk II `#5AA9FF`, Mk III `#B9F2FF`; Breach stays amber and gets hotter and whiter). Remaps keep the base intensity, so no frame drops out. It also lists the cooldown modulate per weapon (Kinetic cyan, Breach amber) and optional chapter tints for the neutral sheets. Preview: `previews/vfx_upgrade_tiers_contact_sheet.webp`.

## Godot use (Godot 4.7, GL Compatibility, mobile)

- Use `CPUParticles3D`, which the game already uses and which is the cheaper choice on mobile. Quad mesh, `material_override` = `StandardMaterial3D` with `shading_mode = unshaded`, `transparency = alpha`, `blend_mode = add` for additive sheets, `billboard_mode = particles`, `billboard_keep_scale = true`, `particles_anim_h_frames = columns`, `particles_anim_v_frames = rows`, `particles_anim_loop` as in the table, and `vertex_color_use_as_albedo = true` so the particle `color` tints.
- One-shot sheets: `amount = 1`, `one_shot = true`, `explosiveness = 1`, `lifetime = frames / fps`, `anim_speed_min = anim_speed_max = 1` (the flipbook then plays exactly once over the lifetime).
- Loops: `one_shot = false`, `particles_anim_loop = true`, `lifetime = frames / fps`.
- Flipbook frames only advance with `billboard_mode = particles`; with billboard disabled or Y-billboard the whole sheet is drawn (seen and fixed in the first render pass). Rotate with `angle_min` / `angle_max`. Use billboard disabled only for single textures such as the spark streak (`particle_flag_align_y = true`).
- Pivots are given as `[u, v]` in the frame; offset the particle node so the pivot sits on the event point (as the presets do for the muzzle, fire, smoke loop and collapse dust).
- Scale: the camera sits about 10.5 m from the play plane, so an effect needs to be at least about 1 m wide to read on a phone. Sizes in the presets: Breach fireball 3.1 m at blast_radius 140 px (scale the root by `blast_radius / 140`), shockwave 3.2 m, Kinetic hit 1.2 m, material impacts 1.1 to 1.4 m, collapse dust 4 m per 1.6 m of component width.
- The project uses filmic tonemapping, which softens additive whites a little; the sheets were checked in engine with that setting (see renders).
- Texture import: keep the default VRAM compression (ETC2 / ASTC on mobile); mipmaps on for the 512 px sheets.
- Suggested hook-up in `MissionView` (coding agent's call): `_on_blast` -> `vfx_breach_explosion.tscn`; `_on_impact` -> `vfx_kinetic_impact.tscn` plus the material preset from `data/materials.json` (metal, glass, electronic, concrete or composite); `_on_component_removed` -> `vfx_component_collapse.tscn` and the chapter destruction sheet; critical core -> `vfx_critical_core_idle.tscn` while alive and `vfx_critical_core_destroyed.tscn` on destruction; damaged state `sparking` -> `SHR-VFX-SPARK_BURST-A` and `SHR-VFX-ARC_ELECTRIC_LOOP-A` (ASSET_CONTRACT section 8), `burning` -> `vfx_burning_loop.tscn`.

### Preset scenes (`godot/presets/`)

| Scene | Emitters | Use |
|---|---|---|
| `vfx_breach_explosion.tscn` | debris, fireball, shockwave, activation flash, 6 smoke puffs, 28 spark streaks | Breach detonation |
| `vfx_kinetic_muzzle.tscn` | flash | Kinetic shot (pivot at the barrel tip) |
| `vfx_kinetic_impact.tscn` | hit flash | Kinetic hit, any material |
| `vfx_impact_metal.tscn`, `_glass`, `_electric`, `_concrete` | one each | Material response |
| `vfx_component_collapse.tscn` | collapse dust, 18 chips | Component removed at ground level |
| `vfx_burning_loop.tscn` | fire loop, smoke loop | Burning component |
| `vfx_critical_core_idle.tscn` | red pulse loop | Critical asset alive |
| `vfx_critical_core_destroyed.tscn` | burst, discharge, smoke | Critical asset destroyed |

All emitters start with `emitting = false`; set `emitting = true` on each child (or call `restart()`), and free the root after the longest lifetime (1.2 s for the Breach scene). They have no scripts.

### Godot validation (actually run, 2026-11-10)

`godot/tools/run_godot_check.sh` copies `project.godot` and `assets/vfx` into a temp project and runs, with `/opt/tfj-tools/bin/godot` (4.7.2.stable.official.ed1daf0bf):

1. `godot --headless --path <work>/project --import`: exit 0, 0 errors (all 51 PNGs imported).
2. `godot --headless --path <work>/project --script res://assets/vfx/godot/tools/build_presets.gd`: builds and saves the 11 scenes with `ResourceSaver` (all `save=0`, i.e. OK).
3. `godot --headless --path <work>/project --script res://assets/vfx/godot/tools/load_presets.gd`: loads and instantiates every scene and checks each emitter's texture against its frame grid: `LOAD summary 11/11 ok`.
4. `xvfb-run -a -s "-screen 0 1280x720x24" godot --path <work>/project --rendering-driver opengl3 --resolution 1280x720 --fixed-fps 30 --script res://assets/vfx/godot/tools/render_presets.gd`: renders every preset for 36 frames under the MissionView camera (FOV 40, offset (-2.2, 2.3, 10.5)), environment (`#15191E`, filmic) and sun. Renderer: OpenGL 4.5 Mesa llvmpipe (software), GL Compatibility. 407 frames written, exit 0.

The full log of the last run is `godot/last_godot_check.log`. This is a software-GL check on the box; it has not been run on a phone GPU.

## Not done / limits

- No `GPUParticles3D` / `ParticleProcessMaterial` presets (CPU particles are the mobile choice and match the existing code).
- No screen-space distortion shader for Meridian; `MRD-VFX-TEMPORAL_DISTORTION-A` is an additive sheet. A refraction shader could be added later if the owner wants it.
- Mesh debris belongs to the destructibles stream; the debris sheets here are supplementary.
- The presets were not tested inside `MissionView` itself (the brief forbids editing `scripts/` and `scenes/`); they were rendered in a copy of its camera and lighting setup.

## Rights

Original procedural work, generated by code written by the asset agent with AI assistance. No third-party images, no AI image generation, and no stock assets were used. Not marked commercially cleared, because ownership of AI-assisted output is not legally settled.

## Rebuild

`assets/vfx/_build/build_all.sh` (Python 3 with numpy, scipy and Pillow), then `assets/vfx/godot/tools/run_godot_check.sh` (copies the freshly built presets back with `cp <work>/project/assets/vfx/godot/presets/*.tscn assets/vfx/godot/presets/`), then `_build/previews.py`, then `ui/_build/manifest_fragment.py`.
