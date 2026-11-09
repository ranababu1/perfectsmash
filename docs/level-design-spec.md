# Temporal: First Jump - 100-Level Design Specification

**Status:** Production design draft for owner review  
**Game identity:** Temporal: First Jump (owner-approved 2026-11-09; application ID `dev.imrn.temporal1`)  
**Chapter I mapping:** see `docs/project-audit.md` §3 for how the existing 20 level IDs map onto levels 1-20 below.  
**Gameplay contract:** Preserve the current aim, launch, 2D physics, objective evaluation, scoring, retry and progression systems. This document defines level content and presentation, not new physics mechanics.

## 1. Design principles

1. The player should understand the objective within three seconds of seeing a level.
2. Every level teaches, combines or tests a skill. Difficulty must come from spatial reasoning and cause-and-effect, not arbitrary shot counts.
3. Use only the current supported level vocabulary until code inspection proves otherwise: wood, stone, glass, static structures, destructible blocks, target cores, destroy_targets, and topple with a threshold line. Do not invent explosives, switches, moving platforms, timers, powers or new physics materials.
4. Use the existing 20 levels as a starting library. The coding agent must inspect and map them to this sequence, retaining stable IDs where practical. Do not discard a working level just to match a title.
5. Every level must be solver-checked and human-play-tested. A solver result is not proof of a satisfying puzzle.
6. Each chapter has a five-level teaching rhythm: establish, combine, deepen, mastery, finale. Levels 5/10/15/20 are deliberate milestone beats.
7. Ordinary levels use a title, one short objective/hint and optional intel fragments only at selected milestones. No voiced dialogue is required during normal gameplay.
8. Chapter backgrounds stay low contrast. Destructible objects, targets, trajectory and objective indicators must remain more visually prominent.

## 2. Difficulty and shot-budget policy

- Intro/teaching: 1-2 meaningful actions, one obvious interaction, generous geometry.
- Intermediate: 2-3 actions, two interacting structural ideas, one readable weak point or chain.
- Advanced: 2-3 actions, multi-stage collapse, target placement requiring a deliberate angle or order.
- Finale: 2-3 actions, a clear multi-part structure, satisfying chain reaction and chapter-specific visual identity.
- The shots field is the maximum action budget, not a difficulty score. Par must reflect the intended efficient solution using existing scoring rules.
- Never reduce a shot budget merely to make a level look hard. Never ship a level whose only solution depends on a tiny, frame-sensitive collision.
- Hints teach a useful observation without revealing an exact launch vector.

## 3. Chapter environment and mechanics palette

| Chapter | Levels | Environment | Visual props | Puzzle vocabulary |
|---|---:|---|---|---|
| I. The Machine That Decided | 1-20 | Helix Systems, New Avalon, 2089 | Relay masts, server cabinets, glass control pods, logistics gantries, cooling stacks | Basic wood/glass/stone interactions, support removal, towers, domino chains, targets at varied heights |
| II. The Price of Perfection | 21-40 | VITA Genomics, Arclight Bio-District, 2092 | Sterile lab frames, bioreactor housings, clean-room glass, storage racks, research vaults | Fragile glass barriers, heavy stone caps, stacked structures, protected targets, multi-target planning |
| III. The Energy Beneath | 41-60 | Nova Grid, Kestrel Energy Basin, 2096 | Reactor rings, cooling towers, cable bridges, containment platforms, energy storage frames | Tall and wide structures, elevated targets, static barriers, chain reactions, multi-step collapse |
| IV. The Quiet Cage | 61-80 | Civitas, Central Governance Zone, 2100 | Sensor towers, data exchange racks, civic screens, relay bridges, archive vaults | Occlusion, target clusters, multiple towers, topple thresholds, precise arcs and controlled cascades |
| V. The Convergence | 81-100 | Meridian, subterranean convergence facility, 2104 | Hybrid server/lab/reactor structures, heavy central core, redundant support frames | Combined skills, layered structures, multi-target sequences, demanding but fair finales |

## 4. Level-by-level mission design

