# Coding agent handoff: integrating the generated assets

**For:** the coding agent that wires art, VFX, UI and audio into the Godot game.
**Written:** 2026-11-10 against `assets` at `30a95a7` (main last merged in: `9f773fd`).
**Read with:** `generated_assets/docs/ASSET_CONTRACT.md` (v1.7, the binding spec; section numbers below point to it). This brief tells you what to do and in what order; the contract has the detail.

Everything below is checked against the files on `assets`. Anything not yet delivered is marked **PENDING** with what is on disk today.

---

## 1. Ground rules

- All generated assets live on the **`assets` branch** under `generated_assets/`. `main` stays untouched until Imran approves the merge. Do not cherry-pick or copy files from `assets` into `main`. Prototype the loader on a branch of your own that is based on `assets`, or in a scratch copy, and keep it out of `main` until Imran approves.
- **Every new asset is `approval_status: pending_review`** (1,293 of 1,303 entries in the current fragments; the other 10 are legacy files and one owner-instructed entry). Nothing is approved to ship yet. `data/audio.json` itself says files are added only after owner approval, so keep `files` empty on `main` until then.
- **Rights caveats (do not ship as cleared):**
  - AI-generated images are **not commercially cleared**. These are the background plates and texture sources (GenerateImage), the two UI backdrops, and the concepts. Check the `rights_status` text of each entry.
  - Procedural and code-generated work (meshes, VFX, UI vector art, synthesised audio) is original work, but ownership of AI-assisted output is not legally settled, so none of it is marked commercially cleared.
  - The fonts (Chakra Petch, Barlow) are SIL OFL 1.1, cleared for embedding. Keep `OFL.txt` beside them and credit both families.
  - The legacy `assets/audio/music/gameplay_bed.ogg` keeps its **unverified** rights status. Do not delete, re-encode or relabel it. `assets/icon/*` and `assets/music/` are legacy and also untouched.
- **Do not edit generated files in place** (glb, png, ogg, the manifest, fragments or tool output). They are rebuilt from source scripts, and hand edits would be lost. If something is wrong (scale, pivot, node name, loudness, a missing variant), write the request down (asset id, what is wrong, what you need) and pass it to Imran for the asset streams.
- Do not regenerate `asset_manifest.json`. The integration stream owns `--merge`.

## 2. How to find and load assets

- **Manifest:** `generated_assets/asset_manifest.json` (`entries`, plus `planned`, `schema` and `fragments`). It is the merge of `generated_assets/manifest_parts/{3d-kits,audio,surfaces,ui-vfx}.json` and is rebuilt on each integration pass. **Right now it lags behind the fragments:** it has 1,199 entries and the fragments have 1,303, because the VITA, Nova Grid and Civitas environment kits and the Civitas and Meridian backgrounds landed after the last merge. Until the next pass, read the fragments, or the union of both by `id`.
- **Entry fields you need:** `id`, `path` (repo-relative, so prefix it with `res://`), `category`, `render_type` (`mesh`, `texture`, `sprite`, `ui`, `audio`, `font`, `reference`), `chapter` (`helix`, `vita`, `nova_grid`, `civitas`, `meridian`, `shared`), and, where they apply, `component_kind`, `material`, `reference_size_px`, `depth_m`, `scale_range`, `states`, `critical`, `animation`, `blend`, `pivot`, `nine_slice`, `bus`, `loop`, `loop_offset_seconds`, `sound_id`, `music_cue`, `ambience_cue`, `levels`.
- **Skip** `render_type: reference` entries and ids ending `-MOCK` (concepts, previews, screen mock-ups). They are review material, not game assets.
- **Ids** are `<CH>-<TYPE>-<NAME>-<VARIANT>` (section 6). `CH` is `HLX`, `VTA`, `NVG`, `CVT`, `MRD`, `SHR`, `OPR` or `GAM`. `TYPE` includes `CMP` (component), `DEB` (debris), `ENV`, `PRP`, `BG`, `MAT`, `DMG`, `DCL`, `VFX`, `UI`, `ICN`, `MUS`, `SFX`, `AMB`, `FNT` and `LOGO`. The file name is the id in lower case with hyphens turned into underscores, for example `HLX-CMP-SERVER_RACK-B` is `generated_assets/destructibles/helix/hlx_cmp_server_rack_b.glb`.
- **Suggested loader:** parse the manifest once at startup, or with a build step that writes a `.tres` lookup. Build these indexes:
  - `(chapter, component_kind)` for `CMP` meshes and for `DEB` meshes
  - `material` for the `SHR-DMG-*` overlays
  - `id` for everything else
  - `sound_id`, `music_cue` and `ambience_cue` for audio

  **Always fall back to today's greybox** (BoxMesh, procedural sound) when an entry is missing, so missing art never breaks a level.
