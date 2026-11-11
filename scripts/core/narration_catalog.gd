class_name NarrationCatalog
extends RefCounted
## Spoken narration for the story cinematics, as data (data/narration.json, generated from the
## narration package manifest by tools/audio/build_narration_map.py). This is the only place
## narration paths and timings live; apply_to() writes them onto the CinematicCatalog:
##   slide.voice           the slide's voice clip (res://)
##   slide.voice_delay     seconds after the slide appears that the line starts (bed pre-roll)
##   slide.subtitle_delay  seconds after the slide appears that its subtitle appears (manifest sync)
##   slide.duration        how long the slide holds (manifest timeline: the line, its gap, and on
##                         the last slide the tail before the end card)
##   sequence.music        the cinematic's own music bed, at sequence.music_volume_db
## Story text is never touched. A sequence missing from the file plays as subtitles over its
## chapter music, as before.

const DEFAULT_PATH := "res://data/narration.json"
const DEFAULT_BUS := "Voice"
## How far the music bed drops under narration (dB) and the envelope of the live duck.
const DEFAULT_DUCK_DB := 9.0
const DEFAULT_DUCK_ATTACK := 0.12
const DEFAULT_DUCK_HOLD := 0.25
const DEFAULT_DUCK_RELEASE := 0.6


class SlideNarration:
	var voice := ""
	## Clip length in seconds (from the manifest; the stream's own length wins when loaded).
	var duration := 0.0
	var voice_at := 0.0
	var subtitle_at := 0.0
	var hold := 0.0


class SequenceNarration:
	var bed := ""
	var bed_volume_db := -10.5
	var slides: Array[SlideNarration] = []


## sequence id -> SequenceNarration
var sequences := {}
var bus := DEFAULT_BUS
var duck_db := DEFAULT_DUCK_DB
var duck_attack := DEFAULT_DUCK_ATTACK
var duck_hold := DEFAULT_DUCK_HOLD
var duck_release := DEFAULT_DUCK_RELEASE
## Delivery status from the file ("integrated", "pending_assets", ...).
var status := ""
var errors := PackedStringArray()


static func key(sequence_id: String, slide_index: int) -> String:
	return "%s/%d" % [sequence_id, slide_index + 1]


static func load_from_file(path: String = DEFAULT_PATH) -> NarrationCatalog:
	var file := FileAccess.open(path, FileAccess.READ)
	if file == null:
		var catalog := NarrationCatalog.new()
		catalog.errors.append("cannot open %s (error %d)" % [path, FileAccess.get_open_error()])
		return catalog
	return from_json_text(file.get_as_text())


static func from_json_text(text: String) -> NarrationCatalog:
	var catalog := NarrationCatalog.new()
	var json := JSON.new()
	if json.parse(text) != OK:
		catalog.errors.append("invalid JSON at line %d: %s" % [json.get_error_line(), json.get_error_message()])
		return catalog
	var root: Variant = json.data
	if not root is Dictionary:
		catalog.errors.append("root must be an object")
		return catalog
	catalog.status = str(root.get("status", ""))
	catalog.bus = str(root.get("bus", DEFAULT_BUS))
	catalog.duck_db = catalog._number(root, "duck_db", DEFAULT_DUCK_DB, "")
	catalog.duck_attack = catalog._number(root, "duck_attack_s", DEFAULT_DUCK_ATTACK, "")
	catalog.duck_hold = catalog._number(root, "duck_hold_s", DEFAULT_DUCK_HOLD, "")
	catalog.duck_release = catalog._number(root, "duck_release_s", DEFAULT_DUCK_RELEASE, "")
	var raw: Variant = root.get("sequences", {})
	if not raw is Dictionary:
		catalog.errors.append("'sequences' must be an object")
		return catalog
	for sequence_id: Variant in raw:
		catalog._add_sequence(str(sequence_id), raw[sequence_id])
	return catalog


func is_valid() -> bool:
	return errors.is_empty()


func voiced_slide_count() -> int:
	var total := 0
	for entry: SequenceNarration in sequences.values():
		total += entry.slides.size()
	return total


func clip_for(sequence_id: String, slide_index: int) -> String:
	var entry: SequenceNarration = sequences.get(sequence_id)
	if entry == null or slide_index < 0 or slide_index >= entry.slides.size():
		return ""
	return entry.slides[slide_index].voice


