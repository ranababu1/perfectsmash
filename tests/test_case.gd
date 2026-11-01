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


## Creates a GameSession in its own SubViewport so it gets an isolated physics world.
func make_session(def: LevelDefinition) -> GameSession:
	await PhysicsWarmup.run(tree)
	var viewport := SubViewport.new()
	viewport.render_target_update_mode = SubViewport.UPDATE_DISABLED
	tree.root.add_child(viewport)
	var session := GameSession.new()
	viewport.add_child(session)
	session.setup(def)
	return session


## Removes the session's world immediately; queue_free alone would leave its bodies
## in the physics space for one more step.
func free_session(session: GameSession) -> void:
	var viewport := session.get_parent()
	tree.root.remove_child(viewport)
	viewport.queue_free()


func wait_physics_frames(count: int) -> void:
	for i in count:
		await tree.physics_frame
