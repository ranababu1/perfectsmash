extends TestCase
## MissionWorld + MissionEngine on the real 2D physics with the Helix greybox (helix_01).
## Shots are placed directly at known positions so each test checks one tactic. Assertions use
## damage-state categories, not exact health, because Godot 2D contact resolution is not
## bit-reproducible run to run.

const HELIX := "res://data/missions/helix_01.json"
const State := DamageableComponent.State
const ProbeAim := preload("res://tools/regression/probe_aim.gd")

var _materials := MaterialCatalog.load_from_file()
var _weapons := WeaponCatalog.load_from_file()
var _viewport: SubViewport


func _world(materials: MaterialCatalog = _materials) -> MissionWorld:
	var def := MissionDefinition.load_from_file(HELIX, materials, _weapons)
	var engine := MissionEngine.new(def, materials, _weapons)
	_viewport = SubViewport.new()
	_viewport.render_target_update_mode = SubViewport.UPDATE_DISABLED
	tree.root.add_child(_viewport)
	var world := MissionWorld.new()
	_viewport.add_child(world)
	world.setup(def, engine, materials)
	return world


func _free() -> void:
	tree.root.remove_child(_viewport)
	_viewport.queue_free()


func _kinetic(world: MissionWorld, from: Vector2) -> void:
	world.spawn_projectile("kinetic_accelerator", world.engine.weapons.kinetic_accelerator.stats, from, Vector2(1700, 0))


func _breach(world: MissionWorld, from: Vector2, velocity: Vector2) -> void:
	world.spawn_projectile("breach_charge", world.engine.weapons.breach_charge.stats, from, velocity)


## Waits until projectiles are gone and the scene has settled (or `seconds` pass).
func _settle(world: MissionWorld, seconds: float = 8.0) -> void:
	await wait_physics_frames(30)
	await _until(func() -> bool: return world.projectiles.is_empty() and world.is_settled(), seconds)


## Fires the Kinetic Accelerator from the operative's muzzle at the core, aiming like a player
## with the arc preview, and waits for the mission to end.
func _finish_core_with_kinetic(world: MissionWorld) -> void:
	world.engine.select_weapon("kinetic_accelerator")
	await _until(func() -> bool: return world.engine.can_fire(), 3.0)
	var plan: Dictionary = ProbeAim.aim(world, world.body_for("aura_core"))
	assert_true(plan.direction != Vector2.ZERO, "a clear kinetic line to the exposed core (blocked by %s)" % plan.blocker)
	world.fire(plan.direction)
	await _until(func() -> bool: return not world.engine.is_active(), 10.0)


## Waits until `condition` holds or `seconds` of physics time pass.
func _until(condition: Callable, seconds: float) -> void:
	var frames := int(seconds * 60.0)
	for i in frames:
		if condition.call():
			return
		await tree.physics_frame


func test_facility_stands_until_attacked() -> void:
	var world := _world()
	await wait_physics_frames(120)
	for id: String in world.bodies:
		assert_eq(world.engine.component_state(id), State.INTACT, id)
		assert_true(world.body_for(id).freeze, "%s stays frozen" % id)
	assert_true(world.is_settled())
	assert_true(world.engine.is_active())
	_free()


func test_kinetic_collapse_exposes_core_and_finishing_shot_destroys_it() -> void:
	var world := _world()
	var e := world.engine
	_kinetic(world, Vector2(803, 530))
	await wait_physics_frames(45)
	assert_eq(e.component_state("pillar_l"), State.DAMAGED, "first hit weakens the column")
	assert_true(world.body_for("deck").freeze, "deck still held")
	_kinetic(world, Vector2(803, 530))
	await _settle(world)
	assert_eq(e.component_state("pillar_l"), State.DESTROYED)
	assert_false(world.body_for("aura_core").freeze, "the core came down with the deck")
	assert_eq(e.component_state("aura_core"), State.CRITICAL, "the collapse exposes and damages the core without destroying it")
	assert_true(e.is_active(), "the objective still needs a finishing shot")
	await _finish_core_with_kinetic(world)
	assert_eq(e.component_state("aura_core"), State.DESTROYED)
	assert_eq(e.phase, MissionEngine.Phase.SUCCEEDED)
	_free()


func test_collapse_from_both_columns_leaves_core_critical() -> void:
	var world := _world()
	var e := world.engine
	e.destroy_component("pillar_l", "test")
	e.destroy_component("pillar_r", "test")
	await _settle(world)
	assert_eq(e.component_state("aura_core"), State.CRITICAL, "a full drop damages but does not destroy the core")
	assert_true(e.is_active())
	_free()


