# Chapter audio plans

Source of truth: `data/audio.json` (`chapters` section). Plan lookup: mission plan, then the plan of the mission's
chapter (`engine.definition.chapter`, 1-5 = helix, vita, nova_grid, civitas, meridian), then the caller's fallback
(`scripts/core/audio_catalog.gd` `plan_for`, used by `scripts/mission/mission_audio.gd`).

Roles per chapter plan: `intensity` = [preparation, tension, combat], `critical_layer`, `victory` / `defeat` (shared
stingers), `ambience` (the bed MissionAudio plays), plus `theme` (chapter intro/select; not played by MissionAudio) and
`boss` (hero missions; not wired to a trigger yet). Other delivered beds are defined as ambience cues for level-specific use.

## Levels and loudness

- Music cues: delivered files measure about -16 LUFS (manifest `loudness_lufs`), cue `volume_db` -10.5 (slice D value).
  Critical layers measure about -19 LUFS and use -12.0, as `helix_critical_layer` does.
- Ambience: delivered about -24 LUFS; primary bed -4.0 dB (as `helix_server_hall`), secondary beds -6.0 dB (as `helix_core`).
- **No human has listened to any of these cues or mixes.** Levels are derived from metadata only. Unverified by ear.

## Rights and approval (manifest, verbatim)

- Every music file below: rights_status `original algorithmic composition produced for the owner; no third-party samples; owner holds all rights (pending owner review)`, approval_status `pending_review`.
- Every ambience file below: rights_status `original synthesised sound design produced for the owner; no third-party samples or recordings; owner holds all rights (pending owner review)`, approval_status `pending_review`.
- Read directly for the Civitas entries; for the other chapters the same strings were matched across all entries by pattern search but not individually re-read. Nothing in the manifest was changed.

## Helix (chapter 1, reference)

| Role | Cue id | File | Manifest id | LUFS | dB | Notes |
|---|---|---|---|---|---|---|
| prep / tension / combat | helix_prep, helix_gameplay, helix_combat | `assets/audio/music/helix/hlx_mus_gameplay_prep.ogg`, `..._gameplay_tension.ogg`, `..._combat_01.ogg` | baseline (slice D) | - | -10.5 | existing |
| critical | helix_critical_layer | `.../hlx_mus_critical_layer_01.ogg` | baseline | - | -12.0 | existing |
| theme | helix_theme | `.../hlx_mus_theme_01.ogg` | HLX-MUS-THEME-01 | - | -10.5 | new cue id, existing file |
| boss | helix_boss | `.../hlx_mus_boss_01.ogg` | HLX-MUS-BOSS-01 | - | -10.5 | new cue id, existing file |
| ambience | helix_server_hall (plan), helix_core, helix_cooling | `assets/audio/ambience/helix/` | baseline | - | -4 / -6 / -6 | `hlx_amb_logistics_01.ogg` is delivered but not yet defined |

Gaps: none. `helix_01` keeps its own mission plan (frozen); the chapter plan is identical so `helix_02..20` match it.

## VITA Genomics (chapter 2)

| Role | Cue id | File (under `assets/audio/`) | Manifest id | LUFS | dB |
|---|---|---|---|---|---|
| preparation | vita_prep | `music/vita/vta_mus_gameplay_prep.ogg` | VTA-MUS-GAMEPLAY-PREP | -16.01 | -10.5 |
| tension | vita_gameplay | `music/vita/vta_mus_gameplay_tension.ogg` | VTA-MUS-GAMEPLAY-TENSION | -16.0 | -10.5 |
| combat | vita_combat | `music/vita/vta_mus_combat_01.ogg` | VTA-MUS-COMBAT-01 | -16.02 | -10.5 |
| critical layer | vita_critical_layer | `music/vita/vta_mus_critical_layer_01.ogg` | VTA-MUS-CRITICAL_LAYER-01 | -18.97 | -12.0 |
| theme | vita_theme | `music/vita/vta_mus_theme_01.ogg` | VTA-MUS-THEME-01 | -16.01 | -10.5 |
| boss | vita_boss | `music/vita/vta_mus_boss_01.ogg` | VTA-MUS-BOSS-01 | -16.16 | -10.5 |
| ambience (plan) | vita_bioreactor | `ambience/vita/vta_amb_bioreactor_01.ogg` | VTA-AMB-BIOREACTOR-01 | -24.1 | -4.0 |
| ambience | vita_cleanroom, vita_growth, vita_archive | `ambience/vita/vta_amb_{cleanroom,growth,archive}_01.ogg` | VTA-AMB-{CLEANROOM,GROWTH,ARCHIVE}-01 | -24.49 / -24.19 / -24.52 | -6.0 |

Gaps: none. Shared victory/defeat stingers used (no chapter-specific stingers wired; `*_mus_transition_stinger.ogg`, intro and outro are delivered but unused).

## Nova Grid (chapter 3)

