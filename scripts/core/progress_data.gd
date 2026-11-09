class_name ProgressData
extends RefCounted
## Local player progress and settings with a versioned, validated serialization format.

const SCHEMA_VERSION := 4
## Older versions that from_dict upgrades in place. v1 had no story or music/voice settings;
## v2 had no missions, Research Data or weapon upgrades; v3 mixed failed runs into best_points
## and had no attempt counters. Nothing is dropped when upgrading.
const MIGRATABLE_VERSIONS := [1, 2, 3]
const MAX_UPGRADE_LEVEL := 3

## Legacy level id -> {"stars": int, "best_shots": int}. Kept intact for old saves.
var level_results := {}
## mission id -> {
##   completed: bool,
##   best_points: int          best Mission Points of a SUCCESSFUL run (leaderboard-eligible; 0 until a success),
##   best_attempt_points: int  best Mission Points of ANY run, failures included (progress feedback only),
##   best_research_data: int, best_shots: int, best_time: float (successful runs only),
##   optional_completed: Array[String] (successful runs only),
##   attempts: int, completions: int  runs recorded,
##   counts_since_upgrade: bool  true when the record was migrated from v3: the counters then only
##                               cover runs played since the upgrade, because earlier history was
##                               never stored and is not reconstructed.
## }
var mission_results := {}
## Spendable upgrade currency and the lifetime total earned.
var research_data := 0
var research_data_earned := 0
## weapon id -> {attribute: level 1-3}
var weapon_upgrades := {}
var sound_enabled := true
var vibration_enabled := true
var music_enabled := true
var voice_enabled := true
## Story sequence ids (cinematics) the player has seen; they become replayable in the Story Archive.
var seen_sequences := {}
## Schema version the data was loaded from (equals SCHEMA_VERSION for fresh or current saves).
var loaded_version := SCHEMA_VERSION
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


func mission_result(mission_id: String) -> Dictionary:
	return mission_results.get(mission_id, {})


func is_mission_completed(mission_id: String) -> bool:
	return bool(mission_result(mission_id).get("completed", false))


## Records a finished mission from a MissionScoring breakdown. Bests only improve. Research Data
## is granted only for improvement over this mission's previous best, so replaying a mission
## cannot farm currency. Returns the Research Data granted.
func record_mission(mission_id: String, score: Dictionary, shots: int, elapsed: float, optional_completed: Array[String]) -> int:
	var previous: Dictionary = mission_results.get(mission_id, {})
	var best_research := int(previous.get("best_research_data", 0))
	var granted := maxi(0, int(score.research_data) - best_research)
	var success := bool(score.success)
	var optional: Array[String] = []
	optional.assign(previous.get("optional_completed", []))
	for id in optional_completed:
		if success and not optional.has(id):
			optional.append(id)
	optional.sort()
	var points := int(score.mission_points)
	var record := {
		"completed": bool(previous.get("completed", false)) or success,
		"best_points": int(previous.get("best_points", 0)),
		"best_attempt_points": maxi(int(previous.get("best_attempt_points", 0)), points),
		"best_research_data": maxi(best_research, int(score.research_data)),
		"best_shots": int(previous.get("best_shots", 0)),
		"best_time": float(previous.get("best_time", 0.0)),
		"optional_completed": optional,
		"attempts": int(previous.get("attempts", 0)) + 1,
		"completions": int(previous.get("completions", 0)) + (1 if success else 0),
		"counts_since_upgrade": bool(previous.get("counts_since_upgrade", false)),
	}
	if success:
		record.best_points = maxi(record.best_points, points)
		var old_shots: int = record.best_shots
		record.best_shots = shots if old_shots == 0 else mini(old_shots, shots)
		var old_time: float = record.best_time
		record.best_time = elapsed if old_time == 0.0 else minf(old_time, elapsed)
	mission_results[mission_id] = record
	research_data += granted
	research_data_earned += granted
	return granted


func spend_research_data(amount: int) -> bool:
	if amount <= 0 or amount > research_data:
		return false
	research_data -= amount
	return true


func upgrade_level(weapon_id: String, attribute: String) -> int:
	return int(weapon_upgrades.get(weapon_id, {}).get(attribute, 0))


func set_upgrade_level(weapon_id: String, attribute: String, level: int) -> void:
	if not weapon_upgrades.has(weapon_id):
		weapon_upgrades[weapon_id] = {}
	weapon_upgrades[weapon_id][attribute] = clampi(level, 0, MAX_UPGRADE_LEVEL)


func has_seen_sequence(sequence_id: String) -> bool:
	return seen_sequences.has(sequence_id)


## Marks a story sequence as seen. Returns true if it was new.
func mark_sequence_seen(sequence_id: String) -> bool:
	if sequence_id.is_empty() or seen_sequences.has(sequence_id):
		return false
	seen_sequences[sequence_id] = true
	return true


func to_dict() -> Dictionary:
	var seen: Array[String] = []
	for key: String in seen_sequences:
		seen.append(key)
	seen.sort()
	return {
		"version": SCHEMA_VERSION,
		"levels": level_results.duplicate(true),
		"settings": {
			"sound": sound_enabled,
			"vibration": vibration_enabled,
			"music": music_enabled,
			"voice": voice_enabled,
		},
		"story": {"seen": seen},
		"missions": mission_results.duplicate(true),
		"research": {"balance": research_data, "earned": research_data_earned},
		"upgrades": weapon_upgrades.duplicate(true),
	}


