# Temporal: First Jump: Product and Engineering Plan

**Document status:** Owner-approved revision 4 (2026-11-09). The original product/engineering baseline is preserved in Git history (commit `e26dd91`); revision history is retained below.  
**Product name:** Temporal: First Jump (owner-approved 2026-11-09)  
**Application ID / bundle ID:** `dev.imrn.temporal1` (Android and iOS)  
**Repository:** github.com/ranababu1/temporal-chapter1, branch `main`  
**Product type:** Story-driven 2D physics destruction puzzle  
**Target platforms:** Android + iOS  
**Engine:** Godot 4.7.2 + GDScript + built-in 2D physics  
**Proposed production renderer:** Godot Mobile (pending Compatibility-vs-Mobile evaluation)  
**Graphics backends:** Vulkan on supported Android devices; Metal on supported Apple devices  
**Primary quality priority:** Mobile performance, frame pacing and battery efficiency  
**Initial content target:** 100 levels across five chapters

## Revision history

- **Rev 4 (2026-11-09, owner-approved via the project execution brief):** Product renamed from "Perfect Smash" to **Temporal: First Jump**; Android application ID and iOS bundle identifier set to `dev.imrn.temporal1`. The new ID is treated as a new store identity: it cannot update any listing created under `dev.imrn.perfectsmash` (none is recorded). Existing signing keys are preserved and kept out of Git. No release or store submission is authorized. Body text referring to "Perfect Smash" below is historical. No other plan content changed.
- **Rev 3 (2026-11-09, owner-approved):** Expanded target platforms from Android to Android + iOS; confirmed mobile performance and battery efficiency as the primary quality priorities; selected Godot 4.7.2 as the engine; and designated the Godot Mobile renderer as the proposed production renderer, subject to a documented Compatibility-vs-Mobile evaluation on representative physical Android and iOS devices. Vulkan is the intended Android backend and Metal the intended Apple backend where supported. Added renderer validation, device compatibility, and iOS/Xcode release requirements. No renderer switch or minimum OS/device support change is authorized until evaluation evidence is reviewed.
- **Rev 2 (2026-11-09, owner-approved):** Reframed the game as a time-travel science-fiction destruction puzzle. Added a skippable opening cinematic, narrated chapter introductions and endings, a five-chapter/100-level narrative plan, a cliffhanger at level 100, a reusable cinematic/content pipeline, and a visual/audio production direction. Core physics puzzle gameplay remains the foundation. Added companion documents: `docs/narrative-bible.md` and `docs/visual-audio-production-guide.md`.
- **Rev 1 (2026-11-01, owner-approved):** Product renamed from "Smash Theory" to "Perfect Smash". No other content changed in that revision.
- The original baseline text is preserved in Git history (commit `e26dd91`).

## 1. Product vision and target audience

The game is a short-session, story-driven physics destruction puzzle. The player is an operative sent from a doomed future into the past to destroy critical infrastructure and research installations that enabled a chain of decisions leading to humanity's extinction.

The player studies a structure, chooses a launch angle and power, and uses a limited number of temporal charges to trigger a satisfying collapse or complete a clear objective. The story gives each target meaning, while the puzzle remains the main interaction.

**Product promise:** "One shot can change everything."

Primary audience:
- Casual players who enjoy physics toys and satisfying destruction.
- Puzzle players who like limited actions, clever solutions and cause-and-effect.
- Players attracted to short sessions, sci-fi mystery and episodic progression.

The story must be understandable without requiring players to watch every cinematic. All cinematics are skippable and replayable from a Story Archive.

## 2. Narrative premise and canon

### 2.1 The premise

In 2149, humanity is approaching extinction. The catastrophe was not caused by one war or one invention. It emerged from several technologies and institutions that became dangerously interconnected: autonomous intelligence, biological engineering, energy extraction and predictive control.

The surviving population discovers a way to send one operative into the past. The operative is equipped with a compact temporal impact device. The mission is to destroy specific facilities and critical prototypes before their research paths converge.

The operative's sponsor and the full origin of the time-travel signal remain unidentified during the first release. The player receives instructions from an anonymous control channel. This mystery is intentional.

### 2.2 First-release timeline

- **2149:** The future is collapsing. The Continuity mission is initiated.
- **2089:** The operative's first intervention begins at Helix Systems.
- **2092:** Bioengineering research is targeted at VITA Genomics.
- **2096:** The Nova Grid energy programme is targeted.
- **2100:** The Civitas predictive-governance network is targeted.
- **2104:** The Meridian convergence facility is discovered and destroyed.
- **After level 100:** The revised timeline still contains an extinction event. Its origin traces to an earlier event in **2041**. The next season travels further into the past.

