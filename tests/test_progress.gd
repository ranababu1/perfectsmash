extends TestCase

const TEST_SAVE := "user://test_progress.json"


func _cleanup() -> void:
	for suffix in ["", ".tmp", ".corrupt"]:
		if FileAccess.file_exists(TEST_SAVE + suffix):
			DirAccess.remove_absolute(ProjectSettings.globalize_path(TEST_SAVE + suffix))


func test_record_win_keeps_best() -> void:
	var p := ProgressData.new()
	assert_true(p.record_win("L01", 2, 2))
	assert_false(p.record_win("L01", 1, 3), "worse result does not improve")
	assert_eq(p.stars_for("L01"), 2)
	assert_true(p.record_win("L01", 3, 1))
	assert_eq(p.stars_for("L01"), 3)
	assert_eq(int(p.level_results["L01"].best_shots), 1)


func test_record_win_clamps_stars() -> void:
	var p := ProgressData.new()
	p.record_win("L01", 9, 1)
	assert_eq(p.stars_for("L01"), 3)


func test_unlocking() -> void:
	var ids: Array[String] = ["A", "B", "C"]
	var p := ProgressData.new()
	assert_true(p.is_unlocked(ids, 0))
	assert_false(p.is_unlocked(ids, 1))
	p.record_win("A", 1, 3)
	assert_true(p.is_unlocked(ids, 1))
	assert_false(p.is_unlocked(ids, 2))
	assert_false(p.is_unlocked(ids, 3), "out of range")
	assert_false(p.is_unlocked(ids, -1), "negative index")


func test_total_stars() -> void:
	var p := ProgressData.new()
	p.record_win("A", 3, 1)
	p.record_win("B", 2, 2)
	assert_eq(p.total_stars(), 5)


func test_round_trip() -> void:
	var p := ProgressData.new()
	p.record_win("L01", 3, 1)
	p.sound_enabled = false
	var copy := ProgressData.from_dict(JSON.parse_string(JSON.stringify(p.to_dict())))
	assert_true(copy.load_warnings.is_empty(), "no warnings: %s" % ", ".join(copy.load_warnings))
	assert_eq(copy.stars_for("L01"), 3)
	assert_false(copy.sound_enabled)
	assert_true(copy.vibration_enabled)


func test_rejects_unknown_version() -> void:
	var p := ProgressData.from_dict({"version": 99, "levels": {"L01": {"stars": 3, "best_shots": 1}}})
	assert_false(p.is_completed("L01"))
	assert_false(p.load_warnings.is_empty())
	p = ProgressData.from_dict({"levels": {}})
	assert_false(p.load_warnings.is_empty(), "missing version warns")


func test_drops_invalid_entries_keeps_valid() -> void:
	var p := ProgressData.from_dict({
		"version": 1,
		"levels": {
			"good": {"stars": 2, "best_shots": 2},
			"bad_stars": {"stars": 7, "best_shots": 1},
			"bad_type": {"stars": "three", "best_shots": 1},
			"not_object": 5,
		},
		"settings": {"sound": "yes", "vibration": false},
	})
	assert_eq(p.stars_for("good"), 2)
	assert_false(p.is_completed("bad_stars"))
	assert_false(p.is_completed("bad_type"))
	assert_false(p.is_completed("not_object"))
	assert_eq(p.load_warnings.size(), 3)
	assert_true(p.sound_enabled, "invalid setting type falls back to default")
	assert_false(p.vibration_enabled)


func test_non_dictionary_root() -> void:
	var p := ProgressData.from_dict("garbage")
	assert_false(p.load_warnings.is_empty())
	assert_eq(p.total_stars(), 0)


func test_save_service_round_trip() -> void:
	_cleanup()
	var service := SaveService.new(TEST_SAVE)
	assert_eq(service.load_progress().total_stars(), 0, "missing file gives defaults")
	var p := ProgressData.new()
	p.record_win("L02", 3, 1)
	assert_eq(service.save_progress(p), OK)
	p.record_win("L03", 2, 2)
	assert_eq(service.save_progress(p), OK, "overwrite existing save")
	var loaded := service.load_progress()
	assert_eq(loaded.stars_for("L02"), 3)
	assert_eq(loaded.stars_for("L03"), 2)
	assert_false(FileAccess.file_exists(TEST_SAVE + ".tmp"), "temp file cleaned up")
	_cleanup()


func test_save_service_corrupt_file() -> void:
	_cleanup()
	var file := FileAccess.open(TEST_SAVE, FileAccess.WRITE)
	file.store_string("{\"version\": 1, \"levels\": {broken")
	file.close()
	var loaded := SaveService.new(TEST_SAVE).load_progress()
	assert_eq(loaded.total_stars(), 0)
	assert_false(loaded.load_warnings.is_empty())
	assert_true(FileAccess.file_exists(TEST_SAVE + ".corrupt"), "corrupt file preserved for diagnosis")
	_cleanup()


