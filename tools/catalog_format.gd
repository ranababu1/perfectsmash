extends RefCounted
## Writes data/levels.json in a compact, diff-friendly layout. Shared by the level tools.

## Compact, diff-friendly layout: one entity per line.
static func format_catalog(data: Dictionary) -> String:
	var out := "{\n\"levels\": [\n"
	var levels: Array = data.levels
	for li in levels.size():
		var l: Dictionary = levels[li]
		out += "{\n"
		out += "\t\"id\": %s, \"name\": %s, \"shots\": %s, \"par\": %s,\n" % [_j(l.id), _j(l.name), _j(l.shots), _j(l.par)]
		out += "\t\"hint\": %s,\n" % _j(l.get("hint", ""))
		out += "\t\"launcher\": %s,\n" % _j(l.launcher)
		out += "\t\"objective\": %s,\n" % _j(l.objective)
		if l.has("ammo"):
			out += "\t\"ammo\": %s,\n" % _j(l.ammo)
		var keys := ["statics", "blocks", "targets"]
		if l.has("allies"):
			keys.append("allies")
		keys.append("solution")
		for key: String in keys:
			var items: Array = l.get(key, [])
			if items.is_empty():
				out += "\t\"%s\": []" % key
			else:
				var lines := PackedStringArray()
				for item: Variant in items:
					lines.append("\t\t" + _j(item))
				out += "\t\"%s\": [\n%s\n\t]" % [key, ",\n".join(lines)]
			out += ",\n" if key != "solution" else "\n"
		out += "}" + (",\n" if li < levels.size() - 1 else "\n")
	return out + "]\n}\n"


## JSON with whole numbers printed as integers and keys kept in a stable, readable order.
static func _j(value: Variant) -> String:
	if value is float:
		return str(int(value)) if value == floorf(value) else str(value)
	if value is int:
		return str(value)
	if value is String:
		return JSON.stringify(value)
	if value is Array:
		var parts := PackedStringArray()
		for v: Variant in value:
			parts.append(_j(v))
		return "[" + ", ".join(parts) + "]"
	if value is Dictionary:
		var order := ["type", "line_y", "zone", "x", "y", "w", "h", "r", "rot", "material", "kind"]
		var keys: Array = value.keys()
		keys.sort_custom(func(a: String, b: String) -> bool:
			var ia := order.find(a)
			var ib := order.find(b)
			return (ia if ia >= 0 else 99) < (ib if ib >= 0 else 99))
		var parts := PackedStringArray()
		for k: String in keys:
			parts.append("%s: %s" % [JSON.stringify(k), _j(value[k])])
		return "{" + ", ".join(parts) + "}"
	return JSON.stringify(value)
