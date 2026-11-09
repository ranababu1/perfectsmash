class_name MissionView
extends Node3D
## Greybox 3D presentation of a MissionWorld, seen through a tilted three-quarter camera.
## Every component is its physics rectangle extruded in depth (front face = collision shape), so
## the picture never implies collisions the 2D simulation does not have. Owns no game rules:
## it mirrors bodies each frame and reacts to world/engine signals with simple VFX.

## Greybox look per component kind: [depth (m), colour, emission colour or null, emission energy].
## The AI core is the only white/red object so the critical asset reads instantly.
const KINDS := {
	"server_rack": [0.8, Color("39424c"), Color("2f8fa3"), 0.25],
	"support_column": [0.5, Color("6b737c"), null, 0.0],
	"service_deck": [1.4, Color("5a6068"), null, 0.0],
	"ai_core": [0.7, Color("d9dde2"), Color("ff3b4e"), 1.2],
	"core_shield": [0.9, Color("80878f"), null, 0.0],
	"power_cell": [0.5, Color("4a4238"), Color("ffae42"), 0.7],
	"blast_wall": [1.2, Color("717880"), null, 0.0],
	"relay_mast": [0.3, Color("5d656e"), null, 0.0],
	"relay_dish": [0.8, Color("8fb6c4"), null, 0.0],
}
const DEFAULT_KIND := [0.8, Color("5a6068"), null, 0.0]
const MARKER_COLOR := Color("ff3b4e")
const MARKER_HEIGHT := 0.75
const STATIC_DEPTH := 1.6
const CAMERA_FOV := 40.0
## Camera placement relative to the framed point: slightly left, raised, pulled back.
const CAMERA_OFFSET := Vector3(-2.2, 2.3, 10.5)
const PREVIEW_DOTS := 14

var world: MissionWorld
var definition: MissionDefinition
var camera: Camera3D
var operative: OperativeRig
var _meshes := {}
var _materials := {}
var _projectiles := {}
var _preview: MultiMeshInstance3D
## critical asset id -> floating target marker
var _markers := {}
var _time := 0.0


func setup(p_world: MissionWorld) -> void:
	world = p_world
	definition = world.definition
	_build_environment()
	_build_camera()
	for s in definition.statics:
		_add_box(ViewMapping.size_to_3d(s.size, STATIC_DEPTH), _flat(Color("4b5158")), ViewMapping.to_3d(s.position, definition.ground_y), s.rotation)
	for c in definition.components:
		_add_component(c)
	operative = OperativeRig.new()
	operative.position = ViewMapping.to_3d(definition.operative, definition.ground_y, 0.3)
	add_child(operative)
	_build_preview()

	world.projectile_spawned.connect(_on_projectile_spawned)
	world.projectile_removed.connect(_on_projectile_removed)
	world.component_removed.connect(_on_component_removed)
	world.blast_happened.connect(_on_blast)
	world.impact_happened.connect(_on_impact)
	world.engine.component_state_changed.connect(_on_component_state_changed)
	_warm_up_effects()


## The first blast flash (alpha-blended) and its omni light need shader variants that nothing
## else in the scene uses; compiling them on the first detonation stalled that frame by
## 0.5-1.1 s on the Android emulator (renderer evaluation, 2026-11-10). Show both once,
## invisibly (zero alpha, near-zero light energy over the facility), while the mission loads,
## so that cost is paid up front. Debris and sparks warm up the same way.
func _warm_up_effects() -> void:
	var centre := ViewMapping.to_3d(Vector2(definition.width / 2.0, definition.ground_y - 150.0), definition.ground_y)
	_spawn_flash(centre, 4.0, 0.0, 0.001)
	# Particles just under the ground surface: drawn (so compiled) but hidden, and not moving.
	var hidden := ViewMapping.to_3d(Vector2(definition.width / 2.0, definition.ground_y + 60.0), definition.ground_y)
	for particles: CPUParticles3D in [_spawn_sparks(hidden), _spawn_debris(hidden, Color.BLACK, Vector3.ONE * 0.1)]:
		particles.initial_velocity_min = 0.0
		particles.initial_velocity_max = 0.0
		particles.gravity = Vector3.ZERO


