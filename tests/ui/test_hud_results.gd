extends TestCase
## MissionHud result panel: Next mission only on success, Missions always, signals emitted.


func _hud() -> MissionHud:
	var hud := MissionHud.new()
	tree.root.add_child(hud)
	return hud


func _engine() -> MissionEngine:
	var materials := MaterialCatalog.load_from_file()
	var weapons := WeaponCatalog.load_from_file()
	var def := MissionDefinition.load_from_file("res://data/missions/helix_01.json", materials, weapons)
	return MissionEngine.new(def, materials, weapons)


func test_success_panel_has_next_and_missions() -> void:
	var hud := _hud()
	var counts := {"next": 0, "exit": 0}
	hud.next_pressed.connect(func() -> void: counts.next += 1)
	hud.exit_pressed.connect(func() -> void: counts.exit += 1)
	hud.show_result(true, _engine())
	var next: Button = hud.find_child("NextButton", true, false)
	var missions: Button = hud.find_child("MissionsButton", true, false)
	assert_true(next != null and missions != null, "Next mission and Missions shown on success")
	next.pressed.emit()
	missions.pressed.emit()
	assert_eq(counts.next, 1)
	assert_eq(counts.exit, 1)
	hud.queue_free()


func test_failure_panel_has_missions_but_no_next() -> void:
	var hud := _hud()
	hud.show_result(false, _engine())
	assert_true(hud.find_child("NextButton", true, false) == null, "no Next on failure")
	assert_true(hud.find_child("MissionsButton", true, false) != null)
	assert_true(hud.find_child("RetryButton", true, false) != null)
	hud.queue_free()
