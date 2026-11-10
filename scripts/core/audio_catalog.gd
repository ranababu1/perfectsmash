class_name AudioCatalog
extends RefCounted
## Loads and validates data/audio.json: sound ids (file variants + procedural fallback, bus), the
## material -> impact and material -> destruction sound maps, music and ambience cues (track,
## volume, bus, loop flag) and per-mission audio plans (intensity steps, critical layer,
## stingers, ambience bed). Node-free; AudioService and MusicDirector use
## it. Missing files are not errors (an approved asset may not have been added yet): they are
## reported by missing_files() and the procedural fallback plays instead.

const DEFAULT_PATH := "res://data/audio.json"
## Procedural sounds AudioService synthesizes; every sound's fallback must be one of these.
const PROCEDURAL := ["launch", "impact", "pop", "shatter", "win", "lose", "click"]
const MAX_PITCH_VARIANCE := 0.5
## Buses in default_bus_layout.tres.
const BUSES := ["Master", "Music", "Ambience", "SFX", "UI"]


class SoundSpec:
	var id := ""
	var fallback := ""
	var volume_db := 0.0
	var pitch_variance := 0.0
	var bus := "SFX"
	var files: Array[String] = []


class MusicCue:
	var id := ""
	var file := ""
	var volume_db := -12.0
	var loop_overlap := 0.0
	var bus := "Music"
	## True for seamless loops (the import loops the stream); false for one-shots and stingers.
	var loops := true


var sounds := {}
var music := {}
var ambience := {}
var impact_by_material := {}
var default_impact := ""
var destroyed_by_material := {}
var default_destroyed := ""
## mission id -> {intensity: Array[String], critical_layer, victory, defeat, ambience}
var missions := {}
var errors := PackedStringArray()


static func load_from_file(path: String = DEFAULT_PATH) -> AudioCatalog:
	var file := FileAccess.open(path, FileAccess.READ)
	if file == null:
		var catalog := AudioCatalog.new()
		catalog.errors.append("cannot open %s (error %d)" % [path, FileAccess.get_open_error()])
		return catalog
	return from_json_text(file.get_as_text())


static func from_json_text(text: String) -> AudioCatalog:
	var catalog := AudioCatalog.new()
	var json := JSON.new()
	if json.parse(text) != OK:
		catalog.errors.append("invalid JSON at line %d: %s" % [json.get_error_line(), json.get_error_message()])
		return catalog
	var root: Variant = json.data
	if not root is Dictionary or not root.get("sounds") is Dictionary or not root.get("music") is Dictionary:
		catalog.errors.append("root must be an object with 'sounds' and 'music' objects")
		return catalog
	for id: Variant in root.sounds:
		catalog._add_sound(id, root.sounds[id])
	for id: Variant in root.music:
		catalog._add_cue(id, root.music[id], catalog.music, "Music")
	var ambience: Variant = root.get("ambience", {})
	if ambience is Dictionary:
		for id: Variant in ambience:
			catalog._add_cue(id, ambience[id], catalog.ambience, "Ambience")
	else:
		catalog.errors.append("'ambience' must be an object")
	var impacts: Variant = root.get("impact_by_material", {})
	if impacts is Dictionary:
		for material: Variant in impacts:
			var sound: Variant = impacts[material]
			if material is String and sound is String and catalog.sounds.has(sound):
				catalog.impact_by_material[material] = sound
			else:
				catalog.errors.append("impact_by_material '%s' must name a known sound" % str(material))
	else:
		catalog.errors.append("'impact_by_material' must be an object")
	var fallback_impact: Variant = root.get("default_impact", "")
	if fallback_impact is String and catalog.sounds.has(fallback_impact):
		catalog.default_impact = fallback_impact
	else:
		catalog.errors.append("'default_impact' must name a known sound")
	var destroyed: Variant = root.get("destroyed_by_material", {})
	if destroyed is Dictionary:
		for material: Variant in destroyed:
			if material is String and destroyed[material] is String and catalog.sounds.has(destroyed[material]):
				catalog.destroyed_by_material[material] = destroyed[material]
			else:
				catalog.errors.append("destroyed_by_material '%s' must name a known sound" % str(material))
	var fallback_destroyed: Variant = root.get("default_destroyed", "")
	if fallback_destroyed is String and (fallback_destroyed.is_empty() or catalog.sounds.has(fallback_destroyed)):
		catalog.default_destroyed = fallback_destroyed
	else:
		catalog.errors.append("'default_destroyed' must name a known sound")
	var missions: Variant = root.get("missions", {})
	if missions is Dictionary:
		for mission_id: Variant in missions:
			catalog._add_mission(mission_id, missions[mission_id])
	return catalog


func is_valid() -> bool:
	return errors.is_empty()


func has_sound(id: String) -> bool:
	return sounds.has(id)


func get_sound(id: String) -> SoundSpec:
	return sounds.get(id)


func get_cue(id: String) -> MusicCue:
	return music.get(id)


func get_ambience(id: String) -> MusicCue:
	return ambience.get(id)


## The destruction sound for a material ("" when none is mapped and there is no default).
func destroyed_sound_for(material_id: String) -> String:
	return destroyed_by_material.get(material_id, default_destroyed)


