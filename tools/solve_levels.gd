extends SceneTree
## Level design tool: searches launch velocities that solve each level within par, using the real
## GameSession in parallel isolated physics worlds (one SubViewport per candidate shot).
##
##   godot --headless --fixed-fps 60 -s tools/solve_levels.gd -- [--write] [--out=FILE] [L03 L07 ...]
##
## --out=FILE writes {"solved": {id: [[vx, vy], ...]}, "unsolved": [ids], "rates": {id: rate}} instead of touching
## levels.json, so several solver processes can run in parallel on disjoint level sets
## (tools/build_campaign.gd --merge=FILE folds the results back in).
##
## Reports, per level, the share of single-shot candidates that win (a rough difficulty signal).
## With --write, verified solutions are stored back into data/levels.json.
## Search is greedy per shot; it prefers the centre of a winning region so the stored shot
## is not a pixel-perfect fluke. Results must still be confirmed by tests/test_level_playthrough.gd.

const CatalogFormat := preload("res://tools/catalog_format.gd")
const ANGLE_MIN := -20.0
const ANGLE_MAX := 75.0
const ANGLE_STEP := 2.5
const POWER_MIN := 0.40
const POWER_MAX := 1.0
const POWER_STEP := 0.05
const BATCH_SIZE := 80
const MAX_FRAMES_PER_BATCH := 60 * 60
## The playthrough test uses a different wait, so a stored solution must not depend on exact timing.
const PRE_LAUNCH_SETTLE_FRAMES := 90
const ROBUST_CANDIDATES := 16
## (power scale, angle offset in radians) applied to a winning shot; all must still win.
const PERTURBATIONS: Array[Vector2] = [
	Vector2(1.0, 0.0), Vector2(0.99, 0.0), Vector2(1.01, 0.0), Vector2(1.0, 0.01), Vector2(1.0, -0.01),
]


func _initialize() -> void:
	_run.call_deferred()


func _run() -> void:
	var args := OS.get_cmdline_user_args()
	var write := args.has("--write")
	var out_path := ""
	for a in args:
		if a.begins_with("--out="):
			out_path = a.trim_prefix("--out=")
	var only: Array = Array(args).filter(func(a: String) -> bool: return not a.begins_with("--"))
	var catalog := LevelCatalog.load_from_file()
	if not catalog.is_valid():
		printerr("catalog invalid: ", catalog.errors)
		quit(1)
		return
	var solutions := {}
	var unsolved := []
	var rates := {}
	for def in catalog.levels:
		if not only.is_empty() and not only.has(def.id):
			continue
		var start := Time.get_ticks_msec()
		var result: Dictionary = await _solve(def)
		print("%s %-16s won=%s fragile=%s shots=%d single-shot win rate=%.1f%%  (%.1fs)" % [
			def.id, def.name, result.won, result.fragile, result.shots.size(), result.single_rate * 100.0,
			(Time.get_ticks_msec() - start) / 1000.0])
		rates[def.id] = snappedf(result.single_rate, 0.001)
		if result.won:
			solutions[def.id] = result.shots
		else:
			unsolved.append(def.id)
	if not unsolved.is_empty():
		print("UNSOLVED within par: ", unsolved)
	if write:
		_write_solutions(solutions)
	if out_path != "":
		var solved := {}
		for id: String in solutions:
			solved[id] = solutions[id].map(func(v: Vector2) -> Array: return [int(v.x), int(v.y)])
		var file := FileAccess.open(out_path, FileAccess.WRITE)
		file.store_string(JSON.stringify({"solved": solved, "unsolved": unsolved, "rates": rates}, "\t"))
		file.close()
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
	await PhysicsWarmup.run(self)
	var candidates := _candidates()
	var prefix: Array[Vector2] = []
	var single_rate := 0.0
	for shot_index in def.par:
		var outcomes: Array = await _evaluate(def, prefix, candidates)
		var wins := outcomes.filter(func(o: Dictionary) -> bool: return o.won).size()
		if shot_index == 0:
			single_rate = float(wins) / candidates.size()
		var ranked := _rank(outcomes, def)
		var last_shot: bool = shot_index == def.par - 1
		if outcomes[ranked[0]].won:
			var winners: Array = ranked.filter(func(i: int) -> bool: return outcomes[i].won).slice(0, ROBUST_CANDIDATES)
			var robust: int = await _first_robust(def, prefix, winners.map(func(i: int) -> Vector2: return candidates[i]))
			if robust >= 0 or last_shot:
				prefix.append(candidates[winners[maxi(robust, 0)]])
				return {"won": true, "fragile": robust < 0, "shots": prefix, "single_rate": single_rate}
		# No robust win yet: keep the best non-winning shot (a winning one would end the level)
		# and look for a robust finish with the next shot.
		var setup_shot: int = ranked.filter(func(i: int) -> bool: return not outcomes[i].won)[0]
		prefix.append(candidates[setup_shot])
	return {"won": false, "fragile": false, "shots": prefix, "single_rate": single_rate}


