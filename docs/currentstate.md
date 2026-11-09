# Current State

_Last updated: 2026-11-10 · Version 0.1.0 (unreleased) · Branch `main` · Remote `origin` (github.com/ranababu1/temporal-chapter1)_

M1 audit findings (toolchain, architecture, level mapping, identity/signing, risks): see `docs/project-audit.md`.

## Purpose and phase

The project is a 2D physics destruction puzzle targeting Android + iOS (Godot 4.7.2). The owner has approved a major narrative/product direction: transform the existing puzzle into a story-driven time-travel destruction game, with a skippable opening cinematic, narrated chapter introductions/outros, and 100 levels across five chapters. The physics gameplay remains the foundation.

**Implementation phase:** Existing playable prototype with 20 levels. Narrative and 100-level expansion are documented/planned only. A production-level design specification now defines all 100 puzzle concepts, intended reasoning, shot budgets and validation gates. No cinematic player, story archive, chapter art reskin, new projectile art, 100-level content or background music has been integrated yet.

## Feature status

| Feature | Status | Notes |
|---|---|---|
| Level data + validation | Implemented | `data/levels.json`, 20 levels |
| Physics session and objectives | Implemented | Existing 2D physics puzzle; preserve behavior |
| Drag-back aiming and trajectory preview | Implemented | Existing input and preview |
| Stars, local progress, unlocks | Implemented | Existing save schema v1 |
| Menu, HUD, pause, results, retry/next | Implemented | Existing UI |
| Procedural SFX and vibration settings | Implemented | Device validation still required |
| Android debug export | Partial | Debug APK runs on emulator; physical-device test still pending |
| 100-level story arc | Planned | Five chapters of 20; see `narrative-bible.md` |
| Opening and chapter cinematics | Planned | 11 sequences; scripts in `narrative-bible.md` |
| Cinematic playback and Story Archive | Planned | Reusable data-driven player, skippable, subtitle/voice/music controls |
| Chapter-specific environment and object art | Planned | See `visual-audio-production-guide.md` |
| Temporal Charge reskin | Planned | Art/audio wrapper only; do not change physics tuning |
| Continuous gameplay music | Candidate on disk, not approved | `assets/music/bg.mp3` (owner-supplied 2026-11-09, **untracked, not integrated**). Metadata says "made with suno" (id `142466df-1693-4ac7-b0ca-3972206ef363`), not the Topview task recorded earlier. Commercial rights depend on the Suno plan at generation time: evidence needed. Objective check: 3:18, 48 kHz stereo MP3 ~181 kbps, −14.8 LUFS integrated, LRA 5.1 LU; 0.7 s silence at start, 0.4 s at end (fade in/out), so it is **not seamless as-is**. Needs a trimmed loop or an engine cross-fade, Ogg Vorbis conversion, and a human listening review |
| Save schema v2 | Implemented (`298a99f`) | Adds `story.seen` (watched sequence ids) and `settings.music` / `settings.voice`; v1 saves migrate in place without warnings and re-save as v2 |
| Chapter catalog | Implemented (`f33acf4`) | `data/chapters.json` + `ChapterCatalog`: 5 chapters, contiguous level ranges 1-100, 11 story sequence ids (`opening`, `chNN_intro`, `chNN_outro`, `finale`) |
| MusicDirector | Implemented, no track (`f8bbcde`) | Two-player cross-fade, ducking, keeps playing while paused, follows `music_enabled`. Created by `main.gd`; nothing plays until an approved track is assigned. No music toggle in the UI yet |
| Chapter scenery themes | Implemented (`28372ac`) | `ChapterTheme` (helix, vita, nova_grid, civitas, meridian): sky/hills/ground colours only; pieces keep shared colours. HUD shows "CHAPTER I · HELIX SYSTEMS · 2089". Menu keeps the default theme |
| Renderer evaluation harness | Implemented (`cd4cf4c`) | `tools/renderer_eval/`; see `docs/renderer-evaluation.md`. Desktop + emulator smoke results only; physical-device data pending |
| App identity: Temporal: First Jump / `dev.imrn.temporal1` | Implemented (2026-11-09) | Project name, menu title/tagline, plain charcoal boot splash, stable `user://` dir `temporal_first_jump`; local Android + iOS presets. App icon art is still the Perfect Smash design (pending new art) |
| iOS export | Not started | iOS preset defined locally (bundle ID only); no iOS export templates installed, no macOS/Xcode available |
| Season 2 | Planned concept | +50 levels, travel further back to 2041 |

## Narrative decisions (owner-approved direction, 2026-11-09)

