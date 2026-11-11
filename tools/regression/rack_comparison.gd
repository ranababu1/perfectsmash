extends SceneTree
## Rack-height comparison (Batch 5). For each Helix layout variant (probe_layouts.gd) it plays
## collapse scenarios from the operative's position, then tries to finish the core with the
## Kinetic Accelerator only, aiming like a player with the arc preview. When nothing reaches the
## core it shoots whatever blocks the line (as a player clearing the way would). Reports the
## core's state after the collapse, how many kinetic rounds the finish took, what was in the
## way, and whether the finish failed without a Breach Charge. Evidence, not a test.
##
##   godot_console --headless --fixed-fps 60 -s tools/regression/rack_comparison.gd [-- --layouts=a,b] [--sweep]
## --sweep also fires every Breach trajectory of the tactics probe (14 angles x 8 powers) and the
## kinetic route at each aim angle, and classifies how each one ends.

const MISSION := "res://data/missions/helix_08.json"
const ProbeAim := preload("res://tools/regression/probe_aim.gd")
const Layouts := preload("res://tools/regression/probe_layouts.gd")
const MAX_FINISH := 6
## [name, weapon, direction degrees above horizontal, power] fired from the muzzle;
## "force_both" destroys both columns directly (a worst-case flat drop).
const SCENARIOS := [
	["kinetic_column_x2", "kinetic_accelerator", 0.0, 1.0],
	["breach_column_45", "breach_charge", 45.0, 0.7],
	["breach_column_30", "breach_charge", 30.0, 0.9],
	["breach_column_25", "breach_charge", 25.0, 1.0],
	["force_both", "", 0.0, 0.0],
]
const STATES := ["intact", "damaged", "critical", "destroyed"]

var _materials := MaterialCatalog.load_from_file()
var _weapons := WeaponCatalog.load_from_file()


func _initialize() -> void:
	_run.call_deferred()


