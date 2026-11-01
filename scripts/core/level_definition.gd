class_name LevelDefinition
extends RefCounted
## A validated, typed description of one handcrafted level.
## Built from a plain Dictionary (JSON) so content stays separate from logic.

const OBJECTIVE_DESTROY_TARGETS := "destroy_targets"
const OBJECTIVE_TOPPLE := "topple"
const MAX_SHOTS := 5
const MIN_TARGET_RADIUS := 8.0
const MAX_TARGET_RADIUS := 60.0

var id := ""
var name := ""
var hint := ""
var shots := 1
var par := 1
var objective_type := OBJECTIVE_DESTROY_TARGETS
## For topple objectives: every block's top edge must end below (greater y than) this line.
var topple_line_y := 0.0
var launcher := Vector2.ZERO
## Each entry: {position: Vector2, size: Vector2, rotation: float (radians)}.
var statics: Array[Dictionary] = []
## Each entry: {position, size, rotation, material: String}.
var blocks: Array[Dictionary] = []
## Each entry: {position: Vector2, radius: float}.
var targets: Array[Dictionary] = []
## Verified launch velocities that solve the level; used by automated tests, never shown to players.
var solution: Array[Vector2] = []

var errors := PackedStringArray()


func is_valid() -> bool:
	return errors.is_empty()


static func from_dict(data: Variant) -> LevelDefinition:
	var def := LevelDefinition.new()
	if not data is Dictionary:
		def.errors.append("level entry is not an object")
		return def
	def._parse(data)
	if def.is_valid():
		def._validate()
	return def


func _parse(data: Dictionary) -> void:
	id = _read_string(data, "id")
	name = _read_string(data, "name")
	hint = str(data.get("hint", ""))
	shots = _read_int(data, "shots")
	par = _read_int(data, "par")
	launcher = _read_vector(data, "launcher")

	var objective: Variant = data.get("objective", {})
	if objective is Dictionary:
		objective_type = str(objective.get("type", ""))
		if objective_type == OBJECTIVE_TOPPLE:
			topple_line_y = _read_float(objective, "line_y")
	else:
		errors.append("objective must be an object")

	for entry: Variant in _read_array(data, "statics"):
		statics.append(_parse_box(entry, false))
	for entry: Variant in _read_array(data, "blocks"):
		blocks.append(_parse_box(entry, true))
	for entry: Variant in _read_array(data, "targets"):
		if entry is Dictionary:
			targets.append({"position": _read_xy(entry), "radius": _read_float(entry, "r")})
		else:
			errors.append("target entry is not an object")
	for entry: Variant in _read_array(data, "solution"):
		if entry is Array and entry.size() == 2 and _is_number(entry[0]) and _is_number(entry[1]):
			solution.append(Vector2(entry[0], entry[1]))
		else:
			errors.append("solution entries must be [vx, vy]")


func _validate() -> void:
	var prefix := "level '%s': " % id
	if shots < 1 or shots > MAX_SHOTS:
		errors.append(prefix + "shots must be between 1 and %d" % MAX_SHOTS)
	if par < 1 or par > shots:
		errors.append(prefix + "par must be between 1 and shots")
	if not _in_world(launcher):
		errors.append(prefix + "launcher is outside the world")
	match objective_type:
		OBJECTIVE_DESTROY_TARGETS:
			if targets.is_empty():
				errors.append(prefix + "destroy_targets needs at least one target")
		OBJECTIVE_TOPPLE:
			if blocks.is_empty():
				errors.append(prefix + "topple needs at least one block")
			if topple_line_y <= 0.0 or topple_line_y >= GameConfig.GROUND_TOP:
				errors.append(prefix + "topple line_y must be above the ground")
		_:
			errors.append(prefix + "unknown objective type '%s'" % objective_type)
	for box: Dictionary in statics + blocks:
		var size: Vector2 = box.size
		if size.x <= 0.0 or size.y <= 0.0:
			errors.append(prefix + "box sizes must be positive")
		if not _in_world(box.position):
			errors.append(prefix + "box at %s is outside the world" % box.position)
	for box: Dictionary in blocks:
		if not GameConfig.MATERIALS.has(box.material):
			errors.append(prefix + "unknown material '%s'" % box.material)
	for target: Dictionary in targets:
		if target.radius < MIN_TARGET_RADIUS or target.radius > MAX_TARGET_RADIUS:
			errors.append(prefix + "target radius out of range")
		if not _in_world(target.position):
			errors.append(prefix + "target at %s is outside the world" % target.position)
	if solution.size() > shots:
		errors.append(prefix + "solution uses more shots than allowed")
	for velocity in solution:
		if velocity.length() > GameConfig.MAX_LAUNCH_SPEED + 0.5:
			errors.append(prefix + "solution velocity exceeds max launch speed")


func _parse_box(entry: Variant, is_block: bool) -> Dictionary:
	if not entry is Dictionary:
		errors.append("box entry is not an object")
		return {"position": Vector2.ZERO, "size": Vector2.ZERO, "rotation": 0.0, "material": ""}
	var rot: Variant = entry.get("rot", 0.0)
	var box := {
		"position": _read_xy(entry),
		"size": Vector2(_read_float(entry, "w"), _read_float(entry, "h")),
		"rotation": deg_to_rad(float(rot)) if _is_number(rot) else 0.0,
	}
	if is_block:
		box["material"] = str(entry.get("material", "wood"))
	return box


static func _in_world(point: Vector2) -> bool:
	return point.x >= 0.0 and point.x <= GameConfig.WORLD_WIDTH \
		and point.y >= 0.0 and point.y <= GameConfig.GROUND_TOP


static func _is_number(value: Variant) -> bool:
	return value is float or value is int


func _read_string(data: Dictionary, key: String) -> String:
	var value: Variant = data.get(key)
	if not value is String or value.is_empty():
		errors.append("missing or empty string '%s'" % key)
		return ""
	return value


func _read_float(data: Dictionary, key: String) -> float:
	var value: Variant = data.get(key)
	if not _is_number(value):
		errors.append("missing number '%s'" % key)
		return 0.0
	return float(value)


func _read_int(data: Dictionary, key: String) -> int:
	var value := _read_float(data, key)
	if value != floorf(value):
		errors.append("'%s' must be a whole number" % key)
	return int(value)


func _read_vector(data: Dictionary, key: String) -> Vector2:
	var value: Variant = data.get(key)
	if value is Array and value.size() == 2 and _is_number(value[0]) and _is_number(value[1]):
		return Vector2(value[0], value[1])
	errors.append("'%s' must be [x, y]" % key)
	return Vector2.ZERO


func _read_xy(data: Dictionary) -> Vector2:
	return Vector2(_read_float(data, "x"), _read_float(data, "y"))


func _read_array(data: Dictionary, key: String) -> Array:
	var value: Variant = data.get(key, [])
	if value is Array:
		return value
	errors.append("'%s' must be an array" % key)
	return []
