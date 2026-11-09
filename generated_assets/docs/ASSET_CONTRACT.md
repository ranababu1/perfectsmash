# Temporal: First Jump - Asset contract (v1)

**Status:** v1, published 2026-11-09 by the integration stream. Binding for every production stream (3d-kits, surfaces, ui-vfx, audio) and the proposed integration contract for the coding agent. Later versions refine it; breaking changes are listed in the change log at the end.
**Derived from code on `main` merged into `assets` at `84a34fd`:** `scripts/mission/view/view_mapping.gd`, `mission_view.gd`, `operative_rig.gd`, `scripts/core/damageable_component.gd`, `material_catalog.gd`, `weapon_catalog.gd`, `scripts/services/music_director.gd`, `audio_service.gd`, `data/materials.json`, `data/weapons.json`, `data/missions/helix_01.json`, `data/chapters.json`, `project.godot`.
**Engine:** Godot 4.7.2 stable, GL Compatibility renderer on desktop and mobile, ETC2/ASTC VRAM compression enabled (`textures/vram_compression/import_etc2_astc=true`).

Where this contract describes something the code does today it says "code". Where it proposes something the coding agent still has to implement it says "proposed". Asset streams must not edit `scripts/`, `scenes/`, `data/` or `project.godot`.

---

## 1. Units and scale

- **100 physics px = 1 m = 1 Godot 3D unit** (code: `ViewMapping.PX_PER_METRE = 100`).
- The 2D physics plane is y-down with the ground at `ground_y` (640 px in `helix_01`). The 3D view is y-up with the ground at y = 0. Conversion (code): `x_m = x_px / 100`, `y_m = (ground_y - y_px) / 100`, `z = 0`.
- Mission widths so far: 1600 px (16 m). Plan backdrops for 14-24 m wide facilities.
- Real-world sanity: operative about 1.75 m tall; server rack 1.0 m tall in `helix_01`. Keep props in believable proportion to the operative.

## 2. Axes and glTF conventions

| | Godot (code) | glTF file | Blender authoring |
|---|---|---|---|
| Up | +Y | +Y | +Z (exporter converts, "+Y Up" on) |
| Toward the camera (front face) | +Z | +Z | -Y (Blender "Front" view looks along +Y, so the front face points to -Y) |
| Right (toward the facility, firing direction) | +X | +X | +X |

- Export glTF 2.0 binary (`.glb`), "+Y Up" enabled, apply all transforms (object scale 1, rotation 0 at export), no cameras or lights in kit files, no animation unless the asset is animated.
- Units: metres, Blender unit scale 1.0.
- 2D rotation maps to a rotation about +Z (code: `rotation_to_3d(r) = (0, 0, -r)`), so a component may roll in the XY plane at any angle once physics releases it. All faces a roll can reveal (front, top, bottom, left, right) must be finished. The back face (-Z) is never seen; it may be a plain cap but must exist (closed mesh, so shadows are correct).

## 3. Gameplay band, depth and visible sides

- The physics plane is z = 0. Each component mesh is **centred on z = 0**: it spans `-depth/2 .. +depth/2` (code: `BoxMesh` of size `(w, h, depth)` placed at z = 0).
- **Front face = physics rectangle.** The silhouette in the XY plane must stay inside the collision rectangle (`w x h`). Small bevels, inset panels and greebles are fine; nothing may stick out of the rectangle in X or Y by more than 1 cm. Detail may protrude in +Z (towards the camera) but stays within the depth below.
- Depth per kind (code `MissionView.KINDS`, metres): server_rack 0.8, support_column 0.5, service_deck 1.4, ai_core 0.7, core_shield 0.9, power_cell 0.5, blast_wall 1.2, relay_mast 0.3, relay_dish 0.8, default 0.8. Statics (fixed ledges, plinths) 1.6.
- **Gameplay depth band:** |z| <= 0.8 m (statics to 0.8 m). Nothing decorative may sit inside z -1.0 .. +1.2 in front of or among gameplay pieces. Pieces must not appear to sit in front of or behind each other.
- Visible sides from the game camera (section 9): front (+Z) always; top (+Y) always (camera is about 14 degrees above); left (-X) for pieces right of the camera, right (+X) for pieces left of it. Texture and model all five.
- Known code issue (currentstate.md): aim picking uses z = 0 while the visible front face is at +depth/2. Do not "fix" it in art by shifting meshes; the centred-on-z=0 rule stands.

