extends SceneTree
## Measures, per level, how repeatable the stored solution is and how heavy the physics is.
## Every replay runs alone in a fresh, isolated physics world (one SubViewport), one after another,
## so the timing numbers cover a single level world, as in the real game.
##
##   godot --headless --fixed-fps 60 -s tools/physics_report.gd -- [--replays=N] [--no-warmup] [L03 L07 ...]
##
## Columns: wins / replays, distinct end states (fingerprints of every body's settled position,
## rounded to 1px), peak live body count, and wall time per simulated frame (mean and worst, ms).
## The timing is this machine's CPU, not a phone's: use it to compare levels and spot outliers.

const PRE_LAUNCH_SETTLE_FRAMES := 150
const MAX_FRAMES_PER_SHOT := int(GameConfig.SIMULATION_TIMEOUT * 60.0) + 120
const DEFAULT_REPLAYS := 10


func _initialize() -> void:
	_run.call_deferred()


func _run() -> void:
	var replays := DEFAULT_REPLAYS
	var warmup := true
	var only := []
	for arg in OS.get_cmdline_user_args():
		if arg.begins_with("--replays="):
			replays = maxi(1, int(arg.trim_prefix("--replays=")))
		elif arg == "--no-warmup":
			warmup = false
		elif not arg.begins_with("--"):
			only.append(arg)
	var catalog := LevelCatalog.load_from_file()
	if not catalog.is_valid():
		printerr("catalog invalid: ", catalog.errors)
		quit(1)
		return
	if warmup:
		await PhysicsWarmup.run(self)
	print("level name              wins   end-states  peak-bodies  step-ms(mean/worst)  first-run")
	var total_wins := 0
	var total_runs := 0
	for i in catalog.levels.size():
		var def: LevelDefinition = catalog.levels[i]
		if not only.is_empty() and not only.has(def.id):
			continue
		var wins := 0
		var states := {}
		var peak_bodies := 0
		var step_sum := 0.0
		var step_count := 0
		var step_worst := 0.0
		var first_won := false
		for r in replays:
			var result: Dictionary = await _replay(def)
			if result.won:
				wins += 1
			if r == 0:
				first_won = result.won
			states[result.fingerprint] = true
			peak_bodies = maxi(peak_bodies, result.peak_bodies)
			step_sum += result.step_sum
			step_count += result.step_count
			step_worst = maxf(step_worst, result.step_worst)
		total_wins += wins
		total_runs += replays
		print("%-2d %s %-16s %3d/%-3d %6d %12d %10.3f / %-8.3f %s" % [
			i + 1, def.id, def.name, wins, replays, states.size(), peak_bodies,
			step_sum / maxf(step_count, 1.0), step_worst, "won" if first_won else "LOST"])
	print("\nTotal: %d/%d replays won (%.1f%%)" % [total_wins, total_runs, 100.0 * total_wins / maxf(total_runs, 1.0)])
	quit(0)


func _replay(def: LevelDefinition) -> Dictionary:
	var viewport := SubViewport.new()
	viewport.render_target_update_mode = SubViewport.UPDATE_DISABLED
	root.add_child(viewport)
	var session := GameSession.new()
	viewport.add_child(session)
	session.setup(def)
	for f in PRE_LAUNCH_SETTLE_FRAMES:
		await physics_frame
	var peak := 0
	var step_sum := 0.0
	var step_count := 0
	var step_worst := 0.0
	for velocity in def.solution:
		if not session.can_launch():
			break
		session.launch(velocity)
		var frames := 0
		var last := Time.get_ticks_usec()
		while session.rules.phase == SessionRules.Phase.SIMULATING and frames < MAX_FRAMES_PER_SHOT:
			await physics_frame
			frames += 1
			# Wall time of a whole frame (physics step + scripts); headless with --fixed-fps runs
			# frames back to back, so this is the full CPU cost of one simulated step.
			var now := Time.get_ticks_usec()
			var ms := (now - last) / 1000.0
			last = now
			step_sum += ms
			step_count += 1
			step_worst = maxf(step_worst, ms)
			peak = maxi(peak, _body_count(session))
	var won := session.rules.phase == SessionRules.Phase.WON and session.rules.shots_used <= def.par
	var fingerprint := _fingerprint(session)
	root.remove_child(viewport)
	viewport.queue_free()
	await process_frame
	return {"won": won, "fingerprint": fingerprint, "peak_bodies": peak,
		"step_sum": step_sum, "step_count": step_count, "step_worst": step_worst}


func _body_count(session: GameSession) -> int:
	var count := 0
	for node in session.get_child(0).get_children():
		if node is RigidBody2D:
			count += 1
	return count


func _fingerprint(session: GameSession) -> String:
	var parts := PackedStringArray()
	for node in session.get_child(0).get_children():
		if node is RigidBody2D and not node.is_queued_for_deletion():
			parts.append("%d,%d" % [roundi(node.global_position.x), roundi(node.global_position.y)])
	return ";".join(parts)
