# Chapter III - Nova Grid, "The Energy Beneath" (levels 41-60)

Missions `nova_grid_01` .. `nova_grid_20` (campaign levels 41-60). Industrial energy basin: reactor rings,
cooling towers, transformer yards, cable bridges and capacitor banks; the core is the `reactor_core`
(an energy component: destroying it sets off a secondary blast, so neighbouring capacitors and
transformers chain).

- **Weapons:** Pulse Cannon (new, introduced in 41-43: near-flat bolt, x3 vs energy components, x1.6 electronics,
  x0.5 concrete, x0.6 steel), plus Kinetic Accelerator, Breach Charge and Penetrator where the puzzle wants them.
- **Curve:** 41-45 establish (1-3 shots), 46-50 combine (2-4), 51-55 deepen (3-5), 56-59 mastery (3-6), 60 finale (4-8).
- **Reading the tables:** probe = `probe_missions.gd solve <id> 3` wins/3 and shots of the intended line (first
  solution).

| Lvl | Mission | Puzzle idea | Weapons (ammo) | Rec. shots | Intended line | Probe |
|---:|---|---|---|---:|---|---|
| 41 | Endless Power | Reactor core on one exposed pylon; teaches the Pulse Cannon on an energy component. | Pulse 6 | 3 | Pulse the core twice (hs 5). | 3/3, 3 shots |
| 42 | The Intake | Core on a deck over a soft transformer sump and a steel pylon; low-angle shot drops the deck. | Pulse 8, Kinetic 6 | 2 | Pulse the sump transformer, then the fallen core. Alt: straight at the core (4 shots). | 3/3, 2 shots |
| 43 | Containment Ring | Four steel ring segments on three capacitor-topped supports above a hidden core; remove the front support. | Pulse 8, Kinetic 6, Breach 1 | 3 | Pulse the front support (ring_s1), then the exposed core. | 3/3, 3 shots |
| 44 | Cooling the Future | Two tall cooling stacks; the near pump cell is the soft point that drops the stack and opens the line to the far core. | Pulse 8, Kinetic 6, Breach 1 | 3 | Pulse the near pump cell, then the far core. | 3/3, 3 shots |
| 45 | The First Pulse | Core and capacitor stack behind a static wall (lob over it) plus an elevated uplink transformer that a flat pulse sees over the wall. | Pulse 6, Kinetic 4, Breach 3 | 2 | Pulse the uplink transformer, Breach lob onto the capacitor stack to blow the core. | 3/3, 2 shots |
| 46 | Load Balancing | Long beam on a soft transformer stack and a steel pylon, core beneath; strike the weak side. | Pulse 8, Kinetic 6, Breach 1 | 3 | Pulse the lower transformer, then the crushed core twice. Alt: Breach lob on the beam, then pulses. | 3/3, 3 shots |
| 47 | Deep Storage | Three layers of concrete storage racks on two capacitor-topped piers over the core; side hit drops the stack. | Pulse 8, Kinetic 6, Breach 1 | 2 | Pulse the near pier, then the core twice. | 3/3, 2 shots |
| 48 | Silent Alarm | Alarm panel and core on a span between a soft tower and a steel pylon, plus a far panel on a tall mast hidden by the span. | Pulse 8, Kinetic 6, Breach 1 | 3 | Pulse the tower base (span drops), finish the core, then the far panel. | 3/3, 3 shots |
| 49 | Overload Window | Static bulkhead with one slot at muzzle height; a capacitor row behind it chains to the core. | Pulse 8, Kinetic 4, Breach 1 | 3 | Pulse the first capacitor through the slot, then the core. | 3/3, 3 shots |
| 50 | The Resonance | Milestone set piece: soft pier, joined cable halves with primed cells, and a bunkered core; strip the platform, open the bunker door, finish the core. | Pulse 10, Kinetic 6, Breach 2 | 4 | Pulse the pier (ring falls), shoot the bunker door, finish the core with pulses. | 3/3, 4 shots |
| 51 | Beyond the Grid | Relay core high on a mast past a static retaining wall; flat bolts see over it, the ground array behind it needs a Breach lob. | Pulse 8, Kinetic 6, Breach 2 | 3 | Breach lob onto the ground array, pulse the core. | 3/3, 3 shots |
| 52 | The Wrong Frequency | Near dish perch blocks the line to the far core perch; silence the dish to open the lane. | Pulse 8, Kinetic 6 | 3 | Pulse the dish, then the core twice. | 3/3, 3 shots |
| 53 | The Deep Core | Heavy cap bar over the core with one soft keystone support, a steel rear post, and two decoy capacitors. | Pulse 8, Kinetic 6, Breach 2 | 3 | Pulse the keystone cell, then the core twice. | 3/3, 3 shots |
| 54 | Blackout Protocol | An entry capacitor bank hides the primed bank that carries a long beam over the core; trip them in order. | Pulse 8, Kinetic 6, Breach 1 | 3 | Pulse the entry bank, then the main bank (beam falls), then the core. | 3/3, 3 shots |
| 55 | The Echo | Two tiers of primed capacitor rows: the lower row's blast brings down the pedestal that carries the upper row onto the core. | Pulse 8, Kinetic 6, Breach 1 | 4 | Pulse the first low cell, clear the pedestal transformer, then the core. | 3/3, 4 shots |
| 56 | Dead Circuit | Heavy canopy over the core hidden behind the near pier; pop the pier cell and the canopy crushes the core. | Pulse 8, Kinetic 6, Breach 2 | 3 | Pulse the near pier cell, then the core. | 3/3, 3 shots |
| 57 | Origin Unknown | Core in a concrete well open only from above, plus a high uplink; lob over the front wall. | Pulse 6, Kinetic 6, Breach 4 | 4 | Breach lob over the wall, pulse the uplink, finish with lobs. | 3/3, 4 shots |
| 58 | The Listening Machine | Receiving frame on primed capacitor piers folds inward; two listening relays in file must be silenced first. | Pulse 8, Kinetic 6, Breach 1, Penetrator 3 | 4 | Pulse both relays, the near pier cell, then the core. | 3/3, 4 shots |
| 59 | Final Containment | Near relay, core and far relay in file along a wide structure; the core's blast helps the far relay. | Pulse 8, Kinetic 6, Breach 1, Penetrator 3 | 4 | Pulse near relay, core, far relay. | 3/3, 4 shots |
| 60 | The Energy Beneath | Finale and largest facility (2200 px): three relays in file, a soft pier under a broad platform carrying a steel upper ring and primed cells, a bunkered core, and a far relay on the platform. | Pulse 12, Kinetic 8, Breach 2, Penetrator 4 | 7 | Pulse the three relays, the pier (staged collapse of platform and ring), the bunker door, the core, then the far relay. | 3/3, 7 shots |

## Notes

- Cores are `reactor_housing` (260 hp, survives falls, secondary blast 110 / 150 px) at default health scale; no
  `health_scale` above 1 is used anywhere. A collapse alone cannot finish a critical asset (it is left at 1 hp), so
  every line ends with a weapon hit or blast on the core.
- Difficulty comes from structure: sequenced soft blockers and relays in file, collapses onto bunkered cores
  (soft door cell, concrete back wall, composite roof), primed capacitor chains (health scale 0.5-0.6 cells) that must
  be triggered in order, static barriers that need a lob or a high flat shot, and one-slot bulkheads.
- Curve: 41-45 = 3,2,3,3,2; 46-50 = 3,2,3,3,4 (50 is the milestone set piece); 51-55 = 3,3,3,3,4;
  56-59 = 3,4,4,4; 60 = 7 (largest facility, staged collapse: relays, pier, platform and upper ring, bunker, core).
- Lobs against barriers (45, 57) use Breach on targets or plane points; Breach reach is about 900 px from the muzzle.
