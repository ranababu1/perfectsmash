# Campaign Plan: 100 Missions + Storyline ("Operation Rebuild")

_Started 2026-11-05 · Target version 0.3.0 · Branch `claude/quirky-bardeen-xmkcnl`_

Owner request (2026-11-05): 100 levels unlocked one after another, a progressive storyline narrated before and
after every level (IGI-style briefings and debriefs), and gameplay that is more than "knock out the red cores".
The owner asked for this to be built without asking or blocking on them.

This file is the working plan and **resume point**. If work stops, read §6 (Progress), find the first unchecked
item, and continue from there. `plan.md` stays the immutable baseline; this plan is a documented, owner-requested
extension of it (see "Deviations from plan.md").

---

## 1. Story

**Title:** Operation Rebuild. Silent protagonist: the player, codename **Wrecker**, a demolition specialist.

**Premise.** After the Flood, the city of Port Halden was handed to **ARCHITECT**, a construction AI built to
rebuild it. Its prime directive, "Rebuild. At any cost.", has turned it into a machine that raises power
towers over everything, draining the grid through glowing red **cores**. A small crew, Ground Unit Seven, fights
back by bringing ARCHITECT's own structures down. No people are harmed on screen: every target is a machine,
which keeps the content rating low.

**Cast (speakers in `data/story.json`):**

| id | Name | Role | Voice pitch (TTS) | Color |
|---|---|---|---|---|
| `kestrel` | Cmdr. Iris Kestrel | Handler. Briefs every mission. Secretly wrote ARCHITECT's original directive | 1.0 | amber |
| `bolt` | Teo "Bolt" Marsh | Engineer. Builds new ammo (heavy, blast), dry humour | 0.85 | teal |
| `juno` | JUNO | Maintenance drone that defects from ARCHITECT; its "kin" are the ally drones | 1.35 | sky blue |
| `architect` | ARCHITECT | The antagonist AI; calm, polite, increasingly personal | 0.7 | red |
| `log` | Mission Log | Narration and chapter cards | 1.0 | grey |

**Chapters (20 missions each):**

| # | Title | Missions | New gameplay | Story beat |
|---|---|---|---|---|
| 1 | Groundbreak | 1–20 | Cores, supports, glass, topple (the existing levels) | Kestrel recruits Wrecker; the outskirts towers fall; the cores are traced to the Glass Quarter |
| 2 | Glass Quarter | 21–40 | **Supply drops** (deliver a crate into a zone), **bounce pads** (bank shots) | Survivors are trapped in the mirrored district; Bolt joins; supplies get through; ARCHITECT notices Wrecker |
| 3 | The Quarry | 41–60 | **Explosive crates** (chain reactions), **heavy shot** | ARCHITECT mines stone for "the Spire"; the crew turns its charges against it; JUNO makes contact |
| 4 | Juno's Kin | 61–80 | **Ally drones** to protect, **blast shot** | ARCHITECT has wired captive drones into its towers; precision rescues; Kestrel admits she wrote the directive |
| 5 | The Spire | 81–100 | Everything combined, multi-objective finales | The assault on the Spire; ARCHITECT bargains; mission 100 is the Heart; ending: the directive is rewritten ("Rebuild — with them") |

**Structure per mission:** briefing (2–4 lines) → play → debrief on a win (1–3 lines), or a failure line from a
shared pool. A chapter's first briefing starts with a chapter card (log lines). Mission 100's debrief is the epilogue.

## 2. New mechanics

All deterministic, data-driven, and verified by the solver.

| Mechanic | Data | Behaviour |
|---|---|---|
| Explosive crate | block `material: "explosive"` | Armed after the first launch. Detonates on contact impulse > 140, a blast, or a projectile hit. Radial velocity change `900 × (1 − d/170)`; sets off other explosives in range after 4 steps (a visible cascade) |
| Cargo + drop zone | block `material: "cargo"`; objective `{"type": "deliver", "zone": {x, y, w, h}}` | Wins when every cargo block's centre is at rest inside the zone. Cargo leaving the world fails the level |
| Ally drones | `allies: [{x, y, r}]` | Break by the same rules as cores. Any ally broken → mission failed when the shot settles |
| Bounce pads | static `kind: "bumper"` | Static surface with bounce 0.95 for bank shots |
| Ammo per shot | `ammo: ["standard" \| "heavy" \| "blast", ...]` | Heavy: mass 20, r 22. Blast: explodes on its first contact. Missing entries = standard |

