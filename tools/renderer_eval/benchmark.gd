extends Node
## Renderer evaluation harness (M3). Runs the same scripted scenarios under whichever renderer the
## project is configured with, and reports frame pacing, CPU/GPU viewport time, draw calls, memory
## and load times as JSON (user://renderer_eval/) plus one log line per scenario.
##
## It is not part of the shipped game. `make_eval_project.py` copies the project into an isolated
## folder, makes this scene the main scene and selects the renderer there, so production settings
## and export presets are never touched. Desktop runs are functional smoke tests only; mobile
## evidence must come from physical devices.
##
## Scenarios drive the real app root (menu, GameScreen, physics) and add proxy scenes for content
## that does not exist yet (chapter parallax art, particles/shaders, cinematics). Proxies are
## labelled as such in the report.

const MainScript := preload("res://scripts/main.gd")
const CONFIG_PATH := "res://tools/renderer_eval/benchmark_config.json"
const OUTPUT_DIR := "user://renderer_eval"
const SAVE_PATH := "user://renderer_eval/benchmark_progress.json"
const FRAME_BUDGET_MS := 1000.0 / 60.0
const SEVERE_FRAME_MS := 1000.0 / 30.0
const PROXY_SIZE := Vector2i(1920, 1080)

var _config := {"variant": "unspecified", "soak_minutes": 0.0}
var _main: Node
var _recording := false
var _frame_ms := PackedFloat32Array()
var _physics_ms := 0.0
var _gpu_ms := 0.0
var _cpu_render_ms := 0.0
var _draw_calls := 0.0
var _max_draw_calls := 0.0
var _last_usec := 0
var _focus_lost := false
var _results := []
var _report := {}


func _ready() -> void:
	process_mode = Node.PROCESS_MODE_ALWAYS
	_report["startup_ms_to_main_scene"] = Time.get_ticks_msec()
	_load_config()
	RenderingServer.viewport_set_measure_render_time(get_viewport().get_viewport_rid(), true)
	_run.call_deferred()


func _notification(what: int) -> void:
	if what == NOTIFICATION_APPLICATION_PAUSED or what == NOTIFICATION_APPLICATION_FOCUS_OUT:
		_focus_lost = true


func _process(_delta: float) -> void:
	var now := Time.get_ticks_usec()
	if _recording and _last_usec > 0:
		_frame_ms.append((now - _last_usec) / 1000.0)
		_physics_ms += Performance.get_monitor(Performance.TIME_PHYSICS_PROCESS) * 1000.0
		var rid := get_viewport().get_viewport_rid()
		_gpu_ms += RenderingServer.viewport_get_measured_render_time_gpu(rid)
		_cpu_render_ms += RenderingServer.viewport_get_measured_render_time_cpu(rid)
		var calls := Performance.get_monitor(Performance.RENDER_TOTAL_DRAW_CALLS_IN_FRAME)
		_draw_calls += calls
		_max_draw_calls = maxf(_max_draw_calls, calls)
	_last_usec = now


func _run() -> void:
	await get_tree().process_frame
	_report["startup_ms_to_first_frame"] = Time.get_ticks_msec()
	_report["environment"] = _environment()
	print("RENDER_EVAL_ENV ", JSON.stringify(_report.environment))

	_main = _make_main()
	add_child(_main)
	await _wait(1.0)
	await _scenario("menu_idle", 6.0, "real")

	_report["level_load_ms"] = await _measure_level_loads()

	_main._start_level(0)
	await _wait(0.5)
	_drive_solutions()
	await _scenario("level_ordinary_L01", 8.0, "real")

	var finale: int = _main.catalog.index_of("L20")
	_main._start_level(maxi(finale, 0))
	await _wait(0.5)
	_drive_solutions()
	await _scenario("destruction_L20_grand_collapse", 12.0, "real")

	_main._game.start(_stress_level(), 99, false)
	await _wait(0.5)
	_drive_stress_shots()
	await _scenario("destruction_stress_synthetic", 12.0, "synthetic level, real physics")

	_main._show_menu()
	await _wait(0.3)
	var proxy := _parallax_proxy()
	add_child(proxy)
	await _wait(0.5)
	await _scenario("background_parallax_proxy", 8.0, "proxy art")
	proxy.queue_free()

	proxy = _particles_shader_proxy()
	add_child(proxy)
	await _wait(0.5)
	await _scenario("particles_shaders_proxy", 8.0, "proxy effects")
	proxy.queue_free()

	proxy = _cinematic_proxy()
	add_child(proxy)
	await _wait(0.3)
	await _scenario("cinematic_proxy", 10.0, "proxy slides")
	proxy.queue_free()

	var soak_minutes := float(_config.get("soak_minutes", 0.0))
	if soak_minutes > 0.0:
		await _soak(soak_minutes)

	_report["scenarios"] = _results
	_report["focus_lost_during_run"] = _focus_lost
	_report["memory"] = _memory()
	_write_report()
	get_tree().quit()


