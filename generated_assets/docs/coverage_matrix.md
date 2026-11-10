# 100-level asset coverage matrix

Generated 2026-11-10 by `generated_assets/tools/build_coverage_matrix.py` from the merged manifest (updated 2026-11-10, 1469 entries on disk, 1294 production entries; concepts and mock layouts do not count). Do not edit by hand; re-run the script.

Status: `ok` available, `fb` shared fallback only, `--` missing. Group columns show available/required.
A level is **full** when every requirement is available, **fallback** when nothing is missing but shared substitutes are used.

## Summary

- Levels fully covered: **100 / 100**; covered with fallbacks: 0; with missing assets: 0.
- Requirements available: 3236 / 3236 level-requirement slots.
- Game-wide requirements available: 36 / 36.

| Chapter | Full | Fallback | Missing |
|---|---:|---:|---:|
| helix | 20 | 0 | 0 |
| vita | 20 | 0 | 0 |
| nova_grid | 20 | 0 | 0 |
| civitas | 20 | 0 | 0 |
| meridian | 20 | 0 | 0 |

Layout archetype use across the campaign (variety check): chain_cell 14, arc_over_wall 13, heavy_cap 9, multi_tier 9, linked_bridge 9, ledges 7, glass_screen 6, domino_row 6, twin_towers 6, frame 6, support_bridge 5, topple_line 5, finale 5, mixed_material 5, ring 5, wide_platform 5, glass_roof 4, tall_mast 3, stack_tower 3, chain_towers 3, indirect_shield 3, exposed_target 2, pyramid 1.

## Game-wide

