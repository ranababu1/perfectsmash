# 100-level asset coverage matrix

Generated 2026-11-10 by `generated_assets/tools/build_coverage_matrix.py` from the merged manifest (updated 2026-11-10, 794 entries on disk, 691 production entries; concepts and mock layouts do not count). Do not edit by hand; re-run the script.

Status: `ok` available, `fb` shared fallback only, `--` missing. Group columns show available/required.
A level is **full** when every requirement is available, **fallback** when nothing is missing but shared substitutes are used.

## Summary

- Levels fully covered: **0 / 100**; covered with fallbacks: 0; with missing assets: 100.
- Requirements available: 2014 / 3176 level-requirement slots.
- Game-wide requirements available: 27 / 36.

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
| HUD elements (weapon slots, ammo, cooldown, reticle, trajectory) | ok | GAM-UI-AIM_RETICLE-A, GAM-UI-AMMO_PIP_BREACH_EMPTY-A, GAM-UI-AMMO_PIP_BREACH_FULL-A |
| Critical asset target marker | ok | GAM-UI-CRITICAL_MARKER_ALL-A, GAM-UI-CRITICAL_MARKER_BRACKETS-A, GAM-UI-CRITICAL_MARKER_DIAMOND-A |
| Objective markers | ok | GAM-UI-OBJECTIVE_MARKER_COMPLETE-A, GAM-UI-OBJECTIVE_MARKER_FAILED-A, GAM-UI-OBJECTIVE_MARKER_OPTIONAL-A |
| Weapon icons | ok | GAM-ICN-WEAPON_BREACH_CHARGE-A, GAM-ICN-WEAPON_DISRUPTOR-A, GAM-ICN-WEAPON_KINETIC_ACCELERATOR-A |
| Objective icons | ok | GAM-ICN-OBJECTIVE_COMPLETE-A, GAM-ICN-OBJECTIVE_FAILED-A, GAM-ICN-OBJECTIVE_OPTIONAL-A |
| Panels and buttons (9-slice kit) | ok | GAM-UI-BUTTON_DANGER_DISABLED-A, GAM-UI-BUTTON_DANGER_HOVER-A, GAM-UI-BUTTON_DANGER_NORMAL-A |
| Main menu backdrop | ok | GAM-BG-MAIN_MENU-A |
| Loading backdrop | ok | GAM-BG-LOADING-A |
| Chapter cards and upgrade tier badges | ok | GAM-UI-CARD_CHAPTER_CIVITAS_LOCKED-A, GAM-UI-CARD_CHAPTER_CIVITAS_NORMAL-A, GAM-UI-CARD_CHAPTER_CIVITAS_SELECTED-A |
| Chapter title treatments | ok | GAM-UI-CHAPTER_TITLE_DECO-01_1X, GAM-UI-CHAPTER_TITLE_DECO-01_2X, GAM-UI-CHAPTER_TITLE_DECO-02_1X |
| Screen layout references (menus, HUD, results, map, upgrades) | ok | GAM-UI-SCREEN_CHAPTER_MAP_01_HELIX-MOCK, GAM-UI-SCREEN_CHAPTER_MAP_02_VITA-MOCK, GAM-UI-SCREEN_CHAPTER_MAP_03_NOVA_GRID-MOCK |
| Godot theme spec | ok | GAM-UI-THEME_SPEC-A |
| Topple threshold marker | ok | SHR-VFX-THRESHOLD_LINE-A |
| Game logo | ok | GAM-LOGO-COMPACT-COLOUR, GAM-LOGO-COMPACT-COLOUR_ON_LIGHT, GAM-LOGO-COMPACT-LIGHT_ON_DARK |
| App icon | ok | GAM-LOGO-APP_ICON-192, GAM-LOGO-APP_ICON-256, GAM-LOGO-APP_ICON-48 |
| Splash screen | ok | GAM-UI-SPLASH-1280X720, GAM-UI-SPLASH-2560X1440, GAM-UI-SPLASH-LOGO_TRANSPARENT |
| UI font | ok | GAM-FNT-BARLOW-BOLD, GAM-FNT-BARLOW-MEDIUM, GAM-FNT-BARLOW-REGULAR |
| Menu music | -- |  |
| Victory stinger | ok | GAM-SFX-UI_VICTORY-01 |
| Defeat stinger | ok | GAM-SFX-UI_DEFEAT-01, SHR-SFX-MACHINE_FAILURE-01, SHR-SFX-MACHINE_FAILURE-02 |
| Ending music | -- |  |
| Kinetic fire SFX | ok | OPR-SFX-KINETIC_CHARGE-01, OPR-SFX-KINETIC_CHARGE-02, OPR-SFX-KINETIC_CHARGE-03 |
| Breach launch / detonation SFX | ok | OPR-SFX-BREACH_ARM-01, OPR-SFX-BREACH_ARM-02, OPR-SFX-BREACH_ARM-03 |
| Metal impact SFX | ok | SHR-SFX-IMPACT_METAL-01, SHR-SFX-IMPACT_METAL-02, SHR-SFX-IMPACT_METAL-03 |
| Glass break SFX | ok | SHR-SFX-IMPACT_GLASS-01, SHR-SFX-IMPACT_GLASS-02, SHR-SFX-IMPACT_GLASS-03 |
| Concrete break SFX | ok | SHR-SFX-IMPACT_CONCRETE-01, SHR-SFX-IMPACT_CONCRETE-02, SHR-SFX-IMPACT_CONCRETE-03 |
| Electrical / machinery SFX | ok | OPR-SFX-SUIT_SERVO-01, OPR-SFX-SUIT_SERVO-02, OPR-SFX-SUIT_SERVO-03 |
| UI SFX | ok | GAM-SFX-UI_ACHIEVEMENT-01, GAM-SFX-UI_BACK-01, GAM-SFX-UI_BACK-02 |
| Alarm SFX | ok | SHR-SFX-ALARM_KLAXON-01, SHR-SFX-ALARM_PULSE-01, SHR-SFX-ALARM_SIREN-01 |
| Opening cinematic | -- |  |