func _make_main() -> Node:
	if FileAccess.file_exists(SAVE_PATH):
		DirAccess.remove_absolute(ProjectSettings.globalize_path(SAVE_PATH))
	DirAccess.make_dir_recursive_absolute(ProjectSettings.globalize_path(OUTPUT_DIR))
	var main: Node = MainScript.new()
	main.cinematics_enabled = false
	main.save = SaveService.new(SAVE_PATH)
	main.boot_mission = "helix_08"
	return main


func _wait(seconds: float) -> void:
	await get_tree().create_timer(seconds).timeout


func _scenario(scenario_name: String, seconds: float, kind: String) -> void:
	_frame_ms = PackedFloat32Array()
	_physics_ms = 0.0
	_gpu_ms = 0.0
	_cpu_render_ms = 0.0
	_draw_calls = 0.0
	_max_draw_calls = 0.0
	_last_usec = 0
	_recording = true
	await _wait(seconds)
	_recording = false
	var result := _summarise(scenario_name, kind, seconds)
	_results.append(result)
	print("RENDER_EVAL_SCENARIO ", JSON.stringify(result))


func _summarise(scenario_name: String, kind: String, seconds: float) -> Dictionary:
	var count := _frame_ms.size()
	var result := {"name": scenario_name, "kind": kind, "duration_s": seconds, "frames": count}
	if count == 0:
		return result
	var sorted := _frame_ms.duplicate()
	sorted.sort()
	var total := 0.0
	var over_budget := 0
	var severe := 0
	for ms in _frame_ms:
		total += ms
		if ms > FRAME_BUDGET_MS * 1.1:
			over_budget += 1
		if ms > SEVERE_FRAME_MS:
			severe += 1
	result["avg_fps"] = snappedf(count / (total / 1000.0), 0.1)
	result["frame_ms_avg"] = snappedf(total / count, 0.01)
	result["frame_ms_p50"] = snappedf(_percentile(sorted, 0.50), 0.01)
	result["frame_ms_p95"] = snappedf(_percentile(sorted, 0.95), 0.01)
	result["frame_ms_p99"] = snappedf(_percentile(sorted, 0.99), 0.01)
	result["frame_ms_max"] = snappedf(sorted[count - 1], 0.01)
	result["frames_over_18_3ms_pct"] = snappedf(100.0 * over_budget / count, 0.01)
	result["frames_over_33_3ms"] = severe
	result["cpu_physics_ms_avg"] = snappedf(_physics_ms / count, 0.001)
	result["viewport_cpu_render_ms_avg"] = snappedf(_cpu_render_ms / count, 0.001)
	# Reported as 0 where the renderer/driver does not support GPU timestamps.
	result["viewport_gpu_render_ms_avg"] = snappedf(_gpu_ms / count, 0.001)
	result["draw_calls_avg"] = snappedf(_draw_calls / count, 0.1)
	result["draw_calls_max"] = _max_draw_calls
	result["static_memory_mb"] = snappedf(OS.get_static_memory_usage() / 1048576.0, 0.1)
	result["video_memory_mb"] = snappedf(Performance.get_monitor(Performance.RENDER_VIDEO_MEM_USED) / 1048576.0, 0.1)
	return result


