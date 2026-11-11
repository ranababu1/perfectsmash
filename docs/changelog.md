# Changelog

All meaningful changes, newest first.

## 2026-11-11 — 1.0.0-rc2 (candidate, untagged): owner-reported fixes and narration architecture

Branch `fix/rc2-owner-issues` → PR against `main`. Plan revision 8 records the owner's decisions.
`v1.0.0-rc1` is untouched; no `v1.0.0-rc2` tag until the owner approves.

- **Weapon fallback (critical):** an empty weapon never stays selected while another has ammunition. `MissionEngine` owns it: the shot that uses the selected weapon's last round schedules a switch that `MissionWorld` applies once no round is in flight (never mid-shot); pressing an empty weapon selects the next usable one; order is mission weapon order after the empty weapon, wrapping; reloading weapons with ammunition count as usable and their reload is untouched; a manual choice with ammunition is kept and cancels a pending switch; with every weapon empty the selection is kept and the out-of-ammunition failure is unchanged. The operative model, hint, aim preview, switch sound and HUD follow `weapon_selected` only (no recursion through `ammo_changed`). The level solver now skips steps for empty weapons (previously a refused no-op shot; same outcome). Files: `scripts/core/mission_engine.gd`, `scripts/mission/mission_world.gd`, `scripts/mission/mission_screen.gd`, `tools/levels/mission_solver.gd`.
- **Main menu from gameplay (critical):** the pause menu has Resume, Restart Mission and Main Menu. Restart and Main Menu ask for confirmation ("Return to Main Menu?" states the mission will not be recorded as completed); Cancel returns to pause. Main Menu returns to the campaign main menu with the tree unpaused, records nothing and leaves the save untouched. A mission screen emits each navigation request at most once (no double transitions). Android back: gameplay → pause, pause → resume, confirmation → pause, decision → Continue, results → mission list (previously a dead end). Leaving mid-mission clears the critical music layer, which could otherwise keep playing over the menu. `UiKit.focus_default` no longer focuses a control that left the tree in the same frame. The top-bar Restart icon keeps its existing instant restart. Files: `scripts/mission/mission_hud.gd`, `scripts/mission/mission_screen.gd`, `scripts/mission/mission_audio.gd`, `scripts/main.gd`, `scripts/ui/ui_kit.gd`.
- **Cinematic narration (critical) — architecture integrated, assets pending:** `data/narration.json` maps `<sequence>/<slide>` to clip paths and is the only place narration paths live; `NarrationCatalog` validates it and sets each slide's `voice`. `CinematicPlayer` plays the clip on the new `Voice` bus as the subtitle appears, holds the slide until the clip ends (+0.6 s), ducks the music 9 dB (0.35 s) and restores it (0.8 s) on silent slides, the end card, skip, finish or leaving the screen; tapping on stops the clip with its slide. Settings → Narration volume (0-100 %, steps of 10) persists as `settings.narration_volume` (additive v4 key; rc1 saves load 1.0); Sound off or 0 % mutes the Voice bus; music, sound and vibration settings unchanged. Opening, five introductions, four endings, finale and Story Archive replays share the path. **No approved narration clips have been delivered**: the mapping is empty (`status: pending_assets`), every slide still plays subtitles only, and narration is not complete. The 50 expected clip keys and the integration steps are in `docs/audio/narration-integration.md`; the export manifest now treats mapped clips as shipped files. Files: `scripts/core/narration_catalog.gd`, `data/narration.json`, `scripts/ui/cinematic/cinematic_player.gd`, `scripts/core/progress_data.gd`, `scripts/ui/settings/settings_screen.gd`, `scripts/main.gd`, `default_bus_layout.tres`, `tools/release/export_manifest.gd`.
- **Tests:** new `tests/weapons/test_weapon_fallback.gd` (8), `tests/campaign/test_pause_navigation.gd` (6), `tests/ui/test_cinematic_narration.gd` (10; uses two existing library sounds as stand-in clips, never mapped for shipping). `test_cinematic_player.gd::test_plays_music_cue_but_never_voice` asserted the revision-7 rule (no audio player at all); the owner reversed that rule, so it became `test_plays_music_cue_and_no_voice_without_clips` (one narration player, no voice and no ducking without a mapped clip).
- **Version:** `config/version` 1.0.0-rc2; Android version code 3 at export.
- **Verification:** headless suite 320 passed, 0 failed, 0 skipped; mission probe (`probe_missions.gd -- solve all 3`) after the weapon change and again on the final branch code: 100/100 stand, 381/381 replays won, exit 0; windowed captures of the pause menu, both confirmations, the HUD after an automatic switch and Settings (1600x720); debug APK `build/temporal1-1.0.0-rc2-debug.apk` (~198 MB) installed as an upgrade over rc1 on the Android 17 emulator (Pixel 10 Pro image): opening cinematic skipped with back, Settings slider set to 50 % and saved, helix_01 won by touch, back on results → mission list, helix_02 last Breach charge → automatic switch to Kinetic, pressing the empty Breach keeps Kinetic, back → pause, Main Menu → confirm → back → pause, Main Menu confirmed with the save byte-identical, Restart Mission confirmed → fresh attempt. Not verified: narration audio (no clips), physical devices, iOS.

## 2026-11-11 — 1.0.0-rc1: complete campaign and release candidate

