# 100-level asset coverage matrix

Generated 2026-11-10 by `generated_assets/tools/build_coverage_matrix.py` from the merged manifest (updated 2026-11-09, 17 entries on disk). Do not edit by hand; re-run the script.

Status: `ok` available, `fb` shared fallback only, `--` missing. Group columns show available/required.
A level is **full** when every requirement is available, **fallback** when nothing is missing but shared substitutes are used.

## Summary

- Levels fully covered: **0 / 100**; covered with fallbacks: 0; with missing assets: 100.
- Requirements available: 0 / 3176 level-requirement slots.
- Game-wide requirements available: 0 / 30.

| Chapter | Full | Fallback | Missing |
|---|---:|---:|---:|
| helix | 0 | 0 | 20 |
| vita | 0 | 0 | 20 |
| nova_grid | 0 | 0 | 20 |
| civitas | 0 | 0 | 20 |
| meridian | 0 | 0 | 20 |

Layout archetype use across the campaign (variety check): chain_cell 14, arc_over_wall 13, heavy_cap 9, multi_tier 9, linked_bridge 9, ledges 7, glass_screen 6, domino_row 6, twin_towers 6, frame 6, support_bridge 5, topple_line 5, finale 5, mixed_material 5, ring 5, wide_platform 5, glass_roof 4, tall_mast 3, stack_tower 3, chain_towers 3, indirect_shield 3, exposed_target 2, pyramid 1.

## Game-wide

| Requirement | Status | Assets |
|---|---|---|
| Operative character mesh | -- |  |
| Operative animations | -- |  |
| Kinetic Accelerator weapon | -- |  |
| Breach Charge launcher | -- |  |
| Kinetic projectile | -- |  |
| Breach canister projectile | -- |  |
| HUD kit | -- |  |
| Weapon icons | -- |  |
| Objective icons | -- |  |
| Menu screens | -- |  |
| Mission result screen | -- |  |
| Progression / chapter map | -- |  |
| Topple threshold marker | -- |  |
| Game logo | -- |  |
| App icon | -- |  |
| Splash screen | -- |  |
| UI font | -- |  |
| Menu music | -- |  |
| Victory stinger | -- |  |
| Defeat stinger | -- |  |
| Ending music | -- |  |
| Kinetic fire SFX | -- |  |
| Breach launch / detonation SFX | -- |  |
| Metal impact SFX | -- |  |
| Glass break SFX | -- |  |
| Concrete break SFX | -- |  |
| Electrical / machinery SFX | -- |  |
| UI SFX | -- |  |
| Alarm SFX | -- |  |
| Opening cinematic | -- |  |

## Chapter 1: Helix Systems (The Machine That Decided), levels 1-20

