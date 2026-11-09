extends SceneTree
## Design-evaluation probe for the Helix layout. Fires real shots from the operative's muzzle
## across a sweep of trajectories and reports, per design variant, how many single Breach
## Charges destroy the AI core, how many kinetic shots each aim angle needs, and what the rack
## cluster and power-cell tactics do. Evidence for balance decisions; not a pass/fail test.
##
##   godot_console --headless --fixed-fps 60 -s tools/regression/tactics_probe.gd [-- --variants=a,b]

const MISSION := "res://data/missions/helix_01.json"
const HOOD := {"id": "core_hood", "kind": "core_shield", "material": "reinforced_steel",
	"position": Vector2(885, 360), "size": Vector2(76, 12), "rotation": 0.0, "health_scale": 1.0,
	"critical_asset": false, "supports": ["aura_core"], "min_supports": -1}
const VARIANTS := ["baseline", "occlusion", "tough_core", "occlusion_hood", "occlusion_loaded", "occlusion_hood_loaded", "proposal", "proposal_hardened"]
const BREACH_ANGLES := [15, 20, 25, 30, 35, 40, 45, 50, 55, 60, 65, 70, 75, 80]
const BREACH_POWERS := [0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
const KINETIC_ANGLES := [-8, -6, -4, -2, 0, 2, 4, 6, 8, 10, 12, 14, 16, 18, 20]
const KINETIC_MAX_SHOTS := 8

var _materials := MaterialCatalog.load_from_file()
var _weapons := WeaponCatalog.load_from_file()


func _initialize() -> void:
	_run.call_deferred()


func _run() -> void:
	var variants: Array = VARIANTS
	for arg in OS.get_cmdline_user_args():
		if arg.begins_with("--variants="):
			variants = arg.trim_prefix("--variants=").split(",")
	for variant: String in variants:
		await _evaluate(variant)
	quit()


func _evaluate(variant: String) -> void:
	# Breach sweep: one charge per trajectory.
	var one_shot := 0
	var core_hit := 0
	var landings := []
	for angle: int in BREACH_ANGLES:
		for power: float in BREACH_POWERS:
			var sim := _make(variant)
			sim.engine.select_weapon("breach_charge")
			sim.world.fire(Vector2.RIGHT.rotated(-deg_to_rad(angle)), power)
			await _settle(sim, 360)
			var state: int = sim.engine.component_state("aura_core")
			if state == DamageableComponent.State.DESTROYED:
				one_shot += 1
				landings.append("%d°/%.1f" % [angle, power])
			elif state > DamageableComponent.State.INTACT:
				core_hit += 1
			_free(sim)
	var total := BREACH_ANGLES.size() * BREACH_POWERS.size()
	# Kinetic: repeat the same aim until the core falls (or the cap).
	var kinetic := []
	var first_hits := []
	for angle: int in KINETIC_ANGLES:
		var sim := _make(variant)
		var hit := [""]
		sim.engine.component_state_changed.connect(func(id: String, _p: int, _c: int) -> void:
			if hit[0] == "":
				hit[0] = id)
		var damaged_first := [""]
		sim.world.impact_happened.connect(func(_at: Vector2, _s: float) -> void: pass)
		var shots := 0
		for i in KINETIC_MAX_SHOTS:
			if not sim.engine.is_active():
				break
			while not sim.engine.can_fire():
				await physics_frame
			sim.world.fire(Vector2.RIGHT.rotated(-deg_to_rad(angle)))
			shots += 1
			await _frames(70)
			if shots == 1:
				first_hits.append("%d°:%s" % [angle, hit[0] if hit[0] != "" else "miss/no-state-change"])
		await _settle(sim, 360)
		kinetic.append([angle, shots if sim.engine.component_state("aura_core") == DamageableComponent.State.DESTROYED else -1])
		_free(sim)
	var clears := kinetic.filter(func(k: Array) -> bool: return k[1] > 0)
	var best := clears.map(func(k: Array) -> int: return k[1])
	best.sort()
	print("PROBE %s breach: one-shot core kills %d/%d (%.0f%%), core damaged but alive %d; one-shot trajectories: %s" % [
		variant, one_shot, total, 100.0 * one_shot / total, core_hit, ", ".join(landings.slice(0, 12))])
	print("PROBE %s kinetic: angles clearing the core within %d shots: %d/%d; fewest shots %s; per angle %s" % [
		variant, KINETIC_MAX_SHOTS, clears.size(), kinetic.size(), str(best[0]) if not best.is_empty() else "-", str(kinetic)])
	# Two-step play: a column breach, then kinetic finishing shots at wherever the core is.
	var two_step := []
	for spec: Array in [[45, 0.7], [30, 0.9], [25, 1.0]]:
		var sim := _make(variant)
		sim.engine.select_weapon("breach_charge")
		sim.world.fire(Vector2.RIGHT.rotated(-deg_to_rad(spec[0])), spec[1])
		await _settle(sim, 360)
		var follow := 0
		sim.engine.select_weapon("kinetic_accelerator")
		while sim.engine.is_active() and sim.engine.component_state("aura_core") != DamageableComponent.State.DESTROYED and follow < 8:
			var core: ComponentBody = sim.world.body_for("aura_core")
			if core == null:
				break
			while not sim.engine.can_fire():
				await physics_frame
			sim.world.fire(core.global_position - sim.world.muzzle_position())
			follow += 1
			await _frames(70)
		two_step.append("%d°/%.1f: core %s after breach + %d kinetic" % [spec[0], spec[1], _state(sim, "aura_core"), follow])
		_free(sim)
	print("PROBE %s two-step: %s" % [variant, " | ".join(two_step)])
	# Placed tactics.
	var rack := _make(variant)
	rack.world.spawn_projectile("breach_charge", rack.engine.weapons.breach_charge.stats, Vector2(674, 480), Vector2(0, 300))
	await _settle(rack, 300)
	var cell := _make(variant)
	cell.engine.apply_damage("power_cell", 9999.0, DamageRules.TYPE_IMPACT, 0.9)
	await _settle(cell, 300)
	if variant == "baseline":
		print("PROBE %s kinetic first shot (first component to change state): %s" % [variant, ", ".join(first_hits)])
	print("PROBE %s placed: rack-cluster breach -> racks %s/%s, core %s | power-cell chain -> core %s" % [
		variant, _state(rack, "rack_1"), _state(rack, "rack_2"), _state(rack, "aura_core"), _state(cell, "aura_core")])
	_free(rack)
	_free(cell)


func _make(variant: String) -> Dictionary:
	var def := MissionDefinition.load_from_file(MISSION, _materials, _weapons)
	for c in def.components:
		if c.id == "aura_core" and (variant == "tough_core" or variant == "proposal"):
			c.health_scale = 3.0
		if c.id == "aura_core" and variant == "proposal_hardened":
			c.material = "composite"
			c.health_scale = 2.0
		if c.id == "blast_wall" and variant.begins_with("proposal"):
			c.size = Vector2(30, 90)
			c.position = Vector2(590, 595)
	if variant.begins_with("occlusion_hood"):
		def.components.append(HOOD.duplicate(true))
	var engine := MissionEngine.new(def, _materials, _weapons)
	var viewport := SubViewport.new()
	viewport.render_target_update_mode = SubViewport.UPDATE_DISABLED
	root.add_child(viewport)
	var world := MissionWorld.new()
	world.blast_occlusion = variant.begins_with("occlusion") or variant.begins_with("proposal")
	world.load_aware_push = variant.ends_with("loaded") or variant.begins_with("proposal")
	viewport.add_child(world)
	world.setup(def, engine, _materials)
	return {"engine": engine, "world": world, "viewport": viewport}


func _settle(sim: Dictionary, max_frames: int) -> void:
	for i in max_frames:
		if sim.world.projectiles.is_empty() and sim.world.is_settled() and i > 30:
			return
		await physics_frame


func _frames(count: int) -> void:
	for i in count:
		await physics_frame


func _free(sim: Dictionary) -> void:
	root.remove_child(sim.viewport)
	(sim.viewport as Node).queue_free()


func _state(sim: Dictionary, id: String) -> String:
	return ["intact", "damaged", "critical", "destroyed"][sim.engine.component_state(id)] if sim.engine.component_state(id) >= 0 else "?"
