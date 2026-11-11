extends TestCase
## Helix missions 01-05: each facility stands until attacked, each recorded solution in
## tools/levels/solutions/<id>.json wins, and the five play back to back through the real app
## (MissionScreen scoring, save file, linear unlocks, Next mission, restart).
## Physics assertions are outcome categories (win / within budget), never exact values.

const PHYSICS_SUITE := true
const Solver := preload("res://tools/levels/mission_solver.gd")
const MainScript := preload("res://scripts/main.gd")
const TEST_SAVE := "user://test_helix_missions_progress.json"
const MISSIONS := ["helix_01", "helix_02", "helix_03", "helix_04", "helix_05"]

var _solutions: Dictionary = preload("res://tools/levels/solution_book.gd").load_all()


func _path(id: String) -> String:
	return "res://data/missions/%s.json" % id


func test_missions_01_to_05_are_authored_valid_and_have_set_dressing() -> void:
	var catalog := MissionCatalog.load_default()
	for id: String in MISSIONS:
		assert_true(catalog.slot(id).authored, "%s authored" % id)
		assert_true(FileAccess.file_exists("res://data/environments/%s.json" % id), "%s has set dressing" % id)
		assert_true(_solutions.has(id), "%s has a recorded solution" % id)
	assert_eq(catalog.first_authored_id(), "helix_01")
	assert_eq(catalog.next_authored_id("helix_04"), "helix_05")


func test_every_facility_stands_until_attacked() -> void:
	for id: String in MISSIONS:
		var made: Dictionary = Solver.make_world(tree, _path(id))
		assert_false(made.has("error"), "%s: %s" % [id, made.get("error", "")])
		if made.has("error"):
			continue
		var moved: Array[String] = await Solver.stand_check(tree, made.world)
		assert_eq(moved, [] as Array[String], "%s: components moved or took damage untouched" % id)
		Solver.free_world(tree, made)
		await tree.process_frame


func test_each_mission_has_a_winning_line_within_its_recommended_shots() -> void:
	for id: String in MISSIONS:
		var best := 1 << 30
		for plan: Dictionary in _solutions[id]:
			var made: Dictionary = Solver.make_world(tree, _path(id))
			await tree.physics_frame
			var result: Dictionary = await Solver.play(tree, made.world, plan.steps)
			var recommended: int = made.world.definition.recommended_shots
			Solver.free_world(tree, made)
			await tree.process_frame
			assert_true(result.success, "%s '%s' wins (%s)" % [id, plan.name, result.blocked])
			if result.success:
				best = mini(best, result.shots)
				assert_true(result.shots <= recommended + 1, "%s '%s' used %d shots, recommended %d" % [id, plan.name, result.shots, recommended])
		var def := MissionDefinition.load_from_file(_path(id), MaterialCatalog.load_from_file(), WeaponCatalog.load_from_file())
		assert_true(best <= def.recommended_shots, "%s: best line %d shots within recommended %d" % [id, best, def.recommended_shots])


func test_both_weapons_are_needed_somewhere_in_01_to_05() -> void:
	var used := {}
	for id: String in MISSIONS:
		for plan: Dictionary in _solutions[id]:
			for step: Dictionary in plan.steps:
				used[step.weapon] = true
	assert_true(used.has("kinetic_accelerator") and used.has("breach_charge"))


## The full loop through Main: play 01..05 in order with Next mission, then restart one.
func test_campaign_01_to_05_through_the_app_saves_and_unlocks() -> void:
	if FileAccess.file_exists(TEST_SAVE):
		DirAccess.remove_absolute(ProjectSettings.globalize_path(TEST_SAVE))
	var main: Node = MainScript.new()
	main.cinematics_enabled = false
	main.save = SaveService.new(TEST_SAVE)
	main.boot_mission = "helix_01"
	tree.root.add_child(main)
	await tree.process_frame
	for i in MISSIONS.size():
		var id: String = MISSIONS[i]
		var screen: MissionScreen = main._mission
		assert_true(screen != null, "%s is on screen" % id)
		if screen == null:
			break
		assert_eq(screen.engine.definition.id, id)
		if i + 1 < MISSIONS.size():
			assert_false(main.missions.is_unlocked(MISSIONS[i + 1], main.progress), "%s locked before %s is won" % [MISSIONS[i + 1], id])
		var result: Dictionary = await Solver.play(tree, screen.world, _solutions[id][0].steps)
		assert_true(result.success, "%s won through the app (%s)" % [id, result.blocked])
		assert_true(main.progress.is_mission_completed(id), "%s recorded as completed" % id)
		assert_true(int(main.progress.mission_result(id).get("best_points", 0)) > 0, "%s has Mission Points" % id)
		if i + 1 < MISSIONS.size():
			assert_true(main.missions.is_unlocked(MISSIONS[i + 1], main.progress), "%s unlocked" % MISSIONS[i + 1])
			screen.next_requested.emit()
			await tree.process_frame
	# Saved to disk, and a fresh load sees the same campaign state.
	var reloaded := SaveService.new(TEST_SAVE).load_progress()
	for id: String in MISSIONS:
		assert_true(reloaded.is_mission_completed(id), "%s completed in the saved file" % id)
	assert_true(reloaded.research_data > 0, "Research Data earned and saved")
	# Restart rebuilds the same mission from its initial layout.
	var last: MissionScreen = main._mission
	last.restart_requested.emit()
	await tree.process_frame
	assert_true(main._mission != null and main._mission != last, "restart builds a fresh mission")
	assert_eq(main._mission.engine.definition.id, "helix_05")
	assert_eq(main._mission.engine.shots_fired(), 0)
	assert_true(main._mission.engine.is_active())
	tree.paused = false
	main.queue_free()
	await tree.process_frame
	DirAccess.remove_absolute(ProjectSettings.globalize_path(TEST_SAVE))
