class_name MissionView
extends Node3D
## 3D presentation of a MissionWorld, seen through a tilted three-quarter camera. Components use
## the integrated production models (AssetLibrary, data/integrated_assets.json) and fall back to
## greybox boxes: either way the front face is the physics rectangle, so the picture never implies
## collisions the 2D simulation does not have. The set dressing comes from
## data/environments/<mission id>.json. Owns no game rules: it mirrors bodies each frame and
## reacts to world/engine signals with VFX: the ui-vfx presets through MissionVfx, debris sets
## (DebrisSet) for destroyed components, and the procedural sparks/flash/chunks as fallback when
## an asset is not integrated.

## Greybox look per component kind: [depth (m), colour, emission colour or null, emission energy].
## Depths also apply to production models (ASSET_CONTRACT 3); colours are the greybox fallback.
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
## Aim-preview dot colour per weapon (the weapon's colour language); others use the default.
const PREVIEW_COLOURS := {
	"kinetic_accelerator": Color("bfefff"), "breach_charge": Color("ffc870"), "penetrator": Color("f4ffff"),
	"pulse_cannon": Color("ffa22e"), "disruptor": Color("6da2ff"), "temporal_lance": Color("c4a2ff"),
}
## Blast flash tint and light per weapon: [flash colour, light energy]; no entry = the Breach look.
## The Disruptor EMP is a shock field, not a fire: no flash sphere and no light.
const BLAST_LOOKS := {
	"pulse_cannon": [Color(1.0, 0.62, 0.2), 2.5],
	"disruptor": [Color(0.3, 0.55, 1.0), 0.0],
}
## Blast lights are a fixed pool created with the view and reused: adding or freeing an
## OmniLight3D per detonation cost about 300 ms per blast on GL Compatibility (Android emulator,
## spike log 2026-11-10). Idle lights keep a tiny energy so they are never culled and the set of
## lights the renderer sees never changes.
const BLAST_LIGHTS := 2
const BLAST_LIGHT_IDLE_ENERGY := 0.01
const BLAST_LIGHT_COLOR := Color("ffb060")
const ENVIRONMENT_DIR := "res://data/environments"
const SUN_PITCH := -36.0
const SUN_YAW := -30.0
const FOG_DENSITY := 0.85
const FOG_DEPTH_BEGIN := 12.0
const FOG_DEPTH_END := 18.0
## Folder holding <mission id>.json set files. Tools (tools/chapter_preview) point it at their own
## sets; the game always uses ENVIRONMENT_DIR.
static var environment_dir := ENVIRONMENT_DIR

var world: MissionWorld
var definition: MissionDefinition
var camera: Camera3D
var operative: OperativeRig
## component id -> ComponentVisual
var _meshes := {}
var _projectiles := {}
## Integrated production assets, loaded once and shared by every mission view.
static var _library: AssetLibrary


static func assets() -> AssetLibrary:
	if _library == null:
		_library = AssetLibrary.load_from_file()
	return _library
## Chapter key of the mission's set ("" when the mission has no environment file).
var chapter := ""
## Asset ids placed by the environment file (set dressing and statics), for reports and tests.
var placed_pieces: Array[String] = []
## The mission's set (environment, sun, set dressing, statics). Purely visual and identical on
## every attempt, so it is kept across restarts of the same mission instead of being rebuilt:
## rebuilding it re-created the sky radiance, shadow light, MultiMesh buffers and materials,
## ~650 ms per restart on the Android emulator (slice E).
var set_root: Node3D
## True when this view reused the previous attempt's set.
var reused_set := false
static var _cached_set: Node3D
static var _cached_set_key := ""
static var _cached_set_info := {}
var _preview: MultiMeshInstance3D
## critical asset id -> floating target marker
var _markers := {}
## Projectile meshes, trails and the breach arming light: ProjectileVisual (contract 11).
## False when the HUD draws the critical-asset marker (GAM-ICN-CRITICAL_ASSET) instead.
var world_markers := true
var _time := 0.0
## Renderer-evaluation switch (tools/renderer_eval): false builds no blast lights at all.
static var blast_lights_enabled := true
var _blast_lights: Array[OmniLight3D] = []
var _next_blast_light := 0
## Pooled blast flashes [MeshInstance3D, StandardMaterial3D]: creating a transparent flash per
## detonation cost ~300 ms per blast on GL Compatibility (emulator spike log, lights disabled).
var _blast_flashes := []
var _next_blast_flash := 0
## Preset effects (pools); `has_preset` false -> procedural fallback.
var vfx: MissionVfx
## Asset ids of the debris sets spawned so far, for reports and tests.
var debris_spawned: Array[String] = []
## component id -> physics material id (selects impact effects).
var _material_of := {}
## Point the camera frames (view space).
var _focus := Vector3.ZERO
## Debris sets drawn once under the floor while the mission loads (shader warm-up).
var _warm_nodes: Array[Node3D] = []
var _warm_frames := 0
const WARM_FRAMES := 3
## Hard impacts below this strength (px/s or impulse) show no effect.
const IMPACT_EFFECT_MIN := 400.0
const CRYSTAL_AURA := Color("c27dff")
const SHIELD_AURA := Color("5fd4ff")


