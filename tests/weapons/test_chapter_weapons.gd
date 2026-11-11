extends TestCase
## The chapter II-V weapons (Penetrator, Pulse Cannon, Disruptor, Temporal Lance) and the rules
## they rely on: piercing, material bonuses, cover-ignoring EMP blasts, shield emitters and the
## Lance-only temporal crystal. Rules cases use the engine directly; physics cases fire real
## projectiles in a small test facility and assert damage-state categories, not exact health.

const PHYSICS_SUITE := true
const State := DamageableComponent.State

var _materials := MaterialCatalog.load_from_file()
var _weapons := WeaponCatalog.load_from_file()
var _viewport: SubViewport


## A flat yard 1600 px wide; the operative stands at x 150. `components` are mission entries.
func _definition(components: Array, weapons: Dictionary, chapter: int = 5) -> MissionDefinition:
	var data := {
		"id": "weapons_test", "name": "Weapons test", "chapter": chapter, "briefing": "test",
		"width": 1600, "ground_y": 640, "operative": [150, 640], "recommended_shots": 1, "target_time": 30,
		"rewards": {"completion_points": 100, "completion_research_data": 1, "optional_research_data": 1},
		"weapons": weapons, "statics": [], "components": components,
		"objectives": [{"id": "core", "type": "destroy_critical", "mandatory": true, "label": "core", "targets": ["core"]}],
	}
	return MissionDefinition.from_json_text(JSON.stringify(data), _materials, _weapons)


func _core(x: float, material: String = "ai_core_module", extra: Dictionary = {}) -> Dictionary:
	var c := {"id": "core", "kind": "ai_core", "material": material, "x": x, "y": 610, "w": 60, "h": 60, "critical_asset": true}
	c.merge(extra, true)
	return c


func _world(def: MissionDefinition) -> MissionWorld:
	assert_true(def.is_valid(), ", ".join(def.errors))
	var engine := MissionEngine.new(def, _materials, _weapons)
	_viewport = SubViewport.new()
	_viewport.render_target_update_mode = SubViewport.UPDATE_DISABLED
	tree.root.add_child(_viewport)
	var world := MissionWorld.new()
	_viewport.add_child(world)
	world.setup(def, engine, _materials)
	return world


func _free() -> void:
	tree.root.remove_child(_viewport)
	_viewport.queue_free()


## Fires `weapon_id` horizontally at ground-hugging height from x 300 towards +x.
func _shoot(world: MissionWorld, weapon_id: String, y: float = 610.0) -> WeaponProjectile:
	var stats: Dictionary = world.engine.weapons[weapon_id].stats
	return world.spawn_projectile(weapon_id, stats, Vector2(300, y), Vector2(float(stats.launch_speed), 0))


func _settle(world: MissionWorld, seconds: float = 6.0) -> void:
	await wait_physics_frames(20)
	for i in int(seconds * 60.0):
		if world.projectiles.is_empty() and world.is_settled():
			return
		await tree.physics_frame


# --- Catalog and rules --------------------------------------------------------------------------

func test_material_multiplier_uses_listed_then_wildcard() -> void:
	var disruptor := _weapons.get_weapon("disruptor").effective_stats()
	assert_eq(WeaponCatalog.material_multiplier(disruptor, "electronic_module"), 5.0)
	assert_eq(WeaponCatalog.material_multiplier(disruptor, "concrete"), 0.1, "'*' covers unlisted materials")
	var kinetic := _weapons.get_weapon("kinetic_accelerator").effective_stats()
	assert_eq(WeaponCatalog.material_multiplier(kinetic, "concrete"), 1.0)


func test_optional_stats_default_and_upgrade() -> void:
	var kinetic := _weapons.get_weapon("kinetic_accelerator").effective_stats()
	assert_eq(int(kinetic.pierce_count), 0)
	var penetrator := _weapons.get_weapon("penetrator")
	assert_eq(int(penetrator.effective_stats().pierce_count), 2)
	assert_eq(int(penetrator.effective_stats({"piercing": 3}).pierce_count), 4, "piercing upgrade adds whole pierces")


func test_each_new_weapon_has_three_upgrade_levels_per_attribute() -> void:
	for id: String in ["penetrator", "pulse_cannon", "disruptor", "temporal_lance"]:
		var spec := _weapons.get_weapon(id)
		assert_true(spec.upgrades.size() >= 3, "%s has upgrade choices" % id)
		for attribute: String in spec.upgrades:
			assert_eq((spec.upgrades[attribute].costs as Array).size(), 3)


