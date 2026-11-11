# Chapter III - Nova Grid, "The Energy Beneath" (levels 41-60)

Missions `nova_grid_01` .. `nova_grid_20` (campaign levels 41-60). Industrial energy basin: reactor rings,
cooling towers, transformer yards, cable bridges and capacitor banks; the core is the `reactor_core`
(an energy component: destroying it sets off a secondary blast, so neighbouring capacitors and
transformers chain).

- **Weapons:** Pulse Cannon (new, introduced in 41-43: near-flat bolt, x3 vs energy components, x1.6 electronics,
  x0.5 concrete, x0.6 steel), plus Kinetic Accelerator, Breach Charge and Penetrator where the puzzle wants them.
- **Curve:** 41-45 establish (2-3 shots), 46-50 combine (2-4), 51-55 deepen (3-5), 56-59 mastery (3-6), 60 finale (4-8).
- **Reading the tables:** probe = `probe_missions.gd solve <id> 3` wins/3 and shots of the intended line (first
  solution). Lobs are recorded as plane points that clear barriers with a safety margin, because the live charge
  sags below the preview arc by about 25-50 px over a long flight.

| Lvl | Mission | Puzzle idea | Weapons (ammo) | Rec. shots | Intended line | Probe |
|---:|---|---|---|---:|---|---|
| 41 | Endless Power | Reactor core on one exposed pylon; teaches the Pulse Cannon on an energy component. | Pulse 6 | 2 | Pulse the core twice (hs 5). | 3/3, 2 shots |
| 42 | The Intake | Core on a deck over a soft transformer sump and a steel pylon; low-angle shot drops the deck. | Pulse 8, Kinetic 6 | 1 | Pulse the sump transformer, then the fallen core. Alt: straight at the core (4 shots). | 3/3, 1 shots |
| 43 | Containment Ring | Four steel ring segments on three capacitor-topped supports above a hidden core; remove the front support. | Pulse 8, Kinetic 6, Breach 1 | 2 | Pulse the front support (ring_s1), then the exposed core. | 3/3, 2 shots |
| 44 | Cooling the Future | Two tall cooling stacks; the near pump cell is the soft point that drops the stack and opens the line to the far core. | Pulse 8, Kinetic 6, Breach 1 | 2 | Pulse the near pump cell, then the far core. | 3/3, 2 shots |
| 45 | The First Pulse | Core behind a static barrier (lob over it) and an elevated uplink transformer that a flat pulse can see over it. | Pulse 6, Kinetic 4, Breach 3 | 2 | Breach lob over the wall onto the capacitor-stack core, pulse the uplink transformer. | 3/3, 2 shots |
| 46 | Load Balancing | Long beam on a soft transformer stack and a steel pylon, core beneath; strike the weak side. | Pulse 8, Kinetic 6, Breach 1 | 2 | Pulse the lower transformer, then the crushed core twice. Alt: Breach lob on the beam, then pulses. | 3/3, 2 shots |
| 47 | Deep Storage | Three layers of concrete storage racks on two capacitor-topped piers over the core; side hit drops the stack. | Pulse 8, Kinetic 6, Breach 1 | 1 | Pulse the near pier, then the core twice. | 3/3, 1 shots |
| 48 | Silent Alarm | Alarm panel and core on a span between a soft three-part tower and a steel pylon; remove the tower, the span goes. | Pulse 8, Kinetic 6, Breach 1 | 1 | Pulse the bottom transformer of the tower, then the core. | 3/3, 1 shots |
| 49 | Overload Window | Static bulkhead with one slot at muzzle height; a capacitor row behind it chains to the core. | Pulse 8, Kinetic 4, Breach 1 | 2 | Pulse the first capacitor through the slot, then the core. | 3/3, 2 shots |
| 50 | The Resonance | Set piece: two cable halves joined over the core with four capacitor loads, one soft pier; the whole ring drops. | Pulse 8, Kinetic 6, Breach 2 | 1 | Pulse the soft pier, then the core twice. Alt: Breach lob onto the ring first (6 shots). | 3/3, 1 shots |
| 51 | Beyond the Grid | Relay core high on a mast past a static retaining wall; flat bolts see over it, low targets do not. | Pulse 8, Kinetic 6, Breach 2 | 1 | Pulse the core three times over the wall (optional: Breach lob onto the ground array). Alt: cell first, 4 shots. | 3/3, 1 shots |
| 52 | The Wrong Frequency | Near dish perch blocks the line to the far core perch; silence the dish to open the lane. | Pulse 8, Kinetic 6 | 2 | Pulse the dish, then the core twice. | 3/3, 2 shots |
| 53 | The Deep Core | Heavy cap bar over the core with one soft keystone support, a steel rear post, and two decoy capacitors. | Pulse 8, Kinetic 6, Breach 2 | 2 | Pulse the keystone cell, then the core twice. | 3/3, 2 shots |
| 54 | Blackout Protocol | A four-cell primed capacitor bank carries one end of a long beam over the core; one pulse trips the whole bank. | Pulse 8, Kinetic 6, Breach 1 | 1 | Pulse the bottom bank cell, then the core twice. | 3/3, 1 shots |
| 55 | The Echo | Two tiers of primed capacitor rows: the lower row's blast brings down the pedestal that carries the upper row onto the core. | Pulse 8, Kinetic 6, Breach 1 | 3 | Pulse the first low cell, clear the pedestal transformer, then the core. | 3/3, 3 shots |
| 56 | Dead Circuit | Heavy canopy over the core hidden behind the near pier; pop the pier cell and the canopy crushes the core. | Pulse 8, Kinetic 6, Breach 2 | 2 | Pulse the near pier cell, then the core. | 3/3, 2 shots |
| 57 | Origin Unknown | Core in a concrete well, open only from above: lob a charge over the front wall. Alt: Kinetic through the wall. | Pulse 6, Kinetic 6, Breach 3 | 2 | Breach lob over the front wall (plane point above it), twice. | 3/3, 2 shots; alt 5-6 shots |
| 58 | The Listening Machine | Receiving frame on two primed capacitor piers folds inward onto the core. | Pulse 8, Kinetic 6, Breach 1, Penetrator 3 | 2 | Pulse the near pier cell, then the core. | 3/3, 2 shots |
| 59 | Final Containment | Near relay, core and far relay in file along a wide structure; the core's blast helps the far relay. | Pulse 8, Kinetic 6, Breach 1, Penetrator 3 | 3 | Pulse near relay, core, far relay. | 3/3, 3 shots |
| 60 | The Energy Beneath | Finale: three signal relays in file, then a soft pier under a broad platform with an upper ring of steel and primed cells over the hidden core; the staged collapse reveals and crushes the core, the right relay falls with the platform. | Pulse 10, Kinetic 8, Breach 2, Penetrator 4 | 4 | Pulse relays l, m, n, then the pier. Alt: Penetrator through the pier. | 3/3, 4 shots; alt 3/3 4 shots |

## Notes and known limits

- **Health scale.** All `health_scale` values are within the guide's 0.5-4 range. Pulse Cannon x3 against energy
  components means a core at scale 4 usually dies to one or two pulses, and falling steel, concrete or composite
  decks destroy a core outright. Shot counts therefore come from access (sequenced soft blockers, collapses,
  barriers, lobs) and mandatory relays, not from health inflation.
- **Difficulty curve is below the target range in places.** Levels 42, 47, 48, 50, 51, 54 have a 1-shot intended
  line (a single support or primed bank brings everything down); 46 and 49-53 sit at 2. The chapter does not reach
  the 3-5 band (51-55) or 3-6 band (56-59) in its recommended counts, and the finale is 4 shots (target 4-8). Raising
  these needs either engine support for tougher cores (e.g. a damage-resistant core material) or more sequenced
  mandatory targets; recorded as an open gap rather than inflating health.
- **Lobs.** The live Breach charge sags 25-50 px below the solver's preview arc over a long flight, and the lowest
  arc that clears a barrier clips it. Barrier levels (45, 57) use plane-point steps well above the wall top.
  Breach cannot reach past roughly x = 1100 at muzzle height.
- Level 17's alternative (Kinetic through the front wall) takes 5-6 shots.