func setup(p_world: MissionWorld) -> void:
	world = p_world
	definition = world.definition
	if _library == null:
		_library = AssetLibrary.load_from_file()
	_attach_set()
	_build_camera()
	vfx = MissionVfx.new()
	vfx.name = "MissionVfx"
	add_child(vfx)
	vfx.setup(_library, _focus.x)
	for c in definition.components:
		_add_component(c)
	world.engine.shield_dropped.connect(_on_shield_dropped)
	operative = OperativeRig.new()
	operative.library = _library
	operative.weapon_id = world.engine.selected_weapon_id
	operative.position = ViewMapping.to_3d(definition.operative, definition.ground_y, 0.3)
	add_child(operative)
	_build_preview()

	world.projectile_spawned.connect(_on_projectile_spawned)
	world.projectile_removed.connect(_on_projectile_removed)
	world.component_removed.connect(_on_component_removed)
	world.blast_happened.connect(_on_blast)
	world.engine.weapon_selected.connect(operative.set_weapon)
	world.impact_happened.connect(_on_impact)
	world.engine.component_state_changed.connect(_on_component_state_changed)
	_build_blast_lights()
	_warm_up_effects()


## Reuses the cached set when it was built for this mission, else builds it.
func _attach_set() -> void:
	var key := _set_key()
	if _cached_set != null and is_instance_valid(_cached_set) and _cached_set_key == key:
		set_root = _cached_set
		_cached_set = null
		chapter = str(_cached_set_info.chapter)
		placed_pieces = _cached_set_info.placed.duplicate()
		add_child(set_root)
		reused_set = true
		return
	release_cached_set()
	set_root = Node3D.new()
	set_root.name = "Set"
	add_child(set_root)
	_build_environment()
	var set_data := _environment_data()
	for s in definition.statics:
		if not _add_static_piece(s, set_data):
			_add_box(ViewMapping.size_to_3d(s.size, STATIC_DEPTH), _flat(Color("4b5158")), ViewMapping.to_3d(s.position, definition.ground_y), s.rotation)


func _set_key() -> String:
	return "%s|%s|%s" % [environment_dir, definition.id, _library.get_instance_id() if _library != null else 0]


func _notification(what: int) -> void:
	# The app root removes the old screen (synchronously) before building the next attempt, so
	# the set is handed over on leaving the tree; freeing without leaving it does the same.
	if what == NOTIFICATION_EXIT_TREE or what == NOTIFICATION_PREDELETE:
		_stash_set()
	elif what == NOTIFICATION_ENTER_TREE and set_root != null and set_root == _cached_set:
		# Back in the tree (not a restart): take the set back.
		_cached_set = null
		add_child(set_root)


func _stash_set() -> void:
	if set_root == null or not is_instance_valid(set_root) or set_root == _cached_set:
		return
	if set_root.get_parent() != null and set_root.get_parent() != self:
		set_root = null  # the next attempt's view already has it
		return
	if set_root.get_parent() == self:
		remove_child(set_root)
	release_cached_set()
	_cached_set = set_root
	_cached_set_key = _set_key()
	_cached_set_info = {"chapter": chapter, "placed": placed_pieces.duplicate()}
	if is_queued_for_deletion() or definition == null:
		set_root = null


## Frees the set kept for the next attempt (leaving missions, quitting, tests).
static func release_cached_set() -> void:
	if _cached_set != null and is_instance_valid(_cached_set):
		_cached_set.free()
	_cached_set = null
	_cached_set_key = ""
	_cached_set_info = {}


