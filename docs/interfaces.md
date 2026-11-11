# Frozen interfaces and ownership (multi-agent run, 2026-11-11)

> **Status (2026-11-11, later):** the `.claude/` agent definitions were removed by the owner and the
> fixed five-workstream setup is paused. The contracts below still hold. The ownership map in §10
> applies whenever work is split across agents; the orchestrator assigns it per task.

Owner: Master Orchestrator. Frozen at baseline commit recorded in `docs/currentstate.md`.
Any change to a contract below is a **shared-interface proposal** (Problem · Current implementation ·
Proposed change · Affected workstreams · Backward compatibility · Tests required). Additive changes
inside a file a workstream owns are allowed where noted.

## Commands (every workstream)

- Full suite: `godot_console --headless --fixed-fps 60 -s tests/run_tests.gd` (exit 0 only when all pass).
- Fast suite: `... -s tests/run_tests.gd -- --unit` (skips physics suites).
- First run in a fresh worktree: `godot_console --headless --import` (cold import of the library takes minutes).
- Boot smoke: `godot_console --headless --quit-after 180` (expect no `ERROR` before the exit-time leak lines).
- Asset validator: `python assets/tools/validate_asset_manifest.py` (must print `PASS`).

## 1. Campaign / mission catalog — `scripts/core/mission_catalog.gd`

- 100 slots from `data/chapters.json`. Slot k (1-based) of a chapter is mission id
  `<chapter theme>_<kk>`: `helix_01..helix_20`, `vita_01..vita_20`, `nova_grid_01..nova_grid_20`,
  `civitas_01..civitas_20`, `meridian_01..meridian_20`.
- File: `data/missions/<id>.json`. A slot is *authored* when the file exists. Optional set dressing:
  `data/environments/<id>.json` (absent = greybox set).
- In the mission file, `id` must equal the file name and `chapter` must equal the chapter number (1-5).
  Enforced by `tests/campaign/test_mission_catalog.gd`; no other file names are allowed in `data/missions/`.
- Level number = `chapter.first_level + k - 1`. Unlocks are linear over authored missions
  (`MissionCatalog.is_unlocked(id, progress)`, completion = `ProgressData.is_mission_completed`).
- API: `load_default()`, `slots`, `slot(id)`, `authored()`, `chapter_slots(n)`, `first_authored_id()`,
  `next_authored_id(id)`, `previous_authored_id(id)`, `is_unlocked(id, progress)`.
- `helix_01` is the reference mission and is frozen (21 test references pin its physics outcomes).

## 2. Mission definition schema — `scripts/core/mission_definition.gd`

As implemented: `id, name, chapter, briefing, width, ground_y, operative, recommended_shots,
target_time, rewards{completion_points, completion_research_data, optional_research_data},
weapons{<weapon id>: {ammunition}}, statics[], components[], objectives[]`. Objective types:
goals `destroy_critical | destroy_components | structural_damage`; constraints `protect | max_shots |
within_time`. Materials from `data/materials.json`; weapons from `data/weapons.json`. Every critical asset
needs a `destroy_critical` objective. Weapons available in the campaign: `kinetic_accelerator`,
`breach_charge` only (owner default 2026-11-11).

## 3. Physics and rules signals (consume, do not change)

- `MissionEngine`: `weapon_selected, weapon_fired, ammo_changed, component_state_changed,
  component_destroyed, components_released, secondary_blast_requested, critical_asset_changed,
  objective_changed, mission_finished, decision_requested`; `apply_damage(id, raw, damage_type, penetration)`.
- Optional-objective decision (engine-owned rule): mandatory goals complete + scene settled + optional
  goals pending → `decision_requested` once; `awaiting_decision` holds the clock and blocks firing.
  `continue_mission()`; `finish_mission()` (allowed when `can_finish_early()`). After Continue the
  mission ends when all optional goals are done, the ammunition runs out, or `finish_mission()`.
  Constraints never count as pending; mandatory failures win as before.