- **Per-level choices:** `generated_assets/environments/level_schedule.json` lists, for levels 1 to 100, the far, mid and near background ids, the haze overlay and a `ready` flag. `generated_assets/docs/coverage_matrix.json` maps each level to its kinds, landmark, music and ambience.

## 3. 3D: components, debris, environment

**Units and axes (code, `view_mapping.gd`):**
- 100 px = 1 m = 1 Godot unit.
- The conversion is `to_3d(p, ground_y, z) = (x/100, (ground_y - y)/100, z)`, and the 2D rotation `r` maps to the 3D rotation `(0, 0, -r)`.
- glb files are +Y up, the front faces +Z (towards the camera), and the firing direction is +X.

**Components (`<CH>-CMP-<KIND>-<A|B|C>.glb`):**
- **Pivot:** the centre of the collision rectangle, at z = 0. Put the instance exactly where `_add_component` puts the BoxMesh today. `_process` already copies the body position and rotation onto whatever node is in `_meshes[id]`. Note that `_meshes` is typed `MeshInstance3D` and `_on_component_removed` casts `.mesh as BoxMesh`, so retype it as `Node3D` and keep the size separately.
- **Scale:** X and Y scale to the physics rectangle with `scale = (w/100, h/100) / (reference_size_px / 100)`. Z stays 1, because the mesh is already built at the kind depth (`depth_m`).
- **Variant choice:** when a kind has several variants (`-A` short, `-B` medium, `-C` long), choose the one that needs the least stretch, and keep the scale inside its `scale_range`.
- **Depth:** the depth per kind matches `MissionView.KINDS`. For example server_rack 0.8, service_deck 1.4 and relay_mast 0.3. Meshes are centred on z = 0. Keep the known aim offset (picking happens at z = 0 while the visible face is at +depth/2) as a code fix. Do not shift meshes to compensate.
- **Nodes:** the root is named after the file stem. Under it are `mesh_intact`, `mesh_light` and `mesh_heavy`, plus the marker empties `fx_spark_NN`, `fx_smoke_NN` and sometimes `fx_glow_NN`.
- **Runtime glTF quirk:** if you load a glb at runtime with `GLTFDocument`, the root comes back as `<stem>2`. Editor-imported PackedScenes are fine.
- **Critical cores:** `ai_core` (HLX), `gene_vault_core` (VTA), `reactor_core` (NVG), `surveillance_core` (CVT) and `convergence_core` (MRD). They are flagged `critical: true`. Keep the 0.75 m clear space above them for the code's marker.

**Damage states (section 8):**
- **All three state nodes import visible, so show exactly one:**
  - INTACT: `mesh_intact`
  - DAMAGED: `mesh_light`, or `mesh_intact` if it is missing
  - CRITICAL: `mesh_heavy`, or the best one before it
- **Surface overlay:** add `SHR-DMG-<MATERIAL>-LIGHT` (DAMAGED) or `-HEAVY` (CRITICAL) as `material.next_pass`. Use a transparent StandardMaterial3D with `uv1_triplanar = true`, `uv1_world_triplanar = false` and 1 tile per metre.
- **The current tint:** it may stay as a subtle darken. Replace the CRITICAL red emission swap with the overlay and the heavy mesh.
- **DESTROYED:** hide the component and spawn the matching `<CH>-DEB-<KIND>-<VAR>.glb`. It contains `husk` and `frag_01..`, each with its own centre and laid out in intact positions. Run the pieces as short-lived, visual-only RigidBody3D or tweened nodes (no gameplay collision), then free them. This replaces `_spawn_debris` grey cubes. Every one of the 127 components has a debris set.

**Materials (section 7):**
- **Slot names:**
  - `mat_<physics_material>_<ch>[_<zone>]` is the physics-material surface. The `_zone` slots are other finishes of the same material.
  - `trim_*`, `emit_*` and `glass_*` are as named.