| L | Name | Archetypes | Struct | Core | Mat+dmg | VFX | Env | BG | Landmark | Music | Amb | Cine | Status |
|---:|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | First Contact | exposed_target | 0/1 | -- | 0/6 | 0/7 | 0/3 | -- | -- relay_array | -- | -- | 0/3 | missing |
| 2 | The Welcome System | tall_mast | 0/2 | -- | 0/9 | 0/8 | 0/3 | -- | -- relay_array | -- | -- | n/a | missing |
| 3 | Traffic of One | support_bridge | 0/2 | -- | 0/9 | 0/8 | 0/3 | -- | -- relay_array | -- | -- | n/a | missing |
| 4 | Supply Chain | stack_tower | 0/2 | -- | 0/6 | 0/7 | 0/3 | -- | -- relay_array | -- | -- | n/a | missing |
| 5 | The Safety Layer | glass_screen | 0/3 | -- | 0/12 | 0/9 | 0/3 | -- | -- relay_array | -- | -- | n/a | missing |
| 6 | Cold Storage | chain_towers, chain_cell | 0/3 | -- | 0/9 | 0/8 | 0/3 | -- | -- logistics_crane | -- | -- | n/a | missing |
| 7 | Blind Spot | heavy_cap | 0/2 | -- | 0/9 | 0/8 | 0/3 | -- | -- logistics_crane | -- | -- | n/a | missing |
| 8 | Human Override | domino_row | 0/2 | -- | 0/9 | 0/8 | 0/3 | -- | -- logistics_crane | -- | -- | n/a | missing |
| 9 | Redundancy | topple_line | 0/3 | n/a | 0/6 | 0/6 | 0/3 | -- | -- logistics_crane | -- | -- | n/a | missing |
| 10 | The Replica | twin_towers | 0/3 | -- | 0/9 | 0/8 | 0/3 | -- | -- logistics_crane | -- | -- | n/a | missing |
| 11 | Priority One | arc_over_wall | 0/3 | -- | 0/9 | 0/8 | 0/3 | -- | -- cooling_tower | -- | -- | n/a | missing |
| 12 | No Exceptions | pyramid | 0/2 | -- | 0/6 | 0/7 | 0/3 | -- | -- cooling_tower | -- | -- | n/a | missing |
| 13 | The Quiet District | glass_roof | 0/2 | -- | 0/9 | 0/8 | 0/3 | -- | -- cooling_tower | -- | -- | n/a | missing |
| 14 | Root Access | indirect_shield | 0/3 | -- | 0/12 | 0/8 | 0/3 | -- | -- cooling_tower | -- | -- | n/a | missing |
| 15 | The Directive | twin_towers, glass_screen | 0/4 | -- | 0/12 | 0/9 | 0/3 | -- | -- cooling_tower | -- | -- | n/a | missing |
| 16 | Failsafe | ledges | 0/2 | -- | 0/6 | 0/7 | 0/3 | -- | -- aura_core_chamber | -- | -- | n/a | missing |
| 17 | Last Backup | topple_line | 0/3 | n/a | 0/6 | 0/6 | 0/3 | -- | -- aura_core_chamber | -- | -- | n/a | missing |
| 18 | Cascade | arc_over_wall | 0/3 | -- | 0/9 | 0/8 | 0/3 | -- | -- aura_core_chamber | -- | -- | n/a | missing |
| 19 | Central Logic | domino_row, ledges, chain_cell | 0/5 | -- | 0/12 | 0/9 | 0/3 | -- | -- aura_core_chamber | -- | -- | n/a | missing |
| 20 | The Machine That Decided | finale | 0/10 | -- | 0/18 | 0/10 | 0/3 | -- | -- aura_core_chamber | -- | -- | 0/1 | missing |

## Chapter 2: VITA Genomics (The Price of Perfection), levels 21-40

