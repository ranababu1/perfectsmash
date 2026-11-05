class_name GameSession
extends Node2D
## Runs one level attempt: builds the physics world, spawns shots, watches for settling and
## evaluates the objective on the settled state. Has no UI or input code, so it runs headless
## for automated level verification.
##
## Explosions (explosive crates, blast shots) are resolved here, in _physics_process, in a fixed
## order: a detonation queues a blast; a blast pushes every body in range and lights a fuse on
## each explosive crate it reaches; fuses burn for CHAIN_DELAY_STEPS steps.

signal shots_changed(remaining: int, budget: int)
signal phase_changed(phase: SessionRules.Phase)
signal launched(velocity: Vector2)
signal target_destroyed(at: Vector2)
signal ally_lost(at: Vector2)
signal block_shattered(at: Vector2)
signal exploded(at: Vector2)
signal impact(strength: float, at: Vector2)
signal shot_resolved(timed_out: bool)
signal finished(won: bool, stars: int, shots_used: int)


var definition: LevelDefinition
var rules: SessionRules
var monitor := SimulationMonitor.new()
var targets_remaining := 0
var allies_lost := 0
var cargo_lost := 0
var _world: Node2D
var _projectile: ProjectileBody
## Pending blast centres (Vector2) to resolve on the next physics step.
var _blasts: Array[Vector2] = []
## Lit fuses: {"body": BlockBody, "steps": int}.
var _fuses: Array[Dictionary] = []


func setup(def: LevelDefinition) -> void:
	definition = def
	restart()


func restart() -> void:
	if _world != null:
		# Remove immediately so old bodies leave the physics space before new ones are added.
		remove_child(_world)
		_world.queue_free()
	_projectile = null
	_blasts.clear()
	_fuses.clear()
	_world = LevelLoader.build(definition)
	add_child(_world)
	targets_remaining = 0
	allies_lost = 0
	cargo_lost = 0
	for node in _world.get_children():
		if node is TargetBody:
			if node.is_ally:
				node.destroyed.connect(_on_ally_destroyed)
			else:
				targets_remaining += 1
				node.destroyed.connect(_on_target_destroyed)
		elif node is BlockBody:
			node.shattered.connect(_on_block_shattered)
			node.impacted.connect(_on_impact)
			node.detonated.connect(_on_detonated)
	rules = SessionRules.new(definition.shots)
	monitor.reset()
	queue_redraw()
	shots_changed.emit(rules.shots_remaining(), rules.shots_budget)
	phase_changed.emit(rules.phase)


func can_launch() -> bool:
	return rules != null and rules.can_launch()


func launcher_position() -> Vector2:
	return definition.launcher


## Ammo of the next shot (or of the last one once the budget is spent).
func current_ammo() -> String:
	return definition.ammo_for_shot(mini(rules.shots_used, rules.shots_budget - 1))


func launch(velocity: Vector2) -> bool:
	if not can_launch():
		return false
	var ammo := current_ammo()
	rules.register_launch()
	_arm_breakables()
	_projectile = ProjectileBody.new(ammo)
	_projectile.position = definition.launcher
	_projectile.linear_velocity = velocity.limit_length(GameConfig.MAX_LAUNCH_SPEED)
	_projectile.impacted.connect(_on_impact)
	_projectile.detonated.connect(_on_projectile_detonated.bind(_projectile))
	_world.add_child(_projectile)
	_projectile.reset_physics_interpolation()
	monitor.reset()
	launched.emit(_projectile.linear_velocity)
	shots_changed.emit(rules.shots_remaining(), rules.shots_budget)
	phase_changed.emit(rules.phase)
	return true


