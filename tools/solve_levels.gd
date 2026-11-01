extends SceneTree
## Level design tool: searches launch velocities that solve each level within par, using the real
## GameSession in parallel isolated physics worlds (one SubViewport per candidate shot).
##
##   godot --headless --fixed-fps 60 -s tools/solve_levels.gd -- [--write] [--stability] [L03 L07 ...]
##
## Reports, per level, the share of single-shot candidates that win (a rough difficulty signal).
## With --write, verified solutions are stored back into data/levels.json.
## Search is greedy per shot; it prefers the centre of a winning region so the stored shot
## is not a pixel-perfect fluke. Results must still be confirmed by tests/test_level_playthrough.gd.

const ANGLE_MIN := -20.0
const ANGLE_MAX := 75.0
const ANGLE_STEP := 2.5
const POWER_MIN := 0.40
const POWER_MAX := 1.0
const POWER_STEP := 0.05
const BATCH_SIZE := 80
const MAX_FRAMES_PER_BATCH := 60 * 60


func _initialize() -> void:
	_run.call_deferred()


func _run() -> void:
	var args := OS.get_cmdline_user_args()
	var write := args.has("--write")
	var only: Array = Array(args).filter(func(a: String) -> bool: return not a.begins_with("--"))
	var catalog := LevelCatalog.load_from_file()
	if not catalog.is_valid():
		printerr("catalog invalid: ", catalog.errors)
		quit(1)
		return
	var solutions := {}
	var unsolved := []
	for def in catalog.levels:
		if not only.is_empty() and not only.has(def.id):
			continue
		var start := Time.get_ticks_msec()
		var result: Dictionary = await _solve(def)
		print("%s %-16s won=%s shots=%d single-shot win rate=%.1f%%  (%.1fs)" % [
			def.id, def.name, result.won, result.shots.size(), result.single_rate * 100.0,
			(Time.get_ticks_msec() - start) / 1000.0])
		if result.won:
			solutions[def.id] = result.shots
		else:
			unsolved.append(def.id)
	if not unsolved.is_empty():
		print("UNSOLVED within par: ", unsolved)
	if write:
		_write_solutions(solutions)
	quit(0)


func _candidates() -> Array[Vector2]:
	var list: Array[Vector2] = []
	var angle := ANGLE_MIN
	while angle <= ANGLE_MAX + 0.001:
		var power := POWER_MIN
		while power <= POWER_MAX + 0.001:
			# Launch toward +x; positive angle aims upward (negative screen y).
			var v := Vector2.RIGHT.rotated(-deg_to_rad(angle)) * GameConfig.MAX_LAUNCH_SPEED * power
			list.append(Vector2(roundf(v.x), roundf(v.y)))
			power += POWER_STEP
		angle += ANGLE_STEP
	return list


func _solve(def: LevelDefinition) -> Dictionary:
	var candidates := _candidates()
	var prefix: Array[Vector2] = []
	var single_rate := 0.0
	for shot_index in def.par:
		var outcomes: Array = await _evaluate(def, prefix, candidates)
		var wins := outcomes.filter(func(o: Dictionary) -> bool: return o.won).size()
		if shot_index == 0:
			single_rate = float(wins) / candidates.size()
		var best := _pick(outcomes, def)
		prefix.append(candidates[best])
		if outcomes[best].won:
			return {"won": true, "shots": prefix, "single_rate": single_rate}
	return {"won": false, "shots": prefix, "single_rate": single_rate}


## Picks the winning candidate with the most winning grid neighbours, else the best partial result.
func _pick(outcomes: Array, def: LevelDefinition) -> int:
	var powers := int(roundf((POWER_MAX - POWER_MIN) / POWER_STEP)) + 1
	var best := 0
	var best_score := -INF
	for i in outcomes.size():
		var o: Dictionary = outcomes[i]
		var neighbours := 0
		for d: int in [-1, 1, -powers, powers, -powers - 1, -powers + 1, powers - 1, powers + 1]:
			var j: int = i + d
			if j >= 0 and j < outcomes.size() and outcomes[j].won == o.won and _progress(outcomes[j], def) >= _progress(o, def):
				neighbours += 1
		var score := (1000.0 if o.won else 0.0) + _progress(o, def) * 10.0 + neighbours
		if score > best_score:
			best_score = score
			best = i
	return best


func _progress(o: Dictionary, def: LevelDefinition) -> float:
	if def.objective_type == LevelDefinition.OBJECTIVE_TOPPLE:
		return clampf((o.highest_top - 300.0) / 300.0, 0.0, 1.0) * 10.0
	return float(def.targets.size() - o.targets_remaining) * 10.0