func test_mission_rejects_a_weapon_from_a_later_chapter() -> void:
	var def := _definition([_core(900)], {"temporal_lance": {"ammunition": 2}}, 2)
	assert_false(def.is_valid())
	assert_true(", ".join(def.errors).contains("unlocks in chapter 5"))
	assert_true(_definition([_core(900)], {"penetrator": {"ammunition": 2}}, 2).is_valid())


func test_unknown_shield_emitter_is_rejected() -> void:
	var def := _definition([_core(900, "ai_core_module", {"shielded_by": ["nope"]})], {"kinetic_accelerator": {"ammunition": 3}})
	assert_false(def.is_valid())


func test_shield_blocks_all_damage_until_every_emitter_falls() -> void:
	var emitters := [
		{"id": "em_a", "kind": "sensor_array", "material": "electronic_module", "x": 700, "y": 620, "w": 30, "h": 40},
		{"id": "em_b", "kind": "sensor_array", "material": "electronic_module", "x": 1300, "y": 620, "w": 30, "h": 40},
	]
	var def := _definition(emitters + [_core(1000, "ai_core_module", {"shielded_by": ["em_a", "em_b"]})], {"kinetic_accelerator": {"ammunition": 3}})
	assert_true(def.is_valid(), ", ".join(def.errors))
	var engine := MissionEngine.new(def, _materials, _weapons)
	var dropped: Array[String] = []
	engine.shield_dropped.connect(func(id: String) -> void: dropped.append(id))
	assert_true(engine.is_shielded("core"))
	assert_eq(engine.apply_damage("core", 9999.0, DamageRules.TYPE_IMPACT), 0.0, "shielded: no damage")
	engine.destroy_component("em_a", "test")
	assert_true(engine.is_shielded("core"), "one emitter still stands")
	assert_eq(dropped, [] as Array[String])
	engine.destroy_component("em_b", "test")
	assert_false(engine.is_shielded("core"))
	assert_eq(dropped, ["core"] as Array[String])
	assert_true(engine.apply_damage("core", 9999.0, DamageRules.TYPE_IMPACT) > 0.0)


func test_temporal_crystal_takes_damage_only_from_the_lance() -> void:
	var def := _definition([_core(1000, "temporal_crystal")], {"kinetic_accelerator": {"ammunition": 3}, "temporal_lance": {"ammunition": 2}})
	var engine := MissionEngine.new(def, _materials, _weapons)
	assert_eq(engine.apply_damage("core", 500.0, DamageRules.TYPE_IMPACT, 0.0, "kinetic_accelerator"), 0.0)
	assert_eq(engine.apply_damage("core", 500.0, DamageRules.TYPE_BLAST, 0.0, "breach_charge"), 0.0)
	assert_eq(engine.apply_damage("core", 500.0, DamageRules.TYPE_STRUCTURAL), 0.0, "collisions do not crack it")
	assert_true(engine.apply_damage("core", 100.0, DamageRules.TYPE_IMPACT, 0.6, "temporal_lance") > 0.0)


# --- Physics --------------------------------------------------------------------------------------

func test_penetrator_passes_through_glass_and_hits_what_is_behind() -> void:
	var glass := {"id": "pane", "kind": "cleanroom_panel", "material": "glass_polymer", "x": 700, "y": 590, "w": 16, "h": 100, "health_scale": 4.0}
	var world := _world(_definition([glass, _core(1000)], {"penetrator": {"ammunition": 2}}, 2))
	_shoot(world, "penetrator")
	await _settle(world)
	assert_true(world.engine.component_state("pane") >= State.DAMAGED, "the pane was hit")
	assert_true(world.engine.component_state("core") >= State.DAMAGED, "the dart flew on into the core")
	assert_eq(world.engine.effective_shots, 1, "one round counts once")
	_free()


func test_kinetic_round_stops_at_the_glass() -> void:
	var glass := {"id": "pane", "kind": "cleanroom_panel", "material": "glass_polymer", "x": 700, "y": 590, "w": 16, "h": 100, "health_scale": 4.0}
	var world := _world(_definition([glass, _core(1000)], {"kinetic_accelerator": {"ammunition": 2}}, 2))
	_shoot(world, "kinetic_accelerator")
	await _settle(world)
	assert_eq(world.engine.component_state("core"), State.INTACT, "no pierce: the core behind is untouched")
	_free()


