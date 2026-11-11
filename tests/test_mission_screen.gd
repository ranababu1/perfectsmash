extends TestCase
## The playable Helix prototype through the real app root: boot, touch aiming, firing, weapon
## switching, cancel, pause and restart.

const TEST_SAVE := "user://test_mission_progress.json"
const MainScript := preload("res://scripts/main.gd")


func _make_main() -> Node:
	if FileAccess.file_exists(TEST_SAVE):
		DirAccess.remove_absolute(ProjectSettings.globalize_path(TEST_SAVE))
	var main: Node = MainScript.new()
	main.cinematics_enabled = false
	main.save = SaveService.new(TEST_SAVE)
	main.boot_mission = "helix_08"
	tree.root.add_child(main)
	await tree.process_frame
	return main


func _free(main: Node) -> void:
	tree.paused = false
	main.queue_free()
	await tree.process_frame


func _mouse(at: Vector2, pressed: bool) -> void:
	var event := InputEventMouseButton.new()
	event.button_index = MOUSE_BUTTON_LEFT
	event.pressed = pressed
	event.position = at
	event.global_position = at
	tree.root.push_input(event, true)


func _motion(at: Vector2) -> void:
	var event := InputEventMouseMotion.new()
	event.position = at
	event.global_position = at
	tree.root.push_input(event, true)


func test_app_boots_into_the_campaign_menu() -> void:
	if FileAccess.file_exists(TEST_SAVE):
		DirAccess.remove_absolute(ProjectSettings.globalize_path(TEST_SAVE))
	var main: Node = MainScript.new()
	main.cinematics_enabled = false
	main.save = SaveService.new(TEST_SAVE)
	tree.root.add_child(main)
	await tree.process_frame
	assert_true(main._campaign != null and main._mission == null, "the campaign menu is the first screen")
	assert_eq(main._campaign.view, CampaignScreen.View.MENU)
	assert_eq(main._campaign.continue_target(), "helix_01", "Continue starts the first mission on a fresh save")
	assert_true(main._menu == null, "legacy menu is not shown")
	await _free(main)


func test_boot_mission_starts_the_requested_mission() -> void:
	var main: Node = await _make_main()
	var screen: MissionScreen = main._mission
	assert_true(screen != null, "boot_mission starts the mission directly")
	assert_true(main._menu == null, "legacy menu is not shown")
	assert_eq(screen.engine.definition.id, "helix_08")
	assert_true(screen.view.operative != null, "operative is in the scene")
	assert_true(screen.view.camera.current)
	await _free(main)


func test_touch_aim_and_release_fires_kinetic() -> void:
	var main: Node = await _make_main()
	var screen: MissionScreen = main._mission
	var target := screen.view.plane_to_screen(Vector2(830.0, 462.0))
	_mouse(target + Vector2(-40, 10), true)
	await tree.process_frame
	_motion(target)
	await tree.process_frame
	assert_eq(screen.view.operative.state, OperativeRig.State.AIM, "operative aims while touching")
	assert_true(screen.view._preview.visible, "trajectory preview shown")
	_mouse(target, false)
	await tree.process_frame
	assert_eq(screen.engine.weapons.kinetic_accelerator.ammo, 13, "release fired one round")
	assert_eq(screen.world.projectiles.size(), 1)
	assert_false(screen.view._preview.visible)
	await tree.process_frame
	assert_eq(screen.view.operative.state, OperativeRig.State.RELOAD, "operative reloads after firing")
	await _free(main)


func test_release_near_operative_cancels() -> void:
	var main: Node = await _make_main()
	var screen: MissionScreen = main._mission
	var muzzle := screen.view.plane_to_screen(screen.world.muzzle_position())
	screen.begin_aim(muzzle + Vector2(6, 0))
	assert_false(screen.release_aim(), "too close to the operative: cancelled")
	assert_eq(screen.engine.shots_fired(), 0)
	await _free(main)


func test_weapon_switch_and_lobbed_power() -> void:
	var main: Node = await _make_main()
	var screen: MissionScreen = main._mission
	screen.hud.weapon_pressed.emit("breach_charge")
	assert_eq(screen.engine.selected_weapon_id, "breach_charge")
	assert_eq(screen.view.operative.weapon_id, "breach_charge")
	var near := screen.view.plane_to_screen(screen.world.muzzle_position() + Vector2(200, -100))
	screen.begin_aim(near)
	var weak := screen._aim_power
	screen.update_aim(screen.view.plane_to_screen(screen.world.muzzle_position() + Vector2(600, -300)))
	assert_true(screen._aim_power > weak, "farther touch = stronger throw")
	assert_true(screen.release_aim())
	assert_eq(screen.engine.weapons.breach_charge.ammo, 2)
	assert_false(screen.engine.can_fire(), "charge reloading")
	await _free(main)