func _build_blast_lights() -> void:
	var centre := ViewMapping.to_3d(Vector2(definition.width / 2.0, definition.ground_y - 150.0), definition.ground_y)
	var sphere := SphereMesh.new()
	sphere.radius = 0.5
	sphere.height = 1.0
	for i in BLAST_LIGHTS:
		var flash := MeshInstance3D.new()
		flash.mesh = sphere
		var material := StandardMaterial3D.new()
		material.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
		material.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
		material.albedo_color = Color(1.0, 0.72, 0.35, 0.0)
		flash.material_override = material
		flash.position = centre
		flash.scale = Vector3.ONE * 0.2
		add_child(flash)
		_blast_flashes.append([flash, material])
	if not blast_lights_enabled:
		return
	for i in BLAST_LIGHTS:
		var light := OmniLight3D.new()
		light.light_color = BLAST_LIGHT_COLOR
		light.light_energy = BLAST_LIGHT_IDLE_ENERGY
		light.omni_range = 4.0
		light.position = centre + Vector3(0, 0, 0.8)
		add_child(light)
		_blast_lights.append(light)


## Effects first used mid-play compiled shaders then: 0.5-1.1 s on the first detonation on the
## Android emulator (renderer evaluation, 2026-11-10). Blast flashes and lights are persistent
## pools (always drawn, so compiled with the mission); debris and sparks are shown once here,
## hidden, while the mission loads.
func _warm_up_effects() -> void:
	# Particles just under the ground surface: drawn (so compiled) but hidden, and not moving.
	var hidden := ViewMapping.to_3d(Vector2(definition.width / 2.0, definition.ground_y + 60.0), definition.ground_y)
	for particles: CPUParticles3D in [_spawn_sparks(hidden), _spawn_debris(hidden, Color.BLACK, Vector3.ONE * 0.1)]:
		particles.initial_velocity_min = 0.0
		particles.initial_velocity_max = 0.0
		particles.gravity = Vector3.ZERO
	# One debris set per kind in the mission, motionless under the floor for a few frames.
	if _library == null:
		return
	var warmed := {}
	for c in definition.components:
		var entry := _library.debris_entry(chapter, c.kind, c.size)
		if entry.is_empty() or warmed.has(entry.id):
			continue
		warmed[entry.id] = true
		var model := _library.instance_debris(chapter, c.kind, c.size)
		if model == null:
			continue
		model.position = Vector3(_focus.x, -1.2, 0.0)
		add_child(model)
		_warm_nodes.append(model)
	# Both projectile looks (meshes, trails, arming and activation sprites), so the first shot of
	# each weapon compiles nothing mid-play.
	for weapon_id: String in ProjectileVisual.ASSETS:
		if not world.engine.weapons.has(weapon_id):
			continue
		var probe := WeaponProjectile.new(weapon_id, world.engine.weapons[weapon_id].stats, Vector2.ZERO, Vector2(1000.0, 0.0))
		var warm := ProjectileVisual.create(probe, _library)
		probe.free()
		add_child(warm)
		warm.park(Vector3(_focus.x, -0.6, 0.0))
		_warm_nodes.append(warm)
	_warm_frames = WARM_FRAMES


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
	(_preview.material_override as StandardMaterial3D).albedo_color = PREVIEW_COLOURS.get(operative.weapon_id, PREVIEW_COLOURS.kinetic_accelerator)
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
	if _warm_frames > 0:
		_warm_frames -= 1
		if _warm_frames == 0:
			for node: Node3D in _warm_nodes:
				node.queue_free()
			_warm_nodes.clear()
	for id: String in _markers.keys():
		var core := world.body_for(id)
		var marker: MeshInstance3D = _markers[id]
		if core == null:
			continue
		var top := ViewMapping.to_3d(core.global_position, definition.ground_y)
		marker.position = top + Vector3(0.0, core.size.y / ViewMapping.PX_PER_METRE / 2.0 + MARKER_HEIGHT + sin(_time * 3.0) * 0.06, 0.0)
		vfx.move_core_idle(id, top + Vector3(0.0, 0.0, 0.4))
		marker.rotation.y = _time * 1.5
		marker.visible = world_markers
	for id: String in _meshes.keys():
		var body := world.body_for(id)
		var visual: ComponentVisual = _meshes[id]
		if body == null:
			continue
		visual.position = ViewMapping.to_3d(body.global_position, definition.ground_y)
		visual.rotation = ViewMapping.rotation_to_3d(body.global_rotation)
		visual.animate(_time)
	for projectile: WeaponProjectile in _projectiles.keys():
		if is_instance_valid(projectile):
			(_projectiles[projectile] as ProjectileVisual).follow(projectile, definition.ground_y, delta)