- Player is an operative sent from a doomed future into the past to destroy the foundations of technologies and institutions that contribute to humanity's extinction.
- Five first-release chapters: The Machine That Decided (1-20), The Price of Perfection (21-40), The Energy Beneath (41-60), The Quiet Cage (61-80), The Convergence (81-100).
- Opening cinematic before level 1; each chapter has an intro and outro. All are skippable and should be replayable through a Story Archive.
- Level 100 ends in an apparent victory, then reveals extinction remains imminent. The new origin timestamp is 2041, setting up a further-past Season 2.
- Keep Control's identity mysterious. The story is designed for ongoing updates (+50 levels in the next content update).
- Core physics, scoring, input and level loop remain unchanged during the narrative reskin.

## Architecture

Existing architecture remains as documented below. Proposed story additions are not implemented:
- `scripts/core/` — gameplay rules, level definitions, objectives, scoring, session rules and progress data.
- `scripts/services/` — `SaveService`, `AudioService`.
- `scripts/game/` — `GameSession`, level loader, bodies, aim controller and effects.
- `scripts/ui/` — `GameScreen`, `Hud`, `MenuScreen`, pause/results and shared UI.
- `data/levels.json` — current 20-level catalogue.
- Added in M4: `scripts/core/chapter_catalog.gd` (+ `data/chapters.json`), `scripts/game/chapter_theme.gd`, `scripts/services/music_director.gd`; story state lives in `ProgressData` v2 (no separate StoryProgressService needed).
- Still planned: `CinematicPlayer`, cinematic definitions/catalog, `StoryArchiveScreen`.

## Documentation added/updated (2026-11-09)

- `docs/plan.md`: owner-approved revision 2 with story-driven 100-level direction and release/expansion requirements.
- `docs/narrative-bible.md`: complete five-chapter story, opening voiceover, chapter intro/outro scripts, 100-level mission map and Season 2 hook.\n- `docs/level-design-spec.md`: production design for all 100 levels, including intended puzzle layouts, skill progression, shot budgets and coding-agent acceptance criteria.
- `docs/visual-audio-production-guide.md`: art direction, chapter art bible, cinematic shot list, prompt templates, asset inventory, narration, music licensing and SFX guidance.

## Platform and renderer decision (owner-approved, 2026-11-09)

- Target platforms: Android + iOS.
- Primary quality priority: mobile performance, stable frame pacing and battery efficiency.
- Engine: Godot 4.7.2 with GDScript and built-in 2D physics.
- Proposed production renderer: Godot Mobile, pending a documented Compatibility-vs-Mobile evaluation.
- Intended backend: Vulkan on supported Android devices; Metal on supported Apple devices.
- Existing project remains on GL Compatibility until the renderer evaluation is completed and the owner approves any production renderer change.
- No minimum Android/iOS version, device support policy, renderer setting or export preset has been changed.

## Toolchain

- Godot 4.7.2.stable.official, GDScript, current project renderer: GL Compatibility.
- No third-party Godot dependencies or addons recorded.

## Last verified build/test status (2026-11-09, commit `86eb01c`)

- `godot_console --headless --fixed-fps 60 -s tests/run_tests.gd` → 50 passed, 0 failed, 1 skipped (GUI routing needs a window).
- `godot_console --resolution 1280x720 --fixed-fps 60 -s tests/run_tests.gd` → 51 passed, 0 failed, 0 skipped.
- `godot_console --headless --export-debug "Android Debug" build/temporal1-debug.apk` → built. `aapt2 dump badging`: package `dev.imrn.temporal1`, label "Temporal: First Jump", versionCode 1, versionName 0.1.0, minSdk 24, targetSdk 36, permission VIBRATE only. `apksigner verify`: signed with the Godot debug keystore.
- Installed and launched on the `Pixel10Pro` emulator (2856×1280): menu renders with the new title; logcat reports OpenGL ES 3.1 / Compatibility. Physical-device validation not yet done (no device attached).

## Export presets (local, gitignored) — required values

`export_presets.cfg` is gitignored, so set these on any new machine:
- **Android Debug:** `package/unique_name="dev.imrn.temporal1"`, `package/name="Temporal: First Jump"`, arm64-v8a + x86_64, `screen/immersive_mode=true`, `permissions/vibrate=true`, `launcher_icons/*` → the four PNGs in `assets/icon/`, export path `build/temporal1-debug.apk`. Debug signing uses the editor's debug keystore (`%APPDATA%\Godot\keystores\debug.keystore`).
- **iOS:** `application/bundle_identifier="dev.imrn.temporal1"`; team ID, provisioning and signing to be set on macOS/Xcode. Requires installing the 4.7.2 iOS export templates.
- No release keystore exists yet. When created, keep it outside the repo; Godot 4 stores keystore passwords in `.godot/export_credentials.cfg` (ignored), not in the preset.

## Identity migration notes

- `dev.imrn.temporal1` is a new application identity. It cannot update a Play listing created under `dev.imrn.perfectsmash`, and installs side by side with the old debug build (confirmed on the emulator: both packages present). Repository records show the old ID was never released; owner to confirm no store upload ever happened.
- Desktop `user://` moved to the custom dir `temporal_first_jump` (Windows: `%APPDATA%\temporal_first_jump`), independent of the display name. Old desktop dev saves under "Perfect Smash" are not migrated.