## Chapter 1: Helix Systems (The Machine That Decided), levels 1-20

| L | Name | Story target | Archetypes | Struct | Core | Mat+dmg | VFX | Env | BG | Landmark | Music | Amb | Cine | Status |
|---:|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | First Contact | Helix perimeter relay | exposed_target | 0/1 | -- | 6/6 | 7/7 | 0/3 | -- | -- relay_array | -- | ok | 0/3 | missing |
| 2 | The Welcome System | Automated security gate | tall_mast | 0/2 | -- | 9/9 | 8/8 | 0/3 | -- | -- relay_array | -- | ok | n/a | missing |
| 3 | Traffic of One | Autonomous traffic-control tower | support_bridge | 0/2 | -- | 9/9 | 8/8 | 0/3 | -- | -- relay_array | -- | ok | n/a | missing |
| 4 | Supply Chain | Logistics sorting structure | stack_tower | 0/2 | -- | 6/6 | 7/7 | 0/3 | -- | -- relay_array | -- | ok | n/a | missing |
| 5 | The Safety Layer | Emergency-response relay | glass_screen | 0/3 | -- | 12/12 | 9/9 | 0/3 | -- | -- relay_array | -- | ok | n/a | missing |
| 6 | Cold Storage | Server-cooling array | chain_towers, chain_cell | 0/3 | -- | 9/9 | 8/8 | 0/3 | -- | -- logistics_crane | -- | ok | n/a | missing |
| 7 | Blind Spot | Surveillance exchange | heavy_cap | 0/2 | -- | 9/9 | 8/8 | 0/3 | -- | -- logistics_crane | -- | ok | n/a | missing |
| 8 | Human Override | Manual control station | domino_row | 0/2 | -- | 9/9 | 8/8 | 0/3 | -- | -- logistics_crane | -- | ok | n/a | missing |
| 9 | Redundancy | Backup server stacks | topple_line | 0/3 | n/a | 6/6 | 6/6 | 0/3 | -- | -- logistics_crane | -- | ok | n/a | missing |
| 10 | The Replica | Replication hub | twin_towers | 0/3 | -- | 9/9 | 8/8 | 0/3 | -- | -- logistics_crane | -- | ok | n/a | missing |
| 11 | Priority One | Resource-allocation centre | arc_over_wall | 0/3 | -- | 9/9 | 8/8 | 0/3 | -- | -- cooling_tower | -- | ok | n/a | missing |
| 12 | No Exceptions | Compliance processing facility | pyramid | 0/2 | -- | 6/6 | 7/7 | 0/3 | -- | -- cooling_tower | -- | ok | n/a | missing |
| 13 | The Quiet District | Local control tower | glass_roof | 0/2 | -- | 9/9 | 8/8 | 0/3 | -- | -- cooling_tower | -- | ok | n/a | missing |
| 14 | Root Access | Core routing structure | indirect_shield | 0/3 | -- | 12/12 | 8/8 | 0/3 | -- | -- cooling_tower | -- | ok | n/a | missing |
| 15 | The Directive | Directive archive | twin_towers, glass_screen | 0/4 | -- | 12/12 | 9/9 | 0/3 | -- | -- cooling_tower | -- | ok | n/a | missing |
| 16 | Failsafe | Emergency power structure | ledges | 0/2 | -- | 6/6 | 7/7 | 0/3 | -- | -- aura_core_chamber | -- | ok | n/a | missing |
| 17 | Last Backup | Cold backup vault | topple_line | 0/3 | n/a | 6/6 | 6/6 | 0/3 | -- | -- aura_core_chamber | -- | ok | n/a | missing |
| 18 | Cascade | Multi-node operations hall | arc_over_wall | 0/3 | -- | 9/9 | 8/8 | 0/3 | -- | -- aura_core_chamber | -- | ok | n/a | missing |
| 19 | Central Logic | AURA central operations structure | domino_row, ledges, chain_cell | 0/5 | -- | 12/12 | 9/9 | 0/3 | -- | -- aura_core_chamber | -- | ok | n/a | missing |
| 20 | The Machine That Decided | Helix central core | finale | 0/10 | -- | 18/18 | 10/10 | 0/3 | -- | -- aura_core_chamber | -- | ok | 0/1 | missing |

