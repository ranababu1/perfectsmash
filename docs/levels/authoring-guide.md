# Campaign level authoring guide (release one, 100 missions)

Owner: orchestrator. Applies to every mission in `data/missions/`. Written 2026-11-11 for the full
campaign build (plan revision 7). Read it completely before authoring.

## 1. Sources of truth (read these, do not reinterpret them)

| What | Where |
|---|---|
| Mission names, visual target, story breadcrumb per level | `docs/narrative-bible.md` §9 (100-level mission map) |
| Puzzle idea, skill and difficulty per level | `docs/level-design-spec.md` §4 (per-chapter tables) and its 2026-11-09 revision section, which overrides the old vocabulary |
| Five-level teaching rhythm | `docs/plan.md` §5; level-design-spec §1.6 |
| Schema | `docs/interfaces.md` §2; `scripts/core/mission_definition.gd` |
| Weapons | `data/weapons.json` (each has a `_role`); §4 below |
| Materials | `data/materials.json`; §5 below |
| Reference missions | `data/missions/helix_02..05.json` (+ `data/environments/`, `tools/levels/solutions/`) |

**Translating the old spec vocabulary.** The level-design-spec tables were written for the retired
slingshot game (wood, stone, glass, "topple below a line"). Keep each level's *puzzle idea and
skill*, expressed with the chapter's institutional components and the current rules:
wood post/plank → `lightweight_alloy` column or `composite` deck; stone block/cap → `concrete`
cap/slab or `reinforced_steel` wall; glass → `glass_polymer` panel/pod; "target" → the chapter's
critical asset (`destroy_critical`) or a set of components (`destroy_components`); "topple below a
line" → `structural_damage` (fraction) or `destroy_components` of the upper structure. Domino rows
and chain reactions use real supports and, from Nova Grid on, `energy_component` cells whose
destruction triggers a secondary blast. Shot counts in the old tables are a guide only (the
revision allows longer multi-stage missions where every shot is a readable decision).

## 2. Files per mission (all four are required)

1. `data/missions/<id>.json` — the facility. `id` = file name; `chapter` = 1-5.
2. `data/environments/<id>.json` — set dressing (presentation only, no collision), using **only**
   the chapter's kit ids (`HLX-`, `VTA-`, `NVG-`, `CVT-`, `MRD-` ENV/PRP pieces listed in
   `data/integrated_assets.json`). Copy the structure of `data/environments/helix_02.json`:
   floor rows, back walls, massing, props. Keep the gameplay band |z| ≤ 0.8 clear. Vary prop choice
   and placement between levels so consecutive missions do not look identical; use the chapter's
   signature props (VITA bioreactor bank / growth chamber / cleanroom airlock / archive vault, Nova
   Grid reactor ring / intake turbine / transformer yard / cooling tower, Civitas prediction room /
   relay spire / screen wall / sensor tower, Meridian convergence chamber / temporal anchor /
   foundation pillars / hybrid stack).
3. `tools/levels/solutions/<id>.json` — an array of solutions `[{name, steps}]`. **The first is the
   intended efficient line and must win within `recommended_shots`.** Add a second, different line
   where the puzzle has one (a player's alternative). Step format: `tools/levels/mission_solver.gd`
   header (`{"weapon", "target"}`, Breach `{"weapon": "breach_charge", "point": [x, y]}`, piercing
   weapons may add `"through": [ids]`). Steps whose target is already destroyed are skipped, so
   fallback steps are allowed after the intended ones.
4. A row in `docs/levels/<theme>.md` (level, name, puzzle idea, weapons, recommended shots, intended
   line, probe result).

## 3. Mission file rules

- Coordinates in px, y down; `ground_y` 640; `width` 1500-2000; operative at x 140-220 on the
  ground. Components are boxes `x, y` (centre), `w, h`; a component resting on the ground has
  `y = ground_y - h/2`. A component resting on another lists it in `supports`; the stand check
  fails if anything moves in 3 s untouched, so stack precisely (top of support = bottom of piece).
  `min_supports` (optional) = how many supports may remain before it falls.
- **Kinds** must exist in the chapter kit (table §6) and each axis must be within the kind's
  `scale_range` of one of its reference sizes (±10%) — `tests/levels/test_campaign_missions.gd`
  checks this. Use the kit's material for a kind unless the puzzle needs otherwise (e.g. a `phase_shield`
  of `temporal_crystal` in Meridian).
