# Smash Theory: Product and Engineering Plan

**Document status:** Original project baseline  
**Product type:** 2D physics destruction puzzle  
**Initial platform:** Android  
**Default engine direction:** Godot 4.x + GDScript with built-in 2D physics

## 1. Product vision and target audience

Smash Theory is a compact destruction puzzle where the player has a limited number of actions to destabilize a structure, trigger a satisfying collapse, and meet a clear objective. The fun should come from understanding cause and effect, not from random explosions alone.

Primary audience:
- Casual players who enjoy physics toys and destruction.
- Puzzle players who like limited moves and clever solutions.
- Players attracted to short, visually rewarding sessions.

Product promise: “One smart hit. A spectacular chain reaction.” This is a positioning hypothesis to validate, not a guarantee of engagement.

## 2. Core gameplay loop and mechanics

1. Show a structure, a target condition, and the available action budget.
2. Player selects an allowed action, such as launching one projectile at a target point.
3. Physics simulates collision, momentum, gravity, and structural response.
4. The level waits for the simulation to settle or reaches a bounded timeout.
5. Evaluate the objective: target objects destroyed/removed, target zone reached, or structure reduced below a threshold.
6. Award a result based on objective completion, actions used, and optional score.
7. Offer retry or next level.

MVP recommendation: use a limited projectile-launch mechanic with simple destructible targets and static/dynamic blocks. Do not start with freeform weapons, complex materials, or multiple projectile classes.

Physics must be deterministic enough for repeatable local play where possible, but do not promise bit-identical results across all devices/engine versions. Daily reproducibility can rely on fixed level setups and rules, not remote physics simulation.

## 3. Unique selling proposition and differentiation

Potential differentiators:
- Short, readable levels with clear cause-and-effect.
- A restrained visual style that makes motion and impact easy to follow.
- Cleverly authored puzzles with multiple plausible approaches.
- Replays that make a satisfying collapse easy to watch or share later.
- A strong “few actions, big result” identity.

Avoid building a generic sandbox with no clear objective. The MVP should teach players to predict structure behavior and reward experimentation.

## 4. MVP scope and explicit exclusions

### Included
- Godot 2D physics.
- Portrait or landscape decision validated in the first prototype; default to landscape only if aiming mechanics require more horizontal space, otherwise portrait.
- Aiming and launching one simple projectile.
- A small set of blocks, static surfaces, and target objects.
- Limited action count per level.
- Win/loss evaluation after the physics simulation settles.
- Retry, next level, basic score/medal, local progress.
- Approximately 20 handcrafted levels for the first public validation build.
- Settings for sound and vibration if included.
- Offline-first play.

### Explicitly excluded
- 3D physics.
- Multiplayer, PvP, clans, chat, accounts, cloud saves.
- User-generated levels, level editor, workshop, or replay sharing in MVP.
- Complex damage/material simulation, deformable meshes, fluids, ragdolls, vehicles, or large-scale destruction.
- Live-service events and backend.
- Monetization until core level completion and retention are validated.
- Unbounded debris counts or expensive per-frame custom physics.

## 5. Progression and difficulty balancing

Progression sequence:
1. One projectile, one obvious weak point.
2. Introduce support blocks and gravity.
3. Require a chain reaction across two or three objects.
4. Add limited-action efficiency goals.
5. Combine previously taught elements in expert levels.

Difficulty factors:
- Number of interactions required.
- Visibility of the weak point.
- Number of plausible shot choices.
- Sensitivity to aim precision.
- Simulation time and readability.
- Action budget and penalty for failure.

Avoid requiring pixel-perfect aiming on touchscreens. Use forgiving aim assistance or a visible trajectory preview only if it does not trivialize the puzzle. A preview can be a later experiment.

Level acceptance:
- Objective can be achieved with the stated action budget.
- Failure states are understandable and recoverable via retry.
- Physics settling logic does not falsely declare a win while objects are still moving.
- No softlock; restart restores the exact initial setup.
- Test on different frame rates and device classes.

## 6. Technical architecture and recommended stack

### Default stack
- Godot 4.x stable and GDScript.
- Godot 2D physics bodies/shapes, using built-in physics unless a measured limitation justifies an alternative.
- Native Android export.
- No external physics engine in MVP.

### Suggested modules
- `LevelDefinition`: level layout, object types, goals, action budget, tuning values.
- `LevelLoader`: validates and instantiates level content.
- `AimController`: touch aiming, launch direction and power.
- `ProjectileController`: launch state, collision response, lifecycle.
- `DestructionRules`: object removal/damage rules and objective state.
- `SimulationMonitor`: detects physics settling using bounded velocity/time checks and a hard timeout.
- `ObjectiveEvaluator`: evaluates completion and score from stable game state.
- `ProgressService` / `SaveService`: local completion and settings persistence.
- UI scenes: aim, HUD, result, retry, settings.

Keep objective evaluation separate from the physics engine and scene presentation. Prefer explicit object groups/types over brittle node-name checks. Use collision layers/masks deliberately and document them.

### Physics guardrails
- Set sensible body counts and collision shape complexity.
- Avoid creating hundreds of debris bodies.
- Reuse or pool only if profiling shows allocation spikes.
- Keep simulation settling thresholds configurable and covered by tests.
- Use a fixed, documented timeout so a level cannot hang forever.
- If physics outcomes vary, design objectives with tolerances rather than fragile exact positions.

## 7. UI/UX and visual direction

