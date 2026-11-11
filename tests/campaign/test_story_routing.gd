extends TestCase
## Story cinematics through the real app: the opening on first launch, a chapter's introduction
## before its first mission, its ending once every mission of the chapter is complete, the Story
## Archive and the Upgrades screen from the main menu. Sequences are skipped to keep tests short.

const TEST_SAVE := "user://test_story_routing_progress.json"
const MainScript := preload("res://scripts/main.gd")


func _make_main(prepare: Callable = Callable()) -> Node:
	if FileAccess.file_exists(TEST_SAVE):
		DirAccess.remove_absolute(ProjectSettings.globalize_path(TEST_SAVE))
	var save := SaveService.new(TEST_SAVE)
	if prepare.is_valid():
		var progress := save.load_progress()
		prepare.call(progress)
		save.save_progress(progress)
	var main: Node = MainScript.new()
	main.save = save
	tree.root.add_child(main)
	await tree.process_frame
	return main


func _free(main: Node) -> void:
	tree.paused = false
	main.queue_free()
	await tree.process_frame
	DirAccess.remove_absolute(ProjectSettings.globalize_path(TEST_SAVE))


func _skip(main: Node) -> void:
	main._cinematic.skip()
	await tree.process_frame
	await tree.process_frame


func test_first_launch_plays_the_opening_then_the_menu() -> void:
	var main: Node = await _make_main()
	assert_true(main._cinematic != null, "opening cinematic first")
	assert_true(main._campaign == null)
	await _skip(main)
	assert_true(main._cinematic == null)
	assert_true(main._campaign != null, "then the main menu")
	assert_true(main.progress.has_seen_sequence("opening"), "opening marked seen")
	assert_true(SaveService.new(TEST_SAVE).load_progress().has_seen_sequence("opening"), "and saved")
	await _free(main)


func test_second_launch_goes_straight_to_the_menu() -> void:
	var main: Node = await _make_main(func(p: ProgressData) -> void: p.mark_sequence_seen("opening"))
	assert_true(main._cinematic == null)
	assert_true(main._campaign != null)
	await _free(main)


func test_chapter_intro_plays_once_before_the_first_mission() -> void:
	var main: Node = await _make_main(func(p: ProgressData) -> void: p.mark_sequence_seen("opening"))
	main._select_mission("helix_01")
	await tree.process_frame
	assert_true(main._cinematic != null, "chapter I introduction")
	await _skip(main)
	assert_true(main._mission != null, "then the mission")
	assert_true(main.progress.has_seen_sequence("ch01_intro"))
	main._show_campaign()
	main._select_mission("helix_01")
	await tree.process_frame
	assert_true(main._cinematic == null and main._mission != null, "not again")
	await _free(main)


func test_chapter_outro_after_the_last_mission_of_a_chapter() -> void:
	var main: Node = await _make_main(func(p: ProgressData) -> void:
		for id: String in ["opening", "ch01_intro"]:
			p.mark_sequence_seen(id))
	var ids: Array[String] = []
	for s in main.missions.chapter_slots(1):
		ids.append(s.id)
	for id in ids.slice(0, ids.size() - 1):
		main.progress.record_mission(id, {"success": true, "mission_points": 100, "research_data": 1}, 1, 1.0, [] as Array[String])
	assert_eq(main._chapter_outro_due(ids[ids.size() - 2]), "", "chapter not complete yet")
	main.progress.record_mission(ids.back(), {"success": true, "mission_points": 100, "research_data": 1}, 1, 1.0, [] as Array[String])
	assert_eq(main._chapter_outro_due(ids.back()), "ch01_outro")
	main._exit_mission(ids.back())
	await tree.process_frame
	assert_true(main._cinematic != null, "chapter I ending")
	await _skip(main)
	assert_true(main._campaign != null, "back to the mission list")
	assert_eq(main._chapter_outro_due(ids.back()), "", "plays once")
	await _free(main)


func test_menu_opens_story_archive_and_upgrades() -> void:
	var main: Node = await _make_main(func(p: ProgressData) -> void: p.mark_sequence_seen("opening"))
	(main._campaign.find_child("ArchiveButton", true, false) as Button).pressed.emit()
	await tree.process_frame
	assert_true(main._archive != null, "Story Archive")
	main._archive.play_requested.emit("opening")
	await tree.process_frame
	assert_true(main._cinematic != null, "replay from the archive")
	await _skip(main)
	assert_true(main._archive != null, "back to the archive")
	main._handle_back()
	await tree.process_frame
	assert_true(main._campaign != null)
	(main._campaign.find_child("UpgradesButton", true, false) as Button).pressed.emit()
	await tree.process_frame
	assert_true(main._upgrades != null, "Upgrades screen")
	main._handle_back()
	await tree.process_frame
	assert_true(main._campaign != null)
	await _free(main)


func test_android_back_skips_a_cinematic() -> void:
	var main: Node = await _make_main()
	assert_true(main._cinematic != null)
	main._handle_back()
	await tree.process_frame
	await tree.process_frame
	assert_true(main._campaign != null)
	await _free(main)
