extends SceneTree
## Frame-time sweep over authored missions, in a real window at real time (desktop only — not a
## substitute for device benchmarks): each mission loads, its intended solution plays, and the
## frame deltas are recorded. Reports load time, median / p95 / p99 / worst frame and the frames over
## 33 ms per mission, plus the worst missions.
##   godot_console --resolution 1280x720 -s tools/perf/campaign_frame_times.gd -- [prefix|all] [report.json]

const MainScript := preload("res://scripts/main.gd")
const Solver := preload("res://tools/levels/mission_solver.gd")
const SolutionBook := preload("res://tools/levels/solution_book.gd")
const SAVE := "user://perf_sweep_progress.json"

var _deltas: Array[float] = []
var _recording := false
var _last := 0


func _initialize() -> void:
	_run.call_deferred()


func _process(_delta: float) -> bool:
	var now := Time.get_ticks_usec()
	if _recording and _last > 0:
		_deltas.append((now - _last) / 1000.0)
	_last = now
	return false


func _run() -> void:
	var args := OS.get_cmdline_user_args()
	var which := args[0] if args.size() > 0 else "all"
	var out := args[1] if args.size() > 1 else ProjectSettings.globalize_path("res://tests/output/perf_sweep.json")
	root.gui_disable_input = true
	root.set_disable_input(true)
	var solutions := SolutionBook.load_all()
	var main: Node = MainScript.new()
	main.cinematics_enabled = false
	main.save = SaveService.new(SAVE)
	root.add_child(main)
	await _frames(20)
	var report := []
	for s in MissionCatalog.load_default().authored():
		if which != "all" and s.id != which and not s.id.begins_with(which + "_"):
			continue
		var start := Time.get_ticks_usec()
		main._show_mission(s.id)
		await process_frame
		var load_ms := (Time.get_ticks_usec() - start) / 1000.0
		await _frames(30)
		_deltas.clear()
		_recording = true
		var screen: MissionScreen = main._mission
		var plans: Array = solutions.get(s.id, [])
		if not plans.is_empty():
			await Solver.play(self, screen.world, plans[0].steps)
		await _frames(60)
		_recording = false
		var sorted := _deltas.duplicate()
		sorted.sort()
		var row := {
			"id": s.id, "load_ms": snappedf(load_ms, 0.1), "frames": sorted.size(),
			"median_ms": _pct(sorted, 0.5), "p95_ms": _pct(sorted, 0.95), "p99_ms": _pct(sorted, 0.99),
			"worst_ms": snappedf(sorted.back() if not sorted.is_empty() else 0.0, 0.1),
			"over_33ms": sorted.filter(func(d: float) -> bool: return d > 33.3).size(),
		}
		report.append(row)
		print("%s load %.0f ms, median %.1f, p99 %.1f, worst %.1f ms, >33ms %d" % [s.id, row.load_ms, row.median_ms, row.p99_ms, row.worst_ms, row.over_33ms])
	var worst := report.duplicate()
	worst.sort_custom(func(a: Dictionary, b: Dictionary) -> bool: return a.p99_ms > b.p99_ms)
	var summary := {"environment": {"os": OS.get_name(), "gpu": RenderingServer.get_video_adapter_name(), "renderer": RenderingServer.get_current_rendering_method()},
			"missions": report, "worst_p99": worst.slice(0, 5)}
	var file := FileAccess.open(out, FileAccess.WRITE)
	file.store_string(JSON.stringify(summary, "\t") + "\n")
	file.close()
	DirAccess.remove_absolute(ProjectSettings.globalize_path(SAVE))
	quit()


func _pct(sorted: Array, q: float) -> float:
	if sorted.is_empty():
		return 0.0
	return snappedf(sorted[clampi(int(ceil(q * sorted.size())) - 1, 0, sorted.size() - 1)], 0.1)


func _frames(count: int) -> void:
	for i in count:
		await process_frame
