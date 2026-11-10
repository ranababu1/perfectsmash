# Current State

_Last updated: 2026-11-11 · Version 0.1.0 (unreleased) · Branch `main` · Remote `origin` (github.com/ranababu1/temporal-chapter1)_

This file was rewritten on 2026-11-11 as a concise handoff after a Stage 0 verification of the live repository. The previous, batch-by-batch version (Batches 1-5, slices A-G, renderer evaluation tables) is preserved in Git at `99f5ee3:docs/currentstate.md`; its measurements remain valid for the commits they name. Ownership and frozen contracts: `docs/interfaces.md`.

## Purpose and phase

Temporal: First Jump is an angled 2.5D tactical destruction puzzle (Godot 4.7.2, 3D presentation over 2D physics, Android + iOS). **Phase:** multi-agent campaign production (plan revision 6): grow one playable Helix mission into a 100-mission, five-chapter campaign.

## Feature status (verified 2026-11-11)

| Feature | Status | Evidence / notes |
|---|---|---|
| Mission rules, damage, structure, objectives, scoring, Research Data | Implemented | `scripts/core/`; suite below |
| Playable missions | **1 of 100** | `data/missions/helix_01.json` only |
| Mission catalog (100 slots, linear unlocks) | Implemented (M0) | `scripts/core/mission_catalog.gd`; app boots the first authored mission; `tests/campaign/` |
| Chapter select / mission select / campaign menu | Not started | ui-ux workstream |
| HUD, pause, results | Implemented | `scripts/mission/mission_hud.gd`; optional `next_pressed` hook not yet in the HUD |
| Operative + Kinetic Accelerator + Breach Charge | Implemented | production models and clips; 2 weapons only |
| Later chapter weapons | Planned, deferred | plan revision 6 |
| Upgrades | Rules only | `upgrade_rules.gd`; no UI |
| Save schema v4 | Implemented | migrates v1-v3 |
| Audio | Helix implemented | `data/audio.json` plans for `helix_01` only; chapters II-V not started |
| Cinematic player / Story Archive | Not started (deferred) | `data/cinematics.json` has 12 sequences |
| Settings screen | Not started | music/voice settings exist in save data only |
| Legacy 20 levels | Retired, frozen | still in the build for regression |

## Asset integration (verified 2026-11-11)

- **Library: complete.** All 2,270 files delivered in `origin/assets@f186977:generated_assets/` are on `main` under `assets/`: 2,182 byte-identical, 71 differ only by the `generated_assets/` → `assets/` rewrite, 17 carry further documented edits (handoff notes, app-icon `used_by`). Manifest: 1,473 delivered, 1,464 on `main` (the 9 legacy `ICON-*` entries removed with owner approval in `110c1d0`). Rights, approval and source fields unchanged; none cleared (1,463 `pending_review`, 1 `owner_instructed`).
- **Validator:** `python assets/tools/validate_asset_manifest.py` → `1464 checked, 1464 present, 417.0 MB … PASS`.
- **In-game: partial.** `data/integrated_assets.json` 618 ids + 10 presets (A 55, B 40, C 18, D 90, F 3, G 348, dependency 64); all five chapter kits load, only Helix is used by a mission. Coverage matrix (100/100) is asset availability, not playable content.
- **Import:** the local editor cache had stale texture UIDs on 17 Helix GLBs (34 `invalid UID` warnings; committed `.import` files were correct). Fixed by reimporting those GLBs; now 0 warnings. Fresh worktrees import cleanly from the committed metadata. A full clean reimport was not re-run in this session.

## Build / test status (2026-11-11)

- `godot_console --headless --fixed-fps 60 -s tests/run_tests.gd` → **217 passed, 0 failed, 1 skipped** (9.0 s) after M0 (213/0/1 before M0).
- `... -- --unit` → 173 passed, 0 failed, 0 skipped.
- Windowed `godot_console --resolution 1280x720 --fixed-fps 60 -s tests/run_tests.gd` on the Windows desktop (before M0) → 214 passed, 0 failed, 0 skipped (253.5 s; the legacy replay test dominates).
- Boot smoke `godot_console --headless --quit-after 180` → exit 0, no errors before exit.
- Exit-time leaks (harmless, test teardown): headless 32 ObjectDB instances / 14 resources; windowed also two GL textures (~341 KB each). Owner: performance-qa.
- Android export: last built from `4e2798a` (slice A era); not rebuilt in this session.

