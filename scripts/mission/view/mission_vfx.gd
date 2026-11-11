class_name MissionVfx
extends Node3D
## Gameplay effects from the ui-vfx stream's CPUParticles3D presets (assets/vfx/godot/presets,
## listed in data/integrated_assets.json `presets`). Owns no rules: MissionView calls it from
## world signals.
##
## Every one-shot preset is a small fixed pool created with the mission and restarted on use.
## Creating effect nodes per event cost ~300 ms per blast on GL Compatibility (Batch 5 spike
## logs), and a particle material drawn for the first time mid-play compiles its shader then, so
## each preset is also emitted once, motionless and under the floor, while the mission loads.
## A missing preset makes `has_preset` false and the caller keeps its procedural fallback.
##
## The chapter II-V weapons have no preset scenes, so their effects are pooled "timed" quads built
## from the integrated flipbooks (additive, camera-facing, tinted per weapon) plus a fresnel shell
## for the Disruptor EMP field. They follow the same rules as the presets: a fixed pool created
## with the mission, drawn once under the floor while it loads, restarted on use.

## Pool size per preset: enough for overlapping events (two charges, a burst of impacts).
const POOLS := {
	"breach_explosion": 2,
	"kinetic_impact": 3,
	"kinetic_muzzle": 2,
	"impact_metal": 3,
	"impact_glass": 2,
	"impact_electric": 3,
	"impact_concrete": 2,
	"component_collapse": 3,
	"critical_core_destroyed": 1,
}
## Physics material -> impact preset (presets' own notes: metal sparks, glass shards,
## electronic arcs, concrete/composite dust).
const IMPACT_BY_MATERIAL := {
	"reinforced_steel": "impact_metal",
	"lightweight_alloy": "impact_metal",
	"glass_polymer": "impact_glass",
	"electronic_module": "impact_electric",
	"energy_component": "impact_electric",
	"ai_core_module": "impact_electric",
	"composite": "impact_concrete",
	"concrete": "impact_concrete",
}
const DEFAULT_IMPACT := "impact_metal"
## Preset reference sizes from their notes: breach explosion at blast_radius 140 px; collapse
## dust for a 1.6 m wide component.
const BREACH_REFERENCE_RADIUS_PX := 140.0
const COLLAPSE_REFERENCE_WIDTH_M := 1.6
const COLLAPSE_SCALE_RANGE := Vector2(0.35, 1.6)
const CORE_IDLE := "critical_core_idle"
## Flipbook / texture effects (asset ids in data/integrated_assets.json): frame grid, rate and
## pool size. A sheet with fps 0 is a static texture (rings) that plays for the call's duration.
const SHEETS := {
	"discharge": {"asset": "SHR-VFX-ENERGY_DISCHARGE-A", "columns": 4, "rows": 4, "fps": 24.0, "pool": 2},
	"electric": {"asset": "SHR-VFX-IMPACT_ELECTRIC-A", "columns": 4, "rows": 4, "fps": 30.0, "pool": 8},
	"spark": {"asset": "SHR-VFX-SPARK_BURST-A", "columns": 4, "rows": 4, "fps": 30.0, "pool": 6},
	"flash": {"asset": "OPR-VFX-KINETIC_IMPACT-A", "columns": 4, "rows": 4, "fps": 30.0, "pool": 4},
	"ring": {"asset": "SHR-VFX-PARTICLE_RING-A", "columns": 1, "rows": 1, "fps": 0.0, "pool": 6},
}
const EMP_SHELLS := 2
const EMP_COLOUR := Color("4f8cff")
const PULSE_COLOUR := Color("ffa22e")
const LANCE_COLOUR := Color("b48cff")
const PIERCE_COLOUR := Color("dff8ff")
## Arc placement in the EMP field is random; a fixed seed keeps captures and tests repeatable.
const FX_SEED := 4242
## Warm-up instances sit this far under the floor (y = 0), at half scale: the largest preset
## quad (3.2 m) then stays below the floor yet inside the camera frustum, so it is drawn (and
## compiled) but never seen. A culled node compiles nothing.
const WARM_DEPTH := 1.2
const WARM_SCALE := 0.5
const WARM_FRAMES := 3

