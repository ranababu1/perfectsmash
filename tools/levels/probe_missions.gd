extends SceneTree
## Level design probe (headless). Run from the project root:
##   godot_console --headless --fixed-fps 60 -s tools/levels/probe_missions.gd -- scout helix_02
##   godot_console --headless --fixed-fps 60 -s tools/levels/probe_missions.gd -- solve helix_02 [replays]
##   godot_console --headless --fixed-fps 60 -s tools/levels/probe_missions.gd -- solve all [replays]
##   godot_console --headless --fixed-fps 60 -s tools/levels/probe_missions.gd -- solve vita [replays]   (a whole chapter)
## scout: for every component, whether the Kinetic Accelerator has a clear line and whether a
##        Breach lob can make first contact with it (nothing is fired).
## solve: stand check (180 frames untouched), then plays each recorded solution in
##        tools/levels/solutions/<id>.json `replays` times and prints success, shots, time.
## Exit code 1 when a stand check fails or a solution wins fewer than ceil(2/3) of its replays.

const Solver := preload("res://tools/levels/mission_solver.gd")
const SolutionBook := preload("res://tools/levels/solution_book.gd")


func _initialize() -> void:
	_run.call_deferred()


func _run() -> void:
	var args := OS.get_cmdline_user_args()
	var mode := args[0] if args.size() > 0 else "solve"
	var which := args[1] if args.size() > 1 else "all"
	var replays := int(args[2]) if args.size() > 2 else 3
	var solutions: Dictionary = SolutionBook.load_all()
	# "all", one mission id, or a chapter theme prefix such as "vita" (vita_01..vita_20).
	var ids: Array = solutions.keys() if which == "all" else solutions.keys().filter(func(k: String) -> bool: return k.begins_with(which + "_"))
	if which != "all" and ids.is_empty():
		ids = [which]
	ids.sort()
	var failed := false
	for id: String in ids:
		var path := "res://data/missions/%s.json" % id
		if mode == "scout":
			await _scout(path)
		else:
			failed = not await _solve(id, path, solutions.get(id, []), replays) or failed
	quit(1 if failed else 0)


func _scout(path: String) -> void:
	var made: Dictionary = Solver.make_world(self, path)
	if made.has("error"):
		print("INVALID ", made.error)
		return
	var world: MissionWorld = made.world
	await physics_frame
	print("== scout %s (muzzle %s)" % [path.get_file(), world.muzzle_position()])
	for id: String in world.bodies:
		var line := "  %-14s" % id
		for weapon_id: String in world.engine.weapon_order:
			world.engine.select_weapon(weapon_id)
			var plan: Dictionary = Solver.aim(world, {"weapon": weapon_id, "target": id})
			line += "  %s: %s" % [weapon_id.left(6), "clear" if plan.direction != Vector2.ZERO else "blocked by " + str(plan.blocker)]
		print(line)
	Solver.free_world(self, made)


func _solve(id: String, path: String, plans: Array, replays: int) -> bool:
	var ok := true
	var made: Dictionary = Solver.make_world(self, path)
	if made.has("error"):
		print("INVALID %s: %s" % [id, made.error])
		return false
	var problems: Array[String] = await Solver.stand_check(self, made.world)
	print("== %s stand check: %s" % [id, "OK" if problems.is_empty() else "FAILED " + str(problems)])
	ok = problems.is_empty()
	var recommended: int = made.world.definition.recommended_shots
	var target_time: float = made.world.definition.target_time
	Solver.free_world(self, made)
	for i in plans.size():
		var plan: Dictionary = plans[i]
		var wins := 0
		for r in replays:
			made = Solver.make_world(self, path)
			await physics_frame
			var result: Dictionary = await Solver.play(self, made.world, plan.steps)
			Solver.free_world(self, made)
			await process_frame
			if result.success:
				wins += 1
			print("  %s #%d replay %d: %s shots %d (recommended %d) effective %d time %.1fs (target %.0fs)%s" % [
				plan.get("name", "solution"), i, r, "WIN" if result.success else "FAIL", result.shots, recommended,
				result.effective, result.elapsed, target_time, ("  blocked: " + result.blocked) if not result.blocked.is_empty() else ""])
			for line: String in result.log:
				print("      " + line)
		if plan.get("expect", "win") == "win" and wins * 3 < replays * 2:
			ok = false
	return ok