## Narrated sequences that do not match `cinematics` (unknown id or a different slide count).
func unknown_keys(cinematics: CinematicCatalog) -> PackedStringArray:
	var unknown := PackedStringArray()
	for sequence_id: String in sequences:
		var sequence := cinematics.get_sequence(sequence_id) if cinematics != null else null
		if sequence == null or sequence.slides.size() != (sequences[sequence_id] as SequenceNarration).slides.size():
			unknown.append(sequence_id)
	return unknown


## Writes voice, timing and bed onto every narrated sequence of `cinematics` (see the header).
## Sequences that do not match are left as they are. Returns the number of voiced slides.
func apply_to(cinematics: CinematicCatalog) -> int:
	var voiced := 0
	if cinematics == null:
		return voiced
	var mismatched := unknown_keys(cinematics)
	for sequence_id: String in sequences:
		if mismatched.has(sequence_id):
			continue
		var entry: SequenceNarration = sequences[sequence_id]
		var sequence := cinematics.get_sequence(sequence_id)
		sequence.music = entry.bed
		sequence.music_volume_db = entry.bed_volume_db
		for i in entry.slides.size():
			var timing := entry.slides[i]
			var slide := sequence.slides[i]
			slide.voice = timing.voice
			slide.voice_delay = timing.voice_at
			slide.subtitle_delay = timing.subtitle_at
			slide.duration = timing.hold
			voiced += 1
	return voiced


## All slide keys of `cinematics` in story order (what a complete narration package covers).
static func expected_keys(cinematics: CinematicCatalog) -> PackedStringArray:
	var keys := PackedStringArray()
	if cinematics == null:
		return keys
	for sequence_id: String in cinematics.order:
		for i in cinematics.get_sequence(sequence_id).slides.size():
			keys.append(key(sequence_id, i))
	return keys


func _add_sequence(sequence_id: String, raw: Variant) -> void:
	var prefix := "narration '%s': " % sequence_id
	if not raw is Dictionary:
		errors.append(prefix + "must be an object")
		return
	var entry := SequenceNarration.new()
	entry.bed = _path(raw, "bed", prefix, true)
	entry.bed_volume_db = _number(raw, "bed_volume_db", -10.5, prefix, true)
	var slides: Variant = raw.get("slides")
	if not slides is Array or slides.is_empty():
		errors.append(prefix + "needs a 'slides' array")
		return
	for i in slides.size():
		var item: Variant = slides[i]
		var slide_prefix := "%s/%d: " % [sequence_id, i + 1]
		if not item is Dictionary:
			errors.append(slide_prefix + "must be an object")
			continue
		var timing := SlideNarration.new()
		timing.voice = _path(item, "voice", slide_prefix, false)
		timing.duration = _number(item, "duration", 0.0, slide_prefix)
		timing.voice_at = _number(item, "voice_at", 0.0, slide_prefix)
		timing.subtitle_at = _number(item, "subtitle_at", timing.voice_at, slide_prefix)
		timing.hold = _number(item, "hold", 0.0, slide_prefix)
		if timing.hold < timing.voice_at + timing.duration:
			errors.append(slide_prefix + "hold %.2f s is shorter than its line" % timing.hold)
		entry.slides.append(timing)
	sequences[sequence_id] = entry


func _path(entry: Dictionary, field: String, prefix: String, optional: bool) -> String:
	var value: Variant = entry.get(field, "")
	if optional and str(value).is_empty():
		return ""
	if not value is String or not (value as String).begins_with("res://"):
		errors.append(prefix + "'%s' must be a res:// path" % field)
		return ""
	if not ResourceLoader.exists(value):
		errors.append(prefix + "file not found %s" % value)
		return ""
	return value


## A non-negative number (any number when `signed`); `fallback` when absent.
func _number(entry: Dictionary, field: String, fallback: float, prefix: String, signed: bool = false) -> float:
	if not entry.has(field):
		return fallback
	var value: Variant = entry[field]
	if (value is float or value is int) and (signed or value >= 0.0):
		return float(value)
	errors.append(prefix + "'%s' must be a %snumber" % [field, "" if signed else "non-negative "])
	return fallback
