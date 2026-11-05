extends SceneTree
## Renders Google Play listing art from the real game into store/ (24-bit PNG, no alpha, as Play
## requires). Needs a window (not --headless) and --fixed-fps so captured moments are repeatable.
##
##   Screenshots (16:9):   godot --resolution 1920x1080 --fixed-fps 60 -s tools/render_store_art.gd
##   Feature graphic:      godot --resolution 1024x500 --fixed-fps 60 -s tools/render_store_art.gd -- --feature
##   Pick moments:         godot --resolution 960x540 --fixed-fps 60 -s tools/render_store_art.gd -- --probe[=L60,L61]
##
## Uses a throwaway save, so the developer's own progress is untouched.

const OUT_DIR := "res://store"
const CAPTURE_SAVE := "user://store_capture_progress.json"
const MainScript := preload("res://scripts/main.gd")
## Physics frames after launch at which each collapse looks most dramatic (picked by eye from
## the --probe contact frames). Re-pick them after any level or physics change.
const COLLAPSE_FRAMES := 88
const CHAIN_FRAMES := 136
## Mission 60's explosive chain mid-cascade, and mission 100's heavy shot striking the spire.
const BLAST_CHAIN_FRAMES := 56
const SPIRE_FRAMES := 16
const SETTLE_BEFORE_LAUNCH := 90


func _initialize() -> void:
	_run.call_deferred()


func _run() -> void:
	DirAccess.make_dir_recursive_absolute(ProjectSettings.globalize_path(OUT_DIR))
	var catalog := LevelCatalog.load_from_file()
	var progress := ProgressData.new()
	# A believable mid-game save: chapter 1 and part of chapter 2 cleared with mixed medals.
	for i in 26:
		progress.record_win(catalog.levels[i].id, [3, 3, 2, 3, 1, 3, 2, 3, 3, 2, 3, 2, 3][i % 13], 1)
	var save := SaveService.new(CAPTURE_SAVE)
	save.save_progress(progress)
	var main: Node = MainScript.new()
	main.save = save
	root.add_child(main)
	await _frames(20)

	var probe_ids := PackedStringArray()
	for a in OS.get_cmdline_user_args():
		if a.begins_with("--probe="):
			probe_ids = a.trim_prefix("--probe=").split(",")
	if OS.get_cmdline_user_args().has("--probe"):
		probe_ids = PackedStringArray(["L20", "L19", "L12"])
	if not probe_ids.is_empty():
		await _probe(main, catalog, probe_ids)
	elif OS.get_cmdline_user_args().has("--feature"):
		await _feature_graphic(main, catalog)
	else:
		await _screenshots(main, catalog)
	DirAccess.remove_absolute(ProjectSettings.globalize_path(CAPTURE_SAVE))
	quit()


func _screenshots(main: Node, catalog: LevelCatalog) -> void:
	await _shot("screenshot_1_menu")

	# A mission briefing with the whole transcript shown.
	main._start_level(catalog.ids().find("L61"))
	await _frames(30)
	main._briefing.dialogue.finish_all()
	await _frames(30)
	await _shot("screenshot_2_briefing")
	main._close_briefing()

	# The finale: the heavy shot striking the spire.
	await _open_level(main, catalog, "L100")
	await _launch_and_wait(main._game, SPIRE_FRAMES)
	await _shot("screenshot_3_spire")

	# An explosive chain mid-cascade.
	await _open_level(main, catalog, "L60")
	await _launch_and_wait(main._game, BLAST_CHAIN_FRAMES)
	await _shot("screenshot_4_chain")

	# The original two-storey collapse.
	await _open_level(main, catalog, "L20")
	await _launch_and_wait(main._game, COLLAPSE_FRAMES)
	await _shot("screenshot_5_collapse")

	# A story debrief after a clean solve.
	await _open_level(main, catalog, "L40")
	main._game.hud.show_result(true, 3, 1, true, 2, main.story.debrief("L40"))
	await create_timer(1.6).timeout
	var debrief: DialogueBox = main._game.hud._overlay.find_child("Debrief", true, false)
	debrief.finish_all()
	await _frames(20)
	await _shot("screenshot_6_debrief")


## 1024x500: an explosive chain going off, the title on the open sky at the left, no HUD.
func _feature_graphic(main: Node, catalog: LevelCatalog) -> void:
	await _open_level(main, catalog, "L60")
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
	await _launch_and_wait(game, BLAST_CHAIN_FRAMES)
	await _shot("feature_graphic")


## Design aid: captures each collapse level every 8 physics frames into store/probe/ to pick the moments.
func _probe(main: Node, catalog: LevelCatalog, ids: PackedStringArray) -> void:
	DirAccess.make_dir_recursive_absolute(ProjectSettings.globalize_path(OUT_DIR + "/probe"))
	for id in ids:
		await _open_level(main, catalog, id)
		main._game.session.launch(main._game.session.definition.solution[0])
		for step in 24:
			for i in 8:
				await physics_frame
			await _shot("probe/%s_%03d" % [id, (step + 1) * 8])


func _open_level(main: Node, catalog: LevelCatalog, id: String) -> void:
	main._start_level(catalog.ids().find(id))
	main._close_briefing()
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
