class_name SaveService
extends RefCounted
## Persists ProgressData as JSON on device storage. Writes go to a temp file first, then replace
## the real file, so an interrupted write cannot leave a half-written save behind.

const DEFAULT_PATH := "user://progress.json"

var path: String


func _init(save_path: String = DEFAULT_PATH) -> void:
	path = save_path


func load_progress() -> ProgressData:
	if not FileAccess.file_exists(path):
		return ProgressData.new()
	var file := FileAccess.open(path, FileAccess.READ)
	if file == null:
		push_warning("SaveService: cannot read %s (error %d); using defaults" % [path, FileAccess.get_open_error()])
		return ProgressData.new()
	var text := file.get_as_text()
	file.close()
	var json := JSON.new()
	if json.parse(text) != OK:
		_preserve_corrupt_file()
		var fresh := ProgressData.new()
		fresh.load_warnings.append("save file was not valid JSON; started fresh")
		push_warning("SaveService: corrupt save moved aside; using defaults")
		return fresh
	var progress := ProgressData.from_dict(json.data)
	for warning in progress.load_warnings:
		push_warning("SaveService: " + warning)
	return progress


func save_progress(progress: ProgressData) -> Error:
	var temp_path := path + ".tmp"
	var file := FileAccess.open(temp_path, FileAccess.WRITE)
	if file == null:
		var open_error := FileAccess.get_open_error()
		push_error("SaveService: cannot write %s (error %d)" % [temp_path, open_error])
		return open_error
	file.store_string(JSON.stringify(progress.to_dict(), "\t"))
	file.close()
	var dir := DirAccess.open(path.get_base_dir())
	if dir == null:
		var dir_error := DirAccess.get_open_error()
		push_error("SaveService: cannot open save directory (error %d)" % dir_error)
		return dir_error
	var err := dir.rename(temp_path, path)
	if err != OK:
		push_error("SaveService: failed to replace save file (error %d)" % err)
	return err


func _preserve_corrupt_file() -> void:
	var dir := DirAccess.open(path.get_base_dir())
	if dir == null:
		push_warning("SaveService: cannot open save directory to preserve corrupt file")
		return
	var err := dir.rename(path, path + ".corrupt")
	if err != OK:
		push_warning("SaveService: could not preserve corrupt file (error %d)" % err)
