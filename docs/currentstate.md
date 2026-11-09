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
| Continuous gameplay music | In production / pending review | AI music task completed; first-pass candidate is available via the generation service. Not yet listened to, approved, loop-tested, license-verified or integrated |
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
- Proposed future modules: `CinematicPlayer`, `CinematicDefinition`, `CinematicCatalog`, `StoryProgressService`, `MusicDirector`, `StoryArchiveScreen`. Names are conceptual; coding agent must inspect project conventions before implementation.

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

1. Run the Compatibility-vs-Mobile renderer evaluation on representative physical Android and iOS devices; record Vulkan/Metal support, frame pacing, thermal behavior, memory, battery observations and visual compatibility. Obtain approval before changing production renderer or minimum OS/device support.\n2. Produce a Temporal: First Jump app icon (current icon art is still the Perfect Smash ball-and-core design).
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
