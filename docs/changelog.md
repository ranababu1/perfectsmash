# Changelog

All meaningful changes, newest first.

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
