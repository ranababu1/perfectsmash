extends TestCase
## End-to-end smoke test through the real app root and input pipeline:
## menu -> level, drag-to-launch works, presses on HUD buttons never launch, pause blocks aiming.

const TEST_SAVE := "user://test_ui_progress.json"
const MainScript := preload("res://scripts/main.gd")


func _click(at: Vector2, pressed: bool) -> void:
	var event := InputEventMouseButton.new()
	event.button_index = MOUSE_BUTTON_LEFT
	event.pressed = pressed
	event.position = at
	event.global_position = at
	tree.root.push_input(event)


func _move(at: Vector2) -> void:
	var event := InputEventMouseMotion.new()
	event.position = at
	event.global_position = at
	tree.root.push_input(event)


func _drag(from: Vector2, to: Vector2) -> void:
	_click(from, true)
	await tree.process_frame
	_move(to)
	await tree.process_frame
	_click(to, false)
	await tree.process_frame


func _make_main() -> Node:
	if FileAccess.file_exists(TEST_SAVE):
		DirAccess.remove_absolute(ProjectSettings.globalize_path(TEST_SAVE))
	var main: Node = MainScript.new()
	main.save = SaveService.new(TEST_SAVE)
	tree.root.add_child(main)
	return main


func test_drag_launches_and_buttons_do_not() -> void:
	var main := _make_main()
	await tree.process_frame
	main._start_level(0)
	await tree.process_frame
	var game: GameScreen = main._game
	assert_true(game != null, "game screen created")
	var launches := []
	game.session.launched.connect(func(v: Vector2) -> void: launches.append(v))

	# Press and release on the Pause button area (top-right) must not launch.
	var vp_size := tree.root.get_visible_rect().size
	var pause_point := Vector2(vp_size.x - 80, 50)
	_click(pause_point, true)
	await tree.process_frame
	_click(pause_point, false)
	await tree.process_frame
	assert_eq(launches.size(), 0, "UI press did not launch")
	assert_true(tree.paused, "pause button paused the game")

	# Aiming while paused does nothing.
	await _drag(Vector2(640, 400), Vector2(500, 450))
	assert_eq(launches.size(), 0, "no launch while paused")
	game.resume()
	await tree.process_frame

	# A short tap below the minimum drag distance does not launch.
	await _drag(Vector2(640, 400), Vector2(630, 400))
	assert_eq(launches.size(), 0, "tiny drag ignored")

	# A real drag launches toward the opposite direction of the pull.
	await _drag(Vector2(640, 400), Vector2(500, 480))
	assert_eq(launches.size(), 1, "drag launched")
	if launches.size() == 1:
		assert_true(launches[0].x > 0.0 and launches[0].y < 0.0, "launch goes right and up")
	assert_false(game.session.can_launch(), "cannot launch while simulating")
	main.queue_free()
	await tree.process_frame
	tree.paused = false


func test_win_is_saved_and_unlocks_next() -> void:
	var main := _make_main()
	await tree.process_frame
	main._start_level(0)
	await tree.process_frame
	var game: GameScreen = main._game
	var def: LevelDefinition = main.catalog.levels[0]
	await tree.physics_frame
	game.session.launch(def.solution[0])
	var frames := 0
	while not game.session.rules.is_finished() and frames < 900:
		await tree.physics_frame
		frames += 1
	assert_eq(game.session.rules.phase, SessionRules.Phase.WON)
	var reloaded := SaveService.new(TEST_SAVE).load_progress()
	assert_eq(reloaded.stars_for(def.id), 3, "win persisted")
	assert_true(reloaded.is_unlocked(main.catalog.ids(), 1), "next level unlocked")
	main.queue_free()
	await tree.process_frame
	DirAccess.remove_absolute(ProjectSettings.globalize_path(TEST_SAVE))
