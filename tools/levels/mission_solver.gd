extends RefCounted
## Plays a mission like a player, through MissionWorld.fire: real muzzle position, ammunition,
## reload cooldowns and settle detection. Used by tools/levels/probe_missions.gd (design probe)
## and tests/levels/ (regression). A solution is a list of steps:
##   {"weapon": "kinetic_accelerator", "target": "<component id>"}   aimed with the arc preview
##   {"weapon": "breach_charge", "target": "<component id>"}         lobbed; first contact = target
##   {"weapon": "breach_charge", "point": [x, y]}                     lobbed through a plane point
## Optional "lift": [px, ...] overrides the kinetic aim offsets tried above the target centre.

const ProbeAim := preload("res://tools/regression/probe_aim.gd")
const SHOT_TIMEOUT := 12.0
const RELOAD_TIMEOUT := 5.0
const FINISH_TIMEOUT := 12.0


## {world: MissionWorld, viewport: SubViewport} or {error: String}.
static func make_world(tree: SceneTree, path: String) -> Dictionary:
	var materials := MaterialCatalog.load_from_file()
	var weapons := WeaponCatalog.load_from_file()
	var def := MissionDefinition.load_from_file(path, materials, weapons)
	if not def.is_valid():
		return {"error": ", ".join(def.errors)}
	var engine := MissionEngine.new(def, materials, weapons)
	var viewport := SubViewport.new()
	viewport.render_target_update_mode = SubViewport.UPDATE_DISABLED
	tree.root.add_child(viewport)
	var world := MissionWorld.new()
	viewport.add_child(world)
	world.setup(def, engine, materials)
	return {"world": world, "viewport": viewport}


static func free_world(tree: SceneTree, made: Dictionary) -> void:
	if made.has("viewport"):
		tree.root.remove_child(made.viewport)
		made.viewport.queue_free()


## Runs `frames` physics frames untouched; returns the ids that moved, unfroze or took damage.
static func stand_check(tree: SceneTree, world: MissionWorld, frames: int = 180) -> Array[String]:
	var start := {}
	for id: String in world.bodies:
		start[id] = world.body_for(id).global_position
	for i in frames:
		await tree.physics_frame
	var problems: Array[String] = []
	for id: String in world.bodies:
		var body := world.body_for(id)
		if body == null or not body.freeze or world.engine.component_state(id) != DamageableComponent.State.INTACT \
				or body.global_position.distance_to(start[id]) > 0.5:
			problems.append(id)
	return problems


## Plays `steps`; returns {success, phase, shots, effective, elapsed, log: Array[String], blocked}.
static func play(tree: SceneTree, world: MissionWorld, steps: Array) -> Dictionary:
	var engine := world.engine
	var log: Array[String] = []
	var blocked := ""
	for step: Dictionary in steps:
		if not engine.is_active():
			break
		# A player does not aim at something already destroyed: skip the step.
		if step.has("target") and (world.body_for(step.target) == null \
				or engine.component_state(step.target) == DamageableComponent.State.DESTROYED):
			continue
		var weapon_id: String = step.weapon
		if not engine.select_weapon(weapon_id) and engine.selected_weapon_id != weapon_id:
			blocked = "cannot select %s" % weapon_id
			break
		await _until(tree, func() -> bool: return engine.can_fire() or not engine.is_active(), RELOAD_TIMEOUT)
		if not engine.is_active():
			break
		var plan := aim(world, step)
		if plan.direction == Vector2.ZERO:
			blocked = "%s at %s blocked by %s" % [weapon_id, step.get("target", step.get("point")), plan.blocker]
			break
		world.fire(plan.direction, plan.power)
		await tree.physics_frame
		await _until(tree, func() -> bool: return (world.projectiles.is_empty() and world.is_settled()) or not engine.is_active(), SHOT_TIMEOUT)
		log.append("%s -> %s: %s" % [weapon_id, step.get("target", step.get("point")), _states(world)])
	if blocked.is_empty():
		await _until(tree, func() -> bool: return not engine.is_active(), FINISH_TIMEOUT)
	return {
		"success": engine.phase == MissionEngine.Phase.SUCCEEDED,
		"phase": engine.phase,
		"shots": engine.shots_fired(),
		"effective": engine.effective_shots,
		"elapsed": snappedf(engine.elapsed, 0.1),
		"log": log,
		"blocked": blocked,
	}


## {direction, power, blocker}. Direction is ZERO when no clear shot was found.
static func aim(world: MissionWorld, step: Dictionary) -> Dictionary:
	var weapon := world.engine.selected_weapon()
	var target: ComponentBody = world.body_for(step.target) if step.has("target") else null
	if weapon.stats.get("blast_radius", 0) > 0 and str(weapon.spec.delivery) == "lobbed":
		var point: Vector2 = target.global_position if target != null else Vector2(step.point[0], step.point[1])
		return _lob(world, weapon, point, target)
	if target == null:
		return {"direction": Vector2.ZERO, "power": 1.0, "blocker": "no target"}
	var plan: Dictionary = ProbeAim.aim(world, target)
	plan["power"] = 1.0
	return plan


## Sweeps elevation and power for a lob whose first contact is `target` (or that passes within
## 20 px of `point` before touching anything). Prefers the lowest arc that works.
static func _lob(world: MissionWorld, weapon: WeaponState, point: Vector2, target: ComponentBody) -> Dictionary:
	var gravity := float(ProjectSettings.get_setting("physics/2d/default_gravity")) * float(weapon.stats.gravity_scale)
	var muzzle := world.muzzle_position()
	var radius := float(weapon.stats.projectile_radius)
	var blocker := ""
	for degrees in range(10, 80, 2):
		var direction := Vector2.from_angle(deg_to_rad(-degrees))
		for step in range(0, 51):
			var power := step / 50.0
			var velocity := weapon.launch_velocity(direction, power)
			if target != null:
				var hit := ProbeAim.first_hit(world, muzzle, velocity, gravity, radius)
				if hit == target:
					return {"direction": direction, "power": power, "blocker": ""}
				if hit is ComponentBody and blocker.is_empty():
					blocker = (hit as ComponentBody).component_id
			elif _passes_near(world, muzzle, velocity, gravity, radius, point):
				return {"direction": direction, "power": power, "blocker": ""}
	return {"direction": Vector2.ZERO, "power": 1.0, "blocker": blocker if not blocker.is_empty() else "no arc"}


static func _passes_near(world: MissionWorld, start: Vector2, velocity: Vector2, gravity: float, radius: float, point: Vector2) -> bool:
	var hit := ProbeAim.first_hit(world, start, velocity, gravity, radius)
	# Time at which the arc reaches the point's x, then distance there.
	if absf(velocity.x) < 1.0:
		return false
	var t := (point.x - start.x) / velocity.x
	if t <= 0.0:
		return false
	var at := start + velocity * t + Vector2(0, 0.5 * gravity * t * t)
	if at.distance_to(point) > 20.0:
		return false
	return hit == null or (hit is Node2D and (hit as Node2D).global_position.distance_to(point) < 90.0)


static func _states(world: MissionWorld) -> String:
	var parts: Array[String] = []
	for id: String in world.engine.components:
		var state := world.engine.component_state(id)
		if state != DamageableComponent.State.INTACT:
			parts.append("%s=%s" % [id, ["I", "D", "C", "X"][state]])
	return " ".join(parts) if not parts.is_empty() else "no damage"


static func _until(tree: SceneTree, condition: Callable, seconds: float) -> void:
	for i in int(seconds * 60.0):
		if condition.call():
			return
		await tree.physics_frame
