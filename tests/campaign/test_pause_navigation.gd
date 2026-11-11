extends TestCase
## Pause menu and in-mission navigation (owner report, rc2): Resume, Restart Mission and Main Menu
## with confirmations, Android back on every panel, and leaving a mission never records it or
## touches progress earned earlier. Runs the real app root.

const PHYSICS_SUITE := true
const TEST_SAVE := "user://test_pause_navigation_progress.json"
const MainScript := preload("res://scripts/main.gd")
const MISSION := "helix_08"


func _remove_save() -> void:
	if FileAccess.file_exists(TEST_SAVE):
		DirAccess.remove_absolute(ProjectSettings.globalize_path(TEST_SAVE))


## Boots straight into MISSION on a save that already holds a completed helix_01 and Research Data.
func _boot() -> Node:
	_remove_save()
	var earlier := ProgressData.new()
	var optional: Array[String] = []
	earlier.record_mission("helix_01", {"success": true, "mission_points": 900, "research_data": 40}, 2, 12.0, optional)
	SaveService.new(TEST_SAVE).save_progress(earlier)
	var main: Node = MainScript.new()
	main.cinematics_enabled = false
	main.save = SaveService.new(TEST_SAVE)
	main.boot_mission = MISSION
	tree.root.add_child(main)
	await tree.process_frame
	return main


func _free(main: Node) -> void:
	tree.paused = false
	main.queue_free()
	await tree.process_frame
	_remove_save()


func _press(screen: MissionScreen, button_name: String) -> void:
	var button := screen.hud.find_child(button_name, true, false) as Button
	assert_true(button != null and button.is_visible_in_tree(), "%s is on screen" % button_name)
	if button != null:
		button.pressed.emit()
	await tree.process_frame


func _saved() -> Dictionary:
	return SaveService.new(TEST_SAVE).load_progress().to_dict()


func test_pause_menu_offers_resume_restart_and_main_menu() -> void:
	var main: Node = await _boot()
	var screen: MissionScreen = main._mission
	screen.pause()
	await tree.process_frame
	assert_true(tree.paused, "the game is paused")
	assert_eq(screen.hud.overlay_kind, MissionHud.OVERLAY_PAUSE)
	var names := []
	for button_name in ["PauseResumeButton", "PauseRestartButton", "PauseMenuButton"]:
		var button := screen.hud.find_child(button_name, true, false) as Button
		assert_true(button != null, "%s exists" % button_name)
		if button != null:
			names.append(button.text)
			assert_true(button.custom_minimum_size.y >= UiKit.BUTTON_HEIGHT, "%s is a comfortable touch target" % button_name)
	assert_eq(names, ["Resume", "Restart Mission", "Main Menu"])
	await _press(screen, "PauseResumeButton")
	assert_false(tree.paused, "Resume returns to gameplay")
	assert_false(screen.hud.has_overlay())
	screen.begin_aim(screen.view.plane_to_screen(Vector2(830.0, 462.0)))
	assert_true(screen._aiming, "aiming works again after Resume")
	screen._cancel_aim()
	await _free(main)


func test_main_menu_needs_confirmation_and_cancel_returns_to_pause() -> void:
	var main: Node = await _boot()
	var screen: MissionScreen = main._mission
	screen.pause()
	await _press(screen, "PauseMenuButton")
	assert_eq(screen.hud.overlay_kind, MissionHud.OVERLAY_CONFIRM_MENU, "Main Menu asks first")
	var detail := screen.hud.find_child("ConfirmDetail", true, false) as Label
	assert_true(detail != null and detail.text.contains("not be recorded as completed"), "the dialog says the mission is not recorded")
	assert_true(main._mission == screen, "nothing happens before confirming")
	await _press(screen, "CancelButton")
	assert_eq(screen.hud.overlay_kind, MissionHud.OVERLAY_PAUSE, "Cancel returns to the pause menu")
	assert_true(tree.paused, "still paused")
	await _free(main)


func test_confirmed_main_menu_leaves_without_recording_anything() -> void:
	var main: Node = await _boot()
	var screen: MissionScreen = main._mission
	var before := _saved()
	var research: int = main.progress.research_data
	screen.world.fire(Vector2(1, -0.1), 1.0)
	for i in 30:
		await tree.physics_frame
	screen.pause()
	await _press(screen, "PauseMenuButton")
	var requests := []
	screen.menu_requested.connect(func() -> void: requests.append("menu"))
	var confirm := screen.hud.find_child("ConfirmButton", true, false) as Button
	confirm.pressed.emit()
	confirm.pressed.emit()
	await tree.process_frame
	assert_eq(requests.size(), 1, "a double tap starts one transition")
	assert_false(tree.paused, "the tree is unpaused before the menu shows")
	assert_true(main._mission == null and main._campaign != null, "back on the campaign screen")
	assert_eq(main._campaign.view, CampaignScreen.View.MENU, "the main menu, not the mission list")
	assert_false(main.progress.is_mission_completed(MISSION), "the abandoned mission is not completed")
	assert_false(main.progress.mission_results.has(MISSION), "no attempt is recorded")
	assert_eq(main.progress.research_data, research, "no rewards")
	assert_true(main.progress.is_mission_completed("helix_01"), "earlier progress is intact")
	assert_eq(_saved(), before, "the save file is unchanged")
	await _free(main)


