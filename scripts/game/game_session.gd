class_name GameSession
extends Node2D
## Runs one level attempt: builds the physics world, spawns shots, watches for settling and
## evaluates the objective on the settled state. Has no UI or input code, so it runs headless
## for automated level verification.

signal shots_changed(remaining: int, budget: int)
signal phase_changed(phase: SessionRules.Phase)
signal launched(velocity: Vector2)
signal target_destroyed(at: Vector2)
signal block_shattered(at: Vector2)
signal impact(strength: float, at: Vector2)
signal shot_resolved(timed_out: bool)
signal finished(won: bool, stars: int, shots_used: int)

const LAUNCHER_POST_HEIGHT := 44.0

var definition: LevelDefinition
var rules: SessionRules
var monitor := SimulationMonitor.new()
var targets_remaining := 0
var _world: Node2D
var _projectile: ProjectileBody


func setup(def: LevelDefinition) -> void:
	definition = def
	restart()


func restart() -> void:
	if _world != null:
		# Remove immediately so old bodies leave the physics space before new ones are added.
		remove_child(_world)
		_world.queue_free()
	_projectile = null
	_world = LevelLoader.build(definition)
	add_child(_world)
	targets_remaining = 0
	for node in _world.get_children():
		if node is TargetBody:
			targets_remaining += 1
			node.destroyed.connect(_on_target_destroyed)
		elif node is BlockBody:
			node.shattered.connect(_on_block_shattered)
			node.impacted.connect(_on_impact)
	rules = SessionRules.new(definition.shots)
	monitor.reset()
	queue_redraw()
	shots_changed.emit(rules.shots_remaining(), rules.shots_budget)
	phase_changed.emit(rules.phase)


func can_launch() -> bool:
	return rules != null and rules.can_launch()


func launcher_position() -> Vector2:
	return definition.launcher


func launch(velocity: Vector2) -> bool:
	if not can_launch():
		return false
	rules.register_launch()
	_arm_breakables()
	_projectile = ProjectileBody.new()
	_projectile.position = definition.launcher
	_projectile.linear_velocity = velocity.limit_length(GameConfig.MAX_LAUNCH_SPEED)
	_projectile.impacted.connect(_on_impact)
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
	var status := monitor.step(delta, max_linear, max_angular)
	if status != SimulationMonitor.Status.RUNNING:
		_resolve_shot(status == SimulationMonitor.Status.TIMED_OUT)


func _resolve_shot(timed_out: bool) -> void:
	if _projectile != null and is_instance_valid(_projectile):
		_world.remove_child(_projectile)
		_projectile.queue_free()
	_projectile = null
	var met := ObjectiveEvaluator.is_met(definition.objective_type, targets_remaining, highest_block_top(), definition.topple_line_y)
	var phase := rules.register_settled(met)
	shot_resolved.emit(timed_out)
	phase_changed.emit(phase)
	if rules.is_finished():
		var won := phase == SessionRules.Phase.WON
		var stars := ScoreRules.stars_for(rules.shots_used, definition.par) if won else 0
		finished.emit(won, stars, rules.shots_used)


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
	if body == _projectile:
		_projectile = null
	_world.remove_child(body)
	body.queue_free()


func _on_target_destroyed(at: Vector2) -> void:
	targets_remaining = maxi(targets_remaining - 1, 0)
	target_destroyed.emit(at)


func _on_block_shattered(at: Vector2) -> void:
	block_shattered.emit(at)


func _on_impact(strength: float, at: Vector2) -> void:
	impact.emit(strength, at)


func _draw() -> void:
	if definition == null:
		return
	# Launcher post: purely visual, the projectile spawns at its tip.
	var tip := definition.launcher
	var base := Vector2(tip.x, GameConfig.GROUND_TOP)
	draw_line(base, tip + Vector2(0, GameConfig.PROJECTILE_RADIUS), Palette.STATIC_EDGE, 10.0)
	draw_line(tip + Vector2(-16, LAUNCHER_POST_HEIGHT * 0.4), tip + Vector2(0, GameConfig.PROJECTILE_RADIUS + 6), Palette.STATIC_EDGE, 6.0)
	draw_line(tip + Vector2(16, LAUNCHER_POST_HEIGHT * 0.4), tip + Vector2(0, GameConfig.PROJECTILE_RADIUS + 6), Palette.STATIC_EDGE, 6.0)
	if definition.objective_type == LevelDefinition.OBJECTIVE_TOPPLE:
		var y := definition.topple_line_y
		var x := 0.0
		while x < GameConfig.WORLD_WIDTH:
			draw_line(Vector2(x, y), Vector2(x + 18.0, y), Palette.TOPPLE_LINE, 3.0)
			x += 30.0
