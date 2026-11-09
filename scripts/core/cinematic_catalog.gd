class_name CinematicCatalog
extends RefCounted
## Story sequences (opening, chapter intros/outros, finale) as validated data from
## data/cinematics.json. One reusable CinematicPlayer plays any of them; no sequence is hard-coded.
## Image, voice and music paths are optional so a sequence can ship as subtitles over a procedural
## plate until approved art and audio exist.

const DEFAULT_PATH := "res://data/cinematics.json"
const SPEAKER_NARRATOR := "narrator"
const SPEAKER_CONTROL := "control"
const SPEAKERS := [SPEAKER_NARRATOR, SPEAKER_CONTROL]
const MOTIONS := ["push_in", "pull_back", "pan_left", "pan_right", "static"]
## Reading pace for subtitle-only slides (about 150 words per minute) plus breathing room.
const READING_WORDS_PER_SECOND := 2.5
const SLIDE_PADDING_SECONDS := 1.2
const MIN_SLIDE_SECONDS := 3.5


class Slide:
	var speaker := SPEAKER_NARRATOR
	var subtitle := ""
	var caption := ""
	var motion := "push_in"
	var image := ""
	var voice := ""
	## Explicit duration in seconds; 0 means derive it from the subtitle length.
	var duration := 0.0

	func word_count() -> int:
		return subtitle.split(" ", false).size()

	func reading_seconds() -> float:
		if duration > 0.0:
			return duration
		return maxf(MIN_SLIDE_SECONDS, word_count() / READING_WORDS_PER_SECOND + SLIDE_PADDING_SECONDS)


class Sequence:
	var id := ""
	var title := ""
	var theme := ChapterTheme.DEFAULT_KEY
	var music := ""
	var slides: Array[Slide] = []
	var end_title := ""
	var end_subtitle := ""

	func estimated_seconds() -> float:
		var total := 0.0
		for slide in slides:
			total += slide.reading_seconds()
		return total


var sequences := {}
var order: Array[String] = []
var errors := PackedStringArray()


static func load_from_file(path: String = DEFAULT_PATH) -> CinematicCatalog:
	var file := FileAccess.open(path, FileAccess.READ)
	if file == null:
		var catalog := CinematicCatalog.new()
		catalog.errors.append("cannot open %s (error %d)" % [path, FileAccess.get_open_error()])
		return catalog
	return from_json_text(file.get_as_text())


static func from_json_text(text: String) -> CinematicCatalog:
	var catalog := CinematicCatalog.new()
	var json := JSON.new()
	if json.parse(text) != OK:
		catalog.errors.append("invalid JSON at line %d: %s" % [json.get_error_line(), json.get_error_message()])
		return catalog
	var root: Variant = json.data
	if not root is Dictionary or not root.get("sequences") is Array:
		catalog.errors.append("root must be an object with a 'sequences' array")
		return catalog
	for entry: Variant in root.sequences:
		catalog._add_sequence(entry)
	if catalog.order.is_empty():
		catalog.errors.append("catalog contains no sequences")
	return catalog


func is_valid() -> bool:
	return errors.is_empty()


func has_sequence(sequence_id: String) -> bool:
	return sequences.has(sequence_id)


func get_sequence(sequence_id: String) -> Sequence:
	return sequences.get(sequence_id)


func slide_count() -> int:
	var total := 0
	for id in order:
		total += (sequences[id] as Sequence).slides.size()
	return total


func _add_sequence(entry: Variant) -> void:
	if not entry is Dictionary:
		errors.append("sequence entry is not an object")
		return
	var sequence := Sequence.new()
	sequence.id = _string(entry, "id", "sequence")
	var prefix := "sequence '%s': " % sequence.id
	sequence.title = _string(entry, "title", prefix)
	sequence.theme = str(entry.get("theme", ChapterTheme.DEFAULT_KEY))
	if not ChapterTheme.has_key(sequence.theme):
		errors.append(prefix + "unknown theme '%s'" % sequence.theme)
	sequence.music = _optional_path(entry, "music", prefix)
	var end_card: Variant = entry.get("end_card", {})
	if end_card is Dictionary:
		sequence.end_title = str(end_card.get("title", ""))
		sequence.end_subtitle = str(end_card.get("subtitle", ""))
	else:
		errors.append(prefix + "end_card must be an object")
	var slides: Variant = entry.get("slides")
	if not slides is Array or slides.is_empty():
		errors.append(prefix + "needs at least one slide")
	else:
		for slide_entry: Variant in slides:
			var slide := _parse_slide(slide_entry, prefix)
			if slide != null:
				sequence.slides.append(slide)
	if sequences.has(sequence.id):
		errors.append(prefix + "duplicate sequence id")
		return
	sequences[sequence.id] = sequence
	order.append(sequence.id)


func _parse_slide(entry: Variant, prefix: String) -> Slide:
	if not entry is Dictionary:
		errors.append(prefix + "slide is not an object")
		return null
	var slide := Slide.new()
	slide.speaker = str(entry.get("speaker", SPEAKER_NARRATOR))
	if not SPEAKERS.has(slide.speaker):
		errors.append(prefix + "unknown speaker '%s'" % slide.speaker)
	slide.subtitle = _string(entry, "subtitle", prefix)
	slide.caption = str(entry.get("caption", ""))
	slide.motion = str(entry.get("motion", "push_in"))
	if not MOTIONS.has(slide.motion):
		errors.append(prefix + "unknown motion '%s'" % slide.motion)
	slide.image = _optional_path(entry, "image", prefix)
	slide.voice = _optional_path(entry, "voice", prefix)
	var duration: Variant = entry.get("duration", 0.0)
	if (duration is float or duration is int) and duration >= 0.0:
		slide.duration = float(duration)
	else:
		errors.append(prefix + "duration must be a non-negative number")
	return slide


func _string(entry: Dictionary, key: String, prefix: String) -> String:
	var value: Variant = entry.get(key)
	if value is String and not value.is_empty():
		return value
	errors.append("%s missing string '%s'" % [prefix, key])
	return ""


func _optional_path(entry: Dictionary, key: String, prefix: String) -> String:
	var value: Variant = entry.get(key, "")
	if value is String and (value.is_empty() or value.begins_with("res://")):
		return value
	errors.append(prefix + "'%s' must be a res:// path" % key)
	return ""
