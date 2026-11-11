extends TestCase
## Data-driven audio (data/audio.json): catalog validation, procedural fallbacks, production file
## variants and buses, material-aware impacts and destruction sounds, MusicDirector cues, synced
## intensity changes, the critical layer, ambience and the per-mission audio plan (MissionAudio).

## Retired 2026-11-11 (licence unverified, owner decision): nothing may reference it.
const BED := "res://assets/audio/music/gameplay_bed.ogg"
const MENU := "res://assets/audio/music/shared/gam_mus_menu_01.ogg"
const TENSION := "res://assets/audio/music/helix/hlx_mus_gameplay_tension.ogg"
## Blocks that reference sound or cue ids; cleared when a test replaces "sounds" or "music".
const DEPENDENT := {"impact_by_material": {}, "destroyed_by_material": {}, "default_destroyed": "", "missions": {}, "chapters": {}}


func _catalog_text(overrides: Dictionary = {}) -> String:
	var data: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(AudioCatalog.DEFAULT_PATH))
	if overrides.has("sounds") or overrides.has("music"):
		data.merge(DEPENDENT, true)
	data.merge(overrides, true)
	return JSON.stringify(data)


func _service(catalog: AudioCatalog) -> AudioService:
	var service := AudioService.new()
	service.catalog = catalog
	tree.root.add_child(service)
	return service


func _director(source: String = "music") -> MusicDirector:
	var director := MusicDirector.new()
	director.catalog = AudioCatalog.load_from_file()
	director.cue_source = source
	tree.root.add_child(director)
	return director


func test_shipped_catalog_is_valid_and_complete() -> void:
	var catalog := AudioCatalog.load_from_file()
	assert_true(catalog.is_valid(), ", ".join(catalog.errors))
	assert_true(catalog.missing_files().is_empty(), "referenced files exist: %s" % ", ".join(catalog.missing_files()))
	for id: String in ["kinetic_fire", "breach_launch", "breach_detonate", "impact_metal", "impact_glass", "impact_electronic",
			"impact_composite", "impact_concrete", "structure_collapse", "machine_failure", "secondary_blast",
			"component_destroyed", "core_destroyed", "core_critical", "weapon_switch", "objective_complete",
			"reload_ready", "mission_success", "mission_fail", "ui_click", "ui_confirm", "ui_back"]:
		assert_true(catalog.has_sound(id), "sound id %s" % id)
		assert_false(catalog.get_sound(id).files.is_empty(), "%s uses production files" % id)
	var materials := MaterialCatalog.load_from_file()
	for material_id: String in materials.order:
		assert_true(catalog.impact_by_material.has(material_id), "impact sound for %s" % material_id)
		assert_true(catalog.destroyed_by_material.has(material_id), "destruction sound for %s" % material_id)
	assert_eq(catalog.impact_sound_for("reinforced_steel"), "impact_metal")
	assert_eq(catalog.impact_sound_for("concrete"), "impact_concrete")
	assert_eq(catalog.impact_sound_for(""), catalog.default_impact, "ground and statics use the default")
	assert_eq(catalog.destroyed_sound_for("composite"), "structure_collapse")
	assert_eq(catalog.destroyed_sound_for("energy_component"), "secondary_blast")
	assert_eq(catalog.get_cue("helix_gameplay").file, TENSION)
	assert_false(catalog.music.has("legacy_bed"), "the unverified legacy bed is retired")
	for cue_id: String in catalog.music:
		assert_true(catalog.get_cue(cue_id).file != BED, "%s must not use gameplay_bed.ogg" % cue_id)
	assert_eq(catalog.get_ambience("helix_server_hall").bus, "Ambience")
	for id: String in catalog.sounds:
		assert_true(AudioServer.get_bus_index(catalog.get_sound(id).bus) >= 0, "%s bus exists" % id)
	var plan := catalog.mission_plan("helix_01")
	assert_eq(plan.intensity, ["helix_prep", "helix_gameplay", "helix_combat"])
	assert_eq(plan.ambience, "helix_server_hall")
	for cue: String in plan.intensity:
		assert_true(str(catalog.get_cue(cue).file).contains("/helix/"), "Helix uses only Helix music (%s)" % cue)