| L | Name | Archetypes | Struct | Core | Mat+dmg | VFX | Env | BG | Landmark | Music | Amb | Cine | Status |
|---:|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 21 | A Longer Life | glass_screen | 0/3 | -- | 0/12 | 0/9 | 0/3 | -- | -- cleanroom_airlock | -- | -- | 0/2 | missing |
| 22 | Clean Room | glass_screen, chain_towers | 0/4 | -- | 0/12 | 0/9 | 0/3 | -- | -- cleanroom_airlock | -- | -- | n/a | missing |
| 23 | The Sequence | stack_tower | 0/2 | -- | 0/6 | 0/7 | 0/3 | -- | -- cleanroom_airlock | -- | -- | n/a | missing |
| 24 | Growth Chamber | heavy_cap, glass_roof | 0/3 | -- | 0/12 | 0/9 | 0/3 | -- | -- cleanroom_airlock | -- | -- | n/a | missing |
| 25 | Trial Run | twin_towers | 0/3 | -- | 0/9 | 0/8 | 0/3 | -- | -- cleanroom_airlock | -- | -- | n/a | missing |
| 26 | Better Than Human | multi_tier | 0/3 | -- | 0/9 | 0/8 | 0/3 | -- | -- bioreactor_bank | -- | -- | n/a | missing |
| 27 | Cold Chain | support_bridge, heavy_cap | 0/3 | -- | 0/12 | 0/9 | 0/3 | -- | -- bioreactor_bank | -- | -- | n/a | missing |
| 28 | The Dependency | indirect_shield | 0/3 | -- | 0/9 | 0/7 | 0/3 | -- | -- bioreactor_bank | -- | -- | n/a | missing |
| 29 | Replication Error | linked_bridge, chain_cell | 0/4 | -- | 0/12 | 0/9 | 0/3 | -- | -- bioreactor_bank | -- | -- | n/a | missing |
| 30 | Controlled Growth | glass_screen | 0/3 | -- | 0/12 | 0/9 | 0/3 | -- | -- bioreactor_bank | -- | -- | n/a | missing |
| 31 | The Patent Wall | arc_over_wall | 0/3 | -- | 0/9 | 0/8 | 0/3 | -- | -- archive_vault | -- | -- | n/a | missing |
| 32 | Patient Zero | heavy_cap | 0/2 | -- | 0/9 | 0/8 | 0/3 | -- | -- archive_vault | -- | -- | n/a | missing |
| 33 | The Upgrade | mixed_material | 0/4 | -- | 0/12 | 0/9 | 0/3 | -- | -- archive_vault | -- | -- | n/a | missing |
| 34 | The Price | heavy_cap | 0/2 | -- | 0/9 | 0/8 | 0/3 | -- | -- archive_vault | -- | -- | n/a | missing |
| 35 | No Consent | frame | 0/3 | -- | 0/12 | 0/8 | 0/3 | -- | -- archive_vault | -- | -- | n/a | missing |
| 36 | The Black Archive | glass_roof, arc_over_wall | 0/5 | -- | 0/15 | 0/10 | 0/3 | -- | -- growth_chamber | -- | -- | n/a | missing |
| 37 | The Prediction | multi_tier | 0/3 | -- | 0/9 | 0/8 | 0/3 | -- | -- growth_chamber | -- | -- | n/a | missing |
| 38 | The Last Batch | twin_towers | 0/3 | -- | 0/9 | 0/8 | 0/3 | -- | -- growth_chamber | -- | -- | n/a | missing |
| 39 | Dependency Chain | linked_bridge, chain_cell | 0/4 | -- | 0/12 | 0/9 | 0/3 | -- | -- growth_chamber | -- | -- | n/a | missing |
| 40 | The Price of Perfection | finale | 0/10 | -- | 0/21 | 0/11 | 0/3 | -- | -- growth_chamber | -- | -- | 0/1 | missing |

## Chapter 3: Nova Grid (The Energy Beneath), levels 41-60

| L | Name | Archetypes | Struct | Core | Mat+dmg | VFX | Env | BG | Landmark | Music | Amb | Cine | Status |
|---:|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 41 | Endless Power | support_bridge | 0/2 | -- | 0/9 | 0/8 | 0/3 | -- | -- intake_turbine | -- | -- | 0/2 | missing |
| 42 | The Intake | frame | 0/3 | -- | 0/12 | 0/9 | 0/3 | -- | -- intake_turbine | -- | -- | n/a | missing |
| 43 | Containment Ring | ring | 0/3 | -- | 0/9 | 0/8 | 0/3 | -- | -- intake_turbine | -- | -- | n/a | missing |
| 44 | Cooling the Future | chain_towers | 0/2 | -- | 0/9 | 0/8 | 0/3 | -- | -- intake_turbine | -- | -- | n/a | missing |
| 45 | The First Pulse | arc_over_wall | 0/3 | -- | 0/9 | 0/8 | 0/3 | -- | -- intake_turbine | -- | -- | n/a | missing |
| 46 | Load Balancing | support_bridge | 0/2 | -- | 0/9 | 0/8 | 0/3 | -- | -- cooling_tower | -- | -- | n/a | missing |
| 47 | Deep Storage | stack_tower | 0/2 | -- | 0/9 | 0/8 | 0/3 | -- | -- cooling_tower | -- | -- | n/a | missing |
| 48 | Silent Alarm | linked_bridge, chain_cell | 0/4 | -- | 0/9 | 0/8 | 0/3 | -- | -- cooling_tower | -- | -- | n/a | missing |
| 49 | Overload Window | mixed_material | 0/4 | -- | 0/12 | 0/9 | 0/3 | -- | -- cooling_tower | -- | -- | n/a | missing |
| 50 | The Resonance | ring, chain_cell | 0/4 | -- | 0/9 | 0/8 | 0/3 | -- | -- cooling_tower | -- | -- | n/a | missing |
| 51 | Beyond the Grid | arc_over_wall | 0/3 | -- | 0/9 | 0/8 | 0/3 | -- | -- transformer_yard | -- | -- | n/a | missing |
| 52 | The Wrong Frequency | ledges, twin_towers | 0/5 | -- | 0/12 | 0/9 | 0/3 | -- | -- transformer_yard | -- | -- | n/a | missing |
| 53 | The Deep Core | heavy_cap | 0/2 | -- | 0/9 | 0/8 | 0/3 | -- | -- transformer_yard | -- | -- | n/a | missing |
| 54 | Blackout Protocol | linked_bridge | 0/3 | -- | 0/9 | 0/8 | 0/3 | -- | -- transformer_yard | -- | -- | n/a | missing |
| 55 | The Echo | domino_row, multi_tier, chain_cell | 0/4 | -- | 0/12 | 0/9 | 0/3 | -- | -- transformer_yard | -- | -- | n/a | missing |
| 56 | Dead Circuit | glass_roof, arc_over_wall | 0/5 | -- | 0/15 | 0/10 | 0/3 | -- | -- reactor_ring | -- | -- | n/a | missing |
| 57 | Origin Unknown | indirect_shield | 0/3 | -- | 0/9 | 0/8 | 0/3 | -- | -- reactor_ring | -- | -- | n/a | missing |
| 58 | The Listening Machine | frame | 0/3 | -- | 0/12 | 0/9 | 0/3 | -- | -- reactor_ring | -- | -- | n/a | missing |
| 59 | Final Containment | wide_platform, chain_cell | 0/5 | -- | 0/12 | 0/9 | 0/3 | -- | -- reactor_ring | -- | -- | n/a | missing |
| 60 | The Energy Beneath | finale, ring | 0/11 | -- | 0/18 | 0/11 | 0/3 | -- | -- reactor_ring | -- | -- | 0/1 | missing |