const BREACH_ANGLES := [15, 20, 25, 30, 35, 40, 45, 50, 55, 60, 65, 70, 75, 80]
const BREACH_POWERS := [0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
const KINETIC_ANGLES := [-4, -2, 0, 2, 4, 6, 8, 10, 12, 14]


func _run() -> void:
	var layouts: Array = Layouts.LAYOUTS
	var sweep := false
	for arg in OS.get_cmdline_user_args():
		if arg.begins_with("--layouts="):
			layouts = arg.trim_prefix("--layouts=").split(",")
		sweep = sweep or arg == "--sweep"
	if sweep:
		for layout: String in layouts:
			await _sweep(layout)
		quit()
		return
	for layout: String in layouts:
		var finished := 0
		var total_shots := 0
		var lines := []
		for scenario: Array in SCENARIOS:
			var r: Dictionary = await _play(layout, scenario)
			lines.append(r.line)
			if r.finished:
				finished += 1
				total_shots += int(r.shots)
		print("RACKS %-13s kinetic finish possible in %d/%d scenarios, %s kinetic rounds on average" % [
			layout, finished, SCENARIOS.size(), ("%.1f" % (float(total_shots) / finished)) if finished > 0 else "-"])
		for line: String in lines:
			print("    ", line)
	quit()


func _play(layout: String, scenario: Array) -> Dictionary:
	var sim := _make(layout)
	var engine: MissionEngine = sim.engine
	var world: MissionWorld = sim.world
	if scenario[1] == "":
		engine.destroy_component("pillar_l", "probe")
		engine.destroy_component("pillar_r", "probe")
	else:
		engine.select_weapon(scenario[1])
		var shots := 2 if scenario[1] == "kinetic_accelerator" else 1
		for i in shots:
			while not engine.can_fire():
				await physics_frame
			world.fire(Vector2.RIGHT.rotated(-deg_to_rad(scenario[2])), scenario[3])
			await _frames(45)
	await _settle(world)
	var after: String = STATES[engine.component_state("aura_core")]
	var core := world.body_for("aura_core")
	var rest := core.global_position if core != null else Vector2.ZERO
	var exposed := core != null and not core.freeze
	var blockers := []
	var used := 0
	engine.select_weapon("kinetic_accelerator")
	while engine.is_active() and world.body_for("aura_core") != null and used < MAX_FINISH:
		while not engine.can_fire():
			await physics_frame
		var plan: Dictionary = ProbeAim.aim(world, world.body_for("aura_core"))
		var direction: Vector2 = plan.direction
		if direction == Vector2.ZERO:
			blockers.append(plan.blocker)
			var blocking := world.body_for(plan.blocker)
			var clear: Dictionary = ProbeAim.aim(world, blocking) if blocking != null else {}
			direction = clear.get("direction", Vector2.ZERO)
			if direction == Vector2.ZERO:
				direction = world.body_for("aura_core").global_position - world.muzzle_position()
		world.fire(direction)
		used += 1
		await _frames(50)
		await _settle(world, 3.0)
	var done := engine.component_state("aura_core") == DamageableComponent.State.DESTROYED
	var line := "%-18s after collapse core %-9s at (%4.0f,%4.0f)%s | %s" % [
		scenario[0], after, rest.x, rest.y, "" if exposed else " still on deck",
		("finished with %d kinetic round(s)" % used) if done else ("NOT finished with %d kinetic rounds" % used)]
	if not blockers.is_empty():
		line += "; in the way: %s" % ", ".join(blockers)
	_free(sim)
	return {"line": line, "finished": done, "shots": used}


## Fires every Breach trajectory once (then a kinetic-only finish), and the kinetic route at each
## angle (up to 3 rounds at the angle until the core is exposed, then the finish). Counts outcomes.
func _sweep(layout: String) -> void:
	var breach := {"one_shot": 0, "kinetic_finish": 0, "blocked": 0, "no_collapse": 0}
	var finish_rounds := 0
	var blocked_by := {}
	for angle: int in BREACH_ANGLES:
		for power: float in BREACH_POWERS:
			var sim := _make(layout)
			sim.engine.select_weapon("breach_charge")
			sim.world.fire(Vector2.RIGHT.rotated(-deg_to_rad(angle)), power)
			await _settle(sim.world)
			var outcome: Dictionary = await _classify(sim)
			breach[outcome.kind] += 1
			if outcome.kind == "kinetic_finish":
				finish_rounds += int(outcome.rounds)
			for b: String in outcome.get("blockers", []):
				blocked_by[b] = int(blocked_by.get(b, 0)) + 1
			_free(sim)
	var kinetic := []
	var kinetic_ok := 0
	for angle: int in KINETIC_ANGLES:
		var sim := _make(layout)
		var shots := 0
		for i in 3:
			var core: ComponentBody = sim.world.body_for("aura_core")
			if core == null or not core.freeze or not sim.engine.is_active():
				break
			while not sim.engine.can_fire():
				await physics_frame
			sim.world.fire(Vector2.RIGHT.rotated(-deg_to_rad(angle)))
			shots += 1
			await _frames(70)
		await _settle(sim.world)
		var outcome: Dictionary = await _classify(sim)
		var total := shots + int(outcome.get("rounds", 0))
		if outcome.kind == "kinetic_finish" or outcome.kind == "one_shot":
			kinetic_ok += 1
			kinetic.append("%d°:%d" % [angle, total])
		else:
			kinetic.append("%d°:%s" % [angle, outcome.kind])
		_free(sim)
	var total_breach := BREACH_ANGLES.size() * BREACH_POWERS.size()
	print("SWEEP %-13s breach %d: one-shot %d, collapse + kinetic finish %d (avg %.1f rounds), collapse but finish blocked %d %s, no collapse %d" % [
		layout, total_breach, breach.one_shot, breach.kinetic_finish, float(finish_rounds) / maxi(breach.kinetic_finish, 1),
		breach.blocked, str(blocked_by), breach.no_collapse])
	print("SWEEP %-13s kinetic route (<=3 at the angle, then finish): clears on %d/%d angles; %s" % [layout, kinetic_ok, KINETIC_ANGLES.size(), ", ".join(kinetic)])


## After a collapse: one_shot (core already destroyed), no_collapse (core still frozen on the
## deck), or a kinetic-only finish attempt -> kinetic_finish (with rounds) / blocked.
func _classify(sim: Dictionary) -> Dictionary:
	var engine: MissionEngine = sim.engine
	var world: MissionWorld = sim.world
	if engine.component_state("aura_core") == DamageableComponent.State.DESTROYED:
		return {"kind": "one_shot"}
	var core := world.body_for("aura_core")
	if core == null or core.freeze:
		return {"kind": "no_collapse"}
	engine.select_weapon("kinetic_accelerator")
	var used := 0
	var blockers := []
	while engine.is_active() and world.body_for("aura_core") != null and used < MAX_FINISH:
		while not engine.can_fire():
			await physics_frame
		var plan: Dictionary = ProbeAim.aim(world, world.body_for("aura_core"))
		var direction: Vector2 = plan.direction
		if direction == Vector2.ZERO:
			blockers.append(plan.blocker)
			var blocking := world.body_for(plan.blocker)
			var clear: Dictionary = ProbeAim.aim(world, blocking) if blocking != null else {}
			direction = clear.get("direction", Vector2.ZERO)
			if direction == Vector2.ZERO:
				break
		world.fire(direction)
		used += 1
		await _frames(50)
		await _settle(world, 3.0)
	if engine.component_state("aura_core") == DamageableComponent.State.DESTROYED:
		return {"kind": "kinetic_finish", "rounds": used, "blockers": blockers}
	return {"kind": "blocked", "rounds": used, "blockers": blockers}


func _make(layout: String) -> Dictionary:
	var def := MissionDefinition.load_from_file(MISSION, _materials, _weapons)
	Layouts.apply(def, layout)
	var engine := MissionEngine.new(def, _materials, _weapons)
	var viewport := SubViewport.new()
	viewport.render_target_update_mode = SubViewport.UPDATE_DISABLED
	root.add_child(viewport)
	var world := MissionWorld.new()
	viewport.add_child(world)
	world.setup(def, engine, _materials)
	return {"engine": engine, "world": world, "viewport": viewport}


func _settle(world: MissionWorld, seconds: float = 8.0) -> void:
	for i in int(seconds * 60.0):
		if i > 30 and world.projectiles.is_empty() and world.is_settled():
			return
		await physics_frame


func _frames(count: int) -> void:
	for i in count:
		await physics_frame


func _free(sim: Dictionary) -> void:
	root.remove_child(sim.viewport)
	(sim.viewport as Node).queue_free()
