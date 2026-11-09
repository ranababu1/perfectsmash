class_name MissionDefinition
extends RefCounted
## One tactical mission as validated data: the facility (static geometry + damageable
## components with explicit supports), the operative position, available weapons and their
## ammunition, objectives, and the efficiency benchmarks used for scoring. There is no
## universal shot cap: ammunition and benchmarks are per mission.
##
## Validation cross-checks material ids, weapon ids, support references and objective targets.
## The definition is plain data with stable ids so a future institution format (Frontlines) can
## map onto the same shape.

const OBJECTIVE_DESTROY_CRITICAL := "destroy_critical"
const OBJECTIVE_DESTROY_COMPONENTS := "destroy_components"
const OBJECTIVE_STRUCTURAL_DAMAGE := "structural_damage"
const OBJECTIVE_PROTECT := "protect"
const OBJECTIVE_MAX_SHOTS := "max_shots"
const OBJECTIVE_WITHIN_TIME := "within_time"
## Goals complete during play; constraints hold until the mission ends (or break).
const GOAL_TYPES := [OBJECTIVE_DESTROY_CRITICAL, OBJECTIVE_DESTROY_COMPONENTS, OBJECTIVE_STRUCTURAL_DAMAGE]
const CONSTRAINT_TYPES := [OBJECTIVE_PROTECT, OBJECTIVE_MAX_SHOTS, OBJECTIVE_WITHIN_TIME]

var id := ""
var name := ""
var chapter := 1
var briefing := ""
var width := 1280.0
var ground_y := 640.0
var operative := Vector2.ZERO
var recommended_shots := 1
var target_time := 60.0
## Rewards (optional "rewards" block; defaults below). Formula weights live in data/scoring.json.
var completion_points := 1000
var completion_research_data := 20
var optional_research_data := 5
## weapon id -> mission ammunition allowance (hard cap before upgrades)
var weapon_ammunition := {}
var weapon_order: Array[String] = []
## {position, size, rotation}
var statics: Array[Dictionary] = []
## {id, kind, material, position, size, rotation, health_scale, critical_asset, supports, min_supports}
var components: Array[Dictionary] = []
## {id, type, mandatory, label, targets: Array[String], count, fraction, limit}
var objectives: Array[Dictionary] = []

var errors := PackedStringArray()


static func load_from_file(path: String, materials: MaterialCatalog, weapons: WeaponCatalog) -> MissionDefinition:
	var file := FileAccess.open(path, FileAccess.READ)
	if file == null:
		var def := MissionDefinition.new()
		def.errors.append("cannot open %s (error %d)" % [path, FileAccess.get_open_error()])
		return def
	return from_json_text(file.get_as_text(), materials, weapons)


static func from_json_text(text: String, materials: MaterialCatalog, weapons: WeaponCatalog) -> MissionDefinition:
	var def := MissionDefinition.new()
	var json := JSON.new()
	if json.parse(text) != OK:
		def.errors.append("invalid JSON at line %d: %s" % [json.get_error_line(), json.get_error_message()])
		return def
	if not json.data is Dictionary:
		def.errors.append("mission root must be an object")
		return def
	def._parse(json.data)
	if def.errors.is_empty():
		def._validate(materials, weapons)
	return def


func is_valid() -> bool:
	return errors.is_empty()


func component(component_id: String) -> Dictionary:
	for c in components:
		if c.id == component_id:
			return c
	return {}


func critical_asset_ids() -> Array[String]:
	var ids: Array[String] = []
	for c in components:
		if c.critical_asset:
			ids.append(c.id)
	return ids


## Structure entries for StructuralDependencySystem.from_entries().
func structure_entries() -> Array:
	var entries := []
	for c in components:
		entries.append({"id": c.id, "supports": c.supports, "min_supports": c.min_supports})
	return entries