func test_precise_column_breach_can_destroy_core_outright() -> void:
	var world := _world()
	var e := world.engine
	e.select_weapon("breach_charge")
	# Expert play from the operative: a charge against the left column (30 degrees, 90% power).
	world.fire(Vector2.RIGHT.rotated(-deg_to_rad(30.0)), 0.9)
	await _until(func() -> bool: return not e.is_active(), 10.0)
	assert_eq(e.component_state("aura_core"), State.DESTROYED)
	assert_eq(e.phase, MissionEngine.Phase.SUCCEEDED)
	_free()


func test_ordinary_deck_breach_does_not_clear_the_mission() -> void:
	for at: Vector2 in [Vector2(815, 380), Vector2(990, 380)]:
		var world := _world()
		var e := world.engine
		_breach(world, at, Vector2(0, 250))
		await _settle(world)
		assert_true(e.component_state("aura_core") != State.DESTROYED, "a charge on the deck at %s does not bypass the objective" % at)
		assert_true(e.is_active())
		_free()


func test_breach_charge_clears_rack_cluster_without_reaching_core() -> void:
	var world := _world()
	var e := world.engine
	var blasts := []
	world.blast_happened.connect(func(c: Vector2, r: float) -> void: blasts.append(r))
	_breach(world, Vector2(674, 480), Vector2(0, 300))
	await wait_physics_frames(120)
	assert_eq(blasts.size(), 1, "one detonation")
	assert_eq(e.effective_shots, 1, "a damaging detonation counts as an effective shot")
	assert_eq(e.component_state("rack_1"), State.DESTROYED, "area damage hits both racks")
	assert_eq(e.component_state("rack_2"), State.DESTROYED)
	assert_true(e.component_state("blast_wall") != State.DESTROYED, "reinforced steel survives")
	assert_eq(e.component_state("aura_core"), State.INTACT)
	assert_true(e.is_active())
	assert_eq(e.objectives.get_objective("racks").progress, 0.5)
	_free()


func test_breach_lobbed_onto_core_leaves_it_critical_for_a_finishing_shot() -> void:
	var world := _world()
	var e := world.engine
	_breach(world, Vector2(885, 300), Vector2(0, 200))
	await _settle(world)
	assert_eq(e.component_state("aura_core"), State.CRITICAL, "a direct charge cripples the core")
	assert_true(e.is_active())
	await _finish_core_with_kinetic(world)
	assert_eq(e.objectives.get_objective("core").status, MissionObjectives.Status.COMPLETE)
	assert_eq(e.phase, MissionEngine.Phase.SUCCEEDED, "succeeds once the debris settles")
	_free()


func test_core_shield_absorbs_kinetic_fire() -> void:
	var world := _world()
	var e := world.engine
	for i in 3:
		_kinetic(world, Vector2(810, 390))
		await wait_physics_frames(45)
	assert_true(e.component_state("core_shield") <= State.DAMAGED, "steel shield holds")
	assert_eq(e.component_state("aura_core"), State.INTACT, "core protected from the front")
	_free()


func test_power_cell_secondary_blast_damages_core() -> void:
	var world := _world()
	var e := world.engine
	var removed := []
	world.component_removed.connect(func(id: String, _at: Vector2) -> void: removed.append(id))
	e.apply_damage("power_cell", 9999.0, DamageRules.TYPE_IMPACT, 0.9)
	await wait_physics_frames(30)
	assert_eq(removed, ["power_cell"])
	assert_true(world.body_for("power_cell") == null, "destroyed body removed")
	var core: DamageableComponent = e.components.aura_core
	assert_true(core.health < core.max_health, "chain reaction reached the core")
	_free()


func test_fire_spends_ammo_from_muzzle_and_settles() -> void:
	var world := _world()
	var e := world.engine
	var shot := world.fire(Vector2(0.3, -1.0))
	assert_true(shot != null)
	assert_eq(shot.position, world.muzzle_position())
	assert_eq(e.weapons.kinetic_accelerator.ammo, 13)
	assert_true(world.fire(Vector2(0.3, -1.0)) == null, "reloading")
	assert_false(world.is_settled(), "a projectile is in flight")
	await _until(func() -> bool: return world.is_settled(), 8.0)
	assert_true(world.is_settled(), "settles after the round leaves or lands")
	assert_eq(world.projectiles.size(), 0)
	_free()


## --- Accuracy: one fired projectile counts as at most one effective shot ---