Dates are narrative anchors, not a requirement to show exact calendar dates in every level.

### 2.3 Five chapters

| Chapter | Levels | Era / location | Primary target | Narrative discovery |
|---|---:|---|---|---|
| I. The Machine That Decided | 1-20 | 2089, Helix Systems | Autonomous civic intelligence | A system designed to reduce human suffering begins treating human choice as instability. |
| II. The Price of Perfection | 21-40 | 2092, VITA Genomics | Human enhancement and bioengineering | A programme meant to eliminate disease creates a dependency humanity cannot reverse. |
| III. The Energy Beneath | 41-60 | 2096, Nova Grid | Revolutionary energy infrastructure | The energy source carries a repeating signal that predates the facility. |
| IV. The Quiet Cage | 61-80 | 2100, Civitas | Predictive governance and behavioural systems | Different institutions are following the same hidden predictions. |
| V. The Convergence | 81-100 | 2104, Meridian | The network connecting all four programmes | The player destroys the visible cause, but the extinction event survives. Its first trace is in 2041. |

The chapter concepts are fictional. Do not depict real companies, real institutions or real people as responsible for the fictional catastrophe.

### 2.4 Story rules

- The player is an operative, not a superhero. Keep the character mostly unseen and without a fixed face or gender.
- The anonymous Control voice is calm, precise and increasingly uncertain. Do not reveal who or what it is in release one.
- The temporal charge is the consistent in-world explanation for the projectile. It should remain visually recognisable across chapters.
- The player destroys key infrastructure, not entire cities or populations. Targets should be understandable, fictional and non-graphic.
- The story must not claim that real-world scientific disciplines are inherently evil. The antagonist is unchecked power, bad incentives, secrecy and systems that remove accountability.
- Do not make the AI a cartoon villain. The frightening part is a reasonable objective taken to an inhuman extreme.
- Every chapter should reveal one answer and raise a larger question.
- Level 100 is a genuine cliffhanger, not a fake-out that invalidates the player's effort. The player saves one version of the future, but discovers the underlying cause remains.

## 3. Core gameplay loop and mechanics

The existing gameplay loop remains:
1. Show a structure, objective and available action budget.
2. Player aims and launches the temporal charge using the existing drag-back input.
3. Built-in 2D physics simulates collision, momentum, gravity and structural response.
4. The level waits for simulation settling or reaches the existing bounded timeout.
5. Objective evaluation determines success or failure.
6. Award score/stars based on the existing rules.
7. Offer retry or next level.

**No narrative feature may require changing physics rules or introducing a new weapon class.** A temporal charge is a visual and narrative wrapper for the existing projectile. It may receive new art, trail, impact VFX and sound, but its physics and tuning must remain unchanged unless separately approved and tested.

## 4. First-release content scope

### Included
- 100 curated levels, grouped into five chapters of 20.
- Five chapter-specific gameplay environments and visual themes.
- One skippable opening cinematic, five chapter introductions and five chapter endings.
- Narrated still-image / parallax cinematics with subtitles and music.
- Reusable cinematic player and data-driven cinematic definitions.
- A Story Archive / replay entry point for unlocked cinematics.
- Chapter-level narrative milestones and a final level-100 cliffhanger.
- A persistent, seamless or cross-faded gameplay background-music bed, with audio settings respected.
- New projectile, target, block and environmental art consistent with the chapter.
- Offline-first play. Cinematic media must be bundled locally; no streaming dependency.

### Explicitly excluded from this release
- Branching story choices or multiple endings.
- Dialogue trees, voiced NPCs or a large cast of visible characters.
- Real-time rendered 3D cutscenes.
- New physics mechanics, projectile classes or material simulation.
- Multiplayer, PvP, accounts, cloud saves or a backend.
- Procedural generation of shipped puzzle layouts.
- User-generated levels or level editor.
- Monetization changes tied to story progression.

## 5. Level progression and difficulty

Each chapter contains four five-level teaching groups:
1. Establish the environment and introduce the chapter's target language.
2. Combine two previously introduced structural ideas.
3. Increase structural complexity and chain-reaction reasoning.
4. Deliver a multi-step challenge and a chapter finale at levels 20, 40, 60, 80 and 100.