## Chapter 4: Civitas (The Quiet Cage), levels 61-80

| L | Name | Archetypes | Struct | Core | Mat+dmg | VFX | Env | BG | Landmark | Music | Amb | Cine | Status |
|---:|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 61 | A Predictable World | tall_mast | 0/2 | -- | 0/9 | 0/8 | 0/3 | -- | -- sensor_tower | -- | -- | 0/2 | missing |
| 62 | The Profile | tall_mast | 0/2 | -- | 0/9 | 0/8 | 0/3 | -- | -- sensor_tower | -- | -- | n/a | missing |
| 63 | The Forecast | arc_over_wall | 0/3 | -- | 0/9 | 0/8 | 0/3 | -- | -- sensor_tower | -- | -- | n/a | missing |
| 64 | Access Denied | glass_screen | 0/3 | -- | 0/12 | 0/9 | 0/3 | -- | -- sensor_tower | -- | -- | n/a | missing |
| 65 | The Invisible Rule | domino_row, arc_over_wall | 0/4 | -- | 0/12 | 0/9 | 0/3 | -- | -- sensor_tower | -- | -- | n/a | missing |
| 66 | Quiet Signals | wide_platform | 0/4 | -- | 0/12 | 0/9 | 0/3 | -- | -- screen_wall | -- | -- | n/a | missing |
| 67 | The Approved Path | support_bridge | 0/2 | -- | 0/9 | 0/8 | 0/3 | -- | -- screen_wall | -- | -- | n/a | missing |
| 68 | The Exception | topple_line | 0/3 | n/a | 0/9 | 0/7 | 0/3 | -- | -- screen_wall | -- | -- | n/a | missing |
| 69 | Public Safety | linked_bridge, chain_cell | 0/4 | -- | 0/12 | 0/9 | 0/3 | -- | -- screen_wall | -- | -- | n/a | missing |
| 70 | The Mirror | frame | 0/3 | -- | 0/12 | 0/9 | 0/3 | -- | -- screen_wall | -- | -- | n/a | missing |
| 71 | The Model Knows | multi_tier | 0/3 | -- | 0/9 | 0/8 | 0/3 | -- | -- prediction_room | -- | -- | n/a | missing |
| 72 | Prewritten | arc_over_wall | 0/3 | -- | 0/9 | 0/8 | 0/3 | -- | -- prediction_room | -- | -- | n/a | missing |
| 73 | The Shared Signature | linked_bridge, chain_cell | 0/4 | -- | 0/12 | 0/9 | 0/3 | -- | -- prediction_room | -- | -- | n/a | missing |
| 74 | The Quiet Cage | wide_platform | 0/4 | -- | 0/12 | 0/9 | 0/3 | -- | -- prediction_room | -- | -- | n/a | missing |
| 75 | No Unknowns | mixed_material | 0/4 | -- | 0/12 | 0/9 | 0/3 | -- | -- prediction_room | -- | -- | n/a | missing |
| 76 | The Future File | heavy_cap, topple_line | 0/4 | -- | 0/12 | 0/9 | 0/3 | -- | -- relay_spire | -- | -- | n/a | missing |
| 77 | The Missing Year | twin_towers | 0/3 | -- | 0/9 | 0/8 | 0/3 | -- | -- relay_spire | -- | -- | n/a | missing |
| 78 | Source Code | arc_over_wall, ledges | 0/4 | -- | 0/12 | 0/8 | 0/3 | -- | -- relay_spire | -- | -- | n/a | missing |
| 79 | The Last Forecast | multi_tier | 0/3 | -- | 0/9 | 0/8 | 0/3 | -- | -- relay_spire | -- | -- | n/a | missing |
| 80 | The Quiet Cage | finale | 0/10 | -- | 0/18 | 0/10 | 0/3 | -- | -- relay_spire | -- | -- | 0/1 | missing |