func test_restart_confirms_and_restarts_the_same_mission() -> void:
	var main: Node = await _boot()
	var screen: MissionScreen = main._mission
	var before := _saved()
	screen.world.fire(Vector2(1, -0.1), 1.0)
	await tree.physics_frame
	assert_eq(screen.engine.shots_fired(), 1)
	screen.pause()
	await _press(screen, "PauseRestartButton")
	assert_eq(screen.hud.overlay_kind, MissionHud.OVERLAY_CONFIRM_RESTART, "Restart asks first")
	await _press(screen, "CancelButton")
	assert_eq(screen.hud.overlay_kind, MissionHud.OVERLAY_PAUSE)
	await _press(screen, "PauseRestartButton")
	await _press(screen, "ConfirmButton")
	var restarted: MissionScreen = main._mission
	assert_true(restarted != null and restarted != screen, "a fresh mission screen")
	assert_eq(restarted.engine.definition.id, MISSION, "the same mission")
	assert_eq(restarted.engine.shots_fired(), 0, "a fresh attempt")
	assert_false(tree.paused)
	assert_false(main.progress.mission_results.has(MISSION), "the abandoned attempt is not recorded")
	assert_eq(_saved(), before, "the save file is unchanged")
	await _free(main)


func test_android_back_on_every_mission_panel() -> void:
	var main: Node = await _boot()
	var screen: MissionScreen = main._mission
	main.notification(Node.NOTIFICATION_WM_GO_BACK_REQUEST)
	await tree.process_frame
	assert_true(tree.paused and screen.hud.overlay_kind == MissionHud.OVERLAY_PAUSE, "gameplay → pause")
	main.notification(Node.NOTIFICATION_WM_GO_BACK_REQUEST)
	await tree.process_frame
	assert_false(tree.paused, "pause → resume")
	assert_false(screen.hud.has_overlay())
	screen.pause()
	screen.hud.confirm_main_menu()
	main.notification(Node.NOTIFICATION_WM_GO_BACK_REQUEST)
	await tree.process_frame
	assert_eq(screen.hud.overlay_kind, MissionHud.OVERLAY_PAUSE, "confirmation → pause menu (cancel)")
	assert_true(main._mission == screen, "back never confirms a dialog")
	screen.resume()
	# Results panel: back acts like the Missions button.
	for id: String in screen.engine.components:
		if screen.engine.components[id].is_critical_asset:
			screen.engine.destroy_component(id, "test")
	screen.engine.finish_mission()
	for i in 120:
		if screen.hud.overlay_kind == MissionHud.OVERLAY_RESULT:
			break
		await tree.process_frame
	assert_eq(screen.hud.overlay_kind, MissionHud.OVERLAY_RESULT, "results are showing")
	var exits := []
	screen.exit_requested.connect(func() -> void: exits.append(true))
	main.notification(Node.NOTIFICATION_WM_GO_BACK_REQUEST)
	screen.handle_back()
	await tree.process_frame
	assert_eq(exits.size(), 1, "a second back on the leaving screen starts no second transition")
	assert_true(main._mission == null and main._campaign != null, "results → mission list, no dead end")
	assert_eq(main._campaign.view, CampaignScreen.View.MISSIONS, "the chapter's mission list")
	await _free(main)


func test_leaving_clears_the_critical_music_layer() -> void:
	var main: Node = await _boot()
	var screen: MissionScreen = main._mission
	if screen.mission_audio == null or str(screen.mission_audio.plan.get("critical_layer", "")).is_empty():
		skip("mission has no critical music layer")
		await _free(main)
		return
	main.music.set_layer(screen.mission_audio.plan.critical_layer, 0.01)
	assert_false(main.music.current_layer.is_empty(), "the critical layer is playing")
	screen.pause()
	screen.hud.confirm_main_menu()
	await _press(screen, "ConfirmButton")
	assert_eq(main.music.current_layer, "", "the layer stops when the mission is left")
	assert_eq(main.music.current_cue, MainScript.MENU_CUE, "menu music plays")
	await _free(main)
