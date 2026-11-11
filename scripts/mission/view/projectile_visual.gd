class_name ProjectileVisual
extends Node3D
## The 3D look of one WeaponProjectile, built from the integrated weapon assets with a greybox
## fallback (ASSET_CONTRACT 11 and 13):
## - the projectile mesh (OPR-PRJ-KINETIC_SLUG-A, OPR-PRJ-BREACH_CANISTER-A), scaled so its
##   cross-section matches the physics radius; the slug points along its velocity, the canister
##   tumbles with the physics body;
## - a velocity trail (OPR-VFX-KINETIC_TRAIL-A, about 0.06 s of travel; OPR-VFX-BREACH_TRAIL-A,
##   about 0.12 s), a camera-facing additive quad stretched back from the projectile;
## - for the Breach Charge, the looping arming light (OPR-VFX-BREACH_ARMING-A, 0.6 m) on the
##   canister and the one-shot activation flash (OPR-VFX-BREACH_ACTIVATION-A) at the launch point.
## The chapter II-V weapons have no projectile models, so their bodies are built from primitives
## (`shape`) and dressed with the shared VFX library, each in its own colour language:
## Penetrator = thin white-cyan dart and streak; Pulse Cannon = glowing amber orb; Disruptor =
## dark canister with crackling blue arcs; Temporal Lance = long white-violet beam-like bolt.
## Owns no rules; MissionView moves it every frame with `follow`.

const ASSETS := {
	"kinetic_accelerator": {"mesh": "OPR-PRJ-KINETIC_SLUG-A", "trail": "OPR-VFX-KINETIC_TRAIL-A", "trail_seconds": 0.06, "trail_height": 0.12, "colour": Color("bdf4ff")},
	"breach_charge": {"mesh": "OPR-PRJ-BREACH_CANISTER-A", "trail": "OPR-VFX-BREACH_TRAIL-A", "trail_seconds": 0.12, "trail_height": 0.3, "colour": Color("e0a040"), "arming": "OPR-VFX-BREACH_ARMING-A", "activation": "OPR-VFX-BREACH_ACTIVATION-A"},
	"penetrator": {
		"shape": "dart", "colour": Color("e8fbff"), "length_m": 0.46,
		"trail": "OPR-VFX-KINETIC_TRAIL-A", "trail_seconds": 0.08, "trail_height": 0.07, "trail_max": 2.2, "trail_tint": Color("f4ffff"),
	},
	"pulse_cannon": {
		"shape": "orb", "colour": Color("ffa22e"),
		"trail": "OPR-VFX-BREACH_TRAIL-A", "trail_seconds": 0.07, "trail_height": 0.34, "trail_tint": Color("ffb44a"),
		"glow": "SHR-VFX-PARTICLE_GLOW-A", "glow_m": 1.0, "glow_tint": Color("ff9a2a"),
	},
	"disruptor": {
		"shape": "canister", "colour": Color("4d8dff"),
		"trail": "OPR-VFX-KINETIC_TRAIL-A", "trail_seconds": 0.07, "trail_height": 0.2, "trail_tint": Color("5c9bff"),
		"glow": "SHR-VFX-PARTICLE_GLOW-A", "glow_m": 0.95, "glow_tint": Color("4f8cff"),
		"arcs": "SHR-VFX-ARC_ELECTRIC_LOOP-A",
	},
	"temporal_lance": {
		"shape": "lance", "colour": Color("f2eaff"), "length_m": 1.0,
		"trail": "OPR-VFX-KINETIC_TRAIL-A", "trail_seconds": 0.12, "trail_height": 0.28, "trail_max": 3.6, "trail_tint": Color("a77bff"),
		"core_height": 0.09, "core_tint": Color("ffffff"),
		"glow": "SHR-VFX-PARTICLE_GLOW-A", "glow_m": 1.2, "glow_tint": Color("b48cff"),
	},
}
## Sprite sheets (ui-vfx notes): frame grid and playback rate.
const ARMING_SHEET := {"hframes": 4, "vframes": 4, "fps": 16.0, "loop": true, "size_m": 0.6}
const ACTIVATION_SHEET := {"hframes": 4, "vframes": 2, "fps": 30.0, "loop": false, "size_m": 0.9}
## Crackling arcs on the Disruptor canister (SHR-VFX-ARC_ELECTRIC_LOOP-A: 4x4 flicker states).
const ARC_SHEET := {"hframes": 4, "vframes": 4, "fps": 24.0, "loop": true, "size_m": 0.8}
const TRAIL_MIN_M := 0.12
const TRAIL_MAX_M := 1.4
## The trail sits just in front of the projectile so the mesh is not hidden behind it.
const TRAIL_Z := -0.02

