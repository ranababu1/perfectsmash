# Batch 5 Pre-Work Review: Findings and Proposals (2026-11-09)

Review of `main` at `b3d8844`, requested by the owner before Batch 5. Investigation, tests and tooling are committed (`33dd17f`, `8225262`, `1f1a636`, `1f417b5`). **No core gameplay or progression rule has been changed.** Items marked **Proposal** await owner approval.

## 1. `ProgressData.record_mission()`: failed runs can raise `best_points`

**Finding (confirmed in code):** `best_points = max(previous, score.mission_points)` runs for every attempt, while `best_shots`, `best_time` and optional-objective credit are already restricted to successful runs. A failed run that destroyed a lot can therefore raise a mission's "best" score, contradicting the documented rule. It also mixes failed-attempt scores into the value a future leaderboard would read.

**Proposal (save schema v4):**
- `best_points`: best Mission Points of a **successful** run only. This is the leaderboard-eligible value.
- New `best_attempt_points`: best points of **any** attempt, including failures. It's shown as progress feedback, preserves failed-attempt destruction scoring, and is never leaderboard-eligible.
- New `attempts` and `completions` counters (useful for difficulty tuning and later analytics).
- Research Data rule unchanged (failures earn 0; grants are improvement-only).
- Migration v3 → v4: records with `completed == false` move `best_points` into `best_attempt_points` and set `best_points` to 0. Completed records keep `best_points`, copy it to `best_attempt_points`, and start the counters at 1/1.

A failure can't out-score a success under the current formula (a success always adds ≥ 1000 completion + 500 critical), so completed records are not contaminated in practice.

## 2. Blast occlusion

**Finding:** `MissionWorld.blast()` damages everything within range by distance only, so walls and shields don't shield. Measured with `tools/regression/tactics_probe.gd`:
- A charge on the deck destroys the support columns beneath it *through* the deck.
- The steel core shield gives no protection from blasts.

**Prototype (committed, off by default):** `blast_occlusion` casts a ray from the blast centre to each target's nearest point. Every intervening component passes `0.5 − blast_resistance` of the blast (minimum 0.05); statics pass 0.05; weapon penetration lets the blocked share through proportionally; blockers compound. Knockback is attenuated the same way. Covered by 5 new tests (default off, steel shielding = 0.1, clear line = 1.0, penetration 0.55, two blockers = 0.05, damage × falloff × transmission).

**Proposal:** enable occlusion, and move the per-material transmission into `data/materials.json` (`blast_transmission`) rather than deriving it from `blast_resistance`.

## 3. Effective-shot accuracy

**Finding:** correct. A projectile reports one strike; its direct hit and blast are summed and recorded once; secondary blasts are never credited. 5 new physics tests lock this in:
- A multi-component blast counts as 1 effective shot.
- A power-cell chain adds nothing.
- A shot through a destroyed component's former position counts 0.
- A ground detonation that damages nothing counts 0.
- Two separate damaging shots count 2.

No change needed.

## 4. The one-shot Breach Charge clear

Sweep of 112 Breach trajectories (14 angles × 8 powers) and 15 Kinetic angles (up to 8 shots each), all fired from the real operative muzzle:

| Variant | Single Breach kills core | Kinetic angles that clear (≤8 shots) | Fewest kinetic shots |
|---|---|---|---|
| Current layout | **31/112 (28%)** | 1/15 | 7 |
| Core health ×2 | 30/112 (27%) | 1/15 | 7 |
| Occlusion | 17/112 (15%) | 1/15 | 7 |
| Occlusion + steel hood on core | 15/112 (13%) | 1/15 | 7 |
| Occlusion + load-aware knockback | 16/112 (14%) | 1/15 | 7 |
| **Proposal:** occlusion + load-aware knockback + blast wall 140→90 px + core health ×2 | **16/112 (14%)**, all of them precise column breaches | **7/15** | **3** |
| Proposal with a hardened (composite) core | 0/112 | 2/15 | 7, and breach + 8 kinetic fails to finish |

**Findings:**
- The one-shot clear is **not** blast damage to the core: core health ×2 barely changes it. A Breach anywhere on the deck destroys the columns through the deck, or knocks the loaded deck loose. The deck then falls, and the core dies in the collapse.
- After occlusion, every remaining one-shot is a charge landed **against the left support column** (x ≈ 802). That's a legitimate, clever play: exploiting the load path.
- From the real operative position, the **Kinetic Accelerator has no useful target**. Low shots hit the steel blast wall, 8° clips the deck, and 10°+ hits the steel core shield. Not one first shot changes any component's state. The layout, not the weapon, removes its tactical role.

**Proposal:** adopt the "Proposal" variant:
- Enable occlusion.
- Make the knockback threshold use the mass of a piece plus everything it carries (`load_aware_push`).
- Lower the blast wall to 90 px.
- Raise the core's `health_scale` from 1.5 to 3.0.

