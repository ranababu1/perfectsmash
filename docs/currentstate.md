# Current State

_Last updated: 2026-11-05 · Version 0.3.0 (unreleased, version code 1) · Branch `claude/quirky-bardeen-xmkcnl` · Remote `origin` (github.com/ranababu1/perfectsmash)_

## Purpose and phase

Perfect Smash (originally titled "Smash Theory") is a 2D physics demolition puzzle for Android (Godot 4). See `plan.md`.
Since 0.3.0 it is a **story campaign, "Operation Rebuild": 100 missions in five chapters**, with a briefing before
and a debrief after every mission (owner request, 2026-11-05; design and resume checklist in `docs/campaign_plan.md`).
**Phase:** release candidate preparation. Everything that doesn't need the owner's devices, accounts or keys is
done; see "Waiting on the owner".

## Milestones (plan §11)

| Milestone | Status | Evidence / what remains |
|---|---|---|
| M0 Physics spike | Partial | Aiming and launching work on desktop and the emulator; UI input cannot launch (tested). Frame cost measured on desktop. **Physical-device run pending (owner).** |
| M1 Rules and objective model | Done | Unit tests for budget, all objective types, fail-on-loss, settle/timeout, restart |
| M2 Playable prototype | Done | No body, fuse or timer can hang a level (10 s timeout; fuses block settling only while burning) |
| M3 Content and progression | Done (automated) | 100 validated missions, each with a solver-verified solution replayed by the tests; story covers all 100; save migrates v1→v3. Human play-test of difficulty pending |
| M4 Usability and performance | Done (automated) / device check pending | Layout tests (menu, settings, HUD, pause, results, briefing, debrief) at 6 aspect ratios; safe-area insets; lifecycle tests. Device checklist in `docs/release.md` §4 |
| M5 Closed testing | Ready to start | Store art + copy for the campaign, privacy policy, Data safety answers, local play report. Needs Play Console setup (owner) |
| M6 Release candidate | Ready except signing/upload | Presets, build script, export plugin. AAB / Gradle release APK build, upload key, Play review and release approval: owner |

## Feature status

| Feature | Status | Notes |
|---|---|---|
| Level data + validation (`LevelDefinition`, `LevelCatalog`) | Implemented | `data/levels.json`, 100 levels (L01–L20 hand-built, L21–L100 from `tools/build_campaign.gd`) |
| Physics session (`GameSession`, `LevelLoader`, bodies) | Implemented | Wood, stone, glass, explosive and cargo blocks; walls and bounce pads; cores and drones |
| Objectives | Implemented | `destroy_targets`, `topple`, `deliver` (crates into a drop zone); drones and cargo as fail conditions |
| Explosions | Implemented | Crates and blast shots; radial velocity change, chained fuses (4 steps), deterministic order; glow effect + small camera shake |
| Ammo | Implemented | Standard, heavy, blast; per shot; colored pips and loaded ball show it |
| Story (`StoryCatalog`, `data/story.json`) | Implemented | 5 chapters, 5 speakers, briefing + debrief for all 100, chapter cards, failure pools |
| Briefing screen | Implemented | Chapter/mission header, typewriter transcript, blueprint schematic, objective + intel, Skip / Begin; level settles underneath |
| Debrief / failure lines | Implemented | In the result panel; failure reason (out of shots / drone lost / crate lost) |
| Voice narration (`Narrator`) | Implemented / untested on device | OS text-to-speech, per-speaker pitch, setting "Voice narration" (default on). No voices in the container, so only the silent path ran here. Android 11+ needs the TTS query, which is added in Gradle builds only |
| Chapter menu | Implemented | 5 tabs × 20 tiles; locked chapters disabled; opens on the next mission's chapter |
| Drag-back aiming + partial trajectory preview | Implemented | 0.3 s preview; "Aim guide" switch for the plan §10 experiment |
| Stars, local progress, unlocks | Implemented | `user://progress.json`, schema v3 (v1/v2 migrate) |
| Settings panel | Implemented | Sound, vibration, aim guide, voice narration, copy play report, reset progress |
| Local play-test stats | Implemented | Per-level attempts/wins/losses/timeouts; report copied to the clipboard on request |
| Safe-area (cutout) insets | Implemented | Mobile only; untested on a real cutout device |
| Sound (procedural) + vibration | Implemented | New `boom` and `radio` sounds; vibration untested on device |
| Pause on background / Android back | Implemented | Back closes Settings, leaves a briefing, toggles pause; automated tests |
| Android export | APK verified / AAB not built here | Debug APK builds and verifies here. Release APK and AAB now use Gradle (blocked in this container: Google Maven) |
| Store listing materials | Implemented | `store/`: feature graphic, 6 screenshots, listing, privacy policy, Play Console answers |
| Analytics | Deliberately absent | Plan §10 |
| Localization | Not in scope | UI and story text are English |

## Architecture

- `scripts/core/`: pure rules, no nodes. `GameConfig` (tuning incl. ammo, blast, bumpers), `LevelDefinition`,
  `LevelCatalog`, `ObjectiveEvaluator` (PENDING/MET/FAILED), `SimulationMonitor`, `DestructionRules`, `ScoreRules`,
  `SessionRules`, `ProgressData`, `StoryCatalog`.
- `scripts/services/`: `SaveService`, `AudioService` (synthesized SFX), `Narrator` (OS TTS).
- `scripts/game/`: `GameSession` (headless-capable level runner, explosions), `LevelLoader`, `BlockBody`, `TargetBody`
  (cores and drones), `ProjectileBody` (ammo), `StaticBox` (walls, bumpers), `AimController`, `BurstEffect`,
  `ExplosionEffect`, `Backdrop`, `Palette`.