- **All 100 missions** merged chapter by chapter (PRs #10 Helix, #11 VITA, #12 Nova Grid, #13 Civitas, #14 Meridian), each verified before merge (probe 3/3 on every recorded line, campaign gate, windowed capture). Chapter design tables in `docs/levels/`. Authored by five Sonnet subagents with per-chapter file ownership; difficulty revised once after the engine fixes (reactor housing, collapse floor).
- **Camera** pulls back (aspect-aware) so wide finales (up to 2200 px) and the operative fit the screen; depth fog follows.
- **Touch aiming** compensates gravity: a direct round passes through the touched point (found on the Android emulator — touching a core's centre fired ~20 px low). **Popups** are centred (the rise animation pinned them to the top edge; regression test added).
- **UI polish:** main menu fits every 16:9 size, aim hint stays one line with five weapons and grows upward, the core marker never covers HUD buttons, Story Archive uses the production UI theme, mission tiles show mission names, mission haptics follow the Vibration setting (the setting had no effect after the legacy game's removal).
- **Release:** version 1.0.0-rc1 (code 2); unsigned release AAB preset (Gradle, arm64); export filters generated from the shipped-asset manifest; size reduced (music/ambience re-encoded Vorbis q1 126 → 46 MB, lossy cinematic stills, 1024 px VFX caps): debug APK 332 → 198 MB, release AAB 145 MB. Rights audit (`docs/release/rights-audit.md`), privacy/data-safety and store listing with screenshots and feature graphic (`docs/store/`, Sonnet subagent), release guide (`docs/release/README.md`).
- **Verification:** suite 296/0/0; probe 381/381; 100/100 missions won through the app; desktop frame-time sweep (median 6.9 ms); Android 17 emulator run (install, cinematic, menu, chapter intro, helix_01 by touch, results). Not verified: physical devices, iOS, human play-test, listening review, rights approval.

## 2026-11-11 — Full-game production: weapon presentation, chapter worlds, engine fixes, legacy removal

- **Weapon presentation** (Sonnet subagent, reviewed and integrated): the four chapter weapons have their production models on the operative, HUD icons and short names (the weapon bar re-flows for 4-6 weapons), distinct projectiles and trails, impact/blast effects (Pulse discharge ring, Disruptor EMP shell with arcs and no push, Lance flash, Penetrator pass-through sparks), coloured aim preview, and per-weapon fire / strike / blast / ready sounds built from existing library files with distinct pitches (no dedicated recordings exist). 33 assets integrated with their manifest rights fields copied verbatim (`slice: E_chapter_weapons`). Per-weapon bottom hints. Tests: `tests/weapons/test_weapon_presentation.gd` (7).
- **Chapter worlds:** `data/atmospheres.json` + `ChapterAtmosphere` give each chapter its own light, sky, fog and accent rim (VITA sterile teal-white, Nova Grid furnace amber, Civitas cold institutional blue, Meridian violet underground); Helix keeps the approved look. Checked in a window with the chapter preview captures; VITA and Nova Grid toned down after the first look so gameplay pieces stay brighter than the floor. The aim hint has an outline so it reads on bright floors.
- **Rule visuals:** temporal-crystal components glow violet, shielded components carry a cyan shell that fades when their last emitter falls.
- **Helix 01 / 08:** the original prototype moved to `helix_08` ("Human Override", gameplay and physics unchanged; its pinned tests and tools follow it); a new gentle `helix_01` ("First Contact", Kinetic only, recommended 2, two lines win 3/3).
- **Engine fixes found by the chapter authors:**
  - Projectiles no longer have air drag: real flight follows the aim preview arc exactly (Godot's default 2D linear damp made lobs land 25-50 px short of the shown arc — a player-facing bug).
  - New material `reactor_housing` for the Nova Grid and Meridian energy cores (260 health, survives falls, large secondary blast; Pulse ×1.6, Disruptor ×1.5): plain energy cells made the cores one-shot.
  - A critical asset is never destroyed by a collapse alone: falls and debris leave it at 1 health (critical, exposed) and a weapon hit or blast must finish it (the approved Batch 5 Helix rule, now for every chapter). `helix_02` retuned to 3 shots (column, column, Breach onto the fallen controller).
- **Retired slingshot game removed** from the build: legacy gameplay, UI, level catalog, rules, `data/levels.json`, its solver and capture tool, and four legacy-only suites (49 files). Kept and still tested: settle monitor, legacy star score (old-save migration), palette, static boxes, chapter themes. The HUD-press safety test was ported to `MissionScreen`; the renderer benchmark keeps its harness and proxies.
- **Chapters authored so far (subagents, per-chapter file ownership):** Nova Grid 20/20, Civitas 20/20, VITA 20/20 pass the gate; revision passes are under way to raise the difficulty curves to the guide's bands and to re-tune lines affected by the engine fixes. Helix 06-20 and Meridian in progress.
- Tests: full headless suite 290 passed, 0 failed (excluding in-progress chapter missions in the campaign gate) — the drop from 325 is the removed legacy suites.

## 2026-11-11 — Full-game production: foundation (branch `campaign/foundation`)

- PRs #7 (campaign routing) and #8 (Helix 01-05, decision prompt) validated (headless suite 275 passed, 0 failed, 1 skipped) and merged into `main` under the owner's new merge permission. Plan revision 7 records the owner's final decisions.
- **Four chapter weapons** (`data/weapons.json`): Penetrator (II), Pulse Cannon (III), Disruptor (IV), Temporal Lance (V), each with three upgrade levels on four attributes and chapter-scaled costs. New data-driven rules: piercing rounds (`pierce_count`, `pierce_speed_keep`, `pierce_max_resistance`), per-weapon `material_bonus`, cover-ignoring blasts (`blast_ignores_cover`), shield emitters (`shielded_by` on components; `MissionEngine.is_shielded`, `shield_dropped`), and the `temporal_crystal` material that only the Temporal Lance can damage (`vulnerable_to`). `MissionEngine.apply_damage` takes an optional damage source. Missions are rejected if they use a weapon from a later chapter. Tests: `tests/weapons/test_chapter_weapons.gd` (14, rules and real physics).
- **Upgrades screen** (`scripts/ui/upgrades/`) and **cinematic player + Story Archive** (`scripts/ui/cinematic/`; stills with pan/zoom, subtitles, music cue per sequence, skip, no voice). Main menu gains Upgrades and Story Archive; the opening plays on first launch, a chapter's introduction before its first mission, its ending once the chapter is complete (the finale after Chapter V); all are marked seen and replayable. Menu screens play the menu cue. Tests: `tests/ui/test_upgrades_screen.gd` (6), `test_cinematic_player.gd` (10), `test_story_archive.gd` (4), `tests/campaign/test_story_routing.gd` (6). Delegated to two Sonnet subagents (disjoint new files); wiring, review and commits by the orchestrator.
- **Music rights:** the `legacy_bed` cue (`gameplay_bed.ogg`, licence unverified) is removed; nothing references the file; the mission fallback is `helix_gameplay`. A test asserts no cue uses it.
- **Tooling:** `tests/run_tests.gd -- --only <text>`; per-mission solution files `tools/levels/solutions/<id>.json` (`solution_book.gd`); `probe_missions.gd -- solve <chapter theme>`; solver aims piercing weapons `through` named components; `docs/levels/authoring-guide.md`; campaign-wide gate `tests/levels/test_campaign_missions.gd` (valid data, chapter weapons, set dressing from the chapter kit, model scale range, stand check, intended solution wins within the recommended shots).
- Test fix: the operative-rig idle assertion accepted only a freshly started idle clip; it failed whenever the rig was already idling (order-dependent, also on `main`); it now accepts the idle clip already playing.
- Results: headless full suite 315 passed, 0 failed, 1 skipped (before the gate suite); `probe_missions.gd -- solve helix 1` all WIN.

## 2026-11-11 — Optional-objective decision prompt

- When the primary objective is complete, the scene has settled and optional goals are still pending, the mission no longer ends on its own. A prompt asks: "Primary objective complete" / "Optional objectives remain. What next?" with Continue and Finish.
  - **Continue** closes the prompt (offered once per attempt), keeps the mission active and shows a persistent Finish button beside Restart and Pause. The mission then ends when all optional goals are done, the ammunition runs out (a success, since the primary is done), or the player presses Finish.
  - **Finish** ends the mission successfully with the score so far; unfinished optional goals fail, intact optional constraints complete (existing `finalize`).
  - While the prompt is open the clock is held and firing is blocked; pause leaves the prompt in place; Android back means Continue.
  - No prompt when there are no optional goals or all are done; constraints (shot/time limits, protect) never count as pending; mandatory failures behave as before.
- The rule lives in `MissionEngine` (`decision_requested`, `awaiting_decision`, `continue_mission()`, `finish_mission()`, `can_finish_early()`) and `MissionObjectives.pending_optional_goals()`; `MissionHud.show_decision()` / `set_finish_available()`; `MissionScreen` wires them.
- Tests: `tests/objectives/test_mission_decision.gd` (18 engine cases), `tests/ui/test_hud_decision.gd` (4), `tests/campaign/test_decision_flow_app.gd` (4 through the app, including the save file). Existing tests whose missions end with optional goals open now answer the prompt with Finish (no assertion removed or loosened); the solver and score replay do the same. The solver waits one physics frame before aiming.
- Delegation: two general-purpose Sonnet subagents in the shared checkout with disjoint files (HUD + its test; engine tests); the orchestrator wrote the engine interface first and reviewed and ran their work. No conflicts.
- `.claude/` agent definitions and settings removed from the repository (owner removed them).
- Results: headless `godot_console --headless --fixed-fps 60 -s tests/run_tests.gd` → 275 passed, 0 failed, 1 skipped; windowed `godot_console --resolution 1280x720 --fixed-fps 60 -s tests/run_tests.gd` → 276 passed, 0 failed, 0 skipped (one earlier windowed attempt stopped mid-run with no summary when the window closed; rerun complete); `probe_missions.gd -- solve all 3` → exit 0, all 3/3; windowed capture with `--fixed-fps 60` → all five missions won and saved, decision flow prompt → Continue → Finish → SUCCEEDED, 22 frames.

## 2026-11-11 — Helix missions 01-05 playable from the main menu

- The app boots into the campaign menu (Continue / Campaign / Settings). `main.gd` gains `boot_mission` so tests and capture tools can start inside a mission.
- New missions with set dressing (`data/missions/`, `data/environments/`), all Kinetic + Breach:
  - `helix_02` The Welcome System: controller high on a gate frame; aim high (3 shots) or drop the frame column (2 shots). Recommended 2.
  - `helix_03` Traffic of One: steel shield and deck block the controller; the left column is the weak point (3 shots). Recommended 3.
  - `helix_04` Supply Chain: a blast wall blocks every Kinetic line; Breach lobs onto the crate stack and the power cell (3 shots, 4 charges). Recommended 3.
  - `helix_05` The Safety Layer: glass pods close the lane; break them and shoot the controller (5 shots), or lob a Breach onto the power cell and finish (3 shots). Recommended 4.
- `tools/levels/`: `mission_solver.gd` plays a mission like a player through `MissionWorld.fire` (real muzzle, ammunition, cooldowns, settle); `probe_missions.gd` (`scout` / `solve`); `solutions.json`; `capture_helix_01_05.gd` (windowed evidence).
- `tests/levels/test_helix_missions.gd`: stand checks, every recorded solution wins within budget, both weapons used, and the five missions played back to back through Main (scoring, save file reloaded from disk, linear unlocks, Next mission, restart).
- Results:
  - `godot_console --headless --fixed-fps 60 -s tests/run_tests.gd` -> 249 passed, 0 failed, 1 skipped.
  - `godot_console --resolution 1280x720 --fixed-fps 60 -s tests/run_tests.gd` (windowed, Windows desktop) -> 250 passed, 0 failed, 0 skipped (285.4 s).
  - `godot_console --headless --fixed-fps 60 -s tools/levels/probe_missions.gd -- solve all 3` -> exit 0. Stand checks OK for 01-05. Wins 3/3: 01 column breach + kinetic 2 shots (rec. 4); 02 aim high 3 / aim low 2 (rec. 2); 03 3 (rec. 3); 04 3 (rec. 3); 05 lane 5 / power cell 3 (rec. 4).
  - `godot_console --resolution 1280x720 -s tools/levels/capture_helix_01_05.gd` (Windows desktop, GL Compatibility, RTX 5060 Ti) -> all five WIN through the app and saved as completed; Research Data balance 197; 19 screenshots in `docs/images/helix_01_05/`.
- Not done: human play-testing, device testing, Android export of this build.

## 2026-11-11 — Campaign routing: menus, settings, Missions/Next, reload-ready sound

- `main.gd` shows `CampaignScreen` (menu, chapter select, mission select) and `SettingsScreen`; the result panel's Missions action (`MissionScreen.exit_requested`) opens the mission's chapter list; Next with no further unlocked mission returns there too; settings toggles update `ProgressData`, the audio service and the music director and are saved; Android back walks settings → campaign → menu → quit.
- `MissionScreen` plays `reload_ready` when the selected weapon's `reload_completed` fires.
- The app still boots straight into the first authored mission (existing tests in other workstreams instance Main and expect a mission); booting into the menu is a later change.
- M1 merged before this: PRs #4 (weapons), #5 (UI screens), #6 (chapter audio, slice H: 42 audio ids, integrated assets 618 → 660). The specialist sessions had no shell tool; the orchestrator ran and committed their work.
- Results: headless 243 passed / 0 failed / 1 skipped (`tests/campaign/test_campaign_routing.gd` +4); boot smoke clean before the exit-time leak lines. Not captured: screenshots of the new screens.

## 2026-11-11 — M0: campaign catalog, test discovery, frozen contracts, agent definitions

- `MissionCatalog` (`scripts/core/mission_catalog.gd`): 100 campaign slots from `data/chapters.json`, ids `<chapter theme>_<nn>` (`helix_01`..`meridian_20`), a slot is authored when `data/missions/<id>.json` exists, linear unlocks over authored missions. `main.gd` boots the first authored mission and restarts the current one; `MissionScreen.next_requested` (connected to an optional HUD `next_pressed`) moves to the next unlocked authored mission.
- `tests/run_tests.gd` also discovers `tests/<folder>/test_*.gd` (`const PHYSICS_SUITE := true` opts out of `--unit`), so workstreams add suites without editing the runner. New `tests/campaign/test_mission_catalog.gd` (4 tests) including the content gate: each mission file's `id`/`chapter` match its slot and it validates.
- `docs/interfaces.md`: frozen contracts and the ownership map for the five specialist workstreams; `.claude/agents/*.md` carry concrete owned/forbidden paths.
- `docs/plan.md` revision 6 appended (multi-agent production, owner defaults); `docs/currentstate.md` rewritten as a concise verified handoff (previous version at `99f5ee3`).
- Local import cache: 17 Helix GLBs reimported (stale texture UIDs; 34 warnings → 0). No committed asset changed.
- Results: headless 217 passed / 0 failed / 1 skipped; `--unit` 173 / 0 / 0; boot smoke exit 0; asset validator PASS (1,464). Windowed (pre-M0) 214 / 0 / 0.

## 2026-11-11 — Slice E, part 1: restart cost, lighting balance, warm-ups

- Restart keeps the mission set: `MissionView` builds the environment, sun, set dressing and statics under one `Set` node and hands it to the next attempt of the same mission (cached on leaving the tree, released on leaving missions, at quit and at the end of the test run). Desktop restart after the first: ready ~29 ms → ~6 ms; the emulator saving (sky radiance, shadow light, MultiMesh buffers, materials) is still to be measured.
- Lighting: depth fog from 12 m to 18 m (behind the facility, which is ~10.5 m from the camera) replaces the exponential fog that hazed the gameplay plane by ~30%; sun lowered from -52° to -36° pitch so the faces of the pieces toward the camera carry more light than the floor. Measured luminance at the start frame: racks 38 → 46, columns 48 → 62, operative 44 → 47, floor 55 → 55, back hall upper area recedes into haze.
- Warm-ups: the unselected weapon model on the operative is drawn for the first frames at load (projectiles are already warmed by `ProjectileVisual`).
- Tests: `wait_process_frames` helper; the overlay test waits rendered frames (it depended on physics catch-up timing); new `test_restart_reuses_the_mission_set`, `test_projectiles_and_hidden_weapon_are_warmed_at_load`. Headless 207 passed / 0 failed / 1 skipped.
- `tools/perf/restart_timing.gd` times app-style restarts on desktop.
- Emulator benchmark not run: the emulator is pinned in lock-task mode by another app (`app.sipsure`), which refuses other launches; left untouched.

## 2026-11-10 - Full asset integration into the game (owner approval)

- `110c1d0` legacy Perfect Smash app icons removed (`assets/icon/*`, 9 files, and `tools/render_icons.gd`); `config/icon` is `assets/ui/branding/app_icon/gam_logo_app_icon_a_256.png`; library manifest 1,464 entries.
- `a14afcb` `teaser_2041` added to `data/cinematics.json` (12 sequences, 50 slides).
- `64ee807` Breach Charge: a launcher that lobs canisters, area damage on contact plus a 2.5 s air-burst fuse (`fuse_seconds`); `ProjectileVisual` draws the slug and canister meshes, the kinetic and breach trails, the breach arming light and the activation flash. Weapon validation: fuse at most 5 s, only blast weapons can have a fuse, lobbed weapons must have a blast.
- `681016c` the kits, debris, environment pieces, landmarks and texture sets of all five chapters integrated (348 ids) with the trails and arming sprites; tools-only chapter previews and `tools/capture_chapters.gd`; audio hook map reports files wired directly in `data/audio.json`.
- `449a501` merged `origin/main` (slice C); projectiles keep `ProjectileVisual` with the slice C muzzle flash; slices renamed F (trails, arming) and G (all chapters) so slice E stays free for the planned polish pass; 618 integrated entries, 10 presets.
- Results: validator PASS with 0 warnings; clean Godot import (no `.godot`) exit 0 with 0 errors, no segfault; load check 1,455 resources, 0 failed; headless tests 211 passed / 0 failed / 1 skipped; windowed (xvfb, GL Compatibility) 212 passed / 0 failed / 0 skipped; chapter captures for all five chapters (13 of 13 production models each); reference check 0 broken references.

## 2026-11-10 — Asset integration slice C: HUD, operative, weapons

- Production UI theme and fonts on the mission HUD, HUD icons, screen-space critical-asset marker; production operative with its animation clips and live aim; weapon and projectile models; integration tool handles theme/scene dependencies and UI kit 1x variants; export keeps the OFL licences.
- Results: headless 205 passed / 0 failed / 1 skipped.

## 2026-11-10 — Asset library refreshed from the latest delivery

- `8b9361a` `assets/` refreshed from `assets@f186977` (owner-approved): 562 files, path rewrite, legacy files and import settings kept. `4752214` integration manifest rebuilt.
- Results: validator 1 warning (teaser_2041), Godot import clean, headless 204 passed / 0 failed / 1 skipped; emulator benchmark logs in `docs/benchmarks/2026-11-10-helix-refresh/`.

## 2026-11-10 — Asset integration slice D: Helix music, ambience, sound effects

- `91d1967` `data/audio.json` on the delivered audio (90 files), buses (`default_bus_layout.tres`), material-aware impact and destruction sounds, one-sound-per-event throttle, `MissionAudio` (intensity steps with position-synced cross-fades, critical layer, stingers), ambience director, loop flags in imports. `AudioCatalog` gains buses, loop flags, ambience, `destroyed_by_material` and mission plans; `MusicDirector` gains a bus, `keep_position` and a layer player.
- Results: headless 204 passed / 0 failed / 1 skipped; emulator install and play without errors.

## 2026-11-10 — Slice B verified and merged

- `380cd10` uid files for the new view scripts; `b649204` integrated textures import VRAM-compressed with mipmaps (emulator video memory ~265 MB → ~95 MB).
- Verification of the cloud-built slice B: Godot import clean; headless 199 passed / 0 failed / 1 skipped; captures; emulator benchmark (Compatibility, `b649204`): 52-55 fps, worst breach frame 68 ms. Logs in `docs/benchmarks/2026-11-10-helix-sliceB/`.
- `96596ab` merged into `main` (normal merge).

## 2026-11-10 — Asset integration slice B: debris sets, damage overlays, gameplay VFX

- Integration selection: slice `B_helix_debris_damage_vfx` (40 ids): the nine Helix debris sets matching the integrated component variants (`HLX-DEB-*`), light/heavy damage overlays for the seven physics materials used by `helix_01` (`SHR-DMG-*`), and the 17 VFX sheets/textures the presets reference. Rights and approval fields copied unchanged (all `pending_review`).
- `build_integration_manifest.py`: `godot_presets` in the selection become `presets` in `data/integrated_assets.json` (10 ui-vfx CPUParticles3D presets); the build fails if a preset references a file that is not integrated. `export_filter.py` ships the listed presets.
- `AssetLibrary`: `instance_debris` (scaled like the component), `damage_overlay`, `damaged_material` (darkened copy with the overlay as an object-space triplanar transparent `next_pass`, shared per source surface and level, contract 8), `preset_scene`.
- `ComponentVisual`: main-material surfaces switch to the light overlay at DAMAGED and heavy at CRITICAL; the heavy overlay is drawn during the existing two-frame load warm-up.
- New `DebrisSet`: the debris set replaces the destroyed component in its last pose; fragments are thrown outward and up (seeded by component id), land on the floor, shrink away after 2.2 s. Visual only, no 3D physics. Procedural chunks remain the fallback.
- New `MissionVfx`: fixed pools of the presets (breach explosion scaled by blast radius, material impacts, kinetic hit and muzzle, collapse dust scaled by width, core destruction) plus the looping core glow that follows the AI core. Each preset and each debris set is drawn once, motionless under the floor, while the mission loads. The flash sphere is hidden when the explosion preset exists; the pooled blast lights stay.
- Tests: 6 new in `tests/test_assets.gd` (debris per component, seeded debris motion and floor landing, overlays per material, shared overlay materials, presets load, view spawns debris/overlays/effects).
- **Not run:** no Godot binary was available in this session (running a downloaded engine was not permitted), so the Godot test suite, import of the new files, export and emulator benchmarks were **not run**. Only a GDScript syntax parse (gdtoolkit 4) of the changed scripts and the Python build tools were executed. Run the suite and an emulator benchmark before treating slice B as verified.

## 2026-11-10 — Asset integration slice A: Helix structures, environment, materials

- `bc46f53` Merged the owner's asset-library PRs (#2/#3: library moved to `assets/`) with a normal merge; slice A's own copies under `generated_assets/` were dropped first (`a14d7c8`).
- `af8a523` Library references `generated_assets/` → `assets/` (manifest, fragments, cue sheets, docs, VFX/UI preset scenes, asset tools); binaries untouched. Validator PASS, 1439 entries.
- `2968737` Godot import metadata for the library (import: no errors).
- `fe828ad`, `4e2798a` Slice A: `data/integrated_assets.json` from `tools/assets/integration_selection.json` (55 ids + 21 texture dependencies, rights unchanged); `AssetLibrary`, `ComponentVisual`; `data/environments/helix_01.json`; graphite lighting; `tools/assets/export_filter.py` (APK 245 → 74.5 MB); `tools/capture_helix.gd`; `tests/test_assets.gd` (8).
- `88e3ce6` Performance: MultiMesh batching of repeated set pieces, damage-state shader warm-up, fewer shadow casters (emulator Compatibility: draw calls ~1,800 → ~600, worst breach frame 1,739 → 66 ms).
- Results: headless 193 passed / 0 failed / 1 skipped; playable debug APK runs on the Android emulator.

## 2026-11-10 — Batch 5: approved rules, rack comparison, physics fix, renderer validation

- `81fefdc` Save schema v4: `best_points` from successful runs only, `best_attempt_points` for any run, `attempts`/`completions` (migrated records flagged `counts_since_upgrade`, counts not fabricated). Migration and round-trip tests.
- `77a9fb5` Blast occlusion on, `blast_transmission` per material in data; load-aware knockback on; `structural_resistance` (optional) and the `ai_core_module` core housing; blast wall 90 px, core ×3.0; collapse probe, preview-style aim helper; replay sequences re-measured.
- `9beb178` Economy simulation driven by `tools/economy/economy_assumptions.json` (prices unchanged).
- `71f8946` `data/audio.json` + `AudioCatalog`; `AudioService` file variants with procedural fallback and material-aware impacts; `MusicDirector.play_cue`; `impact_happened` carries the component id.
- `c97d4c1` Renderer benchmark on the real Helix 3D scene (`mission_benchmark`).
- `9f773fd`, `6ce8c8e`, `503347c` Hitch fixes: effects warmed at load, component emission always enabled, pooled blast lights and flash meshes. Compatibility worst frame in the breach scenario 1113 ms → 38 ms; Mobile 971 ms → ≤103 ms (emulator).
- `7e42a91` Rack comparison (5 layouts × 112 Breach trajectories + kinetic angles, screenshots); `9cfee96`/`2a2c935` chosen layout: racks 3-4 beside the right column, 1-2 at full height beyond the relay mast.
- `2a2c935` Physics: resting contacts no longer count as impacts (a resting released blast wall reported 154 per frame and blocked settling); core `structural_resistance` 0.5 → 0.42; single-charge core kills 0/112, every collapse leaves the core critical, one kinetic round finishes it. Regression test.
- `6219946` Benchmark spike log with recent gameplay events; switch to run without blast lights.
- Git: the six commits after `44a4664` were rewritten (by the owner's request) to remove AI co-author trailers; no force push was made from this session.
- Results: headless 185 passed / 0 failed / 1 skipped; emulator benchmarks from freshly installed builds of `503347c` (logs in `docs/benchmarks/2026-11-10-helix-mission/`). Physical-device validation still pending.

## 2026-11-09 — Batch 5 pre-work review (findings; rule changes pending approval)

- `33dd17f` Accuracy tests: multi-component blast, chain reaction, shot through a destroyed component, empty detonation, two shots.
- `8225262` `tools/regression/score_replay.tscn` (scripted, input-free score replay; also runnable on Android via `make_eval_project.py --main`), a golden scoring breakdown test and a physics replay consistency test. Windows vs Android emulator: identical points, structural damage 0.4516 vs 0.4519, +1 physics frame.
- `1f1a636` Opt-in `blast_occlusion` and `load_aware_push` prototypes (default off) + 6 tests; `tools/regression/tactics_probe.gd` (Breach/Kinetic trajectory sweeps per design variant).
- `1f417b5` `tools/economy/simulate_research_data.py`.
- `docs/batch5-review.md`: findings and proposals for record semantics (save v4), occlusion, Helix protection, pricing and audio integration.
- Results: headless 167 passed / 0 failed / 1 skipped.

## 2026-11-09 — Batch 4: Mission Points, Research Data, upgrades, save v3

- `d6e5071` `data/scoring.json` + `MissionScoring`: Mission Points and Research Data relative to each mission's recommended shots and target time; time weighted lightly with a 30% floor; accuracy from shots that dealt damage; failure keeps destruction points only. Per-mission `rewards` block; `MissionEngine.effective_shots`. New suite `test_scoring` (8).
- `edb98bc` Save schema v3 (missions, Research Data balance/lifetime, weapon upgrades) with v1/v2 migration; anti-farming (only improvement over the mission's best Research Data is granted); upgrade costs in `weapons.json`; `UpgradeRules`. New suite `test_progression` (8).
- `c469756` Mission results scored, stored and saved on finish; result panel shows Mission Points breakdown and Research Data; missions use purchased upgrades. +1 screen test (score, save, no farming on replay).
- Results: headless 155 / 0 / 1 skipped; windowed 156 / 0 / 0; emulator: v1 save migrated to v3 on a real device-style install after a touch-played win.

## 2026-11-09 — Batch 3: first playable Helix prototype

- `33cd669` 2D physics mission world (`ComponentBody`, `WeaponProjectile`, `MissionWorld`): frozen-until-released components, impact-jolt collision damage, direct kinetic damage, Breach detonation with area damage and knockback, secondary-blast chains, settle detection; release propagates to everything resting on a released body. Helix layout tuned from a physics probe (wall/racks moved, core shield added, recommended shots 4). New suite `test_mission_world` (7).
- `874c88c` 3D presentation and play: tilted three-quarter camera over the 2D physics plane, extruded greybox components with damage tints, critical-asset marker, placeholder operative with aim/fire/reload/victory/defeat states, touch-and-hold aiming with 3D trajectory preview, weapon switching, mission HUD, pause/result panels; the app boots into the mission. New suite `test_mission_screen` (5) and `tools/capture_mission.gd`.
- `1109b8a` Fix: objective progress in the HUD now refreshes when components are destroyed (found on the emulator); +1 test.
- Results: headless 138 passed / 0 failed / 1 skipped; windowed 139 / 0 / 0; Android debug APK runs on the emulator with touch aiming verified via `adb input swipe`.

## 2026-11-09 — Production pipeline aligned with the 3D-over-2D-physics architecture

- `plan.md` §9b and a new “3D-ready production pipeline” section in `visual-audio-production-guide.md`: 3D modular components whose front face matches the 2D physics rectangle (100 px = 1 m, centre pivots, glTF, mobile triangle/texture budgets); 2D art for textures, decals, damage variants, VFX, UI and cinematic stills; placeholder operative/weapons; first asset milestone = concepts, material references, texture sets, specs; bulk production gated on the validated Batch 3 greybox; narrated stills, no video dependency.
- Marked the sprite-based guidance (Temporal Charge sprite, object sprite and gameplay-background templates, sprite format rules, approval checklist items) as superseded where it stands; updated plan §6 rendering principles and §9.
- Documentation only; no code changed.

## 2026-11-09 — Batch 2: mission architecture

- `db82117` MissionDefinition + `data/missions/helix_01.json` (Relay Node greybox: blast wall, 4 server racks, 2 support columns, service deck, AURA core (critical), power cell, relay mast + dish; objectives: core (mandatory), racks, relay dish, ≤8 shots).
- `e9b763d` WeaponState: ammunition, reload cooldown, delivery-specific launch velocity.
- `d7a3738` MissionObjectives + MissionEngine: continuous evaluation, independent weapon cooldowns, structural release and secondary-blast signals, critical-asset state, success after settle, failure on mandatory constraint or settled ammo exhaustion. No five-shot dependency (25-attack test).
- Repository: archived the unmerged branch `claude/quirky-bardeen-xmkcnl` (28 commits) as tag `archive/quirky-bardeen-xmkcnl` → `1826028`, verified on the remote, then deleted the branch (owner request).
- New suites: `test_mission_definition` (6), `test_weapon_state` (5), `test_mission_engine` (10).
- Results: headless 125 passed / 0 failed / 1 skipped; windowed 126 / 0 / 0; Android debug export OK.

## 2026-11-09 — Batch 1: materials, weapons, damage, components, structural dependencies

- `99dbd6c` MaterialCatalog + `data/materials.json` (7 materials; physical behaviour only).
- `396bf3c` WeaponCatalog + `data/weapons.json`: Kinetic Accelerator (direct, fixed speed, flat) and Breach Charge (lobbed, variable power, area blast + knockback, limited). Upgrade tables (base + 3 levels) applied by one `effective_stats()` layer; penetration capped at 0.9; ammunition stays integral.
- `2e486ce` DamageRules (deterministic impact/collision/blast/falloff/knockback/resistance maths) and DamageableComponent (progressive states, critical-asset flag, secondary blast).
- `139a570` StructuralDependencySystem (explicit supports, minimum-support redundancy, deterministic cascades, cycle and reference validation).
- `1c844e0` Fixed a flaky music test: its WAV fixture was empty because `wav.data.resize()` resized a copy; it failed in ~50% of windowed runs and never headless. 8/8 windowed runs pass after the fix.
- `dc99024` Gameplay music bed from the owner's track: trimmed Ogg loop with a 4.5 s self-overlap in `MusicDirector`; MP3 master stays gitignored and `.gdignore`d; licence pending (`docs/asset-manifest.md`).
- New suites: `test_materials` (5), `test_weapons` (7), `test_damage` (11), `test_structure` (8), plus 2 music tests.
- Results: headless 104 passed / 0 failed / 1 skipped; windowed 105 / 0 / 0; Android debug export builds.

## 2026-11-09 — Owner clarifications: legacy levels retired, Batch 1 approved

- Recorded owner clarifications in `currentstate.md` and `plan.md` (§9a): the 20 original levels and slingshot mechanics are legacy (regression/reference only); the Helix prototype becomes the first playable experience; responsibility split (MaterialCatalog, WeaponCatalog, DamageRules, DamageableComponent, StructuralDependencySystem, MissionEngine); progressive damage; data-driven upgrades (base + 3); no universal shot cap; five-batch sequence.
- Corrected `project-audit.md` and `level-design-spec.md` where they suggested keeping or mapping the old 20 levels into the campaign.
- Owner instructed that the shared `bg.mp3` be used as background music; licence evidence remains a release blocker.

## 2026-11-09 — Phase 0/1 re-audit and greybox design decisions (`fed4919`)

- Re-audited the codebase against plan revision 5 (`docs/project-audit.md`): reusable systems, gaps (no damage model, single hard-coded projectile, 5-shot cap and per-shot settle, stars-only scoring, flat 2D presentation, slingshot aiming) and risks.
- Owner decisions: 3D presentation layer over 2D physics; reload-cooldown fire flow; per-mission ammo cap + recommended shot benchmark; delete the untested cinematic player draft (done; it was never committed).
- Tests on `6b75504`: headless 71 passed, 0 failed, 1 skipped.

## 2026-11-09 — M4 technical foundations (`298a99f`, `f33acf4`, `f8bbcde`, `28372ac`)

- **Save schema v2** (`ProgressData`): `story.seen` sequence ids, `settings.music`, `settings.voice`. v1 saves are migrated (levels, stars and settings kept; new fields default on) and re-saved as v2. Unknown/newer versions are still rejected. New tests: v1 migration, story/audio round trip, invalid story entries.
- **Chapter catalog**: `data/chapters.json` (titles, organisations, years, level ranges, theme keys, intro/outro sequence ids) validated by `ChapterCatalog` (contiguous ranges from 1, unique ids and sequences). Presentation only; unlocks still follow level order.
- **MusicDirector**: cross-fading music bed at −12 dB with ducking for narration, runs while paused, follows the saved music setting. No track assigned (candidate not approved).
- **Chapter scenery**: `ChapterTheme` palettes per the art bible; `Backdrop`, the level ground and a HUD chapter caption now follow the level's chapter. Gameplay pieces are unchanged. A test enforces that scenery stays at least 0.2 luminance darker than every piece colour.
- `LevelLoader.build`, `GameScreen.start` and `Hud.set_level` gained optional presentation parameters; existing call sites are unchanged.
- Tests: headless 66 passed / 0 failed / 1 skipped. Visual check: L20 under the Helix theme (`tools/capture_screens.gd`).

## 2026-11-09 — M3 renderer evaluation harness and first results (`cd4cf4c`)

- Added `tools/renderer_eval/benchmark.gd` + `benchmark.tscn`: scripted scenarios (menu, L01, L20, synthetic 72-block stress, parallax/particles+shaders/cinematic proxies) recording frame-interval percentiles, viewport CPU/GPU time, draw calls, memory, startup and per-level load time to JSON and `RENDER_EVAL_*` log lines.
- Added `tools/renderer_eval/make_eval_project.py`: builds an isolated project copy per renderer outside the repo, with its own user dir and package `dev.imrn.temporal1.rendereval`. Production `project.godot` and presets are unchanged.
- Ran both variants on Windows desktop (OpenGL3 vs Vulkan) and the `Pixel10Pro` emulator (GLES 3.1 vs Vulkan 1.3 Forward Mobile). All scenarios completed. Mobile showed 120–265 ms first-use pipeline hitches; both renderers hitch at the first subtitle draw. Full tables in `docs/renderer-evaluation.md`. Emulator/desktop numbers are smoke evidence only.
- Recommendation: keep Compatibility in production until physical-device data and real vertical-slice content exist.
- Main project tests after adding the tool: headless 50 passed / 0 failed / 1 skipped.
- Owner-supplied `assets/music/bg.mp3` analysed (not integrated, not committed): Suno provenance in its metadata, −14.8 LUFS, 0.7 s / 0.4 s silent head/tail, so not loop-ready. Licence evidence and a listening review are required.

## 2026-11-09 — M2 application identity: Temporal: First Jump (`86eb01c`)

- `project.godot`: name "Temporal: First Jump", new description, plain charcoal boot splash (Godot logo hidden), custom user dir `temporal_first_jump` so the save path no longer depends on the display name (which contains `:`).
- Menu title "TEMPORAL: FIRST JUMP", tagline "One shot can change everything."
- Local (gitignored) `export_presets.cfg`: Android package `dev.imrn.temporal1`, label "Temporal: First Jump", APK `build/temporal1-debug.apk`; iOS preset with bundle ID `dev.imrn.temporal1`. Signing keys untouched; only the Godot debug keystore exists.
- `plan.md` revision 4 records the rename; spec and production-guide headers updated.
- Migration: new Android ID = new app (no update path from `dev.imrn.perfectsmash`, side-by-side install, no save carry-over). Old desktop dev saves are not migrated. No store impact recorded, since the old ID was never released.
- Tests: headless 50 passed / 0 failed / 1 skipped; windowed 51 passed / 0 failed. Debug APK exported and verified with `aapt2`/`apksigner`, installed and launched on the `Pixel10Pro` emulator.
- Outstanding: the app icon is still Perfect Smash art; no iOS templates or Mac for iOS validation.

## 2026-11-09 — M1 repository and project audit

- Added `docs/project-audit.md`: toolchain/device inventory, architecture review, supported level vocabulary, mapping of the existing 20 levels to Chapter I, identity/signing audit, store-migration implications, renderer/export baseline, risks and recommended sequence.
- Corrected `docs/currentstate.md` header: branch `main`, remote `temporal-chapter1` (it still referenced the old `master`/`perfectsmash` repository).
- Baseline re-verified on this clone: `godot_console --headless --import`, then `godot_console --headless --fixed-fps 60 -s tests/run_tests.gd` → 50 passed, 0 failed, 1 skipped (Godot 4.7.2, Windows 11).
- Findings needing owner input: Chapter I level order (spec order vs. current difficulty order); confirmation that `dev.imrn.perfectsmash` was never uploaded to any store. No physical Android/iOS device, Mac or iOS export templates are available on this machine.

## 2026-11-09 — Android + iOS mobile rendering architecture approved

- Owner confirmed Android + iOS as target platforms and mobile performance/battery efficiency as the primary priority.
- Updated `docs/plan.md` to revision 3: Godot 4.7.2 remains the engine; Godot Mobile is the proposed production renderer; Vulkan is the intended Android backend and Metal the intended Apple backend where supported.
- Added a mandatory Compatibility-vs-Mobile renderer evaluation on representative physical Android and iOS devices before bulk level production. The existing Compatibility renderer remains the known-good baseline until evidence is reviewed.
- Added iOS export/Xcode/Metal/TestFlight and App Store release requirements. Final iOS build/signing requires macOS with Xcode.
- Updated `docs/instructions.md` with renderer-change safeguards, physical-device test evidence requirements, Android+iOS validation and clarified push cadence.
- No renderer setting, export preset, minimum OS version, gameplay code or app identity was changed. Documentation only; no build or tests were run.


## 2026-11-09 — Story-driven 100-level direction and narrative production plan

- Owner approved the direction to turn the existing physics destruction puzzle into a time-travel science-fiction story while preserving the core physics loop.
- Revised `docs/plan.md` to revision 2. The original baseline remains preserved in Git history.
- Added `docs/narrative-bible.md`: opening cinematic script, five chapter introductions and endings, full 100-level mission map, level-100 cliffhanger and Season 2 (+50 levels) expansion spine.
- Added `docs/visual-audio-production-guide.md`: visual identity, five chapter art directions, Temporal Charge concept, cinematic shot list, image prompt templates, asset naming, voiceover workflow, music licensing guidance and SFX inventory.
- Updated `docs/currentstate.md` to distinguish implemented prototype features from planned narrative work.
- No gameplay code, scenes, level data, physics, app identity or assets were changed in this documentation update. No build/test was run; prior verified test evidence remains dated 2026-11-02.
- Initial six-panel environment concept reference and a generated planning poster were created in the conversation workspace. They are not yet imported into the Godot project and should be treated as concept references, not final game assets.
- An original instrumental dark sci-fi ambient gameplay music task completed successfully (Topview task ID `0456971a021d4760a1e4771f3f3901a9`; one generation credit). The first-pass track is available at the temporary generated-asset URL shared in the conversation. It has not yet been listened to, loop-tested, license-verified or integrated.
- Final game name remains pending owner approval. Existing app identity remains Perfect Smash.

## 2026-11-02 — App icon (0.1.0, unreleased)

- Replaced the placeholder icon with a real app icon, designed from common mobile-game icon guidance: one bold subject taken
  from the core mechanic (the golden ball cracking the red core, with an impact flash), a bright cobalt background, no text.
- Source art: `assets/icon/icon_{background,foreground,monochrome}.svg` (Android 108dp adaptive grid; the monochrome layer
  enables Android 13+ themed icons). `tools/render_icons.gd` renders the adaptive layers, `play_store_512.png`, `main_192.png`
  and `project_256.png`, plus a launcher-mask review sheet at `tests/output/icon_preview.png`.
- The adaptive foreground art is scaled to 84% because the Pixel launcher crops tighter than the 72dp spec suggests. Checked in the
  `Pixel10Pro` emulator's app drawer.
- `project.godot` now uses `assets/icon/project_256.png`; the old `icon.svg` was removed. The local Android preset points
  `launcher_icons/*` at the rendered PNGs (the preset file is gitignored, so set these four paths on any new machine).

## 2026-11-02 — UI/UX refresh and difficulty curve (0.1.0, unreleased)

**UI/UX** (modern but restrained: translucent surfaces, hairline borders, one accent per screen)
- New theme: primary (accent) / secondary / round icon buttons, chips, soft panel shadows, press feedback, fade-and-rise panels.
- Vector icon set (`Icon`) for restart, pause, sound, vibration, lock and star; no image assets were added.
- HUD: title/goal chip with ball pips for shots left, round restart/pause buttons, a floating hint pill.
- Pause and result panels redesigned; result stars pop in one at a time and show par when it was missed.
- Menu: top bar (title, star total, sound/vibration toggles), lock icons, the next level highlighted, a one-tap Continue button.
- Scenery: smooth sky gradient, horizon glow and two layers of hills (deterministic), shared by the menu and levels.
- Pieces: rounded, beveled blocks; a core target with a slow breathing halo; a shaded ball; an idle "grab" cue on the launcher.
- Short fade between the menu and levels. On touch screens no button is pre-focused, so there's no stray focus ring.
- `tools/capture_screens.gd` writes screenshots of every screen to `tests/output/screens/` for review.

**Levels**
- L01 is now a single large core on the ground (solver single-shot win rate 14% -> 44%).
- L13 Skylight: lower, wider stone walls and a wider glass roof; the solver no longer flags it as fragile.
- New order: L01 L02 L03 L07 L05 L04 L06 L08 L09 L17 L15 L12 L14 L19 L18 L10 L11 L13 L16 L20, ordered by solver win rate
  and teaching sequence. Dominoes (L08) stays as an intentional breather after the chain-reaction idea is introduced.
  Level IDs are stable save keys and no longer match their display number.

**Test evidence (Godot 4.7.2, Windows 11)**
- Headless: 50 passed, 0 failed, 1 skipped. Windowed: 51 passed, 0 failed, 0 skipped.
- Debug APK installed and launched on the Android emulator `Pixel10Pro` (2856x1280): menu and levels render in landscape.

## 2026-11-02 — Design decision recorded (0.1.0, unreleased)

- Owner agreed: no per-shot timer in the core mode. Recorded in `currentstate.md` along with possible later experiments.

## 2026-11-01 — Owner decisions recorded (0.1.0, unreleased)

- Landscape orientation approved by the owner (closes the plan §4 portrait/landscape question).
- `plan.md` revised with owner approval (rev 1): product name changed to "Perfect Smash" and a revision-history note added.
  No other plan content changed; the original baseline is in commit `e26dd91`.
- Removed the obsolete debug builds (`com.ranababu.smashtheory`, `com.ranababu.perfectsmash`) from the emulator;
  only `dev.imrn.perfectsmash` remains installed.

## 2026-11-01 — Renamed to Perfect Smash (0.1.0, unreleased)

- Owner decision: the product is now **Perfect Smash** (matching the repository name). Updated `application/config/name`
  and the menu title. `plan.md` keeps its original "Smash Theory" wording as the immutable baseline.
- Local Android preset (gitignored): package ID `com.ranababu.smashtheory` → `dev.imrn.perfectsmash` (owner domain imrn.dev; all apps use `dev.imrn.<app>`), APK
  `build/perfectsmash-debug.apk`. Changed before any release, so no store or upgrade impact.
- Migration note: Godot derives the desktop `user://` folder from the app name, so desktop dev saves made under
  "Smash Theory" are not carried over. On Android the new package ID installs as a separate app.

## 2026-11-01 — Playable prototype: physics, 20 levels, UI, Android debug build (0.1.0, unreleased)

**Gameplay**
- `GameSession` runs a level headlessly or in-game: builds bodies from the definition, spawns shots, watches settling,
  evaluates the objective only on the settled state, and enforces the 10 s hard timeout.
- Bodies: wood/stone/glass `BlockBody` (glass shatters on impulse > 300), `TargetBody`, `ProjectileBody` (CCD), `StaticBox`.
- Targets break, once armed by the first launch, on: contact impulse > 220, **a direct projectile touch above 200 px/s**,
  **a velocity jolt above 400 px/s in one step**, or leaving the play area. The last two were added after tracing showed
  a visible direct hit could shove a target without a large reported impulse, which would read as unfair to players.
- Drag-back aiming anywhere in the play area, a 0.3 s partial trajectory preview and a power ring. The pull is measured in
  screen space (fixes a bug where camera updates between press and release distorted the shot).
- 20 handcrafted levels in `data/levels.json` (destroy-targets and topple objectives). L13 changed to par 2 and its pit
  widened; L01's core enlarged (r 24→30) so the tutorial isn't borderline.

**UI / platform**
- Menu with ordered unlocks and star medals, HUD, pause (sound/vibration toggles), result screens, retry/next.
- Procedural sound effects (no audio assets), vibration, auto-pause on app background, Android back handling.
- Fix: gameplay kept running under the pause menu because it inherited the app root's `ALWAYS` process mode;
  `GameScreen` is now `PAUSABLE`.
- Fix: full-rect UI anchors (`set_anchors_and_offsets_preset`); the HUD button strip had collapsed to the top-left.
- `project.godot`: enabled ETC2/ASTC texture import (required for Android export).

**Tooling and tests**
- `tools/solve_levels.gd`: sweeps 468 angle×power shots per step in parallel isolated worlds and keeps only solutions that
  still win under ±1% power / ±0.6° aim perturbation; writes them with `--write`. It reports the single-shot win rate as a rough difficulty signal.
- New suites: `test_game_session`, `test_level_playthrough` (pre-launch stability, solution wins within par in ≥2 of 3
  replays, restart restores layout), `test_ui_flow` (input pipeline, pause blocks aiming, win persists and unlocks).
- Runner supports SKIP; the HUD-button routing test only runs windowed (Godot headless doesn't route GUI mouse input).
- Known: Godot 2D contact resolution can differ between otherwise identical runs; see `currentstate.md`.

**Test evidence (Godot 4.7.2, Windows 11)**
- `godot_console --headless --fixed-fps 60 -s tests/run_tests.gd` → 50 passed, 0 failed, 1 skipped (GUI routing, needs a window).
- `godot_console --resolution 1280x720 --fixed-fps 60 -s tests/run_tests.gd` → 51 passed, 0 failed, 0 skipped.
- `godot_console --headless --export-debug "Android Debug" build/smashtheory-debug.apk` → APK built (x86_64 + arm64; local, gitignored preset).
  Installed on the Android emulator (`sdk_gphone16k_x86_64`, 2424×1080): boots in landscape, menu and levels render,
  touch aiming works, and levels 1–3 were cleared by hand with progress unlocking. Not yet tested on a physical device.

## 2026-11-01 — Project scaffold and core rules (0.1.0, unreleased)

- Initialized git repository (`master`, remote `origin` → github.com/ranababu1/perfectsmash).
- Added Godot 4.7.2 project (`project.godot`), GL Compatibility renderer for broad Android support,
  1280x720 logical landscape canvas with `canvas_items` stretch / `expand` aspect, sensor-landscape orientation.
- **Decision — landscape orientation:** plan §4 defaults to portrait unless aiming needs horizontal room.
  Ballistic launches across a structure need horizontal distance, so landscape was chosen. To be validated in play tests.
- Added pure, node-free core rules in `scripts/core/`: `LevelDefinition` (parse + validate), `LevelCatalog`,
  `ObjectiveEvaluator`, `SimulationMonitor` (settle + hard timeout), `DestructionRules`, `ScoreRules`,
  `SessionRules` (shot budget state machine), `ProgressData` (versioned save schema), and `GameConfig` tuning constants.
- Added `SaveService` with temp-file-then-rename writes and corrupt-save quarantine (`.corrupt`).
- Added dependency-free headless test runner (`tests/run_tests.gd`) and unit suites.
- Tests: `godot_console --headless --fixed-fps 60 -s tests/run_tests.gd -- --unit` → 39 passed, 1 failed
  (expected: `test_shipped_catalog_is_valid` — `data/levels.json` not yet authored).


## 2026-11-09 — Owner-approved tactical destruction, progression and asynchronous Frontlines direction

- Replaced the slingshot-style product direction with an angled 2.5D tactical destruction puzzle featuring a visible anonymous operative.
- Approved retaining the existing 2D physics architecture for the first prototype; full 3D physics is not approved.
- Approved multiple distinct weapons and a staged data-driven weapon framework. Initial prototype scope: Kinetic Accelerator and Breach Charge; later chapter weapons remain planned.
- Approved story-specific destructible institutions, varied structural shapes/material categories, critical components and weak points.
- Approved longer, multi-stage destruction missions. Levels may require 15-25+ shots where justified; recommended shot budgets are performance benchmarks, not universal hard caps.
- Approved separate regular Mission Points and bonus Research Data, with Research Data funding player-selected weapon upgrades alongside automatic chapter technology progression.
- Approved speed and shot-efficiency bonuses relative to level-specific targets, balanced against objective completion and thoughtful play.
- Approved online leaderboards for a later phase, including fair Standard and Competitive categories.
- Approved **Temporal Frontlines** as the working name for asynchronous asymmetric multiplayer: persistent modular institution construction, offline snapshot attacks, defensive systems, attack reports, repairs/recovery protection and competitive rankings.
- Explicitly excluded real-time synchronized multiplayer physics from the initial multiplayer scope. Frontlines must not block the first single-player campaign release.
- Documentation-only decision update. No gameplay implementation, backend integration, build, test or device validation is claimed in this entry.