var weapon_id := ""
## True when the production mesh is shown (false: primitive body or greybox sphere).
var has_model := false
var _model: Node3D
var _tumbles := false
var _trail: MeshInstance3D
var _trail_quad: QuadMesh
var _trail_seconds := 0.0
var _trail_max := TRAIL_MAX_M
## Second, thinner and brighter trail layer (the Lance's white core).
var _core: MeshInstance3D
var _core_quad: QuadMesh
## Camera-facing additive glow behind the body (pulses).
var _glow: MeshInstance3D
## Additive arc flipbook quads (Disruptor).
var _arcs: Array[MeshInstance3D] = []
var _arming: Sprite3D
var _activation: Sprite3D
var _sheet_time := 0.0


static func create(projectile: WeaponProjectile, library: AssetLibrary) -> ProjectileVisual:
	var visual := ProjectileVisual.new()
	visual.weapon_id = projectile.weapon_id
	visual._build(projectile, library)
	return visual


func _build(projectile: WeaponProjectile, library: AssetLibrary) -> void:
	var spec: Dictionary = ASSETS.get(weapon_id, {})
	var radius := float(projectile.stats.projectile_radius) / ViewMapping.PX_PER_METRE
	var colour: Color = spec.get("colour", Color("bdf4ff"))
	_tumbles = projectile.weapon_id == "breach_charge" or spec.get("shape", "") == "canister"
	_trail_max = float(spec.get("trail_max", TRAIL_MAX_M))
	if library != null and spec.has("mesh"):
		_model = library.instance_piece(str(spec.mesh), "shared")
	if _model != null:
		var box := _bounds(_model)
		var cross := maxf(box.size.y, box.size.z)
		if cross > 0.0:
			_model.scale = Vector3.ONE * (radius * 2.0 / cross)
		has_model = true
	elif spec.has("shape"):
		_model = _shaped_body(str(spec.shape), spec, radius)
	else:
		var mesh := MeshInstance3D.new()
		var sphere := SphereMesh.new()
		sphere.radius = radius
		sphere.height = radius * 2.0
		mesh.mesh = sphere
		var material := StandardMaterial3D.new()
		material.albedo_color = colour
		material.emission_enabled = true
		material.emission = colour
		material.emission_energy_multiplier = 1.6
		mesh.material_override = material
		_model = mesh
	add_child(_model)
	var glow_texture := _texture(library, str(spec.get("glow", "")))
	if glow_texture != null:
		_glow = _quad(glow_texture, Vector2.ONE * float(spec.glow_m), spec.get("glow_tint", colour))
		_glow.position.z = TRAIL_Z * 2.0
		add_child(_glow)
	var arc_texture := _texture(library, str(spec.get("arcs", "")))
	if arc_texture != null:
		for i in 2:
			var arc := _quad(arc_texture, Vector2.ONE * float(ARC_SHEET.size_m) * (1.0 - 0.3 * i), Color("9fc4ff"), ARC_SHEET)
			arc.position.z = TRAIL_Z * 3.0
			arc.set_meta("offset", i * 7)
			add_child(arc)
			_arcs.append(arc)
	var trail_texture := _texture(library, str(spec.get("trail", "")))
	if trail_texture != null:
		_trail_seconds = float(spec.trail_seconds)
		_trail_quad = QuadMesh.new()
		_trail_quad.size = Vector2(TRAIL_MIN_M, float(spec.trail_height))
		_trail = MeshInstance3D.new()
		_trail.mesh = _trail_quad
		_trail.material_override = _additive(trail_texture, spec.get("trail_tint", Color.WHITE))
		_trail.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
		_trail.position.z = TRAIL_Z
		add_child(_trail)
		if spec.has("core_height"):
			_core_quad = QuadMesh.new()
			_core_quad.size = Vector2(TRAIL_MIN_M, float(spec.core_height))
			_core = MeshInstance3D.new()
			_core.mesh = _core_quad
			_core.material_override = _additive(trail_texture, spec.get("core_tint", Color.WHITE))
			_core.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
			add_child(_core)
	var arming_texture := _texture(library, str(spec.get("arming", "")))
	if arming_texture != null:
		_arming = _sheet_sprite(arming_texture, ARMING_SHEET)
		add_child(_arming)
	var activation_texture := _texture(library, str(spec.get("activation", "")))
	if activation_texture != null:
		_activation = _sheet_sprite(activation_texture, ACTIVATION_SHEET)
		_activation.top_level = true
		add_child(_activation)


