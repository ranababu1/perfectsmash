class_name TestCase
extends RefCounted
## Minimal assertion base for the dependency-free headless test runner (tests/run_tests.gd).
## Test methods are any methods named test_*; they may be coroutines (use `await`).

var tree: SceneTree
var failures := PackedStringArray()
## Set via skip(); the runner reports the test as skipped with this reason, never as passed.
var skip_reason := ""


func skip(reason: String) -> void:
	skip_reason = reason


func assert_true(condition: bool, message: String = "expected true") -> void:
	if not condition:
		failures.append(message)


func assert_false(condition: bool, message: String = "expected false") -> void:
	if condition:
		failures.append(message)


func assert_eq(actual: Variant, expected: Variant, message: String = "") -> void:
	if typeof(actual) != typeof(expected) or actual != expected:
		failures.append("%s expected <%s> got <%s>" % [message, str(expected), str(actual)])


func assert_near(actual: float, expected: float, tolerance: float, message: String = "") -> void:
	if absf(actual - expected) > tolerance:
		failures.append("%s expected %f ± %f got %f" % [message, expected, tolerance, actual])


func wait_physics_frames(count: int) -> void:
	for i in count:
		await tree.physics_frame


## Rendered frames (warm-ups count these; a slow frame can run several physics steps at once).
func wait_process_frames(count: int) -> void:
	for i in count:
		await tree.process_frame