## preset name -> Array of instances
var _pools := {}
var _next := {}
## critical asset id -> looping idle effect
var _idle := {}
var _warm: Array[Node3D] = []
var _warm_frames := 0
## sheet name -> Array of TimedFx ("emp_shell" holds the EMP shells)
var _fx := {}
var _fx_next := {}
var _running: Array[TimedFx] = []
var _rng := RandomNumberGenerator.new()


## One pooled, timed additive quad (or the EMP shell sphere): flipbook frames, growth and fade.
class TimedFx extends MeshInstance3D:
	var columns := 1
	var rows := 1
	var fps := 0.0
	var tint := Color.WHITE
	var duration := 0.5
	var delay := 0.0
	var size_from := 1.0
	var size_to := 1.0
	var fade := true
	var is_shell := false
	## 1 recolours the sheet by its brightness only (so a cyan flipbook can be amber or violet);
	## 0 keeps the sheet's own colours (multiplied by the tint).
	var mono := 1.0
	var base_material: ShaderMaterial
	var time := 0.0

	## Starts (or restarts) the effect: `size` metres across at the end, growing from `grow_from` of it.
	func start(at: Vector3, size: float, p_tint: Color, p_delay: float, grow_from: float, p_duration: float) -> void:
		position = at
		tint = p_tint
		delay = p_delay
		size_to = size
		size_from = size * grow_from
		if p_duration > 0.0:
			duration = p_duration
		elif fps > 0.0:
			duration = float(columns * rows) / fps
		time = 0.0
		visible = false

	## Advances the effect; false once it has finished (and hidden itself).
	func step(delta: float) -> bool:
		time += delta
		var local := time - delay
		if local < 0.0:
			return true
		if local >= duration:
			visible = false
			return false
		visible = true
		var k := local / duration
		scale = Vector3.ONE * lerpf(size_from, size_to, 1.0 - (1.0 - k) * (1.0 - k))
		var alpha := (1.0 - k) if fade else 1.0
		base_material.set_shader_parameter("tint", Color(tint.r, tint.g, tint.b, alpha))
		if is_shell:
			return true
		base_material.set_shader_parameter("mono", mono)
		if fps > 0.0:
			var frame := mini(int(local * fps), columns * rows - 1)
			base_material.set_shader_parameter("uv_offset", Vector2(float(frame % columns) / columns, float(frame / columns) / rows))
		return true


## Builds the pools from the library's presets (missing ones are skipped). `warm_x` is a view x
## under the framed facility, where the warm-up copies are drawn.
func setup(library: AssetLibrary, warm_x: float) -> void:
	if library == null:
		return
	for preset: String in POOLS:
		var scene := library.preset_scene(preset)
		if scene == null:
			continue
		var pool: Array[Node3D] = []
		for i in int(POOLS[preset]):
			var node := scene.instantiate() as Node3D
			node.visible = false
			add_child(node)
			pool.append(node)
		_pools[preset] = pool
		_next[preset] = 0
		_add_warm_instance(scene, warm_x)
	var idle := library.preset_scene(CORE_IDLE)
	if idle != null:
		_pools[CORE_IDLE] = []
	_rng.seed = FX_SEED
	_build_fx(library, warm_x)


func has_preset(preset: String) -> bool:
	return _pools.has(preset)


## Pulse Cannon discharge: an amber plasma burst and a ring at the blast radius.
func pulse_discharge(at: Vector3, radius_px: float) -> bool:
	var diameter := radius_px * 2.0 / ViewMapping.PX_PER_METRE
	var played := _play_fx("discharge", at, diameter * 1.15, PULSE_COLOUR, 0.0, 0.5)
	_play_fx("ring", at, diameter, Color(1.0, 0.8, 0.45), 0.0, 0.45, 0.2)
	return played