- `scripts/ui/`: `GameScreen`, `Hud`, `MenuScreen` (chapter tabs), `BriefingScreen`, `DialogueBox`, `LevelSchematic`,
  `MissionText`, `SettingsPanel`, `SafeArea`, `StarRow`, `Icon`, `UiKit`. `scripts/main.gd` is the app root; it owns
  saving, narration and the story, and shows a briefing before every mission.
- `addons/android_tts/`: editor-only export plugin adding the TTS `<queries>` manifest entry (Gradle builds).
  It is excluded from exported packages.
- Collision layers: 1 static, 2 blocks, 3 targets/drones, 4 projectile.
- Breaking (only after the first launch arms the level): cores/drones on contact impulse > 220, a projectile touch
  > 200 px/s, a jolt > 400 px/s, or leaving the play area; glass and explosive crates on impulse > 300 (crates also on
  a projectile touch); blast velocity change `900 × (1 − d/170)`.
- Tools: `build_campaign.gd` (missions 21–100), `solve_levels.gd` (solutions; `--out` for parallel runs),
  `catalog_format.gd`, `physics_report.gd`, `capture_screens.gd` (`--levels=` gallery), `render_store_art.gd`
  (`--probe=ids`), `render_icons.gd`, `build_android.sh`.

## Toolchain

- Godot 4.7.2.stable.official, GDScript, GL Compatibility renderer. No third-party addons (one in-repo export plugin).
- Owner machine: Windows 11. Also verified in a Linux container (Ubuntu 24.04, OpenJDK 21, apksigner 0.9 / zipalign
  from Ubuntu packages, export templates 4.7.2).
- Debug APK manifest (0.3.0): minSdk 24, targetSdk 36, versionCode 1, versionName 0.3.0, only `android.permission.VIBRATE`.

## Build / test status (verified 2026-11-05, Linux container)

- Headless: `godot --headless --fixed-fps 60 -s tests/run_tests.gd` → 84 passed, 0 failed, 1 skipped (34 s). Includes
  every mission standing before launch and every stored solution winning ≥2 of 3 replays.
- Windowed (Xvfb): WINDOWED_RESULT
- Physics report (`tools/physics_report.gd -- --replays=3`): 300/300 replays won, one end state per mission, peak 17
  live bodies (L100), mean frame 0.20 ms, worst 8.2 ms on the container CPU.
- Campaign build: `godot --headless --fixed-fps 60 -s tools/build_campaign.gd -- --check` → 80 levels, all stable,
  all with solutions.
- Android: `tools/build_android.sh debug` → signed and verified. Release builds need Gradle, which can't run here.

## Known issues and risks

- **Narration is untested with a real voice.** The container has no TTS voices. On a device, check that speech works,
  that per-speaker pitch sounds right, and that the AAB manifest has the TTS query (`docs/release.md`).
- **Supply drops need precise aim:** solver win rates of 1.2–3.7% of its aim grid (cores are typically 10–60%).
  L80 (chapter 4 finale) has a solution that is sensitive to ±1% power. Play-test these first.
- Difficulty within chapters follows the design table, not player data.
- Physics variance was only ever seen on the owner's Windows machine; Linux replays are bit-identical. Device behaviour
  is unknown, and solutions are verified on desktop builds only (plan §2).
- Godot's headless display server doesn't route mouse events to GUI controls, so the HUD-button test only runs windowed.
- Safe-area insets are untested on real cutout hardware.

## Waiting on the owner (nothing else is blocked on these)

1. **Physical-device run** of `docs/release.md` §4, including narration and the campaign items.
2. **Upload keystore** and **Gradle builds** (`release-aab`, `release-apk`) on the owner's machine.
3. **Play Console:** app, Play App Signing, listing (`store/listing.md`), declarations (`store/play_console_answers.md`,
   re-check the violence answer for explosions), internal → closed testing.
4. **Decisions:** target-audience age groups (suggested 13+), privacy-policy hosting, support email.
5. **Review of decisions made without the owner:** the Operation Rebuild story and cast; new mechanics beyond plan §4
   (ammo types, explosives, cargo, drones, bounce pads); 100 missions; OS text-to-speech narration (default on);
   Gradle for the tester APK; camera shake on explosions; version 0.3.0. Earlier: committed export presets,
   settings gear, armeabi-v7a, edge-to-edge, local play report.
6. Production release approval (plan M6).

## Next recommended actions

1. Device run: narration, touch feel on supply drops, performance on L100 (17 bodies).
2. Closed test with 5–10 players; use play reports to re-tune supply-drop missions and the chapter difficulty curve.
3. If any mission is reported unfair, change its design or variant in `tools/build_campaign.gd`, rebuild with
   `--check`, re-solve it, and run the tests.

## Owner decisions

- Landscape orientation: approved (2026-11-01).
- Product name "Perfect Smash": approved; `plan.md` revised (rev 1, name only).
- Package ID `dev.imrn.perfectsmash` (owner domain imrn.dev).
- Per-shot timer (2026-11-02): not added to the core mode.
- 2026-11-05: complete all pending milestones without blocking on the owner; owner-only steps deferred.
- 2026-11-05: 100 levels with sequential unlocks, an IGI-style narrated storyline before and after every level, and
  varied gameplay; built to the agent's judgement without check-ins (`docs/campaign_plan.md`).
