# Current State

_Last updated: 2026-11-05 · Version 0.2.0 (unreleased, version code 1) · Branch `claude/quirky-bardeen-xmkcnl` · Remote `origin` (github.com/ranababu1/perfectsmash)_

## Work in progress: campaign (0.3.0)

Building the 100-mission "Operation Rebuild" campaign requested by the owner on 2026-11-05. The plan, design and a
**resume checklist** are in `docs/campaign_plan.md` §6. Done so far: Phase 1 (mechanics), Phase 2 (80 new
solver-verified missions, `data/levels.json` now holds 100), Phase 3 (storyline in `data/story.json`), most of
Phase 4 (briefing, debrief, narration, chapter menu, HUD). Next: UI-flow tests, then Phase 5 (verification,
store art, docs).

## Purpose and phase

Perfect Smash (originally titled "Smash Theory") is a compact 2D physics destruction puzzle for Android (Godot 4). See `plan.md`.
**Phase:** release candidate preparation. The game is feature-complete for the MVP scope in plan §4. Every
milestone item that can be done without the owner's devices, accounts or keys is done. The rest needs the owner
(see "Waiting on the owner").

## Milestones (plan §11)

| Milestone | Status | Evidence / what remains |
|---|---|---|
| M0 Physics spike | Partial | Aiming and launching work on desktop and the emulator; UI input cannot launch (tested). Frame cost measured on desktop (`tools/physics_report.gd`). **Physical-device run pending (owner).** |
| M1 Rules and objective model | Done | Unit tests for budget, objectives, win/loss, settle/timeout, restart |
| M2 Playable prototype | Done | 20 levels; no body or timer can hang a level (10 s timeout) |
| M3 Content and progression | Done (automated) | Validated level data; every solution replayed; save persists with schema migration. Human play-test of the difficulty order pending |
| M4 Usability and performance | Done (automated) / device check pending | Layout tests at 6 aspect ratios, safe-area insets, contrast check, lifecycle tests (background, back, pause, settings). Device checklist in `docs/release.md` §4 |
| M5 Closed testing | Ready to start | Store art + copy, privacy policy, Data safety answers, local play report for testers. Needs Play Console setup (owner) |
| M6 Release candidate | Ready except signing/upload | Release presets, build script, signed release APK verified with a throwaway key. AAB build, upload key, Play review and release approval: owner |

## Feature status

| Feature | Status | Notes |
|---|---|---|
| Level data + validation (`LevelDefinition`, `LevelCatalog`) | Implemented | `data/levels.json`, 20 levels |
| Physics session (`GameSession`, `LevelLoader`, bodies) | Implemented | Wood, stone, glass blocks; static surfaces; targets |
| Objectives | Implemented | `destroy_targets`, `topple` (all blocks below a line) |
| Shot budget / win-loss (`SessionRules`) | Implemented | Evaluated only after settle or timeout |
| Settling + 10 s hard timeout (`SimulationMonitor`) | Implemented | Thresholds in `GameConfig` |
| Drag-back aiming + partial trajectory preview | Implemented | 0.3 s preview; can be switched off ("Aim guide") for the plan §10 experiment |
| Stars (par-based), local progress, unlocks | Implemented | `user://progress.json`, schema v2 (v1 saves migrate) |
| Settings panel | Implemented | Sound, vibration, aim guide, copy play report, reset progress (two-tap confirm) |
| Local play-test stats | Implemented | Per-level attempts/wins/losses/timeouts on device only; copied to the clipboard on request |
| Menu, HUD, pause, results, retry/next | Implemented | Menu shows a completion line when all levels are cleared |
| Safe-area (cutout) insets | Implemented | `SafeArea`; mobile only; untested on a real cutout device |
| Sound (procedural) + vibration | Implemented | Vibration untested on device |
| Pause on app background / Android back | Implemented | Automated tests; untested on device |
| Android export | Implemented (APK) / Partial (AAB) | Debug and release APKs build and verify in CI-like Linux; AAB needs the full SDK + Google Maven (owner machine) |
| Store listing materials | Implemented | `store/`: feature graphic, 5 screenshots, listing, privacy policy, Play Console answers |
| Analytics | Deliberately absent | Plan §10; the local play report covers closed testing without an SDK |
| Localization | Not in scope | UI strings are hard-coded English |

## Architecture

- `scripts/core/` — pure rules, no nodes: `GameConfig` (tuning), `LevelDefinition`, `LevelCatalog`,
  `ObjectiveEvaluator`, `SimulationMonitor`, `DestructionRules`, `ScoreRules`, `SessionRules`, `ProgressData`
  (results, settings, play-test stats, report text).
- `scripts/services/` — `SaveService` (temp-file + rename, corrupt file kept as `.corrupt`), `AudioService` (synthesized SFX).
- `scripts/game/` — `GameSession` (headless-capable level runner), `LevelLoader`, `BlockBody`, `TargetBody`,
  `ProjectileBody`, `StaticBox`, `AimController`, `BurstEffect`, `Backdrop`, `Palette`.
- `scripts/ui/` — `GameScreen`, `Hud`, `MenuScreen`, `SettingsPanel`, `SafeArea`, `StarRow`, `Icon` (vector icons),
  `UiKit` (theme + widgets). `scripts/main.gd` is the app root (`scenes/main.tscn`); it owns saving and applies settings.