Descriptions define intended puzzle reasoning. Exact coordinates and dimensions must be authored in the existing coordinate space after inspecting the level loader, physics tuning and solver. Do not copy arbitrary coordinates from this document.

### Chapter I - The Machine That Decided (Levels 1-20)

| Lvl | Mission | Puzzle layout / intended solution idea | Skill / difficulty | Shots |
|---:|---|---|---|---:|
| 01 | First Contact | Single exposed target on a simple low platform; clean direct hit. | Learn aim, launch and target feedback / Intro | 2 |
| 02 | The Welcome System | One narrow wood security mast with target perched high; teach high/low impact choice. | Vertical aiming / Intro | 2 |
| 03 | Traffic of One | Two supports hold a crossbeam above one target; hit a support and let gravity finish. | Weak-point recognition / Intro | 2 |
| 04 | Supply Chain | Three stacked wood crates form a narrow tower; target sits at the top. | Stack instability / Intro | 2 |
| 05 | The Safety Layer | Two fragile glass supports protect a target behind them; one clear direct lane. | Glass introduction / Intro milestone | 2 |
| 06 | Cold Storage | Two adjacent target towers are close enough for one falling tower to disturb the other. | First chain reaction / Intro-intermediate | 2 |
| 07 | Blind Spot | A heavy stone cap rests on two light supports above a target; remove one support. | Weight and gravity / Intermediate | 2 |
| 08 | Human Override | A row of narrow wood posts leads to a target behind the last post. | Domino sequencing / Intermediate | 1 |
| 09 | Redundancy | Topple objective: compact stack with its upper block above the threshold; collapse all blocks below the line. | First topple objective / Intermediate | 2 |
| 10 | The Replica | Two separated target towers, with a clear first target and a second target reachable by a planned follow-up. | Shot sequencing / Intermediate milestone | 2 |
| 11 | Priority One | Target is tucked behind a tall static wall; use a high arc over the wall. | Trajectory planning / Intermediate | 2 |
| 12 | No Exceptions | Pyramid-like wood stack with target on top; find the lower central support. | Load-bearing support / Intermediate | 2 |
| 13 | The Quiet District | Glass roof over a target held by two fixed side supports; break the roof or its supports to expose target. | Material plus target access / Intermediate-advanced | 2 |
| 14 | Root Access | A stone shield sits in front of a target; use impact on a movable wood piece to create a secondary collision. | Indirect impact / Advanced | 2 |
| 15 | The Directive | Two fragile towers with targets at different heights and a single useful firing lane. | Multi-target aiming / Advanced milestone | 3 |
| 16 | Failsafe | Three target positions on ascending static ledges; choose a route that clears more than one per action. | Angle selection / Advanced | 3 |
| 17 | Last Backup | Three separated wood pillars must all be toppled below a line; stagger them so falling bodies can interact. | Multi-object topple / Advanced | 3 |
| 18 | Cascade | Tall barrier blocks direct shots; a high arc reaches a target structure. | Advanced arc / Advanced | 2 |
| 19 | Central Logic | Elevated row of domino posts on a fixed ledge; one impact starts a long chain into the target. | Precision chain reaction / Advanced | 1 |
| 20 | The Machine That Decided | Finale: layered operations hall with multiple supports and three visible target cores. A readable sequence collapses the upper structure into the lower targets. | Combined Chapter I skills / Finale | 3 |

### Chapter II - The Price of Perfection (Levels 21-40)