## Known issues and risks

- Physics is not bit-reproducible run to run; see prior notes and tests.
- Level solutions have only been verified on desktop; device validation remains necessary.
- Existing 20 levels are not yet assigned to the five new narrative chapters or reskinned.
- New level target of 100 must not lead to filler or fragile physics puzzles.
- Cinematic backgrounds must not reduce gameplay structure readability.
- Generated images/music require commercial-use rights and source/attribution evidence before release.
- Generated AI music may be unsuitable for seamless looping; listen, check quality and verify commercial-use terms before adoption.

## Next recommended actions

1. Run `tools/renderer_eval` on physical Android devices (matrix in `docs/renderer-evaluation.md` §4) and, on a Mac, on iPhone/iPad. Preliminary desktop/emulator evidence favours keeping Compatibility; Mobile shows first-use pipeline hitches. Obtain approval before changing production renderer or minimum OS/device support.
1a. Owner: confirm the music's Suno plan/commercial terms and listen-review it; owner: choose the Chapter I level order (`docs/project-audit.md` §3).
2. Produce a Temporal: First Jump app icon (current icon art is still the Perfect Smash ball-and-core design).
3. Review the narrative bible and lock the chapter scripts/story beats.
4. Review the six initial environment concept references and approve the visual language.
5. Finalise the Temporal Charge design and one representative gameplay reskin per chapter.
6. Download and review the generated gameplay music; verify commercial-use terms and loop quality. If unsuitable, choose a verified track under a suitable commercial licence.
7. Implement a small cinematic vertical slice (opening or Chapter I intro) with skip, subtitles, voiceover, music ducking and replay.
8. Reskin one existing level per chapter and validate readability on physical Android and iOS hardware where available.
9. Expand and validate content to 100 levels only after the vertical slice is approved.

## Existing owner decisions

- Android + iOS target platforms approved on 2026-11-09; mobile performance and battery efficiency are the primary priorities.
- Godot 4.7.2 remains the engine. Godot Mobile is the proposed production renderer, pending physical-device evaluation against the existing Compatibility renderer. Intended backends are Vulkan on supported Android devices and Metal on supported Apple devices.
- Production renderer and minimum supported OS/device versions remain unchanged pending test evidence and owner approval.

- Landscape orientation approved.
- Product renamed to Temporal: First Jump; Android/iOS ID `dev.imrn.temporal1` (approved 2026-11-09, replaces Perfect Smash / `dev.imrn.perfectsmash`). No store publication authorized.
- No per-shot timer in core mode.
- Narrative direction and 100-level Season 1 plan approved on 2026-11-09.

No gameplay implementation is claimed by this document.


## Owner-approved gameplay revision (2026-11-09)

The owner has approved a revised product direction. This is a design decision, not an implementation claim.

**Approved identity:** Angled 2.5D tactical destruction puzzle with a visible anonymous operative, multiple evolving weapons, story-specific destructible institutions, regular mission points, bonus Research Data and hybrid weapon upgrades.

**Physics decision:** Retain the existing Godot 2D physics simulation for the first angled 2.5D prototype. True 3D physics is not approved. Validate the angled presentation with a greybox before bulk asset production.

**Weapon direction:** Multiple distinct tactical weapons are approved in principle. Initial prototype scope is Kinetic Accelerator + Breach Charge. Later proposed unlocks include Penetrator, Pulse Cannon, Disruptor and Temporal Lance. These are planned, not implemented.

**Destruction and scoring:** Complex facilities may require multi-stage attacks and more than 3-4 shots, potentially 15-25+ where justified. Recommended shot budgets are scoring benchmarks rather than universal hard limits. Regular Mission Points and bonus Research Data are separate. Research Data funds player-selected weapon upgrades alongside automatic chapter technology unlocks. Speed and shot efficiency are rewarded relative to level-specific benchmarks, but must not dominate objective completion or thoughtful play.

**Online roadmap:** Leaderboards are approved after scoring stabilizes. Temporal Frontlines is the approved working name for asynchronous asymmetric multiplayer: players build persistent institutions from validated modular grid components; other players attack saved, versioned snapshots while the builder is offline. Real-time synchronized physics is explicitly out of scope for the initial multiplayer design. The backend must validate structures, match state, scores, rankings and rewards. Multiplayer must not block the first single-player campaign release.

## Feature status corrections