| Requirement | Status | Assets |
|---|---|---|
| Operative character mesh | ok | OPR-CHR-OPERATIVE-A |
| Operative animations | ok | OPR-ANM-OPERATIVE-AIM_POSE, OPR-ANM-OPERATIVE-DEFEAT, OPR-ANM-OPERATIVE-FIRE_RECOIL |
| Kinetic Accelerator weapon | ok | OPR-WPN-KINETIC_ACCELERATOR-A, OPR-WPN-KINETIC_ACCELERATOR-B, OPR-WPN-KINETIC_ACCELERATOR-C |
| Breach Charge launcher | ok | OPR-WPN-BREACH_CHARGE-A, OPR-WPN-BREACH_CHARGE-B, OPR-WPN-BREACH_CHARGE-C |
| Kinetic projectile | ok | OPR-PRJ-KINETIC_SLUG-A |
| Breach canister projectile | ok | OPR-PRJ-BREACH_CANISTER-A |
| HUD elements (weapon slots, ammo, cooldown, reticle, trajectory) | ok | GAM-UI-AIM_RETICLE-A, GAM-UI-AMMO_PIP_BREACH_EMPTY-A, GAM-UI-AMMO_PIP_BREACH_FULL-A |
| Critical asset target marker | ok | GAM-UI-CRITICAL_MARKER_ALL-A, GAM-UI-CRITICAL_MARKER_BRACKETS-A, GAM-UI-CRITICAL_MARKER_DIAMOND-A |
| Objective markers | ok | GAM-UI-OBJECTIVE_MARKER_COMPLETE-A, GAM-UI-OBJECTIVE_MARKER_FAILED-A, GAM-UI-OBJECTIVE_MARKER_OPTIONAL-A |
| Weapon icons | ok | GAM-ICN-WEAPON_BREACH_CHARGE-A, GAM-ICN-WEAPON_DISRUPTOR-A, GAM-ICN-WEAPON_KINETIC_ACCELERATOR-A |
| Objective icons | ok | GAM-ICN-OBJECTIVE_COMPLETE-A, GAM-ICN-OBJECTIVE_FAILED-A, GAM-ICN-OBJECTIVE_OPTIONAL-A |
| Panels and buttons (9-slice kit) | ok | GAM-UI-BUTTON_DANGER_DISABLED-A, GAM-UI-BUTTON_DANGER_HOVER-A, GAM-UI-BUTTON_DANGER_NORMAL-A |
| Main menu backdrop | ok | GAM-BG-MAIN_MENU-A, GAM-BG-MAIN_MENU-B |
| Loading backdrop | ok | CVT-BG-LOADING-A, GAM-BG-LOADING-A, HLX-BG-LOADING-A |
| Chapter cards and upgrade tier badges | ok | GAM-UI-CARD_CHAPTER_CIVITAS_LOCKED-A, GAM-UI-CARD_CHAPTER_CIVITAS_NORMAL-A, GAM-UI-CARD_CHAPTER_CIVITAS_SELECTED-A |
| Chapter title treatments | ok | GAM-UI-CHAPTER_TITLE_DECO-01_1X, GAM-UI-CHAPTER_TITLE_DECO-01_2X, GAM-UI-CHAPTER_TITLE_DECO-02_1X |
| Screen layout references (menus, HUD, results, map, upgrades) | ok | GAM-UI-SCREEN_CHAPTER_MAP_01_HELIX-MOCK, GAM-UI-SCREEN_CHAPTER_MAP_02_VITA-MOCK, GAM-UI-SCREEN_CHAPTER_MAP_03_NOVA_GRID-MOCK |
| Godot theme spec | ok | GAM-UI-THEME_SPEC-A |
| Topple threshold marker | ok | SHR-VFX-THRESHOLD_LINE-A |
| Game logo | ok | GAM-LOGO-COMPACT-COLOUR, GAM-LOGO-COMPACT-COLOUR_ON_LIGHT, GAM-LOGO-COMPACT-LIGHT_ON_DARK |
| App icon | ok | GAM-LOGO-APP_ICON-192, GAM-LOGO-APP_ICON-256, GAM-LOGO-APP_ICON-48 |
| Splash screen | ok | GAM-UI-SPLASH-1280X720, GAM-UI-SPLASH-2560X1440, GAM-UI-SPLASH-LOGO_TRANSPARENT |
| UI font | ok | GAM-FNT-BARLOW-BOLD, GAM-FNT-BARLOW-MEDIUM, GAM-FNT-BARLOW-REGULAR |
| Menu music | ok | GAM-MUS-MAIN_THEME-01, GAM-MUS-MENU-01 |
| Victory stinger | ok | GAM-MUS-VICTORY-CHAPTER, GAM-MUS-VICTORY-MISSION, GAM-SFX-UI_VICTORY-01 |
| Defeat stinger | ok | GAM-MUS-DEFEAT-MISSION, GAM-SFX-UI_DEFEAT-01, SHR-SFX-MACHINE_FAILURE-01 |
| Ending music | ok | GAM-MUS-ENDING-CREDITS |
| Kinetic fire SFX | ok | OPR-SFX-KINETIC_CHARGE-01, OPR-SFX-KINETIC_CHARGE-02, OPR-SFX-KINETIC_CHARGE-03 |
| Breach launch / detonation SFX | ok | OPR-SFX-BREACH_ARM-01, OPR-SFX-BREACH_ARM-02, OPR-SFX-BREACH_ARM-03 |
| Metal impact SFX | ok | SHR-SFX-IMPACT_METAL-01, SHR-SFX-IMPACT_METAL-02, SHR-SFX-IMPACT_METAL-03 |
| Glass break SFX | ok | SHR-SFX-IMPACT_GLASS-01, SHR-SFX-IMPACT_GLASS-02, SHR-SFX-IMPACT_GLASS-03 |
| Concrete break SFX | ok | SHR-SFX-IMPACT_CONCRETE-01, SHR-SFX-IMPACT_CONCRETE-02, SHR-SFX-IMPACT_CONCRETE-03 |
| Electrical / machinery SFX | ok | OPR-SFX-SUIT_SERVO-01, OPR-SFX-SUIT_SERVO-02, OPR-SFX-SUIT_SERVO-03 |
| UI SFX | ok | GAM-SFX-UI_ACHIEVEMENT-01, GAM-SFX-UI_BACK-01, GAM-SFX-UI_BACK-02 |
| Alarm SFX | ok | SHR-SFX-ALARM_KLAXON-01, SHR-SFX-ALARM_PULSE-01, SHR-SFX-ALARM_SIREN-01 |
| Opening cinematic | ok | GAM-CIN-OPENING-01, GAM-CIN-OPENING-02, GAM-CIN-OPENING-03 |