## 4. Pivots and origins

| Asset family | Origin | Facing |
|---|---|---|
| Destructible component (every `kind`) | Geometric centre of the collision rectangle, z = 0 (code: mesh follows `body.global_position` and rotation) | Front +Z |
| Debris fragment set `*_debris.glb` | Each fragment's own centre; fragments laid out around the component centre in their intact positions | Front +Z |
| Static ledge / plinth | Centre of its rectangle, z = 0 | Front +Z |
| Environment floor / wall / back structure | Floor pieces: top surface at y = 0, left edge at x = 0 (tileable along X); back pieces: bottom-centre on the floor | Front +Z |
| Background card (far layer) | Bottom-centre | Quad faces +Z |
| Operative | Between the feet on the ground (code: `operative.position = to_3d(operative_px, ground_y, 0.3)`, so z = 0.3) | Faces +X (towards the facility) |
| Weapon (held) | Grip / attachment point, which the rig places at the arm, 0.12 m in z in front of the shoulder joint (code: shoulder `(0.12, 1.42, 0)` on the rig) | Barrel along +X, top +Y. Include an empty node named `muzzle` at the muzzle tip |
| Projectile mesh | Centre of mass, sized to the weapon's `projectile_radius` (kinetic 9 px = 0.09 m, breach 13 px = 0.13 m) | Travel direction +X |
| AI core / critical asset | Centre like any component. The code adds a floating red marker 0.75 m above its top: leave that space clear | Front +Z |
| VFX sprite frame | Frame centre (billboarded) unless the manifest gives `pivot` | Camera-facing |

## 5. Component kinds (catalogue v1)

Kinds are the `kind` strings in mission JSON. Helix kinds exist in code today. Chapter II-V kinds are **proposed** names the coding agent should adopt when it authors those missions; asset streams build them now so the library is ready. Default physics material per kind is in brackets (from `data/materials.json`).

| Chapter (code) | Kinds |
|---|---|
| Helix `HLX` (code, `helix_01`) | `server_rack` (electronic_module), `support_column` (lightweight_alloy), `service_deck` (composite), `ai_core` (electronic_module, critical), `core_shield` (reinforced_steel), `power_cell` (energy_component), `blast_wall` (reinforced_steel), `relay_mast` (lightweight_alloy), `relay_dish` (glass_polymer) |
| Helix `HLX` (proposed) | `control_pod_glass` (glass_polymer), `logistics_gantry` (lightweight_alloy), `cooling_stack` (composite), `data_crate` (composite) |
| VITA `VTA` (proposed) | `lab_column` (lightweight_alloy), `lab_deck` (composite), `cleanroom_panel` (glass_polymer), `specimen_rack` (electronic_module), `bioreactor` (glass_polymer), `containment_cap` (concrete), `cryo_cell` (energy_component), `gene_vault_core` (electronic_module, critical) |
| Nova Grid `NVG` (proposed) | `grid_pylon` (reinforced_steel), `cable_bridge` (composite), `transformer` (electronic_module), `cooling_tower_segment` (concrete), `containment_ring_segment` (reinforced_steel), `capacitor_cell` (energy_component), `containment_wall` (concrete), `reactor_core` (energy_component, critical) |
| Civitas `CVT` (proposed) | `civic_column` (concrete), `relay_bridge` (composite), `sensor_mast` (lightweight_alloy), `sensor_array` (glass_polymer), `civic_screen` (glass_polymer), `data_exchange_rack` (electronic_module), `security_wall` (reinforced_steel), `surveillance_core` (electronic_module, critical) |
| Meridian `MRD` (proposed) | `anchor_column` (reinforced_steel), `convergence_deck` (composite), `phase_shield` (glass_polymer), `quantum_stabilizer` (electronic_module), `temporal_cell` (energy_component), `monolith_slab` (concrete), `timeline_relay` (lightweight_alloy), `convergence_core` (energy_component, critical) |
| Shared `SHR` | `generic_block_alloy`, `generic_block_steel`, `generic_block_concrete`, `generic_panel_glass`, `generic_beam_composite` (fallback blocks for structural filler, one per physics material) |

