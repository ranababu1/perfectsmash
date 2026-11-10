# Coding agent handoff: integrating the generated assets

**For:** the coding agent that wires art, VFX, UI and audio into the Godot game.
**Written:** 2026-11-10 against `assets` at `249a49a`; **brought to the final state** by integration pass 17 (all four asset streams finished; `main` `3678b6b` merged into `assets`); asset-side gaps closed in pass 18 (VITA washout, loudness metadata, Godot Theme).
**Read with:** `assets/docs/ASSET_CONTRACT.md` (v1.9, the binding spec; section numbers below point to it). This brief tells you what to do and in what order; the contract has the detail.

Everything below is checked against the files on `assets`. Anything not yet delivered is marked **PENDING** with what is on disk today.

## 0. State on `main` (integration into the game, 2026-11-10)

- **Library on `main`:** `assets/` holds the complete delivery from `assets@f186977` (integration pass 18; every delivered file byte-identical, text files with the `generated_assets/` to `assets/` path rewrite). `assets/asset_manifest.json` has 1,464 entries (417.0 MB): 1,456 from the four fragments (3d-kits 418, surfaces 475, ui-vfx 318, audio 245) plus 8 base entries (the legacy `gameplay_bed.ogg` and 7 style-concept references). The 9 legacy `ICON-*` entries (Perfect Smash app icons, `assets/icon/*`) were removed with their files; `gam_logo_app_icon_a_*` replaces them and `project.godot` `config/icon` points at the new 256 px icon. `validate_asset_manifest.py --check --loudness`: PASS, 0 errors, 0 warnings.
- **In the game:** `data/integrated_assets.json` (built by `tools/assets/build_integration_manifest.py` from `tools/assets/integration_selection.json`) now integrates the kits, debris, environment pieces, landmarks and texture sets of all five chapters (slice G), the weapon trails and breach arming and activation sprites (slice F; the projectile meshes came with slice C), plus the Helix slices A (structures, environment, materials), B (debris, damage, VFX), C (HUD theme and icons, operative, weapon models) and D (audio): 618 entries and 10 VFX presets. Missions other than `helix_01` do not exist yet, so chapters II to V are seen in-game only through the tools-only previews in `tools/chapter_preview/` (`tools/capture_chapters.gd`).
- **Breach Charge (confirmed by Imran):** a launcher that lobs canisters. Area damage on contact, plus a 2.5 s air-burst fuse (`fuse_seconds`) for a canister that has hit nothing. The canister mesh `OPR-PRJ-BREACH_CANISTER-A` tumbles with the physics body, with the breach trail, arming light and activation flash (`scripts/mission/view/projectile_visual.gd`). The Kinetic Accelerator stays the precision direct-impact weapon (slug mesh and kinetic trail).
- **Cinematics:** `teaser_2041` is in `data/cinematics.json` (no chapter plays it yet).
- **Coverage:** 3,236 of 3,236 requirements, 100 of 100 levels full, 36 of 36 game-wide items (design-spec level mapping; only `helix_01` is an authored mission).
- **The `assets` branch** is kept unchanged as the source and archive of the delivery.
- Sections below that say **PENDING** for the operative, weapons, projectiles and cinematics are superseded: all of them are delivered (see section 9).

---

## 1. Ground rules

- All generated assets live on the **`assets` branch** under `assets/`. `main` stays untouched until Imran approves the merge. Do not cherry-pick or copy files from `assets` into `main`. Prototype the loader on a branch of your own that is based on `assets`, or in a scratch copy, and keep it out of `main` until Imran approves.
- **Every new asset is `approval_status: pending_review`** (1,463 of 1,473 entries after pass 18; the other 10 are 9 legacy files and one owner-instructed entry). Nothing is approved to ship yet. `data/audio.json` itself says files are added only after owner approval, so keep `files` empty on `main` until then.
- **Rights caveats (do not ship as cleared):**
  - AI-generated images are **not commercially cleared**. These are the background plates and texture sources (GenerateImage), the two UI backdrops, and the concepts. Check the `rights_status` text of each entry.
  - Procedural and code-generated work (meshes, VFX, UI vector art, synthesised audio) is original work, but ownership of AI-assisted output is not legally settled, so none of it is marked commercially cleared.
  - The fonts (Chakra Petch, Barlow) are SIL OFL 1.1, cleared for embedding. Keep `OFL.txt` beside them and credit both families.
  - The legacy `assets/audio/music/gameplay_bed.ogg` keeps its **unverified** rights status. Do not delete, re-encode or relabel it. The legacy `assets/icon/*` set was replaced by `assets/ui/branding/app_icon/` and removed on 2026-11-10. `assets/music/` (the untracked owner master) is legacy and also untouched.
