class_name AudioCatalog
extends RefCounted
## Loads and validates data/audio.json: sound ids (file variants + procedural fallback), the
## material -> impact sound map, and music cues. Node-free; AudioService and MusicDirector use
## it. Missing files are not errors (an approved asset may not have been added yet): they are
## reported by missing_files() and the procedural fallback plays instead.

const DEFAULT_PATH := "res://data/audio.json"
## Procedural sounds AudioService synthesizes; every sound's fallback must be one of these.
const PROCEDURAL := ["launch", "impact", "pop", "shatter", "win", "lose", "click"]
const MAX_PITCH_VARIANCE := 0.5


class SoundSpec:
	var id := ""
	var fallback := ""
	var volume_db := 0.0
	var pitch_variance := 0.0
	var files: Array[String] = []


class MusicCue:
	var id := ""
	var file := ""
	var volume_db := -12.0
	var loop_overlap := 0.0


var sounds := {}
var music := {}
var impact_by_material := {}
var default_impact := ""
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
		catalog._add_cue(id, root.music[id])
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
	return catalog


func is_valid() -> bool:
	return errors.is_empty()


func has_sound(id: String) -> bool:
	return sounds.has(id)


func get_sound(id: String) -> SoundSpec:
	return sounds.get(id)


func get_cue(id: String) -> MusicCue:
	return music.get(id)


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
	for cue: MusicCue in music.values():
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
	sounds[spec.id] = spec


func _add_cue(id: Variant, entry: Variant) -> void:
	if not id is String or id.is_empty() or not entry is Dictionary:
		errors.append("music cue '%s' must be an object" % str(id))
		return
	var cue := MusicCue.new()
	cue.id = id
	var prefix := "music cue '%s': " % id
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
	music[cue.id] = cue
