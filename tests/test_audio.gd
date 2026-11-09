extends TestCase
## Data-driven audio (data/audio.json): catalog validation, procedural fallbacks, file variants,
## material-aware impacts and MusicDirector cues. Uses the shipped gameplay bed as a stand-in
## file; no new audio assets are needed.

const BED := "res://assets/audio/music/gameplay_bed.ogg"


func _catalog_text(overrides: Dictionary = {}) -> String:
	var data: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(AudioCatalog.DEFAULT_PATH))
	data.merge(overrides, true)
	return JSON.stringify(data)


func _service(catalog: AudioCatalog) -> AudioService:
	var service := AudioService.new()
	service.catalog = catalog
	tree.root.add_child(service)
	return service


func test_shipped_catalog_is_valid_and_complete() -> void:
	var catalog := AudioCatalog.load_from_file()
	assert_true(catalog.is_valid(), ", ".join(catalog.errors))
	assert_true(catalog.missing_files().is_empty(), "referenced files exist: %s" % ", ".join(catalog.missing_files()))
	for id: String in ["kinetic_fire", "breach_launch", "breach_detonate", "impact_metal", "impact_glass", "impact_electronic",
			"component_destroyed", "core_destroyed", "reload_ready", "mission_success", "mission_fail", "ui_click"]:
		assert_true(catalog.has_sound(id), "sound id %s" % id)
	var materials := MaterialCatalog.load_from_file()
	for material_id: String in materials.order:
		assert_true(catalog.impact_by_material.has(material_id), "impact sound for %s" % material_id)
	assert_eq(catalog.impact_sound_for("reinforced_steel"), "impact_metal")
	assert_eq(catalog.impact_sound_for(""), catalog.default_impact, "ground and statics use the default")
	for cue: String in ["helix_gameplay", "menu", "cinematic"]:
		assert_true(catalog.get_cue(cue) != null, "music cue %s" % cue)
	assert_eq(catalog.get_cue("helix_gameplay").file, BED)
	assert_near(catalog.get_cue("helix_gameplay").loop_overlap, 4.5, 0.001)


func test_catalog_rejects_invalid_entries() -> void:
	var bad := AudioCatalog.from_json_text(_catalog_text({
		"sounds": {
			"a": {"fallback": "trumpet", "files": []},
			"b": {"fallback": "click", "volume_db": 50, "files": []},
			"c": {"fallback": "click", "files": ["C:/sounds/x.ogg"]},
			"d": {"fallback": "click", "pitch_variance": 2.0, "files": []},
		},
		"impact_by_material": {"reinforced_steel": "nope"},
		"default_impact": "missing",
		"music": {"m": {"file": "music.ogg", "volume_db": 3}},
	}))
	assert_false(bad.is_valid())
	assert_eq(bad.errors.size(), 8, ", ".join(bad.errors))
	assert_false(AudioCatalog.from_json_text("{}").is_valid())
	assert_false(AudioCatalog.from_json_text("{bad").is_valid())
	assert_false(AudioCatalog.load_from_file("res://data/none.json").is_valid())


func test_missing_files_fall_back_to_procedural_sounds() -> void:
	var catalog := AudioCatalog.from_json_text(_catalog_text({"sounds": {
		"kinetic_fire": {"fallback": "launch", "files": ["res://assets/audio/sfx/not_approved_yet.ogg"]},
		"impact_generic": {"fallback": "impact", "files": []},
	}, "impact_by_material": {}, "default_impact": "impact_generic"}))
	assert_true(catalog.is_valid(), ", ".join(catalog.errors))
	assert_eq(catalog.missing_files(), PackedStringArray(["res://assets/audio/sfx/not_approved_yet.ogg"]))
	var service := _service(catalog)
	assert_eq(service.source_for("kinetic_fire"), "procedural:launch", "missing file: procedural fallback")
	assert_eq(service.source_for("click"), "procedural:click", "legacy procedural names still play")
	assert_eq(service.source_for("nonexistent"), "")
	service.play("kinetic_fire")
	service.play("click")
	service.queue_free()


func test_existing_file_variants_take_priority() -> void:
	var catalog := AudioCatalog.from_json_text(_catalog_text({"sounds": {
		"mission_success": {"fallback": "win", "files": [BED]},
		"impact_generic": {"fallback": "impact", "files": []},
	}, "impact_by_material": {}, "default_impact": "impact_generic"}))
	var service := _service(catalog)
	assert_eq(service.source_for("mission_success"), "file")
	service.enabled = false
	service.play("mission_success")
	service.queue_free()


func test_impacts_follow_the_material() -> void:
	var service := _service(AudioCatalog.load_from_file())
	assert_eq(service.impact_sound_for("glass_polymer"), "impact_glass")
	assert_eq(service.impact_sound_for("ai_core_module"), "impact_electronic")
	assert_eq(service.impact_sound_for("unknown_material"), "impact_generic")
	service.play_impact(900.0, "reinforced_steel")
	service.queue_free()


func test_music_cues_set_track_volume_and_overlap() -> void:
	var director := MusicDirector.new()
	director.catalog = AudioCatalog.load_from_file()
	tree.root.add_child(director)
	assert_true(director.play_cue("helix_gameplay", 0.01))
	assert_eq(director.current_cue, "helix_gameplay")
	assert_eq(director.current_stream.resource_path, BED)
	assert_near(director.loop_overlap, 4.5, 0.001)
	assert_near(director.target_volume_db(), -12.0, 0.001)
	assert_false(director.play_cue("menu"), "a cue without a track yet is refused")
	assert_false(director.play_cue("nope"), "unknown cue refused")
	assert_eq(director.current_cue, "helix_gameplay", "the current music keeps playing")
	assert_true(director.play_cue("helix_gameplay"), "same cue again is a no-op")
	director.stop(0.01)
	assert_eq(director.current_cue, "")
	director.queue_free()