static func _percentile(sorted: PackedFloat32Array, q: float) -> float:
	var index := clampi(int(ceil(q * sorted.size())) - 1, 0, sorted.size() - 1)
	return sorted[index]


func _measure_level_loads() -> Array:
	var loads := []
	for i in _main.catalog.levels.size():
		var start := Time.get_ticks_usec()
		_main._start_level(i)
		await get_tree().process_frame
		loads.append({"id": _main.catalog.levels[i].id, "ms_to_next_frame": snappedf((Time.get_ticks_usec() - start) / 1000.0, 0.01)})
	_main._show_menu()
	await _wait(0.3)
	return loads


## Fires the level's stored solution shots whenever the session accepts a launch.
func _drive_solutions() -> void:
	var game: GameScreen = _main._game
	var shots: Array[Vector2] = game.session.definition.solution
	for velocity in shots:
		while is_instance_valid(game) and not game.session.can_launch():
			await get_tree().physics_frame
		if not is_instance_valid(game):
			return
		game.session.launch(velocity)
		await _wait(0.2)


func _drive_stress_shots() -> void:
	var game: GameScreen = _main._game
	for velocity: Vector2 in [Vector2(1150, -300), Vector2(1200, -420), Vector2(1250, -200)]:
		var waited := 0
		while is_instance_valid(game) and not game.session.can_launch() and waited < 600:
			await get_tree().physics_frame
			waited += 1
		if not is_instance_valid(game) or not game.session.can_launch():
			return
		game.session.launch(velocity)
		await _wait(0.2)


## A deliberately heavy layout (60 wood blocks, 8 glass, 4 stone, 3 targets) for worst-case
## destruction load. Not a shipped level.
func _stress_level() -> LevelDefinition:
	var blocks := []
	for column in 10:
		for row in 6:
			blocks.append({"x": 720 + column * 44, "y": 620 - row * 40, "w": 40, "h": 38, "material": "wood"})
	for i in 8:
		blocks.append({"x": 700 + i * 60, "y": 375, "w": 56, "h": 12, "material": "glass"})
	for i in 4:
		blocks.append({"x": 760 + i * 120, "y": 345, "w": 100, "h": 30, "material": "stone"})
	var data := {
		"id": "BENCH_STRESS", "name": "Stress", "hint": "", "shots": 3, "par": 3,
		"launcher": [180, 540], "objective": {"type": "destroy_targets"},
		"statics": [], "blocks": blocks,
		"targets": [{"x": 800, "y": 310, "r": 18}, {"x": 920, "y": 310, "r": 18}, {"x": 1040, "y": 310, "r": 18}],
	}
	var def := LevelDefinition.from_dict(data)
	if not def.is_valid():
		push_error("renderer_eval: stress level invalid: %s" % ", ".join(def.errors))
	return def


## Three full-screen translucent layers drifting at different speeds: the overdraw pattern a
## chapter background with parallax will produce.
func _parallax_proxy() -> Node:
	var layer := CanvasLayer.new()
	layer.layer = 50
	var root := Control.new()
	root.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	layer.add_child(root)
	var colors := [Color("1b2230"), Color("2a3442"), Color("3a4656")]
	for i in 3:
		var rect := TextureRect.new()
		rect.texture = _proxy_texture(colors[i], 0.15 + i * 0.1, i)
		rect.size = Vector2(PROXY_SIZE) * 1.2
		rect.modulate.a = 1.0 if i == 0 else 0.6
		rect.stretch_mode = TextureRect.STRETCH_SCALE
		root.add_child(rect)
		var tween := rect.create_tween().set_loops()
		tween.tween_property(rect, "position:x", -120.0 * (i + 1), 4.0)
		tween.tween_property(rect, "position:x", 0.0, 4.0)
	return layer