| Lvl | Mission | Puzzle layout / intended solution idea | Skill / difficulty | Shots |
|---:|---|---|---|---:|
| 21 | A Longer Life | One target inside a simple glass lab enclosure; expose it with a direct glass break. | Chapter reset, familiar mechanic / Intro | 2 |
| 22 | Clean Room | Two glass panels stand in front of a wood support tower; remove the panel or tower to reach target. | Glass as barrier / Intro | 2 |
| 23 | The Sequence | A genomics rack made of repeated narrow wood uprights; target rests on top. | Repeated supports / Intro | 2 |
| 24 | Growth Chamber | One stone cap is supported by glass columns; break the fragile supports to drop the cap. | Material contrast / Intermediate | 2 |
| 25 | Trial Run | Two small containment frames, each with a target; arrange one collapse to strike both if possible. | Two-target planning / Intermediate milestone | 3 |
| 26 | Better Than Human | Target is high inside a tall bioreactor frame; attack a side support rather than the target directly. | Structural access / Intermediate | 2 |
| 27 | Cold Chain | A long storage rack with a heavy top beam and a target near one end; hit the opposite support to rotate the beam. | Controlled beam collapse / Intermediate | 2 |
| 28 | The Dependency | A target is protected by a stone front block and fragile rear supports; use a side structure to create a falling collision. | Indirect route / Intermediate | 2 |
| 29 | Replication Error | Two stacked towers are connected by a shared top beam; remove the shared support to start a cascade. | Shared-support reasoning / Intermediate | 2 |
| 30 | Controlled Growth | Three target cores in a row, each separated by a glass panel; one shot opens the first lane, second completes the sequence. | Multi-target / Intermediate milestone | 3 |
| 31 | The Patent Wall | Tall archive stacks with a target on a narrow upper shelf; arc over a static divider. | Precision arc / Intermediate-advanced | 2 |
| 32 | Patient Zero | Target sits in a protected lower bay beneath a heavy stone cap; remove side supports in a deliberate order. | Layered support / Advanced | 2 |
| 33 | The Upgrade | A vertical production tower with glass outer panels and wood interior supports; break the panel to destabilise the core. | Mixed-material collapse / Advanced | 2 |
| 34 | The Price | Two heavy caps balance on opposite ends of a central support; strike the centre support to trigger a readable collapse. | Symmetric structure / Advanced | 2 |
| 35 | No Consent | Three targets in a tall enclosure with a narrow opening; plan one high and one low trajectory. | Two-angle planning / Advanced | 3 |
| 36 | The Black Archive | A target is hidden behind a stone wall, but a fragile glass roof and wood side frame allow an overhead collapse. | Occlusion / Advanced | 2 |
| 37 | The Prediction | A multi-tier stack with one critical narrow support beneath the top tier; identify the load path. | Precision weak point / Advanced | 2 |
| 38 | The Last Batch | Two separated lab towers; first collapse must not block the second firing lane. | Order and lane management / Advanced | 3 |
| 39 | Dependency Chain | Large linked frame with two target cores at opposite ends; one shot weakens, another completes the cascade. | Multi-stage sequence / Advanced | 3 |
| 40 | The Price of Perfection | Finale: central bioreactor frame, glass containment shell, heavy cap and multiple targets. A controlled support failure brings the shell down into the target zone. | Combined Chapter II skills / Finale | 3 |

### Chapter III - The Energy Beneath (Levels 41-60)