Difficulty should be authored from puzzle reasoning, not merely from solver win rate. Continue using the existing solver as a robustness signal, not as a substitute for human play-testing.

### Level acceptance
- Every level is solvable within its stated action budget.
- The objective is visually and textually clear.
- The structure and target art communicate the objective without excessive UI explanation.
- Failure is understandable and retry restores the exact initial layout.
- Physics settling does not declare a win while objects are still moving.
- No softlock or unbounded body count.
- Test on different frame rates, aspect ratios and Android device classes.
- The narrative wrapper must not obscure aiming, projectile trajectory, destructible objects or objective targets.

The detailed 100-level mission map is in `docs/narrative-bible.md`.

## 6. Technical architecture and content pipeline

### Existing architecture

Retain the established separation:
- `scripts/core/`: gameplay rules and data validation.
- `scripts/game/`: physics session, level loading, bodies, aiming and effects.
- `scripts/services/`: persistence and audio.
- `scripts/ui/`: menu, HUD, pause, results and navigation.
- `data/levels.json`: level definitions.
- `tests/` and `tools/`: automated validation and level-solving tools.

### New recommended modules (planned, not implemented)

- `CinematicPlayer`: one reusable scene/controller for all narrated sequences.
- `CinematicDefinition`: validated data model for slides, timing, voiceover, subtitles, image references, transitions and optional motion.
- `CinematicCatalog`: loads opening and chapter sequences by stable IDs.
- `StoryProgressService`: records unlocked/watched story sequences, using the existing safe save approach.
- `MusicDirector`: selects and cross-fades the menu, chapter and cinematic music beds while respecting mute/volume settings.
- `StoryArchiveScreen`: replay unlocked cinematics without affecting level progression.

These modules must not own or alter gameplay physics. Keep cinematic definitions in data/resources rather than hard-coding story text into scene scripts.

### Cinematic playback requirements
- 16:9 landscape composition, designed for the existing landscape game.
- Skippable from the first frame with a clear, comfortable touch target.
- Subtitles always available; narration and music can be independently muted.
- Continue automatically after the last slide, with a short transition to gameplay.
- Skipping must not skip or corrupt level unlocks, stars or save state.
- A sequence can be replayed from the Story Archive after it is unlocked.
- Resume/interrupt behavior must be deliberate if the app is backgrounded.
- Images and audio are compressed and packaged locally. No remote media request during gameplay.
- Use a single consistent narrator identity. Control transmissions may use a lightly processed secondary voice, but avoid an expensive cast.

### Data-driven sequence shape (conceptual)

A cinematic sequence contains:
- Stable ID, chapter ID and sequence type (opening / chapter intro / chapter outro / finale).
- Ordered slides.
- Per slide: image resource, voiceover audio resource, subtitle text, minimum duration, transition and optional camera movement.
- Sequence-level music cue and end action.

The coding agent must inspect the actual Godot project before choosing final resource paths or script names. Do not implement this conceptual schema blindly.


### Renderer and mobile platform architecture

**Owner-approved targets and priorities (2026-11-09)**
- Platforms: Android + iOS.
- Primary quality priority: mobile performance, stable frame pacing, thermal behavior and battery efficiency.
- Engine: Godot 4.7.2, GDScript and built-in 2D physics.
- Proposed production renderer: Godot Mobile.
- Intended graphics backend: Vulkan on supported Android devices; Metal on supported Apple devices.
- Existing project renderer: Compatibility. It remains the known-good baseline until the evaluation below is completed.

**Renderer decision gate (must happen before bulk level production)**
1. Preserve the existing Compatibility configuration and establish a reproducible baseline.
2. Create an isolated Mobile-renderer test configuration or test branch without overwriting user work.
3. Test representative gameplay scenes: ordinary level, the most demanding destruction/collision level, UI/menu, chapter background/parallax, particles/shaders and a cinematic sequence.
4. Run the same test scenarios on representative physical Android and iOS devices. Record exact device, OS, GPU, Godot version, renderer and backend.
5. Compare frame pacing (including frame-time spikes), sustained performance, thermal behavior, memory use, battery observations, visual output, shader/material compatibility and startup/loading.
6. Verify actual Vulkan/Metal capability on each test device. Do not infer Vulkan support from Android API level or Metal feature support from device age alone.
7. Document failures, fallbacks and device exclusions. Recommend Mobile as production only if the results meet the mobile quality goals without unacceptable compatibility regressions.
8. Do not change minimum supported Android/iOS versions, production renderer settings or export presets until the owner reviews the evidence and approves the change.

