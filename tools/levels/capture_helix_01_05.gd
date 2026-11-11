extends SceneTree
## Gameplay evidence for Helix 01-05 through the real app: main menu, chapter and mission select,
## then each mission played with its first recorded solution (tools/levels/solutions.json):
## start frame, after the first shot, and the result panel. Writes WebP to docs/images/helix_01_05/.
## Needs a window (not --headless):
##   godot_console --resolution 1280x720 -s tools/levels/capture_helix_01_05.gd

const OUT_DIR := "res://docs/images/helix_01_05"
const CAPTURE_SAVE := "user://capture_helix_01_05_progress.json"
const MainScript := preload("res://scripts/main.gd")
const Solver := preload("res://tools/levels/mission_solver.gd")
const MISSIONS := ["helix_01", "helix_02", "helix_03", "helix_04", "helix_05"]

var _log: Array[String] = []


func _initialize() -> void:
	_run.call_deferred()


func _run() -> void:
	DirAccess.make_dir_recursive_absolute(ProjectSettings.globalize_path(OUT_DIR))
	if FileAccess.file_exists(CAPTURE_SAVE):
		DirAccess.remove_absolute(ProjectSettings.globalize_path(CAPTURE_SAVE))
	var solutions: Dictionary = JSON.parse_string(FileAccess.get_file_as_string("res://tools/levels/solutions.json"))
	var main: Node = MainScript.new()
	main.save = SaveService.new(CAPTURE_SAVE)
	root.add_child(main)
	await _frames(30)
	await _shot("00_main_menu")
	main._campaign.show_chapters()
	await _frames(10)
	await _shot("01_chapter_select")
	main._campaign.show_missions(1)
	await _frames(10)
	await _shot("02_mission_select_fresh")

	for id: String in MISSIONS:
		main._show_mission(id)
		await _frames(45)
		var screen: MissionScreen = main._mission
		await _shot("%s_a_start" % id)
		var steps: Array = solutions[id][0].steps
		await Solver.play(self, screen.world, steps.slice(0, 1), false)
		await _shot("%s_b_after_first_shot" % id)
		var result: Dictionary = await Solver.play(self, screen.world, steps.slice(1))
		for i in 300:
			if screen.hud.has_overlay():
				break
			await process_frame
		await _frames(30)
		await _shot("%s_c_result" % id)
		_log.append("%s: %s, shots %d, effective %d, mission time %.1fs, saved completed=%s" % [
			id, "WIN" if screen.engine.phase == MissionEngine.Phase.SUCCEEDED else "NOT WON", screen.engine.shots_fired(),
			screen.engine.effective_shots, screen.engine.elapsed, main.progress.is_mission_completed(id)])

	screen_exit(main)
	await _frames(15)
	await _shot("03_mission_select_after_five")
	for line in _log:
		print(line)
	print("Research Data balance: %d" % main.progress.research_data)
	DirAccess.remove_absolute(ProjectSettings.globalize_path(CAPTURE_SAVE))
	quit()


func screen_exit(main: Node) -> void:
	main._mission.exit_requested.emit()


func _frames(count: int) -> void:
	for i in count:
		await process_frame


func _shot(shot_name: String) -> void:
	await RenderingServer.frame_post_draw
	var path := ProjectSettings.globalize_path("%s/%s.webp" % [OUT_DIR, shot_name])
	var err := root.get_texture().get_image().save_webp(path, true, 0.8)
	if err != OK:
		push_error("Could not save %s (error %d)" % [path, err])
	else:
		print("saved ", path)
