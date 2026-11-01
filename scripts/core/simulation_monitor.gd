class_name SimulationMonitor
extends RefCounted
## Detects when a shot's physics simulation has settled, with a hard timeout so a level can never hang.
## Settled = every dynamic body stays below the speed thresholds for hold_time continuous seconds,
## and at least min_time has elapsed since the launch.

enum Status { RUNNING, SETTLED, TIMED_OUT }

var linear_threshold := GameConfig.SETTLE_LINEAR_SPEED
var angular_threshold := GameConfig.SETTLE_ANGULAR_SPEED
var hold_time := GameConfig.SETTLE_HOLD_TIME
var min_time := GameConfig.SETTLE_MIN_TIME
var timeout := GameConfig.SIMULATION_TIMEOUT

var elapsed := 0.0
var calm_time := 0.0


func reset() -> void:
	elapsed = 0.0
	calm_time = 0.0


func step(delta: float, max_linear_speed: float, max_angular_speed: float) -> Status:
	elapsed += delta
	if max_linear_speed < linear_threshold and absf(max_angular_speed) < angular_threshold:
		calm_time += delta
	else:
		calm_time = 0.0
	if elapsed >= min_time and calm_time >= hold_time:
		return Status.SETTLED
	if elapsed >= timeout:
		return Status.TIMED_OUT
	return Status.RUNNING