## Disruptor EMP: a large translucent blue shockwave shell and rings with electric arcs inside it.
## No fireball, no debris: the field pushes nothing.
func emp_burst(at: Vector3, radius_px: float) -> bool:
	var diameter := radius_px * 2.0 / ViewMapping.PX_PER_METRE
	if not _fx.has("electric") and _fx.get("emp_shell", []).is_empty():
		return false
	_start_next("emp_shell", at, diameter, EMP_COLOUR, 0.0, 0.25, 0.55)
	_play_fx("ring", at, diameter * 1.05, Color(0.7, 0.88, 1.0), 0.0, 0.5, 0.15)
	_play_fx("ring", at, diameter * 0.8, EMP_COLOUR, 0.12, 0.5, 0.15)
	for i in 5:
		var offset := Vector3(_rng.randf_range(-0.55, 0.55) * diameter / 2.0, _rng.randf_range(-0.4, 0.55) * diameter / 2.0, 0.1)
		_play_fx("electric", at + offset, _rng.randf_range(0.9, 1.4), Color(0.85, 0.95, 1.0), 0.04 * i + _rng.randf_range(0.0, 0.05), 0.0, 1.0, false, 0.0)
	return true


## Temporal Lance strike: a white-violet flash, a spark burst and a thin ring (a clean cut, no fire).
func lance_strike(at: Vector3) -> bool:
	var played := _play_fx("flash", at, 1.5, Color(0.86, 0.78, 1.0))
	_play_fx("spark", at, 1.7, LANCE_COLOUR)
	_play_fx("ring", at, 1.4, Color(0.8, 0.7, 1.0), 0.0, 0.3, 0.2)
	return played


## A small sharp spark where a Penetrator round goes through (or stops in) a component.
func pierce_spark(at: Vector3) -> bool:
	var played := _play_fx("spark", at, 0.9, PIERCE_COLOUR)
	_play_fx("flash", at, 0.55, Color(0.8, 0.97, 1.0))
	return played


## Muzzle flash of a weapon (the kinetic preset flash points along +X, the sheets are round).
func weapon_muzzle(weapon_id: String, at: Vector3, angle: float) -> bool:
	match weapon_id:
		"pulse_cannon":
			return _play_fx("flash", at, 0.7, PULSE_COLOUR)
		"disruptor":
			return _play_fx("electric", at, 0.6, Color(0.85, 0.95, 1.0), 0.0, 0.0, 1.0, true, 0.0)
		"temporal_lance":
			return _play_fx("spark", at, 0.9, LANCE_COLOUR)
		"penetrator":
			return _play("kinetic_muzzle", at, 0.7, angle)
	return muzzle(at, angle)


## Breach detonation scaled to the blast radius.
func breach_explosion(at: Vector3, radius_px: float) -> bool:
	return _play("breach_explosion", at, radius_px / BREACH_REFERENCE_RADIUS_PX)


## Material-specific impact (projectile strikes and hard structural collisions).
func impact(at: Vector3, material_id: String) -> bool:
	return _play(IMPACT_BY_MATERIAL.get(material_id, DEFAULT_IMPACT), at, 1.0)


## The Kinetic Accelerator's own hit flash, on top of the material impact (preset note).
func kinetic_hit(at: Vector3) -> bool:
	return _play("kinetic_impact", at, 1.0)


## Muzzle flash; the preset's flash points along +X, so it is turned to the aim angle.
func muzzle(at: Vector3, angle: float) -> bool:
	return _play("kinetic_muzzle", at, 1.0, angle)


## Collapse dust and chips for a removed component, scaled by its width.
func collapse(at: Vector3, width_m: float) -> bool:
	var s := clampf(width_m / COLLAPSE_REFERENCE_WIDTH_M, COLLAPSE_SCALE_RANGE.x, COLLAPSE_SCALE_RANGE.y)
	return _play("component_collapse", at, s)


func core_destroyed(at: Vector3) -> bool:
	return _play("critical_core_destroyed", at, 1.0)


