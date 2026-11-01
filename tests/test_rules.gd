extends TestCase


func test_session_win_on_first_shot() -> void:
	var rules := SessionRules.new(3)
	assert_true(rules.can_launch())
	assert_true(rules.register_launch())
	assert_false(rules.can_launch(), "no launch while simulating")
	assert_false(rules.register_launch(), "second launch rejected while simulating")
	assert_eq(rules.register_settled(true), SessionRules.Phase.WON)
	assert_eq(rules.shots_used, 1)
	assert_false(rules.can_launch(), "no launch after win")


func test_session_returns_to_ready_with_shots_left() -> void:
	var rules := SessionRules.new(2)
	rules.register_launch()
	assert_eq(rules.register_settled(false), SessionRules.Phase.READY)
	assert_eq(rules.shots_remaining(), 1)


func test_session_loses_when_budget_spent() -> void:
	var rules := SessionRules.new(2)
	rules.register_launch()
	rules.register_settled(false)
	rules.register_launch()
	assert_eq(rules.register_settled(false), SessionRules.Phase.LOST)
	assert_true(rules.is_finished())
	assert_false(rules.can_launch())


func test_session_win_on_last_shot_beats_loss() -> void:
	var rules := SessionRules.new(1)
	rules.register_launch()
	assert_eq(rules.register_settled(true), SessionRules.Phase.WON)


func test_session_settled_outside_simulation_is_ignored() -> void:
	var rules := SessionRules.new(1)
	assert_eq(rules.register_settled(true), SessionRules.Phase.READY, "cannot win without launching")


func test_session_minimum_budget() -> void:
	assert_eq(SessionRules.new(0).shots_budget, 1)


func test_objective_destroy_targets() -> void:
	var t := LevelDefinition.OBJECTIVE_DESTROY_TARGETS
	assert_true(ObjectiveEvaluator.is_met(t, 0, 100.0, 0.0))
	assert_false(ObjectiveEvaluator.is_met(t, 1, INF, 0.0))


func test_objective_topple_boundary() -> void:
	var t := LevelDefinition.OBJECTIVE_TOPPLE
	assert_true(ObjectiveEvaluator.is_met(t, 5, 520.0, 500.0), "top below line")
	assert_true(ObjectiveEvaluator.is_met(t, 5, 500.0, 500.0), "top exactly on line")
	assert_false(ObjectiveEvaluator.is_met(t, 0, 499.0, 500.0), "top above line")
	assert_true(ObjectiveEvaluator.is_met(t, 0, INF, 500.0), "no blocks left")


func test_objective_is_repeatable() -> void:
	var t := LevelDefinition.OBJECTIVE_DESTROY_TARGETS
	for i in 3:
		assert_true(ObjectiveEvaluator.is_met(t, 0, 0.0, 0.0), "same input, same answer")


func test_monitor_settles_after_hold_time() -> void:
	var monitor := SimulationMonitor.new()
	monitor.min_time = 0.5
	monitor.hold_time = 0.3
	var dt := 1.0 / 60.0
	var status := SimulationMonitor.Status.RUNNING
	var frames := 0
	while status == SimulationMonitor.Status.RUNNING and frames < 1000:
		status = monitor.step(dt, 0.0, 0.0)
		frames += 1
	assert_eq(status, SimulationMonitor.Status.SETTLED)
	assert_true(monitor.elapsed >= 0.5 - 0.001, "respects minimum time")


func test_monitor_motion_resets_calm_timer() -> void:
	var monitor := SimulationMonitor.new()
	monitor.min_time = 0.0
	monitor.hold_time = 0.5
	monitor.step(0.4, 0.0, 0.0)
	monitor.step(0.05, 500.0, 0.0)
	assert_near(monitor.calm_time, 0.0, 0.0001, "fast body resets calm time")
	assert_eq(monitor.step(0.4, 0.0, 0.0), SimulationMonitor.Status.RUNNING)
	assert_eq(monitor.step(0.2, 0.0, 0.0), SimulationMonitor.Status.SETTLED)


func test_monitor_spinning_body_is_not_settled() -> void:
	var monitor := SimulationMonitor.new()
	monitor.min_time = 0.0
	monitor.hold_time = 0.1
	assert_eq(monitor.step(0.2, 0.0, -5.0), SimulationMonitor.Status.RUNNING)


func test_monitor_times_out() -> void:
	var monitor := SimulationMonitor.new()
	monitor.timeout = 2.0
	var status := SimulationMonitor.Status.RUNNING
	var frames := 0
	while status == SimulationMonitor.Status.RUNNING and frames < 10000:
		status = monitor.step(1.0 / 60.0, 100.0, 0.0)
		frames += 1
	assert_eq(status, SimulationMonitor.Status.TIMED_OUT)
	assert_near(monitor.elapsed, 2.0, 0.05)


func test_monitor_reset() -> void:
	var monitor := SimulationMonitor.new()
	monitor.step(1.0, 0.0, 0.0)
	monitor.reset()
	assert_near(monitor.elapsed, 0.0, 0.0)
	assert_near(monitor.calm_time, 0.0, 0.0)


func test_destruction_requires_arming_and_threshold() -> void:
	assert_false(DestructionRules.breaks_on_impact(false, 9999.0, 100.0), "unarmed never breaks")
	assert_false(DestructionRules.breaks_on_impact(true, 100.0, 100.0), "exactly threshold holds")
	assert_true(DestructionRules.breaks_on_impact(true, 100.5, 100.0))


func test_projectile_hit_and_jolt_rules() -> void:
	var hit := GameConfig.TARGET_PROJECTILE_HIT_SPEED
	assert_false(DestructionRules.breaks_on_projectile_hit(false, hit * 10.0), "unarmed")
	assert_false(DestructionRules.breaks_on_projectile_hit(true, hit), "at threshold holds")
	assert_true(DestructionRules.breaks_on_projectile_hit(true, hit + 1.0))
	var jolt := GameConfig.TARGET_BREAK_VELOCITY_CHANGE
	assert_false(DestructionRules.breaks_on_jolt(false, jolt * 10.0), "unarmed")
	assert_false(DestructionRules.breaks_on_jolt(true, jolt), "at threshold holds")
	assert_true(DestructionRules.breaks_on_jolt(true, jolt + 1.0))
	# One step of gravity on a resting or falling body must never count as a jolt.
	assert_false(DestructionRules.breaks_on_jolt(true, 980.0 / 60.0))


func test_out_of_bounds() -> void:
	assert_false(DestructionRules.is_out_of_bounds(Vector2(640, 300)))
	assert_true(DestructionRules.is_out_of_bounds(Vector2(640, 5000)))
	assert_true(DestructionRules.is_out_of_bounds(Vector2(-1000, 300)))


func test_stars() -> void:
	assert_eq(ScoreRules.stars_for(1, 1), 3)
	assert_eq(ScoreRules.stars_for(2, 2), 3)
	assert_eq(ScoreRules.stars_for(2, 1), 2)
	assert_eq(ScoreRules.stars_for(3, 1), 1)
	assert_eq(ScoreRules.stars_for(5, 1), 1)
