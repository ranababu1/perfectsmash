extends TestCase
## The optional-objective decision prompt through the real app: MissionEngine.decision_requested
## -> MissionScreen -> MissionHud buttons -> results, scoring and the save file.

const PHYSICS_SUITE := true
const TEST_SAVE := "user://test_decision_flow_progress.json"
const MainScript := preload("res://scripts/main.gd")
const Status := MissionObjectives.Status


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
	DirAccess.remove_absolute(ProjectSettings.globalize_path(TEST_SAVE))


## Destroys the core and waits until the scene settles and the prompt opens.
func _reach_prompt(screen: MissionScreen) -> void:
	screen.engine.apply_damage("aura_core", 9999.0, DamageRules.TYPE_IMPACT, 0.9)
	for i in 600:
		if screen.engine.awaiting_decision or not screen.engine.is_active():
			return
		await tree.physics_frame


func _button(screen: MissionScreen, node_name: String) -> Button:
	return screen.hud.find_child(node_name, true, false) as Button


func test_prompt_shows_with_exact_copy_and_holds_the_mission() -> void:
	var main: Node = await _make_main()
	var screen: MissionScreen = main._mission
	await _reach_prompt(screen)
	assert_true(screen.engine.awaiting_decision and screen.engine.is_active(), "primary done, optional pending: prompt, mission active")
	assert_true(screen.hud.has_overlay())
	var texts: Array[String] = []
	for label: Label in screen.hud.find_children("*", "Label", true, false):
		texts.append(label.text)
	assert_true(texts.has("Primary objective complete"), str(texts))
	assert_true(texts.has("Optional objectives remain. What next?"))
	assert_eq(_button(screen, "DecisionContinueButton").text, "Continue")
	assert_eq(_button(screen, "DecisionFinishButton").text, "Finish")
	var clock := screen.engine.elapsed
	await wait_physics_frames(60)
	assert_true(screen.engine.is_active(), "no automatic finish while the prompt is open")
	assert_eq(screen.engine.elapsed, clock, "clock held while deciding")
	assert_false(screen.engine.can_fire())
	screen.pause()
	assert_false(tree.paused, "pause does not replace the prompt")
	assert_eq(main.progress.is_mission_completed("helix_01"), false, "nothing recorded yet")
	await _free(main)


func test_continue_then_finish_button_ends_with_results_and_saves() -> void:
	var main: Node = await _make_main()
	var screen: MissionScreen = main._mission
	await _reach_prompt(screen)
	_button(screen, "DecisionContinueButton").pressed.emit()
	await tree.process_frame
	assert_false(screen.hud.has_overlay(), "Continue closes the prompt")
	assert_true(screen.engine.is_active() and not screen.engine.awaiting_decision)
	assert_true(_button(screen, "FinishButton").visible, "a Finish action stays available")
	await wait_physics_frames(90)
	assert_false(screen.hud.has_overlay(), "the prompt does not come back")
	# Optional goals can still be pursued: wipe the racks.
	for rack: String in ["rack_1", "rack_2", "rack_3", "rack_4"]:
		screen.engine.apply_damage(rack, 9999.0, DamageRules.TYPE_IMPACT, 0.9)
	assert_eq(screen.engine.objectives.get_objective("racks").status, Status.COMPLETE)
	_button(screen, "FinishButton").pressed.emit()
	assert_eq(screen.engine.phase, MissionEngine.Phase.SUCCEEDED)
	assert_false(_button(screen, "FinishButton").visible)
	assert_eq(screen.engine.objectives.get_objective("relay").status, Status.FAILED, "unfinished optional goal is not completed")
	assert_eq(screen.engine.objectives.get_objective("racks").status, Status.COMPLETE)
	assert_true(int(screen.last_score.mission_points) > 1000, "score kept")
	for i in 200:
		if screen.hud.has_overlay():
			break
		await tree.process_frame
	assert_true(_button(screen, "NextButton") != null, "normal results panel with Next mission")
	var saved := SaveService.new(TEST_SAVE).load_progress()
	assert_true(saved.is_mission_completed("helix_01"))
	# Stored sorted; the unfinished "relay" goal is not saved as completed.
	assert_eq(saved.mission_result("helix_01").get("optional_completed", []), ["efficient", "racks"], str(saved.mission_result("helix_01")))
	await _free(main)


func test_finish_from_the_prompt_goes_to_results() -> void:
	var main: Node = await _make_main()
	var screen: MissionScreen = main._mission
	await _reach_prompt(screen)
	_button(screen, "DecisionFinishButton").pressed.emit()
	assert_eq(screen.engine.phase, MissionEngine.Phase.SUCCEEDED)
	assert_eq(screen.engine.objectives.get_objective("racks").status, Status.FAILED)
	for i in 200:
		if _button(screen, "NextButton") != null:
			break
		await tree.process_frame
	assert_true(_button(screen, "NextButton") != null, "results after Finish")
	assert_true(main.progress.is_mission_completed("helix_01"))
	await _free(main)


func test_android_back_at_the_prompt_means_continue() -> void:
	var main: Node = await _make_main()
	var screen: MissionScreen = main._mission
	await _reach_prompt(screen)
	main._handle_back()
	await tree.process_frame
	assert_false(screen.engine.awaiting_decision)
	assert_true(screen.engine.is_active())
	assert_false(screen.hud.has_overlay())
	await _free(main)