- **Do not edit generated files in place** (glb, png, ogg, the manifest, fragments or tool output). They are rebuilt from source scripts, and hand edits would be lost. If something is wrong (scale, pivot, node name, loudness, a missing variant), write the request down (asset id, what is wrong, what you need) and pass it to Imran for the asset streams.
- Do not regenerate `asset_manifest.json`. The integration stream owns `--merge`.

## 2. How to find and load assets

- **Manifest:** `assets/asset_manifest.json` (`entries`, plus `planned`, `schema` and `fragments`). It is the merge of `assets/manifest_parts/{3d-kits,audio,surfaces,ui-vfx}.json` and is rebuilt on each integration pass. It can lag behind the fragments between integration passes; `python3 assets/tools/validate_asset_manifest.py --check` says whether it is current (after pass 18 it is: 1,473 entries, level with the fragments). If it lags, read the fragments, or the union of both by `id`, until the next pass catches up.
- **Entry fields you need:** `id`, `path` (repo-relative, so prefix it with `res://`), `category`, `render_type` (`mesh`, `texture`, `sprite`, `ui`, `audio`, `font`, `reference`), `chapter` (`helix`, `vita`, `nova_grid`, `civitas`, `meridian`, `shared`), and, where they apply, `component_kind`, `material`, `reference_size_px`, `depth_m`, `scale_range`, `states`, `critical`, `animation`, `blend`, `pivot`, `nine_slice`, `bus`, `loop`, `loop_offset_seconds`, `sound_id`, `music_cue`, `ambience_cue`, `levels`.
- **Skip** `render_type: reference` entries and ids ending `-MOCK` (concepts, previews, screen mock-ups). They are review material, not game assets.
- **Ids** are `<CH>-<TYPE>-<NAME>-<VARIANT>` (section 6). `CH` is `HLX`, `VTA`, `NVG`, `CVT`, `MRD`, `SHR`, `OPR` or `GAM`. `TYPE` includes `CMP` (component), `DEB` (debris), `ENV`, `PRP`, `BG`, `MAT`, `DMG`, `DCL`, `VFX`, `UI`, `ICN`, `MUS`, `SFX`, `AMB`, `FNT` and `LOGO`. The file name is the id in lower case with hyphens turned into underscores, for example `HLX-CMP-SERVER_RACK-B` is `assets/destructibles/helix/hlx_cmp_server_rack_b.glb`.
- **Suggested loader:** parse the manifest once at startup, or with a build step that writes a `.tres` lookup. Build these indexes:
  - `(chapter, component_kind)` for `CMP` meshes and for `DEB` meshes
  - `material` for the `SHR-DMG-*` overlays
  - `id` for everything else
  - `sound_id`, `music_cue` and `ambience_cue` for audio

  **Always fall back to today's greybox** (BoxMesh, procedural sound) when an entry is missing, so missing art never breaks a level.
- **Per-level choices:** `assets/environments/level_schedule.json` lists, for levels 1 to 100, the far, mid and near background ids, the haze overlay and a `ready` flag. `assets/docs/coverage_matrix.json` maps each level to its kinds, landmark, music and ambience.

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
  - Delivered for all five chapters (the Meridian kit landed in `249a49a`).
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
- **11 ready preset scenes** live in `assets/vfx/godot/presets/`. They have no scripts and every emitter starts with `emitting = false`. To use one, instance it, set `emitting = true` on each child (or call `restart()`), and free it after its longest lifetime (1.2 s for the Breach scene). Hook them in like this:

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
- **Upgrade tiers** are listed in `assets/vfx/upgrade_tiers.json`:
  - Base uses the `-A` sheets.
  - Mk I uses `-A` at scale 1.08.
  - Mk II uses the `-T2` sheets (`#5AA9FF`) at 1.12.
  - Mk III uses the `-T3` sheets (`#B9F2FF`) at 1.22. The Breach Charge stays amber and gets hotter.

  The tier is the highest upgrade level owned for that weapon. The file also gives the cooldown modulate per weapon.
- **Also delivered:** chapter-specific sheets, `SHR-VFX-THRESHOLD_LINE-A` (the topple-line marker) and the trails `OPR-VFX-KINETIC_TRAIL-A` and `OPR-VFX-BREACH_TRAIL-A`.

## 5. UI, fonts, branding

