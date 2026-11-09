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


func has_preset(preset: String) -> bool:
	return _pools.has(preset)


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


func _process(_delta: float) -> void:
	if _warm_frames <= 0:
		return
	_warm_frames -= 1
	if _warm_frames == 0:
		for node: Node3D in _warm:
			node.queue_free()
		_warm.clear()