- Weapon fallback (engine-owned, rc2): `select_weapon(id)` never leaves an empty weapon selected while
  another has ammunition (it selects `usable_weapon_after(id)`: next in mission weapon order, wrapping;
  reloading weapons with ammunition count as usable); returns false when no weapon has ammunition.
  The shot that uses the selected weapon's last round sets `auto_select_pending`; `MissionWorld`
  calls `apply_pending_auto_select()` once no round is in flight. A manual selection clears it.
  Presentation (operative, hint, switch sound, HUD) follows `weapon_selected` only.
- `MissionWorld`: `projectile_spawned, projectile_removed, component_removed, blast_happened,
  impact_happened`; `blast(...)`, `fire(direction, power)`.
- Component states: `DamageableComponent.State` INTACT → DAMAGED → CRITICAL → DESTROYED.

## 4. HUD contract — `MissionHud` (`scripts/mission/mission_hud.gd`, owned by ui-ux)

`MissionScreen` calls exactly these; their signatures are frozen:
`set_weapons(Array[WeaponState])`, `update_weapons(Dictionary, selected_id)`,
`update_stats(shots, recommended, elapsed, target)`, `update_objectives(MissionObjectives)`,
`place_critical_marker(Variant)`, `set_hint(String)`, `has_overlay()`, `show_pause()`,
`show_result(success, engine, score, granted, balance)`, `hide_overlay()`, property `library`.
Signals: `weapon_pressed(id)`, `pause_pressed`, `resume_pressed`, `restart_pressed`, and the optional
`next_pressed` (connected only if the HUD declares it; `MissionScreen.next_requested` → main.gd → next
unlocked authored mission), `exit_pressed` (results → Missions).
Decision flow (2026-11-11): `show_decision()` (title "Primary objective complete", subtitle "Optional
objectives remain. What next?", buttons Continue / Finish; the HUD closes the panel itself),
`set_finish_available(bool)` (persistent Finish button in the top-right row), signals `continue_pressed`,
`finish_pressed`.
Pause and navigation (rc2): `show_pause()` offers Resume / Restart Mission / Main Menu; Restart and
Main Menu open a confirmation (`confirm_restart()`, `confirm_main_menu()`; Cancel returns to the pause
menu). Confirmed Main Menu emits `menu_pressed` → `MissionScreen.menu_requested` → main.gd main menu,
recording nothing. `overlay_kind` (`OVERLAY_PAUSE`, `OVERLAY_CONFIRM_MENU`, `OVERLAY_CONFIRM_RESTART`,
`OVERLAY_DECISION`, `OVERLAY_RESULT` or "") and `is_confirming()` let `MissionScreen.handle_back()`
act on the open panel. MissionScreen emits each navigation request at most once.
Additions to the HUD are free; removals or signature changes are proposals.

## 5. Weapons — `data/weapons.json`, `WeaponCatalog`, `WeaponState` (owned by operative-weapons)

Weapon ids `kinetic_accelerator`, `breach_charge` and the existing stat keys are frozen (missions and
tests reference them). `WeaponCatalog.effective_stats(levels)` signature frozen. Adding stat keys is
allowed when existing tests stay green.

## 6. Audio events — `data/audio.json` (owned by audio-atmosphere)

Existing ids are frozen: the 23 `sounds` at baseline (`breach_detonate, breach_launch,
component_destroyed, core_critical, core_destroyed, impact_{composite,concrete,electronic,generic,glass,metal},
kinetic_fire, machine_failure, mission_fail, mission_success, objective_complete, reload_ready,
secondary_blast, structure_collapse, ui_back, ui_click, ui_confirm, weapon_switch`), the 9 music cues,
3 ambience beds, the material maps and `missions.helix_01`. Adding ids is free. Gameplay and UI call
`AudioService.play(id)` / `MusicDirector.play_cue(id)` only, never AudioStreamPlayer nodes.

## 7. Save schema v4 — `scripts/core/progress_data.gd` (orchestrator)

Any change needs a migration and orchestrator review. Settings fields: `sound_enabled,
vibration_enabled, music_enabled, voice_enabled, narration_volume` (0.0-1.0, added in rc2 as an
optional key: saves without it load 1.0, invalid values load 1.0 with a warning).

## 7a. Narration (rc2) — `data/narration.json`, `NarrationCatalog`, `CinematicPlayer`

Clip keys `<sequence id>/<slide number from 1>` → `res://` paths; `NarrationCatalog.apply_to(cinematics)`
sets `Slide.voice`. `CinematicPlayer` plays it on the `Voice` bus with the subtitle, holds the slide
for the clip + `VOICE_TAIL`, ducks `MusicDirector` by `duck_db` and restores on silent stages, skip,
finish and exit. Hand-off and expected keys: `docs/audio/narration-integration.md`.

## 8. Asset baseline

`assets/**`, `assets/asset_manifest.json` and `data/integrated_assets.json` are orchestrator-only.
Workstreams reference only ids already in `data/integrated_assets.json` (618 ids at baseline) or
request new ids from the manifest through the orchestrator. Never change `rights_status` or
`approval_status`.

## 9. Tests

Each workstream puts new suites in its own folder (`tests/levels/`, `tests/weapons/`, `tests/ui/`,
`tests/audio/`, `tests/qa/`); `tests/run_tests.gd` discovers `tests/<folder>/test_*.gd` automatically.
A suite that needs physics frames declares `const PHYSICS_SUITE := true`.

## 10. Ownership map

| Path | Owner |
|---|---|
| `project.godot`, `default_bus_layout.tres`, `.gitignore`, `.gitattributes`, `scenes/main.tscn`, `scripts/main.gd` | orchestrator |
| `assets/**`, `data/integrated_assets.json`, `tools/assets/**`, `tools/chapter_preview/**`, `tools/capture_*.gd`, `tools/economy/**` | orchestrator |
| `scripts/core/*` except weapon and audio files below; `scripts/services/save_service.gd`; `data/{materials,scoring,cinematics}.json` | orchestrator |
| `scripts/mission/{mission_screen,mission_world,component_body}.gd`, `scripts/mission/view/{mission_view,asset_library,component_visual,debris_set,mission_vfx,view_mapping}.gd` | orchestrator |
| `data/missions/helix_01.json`, `data/environments/helix_01.json` | orchestrator (frozen) |
| Legacy: `scripts/game/**`, `scripts/ui/{game_screen,hud,menu_screen,star_row}.gd`, `data/levels.json`, `tools/solve_levels.gd`, legacy suites | orchestrator (frozen) |
| `docs/*.md` at top level, `tests/campaign/**`, `tests/objectives/**` | orchestrator |
| `data/missions/*.json` (others), `data/environments/*.json` (others), `data/chapters.json`, `tools/levels/**`, `tests/levels/**`, `docs/levels/**` | levels |
| `scripts/mission/view/{operative_rig,projectile_visual}.gd`, `scripts/mission/weapon_projectile.gd`, `scripts/core/{weapon_catalog,weapon_state}.gd`, `data/weapons.json`, `tests/{test_weapons,test_weapon_state}.gd`, `tests/weapons/**`, `docs/operative/**` | operative-weapons |
| `scripts/mission/mission_hud.gd`, `scripts/ui/{ui_kit,icon}.gd`, new `scripts/ui/{campaign,settings,upgrades,common}/**`, `scenes/ui/**`, `tests/ui/**`, `docs/ui/**` | ui-ux |
| `scripts/services/{audio_service,music_director}.gd`, `scripts/core/audio_catalog.gd`, `scripts/mission/mission_audio.gd`, `data/audio.json`, `tests/{test_audio,test_music}.gd`, `tests/audio/**`, `audio_staging/**`, `docs/audio/**` | audio-atmosphere |
| `tests/{run_tests,test_case,physics_warmup,test_assets,test_mission_world,test_mission_screen}.gd`, `tests/qa/**`, `tools/{regression,perf,renderer_eval}/**`, `docs/benchmarks/**`, `docs/qa/**` | performance-qa |
