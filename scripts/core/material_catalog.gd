class_name MaterialCatalog
extends RefCounted
## Loads and validates physical material definitions (data/materials.json). Materials describe
## behaviour only: mass, friction, health, resistances and damage thresholds, plus an optional
## secondary blast on destruction. How a material looks is a presentation concern.

const DEFAULT_PATH := "res://data/materials.json"
const MAX_RESISTANCE := 0.95
## Even the densest blocker lets a little of a blast through.
const MIN_BLAST_TRANSMISSION := 0.05


class MaterialSpec:
	var id := ""
	var density := 0.0
	var friction := 0.0
	var bounce := 0.0
	var health := 0.0
	var impact_resistance := 0.0
	## Resistance to structural damage (falls, crushing, debris). Optional in data; defaults to
	## impact_resistance. A shock-mounted housing survives drops but not weapon fire.
	var structural_resistance := 0.0
	var blast_resistance := 0.0
	var min_damage := 0.0
	## Share of a blast that passes through this material when it occludes a target.
	var blast_transmission := 1.0
	## Secondary blast when a component of this material is destroyed (0 = none).
	var secondary_blast_damage := 0.0
	var secondary_blast_radius := 0.0
	var secondary_blast_impulse := 0.0

	func has_secondary_blast() -> bool:
		return secondary_blast_damage > 0.0 and secondary_blast_radius > 0.0

	func mass_for(size: Vector2) -> float:
		return size.x * size.y * density


var materials := {}
var order: Array[String] = []
var errors := PackedStringArray()


static func load_from_file(path: String = DEFAULT_PATH) -> MaterialCatalog:
	var file := FileAccess.open(path, FileAccess.READ)
	if file == null:
		var catalog := MaterialCatalog.new()
		catalog.errors.append("cannot open %s (error %d)" % [path, FileAccess.get_open_error()])
		return catalog
	return from_json_text(file.get_as_text())


static func from_json_text(text: String) -> MaterialCatalog:
	var catalog := MaterialCatalog.new()
	var json := JSON.new()
	if json.parse(text) != OK:
		catalog.errors.append("invalid JSON at line %d: %s" % [json.get_error_line(), json.get_error_message()])
		return catalog
	var root: Variant = json.data
	if not root is Dictionary or not root.get("materials") is Array:
		catalog.errors.append("root must be an object with a 'materials' array")
		return catalog
	for entry: Variant in root.materials:
		catalog._add(entry)
	if catalog.order.is_empty():
		catalog.errors.append("catalog contains no materials")
	return catalog


func is_valid() -> bool:
	return errors.is_empty()


func has_material(material_id: String) -> bool:
	return materials.has(material_id)


## The material with this id, or null (callers must handle a missing definition).
func get_material(material_id: String) -> MaterialSpec:
	return materials.get(material_id)


func _add(entry: Variant) -> void:
	if not entry is Dictionary:
		errors.append("material entry is not an object")
		return
	var spec := MaterialSpec.new()
	var raw_id: Variant = entry.get("id")
	if not raw_id is String or raw_id.is_empty():
		errors.append("material without a string 'id'")
		return
	spec.id = raw_id
	var prefix := "material '%s': " % spec.id
	spec.density = _number(entry, "density", prefix, 0.0, INF, false)
	spec.friction = _number(entry, "friction", prefix, 0.0, 2.0, true)
	spec.bounce = _number(entry, "bounce", prefix, 0.0, 1.0, true)
	spec.health = _number(entry, "health", prefix, 0.0, INF, false)
	spec.impact_resistance = _number(entry, "impact_resistance", prefix, 0.0, MAX_RESISTANCE, true)
	spec.blast_resistance = _number(entry, "blast_resistance", prefix, 0.0, MAX_RESISTANCE, true)
	spec.structural_resistance = spec.impact_resistance
	if entry.has("structural_resistance"):
		spec.structural_resistance = _number(entry, "structural_resistance", prefix, 0.0, MAX_RESISTANCE, true)
	spec.min_damage = _number(entry, "min_damage", prefix, 0.0, INF, true)
	spec.blast_transmission = _number(entry, "blast_transmission", prefix, MIN_BLAST_TRANSMISSION, 1.0, true)
	var secondary: Variant = entry.get("on_destroyed")
	if secondary != null:
		if secondary is Dictionary:
			spec.secondary_blast_damage = _number(secondary, "blast_damage", prefix + "on_destroyed ", 0.0, INF, false)
			spec.secondary_blast_radius = _number(secondary, "blast_radius", prefix + "on_destroyed ", 0.0, INF, false)
			spec.secondary_blast_impulse = _number(secondary, "blast_impulse", prefix + "on_destroyed ", 0.0, INF, true)
		else:
			errors.append(prefix + "on_destroyed must be an object")
	if materials.has(spec.id):
		errors.append(prefix + "duplicate id")
		return
	materials[spec.id] = spec
	order.append(spec.id)


## Reads a required number in [low, high]; `inclusive_low` false means it must be > low.
func _number(entry: Dictionary, key: String, prefix: String, low: float, high: float, inclusive_low: bool) -> float:
	var value: Variant = entry.get(key)
	if not (value is float or value is int):
		errors.append(prefix + "missing number '%s'" % key)
		return 0.0
	var v := float(value)
	if v > high or v < low or (not inclusive_low and v == low):
		errors.append(prefix + "'%s' = %s is out of range" % [key, str(v)])
	return v
