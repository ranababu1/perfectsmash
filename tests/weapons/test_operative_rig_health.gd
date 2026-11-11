extends TestCase
## Operative rig health in the Helix mission: drives idle -> ready -> aim -> fire (both weapons)
## -> reload -> weapon switch -> victory/defeat through the real MissionScreen and checks that each
## state or clip transition actually happens (clips are recorded from AnimationPlayer.animation_started).

const PHYSICS_SUITE := true
const TEST_SAVE := "user://test_operative_rig_progress.json"
const MainScript := preload("res://scripts/main.gd")
const CLIPS := ["idle", "ready", "aim_pose", "fire_recoil", "reload", "weapon_switch", "victory", "defeat"]

var _started: Array[String] = []


func _make_main() -> Node:
	if FileAccess.file_exists(TEST_SAVE):
		DirAccess.remove_absolute(ProjectSettings.globalize_path(TEST_SAVE))
	var main: Node = MainScript.new()
	main.save = SaveService.new(TEST_SAVE)
	main.boot_mission = "helix_01"
	tree.root.add_child(main)
	await tree.process_frame
	return main


func _free(main: Node) -> void:
	tree.paused = false
	main.queue_free()
	await tree.process_frame


func _on_started(clip: StringName) -> void:
	_started.append(String(clip))


## Waits until the rig's one-shot clip (if any) has handed back to its loop.
func _settle(rig: OperativeRig) -> void:
	for i in 600:
		if rig._one_shot.is_empty():
			return
		await tree.process_frame


func test_rig_walks_through_every_state_and_clip() -> void:
	var main: Node = await _make_main()
	var screen: MissionScreen = main._mission
	var rig: OperativeRig = screen.view.operative
	assert_true(rig.uses_model, "production operative model is in use")
	if not rig.uses_model:
		await _free(main)
		return
	for clip: String in CLIPS:
		assert_true(rig._animation.has_animation(clip), "clip '%s' exists" % clip)
	rig._animation.animation_started.connect(_on_started)
	var target := screen.view.plane_to_screen(Vector2(830.0, 462.0))

	# idle: no input for longer than IDLE_AFTER
	screen._since_input = MissionScreen.IDLE_AFTER + 1.0
	await tree.process_frame
	await tree.process_frame
	assert_eq(rig.state, OperativeRig.State.IDLE, "idle after inactivity")
	assert_true(_started.has("idle"), "idle clip played")

	# ready: recent input
	_started.clear()
	screen._since_input = 0.0
	await tree.process_frame
	await tree.process_frame
	assert_eq(rig.state, OperativeRig.State.READY, "ready after input")
	assert_true(_started.has("ready"), "ready clip played")

	# aim
	_started.clear()
	screen.begin_aim(target + Vector2(-40, 10))
	screen.update_aim(target)
	await tree.process_frame
	await tree.process_frame
	assert_eq(rig.state, OperativeRig.State.AIM, "aim while touching")
	assert_true(_started.has("aim_pose"), "aim pose clip played")

	# fire kinetic, then reload
	_started.clear()
	assert_true(screen.release_aim(), "kinetic fired")
	assert_true(_started.has("fire_recoil"), "kinetic fire recoil clip played")
	await tree.process_frame
	assert_eq(rig.state, OperativeRig.State.RELOAD, "reload state after firing")
	await _settle(rig)
	assert_true(_started.has("reload"), "reload clip played after the recoil hands back")

	# weapon switch to the Breach Charge
	_started.clear()
	screen.select_weapon("breach_charge")
	assert_eq(rig.weapon_id, "breach_charge")
	assert_true(_started.has("weapon_switch"), "weapon switch clip played")
	await _settle(rig)

	# fire the Breach Charge (lobbed)
	_started.clear()
	screen.begin_aim(screen.view.plane_to_screen(screen.world.muzzle_position() + Vector2(500, -250)))
	await tree.process_frame
	assert_true(screen.release_aim(), "breach charge fired")
	assert_true(_started.has("fire_recoil"), "breach fire recoil clip played")
	assert_eq(screen.engine.weapons.breach_charge.ammo, 2)
	await tree.process_frame
	assert_eq(rig.state, OperativeRig.State.RELOAD, "reload state after the charge")
	await _settle(rig)

	# switch back
	_started.clear()
	screen.select_weapon("kinetic_accelerator")
	assert_eq(rig.weapon_id, "kinetic_accelerator")
	assert_true(_started.has("weapon_switch"), "switching back plays the clip again")
	await _settle(rig)

	# defeat pose (driven directly: the screen's own _process picks the state from the engine phase)
	screen.set_process(false)
	_started.clear()
	rig.set_state(OperativeRig.State.DEFEAT)
	await tree.process_frame
	assert_true(_started.has("defeat"), "defeat clip played")
	screen.set_process(true)

	# victory through the real engine
	_started.clear()
	screen.engine.apply_damage("aura_core", 9999.0, DamageRules.TYPE_IMPACT, 0.9)
	for i in 600:
		if not screen.engine.is_active() or screen.engine.awaiting_decision:
			break
		await tree.physics_frame
	assert_true(screen.engine.awaiting_decision, "optional goals pending: the decision prompt is shown")
	screen.finish_mission()
	await _settle(rig)
	await tree.process_frame
	await tree.process_frame
	assert_eq(screen.engine.phase, MissionEngine.Phase.SUCCEEDED)
	assert_eq(rig.state, OperativeRig.State.VICTORY, "victory state on success")
	assert_true(_started.has("victory"), "victory clip played")
	await _free(main)


func test_reload_completed_fires_once_in_a_live_mission() -> void:
	var main: Node = await _make_main()
	var screen: MissionScreen = main._mission
	var weapon: WeaponState = screen.engine.weapons.kinetic_accelerator
	var events: Array = []
	weapon.reload_completed.connect(func(id: String) -> void: events.append(id))
	var target := screen.view.plane_to_screen(Vector2(830.0, 462.0))
	screen.begin_aim(target)
	assert_true(screen.release_aim())
	for i in 150:
		await tree.physics_frame
	assert_eq(events.size(), 1, "exactly one reload-complete after one shot")
	assert_true(weapon.can_fire())
	await _free(main)