## Screen position of the marker point above a critical asset (null when it is gone or behind
## the camera), for the HUD's critical-asset marker.
func marker_screen_position(component_id: String) -> Variant:
	var core := world.body_for(component_id)
	if core == null:
		return null
	var top := ViewMapping.to_3d(core.global_position, definition.ground_y) + Vector3(0.0, core.size.y / ViewMapping.PX_PER_METRE / 2.0 + MARKER_HEIGHT, 0.0)
	if camera.is_position_behind(top):
		return null
	return camera.unproject_position(top)


func _build_environment() -> void:
	var has_set := not _environment_data().is_empty()
	var env := Environment.new()
	env.background_mode = Environment.BG_COLOR
	env.background_color = Color("15191e")
	env.ambient_light_source = Environment.AMBIENT_SOURCE_COLOR
	env.ambient_light_color = Color("8090a0")
	env.ambient_light_energy = 0.55
	env.tonemap_mode = Environment.TONE_MAPPER_FILMIC
	var atmosphere := ChapterAtmosphere.for_theme(str(_environment_data().get("chapter", "helix")))
	if has_set:
		# Production set: the chapter's palette (data/atmospheres.json; Helix keeps the approved
		# slice-E graphite hall): fill, a reflection-only sky so metals read as metal
		# (ASSET_CONTRACT 9), and depth fog so the back recedes.
		atmosphere.apply_environment(env)
		# Depth fog from just behind the gameplay plane (camera ~10.5 m away) to the back wall:
		# the facility stays crisp and the hall behind it recedes (slice E; the earlier
		# exponential fog hazed the gameplay plane ~30% and the back wall barely more).
		env.fog_enabled = true
		env.fog_mode = Environment.FOG_MODE_DEPTH
		env.fog_depth_begin = FOG_DEPTH_BEGIN
		env.fog_depth_end = FOG_DEPTH_END
		env.fog_depth_curve = 1.0
		env.fog_sky_affect = 0.0
	var world_env := WorldEnvironment.new()
	world_env.environment = env
	set_root.add_child(world_env)

	var sun := DirectionalLight3D.new()
	sun.rotation_degrees = Vector3(SUN_PITCH, SUN_YAW, 0.0)
	sun.light_energy = 1.0 if has_set else 1.15
	sun.light_color = Color("dfe8f0")
	sun.shadow_enabled = true
	sun.directional_shadow_max_distance = 40.0
	if has_set:
		atmosphere.apply_sun(sun)
		var rim := atmosphere.make_rim()
		if rim != null:
			set_root.add_child(rim)
	set_root.add_child(sun)

	if _build_set():
		return
	var width_m := definition.width / ViewMapping.PX_PER_METRE
	# Greybox fallback. Floor: a slab whose top is the physics ground line.
	_add_box(Vector3(width_m + 30.0, 0.4, 14.0), _flat(Color("23282e")), Vector3(width_m / 2.0, -0.2, -2.0), 0.0)
	# Low-contrast facility backdrop: back wall and a few distant blocks.
	_add_box(Vector3(width_m + 30.0, 9.0, 0.4), _flat(Color("1b2026")), Vector3(width_m / 2.0, 4.5, -6.0), 0.0)
	var rng := RandomNumberGenerator.new()
	rng.seed = hash(definition.id)
	for i in 9:
		var w := rng.randf_range(1.2, 3.0)
		var h := rng.randf_range(2.0, 6.5)
		_add_box(Vector3(w, h, 1.0), _flat(Color("20262c")), Vector3(rng.randf_range(-2.0, width_m + 2.0), h / 2.0, -5.0), 0.0)


func _environment_data() -> Dictionary:
	var path := "%s/%s.json" % [environment_dir, definition.id]
	if not FileAccess.file_exists(path):
		return {}
	var data: Variant = JSON.parse_string(FileAccess.get_file_as_string(path))
	return data if data is Dictionary else {}