- **Colour:** it is in each slot's `baseColorFactor`, and the kits carry no `COLOR_0`. Still set `vertex_color_use_as_albedo = true` on any surface that does have vertex colours (contract v1.7).
- **Emission maps are masks:** set `emission_operator = MULTIPLY`.
- **Physics materials:** they are the ids in `data/materials.json`: `lightweight_alloy`, `reinforced_steel`, `composite`, `glass_polymer`, `concrete`, `electronic_module`, `ai_core_module` and `energy_component`. The manifest `material` field always uses one of these.
  - `ai_core_module` has no texture set of its own, so fall back to the chapter's `electronic_module` set and overlays.
  - The NVG and MRD cores are `energy_component`.
- **Optional tileable PBR sets:** `<CH>-MAT-<MATERIAL>-A` gives `_albedo` (sRGB), `_normal` (OpenGL, normal-map import), `_orm` (R occlusion, G roughness, B metallic; import it as linear) and `_emission`. The UVs are world-scale box projections at 1 UV = 1 m, so the sets line up with the overlays. Glass sets carry alpha, so use `transparency = ALPHA`.

**Camera and light:**
- The assets were authored and previewed under the **exact** `MissionView` setup: FOV 40, offset (-2.2, 2.3, 10.5), looking at focus + (0, -0.4, 0); sun rotation (-52, -38, 0), energy 1.15, colour `#dfe8f0`, shadows to 40 m; background `#15191e`, ambient `#8090a0` at 0.55; Filmic tonemap, no glow. Do not change these when swapping in art.
- **Proposed change (section 9):** add a dark `ProceduralSkyMaterial` used only for reflections, so metals stop reading near black. Keep the background and ambient colours. The harness renders `*_proposed_env.png` with exactly this set-up so you can compare.

**Environment and backgrounds (section 10, `environments/PRODUCTION_NOTES.md`):**
- **Kit modules:** `<CH>-ENV-*` and `<CH>-PRP-*`, 21 per chapter. They cover floor tiles (top at y = 0, left edge at x = 0), back walls, pillar, catwalk, truss, massing, two statics (`LEDGE_STATIC`, `PLINTH_STATIC`, centred and 1.6 m deep), four near props and four band landmarks.
  - Delivered for HLX, VTA, NVG and CVT. **PENDING:** the Meridian kit.
- **Background cards:** `<CH>-BG-FAR|MID|NEAR_<band>_<ZONE>-A` are delivered for all five chapters, four bands each, plus two variant far plates. They are unshaded quads:
  - far: 72 x 36 m at z -30, with the horizon at camera height (y 3.9 m)
  - mid: 28 x 14 m at z -20, bottom at y -1, repeated with flips
  - near: 16 x 8 m at z -12, bottom at y -0.4, repeated with flips
  - **Remove or open up the greybox back wall at z -6 and the seeded blocks at z -5 first**, because they hide every card. Extend the floor to z -12.
- **Overlays and loops:** `SHR-BG-OVL_*` and `SHR-BG-LOOP_*` (flipbooks with an `animation` block) are optional atmosphere layers.

## 4. VFX (`vfx/PRODUCTION_NOTES.md`, section 13)

- **Sheets:** 51 entries, PNG with straight alpha. Each animated entry has `animation: {frames, columns, rows, fps, loop}`, `blend` (`add` or `mix`) and `pivot` `[u, v]` in the frame. The library table in the notes lists all of them.
- **Recipe:**
  - Use `CPUParticles3D` with a quad mesh and a StandardMaterial3D that is unshaded, alpha, `blend_mode` from `blend`, `billboard_mode = PARTICLES`, `particles_anim_h_frames = columns`, `particles_anim_v_frames = rows` and `vertex_color_use_as_albedo = true`.
  - For one-shots, set `lifetime = frames / fps` and `anim_speed = 1`.
  - Flipbooks only advance with `billboard_mode = PARTICLES`.
  - For the variant atlases (`DEBRIS_CHIP_SMALL`, `DEBRIS_FRAGMENT_LARGE`, `GLASS_SHARD`), set anim speed 0 and anim offset 0..1.
- **11 ready preset scenes** live in `generated_assets/vfx/godot/presets/`. They have no scripts and every emitter starts with `emitting = false`. To use one, instance it, set `emitting = true` on each child (or call `restart()`), and free it after its longest lifetime (1.2 s for the Breach scene). Hook them in like this:

| MissionView hook | Preset |
|---|---|
| `_on_blast(center, radius)` | `vfx_breach_explosion.tscn`, root scaled by `radius / 140` |
| kinetic fire (weapon `muzzle` empty when weapons exist) | `vfx_kinetic_muzzle.tscn` |
| `_on_impact(at, strength, component_id)` | `vfx_kinetic_impact.tscn` plus the material preset `vfx_impact_metal`, `_glass`, `_electric` or `_concrete`, chosen by the hit component's material |
| `_on_component_removed` | `vfx_component_collapse.tscn` (plus debris glb, section 3) |
| critical asset alive / destroyed | `vfx_critical_core_idle.tscn` / `vfx_critical_core_destroyed.tscn` |
| CRITICAL state on electronic, ai_core or energy materials | `SHR-VFX-SPARK_BURST-A` + `SHR-VFX-ARC_ELECTRIC_LOOP-A` at the `fx_spark_*` empties |
| burning component | `vfx_burning_loop.tscn` |

- **Keep `_warm_up_effects`.** Add one invisible instance of each preset you use so their shaders compile at load. The stall it fixes was measured on the emulator.
- **Upgrade tiers** are listed in `generated_assets/vfx/upgrade_tiers.json`:
  - Base uses the `-A` sheets.
  - Mk I uses `-A` at scale 1.08.
  - Mk II uses the `-T2` sheets (`#5AA9FF`) at 1.12.
  - Mk III uses the `-T3` sheets (`#B9F2FF`) at 1.22. The Breach Charge stays amber and gets hotter.

  The tier is the highest upgrade level owned for that weapon. The file also gives the cooldown modulate per weapon.
- **Also delivered:** chapter-specific sheets, `SHR-VFX-THRESHOLD_LINE-A` (the topple-line marker) and the trails `OPR-VFX-KINETIC_TRAIL-A` and `OPR-VFX-BREACH_TRAIL-A`.

## 5. UI, fonts, branding

- **Theme:** `generated_assets/ui/theme/tfj_theme_spec.json` is a spec, not a `.tres`. Build a `Theme` from it, by script or by hand. It has these keys:
  - `colors`, `chapter_accents`, `upgrade_tiers`, `fonts`, `type_roles`, `spacing`, `hud_layout` (matches the current MissionHud placement), `damage_numbers` and `motion`
  - `theme`, with style boxes for Button, PrimaryButton, DangerButton, IconButton, the Panel* types, Chip, TabBar, HSlider, CheckButton, ProgressBar, TextureProgressBar_Cooldown, Label and Tooltip

  Replace the colours in `scripts/ui/ui_kit.gd` with the spec values.
- **9-slice:** in a `StyleBoxTexture`, use the **1x** PNG with its **1x margins**. Both are given per style in the spec, and the margins also appear in the manifest `nine_slice`. A 2x texture with 2x margins draws corners at double size. On phones, prefer the `flat_equivalents` StyleBoxFlat values: chamfer radius 12 (10 for buttons) with `corner_detail = 1` stays sharp at any scale. Use the 2x PNGs for TextureRect icons, and for NinePatchRect drawn at half scale.
- **Icons:** 87 icons, each at 64 px (1x) and 128 px (2x), with 256 px hero versions for weapons, upgrades and chapter emblems. They are white on transparent, so tint them with `self_modulate`. Weapon icons are silhouettes until the weapon meshes exist.
- **Fonts:** `generated_assets/fonts/`, OFL 1.1.
  - Chakra Petch is the display face (titles, numerals).
  - Barlow is the UI and body face.
  - Import the .ttf files directly with LCD antialiasing off, Light hinting and MSDF off.
  - No UI image contains baked text; every string is a Label.
- **Branding:** the logo lockups and mark are in `ui/branding/logo/`. The five chapter title layers are in `ui/branding/chapter_titles/game/`; place the three Labels over them as described in `ui/PRODUCTION_NOTES.md`.
- **Splash:** `ui/branding/splash/gam_ui_splash_a_1280x720.png` (a 2560x1440 version is also there). The alternative is the transparent logo with `boot_splash/bg_color = #080C10`.
- **App icon (Android export, once approved):** set these preset fields:
  - `launcher_icons/adaptive_foreground_432x432`, `_background_432x432` and `_monochrome_432x432`: the files in `ui/branding/app_icon/android_adaptive/`
  - `launcher_icons/main_192x192`: `gam_logo_app_icon_a_192.png`
  - project `config/icon` candidate: `gam_logo_app_icon_a_256.png`
  - Play Store icon: `gam_logo_app_icon_a_512.png`

  `assets/icon/*` is legacy. Leave it, and leave `project.godot`, unchanged until Imran approves.