## Chapter 2: VITA Genomics (The Price of Perfection), levels 21-40

| L | Name | Story target | Archetypes | Struct | Core | Mat+dmg | VFX | Env | BG | Landmark | Music | Amb | Cine | Status |
|---:|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 21 | A Longer Life | VITA campus entrance | glass_screen | 0/3 | -- | 12/12 | 9/9 | 0/3 | -- | -- cleanroom_airlock | -- | ok | 0/2 | missing |
| 22 | Clean Room | Sterile research structures | glass_screen, chain_towers | 0/4 | -- | 12/12 | 9/9 | 0/3 | -- | -- cleanroom_airlock | -- | ok | n/a | missing |
| 23 | The Sequence | Genomics analysis racks | stack_tower | 0/2 | -- | 6/6 | 7/7 | 0/3 | -- | -- cleanroom_airlock | -- | ok | n/a | missing |
| 24 | Growth Chamber | Bioreactor support frame | heavy_cap, glass_roof | 0/3 | -- | 12/12 | 9/9 | 0/3 | -- | -- cleanroom_airlock | -- | ok | n/a | missing |
| 25 | Trial Run | Clinical automation hub | twin_towers | 0/3 | -- | 9/9 | 8/8 | 0/3 | -- | -- cleanroom_airlock | -- | ok | n/a | missing |
| 26 | Better Than Human | Enhancement lab | multi_tier | 0/3 | -- | 9/9 | 8/8 | 0/3 | -- | -- bioreactor_bank | -- | ok | n/a | missing |
| 27 | Cold Chain | Distribution and storage racks | support_bridge, heavy_cap | 0/3 | -- | 12/12 | 9/9 | 0/3 | -- | -- bioreactor_bank | -- | ok | n/a | missing |
| 28 | The Dependency | Life-support research infrastructure | indirect_shield | 0/3 | -- | 9/9 | 7/7 | 0/3 | -- | -- bioreactor_bank | -- | ok | n/a | missing |
| 29 | Replication Error | Containment support structure | linked_bridge, chain_cell | 0/4 | -- | 12/12 | 9/9 | 0/3 | -- | -- bioreactor_bank | -- | ok | n/a | missing |
| 30 | Controlled Growth | Production line | glass_screen | 0/3 | -- | 12/12 | 9/9 | 0/3 | -- | -- bioreactor_bank | -- | ok | n/a | missing |
| 31 | The Patent Wall | Research archive stacks | arc_over_wall | 0/3 | -- | 9/9 | 8/8 | 0/3 | -- | -- archive_vault | -- | ok | n/a | missing |
| 32 | Patient Zero | Sealed trial wing | heavy_cap | 0/2 | -- | 9/9 | 8/8 | 0/3 | -- | -- archive_vault | -- | ok | n/a | missing |
| 33 | The Upgrade | Automated treatment platform | mixed_material | 0/4 | -- | 12/12 | 9/9 | 0/3 | -- | -- archive_vault | -- | ok | n/a | missing |
| 34 | The Price | Resource and cooling structure | heavy_cap | 0/2 | -- | 9/9 | 8/8 | 0/3 | -- | -- archive_vault | -- | ok | n/a | missing |
| 35 | No Consent | Data and trial control centre | frame | 0/3 | -- | 12/12 | 8/8 | 0/3 | -- | -- archive_vault | -- | ok | n/a | missing |
| 36 | The Black Archive | Encrypted research vault | glass_roof, arc_over_wall | 0/5 | -- | 15/15 | 10/10 | 0/3 | -- | -- growth_chamber | -- | ok | n/a | missing |
| 37 | The Prediction | Forecast computation hall | multi_tier | 0/3 | -- | 9/9 | 8/8 | 0/3 | -- | -- growth_chamber | -- | ok | n/a | missing |
| 38 | The Last Batch | Production support array | twin_towers | 0/3 | -- | 9/9 | 8/8 | 0/3 | -- | -- growth_chamber | -- | ok | n/a | missing |
| 39 | Dependency Chain | Central VITA support structure | linked_bridge, chain_cell | 0/4 | -- | 12/12 | 9/9 | 0/3 | -- | -- growth_chamber | -- | ok | n/a | missing |
| 40 | The Price of Perfection | VITA research core | finale | 0/10 | -- | 21/21 | 11/11 | 0/3 | -- | -- growth_chamber | -- | ok | 0/1 | missing |

