extends RefCounted
## Recorded player solutions, one file per mission: tools/levels/solutions/<mission id>.json holds
## an array of {name, steps} (step format: tools/levels/mission_solver.gd). One file per mission
## lets several level authors work at once without touching the same file.

const DIR := "res://tools/levels/solutions"


## mission id -> Array of solutions, for every file in the folder.
static func load_all() -> Dictionary:
	var book := {}
	var dir := DirAccess.open(DIR)
	if dir == null:
		return book
	for file: String in dir.get_files():
		if file.ends_with(".json"):
			var parsed: Variant = JSON.parse_string(FileAccess.get_file_as_string(DIR.path_join(file)))
			if parsed is Array:
				book[file.get_basename()] = parsed
			else:
				push_error("SolutionBook: %s is not an array of solutions" % file)
	return book


static func for_mission(mission_id: String) -> Array:
	var path := DIR.path_join(mission_id + ".json")
	if not FileAccess.file_exists(path):
		return []
	var parsed: Variant = JSON.parse_string(FileAccess.get_file_as_string(path))
	return parsed if parsed is Array else []