func _parse(data: Dictionary) -> void:
	id = _string(data, "id")
	name = _string(data, "name")
	briefing = str(data.get("briefing", ""))
	chapter = _whole(data, "chapter", 1)
	width = _number(data, "width")
	ground_y = _number(data, "ground_y")
	operative = _vector(data, "operative")
	recommended_shots = _whole(data, "recommended_shots", 1)
	target_time = _number(data, "target_time")
	var rewards: Variant = data.get("rewards", {})
	if rewards is Dictionary:
		completion_points = _reward(rewards, "completion_points", completion_points)
		completion_research_data = _reward(rewards, "completion_research_data", completion_research_data)
		optional_research_data = _reward(rewards, "optional_research_data", optional_research_data)
	else:
		errors.append("'rewards' must be an object")

	var raw_weapons: Variant = data.get("weapons")
	if raw_weapons is Dictionary and not raw_weapons.is_empty():
		for weapon_id: Variant in raw_weapons:
			var entry: Variant = raw_weapons[weapon_id]
			var ammo: Variant = entry.get("ammunition") if entry is Dictionary else null
			if (ammo is float or ammo is int) and ammo >= 1 and ammo == floorf(ammo):
				weapon_ammunition[str(weapon_id)] = int(ammo)
				weapon_order.append(str(weapon_id))
			else:
				errors.append("weapon '%s': ammunition must be a whole number >= 1" % str(weapon_id))
	else:
		errors.append("'weapons' must be a non-empty object")

	for entry: Variant in _array(data, "statics"):
		if entry is Dictionary:
			statics.append({"position": _xy(entry), "size": _size(entry), "rotation": _rotation(entry)})
		else:
			errors.append("static entry is not an object")
	for entry: Variant in _array(data, "components"):
		if entry is Dictionary:
			components.append(_parse_component(entry))
		else:
			errors.append("component entry is not an object")
	for entry: Variant in _array(data, "objectives"):
		if entry is Dictionary:
			objectives.append(_parse_objective(entry))
		else:
			errors.append("objective entry is not an object")


func _parse_component(entry: Dictionary) -> Dictionary:
	var supports: Array[String] = []
	var raw_supports: Variant = entry.get("supports", [])
	if raw_supports is Array and raw_supports.all(func(s: Variant) -> bool: return s is String):
		supports.assign(raw_supports)
	else:
		errors.append("component '%s': supports must be an array of ids" % str(entry.get("id")))
	var scale: Variant = entry.get("health_scale", 1.0)
	var minimum: Variant = entry.get("min_supports", -1)
	return {
		"id": _string(entry, "id"),
		"kind": _string(entry, "kind"),
		"material": _string(entry, "material"),
		"position": _xy(entry),
		"size": _size(entry),
		"rotation": _rotation(entry),
		"health_scale": float(scale) if (scale is float or scale is int) else 0.0,
		"critical_asset": entry.get("critical_asset", false) == true,
		"supports": supports,
		"min_supports": int(minimum) if (minimum is float or minimum is int) else -1,
	}


func _parse_objective(entry: Dictionary) -> Dictionary:
	var targets: Array[String] = []
	var raw_targets: Variant = entry.get("targets", [])
	if raw_targets is Array and raw_targets.all(func(s: Variant) -> bool: return s is String):
		targets.assign(raw_targets)
	else:
		errors.append("objective '%s': targets must be an array of ids" % str(entry.get("id")))
	var mandatory: Variant = entry.get("mandatory", false)
	return {
		"id": _string(entry, "id"),
		"type": str(entry.get("type", "")),
		"mandatory": mandatory == true,
		"label": _string(entry, "label"),
		"targets": targets,
		"count": int(entry.get("count", targets.size())) if (entry.get("count", 0) is float or entry.get("count", 0) is int) else -1,
		"fraction": float(entry.get("fraction", 0.0)) if (entry.get("fraction", 0.0) is float or entry.get("fraction", 0.0) is int) else -1.0,
		"limit": float(entry.get("limit", 0.0)) if (entry.get("limit", 0.0) is float or entry.get("limit", 0.0) is int) else -1.0,
	}