## Index of the first shot that still wins under every small aim perturbation, or -1.
## Guards against storing a lucky shot that only wins with bit-exact physics.
func _first_robust(def: LevelDefinition, prefix: Array[Vector2], shots: Array) -> int:
	var variants: Array[Vector2] = []
	for v: Vector2 in shots:
		for p: Vector2 in PERTURBATIONS:
			variants.append((v * p.x).rotated(p.y))
	var outcomes: Array = await _evaluate(def, prefix, variants)
	for i in shots.size():
		var all_won := true
		for k in PERTURBATIONS.size():
			all_won = all_won and outcomes[i * PERTURBATIONS.size() + k].won
		if all_won:
			return i
	return -1


## Candidate indices, best first: winners with the most winning grid neighbours, then best partial results.
func _rank(outcomes: Array, def: LevelDefinition) -> Array:
	var powers := int(roundf((POWER_MAX - POWER_MIN) / POWER_STEP)) + 1
	var scores := []
	for i in outcomes.size():
		var o: Dictionary = outcomes[i]
		var neighbours := 0
		for d: int in [-1, 1, -powers, powers, -powers - 1, -powers + 1, powers - 1, powers + 1]:
			var j: int = i + d
			if j >= 0 and j < outcomes.size() and outcomes[j].won == o.won and _progress(outcomes[j], def) >= _progress(o, def):
				neighbours += 1
		scores.append((1000.0 if o.won else 0.0) + _progress(o, def) * 10.0 + neighbours)
	var order := range(outcomes.size())
	order.sort_custom(func(a: int, b: int) -> bool: return scores[a] > scores[b])
	return order


func _progress(o: Dictionary, def: LevelDefinition) -> float:
	# A shot that loses an ally or the cargo can never lead to a win.
	if o.failed:
		return -100.0
	if def.objective_type == LevelDefinition.OBJECTIVE_TOPPLE:
		return clampf((o.highest_top - 300.0) / 300.0, 0.0, 1.0) * 10.0
	if def.objective_type == LevelDefinition.OBJECTIVE_DELIVER:
		return clampf(1.0 - o.cargo_distance / 800.0, 0.0, 1.0) * 10.0
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
	# Let structures come to rest (bodies sleep) before the first shot, as they do before a
	# player can aim. Outcomes from a settled state are reproducible; from a fresh load they are not.
	for i in PRE_LAUNCH_SETTLE_FRAMES:
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
			"failed": session.allies_lost > 0 or session.cargo_lost > 0,
			"targets_remaining": session.targets_remaining,
			"highest_top": session.highest_block_top(),
			"cargo_distance": session.cargo_distance_to_zone(),
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
	file.store_string(CatalogFormat.format_catalog(data))
	print("wrote solutions for ", solutions.keys())