## Places the mission's set dressing from data/environments/<id>.json. Returns false (greybox
## backdrop instead) when there is no file or none of its pieces is integrated.
func _build_set() -> bool:
	var data := _environment_data()
	if data.is_empty() or _library == null:
		return false
	chapter = str(data.get("chapter", ""))
	var placed := 0
	for piece: Variant in data.get("pieces", []):
		if not piece is Dictionary:
			continue
		var xs: Array = []
		if piece.has("repeat"):
			var r: Dictionary = piece.repeat
			var x := float(r.x_from)
			while x <= float(r.x_to) + 0.001:
				xs.append(x)
				x += float(r.step)
		else:
			xs.append(float(piece.get("x", 0.0)))
		var transforms: Array[Transform3D] = []
		for x: float in xs:
			var basis := Basis(Vector3.UP, deg_to_rad(float(piece.get("rot", 0.0)))).scaled(Vector3.ONE * float(piece.get("scale", 1.0)))
			transforms.append(Transform3D(basis, Vector3(x, float(piece.get("y", 0.0)), float(piece.get("z", 0.0)))))
		var shadows: bool = piece.get("shadows", true)
		var count := _place_piece(str(piece.id), transforms, shadows)
		for i in count:
			placed_pieces.append(str(piece.id))
		placed += count
	return placed > 0


## Places one set piece at each transform. Repeated pieces become one MultiMeshInstance3D per
## mesh in the piece, so a row of 11 floor tiles costs its surface count in draw calls instead
## of 11 times that (slice A measured ~1,800 draw calls with one node per piece). Returns the
## number placed.
func _place_piece(asset_id: String, transforms: Array[Transform3D], shadows: bool) -> int:
	var template := _library.instance_piece(asset_id, chapter)
	if template == null:
		return 0
	var cast := GeometryInstance3D.SHADOW_CASTING_SETTING_ON if shadows else GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	if transforms.size() == 1:
		template.transform = transforms[0]
		set_root.add_child(template)
		for mesh_instance: MeshInstance3D in template.find_children("*", "MeshInstance3D", true, false):
			mesh_instance.cast_shadow = cast
		return 1
	for mesh_instance: MeshInstance3D in template.find_children("*", "MeshInstance3D", true, false):
		if not mesh_instance.visible or mesh_instance.mesh == null:
			continue
		var local := _relative_transform(template, mesh_instance)
		var mesh := mesh_instance.mesh
		# Bake per-surface overrides into a copy of the mesh so the MultiMesh draws them.
		var overridden := false
		for surface in mesh.get_surface_count():
			if mesh_instance.get_surface_override_material(surface) != null:
				overridden = true
		if overridden:
			mesh = mesh.duplicate()
			for surface in mesh.get_surface_count():
				var material := mesh_instance.get_surface_override_material(surface)
				if material != null:
					mesh.surface_set_material(surface, material)
		var multimesh := MultiMesh.new()
		multimesh.transform_format = MultiMesh.TRANSFORM_3D
		multimesh.mesh = mesh
		multimesh.instance_count = transforms.size()
		for i in transforms.size():
			multimesh.set_instance_transform(i, transforms[i] * local)
		var batch := MultiMeshInstance3D.new()
		batch.name = "%s_batch" % asset_id
		batch.multimesh = multimesh
		batch.cast_shadow = cast
		set_root.add_child(batch)
	template.free()
	return transforms.size()


static func _relative_transform(root: Node3D, node: Node3D) -> Transform3D:
	var t := Transform3D.IDENTITY
	var current: Node = node
	while current != null and current != root:
		if current is Node3D:
			t = (current as Node3D).transform * t
		current = current.get_parent()
	return t


## A static ledge or plinth from the set's kit, scaled to the static rectangle (statics use the
## component pivot: centre of the rectangle, z = 0).
func _add_static_piece(s: Dictionary, data: Dictionary) -> bool:
	var kit: Dictionary = data.get("statics", {})
	if kit.is_empty() or _library == null:
		return false
	var low: bool = s.size.y / ViewMapping.PX_PER_METRE <= float(kit.get("low_max_height_m", 0.45))
	var asset_id := str(kit.get("low" if low else "tall", ""))
	var node := _library.instance_piece(asset_id, chapter)
	if node == null:
		return false
	var dims := _piece_size_m(asset_id)
	node.scale = Vector3(s.size.x / ViewMapping.PX_PER_METRE / dims.x, s.size.y / ViewMapping.PX_PER_METRE / dims.y, 1.0)
	node.position = ViewMapping.to_3d(s.position, definition.ground_y)
	node.rotation = ViewMapping.rotation_to_3d(s.rotation)
	set_root.add_child(node)
	placed_pieces.append(asset_id)
	return true


