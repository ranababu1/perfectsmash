extends TestCase
## main.gd routing between MissionScreen, CampaignScreen and SettingsScreen, and the
## reload-ready sound hookup in MissionScreen.

const PHYSICS_SUITE := true
const TEST_SAVE := "user://test_campaign_routing_progress.json"
const MainScript := preload("res://scripts/main.gd")


func _make_main() -> Node:
	if FileAccess.file_exists(TEST_SAVE):
		DirAccess.remove_absolute(ProjectSettings.globalize_path(TEST_SAVE))
	var main: Node = MainScript.new()
	main.cinematics_enabled = false
	main.save = SaveService.new(TEST_SAVE)
	main.boot_mission = "helix_01"
	tree.root.add_child(main)
	await tree.process_frame
	return main


func _free(main: Node) -> void:
	tree.paused = false
	main.queue_free()
	await tree.process_frame
	await tree.process_frame


func test_missions_action_opens_the_chapter_list_and_selection_starts_a_mission() -> void:
	var main: Node = await _make_main()
	assert_true(main._mission != null, "boot_mission starts helix_01")
	main._mission.exit_requested.emit()
	await tree.process_frame
	assert_true(main._mission == null and main._campaign != null, "Missions opens the campaign")
	assert_eq(main._campaign.view, CampaignScreen.View.MISSIONS)
	assert_eq(main._campaign.current_chapter, 1, "opens the mission's own chapter")
	main._campaign.mission_selected.emit("helix_01")
	await tree.process_frame
	assert_true(main._campaign == null and main._mission != null, "selecting a mission starts it")
	assert_eq(main._mission.mission_path, "res://data/missions/helix_01.json")
	await _free(main)


func test_next_without_a_next_mission_returns_to_the_campaign() -> void:
	var main: Node = await _make_main()
	var last_id: String = main.missions.authored()[-1].id
	main._show_mission(last_id)
	await tree.process_frame
	main._mission.next_requested.emit()
	await tree.process_frame
	assert_true(main._campaign != null, "no next mission: back to the mission list")
	await _free(main)


func test_settings_round_trip_updates_progress_and_audio() -> void:
	var main: Node = await _make_main()
	main._show_campaign()
	await tree.process_frame
	main._campaign.settings_requested.emit()
	await tree.process_frame
	assert_true(main._settings != null, "settings screen shown")
	main._settings.music_toggled.emit(false)
	assert_false(main.progress.music_enabled)
	assert_false(main.music.enabled, "music director follows the setting")
	main._settings.vibration_toggled.emit(false)
	assert_false(main.progress.vibration_enabled)
	main._settings.back_pressed.emit()
	await tree.process_frame
	assert_true(main._settings == null and main._campaign != null, "back returns to the campaign")
	main._handle_back()
	await tree.process_frame
	assert_true(main._campaign != null, "back on the menu root keeps the campaign (desktop)")
	await _free(main)


func test_reload_completed_plays_reload_ready_for_the_selected_weapon() -> void:
	var main: Node = await _make_main()
	var screen: MissionScreen = main._mission
	var weapon: WeaponState = screen.engine.weapons[screen.engine.selected_weapon_id]
	var calls := {"n": 0}
	weapon.reload_completed.connect(func(_id: String) -> void: calls.n += 1)
	weapon.fire()
	for i in 200:
		await tree.physics_frame
		if calls.n > 0:
			break
	assert_eq(calls.n, 1, "the reload completed during the mission")
	assert_true(weapon.reload_completed.get_connections().any(
		func(c: Dictionary) -> bool: return c.callable.get_method() == "_on_reload_completed"),
		"MissionScreen listens for reload_completed")
	await _free(main)
