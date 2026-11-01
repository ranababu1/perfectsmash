extends TestCase
## Physics acceptance checks for every shipped level (plan §5 "Level acceptance"):
## - the structure stands on its own before any shot (no pre-launch collapse or target loss);
## - the stored solution wins within par through the real GameSession;
## - restarting rebuilds the exact initial layout.

const STABILITY_FRAMES := 180
const MAX_DRIFT := 3.0
const MAX_FRAMES_PER_SHOT := int(GameConfig.SIMULATION_TIMEOUT * 60.0) + 120


func _snapshot(session: GameSession) -> Array:
	var positions := []
	for node in session.get_child(0).get_children():
		if node is RigidBody2D:
			positions.append(node.global_position)
	return positions


func _new_session(def: LevelDefinition) -> GameSession:
	var session := GameSession.new()
	tree.root.add_child(session)
	session.setup(def)
	return session


func test_levels_stand_before_launch() -> void:
	for def in LevelCatalog.load_from_file().levels:
		var session := _new_session(def)
		var before := _snapshot(session)
		await wait_physics_frames(STABILITY_FRAMES)
		var after := _snapshot(session)
		assert_eq(after.size(), before.size(), "%s lost bodies before launch" % def.id)
		for i in mini(before.size(), after.size()):
			var drift: float = before[i].distance_to(after[i])
			if drift > MAX_DRIFT:
				failures.append("%s body %d drifted %.1fpx before launch" % [def.id, i, drift])
				break
		assert_eq(session.targets_remaining, def.targets.size(), "%s targets intact" % def.id)
		session.queue_free()


func test_solutions_win_within_par() -> void:
	for def in LevelCatalog.load_from_file().levels:
		var session := _new_session(def)
		await tree.physics_frame
		for velocity in def.solution:
			if not session.can_launch():
				break
			session.launch(velocity)
			var frames := 0
			while session.rules.phase == SessionRules.Phase.SIMULATING and frames < MAX_FRAMES_PER_SHOT:
				await tree.physics_frame
				frames += 1
			assert_true(frames < MAX_FRAMES_PER_SHOT, "%s simulation never resolved" % def.id)
		assert_eq(session.rules.phase, SessionRules.Phase.WON, "%s solution %s did not win:" % [def.id, def.solution])
		assert_true(session.rules.shots_used <= def.par, "%s solution exceeds par" % def.id)
		session.queue_free()


func test_restart_restores_initial_layout() -> void:
	var def: LevelDefinition = LevelCatalog.load_from_file().levels[2]
	var session := _new_session(def)
	var initial := _snapshot(session)
	session.launch(def.solution[0])
	await wait_physics_frames(120)
	session.restart()
	assert_eq(_snapshot(session), initial, "restart rebuilds identical positions")
	assert_eq(session.targets_remaining, def.targets.size())
	assert_eq(session.rules.shots_used, 0)
	assert_true(session.can_launch())
	session.queue_free()