func _physics_process(delta: float) -> void:
	if rules == null or rules.phase != SessionRules.Phase.SIMULATING:
		return
	_resolve_explosions()
	var max_linear := 0.0
	var max_angular := 0.0
	for node in _world.get_children():
		var body := node as RigidBody2D
		if body == null or body.is_queued_for_deletion():
			continue
		if DestructionRules.is_out_of_bounds(body.global_position):
			_remove_out_of_bounds(body)
			continue
		max_linear = maxf(max_linear, body.linear_velocity.length())
		max_angular = maxf(max_angular, absf(body.angular_velocity))
	if not _blasts.is_empty() or not _fuses.is_empty():
		# A burning fuse is pending motion: never call the shot settled before it goes off.
		max_linear = INF
	var status := monitor.step(delta, max_linear, max_angular)
	if status != SimulationMonitor.Status.RUNNING:
		_resolve_shot(status == SimulationMonitor.Status.TIMED_OUT)


func _resolve_explosions() -> void:
	var burning: Array[Dictionary] = []
	for fuse in _fuses:
		fuse.steps -= 1
		if fuse.steps > 0:
			burning.append(fuse)
		elif is_instance_valid(fuse.body):
			fuse.body.detonate()
	_fuses = burning
	var blasts := _blasts.duplicate()
	_blasts.clear()
	for at in blasts:
		_explode(at)


## Pushes every body in range outward and lights the fuses of explosive crates it reaches.
func _explode(at: Vector2) -> void:
	exploded.emit(at)
	for node in _world.get_children():
		var body := node as RigidBody2D
		if body == null or body.is_queued_for_deletion():
			continue
		var offset := body.global_position - at
		var distance := offset.length()
		if distance >= GameConfig.BLAST_RADIUS:
			continue
		if body is BlockBody and body.is_explosive():
			if not body.is_broken() and not _fuses.any(func(f: Dictionary) -> bool: return f.body == body):
				_fuses.append({"body": body, "steps": GameConfig.CHAIN_DELAY_STEPS})
			continue
		var direction := offset / distance if distance > 0.001 else Vector2.UP
		var speed := GameConfig.BLAST_SPEED * (1.0 - distance / GameConfig.BLAST_RADIUS)
		body.sleeping = false
		body.apply_central_impulse(direction * speed * body.mass)


func _resolve_shot(timed_out: bool) -> void:
	if _projectile != null and is_instance_valid(_projectile):
		_world.remove_child(_projectile)
		_projectile.queue_free()
	_projectile = null
	var outcome := ObjectiveEvaluator.evaluate(definition.objective_type, state_snapshot())
	var phase := rules.register_settled(outcome == ObjectiveEvaluator.Outcome.MET, outcome == ObjectiveEvaluator.Outcome.FAILED)
	shot_resolved.emit(timed_out)
	phase_changed.emit(phase)
	if rules.is_finished():
		var won := phase == SessionRules.Phase.WON
		var stars := ScoreRules.stars_for(rules.shots_used, definition.par) if won else 0
		finished.emit(won, stars, rules.shots_used)


## Everything ObjectiveEvaluator needs, read from the current (settled) world.
func state_snapshot() -> Dictionary:
	var cargo_total := definition.cargo_count()
	var in_zone := 0
	for node in _world.get_children():
		var block := node as BlockBody
		if block != null and block.is_cargo() and not block.is_queued_for_deletion() and definition.zone.has_point(block.global_position):
			in_zone += 1
	return {
		"targets_remaining": targets_remaining,
		"highest_block_top": highest_block_top(),
		"topple_line_y": definition.topple_line_y,
		"cargo_total": cargo_total,
		"cargo_in_zone": in_zone,
		"cargo_lost": cargo_lost,
		"allies_lost": allies_lost,
	}


## Distance from the nearest remaining cargo crate to the drop zone centre (solver progress signal).
func cargo_distance_to_zone() -> float:
	var best := INF
	for node in _world.get_children():
		var block := node as BlockBody
		if block != null and block.is_cargo() and not block.is_queued_for_deletion():
			best = minf(best, block.global_position.distance_to(definition.zone.get_center()))
	return best