**Reference sizes.** Missions give every component its own `w x h`. A kit mesh is authored at a reference size and the view scales it in X and Y to the actual rectangle (proposed: `scale = (w/100, h/100) / reference_size_m`; depth stays at the kind depth). Record `reference_size_px` (`[w, h]`) and `depth_m` in the manifest, plus `scale_range` (min, max per axis) the mesh still looks right at. Use the `helix_01` sizes for Helix kinds (for example server_rack 40 x 100, support_column 26 x 160, service_deck 200 x 24, ai_core 60 x 60, core_shield 16 x 80, power_cell 36 x 40, blast_wall 30 x 140, relay_mast 22 x 220, relay_dish 70 x 24). Where one mesh cannot stretch well (columns, masts, decks) supply length variants (`-A` short, `-B` medium, `-C` long) or design the mesh so its middle section stretches cleanly (end caps at the ends, plain repeating middle).

## 6. Naming

**Asset id:** `<CH>-<TYPE>-<NAME>-<VARIANT>`, upper case, hyphen separated, `NAME` in upper snake case.
- `CH`: `HLX` Helix, `VTA` VITA, `NVG` Nova Grid, `CVT` Civitas, `MRD` Meridian, `SHR` shared, `OPR` operative and arsenal (chapter-independent), `GAM` game-wide (logo, menus, credits).
- `TYPE`: `CMP` destructible component, `DEB` debris set, `ENV` environment kit piece, `BG` background layer, `PRP` non-gameplay prop, `MAT` material texture set, `DCL` decal, `DMG` damage overlay, `VFX` effect, `UI` UI element, `ICN` icon, `CHR` character, `ANM` animation, `WPN` weapon, `PRJ` projectile, `CIN` cinematic still or clip, `MUS` music, `SFX` sound effect, `AMB` ambience, `VO` voice, `FNT` font, `LOGO` branding.
- `VARIANT`: `A`, `B`, `C` for shape variants, or a two-digit number for sequences (`01`).
- Examples: `HLX-CMP-SERVER_RACK-A`, `HLX-DEB-SERVER_RACK-A`, `VTA-MAT-GLASS_POLYMER-A`, `SHR-DMG-REINFORCED_STEEL-HEAVY`, `OPR-WPN-KINETIC_ACCELERATOR-A`, `NVG-MUS-GAMEPLAY-01`, `SHR-SFX-IMPACT_METAL-03`.

**File name:** the id in lower case with hyphens turned into underscores, plus a role suffix where a set has several files: `hlx_cmp_server_rack_a.glb`, `hlx_mat_electronic_module_a_albedo.png`, `_normal.png`, `_orm.png`, `_emission.png`.
**Folders:** `generated_assets/<category>/<chapter folder>/`, chapter folders `helix`, `vita`, `nova_grid`, `civitas`, `meridian`, `shared` (same keys as `data/chapters.json` themes and `ChapterTheme`). Concepts stay in `<category>/concepts/`, previews in `<category>/previews/`.
**Inside glb files:** root node named after the file stem; mesh nodes `mesh_intact` (required), optional `mesh_heavy`; marker empties `fx_spark_01..`, `fx_smoke_01..`, `fx_glow_01..`, `muzzle`, `socket_<name>`; no spaces or dots in node or material names.

## 7. Materials and data/materials.json

Physics materials (code, `data/materials.json`): `lightweight_alloy`, `reinforced_steel`, `composite`, `glass_polymer`, `concrete`, `electronic_module`, `energy_component`. Visual look is presentation-only; the JSON holds physics.

