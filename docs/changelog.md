# Changelog

All meaningful changes, newest first.

## 2026-11-05 — Release preparation: settings, play-test stats, screen sizes, Android release, store kit (0.2.0, unreleased)

Owner request: finish every pending milestone item that doesn't need the owner; leave signing, review and store
submission to them. Work done in a Linux container (Godot 4.7.2 official Linux build, Xvfb for windowed runs).

**Gameplay / UI**
- New **Settings** panel (gear in the menu top bar; it replaces the separate sound and vibration buttons there):
  sound, vibration, **aim guide** (turns the 0.3 s trajectory preview on or off, enabling the plan §10 experiment),
  **Copy play report**, and **Reset progress** (two taps within 3 s; settings are kept). Android back closes it.
- Pause panel gained the aim-guide toggle.
- Menu shows a completion line once every level is cleared ("Perfect run" at 60/60 stars).
- **Safe-area insets** (`SafeArea`): on phones and tablets the HUD corners, hint and menu content move clear of display
  cutouts and rounded corners. Release presets enable edge-to-edge, so this matters on cutout phones.
- Contrast: the HUD level number and the settings footer now use `TEXT_DIM` (6.8:1 on panels; `TEXT_FAINT` was 3.1:1).

**Save data (schema v2)**
- Adds `settings.aim_guide` and per-level `stats` (attempts, wins, losses, timeouts). Loading a v1 save keeps every result
  and setting with no warnings, and the next save rewrites it as v2. Newer or unknown versions are still refused.
- Stats never leave the device. The play report is plain text (level ids, counters, stars, aim-guide setting) put on the
  clipboard only when the player taps the button.

**Android release**
- `export_presets.cfg` is now committed (it was gitignored). Godot 4 keeps credentials out of it, and
  `tests/test_release_config.gd` enforces empty keystore fields, a single version code, empty `version/name`
  (so `project.godot` is the one version-name source), VIBRATE as the only permission, and icon paths that exist.
  **Migration:** move your local untracked copy aside before pulling.
- Presets: "Android Debug" (APK, arm64 + x86_64), "Android Release" (AAB via Gradle, arm64 + armv7),
  "Android Release APK" (for sideloading to testers). Immersive, edge-to-edge, `allowBackup` off.
- `tools/build_android.sh debug|release-apk|release-aab`: signing only from `GODOT_ANDROID_KEYSTORE_*` environment
  variables, creates a local debug keystore if needed, then verifies the signature and prints the SHA-256.
- Version name bumped to **0.2.0**; version code stays 1 (nothing has been uploaded yet).

**Store / release kit** (`store/`, `docs/release.md`)
- Feature graphic (1024×500) and five 1920×1080 screenshots rendered from the real game by `tools/render_store_art.gd`
  (24-bit PNG, no alpha). `--probe` writes contact frames to pick collapse moments.
- Listing copy within Play limits (short description 68/80, full 1,007/4000), privacy policy, Data safety / content
  rating / target audience answers, and a release guide with an owner device checklist.

**Tools / tests**
- `tools/physics_report.gd`: per-level repeatability (wins, distinct end states), peak body count and frame cost.
- Test runner now fails a suite that does not parse (it was silently skipped before).
- New suites: `test_layout.gd` (menu, settings, HUD, pause, win and lose layouts at 16:9, 19.5:9, 20:9, 21:9, 16:10 and
  4:3: every button on screen, at least 60 units, no overlaps; inset handling; inset conversion) and
  `test_release_config.gd`. New tests for v1→v2 migration, stats validation, the report, the settings panel,
  reset, backgrounding, back-button handling and loss/attempt counting.
- `tests/output/.gdignore` keeps review screenshots out of the asset import.

**Findings**
- Physics repeatability on Linux: 10 replays × 20 levels, each in a fresh world, all won with exactly one end state per
  level, with and without the warm-up. The run-to-run variance seen earlier on Windows did not reproduce here, so it is
  platform- or machine-specific.
- Cost: at most 11 live bodies; mean frame 0.25 ms, worst about 6 ms on the container CPU (16.7 ms budget at 60 fps).
  Desktop numbers only; phones are slower.
- Built release APK manifest: minSdk 24, targetSdk 36, versionCode 1, versionName 0.2.0; the only requested permission
  is VIBRATE (the `DUMP` string is the protection on AndroidX's profile-installer receiver, not a requested permission).

**Test evidence (Godot 4.7.2, Ubuntu 24.04 container)**
- Headless: 65 passed, 0 failed, 1 skipped. Windowed (Xvfb): 66 passed, 0 failed, 0 skipped (303 s).
- `tools/build_android.sh debug` → `perfectsmash-debug.apk` (57.8 MB), `apksigner verify` OK.
- `tools/build_android.sh release-apk` with a throwaway key → `perfectsmash-release.apk` (53.2 MB), `apksigner verify` OK.
- Not run: `release-aab` (the container cannot reach Google's Maven repository); any physical-device or emulator run.

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
