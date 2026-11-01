extends TestCase
## GameSession behaviour with synthetic levels: misses consume shots, budgets end in a loss,
## launches are refused while simulating, and simulations always resolve.

const MAX_FRAMES := int(GameConfig.SIMULATION_TIMEOUT * 60.0) + 120


func _level(shots: int) -> LevelDefinition:
	var def := LevelDefinition.from_dict({
		"id": "S01", "name": "Synthetic", "shots": shots, "par": 1,
		"launcher": [180, 540],
		"objective": {"type": "destroy_targets"},
		"blocks": [{"x": 900, "y": 610, "w": 60, "h": 60, "material": "stone"}],
		"targets": [{"x": 900, "y": 556, "r": 24}],
	})
	assert_true(def.is_valid(), "synthetic level valid: %s" % ", ".join(def.errors))
	return def


func _wait_resolved(session: GameSession) -> int:
	var frames := 0
	while session.rules.phase == SessionRules.Phase.SIMULATING and frames < MAX_FRAMES:
		await tree.physics_frame
		frames += 1
	return frames


func test_miss_consumes_shot_then_loses() -> void:
	var session := GameSession.new()
	tree.root.add_child(session)
	session.setup(_level(2))
	var finished_args := []
	session.finished.connect(func(won: bool, stars: int, used: int) -> void: finished_args.append([won, stars, used]))
	# Fire backwards, away from the structure.
	assert_true(session.launch(Vector2(-600, -300)))
	assert_false(session.launch(Vector2(-600, -300)), "cannot launch while simulating")
	var frames: int = await _wait_resolved(session)
	assert_true(frames < MAX_FRAMES, "first shot resolved")
	assert_eq(session.rules.phase, SessionRules.Phase.READY)
	assert_eq(session.rules.shots_remaining(), 1)
	assert_true(session.launch(Vector2(-600, -300)))
	await _wait_resolved(session)
	assert_eq(session.rules.phase, SessionRules.Phase.LOST)
	assert_eq(finished_args, [[false, 0, 2]], "finished emitted once with a loss")
	assert_false(session.can_launch())
	session.queue_free()


func test_direct_hit_wins_with_three_stars() -> void:
	var def := _level(3)
	var session := GameSession.new()
	tree.root.add_child(session)
	session.setup(def)
	var finished_args := []
	session.finished.connect(func(won: bool, stars: int, used: int) -> void: finished_args.append([won, stars, used]))
	# Flat, fast shot straight at the target's height.
	var to_target := Vector2(900, 556) - def.launcher
	session.launch(Vector2(GameConfig.MAX_LAUNCH_SPEED, 0).rotated(to_target.angle() - 0.08))
	await _wait_resolved(session)
	assert_eq(session.targets_remaining, 0, "target destroyed")
	assert_eq(finished_args, [[true, 3, 1]])
	session.queue_free()


func test_launch_speed_is_clamped() -> void:
	var session := GameSession.new()
	tree.root.add_child(session)
	session.setup(_level(1))
	var speeds := []
	session.launched.connect(func(v: Vector2) -> void: speeds.append(v.length()))
	session.launch(Vector2(-99999, 0))
	assert_near(speeds[0], GameConfig.MAX_LAUNCH_SPEED, 0.5)
	session.queue_free()


func test_targets_unarmed_before_launch() -> void:
	var session := GameSession.new()
	tree.root.add_child(session)
	session.setup(_level(1))
	for node in session.get_child(0).get_children():
		if node is TargetBody:
			# A huge impulse before the first launch must not break anything.
			assert_false(DestructionRules.breaks_on_impact(node.armed, 1e6, GameConfig.TARGET_BREAK_IMPULSE))
	session.queue_free()