**Rendering principles**
- Prefer baked/static artwork, restrained 2D lighting, layered backgrounds and efficient sprite effects over expensive real-time full-screen effects.
- Use conservative particle counts, overdraw and transparent full-screen layers.
- Keep shaders simple and provide a tested fallback for optional visual effects where necessary.
- Rendering backend changes must not alter physics, collision tuning, level outcomes, scoring or save data.
- Compatibility may remain a fallback build/configuration if the device matrix demonstrates a real need and the maintenance cost is acceptable.

**Initial performance goals (targets, not measured claims)**
- Target 60 FPS with consistent frame pacing on the agreed device matrix; do not treat this as a guarantee for every device.
- Keep the 16.67 ms frame budget as the 60 FPS reference.
- Avoid sustained thermal throttling during representative play sessions.
- Measure memory, loading and battery behavior on physical devices; do not infer them from editor or emulator results alone.

**Platform and release constraints**
- Android builds must validate actual GPU/backend compatibility, touch behavior, lifecycle and thermal performance.
- iOS rendering uses Metal where supported. Godot iOS export must be opened, built and signed with Xcode on macOS.
- Windows development can prepare the project and export an iOS project, but cannot replace final Xcode build, signing, TestFlight and App Store validation.
- Android and iOS should share gameplay/content code. Platform-specific export, signing, permissions and backend settings remain separate and documented.

## 7. UI/UX and visual direction

### Gameplay
- Preserve high-contrast, readable structures and targets.
- Replace the generic ball with a compact, recognisable temporal charge.
- Replace generic scenery with chapter-specific fictional facilities.
- Keep destructible objects legible against the background. Foreground structures must have stronger contrast and sharper edges than scenery.
- Use controlled impact effects. No full-screen flashes that hide the puzzle.
- Preserve objective and remaining-action visibility.
- Maintain the current landscape orientation and validate common phone aspect ratios and safe areas.

### Cinematic art direction
- Grounded, cinematic science fiction rather than neon cyberpunk.
- Dark charcoal, cold steel, muted blue/cyan temporal energy, restrained amber warning accents.
- Architectural scale, environmental storytelling, believable industrial design.
- 16:9 wide frames with clear subject placement and negative space for subtitles.
- No text, UI, logos, watermarks or fake readable signage baked into generated artwork.
- Generate clean plates. Add all titles, dates, subtitles and HUD graphics in Godot.
- Keep the operative as a silhouette or partial figure. Avoid a fixed face to preserve player projection.
- Avoid purple/pink gradients, excessive bloom, random floating glyphs and generic AI-art visual noise.

See `docs/visual-audio-production-guide.md` for prompt templates, image inventory and audio guidance.

## 8. Audio and music direction

- Continuous gameplay music should be restrained dark sci-fi ambient: slow evolving synth pads, low drones, subtle rhythmic pulses and sparse mechanical texture.
- Music must support long puzzle sessions and must not compete with impact SFX or narration.
- Use one main gameplay bed with seamless looping/cross-fade, plus optional chapter variations that share a common motif.
- Cinematics can use a separate restrained score with a beginning and end.
- Narration must remain intelligible on phone speakers. Duck music under voiceover.
- All audio must have documented commercial-game rights. Keep the original license file and source URL in the asset pack and project credits where required.
- Do not use a track just because it is described as "no copyright". Verify the exact asset license, attribution, redistribution and Content ID terms before release.
- A commissioned or generated original score is preferred for long-term identity, provided the generation service's commercial-use terms are checked and retained.

Initial research candidates are listed in the audio guide. They are candidates only, not approved or integrated game assets.

## 9. AI-assisted development and asset production

- Use AI to produce consistent environment concept art, cinematic frames, object concepts and music prototypes.
- Generate chapter art from a locked style reference and chapter-specific prompt templates.
- Generate separate foreground/gameplay assets with transparent backgrounds when needed; cinematic background images are not substitutes for clean gameplay sprites.
- Review every generated asset for consistency, unwanted text, artefacts, visual clarity and commercial-use rights.
- Keep source prompts, output IDs/files, license evidence and intended use in the asset manifest.
- Do not create 100 unique full-screen backgrounds. Use five chapter environment families, reusable props and a small number of cinematic keyframes.
- Never ship an image with accidental text, logos, watermarks or legible brand marks.

