class_name MissionCatalog
extends RefCounted
## The campaign: which mission occupies each of the chapter level slots, and which are unlocked.
## Missions are found by convention, not by an index file: chapter N's slot k (1-based) is
## `res://data/missions/<chapter theme>_<kk>.json`, e.g. helix_01 .. helix_20, vita_01 .. meridian_20.
## A slot whose file does not exist is an unauthored slot. The catalog never parses mission files;
## MissionDefinition validates their contents.
## Unlocks are linear over authored missions: the first is always open, each later one opens when
## the previous authored mission has been completed.

const MISSIONS_DIR := "res://data/missions"


class Slot:
	var id := ""
	var path := ""
	var chapter: ChapterCatalog.Chapter
	## 1-based position inside the chapter.
	var index := 0
	## 1-based position in the whole campaign (chapter.first_level + index - 1).
	var level_number := 0
	var authored := false
	var _name := ""

	## The mission's display name from its file ("" when not authored); read once.
	func display_name() -> String:
		if _name.is_empty() and authored and FileAccess.file_exists(path):
			var data: Variant = JSON.parse_string(FileAccess.get_file_as_string(path))
			_name = str((data as Dictionary).get("name", "")) if data is Dictionary else ""
		return _name


var chapters: ChapterCatalog
var slots: Array[Slot] = []
var errors := PackedStringArray()
var _by_id := {}


static func load_default() -> MissionCatalog:
	return from_chapters(ChapterCatalog.load_from_file())


## `exists` maps a res:// path to whether the file is present (injected by tests).
static func from_chapters(p_chapters: ChapterCatalog, exists: Callable = Callable()) -> MissionCatalog:
	var catalog := MissionCatalog.new()
	catalog.chapters = p_chapters
	if p_chapters == null or not p_chapters.is_valid():
		catalog.errors.append("chapter catalog invalid")
		return catalog
	var check := exists if exists.is_valid() else func(path: String) -> bool: return FileAccess.file_exists(path)
	for chapter in p_chapters.chapters:
		for index in range(1, chapter.last_level - chapter.first_level + 2):
			var slot := Slot.new()
			slot.id = mission_id(chapter.theme, index)
			slot.path = MISSIONS_DIR.path_join(slot.id + ".json")
			slot.chapter = chapter
			slot.index = index
			slot.level_number = chapter.first_level + index - 1
			slot.authored = bool(check.call(slot.path))
			if catalog._by_id.has(slot.id):
				catalog.errors.append("duplicate mission id '%s' (two chapters share theme '%s')" % [slot.id, chapter.theme])
			catalog._by_id[slot.id] = slot
			catalog.slots.append(slot)
	return catalog


static func mission_id(chapter_theme: String, index: int) -> String:
	return "%s_%02d" % [chapter_theme, index]


func is_valid() -> bool:
	return errors.is_empty()


func slot(id: String) -> Slot:
	return _by_id.get(id)


func authored() -> Array[Slot]:
	var result: Array[Slot] = []
	for s in slots:
		if s.authored:
			result.append(s)
	return result


func chapter_slots(chapter_number: int) -> Array[Slot]:
	var result: Array[Slot] = []
	for s in slots:
		if s.chapter.number == chapter_number:
			result.append(s)
	return result


func first_authored_id() -> String:
	var list := authored()
	return list[0].id if not list.is_empty() else ""


## The next authored mission after `id` in campaign order, or "" at the end.
func next_authored_id(id: String) -> String:
	var current := slot(id)
	if current == null:
		return ""
	for s in slots:
		if s.authored and s.level_number > current.level_number:
			return s.id
	return ""


func previous_authored_id(id: String) -> String:
	var current := slot(id)
	if current == null:
		return ""
	var previous := ""
	for s in slots:
		if s.level_number >= current.level_number:
			break
		if s.authored:
			previous = s.id
	return previous


## `progress` may be null (tools/tests): then only the first authored mission is unlocked.
func is_unlocked(id: String, progress: ProgressData) -> bool:
	var s := slot(id)
	if s == null or not s.authored:
		return false
	var previous := previous_authored_id(id)
	if previous.is_empty():
		return true
	return progress != null and progress.is_mission_completed(previous)
