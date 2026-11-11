# Chapter IV - Civitas, "The Quiet Cage" (levels 61-80)

Owner: level design. Missions `civitas_01` ... `civitas_20`; data in `data/missions/civitas_*.json`,
set dressing in `data/environments/civitas_*.json`, recorded solutions in
`tools/levels/solutions/civitas_*.json`. Rules: `docs/levels/authoring-guide.md`.

**Weapons.** Kinetic Accelerator and Breach Charge (Chapter I), Penetrator (II), Pulse Cannon (III)
and the chapter's new **Disruptor**: a slow arcing canister whose EMP (radius 170) ignores cover,
pushes nothing, deals x5 to electronics, x2.5 to cores, x2 to energy cells and x0.1 to structure.
Levels 1-3 introduce it (a wall the EMP crosses; a shield emitter behind a wall). The chapter's
signature rule is `shielded_by`: a component takes no damage while any listed emitter stands.
Shield emitters are `sensor_array` pieces made of `electronic_module` (so the EMP burns them out).

**Probe note.** Direct weapons (Disruptor included) are aimed at the component the round strikes
first. An EMP through a wall is therefore recorded as a shot at the wall (`target: wall`).
Floating-point and aim tolerance: keep kinetic targets large and within about 900 px; very small
elevated targets (60x40 at 950 px) hit the support under them in some replays.

**Curve.** 1-5 establish (2-3 shots: cover, heights, shield, glass screen, a support cascade that
strips two emitters), 6-10 combine, 11-15 deepen (3-5), 16-19 mastery (3-6), 20 finale.

