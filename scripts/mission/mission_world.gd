class_name MissionWorld
extends Node2D
## The 2D physics side of a mission: ground, static geometry, one ComponentBody per facility
## component and the projectiles in flight. It translates physics events into MissionEngine
## calls (projectile hits, blasts, collision damage, falls) and engine signals back into physics
## (release unsupported or unstable bodies, remove destroyed ones, apply secondary blasts).
## It is never drawn: the 3D MissionView renders it. Headless-testable.

signal projectile_spawned(projectile: WeaponProjectile)
signal projectile_removed(projectile: WeaponProjectile)
signal component_removed(component_id: String, at: Vector2)
signal blast_happened(center: Vector2, radius: float)
## A hard hit: a projectile strike or a structural collision. `component_id` is the component
## that was hit ("" for the ground and static geometry), so feedback can follow its material.
signal impact_happened(at: Vector2, strength: float, component_id: String)

## Where the weapon muzzle sits relative to the operative's feet (px; y up is negative).
const MUZZLE_OFFSET := Vector2(46.0, -128.0)
const GROUND_DEPTH := 400.0
const GROUND_MARGIN := 800.0
## A blast only knocks a frozen piece loose if it would move it at least this fast (px/s).
const MIN_PUSH_SPEED := 60.0
const SETTLE_MIN_TIME := 0.3
## Blast occlusion: a component between a blast and its target passes its material's
## blast_transmission (data/materials.json); static geometry and unknown materials pass the
## minimum. Blockers compound, up to OCCLUSION_MAX_BLOCKERS along one ray.
const OCCLUSION_MIN_TRANSMISSION := MaterialCatalog.MIN_BLAST_TRANSMISSION
const OCCLUSION_MAX_BLOCKERS := 4

var engine: MissionEngine
var definition: MissionDefinition
var bodies := {}
var projectiles: Array[WeaponProjectile] = []
var monitor := SimulationMonitor.new()
## Intervening components/statics attenuate blast damage and knockback (approved Batch 5 rule;
## the switch exists for comparison probes and tests).
var blast_occlusion := true
## A blast must move a piece *and everything resting on it* at MIN_PUSH_SPEED to knock it loose,
## so loaded structures are harder to dislodge (approved Batch 5 rule; switchable for probes).
var load_aware_push := true
var materials: MaterialCatalog
var _settled := true
var _kill_bounds := Rect2()
## Last position of destroyed components, for their secondary blasts.
var _secondary_origin := {}


func setup(p_definition: MissionDefinition, p_engine: MissionEngine, p_materials: MaterialCatalog) -> void:
	definition = p_definition
	engine = p_engine
	materials = p_materials if p_materials != null else materials
	visible = false
	monitor.min_time = SETTLE_MIN_TIME
	_kill_bounds = Rect2(-GROUND_MARGIN, -definition.ground_y * 3.0, definition.width + GROUND_MARGIN * 2.0, definition.ground_y * 3.0 + GROUND_DEPTH * 2.0)

	var ground := StaticBox.new(Vector2(definition.width + GROUND_MARGIN * 2.0, GROUND_DEPTH))
	ground.name = "Ground"
	ground.position = Vector2(definition.width / 2.0, definition.ground_y + GROUND_DEPTH / 2.0)
	add_child(ground)
	for s in definition.statics:
		var box := StaticBox.new(s.size)
		box.position = s.position
		box.rotation = s.rotation
		add_child(box)
	for c in definition.components:
		var body := ComponentBody.new(c, p_materials.get_material(c.material))
		body.impacted.connect(_on_component_impacted)
		add_child(body)
		bodies[c.id] = body

	engine.components_released.connect(_on_released)
	engine.component_state_changed.connect(_on_component_state_changed)
	engine.component_destroyed.connect(_on_component_destroyed)
	engine.secondary_blast_requested.connect(_on_secondary_blast)


func muzzle_position() -> Vector2:
	return definition.operative + MUZZLE_OFFSET


## Fires the engine's selected weapon. Returns the projectile, or null when the engine refused.
func fire(direction: Vector2, power: float = 1.0) -> WeaponProjectile:
	var weapon := engine.selected_weapon()
	var velocity := engine.fire(direction, power)
	if velocity == Vector2.ZERO:
		return null
	return spawn_projectile(weapon.id(), weapon.stats, muzzle_position(), velocity)


## Adds a projectile directly (also used by tests to place precise shots).
func spawn_projectile(weapon_id: String, stats: Dictionary, start: Vector2, velocity: Vector2) -> WeaponProjectile:
	var projectile := WeaponProjectile.new(weapon_id, stats, start, velocity)
	projectile.struck.connect(_on_projectile_struck)
	add_child(projectile)
	projectile.reset_physics_interpolation()
	projectiles.append(projectile)
	_settled = false
	monitor.reset()
	projectile_spawned.emit(projectile)
	return projectile