## Chapter 3: Nova Grid (The Energy Beneath), levels 41-60

| L | Name | Story target | Archetypes | Struct | Core | Mat+dmg | VFX | Env | BG | Landmark | Music | Amb | Cine | Status |
|---:|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 41 | Endless Power | Nova Grid perimeter | support_bridge | 0/2 | -- | 9/9 | 8/8 | 0/3 | -- | -- intake_turbine | -- | ok | 0/2 | missing |
| 42 | The Intake | Energy capture structure | frame | 0/3 | -- | 12/12 | 9/9 | 0/3 | -- | -- intake_turbine | -- | ok | n/a | missing |
| 43 | Containment Ring | Reactor support ring | ring | 0/3 | -- | 9/9 | 8/8 | 0/3 | -- | -- intake_turbine | -- | ok | n/a | missing |
| 44 | Cooling the Future | Cooling tower array | chain_towers | 0/2 | -- | 9/9 | 8/8 | 0/3 | -- | -- intake_turbine | -- | ok | n/a | missing |
| 45 | The First Pulse | Resonance relay | arc_over_wall | 0/3 | -- | 9/9 | 8/8 | 0/3 | -- | -- intake_turbine | -- | ok | n/a | missing |
| 46 | Load Balancing | Distribution tower | support_bridge | 0/2 | -- | 9/9 | 8/8 | 0/3 | -- | -- cooling_tower | -- | ok | n/a | missing |
| 47 | Deep Storage | Energy storage racks | stack_tower | 0/2 | -- | 9/9 | 8/8 | 0/3 | -- | -- cooling_tower | -- | ok | n/a | missing |
| 48 | Silent Alarm | Monitoring station | linked_bridge, chain_cell | 0/4 | -- | 9/9 | 8/8 | 0/3 | -- | -- cooling_tower | -- | ok | n/a | missing |
| 49 | Overload Window | Power conversion array | mixed_material | 0/4 | -- | 12/12 | 9/9 | 0/3 | -- | -- cooling_tower | -- | ok | n/a | missing |
| 50 | The Resonance | Main containment platform | ring, chain_cell | 0/4 | -- | 9/9 | 8/8 | 0/3 | -- | -- cooling_tower | -- | ok | n/a | missing |
| 51 | Beyond the Grid | Long-distance relay | arc_over_wall | 0/3 | -- | 9/9 | 8/8 | 0/3 | -- | -- transformer_yard | -- | ok | n/a | missing |
| 52 | The Wrong Frequency | Signal processing array | ledges, twin_towers | 0/5 | -- | 12/12 | 9/9 | 0/3 | -- | -- transformer_yard | -- | ok | n/a | missing |
| 53 | The Deep Core | Reactor service structure | heavy_cap | 0/2 | -- | 9/9 | 8/8 | 0/3 | -- | -- transformer_yard | -- | ok | n/a | missing |
| 54 | Blackout Protocol | Backup power structures | linked_bridge | 0/3 | -- | 9/9 | 8/8 | 0/3 | -- | -- transformer_yard | -- | ok | n/a | missing |
| 55 | The Echo | Resonance chamber | domino_row, multi_tier, chain_cell | 0/4 | -- | 12/12 | 9/9 | 0/3 | -- | -- transformer_yard | -- | ok | n/a | missing |
| 56 | Dead Circuit | Transmission relay | glass_roof, arc_over_wall | 0/5 | -- | 15/15 | 10/10 | 0/3 | -- | -- reactor_ring | -- | ok | n/a | missing |
| 57 | Origin Unknown | Data capture structure | indirect_shield | 0/3 | -- | 9/9 | 8/8 | 0/3 | -- | -- reactor_ring | -- | ok | n/a | missing |
| 58 | The Listening Machine | Research platform | frame | 0/3 | -- | 12/12 | 9/9 | 0/3 | -- | -- reactor_ring | -- | ok | n/a | missing |
| 59 | Final Containment | Central energy supports | wide_platform, chain_cell | 0/5 | -- | 12/12 | 9/9 | 0/3 | -- | -- reactor_ring | -- | ok | n/a | missing |
| 60 | The Energy Beneath | Nova Grid core | finale, ring | 0/11 | -- | 18/18 | 11/11 | 0/3 | -- | -- reactor_ring | -- | ok | 0/1 | missing |

## Chapter 4: Civitas (The Quiet Cage), levels 61-80

