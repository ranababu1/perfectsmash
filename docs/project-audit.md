# Project Audit — M1 (2026-11-09)

Baseline audit performed before the Temporal: First Jump identity migration and renderer evaluation.
Everything below was checked against the repository and local toolchain on 2026-11-09 unless marked otherwise.

## 1. Repository and toolchain

| Item | Finding |
|---|---|
| Remote | `origin` → `git@github.com:ranababu1/temporal-chapter1.git` (SSH form of the canonical repo) |
| Branch | `main`, clean working tree at `4756073` |
| History | Documentation commits on top of the Perfect Smash prototype. The older working copy `../smashtheory` (remote `perfectsmash`, branch `master`) still exists locally and holds the old gitignored export preset and build output. It was read, not modified. |
| Godot | `4.7.2.stable.official.ed1daf0bf` (`godot_console` on PATH via WinGet) |
| Export templates | Android only (`android_debug.apk`, `android_release.apk`, `android_source.zip`). **No iOS templates installed.** |
| Android SDK / JDK | SDK at `%LOCALAPPDATA%\Android\Sdk`, JDK Amazon Corretto 21 (from editor settings) |
| Devices | `adb devices`: none attached. AVDs available: `Pixel10Pro`, `Pixel_10a` (emulators only) |
| macOS / Xcode | Not available on this machine |
| Baseline tests | `godot_console --headless --fixed-fps 60 -s tests/run_tests.gd` → **50 passed, 0 failed, 1 skipped** (GUI routing needs a window). Matches the 2026-11-02 record. |

`docs/currentstate.md` still described the old `master` branch and `perfectsmash` remote; corrected in this change.

## 2. Architecture (reuse as-is)

The code is small (~2,300 lines of GDScript), cleanly layered and well tested. No rewrite is warranted.

- `scripts/core/` — node-free rules: `LevelDefinition` (parse + validate), `LevelCatalog`, `ObjectiveEvaluator`, `SimulationMonitor` (settle + 10 s timeout), `DestructionRules`, `ScoreRules`, `SessionRules`, `ProgressData` (save schema v1), `GameConfig` (all tuning).
- `scripts/game/` — `GameSession` (headless-capable physics session), `LevelLoader`, `BlockBody`/`TargetBody`/`ProjectileBody`/`StaticBox`, `AimController`, `BurstEffect`, `Backdrop` (procedural sky/hills), `Palette`.
- `scripts/services/` — `SaveService` (temp-file + rename, corrupt-file quarantine), `AudioService` (procedurally synthesised SFX, no audio files).
- `scripts/ui/` — `MenuScreen`, `GameScreen`, `Hud`, `Icon` (vector icons), `StarRow`, `UiKit` (theme built in code).
- `scripts/main.gd` — app root: menu ↔ game switching, fade veil, Android back, auto-pause on background.
- All visuals are drawn procedurally (`_draw`), there are **no texture assets** besides app icons. This is cheap on any renderer and makes the chapter reskin a contained change to `Palette`, `Backdrop` and body `_draw` methods.

### Supported level vocabulary (from code)

- Objectives: `destroy_targets`, `topple` (with `line_y`).
- Materials: `wood`, `stone`, `glass` (glass breaks above impulse 300).
- Elements: `statics` (fixed boxes, optional rotation), `blocks`, `targets` (radius 8–60), one `launcher`.
- Limits: shots 1–5, par ≤ shots, everything inside 1280×640 world, max launch speed 1300.
- Optional `solution` array of verified launch velocities (used by tests, never shown).

Everything in `docs/level-design-spec.md` uses this vocabulary. **No schema extension is required** for the 100 levels. Chapter membership can be derived from catalog position (20 per chapter) or added as an optional field later; this is a presentation concern only.

### Save and progression

- `user://progress.json`, schema v1: `levels{id: {stars, best_shots}}` + `settings{sound, vibration}`.
- Level IDs are stable save keys; unlocking is sequential by **catalog order** (level *n* unlocks when *n−1* is completed).
- Appending levels 21–100 after the existing 20 is save-compatible. Re-ordering the existing 20 would change which levels an existing save sees as unlocked (no data loss, but unlocks could shift).
- No story/cinematic state exists yet. A v2 schema (watched sequences, separate music/voice/SFX toggles) will need a tested v1 → v2 migration; v1 currently rejects any other version.