func _evaluate(def: LevelDefinition, prefix: Array[Vector2], candidates: Array[Vector2]) -> Array:
	var outcomes := []
	var i := 0
	while i < candidates.size():
		var batch := candidates.slice(i, mini(i + BATCH_SIZE, candidates.size()))
		outcomes.append_array(await _run_batch(def, prefix, batch))
		i += BATCH_SIZE
	return outcomes


func _run_batch(def: LevelDefinition, prefix: Array[Vector2], batch: Array) -> Array:
	var runs := []
	for velocity: Vector2 in batch:
		var viewport := SubViewport.new()
		viewport.render_target_update_mode = SubViewport.UPDATE_DISABLED
		viewport.size = Vector2i(2, 2)
		root.add_child(viewport)
		var session := GameSession.new()
		viewport.add_child(session)
		session.setup(def)
		var shots: Array[Vector2] = prefix.duplicate()
		shots.append(velocity)
		runs.append({"viewport": viewport, "session": session, "shots": shots, "next": 0})
	# Let every world settle one frame before launching, as the game does.
	await physics_frame
	var frames := 0
	while frames < MAX_FRAMES_PER_BATCH:
		var all_done := true
		for run: Dictionary in runs:
			var session: GameSession = run.session
			if session.rules.is_finished():
				continue
			if session.can_launch():
				if run.next < run.shots.size():
					session.launch(run.shots[run.next])
					run.next += 1
				else:
					continue
			all_done = false
		if all_done:
			break
		await physics_frame
		frames += 1
	var outcomes := []
	for run: Dictionary in runs:
		var session: GameSession = run.session
		outcomes.append({
			"won": session.rules.phase == SessionRules.Phase.WON,
			"targets_remaining": session.targets_remaining,
			"highest_top": session.highest_block_top(),
		})
		run.viewport.queue_free()
	await process_frame
	return outcomes


func _write_solutions(solutions: Dictionary) -> void:
	var path := LevelCatalog.DEFAULT_PATH
	var text := FileAccess.get_file_as_string(path)
	var data: Dictionary = JSON.parse_string(text)
	for level: Dictionary in data.levels:
		if solutions.has(level.id):
			var list := []
			for v: Vector2 in solutions[level.id]:
				list.append([int(v.x), int(v.y)])
			level.solution = list
	var file := FileAccess.open(path, FileAccess.WRITE)
	if file == null:
		printerr("cannot write ", path)
		return
	file.store_string(_format_catalog(data))
	print("wrote solutions for ", solutions.keys())


## Compact, diff-friendly layout: one entity per line.
func _format_catalog(data: Dictionary) -> String:
	var out := "{\n\"levels\": [\n"
	var levels: Array = data.levels
	for li in levels.size():
		var l: Dictionary = levels[li]
		out += "{\n"
		out += "\t\"id\": %s, \"name\": %s, \"shots\": %s, \"par\": %s,\n" % [_j(l.id), _j(l.name), _j(l.shots), _j(l.par)]
		out += "\t\"hint\": %s,\n" % _j(l.get("hint", ""))
		out += "\t\"launcher\": %s,\n" % _j(l.launcher)
		out += "\t\"objective\": %s,\n" % _j(l.objective)
		for key in ["statics", "blocks", "targets", "solution"]:
			var items: Array = l.get(key, [])
			if items.is_empty():
				out += "\t\"%s\": []" % key
			else:
				var lines := PackedStringArray()
				for item: Variant in items:
					lines.append("\t\t" + _j(item))
				out += "\t\"%s\": [\n%s\n\t]" % [key, ",\n".join(lines)]
			out += ",\n" if key != "solution" else "\n"
		out += "}" + (",\n" if li < levels.size() - 1 else "\n")
	return out + "]\n}\n"


## JSON with whole numbers printed as integers and keys kept in a stable, readable order.
func _j(value: Variant) -> String:
	if value is float:
		return str(int(value)) if value == floorf(value) else str(value)
	if value is int:
		return str(value)
	if value is String:
		return JSON.stringify(value)
	if value is Array:
		var parts := PackedStringArray()
		for v: Variant in value:
			parts.append(_j(v))
		return "[" + ", ".join(parts) + "]"
	if value is Dictionary:
		var order := ["type", "line_y", "x", "y", "w", "h", "r", "rot", "material"]
		var keys: Array = value.keys()
		keys.sort_custom(func(a: String, b: String) -> bool:
			var ia := order.find(a)
			var ib := order.find(b)
			return (ia if ia >= 0 else 99) < (ib if ib >= 0 else 99))
		var parts := PackedStringArray()
		for k: String in keys:
			parts.append("%s: %s" % [JSON.stringify(k), _j(value[k])])
		return "{" + ", ".join(parts) + "}"
	return JSON.stringify(value)