## Width and height in metres from a manifest entry's "dimensions" ("2.00 x 0.30 x 1.60 m").
func _piece_size_m(asset_id: String) -> Vector2:
	var text := str(_library.entries.get(asset_id, {}).get("dimensions", "1 x 1 x 1"))
	var parts := text.replace(" m", "").split(" x ")
	return Vector2(float(parts[0]), float(parts[1])) if parts.size() >= 2 else Vector2.ONE


func _build_camera() -> void:
	camera = Camera3D.new()
	camera.fov = CAMERA_FOV
	var left := minf(definition.operative.x, _facility_left())
	var right := _facility_right()
	var focus := Vector3((left + right) / 2.0 / ViewMapping.PX_PER_METRE, 1.6, 0.0)
	_focus = focus
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


func _on_shield_dropped(component_id: String) -> void:
	var visual: ComponentVisual = _meshes.get(component_id)
	if visual != null and is_instance_valid(visual):
		visual.remove_aura("shield")


func _add_component(c: Dictionary) -> void:
	var look: Array = KINDS.get(c.kind, DEFAULT_KIND)
	var visual := ComponentVisual.create(c, look, _library, chapter)
	visual.position = ViewMapping.to_3d(c.position, definition.ground_y)
	visual.rotation = ViewMapping.rotation_to_3d(c.rotation)
	add_child(visual)
	_meshes[c.id] = visual
	_material_of[c.id] = str(c.get("material", ""))
	# Rules that must read at a glance: Lance-only crystal and shield-protected pieces.
	if str(c.get("material", "")) == "temporal_crystal":
		visual.add_aura("crystal", CRYSTAL_AURA)
	if not (c.get("shielded_by", []) as Array).is_empty():
		visual.add_aura("shield", SHIELD_AURA)
	if c.critical_asset:
		_markers[c.id] = _add_marker()
		vfx.start_core_idle(c.id, _library, visual.position + Vector3(0.0, 0.0, 0.4))


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
	set_root.add_child(mesh)
	return mesh


static func _flat(color: Color) -> StandardMaterial3D:
	var material := StandardMaterial3D.new()
	material.albedo_color = color
	material.roughness = 0.75
	material.metallic = 0.25
	return material


func _on_component_state_changed(component_id: String, _previous: int, current: int) -> void:
	var visual: ComponentVisual = _meshes.get(component_id)
	if visual != null:
		visual.set_state(current)


func _on_component_removed(component_id: String, at: Vector2) -> void:
	var visual: ComponentVisual = _meshes.get(component_id)
	_meshes.erase(component_id)
	var at_3d := ViewMapping.to_3d(at, definition.ground_y)
	if _markers.has(component_id):
		(_markers[component_id] as Node).queue_free()
		_markers.erase(component_id)
		vfx.stop_core_idle(component_id)
		vfx.core_destroyed(at_3d + Vector3(0.0, 0.0, 0.4))
	if visual == null:
		return
	vfx.collapse(at_3d, visual.size_m.x)
	if not _spawn_debris_set(component_id, visual):
		_spawn_debris(at_3d, visual.base_color, visual.size_m)
	visual.queue_free()


## The library's debris set where the component was, with its last pose. False when none is
## integrated for the kind (caller falls back to procedural chunks).
func _spawn_debris_set(component_id: String, visual: ComponentVisual) -> bool:
	if _library == null:
		return false
	var model := _library.instance_debris(chapter, visual.kind, visual.size_px)
	if model == null:
		return false
	var entry := _library.debris_entry(chapter, visual.kind, visual.size_px)
	var debris := DebrisSet.create(model, visual.position, visual.rotation.z, component_id, str(entry.id))
	add_child(debris)
	debris_spawned.append(debris.asset_id)
	return true


func _on_projectile_spawned(projectile: WeaponProjectile) -> void:
	var visual := ProjectileVisual.create(projectile, _library)
	add_child(visual)
	visual.follow(projectile, definition.ground_y, 0.0)
	_projectiles[projectile] = visual
	if not projectile.weapon_id == "breach_charge":
		var flash_at: Vector3 = operative.muzzle.global_position if operative != null and operative.muzzle != null else visual.position
		vfx.weapon_muzzle(projectile.weapon_id, flash_at, ViewMapping.direction_angle(projectile.linear_velocity))
		projectile.struck.connect(_on_weapon_struck)