## The point in the 2D physics plane under a screen position (null if the ray misses it).
func screen_to_plane(screen_position: Vector2) -> Variant:
	var origin := camera.project_ray_origin(screen_position)
	var direction := camera.project_ray_normal(screen_position)
	var hit: Variant = Plane(Vector3.BACK, 0.0).intersects_ray(origin, direction)
	if hit == null:
		return null
	return ViewMapping.to_2d(hit, definition.ground_y)


func plane_to_screen(point: Vector2) -> Vector2:
	return camera.unproject_position(ViewMapping.to_3d(point, definition.ground_y))


## Shows the predicted path for a launch velocity (empty array hides it).
func show_preview(start: Vector2, velocity: Vector2, gravity_scale: float, seconds: float) -> void:
	var gravity := float(ProjectSettings.get_setting("physics/2d/default_gravity", 980.0)) * gravity_scale
	var multimesh := _preview.multimesh
	multimesh.visible_instance_count = PREVIEW_DOTS
	for i in PREVIEW_DOTS:
		var t := seconds * float(i + 1) / PREVIEW_DOTS
		var p := start + velocity * t + Vector2(0.0, 0.5 * gravity * t * t)
		var scale := lerpf(1.0, 0.45, float(i) / PREVIEW_DOTS)
		multimesh.set_instance_transform(i, Transform3D(Basis.from_scale(Vector3.ONE * scale), ViewMapping.to_3d(p, definition.ground_y, 0.05)))
	_preview.visible = true


func hide_preview() -> void:
	_preview.visible = false


func _process(delta: float) -> void:
	_time += delta
	for id: String in _markers.keys():
		var core := world.body_for(id)
		var marker: MeshInstance3D = _markers[id]
		if core == null:
			continue
		var top := ViewMapping.to_3d(core.global_position, definition.ground_y)
		marker.position = top + Vector3(0.0, core.size.y / ViewMapping.PX_PER_METRE / 2.0 + MARKER_HEIGHT + sin(_time * 3.0) * 0.06, 0.0)
		marker.rotation.y = _time * 1.5
		var material: StandardMaterial3D = _materials[id][0]
		material.emission_energy_multiplier = 1.0 + sin(_time * 4.0) * 0.4
	for id: String in _meshes.keys():
		var body := world.body_for(id)
		var mesh: MeshInstance3D = _meshes[id]
		if body == null:
			continue
		mesh.position = ViewMapping.to_3d(body.global_position, definition.ground_y)
		mesh.rotation = ViewMapping.rotation_to_3d(body.global_rotation)
	for projectile: WeaponProjectile in _projectiles.keys():
		if is_instance_valid(projectile):
			(_projectiles[projectile] as Node3D).position = ViewMapping.to_3d(projectile.global_position, definition.ground_y)


func _build_environment() -> void:
	var env := Environment.new()
	env.background_mode = Environment.BG_COLOR
	env.background_color = Color("15191e")
	env.ambient_light_source = Environment.AMBIENT_SOURCE_COLOR
	env.ambient_light_color = Color("8090a0")
	env.ambient_light_energy = 0.55
	env.tonemap_mode = Environment.TONE_MAPPER_FILMIC
	var world_env := WorldEnvironment.new()
	world_env.environment = env
	add_child(world_env)

	var sun := DirectionalLight3D.new()
	sun.rotation_degrees = Vector3(-52.0, -38.0, 0.0)
	sun.light_energy = 1.15
	sun.light_color = Color("dfe8f0")
	sun.shadow_enabled = true
	sun.directional_shadow_max_distance = 40.0
	add_child(sun)

	var width_m := definition.width / ViewMapping.PX_PER_METRE
	# Floor: a slab whose top is the physics ground line.
	_add_box(Vector3(width_m + 30.0, 0.4, 14.0), _flat(Color("23282e")), Vector3(width_m / 2.0, -0.2, -2.0), 0.0)
	# Low-contrast facility backdrop: back wall and a few distant blocks.
	_add_box(Vector3(width_m + 30.0, 9.0, 0.4), _flat(Color("1b2026")), Vector3(width_m / 2.0, 4.5, -6.0), 0.0)
	var rng := RandomNumberGenerator.new()
	rng.seed = hash(definition.id)
	for i in 9:
		var w := rng.randf_range(1.2, 3.0)
		var h := rng.randf_range(2.0, 6.5)
		_add_box(Vector3(w, h, 1.0), _flat(Color("20262c")), Vector3(rng.randf_range(-2.0, width_m + 2.0), h / 2.0, -5.0), 0.0)


