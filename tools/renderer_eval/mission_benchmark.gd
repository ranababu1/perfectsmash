extends "res://tools/renderer_eval/benchmark.gd"
## Renderer evaluation on the actual 3D gameplay scene (Batch 5). Boots the real app root into
## the Helix mission (MissionScreen: 3D view over the 2D physics) and measures scripted play:
## idle, aiming with the arc preview, a kinetic collapse and finish, breach blasts with a power
## cell chain, and repeated mission restarts. No proxies. Reuses the frame-time, memory and
## report code of benchmark.gd; reports go to user://renderer_eval/ as "mission_<variant>_*.json".
##
## Desktop:  godot_console --rendering-method mobile --fixed-fps 0 tools/renderer_eval/mission_benchmark.tscn
## Android:  python tools/renderer_eval/make_eval_project.py --variant mobile --main res://tools/renderer_eval/mission_benchmark.tscn --out ../temporal-eval-mobile

const ProbeAim := preload("res://tools/regression/probe_aim.gd")
const RESTARTS := 8
## Frames slower than this are logged as RENDER_EVAL_SPIKE with the gameplay events of the
## preceding frames, to find what caused them.
const SPIKE_MS := 100.0

var _events: Array[String] = []
var _spike_last_usec := 0
var _watched: Object


func _run() -> void:
	await get_tree().process_frame
	_config["variant"] = "mission_" + str(_config.get("variant", "unspecified"))
	_report["startup_ms_to_first_frame"] = Time.get_ticks_msec()
	_report["environment"] = _environment()
	_report["environment"]["benchmark"] = "mission_benchmark (real Helix 3D gameplay scene)"
	print("RENDER_EVAL_ENV ", JSON.stringify(_report.environment))

	_main = _make_main()
	var boot_start := Time.get_ticks_usec()
	add_child(_main)
	await get_tree().process_frame
	_report["mission_boot_ms"] = snappedf((Time.get_ticks_usec() - boot_start) / 1000.0, 0.01)
	await _wait(1.0)
	await _scenario("mission_idle", 6.0, "real")

	_drive_aim(6.0)
	await _scenario("mission_aiming_preview", 6.0, "real")

	_drive_kinetic_collapse()
	await _scenario("mission_kinetic_collapse_finish", 10.0, "real")

	await _restart()
	_drive_breach_chain()
	await _scenario("mission_breach_blasts_chain", 10.0, "real")

	_report["restart_ms"] = await _measure_restarts()

	var soak_minutes := float(_config.get("soak_minutes", 0.0))
	if soak_minutes > 0.0:
		await _mission_soak(soak_minutes)

	_report["scenarios"] = _results
	_report["focus_lost_during_run"] = _focus_lost
	_report["memory"] = _memory()
	_write_report()
	get_tree().quit()


func _screen() -> MissionScreen:
	var screen: MissionScreen = _main._mission
	if screen != null and screen != _watched:
		_watch(screen)
	return screen


## Records gameplay events (with the frame they happened in) for the spike log.
func _watch(screen: MissionScreen) -> void:
	_watched = screen
	screen.world.blast_happened.connect(func(_c: Vector2, _r: float) -> void: _event("blast"))
	screen.world.projectile_spawned.connect(func(p: WeaponProjectile) -> void: _event("spawn " + p.weapon_id))
	screen.world.component_removed.connect(func(id: String, _at: Vector2) -> void: _event("removed " + id))
	screen.world.impact_happened.connect(func(_a: Vector2, s: float, id: String) -> void: _event("impact %s %.0f" % [id, s]))
	screen.engine.component_state_changed.connect(func(id: String, _p: int, c: int) -> void: _event("state %s %d" % [id, c]))


func _event(text: String) -> void:
	_events.append("f%d %s" % [Engine.get_process_frames(), text])
	if _events.size() > 12:
		_events.pop_front()


func _process(delta: float) -> void:
	super(delta)
	var now := Time.get_ticks_usec()
	if _spike_last_usec > 0 and (now - _spike_last_usec) / 1000.0 > SPIKE_MS:
		print("RENDER_EVAL_SPIKE %.1f ms at f%d after %s" % [(now - _spike_last_usec) / 1000.0, Engine.get_process_frames(), str(_events.slice(-6))])
	_spike_last_usec = now