## Smallest y of any intact block's top edge; INF when no blocks remain.
func highest_block_top() -> float:
	var top := INF
	for node in _world.get_children():
		var block := node as BlockBody
		if block != null and not block.is_broken() and not block.is_queued_for_deletion():
			top = minf(top, block.top_y())
	return top


func _arm_breakables() -> void:
	for node in _world.get_children():
		if node is TargetBody or node is BlockBody:
			node.armed = true


func _remove_out_of_bounds(body: RigidBody2D) -> void:
	if body is TargetBody:
		body.destroy()
		return
	if body is BlockBody and body.is_cargo():
		cargo_lost += 1
	if body == _projectile:
		_projectile = null
	_world.remove_child(body)
	body.queue_free()


func _on_target_destroyed(at: Vector2) -> void:
	targets_remaining = maxi(targets_remaining - 1, 0)
	target_destroyed.emit(at)


func _on_ally_destroyed(at: Vector2) -> void:
	allies_lost += 1
	ally_lost.emit(at)


func _on_block_shattered(at: Vector2) -> void:
	block_shattered.emit(at)


func _on_detonated(at: Vector2) -> void:
	_blasts.append(at)


func _on_projectile_detonated(at: Vector2, projectile: ProjectileBody) -> void:
	_blasts.append(at)
	if is_instance_valid(projectile):
		projectile.queue_free()
	if projectile == _projectile:
		_projectile = null


func _on_impact(strength: float, at: Vector2) -> void:
	impact.emit(strength, at)


func _draw() -> void:
	if definition == null:
		return
	# Launcher post: purely visual, the projectile spawns at its tip.
	var tip := definition.launcher
	var base := Vector2(tip.x, GameConfig.GROUND_TOP)
	var yoke := tip + Vector2(0, GameConfig.PROJECTILE_RADIUS + 10)
	draw_line(base, yoke, Palette.STATIC_EDGE, 8.0, true)
	draw_line(yoke, tip + Vector2(-14, 6), Palette.STATIC_EDGE, 5.0, true)
	draw_line(yoke, tip + Vector2(14, 6), Palette.STATIC_EDGE, 5.0, true)
	draw_circle(base, 9.0, Palette.STATIC, true, -1.0, true)
	if definition.objective_type == LevelDefinition.OBJECTIVE_TOPPLE:
		var y := definition.topple_line_y
		var x := 0.0
		# A faint wash below the line shows the "safe" zone; the dashes mark the exact limit.
		draw_rect(Rect2(-600, y, GameConfig.WORLD_WIDTH + 1200, GameConfig.GROUND_TOP - y), Color(Palette.TOPPLE_LINE, 0.05))
		while x < GameConfig.WORLD_WIDTH:
			draw_line(Vector2(x, y), Vector2(x + 14.0, y), Color(Palette.TOPPLE_LINE, 0.8), 2.0, true)
			x += 24.0
	elif definition.objective_type == LevelDefinition.OBJECTIVE_DELIVER:
		_draw_drop_zone(definition.zone)


## Drop zone: a soft mint wash, dashed outline and a down chevron, like a marked landing pad.
func _draw_drop_zone(zone: Rect2) -> void:
	draw_rect(zone, Color(Palette.DROP_ZONE, 0.08))
	var corners := [zone.position, Vector2(zone.end.x, zone.position.y), zone.end, Vector2(zone.position.x, zone.end.y)]
	for i in 4:
		var a: Vector2 = corners[i]
		var b: Vector2 = corners[(i + 1) % 4]
		var length := a.distance_to(b)
		var t := 0.0
		while t < length:
			draw_line(a.lerp(b, t / length), a.lerp(b, minf(t + 12.0, length) / length), Color(Palette.DROP_ZONE, 0.85), 2.0, true)
			t += 20.0
	var c := Vector2(zone.get_center().x, zone.position.y + 14.0)
	draw_polyline(PackedVector2Array([c + Vector2(-12, -6), c + Vector2(0, 4), c + Vector2(12, -6)]), Color(Palette.DROP_ZONE, 0.9), 3.0, true)