## Parks a warm-up copy at `at` with every part in view (drawn once so its shaders compile).
func park(at: Vector3) -> void:
	position = at
	if _activation != null:
		_activation.top_level = false
		_activation.position = Vector3.ZERO


## Places the visual on its projectile; call every frame.
func follow(projectile: WeaponProjectile, ground_y: float, delta: float) -> void:
	position = ViewMapping.to_3d(projectile.global_position, ground_y)
	if _activation != null and _activation.is_inside_tree() and _sheet_time == 0.0:
		_activation.global_position = global_position
	_sheet_time += delta
	var velocity := projectile.linear_velocity
	var angle := ViewMapping.direction_angle(velocity) if velocity.length() > 1.0 else 0.0
	if _tumbles:
		_model.rotation = ViewMapping.rotation_to_3d(projectile.global_rotation)
	else:
		_model.rotation = Vector3(0.0, 0.0, angle)
	if _trail != null:
		var length := clampf(velocity.length() / ViewMapping.PX_PER_METRE * _trail_seconds, TRAIL_MIN_M, _trail_max)
		_trail_quad.size.x = length
		# The trail texture's head is its right edge (pivot u = 1.0): run it back from the projectile.
		_trail.rotation = Vector3(0.0, 0.0, angle)
		_trail.position = Vector3(-cos(angle) * length / 2.0, -sin(angle) * length / 2.0, TRAIL_Z)
		if _core != null:
			var core_length := length * 0.85
			_core_quad.size.x = core_length
			_core.rotation = Vector3(0.0, 0.0, angle)
			_core.position = Vector3(-cos(angle) * core_length / 2.0, -sin(angle) * core_length / 2.0, TRAIL_Z * 1.5)
	if _glow != null:
		_glow.scale = Vector3.ONE * (1.0 + 0.12 * sin(_sheet_time * 22.0))
	for arc in _arcs:
		_set_frame(arc, ARC_SHEET, int(_sheet_time * float(ARC_SHEET.fps)) + int(arc.get_meta("offset")))
	if _arming != null:
		_arming.frame = _sheet_frame(ARMING_SHEET, _sheet_time)
	if _activation != null:
		var frame := _sheet_frame(ACTIVATION_SHEET, _sheet_time)
		if frame < 0:
			_activation.queue_free()
			_activation = null
		else:
			_activation.frame = frame


static func _sheet_frame(sheet: Dictionary, time: float) -> int:
	var count := int(sheet.hframes) * int(sheet.vframes)
	var frame := int(time * float(sheet.fps))
	if bool(sheet.loop):
		return frame % count
	return frame if frame < count else -1


static func _sheet_sprite(texture: Texture2D, sheet: Dictionary) -> Sprite3D:
	var sprite := Sprite3D.new()
	sprite.texture = texture
	sprite.hframes = int(sheet.hframes)
	sprite.vframes = int(sheet.vframes)
	sprite.pixel_size = float(sheet.size_m) / (texture.get_width() / float(sheet.hframes))
	sprite.billboard = BaseMaterial3D.BILLBOARD_ENABLED
	sprite.shaded = false
	sprite.double_sided = true
	sprite.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	sprite.position.z = 0.05
	return sprite


static func _additive(texture: Texture2D, tint: Color = Color.WHITE) -> StandardMaterial3D:
	var material := StandardMaterial3D.new()
	material.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
	material.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
	material.blend_mode = BaseMaterial3D.BLEND_MODE_ADD
	material.cull_mode = BaseMaterial3D.CULL_DISABLED
	material.albedo_texture = texture
	material.albedo_color = tint
	return material


## A camera-facing additive quad; pass a sheet to make it a flipbook driven by `_set_frame`.
static func _quad(texture: Texture2D, size: Vector2, tint: Color, sheet: Dictionary = {}) -> MeshInstance3D:
	var quad := QuadMesh.new()
	quad.size = size
	var material := _additive(texture, tint)
	material.billboard_mode = BaseMaterial3D.BILLBOARD_ENABLED
	material.billboard_keep_scale = true
	if not sheet.is_empty():
		material.uv1_scale = Vector3(1.0 / float(sheet.hframes), 1.0 / float(sheet.vframes), 1.0)
	var node := MeshInstance3D.new()
	node.mesh = quad
	node.material_override = material
	node.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	return node