## Upgrade path: a save written by 0.1.0 (schema v1, exact on-disk shape) loads without loss or warnings.
func test_migrates_v1_save() -> void:
	_cleanup()
	var file := FileAccess.open(TEST_SAVE, FileAccess.WRITE)
	file.store_string('{"version": 1, "levels": {"L01": {"stars": 3, "best_shots": 1}, "L02": {"stars": 1, "best_shots": 4}},'
		+ ' "settings": {"sound": false, "vibration": true}}')
	file.close()
	var service := SaveService.new(TEST_SAVE)
	var loaded := service.load_progress()
	assert_true(loaded.load_warnings.is_empty(), "v1 loads cleanly: %s" % ", ".join(loaded.load_warnings))
	assert_eq(loaded.stars_for("L01"), 3)
	assert_eq(loaded.stars_for("L02"), 1)
	assert_false(loaded.sound_enabled)
	assert_true(loaded.aim_guide_enabled, "new setting defaults on")
	assert_true(loaded.narration_enabled, "v3 setting defaults on")
	assert_true(loaded.level_stats.is_empty())
	# Saving rewrites it as the current schema.
	assert_eq(service.save_progress(loaded), OK)
	var raw: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(TEST_SAVE))
	assert_eq(int(raw.version), ProgressData.SCHEMA_VERSION)
	assert_eq(service.load_progress().stars_for("L02"), 1)
	_cleanup()


func test_stats_and_aim_guide_round_trip() -> void:
	var p := ProgressData.new()
	p.count_stat("L01", "attempts")
	p.count_stat("L01", "attempts")
	p.count_stat("L01", "losses")
	p.count_stat("L01", "timeouts")
	p.aim_guide_enabled = false
	var copy := ProgressData.from_dict(JSON.parse_string(JSON.stringify(p.to_dict())))
	assert_true(copy.load_warnings.is_empty(), "no warnings: %s" % ", ".join(copy.load_warnings))
	assert_eq(copy.stat("L01", "attempts"), 2)
	assert_eq(copy.stat("L01", "losses"), 1)
	assert_eq(copy.stat("L01", "timeouts"), 1)
	assert_eq(copy.stat("L01", "wins"), 0)
	assert_eq(copy.stat("L09", "attempts"), 0, "unknown level counts as zero")
	assert_false(copy.aim_guide_enabled)


func test_drops_invalid_stats() -> void:
	var p := ProgressData.from_dict({"version": 2, "levels": {}, "stats": {
		"ok": {"attempts": 3, "wins": 1},
		"negative": {"attempts": -1},
		"text": {"attempts": "lots"},
	}})
	assert_eq(p.stat("ok", "attempts"), 3)
	assert_eq(p.stat("ok", "losses"), 0, "missing counter defaults to 0")
	assert_false(p.level_stats.has("negative"))
	assert_false(p.level_stats.has("text"))
	assert_eq(p.load_warnings.size(), 2)


func test_playtest_report_lists_only_played_levels() -> void:
	var p := ProgressData.new()
	p.count_stat("B", "attempts")
	p.record_win("B", 2, 3)
	var ids: Array[String] = ["A", "B", "C"]
	var report := p.playtest_report(ids, "9.9.9")
	assert_true(report.begins_with("Perfect Smash 9.9.9"), "header")
	assert_true(report.contains("B "), "played level listed")
	assert_false(report.contains("A "), "unplayed level omitted")
	assert_eq(report.split("\n").size(), 4, "header, settings, columns, one row")


func test_v2_save_migrates_and_narration_round_trips() -> void:
	var v2 := ProgressData.from_dict({"version": 2, "levels": {"L01": {"stars": 2, "best_shots": 2}},
		"stats": {"L01": {"attempts": 4}}, "settings": {"sound": true, "vibration": true, "aim_guide": false}})
	assert_true(v2.load_warnings.is_empty(), "v2 loads cleanly: %s" % ", ".join(v2.load_warnings))
	assert_eq(v2.stars_for("L01"), 2)
	assert_eq(v2.stat("L01", "attempts"), 4)
	assert_false(v2.aim_guide_enabled)
	assert_true(v2.narration_enabled)
	v2.narration_enabled = false
	var copy := ProgressData.from_dict(JSON.parse_string(JSON.stringify(v2.to_dict())))
	assert_false(copy.narration_enabled, "narration off persisted")
	assert_eq(int(v2.to_dict().version), 3)