- **Also delivered:** a cooldown ring (`TextureProgressBar`, clockwise), a layered critical-asset marker for a CanvasLayer at the unprojected marker point, an aim reticle, a trajectory dot, ammo pips and off-screen indicators. The 23 screen mock-ups are layout references only.

## 6. Audio (`audio/PRODUCTION_NOTES.md`, `CUE_SHEET.md`, `QC_REPORT.md`, `docs/audio_hook_map.md`)

- **Format:** Ogg Vorbis q6, 44.1 kHz. Music and ambience are stereo; SFX are mono apart from large events. The short UI clicks are 16-bit WAV.
- **Buses:** create `default_bus_layout.tres` with `Master` fed by `Music`, `Ambience`, `SFX`, `UI` and `Voice`. Neither MusicDirector nor AudioService sets a bus today. Every audio entry has a `bus`: Music 55, SFX 148, UI 22, Ambience 20.
- **Code ids already in `data/audio.json`:** 12 of the 13 sound ids have their own files, and `impact_generic` is covered by the composite and concrete sets. All three music cues are covered:
  - `helix_gameplay`: `HLX-MUS-GAMEPLAY-TENSION`
  - `menu`: `GAM-MUS-MENU-01`
  - `cinematic`: `GAM-MUS-OPENING-01`

  `docs/audio_hook_map.md` lists the exact files per id. To wire them, put their `res://` paths in `files` once they are approved.
- **Changes to make in `data/audio.json` and the code:**
  1. Add `impact_composite` and `impact_concrete` sounds, and point `impact_by_material.composite` and `.concrete` at them. They map to `impact_generic` today.
  2. Make `core_destroyed` chapter-specific with 3 variants each, either as `core_destroyed_<chapter>` ids or by filtering the files by chapter folder (`audio/sfx/<chapter>/<ch>_sfx_core_destroyed_0N.ogg`).
  3. Add the delivered ids not yet used by code: `alarm`, `secondary_blast`, `weapon_switch`, `objective_complete`, `ui_confirm` and `ui_back`.
  4. Add music cues `<chapter>_gameplay`, `_combat`, `_boss`, `_intro` and `_outro` for all five chapters, plus `ending`, and an `ambience` block keyed `<chapter>_<band>` (20 beds).
  5. Set `loop_overlap: 0` for every self-looping file.
- **Loops:** 52 loop entries have `loop: true`. Godot does not loop Ogg by default, so set `stream.loop = true` (and `loop_offset` from `loop_offset_seconds` on the five boss tracks, where an 8-bar intro plays once) at load, or in the `.import` settings. The QC confirmed the seams in the decoded files.
- **Adaptive set:** each chapter's `GAMEPLAY-PREP`, `GAMEPLAY-TENSION`, `COMBAT-01` and `CRITICAL_LAYER-01` have the same sample length, tempo and key. You can cross-fade them in sync or play them with `AudioStreamSynchronized`.
- **Critical layer ducking:** while the critical layer plays over the tension or combat bed, **lower the bed by 3 dB**. Measured on the files: without the dip, the Helix pair reaches +0.6 dBTP; with it, about -16 LUFS and -1.7 to -4.3 dBTP. MusicDirector's `duck()` is the narration duck, so add a separate bed offset.
- **Loudness:** music is mastered at -16 LUFS with true peak at or below -1 dBTP. The existing -12 dB bed volume leaves headroom, so keep the relative levels when you set volumes.
- **Keep AudioService's procedural fallbacks** for any id without files.

## 7. Cinematics