## Tolerant loader: invalid fields are dropped with a warning instead of failing the whole save.
static func from_dict(data: Variant) -> ProgressData:
	var progress := ProgressData.new()
	if not data is Dictionary:
		progress.load_warnings.append("save root is not an object; using defaults")
		return progress
	var version: Variant = data.get("version")
	if not _is_whole(version) or not (int(version) == SCHEMA_VERSION or MIGRATABLE_VERSIONS.has(int(version))):
		# Unknown or newer versions are not trusted.
		progress.load_warnings.append("unsupported save version %s; using defaults" % str(version))
		return progress
	# v1 -> v2: levels and settings keep their shape; new fields start at their defaults.
	progress.loaded_version = int(version)

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
		if settings.get("music") is bool:
			progress.music_enabled = settings.music
		if settings.get("voice") is bool:
			progress.voice_enabled = settings.voice
	else:
		progress.load_warnings.append("'settings' is not an object")

	var story: Variant = data.get("story", {})
	if story is Dictionary and story.get("seen", []) is Array:
		for entry: Variant in story.get("seen", []):
			if entry is String and not entry.is_empty():
				progress.seen_sequences[entry] = true
			else:
				progress.load_warnings.append("dropped invalid story sequence id '%s'" % str(entry))
	else:
		progress.load_warnings.append("'story' is not a valid object")

	progress._load_missions(data.get("missions", {}))
	var research: Variant = data.get("research", {})
	if research is Dictionary:
		var balance: Variant = research.get("balance", 0)
		var earned: Variant = research.get("earned", 0)
		if _is_whole(balance) and _is_whole(earned) and balance >= 0 and earned >= balance:
			progress.research_data = int(balance)
			progress.research_data_earned = int(earned)
		else:
			progress.load_warnings.append("invalid Research Data totals; reset to 0")
	else:
		progress.load_warnings.append("'research' is not an object")
	var upgrades: Variant = data.get("upgrades", {})
	if upgrades is Dictionary:
		for weapon_id: Variant in upgrades:
			var weapon_levels: Variant = upgrades[weapon_id]
			if not weapon_id is String or not weapon_levels is Dictionary:
				progress.load_warnings.append("dropped invalid upgrades for '%s'" % str(weapon_id))
				continue
			for attribute: Variant in weapon_levels:
				var level: Variant = weapon_levels[attribute]
				if attribute is String and _is_whole(level) and level >= 0 and level <= MAX_UPGRADE_LEVEL:
					progress.set_upgrade_level(weapon_id, attribute, int(level))
				else:
					progress.load_warnings.append("dropped invalid upgrade %s.%s" % [weapon_id, str(attribute)])
	else:
		progress.load_warnings.append("'upgrades' is not an object")
	return progress


func _load_missions(raw: Variant) -> void:
	if not raw is Dictionary:
		load_warnings.append("'missions' is not an object")
		return
	for mission_id: Variant in raw:
		var entry: Variant = raw[mission_id]
		var ok: bool = mission_id is String and entry is Dictionary 			and entry.get("completed") is bool 			and _is_whole(entry.get("best_points")) and entry.best_points >= 0 			and _is_whole(entry.get("best_research_data")) and entry.best_research_data >= 0 			and _is_whole(entry.get("best_shots")) and entry.best_shots >= 0 			and (entry.get("best_time") is float or entry.get("best_time") is int) and entry.best_time >= 0 			and entry.get("optional_completed") is Array 			and (entry.optional_completed as Array).all(func(v: Variant) -> bool: return v is String)
		if ok and loaded_version >= 4:
			ok = _is_whole(entry.get("best_attempt_points")) and entry.best_attempt_points >= entry.best_points 				and _is_whole(entry.get("attempts")) and _is_whole(entry.get("completions")) 				and entry.completions >= 0 and entry.attempts >= entry.completions 				and entry.get("counts_since_upgrade") is bool
		if not ok:
			load_warnings.append("dropped invalid mission result '%s'" % str(mission_id))
			continue
		var optional: Array[String] = []
		optional.assign(entry.optional_completed)
		var record := {
			"completed": entry.completed,
			"best_points": int(entry.best_points),
			"best_attempt_points": int(entry.get("best_attempt_points", 0)),
			"best_research_data": int(entry.best_research_data),
			"best_shots": int(entry.best_shots),
			"best_time": float(entry.best_time),
			"optional_completed": optional,
			"attempts": int(entry.get("attempts", 0)),
			"completions": int(entry.get("completions", 0)),
			"counts_since_upgrade": bool(entry.get("counts_since_upgrade", false)),
		}
		if loaded_version < 4:
			# v3 -> v4. v3 kept the best points of ANY run. Every success scores at least the
			# completion and critical-asset bonuses, more than any failure can reach, so a completed
			# record's best_points came from a successful run and stays leaderboard-eligible. An
			# uncompleted record only has failed runs: its points become attempt points only.
			# Counters are not reconstructed: they start at 0 and the record is flagged.
			record.best_attempt_points = record.best_points
			if not record.completed:
				record.best_points = 0
			record.counts_since_upgrade = true
		mission_results[mission_id] = record


static func _is_whole(value: Variant) -> bool:
	return (value is int) or (value is float and value == floorf(value))