| Lvl | Mission | Puzzle layout / intended solution idea | Skill / difficulty | Shots |
|---:|---|---|---|---:|
| 41 | Endless Power | A simple reactor support tower with one exposed target and a clear direct shot. | Chapter reset / Intro | 2 |
| 42 | The Intake | A tall intake frame with target behind one wood support; remove the support from a low angle. | Low-angle approach / Intro | 2 |
| 43 | Containment Ring | Three supports hold a wide ring-like beam; one target beneath the centre. | Wide-span structure / Intermediate | 2 |
| 44 | Cooling the Future | Two tall cooling stacks with targets near their tops; use falling structure to reach the target. | Tall structures / Intermediate | 2 |
| 45 | The First Pulse | A target is positioned beyond a static containment wall; a high arc is the clean solution. | Arc over barrier / Intermediate milestone | 2 |
| 46 | Load Balancing | A long beam rests on two uneven supports; strike the weaker side to rotate it toward target. | Asymmetric support / Intermediate | 2 |
| 47 | Deep Storage | Multiple stacked storage blocks with a target in the lower centre; collapse upper layers through a side hit. | Vertical cascade / Intermediate | 2 |
| 48 | Silent Alarm | Two target towers are linked by a narrow bridge; remove the bridge support to create a chain. | Linked structures / Intermediate | 2 |
| 49 | Overload Window | A stone top plate is supported by glass and wood; the target sits below the plate. | Material ordering / Advanced | 2 |
| 50 | The Resonance | Set piece: ring-shaped arrangement of supports with target at centre; a side impact starts a circular-looking collapse using ordinary rigid bodies. | Spatial planning / Advanced milestone | 3 |
| 51 | Beyond the Grid | A distant target is raised behind a static barrier; use a steep arc without hitting the barrier. | Long-range arc / Advanced | 2 |
| 52 | The Wrong Frequency | Two elevated targets at different heights; first shot creates access for second. | Two-shot sequencing / Advanced | 3 |
| 53 | The Deep Core | A central target under a heavy cap with offset supports; remove the offset support, not the centre. | Offset weak point / Advanced | 2 |
| 54 | Blackout Protocol | Two towers support a long beam above a target; one tower must fall first to rotate beam into target. | Controlled beam rotation / Advanced | 2 |
| 55 | The Echo | Repeating domino structures on two levels; first chain triggers the second. | Multi-tier chain / Advanced | 2 |
| 56 | Dead Circuit | Target behind a fixed wall and under a glass canopy; use the canopy collapse as an indirect strike. | Indirect target access / Advanced | 2 |
| 57 | Origin Unknown | A target is shielded by stone but exposed from above; use an elevated launch arc. | Geometry reading / Advanced | 2 |
| 58 | The Listening Machine | Several supports surround one target; the intended first hit causes the top frame to fall inward. | Inward collapse / Advanced | 2 |
| 59 | Final Containment | Three targets distributed across a wide structure; efficient solution requires two shots with a planned order. | Multi-target mastery / Advanced | 3 |
| 60 | The Energy Beneath | Finale: broad reactor platform with upper ring, lower supports and three targets. A staged collapse reveals the central signal chamber. | Combined Chapter III skills / Finale | 3 |

### Chapter IV - The Quiet Cage (Levels 61-80)

| Lvl | Mission | Puzzle layout / intended solution idea | Skill / difficulty | Shots |
|---:|---|---|---|---:|
| 61 | A Predictable World | One sensor tower and one target, with a simple support to remove. | Chapter reset / Intro | 2 |
| 62 | The Profile | Two narrow sensor masts, each with a target at a different height. | Vertical target planning / Intro | 2 |
| 63 | The Forecast | A target behind a tall static data wall; a high arc provides access. | Arc / Intermediate | 2 |
| 64 | Access Denied | A glass access screen protects a lower target; break screen then strike target. | Two-action access / Intermediate | 2 |
| 65 | The Invisible Rule | A line of narrow posts leads to a target behind a fixed divider; set off the chain from a safe angle. | Chain plus barrier / Intermediate milestone | 2 |
| 66 | Quiet Signals | Three small target towers are spaced across a wide platform; use a planned sequence, not random shots. | Multi-target / Intermediate | 3 |
| 67 | The Approved Path | A target rests on an elevated beam with a narrow support; attack the support from below. | Low trajectory / Intermediate | 2 |
| 68 | The Exception | Topple objective with a staggered stack and a threshold that requires all blocks to settle below it. | Topple mastery / Intermediate | 2 |
| 69 | Public Safety | Two sensor towers are linked by a high crossbeam; collapsing one end swings the beam into the other. | Linked tower cascade / Advanced | 2 |
| 70 | The Mirror | Target sits inside a frame; remove one of two outer supports to open a lane. | Symmetry and choice / Advanced milestone | 2 |
| 71 | The Model Knows | Three targets occupy upper, middle and lower tiers; one shot should create a cascade, second cleans up. | Vertical cascade / Advanced | 3 |
| 72 | Prewritten | A static wall separates launcher from target; only a narrow high arc reaches the rear structure. | Precision arc / Advanced | 2 |
| 73 | The Shared Signature | Three towers share a long support beam; the correct end support creates a chain across all targets. | Shared support / Advanced | 2 |
| 74 | The Quiet Cage | A wide civic relay frame has targets at both ends and a central load-bearing stack. | Wide structure / Advanced | 3 |
| 75 | No Unknowns | A tall stack of mixed wood, glass and stone hides the critical support at its base. | Mixed-material weak point / Advanced milestone | 2 |
| 76 | The Future File | A target is trapped below a heavy slab and above a topple line; collapse must clear both objective conditions. | Combined objective reasoning / Advanced | 3 |
| 77 | The Missing Year | Two separate structures with a single shared trajectory window; first shot must preserve access to the second. | Shot order / Advanced | 3 |
| 78 | Source Code | A target sits on a narrow ledge beyond a tall static barrier; one high arc and a follow-up support strike. | Arc plus precision / Advanced | 3 |
| 79 | The Last Forecast | A dense but stable structure with a clearly telegraphed weak support and three targets. | Pre-finale mastery / Advanced | 3 |
| 80 | The Quiet Cage | Finale: central civic tower, side relay masts, elevated crossbeam and multiple targets. A staged collapse disables the full relay network. | Combined Chapter IV skills / Finale | 3 |