## Starts the looping red glow on a critical asset (follow it with `move_core_idle`).
func start_core_idle(asset_id: String, library: AssetLibrary, at: Vector3) -> void:
	if _idle.has(asset_id) or not has_preset(CORE_IDLE):
		return
	var node := library.preset_scene(CORE_IDLE).instantiate() as Node3D
	node.position = at
	add_child(node)
	_set_emitting(node, true, false)
	_idle[asset_id] = node


func move_core_idle(asset_id: String, at: Vector3) -> void:
	var node: Node3D = _idle.get(asset_id)
	if node != null:
		node.position = at


func stop_core_idle(asset_id: String) -> void:
	var node: Node3D = _idle.get(asset_id)
	_idle.erase(asset_id)
	if node != null:
		node.queue_free()


## Plays one pooled quad of `sheet`; false when that sheet is not integrated.
func _play_fx(sheet: String, at: Vector3, size: float, tint: Color, delay: float = 0.0, duration: float = 0.0, grow_from: float = 1.0, fade: bool = true, mono: float = 1.0) -> bool:
	return _start_next(sheet, at, size, tint, delay, grow_from, duration, fade, mono)


func _start_next(sheet: String, at: Vector3, size: float, tint: Color, delay: float, grow_from: float, duration: float, fade: bool = true, mono: float = 1.0) -> bool:
	var pool: Array = _fx.get(sheet, [])
	if pool.is_empty():
		return false
	var index: int = _fx_next[sheet]
	_fx_next[sheet] = (index + 1) % pool.size()
	var fx: TimedFx = pool[index]
	fx.fade = fade
	fx.mono = mono
	fx.start(at, size, tint, delay, grow_from, duration)
	if not _running.has(fx):
		_running.append(fx)
	return true


func _build_fx(library: AssetLibrary, warm_x: float) -> void:
	var quad := QuadMesh.new()
	quad.size = Vector2.ONE
	var quad_shader := Shader.new()
	quad_shader.code = FX_QUAD_SHADER
	for sheet: String in SHEETS:
		var spec: Dictionary = SHEETS[sheet]
		var texture := library.texture(str(spec.asset))
		if texture == null:
			continue
		var pool: Array = []
		for i in int(spec.pool):
			var fx := TimedFx.new()
			fx.mesh = quad
			fx.columns = int(spec.columns)
			fx.rows = int(spec.rows)
			fx.fps = float(spec.fps)
			var material := ShaderMaterial.new()
			material.shader = quad_shader
			material.set_shader_parameter("tex", texture)
			material.set_shader_parameter("uv_scale", Vector2(1.0 / fx.columns, 1.0 / fx.rows))
			fx.base_material = material
			fx.material_override = material
			fx.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
			_add_fx_node(fx, warm_x)
			pool.append(fx)
		_fx[sheet] = pool
		_fx_next[sheet] = 0
	var shader := Shader.new()
	shader.code = EMP_SHELL_SHADER
	var shell_mesh := SphereMesh.new()
	shell_mesh.radius = 0.5
	shell_mesh.height = 1.0
	shell_mesh.radial_segments = 24
	shell_mesh.rings = 12
	var shells: Array = []
	for i in EMP_SHELLS:
		var fx := TimedFx.new()
		fx.mesh = shell_mesh
		fx.is_shell = true
		var material := ShaderMaterial.new()
		material.shader = shader
		material.set_shader_parameter("tint", EMP_COLOUR)
		fx.base_material = material
		fx.material_override = material
		fx.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
		_add_fx_node(fx, warm_x)
		shells.append(fx)
	_fx["emp_shell"] = shells
	_fx_next["emp_shell"] = 0


## Pooled quads start hidden but are drawn motionless under the floor for the warm-up frames.
func _add_fx_node(fx: TimedFx, warm_x: float) -> void:
	fx.position = Vector3(warm_x, -WARM_DEPTH, 0.0)
	fx.scale = Vector3.ONE * WARM_SCALE
	fx.visible = true
	add_child(fx)
	_warm.append(fx)
	_warm_frames = WARM_FRAMES