## 3. The existing 20 levels → Chapter I

All 20 existing levels belong to Chapter I (levels 1–20). Chapters II–V (80 levels) are entirely new content.
The spec's Chapter I table was clearly written from the original level IDs. Current display order (set 2026-11-02 by solver win rate) differs from the spec order.

| Spec # | Spec mission | Existing level | Fit |
|---:|---|---|---|
| 1 | First Contact | L01 First Contact | Exact. Spec shots 2, current 3 |
| 2 | The Welcome System | L02 Tall Order | Exact |
| 3 | Traffic of One | L03 Support Beam | Exact |
| 4 | Supply Chain | L04 Stacked | Exact |
| 5 | The Safety Layer | L05 Glass House | Exact |
| 6 | Cold Storage | L06 Neighbours | Exact |
| 7 | Blind Spot | L07 Heavy Lid | Exact |
| 8 | Human Override | L08 Dominoes | Exact |
| 9 | Redundancy | L09 Below the Line | Exact (topple) |
| 10 | The Replica | **L11 Far Apart** | Good (two separated towers, two shots) |
| 11 | Priority One | **L18 Over the Wall** | Good (arc over a static wall) |
| 12 | No Exceptions | L12 Pyramid | Exact |
| 13 | The Quiet District | L13 Skylight | Exact |
| 14 | Root Access | L14 Shield Wall | Exact |
| 15 | The Directive | L15 Twin Glass | Exact |
| 16 | Failsafe | L16 Staircase | Exact |
| 17 | Last Backup | L17 Timber | Exact (topple) |
| 18 | Cascade | **L10 High Ledge** | **Weak.** Spec wants a tall barrier + high arc (duplicates #11); L10 is "push a block off a ledge onto a target". Recommend rewriting spec #18 to match L10 rather than redesigning a working level. |
| 19 | Central Logic | L19 Chain Reaction | Exact |
| 20 | The Machine That Decided | L20 Grand Collapse | Exact (finale) |

**Owner decision needed (not blocking M2/M3):** adopt the spec order above, or keep the 2026-11-02 difficulty order and only retitle. The spec order puts L04/L07 earlier and L10/L11/L18 in different slots; solver win rates should be re-run on the chosen order before locking it.

Other level observations:
- Spec shot budgets mostly match; L01 (3 vs 2), L11 (3, spec 2) and L13 (3, spec 2) differ slightly. Shots are a ceiling, not difficulty; keep current values unless play-testing says otherwise.
- The current titles/hints are Perfect Smash flavoured ("Tall Order", "Hit the red core"); they will be rewritten as narrative titles when the Chapter I reskin lands, keeping IDs.

## 4. Application identity and signing

| Item | Before | Notes |
|---|---|---|
| `application/config/name` | `Perfect Smash` | Also drives the desktop `user://` folder name |
| Menu title | `PERFECT SMASH` (hard-coded in `menu_screen.gd`) | Tagline "One smart hit. A spectacular chain reaction." |
| Android package | `dev.imrn.perfectsmash` | Only in the gitignored local `export_presets.cfg` of `../smashtheory`; this clone has no preset |
| iOS bundle ID | None — no iOS preset has ever existed | |
| Signing | Godot debug keystore only, at `%APPDATA%\Godot\keystores\debug.keystore`, configured in editor settings (outside Git). **No release keystore found** in either working copy. Nothing signing-related is in Git. |
| Store status | Changelog records debug APKs on emulators only, "changed before any release". No evidence of any Play Store or App Store listing in the repository. **Needs owner confirmation.** |

### Store migration implications of `dev.imrn.temporal1`

- An Android application ID is permanent for a Play listing. A new ID is a **new app** in Play Console: no update path from `dev.imrn.perfectsmash`, no carried-over installs, ratings, reviews or statistics, and on device it installs side by side with the old app (separate data directory, so no save carry-over).
- If `dev.imrn.perfectsmash` was never uploaded to Play (which is what the repository records), there is no store impact. Only local debug installs are affected.
- If it *was* uploaded anywhere (even internal testing), that listing stays as-is. The package name can never be reused for another app, and the new app needs its own listing, Play App Signing enrolment and upload key.
- iOS: the bundle ID `dev.imrn.temporal1` must be registered in the Apple Developer account (explicit App ID) before signing. It is also permanent per App Store Connect record.
- Desktop dev saves: Godot derives the `user://` folder from `config/name`. To make the save location independent of the display name (which also contains a `:`), the migration sets a custom user dir name.

## 5. Renderer and export configuration

- `rendering/renderer/rendering_method="gl_compatibility"` and `rendering_method.mobile="gl_compatibility"` — production baseline, unchanged.
- ETC2/ASTC import enabled. Physics 60 Hz with interpolation. 1280×720 canvas, `canvas_items` / `expand`, sensor-landscape.
- Old Android preset: arm64-v8a + x86_64, non-Gradle build, immersive mode, vibrate permission, adaptive icons, version code 1.
- The rendering load is light: procedural 2D polygons, one `BurstEffect`, no shaders, no textures. The renderer choice will matter more once chapter artwork, parallax and cinematics land.

## 6. Risks

| Risk | Severity | Mitigation |
|---|---|---|
| No physical Android or iOS device and no Mac available here | High for M3/M8 | Build the measurement harness now and run it on desktop and emulator for functional checks only. Physical-device numbers are **blocked** until hardware is connected. |
| No iOS export templates | Medium | Install 4.7.2 iOS templates when an iOS preset is needed; the Xcode build still needs macOS |
| Physics is not bit-reproducible run to run | Medium | Already handled: tests accept 2 of 3 replays; solver keeps perturbation-robust shots. Keep this for new levels. |
| 80 new levels (chapters II–V) | High effort | Batches of 5 with the solver and playthrough tests; the solver also works for authoring |
| Story state needs save schema v2 | Medium | Explicit, tested v1→v2 migration before cinematics ship |
| Untracked export presets | Low/medium | Presets are gitignored, so identity in exports depends on each machine. Documented required values in `currentstate.md`. |
| Unreviewed generated music and concept art | Medium | Not integrated; licensing evidence required first |

## 7. Recommended implementation sequence

1. **M2 identity** (this change set): name, menu title, user dir, local Android preset `dev.imrn.temporal1`, documented iOS bundle ID, docs.
2. **M3 renderer evaluation:** add a repeatable benchmark tool (scripted scenes, frame-time stats, JSON report) that runs under either renderer via `--rendering-method` without touching production settings. Collect desktop and emulator smoke data now; collect physical-device data when hardware is available.
3. **M4 foundations:** save schema v2 + migration; chapter metadata; `MusicDirector` and split audio settings; reskin hooks in `Palette`/`Backdrop` per chapter.
4. **M5 vertical slice:** reskinned Chapter I level plus first levels of chapters II–V (21, 41, 61, 81), cinematic player with the opening sequence.
5. **M6–M9** as in the brief.

---

# Phase 0/1 re-audit against plan revision 5 (2026-11-09, `6b75504`)

Re-run after the owner pushed the tactical-destruction direction (6 doc commits, `812cd1f`..`6b75504`). Working tree: clean apart from two untracked local items: `assets/music/bg.mp3` (unapproved candidate) and `scripts/ui/cinematic_player.gd` (written before the plan change; untested, not wired in).
Tests on `6b75504`: `godot_console --headless --fixed-fps 60 -s tests/run_tests.gd` → **71 passed, 0 failed, 1 skipped** (GUI routing, needs a window).

## What carries over unchanged

| System | Files | Fit for revision 5 |
|---|---|---|
| Headless-capable physics session, settle detection, 10 s timeout | `game_session.gd`, `simulation_monitor.gd` | Reuse; per-shot settle needs rethinking for long missions (below) |
| 2D rigid-body physics, CCD projectile, material density/friction | `block_body.gd`, `projectile_body.gd`, `game_config.gd` | Reuse as the simulation plane under the 2.5D view |
| Data-driven, validated level loading | `level_definition.gd`, `level_catalog.gd`, `level_loader.gd` | Pattern reused for missions/components/weapons |
| Versioned save with migration (v2) | `progress_data.gd`, `save_service.gd` | Extend to v3 for mission points, Research Data, upgrades |
| Chapters, chapter scenery themes, cinematic data, MusicDirector | `chapter_catalog.gd`, `chapter_theme.gd`, `cinematic_catalog.gd`, `music_director.gd` | Still valid (Phase 4) |
| Test runner, solver, screenshot tool, renderer benchmark | `tests/`, `tools/` | Reuse; solver needs a weapon-aware variant later |
| Identity, export presets, Android debug pipeline | `project.godot`, local presets | Unchanged |

## Gaps against revision 5

1. **No damage model.** Breakage is binary: glass breaks above impulse 300, targets break on impulse > 220, a fast projectile touch, a velocity jolt or leaving the world. Wood and stone never break. Needs per-component integrity, per-material resistance and damage types (kinetic, blast).
2. **One projectile type, hard-coded.** `ProjectileBody` + `GameConfig` constants; no weapon definitions, ammunition, cooldown or area effects.
3. **Hard shot cap of 5** (`LevelDefinition.MAX_SHOTS`) and a turn flow that waits for the whole world to settle after every shot (`SessionRules`). 15-25 shot missions at 1-10 s settle per shot would drag.
4. **Scoring is stars by par only** (`ScoreRules`). No Mission Points, Research Data, target time or optional objectives.
5. **Objectives**: only `destroy_targets` (circular cores) and `topple`. No critical-asset components, multi-part objects, or structural dependencies beyond plain gravity.
6. **Presentation is flat 2D canvas drawing** (`_draw` per body). No camera angle, operative, depth cues or shadows.
7. **Aiming is slingshot drag-back** (`aim_controller.gd`): the exact interaction revision 5 wants to move away from.
8. Docs: `plan.md` header still says revision 4 although revision 5 is appended; the original level table (wood/stone/glass, ≤3 shots) is superseded by the appended section. Not edited by this audit.

## Technical risks

- **Depth honesty**: every collision happens in one 2D plane. The 2.5D view must place all destructible parts on that plane; depth is decoration only.
- **Physics cost of large facilities**: 15-25 shot institutions mean many bodies. Recommend that components stay frozen until a support they depend on breaks (authored dependencies), which is cheaper, more readable and more repeatable than simulating everything all the time.
- **Non-determinism** (already documented) matters more for long missions and for future Frontlines validation. Keep solver and replay tests tolerant; never rely on bit-exact replays.
- **Renderer**: a 3D presentation layer would change the renderer evaluation; re-run `tools/renderer_eval` with a 3D proxy before deciding.
- **Keep the existing 20 levels playable** while the prototype is built (separate mission entry, no breaking schema changes).

## Proposed greybox implementation (pending owner decisions)

- **Batch 1 (rules + data, headless):** `data/materials.json`, `data/weapons.json` (Kinetic Accelerator, Breach Charge), `MaterialCatalog`, `WeaponDefinition`/`WeaponCatalog`, `DamageRules` (kinetic damage from impact energy × material resistance; blast damage and impulse with distance falloff), upgrade-modifier hooks (base + 3 levels, no UI). Tests.
- **Batch 2 (destructible components + mission session, headless):** `ComponentBody` (integrity, material, critical flag, `depends_on` anchors), `MissionDefinition` (components, critical assets, objectives, ammunition, recommended shots, target time), `MissionSession` (weapon selection, cooldown/reload, ammo, continuous objective evaluation), legacy `GameSession` untouched. Tests.
- **Batch 3 (presentation):** angled camera/projection, greybox operative with idle/ready/aim/fire/reload/react states, weapon-specific aim, weapon-switch HUD, Helix greybox mission (server racks, relay mast, control node, AI core) reachable from the menu next to the legacy levels. Screenshots, emulator run.
- **Batch 4 (scoring):** Mission Points and Research Data per level-specific benchmarks; save v3 migration. Tests.

Likely files: new `scripts/core/{material_catalog,weapon_catalog,damage_rules,mission_definition,mission_scoring}.gd`, `scripts/game/{component_body,mission_session,kinetic_round,breach_charge,operative}.gd`, `scripts/ui/mission_screen.gd`, `data/{materials,weapons}.json`, `data/missions/helix_greybox.json`, small edits to `main.gd`, `menu_screen.gd`, `progress_data.gd` (v3), `tests/run_tests.gd`, new test suites.
