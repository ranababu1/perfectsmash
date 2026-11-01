class_name ProgressData
extends RefCounted
## Local player progress and settings with a versioned, validated serialization format.

const SCHEMA_VERSION := 1

## level id -> {"stars": int, "best_shots": int}
var level_results := {}
var sound_enabled := true
var vibration_enabled := true
## Problems found while loading; non-empty means some data was discarded.
var load_warnings := PackedStringArray()


func stars_for(level_id: String) -> int:
	return int(level_results.get(level_id, {}).get("stars", 0))


func is_completed(level_id: String) -> bool:
	return level_results.has(level_id)


func is_unlocked(level_ids: Array[String], index: int) -> bool:
	if index < 0 or index >= level_ids.size():
		return false
	if index == 0:
		return true
	return is_completed(level_ids[index - 1])


func total_stars() -> int:
	var total := 0
	for result: Dictionary in level_results.values():
		total += int(result.stars)
	return total


## Records a win, keeping the best result. Returns true if anything improved.
func record_win(level_id: String, stars: int, shots_used: int) -> bool:
	stars = clampi(stars, 1, ScoreRules.MAX_STARS)
	if not level_results.has(level_id):
		level_results[level_id] = {"stars": stars, "best_shots": shots_used}
		return true
	var current: Dictionary = level_results[level_id]
	var improved := false
	if stars > int(current.stars):
		current.stars = stars
		improved = true
	if shots_used < int(current.best_shots):
		current.best_shots = shots_used
		improved = true
	return improved


func to_dict() -> Dictionary:
	return {
		"version": SCHEMA_VERSION,
		"levels": level_results.duplicate(true),
		"settings": {"sound": sound_enabled, "vibration": vibration_enabled},
	}


## Tolerant loader: invalid fields are dropped with a warning instead of failing the whole save.
static func from_dict(data: Variant) -> ProgressData:
	var progress := ProgressData.new()
	if not data is Dictionary:
		progress.load_warnings.append("save root is not an object; using defaults")
		return progress
	var version: Variant = data.get("version")
	if not _is_whole(version) or int(version) != SCHEMA_VERSION:
		# No older schemas exist yet; unknown or newer versions are not trusted.
		progress.load_warnings.append("unsupported save version %s; using defaults" % str(version))
		return progress

	var levels: Variant = data.get("levels", {})
	if levels is Dictionary:
		for key: Variant in levels:
			var entry: Variant = levels[key]
			if key is String and entry is Dictionary and _is_whole(entry.get("stars")) and _is_whole(entry.get("best_shots")):
				var stars := int(entry.stars)
				var best := int(entry.best_shots)
				if stars >= 1 and stars <= ScoreRules.MAX_STARS and best >= 1:
					progress.level_results[key] = {"stars": stars, "best_shots": best}
					continue
			progress.load_warnings.append("dropped invalid result for level '%s'" % str(key))
	else:
		progress.load_warnings.append("'levels' is not an object")

	var settings: Variant = data.get("settings", {})
	if settings is Dictionary:
		if settings.get("sound") is bool:
			progress.sound_enabled = settings.sound
		if settings.get("vibration") is bool:
			progress.vibration_enabled = settings.vibration
	else:
		progress.load_warnings.append("'settings' is not an object")
	return progress


static func _is_whole(value: Variant) -> bool:
	return (value is int) or (value is float and value == floorf(value))