- Collision layers: 1 static, 2 blocks, 3 targets, 4 projectile; everything collides with everything.
- Target breaks (only after the first launch "arms" it) on: contact impulse > 220, a direct projectile touch faster than 200 px/s,
  a velocity change > 400 px/s in one step, or leaving the play area. Glass breaks on impulse > 300.
- `export_presets.cfg` (committed): "Android Debug" APK (arm64 + x86_64), "Android Release" AAB (Gradle; arm64 + armv7),
  "Android Release APK" (arm64 + armv7). Package `dev.imrn.perfectsmash`, VIBRATE only, immersive + edge-to-edge.
  No secrets: signing comes from `GODOT_ANDROID_KEYSTORE_*` environment variables.
- Tools: `solve_levels.gd` (solution search), `physics_report.gd` (repeatability + cost), `capture_screens.gd`
  (UI review), `render_store_art.gd` (Play art), `render_icons.gd`, `build_android.sh`.

## Toolchain

- Godot 4.7.2.stable.official, GDScript, GL Compatibility renderer. No third-party addons.
- Owner machine: Windows 11 (winget `GodotEngine.GodotEngine`). Also verified in a Linux container (Ubuntu 24.04,
  OpenJDK 21, apksigner 0.9 / zipalign from Ubuntu packages).
- Built APK manifest: minSdk 24, targetSdk 36, versionCode 1, versionName 0.2.0, only `android.permission.VIBRATE`.

## Build / test status (verified 2026-11-05, Linux container)

- Headless: `godot --headless --fixed-fps 60 -s tests/run_tests.gd` → 65 passed, 0 failed, 1 skipped (GUI routing needs a window).
- Windowed (Xvfb): `godot --resolution 1280x720 --fixed-fps 60 -s tests/run_tests.gd` → 66 passed, 0 failed, 0 skipped (303 s).
- Unit only: append `-- --unit` (includes layout and release-config suites).
- Physics report: `godot --headless --fixed-fps 60 -s tools/physics_report.gd -- --replays=10` → 200/200 replays won,
  1 distinct end state per level; also identical with `--no-warmup`. Peak 11 live bodies; mean frame 0.25 ms,
  worst about 6 ms (desktop CPU).
- Android: `tools/build_android.sh debug` and `release-apk` built and passed `apksigner verify`
  (release APK signed with a throwaway test key; not an upload key). `release-aab` not run here (Google Maven blocked
  in the container).
- Store art: `godot --resolution 1920x1080 --fixed-fps 60 -s tools/render_store_art.gd` (+ `--feature` at 1024x500).

## Known issues and risks

- **Physics variance seen on Windows only.** Earlier, an identical L01 shot occasionally resolved differently on the owner's
  Windows build. On Linux (same Godot version) 200 sequential replays, with and without the warm-up, were bit-identical.
  So the variance is platform- or machine-specific, not inherent to the levels. Mitigations stay in place (3 replays,
  ≥2 wins; perturbation-robust solutions; warm-up). Device behaviour is still unknown.
- Solutions are verified on desktop builds only; plan §2 says not to promise identical physics across devices.
- Difficulty order comes from solver win rate; it needs human play-testing.
- Godot's headless display server doesn't route mouse events to GUI controls, so the HUD-button test only runs windowed.
- On 4:3 tablets the level shows a lot of empty sky above the structure (layout fits; purely cosmetic).
- Safe-area insets are untested on real cutout hardware; edge-to-edge mode depends on them.

## Waiting on the owner (nothing else is blocked on these)

1. **Physical-device run** of the checklist in `docs/release.md` §4 (M0/M4).
2. **Upload keystore** and **AAB build** on the owner's machine (`tools/build_android.sh release-aab`).
3. **Play Console:** create the app, Play App Signing, listing, declarations (`store/play_console_answers.md`), internal → closed testing.
4. **Decisions:** target-audience age groups (suggested 13+), where to host the privacy policy, support contact email.
5. **Review of decisions made without the owner (2026-11-05):** committing `export_presets.cfg`; replacing the menu's
   sound/vibration buttons with a settings gear; version 0.2.0; armeabi-v7a included in release builds; edge-to-edge
   display; local play-test stats and the copyable report.
6. Production release approval (plan M6).

## Next recommended actions

1. Run the device checklist; fix anything it finds.
2. Build the AAB, upload to internal testing, then closed testing with 5–10 players (plan §12 experiments).
3. Collect play reports; re-tune the level order and the aim-guide default from them.

## Owner decisions

- Landscape orientation: approved (2026-11-01).
- Product name "Perfect Smash": approved; `plan.md` revised (rev 1, name only).
- Package ID `dev.imrn.perfectsmash` (owner domain imrn.dev).
- Per-shot timer (2026-11-02): not added to the core mode, because time pressure works against deliberate puzzle-solving and
  touch aiming. A separate timed mode, a speed badge, or a fast-forward during collapse may be considered later as experiments.
- 2026-11-05: owner asked for all pending milestones to be completed without blocking on them; owner-only steps
  (signing, review, store submission) are deferred to the owner.