## Chapter 1: Helix Systems (The Machine That Decided), levels 1-20

| L | Name | Story target | Archetypes | Struct | Core | Mat+dmg | VFX | Env | BG | Landmark | Music | Amb | Cine | Status |
|---:|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | First Contact | Helix perimeter relay | exposed_target | 1/1 | ok | 6/6 | 7/7 | 3/3 | ok | ok relay_array | ok | ok | 3/3 | full |
| 2 | The Welcome System | Automated security gate | tall_mast | 2/2 | ok | 9/9 | 8/8 | 3/3 | ok | ok relay_array | ok | ok | n/a | full |
| 3 | Traffic of One | Autonomous traffic-control tower | support_bridge | 2/2 | ok | 9/9 | 8/8 | 3/3 | ok | ok relay_array | ok | ok | n/a | full |
| 4 | Supply Chain | Logistics sorting structure | stack_tower | 2/2 | ok | 9/9 | 7/7 | 3/3 | ok | ok relay_array | ok | ok | n/a | full |
| 5 | The Safety Layer | Emergency-response relay | glass_screen | 3/3 | ok | 12/12 | 9/9 | 3/3 | ok | ok relay_array | ok | ok | n/a | full |
| 6 | Cold Storage | Server-cooling array | chain_towers, chain_cell | 3/3 | ok | 12/12 | 8/8 | 3/3 | ok | ok logistics_crane | ok | ok | n/a | full |
| 7 | Blind Spot | Surveillance exchange | heavy_cap | 2/2 | ok | 9/9 | 8/8 | 3/3 | ok | ok logistics_crane | ok | ok | n/a | full |
| 8 | Human Override | Manual control station | domino_row | 2/2 | ok | 9/9 | 8/8 | 3/3 | ok | ok logistics_crane | ok | ok | n/a | full |
| 9 | Redundancy | Backup server stacks | topple_line | 3/3 | n/a | 6/6 | 6/6 | 3/3 | ok | ok logistics_crane | ok | ok | n/a | full |
| 10 | The Replica | Replication hub | twin_towers | 3/3 | ok | 12/12 | 8/8 | 3/3 | ok | ok logistics_crane | ok | ok | n/a | full |
| 11 | Priority One | Resource-allocation centre | arc_over_wall | 3/3 | ok | 9/9 | 8/8 | 3/3 | ok | ok cooling_tower | ok | ok | n/a | full |
| 12 | No Exceptions | Compliance processing facility | pyramid | 2/2 | ok | 6/6 | 7/7 | 3/3 | ok | ok cooling_tower | ok | ok | n/a | full |
| 13 | The Quiet District | Local control tower | glass_roof | 2/2 | ok | 9/9 | 8/8 | 3/3 | ok | ok cooling_tower | ok | ok | n/a | full |
| 14 | Root Access | Core routing structure | indirect_shield | 3/3 | ok | 12/12 | 8/8 | 3/3 | ok | ok cooling_tower | ok | ok | n/a | full |
| 15 | The Directive | Directive archive | twin_towers, glass_screen | 4/4 | ok | 15/15 | 9/9 | 3/3 | ok | ok cooling_tower | ok | ok | n/a | full |
| 16 | Failsafe | Emergency power structure | ledges | 2/2 | ok | 6/6 | 7/7 | 3/3 | ok | ok aura_core_chamber | ok | ok | n/a | full |
| 17 | Last Backup | Cold backup vault | topple_line | 3/3 | n/a | 6/6 | 6/6 | 3/3 | ok | ok aura_core_chamber | ok | ok | n/a | full |
| 18 | Cascade | Multi-node operations hall | arc_over_wall | 3/3 | ok | 9/9 | 8/8 | 3/3 | ok | ok aura_core_chamber | ok | ok | n/a | full |
| 19 | Central Logic | AURA central operations structure | domino_row, ledges, chain_cell | 5/5 | ok | 12/12 | 9/9 | 3/3 | ok | ok aura_core_chamber | ok | ok | n/a | full |
| 20 | The Machine That Decided | Helix central core | finale | 10/10 | ok | 21/21 | 10/10 | 3/3 | ok | ok aura_core_chamber | ok | ok | 1/1 | full |