func test_multi_component_blast_counts_one_effective_shot() -> void:
	var world := _world()
	var e := world.engine
	var damaged := {}
	e.component_state_changed.connect(func(id: String, _p: int, _c: int) -> void: damaged[id] = true)
	_breach(world, Vector2(674, 480), Vector2(0, 300))
	await wait_physics_frames(120)
	assert_true(damaged.size() >= 2, "the blast damaged several components: %s" % str(damaged.keys()))
	assert_eq(e.effective_shots, 1)
	_free()


func test_secondary_chain_reaction_adds_no_effective_shots() -> void:
	var world := _world()
	var e := world.engine
	var chain := []
	e.secondary_blast_requested.connect(func(id: String, _b: Dictionary) -> void: chain.append(id))
	_breach(world, Vector2(955, 330), Vector2(0, 150))
	await wait_physics_frames(180)
	assert_eq(chain, ["power_cell"], "the power cell exploded as a secondary effect")
	assert_eq(e.effective_shots, 1, "the chain is credited to the single shot that started it")
	_free()


func test_shot_through_destroyed_component_is_not_effective() -> void:
	var world := _world()
	var e := world.engine
	e.destroy_component("relay_dish", "test")
	await wait_physics_frames(2)
	# Fly through where the dish was, above the mast, into open space.
	_kinetic(world, Vector2(1120, 368))
	await wait_physics_frames(90)
	assert_eq(e.effective_shots, 0)
	_free()


func test_detonation_that_damages_nothing_is_not_effective() -> void:
	var world := _world()
	var e := world.engine
	_breach(world, Vector2(330, 560), Vector2(0, 200))
	await wait_physics_frames(60)
	assert_true(world.projectiles.is_empty(), "the charge detonated on the ground")
	assert_eq(e.effective_shots, 0)
	_free()


func test_two_damaging_shots_count_twice() -> void:
	var world := _world()
	var e := world.engine
	_kinetic(world, Vector2(803, 530))
	await wait_physics_frames(45)
	_kinetic(world, Vector2(1150, 470))
	await wait_physics_frames(45)
	assert_eq(e.effective_shots, 2)
	_free()


## --- Scoring consistency for fixed scripted input (tools/regression/score_replay.gd) ---
## Godot 2D physics is deterministic for identical input on one platform, but not bit-identical
## across platforms: the same sequence measured 0.4516 structural damage on Windows x86_64 and
## 0.4519 on the Android x86_64 emulator (2026-11-09). Hence: exact within a run, tolerance
## against the reference (docs/instructions.md, "Physics tolerances"). Reference re-measured on
## Windows x86_64 after the Batch 5 tuning (2026-11-10): 3648 points, damage 0.3476.

const ScoreReplay := preload("res://tools/regression/score_replay.gd")


func test_scripted_replay_is_repeatable_and_near_reference() -> void:
	var scoring := MissionScoring.load_from_file()
	var summaries := []
	for i in 2:
		var result: Dictionary = await ScoreReplay.play(tree.root, "kinetic_collapse_finish")
		summaries.append(ScoreReplay.summary(scoring, result.engine))
		tree.root.remove_child(result.viewport)
		(result.viewport as Node).queue_free()
	var a: Dictionary = summaries[0]
	var b: Dictionary = summaries[1]
	assert_eq(a.mission_points, b.mission_points, "same input, same platform, same score")
	assert_eq(a.structural_damage, b.structural_damage)
	assert_eq(a.physics_frames, b.physics_frames)
	assert_eq(a.phase, MissionEngine.Phase.SUCCEEDED)
	assert_eq(a.shots, 3)
	assert_eq(a.effective_shots, 3)
	assert_eq(a.research_data, 40)
	assert_near(float(a.structural_damage), 0.3476, 0.01, "reference structural damage")
	assert_true(absi(int(a.mission_points) - 3648) <= 15, "within tolerance of the 3648 reference: %d" % a.mission_points)


## --- Blast occlusion (approved Batch 5 rule; transmission per material in data/materials.json) ---

func test_occlusion_and_load_aware_push_are_on() -> void:
	var world := _world()
	assert_true(world.blast_occlusion)
	assert_true(world.load_aware_push)
	_free()