| L | Name | Story target | Archetypes | Struct | Core | Mat+dmg | VFX | Env | BG | Landmark | Music | Amb | Cine | Status |
|---:|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 61 | A Predictable World | Civitas district gateway | tall_mast | 0/2 | -- | 9/9 | 8/8 | 0/3 | -- | -- sensor_tower | -- | ok | 0/2 | missing |
| 62 | The Profile | Identity processing structure | tall_mast | 0/2 | -- | 9/9 | 8/8 | 0/3 | -- | -- sensor_tower | -- | ok | n/a | missing |
| 63 | The Forecast | Prediction server array | arc_over_wall | 0/3 | -- | 9/9 | 8/8 | 0/3 | -- | -- sensor_tower | -- | ok | n/a | missing |
| 64 | Access Denied | Civic access relay | glass_screen | 0/3 | -- | 12/12 | 9/9 | 0/3 | -- | -- sensor_tower | -- | ok | n/a | missing |
| 65 | The Invisible Rule | Policy automation tower | domino_row, arc_over_wall | 0/4 | -- | 12/12 | 9/9 | 0/3 | -- | -- sensor_tower | -- | ok | n/a | missing |
| 66 | Quiet Signals | Behavioural data exchange | wide_platform | 0/4 | -- | 12/12 | 9/9 | 0/3 | -- | -- screen_wall | -- | ok | n/a | missing |
| 67 | The Approved Path | Mobility control structure | support_bridge | 0/2 | -- | 9/9 | 8/8 | 0/3 | -- | -- screen_wall | -- | ok | n/a | missing |
| 68 | The Exception | Human review centre | topple_line | 0/3 | n/a | 9/9 | 7/7 | 0/3 | -- | -- screen_wall | -- | ok | n/a | missing |
| 69 | Public Safety | Emergency prediction node | linked_bridge, chain_cell | 0/4 | -- | 12/12 | 9/9 | 0/3 | -- | -- screen_wall | -- | ok | n/a | missing |
| 70 | The Mirror | Civic model archive | frame | 0/3 | -- | 12/12 | 9/9 | 0/3 | -- | -- screen_wall | -- | ok | n/a | missing |
| 71 | The Model Knows | Forecast compute tower | multi_tier | 0/3 | -- | 9/9 | 8/8 | 0/3 | -- | -- prediction_room | -- | ok | n/a | missing |
| 72 | Prewritten | Scenario archive | arc_over_wall | 0/3 | -- | 9/9 | 8/8 | 0/3 | -- | -- prediction_room | -- | ok | n/a | missing |
| 73 | The Shared Signature | Cross-industry relay | linked_bridge, chain_cell | 0/4 | -- | 12/12 | 9/9 | 0/3 | -- | -- prediction_room | -- | ok | n/a | missing |
| 74 | The Quiet Cage | Central surveillance exchange | wide_platform | 0/4 | -- | 12/12 | 9/9 | 0/3 | -- | -- prediction_room | -- | ok | n/a | missing |
| 75 | No Unknowns | Forecast control hall | mixed_material | 0/4 | -- | 12/12 | 9/9 | 0/3 | -- | -- prediction_room | -- | ok | n/a | missing |
| 76 | The Future File | Encrypted timeline vault | heavy_cap, topple_line | 0/4 | -- | 12/12 | 9/9 | 0/3 | -- | -- relay_spire | -- | ok | n/a | missing |
| 77 | The Missing Year | Timeline indexing structure | twin_towers | 0/3 | -- | 9/9 | 8/8 | 0/3 | -- | -- relay_spire | -- | ok | n/a | missing |
| 78 | Source Code | Prediction engine supports | arc_over_wall, ledges | 0/4 | -- | 12/12 | 8/8 | 0/3 | -- | -- relay_spire | -- | ok | n/a | missing |
| 79 | The Last Forecast | Central Civitas structure | multi_tier | 0/3 | -- | 9/9 | 8/8 | 0/3 | -- | -- relay_spire | -- | ok | n/a | missing |
| 80 | The Quiet Cage | Civitas prediction core | finale | 0/10 | -- | 18/18 | 10/10 | 0/3 | -- | -- relay_spire | -- | ok | 0/1 | missing |

## Chapter 5: Meridian (The Convergence), levels 81-100