## Chapter 5: Meridian (The Convergence), levels 81-100

| L | Name | Archetypes | Struct | Core | Mat+dmg | VFX | Env | BG | Landmark | Music | Amb | Cine | Status |
|---:|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 81 | No Public Record | exposed_target | 0/1 | -- | 0/6 | 0/7 | 0/3 | -- | -- hybrid_stack | -- | -- | 0/2 | missing |
| 82 | Beneath the City | multi_tier | 0/3 | -- | 0/12 | 0/9 | 0/3 | -- | -- hybrid_stack | -- | -- | n/a | missing |
| 83 | Four Foundations | wide_platform | 0/4 | -- | 0/15 | 0/9 | 0/3 | -- | -- hybrid_stack | -- | -- | n/a | missing |
| 84 | The Common Model | arc_over_wall, ledges | 0/4 | -- | 0/12 | 0/9 | 0/3 | -- | -- hybrid_stack | -- | -- | n/a | missing |
| 85 | The Hidden Budget | heavy_cap | 0/2 | -- | 0/9 | 0/8 | 0/3 | -- | -- hybrid_stack | -- | -- | n/a | missing |
| 86 | The First Directive | domino_row, ledges | 0/4 | -- | 0/9 | 0/8 | 0/3 | -- | -- foundation_pillars | -- | -- | n/a | missing |
| 87 | The Operator | frame | 0/3 | -- | 0/12 | 0/9 | 0/3 | -- | -- foundation_pillars | -- | -- | n/a | missing |
| 88 | The Convergence Engine | multi_tier | 0/3 | -- | 0/12 | 0/9 | 0/3 | -- | -- foundation_pillars | -- | -- | n/a | missing |
| 89 | The Failsafe Network | linked_bridge | 0/3 | -- | 0/12 | 0/8 | 0/3 | -- | -- foundation_pillars | -- | -- | n/a | missing |
| 90 | The Other Timeline | linked_bridge, ledges, chain_cell | 0/6 | -- | 0/12 | 0/8 | 0/3 | -- | -- foundation_pillars | -- | -- | n/a | missing |
| 91 | The Chosen Outcome | ring, chain_cell | 0/4 | -- | 0/12 | 0/8 | 0/3 | -- | -- temporal_anchor | -- | -- | n/a | missing |
| 92 | The Human Variable | topple_line, mixed_material | 0/5 | n/a | 0/12 | 0/8 | 0/3 | -- | -- temporal_anchor | -- | -- | n/a | missing |
| 93 | The Last Safeguard | heavy_cap, frame | 0/4 | -- | 0/12 | 0/9 | 0/3 | -- | -- temporal_anchor | -- | -- | n/a | missing |
| 94 | Break the Chain | domino_row, chain_cell | 0/3 | -- | 0/9 | 0/8 | 0/3 | -- | -- temporal_anchor | -- | -- | n/a | missing |
| 95 | The Core Directive | multi_tier | 0/3 | -- | 0/12 | 0/9 | 0/3 | -- | -- temporal_anchor | -- | -- | n/a | missing |
| 96 | Before the Beginning | arc_over_wall | 0/3 | -- | 0/9 | 0/8 | 0/3 | -- | -- convergence_chamber | -- | -- | n/a | missing |
| 97 | The Final Relay | linked_bridge, chain_cell | 0/4 | -- | 0/12 | 0/8 | 0/3 | -- | -- convergence_chamber | -- | -- | n/a | missing |
| 98 | No Return Path | mixed_material | 0/4 | -- | 0/12 | 0/9 | 0/3 | -- | -- convergence_chamber | -- | -- | n/a | missing |
| 99 | The Last Structure | multi_tier, wide_platform | 0/4 | -- | 0/15 | 0/9 | 0/3 | -- | -- convergence_chamber | -- | -- | n/a | missing |
| 100 | The Wrong Future | finale, ring | 0/11 | -- | 0/21 | 0/11 | 0/3 | -- | -- convergence_chamber | -- | -- | 0/2 | missing |