func test_production_files_carry_manifest_rights() -> void:
	var data: Dictionary = JSON.parse_string(FileAccess.get_file_as_string("res://data/integrated_assets.json"))
	var by_path := {}
	for entry: Dictionary in data.entries:
		by_path["res://" + str(entry.path)] = entry
	var catalog := AudioCatalog.load_from_file()
	for id: String in catalog.sounds:
		for path in catalog.get_sound(id).files:
			assert_true(by_path.has(path), "%s: %s is an integrated asset" % [id, path])
			assert_eq(str(by_path[path].approval_status), "pending_review")


func test_catalog_rejects_invalid_entries() -> void:
	var bad := AudioCatalog.from_json_text(_catalog_text({
		"sounds": {
			"a": {"fallback": "trumpet", "files": []},
			"b": {"fallback": "click", "volume_db": 50, "files": []},
			"c": {"fallback": "click", "files": ["C:/sounds/x.ogg"]},
			"d": {"fallback": "click", "pitch_variance": 2.0, "files": [], "bus": "Radio"},
		},
		"impact_by_material": {"reinforced_steel": "nope"},
		"default_impact": "missing",
		"music": {"m": {"file": "music.ogg", "volume_db": 3}},
		"missions": {"x": {"intensity": ["nope"]}},
	}))
	assert_false(bad.is_valid())
	assert_eq(bad.errors.size(), 10, ", ".join(bad.errors))
	assert_false(AudioCatalog.from_json_text("{}").is_valid())
	assert_false(AudioCatalog.from_json_text("{bad").is_valid())
	assert_false(AudioCatalog.load_from_file("res://data/none.json").is_valid())


func test_missing_files_fall_back_to_procedural_sounds() -> void:
	var catalog := AudioCatalog.from_json_text(_catalog_text({"sounds": {
		"kinetic_fire": {"fallback": "launch", "files": ["res://assets/audio/sfx/not_approved_yet.ogg"]},
		"impact_generic": {"fallback": "impact", "files": []},
	}, "default_impact": "impact_generic"}))
	assert_true(catalog.is_valid(), ", ".join(catalog.errors))
	assert_eq(catalog.missing_files(), PackedStringArray(["res://assets/audio/sfx/not_approved_yet.ogg"]))
	var service := _service(catalog)
	assert_eq(service.source_for("kinetic_fire"), "procedural:launch", "missing file: procedural fallback")
	assert_eq(service.source_for("click"), "procedural:click", "legacy procedural names still play")
	assert_eq(service.source_for("nonexistent"), "")
	service.play("kinetic_fire")
	service.play("click")
	service.queue_free()


func test_production_variants_play_on_their_bus() -> void:
	var service := _service(AudioCatalog.load_from_file())
	assert_eq(service.source_for("breach_detonate"), "file")
	assert_eq(service.source_for("ui_click"), "file")
	service.play("ui_click")
	var used := service._players.filter(func(p: AudioStreamPlayer) -> bool: return p.stream != null)
	assert_eq(used.size(), 1)
	assert_eq((used[0] as AudioStreamPlayer).bus, &"UI")
	service.queue_free()


func test_one_event_plays_one_sound() -> void:
	var service := _service(AudioCatalog.load_from_file())
	for i in 3:
		service.play("structure_collapse")
	var used := service._players.filter(func(p: AudioStreamPlayer) -> bool: return p.stream != null)
	assert_eq(used.size(), 1, "the same sound does not stack within one event")
	service.play("kinetic_fire")
	used = service._players.filter(func(p: AudioStreamPlayer) -> bool: return p.stream != null)
	assert_eq(used.size(), 2, "different sounds still play together")
	service.queue_free()


func test_impacts_and_destruction_follow_the_material() -> void:
	var service := _service(AudioCatalog.load_from_file())
	assert_eq(service.impact_sound_for("glass_polymer"), "impact_glass")
	assert_eq(service.impact_sound_for("ai_core_module"), "impact_electronic")
	assert_eq(service.impact_sound_for("unknown_material"), "impact_generic")
	service.play_impact(900.0, "reinforced_steel")
	service.play_destroyed("lightweight_alloy")
	service.queue_free()


