extends SceneTree
## Design aid for the Helix greybox: boots the real app (which opens the mission), drives aiming
## through MissionScreen's public aim API and writes screenshots to tests/output/mission/.
## Needs a window (not --headless):
##   godot_console --resolution 1280x720 -s tools/capture_mission.gd [-- --size=WxH]

const OUT_DIR := "res://tests/output/mission"
const CAPTURE_SAVE := "user://capture_mission_progress.json"
const MainScript := preload("res://scripts/main.gd")


func _initialize() -> void:
	_run.call_deferred()


func _run() -> void:
	DirAccess.make_dir_recursive_absolute(ProjectSettings.globalize_path(OUT_DIR))
	var main: Node = MainScript.new()
	main.cinematics_enabled = false
	main.save = SaveService.new(CAPTURE_SAVE)
	main.boot_mission = "helix_08"
	root.add_child(main)
	await _frames(40)
	var screen: MissionScreen = main._mission
	await _shot("01_mission_start")

	# Kinetic: aim at the top of the left support column, past the blast wall.
	var column_top := Vector2(830.0, 462.0)
	screen.begin_aim(screen.view.plane_to_screen(column_top))
	await _frames(20)
	await _shot("02_aim_kinetic")
	screen.release_aim()
	await _frames(8)
	await _shot("03_kinetic_in_flight")
	await _frames(70)
	await _shot("04_after_kinetic_hit")

	# Breach Charge: arc preview over the shield toward the core.
	screen.select_weapon("breach_charge")
	await _frames(10)
	screen.begin_aim(screen.view.plane_to_screen(Vector2(760.0, 120.0)))
	await _frames(20)
	await _shot("05_aim_breach_arc")
	screen.release_aim()
	await _frames(30)
	await _shot("06_breach_detonation")
	await _frames(150)
	await _shot("07_after_breach")

	screen.pause()
	await _frames(20)
	await _shot("08_pause")
	screen.resume()
	# Finish the mission for the result panel if it is still running.
	if screen.engine.is_active():
		screen.engine.apply_damage("aura_core", 9999.0, DamageRules.TYPE_IMPACT, 0.9)
	for i in 600:
		if screen.hud.has_overlay():
			break
		await process_frame
	await _frames(40)
	await _shot("09_result")

	DirAccess.remove_absolute(ProjectSettings.globalize_path(CAPTURE_SAVE))
	quit()


func _frames(count: int) -> void:
	for i in count:
		await process_frame


func _shot(shot_name: String) -> void:
	await RenderingServer.frame_post_draw
	var path := ProjectSettings.globalize_path("%s/%s.png" % [OUT_DIR, shot_name])
	var err := root.get_texture().get_image().save_png(path)
	if err != OK:
		push_error("Could not save %s (error %d)" % [path, err])
	else:
		print("saved ", path)