- **Theme:** `assets/ui/theme/tfj_theme.tres` is a Godot 4 `Theme` built from the spec by `ui/theme/build_theme.gd`. It loads in Godot 4.7.2. Assign it to your root Control or as the project GUI theme. Type variations: `PrimaryButton`, `DangerButton`, `IconButton`, `PanelModal`, `PanelInset`, `PanelHeader`, `Chip`, `TooltipPanel`, `TooltipLabel`, `ProgressBarEnergy`, `ProgressBarIntegrity`, `ProgressBarSuccess`, and one Label variation per type role (`LabelTitle`, `LabelBody`, `LabelCaption`, `LabelLabelCaps` and so on). The palette, chapter accents, tiers and spacing are items on the custom type `TFJ`, for example `theme.get_color("scrim", "TFJ")` or `theme.get_constant("spacing_m", "TFJ")`. Set these on the nodes yourself, because they are not theme items: `uppercase` for the uppercase roles, minimum sizes, the cooldown `TextureProgressBar` textures and fill mode, and the HUD layout. `ui/screens/webp_1x/gam_ui_screen_theme_applied_mock.webp` is a Godot render with the theme applied. If files move, rebuild the `.tres` with the script; do not edit it by hand. The spec, `assets/ui/theme/tfj_theme_spec.json`, has these keys:
  - `colors`, `chapter_accents`, `upgrade_tiers`, `fonts`, `type_roles`, `spacing`, `hud_layout` (matches the current MissionHud placement), `damage_numbers` and `motion`
  - `theme`, with style boxes for Button, PrimaryButton, DangerButton, IconButton, the Panel* types, Chip, TabBar, HSlider, CheckButton, ProgressBar, TextureProgressBar_Cooldown, Label and Tooltip

  Replace the colours in `scripts/ui/ui_kit.gd` with the spec values.
- **9-slice:** in a `StyleBoxTexture`, use the **1x** PNG with its **1x margins**. Both are given per style in the spec, and the margins also appear in the manifest `nine_slice`. A 2x texture with 2x margins draws corners at double size. On phones, prefer the `flat_equivalents` StyleBoxFlat values: chamfer radius 12 (10 for buttons) with `corner_detail = 1` stays sharp at any scale. Use the 2x PNGs for TextureRect icons, and for NinePatchRect drawn at half scale.
- **Icons:** 87 icons, each at 64 px (1x) and 128 px (2x), with 256 px hero versions for weapons, upgrades and chapter emblems. They are white on transparent, so tint them with `self_modulate`. Weapon icons are silhouettes until the weapon meshes exist.
- **Fonts:** `assets/fonts/`, OFL 1.1.
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

  Done on 2026-11-10 (owner approval): `config/icon` uses `gam_logo_app_icon_a_256.png` and the legacy `assets/icon/*` set is removed. Set the launcher icons in your local `export_presets.cfg`.
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

- **Delivered.** 56 stills (1920 x 1080 WebP, AI-generated and upscaled, not commercially cleared) for all 11 game sequences, plus a 2041 teaser. `assets/cinematics/cinematic_sequences.json` is a CinematicCatalog-compatible copy of `data/cinematics.json` with an `image` per slide; the validator checks it slide for slide against `data/cinematics.json` (speaker, subtitle, caption) and checks that every image exists. SRT and JSON subtitles are in `assets/cinematics/subtitles/`. The extra `teaser_2041` sequence is not in `data/cinematics.json` yet.
- **On `main` now:** `data/cinematics.json` has 11 sequences (opening, `ch01_intro` to `ch05_intro`, `ch01_outro` to `ch04_outro`, and finale). Each slide has `speaker`, `subtitle`, `motion` (`push_in`, `pan_left`, `pull_back`...) and `caption`, and each sequence has an `end_card`. There is no image field yet.
- **Proposed format:** 1920 x 1080 stills (WebP q90), 16:9, with a quiet lower band for subtitles and no baked text (section 16). They need ids `GAM-CIN-OPENING-*`, `<CH>-CIN-INTRO-*`, `<CH>-CIN-OUTRO-*` and `GAM-CIN-FINALE-*`. Subtitles and captions stay as Godot Labels from the JSON. When stills land, add an image id per slide, for example `"still": "HLX-CIN-INTRO-01"`.
- **Already delivered:** the cinematic scores (`<CH>-MUS-INTRO-01`, `<CH>-MUS-OUTRO-01`, `GAM-MUS-OPENING-01`, `GAM-MUS-FINALE-01`, `GAM-MUS-ENDING-CREDITS`) and `<CH>-MUS-TRANSITION-STINGER`. They are mixed at -16.5 LUFS to leave room for narration.

## 8. TODO, in priority order