func test_music_cues_set_track_volume_and_overlap() -> void:
	var director := _director()
	# Loop overlap and volume come from the cue (a test cue on a shipped track).
	var overlap := MusicDirector.new()
	overlap.catalog = AudioCatalog.load_from_file()
	var cue := AudioCatalog.MusicCue.new()
	cue.id = "overlap_test"
	cue.file = MENU
	cue.volume_db = -12.0
	cue.loop_overlap = 4.5
	cue.bus = "Music"
	overlap.catalog.music["overlap_test"] = cue
	tree.root.add_child(overlap)
	assert_true(overlap.play_cue("overlap_test", 0.01))
	assert_eq(overlap.current_stream.resource_path, MENU)
	assert_near(overlap.loop_overlap, 4.5, 0.001)
	assert_near(overlap.target_volume_db(), -12.0, 0.001)
	overlap.queue_free()
	assert_true(director.play_cue("helix_gameplay", 0.01))
	assert_eq(director.current_stream.resource_path, TENSION)
	assert_near(director.loop_overlap, 0.0, 0.001, "the Helix tracks loop by themselves")
	assert_true((director.current_stream as AudioStreamOggVorbis).loop, "loop flag set in the import")
	assert_false(director.play_cue("nope"), "unknown cue refused")
	assert_eq(director.current_cue, "helix_gameplay", "the current music keeps playing")
	assert_true(director.play_cue("helix_gameplay"), "same cue again is a no-op")
	director.stop(0.01)
	assert_eq(director.current_cue, "")
	director.queue_free()


func test_intensity_change_keeps_position_and_layer_follows() -> void:
	var director := _director()
	director.play_cue("helix_prep", 0.01)
	director.active_player().seek(12.0)
	assert_true(director.play_cue("helix_gameplay", 0.01, true))
	assert_true(director.active_player().get_playback_position() >= 11.5, "the next intensity starts where the last one was")
	assert_true(director.set_layer("helix_critical_layer", 0.01))
	assert_eq(director.current_layer, "helix_critical_layer")
	assert_true(director.layer_player().playing)
	assert_true(absf(director.layer_player().get_playback_position() - director.active_player().get_playback_position()) < 0.5, "layer in time with the track")
	director.set_layer("", 0.01)
	assert_eq(director.current_layer, "")
	director.queue_free()


func test_ambience_director_reads_ambience_cues() -> void:
	var bed := _director("ambience")
	bed.bus = "Ambience"
	assert_true(bed.play_cue("helix_server_hall", 0.01))
	assert_eq(bed.active_player().bus, &"Ambience")
	assert_false(bed.play_cue("helix_gameplay"), "music cues are not ambience")
	bed.queue_free()


func test_mission_audio_raises_intensity_with_the_action() -> void:
	var music := _director()
	var bed := _director("ambience")
	var screen := MissionScreen.new(_service(AudioCatalog.load_from_file()))
	screen.music = music
	screen.ambience = bed
	tree.root.add_child(screen)
	await wait_physics_frames(2)
	assert_eq(music.current_cue, "helix_prep", "preparation before the first shot")
	assert_eq(bed.current_cue, "helix_server_hall")
	screen.world.fire(Vector2(600, -60))
	assert_eq(music.current_cue, "helix_gameplay", "first shot raises the tension")
	screen.engine.apply_damage("rack_1", 9999.0, DamageRules.TYPE_IMPACT, 0.9)
	assert_eq(music.current_cue, "helix_combat", "first destruction: combat")
	screen.engine.apply_damage("aura_core", 170.0, DamageRules.TYPE_IMPACT, 0.9)
	assert_eq(music.current_layer, "helix_critical_layer", "critical core adds the layer")
	screen.engine.apply_damage("aura_core", 9999.0, DamageRules.TYPE_IMPACT, 0.9)
	for i in 600:
		if not screen.engine.is_active() or screen.engine.awaiting_decision:
			break
		await tree.physics_frame
	assert_true(screen.engine.awaiting_decision, "optional goals pending: the decision prompt is shown")
	screen.finish_mission()
	assert_eq(music.current_cue, "victory_mission")
	assert_eq(music.current_layer, "")
	screen.queue_free()
	music.queue_free()
	bed.queue_free()
	await wait_physics_frames(1)
