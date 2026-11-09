extends SceneTree
## Screenshots of the Helix mission for asset-integration reviews: the real MissionScreen (3D
## view + HUD) without the app root, so focus loss cannot auto-pause it. Same camera and
## resolution every run. Writes tests/output/helix/<tag>_<step>.png. Needs a window:
##   godot_console --resolution 1280x720 -s tools/capture_helix.gd [-- --tag=after]

const OUT_DIR := "res://tests/output/helix"
const ProbeAim := preload("res://tools/regression/probe_aim.gd")

var _tag := "capture"


func _initialize() -> void:
	for arg in OS.get_cmdline_user_args():
		if arg.begins_with("--tag="):
			_tag = arg.trim_prefix("--tag=")
	_run.call_deferred()


func _run() -> void:
	DirAccess.make_dir_recursive_absolute(ProjectSettings.globalize_path(OUT_DIR))
	var screen := MissionScreen.new()
	root.add_child(screen)
	await _frames(30)
	await _shot("1_start")
	# Kinetic aim with the preview, at the left column.
	screen.begin_aim(screen.view.plane_to_screen(Vector2(826, 512)))
	await _frames(10)
	await _shot("2_aim_kinetic")
	screen.release_aim()
	await _frames(70)
	await _shot("3_column_hit")
	# Breach collapse of the left column (45 degrees, 70%).
	screen.select_weapon("breach_charge")
	await _frames(80)
	screen.world.fire(Vector2.RIGHT.rotated(-deg_to_rad(45.0)), 0.7)
	for i in 40:
		await physics_frame
		if not screen.world.projectiles.is_empty():
			continue
		break
	await _frames(4)
	await _shot("4_breach_detonation")
	for i in 600:
		if i > 60 and screen.world.projectiles.is_empty() and screen.world.is_settled():
			break
		await physics_frame
	await _shot("5_core_exposed")
	screen.select_weapon("kinetic_accelerator")
	await _frames(70)
	var core := screen.world.body_for("aura_core")
	if core != null:
		var plan: Dictionary = ProbeAim.aim(screen.world, core)
		var direction: Vector2 = plan.direction if plan.direction != Vector2.ZERO else core.global_position - screen.world.muzzle_position()
		screen.begin_aim(screen.view.plane_to_screen(screen.world.muzzle_position() + direction.normalized() * 500.0))
		await _frames(10)
		await _shot("6_aim_finish")
		screen.release_aim()
		await _frames(40)
		await _shot("7_core_destroyed")
	for i in 600:
		if screen.hud.has_overlay():
			break
		await process_frame
	await _frames(30)
	await _shot("8_result")
	print("CAPTURE_HELIX %s core %s, pieces %d" % [_tag, ["intact", "damaged", "critical", "destroyed"][screen.engine.component_state("aura_core")], screen.view.placed_pieces.size()])
	quit()


func _shot(step: String) -> void:
	await process_frame
	root.get_texture().get_image().save_png(ProjectSettings.globalize_path("%s/%s_%s.png" % [OUT_DIR, _tag, step]))


func _frames(count: int) -> void:
	for i in count:
		await process_frame