func _play(preset: String, at: Vector3, scale_factor: float, angle: float = 0.0) -> bool:
	var pool: Array = _pools.get(preset, [])
	if pool.is_empty():
		return false
	var index: int = _next[preset]
	_next[preset] = (index + 1) % pool.size()
	var node: Node3D = pool[index]
	node.position = at
	node.rotation = Vector3(0.0, 0.0, angle)
	node.scale = Vector3.ONE * scale_factor
	node.visible = true
	_set_emitting(node, true, true)
	return true


static func _set_emitting(root: Node, emitting: bool, restart: bool) -> void:
	for particles: CPUParticles3D in root.find_children("*", "CPUParticles3D", true, false):
		if restart:
			particles.restart()
		particles.emitting = emitting


## A motionless copy under the floor, emitting for a few frames so its materials compile.
func _add_warm_instance(scene: PackedScene, warm_x: float) -> void:
	var node := scene.instantiate() as Node3D
	node.position = Vector3(warm_x, -WARM_DEPTH, 0.0)
	node.scale = Vector3.ONE * WARM_SCALE
	add_child(node)
	for particles: CPUParticles3D in node.find_children("*", "CPUParticles3D", true, false):
		particles.initial_velocity_min = 0.0
		particles.initial_velocity_max = 0.0
		particles.gravity = Vector3.ZERO
		particles.emission_shape = CPUParticles3D.EMISSION_SHAPE_POINT
		particles.restart()
		particles.emitting = true
	_warm.append(node)
	_warm_frames = WARM_FRAMES


func _process(delta: float) -> void:
	var index := _running.size() - 1
	while index >= 0:
		if not _running[index].step(delta):
			_running.remove_at(index)
		index -= 1
	if _warm_frames <= 0:
		return
	_warm_frames -= 1
	if _warm_frames == 0:
		for node: Node3D in _warm:
			if node is TimedFx:
				node.visible = false
			else:
				node.queue_free()
		_warm.clear()


## Camera-facing additive flipbook quad; `mono` recolours the sheet by brightness (tint = colour).
const FX_QUAD_SHADER := """shader_type spatial;
render_mode blend_add, unshaded, cull_disabled, depth_draw_never, shadows_disabled;
uniform sampler2D tex : source_color, filter_linear_mipmap, repeat_disable;
uniform vec4 tint : source_color = vec4(1.0);
uniform vec2 uv_scale = vec2(1.0);
uniform vec2 uv_offset = vec2(0.0);
uniform float mono = 1.0;
void vertex() {
	MODELVIEW_MATRIX = VIEW_MATRIX * mat4(INV_VIEW_MATRIX[0], INV_VIEW_MATRIX[1], INV_VIEW_MATRIX[2], MODEL_MATRIX[3]);
	MODELVIEW_MATRIX = MODELVIEW_MATRIX * mat4(vec4(length(MODEL_MATRIX[0].xyz), 0.0, 0.0, 0.0), vec4(0.0, length(MODEL_MATRIX[1].xyz), 0.0, 0.0), vec4(0.0, 0.0, length(MODEL_MATRIX[2].xyz), 0.0), vec4(0.0, 0.0, 0.0, 1.0));
}
void fragment() {
	vec4 c = texture(tex, UV * uv_scale + uv_offset);
	float l = dot(c.rgb, vec3(0.299, 0.587, 0.114));
	ALBEDO = mix(c.rgb, vec3(l * 1.5), mono) * tint.rgb;
	ALPHA = clamp(c.a, 0.0, 1.0) * tint.a;
}
"""

## Fresnel shell for the EMP field: faint translucent body, bright rim, additive.
const EMP_SHELL_SHADER := """shader_type spatial;
render_mode blend_add, unshaded, cull_disabled, depth_draw_never, shadows_disabled;
uniform vec4 tint : source_color = vec4(0.3, 0.55, 1.0, 1.0);
void fragment() {
	float rim = pow(1.0 - abs(dot(normalize(NORMAL), normalize(VIEW))), 2.2);
	ALBEDO = tint.rgb;
	ALPHA = (0.1 + rim * 0.9) * tint.a;
}
"""