- **glTF material slot names:** `mat_<material_id>_<chapter code lower>` for the surface that represents the physics material, e.g. `mat_reinforced_steel_hlx`, `mat_glass_polymer_vta`. Secondary surfaces: `trim_<name>_<ch>` (paint, rubber, cable), `emit_<colour>_<ch>` (light strips, screens, coils), `glass_<name>_<ch>` (transparent parts). A component's main slot must use the physics material in its mission data or the kind default above, so damage overlays (section 8) match.
- **Texture set per material id and chapter:** id `<CH>-MAT-<MATERIAL_ID>-A`, files `<id>_albedo.png` (sRGB), `_normal.png` (OpenGL +Y normal convention, which is what glTF and Godot use), `_orm.png` (R occlusion, G roughness, B metallic: glTF packing), optional `_emission.png`. Tileable, flat-lit, no baked shadows or perspective, no text or logos.
- **Texel density:** the game camera shows about 94 px per metre at 720p and about 180 px per metre on a 1440p-tall phone screen. Target 256-512 px/m on gameplay pieces (512 px/m for the AI core and other critical assets); never above 1024 px/m.
- **Texture sizes:** 512 x 512 standard, 1024 x 1024 hero and tileable material sets, 2048 x 1024 maximum for far background cards. Powers of two everywhere except UI.
- **Embedded or shared textures:** kit glb files may embed their textures (PNG or JPEG inside the glb, self-contained import) or carry only material slots that the coding agent binds to the shared material sets by name. Record which in the manifest `notes`. Keep one glb under 3 MB (hero under 6 MB).
- **Chapter palettes** (gameplay pieces; backgrounds darker and lower contrast): Helix cold steel and graphite, cyan `#2f8fa3` to `#5fd4e8` compute light, orange only for warnings and danger. VITA sterile white and pale grey, glass, restrained green `#7fd8a0`. Nova Grid graphite, amber heat `#ffae42`, electric blue `#4aa8ff`. Civitas desaturated concrete and blue-grey, cold blue, red security `#ff3b4e` used sparingly. Meridian graphite and polished dark stone, violet `#8f7cff`, cyan and white, restrained. Critical assets keep the code's rule: white housing with red `#ff3b4e` emission reads as "the target" in every chapter.

## 8. Damage states

Code states (`DamageableComponent.State`): `INTACT` (>= 75% health), `DAMAGED` (< 75%), `CRITICAL` (< 35%, unstable, released to physics), `DESTROYED` (0, body removed and debris spawned). States only advance.

**Contract states and their art:**

| Contract state | Code state | Art delivered | How it is shown (proposed hook) |
|---|---|---|---|
| `intact` | INTACT | Kit glb, `mesh_intact` | Default |
| `light` | DAMAGED | Tileable RGBA overlay per material: `SHR-DMG-<MATERIAL_ID>-LIGHT` (scuffs, dents, hairline cracks, chipped paint) | `material.next_pass` = transparent StandardMaterial3D with the overlay as albedo, object-space triplanar (`uv1_triplanar = true`, `uv1_world_triplanar = false`, 1 tile per metre); main albedo darkened by about 15% (code already darkens 25%) |
| `heavy` | CRITICAL | Overlay `SHR-DMG-<MATERIAL_ID>-HEAVY` (deep cracks, scorch, exposed structure); optional `mesh_heavy` node in the same glb for hero pieces (bent, broken panels), hidden by default | Swap overlay; show `mesh_heavy` and hide `mesh_intact` if present; electronic and energy materials also flicker emission |
| `sparking` (optional) | CRITICAL, for `electronic_module` and `energy_component` | VFX sprite sheet `SHR-VFX-SPARK_BURST-*` and `SHR-VFX-ARC_*`, emitted from `fx_spark_*` empties if present, else random points on the front face | Looping CPUParticles3D at heavy state |
| `destroyed` | DESTROYED | Debris glb `<CH>-DEB-<KIND>-A`: 4-10 closed fragments that together read as the broken component, same materials, total tris <= 1.5x the intact mesh. Plus VFX (dust, sparks, glass shards per material) | Fragments spawned as short-lived visual-only RigidBody3D or CPUParticles3D meshes at the removed body (code today spawns grey cubes) |