## Chapter 2: VITA Genomics (The Price of Perfection), levels 21-40

| L | Name | Story target | Archetypes | Struct | Core | Mat+dmg | VFX | Env | BG | Landmark | Music | Amb | Cine | Status |
|---:|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 21 | A Longer Life | VITA campus entrance | glass_screen | 3/3 | ok | 12/12 | 9/9 | 3/3 | ok | ok cleanroom_airlock | ok | ok | 2/2 | full |
| 22 | Clean Room | Sterile research structures | glass_screen, chain_towers | 4/4 | ok | 15/15 | 9/9 | 3/3 | ok | ok cleanroom_airlock | ok | ok | n/a | full |
| 23 | The Sequence | Genomics analysis racks | stack_tower | 2/2 | ok | 9/9 | 7/7 | 3/3 | ok | ok cleanroom_airlock | ok | ok | n/a | full |
| 24 | Growth Chamber | Bioreactor support frame | heavy_cap, glass_roof | 3/3 | ok | 12/12 | 9/9 | 3/3 | ok | ok cleanroom_airlock | ok | ok | n/a | full |
| 25 | Trial Run | Clinical automation hub | twin_towers | 3/3 | ok | 12/12 | 8/8 | 3/3 | ok | ok cleanroom_airlock | ok | ok | n/a | full |
| 26 | Better Than Human | Enhancement lab | multi_tier | 3/3 | ok | 12/12 | 8/8 | 3/3 | ok | ok bioreactor_bank | ok | ok | n/a | full |
| 27 | Cold Chain | Distribution and storage racks | support_bridge, heavy_cap | 3/3 | ok | 12/12 | 9/9 | 3/3 | ok | ok bioreactor_bank | ok | ok | n/a | full |
| 28 | The Dependency | Life-support research infrastructure | indirect_shield | 3/3 | ok | 9/9 | 7/7 | 3/3 | ok | ok bioreactor_bank | ok | ok | n/a | full |
| 29 | Replication Error | Containment support structure | linked_bridge, chain_cell | 4/4 | ok | 12/12 | 9/9 | 3/3 | ok | ok bioreactor_bank | ok | ok | n/a | full |
| 30 | Controlled Growth | Production line | glass_screen | 3/3 | ok | 12/12 | 9/9 | 3/3 | ok | ok bioreactor_bank | ok | ok | n/a | full |
| 31 | The Patent Wall | Research archive stacks | arc_over_wall | 3/3 | ok | 9/9 | 8/8 | 3/3 | ok | ok archive_vault | ok | ok | n/a | full |
| 32 | Patient Zero | Sealed trial wing | heavy_cap | 2/2 | ok | 9/9 | 8/8 | 3/3 | ok | ok archive_vault | ok | ok | n/a | full |
| 33 | The Upgrade | Automated treatment platform | mixed_material | 4/4 | ok | 12/12 | 9/9 | 3/3 | ok | ok archive_vault | ok | ok | n/a | full |
| 34 | The Price | Resource and cooling structure | heavy_cap | 2/2 | ok | 9/9 | 8/8 | 3/3 | ok | ok archive_vault | ok | ok | n/a | full |
| 35 | No Consent | Data and trial control centre | frame | 3/3 | ok | 12/12 | 8/8 | 3/3 | ok | ok archive_vault | ok | ok | n/a | full |
| 36 | The Black Archive | Encrypted research vault | glass_roof, arc_over_wall | 5/5 | ok | 15/15 | 10/10 | 3/3 | ok | ok growth_chamber | ok | ok | n/a | full |
| 37 | The Prediction | Forecast computation hall | multi_tier | 3/3 | ok | 12/12 | 8/8 | 3/3 | ok | ok growth_chamber | ok | ok | n/a | full |
| 38 | The Last Batch | Production support array | twin_towers | 3/3 | ok | 12/12 | 8/8 | 3/3 | ok | ok growth_chamber | ok | ok | n/a | full |
| 39 | Dependency Chain | Central VITA support structure | linked_bridge, chain_cell | 4/4 | ok | 12/12 | 9/9 | 3/3 | ok | ok growth_chamber | ok | ok | n/a | full |
| 40 | The Price of Perfection | VITA research core | finale | 10/10 | ok | 24/24 | 11/11 | 3/3 | ok | ok growth_chamber | ok | ok | 1/1 | full |