**Effect:** the precise column Breach stays a reward for expert play. Breaches elsewhere no longer clear the mission. The Kinetic Accelerator gets a real "collapse the support" route of 3–6 shots. The rack-cluster Breach still clears both racks without touching the core.

**Open question for the owner:** should a collapse always destroy the core? If not, a middle value between the "Proposal" and "hardened" variants can turn a collapse into "core exposed and damaged, finish it off". Tuning would happen in Batch 5 with this probe.

## 5. Desktop (3752) vs Android (3746) score

**Exact source:**
1. **Different input (main cause).** The desktop capture fired a Kinetic shot plus a scripted Breach. The Android run was one Breach from a real touch on a 2856×1280 screen, which projects to a different aim point and launch velocity. Only the structural-destruction term differed (452 vs 446).
2. **Small cross-platform physics divergence (secondary).** The identical scripted sequence (`tools/regression/score_replay.tscn`) gave, on the same build:

| Sequence | Windows x86_64 | Android emulator x86_64 |
|---|---|---|
| kinetic_then_breach | 3752 points, damage 0.4516, 171 frames | 3752 points, 0.4519, 172 frames |
| breach_only | 3734, 0.4337, 152 frames | 3734, 0.4340, 153 frames |
| two_kinetic_column | 436, 0.0359, 1270 frames | identical |

Scoring maths is deterministic. Godot 2D physics is repeatable on one platform but **not bit-identical across platforms**. This one is absorbed by rounding, but it can flip a rounded point, and physical ARM devices may diverge more.

**Regression tests added:**
- A golden pure-scoring breakdown, with exact values and no physics.
- A scripted physics replay run twice in one process (must be identical) and checked within tolerance of the measured reference.
- The replay scene can be run on any device via `make_eval_project.py --main res://tools/regression/score_replay.tscn`.

**Implication for leaderboards:** a server cannot re-simulate a client's physics bit-exactly. Validation should rely on plausibility bounds per score term, not exact replay.

## 6. Research Data economy (`tools/economy/simulate_research_data.py`)

The model covers 100 missions, 3 optional objectives each, 6 planned weapons × 4 attributes × 3 levels (72 levels), and three profiles. "Affordable" = RD earned ÷ cost of every upgrade available so far.

| Scheme | Casual (ch1→ch5) | Typical | Completionist |
|---|---|---|---|
| Current 30/60/100 flat (4,560 RD total) | 41% → 69% | 52% → 87% | 62% → 100% by **ch4** |
| B: 25/50/90, +50% per later unlock chapter, rewards +25% per chapter (7,260 RD) | 47% → 65% | 60% → 82% | 72% → 98% |
| C: 20/40/70 flat (3,120 RD) | 60% → 100% | 100% by ch2 | 100% by ch2 |

**Finding:** current prices are reasonable overall. But with flat prices and rewards that accumulate, later weapons become trivially cheap: a completionist maxes everything by chapter 4, and new weapons get fully upgraded on unlock, so upgrade choices stop mattering.

**Proposal:** scheme B, or similar chapter-scaled prices and rewards, keeping affordability steady at roughly 65% (casual) / 80% (typical) / ~100% (completionist). Final numbers to be set once real per-mission rewards exist; the tool reads the live data files.

## 7. Audio integration (with the asset agent)

**Finding:** the asset agent (`assets` branch) stages audio in `generated_assets/audio/` with per-clip licence records in `asset_manifest.json`. It has no music or voice synthesis of its own. It leaves `gameplay_bed.ogg` alone.

**Proposal (no new audio system):**
- **Sound effects:** extend `AudioService` with a data map, `data/audio.json`, from sound id to Ogg variants. Example ids: `kinetic_fire`, `breach_launch`, `breach_detonate`, `impact_metal` / `glass` / `electronic`, `component_destroyed`, `core_destroyed`, `reload_ready`, `mission_success` / `fail`. The existing procedural sounds stay as the fallback when a file is missing.
- **Music:** add `MusicDirector` cue ids (`menu`, `helix_gameplay`, `cinematic`) with per-cue volume and loop overlap.
- **Material-aware impacts:** `MissionWorld.impact_happened` gains the component id, so impact sounds can follow the material.
- **Hand-off:** the asset agent delivers files plus manifest entries on `assets`. The coding agent copies only owner-approved files into `assets/audio/` on `main`. Nothing from `assets` is merged into `main` without explicit approval.

## Next steps once approved

1. Implement save v4 (item 1).
2. Apply the Helix "Proposal" tuning and enable occlusion + load-aware push (items 2 and 4); re-run the probe and the full suite.
3. Set chapter-scaled upgrade pricing (item 6).
4. Extend `AudioService` / `MusicDirector` (item 7).
5. Remaining Batch 5: physics tuning, renderer comparison on the real 3D gameplay scene, and physical Android device testing (needs a device connected over USB).