| L | Name | Story target | Archetypes | Struct | Core | Mat+dmg | VFX | Env | BG | Landmark | Music | Amb | Cine | Status |
|---:|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 81 | No Public Record | Meridian outer access | exposed_target | 0/1 | -- | 6/6 | 7/7 | 0/3 | -- | -- hybrid_stack | -- | ok | 0/2 | missing |
| 82 | Beneath the City | Underground support structures | multi_tier | 0/3 | -- | 12/12 | 9/9 | 0/3 | -- | -- hybrid_stack | -- | ok | n/a | missing |
| 83 | Four Foundations | Combined server, lab and reactor structures | wide_platform | 0/4 | -- | 15/15 | 9/9 | 0/3 | -- | -- hybrid_stack | -- | ok | n/a | missing |
| 84 | The Common Model | Shared prediction array | arc_over_wall, ledges | 0/4 | -- | 12/12 | 9/9 | 0/3 | -- | -- hybrid_stack | -- | ok | n/a | missing |
| 85 | The Hidden Budget | Resource and power hub | heavy_cap | 0/2 | -- | 9/9 | 8/8 | 0/3 | -- | -- hybrid_stack | -- | ok | n/a | missing |
| 86 | The First Directive | Directive relay | domino_row, ledges | 0/4 | -- | 9/9 | 8/8 | 0/3 | -- | -- foundation_pillars | -- | ok | n/a | missing |
| 87 | The Operator | Central control structure | frame | 0/3 | -- | 12/12 | 9/9 | 0/3 | -- | -- foundation_pillars | -- | ok | n/a | missing |
| 88 | The Convergence Engine | Multi-support core | multi_tier | 0/3 | -- | 12/12 | 9/9 | 0/3 | -- | -- foundation_pillars | -- | ok | n/a | missing |
| 89 | The Failsafe Network | Redundant relay structures | linked_bridge | 0/3 | -- | 12/12 | 8/8 | 0/3 | -- | -- foundation_pillars | -- | ok | n/a | missing |
| 90 | The Other Timeline | Simulation chamber | linked_bridge, ledges, chain_cell | 0/6 | -- | 12/12 | 8/8 | 0/3 | -- | -- foundation_pillars | -- | ok | n/a | missing |
| 91 | The Chosen Outcome | Forecast selection array | ring, chain_cell | 0/4 | -- | 12/12 | 8/8 | 0/3 | -- | -- temporal_anchor | -- | ok | n/a | missing |
| 92 | The Human Variable | Human oversight structure | topple_line, mixed_material | 0/5 | n/a | 12/12 | 8/8 | 0/3 | -- | -- temporal_anchor | -- | ok | n/a | missing |
| 93 | The Last Safeguard | Containment supports | heavy_cap, frame | 0/4 | -- | 12/12 | 9/9 | 0/3 | -- | -- temporal_anchor | -- | ok | n/a | missing |
| 94 | Break the Chain | Linked infrastructure | domino_row, chain_cell | 0/3 | -- | 9/9 | 8/8 | 0/3 | -- | -- temporal_anchor | -- | ok | n/a | missing |
| 95 | The Core Directive | Main directive chamber | multi_tier | 0/3 | -- | 12/12 | 9/9 | 0/3 | -- | -- temporal_anchor | -- | ok | n/a | missing |
| 96 | Before the Beginning | Historical archive structure | arc_over_wall | 0/3 | -- | 9/9 | 8/8 | 0/3 | -- | -- convergence_chamber | -- | ok | n/a | missing |
| 97 | The Final Relay | Temporal relay structure | linked_bridge, chain_cell | 0/4 | -- | 12/12 | 8/8 | 0/3 | -- | -- convergence_chamber | -- | ok | n/a | missing |
| 98 | No Return Path | Time-synchronisation supports | mixed_material | 0/4 | -- | 12/12 | 9/9 | 0/3 | -- | -- convergence_chamber | -- | ok | n/a | missing |
| 99 | The Last Structure | Final support array | multi_tier, wide_platform | 0/4 | -- | 15/15 | 9/9 | 0/3 | -- | -- convergence_chamber | -- | ok | n/a | missing |
| 100 | The Wrong Future | Meridian central core | finale, ring | 0/11 | -- | 21/21 | 11/11 | 0/3 | -- | -- convergence_chamber | -- | ok | 0/2 | missing |

## Missing assets ranked by levels affected