- `critical_asset: true` on the chapter's core (`ai_core`, `gene_vault_core`, `reactor_core`,
  `surveillance_core`, `convergence_core`), always with a `destroy_critical` objective. Use
  `health_scale` (0.5-4) to tune a single piece; prefer geometry over health inflation.
- Objectives: exactly one or two mandatory goals; one or two optional goals that reward a
  different, readable action (cut a relay, save a shot, destroy every rack); usually one `max_shots`
  constraint as an optional efficiency goal (limit ≈ recommended + 1 or 2). Labels are short
  imperatives ("Destroy the gene vault core"). Mandatory `protect` constraints only where the story
  calls for it (e.g. "Do not breach the cryo cells").
- `recommended_shots` = shots of the intended line. Ammunition per weapon: enough for the intended
  line plus a fair margin (total ≈ 1.5-2× recommended, Breach and Lance kept scarce). Never make a
  level depend on an upgrade.
- `target_time` (s): ≈ 20 + 10 × recommended shots, +15 for finales. It is a human estimate; the
  probe's times exclude aiming.
- `rewards`: completion_points 1000 + 100 × (chapter − 1) (+500 on levels 10 and 20 of a chapter);
  completion_research_data 20 / 25 / 30 / 35 / 40 by chapter (+50% on chapter finales);
  optional_research_data 5 / 6 / 7 / 8 / 9.
- `name` = the narrative-bible mission name; `briefing` = one or two sentences drawn from the
  breadcrumb, in the bible's tone (§2: restrained, factual, no jokes). Briefings may hint at the
  weak point but never give a launch vector.

## 4. Weapons by chapter (unlock at the chapter start)

| Chapter | New weapon | Role (data/weapons.json `_role`) | Puzzle uses |
|---|---|---|---|
| I Helix | Kinetic Accelerator, Breach Charge | direct impact; lobbed area charge | supports, weak points, lobs over walls |
| II VITA | **Penetrator** | high armour penetration; passes through up to 2 components it destroys or light ones (impact resistance ≤ 0.2: glass, electronics, alloy, energy) | targets behind glass, lines of specimen racks, sealed vaults |
| III Nova Grid | **Pulse Cannon** | near-flat bolt + small discharge; ×3 vs energy components, ×1.6 electronics, ×0.5 concrete | overload capacitor chains, secondary-blast cascades |
| IV Civitas | **Disruptor** | wide EMP (radius 170) that ignores cover and pushes nothing; ×5 electronics, ×2.5 cores, ×0.1 structure | shield emitters (`shielded_by`) and racks behind walls |
| V Meridian | **Temporal Lance** | straight, passes through 3 components; the only weapon that damages `temporal_crystal` | crystal anchors / stabiliser lattices, lines of shields |

A mission lists only the weapons its puzzle wants (any unlocked ones). Introduce the new weapon in
levels 1-3 of its chapter with a clean, readable situation, then combine it with earlier weapons.
Chapter V finales combine everything.

**Shields (Civitas, Meridian).** `"shielded_by": ["emitter_id", ...]` makes a component immune to
all damage while any listed emitter stands. Emitters should be visible (`sensor_array`,
`quantum_stabilizer`, `timeline_relay` ...) and reachable; the Disruptor is the efficient answer
(through walls) but a direct line must also be possible unless the level teaches the Disruptor.

## 5. Materials (data/materials.json)

lightweight_alloy (light, weak), composite (decks), reinforced_steel (very tough, blocks blasts),
concrete (blast-resistant, chips under impact), glass_polymer (fragile), electronic_module (soft),
ai_core_module (soft to weapons, survives falls), energy_component (soft; destroyed → secondary
blast 70 dmg / 110 px), temporal_crystal (immune to everything but the Temporal Lance).
Blasts are occluded by components between the blast and a target (steel and concrete block most).

**Flight (2026-11-11).** Projectiles have no air drag: real flight follows the aim preview's
ballistic arc exactly (an earlier default damping made lobs land 25-50 px short). The Breach Charge
(950 px/s, full gravity) reaches roughly 900 px horizontally from the muzzle at most, so lob targets
should sit within x ≈ 1100 for an operative at x 180. `health_scale` must stay within 0.5-4.

## 6. Chapter kits (component kind → material, reference sizes px)