## Chapter 3: Nova Grid (The Energy Beneath), levels 41-60

| L | Name | Story target | Archetypes | Struct | Core | Mat+dmg | VFX | Env | BG | Landmark | Music | Amb | Cine | Status |
|---:|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 41 | Endless Power | Nova Grid perimeter | support_bridge | 2/2 | ok | 9/9 | 8/8 | 3/3 | ok | ok intake_turbine | ok | ok | 2/2 | full |
| 42 | The Intake | Energy capture structure | frame | 3/3 | ok | 12/12 | 9/9 | 3/3 | ok | ok intake_turbine | ok | ok | n/a | full |
| 43 | Containment Ring | Reactor support ring | ring | 3/3 | ok | 9/9 | 8/8 | 3/3 | ok | ok intake_turbine | ok | ok | n/a | full |
| 44 | Cooling the Future | Cooling tower array | chain_towers | 2/2 | ok | 9/9 | 8/8 | 3/3 | ok | ok intake_turbine | ok | ok | n/a | full |
| 45 | The First Pulse | Resonance relay | arc_over_wall | 3/3 | ok | 9/9 | 8/8 | 3/3 | ok | ok intake_turbine | ok | ok | n/a | full |
| 46 | Load Balancing | Distribution tower | support_bridge | 2/2 | ok | 9/9 | 8/8 | 3/3 | ok | ok cooling_tower | ok | ok | n/a | full |
| 47 | Deep Storage | Energy storage racks | stack_tower | 2/2 | ok | 9/9 | 8/8 | 3/3 | ok | ok cooling_tower | ok | ok | n/a | full |
| 48 | Silent Alarm | Monitoring station | linked_bridge, chain_cell | 4/4 | ok | 9/9 | 8/8 | 3/3 | ok | ok cooling_tower | ok | ok | n/a | full |
| 49 | Overload Window | Power conversion array | mixed_material | 4/4 | ok | 12/12 | 9/9 | 3/3 | ok | ok cooling_tower | ok | ok | n/a | full |
| 50 | The Resonance | Main containment platform | ring, chain_cell | 4/4 | ok | 9/9 | 8/8 | 3/3 | ok | ok cooling_tower | ok | ok | n/a | full |
| 51 | Beyond the Grid | Long-distance relay | arc_over_wall | 3/3 | ok | 9/9 | 8/8 | 3/3 | ok | ok transformer_yard | ok | ok | n/a | full |
| 52 | The Wrong Frequency | Signal processing array | ledges, twin_towers | 5/5 | ok | 12/12 | 9/9 | 3/3 | ok | ok transformer_yard | ok | ok | n/a | full |
| 53 | The Deep Core | Reactor service structure | heavy_cap | 2/2 | ok | 9/9 | 8/8 | 3/3 | ok | ok transformer_yard | ok | ok | n/a | full |
| 54 | Blackout Protocol | Backup power structures | linked_bridge | 3/3 | ok | 9/9 | 8/8 | 3/3 | ok | ok transformer_yard | ok | ok | n/a | full |
| 55 | The Echo | Resonance chamber | domino_row, multi_tier, chain_cell | 4/4 | ok | 12/12 | 9/9 | 3/3 | ok | ok transformer_yard | ok | ok | n/a | full |
| 56 | Dead Circuit | Transmission relay | glass_roof, arc_over_wall | 5/5 | ok | 15/15 | 10/10 | 3/3 | ok | ok reactor_ring | ok | ok | n/a | full |
| 57 | Origin Unknown | Data capture structure | indirect_shield | 3/3 | ok | 9/9 | 8/8 | 3/3 | ok | ok reactor_ring | ok | ok | n/a | full |
| 58 | The Listening Machine | Research platform | frame | 3/3 | ok | 12/12 | 9/9 | 3/3 | ok | ok reactor_ring | ok | ok | n/a | full |
| 59 | Final Containment | Central energy supports | wide_platform, chain_cell | 5/5 | ok | 12/12 | 9/9 | 3/3 | ok | ok reactor_ring | ok | ok | n/a | full |
| 60 | The Energy Beneath | Nova Grid core | finale, ring | 11/11 | ok | 18/18 | 11/11 | 3/3 | ok | ok reactor_ring | ok | ok | 1/1 | full |

