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
	tree.root.push_input(event, true)


func _move(at: Vector2) -> void:
	var event := InputEventMouseMotion.new()
	event.position = at
	event.global_position = at
	tree.root.push_input(event, true)


func _drag(from: Vector2, to: Vector2) -> void:
	_click(from, true)
	await tree.process_frame
	_move(to)
	await tree.process_frame
	_click(to, false)
	await tree.process_frame


func _make_main() -> Node:
	await PhysicsWarmup.run(tree)
	if FileAccess.file_exists(TEST_SAVE):
		DirAccess.remove_absolute(ProjectSettings.globalize_path(TEST_SAVE))
	var main: Node = MainScript.new()
	main.save = SaveService.new(TEST_SAVE)
	tree.root.add_child(main)
	return main


func test_drag_launches_and_pause_blocks_aim() -> void:
	var main: Node = await _make_main()
	await tree.process_frame
	main._start_level(0)
	await tree.process_frame
	main._close_briefing()
	var game: GameScreen = main._game
	assert_true(game != null, "game screen created")
	var launches := []
	game.session.launched.connect(func(v: Vector2) -> void: launches.append(v))

	# Aiming while paused does nothing.
	game.pause()
	assert_true(tree.paused, "pause() paused the tree")
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
	var main: Node = await _make_main()
	await tree.process_frame
	main._start_level(0)
	await tree.process_frame
	main._close_briefing()
	var game: GameScreen = main._game
	var def: LevelDefinition = main.catalog.levels[0]
	await wait_physics_frames(150)
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


## Godot's headless display server does not route mouse events to GUI controls, so this
## check only runs in a windowed test run (see tests/run_tests.gd header).
func test_hud_button_press_does_not_launch() -> void:
	if DisplayServer.get_name() == "headless":
		skip("GUI input routing needs a window; run tests without --headless")
		return
	var main: Node = await _make_main()
	await tree.process_frame
	main._start_level(0)
	await tree.process_frame
	main._close_briefing()
	var game: GameScreen = main._game
	var launches := []
	game.session.launched.connect(func(v: Vector2) -> void: launches.append(v))
	tree.root.notification(Window.NOTIFICATION_VP_MOUSE_ENTER)
	var pause_point := Vector2(tree.root.get_visible_rect().size.x - 80, 50)
	_move(pause_point)
	await tree.process_frame
	_click(pause_point, true)
	await tree.process_frame
	_move(pause_point + Vector2(-150, 200))
	await tree.process_frame
	_click(pause_point + Vector2(-150, 200), false)
	await tree.process_frame
	assert_eq(launches.size(), 0, "a drag that starts on a HUD button never launches")
	main.queue_free()
	await tree.process_frame
	tree.paused = false


func test_settings_panel_toggles_persist_and_back_closes() -> void:
	var main: Node = await _make_main()
	await tree.process_frame
	main._open_settings()
	await tree.process_frame
	var panel: SettingsPanel = main._settings
	assert_true(panel != null, "settings opened")
	var guide: Button = panel.find_child("Toggle_aim_guide", true, false)
	assert_true(guide != null and guide.button_pressed, "aim guide shown as on")
	guide.button_pressed = false
	var sound: Button = panel.find_child("Toggle_sound", true, false)
	sound.button_pressed = false
	var reloaded := SaveService.new(TEST_SAVE).load_progress()
	assert_false(reloaded.aim_guide_enabled, "aim guide off persisted")
	assert_false(reloaded.sound_enabled, "sound off persisted")
	assert_false(main.audio.enabled, "audio muted immediately")
	main._handle_back()
	await tree.process_frame
	assert_true(main._settings == null, "back closes settings")
	assert_true(main._menu != null, "still on the menu")

	main._start_level(0)
	await tree.process_frame
	main._close_briefing()
	assert_false(main._game.aim.show_guide, "level uses the saved aim guide setting")
	main.queue_free()
	await tree.process_frame
	DirAccess.remove_absolute(ProjectSettings.globalize_path(TEST_SAVE))


func test_reset_progress_clears_results_keeps_settings() -> void:
	var main: Node = await _make_main()
	await tree.process_frame
	main.progress.record_win(main.catalog.ids()[0], 3, 1)
	main.progress.vibration_enabled = false
	main._open_settings()
	await tree.process_frame
	main._settings.reset_confirmed.emit()
	await tree.process_frame
	var reloaded := SaveService.new(TEST_SAVE).load_progress()
	assert_eq(reloaded.total_stars(), 0, "results cleared")
	assert_false(reloaded.vibration_enabled, "settings kept")
	assert_true(main._settings == null, "menu rebuilt without the panel")
	main.queue_free()
	await tree.process_frame
	DirAccess.remove_absolute(ProjectSettings.globalize_path(TEST_SAVE))