| Wanted asset (id pattern) | Levels | First level |
|---|---:|---:|
| `HLX-ENV-<STRUCTURE>-A` | 20 | 1 |
| `HLX-ENV-BACK_WALL-A` | 20 | 1 |
| `HLX-ENV-FLOOR-A` | 20 | 1 |
| `VTA-CMP-GENE_VAULT_CORE-A` | 20 | 21 |
| `VTA-DEB-GENE_VAULT_CORE-A` | 20 | 21 |
| `VTA-ENV-<STRUCTURE>-A` | 20 | 21 |
| `VTA-ENV-BACK_WALL-A` | 20 | 21 |
| `VTA-ENV-FLOOR-A` | 20 | 21 |
| `NVG-CMP-REACTOR_CORE-A` | 20 | 41 |
| `NVG-DEB-REACTOR_CORE-A` | 20 | 41 |
| `NVG-ENV-<STRUCTURE>-A` | 20 | 41 |
| `NVG-ENV-BACK_WALL-A` | 20 | 41 |
| `NVG-ENV-FLOOR-A` | 20 | 41 |
| `CVT-ENV-<STRUCTURE>-A` | 20 | 61 |
| `CVT-ENV-BACK_WALL-A` | 20 | 61 |
| `CVT-ENV-FLOOR-A` | 20 | 61 |
| `MRD-ENV-<STRUCTURE>-A` | 20 | 81 |
| `MRD-ENV-BACK_WALL-A` | 20 | 81 |
| `MRD-ENV-FLOOR-A` | 20 | 81 |
| `CVT-CMP-SURVEILLANCE_CORE-A` | 19 | 61 |
| `CVT-DEB-SURVEILLANCE_CORE-A` | 19 | 61 |
| `MRD-CMP-CONVERGENCE_CORE-A` | 19 | 81 |
| `MRD-DEB-CONVERGENCE_CORE-A` | 19 | 81 |
| `HLX-CMP-AI_CORE-A` | 18 | 1 |
| `HLX-DEB-AI_CORE-A` | 18 | 1 |
| `VTA-CMP-LAB_COLUMN-A` | 18 | 21 |
| `MRD-CMP-CONVERGENCE_DECK-A` | 18 | 81 |
| `NVG-CMP-GRID_PYLON-A` | 17 | 41 |
| `CVT-CMP-RELAY_BRIDGE-A` | 17 | 63 |
| `MRD-CMP-ANCHOR_COLUMN-A` | 17 | 82 |
| `HLX-MUS-GAMEPLAY-01` | 15 | 1 |
| `VTA-MUS-GAMEPLAY-01` | 15 | 21 |
| `NVG-CMP-CABLE_BRIDGE-A` | 15 | 41 |
| `NVG-MUS-GAMEPLAY-01` | 15 | 41 |
| `CVT-MUS-GAMEPLAY-01` | 15 | 61 |
| `CVT-CMP-CIVIC_COLUMN-A` | 15 | 64 |
| `MRD-MUS-GAMEPLAY-01` | 15 | 81 |
| `VTA-CMP-LAB_DECK-A` | 14 | 21 |
| `HLX-CMP-SERVICE_DECK-A` | 13 | 1 |
| `HLX-CMP-SUPPORT_COLUMN-A` | 13 | 3 |
| `SHR-CMP-GENERIC_BLOCK_STEEL-A` | 12 | 28 |
| `VTA-CMP-CONTAINMENT_CAP-A` | 8 | 24 |
| `CVT-CMP-DATA_EXCHANGE_RACK-A` | 8 | 66 |
| `MRD-CMP-MONOLITH_SLAB-A` | 8 | 84 |
| `HLX-CMP-DATA_CRATE-A` | 7 | 4 |
| `VTA-CMP-CLEANROOM_PANEL-A` | 7 | 21 |
| `VTA-CMP-SPECIMEN_RACK-A` | 7 | 22 |
| `SHR-CMP-GENERIC_BLOCK_ALLOY-A` | 7 | 23 |
| `NVG-CMP-CONTAINMENT_WALL-A` | 7 | 42 |
| `CVT-CMP-SENSOR_MAST-A` | 7 | 61 |
| `MRD-CMP-TIMELINE_RELAY-A` | 7 | 83 |
| `NVG-CMP-TRANSFORMER-A` | 6 | 44 |
| `CVT-CMP-SECURITY_WALL-A` | 6 | 63 |
| `MRD-CMP-QUANTUM_STABILIZER-A` | 6 | 82 |
| `HLX-BG-FAR-A` | 5 | 1 |
| `HLX-PRP-RELAY_ARRAY-A` | 5 | 1 |
| `HLX-CMP-SERVER_RACK-A` | 5 | 4 |
| `HLX-BG-FAR-B` | 5 | 6 |
| `HLX-PRP-LOGISTICS_CRANE-A` | 5 | 6 |
| `SHR-CMP-GENERIC_BLOCK_CONCRETE-A` | 5 | 7 |
| `HLX-BG-FAR-C` | 5 | 11 |
| `HLX-PRP-COOLING_TOWER-A` | 5 | 11 |
| `HLX-BG-FAR-D` | 5 | 16 |
| `HLX-PRP-AURA_CORE_CHAMBER-A` | 5 | 16 |
| `VTA-BG-FAR-A` | 5 | 21 |
| `VTA-PRP-CLEANROOM_AIRLOCK-A` | 5 | 21 |
| `VTA-BG-FAR-B` | 5 | 26 |
| `VTA-PRP-BIOREACTOR_BANK-A` | 5 | 26 |
| `VTA-BG-FAR-C` | 5 | 31 |
| `VTA-PRP-ARCHIVE_VAULT-A` | 5 | 31 |
| `VTA-BG-FAR-D` | 5 | 36 |
| `VTA-PRP-GROWTH_CHAMBER-A` | 5 | 36 |
| `NVG-BG-FAR-A` | 5 | 41 |
| `NVG-PRP-INTAKE_TURBINE-A` | 5 | 41 |
| `NVG-BG-FAR-B` | 5 | 46 |
| `NVG-PRP-COOLING_TOWER-A` | 5 | 46 |
| `NVG-CMP-CAPACITOR_CELL-A` | 5 | 48 |
| `NVG-BG-FAR-C` | 5 | 51 |
| `NVG-PRP-TRANSFORMER_YARD-A` | 5 | 51 |
| `NVG-BG-FAR-D` | 5 | 56 |
| `NVG-PRP-REACTOR_RING-A` | 5 | 56 |
| `CVT-BG-FAR-A` | 5 | 61 |
| `CVT-PRP-SENSOR_TOWER-A` | 5 | 61 |
| `CVT-BG-FAR-B` | 5 | 66 |
| `CVT-PRP-SCREEN_WALL-A` | 5 | 66 |
| `CVT-BG-FAR-C` | 5 | 71 |
| `CVT-PRP-PREDICTION_ROOM-A` | 5 | 71 |
| `CVT-BG-FAR-D` | 5 | 76 |
| `CVT-PRP-RELAY_SPIRE-A` | 5 | 76 |
| `MRD-BG-FAR-A` | 5 | 81 |
| `MRD-PRP-HYBRID_STACK-A` | 5 | 81 |
| `MRD-BG-FAR-B` | 5 | 86 |
| `MRD-PRP-FOUNDATION_PILLARS-A` | 5 | 86 |
| `MRD-CMP-TEMPORAL_CELL-A` | 5 | 90 |
| `MRD-BG-FAR-C` | 5 | 91 |
| `MRD-PRP-TEMPORAL_ANCHOR-A` | 5 | 91 |
| `MRD-BG-FAR-D` | 5 | 96 |
| `MRD-PRP-CONVERGENCE_CHAMBER-A` | 5 | 96 |
| `HLX-CMP-CONTROL_POD_GLASS-A` | 4 | 5 |
| `HLX-ENV-STATIC_LEDGE-A` | 4 | 11 |
| `HLX-MUS-COMBAT-01` | 4 | 16 |
| `VTA-MUS-COMBAT-01` | 4 | 36 |
| `NVG-ENV-STATIC_LEDGE-A` | 4 | 45 |
| `NVG-MUS-COMBAT-01` | 4 | 56 |
| `CVT-ENV-STATIC_LEDGE-A` | 4 | 63 |
| `CVT-MUS-COMBAT-01` | 4 | 76 |
| `MRD-ENV-STATIC_LEDGE-A` | 4 | 84 |
| `MRD-MUS-COMBAT-01` | 4 | 96 |
| `HLX-CMP-POWER_CELL-A` | 3 | 6 |
| `HLX-CMP-BLAST_WALL-A` | 3 | 11 |
| `VTA-CMP-CRYO_CELL-A` | 3 | 29 |
| `NVG-CMP-CONTAINMENT_RING_SEGMENT-A` | 3 | 43 |
| `SHR-CMP-GENERIC_PANEL_GLASS-A` | 3 | 49 |
| `CVT-CMP-SENSOR_ARRAY-A` | 3 | 61 |
| `CVT-CMP-CIVIC_SCREEN-A` | 3 | 64 |
| `MRD-CMP-PHASE_SHIELD-A` | 3 | 92 |
| `HLX-CMP-RELAY_DISH-A` | 2 | 2 |
| `HLX-CMP-RELAY_MAST-A` | 2 | 2 |
| `HLX-CMP-CORE_SHIELD-A` | 2 | 14 |
| `VTA-ENV-STATIC_LEDGE-A` | 2 | 31 |
| ... 25 more in coverage_matrix.json | | |

## How requirements are derived

- Structural components: each level's layout archetypes (from the puzzle notes in `docs/level-design-spec.md`) give structural roles; each chapter maps roles to its component kinds (ASSET_CONTRACT section 5). A chapter kind with only a shared generic block of the same physics material counts as fallback.
- Critical asset: the chapter core kind plus its debris set, except pure topple levels 9, 17, 68 and 92.
- Materials: a texture set per physics material used (chapter set, or shared as fallback) plus light and heavy damage overlays.
- VFX: weapon effects for every level plus material-specific destruction effects and the critical destruction effect.
- Environment: chapter floor, back wall and mid-back structures; a far background layer rotated by band.
- Story targets and breadcrumbs come from the mission map in `docs/narrative-bible.md` section 9; they steer dressing and landmark choice per level.
- Variety: one landmark prop per band of five levels (four per chapter, 20 in total) and two dressing props rotated from the chapter prop pool.
- Music: chapter gameplay theme for bands 1-3, combat theme for band 4, boss or finale theme on levels 20/40/60/80/100. Ambience by band with the chapter bed as fallback. Cinematics on chapter intros, outros, the opening (level 1) and the finale (level 100).