- Bold, clean 2D shapes and high-contrast targets.
- Make the objective and remaining actions visible before the player acts.
- Use a clear drag/aim/launch gesture with a visible affordance.
- Distinguish background, structural pieces, projectile, and objective objects.
- Use impact effects sparingly; readability and perceived weight matter more than screen-filling particles.
- Offer immediate retry after failure and a fast route to the next level after success.
- Keep camera motion restrained and ensure UI remains usable on common aspect ratios.
- Support pause/resume and avoid accidentally firing when a user touches UI controls.

## 8. AI-assisted development opportunities

- Generate candidate level layouts and weak-point hypotheses, then simulate and manually validate them.
- Draft test matrices for collision groups, settling, scoring, and restart behavior.
- Generate placeholder textures and sound concepts with licensing and consistency checks.
- Use AI to help inspect anonymized play-test results for levels with high retry/abandonment rates.
- Use code assistants for small, tested GDScript changes and documentation.

Never accept an AI-proposed physics formula, level, or success condition without tests and play-testing. Do not expose secrets or personal player data to AI tools. Review commercial-use rights for generated assets.

## 9. Monetization strategy

Do not monetize the first prototype. Validate the satisfaction of the destruction loop first.

Possible future options:
- Rewarded ad for an optional extra attempt after a level failure.
- One-time ad removal.
- Cosmetic projectile trails or block themes.
- Optional curated level packs.

Avoid forced ads during a collapse or immediately before a retry. Test the effect of any ad placement on retry rate, session length, D1/D7 retention, and store reviews.

## 10. Analytics, retention, and viral growth

Potential events:
- `tutorial_started`, `tutorial_completed`
- `level_started`, `level_completed`, `level_failed`
- `attempt_used`, `retry_used`, `simulation_timeout`
- `session_length_bucket`, `levels_per_session`
- `share_sheet_opened` if replay/result sharing is later introduced

Keep measurement minimal and privacy-reviewed. The initial prototype can use consented play-test observations without a third-party SDK.

Metrics and proposed hypothesis gates:
- Store listing conversion: installs / listing visitors; target initial test ≥20% with traffic source reported.
- Tutorial completion: target ≥80% in a usability cohort.
- D1 retention: initial hypothesis ≥25%; D7 ≥8%, interpreted with sample size and traffic source.
- Engagement: median session length, levels per session, retries per level, successful completion rate.
- Sharing: later measure share-sheet opens per eligible user; do not treat opening the Android share sheet as proof a share was sent.

Experiments:
1. Compare “clever destruction puzzle” store creative against “spectacular chain reaction” creative.
2. Test whether a trajectory preview improves completion without reducing perceived skill.
3. Compare objective clarity variants in the first three levels.
4. Later test short replay cards or clips only if capture/export is reliable and privacy-safe.

## 11. Development milestones and acceptance criteria

### M0: Physics spike
- A projectile can be aimed and launched on a physical Android device.
- Physics runs smoothly on a low-to-mid-range target device.
- Input cannot accidentally launch when interacting with UI.

### M1: Rules and objective model
- Unit tests cover action budget, target condition, win/loss state, and repeated evaluation.
- Simulation settling and timeout behavior are defined.
- Restart restores the same level definition and initial state.

### M2: Playable prototype
- At least five test levels demonstrate the core loop.
- Success/failure is clear and repeatable enough for intended gameplay.
- No physics body or timer can leave a level permanently stuck.

### M3: Content and progression
- Initial curated levels load through validated definitions.
- Every level is manually checked and automated checks cover objective/configuration consistency.
- Progress persists safely across app restarts.

### M4: Usability and performance
- Aiming is usable on multiple screen sizes.
- Collision and target visuals remain legible during chain reactions.
- Pause/resume, audio settings, retry, and app backgrounding are tested.
- No known blocker prevents a complete play-through.

### M5: Closed testing
- Test across representative Android devices and frame-rate conditions.
- Record level completion, retries, session engagement, tutorial completion, D1/D7, and store conversion.
- Review crash/ANR and simulation timeout reports.

### M6: Release candidate
- Clean install and upgrade paths verified.
- Google Play listing, privacy, content rating, permissions, signing, release notes, and current platform requirements reviewed.
- Explicit release approval recorded.

## 12. Risks, assumptions, and validation experiments

Risks:
- Physics may feel random rather than skill-based.
- Small device screens can make aiming difficult.
- Physics settling logic may trigger wins too early or too late.
- Excessive debris or effects can hurt performance.
- The core mechanic may not differentiate in a crowded category.

Assumptions:
- A limited action budget creates meaningful decisions.
- Players enjoy watching consequences of their own choices.
- Short, curated levels are more useful for initial validation than a sandbox.

Experiments:
- Observe five to ten players aiming without explanation.
- Compare objective-completion reliability on low-, mid-, and high-range devices.
- Measure retries and abandonment by level.
- Run performance profiling before increasing body counts or particle complexity.

## 13. Google Play release strategy

- Check current Play Console target API and policy requirements at release time.
- Use internal testing, then closed testing before production.
- Prepare icon, screenshots, store copy, privacy policy, Data safety answers, content rating, ads declaration, and support details.
- Confirm all third-party assets and audio are licensed for distribution.
- Test app lifecycle, physics behavior, clean install, upgrade, and save persistence on physical Android devices.
- Use an Android App Bundle unless current Play guidance says otherwise.
- Keep signing material out of Git; use Play App Signing where appropriate.
- Roll out gradually if available and monitor crashes/ANRs, level failure, timeouts, conversion, tutorial completion, and D1/D7.
- Never use deceptive destruction claims, fake reviews, or unverified performance statements.
