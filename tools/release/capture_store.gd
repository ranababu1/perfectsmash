extends SceneTree
## Store screenshots, taken through the real app (windowed, 1920x1080, full resolution PNG):
##   godot_console --resolution 1920x1080 --fixed-fps 60 -s tools/release/capture_store.gd -- <out dir> [scout]
## Writes menu/screen shots, one cinematic frame, and for each chapter finale an opening frame and
## a mid-destruction frame (a moment after a shot of its first recorded solution,
## tools/levels/solutions/<id>.json). With `scout` it instead dumps every shot of the five finales
## at several delays, to choose the MOMENTS below. Uses a throwaway save under user:// and deletes it.

const MainScript := preload("res://scripts/main.gd")
const Solver := preload("res://tools/levels/mission_solver.gd")
const SolutionBook := preload("res://tools/levels/solution_book.gd")
const CAPTURE_SAVE := "user://capture_store_progress.json"

## mission id -> [shot index (0-based) in the first solution, frames after firing to capture].
const MOMENTS := {
	"helix_20": [2, 30],
	"vita_20": [2, 30],
	"nova_grid_20": [3, 30],
	"civitas_20": [1, 30],
	"meridian_20": [1, 30],
}
const SEEN := ["opening", "ch01_intro", "ch01_outro", "ch02_intro", "ch02_outro", "ch03_intro"]

var _out := ""


func _initialize() -> void:
	_run.call_deferred()


func _run() -> void:
	var args := OS.get_cmdline_user_args()
	_out = args[0] if args.size() > 0 else ProjectSettings.globalize_path("res://docs/store/screenshots")
	var scout := args.size() > 1 and args[1] == "scout"
	DirAccess.make_dir_recursive_absolute(_out)
	# A decorated window is clamped to the usable screen height (not 16:9): go borderless at the origin.
	DisplayServer.window_set_flag(DisplayServer.WINDOW_FLAG_BORDERLESS, true)
	DisplayServer.window_set_size(Vector2i(1920, 1080))
	DisplayServer.window_set_position(Vector2i(0, 0))
	await _frames(5)
	root.gui_disable_input = true
	root.set_disable_input(true)
	var solutions := SolutionBook.load_all()
	var main: Node = MainScript.new()
	main.cinematics_enabled = false
	main.save = SaveService.new(CAPTURE_SAVE)
	root.add_child(main)
	await _frames(10)
	_seed_progress(main)
	if scout:
		for id in MOMENTS:
			await _scout(main, id, solutions.get(id, []))
		_finish()
		return
	main._show_campaign()
	await _frames(50)
	await _shot("01_main_menu")
	main._campaign.show_chapters()
	await _frames(40)
	await _shot("02_chapter_select")
	main._show_campaign(2)
	await _frames(40)
	await _shot("03_mission_select")
	main._show_upgrades()
	await _frames(50)
	await _shot("04_upgrades")
	main._show_archive()
	await _frames(50)
	await _shot("05_story_archive")
	main._show_cinematic("ch01_intro", main._show_campaign)
	await _frames(240)
	await _shot("06_cinematic")
	var n := 7
	for id in MOMENTS:
		main._show_mission(id)
		await _frames(60)
		await _shot("%02d_%s_a_start" % [n, id])
		var plans: Array = solutions.get(id, [])
		if not plans.is_empty():
			var m: Array = MOMENTS[id]
			await _play_to(main._mission.world, plans[0].steps, m[0])
			await _fire_step(main._mission.world, plans[0].steps[m[0]])
			await _frames(m[1])
			await _shot("%02d_%s_b_destruction" % [n, id])
		n += 1
	_finish()


func _finish() -> void:
	DirAccess.remove_absolute(ProjectSettings.globalize_path(CAPTURE_SAVE))
	quit()


## A believable mid-campaign save: Helix complete, VITA partly, some Research Data, a few stories seen.
func _seed_progress(main: Node) -> void:
	var p: ProgressData = main.progress
	var ids: Array[String] = []
	for s in main.missions.authored():
		ids.append(s.id)
	var n := 0
	for id in ids:
		if n >= 26:
			break
		var score := {"success": true, "mission_points": 2400 + (n % 5) * 310, "research_data": 30 + (n % 4) * 8}
		p.record_mission(id, score, 3 + n % 3, 40.0 + n, [])
		n += 1
	p.research_data = 320
	for seq in SEEN:
		p.mark_sequence_seen(seq)


func _play_to(world: MissionWorld, steps: Array, count: int) -> void:
	for i in count:
		await _fire_step(world, steps[i])
		await Solver._until(self, func() -> bool: return world.projectiles.is_empty() and world.is_settled() or not world.engine.is_active(), 12.0)


func _fire_step(world: MissionWorld, step: Dictionary) -> bool:
	var engine := world.engine
	await physics_frame
	if step.has("target") and (world.body_for(step.target) == null \
			or engine.component_state(step.target) == DamageableComponent.State.DESTROYED):
		return false
	engine.select_weapon(step.weapon)
	await Solver._until(self, func() -> bool: return engine.can_fire() or not engine.is_active(), 5.0)
	var plan := Solver.aim(world, step)
	if plan.direction == Vector2.ZERO:
		return false
	world.fire(plan.direction, plan.power)
	return true


func _scout(main: Node, id: String, plans: Array) -> void:
	main._show_mission(id)
	await _frames(40)
	if plans.is_empty():
		return
	var steps: Array = plans[0].steps
	var world: MissionWorld = main._mission.world
	for i in mini(steps.size(), 6):
		if not await _fire_step(world, steps[i]):
			continue
		var waited := 0
		for d in [15, 30, 50]:
			await _frames(d - waited)
			waited = d
			await _shot("scout_%s_s%d_f%d" % [id, i, d], true)
		await Solver._until(self, func() -> bool: return world.projectiles.is_empty() and world.is_settled() or not world.engine.is_active(), 12.0)
		if not world.engine.is_active():
			break


func _frames(count: int) -> void:
	for i in count:
		await process_frame


func _shot(shot_name: String, small: bool = false) -> void:
	await RenderingServer.frame_post_draw
	var image := root.get_texture().get_image()
	if small:
		image.resize(960, 540, Image.INTERPOLATE_BILINEAR)
	image.save_png(_out.path_join(shot_name + ".png"))