func _particles_shader_proxy() -> Node:
	var layer := CanvasLayer.new()
	layer.layer = 50
	var root := Node2D.new()
	layer.add_child(root)
	var view := get_viewport().get_visible_rect().size
	for i in 4:
		var particles := GPUParticles2D.new()
		particles.amount = 96
		particles.lifetime = 1.2
		particles.explosiveness = 0.6
		particles.position = Vector2(view.x * (0.2 + i * 0.2), view.y * 0.55)
		var material := ParticleProcessMaterial.new()
		material.direction = Vector3(0, -1, 0)
		material.spread = 70.0
		material.initial_velocity_min = 120.0
		material.initial_velocity_max = 320.0
		material.gravity = Vector3(0, 400, 0)
		material.scale_min = 2.0
		material.scale_max = 5.0
		material.color = Color(0.45, 0.85, 1.0, 0.8)
		particles.process_material = material
		root.add_child(particles)
	var ripple := ColorRect.new()
	ripple.size = view
	ripple.mouse_filter = Control.MOUSE_FILTER_IGNORE
	ripple.material = _shader_material(RIPPLE_SHADER)
	layer.add_child(ripple)
	# A screen-reading distortion, as a temporal-charge impact effect might use.
	var distortion := ColorRect.new()
	distortion.position = view * 0.3
	distortion.size = view * 0.4
	distortion.mouse_filter = Control.MOUSE_FILTER_IGNORE
	distortion.material = _shader_material(DISTORTION_SHADER)
	layer.add_child(distortion)
	return layer


func _cinematic_proxy() -> Node:
	var layer := CanvasLayer.new()
	layer.layer = 60
	var root := Control.new()
	root.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	layer.add_child(root)
	var view := get_viewport().get_visible_rect().size
	var slides := []
	for i in 2:
		var slide := TextureRect.new()
		slide.texture = _proxy_texture(Color("202a36") if i == 0 else Color("2c2620"), 0.35, i + 5)
		slide.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_COVERED
		slide.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
		slide.size = view
		slide.pivot_offset = view * 0.5
		slide.modulate.a = 1.0 if i == 0 else 0.0
		root.add_child(slide)
		slides.append(slide)
	var first: TextureRect = slides[0]
	var second: TextureRect = slides[1]
	first.create_tween().tween_property(first, "scale", Vector2.ONE * 1.08, 10.0)
	var fade := second.create_tween()
	fade.tween_interval(4.5)
	fade.tween_property(second, "modulate:a", 1.0, 1.0)
	fade.parallel().tween_property(second, "scale", Vector2.ONE * 1.05, 6.0)
	var subtitle := Label.new()
	subtitle.text = "Humanity believed every problem had a solution."
	subtitle.add_theme_font_size_override("font_size", 30)
	subtitle.add_theme_constant_override("outline_size", 6)
	subtitle.add_theme_color_override("font_outline_color", Color(0, 0, 0, 0.8))
	subtitle.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	subtitle.position = Vector2(0, view.y * 0.86)
	subtitle.size = Vector2(view.x, 60)
	root.add_child(subtitle)
	return layer


## Repeats the stress level for the configured minutes, reporting each minute separately so a
## thermal slowdown shows up as rising frame times.
func _soak(minutes: float) -> void:
	var rounds := int(ceil(minutes))
	for minute in rounds:
		_main._start_level(0)
		await get_tree().process_frame
		_main._game.start(_stress_level(), 99, false)
		await _wait(0.3)
		_soak_driver(60.0)
		await _scenario("soak_minute_%02d" % (minute + 1), 60.0, "synthetic level, sustained")


func _soak_driver(seconds: float) -> void:
	var deadline := Time.get_ticks_msec() + int(seconds * 1000.0)
	while Time.get_ticks_msec() < deadline:
		await _drive_stress_shots()
		if Time.get_ticks_msec() >= deadline or not is_instance_valid(_main._game):
			return
		_main._game.start(_stress_level(), 99, false)
		await _wait(0.3)


func _proxy_texture(base: Color, contrast: float, seed_value: int) -> Texture2D:
	var noise := FastNoiseLite.new()
	noise.seed = seed_value
	noise.frequency = 0.004
	var image := noise.get_seamless_image(512, 288)
	image.convert(Image.FORMAT_RGBA8)
	var tinted := Image.create(512, 288, false, Image.FORMAT_RGBA8)
	for y in 288:
		for x in 512:
			var v := image.get_pixel(x, y).r
			tinted.set_pixel(x, y, base.lightened((v - 0.5) * contrast))
	tinted.resize(PROXY_SIZE.x, PROXY_SIZE.y, Image.INTERPOLATE_BILINEAR)
	return ImageTexture.create_from_image(tinted)