## Chapter 4: Civitas (The Quiet Cage), levels 61-80

| L | Name | Story target | Archetypes | Struct | Core | Mat+dmg | VFX | Env | BG | Landmark | Music | Amb | Cine | Status |
|---:|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 61 | A Predictable World | Civitas district gateway | tall_mast | 2/2 | ok | 9/9 | 8/8 | 3/3 | ok | ok sensor_tower | ok | ok | 2/2 | full |
| 62 | The Profile | Identity processing structure | tall_mast | 2/2 | ok | 9/9 | 8/8 | 3/3 | ok | ok sensor_tower | ok | ok | n/a | full |
| 63 | The Forecast | Prediction server array | arc_over_wall | 3/3 | ok | 9/9 | 8/8 | 3/3 | ok | ok sensor_tower | ok | ok | n/a | full |
| 64 | Access Denied | Civic access relay | glass_screen | 3/3 | ok | 12/12 | 9/9 | 3/3 | ok | ok sensor_tower | ok | ok | n/a | full |
| 65 | The Invisible Rule | Policy automation tower | domino_row, arc_over_wall | 4/4 | ok | 12/12 | 9/9 | 3/3 | ok | ok sensor_tower | ok | ok | n/a | full |
| 66 | Quiet Signals | Behavioural data exchange | wide_platform | 4/4 | ok | 15/15 | 9/9 | 3/3 | ok | ok screen_wall | ok | ok | n/a | full |
| 67 | The Approved Path | Mobility control structure | support_bridge | 2/2 | ok | 9/9 | 8/8 | 3/3 | ok | ok screen_wall | ok | ok | n/a | full |
| 68 | The Exception | Human review centre | topple_line | 3/3 | n/a | 9/9 | 7/7 | 3/3 | ok | ok screen_wall | ok | ok | n/a | full |
| 69 | Public Safety | Emergency prediction node | linked_bridge, chain_cell | 4/4 | ok | 15/15 | 9/9 | 3/3 | ok | ok screen_wall | ok | ok | n/a | full |
| 70 | The Mirror | Civic model archive | frame | 3/3 | ok | 12/12 | 9/9 | 3/3 | ok | ok screen_wall | ok | ok | n/a | full |
| 71 | The Model Knows | Forecast compute tower | multi_tier | 3/3 | ok | 12/12 | 8/8 | 3/3 | ok | ok prediction_room | ok | ok | n/a | full |
| 72 | Prewritten | Scenario archive | arc_over_wall | 3/3 | ok | 9/9 | 8/8 | 3/3 | ok | ok prediction_room | ok | ok | n/a | full |
| 73 | The Shared Signature | Cross-industry relay | linked_bridge, chain_cell | 4/4 | ok | 15/15 | 9/9 | 3/3 | ok | ok prediction_room | ok | ok | n/a | full |
| 74 | The Quiet Cage | Central surveillance exchange | wide_platform | 4/4 | ok | 15/15 | 9/9 | 3/3 | ok | ok prediction_room | ok | ok | n/a | full |
| 75 | No Unknowns | Forecast control hall | mixed_material | 4/4 | ok | 12/12 | 9/9 | 3/3 | ok | ok prediction_room | ok | ok | n/a | full |
| 76 | The Future File | Encrypted timeline vault | heavy_cap, topple_line | 4/4 | ok | 12/12 | 9/9 | 3/3 | ok | ok relay_spire | ok | ok | n/a | full |
| 77 | The Missing Year | Timeline indexing structure | twin_towers | 3/3 | ok | 12/12 | 8/8 | 3/3 | ok | ok relay_spire | ok | ok | n/a | full |
| 78 | Source Code | Prediction engine supports | arc_over_wall, ledges | 4/4 | ok | 12/12 | 8/8 | 3/3 | ok | ok relay_spire | ok | ok | n/a | full |
| 79 | The Last Forecast | Central Civitas structure | multi_tier | 3/3 | ok | 12/12 | 8/8 | 3/3 | ok | ok relay_spire | ok | ok | n/a | full |
| 80 | The Quiet Cage | Civitas prediction core | finale | 10/10 | ok | 21/21 | 10/10 | 3/3 | ok | ok relay_spire | ok | ok | 1/1 | full |

