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
## Owns no rules; MissionView moves it every frame with `follow`.

const ASSETS := {
	"kinetic_accelerator": {"mesh": "OPR-PRJ-KINETIC_SLUG-A", "trail": "OPR-VFX-KINETIC_TRAIL-A", "trail_seconds": 0.06, "trail_height": 0.12, "colour": Color("bdf4ff")},
	"breach_charge": {"mesh": "OPR-PRJ-BREACH_CANISTER-A", "trail": "OPR-VFX-BREACH_TRAIL-A", "trail_seconds": 0.12, "trail_height": 0.3, "colour": Color("e0a040"), "arming": "OPR-VFX-BREACH_ARMING-A", "activation": "OPR-VFX-BREACH_ACTIVATION-A"},
}
## Sprite sheets (ui-vfx notes): frame grid and playback rate.
const ARMING_SHEET := {"hframes": 4, "vframes": 4, "fps": 16.0, "loop": true, "size_m": 0.6}
const ACTIVATION_SHEET := {"hframes": 4, "vframes": 2, "fps": 30.0, "loop": false, "size_m": 0.9}
const TRAIL_MIN_M := 0.12
const TRAIL_MAX_M := 1.4
## The trail sits just in front of the projectile so the mesh is not hidden behind it.
const TRAIL_Z := -0.02

var weapon_id := ""
## True when the production mesh is shown (false: greybox sphere).
var has_model := false
var _model: Node3D
var _tumbles := false
var _trail: MeshInstance3D
var _trail_quad: QuadMesh
var _trail_seconds := 0.0
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
	_tumbles = projectile.weapon_id == "breach_charge"
	if library != null and spec.has("mesh"):
		_model = library.instance_piece(str(spec.mesh), "shared")
	if _model != null:
		var box := _bounds(_model)
		var cross := maxf(box.size.y, box.size.z)
		if cross > 0.0:
			_model.scale = Vector3.ONE * (radius * 2.0 / cross)
		has_model = true
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
	var trail_texture := _texture(library, str(spec.get("trail", "")))
	if trail_texture != null:
		_trail_seconds = float(spec.trail_seconds)
		_trail_quad = QuadMesh.new()
		_trail_quad.size = Vector2(TRAIL_MIN_M, float(spec.trail_height))
		_trail = MeshInstance3D.new()
		_trail.mesh = _trail_quad
		_trail.material_override = _additive(trail_texture)
		_trail.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
		_trail.position.z = TRAIL_Z
		add_child(_trail)
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
		var length := clampf(velocity.length() / ViewMapping.PX_PER_METRE * _trail_seconds, TRAIL_MIN_M, TRAIL_MAX_M)
		_trail_quad.size.x = length
		# The trail texture's head is its right edge (pivot u = 1.0): run it back from the projectile.
		_trail.rotation = Vector3(0.0, 0.0, angle)
		_trail.position = Vector3(-cos(angle) * length / 2.0, -sin(angle) * length / 2.0, TRAIL_Z)
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


static func _additive(texture: Texture2D) -> StandardMaterial3D:
	var material := StandardMaterial3D.new()
	material.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
	material.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
	material.blend_mode = BaseMaterial3D.BLEND_MODE_ADD
	material.cull_mode = BaseMaterial3D.CULL_DISABLED
	material.albedo_texture = texture
	return material


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