func _build_camera() -> void:
	camera = Camera3D.new()
	camera.fov = CAMERA_FOV
	var left := minf(definition.operative.x, _facility_left())
	var right := _facility_right()
	var focus := Vector3((left + right) / 2.0 / ViewMapping.PX_PER_METRE, 1.6, 0.0)
	camera.position = focus + CAMERA_OFFSET
	add_child(camera)
	camera.look_at(focus + Vector3(0.0, -0.4, 0.0), Vector3.UP)
	camera.current = true


func _facility_left() -> float:
	var x := INF
	for c in definition.components:
		x = minf(x, c.position.x - c.size.x / 2.0)
	return x


func _facility_right() -> float:
	var x := -INF
	for c in definition.components:
		x = maxf(x, c.position.x + c.size.x / 2.0)
	return x


func _build_preview() -> void:
	var dot := SphereMesh.new()
	dot.radius = 0.05
	dot.height = 0.1
	var multimesh := MultiMesh.new()
	multimesh.transform_format = MultiMesh.TRANSFORM_3D
	multimesh.mesh = dot
	multimesh.instance_count = PREVIEW_DOTS
	_preview = MultiMeshInstance3D.new()
	_preview.multimesh = multimesh
	var material := _flat(Color("bfefff"))
	material.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
	_preview.material_override = material
	_preview.visible = false
	add_child(_preview)


func _add_component(c: Dictionary) -> void:
	var look: Array = KINDS.get(c.kind, DEFAULT_KIND)
	var material := _flat(look[1])
	if look[2] != null:
		material.emission_enabled = true
		material.emission = look[2]
		material.emission_energy_multiplier = look[3]
	var mesh := _add_box(ViewMapping.size_to_3d(c.size, look[0]), material, ViewMapping.to_3d(c.position, definition.ground_y), c.rotation)
	_meshes[c.id] = mesh
	_materials[c.id] = [material, look[1]]
	if c.critical_asset:
		_markers[c.id] = _add_marker()


## A floating, slowly turning red pointer above a critical asset.
func _add_marker() -> MeshInstance3D:
	var marker := MeshInstance3D.new()
	var prism := PrismMesh.new()
	prism.size = Vector3(0.28, 0.3, 0.28)
	marker.mesh = prism
	marker.rotation = Vector3(PI, 0.0, 0.0)
	var material := StandardMaterial3D.new()
	material.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
	material.albedo_color = MARKER_COLOR
	marker.material_override = material
	add_child(marker)
	return marker


func _add_box(size: Vector3, material: Material, at: Vector3, rotation_2d: float) -> MeshInstance3D:
	var mesh := MeshInstance3D.new()
	var box := BoxMesh.new()
	box.size = size
	mesh.mesh = box
	mesh.material_override = material
	mesh.position = at
	mesh.rotation = ViewMapping.rotation_to_3d(rotation_2d)
	add_child(mesh)
	return mesh


static func _flat(color: Color) -> StandardMaterial3D:
	var material := StandardMaterial3D.new()
	material.albedo_color = color
	material.roughness = 0.75
	material.metallic = 0.25
	return material


func _on_component_state_changed(component_id: String, _previous: int, current: int) -> void:
	if not _materials.has(component_id):
		return
	var material: StandardMaterial3D = _materials[component_id][0]
	var base: Color = _materials[component_id][1]
	match current:
		DamageableComponent.State.DAMAGED:
			material.albedo_color = base.darkened(0.25)
		DamageableComponent.State.CRITICAL:
			material.albedo_color = base.darkened(0.45)
			material.emission_enabled = true
			material.emission = Color("ff4a30")
			material.emission_energy_multiplier = 0.8


func _on_component_removed(component_id: String, at: Vector2) -> void:
	var mesh: MeshInstance3D = _meshes.get(component_id)
	_meshes.erase(component_id)
	if _markers.has(component_id):
		(_markers[component_id] as Node).queue_free()
		_markers.erase(component_id)
	if mesh == null:
		return
	var color: Color = _materials[component_id][1]
	_spawn_debris(ViewMapping.to_3d(at, definition.ground_y), color, (mesh.mesh as BoxMesh).size)
	mesh.queue_free()