## 10. Monetization, analytics and retention

The narrative direction does not change the existing monetization decision: do not monetize until core level completion and retention are validated.

Potential future options remain optional rewarded attempts, one-time ad removal and cosmetic themes. No forced ad may interrupt a cinematic, a collapse or an immediate retry.

Keep analytics minimal and privacy-reviewed. Useful measurements include:
- Cinematic started / completed / skipped.
- Chapter intro completion and chapter-finale reach.
- Level started / completed / failed / retried.
- Session length and levels per session.
- Crash, ANR and simulation timeout.

Do not treat a cinematic skip as a negative engagement event by itself. Track it to understand player preference, not to punish skipping.

## 11. Development milestones and acceptance criteria

### M0-M4: Existing core
Preserve the existing physics, rules, save and UI acceptance criteria. Re-verify before adding content.

### M5: Renderer evaluation and mobile platform foundation
- Preserve and benchmark the existing Compatibility renderer.
- Create and benchmark an isolated Mobile-renderer configuration.
- Validate Vulkan on representative Android hardware and Metal on representative iOS hardware.
- Compare frame pacing, sustained performance, thermal behavior, memory, battery observations and visual compatibility.
- Document device matrix, results, limitations and recommendation; obtain owner approval before changing production renderer or minimum OS/device support.
- Verify the Godot-to-Xcode iOS export workflow on macOS if available; otherwise record it as pending and do not claim iOS build validation.

### M6: Narrative and visual vertical slice
- Approve final game name separately.
- Lock one visual style reference and temporal-charge design.
- Produce and review opening cinematic frames.
- Implement a small cinematic prototype with skip, subtitles, voiceover, music ducking and replay.
- Reskin one existing level in each of the five chapter environments before bulk production.
- Validate gameplay readability on physical Android and iOS devices where available; record any platform validation still pending.

### M7: 100-level content build
- Author 100 levels in five 20-level chapters.
- Reuse current 20 level definitions where suitable; retain stable IDs or implement an explicit, tested migration if IDs change.
- Verify every new or modified level with solver tooling and human play-testing.
- Add chapter intros/outros and level-100 ending.
- Verify asset sizes, loading, memory, Android export and iOS/Xcode export workflow.

### M8: Audio and cinematic integration
- Record/generate final narration.
- Integrate the approved continuous gameplay music bed and cinematic cues.
- Confirm all licenses and credits.
- Test mute, volume, pause, backgrounding, skip and replay.

### M9: Closed testing and release candidate
- Test all 100 levels end-to-end on representative physical Android and iOS devices.
- Verify clean install, upgrade path, save integrity, level unlocks and cinematic archive.
- Check crashes/ANRs, memory, frame pacing, loading, audio loops and touch targets.
- Prepare store assets, privacy disclosures, release notes and signing.
- Obtain explicit release approval before production rollout.

## 12. Risks, assumptions and validation

Risks:
- Story slides may slow players who only want puzzles. Mitigation: skippable, short, replayable.
- Background art may reduce gameplay readability. Mitigation: separate art layers and contrast tests.
- Generated art may drift between chapters. Mitigation: locked style reference and asset review.
- Long music loops may fatigue players. Mitigation: restrained arrangement, seamless cross-fades and chapter variants.
- The 100-level target may dilute puzzle quality. Mitigation: chapter-level play-test gates; do not ship filler levels.
- The level-100 cliffhanger may frustrate players if the first release feels incomplete. Mitigation: make the first 100 levels a complete intervention arc with a meaningful apparent victory before revealing the deeper cause.

Assumptions:
- The existing physics puzzle remains enjoyable with a narrative wrapper.
- Players accept brief narrated story sequences between chapters.
- A consistent visual identity and satisfying destruction are more important than elaborate cutscenes.

## 13. Expansion strategy

- **Release 1:** 100 levels, five chapters, ends with the discovery that the first extinction trigger originated in 2041.
- **Update 1:** +50 levels, Season 2 / "The First Mistake", travelling further into the past to investigate the 2041 event.
- **Future updates:** Add 25-50 level story arcs as production capacity allows. Each arc must have its own local objective, chapter reveal and forward hook.
- Do not make the story dependent on an exact number of future updates. Keep the mystery expandable and avoid revealing the ultimate cause until the narrative has earned it.

## 14. Android / Google Play release strategy