| Lvl | Mission | Puzzle idea | Weapons | Rec. shots | Intended line | Probe |
|---:|---|---|---|---:|---|---|
| 61 | A Predictable World (`civitas_01`) | Core and two racks behind a steel wall; the EMP crosses the wall. | Disruptor, Kinetic | 2 | Disruptor at the wall x2 (second finishes the core) | 3/3, 2 shots |
| 62 | The Profile (`civitas_02`) | Core on the tall tower, rack on the short one; heights and one field for both. | Disruptor, Kinetic | 2 | Disruptor at the core (rack burns too), then Kinetic at the core | 3/3, 2 shots; alt (topple the tall mast) 3/3, 2 |
| 63 | The Forecast (`civitas_03`) | Shield emitter hidden behind a steel wall, core elevated and shielded. | Disruptor, Kinetic | 2 | Disruptor at the wall (burns the emitter), Kinetic at the core | 3/3, 2 shots |
| 64 | Access Denied (`civitas_04`) | Core shielded by a column-top emitter and sealed behind a glass access screen. | Penetrator, Kinetic | 3 | Kinetic at the emitter, Penetrator through the screen x2 | 3/3, 3 shots; alt (break the screen) 3/3, 5 |
| 65 | The Invisible Rule (`civitas_05`) | Core in plain sight but shielded by two racks under a hanging span, behind the core line. | Kinetic | 3 | Kinetic at the near post x2 (span falls and crushes both emitters), Kinetic at the core | 3/3, 3 shots |
| 66 | Quiet Signals (`civitas_06`) | Three staggered signal towers shield the core; the EMP covers the near pair, the third needs a round. | Disruptor, Kinetic | 3 | Disruptor at the near array (burns the near pair), Kinetic at the far array, Kinetic at the core | 3/3, 3 shots; alt (one by one) 3/3, 4 |
| 67 | The Approved Path (`civitas_07`) | Gate, emitter, core and a second gate on one line; the Penetrator passes the glass. | Penetrator, Kinetic | 2 | Penetrator through the gate into the emitter, Penetrator at the core | 3/3, 2 shots; alt (open the gate first) 3/3, 4 |
| 68 | The Exception (`civitas_08`) | Two-tier review stack on thin masts, core on the top deck. | Kinetic | 2 | Kinetic x2 at one base mast; the stack collapses on the core | 3/3, 2 shots |
| 69 | Public Safety (`civitas_09`) | Crossbeam between two sensor towers carries both emitters over the shielded core. | Kinetic | 2 | Kinetic x2 at one tower; the beam falls and takes emitters and core | 3/3, 2 shots |
| 70 | The Mirror (`civitas_10`) | Two mirrored emitters around the core; a steel screen hides the right one. | Disruptor, Kinetic | 3 | Kinetic at the open emitter, Disruptor at the core x2 (the field crosses the screen) | 3/3, 3 shots |
| 71 | The Model Knows (`civitas_11`) | Three emitter tiers (one on a pedestal, two on a stacked tower) shield a core standing apart. | Kinetic | 4 | Kinetic at the pedestal emitter, Kinetic x2 at a base mast (the tower falls and burns out both upper tiers), Kinetic at the core | 3/3, 4 shots |
| 72 | Prewritten (`civitas_12`) | A steel wall stands between the operative and the archive; only a lob or a field reaches the emitter and core behind it. | Breach, Disruptor, Kinetic | 2 | Breach lob at the emitter on its pedestal, Breach lob at the core | 3/3, 2 shots; alt (Disruptor at the wall, Breach at the core) 3/3, 2 |
| 73 | The Shared Signature (`civitas_13`) | Three signal towers stand on one long beam; the near end post is the shared weak point. | Kinetic | 3 | Kinetic x2 at the near end post (beam, masts and arrays fall), Kinetic at the core | 3/3, 3 shots |
| 74 | The Quiet Cage (`civitas_14`) | Four racks shield the core: two in the open, two behind a wall. | Pulse Cannon, Disruptor, Kinetic | 4 | Pulse at each open rack (small discharge takes the pair), Disruptor at the wall (field takes the two behind it), Kinetic at the core | 3/3, 4 shots |
| 75 | No Unknowns (`civitas_15`) | A mixed-material hall (steel wall, rack, concrete plinth, composite decks) stands on one weak alloy foot hidden behind glass screens. | Penetrator, Kinetic | 3 | Penetrator x3 through both screens into the foot (the hall falls on the core) | 3/3, 3 shots |
| 76 | The Future File (`civitas_16`) | Vault core under a concrete slab behind a steel front wall; its single emitter rides on the slab. | Kinetic, Disruptor | 3 | Kinetic at the roof emitter, Disruptor at the wall x2 (field reaches the core) | 3/3, 3 shots |
| 77 | The Missing Year (`civitas_17`) | Two emitter towers on one window: the near mast blocks the far emitter, so it must go first. Core on a tall column. | Kinetic, Disruptor | 4 | Kinetic x2 at the near mast, Kinetic at the far emitter, Kinetic at the core | 3/3, 4 shots |
| 78 | Source Code (`civitas_18`) | Core and emitter on a narrow ledge atop a 300 px mast beyond a barrier; high shot for the seal, then the support. | Kinetic | 3 | Kinetic at the emitter, Kinetic x2 at the mast (ledge and core fall) | 3/3, 3 shots |
| 79 | The Last Forecast (`civitas_19`) | Core sealed three ways: a ground emitter behind a wall (field), two deck emitters on a hall standing on a weak foot behind glass (Penetrator), core on a column. | Disruptor, Penetrator, Kinetic | 4 | Disruptor at the wall, Penetrator x2 through the screens into the foot, Kinetic at the core | 3/3, 4 shots |
| 80 | The Quiet Cage (`civitas_20`) | Finale: wall-hidden emitter, glass-screened relay mast carrying a crossbeam with a central tower, a third emitter on the right mast, core on a tall column. | Disruptor, Penetrator, Kinetic (Breach, Pulse in the alternate line) | 6 | Disruptor at the wall, Penetrator x2 into the left mast (beam and its emitter fall), Kinetic at the right emitter, Kinetic x2 at the core | 3/3, 6 shots; alt (Breach lob replaces the field) 3/3, 6 |

## Authoring notes and open issues

- No gate is unmet: every recorded solution wins 3/3 replays and the intended lines fit `recommended_shots`.
- Falling structures kill cores (levels 2, 8, 9, 15, 18): a cascade is usually the efficient answer, so cover is
  provided by walls and shields rather than by the core's toughness.
- A support with `min_supports` equal to its support count did not drop its deck when only one of three supports
  fell (level 20 first draft); two-support decks behave as expected. Possible engine/rule question.
- Ground-hugging disruptor and lob shots land at a wall's foot; EMP reach is measured to the nearest edge, so
  emitters on tall pedestals (> about 170 px above the impact) are out of reach.