## The audio plan of a mission ({} when it has none).
func mission_plan(mission_id: String) -> Dictionary:
	return missions.get(mission_id, {})


## The impact sound for a material (the default impact for unknown or empty materials).
func impact_sound_for(material_id: String) -> String:
	return impact_by_material.get(material_id, default_impact)


## Referenced files that do not exist in the project (sounds and music).
func missing_files() -> PackedStringArray:
	var missing := PackedStringArray()
	for spec: SoundSpec in sounds.values():
		for path in spec.files:
			if not ResourceLoader.exists(path):
				missing.append(path)
	for cue: MusicCue in music.values() + ambience.values():
		if not cue.file.is_empty() and not ResourceLoader.exists(cue.file):
			missing.append(cue.file)
	return missing


func _add_sound(id: Variant, entry: Variant) -> void:
	if not id is String or id.is_empty() or not entry is Dictionary:
		errors.append("sound '%s' must be an object" % str(id))
		return
	var spec := SoundSpec.new()
	spec.id = id
	var prefix := "sound '%s': " % id
	var fallback: Variant = entry.get("fallback")
	if fallback is String and PROCEDURAL.has(fallback):
		spec.fallback = fallback
	else:
		errors.append(prefix + "fallback must be one of %s" % str(PROCEDURAL))
	var volume: Variant = entry.get("volume_db", 0.0)
	if (volume is float or volume is int) and volume >= -40.0 and volume <= 12.0:
		spec.volume_db = float(volume)
	else:
		errors.append(prefix + "volume_db must be a number in [-40, 12]")
	var variance: Variant = entry.get("pitch_variance", 0.0)
	if (variance is float or variance is int) and variance >= 0.0 and variance <= MAX_PITCH_VARIANCE:
		spec.pitch_variance = float(variance)
	else:
		errors.append(prefix + "pitch_variance must be in [0, %s]" % MAX_PITCH_VARIANCE)
	var files: Variant = entry.get("files", [])
	if files is Array and files.all(func(f: Variant) -> bool: return f is String and (f as String).begins_with("res://")):
		spec.files.assign(files)
	else:
		errors.append(prefix + "files must be an array of res:// paths")
	var bus: Variant = entry.get("bus", "SFX")
	if bus is String and BUSES.has(bus):
		spec.bus = bus
	else:
		errors.append(prefix + "bus must be one of %s" % str(BUSES))
	sounds[spec.id] = spec


func _add_cue(id: Variant, entry: Variant, into: Dictionary, default_bus: String) -> void:
	if not id is String or id.is_empty() or not entry is Dictionary:
		errors.append("music cue '%s' must be an object" % str(id))
		return
	var cue := MusicCue.new()
	cue.id = id
	cue.bus = default_bus
	var prefix := "music cue '%s': " % id
	var bus: Variant = entry.get("bus", default_bus)
	if bus is String and BUSES.has(bus):
		cue.bus = bus
	else:
		errors.append(prefix + "bus must be one of %s" % str(BUSES))
	var loops: Variant = entry.get("loops", true)
	if loops is bool:
		cue.loops = loops
	else:
		errors.append(prefix + "loops must be true or false")
	var file: Variant = entry.get("file", "")
	if file is String and (file.is_empty() or (file as String).begins_with("res://")):
		cue.file = file
	else:
		errors.append(prefix + "file must be empty or a res:// path")
	var volume: Variant = entry.get("volume_db", -12.0)
	if (volume is float or volume is int) and volume >= -40.0 and volume <= 0.0:
		cue.volume_db = float(volume)
	else:
		errors.append(prefix + "volume_db must be a number in [-40, 0]")
	var overlap: Variant = entry.get("loop_overlap", 0.0)
	if (overlap is float or overlap is int) and overlap >= 0.0:
		cue.loop_overlap = float(overlap)
	else:
		errors.append(prefix + "loop_overlap must be >= 0")
	into[cue.id] = cue


func _add_mission(mission_id: Variant, entry: Variant) -> void:
	if not mission_id is String or not entry is Dictionary:
		errors.append("mission audio '%s' must be an object" % str(mission_id))
		return
	var prefix := "mission audio '%s': " % mission_id
	var intensity: Variant = entry.get("intensity", [])
	if not intensity is Array or not intensity.all(func(c: Variant) -> bool: return c is String and music.has(c)):
		errors.append(prefix + "intensity must list known music cues")
		intensity = []
	var plan := {"intensity": intensity, "critical_layer": "", "victory": "", "defeat": "", "ambience": ""}
	for key: String in ["critical_layer", "victory", "defeat"]:
		var cue: Variant = entry.get(key, "")
		if cue is String and (cue.is_empty() or music.has(cue)):
			plan[key] = cue
		else:
			errors.append(prefix + "%s must name a known music cue" % key)
	var bed: Variant = entry.get("ambience", "")
	if bed is String and (bed.is_empty() or ambience.has(bed)):
		plan.ambience = bed
	else:
		errors.append(prefix + "ambience must name a known ambience cue")
	missions[mission_id] = plan