- Check current Play Console target API and policy requirements at release time.
- Use internal testing, then closed testing before production.
- Prepare icon, screenshots, feature graphic, store copy, privacy policy, Data safety answers, content rating, ads declaration, support details and credits.
- Confirm all generated and third-party art/audio are licensed for commercial distribution.
- Test app lifecycle, physics behavior, clean install, upgrade, save persistence and all 100 levels on physical Android devices.
- Use an Android App Bundle unless current Play guidance says otherwise.
- Keep signing material out of Git; use Play App Signing where appropriate.
- Roll out gradually if available and monitor crashes/ANRs, level failures, timeouts, conversion, tutorial completion and retention.
- Obtain explicit owner approval before production release.


## 15. iOS / App Store release strategy

- Generate the iOS export from the approved Godot project and open it in Xcode on macOS.
- Verify the selected renderer and Metal backend on representative physical iPhones/iPads in the supported device matrix.
- Configure bundle identifier, signing team, provisioning profiles, capabilities and entitlements deliberately; keep certificates, private keys and provisioning secrets out of Git.
- Validate app lifecycle, audio interruption, safe areas, touch targets, landscape behavior, save persistence, thermal behavior, memory and performance on physical devices.
- Use TestFlight for internal and external beta validation before App Store submission.
- Prepare App Store screenshots, description, age rating, privacy disclosures, support details and required metadata.
- Verify the current App Store review requirements and privacy declarations at release time.
- Test clean install and upgrade behavior, including persistence of existing local progress where applicable.
- A successful Godot export is not proof of a successful Xcode build, signing, TestFlight upload or App Store approval.
- Obtain explicit owner approval before production release.


---

# Owner-approved product revision 5: Tactical destruction, progression and Frontlines

**Approved:** 2026-11-09. This revision supersedes conflicting gameplay, scope and exclusion statements in earlier sections of this document. Earlier text remains in Git history as the prior product baseline.

## 1. Revised product identity

Temporal: First Jump is an **angled 2.5D tactical destruction puzzle** with a visible operative, multiple evolving weapons, story-specific destructible institutions, a hybrid upgrade economy and an optional asynchronous competitive mode.

It is not a slingshot/Angry Birds-style game with a science-fiction reskin.

**Core promise:** Every structure has a weakness. Every weapon has a purpose. Every shot should feel deliberate.

The selected presentation is an angled 2.5D / three-quarter view. The initial technical approach is to retain Godot's existing 2D physics and construct depth through art, layers, perspective-aware composition and controlled transforms. Do not migrate to full 3D physics unless a validated prototype demonstrates that genuine depth-dependent collision is essential and the owner approves the cost and risk.

The operative is visible at the firing position, anonymous, without a fixed face or gender. Character and suit presentation may evolve with chapter technology. Keep the first animation scope small: idle, ready, aim, charge where applicable, fire/recoil, reload/cooldown, and basic mission reactions.

## 2. Revised core gameplay loop

1. Introduce the mission, target institution and objectives.
2. Let the player inspect the structure and identify critical assets and weaknesses.
3. Select an unlocked weapon and review ammunition/energy constraints.
4. Aim using mobile-friendly touch controls and clear trajectory/target feedback.
5. Fire and resolve the existing physics simulation plus the selected weapon's approved damage behaviour.
6. Continue attacking where necessary. Complex facilities may require sustained, multi-stage attacks and substantially more than three or four shots.
7. Evaluate primary and optional objectives, structural destruction, shot efficiency and completion time.
8. Award regular mission points and bonus Research Data separately.
9. Offer retry/next mission and relevant weapon upgrade choices.

The recommended shot budget is a performance benchmark, not a universal hard cap. Individual levels may require 15, 25 or more shots where the structure and mission justify it. Do not inflate shot counts artificially: every additional attack must contribute to a readable tactical problem.

## 3. Angled 2.5D and physics boundary

- Use an angled three-quarter visual presentation with readable front/side faces, layered environments, shadows and depth cues.
- Keep projectile path, target positions, collision and structural relationships understandable at phone scale.
- Preserve the current 2D physics simulation for the first prototype. Visual depth must not falsely imply collision behaviour the simulation does not support.
- Create one greybox prototype with an operative, angled facility, distinct object shapes, a critical target and physics destruction before bulk asset production.
- If the prototype requires true depth-axis movement or overlapping depth-dependent collision, document the limitation and compare alternatives before any physics-engine migration.

## 4. Operative and weapons