### Chapter V - The Convergence (Levels 81-100)

| Lvl | Mission | Puzzle layout / intended solution idea | Skill / difficulty | Shots |
|---:|---|---|---|---:|
| 81 | No Public Record | A simple hybrid server frame with one exposed target; establish the final environment. | Chapter reset / Intro | 2 |
| 82 | Beneath the City | A tall underground support frame with target at the base; remove a side support to drop the upper structure. | Vertical collapse / Intermediate | 2 |
| 83 | Four Foundations | Four small support clusters protect one central target; find a cascade path across the clusters. | Combined structures / Intermediate | 3 |
| 84 | The Common Model | Three targets at different heights behind a static wall; arc and collapse sequencing. | Multi-height target planning / Intermediate | 3 |
| 85 | The Hidden Budget | A heavy stone cap balances on light supports above two targets. | Weight transfer / Intermediate milestone | 2 |
| 86 | The First Directive | A narrow bridge of domino posts crosses a gap to a target structure. | Long chain / Advanced | 2 |
| 87 | The Operator | A central target is hidden inside a dense frame with two possible weak points; one is safer and more efficient. | Weak-point selection / Advanced | 2 |
| 88 | The Convergence Engine | Three-tier central structure with a target on each tier; collapse top-down in a controlled sequence. | Layered target sequence / Advanced | 3 |
| 89 | The Failsafe Network | Two redundant towers support the same crossbeam; both must fall before the target is exposed. | Redundancy reasoning / Advanced | 3 |
| 90 | The Other Timeline | Two linked structures on separate elevations; first collapse redirects falling mass into the second. | Cross-structure chain / Advanced milestone | 3 |
| 91 | The Chosen Outcome | Multiple targets arranged around a central support; one precise shot must start a controlled outward collapse. | Precision chain / Advanced | 3 |
| 92 | The Human Variable | Topple objective with a broad mixed-material structure; every movable block must finish below the threshold. | Topple under complexity / Advanced | 3 |
| 93 | The Last Safeguard | A heavy central cap protected by two outer frames; remove outer frames in a deliberate order. | Multi-stage access / Advanced | 3 |
| 94 | Break the Chain | Long chain reaction spanning three structural groups, with target at the end. | Long-range cascade / Advanced | 2 |
| 95 | The Core Directive | Large layered frame with three target cores and one critical central support. | Finale preparation / Advanced | 3 |
| 96 | Before the Beginning | A small historical archive structure with target behind a fixed wall and a narrow top opening. | Precision arc / Advanced | 2 |
| 97 | The Final Relay | A temporal relay frame with two targets and a chain of light supports; one action opens the second shot. | Two-stage sequence / Advanced | 3 |
| 98 | No Return Path | Tall narrow tower with a heavy cap, glass side panels and a target at the bottom. | Mixed-material precision / Advanced | 3 |
| 99 | The Last Structure | Final pre-finale puzzle: broad multi-tier frame, three targets, two clear weak points and no pixel-perfect shot. | Comprehensive mastery / Advanced | 3 |
| 100 | The Wrong Future | Finale: Meridian central core, hybrid layered structure, multiple target cores and a visible central objective. Success triggers the apparent-victory cinematic and 2041 reveal. | Full-release finale / Finale | 3 |