static func _set_frame(quad: MeshInstance3D, sheet: Dictionary, frame: int) -> void:
	var columns := int(sheet.hframes)
	frame = posmod(frame, columns * int(sheet.vframes))
	var material := quad.material_override as StandardMaterial3D
	material.uv1_offset = Vector3(float(frame % columns) / float(columns), float(frame / columns) / float(sheet.vframes), 0.0)


## An unshaded, always-bright body part.
static func _bright(colour: Color) -> StandardMaterial3D:
	var material := StandardMaterial3D.new()
	material.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
	material.albedo_color = colour
	return material


static func _part(mesh: Mesh, material: Material, rotation_z_deg: float = 0.0) -> MeshInstance3D:
	var node := MeshInstance3D.new()
	node.mesh = mesh
	node.material_override = material
	node.rotation_degrees.z = rotation_z_deg
	node.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	return node


static func _cylinder(radius: float, height: float, tip_radius: float = -1.0) -> CylinderMesh:
	var mesh := CylinderMesh.new()
	mesh.top_radius = radius if tip_radius < 0.0 else tip_radius
	mesh.bottom_radius = radius
	mesh.height = height
	mesh.radial_segments = 12
	mesh.rings = 1
	return mesh


## The primitive body of a chapter II-V projectile, pointing along +x, `radius` m in physics radius.
static func _shaped_body(shape: String, spec: Dictionary, radius: float) -> Node3D:
	var root := Node3D.new()
	var colour: Color = spec.get("colour", Color.WHITE)
	var length := float(spec.get("length_m", 0.4))
	match shape:
		"dart":
			# Needle: a bright shaft with a sharp white cone tip (+x).
			var shaft := _part(_cylinder(radius * 0.5, length * 0.72), _bright(colour), -90.0)
			shaft.position.x = -length * 0.14
			var tip := _part(_cylinder(radius * 0.5, length * 0.28, 0.0), _bright(Color.WHITE), -90.0)
			tip.position.x = length * 0.36
			root.add_child(shaft)
			root.add_child(tip)
		"orb":
			var shell := SphereMesh.new()
			shell.radius = radius
			shell.height = radius * 2.0
			var core := SphereMesh.new()
			core.radius = radius * 0.55
			core.height = radius * 1.1
			root.add_child(_part(shell, _bright(colour)))
			root.add_child(_part(core, _bright(Color("fff3d0"))))
		"canister":
			# Dark steel cylinder with two blue glowing end bands; tumbles with the body.
			var steel := StandardMaterial3D.new()
			steel.albedo_color = Color("2a3440")
			steel.metallic = 0.6
			steel.roughness = 0.45
			root.add_child(_part(_cylinder(radius * 0.8, radius * 2.6), steel, 90.0))
			for side: float in [-1.0, 1.0]:
				var ring := _part(_cylinder(radius * 0.92, radius * 0.4), _bright(colour), 90.0)
				ring.position.x = side * radius * 0.95
				root.add_child(ring)
		"lance":
			# White-hot core inside a violet sheath: a bolt rather than a bullet.
			var core := BoxMesh.new()
			core.size = Vector3(length, radius * 0.28, radius * 0.28)
			var sheath := BoxMesh.new()
			sheath.size = Vector3(length * 1.05, radius * 0.6, radius * 0.6)
			var violet := _bright(Color(0.62, 0.42, 1.0, 0.45))
			violet.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
			violet.blend_mode = BaseMaterial3D.BLEND_MODE_ADD
			root.add_child(_part(core, _bright(colour)))
			root.add_child(_part(sheath, violet))
	return root


static func _texture(library: AssetLibrary, asset_id: String) -> Texture2D:
	if library == null or asset_id.is_empty():
		return null
	return library.texture(asset_id)


## Combined local bounds of every mesh under `root` (before scaling).
static func _bounds(root: Node3D) -> AABB:
	var box := AABB()
	var first := true
	var stack: Array[Node] = [root]
	while not stack.is_empty():
		var node: Node = stack.pop_back()
		stack.append_array(node.get_children())
		if node is MeshInstance3D and (node as MeshInstance3D).mesh != null:
			var mesh_node := node as MeshInstance3D
			var xform := Transform3D.IDENTITY
			var walk: Node = mesh_node
			while walk != root and walk is Node3D:
				xform = (walk as Node3D).transform * xform
				walk = walk.get_parent()
			var part := xform * mesh_node.mesh.get_aabb()
			box = part if first else box.merge(part)
			first = false
	return box
