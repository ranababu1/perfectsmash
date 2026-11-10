extends SceneTree
## Asset-integration screenshots in the real game scenes: the app's main scene as it boots, then
## the real MissionScreen (3D view, HUD, physics) for helix_01 and for the four tools-only chapter
## previews (tools/chapter_preview), each with a Breach Charge shot. Writes PNGs to the folder
## given with --out (default tests/output/chapters). Needs a window (xvfb works):
##   godot --path . --rendering-driver opengl3 --resolution 1280x720 --fixed-fps 60 \
##     -s tools/capture_chapters.gd -- --out=/tmp/chapters

const MainScene := preload("res://scenes/main.tscn")
const CAPTURE_SAVE := "user://capture_chapters_progress.json"
const PREVIEW_DIR := "res://tools/chapter_preview"
const MISSIONS := [
	["helix", "res://data/missions/helix_01.json", MissionView.ENVIRONMENT_DIR],
	["vita", PREVIEW_DIR + "/vita_preview.json", PREVIEW_DIR + "/environments"],
	["nova_grid", PREVIEW_DIR + "/nova_grid_preview.json", PREVIEW_DIR + "/environments"],
	["civitas", PREVIEW_DIR + "/civitas_preview.json", PREVIEW_DIR + "/environments"],
	["meridian", PREVIEW_DIR + "/meridian_preview.json", PREVIEW_DIR + "/environments"],
]
## Breach Charge aim point in the physics plane: an arc over the shield onto the core deck.
const BREACH_AIM := Vector2(760.0, 120.0)

var _out := "res://tests/output/chapters"


func _initialize() -> void:
	for arg in OS.get_cmdline_user_args():
		if arg.begins_with("--out="):
			_out = arg.trim_prefix("--out=")
	_run.call_deferred()


func _run() -> void:
	DirAccess.make_dir_recursive_absolute(_abs(_out))
	# 1. The real main scene (boots straight into the Helix mission).
	var main: Node = MainScene.instantiate()
	main.save = SaveService.new(CAPTURE_SAVE)
	root.add_child(main)
	await _frames(60)
	await _shot("00_main_scene_boot")
	main.queue_free()
	await _frames(5)
	# 2. One mission per chapter, each with a Breach Charge shot.
	var index := 1
	for spec: Array in MISSIONS:
		var chapter: String = spec[0]
		MissionView.environment_dir = spec[2]
		var screen := MissionScreen.new(null, null, null, spec[1])
		root.add_child(screen)
		await _frames(45)
		var tag := "%02d_%s" % [index, chapter]
		await _shot(tag + "_start")
		screen.select_weapon("breach_charge")
		await _frames(150)
		screen.begin_aim(screen.view.plane_to_screen(BREACH_AIM))
		await _frames(12)
		if chapter == "helix":
			await _shot(tag + "_breach_aim_arc")
		screen.release_aim()
		var shot_in_flight := false
		for i in 240:
			await process_frame
			if not shot_in_flight and chapter == "helix" and i == 14 and not screen.world.projectiles.is_empty():
				await _shot(tag + "_breach_in_flight")
				shot_in_flight = true
			if i > 2 and screen.world.projectiles.is_empty():
				break
		await _frames(5)
		await _shot(tag + "_breach_detonation")
		for i in 300:
			if i > 60 and screen.world.is_settled():
				break
			await process_frame
		await _shot(tag + "_after_breach")
		print("CAPTURE_CHAPTER %s pieces %d, models %d of %d, debris %d" % [chapter, screen.view.placed_pieces.size(), _models(screen.view), screen.view._meshes.size(), screen.view.debris_spawned.size()])
		screen.queue_free()
		await _frames(5)
		index += 1
	MissionView.environment_dir = MissionView.ENVIRONMENT_DIR
	MissionView.release_cached_set()
	DirAccess.remove_absolute(_abs(CAPTURE_SAVE))
	quit()


func _models(view: MissionView) -> int:
	var count := 0
	for id: String in view._meshes:
		if (view._meshes[id] as ComponentVisual).uses_model:
			count += 1
	return count


func _abs(path: String) -> String:
	return ProjectSettings.globalize_path(path) if path.begins_with("res://") or path.begins_with("user://") else path


func _shot(step: String) -> void:
	await RenderingServer.frame_post_draw
	var path := "%s/%s.png" % [_abs(_out), step]
	var err := root.get_texture().get_image().save_png(path)
	print("saved " if err == OK else "FAILED ", path)


func _frames(count: int) -> void:
	for i in count:
		await process_frame