func test_steel_shield_attenuates_blast_and_clear_line_does_not() -> void:
	var world := _world()
	world.blast_occlusion = true
	await wait_physics_frames(2)
	var core := world.body_for("aura_core")
	# Left of the 16 px steel core_shield: the ray to the core crosses the shield.
	var shielded := world.blast_transmission(Vector2(822, 390), core)
	assert_near(shielded, _materials.get_material("reinforced_steel").blast_transmission, 0.001, "reinforced steel passes its data value")
	assert_near(shielded, 0.1, 0.001)
	# Directly above the core: clear line of sight.
	assert_near(world.blast_transmission(Vector2(885, 300), core), 1.0, 0.001)
	# Inside the target's box: always full.
	assert_near(world.blast_transmission(core.global_position, core), 1.0, 0.001)
	_free()


func test_penetration_lets_blast_through_blockers() -> void:
	var world := _world()
	world.blast_occlusion = true
	await wait_physics_frames(2)
	var core := world.body_for("aura_core")
	assert_near(world.blast_transmission(Vector2(822, 390), core, 0.5), 0.1 + 0.9 * 0.5, 0.001)
	_free()


func test_blockers_compound() -> void:
	var world := _world()
	await wait_physics_frames(2)
	# Right of the blast wall, aiming at rack_2 through rack_1 (electronics pass 0.5).
	var through_one := world.blast_transmission(Vector2(622, 590), world.body_for("rack_2"))
	assert_near(through_one, 0.5, 0.001)
	# From left of the blast wall: steel wall (0.1) then rack_1 (0.5).
	var through_two := world.blast_transmission(Vector2(560, 590), world.body_for("rack_2"))
	assert_near(through_two, 0.05, 0.001)
	# Penetration applies to each blocker before compounding.
	var p := 0.5
	assert_near(world.blast_transmission(Vector2(560, 590), world.body_for("rack_2"), p), (0.1 + 0.9 * p) * (0.5 + 0.5 * p), 0.001)
	_free()


func test_occlusion_reduces_blast_damage_with_falloff() -> void:
	var off := _world()
	off.blast_occlusion = false
	off.blast(Vector2(822, 390), 160.0, 140.0, 900.0, 0.25)
	var core_off: float = off.engine.components.aura_core.health
	_free()
	var on := _world()
	on.blast_occlusion = true
	await wait_physics_frames(2)
	on.blast(Vector2(822, 390), 160.0, 140.0, 900.0, 0.25)
	var core_on: float = on.engine.components.aura_core.health
	assert_true(core_on > core_off, "shielded core keeps more health (%.0f vs %.0f)" % [core_on, core_off])
	var max_health: float = on.engine.components.aura_core.max_health
	var expected_loss := DamageRules.blast_damage(160.0, 33.0, 140.0, 0.25) * 0.1
	assert_near(max_health - core_on, expected_loss if expected_loss >= 4.0 else 0.0, 3.0, "falloff x transmission")
	_free()


func test_static_geometry_blocks_blasts() -> void:
	var world := _world()
	var screen := StaticBox.new(Vector2(20, 120))
	screen.position = Vector2(1300, 560)
	world.add_child(screen)
	await wait_physics_frames(2)
	var mast := world.body_for("relay_mast")
	# From right of the static screen, the ray to the mast crosses it.
	assert_near(world.blast_transmission(Vector2(1340, 560), mast), MaterialCatalog.MIN_BLAST_TRANSMISSION, 0.001, "statics pass the minimum")
	assert_near(world.blast_transmission(Vector2(1340, 560), mast, 0.5), 0.05 + 0.95 * 0.5, 0.001, "penetration still works through statics")
	_free()


func test_transmission_follows_material_data() -> void:
	var data: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(MaterialCatalog.DEFAULT_PATH))
	for m: Dictionary in data.materials:
		if m.id == "reinforced_steel":
			m.blast_transmission = 0.3
	var custom := MaterialCatalog.from_json_text(JSON.stringify(data))
	assert_true(custom.is_valid(), ", ".join(custom.errors))
	var world := _world(custom)
	await wait_physics_frames(2)
	assert_near(world.blast_transmission(Vector2(822, 390), world.body_for("aura_core")), 0.3, 0.001, "the steel shield passes what the data says")
	_free()


func test_load_aware_push_counts_carried_mass() -> void:
	var world := _world()
	var deck_load := world.supported_mass("deck")
	var expected := 0.0
	for id: String in ["deck", "core_shield", "aura_core", "power_cell"]:
		expected += world.body_for(id).mass
	assert_near(deck_load, expected, 0.01, "the deck carries the shield, core and cell")
	assert_true(world.supported_mass("pillar_l") > deck_load, "the column carries the loaded deck")
	assert_near(world.supported_mass("relay_dish"), world.body_for("relay_dish").mass, 0.001)
	_free()