func _on_projectile_spawned(projectile: WeaponProjectile) -> void:
	var mesh := MeshInstance3D.new()
	var sphere := SphereMesh.new()
	var radius := float(projectile.stats.projectile_radius) / ViewMapping.PX_PER_METRE
	sphere.radius = radius
	sphere.height = radius * 2.0
	mesh.mesh = sphere
	var lobbed := projectile.weapon_id == "breach_charge"
	var material := _flat(Color("e0a040") if lobbed else Color("bdf4ff"))
	material.emission_enabled = true
	material.emission = material.albedo_color
	material.emission_energy_multiplier = 1.6
	mesh.material_override = material
	mesh.position = ViewMapping.to_3d(projectile.global_position, definition.ground_y)
	add_child(mesh)
	_projectiles[projectile] = mesh


func _on_projectile_removed(projectile: WeaponProjectile) -> void:
	var mesh: Node3D = _projectiles.get(projectile)
	_projectiles.erase(projectile)
	if mesh != null:
		mesh.queue_free()


func _on_blast(center: Vector2, radius: float) -> void:
	_spawn_flash(ViewMapping.to_3d(center, definition.ground_y), radius / ViewMapping.PX_PER_METRE * 2.0, 0.7, 4.0)


func _spawn_flash(at: Vector3, size: float, alpha: float, light_energy: float) -> void:
	var flash := MeshInstance3D.new()
	var sphere := SphereMesh.new()
	sphere.radius = 0.5
	sphere.height = 1.0
	flash.mesh = sphere
	var material := StandardMaterial3D.new()
	material.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
	material.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
	material.albedo_color = Color(1.0, 0.72, 0.35, alpha)
	flash.material_override = material
	flash.position = at
	add_child(flash)
	var tween := flash.create_tween().set_parallel()
	tween.tween_property(flash, "scale", Vector3.ONE * size, 0.3).from(Vector3.ONE * 0.2)
	tween.tween_property(material, "albedo_color:a", 0.0, 0.35)
	tween.chain().tween_callback(flash.queue_free)
	var light := OmniLight3D.new()
	light.light_color = Color("ffb060")
	light.light_energy = light_energy
	light.omni_range = size * 1.5
	light.position = at + Vector3(0, 0, 0.8)
	add_child(light)
	light.create_tween().tween_property(light, "light_energy", 0.0, 0.3).finished.connect(light.queue_free)


func _on_impact(at: Vector2, strength: float, _component_id: String) -> void:
	if strength < 400.0:
		return
	_spawn_sparks(ViewMapping.to_3d(at, definition.ground_y, 0.3))


func _spawn_sparks(at: Vector3) -> CPUParticles3D:
	var sparks := CPUParticles3D.new()
	sparks.one_shot = true
	sparks.amount = 14
	sparks.lifetime = 0.35
	sparks.explosiveness = 1.0
	sparks.spread = 180.0
	sparks.initial_velocity_min = 2.0
	sparks.initial_velocity_max = 5.0
	var dot := SphereMesh.new()
	dot.radius = 0.025
	dot.height = 0.05
	sparks.mesh = dot
	var material := StandardMaterial3D.new()
	material.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
	material.albedo_color = Color("ffd890")
	sparks.material_override = material
	sparks.position = at
	add_child(sparks)
	sparks.emitting = true
	sparks.finished.connect(sparks.queue_free)
	return sparks


func _spawn_debris(at: Vector3, color: Color, size: Vector3) -> CPUParticles3D:
	var debris := CPUParticles3D.new()
	debris.one_shot = true
	debris.amount = 10
	debris.lifetime = 0.9
	debris.explosiveness = 0.9
	debris.spread = 70.0
	debris.direction = Vector3.UP
	debris.initial_velocity_min = 1.5
	debris.initial_velocity_max = 3.5
	debris.gravity = Vector3(0, -9.8, 0)
	var chunk := BoxMesh.new()
	chunk.size = Vector3.ONE * clampf(minf(size.x, size.y) * 0.35, 0.05, 0.18)
	debris.mesh = chunk
	debris.material_override = _flat(color.darkened(0.2))
	debris.position = at
	add_child(debris)
	debris.emitting = true
	debris.finished.connect(debris.queue_free)
	return debris
