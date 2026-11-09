class_name DebrisSet
extends Node3D
## The destroyed state of a component (ASSET_CONTRACT 8): the library's debris set placed where
## the component was, its fragments thrown outward and up, falling to the floor, then shrinking
## away. Visual only: no collision and no 3D physics (the game's physics stays 2D), and the
## motion is seeded from the component id, so the same destruction always looks the same.

const GRAVITY := 9.8
## Seconds before fragments start shrinking, and how long the shrink takes.
const REST_TIME := 2.2
const SHRINK_TIME := 0.5
## Launch speeds (m/s): outward from the component centre, and upward.
const OUTWARD_SPEED := Vector2(0.6, 2.2)
const UPWARD_SPEED := Vector2(0.8, 2.6)
## Fragments stay near the physics plane so they never fly at the camera or into the back wall.
const MAX_DEPTH_SPEED := 0.5
const SPIN_SPEED := Vector2(2.0, 7.0)
## Bounce on the floor: vertical speed kept, horizontal speed kept.
const FLOOR_BOUNCE := 0.25
const FLOOR_FRICTION := 0.55
## The floor top is y = 0 in the view (ViewMapping: physics ground line).
const FLOOR_Y := 0.0
## The husk (the broken base the set is built around) moves much less than loose fragments.
const HUSK_SPEED_SCALE := 0.25

## Asset id of the debris set shown.
var asset_id := ""
var _fragments: Array[Dictionary] = []
var _age := 0.0
var _model: Node3D


## Places `model` (AssetLibrary.instance_debris) at `at` with the component's z rotation; the
## caller adds the returned node to the view.
static func create(model: Node3D, at: Vector3, rotation_z: float, seed_key: String, p_asset_id: String) -> DebrisSet:
	var debris := DebrisSet.new()
	debris.name = "Debris_" + seed_key
	debris.asset_id = p_asset_id
	debris.position = at
	debris.rotation = Vector3(0.0, 0.0, rotation_z)
	debris._model = model
	debris.add_child(model)
	var rng := RandomNumberGenerator.new()
	rng.seed = hash(seed_key)
	for fragment: MeshInstance3D in model.find_children("*", "MeshInstance3D", true, false):
		debris._fragments.append(debris._launch(fragment, rng))
	return debris


func fragment_count() -> int:
	return _fragments.size()


func _launch(fragment: MeshInstance3D, rng: RandomNumberGenerator) -> Dictionary:
	# Offset from the set's centre in the set's own (rotated, unscaled) space, then to the view.
	var local_offset := _model.transform * _relative_position(fragment)
	var outward := Basis(Vector3.BACK, rotation.z) * local_offset
	var direction := Vector2(outward.x, outward.y)
	direction = direction.normalized() if direction.length() > 0.001 else Vector2(rng.randf_range(-1.0, 1.0), 0.0).normalized()
	var husk := str(fragment.name).begins_with("husk")
	var speed_scale := HUSK_SPEED_SCALE if husk else 1.0
	var velocity := Vector3(
		direction.x * rng.randf_range(OUTWARD_SPEED.x, OUTWARD_SPEED.y),
		maxf(direction.y, 0.0) * OUTWARD_SPEED.x + rng.randf_range(UPWARD_SPEED.x, UPWARD_SPEED.y),
		rng.randf_range(-MAX_DEPTH_SPEED, MAX_DEPTH_SPEED)) * speed_scale
	var axis := Vector3(rng.randf_range(-1.0, 1.0), rng.randf_range(-1.0, 1.0), rng.randf_range(-1.0, 1.0))
	if axis.length() < 0.01:
		axis = Vector3.BACK
	var box := fragment.get_aabb()
	var half_height := 0.5 * minf(box.size.y * absf(_model.scale.y), box.size.x * absf(_model.scale.x))
	return {
		"node": fragment,
		"velocity": velocity,
		"axis": axis.normalized(),
		"spin": rng.randf_range(SPIN_SPEED.x, SPIN_SPEED.y) * speed_scale * (1.0 if rng.randf() < 0.5 else -1.0),
		"rest_y": FLOOR_Y + maxf(half_height, 0.02),
		"scale": fragment.scale,
	}


## Position of `node` relative to the model root (product of intermediate transforms).
func _relative_position(node: Node3D) -> Vector3:
	var t := Transform3D.IDENTITY
	var current: Node = node
	while current != null and current != _model:
		if current is Node3D:
			t = (current as Node3D).transform * t
		current = current.get_parent()
	return t.origin


func _process(delta: float) -> void:
	_age += delta
	for fragment: Dictionary in _fragments:
		var node: MeshInstance3D = fragment.node
		if not is_instance_valid(node):
			continue
		var velocity: Vector3 = fragment.velocity
		velocity.y -= GRAVITY * delta
		var at := node.global_position + velocity * delta
		var rest_y: float = fragment.rest_y
		if at.y < rest_y:
			at.y = rest_y
			velocity.y = -velocity.y * FLOOR_BOUNCE if absf(velocity.y) > 0.6 else 0.0
			velocity.x *= FLOOR_FRICTION
			velocity.z *= FLOOR_FRICTION
			fragment.spin = float(fragment.spin) * FLOOR_FRICTION
		fragment.velocity = velocity
		node.global_position = at
		if absf(float(fragment.spin)) > 0.01:
			node.rotate_object_local(fragment.axis, float(fragment.spin) * delta)
		if _age > REST_TIME:
			var t := clampf((_age - REST_TIME) / SHRINK_TIME, 0.0, 1.0)
			node.scale = (fragment.scale as Vector3) * (1.0 - t)
	if _age > REST_TIME + SHRINK_TIME:
		queue_free()
