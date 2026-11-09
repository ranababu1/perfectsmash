# Current State

_Last updated: 2026-11-09 · Version 0.1.0 (unreleased) · Branch `main` · Remote `origin` (github.com/ranababu1/temporal-chapter1)_

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