So: **one shared mesh per component with overlay and emission swaps**, optional `mesh_heavy` geometry for hero pieces, and a separate debris set for destruction. Overlays are per physics material and shared by all chapters (chapter tint via the overlay material's albedo colour), which keeps the texture count small. Tileable overlay size 512 x 512 RGBA PNG.

## 9. Camera and lighting (match MissionView, code)

Reproduce this exactly in previews and turntables:

- `Camera3D` perspective, FOV 40 degrees (vertical, Godot default keep-height), base viewport 1280 x 720 (stretch `canvas_items`, aspect `expand`, so wide phones show more width).
- Focus point: horizontal centre of the operative and the facility, y = 1.6 m, z = 0. Camera position = focus + (-2.2, 2.3, 10.5); it looks at focus + (0, -0.4, 0). That is about 14.1 degrees pitch down and 11.8 degrees yaw to the right; the camera sits slightly left of centre.
- Environment: background colour `#15191e`, ambient colour `#8090a0` energy 0.55, tonemap Filmic, no sky, no glow in code yet (assets must not depend on glow; emission should read without it).
- Sun: `DirectionalLight3D` rotation (-52, -38, 0) degrees, energy 1.15, colour `#dfe8f0`, shadows on, max distance 40 m. Light travels toward (0.38, -0.79, -0.49): it comes from the upper left and slightly in front, so front, top and left faces are lit and shadows fall right and backwards.
- Floor (code greybox): slab top at y = 0, colour `#23282e`. Back wall at z = -6 (9 m tall), distant blocks at z = -5.
- GL Compatibility: no SDFGI, no SSAO, no volumetric fog, no screen-space reflections. Bake ambient occlusion into textures; use emission plus a few OmniLight3D for local light.

## 10. Environment and background layers

| Layer | z range (m) | Content | Rules |
|---|---|---|---|
| Floor | top at y = 0, z -9 .. +5 | Tileable floor kit pieces per chapter (1 m and 4 m modules) | Darker than gameplay pieces, low detail contrast |
| Gameplay band | -0.8 .. +0.8 | Components and statics only | Highest contrast in the frame |
| Near back | -2.5 .. -4 | Low walls, railings, consoles, pipes (props, no collision) | Never taller than 3 m directly behind a critical asset |
| Mid back | -4 .. -8 | Facility walls, gantries, windows, chapter landmarks | Value range compressed, 30-50% darker than gameplay pieces |
| Far cards | -12 .. -30 | Textured quads or cylinders (skyline, cavern, megastructure) | 2048 x 1024 WebP or PNG, unshaded or very low light response |

Background props must never cover a target or the trajectory line. Keep the band behind the critical asset quiet (no bright emission directly behind it).

## 11. Operative, weapons and animation

- Code: `OperativeRig` primitive placeholder with states `IDLE, READY, AIM, RELOAD, VICTORY, DEFEAT`, arm rotating at the shoulder around Z, recoil, weapon swap by visibility. Height about 1.75 m, faces +X.
- Final representation is decided after the greybox visual test (owner). Until then deliver a rigged glb whose node names the coding agent can drive like the placeholder: `torso`, `arm_weapon` (pivot at shoulder, rotates about +Z), `weapon_socket` under the arm, `head` with an emissive visor material, legs. Animations as glTF actions named `idle`, `ready`, `aim_pose`, `fire_recoil`, `reload`, `victory`, `defeat`, 30 fps, in place (no root motion), loopable ones flagged `loop` in the manifest.
- Weapons: separate glb per weapon (`OPR-WPN-KINETIC_ACCELERATOR-A`, `OPR-WPN-BREACH_CHARGE-A`), origin at the grip, barrel +X, `muzzle` empty. Kinetic Accelerator: electromagnetic rail, cyan coil, not an assault rifle. Breach Charge: launcher firing lobbed canisters, amber arming band; canister projectile glb `OPR-PRJ-BREACH_CANISTER-A` (0.13 m radius envelope), kinetic slug `OPR-PRJ-KINETIC_SLUG-A` (0.09 m).
- Budgets: operative <= 6,000 tris, one 1024 texture set; weapons <= 2,500 tris, 512 sets.

## 12. Mesh budgets

Standard component 200-1,500 tris; hero and critical assets <= 3,000; debris set <= 1.5x its component; environment modules <= 2,000 each; one or two materials per component (one main slot plus at most one emissive or glass slot). Closed, manifold where practical, consistent outward normals, smooth/flat shading set intentionally, UV0 for textures; UV1 not required. No n-gons in exported meshes (triangulate on export is fine).

## 13. VFX sprite sheets

- PNG RGBA, straight (not premultiplied) alpha, sRGB.
- Grid flipbooks: uniform frames, sheet width divisible by `columns` and height by `rows`; frames read left to right, top to bottom. Frame sizes 128, 256 or 512 px square; sheet at most 2048 x 2048.
- Manifest `animation` block: `{"frames": N, "columns": C, "rows": R, "fps": F, "loop": false}`. `frames <= columns x rows`; unused trailing cells transparent.
- Godot use (proposed): `CPUParticles3D` or `GPUParticles3D` (Compatibility supports both; prefer CPU on mobile) with a `StandardMaterial3D`, billboard mode `particles`, `particles_anim_h_frames = C`, `particles_anim_v_frames = R`. Additive effects (flashes, sparks, arcs, energy) are flagged `"blend": "add"` and painted on transparent with bright cores; alpha-blended effects (smoke, dust, debris) are `"blend": "mix"`.
- Keep 2 px of empty margin inside every frame so filtering does not bleed. No baked text. Orange and amber only for weapon energy, blasts and danger.
- Chapter variants are tints of shared sheets wherever possible.

## 14. UI and 9-slice

- Base viewport 1280 x 720, stretched with `canvas_items` / `expand` to phones (for example 2856 x 1280, about 1.8x). **Author UI at 2x the base size** (a 64 px icon at base is a 128 px file) and display at base size with linear filtering and mipmaps.
- 9-slice panels and buttons: PNG RGBA, corners designed to survive any stretch, manifest block `"nine_slice": {"left": L, "top": T, "right": R, "bottom": B}` in file pixels (so the coding agent sets `StyleBoxTexture` texture margins or `NinePatchRect` patch margins to these values and `axis_stretch` to stretch or tile as given in `notes`).
- Icons: square, 128 x 128 (64 base) or 256 x 256 for hero icons, centred, 8 px safe margin, white or chapter-neutral on transparent so the code can tint with `modulate`; coloured icons say so in `notes`.
- No baked text in any UI image. Text is rendered by Godot with the shipped fonts (fonts need an OFL or similar licence text saved beside them).
- App icon and splash: Android adaptive icon layers 432 x 432 (foreground inside the 288 px safe zone), monochrome layer, Play Store 512 x 512, project icon 256; splash 1280 x 720 minimum and 2560 x 1440 master. Existing legacy files in `assets/icon/` stay untouched; replacements live under `generated_assets/ui/app_icon/` until the owner approves integration.

## 15. Audio

- **Format in game:** Ogg Vorbis (`.ogg`), 44.1 kHz (Godot default mix rate), quality about 6 (roughly 160-192 kbps stereo). Music and ambience stereo; SFX mono unless the stereo image matters (UI and stingers may be stereo). Very short UI clicks may be 16-bit PCM WAV, mono, 44.1 kHz.
- **Masters:** 48 kHz or 44.1 kHz 24-bit WAV kept on the box at `/workspace/tfj-masters/audio/` (listed in the manifest as `master_path`, box-only); small FLAC masters may be committed.
- **Buses (proposed; no `default_bus_layout.tres` exists yet):** `Master` <- `Music`, `Ambience`, `SFX`, `UI`, `Voice`. Manifest field `bus` names the target bus. Code today plays music through `MusicDirector` at -12 dB and synthesises SFX in `AudioService`.
- **Loudness targets (integrated, measured on the delivered file):** music -16 LUFS (+-1), true peak <= -1 dBTP; ambience beds -24 LUFS; stingers and transitions -16 LUFS; SFX peaks -3 to -1 dBFS with momentary loudness by family: weapons and explosions -14 to -10 LUFS-M, impacts and debris -18 to -14, machinery -20, UI -22 to -18. Voice -18 LUFS. The legacy `gameplay_bed.ogg` measures -14.8 LUFS; it is preserved as is (rights unverified).
- **Loops:** loopable files must loop sample-accurately (no click at the seam); set `"loop": true` in the manifest and, if the loop does not start at 0, `"loop_offset_seconds"`. Alternatively deliver a track with its own fade in and out and give `"loop_overlap_seconds"` (code: `MusicDirector.loop_overlap`).
- **Durations:** gameplay themes 2-4 minutes, menu 1.5-3, boss and finale cues 2-4, stingers and transitions 2-12 s, ambience loops 45-120 s, SFX 0.05-4 s.
- **Rights:** record `source` (tool or service, plan, prompt or patch reference) and `rights_status` for every file. AI or service output is never marked commercially cleared without saved terms evidence.

## 16. Video and cinematics

- Narrated stills are the primary format (repo plan): 1920 x 1080 WebP (quality 90) or PNG masters, 16:9, with a quiet lower band for subtitles; no baked text. Parallax layers, where supplied, as separate RGBA PNGs at the same size.
- Short accent clips only: WebM VP9 or Ogg Theora (Godot `VideoStreamTheora` plays `.ogv` natively), 1280 x 720 or 1920 x 1080, 24 or 30 fps, under 12 s, no audio track (audio comes from the music and SFX library).

## 17. Manifest and how the game should load assets

- **Fragments:** each stream writes `generated_assets/manifest_parts/<stream>.json`: `{"stream": "<name>", "updated": "YYYY-MM-DD", "entries": [ ... ]}`. Entry schema = `asset_manifest.json` (required: `id`, `path`, `category`, `render_type`, `format`, `purpose`, `source`, `rights_status`, `approval_status`, `used_by`; optional: `dimensions`, `duration_seconds`, `notes`, `chapter`, `pivot`, `animation`, `loop`, `material`, `component_kind`, `levels`, plus the contract fields `reference_size_px`, `depth_m`, `scale_range`, `tris`, `states`, `nine_slice`, `blend`, `bus`, `sample_rate`, `channels`, `loudness_lufs`, `master_path`, `loop_offset_seconds`, `loop_overlap_seconds`). Only list files that exist. `approval_status` for new work is `pending_review`.
- **Chapter values:** `helix`, `vita`, `nova_grid`, `civitas`, `meridian`, `shared`.
- **Merge:** `python3 generated_assets/tools/validate_asset_manifest.py --merge` (integration stream) merges all fragments into `asset_manifest.json` with cross-fragment duplicate checks and deep file checks.
- **Coding agent (proposed loader):** read `generated_assets/asset_manifest.json` once at startup (or a build step converts it to a `.tres` lookup), index entries by `(chapter, component_kind)` for `render_type == "mesh"` and `category == "destructibles"`, and in `MissionView._add_component` instance `load(path)` (a `PackedScene` from the glb import) instead of the greybox `BoxMesh`, scaling X and Y to the physics rectangle as in section 5. Fall back to the current greybox box when no entry exists, so missing art never breaks a level. Debris sets by `(chapter, component_kind)` with id type `DEB`. Damage overlays by `material`. Music by `id`; levels and chapters map to tracks through `generated_assets/docs/coverage_matrix.json`. Nothing under `generated_assets/` is wired into the game until the owner approves integration into `main`.

## 18. Validation the integration stream runs

- `python3 generated_assets/tools/validate_asset_manifest.py --merge`: schema, ids, paths, image size and alpha, glb parse (nodes, bounds, materials, tris), audio duration and sample rate, sprite-sheet divisibility, and contract checks (pivot centred, front face inside the reference rectangle, depth within the kind depth).
- `generated_assets/tools/godot/run_import_check.sh`: copies the repo to a temp dir, runs Godot 4.7.2 `--headless --import`, then loads every manifest glb, png, ogg and font and reports failures.
- `generated_assets/tools/godot/render_previews.sh`: renders kits under the MissionView camera and light to PNG (Xvfb, software OpenGL) into `generated_assets/docs/previews/`.

## Change log

- v1 (2026-11-09): first version.