func is_settled() -> bool:
	return _settled


func body_for(component_id: String) -> ComponentBody:
	var body: ComponentBody = bodies.get(component_id)
	return body if body != null and is_instance_valid(body) else null


## Applies blast damage and knockback to every component whose nearest edge is in range.
## Returns the total damage applied.
## `weapon_stats` (optional) adds the weapon's material bonus and `blast_ignores_cover`; `source`
## is the weapon id (secondary blasts pass none).
func blast(center: Vector2, damage: float, radius: float, impulse: float, edge_fraction: float, penetration: float = 0.0, weapon_stats: Dictionary = {}, source: String = "") -> float:
	var ignore_cover := float(weapon_stats.get("blast_ignores_cover", 0.0)) > 0.0
	var applied := 0.0
	blast_happened.emit(center, radius)
	for id: String in bodies.keys():
		var body := body_for(id)
		if body == null:
			continue
		var distance := DamageRules.distance_to_box(center, body.global_position, body.size / 2.0, body.global_rotation)
		if distance > radius:
			continue
		var transmission := blast_transmission(center, body, penetration) if blast_occlusion and not ignore_cover else 1.0
		var bonus := WeaponCatalog.material_multiplier(weapon_stats, body.material_id)
		applied += engine.apply_damage(id, DamageRules.blast_damage(damage, distance, radius, edge_fraction) * transmission * bonus, DamageRules.TYPE_BLAST, penetration, source)
		body = body_for(id)
		if body == null or body.is_queued_for_deletion():
			continue
		var push := DamageRules.blast_impulse(impulse, center, body.global_position, radius + body.size.length() / 2.0, edge_fraction)
		if blast_occlusion and not ignore_cover:
			push *= blast_transmission(center, body, penetration)
		var pushed_mass := supported_mass(id) if load_aware_push else body.mass
		if push.length() / pushed_mass >= MIN_PUSH_SPEED:
			release_component(id)
			body.push(push)
	_settled = false
	monitor.reset()
	return applied


## Hands a component to physics together with everything that rests on it: a frozen piece must
## never be left hanging on a support that can now move. (Structural *failure* is separate and
## only follows destruction, via StructuralDependencySystem.)
func release_component(component_id: String) -> void:
	var queue: Array[String] = [component_id]
	var seen := {}
	while not queue.is_empty():
		var id: String = queue.pop_front()
		if seen.has(id):
			continue
		seen[id] = true
		var body := body_for(id)
		if body != null:
			body.release()
		for dependent: String in engine.structure.dependents_of(id):
			queue.append(dependent)
	_settled = false
	monitor.reset()


## Mass of a component plus every intact component resting on it (directly or indirectly).
func supported_mass(component_id: String) -> float:
	var total := 0.0
	var queue: Array[String] = [component_id]
	var seen := {}
	while not queue.is_empty():
		var id: String = queue.pop_front()
		if seen.has(id):
			continue
		seen[id] = true
		var body := body_for(id)
		if body != null:
			total += body.mass
		for dependent: String in engine.structure.dependents_of(id):
			queue.append(dependent)
	return maxf(total, 0.001)


## Share of a blast that reaches `target` from `center`: a ray to the target's nearest point is
## checked for intervening components (by their material's blast resistance) and statics.
## Penetration lets part of the blocked share through.
func blast_transmission(center: Vector2, target: ComponentBody, penetration: float = 0.0) -> float:
	var local := (center - target.global_position).rotated(-target.global_rotation)
	var half := target.size / 2.0
	var nearest_local := Vector2(clampf(local.x, -half.x, half.x), clampf(local.y, -half.y, half.y))
	if nearest_local == local:
		return 1.0
	var nearest := target.global_position + nearest_local.rotated(target.global_rotation)
	var space := get_world_2d().direct_space_state
	var exclude: Array[RID] = [target.get_rid()]
	for p in projectiles:
		if is_instance_valid(p):
			exclude.append(p.get_rid())
	var transmission := 1.0
	for i in OCCLUSION_MAX_BLOCKERS:
		var query := PhysicsRayQueryParameters2D.create(center, nearest, ComponentBody.STATIC_LAYER | ComponentBody.COLLISION_LAYER, exclude)
		var hit := space.intersect_ray(query)
		if hit.is_empty():
			break
		var blocker: Object = hit.collider
		var passes := OCCLUSION_MIN_TRANSMISSION
		if blocker is ComponentBody and materials != null:
			var material := materials.get_material((blocker as ComponentBody).material_id)
			if material != null:
				passes = maxf(OCCLUSION_MIN_TRANSMISSION, material.blast_transmission)
		passes += (1.0 - passes) * clampf(penetration, 0.0, WeaponCatalog.MAX_PENETRATION)
		transmission *= passes
		exclude.append(hit.rid)
	return transmission