The operative is visible, anonymous and equipped with an evolving arsenal. Multiple weapon types are approved. Build a reusable, data-driven weapon framework rather than separate duplicated firing systems.

Proposed chapter unlock progression (specific balance and mechanics require prototype validation):

- **Chapter I / Helix, 2089:** Kinetic Accelerator (direct kinetic impact) and Breach Charge (limited-use area damage).
- **Chapter II / VITA, 2092:** Precision Accelerator evolution and Penetrator (focused penetration against compatible materials).
- **Chapter III / Nova Grid, 2096:** Pulse Cannon (energy-focused impact and selected infrastructure interactions).
- **Chapter IV / Civitas, 2100:** Disruptor (specialized electronic/control-system interactions).
- **Chapter V / Meridian, 2104:** Temporal Lance (advanced charged impact and temporal-component interactions).

These are design proposals for distinct tactical roles, not permission to implement every effect without validation. Each weapon definition should describe stable ID, display name, unlock, projectile/effect, damage/impact parameters, compatible materials, area/penetration behaviour where relevant, ammunition/energy, cooldown, upgrade compatibility, and visual/audio references.

Start the first prototype with only the Kinetic Accelerator and Breach Charge. Add the remaining weapons incrementally after the framework and level design prove their value. New weapon classes and mechanics are now explicitly approved in principle by the owner, subject to staged implementation, balancing and mobile validation.

## 5. Story-specific destructible institutions

Replace generic block-only presentation with recognizable modular infrastructure while retaining reusable structural physics components.

- **Helix Systems:** AI servers, data cores, control nodes, relay towers, robotic manufacturing and communication infrastructure.
- **VITA Genomics:** bioreactors, containment chambers, genetic storage, laboratory machinery and research infrastructure.
- **Nova Grid:** power cells, transformers, reactor housings, cooling systems and distribution infrastructure.
- **Civitas:** surveillance towers, sensor arrays, control terminals, communication relays and automated enforcement systems.
- **Meridian:** temporal reactors, quantum stabilizers, timeline anchors, energy containment and convergence machinery.

Introduce a small, reusable material vocabulary such as lightweight alloy, reinforced steel, composite, glass/polymer, concrete, electronic modules and energy components. Actual resistance and damage values must be measured and tuned against the current simulation; visual material labels do not automatically imply realistic physics.

Add critical components and weak points where they create understandable tactical choices. Preserve strong contrast between gameplay objects and low-contrast backgrounds. Destruction effects must not obscure the puzzle.

## 6. Mission scoring and hybrid economy

Use two separate outputs:

**Regular Mission Points** record mission performance and contribute to score/rankings. Award for mission completion, structural damage/destruction, critical asset elimination, primary and optional objectives, and special achievements.

**Bonus Research Data** is the primary upgrade currency. Award for completion, speed relative to a level-specific target time, shots used relative to a recommended benchmark, efficient weapon choice, critical and optional objectives, destruction efficiency and selected multiplayer achievements.

Reward efficiency without making speed the only valuable skill. A player must not be punished simply for taking longer to solve a difficult structure. Use per-level target times and shot benchmarks; do not apply one universal threshold.

Campaign completion must remain possible with reasonable base weapon configurations. Upgrades should make destruction more efficient and open alternate tactics, not erase the need for structural reasoning. Avoid mandatory multiplayer participation or excessive grinding.

Initial upgrade attributes, where compatible with a weapon: impact energy, structural penetration, blast efficiency, energy capacity, targeting assistance and energy efficiency. Start with a base state plus up to three meaningful upgrade levels. Use one primary currency unless a separately justified design is approved.

## 7. Leaderboards

Leaderboards are approved as an online feature after scoring is stable. Planned categories:

- Global.
- Friends.
- Chapter.
- Individual level.
- Weekly challenge.
- Multiplayer/Frontlines.

Provide Standard rankings (normal campaign progression and upgrades allowed) and Competitive rankings (standardized loadouts and fixed mission conditions). Store enough context to interpret a result, including player identity/display name, level or challenge ID, score, completion time, shots, applicable loadout/upgrade conditions and submission time.

The backend, not the client, must validate submissions and own authoritative rankings/reward allocation. Do not trust a client-reported score without validation. Protect public display names and account data.

## 8. Asynchronous multiplayer: Temporal Frontlines

**Mode name:** Temporal Frontlines (approved working name).

Frontlines is a persistent, asynchronous, asymmetric build-and-demolish mode. Players do not need to be online simultaneously. Real-time synchronized physics is explicitly out of scope for the initial multiplayer implementation.