## Lifecycle (plan M4): backgrounding pauses play, back toggles the pause menu, and restarts/losses
## are counted in the local play-test stats.
func test_background_back_and_stats() -> void:
	var main: Node = await _make_main()
	await tree.process_frame
	main._start_level(0)
	await tree.process_frame
	main._close_briefing()
	var game: GameScreen = main._game
	var id: String = main.catalog.ids()[0]
	assert_eq(main.progress.stat(id, "attempts"), 1, "start counts an attempt")

	main.notification(Node.NOTIFICATION_APPLICATION_FOCUS_OUT)
	assert_true(tree.paused, "losing focus pauses")
	assert_true(game.hud.has_overlay(), "pause menu shown")
	main._handle_back()
	assert_false(tree.paused, "back resumes from pause")
	main._handle_back()
	assert_true(tree.paused, "back opens pause during play")
	game.resume()
	main.notification(Node.NOTIFICATION_APPLICATION_PAUSED)
	assert_true(tree.paused, "app pause (Android background) pauses")
	game.restart()
	assert_false(tree.paused, "restart unpauses")
	assert_eq(main.progress.stat(id, "attempts"), 2, "restart counts an attempt")

	# Use every shot on a harmless miss straight down-left to lose.
	var budget: int = main.catalog.levels[0].shots
	for i in budget:
		while not game.session.can_launch():
			await tree.physics_frame
		game.session.launch(Vector2(-300, 50))
	var frames := 0
	while not game.session.rules.is_finished() and frames < 1500:
		await tree.physics_frame
		frames += 1
	assert_eq(game.session.rules.phase, SessionRules.Phase.LOST, "misses lose")
	var reloaded := SaveService.new(TEST_SAVE).load_progress()
	assert_eq(reloaded.stat(id, "losses"), 1, "loss counted and saved")
	assert_eq(reloaded.stat(id, "attempts"), 2)
	main.queue_free()
	await tree.process_frame
	tree.paused = false
	DirAccess.remove_absolute(ProjectSettings.globalize_path(TEST_SAVE))



## Story loop: briefing before the mission (back returns to the menu), Begin starts play, a win shows
## the debrief, and Next mission opens the next briefing.
func test_briefing_debrief_and_next_mission() -> void:
	var main: Node = await _make_main()
	await tree.process_frame
	assert_true(main.story != null, "story loaded and valid")
	main._start_level(0)
	await tree.process_frame
	assert_true(main._briefing != null, "briefing shown before mission 1")
	var lines: Array = main.story.briefing(0, main.catalog.ids()[0])
	assert_eq(lines[0].speaker, "log", "mission 1 opens with the chapter card")
	main._handle_back()
	await tree.process_frame
	assert_true(main._briefing == null and main._menu != null, "back from the briefing returns to the menu")

	main._start_level(0)
	await tree.process_frame
	main._briefing.begin_pressed.emit()
	await tree.process_frame
	assert_true(main._briefing == null, "begin closes the briefing")
	var game: GameScreen = main._game
	var def: LevelDefinition = main.catalog.levels[0]
	await wait_physics_frames(150)
	game.session.launch(def.solution[0])
	var frames := 0
	while not game.hud.has_overlay() and frames < 1200:
		await tree.physics_frame
		frames += 1
	await tree.create_timer(0.1).timeout
	assert_true(game.hud.has_overlay(), "result shown")
	var debrief: DialogueBox = game.hud._overlay.find_child("Debrief", true, false)
	assert_true(debrief != null, "debrief dialogue in the result panel")
	game.hud.next_pressed.emit()
	await tree.process_frame
	assert_eq(main._level_index, 1, "next mission")
	assert_true(main._briefing != null, "next mission opens with its briefing")
	main.queue_free()
	await tree.process_frame
	tree.paused = false
	DirAccess.remove_absolute(ProjectSettings.globalize_path(TEST_SAVE))


func test_dialogue_box_types_advances_and_skips() -> void:
	var box := DialogueBox.new()
	tree.root.add_child(box)
	var lines: Array[Dictionary] = [
		{"speaker": "kestrel", "name": "KESTREL", "color": Color.ORANGE, "pitch": 1.0, "text": "First line."},
		{"speaker": "bolt", "name": "BOLT", "color": Color.AQUA, "pitch": 0.9, "text": "Second line, a bit longer."},
	]
	var shown := []
	box.all_shown.connect(func() -> void: shown.append(true))
	box.play(lines)
	assert_false(box.is_done(), "typing")
	box.advance()
	box.advance()
	assert_false(box.is_done(), "second line started")
	box.finish_all()
	assert_true(box.is_done(), "skip shows everything")
	assert_eq(shown.size(), 1, "all_shown emitted once")
	box.queue_free()