func _validate(materials: MaterialCatalog, weapons: WeaponCatalog) -> void:
	var prefix := "mission '%s': " % id
	if width <= 0.0 or ground_y <= 0.0:
		errors.append(prefix + "width and ground_y must be positive")
	if not _inside(operative):
		errors.append(prefix + "operative is outside the mission area")
	if recommended_shots < 1:
		errors.append(prefix + "recommended_shots must be >= 1")
	if target_time <= 0.0:
		errors.append(prefix + "target_time must be positive")

	var total_ammo := 0
	for weapon_id in weapon_order:
		if not weapons.has_weapon(weapon_id):
			errors.append(prefix + "unknown weapon '%s'" % weapon_id)
		total_ammo += int(weapon_ammunition[weapon_id])
	if total_ammo < recommended_shots:
		errors.append(prefix + "ammunition (%d) is below the recommended shots (%d)" % [total_ammo, recommended_shots])

	for s in statics:
		_check_box(s, prefix + "static")

	var ids := {}
	for c in components:
		var where := prefix + "component '%s': " % c.id
		if ids.has(c.id):
			errors.append(where + "duplicate id")
		ids[c.id] = true
		if not materials.has_material(c.material):
			errors.append(where + "unknown material '%s'" % c.material)
		if c.health_scale <= 0.0:
			errors.append(where + "health_scale must be positive")
		_check_box(c, where.trim_suffix(": "))
	if components.is_empty():
		errors.append(prefix + "mission has no components")

	var structure := StructuralDependencySystem.from_entries(structure_entries())
	for problem in structure.errors:
		errors.append(prefix + problem)

	var has_mandatory_goal := false
	var objective_ids := {}
	for o in objectives:
		var where := prefix + "objective '%s': " % o.id
		if objective_ids.has(o.id):
			errors.append(where + "duplicate id")
		objective_ids[o.id] = true
		if not GOAL_TYPES.has(o.type) and not CONSTRAINT_TYPES.has(o.type):
			errors.append(where + "unknown type '%s'" % o.type)
			continue
		if o.mandatory and GOAL_TYPES.has(o.type):
			has_mandatory_goal = true
		for target: String in o.targets:
			if not ids.has(target):
				errors.append(where + "unknown target '%s'" % target)
			elif o.type == OBJECTIVE_DESTROY_CRITICAL and not component(target).critical_asset:
				errors.append(where + "'%s' is not a critical asset" % target)
		match o.type:
			OBJECTIVE_DESTROY_CRITICAL, OBJECTIVE_DESTROY_COMPONENTS, OBJECTIVE_PROTECT:
				if o.targets.is_empty():
					errors.append(where + "needs targets")
				if o.type == OBJECTIVE_DESTROY_COMPONENTS and (o.count < 1 or o.count > o.targets.size()):
					errors.append(where + "count must be 1-%d" % o.targets.size())
			OBJECTIVE_STRUCTURAL_DAMAGE:
				if o.fraction <= 0.0 or o.fraction > 1.0:
					errors.append(where + "fraction must be in (0, 1]")
			OBJECTIVE_MAX_SHOTS, OBJECTIVE_WITHIN_TIME:
				if o.limit <= 0.0:
					errors.append(where + "limit must be positive")
	if not has_mandatory_goal:
		errors.append(prefix + "needs at least one mandatory goal objective")
	for asset_id in critical_asset_ids():
		var covered := objectives.any(func(o: Dictionary) -> bool: return o.type == OBJECTIVE_DESTROY_CRITICAL and o.targets.has(asset_id))
		if not covered:
			errors.append(prefix + "critical asset '%s' has no destroy_critical objective" % asset_id)


func _check_box(box: Dictionary, where: String) -> void:
	var size: Vector2 = box.size
	if size.x <= 0.0 or size.y <= 0.0:
		errors.append(where + ": size must be positive")
	if not _inside(box.position):
		errors.append(where + ": position %s is outside the mission area" % box.position)


func _inside(point: Vector2) -> bool:
	return point.x >= 0.0 and point.x <= width and point.y >= -ground_y and point.y <= ground_y


func _string(data: Dictionary, key: String) -> String:
	var value: Variant = data.get(key)
	if value is String and not value.is_empty():
		return value
	errors.append("missing string '%s'" % key)
	return ""


func _number(data: Dictionary, key: String) -> float:
	var value: Variant = data.get(key)
	if value is float or value is int:
		return float(value)
	errors.append("missing number '%s'" % key)
	return 0.0


func _whole(data: Dictionary, key: String, fallback: int) -> int:
	var value: Variant = data.get(key)
	if (value is float or value is int) and value == floorf(value):
		return int(value)
	errors.append("'%s' must be a whole number" % key)
	return fallback


func _reward(rewards: Dictionary, key: String, fallback: int) -> int:
	if not rewards.has(key):
		return fallback
	var value: Variant = rewards[key]
	if (value is float or value is int) and value >= 0 and value == floorf(value):
		return int(value)
	errors.append("rewards.%s must be a whole number >= 0" % key)
	return fallback


func _vector(data: Dictionary, key: String) -> Vector2:
	var value: Variant = data.get(key)
	if value is Array and value.size() == 2 and (value[0] is float or value[0] is int) and (value[1] is float or value[1] is int):
		return Vector2(value[0], value[1])
	errors.append("'%s' must be [x, y]" % key)
	return Vector2.ZERO


func _array(data: Dictionary, key: String) -> Array:
	var value: Variant = data.get(key, [])
	if value is Array:
		return value
	errors.append("'%s' must be an array" % key)
	return []


func _xy(entry: Dictionary) -> Vector2:
	return Vector2(_number(entry, "x"), _number(entry, "y"))


func _size(entry: Dictionary) -> Vector2:
	return Vector2(_number(entry, "w"), _number(entry, "h"))


func _rotation(entry: Dictionary) -> float:
	var rot: Variant = entry.get("rot", 0.0)
	return deg_to_rad(float(rot)) if (rot is float or rot is int) else 0.0
