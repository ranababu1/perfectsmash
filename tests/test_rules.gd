extends TestCase
## Engine rules kept from the retired slingshot game: the settle monitor (used by MissionWorld)
## and the legacy star score (still read when old saves are migrated).


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


func test_stars() -> void:
	assert_eq(ScoreRules.stars_for(1, 1), 3)
	assert_eq(ScoreRules.stars_for(2, 2), 3)
	assert_eq(ScoreRules.stars_for(2, 1), 2)
	assert_eq(ScoreRules.stars_for(3, 1), 1)
	assert_eq(ScoreRules.stars_for(5, 1), 1)