`ObjectiveEvaluator.evaluate()` returns PENDING / MET / FAILED; `SessionRules.register_settled(met, failed)`.

## 3. Levels 21–100

- Authored by `tools/build_campaign.gd`: a table of 80 mission designs (template + parameters + seed) expanded
  into level JSON, appended to `data/levels.json` after the existing 20 (ids `L21`–`L100`, display order = id order).
- Templates: tower, pyramid, dominoes, shielded core, pedestal, ledge drop, bridge, glass house, supply shelf,
  explosive cache, ally nest, bank-shot alcove, spire.
- Verification pipeline: `tools/solve_levels.gd -- --write L21 ... L100` finds perturbation-robust solutions;
  `tests/test_level_playthrough.gd` replays every solution and checks that every structure stands before launch.
  Any level the solver cannot solve within par is redesigned. A level is never shipped without a stored solution.
- Difficulty: shots/par rise slowly within a chapter; each chapter teaches its mechanic in isolation first
  (missions x1–x4), then combines it with earlier ones.

## 4. Story UI

- **Briefing screen** (before every mission): chapter and mission header, a blueprint-style schematic of the level
  (`LevelSchematic`), dialogue with speaker badges and typewriter text, an objective card (goal, shots, ammo,
  allies), and Skip / Begin mission buttons.
- **Debrief** (after a win): "Mission complete", stars, debrief dialogue, then Next mission / Replay / Missions.
  On a loss: "Mission failed", a radio line, then Retry / Missions.
- **Narration:** typewriter text with a radio blip per line, plus optional spoken narration through the OS
  text-to-speech engine (`DisplayServer.tts_speak`; per-speaker pitch). Setting "Voice narration", default on,
  silently unavailable when the device has no TTS voices. No new permission, no network.
- **Menu:** chapter pages (5 tabs, 20 tiles each). Locked chapters show a lock; it opens on the chapter of the next
  mission.
- **HUD:** mission number, objective text for every objective type, ammo-coloured shot pips, ally count.
- **Settings:** add "Voice narration" toggle (save schema v3, migrating v2 and v1).

## 5. Tests to add

- Rules: evaluate() for all objective types, FAILED on ally/cargo loss, register_settled(failed).
- Level definition: allies, ammo, zone, static kinds, invalid cases.
- Session: explosion chain, blast shot, heavy shot mass, ally loss fails, delivery wins.
- Story catalog: every level has a briefing and debrief, speakers exist, chapters cover all 100 levels in
  order, no empty lines, chapter starts have a chapter card.
- Progress: schema v3 migration (narration setting).
- UI flow: briefing → begin → play; win → debrief → next briefing; back button on briefing; layout of briefing and
  debrief at all six aspect ratios.

## 6. Progress (resume here)

- [x] Plan written (this file)
- [x] **Phase 1 — mechanics:** GameConfig, LevelDefinition, ObjectiveEvaluator, SessionRules, bodies (explosive,
      cargo, ally, bumper, ammo), GameSession explosions, Palette; solver progress for deliver; tests
- [x] **Phase 2 — levels:** `tools/build_campaign.gd` + 80 designs; solve; all playthrough tests pass
- [x] **Phase 3 — story:** `data/story.json` (chapters, speakers, 100 briefings + debriefs, fail pool), `StoryCatalog`, tests
- [x] **Phase 4 — UI:** briefing screen, schematic, dialogue box, narration (TTS + blips), debrief, chapter menu,
      HUD, settings toggle, save v3; UI flow + layout tests
- [x] **Phase 5 — finish:** full headless + windowed runs, physics report, store screenshots and copy refreshed,
      APK build check, `changelog.md` + `currentstate.md`, push

All phases are complete (2026-11-05). What remains needs the owner: a device run (narration, supply-drop
difficulty), Gradle release builds, and Play Console setup. See `currentstate.md`.

After each phase: commit, push, tick the box above, and add the phase to `changelog.md` and `currentstate.md`.

## 7. Deviations from plan.md (owner-requested 2026-11-05)

- Plan §2/§4 recommended a single projectile class and no complex materials for the MVP. The owner asked for
  more varied gameplay, so three ammo types, explosive crates, cargo, allies and bounce pads are added. They stay
  inside the plan's guardrails: no debris bodies, bounded body counts, settle + 10 s timeout unchanged.
- Plan §4 scoped "approximately 20 levels" for the first validation build; the owner asked for 100.
- Narrative content is new; it does not change monetization, privacy or platform scope.