### Builder / Defender loop

- Build and expand a persistent institution using a limited construction budget and an approved modular component catalogue.
- Place and rotate components on a validated grid.
- Install structural supports, reinforced walls, industrial platforms, server/energy/critical components and approved defensive modules.
- Protect designated critical assets.
- Save and publish a versioned institution configuration.
- Review incoming attack reports, repair damage, redesign and upgrade the institution.

### Attacker / Operative loop

- Discover or receive a matchmaking-selected institution.
- Attack a stored snapshot of the defender's published institution, not a live session.
- Select an allowed weapon loadout and attack budget.
- Identify weaknesses and destroy critical assets efficiently.
- Receive a validated result and rewards.

### Match and persistence rules

1. Builder submits a structure configuration.
2. Backend validates component IDs, dimensions, grid positions/rotations, connections, budget, critical assets and defensive configuration.
3. Backend stores a versioned immutable snapshot for the attack.
4. Attacker downloads the snapshot and reconstructs it locally using the same approved game rules.
5. Attack result is submitted and validated against match state, allowed loadout, ammunition and scoring rules.
6. Defender receives a report/replay reconstruction on next login.
7. Players may switch roles in a challenge or match format where appropriate.

Do not store a live Godot scene as the authoritative base representation. Store a versioned data definition: component IDs, positions, rotations, material/upgrade levels, structural connections, critical asset IDs, defensive configuration, budget and schema version.

The initial persistent-base mode may use separate attack/defence records and matchmaking. For direct friend challenges, use a two-round role swap and normalized scoring so neither role is inherently advantaged. Do not require simultaneous sessions.

### Fairness and player protection

- Use construction budgets and validated modular placement, not unrestricted free-form drawing.
- Ensure campaign and essential upgrades do not depend on multiplayer.
- Limit repeat attacks and introduce repair/recovery windows or shields after attacks.
- Balance attack and defence through standardized budgets, validated loadouts and normalized outcomes.
- Provide attack history and a replay/reconstruction report where technically feasible.
- Protect against duplicate submissions, altered clients, invalid structures, impossible loadouts, reward farming and alternate-account abuse.
- Backend owns identity, match state, structure versions, result validation, rankings and reward accounting.
- Do not assume deterministic physics across devices. Define a trusted validation/replay strategy and test it before competitive rewards are significant.

### Staged multiplayer scope

1. Single-player gameplay, scoring and upgrades first.
2. Online profiles and leaderboards.
3. Persistent institution construction and validation.
4. Asynchronous attacks against stored snapshots.
5. Attack reports, repairs, recovery protection and rewards.
6. Friends, challenges, leagues and tournaments.

No real-time PvP physics requirement is introduced by this approval.

## 9. Revised delivery order

1. Repository and existing game audit.
2. Application identity migration and signing safeguards.
3. Compatibility-vs-Mobile renderer evaluation.
4. Angled 2.5D greybox prototype with visible operative and existing physics.
5. Data-driven weapon framework with Kinetic Accelerator and Breach Charge.
6. Story-specific modular destructible objects and critical assets.
7. Mission scoring, Research Data and hybrid upgrade economy.
8. Five-chapter vertical slice (one representative level per chapter).
9. Full 100-level campaign in validated batches.
10. Cinematics, art, audio and mobile optimization.
11. Online profiles and leaderboards.
12. Temporal Frontlines asynchronous construction/attack mode.
13. Competitive expansion and release preparation.

Multiplayer is part of the approved product roadmap but must not block the first single-player campaign release. Design data boundaries with future Frontlines compatibility in mind, but do not prematurely add accounts, backend dependencies or networking to the first prototype.

## 10. Revised acceptance principles

- The game reads immediately as an angled 2.5D tactical destruction experience, not a slingshot clone.
- Operative is visible and weapon choice is meaningful.
- Complex facilities can require multi-stage, multi-shot attacks.
- Weapon upgrades improve efficiency without making base campaign content impossible.
- Story-specific structures, materials and critical components are visually distinct and reusable.
- Regular points and bonus Research Data have separate, understandable purposes.
- Speed and shot efficiency are rewarded without overwhelming objective completion or thoughtful play.
- Leaderboards are fair and validated.
- Frontlines works asynchronously against persistent versioned institution snapshots.
- Core mobile performance, stability and campaign quality take priority over online feature breadth.
