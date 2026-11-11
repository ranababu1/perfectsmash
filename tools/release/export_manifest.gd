extends SceneTree
## Release tool: works out which files under res://assets the shipped game actually uses, so the
## export can leave everything else out (sources, previews, concepts, unused variants, retired
## files) and the rights audit can list exactly what ships.
##   godot_console --headless -s tools/release/export_manifest.gd
## Roots: every integrated asset (data/integrated_assets.json), every audio file (data/audio.json),
## every cinematic still (data/cinematics.json), every res://assets path written in scripts/ and
## scenes/, and project.godot. Dependencies are followed with ResourceLoader.get_dependencies.
## Writes docs/release/shipped-assets.json ({used: [...], excluded: [...], bytes}) and prints the
## exclude filter for export_presets.cfg.

const OUT := "res://docs/release/shipped-assets.json"
## Never shipped, whatever references them: retired or unverified-licence files (plan revision 7).
const NEVER := ["res://assets/audio/music/gameplay_bed.ogg", "res://assets/music/bg.mp3"]
const RESOURCE_EXTENSIONS := ["png", "webp", "jpg", "glb", "gltf", "ogg", "wav", "mp3", "ttf", "otf", "tres", "res", "tscn", "svg", "exr", "hdr", "gdshader", "material"]

var _used := {}


func _initialize() -> void:
	_run.call_deferred()


func _run() -> void:
	var roots: Array[String] = []
	_from_json("res://data/integrated_assets.json", roots)
	_from_json("res://data/audio.json", roots)
	_from_json("res://data/cinematics.json", roots)
	for folder: String in ["res://scripts", "res://scenes"]:
		_from_sources(folder, roots)
	_from_text(FileAccess.get_file_as_string("res://project.godot"), roots)
	for path in roots:
		_add(path)
	var all_files: Array[String] = []
	_walk("res://assets", all_files)
	var excluded: Array[String] = []
	var used_bytes := 0
	var excluded_bytes := 0
	for path in all_files:
		var size := FileAccess.get_file_as_bytes(path).size() if FileAccess.file_exists(path) else 0
		if _used.has(path) and not NEVER.has(path):
			used_bytes += size
		else:
			excluded.append(path)
			excluded_bytes += size
	var used: Array = _used.keys().filter(func(p: String) -> bool: return p.begins_with("res://assets/") and not NEVER.has(p))
	used.sort()
	excluded.sort()
	DirAccess.make_dir_recursive_absolute(ProjectSettings.globalize_path("res://docs/release"))
	var file := FileAccess.open(OUT, FileAccess.WRITE)
	file.store_string(JSON.stringify({"used": used, "excluded": excluded, "used_bytes": used_bytes, "excluded_bytes": excluded_bytes}, "\t") + "\n")
	file.close()
	print("used %d files (%.1f MB), excluded %d files (%.1f MB) -> %s" % [used.size(), used_bytes / 1048576.0, excluded.size(), excluded_bytes / 1048576.0, OUT])
	quit()


func _add(path: String) -> void:
	if path.is_empty() or _used.has(path):
		return
	if not FileAccess.file_exists(path) and not ResourceLoader.exists(path):
		return
	_used[path] = true
	if ResourceLoader.exists(path):
		for dependency: String in ResourceLoader.get_dependencies(path):
			# Entries look like "uid://...::Type::res://path" or a plain path.
			var dep := dependency.get_slice("::", 2) if dependency.contains("::") else dependency
			_add(dep)


func _from_json(path: String, roots: Array[String]) -> void:
	_from_text(FileAccess.get_file_as_string(path), roots)


func _from_sources(folder: String, roots: Array[String]) -> void:
	var files: Array[String] = []
	_walk(folder, files)
	for path in files:
		if path.ends_with(".gd") or path.ends_with(".tscn") or path.ends_with(".tres"):
			_from_text(FileAccess.get_file_as_string(path), roots)


## Every res://assets/... or assets/... path in a text (JSON paths are often project-relative).
func _from_text(text: String, roots: Array[String]) -> void:
	var regex := RegEx.create_from_string("(res://)?assets/[A-Za-z0-9_./-]+\\.([a-z0-9]+)")
	for match in regex.search_all(text):
		if RESOURCE_EXTENSIONS.has(match.get_string(2)):
			var path := match.get_string()
			roots.append(path if path.begins_with("res://") else "res://" + path)


func _walk(folder: String, out: Array[String]) -> void:
	var dir := DirAccess.open(folder)
	if dir == null:
		return
	for sub: String in dir.get_directories():
		if not sub.begins_with("."):
			_walk(folder.path_join(sub), out)
	for file: String in dir.get_files():
		if not file.ends_with(".import") and not file.ends_with(".uid") and RESOURCE_EXTENSIONS.has(file.get_extension()):
			out.append(folder.path_join(file))
