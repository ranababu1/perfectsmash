extends SceneTree
## Renders Google Play listing art from the real game into store/ (24-bit PNG, no alpha, as Play
## requires). Needs a window (not --headless) and --fixed-fps so captured moments are repeatable.
##
##   Screenshots (16:9):   godot --resolution 1920x1080 --fixed-fps 60 -s tools/render_store_art.gd
##   Feature graphic:      godot --resolution 1024x500 --fixed-fps 60 -s tools/render_store_art.gd -- --feature
##   Pick moments:         godot --resolution 960x540 --fixed-fps 60 -s tools/render_store_art.gd -- --probe
##
## Uses a throwaway save, so the developer's own progress is untouched.

const OUT_DIR := "res://store"
const CAPTURE_SAVE := "user://store_capture_progress.json"
const MainScript := preload("res://scripts/main.gd")
## Physics frames after launch at which each collapse looks most dramatic (picked by eye from
## the --probe contact frames). Re-pick them after any level or physics change.
const COLLAPSE_FRAMES := 88
const CHAIN_FRAMES := 136
const SETTLE_BEFORE_LAUNCH := 90


func _initialize() -> void:
	_run.call_deferred()


func _run() -> void:
	DirAccess.make_dir_recursive_absolute(ProjectSettings.globalize_path(OUT_DIR))
	var catalog := LevelCatalog.load_from_file()
	var progress := ProgressData.new()
	# A believable mid-game save: the first eleven levels cleared with mixed medals.
	for i in 11:
		progress.record_win(catalog.levels[i].id, [3, 3, 2, 3, 1, 3, 2, 3, 3, 2, 3][i], 1)
	var save := SaveService.new(CAPTURE_SAVE)
	save.save_progress(progress)
	var main: Node = MainScript.new()
	main.save = save
	root.add_child(main)
	await _frames(20)

	if OS.get_cmdline_user_args().has("--probe"):
		await _probe(main, catalog)
	elif OS.get_cmdline_user_args().has("--feature"):
		await _feature_graphic(main, catalog)
	else:
		await _screenshots(main, catalog)
	DirAccess.remove_absolute(ProjectSettings.globalize_path(CAPTURE_SAVE))
	quit()


func _screenshots(main: Node, catalog: LevelCatalog) -> void:
	await _shot("screenshot_1_menu")

	# Aiming at the Pyramid with the guide visible.
	await _open_level(main, catalog, "L12")
	var game: GameScreen = main._game
	var origin := game.session.launcher_position()
	game.aim._dragging = true
	game.aim._drag_start = origin + Vector2(260, 40)
	game.aim._drag_current = origin + Vector2(80, 130)
	await _frames(6)
	await _shot("screenshot_2_aim")
	game.aim.cancel()

	# Mid-collapse on the final level.
	await _open_level(main, catalog, "L20")
	await _launch_and_wait(main._game, COLLAPSE_FRAMES)
	await _shot("screenshot_3_collapse")

	# Chain reaction level, a little later in the fall.
	await _open_level(main, catalog, "L19")
	await _launch_and_wait(main._game, CHAIN_FRAMES)
	await _shot("screenshot_4_chain")

	# The result panel after a clean solve.
	await _open_level(main, catalog, "L08")
	main._game.hud.show_result(true, 3, 1, true, 1)
	# Stars pop in one at a time; wait for all three.
	await create_timer(1.6).timeout
	await _frames(10)
	await _shot("screenshot_5_clear")


## 1024x500: the final level collapsing, the title on the open sky at the left, no HUD.
func _feature_graphic(main: Node, catalog: LevelCatalog) -> void:
	await _open_level(main, catalog, "L20")
	var game: GameScreen = main._game
	game.hud.visible = false
	var layer := CanvasLayer.new()
	root.add_child(layer)
	var titles := VBoxContainer.new()
	titles.position = Vector2(64, 150)
	titles.add_theme_constant_override("separation", 4)
	var title := UiKit.label("PERFECT SMASH", 76, Palette.TEXT)
	title.horizontal_alignment = HORIZONTAL_ALIGNMENT_LEFT
	title.add_theme_font_override("font", MenuScreen._spaced_font(6))
	var tagline := UiKit.label("One smart hit. A spectacular chain reaction.", 30, Palette.TEXT_DIM)
	tagline.horizontal_alignment = HORIZONTAL_ALIGNMENT_LEFT
	titles.add_child(title)
	titles.add_child(tagline)
	layer.add_child(titles)
	await _launch_and_wait(game, COLLAPSE_FRAMES)
	await _shot("feature_graphic")


## Design aid: captures each collapse level every 8 physics frames into store/probe/ to pick the moments.
func _probe(main: Node, catalog: LevelCatalog) -> void:
	DirAccess.make_dir_recursive_absolute(ProjectSettings.globalize_path(OUT_DIR + "/probe"))
	for id in ["L20", "L19", "L12"]:
		await _open_level(main, catalog, id)
		main._game.session.launch(main._game.session.definition.solution[0])
		for step in 24:
			for i in 8:
				await physics_frame
			await _shot("probe/%s_%03d" % [id, (step + 1) * 8])


func _open_level(main: Node, catalog: LevelCatalog, id: String) -> void:
	main._start_level(catalog.ids().find(id))
	await _frames(SETTLE_BEFORE_LAUNCH)
	main._game.hud.fade_hint()
	await _frames(40)


func _launch_and_wait(game: GameScreen, frames: int) -> void:
	game.session.launch(game.session.definition.solution[0])
	for i in frames:
		await physics_frame


func _frames(count: int) -> void:
	for i in count:
		await process_frame


func _shot(file_name: String) -> void:
	await RenderingServer.frame_post_draw
	var image := root.get_texture().get_image()
	image.convert(Image.FORMAT_RGB8)
	var path := ProjectSettings.globalize_path("%s/%s.png" % [OUT_DIR, file_name])
	var err := image.save_png(path)
	if err != OK:
		push_error("Could not save %s (error %d)" % [path, err])
	else:
		print("saved %s (%dx%d)" % [path, image.get_width(), image.get_height()])