## Chapter 5: Meridian (The Convergence), levels 81-100

| L | Name | Story target | Archetypes | Struct | Core | Mat+dmg | VFX | Env | BG | Landmark | Music | Amb | Cine | Status |
|---:|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 81 | No Public Record | Meridian outer access | exposed_target | 1/1 | ok | 6/6 | 7/7 | 3/3 | ok | ok hybrid_stack | ok | ok | 2/2 | full |
| 82 | Beneath the City | Underground support structures | multi_tier | 3/3 | ok | 12/12 | 9/9 | 3/3 | ok | ok hybrid_stack | ok | ok | n/a | full |
| 83 | Four Foundations | Combined server, lab and reactor structures | wide_platform | 4/4 | ok | 15/15 | 9/9 | 3/3 | ok | ok hybrid_stack | ok | ok | n/a | full |
| 84 | The Common Model | Shared prediction array | arc_over_wall, ledges | 4/4 | ok | 12/12 | 9/9 | 3/3 | ok | ok hybrid_stack | ok | ok | n/a | full |
| 85 | The Hidden Budget | Resource and power hub | heavy_cap | 2/2 | ok | 9/9 | 8/8 | 3/3 | ok | ok hybrid_stack | ok | ok | n/a | full |
| 86 | The First Directive | Directive relay | domino_row, ledges | 4/4 | ok | 9/9 | 8/8 | 3/3 | ok | ok foundation_pillars | ok | ok | n/a | full |
| 87 | The Operator | Central control structure | frame | 3/3 | ok | 12/12 | 9/9 | 3/3 | ok | ok foundation_pillars | ok | ok | n/a | full |
| 88 | The Convergence Engine | Multi-support core | multi_tier | 3/3 | ok | 12/12 | 9/9 | 3/3 | ok | ok foundation_pillars | ok | ok | n/a | full |
| 89 | The Failsafe Network | Redundant relay structures | linked_bridge | 3/3 | ok | 12/12 | 8/8 | 3/3 | ok | ok foundation_pillars | ok | ok | n/a | full |
| 90 | The Other Timeline | Simulation chamber | linked_bridge, ledges, chain_cell | 6/6 | ok | 12/12 | 8/8 | 3/3 | ok | ok foundation_pillars | ok | ok | n/a | full |
| 91 | The Chosen Outcome | Forecast selection array | ring, chain_cell | 4/4 | ok | 12/12 | 8/8 | 3/3 | ok | ok temporal_anchor | ok | ok | n/a | full |
| 92 | The Human Variable | Human oversight structure | topple_line, mixed_material | 5/5 | n/a | 12/12 | 8/8 | 3/3 | ok | ok temporal_anchor | ok | ok | n/a | full |
| 93 | The Last Safeguard | Containment supports | heavy_cap, frame | 4/4 | ok | 12/12 | 9/9 | 3/3 | ok | ok temporal_anchor | ok | ok | n/a | full |
| 94 | Break the Chain | Linked infrastructure | domino_row, chain_cell | 3/3 | ok | 9/9 | 8/8 | 3/3 | ok | ok temporal_anchor | ok | ok | n/a | full |
| 95 | The Core Directive | Main directive chamber | multi_tier | 3/3 | ok | 12/12 | 9/9 | 3/3 | ok | ok temporal_anchor | ok | ok | n/a | full |
| 96 | Before the Beginning | Historical archive structure | arc_over_wall | 3/3 | ok | 9/9 | 8/8 | 3/3 | ok | ok convergence_chamber | ok | ok | n/a | full |
| 97 | The Final Relay | Temporal relay structure | linked_bridge, chain_cell | 4/4 | ok | 12/12 | 8/8 | 3/3 | ok | ok convergence_chamber | ok | ok | n/a | full |
| 98 | No Return Path | Time-synchronisation supports | mixed_material | 4/4 | ok | 12/12 | 9/9 | 3/3 | ok | ok convergence_chamber | ok | ok | n/a | full |
| 99 | The Last Structure | Final support array | multi_tier, wide_platform | 4/4 | ok | 15/15 | 9/9 | 3/3 | ok | ok convergence_chamber | ok | ok | n/a | full |
| 100 | The Wrong Future | Meridian central core | finale, ring | 11/11 | ok | 21/21 | 11/11 | 3/3 | ok | ok convergence_chamber | ok | ok | 2/2 | full |

