extends RefCounted
## Aiming helper for the design probes. Emulates a player using the arc preview: it tries aim
## points from the target's centre upwards and returns the first direction whose ballistic path
## (fixed-speed weapon, its gravity scale) first strikes `target`. Returns Vector2.ZERO when no
## clear line exists, together with the component that blocks the centre aim.

const STEP := 1.0 / 60.0
const MAX_TIME := 1.5
const LIFTS := [0, -4, -8, -12, -16, -20, -24, -28, -32, -40, -50, -60, -75, -90]


## Returns {direction: Vector2 (ZERO when blocked), blocker: String (component id, "static" or "")}.
## `through`: component ids a piercing round is expected to pass (treated as transparent).
static func aim(world: MissionWorld, target: ComponentBody, through: Array = []) -> Dictionary:
	var transparent: Array[RID] = []
	for id: Variant in through:
		var body := world.body_for(str(id))
		if body != null:
			transparent.append(body.get_rid())
	var weapon := world.engine.selected_weapon()
	var gravity := float(ProjectSettings.get_setting("physics/2d/default_gravity")) * float(weapon.stats.gravity_scale)
	var muzzle := world.muzzle_position()
	var blocker := ""
	var trace := []
	var clearable := []
	for lift: int in LIFTS:
		var direction := (target.global_position + Vector2(0, lift)) - muzzle
		var hit := first_hit(world, muzzle, weapon.launch_velocity(direction, 1.0), gravity, float(weapon.stats.projectile_radius), transparent)
		trace.append("%d:%s" % [lift, (hit as ComponentBody).component_id if hit is ComponentBody else ("static" if hit != null else "none")])
		if hit == target:
			return {"direction": direction, "blocker": "", "trace": trace}
		if lift == 0:
			blocker = (hit as ComponentBody).component_id if hit is ComponentBody else ("static" if hit != null else "")
		# A player clears the softest thing in the way: prefer a non-steel component.
		if hit is ComponentBody and (hit as ComponentBody).material_id != "reinforced_steel" and not clearable.has((hit as ComponentBody).component_id):
			clearable.append((hit as ComponentBody).component_id)
	if not clearable.is_empty():
		blocker = clearable[0]
	return {"direction": Vector2.ZERO, "blocker": blocker, "trace": trace}


static func first_hit(world: MissionWorld, start: Vector2, velocity: Vector2, gravity: float, radius: float = 4.0, transparent: Array[RID] = []) -> Object:
	var space := world.get_world_2d().direct_space_state
	var exclude: Array[RID] = transparent.duplicate()
	for p in world.projectiles:
		if is_instance_valid(p):
			exclude.append(p.get_rid())
	var circle := CircleShape2D.new()
	circle.radius = radius
	var query := PhysicsShapeQueryParameters2D.new()
	query.shape = circle
	query.collision_mask = ComponentBody.STATIC_LAYER | ComponentBody.COLLISION_LAYER
	query.exclude = exclude
	var position := start
	var t := 0.0
	while t < MAX_TIME:
		var next := start + velocity * (t + STEP) + Vector2(0, 0.5 * gravity * (t + STEP) * (t + STEP))
		query.transform = Transform2D(0.0, position)
		query.motion = next - position
		var fractions := space.cast_motion(query)
		if fractions.size() == 2 and fractions[1] < 1.0:
			query.transform = Transform2D(0.0, position + (next - position) * fractions[1])
			query.motion = Vector2.ZERO
			var hits := space.intersect_shape(query, 1)
			return hits[0].collider if not hits.is_empty() else null
		position = next
		t += STEP
	return null
