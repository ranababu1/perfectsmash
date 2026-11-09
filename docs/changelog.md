# Changelog

All meaningful changes, newest first.

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