## Missing assets ranked by levels affected

| Wanted asset (id pattern) | Levels | First level |
|---|---:|---:|

## How requirements are derived

- Structural components: each level's layout archetypes (from the puzzle notes in `docs/level-design-spec.md`) give structural roles; each chapter maps roles to its component kinds (ASSET_CONTRACT section 5). A chapter kind with only a shared generic block of the same physics material counts as fallback.
- Critical asset: the chapter core kind plus its debris set, except pure topple levels 9, 17, 68 and 92.
- Materials: a texture set per physics material used (chapter set, or shared as fallback) plus light and heavy damage overlays.
- VFX: weapon effects for every level plus material-specific destruction effects and the critical destruction effect.
- Environment: chapter floor, back wall and mid-back structures; a far background layer rotated by band.
- Story targets and breadcrumbs come from the mission map in `docs/narrative-bible.md` section 9; they steer dressing and landmark choice per level.
- Variety: one landmark prop per band of five levels (four per chapter, 20 in total) and two dressing props rotated from the chapter prop pool.
- Music: chapter gameplay theme for bands 1-3, combat theme for band 4, boss or finale theme on levels 20/40/60/80/100. Ambience by band with the chapter bed as fallback. Cinematics on chapter intros, outros, the opening (level 1) and the finale (level 100).

