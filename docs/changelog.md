# Changelog

All meaningful changes, newest first.

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