func test_penetrator_does_not_pass_steel_it_cannot_break() -> void:
	var steel := {"id": "plate", "kind": "containment_cap", "material": "reinforced_steel", "x": 700, "y": 590, "w": 20, "h": 100, "health_scale": 3.0}
	var world := _world(_definition([steel, _core(1000)], {"penetrator": {"ammunition": 2}}, 2))
	_shoot(world, "penetrator")
	await _settle(world)
	var plate: DamageableComponent = world.engine.components.plate
	assert_true(plate.health < plate.max_health * 0.95, "armour penetration bites into steel (%.0f of %.0f left)" % [plate.health, plate.max_health])
	assert_eq(world.engine.component_state("core"), State.INTACT, "but the dart stops in it")
	_free()


func test_pulse_cannon_overloads_energy_cells_faster_than_kinetic() -> void:
	var cell := {"id": "core", "kind": "capacitor_cell", "material": "energy_component", "x": 1000, "y": 600, "w": 50, "h": 80, "health_scale": 3.0, "critical_asset": true}
	var world := _world(_definition([cell], {"pulse_cannon": {"ammunition": 2}, "kinetic_accelerator": {"ammunition": 2}}, 3))
	_shoot(world, "pulse_cannon")
	await _settle(world)
	var pulse_left: float = world.engine.components.core.health
	_free()
	world = _world(_definition([cell], {"pulse_cannon": {"ammunition": 2}, "kinetic_accelerator": {"ammunition": 2}}, 3))
	_shoot(world, "kinetic_accelerator")
	await _settle(world)
	var kinetic_left: float = world.engine.components.core.health
	_free()
	assert_true(pulse_left < kinetic_left, "pulse leaves %.0f, kinetic %.0f" % [pulse_left, kinetic_left])


func test_disruptor_emp_reaches_electronics_behind_a_wall_without_pushing() -> void:
	var wall := {"id": "wall", "kind": "security_wall", "material": "concrete", "x": 900, "y": 560, "w": 40, "h": 160, "health_scale": 4.0}
	var rack := {"id": "core", "kind": "data_exchange_rack", "material": "electronic_module", "x": 1000, "y": 610, "w": 40, "h": 60, "critical_asset": true}
	var world := _world(_definition([wall, rack], {"disruptor": {"ammunition": 2}}, 4))
	_shoot(world, "disruptor", 520.0)
	await _settle(world)
	assert_eq(world.engine.component_state("core"), State.DESTROYED, "EMP through the wall burns out the rack")
	assert_true(world.engine.component_state("wall") <= State.DAMAGED, "structure barely scratched")
	assert_true(world.body_for("wall") != null and world.body_for("wall").freeze, "no knockback")
	_free()


func test_breach_behind_the_same_wall_is_absorbed() -> void:
	var wall := {"id": "wall", "kind": "security_wall", "material": "concrete", "x": 900, "y": 560, "w": 40, "h": 160, "health_scale": 4.0}
	var rack := {"id": "core", "kind": "data_exchange_rack", "material": "electronic_module", "x": 1000, "y": 610, "w": 40, "h": 60, "health_scale": 2.0, "critical_asset": true}
	var world := _world(_definition([wall, rack], {"breach_charge": {"ammunition": 2}}, 4))
	world.blast(Vector2(860, 610), 160.0, 140.0, 900.0, 0.25)
	assert_true(world.engine.component_state("core") < State.DESTROYED, "a normal blast is occluded by concrete")
	_free()


func test_temporal_lance_breaks_crystal_through_two_panels() -> void:
	var a := {"id": "p1", "kind": "phase_shield", "material": "composite", "x": 600, "y": 600, "w": 20, "h": 80}
	var b := {"id": "p2", "kind": "phase_shield", "material": "composite", "x": 800, "y": 600, "w": 20, "h": 80}
	var crystal := _core(1100, "temporal_crystal")
	var world := _world(_definition([a, b, crystal], {"temporal_lance": {"ammunition": 2}, "kinetic_accelerator": {"ammunition": 4}}))
	_shoot(world, "kinetic_accelerator")
	await _settle(world)
	assert_eq(world.engine.component_state("core"), State.INTACT, "kinetic cannot touch the crystal")
	_shoot(world, "temporal_lance")
	await _settle(world)
	assert_true(world.engine.component_state("core") >= State.DAMAGED, "the lance passes both panels and cracks the crystal")
	_free()
