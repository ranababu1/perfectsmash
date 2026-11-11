class_name NarrationCatalog
extends RefCounted
## Spoken narration for the story cinematics, as data (data/narration.json): which audio clip
## voices which slide. This is the only place narration paths live; CinematicCatalog slides get
## their `voice` from here (apply_to), and CinematicPlayer plays whatever a slide carries.
##
## Clip keys are "<sequence id>/<slide number>" with slides numbered from 1 in data/cinematics.json
## order, e.g. "opening/1", "helix_intro/3". A slide without a clip plays as subtitles only, so
## narration can be integrated sequence by sequence as approved clips arrive. Paths must be
## res:// files that exist; nothing is guessed or generated.

const DEFAULT_PATH := "res://data/narration.json"
const DEFAULT_BUS := "Voice"
## How far the music bed drops under narration (dB) and how fast it moves.
const DEFAULT_DUCK_DB := 9.0

## "<sequence id>/<slide number>" -> res:// path
var clips := {}
var bus := DEFAULT_BUS
var duck_db := DEFAULT_DUCK_DB
## Free-text delivery status from the file ("pending_assets", "integrated", ...).
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
	var duck: Variant = root.get("duck_db", DEFAULT_DUCK_DB)
	if (duck is float or duck is int) and duck >= 0.0:
		catalog.duck_db = float(duck)
	else:
		catalog.errors.append("duck_db must be a non-negative number")
	var raw: Variant = root.get("clips", {})
	if not raw is Dictionary:
		catalog.errors.append("'clips' must be an object")
		return catalog
	for clip_key: Variant in raw:
		var path: Variant = raw[clip_key]
		if not clip_key is String or not path is String or not (path as String).begins_with("res://"):
			catalog.errors.append("clip '%s' must map to a res:// path" % str(clip_key))
			continue
		if not ResourceLoader.exists(path):
			catalog.errors.append("clip '%s': file not found %s" % [clip_key, path])
			continue
		catalog.clips[clip_key] = path
	return catalog


func is_valid() -> bool:
	return errors.is_empty()


func clip_for(sequence_id: String, slide_index: int) -> String:
	return clips.get(key(sequence_id, slide_index), "")


## Every clip key that names a real slide of `cinematics`; returns the keys that do not.
func unknown_keys(cinematics: CinematicCatalog) -> PackedStringArray:
	var unknown := PackedStringArray()
	for clip_key: String in clips:
		var sequence_id := clip_key.get_slice("/", 0)
		var number := clip_key.get_slice("/", 1)
		var sequence := cinematics.get_sequence(sequence_id) if cinematics != null else null
		if sequence == null or not number.is_valid_int() or int(number) < 1 or int(number) > sequence.slides.size():
			unknown.append(clip_key)
	return unknown


## Sets each slide's `voice` from the mapping (slides without a clip get ""). Returns the number of
## slides that now carry narration.
func apply_to(cinematics: CinematicCatalog) -> int:
	var voiced := 0
	if cinematics == null:
		return voiced
	for sequence_id: String in cinematics.order:
		var sequence := cinematics.get_sequence(sequence_id)
		for i in sequence.slides.size():
			sequence.slides[i].voice = clip_for(sequence_id, i)
			if not sequence.slides[i].voice.is_empty():
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