## Performance

All measurements are **desktop or Android emulator; no physical-device measurement exists.** Latest emulator run `4752214` (before slices C and E): median frame 16 ms, p99 45-48 ms, 46-54 fps. Slice C and slice E part 1 have no emulator run. Logs: `docs/benchmarks/`. Open: rack-collapse hitch (~160-210 ms, emulator), first load, APK texture-format split.

## Architecture (key files)

- Rules (node-free): `scripts/core/` — `mission_definition`, `mission_engine`, `mission_objectives`, `damage_rules`, `damageable_component`, `structural_dependency_system`, `material_catalog`, `weapon_catalog`, `weapon_state`, `mission_scoring`, `progress_data`, `upgrade_rules`, `chapter_catalog`, `mission_catalog`, `audio_catalog`, `cinematic_catalog`.
- Physics: `scripts/mission/mission_world.gd`, `component_body.gd`, `weapon_projectile.gd`.
- Presentation: `scripts/mission/view/` (`mission_view`, `asset_library`, `component_visual`, `debris_set`, `mission_vfx`, `operative_rig`, `projectile_visual`).
- Screen and HUD: `scripts/mission/mission_screen.gd`, `mission_hud.gd`, `mission_audio.gd`; app root `scripts/main.gd`.
- Services: `scripts/services/{save_service,audio_service,music_director}.gd`.
- Data: `data/{chapters,materials,weapons,scoring,audio,cinematics,integrated_assets}.json`, `data/missions/`, `data/environments/`.
- Tests: `tests/run_tests.gd` (listed suites + auto-discovered `tests/<folder>/test_*.gd`).

## Workstreams (plan revision 6)

| Workstream | Branch | Status |
|---|---|---|
| Orchestrator M0 (catalog, runner discovery, contracts, asset baseline) | `main` | Complete (this commit) |
| levels: Helix 02-20 | `agent/levels-100` | Not started |
| operative-weapons | `agent/operative-weapons` | Not started |
| ui-ux: campaign navigation, results next-mission, settings | `agent/ui-ux` | Not started |
| audio-atmosphere: chapter plans and ambience | `agent/audio-atmosphere` | Not started |
| performance-qa: validators, benchmark, leak triage | `agent/performance-qa` | Not started |

## Known issues and risks

- 99 missions to author; each must be physics-validated, not just schema-valid.
- `level-design-spec.md` §1-5 describe the retired game; its 2026-11-09 revision section governs.
- Physics is repeatable on one platform, not bit-identical across platforms (tolerances: `instructions.md` §11).
- Worktrees: each needs ~411 MB of assets plus a cold Godot import (~0.7 GB `.godot`).
- `.claude/agents/settings.json` is inert; Claude Code reads `.claude/settings.json` (owner to move it; agents could not modify permission settings).
- Rights: AI-assisted assets not commercially cleared; `gameplay_bed.ogg` licence unverified (release blocker).
- Physical-device validation: not done (human task).

## Decisions in force (owner defaults, 2026-11-11)

Owner merges PRs; Kinetic + Breach only for all 100 missions; cinematic player deferred; legacy levels kept frozen; plan revision 6 appended. Earlier owner decisions (platforms, renderer = GL Compatibility, landscape, app id `dev.imrn.temporal1`, Batch 5 rules, full asset integration approval) are unchanged; see `docs/plan.md` and `99f5ee3:docs/currentstate.md`.

## Next actions

1. Launch the five workstreams (M1).
2. Owner: move `.claude/agents/settings.json` to `.claude/settings.json` (and use `godot_console`).
3. Physical Android device run of `tools/renderer_eval/mission_benchmark.tscn` (human task).
