extends SceneTree
## Design-evaluation probe: how much damage the AI core takes, and from what, when the Helix
## deck comes down. Runs fixed collapse scenarios on the shipped helix_01 data and prints the
## core's damage timeline per scenario (blasts, its own landing jolts, debris landing on it).
## Evidence for the "collapse exposes the core, a finishing shot destroys it" rule; not a test.
##
##   godot_console --headless --fixed-fps 60 -s tools/regression/collapse_probe.gd [-- --verbose]

const MISSION := "res://data/missions/helix_08.json"
const CORE := "aura_core"
const ProbeAim := preload("res://tools/regression/probe_aim.gd")

var _materials := MaterialCatalog.load_from_file()
var _weapons := WeaponCatalog.load_from_file()
var _verbose := false


func _initialize() -> void:
	_verbose = OS.get_cmdline_user_args().has("--verbose")
	_run.call_deferred()


func _run() -> void:
	for scenario: String in scenarios():
		await _evaluate(scenario)
	quit()


static func scenarios() -> Array[String]:
	return ["kinetic_column_l", "kinetic_column_r", "breach_column_l", "breach_deck_left", "breach_deck_right",
		"breach_on_core", "force_column_l", "force_both_columns", "power_cell_chain"]


func _evaluate(scenario: String) -> void:
	var sim := _make()
	var engine: MissionEngine = sim.engine
	var world: MissionWorld = sim.world
	var core_state := engine.components[CORE] as DamageableComponent
	var log := []
	var by_cause := {"blast": 0.0, "landing": 0.0, "debris": 0.0, "other": 0.0}
	var cause := ["other"]
	world.blast_happened.connect(func(_c: Vector2, _r: float) -> void: cause[0] = "blast")
	var core_body := world.body_for(CORE)
	core_body.impacted.connect(func(_b: ComponentBody, impulse: float, others: Array) -> void:
		cause[0] = "landing %.0f" % impulse)
	for id: String in world.bodies:
		if id == CORE:
			continue
		(world.bodies[id] as ComponentBody).impacted.connect(func(b: ComponentBody, impulse: float, others: Array) -> void:
			if others.has(world.body_for(CORE)):
				cause[0] = "debris %s %.0f" % [b.component_id, impulse])
	await _start(scenario, sim)
	var health := core_state.health
	for frame in 600:
		if core_state.health < health:
			var lost := health - core_state.health
			var kind: String = (cause[0] as String).get_slice(" ", 0)
			by_cause[kind if by_cause.has(kind) else "other"] += lost
			log.append("f%d -%.0f (%s)" % [frame, lost, cause[0]])
			health = core_state.health
		cause[0] = "other"
		if engine.phase != MissionEngine.Phase.ACTIVE and frame > 30:
			break
		if world.projectiles.is_empty() and world.is_settled() and frame > 60:
			break
		await physics_frame
	var states := ["intact", "damaged", "critical", "destroyed"]
	print("COLLAPSE %-18s core %-9s %3.0f/%3.0f hp | blast %3.0f, landing %3.0f, debris %3.0f, other %3.0f | deck %s, mission %s" % [
		scenario, states[core_state.state], core_state.health, core_state.max_health,
		by_cause.blast, by_cause.landing, by_cause.debris, by_cause.other,
		states[engine.component_state("deck")], ["active", "succeeded", "failed"][engine.phase]])
	if _verbose:
		print("    ", ", ".join(log))
	# Finishing shots: the operative's Kinetic Accelerator aimed at wherever the core came to rest.
	if engine.is_active() and world.body_for(CORE) != null:
		var rest := world.body_for(CORE).global_position
		var struck := []
		world.projectile_spawned.connect(func(p: WeaponProjectile) -> void:
			p.struck.connect(func(_p: WeaponProjectile, target: Node, _s: float) -> void:
				struck.append((target as ComponentBody).component_id if target is ComponentBody else "static/ground")))
		engine.select_weapon("kinetic_accelerator")
		var shots := 0
		var blockers := []
		while engine.is_active() and world.body_for(CORE) != null and shots < 4:
			while not engine.can_fire():
				await physics_frame
			# Aim like a player with the arc preview; if nothing reaches the core, clear the blocker.
			var plan: Dictionary = ProbeAim.aim(world, world.body_for(CORE))
			var direction: Vector2 = plan.direction
			if direction == Vector2.ZERO:
				blockers.append(plan.blocker)
				if _verbose:
					print("      aim trace: ", plan.trace)
				var blocking := world.body_for(plan.blocker)
				var blocked_plan: Dictionary = ProbeAim.aim(world, blocking) if blocking != null else {}
				direction = blocked_plan.get("direction", Vector2.ZERO)
				if direction == Vector2.ZERO:
					break
			world.fire(direction)
			shots += 1
			await _frames(70)
		print("    core at rest (%.0f, %.0f); %d kinetic finishing shot(s) -> core %s; blocked by %s; struck %s" % [
			rest.x, rest.y, shots, states[core_state.state], str(blockers), str(struck)])
	_free(sim)


func _start(scenario: String, sim: Dictionary) -> void:
	var engine: MissionEngine = sim.engine
	var world: MissionWorld = sim.world
	var kinetic: Dictionary = engine.weapons.kinetic_accelerator.stats
	var breach: Dictionary = engine.weapons.breach_charge.stats
	match scenario:
		"kinetic_column_l":
			for i in 2:
				world.spawn_projectile("kinetic_accelerator", kinetic, Vector2(803, 530), Vector2(1700, 0))
				await _frames(45)
		"kinetic_column_r":
			for i in 2:
				world.spawn_projectile("kinetic_accelerator", kinetic, Vector2(1000, 530), Vector2(-1700, 0))
				await _frames(45)
		"breach_column_l":
			world.spawn_projectile("breach_charge", breach, Vector2(800, 480), Vector2(0, 300))
		"breach_deck_left":
			world.spawn_projectile("breach_charge", breach, Vector2(815, 380), Vector2(0, 250))
		"breach_deck_right":
			world.spawn_projectile("breach_charge", breach, Vector2(990, 380), Vector2(0, 250))
		"breach_on_core":
			world.spawn_projectile("breach_charge", breach, Vector2(885, 300), Vector2(0, 200))
		"force_column_l":
			engine.destroy_component("pillar_l", "probe")
		"force_both_columns":
			engine.destroy_component("pillar_l", "probe")
			engine.destroy_component("pillar_r", "probe")
		"power_cell_chain":
			engine.apply_damage("power_cell", 9999.0, DamageRules.TYPE_IMPACT, 0.9)


func _make() -> Dictionary:
	var def := MissionDefinition.load_from_file(MISSION, _materials, _weapons)
	var engine := MissionEngine.new(def, _materials, _weapons)
	var viewport := SubViewport.new()
	viewport.render_target_update_mode = SubViewport.UPDATE_DISABLED
	root.add_child(viewport)
	var world := MissionWorld.new()
	viewport.add_child(world)
	world.setup(def, engine, _materials)
	return {"engine": engine, "world": world, "viewport": viewport}


func _frames(count: int) -> void:
	for i in count:
		await physics_frame


func _free(sim: Dictionary) -> void:
	root.remove_child(sim.viewport)
	(sim.viewport as Node).queue_free()