## 5. Milestone narrative and level cadence

- Opening cinematic plays once before level 1; replayable from Story Archive after unlock.
- Chapter intros play before levels 1, 21, 41, 61 and 81.
- Chapter outros play after levels 20, 40, 60 and 80.
- Level 100 plays the longer finale sequence after success is committed to the save.
- Optional one-line intel can appear at levels 1, 5, 10, 15 and 20 of each chapter. Keep each line short and never block input.
- No ordinary level requires voiceover or a unique cutscene.

## 6. Data and implementation contract for the coding agent

### Inspect before changing
Read docs/instructions.md, docs/currentstate.md, relevant sections of docs/plan.md, docs/narrative-bible.md, this document and the current data/levels.json. Inspect the level schema, loader, validator, solver, scoring, save/progression and tests before modifying content. Confirm exact supported objective types, material identifiers, coordinate bounds, body limits and physics tuning from code.

### Required implementation sequence
1. **Baseline:** Verify branch, clean/dirty working tree, Godot version, current 20-level catalogue, test commands and solver results. Preserve uncommitted user changes.
2. **Schema audit:** Produce a short report mapping every design element here to an existing supported level field. If a required feature is unsupported, do not silently add a mechanic. Propose the smallest safe extension and wait for approval.
3. **Vertical slice:** Implement and validate five representative reskins/levels, one from each chapter, while preserving the current gameplay loop. Build and test on Android.
4. **Chapter batches:** Add levels in batches of five. For each batch run JSON/schema validation, solver checks, automated tests, visual review and a playable manual pass before proceeding.
5. **Progression:** Verify 1-100 unlock order, save migration from existing 20-level players, stars, retries, next-level navigation and chapter boundaries.
6. **Story layer:** Implement cinematics and Story Archive as a separate feature set. Do not couple cinematic playback to physics session state.
7. **Release validation:** Full 100-level regression, representative device/aspect-ratio tests, audio/cinematic interruption tests, Android export and clean-install/upgrade checks.

### Content validation gates
- Exactly 100 unique stable level IDs in the first-release catalogue.
- Every level has valid required fields and only supported values.
- Every level has at least one verified solution within its shot budget.
- No solution relies on nondeterministic, extremely narrow or frame-sensitive collision timing.
- No level starts with overlapping bodies unless the existing engine explicitly supports and validates that arrangement.
- No target is obscured by decorative art or background elements.
- Level objective, hint, chapter label and level name agree.
- All levels load without warnings/errors on the target Godot version.
- Every chapter has a distinct environment palette, but gameplay contrast remains consistent.
- Save migration preserves existing progress and maps old level IDs explicitly.

### Git and documentation rules
Follow docs/instructions.md exactly. Work on the existing intended branch unless the owner approves a branch change. Do not reset, clean, force-push, rewrite history or discard user changes. Push after each buildable file change or at the stated 50-line threshold, whichever comes first. Update docs/changelog.md and docs/currentstate.md with verified results. Never claim a test/build/push succeeded without actual command evidence.

## 7. Definition of done for the 100-level content milestone

- 100 levels are present, unique, loadable and ordered by chapter.
- All 100 pass schema validation and solver verification.
- Human play-test notes exist for all 100, with at least one full end-to-end playthrough on a physical Android device.
- No regression to physics, aiming, score, retry, save or progression behavior.
- The existing 20-level save data migrates safely.
- Chapter intros/outros and the level-100 finale unlock and replay correctly.
- currentstate.md states exactly what is implemented and what remains outstanding.
