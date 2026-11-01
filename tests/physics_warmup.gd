class_name PhysicsWarmup
extends RefCounted
## Observed with Godot 4.7.2: the first collision of a given kind in a process can resolve
## differently from every later, identical shot (cause not yet identified; see currentstate.md).
## A synthetic warm-up was not enough, so verification tools replay the first shipped level's
## stored solution once, so stored solutions are checked against steady-state behaviour.

const SETTLE_FRAMES := 90
const MAX_FRAMES := 900

static var _done := false


static func run(tree: SceneTree) -> void:
	if _done:
		return
	_done = true
	var catalog := LevelCatalog.load_from_file()
	if catalog.levels.is_empty():
		push_warning("PhysicsWarmup: no levels to warm up with")
		return
	var def: LevelDefinition = catalog.levels[0]
	var viewport := SubViewport.new()
	viewport.render_target_update_mode = SubViewport.UPDATE_DISABLED
	tree.root.add_child(viewport)
	var session := GameSession.new()
	viewport.add_child(session)
	session.setup(def)
	for i in SETTLE_FRAMES:
		await tree.physics_frame
	# Any shot works if the level has no stored solution yet; it still exercises collisions.
	session.launch(def.solution[0] if not def.solution.is_empty() else Vector2(1100, -200))
	var frames := 0
	while session.rules.phase == SessionRules.Phase.SIMULATING and frames < MAX_FRAMES:
		await tree.physics_frame
		frames += 1
	tree.root.remove_child(viewport)
	viewport.queue_free()