func _physics_process(delta: float) -> void:
	if engine == null:
		return
	var max_linear := 0.0
	var max_angular := 0.0
	for projectile in projectiles.duplicate():
		if not is_instance_valid(projectile):
			projectiles.erase(projectile)
			continue
		if projectile.age > WeaponProjectile.MAX_LIFETIME or not _kill_bounds.has_point(projectile.global_position):
			_remove_projectile(projectile)
			continue
		max_linear = INF
	for id: String in bodies.keys():
		var body := body_for(id)
		if body == null or body.freeze:
			continue
		if not _kill_bounds.has_point(body.global_position):
			engine.destroy_component(id, "out_of_bounds")
			continue
		max_linear = maxf(max_linear, body.linear_velocity.length())
		max_angular = maxf(max_angular, absf(body.angular_velocity))
	if _settled:
		pass
	elif monitor.step(delta, max_linear, max_angular) != SimulationMonitor.Status.RUNNING:
		_settled = true
	engine.tick(delta, _settled)


func _on_projectile_struck(projectile: WeaponProjectile, target: Node, impact_speed: float) -> void:
	var stats := projectile.stats
	var at := projectile.global_position
	impact_happened.emit(at, impact_speed, (target as ComponentBody).component_id if target is ComponentBody else "")
	var applied := 0.0
	var source := projectile.weapon_id
	if target is ComponentBody and float(stats.impact_damage) > 0.0:
		var body := target as ComponentBody
		var damage := DamageRules.projectile_impact_damage(float(stats.impact_damage), impact_speed, float(stats.launch_speed))
		damage *= WeaponCatalog.material_multiplier(stats, body.material_id)
		applied += engine.apply_damage(body.component_id, damage, DamageRules.TYPE_IMPACT, float(stats.penetration), source)
		if projectile.pierces_left > 0 and _can_pierce(projectile, body):
			if applied > 0.0 and not projectile.counted_effective:
				projectile.counted_effective = true
				engine.record_effective_shot()
			projectile.pass_through(body)
			return
	if float(stats.blast_damage) > 0.0:
		applied += blast(at, float(stats.blast_damage), float(stats.blast_radius), float(stats.blast_impulse), float(stats.blast_edge_falloff), float(stats.penetration), stats, source)
	if applied > 0.0 and not projectile.counted_effective:
		projectile.counted_effective = true
		engine.record_effective_shot()
	# Rounds and charges are spent on their (final) strike.
	_remove_projectile.call_deferred(projectile)


## A piercing round passes through a component it destroyed, or one whose material is no
## tougher than the weapon's `pierce_max_resistance` (impact resistance).
func _can_pierce(projectile: WeaponProjectile, body: ComponentBody) -> bool:
	if not is_instance_valid(body) or body.is_queued_for_deletion() or engine.component_state(body.component_id) == DamageableComponent.State.DESTROYED:
		return true
	var material := materials.get_material(body.material_id) if materials != null else null
	return material != null and material.impact_resistance <= float(projectile.stats.get("pierce_max_resistance", 0.95))


func _on_component_impacted(body: ComponentBody, impulse: float, others: Array) -> void:
	var damage := DamageRules.collision_damage(impulse)
	if damage <= 0.0:
		return
	impact_happened.emit(body.global_position, impulse, body.component_id)
	engine.apply_damage(body.component_id, damage, DamageRules.TYPE_STRUCTURAL)
	for other: Variant in others:
		if other is ComponentBody and is_instance_valid(other) and (other as ComponentBody).freeze:
			engine.apply_damage((other as ComponentBody).component_id, damage, DamageRules.TYPE_STRUCTURAL)
	_settled = false


func _on_released(component_ids: Array[String]) -> void:
	for id in component_ids:
		release_component(id)


func _on_component_state_changed(component_id: String, _previous: int, current: int) -> void:
	if current == DamageableComponent.State.CRITICAL:
		release_component(component_id)


func _on_component_destroyed(component_id: String) -> void:
	var body := body_for(component_id)
	if body == null:
		return
	component_removed.emit(component_id, body.global_position)
	bodies.erase(component_id)
	_secondary_origin[component_id] = body.global_position
	remove_child.call_deferred(body)
	body.queue_free()
	_settled = false
	monitor.reset()



func _on_secondary_blast(component_id: String, blast_data: Dictionary) -> void:
	var center: Vector2 = _secondary_origin.get(component_id, Vector2.ZERO)
	# Deferred so the chain resolves outside the physics callback that destroyed the source.
	blast.call_deferred(center, float(blast_data.damage), float(blast_data.radius), float(blast_data.impulse), 0.25)


func _remove_projectile(projectile: WeaponProjectile) -> void:
	if not is_instance_valid(projectile) or not projectiles.has(projectile):
		return
	projectiles.erase(projectile)
	projectile_removed.emit(projectile)
	projectile.queue_free()
	monitor.reset()
	_settled = false
