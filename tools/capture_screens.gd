extends SceneTree
## Design aid: boots the real app with a throwaway save and writes PNG screenshots of the main screens
## to tests/output/screens/. Needs a window (not --headless):
##   godot_console --resolution 1280x720 -s tools/capture_screens.gd [-- --level=N]

const OUT_DIR := "res://tests/output/screens"
const CAPTURE_SAVE := "user://capture_progress.json"
const MainScript := preload("res://scripts/main.gd")


func _initialize() -> void:
	_run.call_deferred()


func _run() -> void:
	DirAccess.make_dir_recursive_absolute(ProjectSettings.globalize_path(OUT_DIR))
	var level := 0
	for arg in OS.get_cmdline_user_args():
		if arg.begins_with("--level="):
			level = int(arg.trim_prefix("--level=")) - 1

	var progress := ProgressData.new()
	var catalog := LevelCatalog.load_from_file()
	# Fake a partly played save so the menu shows locked, unlocked and starred tiles.
	for i in mini(6, catalog.levels.size()):
		progress.record_win(catalog.levels[i].id, 3 - i % 3, 1)
	var save := SaveService.new(CAPTURE_SAVE)
	save.save_progress(progress)

	var main: Node = MainScript.new()
	main.save = save
	root.add_child(main)
	await _settle(20)
	await _shot("menu")
	main._open_settings()
	await _settle(30)
	await _shot("settings")
	main.close_settings()

	main._start_level(level)
	await _settle(60)
	await _shot("level")

	var game: GameScreen = main._game
	var origin := game.session.launcher_position()
	game.aim._dragging = true
	game.aim._drag_start = origin + Vector2(200, 0)
	game.aim._drag_current = origin + Vector2(80, 70)
	await _settle(4)
	await _shot("aiming")
	game.aim.cancel()

	game.pause()
	await _settle(30)
	await _shot("pause")
	game.resume()

	game.hud.show_result(true, 2, 2, true)
	await _settle(40)
	await _shot("win")
	game.hud.show_result(false, 0, 2, true)
	await _settle(40)
	await _shot("lose")

	DirAccess.remove_absolute(ProjectSettings.globalize_path(CAPTURE_SAVE))
	quit()


func _settle(frames: int) -> void:
	for i in frames:
		await process_frame


func _shot(name: String) -> void:
	await RenderingServer.frame_post_draw
	var path := ProjectSettings.globalize_path("%s/%s.png" % [OUT_DIR, name])
	var err := root.get_texture().get_image().save_png(path)
	if err != OK:
		push_error("Could not save %s (error %d)" % [path, err])
	else:
		print("saved ", path)
