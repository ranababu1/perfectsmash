class_name ProgressData
extends RefCounted
## Local player progress and settings with a versioned, validated serialization format.

## v2 (0.2.0): adds the aim-guide setting and local play-test stats. v1 saves load unchanged
## with defaults for the new fields.
const SCHEMA_VERSION := 2
const OLDEST_SUPPORTED_VERSION := 1
## Counters kept per level for play-test feedback. They never leave the device unless the player
## copies the report themselves (see playtest_report()).
const STAT_KEYS: Array[String] = ["attempts", "wins", "losses", "timeouts"]

## level id -> {"stars": int, "best_shots": int}
var level_results := {}
## level id -> {"attempts": int, "wins": int, "losses": int, "timeouts": int}
var level_stats := {}
var sound_enabled := true
var vibration_enabled := true
## Shows the short trajectory preview while aiming (plan §10 experiment: preview on/off).
var aim_guide_enabled := true
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


## Adds one to a play-test counter (one of STAT_KEYS) for a level.
func count_stat(level_id: String, key: String) -> void:
	if not STAT_KEYS.has(key):
		push_error("ProgressData: unknown stat '%s'" % key)
		return
	if not level_stats.has(level_id):
		var fresh := {}
		for k in STAT_KEYS:
			fresh[k] = 0
		level_stats[level_id] = fresh
	level_stats[level_id][key] += 1


func stat(level_id: String, key: String) -> int:
	return int(level_stats.get(level_id, {}).get(key, 0))


## Plain-text summary a tester can copy and send to the developer. Contains only level ids,
## counters, stars and settings: nothing that identifies the player or the device.
func playtest_report(level_ids: Array[String], version: String) -> String:
	var lines := PackedStringArray()
	lines.append("Perfect Smash %s play-test report" % version)
	lines.append("aim guide: %s" % ("on" if aim_guide_enabled else "off"))
	lines.append("#   level  stars  best  attempts  wins  losses  timeouts")
	for i in level_ids.size():
		var id := level_ids[i]
		if not level_stats.has(id) and not level_results.has(id):
			continue
		var best: Variant = level_results.get(id, {}).get("best_shots", "-")
		lines.append("%-3d %-6s %5d  %4s  %8d  %4d  %6d  %8d" % [i + 1, id, stars_for(id), str(best),
			stat(id, "attempts"), stat(id, "wins"), stat(id, "losses"), stat(id, "timeouts")])
	return "\n".join(lines)


func to_dict() -> Dictionary:
	return {
		"version": SCHEMA_VERSION,
		"levels": level_results.duplicate(true),
		"stats": level_stats.duplicate(true),
		"settings": {"sound": sound_enabled, "vibration": vibration_enabled, "aim_guide": aim_guide_enabled},
	}


## Tolerant loader: invalid fields are dropped with a warning instead of failing the whole save.
static func from_dict(data: Variant) -> ProgressData:
	var progress := ProgressData.new()
	if not data is Dictionary:
		progress.load_warnings.append("save root is not an object; using defaults")
		return progress
	var version: Variant = data.get("version")
	if not _is_whole(version) or int(version) < OLDEST_SUPPORTED_VERSION or int(version) > SCHEMA_VERSION:
		# Unknown or newer versions are not trusted (a downgrade must not misread a newer save).
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
		if settings.get("aim_guide") is bool:
			progress.aim_guide_enabled = settings.aim_guide
	else:
		progress.load_warnings.append("'settings' is not an object")

	# v1 saves have no stats; that is expected, not a warning.
	var stats: Variant = data.get("stats", {})
	if stats is Dictionary:
		for key: Variant in stats:
			var entry: Variant = stats[key]
			if key is String and entry is Dictionary and _valid_stats(entry):
				var clean := {}
				for k in STAT_KEYS:
					clean[k] = int(entry.get(k, 0))
				progress.level_stats[key] = clean
			else:
				progress.load_warnings.append("dropped invalid stats for level '%s'" % str(key))
	else:
		progress.load_warnings.append("'stats' is not an object")
	return progress


static func _valid_stats(entry: Dictionary) -> bool:
	for k in STAT_KEYS:
		var v: Variant = entry.get(k, 0)
		if not _is_whole(v) or int(v) < 0:
			return false
	return true


static func _is_whole(value: Variant) -> bool:
	return (value is int) or (value is float and value == floorf(value))