- **PENDING.** No cinematic stills (`*-CIN-*`) have been delivered yet. `generated_assets/cinematics/` holds only its README.
- **On `main` now:** `data/cinematics.json` has 11 sequences (opening, `ch01_intro` to `ch05_intro`, `ch01_outro` to `ch04_outro`, and finale). Each slide has `speaker`, `subtitle`, `motion` (`push_in`, `pan_left`, `pull_back`...) and `caption`, and each sequence has an `end_card`. There is no image field yet.
- **Proposed format:** 1920 x 1080 stills (WebP q90), 16:9, with a quiet lower band for subtitles and no baked text (section 16). They need ids `GAM-CIN-OPENING-*`, `<CH>-CIN-INTRO-*`, `<CH>-CIN-OUTRO-*` and `GAM-CIN-FINALE-*`. Subtitles and captions stay as Godot Labels from the JSON. When stills land, add an image id per slide, for example `"still": "HLX-CIN-INTRO-01"`.
- **Already delivered:** the cinematic scores (`<CH>-MUS-INTRO-01`, `<CH>-MUS-OUTRO-01`, `GAM-MUS-OPENING-01`, `GAM-MUS-FINALE-01`, `GAM-MUS-ENDING-CREDITS`) and `<CH>-MUS-TRANSITION-STINGER`. They are mixed at -16.5 LUFS to leave room for narration.

## 8. TODO, in priority order

1. Create a working branch from `assets` (not `main`). Run `python3 generated_assets/tools/validate_asset_manifest.py --quiet` and `generated_assets/tools/godot/run_import_check.sh`. The first headless import has twice segfaulted (exit 139) and passed on retry. Add `.gdignore` to the `previews/` and `source/` folders in your copy, so Godot skips the review files; animated WebP previews fail to import. Leave the generated files themselves alone.
2. **Manifest loader** (section 2) with greybox fallback.
3. **Component meshes in `MissionView._add_component`:** instance the glb, scale it to the rectangle, keep the pivot, retype `_meshes` as Node3D, and fall back to the BoxMesh.
4. **Damage states:** in `_on_component_state_changed`, show one state node and add the overlay `next_pass`. In `_on_component_removed`, hide the component and spawn the debris glb.
5. **VFX presets** on the hooks in section 4, with warm-up.
6. **Environment:** remove or lower the z -6 wall and the z -5 blocks, add the floor tiles and back modules, and add the three background cards per `level_schedule.json`.
7. **Audio:** bus layout, the `data/audio.json` changes in section 6, loop flags, and the 3 dB bed dip under the critical layer.
8. **UI:** build the Theme from the spec, load the fonts, swap in the HUD kit and the icons.
9. Optionally, add the reflection-only sky (section 9) and compare it against the harness renders.
10. **Helix greybox integration test (the deciding step):** play `helix_01` with the Helix kit, damage states, debris, VFX, backgrounds and audio in place, using the placeholder `OperativeRig`. Capture screenshots and an emulator or phone run (frame time, first-detonation stall). Send them to Imran. **The final operative representation is decided from this test**: a full mesh, a stylised low-poly figure, or a refined primitive rig. Until then, keep `OperativeRig` and its state machine as they are.

## 9. Known gaps and open questions

- **PENDING (not on disk):**
  - operative mesh and animations (on hold until the greybox decision)
  - weapon meshes (Kinetic Accelerator, Breach Charge launcher)
  - projectile meshes (kinetic slug, breach canister)
  - the Meridian environment kit
  - cinematic stills
  - a Godot Theme `.tres`

  The coverage matrix (on the last merge) shows 2 of 100 levels full, 16 with shared fallbacks and 82 with something missing, mostly the environment kits that have since landed and the cinematics. The next integration pass will refresh it.
- **Chapter II to V kinds** (`lab_column`, `grid_pylon`, `civic_column`, `anchor_column`...) are proposed names (section 5). Missions for those chapters should use them, or tell us your names so the kits can be renamed.
- **Breach Charge design:** it is assumed to be a launcher that fires lobbed canisters. Imran has not yet confirmed this.
- **Validation done so far, honestly:**
  - Godot 4.7.2 headless import and load of every manifest file (last full pass 1,206 / 1,206).
  - Renders under a copy of the MissionView camera and light, on the box's software OpenGL (llvmpipe).
  - Godot load of all 245 audio files.

  **Not done:** any test inside the real `MissionView` scene or on a phone GPU. Your integration is the first in-game test.
- **Audio:** the hook map lists `ending` for two cues (`GAM-MUS-FINALE-01` and `GAM-MUS-ENDING-CREDITS`). Decide which one plays after the finale and which over the credits. The proposed cue names for prep, critical layer, theme and stingers are only in the entry `notes`.
- **Repetition:** wide shots show mid and near card repeats. Each chapter has only an `-A` texture set per material.
- **Repo size:** `generated_assets/` is about 334 MB. Plan export filters so previews, sources and mock-ups stay out of the APK.
