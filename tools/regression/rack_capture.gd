extends SceneTree
## Screenshots for the rack-height comparison: the real MissionScreen (3D view, HUD) on each
## layout variant at the same camera and resolution: start, after a 45 degree / 70% Breach
## collapse, aiming the kinetic finishing shot with the arc preview, and after the finish.
## Writes tests/output/racks/<layout>_<step>.png. Needs a window:
##   godot_console --resolution 1280x720 -s tools/regression/rack_capture.gd [-- --layouts=a,b]

const OUT_DIR := "res://tests/output/racks"
const MISSION := "res://data/missions/helix_01.json"
const ProbeAim := preload("res://tools/regression/probe_aim.gd")
const Layouts := preload("res://tools/regression/probe_layouts.gd")


func _initialize() -> void:
	_run.call_deferred()


func _run() -> void:
	DirAccess.make_dir_recursive_absolute(ProjectSettings.globalize_path(OUT_DIR))
	var layouts: Array = ["shipped", "one_bank", "short_racks", "tall_racks", "racks_70"]
	for arg in OS.get_cmdline_user_args():
		if arg.begins_with("--layouts="):
			layouts = arg.trim_prefix("--layouts=").split(",")
	for layout: String in layouts:
		var data: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(MISSION))
		Layouts.apply_json(data, layout)
		var path := "user://rack_capture_%s.json" % layout
		var file := FileAccess.open(path, FileAccess.WRITE)
		file.store_string(JSON.stringify(data))
		file.close()
		var screen := MissionScreen.new(null, null, null, path)
		root.add_child(screen)
		await _frames(30)
		await _shot(layout, "1_start")
		screen.select_weapon("breach_charge")
		screen.world.fire(Vector2.RIGHT.rotated(-deg_to_rad(45.0)), 0.7)
		for i in 600:
			if i > 60 and screen.world.projectiles.is_empty() and screen.world.is_settled():
				break
			await physics_frame
		await _shot(layout, "2_after_breach_collapse")
		screen.select_weapon("kinetic_accelerator")
		await _frames(70)
		var core := screen.world.body_for("aura_core")
		if core != null:
			var plan: Dictionary = ProbeAim.aim(screen.world, core)
			var direction: Vector2 = plan.direction if plan.direction != Vector2.ZERO else core.global_position - screen.world.muzzle_position()
			var target := screen.world.muzzle_position() + direction.normalized() * 500.0
			screen.begin_aim(screen.view.plane_to_screen(target))
			await _frames(10)
			await _shot(layout, "3_aim_finish")
			screen.release_aim()
			await _frames(120)
		await _shot(layout, "4_after_finish")
		print("RACK_CAPTURE %s core %s" % [layout, ["intact", "damaged", "critical", "destroyed"][screen.engine.component_state("aura_core")]])
		screen.queue_free()
		await _frames(5)
	quit()


func _shot(layout: String, step: String) -> void:
	await process_frame
	var image := root.get_texture().get_image()
	image.save_png(ProjectSettings.globalize_path("%s/%s_%s.png" % [OUT_DIR, layout, step]))


func _frames(count: int) -> void:
	for i in count:
		await process_frame
