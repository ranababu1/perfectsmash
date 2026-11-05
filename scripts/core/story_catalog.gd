class_name StoryCatalog
extends RefCounted
## The campaign storyline from data/story.json: speakers, chapters (by mission number), a briefing
## and a debrief for every mission, and pools of failure lines. Content only, no presentation.
##
## A dialogue line is returned as {"speaker": id, "name": String, "color": Color, "pitch": float, "text": String}.

const DEFAULT_PATH := "res://data/story.json"

var title := ""
## id -> {"name": String, "color": Color, "pitch": float}
var speakers := {}
## Each: {"title", "subtitle", "first": int, "last": int (1-based mission numbers), "intro": Array}
var chapters: Array[Dictionary] = []
## level id -> {"briefing": Array, "debrief": Array} of [speaker, text] pairs
var missions := {}
var fail_lines := {"fail": [], "fail_ally": [], "fail_cargo": []}
var errors := PackedStringArray()


static func load_from_file(path: String = DEFAULT_PATH) -> StoryCatalog:
	var story := StoryCatalog.new()
	var text := FileAccess.get_file_as_string(path)
	if text.is_empty():
		story.errors.append("cannot read %s" % path)
		return story
	var data: Variant = JSON.parse_string(text)
	if not data is Dictionary:
		story.errors.append("story is not a JSON object")
		return story
	story._parse(data)
	return story


func is_valid() -> bool:
	return errors.is_empty()


func _parse(data: Dictionary) -> void:
	title = str(data.get("title", ""))
	var raw_speakers: Variant = data.get("speakers", {})
	if raw_speakers is Dictionary:
		for id: String in raw_speakers:
			var s: Dictionary = raw_speakers[id]
			speakers[id] = {"name": str(s.get("name", id)), "color": Color(str(s.get("color", "ffffff"))), "pitch": float(s.get("pitch", 1.0))}
	for c: Variant in data.get("chapters", []):
		if c is Dictionary:
			chapters.append({"title": str(c.get("title", "")), "subtitle": str(c.get("subtitle", "")),
				"first": int(c.get("first", 0)), "last": int(c.get("last", 0)), "intro": c.get("intro", [])})
	var raw_missions: Variant = data.get("missions", {})
	if raw_missions is Dictionary:
		missions = raw_missions
	for key: String in fail_lines:
		fail_lines[key] = data.get(key, [])
	_check_lines("fail", fail_lines.fail, true)
	for c in chapters:
		_check_lines("chapter '%s' intro" % c.title, c.intro, false)
	for id: String in missions:
		var m: Variant = missions[id]
		if not m is Dictionary:
			errors.append("mission %s is not an object" % id)
			continue
		_check_lines("%s briefing" % id, m.get("briefing", []), true)
		_check_lines("%s debrief" % id, m.get("debrief", []), true)


func _check_lines(where: String, lines: Variant, required: bool) -> void:
	if not lines is Array or (required and lines.is_empty()):
		errors.append("%s: needs at least one line" % where)
		return
	for line: Variant in lines:
		if not line is Array or line.size() != 2 or not speakers.has(str(line[0])) or str(line[1]).strip_edges().is_empty():
			errors.append("%s: bad line %s" % [where, str(line)])


## Cross-checks against the level catalog: every level has a mission entry, chapters tile 1..N.
func validate_against(level_ids: Array[String]) -> PackedStringArray:
	var problems := PackedStringArray()
	for id in level_ids:
		if not missions.has(id):
			problems.append("no story for level %s" % id)
	for id: String in missions:
		if not level_ids.has(id):
			problems.append("story for unknown level %s" % id)
	var expected := 1
	for c in chapters:
		if c.first != expected or c.last < c.first:
			problems.append("chapter '%s' covers %d-%d, expected to start at %d" % [c.title, c.first, c.last, expected])
		expected = c.last + 1
	if expected != level_ids.size() + 1:
		problems.append("chapters cover %d missions, catalog has %d" % [expected - 1, level_ids.size()])
	return problems


## 0-based chapter index for a 0-based level index, or -1.
func chapter_index(level_index: int) -> int:
	for i in chapters.size():
		if level_index + 1 >= chapters[i].first and level_index + 1 <= chapters[i].last:
			return i
	return -1


func is_chapter_start(level_index: int) -> bool:
	var c := chapter_index(level_index)
	return c >= 0 and chapters[c].first == level_index + 1


## Briefing lines; the first mission of a chapter opens with the chapter's intro.
func briefing(level_index: int, level_id: String) -> Array[Dictionary]:
	var raw: Array = []
	if is_chapter_start(level_index):
		raw.append_array(chapters[chapter_index(level_index)].intro)
	raw.append_array(missions.get(level_id, {}).get("briefing", []))
	return _lines(raw)


func debrief(level_id: String) -> Array[Dictionary]:
	return _lines(missions.get(level_id, {}).get("debrief", []))


## One line for a failed attempt. kind: "fail", "fail_ally" or "fail_cargo". `pick` chooses
## deterministically (for example the attempt count), so the same failure doesn't always repeat.
func fail_line(kind: String, pick: int) -> Dictionary:
	var pool: Array = fail_lines.get(kind, [])
	if pool.is_empty():
		pool = fail_lines.fail
	if pool.is_empty():
		return {}
	return _lines([pool[posmod(pick, pool.size())]])[0]


func _lines(raw: Array) -> Array[Dictionary]:
	var out: Array[Dictionary] = []
	for line: Array in raw:
		var s: Dictionary = speakers.get(str(line[0]), {"name": str(line[0]), "color": Color.WHITE, "pitch": 1.0})
		out.append({"speaker": str(line[0]), "name": s.name, "color": s.color, "pitch": s.pitch, "text": str(line[1])})
	return out