| Role | Cue id | File (under `assets/audio/`) | Manifest id | LUFS | dB |
|---|---|---|---|---|---|
| preparation | nova_grid_prep | `music/nova_grid/nvg_mus_gameplay_prep.ogg` | NVG-MUS-GAMEPLAY-PREP | -15.98 | -10.5 |
| tension | nova_grid_gameplay | `music/nova_grid/nvg_mus_gameplay_tension.ogg` | NVG-MUS-GAMEPLAY-TENSION | -15.99 | -10.5 |
| combat | nova_grid_combat | `music/nova_grid/nvg_mus_combat_01.ogg` | NVG-MUS-COMBAT-01 | -16.01 | -10.5 |
| critical layer | nova_grid_critical_layer | `music/nova_grid/nvg_mus_critical_layer_01.ogg` | NVG-MUS-CRITICAL_LAYER-01 | -18.97 | -12.0 |
| theme | nova_grid_theme | `music/nova_grid/nvg_mus_theme_01.ogg` | NVG-MUS-THEME-01 | -16.0 | -10.5 |
| boss | nova_grid_boss | `music/nova_grid/nvg_mus_boss_01.ogg` | NVG-MUS-BOSS-01 | -16.15 | -10.5 |
| ambience (plan) | nova_grid_reactor | `ambience/nova_grid/nvg_amb_reactor_01.ogg` | NVG-AMB-REACTOR-01 | -24.03 | -4.0 |
| ambience | nova_grid_cooling, nova_grid_intake, nova_grid_transformer | `ambience/nova_grid/nvg_amb_{cooling,intake,transformer}_01.ogg` | NVG-AMB-{COOLING,INTAKE,TRANSFORMER}-01 | -24.29 / -24.13 / -23.97 | -6.0 |

Gaps: none (same unused extras as VITA).

## Civitas (chapter 4)

| Role | Cue id | File (under `assets/audio/`) | Manifest id | LUFS | dB |
|---|---|---|---|---|---|
| preparation | civitas_prep | `music/civitas/cvt_mus_gameplay_prep.ogg` | CVT-MUS-GAMEPLAY-PREP | -16.08 | -10.5 |
| tension | civitas_gameplay | `music/civitas/cvt_mus_gameplay_tension.ogg` | CVT-MUS-GAMEPLAY-TENSION | -16.13 | -10.5 |
| combat | civitas_combat | `music/civitas/cvt_mus_combat_01.ogg` | CVT-MUS-COMBAT-01 | -16.08 | -10.5 |
| critical layer | civitas_critical_layer | `music/civitas/cvt_mus_critical_layer_01.ogg` | CVT-MUS-CRITICAL_LAYER-01 | -18.98 | -12.0 |
| theme | civitas_theme | `music/civitas/cvt_mus_theme_01.ogg` | CVT-MUS-THEME-01 | -16.05 | -10.5 |
| boss | civitas_boss | `music/civitas/cvt_mus_boss_01.ogg` | CVT-MUS-BOSS-01 | -16.25 | -10.5 |
| ambience (plan) | civitas_control | `ambience/civitas/cvt_amb_control_01.ogg` | CVT-AMB-CONTROL-01 | -24.14 | -4.0 |
| ambience | civitas_plaza, civitas_spire, civitas_street | `ambience/civitas/cvt_amb_{plaza,spire,street}_01.ogg` | CVT-AMB-{PLAZA,SPIRE,STREET}-01 | -24.17 / -24.2 / -24.06 | -6.0 |

Gaps: none.

## Meridian (chapter 5)

| Role | Cue id | File (under `assets/audio/`) | Manifest id | LUFS | dB |
|---|---|---|---|---|---|
| preparation | meridian_prep | `music/meridian/mrd_mus_gameplay_prep.ogg` | MRD-MUS-GAMEPLAY-PREP | -15.98 | -10.5 |
| tension | meridian_gameplay | `music/meridian/mrd_mus_gameplay_tension.ogg` | MRD-MUS-GAMEPLAY-TENSION | -15.99 | -10.5 |
| combat | meridian_combat | `music/meridian/mrd_mus_combat_01.ogg` | MRD-MUS-COMBAT-01 | -16.01 | -10.5 |
| critical layer | meridian_critical_layer | `music/meridian/mrd_mus_critical_layer_01.ogg` | MRD-MUS-CRITICAL_LAYER-01 | -18.98 | -12.0 |
| theme | meridian_theme | `music/meridian/mrd_mus_theme_01.ogg` | MRD-MUS-THEME-01 | -15.99 | -10.5 |
| boss | meridian_boss | `music/meridian/mrd_mus_boss_01.ogg` | MRD-MUS-BOSS-01 | -16.16 | -10.5 |
| ambience (plan) | meridian_cavern | `ambience/meridian/mrd_amb_cavern_01.ogg` | MRD-AMB-CAVERN-01 | -23.98 | -4.0 |
| ambience | meridian_anchor, meridian_convergence, meridian_excavation | `ambience/meridian/mrd_amb_{anchor,convergence,excavation}_01.ogg` | MRD-AMB-{ANCHOR,CONVERGENCE,EXCAVATION}-01 | -24.01 / -24.05 / -24.04 | -6.0 |

Gaps: none.

## Notes

- Theme tracks are one-shots (manifest `loop: false`, cue `loops: false`); boss tracks have an 8-bar intro then loop from `loop_offset_seconds` (CVT: 19.2 s). The `loops` flag follows the manifest; the loop point lives in the file's import, which this workstream does not edit.
- The new files are not yet in `data/integrated_assets.json`; the orchestrator must integrate them before export.
- LUFS values are the manifest's `loudness_lufs` per entry.