1. Create a working branch from `assets` (not `main`). Run `python3 assets/tools/validate_asset_manifest.py --quiet` and `assets/tools/godot/run_import_check.sh`. The first headless import has twice segfaulted (exit 139) and passed on retry. Add `.gdignore` to the `previews/` and `source/` folders in your copy, so Godot skips the review files; animated WebP previews fail to import. Leave the generated files themselves alone.
2. **Manifest loader** (section 2) with greybox fallback.
3. **Component meshes in `MissionView._add_component`:** instance the glb, scale it to the rectangle, keep the pivot, retype `_meshes` as Node3D, and fall back to the BoxMesh.
4. **Damage states:** in `_on_component_state_changed`, show one state node and add the overlay `next_pass`. In `_on_component_removed`, hide the component and spawn the debris glb.
5. **VFX presets** on the hooks in section 4, with warm-up.
6. **Environment:** remove or lower the z -6 wall and the z -5 blocks, add the floor tiles and back modules, and add the three background cards per `level_schedule.json`.
7. **Audio:** bus layout, the `data/audio.json` changes in section 6, loop flags, and the 3 dB bed dip under the critical layer.
8. **UI:** apply `ui/theme/tfj_theme.tres`, swap in the HUD kit and the icons.
9. Optionally, add the reflection-only sky (section 9) and compare it against the harness renders.
10. **Helix greybox integration test (the deciding step):** play `helix_01` with the Helix kit, damage states, debris, VFX, backgrounds and audio in place, using the placeholder `OperativeRig`. Capture screenshots and an emulator or phone run (frame time, first-detonation stall). Send them to Imran. **The final operative representation is decided from this test**: a full mesh, a stylised low-poly figure, or a refined primitive rig. Until then, keep `OperativeRig` and its state machine as they are.

## 9. Known gaps and open questions

- **Delivered since this brief was first written:** the rigged operative `OPR-CHR-OPERATIVE-A` (9 clips; the greybox decision in section 8 still applies), weapons (`OPR-WPN-KINETIC_ACCELERATOR-A` to `-C`, `OPR-WPN-BREACH_CHARGE-A` to `-C`, plus future weapons), the projectiles `OPR-PRJ-KINETIC_SLUG-A` and `OPR-PRJ-BREACH_CANISTER-A`, environment kits for all five chapters, and the cinematic stills.
- **Godot Theme:** delivered in pass 18 (`ui/theme/tfj_theme.tres`).
- **Coverage (final pass):** 100 of 100 levels full, 3,236 of 3,236 requirements.
- **Findings from pass 17, closed in pass 18:**
  - VITA washout: fixed in the materials (revision 4). The floor albedo is now about 141 / 138 / 126 sRGB with a warm tint against the blue light, the white panels are darker with more detail contrast, and the floor tile glbs have a lower composite factor. Clipped pixels in `harness_mission_vita.webp` fell from 29.1% to 1.5% (floor band from 71.7% to 0.3%). No exposure change is needed in the chapter environment. The Cycles environment sheet and the material tile previews still show revision 3.
  - Loudness metadata: `SHR-SFX-IMPACT_COMPOSITE-02`, `-03` and `-04` now record -22.0, -22.3 and -21.7 LUFS (measured). The audio files are unchanged.
  - `teaser_2041` was added to `data/cinematics.json` on `main` (2026-11-10).
- **Chapter II to V kinds** (`lab_column`, `grid_pylon`, `civic_column`, `anchor_column`...) are proposed names (section 5). Missions for those chapters should use them, or tell us your names so the kits can be renamed.
- **Breach Charge design:** confirmed by Imran (2026-11-10): a launcher that lobs canisters, an area-damage weapon distinct from the precision direct-impact Kinetic Accelerator. Implemented on `main` (section 0).
- **Validation done so far, honestly:**
  - Godot 4.7.2 headless import and load of every manifest file (pass 18: 1,464 loaded, 0 failed, including the Theme).
  - Renders under a copy of the MissionView camera and light, on the box's software OpenGL (llvmpipe).
  - Godot load of all 245 audio files.

  **Not done:** any test inside the real `MissionView` scene or on a phone GPU. Your integration is the first in-game test.
- **Audio:** the hook map lists `ending` for two cues (`GAM-MUS-FINALE-01` and `GAM-MUS-ENDING-CREDITS`). Decide which one plays after the finale and which over the credits. The proposed cue names for prep, critical layer, theme and stingers are only in the entry `notes`.
- **Repetition:** wide shots show mid and near card repeats. Each chapter has only an `-A` texture set per material.
- **Repo size:** `assets/` is about 386 MB on disk (and `assets/`, main's copy, 366 MB; git stores identical files once, and `.git` is 401 MB). Plan export filters so previews, sources and mock-ups stay out of the APK.
