class_name LevelCatalog
extends RefCounted
## Loads and validates the ordered list of levels from a JSON file.

const DEFAULT_PATH := "res://data/levels.json"

var levels: Array[LevelDefinition] = []
var errors := PackedStringArray()


static func load_from_file(path: String = DEFAULT_PATH) -> LevelCatalog:
	var file := FileAccess.open(path, FileAccess.READ)
	if file == null:
		var catalog := LevelCatalog.new()
		catalog.errors.append("cannot open %s (error %d)" % [path, FileAccess.get_open_error()])
		return catalog
	return from_json_text(file.get_as_text())


static func from_json_text(text: String) -> LevelCatalog:
	var catalog := LevelCatalog.new()
	var json := JSON.new()
	if json.parse(text) != OK:
		catalog.errors.append("invalid JSON at line %d: %s" % [json.get_error_line(), json.get_error_message()])
		return catalog
	var root: Variant = json.data
	if not root is Dictionary or not root.get("levels") is Array:
		catalog.errors.append("root must be an object with a 'levels' array")
		return catalog
	var seen_ids := {}
	for entry: Variant in root.levels:
		var def := LevelDefinition.from_dict(entry)
		catalog.errors.append_array(def.errors)
		if seen_ids.has(def.id):
			catalog.errors.append("duplicate level id '%s'" % def.id)
		seen_ids[def.id] = true
		catalog.levels.append(def)
	if catalog.levels.is_empty():
		catalog.errors.append("catalog contains no levels")
	return catalog


func is_valid() -> bool:
	return errors.is_empty()


func ids() -> Array[String]:
	var result: Array[String] = []
	for def in levels:
		result.append(def.id)
	return result


func index_of(level_id: String) -> int:
	for i in levels.size():
		if levels[i].id == level_id:
			return i
	return -1