## Missing assets ranked by levels affected

| Wanted asset (id pattern) | Levels | First level |
|---|---:|---:|
| `SHR-VFX-BREACH_BLAST-A` | 100 | 1 |
| `SHR-VFX-IMPACT_SPARKS-A` | 100 | 1 |
| `SHR-VFX-KINETIC_MUZZLE_FLASH-A` | 100 | 1 |
| `SHR-VFX-SMOKE-A` | 100 | 1 |
| `SHR-VFX-METAL_SPARKS-A` | 86 | 2 |
| `SHR-DMG-COMPOSITE-HEAVY` | 80 | 1 |
| `SHR-DMG-COMPOSITE-LIGHT` | 80 | 1 |
| `SHR-VFX-DEBRIS_CHIPS-A` | 80 | 1 |
| `SHR-DMG-ELECTRONIC_MODULE-HEAVY` | 69 | 1 |
| `SHR-DMG-ELECTRONIC_MODULE-LIGHT` | 69 | 1 |
| `SHR-VFX-ELECTRICAL_ARCS-A` | 69 | 1 |
| `SHR-DMG-LIGHTWEIGHT_ALLOY-HEAVY` | 51 | 2 |
| `SHR-DMG-LIGHTWEIGHT_ALLOY-LIGHT` | 51 | 2 |
| `SHR-DMG-REINFORCED_STEEL-HEAVY` | 49 | 11 |
| `SHR-DMG-REINFORCED_STEEL-LIGHT` | 49 | 11 |
| `SHR-DMG-ENERGY_COMPONENT-HEAVY` | 45 | 6 |
| `SHR-DMG-ENERGY_COMPONENT-LIGHT` | 45 | 6 |
| `SHR-VFX-ENERGY_DISCHARGE-A` | 45 | 6 |
| `SHR-DMG-CONCRETE-HEAVY` | 41 | 7 |
| `SHR-DMG-CONCRETE-LIGHT` | 41 | 7 |
| `SHR-VFX-CONCRETE_DUST-A` | 41 | 7 |
| `SHR-DMG-GLASS_POLYMER-HEAVY` | 23 | 2 |
| `SHR-DMG-GLASS_POLYMER-LIGHT` | 23 | 2 |
| `SHR-VFX-GLASS_SHARDS-A` | 23 | 2 |
| `HLX-ENV-<STRUCTURE>-A` | 20 | 1 |
| `HLX-ENV-BACK_WALL-A` | 20 | 1 |
| `HLX-ENV-FLOOR-A` | 20 | 1 |
| `VTA-CMP-GENE_VAULT_CORE-A` | 20 | 21 |
| `VTA-DEB-GENE_VAULT_CORE-A` | 20 | 21 |
| `VTA-ENV-<STRUCTURE>-A` | 20 | 21 |
| `VTA-ENV-BACK_WALL-A` | 20 | 21 |
| `VTA-ENV-FLOOR-A` | 20 | 21 |
| `VTA-MAT-ELECTRONIC_MODULE-A` | 20 | 21 |
| `VTA-VFX-CORE_DESTRUCTION-A` | 20 | 21 |
| `NVG-CMP-REACTOR_CORE-A` | 20 | 41 |
| `NVG-DEB-REACTOR_CORE-A` | 20 | 41 |
| `NVG-ENV-<STRUCTURE>-A` | 20 | 41 |
| `NVG-ENV-BACK_WALL-A` | 20 | 41 |
| `NVG-ENV-FLOOR-A` | 20 | 41 |
| `NVG-MAT-ENERGY_COMPONENT-A` | 20 | 41 |
| `NVG-VFX-CORE_DESTRUCTION-A` | 20 | 41 |
| `CVT-ENV-<STRUCTURE>-A` | 20 | 61 |
| `CVT-ENV-BACK_WALL-A` | 20 | 61 |
| `CVT-ENV-FLOOR-A` | 20 | 61 |
| `MRD-ENV-<STRUCTURE>-A` | 20 | 81 |
| `MRD-ENV-BACK_WALL-A` | 20 | 81 |
| `MRD-ENV-FLOOR-A` | 20 | 81 |
| `VTA-MAT-LIGHTWEIGHT_ALLOY-A` | 19 | 21 |
| `CVT-CMP-SURVEILLANCE_CORE-A` | 19 | 61 |
| `CVT-DEB-SURVEILLANCE_CORE-A` | 19 | 61 |
| `CVT-MAT-ELECTRONIC_MODULE-A` | 19 | 61 |
| `CVT-VFX-CORE_DESTRUCTION-A` | 19 | 61 |
| `MRD-CMP-CONVERGENCE_CORE-A` | 19 | 81 |
| `MRD-DEB-CONVERGENCE_CORE-A` | 19 | 81 |
| `MRD-MAT-ENERGY_COMPONENT-A` | 19 | 81 |
| `MRD-VFX-CORE_DESTRUCTION-A` | 19 | 81 |
| `HLX-CMP-AI_CORE-A` | 18 | 1 |
| `HLX-DEB-AI_CORE-A` | 18 | 1 |
| `HLX-MAT-ELECTRONIC_MODULE-A` | 18 | 1 |
| `HLX-VFX-CORE_DESTRUCTION-A` | 18 | 1 |
| `VTA-CMP-LAB_COLUMN-A` | 18 | 21 |
| `NVG-MAT-REINFORCED_STEEL-A` | 18 | 41 |
| `MRD-CMP-CONVERGENCE_DECK-A` | 18 | 81 |
| `MRD-MAT-COMPOSITE-A` | 18 | 81 |
| `MRD-MAT-REINFORCED_STEEL-A` | 18 | 82 |
| `NVG-CMP-GRID_PYLON-A` | 17 | 41 |
| `CVT-CMP-RELAY_BRIDGE-A` | 17 | 63 |
| `CVT-MAT-COMPOSITE-A` | 17 | 63 |
| `MRD-CMP-ANCHOR_COLUMN-A` | 17 | 82 |
| `HLX-MAT-COMPOSITE-A` | 16 | 1 |
| `HLX-MUS-GAMEPLAY-01` | 15 | 1 |
| `VTA-MUS-GAMEPLAY-01` | 15 | 21 |
| `NVG-CMP-CABLE_BRIDGE-A` | 15 | 41 |
| `NVG-MAT-COMPOSITE-A` | 15 | 41 |
| `NVG-MUS-GAMEPLAY-01` | 15 | 41 |
| `CVT-MUS-GAMEPLAY-01` | 15 | 61 |
| `CVT-CMP-CIVIC_COLUMN-A` | 15 | 64 |
| `CVT-MAT-CONCRETE-A` | 15 | 64 |
| `MRD-MUS-GAMEPLAY-01` | 15 | 81 |
| `HLX-MAT-LIGHTWEIGHT_ALLOY-A` | 14 | 2 |
| `VTA-CMP-LAB_DECK-A` | 14 | 21 |
| `VTA-MAT-COMPOSITE-A` | 14 | 21 |
| `HLX-CMP-SERVICE_DECK-A` | 13 | 1 |
| `HLX-CMP-SUPPORT_COLUMN-A` | 13 | 3 |
| `SHR-CMP-GENERIC_BLOCK_STEEL-A` | 12 | 28 |
| `CVT-MAT-LIGHTWEIGHT_ALLOY-A` | 11 | 61 |
| `NVG-MAT-CONCRETE-A` | 9 | 42 |
| `VTA-CMP-CONTAINMENT_CAP-A` | 8 | 24 |
| `VTA-MAT-CONCRETE-A` | 8 | 24 |
| `CVT-CMP-DATA_EXCHANGE_RACK-A` | 8 | 66 |
| `MRD-CMP-MONOLITH_SLAB-A` | 8 | 84 |
| `MRD-MAT-CONCRETE-A` | 8 | 84 |
| `HLX-CMP-DATA_CRATE-A` | 7 | 4 |
| `VTA-CMP-CLEANROOM_PANEL-A` | 7 | 21 |
| `VTA-MAT-GLASS_POLYMER-A` | 7 | 21 |
| `VTA-CMP-SPECIMEN_RACK-A` | 7 | 22 |
| `SHR-CMP-GENERIC_BLOCK_ALLOY-A` | 7 | 23 |
| `NVG-CMP-CONTAINMENT_WALL-A` | 7 | 42 |
| `CVT-CMP-SENSOR_MAST-A` | 7 | 61 |
| `MRD-CMP-TIMELINE_RELAY-A` | 7 | 83 |
| `MRD-MAT-LIGHTWEIGHT_ALLOY-A` | 7 | 83 |
| `NVG-CMP-TRANSFORMER-A` | 6 | 44 |
| `NVG-MAT-ELECTRONIC_MODULE-A` | 6 | 44 |
| `CVT-CMP-SECURITY_WALL-A` | 6 | 63 |
| `CVT-MAT-REINFORCED_STEEL-A` | 6 | 63 |
| `MRD-CMP-QUANTUM_STABILIZER-A` | 6 | 82 |
| `MRD-MAT-ELECTRONIC_MODULE-A` | 6 | 82 |
| `HLX-AMB-SERVER_HALL-01` | 5 | 1 |
| `HLX-BG-FAR-A` | 5 | 1 |
| `HLX-PRP-RELAY_ARRAY-A` | 5 | 1 |
| `HLX-MAT-GLASS_POLYMER-A` | 5 | 2 |
| `HLX-CMP-SERVER_RACK-A` | 5 | 4 |
| `HLX-AMB-LOGISTICS-01` | 5 | 6 |
| `HLX-BG-FAR-B` | 5 | 6 |
| `HLX-PRP-LOGISTICS_CRANE-A` | 5 | 6 |
| `SHR-CMP-GENERIC_BLOCK_CONCRETE-A` | 5 | 7 |
| `HLX-AMB-COOLING-01` | 5 | 11 |
| `HLX-BG-FAR-C` | 5 | 11 |
| `HLX-PRP-COOLING_TOWER-A` | 5 | 11 |
| `HLX-AMB-CORE-01` | 5 | 16 |
| ... 107 more in coverage_matrix.json | | |

## How requirements are derived

- Structural components: each level's layout archetypes (from the puzzle notes in `docs/level-design-spec.md`) give structural roles; each chapter maps roles to its component kinds (ASSET_CONTRACT section 5). A chapter kind with only a shared generic block of the same physics material counts as fallback.
- Critical asset: the chapter core kind plus its debris set, except pure topple levels 9, 17, 68 and 92.
- Materials: a texture set per physics material used (chapter set, or shared as fallback) plus light and heavy damage overlays.
- VFX: weapon effects for every level plus material-specific destruction effects and the critical destruction effect.
- Environment: chapter floor, back wall and mid-back structures; a far background layer rotated by band.
- Variety: one landmark prop per band of five levels (four per chapter, 20 in total) and two dressing props rotated from the chapter prop pool.
- Music: chapter gameplay theme for bands 1-3, combat theme for band 4, boss or finale theme on levels 20/40/60/80/100. Ambience by band with the chapter bed as fallback. Cinematics on chapter intros, outros, the opening (level 1) and the finale (level 100).