| Feature | Status | Notes |
|---|---|---|
| Angled 2.5D presentation | Approved / planned | Greybox prototype not yet verified |
| Visible operative | Approved / planned | Character art and animation not integrated |
| Multiple weapon framework | Approved / planned | Initial prototype: Kinetic Accelerator + Breach Charge; no implementation claimed |
| Story-specific destructible institutions | Approved / planned | Reusable component/material design pending prototype |
| Mission Points + Research Data economy | Approved / planned | Scoring/reward implementation not yet verified |
| Hybrid weapon upgrades | Approved / planned | Chapter unlocks plus player-selected upgrades; not implemented |
| Online leaderboards | Approved / planned | Later phase; backend not selected/implemented |
| Temporal Frontlines asynchronous multiplayer | Approved / planned | Persistent modular institutions and offline attacks; no backend or multiplayer implementation claimed |
| Real-time synchronized multiplayer | Excluded from initial scope | No simultaneous physics sessions planned |

## Asset integration: Helix slice A (2026-11-10, `fe828ad`..`88e3ce6`)

- Production library on `main` under `assets/` (owner PRs #2/#3); references updated from `generated_assets/` to `assets/` (`af8a523`); validator PASS (1439 entries); Godot import of the whole library without errors; import metadata committed.
- Slice A integrated (development use only, rights unchanged): 9 Helix component models, 19 environment/prop models, Helix texture sets, and 21 shared texture files the models reference. `AssetLibrary` + `ComponentVisual` (models follow physics bodies, damage-state nodes switch with component states, greybox fallback), set dressing from `data/environments/helix_01.json`, kit ledge for statics, graphite lighting with reflection sky and fog.
- Builds ship only integrated assets (`tools/assets/export_filter.py`): APK 74.5 MB (245 MB without the filter).
- Performance (emulator, Compatibility): draw calls ~120 → ~1,800 → ~600 after batching; worst breach frame 66 ms; restarts ~650 ms and 9-10 s first load still to optimise (slice E). Details and screenshots: `docs/asset-integration-report.md`, `docs/images/assets/`.
- Playable build: `build/temporal1-debug.apk` (local, from `4e2798a`; rebuild with `godot_console --headless --export-debug "Android Debug" build/temporal1-debug.apk` after `python tools/assets/export_filter.py --apply export_presets.cfg`). Runs on the emulator; **no physical device tested**.
- Tests: headless 193 passed / 0 failed / 1 skipped.
- Next: slice B (core damage progression, debris sets, damage overlays, VFX), C (HUD/typography/weapon presentation), D (Helix music, SFX, ambience), E (performance, lighting, polish).

## Batch 5 — approved changes and validation (2026-11-10, `81fefdc`..`503347c`)

Owner-approved: save v4, blast occlusion with material data, load-aware knockback, blast wall 90 px, core health ×3.0, collapse leaves the core critical and a Kinetic shot generally finishes it, economy direction (prices unchanged), audio data architecture. Not approved as final: the 40 px racks (comparison below).

| Area | State |
|---|---|
| Save schema v4 | `best_points` = successful runs only (leaderboard-eligible); `best_attempt_points` = any run; `attempts`/`completions` counters. v3 records migrate without loss; counters start at 0 with `counts_since_upgrade: true` (history not reconstructed) |
| Blast occlusion | On. Per-material `blast_transmission` in `data/materials.json`; statics and unknown materials pass 0.05; penetration and compounding unchanged |
| Load-aware knockback | On (`MissionWorld.load_aware_push`) |
| Core housing | New material `ai_core_module`: weapon resistances as electronics, `structural_resistance` 0.42 (falls/crushing). Materials gain optional `structural_resistance` (defaults to impact resistance) |
| Resting-contact fix | `ComponentBody` allows one gravity step of support: a resting released heavy body no longer reports an impact every frame (the blast wall did, 154 per frame, and the scene never settled) |
| Helix layout | Blast wall 30 × 90; core health ×3.0; racks 3-4 beside the right column (x 1030 / 1080), racks 1-2 at full 40 × 100 beyond the relay mast (x 1262 / 1304) |
| Outcome (sweep, 112 Breach trajectories + 10 kinetic angles) | 0 single-charge core kills; 35 collapses leave the core critical and a kinetic finish works (1.4 rounds); 0 collapses leave it unreachable; kinetic route clears on 7/10 angles in 3 rounds. Expert line: column Breach + one Kinetic round (2 shots) |
| Economy | Prices unchanged; chapter-scaled scheme B recorded as provisional direction in `tools/economy/economy_assumptions.json` |
| Audio architecture | `data/audio.json` + `AudioCatalog`; `AudioService` file variants with procedural fallback; material-aware impacts; `MusicDirector.play_cue`. No production audio files integrated yet |

**Server rack comparison** (`tools/regression/rack_comparison.gd`, `rack_capture.gd`; screenshots `docs/images/batch5/rack_*.webp`):

| Layout | Breach: collapse + kinetic finish | Kinetic route | Notes |
|---|---|---|---|
| 100 px racks in front (original) | 12 (2.1 rounds; rack 1 shot first) | 4/10 angles, 6-9 rounds | racks hide the fallen core from flat kinetic fire |
| 40 px racks in front (test variant) | 24 (1.3) | 7/10, 3 | proportions lost |
| 70 px racks in front | 16 (1.3) | 6/10, 3 | |
| 100 px racks in one bank behind the structure | 29 (1.4) | 7/10, 3 | one charge cleared all four racks and the relay mast |
| **Chosen: split bank** (3-4 beside the column, 1-2 beyond the mast) | same as one bank | 7/10, 3 | keeps proportions; a charge reaches only a pair |
| Static plinth under the deck | worse (core slid off) | | rejected |
| Weaker steel shield | no change (shield did not break) | | rejected; in real trajectories the shield never blocked a finish |

Numbers above were measured before the resting-contact fix except the final sweep row (0 / 35 / 0, 7/10).

**Renderer comparison on the real Helix scene** (`tools/renderer_eval/mission_benchmark.tscn`; logs and reports in `docs/benchmarks/2026-11-10-helix-mission/`, build `503347c`):

| | GL Compatibility | Mobile (Vulkan) |
|---|---|---|
| Emulator (x86_64, host GPU via translation), fps | 55-60 | 59-60 |
| Emulator worst frame, breach scenario | 38 ms (was 1113 ms on `9f773fd`, ~300 ms per blast on `9cfee96`) | 103 ms once (was 971 ms) |
| Emulator draw calls / video memory | ~120 / 35-37 MB | ~87 / 76-89 MB |
| Emulator viewport CPU render time | 2.0-3.7 ms | 0.56-0.63 ms |
| Mission restart (emulator) | 32-63 ms | 46-56 ms |
| Desktop (RTX 5060 Ti), fps / draw calls / VRAM / restart | 144 (vsync) / 116-132 / 15 MB / 7 ms | 144 / 86-96 / 66-68 MB / 18 ms |
| Visual (same frame, `docs/images/batch5/renderer_*`) | as authored; core white with red emission | linear HDR: core reads pink, cyan more saturated |

Hitch fixes: effects compiled at load; blast lights and flash meshes are persistent pools (creating them per detonation cost ~300 ms each on Compatibility). **Recommendation:** keep GL Compatibility as the production renderer (approved; lowest memory, no hitches now, colour as authored). Mobile remains the candidate if physical devices show lower CPU render cost matters; decide after physical-device runs. **Physical-device testing has not been done** (no USB device connected); emulator numbers are not representative of phone GPUs.

Tests: headless 185 passed / 0 failed / 1 skipped (`503347c`).

## Batch 5 pre-work review (2026-11-09, `33dd17f`..`1f417b5`) — superseded by the section above

Findings and proposals: `docs/batch5-review.md`. No gameplay or progression rule changed yet.
- **Committed (no rule change):** 5 accuracy tests; golden pure-scoring test; scripted cross-platform score replay (`tools/regression/score_replay.tscn`) plus a repeatability test; opt-in `blast_occlusion` and `load_aware_push` prototypes in `MissionWorld` (both **off**) with 6 tests; `tools/regression/tactics_probe.gd`; `tools/economy/simulate_research_data.py`; `make_eval_project.py --main`.
- **Key findings:**
  - Failed runs can raise `best_points`.
  - Blasts ignore shielding.
  - 28% of Breach trajectories one-shot the core, via collapse rather than direct damage.
  - The Kinetic Accelerator has no useful target from the operative position.
  - The 3752/3746 score gap came from different inputs; physics also differs slightly across platforms (0.4516 vs 0.4519 damage).
  - Flat upgrade prices make late weapons trivially affordable.
- Tests: headless 167 passed / 0 failed / 1 skipped.

## Batch 4 — mission scoring and progression (implemented 2026-11-09, `d6e5071`..`c469756`)

| Part | Files | Notes |
|---|---|---|
| Scoring formula | `data/scoring.json`, `scripts/core/mission_scoring.gd` | **Mission Points** = completion (per mission) + 500 per critical asset destroyed + up to 1000 for structural destruction + 300 per optional objective + up to 800 shot efficiency + up to 300 time efficiency + up to 400 accuracy (shots that damaged something). Shot credit is full at or under the mission's recommended shots and reaches 0 at 2×; time credit is full at or under the target time and never drops below 30% (floor at 3×). Time is ~6% of the maximum. Failure keeps destruction/critical/accuracy points but earns no completion, efficiency or Research Data. **Research Data** = mission completion + per optional objective + up to 15 efficiency (70% shots / 30% time) |
| Mission rewards | `data/missions/*.json` `rewards` | `completion_points`, `completion_research_data`, `optional_research_data` (defaults 1000 / 20 / 5) |
| Accuracy | `MissionEngine.effective_shots`, `MissionWorld` | A shot counts as effective when its hit or blast applied damage |
| Save schema v3 | `scripts/core/progress_data.gd` | Adds `missions` (completed, best points, best Research Data, best shots, best time, optional objectives done), `research` (balance, lifetime earned) and `upgrades` (weapon → attribute → level). v1 and v2 migrate in place; legacy level results, settings and story are kept. Invalid fields are dropped with warnings; balance above lifetime earnings is rejected |
| Anti-farming | `ProgressData.record_mission` | Research Data granted = improvement over this mission's previous best Research Data; bests only improve; failed runs never replace bests or grant optional credit |
| Upgrades | `data/weapons.json` `costs`, `scripts/core/upgrade_rules.gd` | Costs 30/60/100 Research Data per level (placeholder values); purchase/affordability rules; levels filtered against the catalog before reaching MissionEngine. No upgrade UI yet |
| Integration | `mission_screen.gd`, `mission_hud.gd`, `main.gd` | Missions start with the player's upgrades; results are scored, recorded and saved on finish; result panel shows Mission Points (with breakdown), Research Data gained and balance |

**Verification (2026-11-09, `c469756`):** headless 155 passed / 0 failed / 1 skipped; windowed 156 / 0 / 0. On the `Pixel10Pro` emulator a real **v1 save** (5 legacy level results from an earlier session) loaded without warnings and, after a mission won with one touch-aimed Breach lob, was rewritten as **v3** with the legacy results and settings intact plus `helix_01` (3746 points, 40 Research Data, balance 40).

**Open points:** upgrade UI and pricing balance; Standard vs. Competitive ranking conditions are not modelled yet (leaderboards are a later phase); the one-shot Breach-lob clear scores nearly maximum points, which makes the Helix layout balance (Batch 5) more pressing.

## Batch 3 — first playable Helix prototype (implemented 2026-11-09, `33cd669`..`1109b8a`)

**The app now boots straight into the Helix greybox mission (`helix_01`, Relay Node).** The legacy menu/levels are no longer shown (code kept for regression tests/reference).

| Part | Files | Notes |
|---|---|---|
| 2D physics world | `scripts/mission/mission_world.gd`, `component_body.gd`, `weapon_projectile.gd` | Components start frozen; released to physics on support loss, CRITICAL state or blast push, together with everything resting on them. Collision damage from impact jolts (gravity removed, so resting contacts deal none). Kinetic rounds deal speed-scaled direct damage; Breach Charges detonate on first contact (area damage to nearest edges + knockback). Secondary blasts (power cell) chain. Settle detection gates mission success |
| 3D presentation | `scripts/mission/view/mission_view.gd`, `view_mapping.gd`, `operative_rig.gd` | Godot 3D, tilted three-quarter `Camera3D` (FOV 40), directional light + shadows, greybox facility backdrop. Each component = its physics rectangle extruded in depth (front face = collision shape). Damage tint per state; red floating marker + white/red housing identify the AI core; projectile meshes; blast flash + light, sparks, debris. Touch picking via camera ray onto the z = 0 physics plane |
| Operative | `operative_rig.gd` | Placeholder primitives, anonymous helmet/visor. States: idle, ready, aim (arm tracks aim), fire recoil, reload (weapon lowered during cooldown), victory, defeat. Visible weapon swap (rail vs. launcher) |
| Screen, input, HUD | `scripts/mission/mission_screen.gd`, `mission_hud.gd`, `scripts/main.gd` | Touch-and-hold to aim at a point (not pull-back), release to fire, release near the operative to cancel; Breach power = finger distance. Weapon buttons with ammo + reload bar, objectives with progress, shots vs. recommended, time vs. target, pause, restart, result panel. Android back pauses; app backgrounding pauses |
| Tooling | `tools/capture_mission.gd` | Writes 9 review screenshots to `tests/output/mission/` |

**Helix layout tuning (measured with a physics probe, then locked into tests):** blast wall and racks moved left so a rack-cluster Breach no longer topples the deck; a reinforced-steel `core_shield` in front of the core blocks direct kinetic sniping; recommended shots 6 → 4. Verified tactics: 2 precise kinetic hits on the left column collapse the deck and destroy the core; a Breach lobbed over the shield destroys the core; a Breach on the rack cluster clears two racks without reaching the core; destroying the power cell chains damage into the core.

**Verification (2026-11-09, `1109b8a`):** headless 138 passed / 0 failed / 1 skipped; windowed 139 / 0 / 0. Android debug APK (60.4 MB) installed on the `Pixel10Pro` emulator (2856×1280): boots into the mission on Compatibility/OpenGL ES 3.1 without log errors; `adb input swipe` touch aiming fired the Kinetic Accelerator, a tap switched to Breach, a swipe threw a charge that destroyed one rack and left the next critical.

**Known issues / not yet done:**
- Not tested on a physical device; no frame-time data for the 3D scene yet. The renderer benchmark still uses the old 2D proxies: re-run Compatibility vs Mobile with this 3D scene and a larger facility (Batch 5).
- Aim picking uses the z = 0 physics plane, while visible front faces sit half a component depth in front of it, so touching the visible top edge of a piece can aim slightly off; kinetic rounds also drop a little (gravity × 0.25). The preview shows the true path. Candidate fix: snap/assist toward the touched component (Batch 5 or the targeting-assistance upgrade).
- Balance is first-pass: the mission can be won in 1-2 well-placed shots against a recommended 4. Needs hands-on play-testing.
- Operative and weapons are placeholders with procedural animation only.

## Production pipeline alignment (owner, 2026-11-09)

Option B is the planned architecture: Godot 3D rendering + tilted three-quarter camera over the existing 2D physics, with a placeholder 3D operative (Batch 3). Gameplay objects are 3D modular geometry with textures (no per-object PNG sprites); 2D art is for textures, decals, damage variants, VFX, UI and narrated-still cinematics (no video dependency). The first asset milestone is concepts, material references, textures and specs; bulk asset production waits for the validated Batch 3 greybox. See `plan.md` §9b and the guide's “3D-ready production pipeline”.

## Batch 2 — mission architecture (implemented 2026-11-09, `db82117`..`d7a3738`)

| System | Files | Status |
|---|---|---|
| MissionDefinition | `scripts/core/mission_definition.gd`, `data/missions/helix_01.json` | Implemented. Facility statics + damageable components (material, geometry, health scale, critical-asset flag, supports), operative position, weapon allowances, recommended shots, target time, objectives. Cross-validated against materials, weapons, structure graph and objective targets; every critical asset must have a destroy_critical objective; at least one mandatory goal |
| WeaponState | `scripts/core/weapon_state.gd` | Implemented. Per-mission ammunition (mission allowance + capacity upgrades), reload cooldown, shots fired; direct = fixed speed, lobbed = power maps to the speed range |
| MissionObjectives | `scripts/core/mission_objectives.gd` | Implemented. Goals: destroy_critical, destroy_components (N of M), structural_damage (fraction). Constraints: protect, max_shots, within_time. Mandatory/optional, progress, finalize |
| MissionEngine | `scripts/core/mission_engine.gd` | Implemented. Weapon selection and firing with independent cooldowns; damage routing; structural releases and secondary-blast requests as signals; critical-asset state signal; continuous evaluation; success = mandatory goals complete + scene settled; failure = broken mandatory constraint, or no ammunition once settled. No shot cap |

The Helix greybox layout (`helix_01`) is data-valid but not yet physics-verified; that happens in Batch 3 with the playable scene.

Last verified (2026-11-09, `d7a3738`): headless 125 passed / 0 failed / 1 skipped; windowed 126 / 0 / 0; Android debug export includes `data/missions/helix_01.json`.

## Batch 1 — tactical foundation (implemented 2026-11-09, `99dbd6c`..`1c844e0`)

Node-free core systems under `scripts/core/`, each with its own test suite. Nothing in the running game uses them yet; Batch 2 (mission architecture) and Batch 3 (Helix prototype) wire them in.

| System | Files | Status |
|---|---|---|
| MaterialCatalog | `data/materials.json`, `material_catalog.gd` | Implemented. 7 materials (lightweight_alloy, reinforced_steel, composite, glass_polymer, concrete, electronic_module, energy_component): density, friction, bounce, health, impact/blast resistance, per-hit minimum, optional secondary blast. Untuned starting values |
| WeaponCatalog + upgrade layer | `data/weapons.json`, `weapon_catalog.gd` | Implemented. Kinetic Accelerator (direct, fixed 1700 px/s, gravity ×0.25, 90 impact) and Breach Charge (lobbed, 350-950 px/s, blast 160 dmg / 140 px / 900 impulse, 3 charges). `effective_stats(levels)` applies base + 3 upgrade levels from data |
| DamageRules | `damage_rules.gd` | Implemented. Speed-scaled projectile damage, collision damage above an impulse floor, resistance with penetration and per-hit minimum, linear blast falloff, radial knockback, distance to rotated boxes |
| DamageableComponent | `damageable_component.gd` | Implemented. Health with INTACT → DAMAGED (<75%) → CRITICAL/unstable (<35%) → DESTROYED; signals; critical-asset flag; secondary blast on destruction |
| StructuralDependencySystem | `structural_dependency_system.gd` | Implemented. Explicit "rests on" graph, all-or-minimum support rules, deterministic cascades, validation (unknown, self, duplicate, range, cycles) |
| MissionEngine | see Batch 2 below | Implemented |

Legacy note: the old `GameSession`/levels are untouched and still run (legacy, reference only).
Music: `assets/audio/music/gameplay_bed.ogg` plays from startup (owner instruction); the sound toggle mutes it; licence evidence is a release blocker (`docs/asset-manifest.md`).

Last verified (2026-11-09, `1c844e0`): headless `godot_console --headless --fixed-fps 60 -s tests/run_tests.gd` → 104 passed, 0 failed, 1 skipped; windowed `godot_console --resolution 1280x720 --fixed-fps 60 -s tests/run_tests.gd` → 105 passed, 0 failed; `--export-debug "Android Debug"` → APK built (60.3 MB).

## Owner clarifications to revision 5 (2026-11-09)

- **The old gameplay is retired.** Slingshot pull-back aiming, generic blocks and targets, the single projectile, the five-shot cap, all-or-nothing destruction and stars-only scoring are not part of Temporal: First Jump. The existing 20 levels are **legacy**: kept temporarily for regression and reference only, never maintained as a parallel campaign, never made compatible with new systems and never the primary menu. Remove them later only after checking references.
- **Preserved technology:** physics simulation, data-driven loading, save/migration infrastructure, services, audio, the test runner and tests, useful solver utilities, the renderer benchmark, and reusable UI/platform code.
- **The Helix Systems prototype becomes the first playable experience.**
- **Responsibility split:** MaterialCatalog (load/validate materials), WeaponCatalog (load/validate weapons and upgrade data), DamageRules (impact, blast, falloff, impulse maths), DamageableComponent (health, damage states, destruction), StructuralDependencySystem (supports, connections, instability cascades), MissionEngine (objectives, ammunition, weapon state, completion). No combined controller. Material behaviour is data; visuals are separate from physics.
- **Progressive damage:** intact → damaged → critical/unstable → destroyed, with direct and blast damage, distance falloff, knockback, material resistance, dependencies, secondary effects and a separate critical-asset objective state. Deterministic calculations where practical; explicit structural relationships rather than a full structural solver.
- **Upgrades:** base + 3 levels per attribute, defined in data, applied through one effective-stats layer. No upgrade UI or economy in Batch 1. Mission Points (performance/rankings) and Research Data (upgrades) stay separate.
- **2.5D:** angled three-quarter presentation (3D-rendered view) over the existing 2D physics. No 3D physics.
- **No universal shot cap** in the new mission system. Missions define recommended shot budget, target time, critical assets, mandatory/optional objectives, weapon availability, ammunition, Mission Points and Research Data rules.
- **Approved batch sequence:** (1) foundation: materials, weapons, damage, damageable component, structural dependencies, tests; (2) mission architecture: mission data, objectives, critical asset state, weapon state, ammunition/cooldown, continuous evaluation, no five-shot dependency; (3) first playable Helix prototype; (4) Mission Points, Research Data, rewards, upgrade calculation, save v3 migration (no save resets); (5) polish and validation: tuning, balance, animation, audio, mobile performance, emulator and physical-device testing. Each batch is reported before the next starts.
- **Renderer:** repeat the Compatibility vs Mobile evaluation with representative 2.5D content and large-facility physics workloads before any decision. Watch body counts from the start.
- **Background music:** the owner instructed (2026-11-09) that the shared track (`assets/music/bg.mp3`) be used as the background music. Integrated as a trimmed Ogg loop. **Licence evidence (Suno plan/terms at generation time) is still outstanding and is a release blocker.**
- Frontlines stays later-phase: structured, versioned component data, no backend/accounts/networking now.

## Greybox design decisions (owner, 2026-11-09)

- **2.5D rendering:** a 3D presentation layer over the existing 2D physics. Each 2D body drives a simple 3D mesh seen through a tilted perspective camera with lighting and shadows; the operative is a 3D greybox. All collision stays in the single 2D physics plane, so depth is visual only. The renderer benchmark must be re-run with 3D content before any renderer decision.
- **Fire flow:** weapons fire again after a reload cooldown, even while debris is moving. Objectives are evaluated continuously. A mission ends when its critical objectives are met, or when ammunition is exhausted and the scene has settled.
- **Ammunition:** each mission defines a recommended shot benchmark (scoring) and a higher hard ammunition cap (fail state), with a separate small Breach Charge count.
- **Cinematic player:** the untested pre-revision draft was deleted. Cinematics will be rebuilt from `data/cinematics.json` in Phase 4.
- Greybox batch plan: `docs/project-audit.md` (Phase 0/1 re-audit section).

## Updated next actions

1. Audit existing physics, aiming, projectile, object, level and save architecture against the revised direction.
2. Build the angled 2.5D Helix greybox with visible operative, two weapons, distinct structures and AI core.
3. Validate the prototype on representative mobile hardware before bulk art or level conversion.
4. Design the data-driven weapon and material/component definitions from the verified existing architecture.
5. Implement Mission Points, Research Data and upgrade economy only after prototype mechanics are stable.
6. Update level concepts and shot budgets to support multi-stage destruction.
7. Keep leaderboards and Frontlines in the architecture roadmap, but defer backend implementation until the single-player foundation is stable.

No implementation, test, backend selection or multiplayer validation is claimed by this update.
