# Current State

_Last updated: 2026-11-01 · Version 0.1.0 (unreleased) · Branch `master` · Remote `origin` (github.com/ranababu1/perfectsmash)_

## Purpose and phase

Perfect Smash (originally titled "Smash Theory") is a compact 2D physics destruction puzzle for Android (Godot 4). See `plan.md`.
**Phase:** M2 (playable prototype) reached on desktop, with M3 content (20 levels) in place.
M0's "on a physical Android device" criterion is **not yet verified**: no device test or Android export has been done.

## Feature status

| Feature | Status | Notes |
|---|---|---|
| Level data + validation (`LevelDefinition`, `LevelCatalog`) | Implemented | `data/levels.json`, 20 levels |
| Physics session (`GameSession`, `LevelLoader`, bodies) | Implemented | Wood, stone, glass blocks; static surfaces; targets |
| Objectives | Implemented | `destroy_targets`, `topple` (all blocks below a line) |
| Shot budget / win-loss (`SessionRules`) | Implemented | Evaluated only after settle or timeout |
| Settling + 10 s hard timeout (`SimulationMonitor`) | Implemented | Thresholds in `GameConfig` |
| Drag-back aiming + partial trajectory preview | Implemented | 0.3 s preview (plan §5 allows; experiment pending) |
| Stars (par-based), local progress, unlocks | Implemented | `user://progress.json`, schema v1 |
| Menu, HUD, pause, results, retry/next | Implemented | Built in code (`scripts/ui`) |
| Sound (procedural) + vibration settings | Implemented | Vibration untested on device |
| Pause on app background / Android back | Implemented | Untested on device |
| Android debug export | Partial | Local gitignored preset; debug-signed APK runs on emulator; no release signing |
| Analytics | Planned (deliberately absent) | Plan §10: privacy review first |
| Localization | Not in scope for this milestone | UI strings are hard-coded English |

## Architecture

- `scripts/core/` — pure rules, no nodes: `GameConfig` (tuning), `LevelDefinition`, `LevelCatalog`,
  `ObjectiveEvaluator`, `SimulationMonitor`, `DestructionRules`, `ScoreRules`, `SessionRules`, `ProgressData`.
- `scripts/services/` — `SaveService` (temp-file + rename, corrupt file kept as `.corrupt`), `AudioService` (synthesized SFX).
- `scripts/game/` — `GameSession` (headless-capable level runner), `LevelLoader`, `BlockBody`, `TargetBody`,
  `ProjectileBody`, `StaticBox`, `AimController`, `BurstEffect`, `Palette`.
- `scripts/ui/` — `GameScreen`, `Hud`, `MenuScreen`, `StarRow`, `UiKit`. `scripts/main.gd` is the app root (`scenes/main.tscn`).
- Collision layers: 1 static, 2 blocks, 3 targets, 4 projectile; everything collides with everything.
- Target breaks (only after the first launch "arms" it) on: contact impulse > 220, a direct projectile touch faster than 200 px/s,
  a velocity change > 400 px/s in one step, or leaving the play area. Glass breaks on impulse > 300.
- `tools/solve_levels.gd` — design tool: sweeps launch angle × power in parallel isolated worlds, picks a solution
  that still wins under ±1% power / ±0.6° aim perturbation, and writes it to `levels.json` (`--write`).

## Toolchain

- Godot 4.7.2.stable.official (winget `GodotEngine.GodotEngine`), GDScript, GL Compatibility renderer.
- No third-party dependencies or addons.

## Build / test status (verified 2026-11-01)

- Headless: `godot_console --headless --fixed-fps 60 -s tests/run_tests.gd` → 50 passed, 0 failed, 1 skipped.
- Windowed (adds GUI input-routing check): `godot_console --resolution 1280x720 --fixed-fps 60 -s tests/run_tests.gd` → 51 passed, 0 failed.
- Unit only: append `-- --unit`.
- Re-verify levels after any physics/tuning change: `godot_console --headless --fixed-fps 60 -s tools/solve_levels.gd -- --write`, then run tests.
- Android debug APK: `godot_console --headless --export-debug "Android Debug" build/perfectsmash-debug.apk` works with a local
  `export_presets.cfg` (gitignored; arm64-v8a + x86_64, VIBRATE permission, package `dev.imrn.perfectsmash`, the owner's standard `dev.imrn.<app>` scheme).
  Ran on the emulator `sdk_gphone16k_x86_64` and levels 1–3 were played through by hand. The emulator build predates the final L01 tweak.
  **No physical-device test yet.**

## Known issues and risks

- **Physics is not bit-reproducible run to run:** an identical shot from an identical settled layout can occasionally resolve
  differently (seen with L01 on Godot 4.7.2; most likely contact ordering depending on engine-internal state). Mitigations: tests
  replay each solution 3× and require ≥2 wins, the solver requires perturbation-robust shots, and a warm-up replay runs first
  (`tests/physics_warmup.gd`). L13's best two-shot solution is still flagged fragile by the solver.
- Solutions are verified on this desktop build only. Plan §2 says not to promise identical physics across devices; levels need device checks.
- Difficulty curve is uneven: from solver win rates, L08 Dominoes (~56% of grid shots win) is easier than L01, and L10/L11/L13/L16 are the hardest. Needs play-test tuning.
- Godot's headless display server doesn't route mouse events to GUI controls, so the HUD-button test only runs windowed (it reports SKIP when headless).
- Menu layout is tight vertically at 720px; check on short, wide phones.

## Next recommended actions

1. Test on a physical Android device (M0/M4): touch feel, performance, vibration, pause/resume.
2. Play-test the 20 levels; reorder/tune for a smoother curve (use the solver's win rate as a guide).
3. Run the trajectory-preview experiment (plan §10) — the preview length is `GameConfig.PREVIEW_DURATION`.
4. Investigate the run-to-run physics variance (minimal repro; check the engine issue tracker).
5. Decide on app icon/branding and store assets before closed testing (M5).

## Owner decisions (2026-11-01)

- Landscape orientation: approved.
- Product name "Perfect Smash": approved; `plan.md` revised (rev 1, name only).
- Package ID `dev.imrn.perfectsmash` (owner domain imrn.dev).

No decisions are currently pending.
