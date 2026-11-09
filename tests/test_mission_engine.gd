extends TestCase
## MissionEngine and MissionObjectives: weapon state, damage routing, structural releases,
## critical assets, objectives, success and failure. Headless, no physics.

const HELIX := "res://data/missions/helix_01.json"

var _materials := MaterialCatalog.load_from_file()
var _weapons := WeaponCatalog.load_from_file()


func _engine(levels: Dictionary = {}) -> MissionEngine:
	var def := MissionDefinition.load_from_file(HELIX, _materials, _weapons)
	return MissionEngine.new(def, _materials, _weapons, levels)


func _custom(objectives: Array, ammo: int = 30, extra_components: Array = []) -> MissionEngine:
	var components := [
		{"id": "base", "kind": "k", "material": "concrete", "x": 800, "y": 560, "w": 40, "h": 160},
		{"id": "core", "kind": "ai_core", "material": "electronic_module", "x": 800, "y": 450, "w": 50, "h": 50, "critical_asset": true, "supports": ["base"]},
	]
	components.append_array(extra_components)
	var data := {
		"id": "t", "name": "T", "chapter": 1, "width": 1600, "ground_y": 640, "operative": [100, 640],
		"recommended_shots": 1, "target_time": 30,
		"weapons": {"kinetic_accelerator": {"ammunition": ammo}},
		"components": components, "objectives": objectives,
	}
	var def := MissionDefinition.from_json_text(JSON.stringify(data), _materials, _weapons)
	assert_true(def.is_valid(), ", ".join(def.errors))
	return MissionEngine.new(def, _materials, _weapons)


func _core_objective() -> Dictionary:
	return {"id": "core", "type": "destroy_critical", "mandatory": true, "label": "L", "targets": ["core"]}


func _kill(engine: MissionEngine, id: String) -> void:
	engine.apply_damage(id, 100000.0, DamageRules.TYPE_IMPACT, 0.9)


func test_weapon_switching_and_independent_cooldowns() -> void:
	var e := _engine()
	assert_eq(e.selected_weapon_id, "kinetic_accelerator")
	var switched := []
	e.weapon_selected.connect(func(id: String) -> void: switched.append(id))
	assert_true(e.fire(Vector2.RIGHT) != Vector2.ZERO)
	assert_eq(e.fire(Vector2.RIGHT), Vector2.ZERO, "kinetic is reloading")
	assert_true(e.select_weapon("breach_charge"))
	assert_true(e.can_fire(), "breach has its own cooldown")
	var v := e.fire(Vector2(1, -1), 0.0)
	assert_near(v.length(), 350.0, 0.01, "lobbed power maps to speed")
	assert_false(e.select_weapon("railgun"))
	assert_eq(e.selected_weapon_id, "breach_charge")
	assert_eq(switched, ["breach_charge"])
	assert_eq(e.weapons.kinetic_accelerator.ammo, 13)
	assert_eq(e.weapons.breach_charge.ammo, 2)
	assert_eq(e.shots_fired(), 2)


func test_no_five_shot_cap() -> void:
	var e := _custom([_core_objective()], 30)
	var fired := 0
	for i in 25:
		if e.fire(Vector2.RIGHT) != Vector2.ZERO:
			fired += 1
		e.tick(1.5, false)
	assert_eq(fired, 25, "25 attacks allowed when the mission provides the ammunition")
	assert_true(e.is_active())


func test_damage_cascade_and_secondary_blast() -> void:
	var e := _engine()
	var released: Array = []
	var blasts := []
	e.components_released.connect(func(ids: Array[String]) -> void: released.append_array(ids))
	e.secondary_blast_requested.connect(func(id: String, b: Dictionary) -> void: blasts.append([id, b.radius]))
	assert_true(e.apply_damage("pillar_l", 60.0, DamageRules.TYPE_IMPACT) > 0.0)
	assert_eq(e.component_state("pillar_l"), DamageableComponent.State.DAMAGED)
	assert_eq(released.size(), 0)
	_kill(e, "pillar_l")
	assert_eq(released, ["deck", "core_shield", "aura_core", "power_cell"])
	assert_eq(e.component_state("aura_core"), DamageableComponent.State.INTACT, "released, not destroyed")
	_kill(e, "power_cell")
	assert_eq(blasts, [["power_cell", 110.0]])
	assert_near(e.apply_damage("ghost", 10.0, DamageRules.TYPE_IMPACT), 0.0, 0.001)


