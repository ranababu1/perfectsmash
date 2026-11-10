extends TestCase
## CampaignScreen: menu, chapter select and mission select against a fake 100-slot catalog.

var _got := ""


func _catalog(authored_ids: Array) -> MissionCatalog:
	var exists := func(path: String) -> bool: return authored_ids.has(path.get_file().get_basename())
	return MissionCatalog.from_chapters(ChapterCatalog.load_from_file(), exists)


func _screen(authored_ids: Array, progress: ProgressData) -> CampaignScreen:
	var catalog := _catalog(authored_ids)
	var screen := CampaignScreen.new(catalog, catalog.chapters, progress)
	tree.root.add_child(screen)
	return screen


func _remember(id: String) -> void:
	_got = id


func test_continue_targets_first_unlocked_uncompleted() -> void:
	var progress := ProgressData.new()
	var screen := _screen(["helix_01", "helix_02", "vita_01"], progress)
	assert_eq(screen.continue_target(), "helix_01")
	progress.mission_results["helix_01"] = {"completed": true, "best_points": 900}
	assert_eq(screen.continue_target(), "helix_02")
	progress.mission_results["helix_02"] = {"completed": true, "best_points": 800}
	progress.mission_results["vita_01"] = {"completed": true, "best_points": 700}
	assert_eq(screen.continue_target(), "", "everything completed: nothing to continue")
	screen.queue_free()


func test_continue_button_emits_and_disables() -> void:
	var screen := _screen(["helix_01"], ProgressData.new())
	_got = ""
	screen.mission_selected.connect(_remember)
	var button: Button = screen.find_child("ContinueButton", true, false)
	assert_true(button != null and not button.disabled)
	button.pressed.emit()
	assert_eq(_got, "helix_01")
	screen.queue_free()
	var empty := _screen([], ProgressData.new())
	assert_true((empty.find_child("ContinueButton", true, false) as Button).disabled, "no authored missions: Continue disabled")
	empty.queue_free()


func test_slot_states() -> void:
	var progress := ProgressData.new()
	var screen := _screen(["helix_01", "helix_02", "vita_01"], progress)
	assert_eq(screen.slot_state("helix_01"), CampaignScreen.SlotState.AVAILABLE)
	assert_eq(screen.slot_state("helix_02"), CampaignScreen.SlotState.LOCKED)
	assert_eq(screen.slot_state("helix_03"), CampaignScreen.SlotState.UNAVAILABLE)
	progress.mission_results["helix_01"] = {"completed": true, "best_points": 1234}
	assert_eq(screen.slot_state("helix_01"), CampaignScreen.SlotState.COMPLETED)
	assert_eq(screen.slot_state("helix_02"), CampaignScreen.SlotState.AVAILABLE)
	screen.queue_free()


func test_chapter_select_lists_five_with_lock_states() -> void:
	var progress := ProgressData.new()
	var screen := _screen(["helix_01", "helix_02", "vita_01"], progress)
	screen.show_chapters()
	for n in range(1, 6):
		assert_true(screen.find_child("Chapter_%d" % n, true, false) != null, "chapter %d tile" % n)
	assert_false((screen.find_child("Chapter_1", true, false) as Button).disabled)
	assert_true((screen.find_child("Chapter_2", true, false) as Button).disabled, "vita locked until helix_02 is done")
	assert_true((screen.find_child("Chapter_3", true, false) as Button).disabled, "no authored missions")
	assert_true((screen.find_child("Chapter_1", true, false) as Button).text.contains("0 / 20 complete"))
	progress.mission_results["helix_01"] = {"completed": true, "best_points": 1}
	progress.mission_results["helix_02"] = {"completed": true, "best_points": 1}
	screen.show_chapters()
	assert_false((screen.find_child("Chapter_2", true, false) as Button).disabled)
	assert_true((screen.find_child("Chapter_1", true, false) as Button).text.contains("2 / 20 complete"))
	screen.queue_free()


func test_mission_select_has_twenty_slots_and_states() -> void:
	var progress := ProgressData.new()
	progress.mission_results["helix_01"] = {"completed": true, "best_points": 1234}
	var screen := _screen(["helix_01", "helix_02", "helix_03"], progress)
	screen.show_missions(1)
	var list: Control = screen.find_child("List", true, false)
	assert_eq(list.get_child_count(), 20)
	var done: Button = screen.find_child("Mission_helix_01", true, false)
	assert_true(done.text.contains("1234"), "completed shows best Mission Points")
	assert_false(done.disabled, "completed missions can be replayed")
	assert_false((screen.find_child("Mission_helix_02", true, false) as Button).disabled)
	var locked: Button = screen.find_child("Mission_helix_03", true, false)
	assert_true(locked.disabled and locked.text.contains("Locked"))
	var missing: Button = screen.find_child("Mission_helix_04", true, false)
	assert_true(missing.disabled and missing.text.contains("Not yet available"))
	for child in list.get_children():
		assert_true((child as Control).custom_minimum_size.y >= 88.0, "touch target height")
	_got = ""
	screen.mission_selected.connect(_remember)
	(screen.find_child("Mission_helix_02", true, false) as Button).pressed.emit()
	assert_eq(_got, "helix_02")
	assert_true(screen.go_back(), "back from missions")
	assert_eq(screen.view, CampaignScreen.View.CHAPTERS)
	assert_true(screen.go_back(), "back from chapters")
	assert_eq(screen.view, CampaignScreen.View.MENU)
	assert_false(screen.go_back(), "menu has nowhere to go back to")
	screen.queue_free()


func test_settings_requested_signal() -> void:
	var screen := _screen(["helix_01"], ProgressData.new())
	var fired := [false]
	screen.settings_requested.connect(func() -> void: fired[0] = true)
	(screen.find_child("SettingsButton", true, false) as Button).pressed.emit()
	assert_true(fired[0])
	screen.queue_free()