func _restart() -> void:
	_screen().restart_requested.emit()
	_event("restart")
	await get_tree().process_frame
	await _wait(0.5)


## Touch-and-hold aiming that sweeps the aim point, so the trajectory preview updates every frame.
func _drive_aim(seconds: float) -> void:
	var screen := _screen()
	var muzzle := screen.world.muzzle_position()
	screen.begin_aim(screen.view.plane_to_screen(muzzle + Vector2(500, -60)))
	var elapsed := 0.0
	while elapsed < seconds and is_instance_valid(screen):
		var swing := sin(elapsed * 1.7)
		screen.update_aim(screen.view.plane_to_screen(muzzle + Vector2(520 + 120 * swing, -90 + 70 * cos(elapsed * 1.3))))
		await get_tree().process_frame
		elapsed += get_process_delta_time()
	if is_instance_valid(screen):
		screen.update_aim(screen.view.plane_to_screen(muzzle + Vector2(10, 0)))
		screen.release_aim()


## The kinetic route: two rounds into the left column, then a finishing round at the exposed core.
func _drive_kinetic_collapse() -> void:
	var screen := _screen()
	var world := screen.world
	var engine := screen.engine
	engine.select_weapon("kinetic_accelerator")
	for i in 2:
		while not engine.can_fire():
			await get_tree().physics_frame
		world.fire(Vector2(826, 512) - world.muzzle_position())
		await _wait(1.2)
	await _wait(2.5)
	var core := world.body_for("aura_core")
	if core != null and engine.is_active():
		while not engine.can_fire():
			await get_tree().physics_frame
		# The aim search is the benchmark driver's own work (many shape casts in one frame), not
		# gameplay: restart the frame clocks after it so it is not measured as a game hitch.
		var plan: Dictionary = ProbeAim.aim(world, core)
		_last_usec = Time.get_ticks_usec()
		_spike_last_usec = _last_usec
		_event("driver aim search (excluded)")
		world.fire(plan.direction if plan.direction != Vector2.ZERO else core.global_position - world.muzzle_position())


## Breach blasts: the rack cluster, the deck by the power cell (chain reaction), then the core.
func _drive_breach_chain() -> void:
	var screen := _screen()
	var world := screen.world
	var stats: Dictionary = screen.engine.weapons.breach_charge.stats
	world.spawn_projectile("breach_charge", stats, Vector2(674, 480), Vector2(0, 300))
	await _wait(1.5)
	world.spawn_projectile("breach_charge", stats, Vector2(955, 330), Vector2(0, 150))
	await _wait(2.0)
	world.spawn_projectile("breach_charge", stats, Vector2(885, 300), Vector2(0, 200))


func _measure_restarts() -> Array:
	var times := []
	for i in RESTARTS:
		var start := Time.get_ticks_usec()
		_screen().restart_requested.emit()
		_event("restart")
		await get_tree().process_frame
		times.append(snappedf((Time.get_ticks_usec() - start) / 1000.0, 0.01))
		await _wait(0.3)
	print("RENDER_EVAL_RESTARTS ", JSON.stringify(times))
	return times


func _mission_soak(minutes: float) -> void:
	var end := Time.get_ticks_msec() + int(minutes * 60000.0)
	var memory_start := OS.get_static_memory_usage()
	var cycles := 0
	_frame_ms = PackedFloat32Array()
	_last_usec = 0
	_recording = true
	while Time.get_ticks_msec() < end:
		await _restart()
		_drive_breach_chain()
		await _wait(6.0)
		cycles += 1
	_recording = false
	var result := _summarise("mission_soak", "real", minutes * 60.0)
	result["cycles"] = cycles
	result["static_memory_growth_mb"] = snappedf((OS.get_static_memory_usage() - memory_start) / 1048576.0, 0.1)
	_results.append(result)
	print("RENDER_EVAL_SCENARIO ", JSON.stringify(result))