func test_critical_asset_state_and_mission_success_waits_for_settle() -> void:
	var e := _engine()
	var critical := []
	var finished := []
	e.critical_asset_changed.connect(func(id: String, s: int) -> void: critical.append(s))
	e.mission_finished.connect(func(ok: bool) -> void: finished.append(ok))
	e.apply_damage("aura_core", 80.0, DamageRules.TYPE_IMPACT)
	assert_eq(critical, [DamageableComponent.State.DAMAGED])
	assert_eq(e.critical_asset_states(), {"aura_core": DamageableComponent.State.DAMAGED})
	_kill(e, "aura_core")
	assert_eq(e.objectives.get_objective("core").status, MissionObjectives.Status.COMPLETE)
	assert_true(e.is_active(), "debris still moving: not over yet")
	e.tick(0.1, false)
	assert_true(e.is_active())
	e.tick(0.1, true)
	assert_eq(e.phase, MissionEngine.Phase.SUCCEEDED)
	assert_eq(finished, [true])
	assert_eq(e.objectives.get_objective("efficient").status, MissionObjectives.Status.COMPLETE, "intact constraint completes on success")
	assert_eq(e.objectives.get_objective("racks").status, MissionObjectives.Status.FAILED, "optional goal not achieved")
	assert_eq(e.fire(Vector2.RIGHT), Vector2.ZERO, "no firing after the mission ends")
	assert_near(e.apply_damage("rack_1", 500.0, DamageRules.TYPE_IMPACT), 0.0, 0.001)


func test_optional_objectives_progress_and_break() -> void:
	var e := _engine()
	_kill(e, "rack_1")
	_kill(e, "rack_2")
	assert_near(e.objectives.get_objective("racks").progress, 0.5, 0.001)
	for i in 9:
		e.fire(Vector2.RIGHT)
		e.tick(1.5, false)
	assert_eq(e.objectives.get_objective("efficient").status, MissionObjectives.Status.FAILED, "9 shots > 8")
	assert_true(e.is_active(), "an optional constraint never ends the mission")
	_kill(e, "rack_3")
	_kill(e, "rack_4")
	assert_eq(e.objectives.get_objective("racks").status, MissionObjectives.Status.COMPLETE)
	assert_eq(e.objectives.completed_optional_count(), 1)


func test_failure_on_ammo_exhaustion_only_after_settle() -> void:
	var e := _custom([_core_objective()], 2)
	var finished := []
	e.mission_finished.connect(func(ok: bool) -> void: finished.append(ok))
	e.fire(Vector2.RIGHT)
	e.tick(2.0, false)
	e.fire(Vector2.RIGHT)
	assert_false(e.has_ammo_left())
	e.tick(0.5, false)
	assert_true(e.is_active(), "last shot may still land")
	e.tick(0.5, true)
	assert_eq(e.phase, MissionEngine.Phase.FAILED)
	assert_eq(finished, [false])
	assert_eq(e.objectives.get_objective("core").status, MissionObjectives.Status.FAILED)


func test_mandatory_protect_fails_immediately() -> void:
	var archive := {"id": "archive", "kind": "archive", "material": "glass_polymer", "x": 1000, "y": 600, "w": 40, "h": 40}
	var e := _custom([_core_objective(), {"id": "p", "type": "protect", "mandatory": true, "label": "Spare the archive", "targets": ["archive"]}], 10, [archive])
	_kill(e, "archive")
	assert_eq(e.phase, MissionEngine.Phase.FAILED)
	assert_eq(e.objectives.get_objective("p").status, MissionObjectives.Status.FAILED)


func test_structural_damage_and_time_objectives() -> void:
	var e := _custom([
		_core_objective(),
		{"id": "wreck", "type": "structural_damage", "mandatory": false, "label": "L", "fraction": 0.5},
		{"id": "fast", "type": "within_time", "mandatory": false, "label": "L", "limit": 5},
	])
	e.apply_damage("base", 300.0, DamageRules.TYPE_IMPACT, 0.9)
	assert_true(e.structural_damage_fraction() > 0.5, "base is most of the facility's health")
	e.tick(0.0, false)
	assert_eq(e.objectives.get_objective("wreck").status, MissionObjectives.Status.COMPLETE)
	e.tick(6.0, false)
	assert_eq(e.objectives.get_objective("fast").status, MissionObjectives.Status.FAILED)


func test_destroy_component_and_upgrades() -> void:
	var e := _engine({"breach_charge": {"energy_capacity": 3}, "kinetic_accelerator": {"impact_energy": 2}})
	assert_eq(e.weapons.breach_charge.ammo, 6)
	assert_near(e.weapons.kinetic_accelerator.stats.impact_damage, 117.0, 0.001)
	e.destroy_component("relay_dish", "out_of_bounds")
	assert_eq(e.objectives.get_objective("relay").status, MissionObjectives.Status.COMPLETE)


func test_objectives_finalize_on_failure() -> void:
	var o := MissionObjectives.new([
		{"id": "g", "type": "destroy_components", "mandatory": true, "label": "L", "targets": ["a"], "count": 1, "fraction": 0.0, "limit": 0.0},
		{"id": "c", "type": "max_shots", "mandatory": false, "label": "L", "targets": [] as Array[String], "count": 0, "fraction": 0.0, "limit": 3.0},
	])
	assert_eq(o.update({"destroyed": {}, "shots": 1}).size(), 0)
	var changed := o.finalize(false)
	assert_eq(changed.size(), 2)
	assert_eq(o.get_objective("c").status, MissionObjectives.Status.FAILED, "constraints do not complete on failure")
	assert_true(o.get_objective("missing") == null)