static func _shader_material(code: String) -> ShaderMaterial:
	var shader := Shader.new()
	shader.code = code
	var material := ShaderMaterial.new()
	material.shader = shader
	return material


const RIPPLE_SHADER := """
shader_type canvas_item;
void fragment() {
	vec2 uv = UV - 0.5;
	float r = length(uv);
	float ripple = sin(r * 40.0 - TIME * 6.0) * exp(-r * 4.0);
	float vignette = smoothstep(0.3, 0.8, r);
	COLOR = vec4(vec3(0.25, 0.75, 0.9) * abs(ripple), vignette * 0.45 + abs(ripple) * 0.12);
}
"""

const DISTORTION_SHADER := """
shader_type canvas_item;
uniform sampler2D screen_texture : hint_screen_texture, filter_linear;
void fragment() {
	vec2 uv = UV - 0.5;
	float wave = sin(length(uv) * 30.0 - TIME * 8.0) * 0.006;
	COLOR = texture(screen_texture, SCREEN_UV + normalize(uv + 0.0001) * wave);
}
"""


func _environment() -> Dictionary:
	return {
		"variant": _config.get("variant", "unspecified"),
		"godot": Engine.get_version_info().get("string", ""),
		"os": OS.get_name(),
		"os_version": OS.get_version(),
		"model": OS.get_model_name(),
		"processor": OS.get_processor_name(),
		"processor_count": OS.get_processor_count(),
		"rendering_method_setting": ProjectSettings.get_setting("rendering/renderer/rendering_method", ""),
		"rendering_method_active": _call_or(RenderingServer, "get_current_rendering_method", "unknown"),
		"rendering_driver_active": _call_or(RenderingServer, "get_current_rendering_driver_name", "unknown"),
		"video_adapter": RenderingServer.get_video_adapter_name(),
		"video_vendor": RenderingServer.get_video_adapter_vendor(),
		"video_api_version": RenderingServer.get_video_adapter_api_version(),
		"screen_size": DisplayServer.screen_get_size(),
		"window_size": DisplayServer.window_get_size(),
		"refresh_rate": DisplayServer.screen_get_refresh_rate(),
		"vsync_mode": DisplayServer.window_get_vsync_mode(),
	}


func _memory() -> Dictionary:
	return {
		"static_mb_end": snappedf(OS.get_static_memory_usage() / 1048576.0, 0.1),
		"static_mb_peak": snappedf(OS.get_static_memory_peak_usage() / 1048576.0, 0.1),
		"video_mb_end": snappedf(Performance.get_monitor(Performance.RENDER_VIDEO_MEM_USED) / 1048576.0, 0.1),
		"texture_mb_end": snappedf(Performance.get_monitor(Performance.RENDER_TEXTURE_MEM_USED) / 1048576.0, 0.1),
	}


static func _call_or(target: Object, method: String, fallback: Variant) -> Variant:
	return target.call(method) if target.has_method(method) else fallback


func _load_config() -> void:
	if not FileAccess.file_exists(CONFIG_PATH):
		return
	var parsed: Variant = JSON.parse_string(FileAccess.get_file_as_string(CONFIG_PATH))
	if parsed is Dictionary:
		_config.merge(parsed, true)
	else:
		push_warning("renderer_eval: ignoring unreadable %s" % CONFIG_PATH)


func _write_report() -> void:
	var stamp := Time.get_datetime_string_from_system(true).replace(":", "").replace("-", "")
	var path := "%s/%s_%s.json" % [OUTPUT_DIR, str(_config.get("variant", "run")), stamp]
	var file := FileAccess.open(path, FileAccess.WRITE)
	if file == null:
		push_error("renderer_eval: cannot write %s (error %d)" % [path, FileAccess.get_open_error()])
		print("RENDER_EVAL_REPORT_FAILED")
		return
	file.store_string(JSON.stringify(_report, "\t"))
	file.close()
	print("RENDER_EVAL_DONE ", ProjectSettings.globalize_path(path))