## Direct-fire strikes (every strike of a piercing round, and its final one). Blast weapons also
## get their discharge / EMP from `_on_blast`.
func _on_weapon_struck(projectile: WeaponProjectile, _target: Node, _impact_speed: float) -> void:
	var at := ViewMapping.to_3d(projectile.global_position, definition.ground_y, 0.3)
	match projectile.weapon_id:
		"penetrator":
			vfx.pierce_spark(at)
		"temporal_lance":
			vfx.lance_strike(at)
		"pulse_cannon", "disruptor":
			pass
		_:
			vfx.kinetic_hit(at)


func _on_projectile_removed(projectile: WeaponProjectile) -> void:
	var mesh: Node3D = _projectiles.get(projectile)
	_projectiles.erase(projectile)
	if mesh != null:
		mesh.queue_free()


## The weapon whose blast was last shown ("" for secondary blasts); MissionScreen reads it to pick
## the blast sound, since the blast signal itself names no weapon.
var last_blast_weapon := ""


func _on_blast(center: Vector2, radius: float) -> void:
	var at := ViewMapping.to_3d(center, definition.ground_y)
	last_blast_weapon = _blast_source(center, radius)
	if BLAST_LOOKS.has(last_blast_weapon):
		var look: Array = BLAST_LOOKS[last_blast_weapon]
		var shown := false
		if last_blast_weapon == "disruptor":
			shown = vfx.emp_burst(at + Vector3(0.0, 0.0, 0.3), radius)
		else:
			shown = vfx.pulse_discharge(at + Vector3(0.0, 0.0, 0.3), radius)
		_spawn_flash(at, radius / ViewMapping.PX_PER_METRE * 2.0, 0.0 if shown else 0.5, float(look[1]), look[0])
		return
	# With the preset the fireball replaces the flash sphere; the pooled light still lights the set.
	var preset := vfx.breach_explosion(at + Vector3(0.0, 0.0, 0.3), radius)
	_spawn_flash(at, radius / ViewMapping.PX_PER_METRE * 2.0, 0.0 if preset else 0.7, 4.0)


## The weapon that caused a blast: the struck projectile sitting at its centre; failing that the
## blast weapon whose radius matches; "" for a secondary (chain) blast.
func _blast_source(center: Vector2, radius: float) -> String:
	for projectile: WeaponProjectile in _projectiles.keys():
		if is_instance_valid(projectile) and projectile.has_struck() and projectile.global_position.distance_to(center) < 2.0:
			return projectile.weapon_id
	for id: String in world.engine.weapons:
		var stats: Dictionary = world.engine.weapons[id].stats
		if float(stats.blast_damage) > 0.0 and is_equal_approx(float(stats.blast_radius), radius):
			return id
	return ""


func _spawn_flash(at: Vector3, size: float, alpha: float, light_energy: float, tint: Color = Color(1.0, 0.72, 0.35)) -> void:
	if not _blast_flashes.is_empty():
		var entry: Array = _blast_flashes[_next_blast_flash]
		_next_blast_flash = (_next_blast_flash + 1) % _blast_flashes.size()
		var flash: MeshInstance3D = entry[0]
		var material: StandardMaterial3D = entry[1]
		flash.position = at
		material.albedo_color = Color(tint, alpha)
		var tween := flash.create_tween().set_parallel()
		tween.tween_property(flash, "scale", Vector3.ONE * size, 0.3).from(Vector3.ONE * 0.2)
		tween.tween_property(material, "albedo_color:a", 0.0, 0.35)
	if light_energy <= 0.0 or _blast_lights.is_empty():
		return
	var light := _blast_lights[_next_blast_light]
	_next_blast_light = (_next_blast_light + 1) % _blast_lights.size()
	light.omni_range = size * 1.5
	light.position = at + Vector3(0, 0, 0.8)
	light.light_energy = light_energy
	light.create_tween().tween_property(light, "light_energy", BLAST_LIGHT_IDLE_ENERGY, 0.3)


func _on_impact(at: Vector2, strength: float, component_id: String) -> void:
	if strength < IMPACT_EFFECT_MIN:
		return
	var at_3d := ViewMapping.to_3d(at, definition.ground_y, 0.3)
	if not vfx.impact(at_3d, _material_of.get(component_id, "")):
		_spawn_sparks(at_3d)


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
