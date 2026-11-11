extends SceneTree
## Visual review of authored missions through the real app (MissionScreen: 3D set, chapter
## atmosphere, HUD): for each mission, the opening frame and the frame after its intended solution
## (tools/levels/solutions/<id>.json, first entry) has played. Needs a window (not --headless):
##   godot_console --resolution 1280x720 --fixed-fps 60 -s tools/levels/capture_campaign.gd -- <prefix|id|all> <out dir>
## Writes <out>/<id>_a_start.webp and <out>/<id>_b_end.webp and prints one line per mission.

const MainScript := preload("res://scripts/main.gd")
const Solver := preload("res://tools/levels/mission_solver.gd")
const SolutionBook := preload("res://tools/levels/solution_book.gd")
const CAPTURE_SAVE := "user://capture_campaign_progress.json"


func _initialize() -> void:
	_run.call_deferred()


func _run() -> void:
	var args := OS.get_cmdline_user_args()
	var which := args[0] if args.size() > 0 else "all"
	var out := args[1] if args.size() > 1 else ProjectSettings.globalize_path("res://tests/output/campaign")
	DirAccess.make_dir_recursive_absolute(out)
	root.gui_disable_input = true
	root.set_disable_input(true)
	var solutions := SolutionBook.load_all()
	var ids: Array[String] = []
	for s in MissionCatalog.load_default().authored():
		if which == "all" or s.id == which or s.id.begins_with(which + "_"):
			ids.append(s.id)
	var main: Node = MainScript.new()
	main.cinematics_enabled = false
	main.save = SaveService.new(CAPTURE_SAVE)
	root.add_child(main)
	await _frames(10)
	for id in ids:
		main._show_mission(id)
		await _frames(40)
		var screen: MissionScreen = main._mission
		await _shot(out, "%s_a_start" % id)
		var plans: Array = solutions.get(id, [])
		var result := {"success": false, "shots": 0, "blocked": "no solution"}
		if not plans.is_empty():
			result = await Solver.play(self, screen.world, plans[0].steps)
		for i in 240:
			if screen.hud.has_overlay():
				break
			await process_frame
		await _frames(20)
		await _shot(out, "%s_b_end" % id)
		print("%s: %s shots %d/%d %s" % [id, "WIN" if result.success else "NOT WON", result.shots,
				screen.engine.definition.recommended_shots, result.blocked])
	DirAccess.remove_absolute(ProjectSettings.globalize_path(CAPTURE_SAVE))
	quit()


func _frames(count: int) -> void:
	for i in count:
		await process_frame


func _shot(out: String, shot_name: String) -> void:
	await RenderingServer.frame_post_draw
	var image := root.get_texture().get_image()
	image.resize(960, 540, Image.INTERPOLATE_BILINEAR)
	image.save_webp(out.path_join(shot_name + ".webp"), true, 0.75)
