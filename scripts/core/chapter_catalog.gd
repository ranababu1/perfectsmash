class_name ChapterCatalog
extends RefCounted
## Narrative chapters: which display-level range belongs to which chapter, plus the story sequence
## ids played around it. Presentation data only; it never affects physics, scoring or unlocks.
## Level numbers are 1-based positions in the level catalog, not level ids.

const DEFAULT_PATH := "res://data/chapters.json"
const REQUIRED_STRINGS := ["id", "title", "organization", "theme", "intro_sequence", "outro_sequence"]


class Chapter:
	var id := ""
	var number := 0
	var title := ""
	var organization := ""
	var year := 0
	var first_level := 0
	var last_level := 0
	var theme := ""
	var intro_sequence := ""
	var outro_sequence := ""

	func contains_level(level_number: int) -> bool:
		return level_number >= first_level and level_number <= last_level


var opening_sequence := ""
var chapters: Array[Chapter] = []
var errors := PackedStringArray()


static func load_from_file(path: String = DEFAULT_PATH) -> ChapterCatalog:
	var file := FileAccess.open(path, FileAccess.READ)
	if file == null:
		var catalog := ChapterCatalog.new()
		catalog.errors.append("cannot open %s (error %d)" % [path, FileAccess.get_open_error()])
		return catalog
	return from_json_text(file.get_as_text())


static func from_json_text(text: String) -> ChapterCatalog:
	var catalog := ChapterCatalog.new()
	var json := JSON.new()
	if json.parse(text) != OK:
		catalog.errors.append("invalid JSON at line %d: %s" % [json.get_error_line(), json.get_error_message()])
		return catalog
	catalog._parse(json.data)
	return catalog


func is_valid() -> bool:
	return errors.is_empty()


## The chapter containing a 1-based level number, or null.
func chapter_for_level(level_number: int) -> Chapter:
	for chapter in chapters:
		if chapter.contains_level(level_number):
			return chapter
	return null


func total_levels() -> int:
	return chapters[-1].last_level if not chapters.is_empty() else 0


## Every story sequence id referenced by the catalog, in play order.
func sequence_ids() -> Array[String]:
	var ids: Array[String] = []
	if not opening_sequence.is_empty():
		ids.append(opening_sequence)
	for chapter in chapters:
		ids.append(chapter.intro_sequence)
		ids.append(chapter.outro_sequence)
	return ids


func _parse(root: Variant) -> void:
	if not root is Dictionary or not root.get("chapters") is Array:
		errors.append("root must be an object with a 'chapters' array")
		return
	var opening: Variant = root.get("opening_sequence", "")
	opening_sequence = opening if opening is String else ""
	var expected_first := 1
	var seen_ids := {}
	var seen_sequences := {opening_sequence: true} if not opening_sequence.is_empty() else {}
	for entry: Variant in root.chapters:
		if not entry is Dictionary:
			errors.append("chapter entry is not an object")
			continue
		var chapter := Chapter.new()
		chapter.number = chapters.size() + 1
		for key: String in REQUIRED_STRINGS:
			var value: Variant = entry.get(key)
			if value is String and not value.is_empty():
				chapter.set(key, value)
			else:
				errors.append("chapter %d: missing string '%s'" % [chapter.number, key])
		for key: String in ["year", "first_level", "last_level"]:
			var value: Variant = entry.get(key)
			if (value is int) or (value is float and value == floorf(value)):
				chapter.set(key, int(value))
			else:
				errors.append("chapter %d: '%s' must be a whole number" % [chapter.number, key])
		var prefix := "chapter '%s': " % chapter.id
		if chapter.first_level != expected_first:
			errors.append(prefix + "first_level must be %d (ranges must be contiguous from 1)" % expected_first)
		if chapter.last_level < chapter.first_level:
			errors.append(prefix + "last_level is before first_level")
		if seen_ids.has(chapter.id):
			errors.append(prefix + "duplicate chapter id")
		seen_ids[chapter.id] = true
		for sequence: String in [chapter.intro_sequence, chapter.outro_sequence]:
			if seen_sequences.has(sequence):
				errors.append(prefix + "sequence id '%s' is used twice" % sequence)
			seen_sequences[sequence] = true
		expected_first = chapter.last_level + 1
		chapters.append(chapter)
	if chapters.is_empty():
		errors.append("catalog contains no chapters")