Generated from `data/integrated_assets.json` on 2026-11-11; `scale_range` 0.8-1.25 unless noted.

- **helix**: ai_core (ai_core_module 60×60, 0.85-1.25, critical), blast_wall (steel 30×90, 30×140, 40×200; 0.8-1.3), control_pod_glass (glass 60×80), cooling_stack (composite 40×120), core_shield (steel 16×80; 0.8-1.6), data_crate (composite 50×50), logistics_gantry (alloy 120×100; 0.75-1.3), power_cell (energy 36×40), relay_dish (glass 70×24), relay_mast (alloy 22×140, 22×220), server_rack (electronic 40×40, 40×100, 50×160; up to 1.5), service_deck (composite 120×24, 200×24, 320×24; 0.75-1.3), support_column (alloy 26×100, 26×160, 30×240; 0.7-1.3).
- **vita**: gene_vault_core (ai_core_module 70×110, critical), bioreactor (glass 50×100, 60×140), cleanroom_panel (glass 14×90, 60×120, 100×80), containment_cap (concrete 80×40, 120×30), cryo_cell (energy 36×50), lab_column (alloy 26×100, 26×160, 30×240), lab_deck (composite 120×24, 200×24, 320×24), specimen_rack (electronic 40×100, 50×140).
- **nova_grid**: reactor_core (energy 80×120, critical), cable_bridge (composite 160×24, 240×30), capacitor_cell (energy 40×60), containment_ring_segment (steel 120×50), containment_wall (concrete 40×160, 60×120), cooling_tower_segment (concrete 80×120, 120×80), grid_pylon (steel 40×200, 50×260), transformer (electronic 60×80, 80×100).
- **civitas**: surveillance_core (ai_core_module 70×110, critical), civic_column (concrete 30×120, 40×200, 40×280), civic_screen (glass 60×100, 120×70), data_exchange_rack (electronic 40×120, 50×90), relay_bridge (composite 160×24, 240×24), security_wall (steel 30×140, 40×200), sensor_array (glass 60×40, 90×60), sensor_mast (alloy 22×160, 22×240).
- **meridian**: convergence_core (energy 80×120, critical), anchor_column (steel 30×160, 40×260), convergence_deck (composite 200×24, 320×30), monolith_slab (concrete 60×160, 140×40), phase_shield (glass 20×120, 80×120), quantum_stabilizer (electronic 50×80), temporal_cell (energy 36×50), timeline_relay (alloy 24×200).

Nova Grid `reactor_core` and Meridian `convergence_core` use the material **`reactor_housing`**
(added 2026-11-11 after the first Nova Grid pass: as plain `energy_component` the cores died to one
Pulse shot or any falling deck, which flattened the difficulty curve). It has 260 health, survives
falls (structural resistance 0.6), takes ×1.6 from the Pulse Cannon and ×1.5 from the Disruptor, and
sets off a large secondary blast (110 damage, 150 px) when destroyed. Use plain `energy_component`
for capacitor / cryo / temporal cells and power cells.
Any kind may carry another material when the puzzle needs it (e.g. Meridian `phase_shield` or
`temporal_cell` as `temporal_crystal`), keeping the kind's size rules.

## 7. Workflow and gates (every level)

```
godot_console --headless --fixed-fps 60 -s tools/levels/probe_missions.gd -- scout <id>    # lines of fire / lobs
godot_console --headless --fixed-fps 60 -s tools/levels/probe_missions.gd -- solve <id> 3  # stand check + 3 replays
CAMPAIGN_FILTER=<theme> godot_console --headless --fixed-fps 60 -s tests/run_tests.gd -- --only campaign_missions
```

A level is done when: the data validates; the stand check passes; every recorded solution wins at
least 2 of 3 replays and the intended one 3 of 3 within `recommended_shots`; the campaign-missions
gate passes; the puzzle matches its spec row's idea and skill; the objective reads in three seconds
(the critical asset or targets are visible from the operative's side, not hidden behind decoration);
no solution depends on a frame-perfect collision (if a line only works with one exact aim, change
the geometry). Then add the docs row.

Difficulty within a chapter: levels 1-5 establish (1-3 shots), 6-10 combine (2-4), 11-15 deepen
(3-5), 16-19 mastery (3-6), 20 finale (4-8, the chapter's largest facility, all its weapons).
Later chapters start slightly above the previous chapter's middle, never above its finale.