func test_pause_blocks_aim_and_restart_rebuilds() -> void:
	var main: Node = await _make_main()
	var screen: MissionScreen = main._mission
	screen.pause()
	assert_true(tree.paused)
	assert_true(screen.hud.has_overlay())
	screen.begin_aim(screen.view.plane_to_screen(Vector2(830.0, 462.0)))
	assert_false(screen.release_aim(), "no aiming while paused")
	screen.resume()
	assert_false(tree.paused)
	screen.restart_requested.emit()
	await tree.process_frame
	assert_true(main._mission != null and main._mission != screen, "restart builds a fresh mission")
	assert_eq(main._mission.engine.shots_fired(), 0)
	await _free(main)


func test_objective_progress_refreshes_on_destruction() -> void:
	var main: Node = await _make_main()
	var screen: MissionScreen = main._mission
	screen.engine.apply_damage("rack_1", 9999.0, DamageRules.TYPE_IMPACT, 0.9)
	await tree.process_frame
	var texts := []
	for row: Node in screen.hud._objective_box.get_children():
		if row.is_queued_for_deletion():
			continue
		for label: Label in ([row] if row is Label else row.find_children("*", "Label", true, false)):
			texts.append(label.text)
	assert_true(texts.any(func(t: String) -> bool: return t.contains("server racks") and t.contains("25%")), str(texts))
	await _free(main)


func test_finished_mission_is_scored_saved_and_not_farmable() -> void:
	var main: Node = await _make_main()
	var screen: MissionScreen = main._mission
	screen.engine.apply_damage("aura_core", 9999.0, DamageRules.TYPE_IMPACT, 0.9)
	for i in 600:
		if not screen.engine.is_active() or screen.engine.awaiting_decision:
			break
		await tree.physics_frame
	assert_true(screen.engine.awaiting_decision, "optional goals pending: the decision prompt is shown")
	screen.finish_mission()
	assert_eq(screen.engine.phase, MissionEngine.Phase.SUCCEEDED)
	assert_true(screen.last_score.mission_points > 1000)
	assert_true(screen.last_research_granted >= 20, "completion Research Data granted")
	var stored := SaveService.new(TEST_SAVE).load_progress()
	assert_true(stored.is_mission_completed("helix_08"), "result written to disk")
	assert_eq(stored.research_data, screen.last_research_granted)
	var first_score: Dictionary = screen.last_score.duplicate()
	var first_granted := screen.last_research_granted
	# Same mission again with an identical result: no new Research Data.
	screen.restart_requested.emit()
	await tree.process_frame
	var again: MissionScreen = main._mission
	again.engine.apply_damage("aura_core", 9999.0, DamageRules.TYPE_IMPACT, 0.9)
	for i in 600:
		if not again.engine.is_active() or again.engine.awaiting_decision:
			break
		await tree.physics_frame
	assert_true(again.engine.awaiting_decision, "the prompt is offered again on a fresh attempt")
	again.finish_mission()
	assert_eq(int(again.last_score.research_data), int(first_score.research_data), "identical run, identical score")
	assert_eq(again.last_research_granted, 0, "replaying for the same result earns no Research Data")
	var reloaded := SaveService.new(TEST_SAVE).load_progress()
	assert_eq(reloaded.research_data, first_granted)
	assert_eq(reloaded.mission_result("helix_08").attempts, 2, "both runs counted")
	assert_eq(reloaded.mission_result("helix_08").completions, 2)
	await _free(main)


func test_hud_uses_production_theme_icons_and_operative() -> void:
	var main: Node = await _make_main()
	var screen: MissionScreen = main._mission
	await tree.process_frame
	assert_true(screen.hud.theme != null and screen.hud.theme.resource_path.ends_with("tfj_theme.tres"), "production UI theme")
	assert_true(screen.hud.icon("kinetic_accelerator") != null, "weapon icons")
	var weapon_button: Button = screen.hud._weapon_buttons["kinetic_accelerator"]
	assert_true(weapon_button.icon != null, "weapon button shows its icon")
	assert_true(weapon_button.text.contains("14"), "ammunition stays a live label")
	assert_true(screen.hud.critical_marker != null and screen.hud.critical_marker.visible, "critical-asset marker on screen")
	assert_false(screen.view.world_markers, "the HUD marker replaces the 3D marker")
	assert_true(screen.view.operative.uses_model, "production operative model")
	assert_true(screen.view.operative.muzzle != null, "weapon model with its muzzle marker")
	screen.select_weapon("breach_charge")
	assert_eq(String(screen.view.operative.muzzle.get_parent().name), "opr_wpn_breach_charge_a", "the shown weapon follows the selection")
	await _free(main)
