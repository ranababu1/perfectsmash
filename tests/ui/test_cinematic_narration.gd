extends TestCase
## Story narration (owner-approved 2026-11-11): NarrationCatalog mapping, CinematicPlayer clip
## playback in step with subtitles, music ducking and restore, skip / leave stop the clip, the
## narration volume setting, and Story Archive replays. No approved narration clips exist yet, so
## these tests use two existing short library sounds as stand-in clips; they are never mapped in
## data/narration.json.

const CLIP_A := "res://assets/audio/sfx/shared/opr_sfx_weapon_switch_01.ogg"
const CLIP_B := "res://assets/audio/sfx/shared/opr_sfx_weapon_switch_02.ogg"
const TEST_SAVE := "user://test_cinematic_narration_progress.json"
const MainScript := preload("res://scripts/main.gd")

var _ended: Array = []


func _slide(text: String, voice: String = "", duration: float = 0.5) -> CinematicCatalog.Slide:
	var slide := CinematicCatalog.Slide.new()
	slide.subtitle = text
	slide.voice = voice
	slide.duration = duration
	return slide


## Narrated, silent, narrated.
func _sequence() -> CinematicCatalog.Sequence:
	var sequence := CinematicCatalog.Sequence.new()
	sequence.id = "synthetic"
	sequence.slides.append(_slide("One.", CLIP_A))
	sequence.slides.append(_slide("Two."))
	sequence.slides.append(_slide("Three.", CLIP_B))
	return sequence


func _music() -> MusicDirector:
	var music := MusicDirector.new()
	tree.root.add_child(music)
	return music


func _player(music: MusicDirector = null) -> CinematicPlayer:
	var player := CinematicPlayer.new()
	player.music = music
	tree.root.add_child(player)
	_ended = []
	player.finished.connect(func(id: String, skipped: bool) -> void: _ended.append([id, skipped]))
	return player


func _length(path: String) -> float:
	return (load(path) as AudioStream).get_length()


func test_clip_starts_with_its_slide_and_subtitle() -> void:
	var music := _music()
	var bed := music.target_volume_db()
	var player := _player(music)
	player.play(_sequence())
	assert_eq(player.current_voice, CLIP_A, "slide 1 plays its clip")
	assert_eq(player.voice_player().stream.resource_path, CLIP_A)
	assert_eq(player.subtitle_label.text, "One.", "the subtitle shows with its clip")
	assert_true(player.is_music_ducked(), "music ducks under narration")
	assert_near(music.target_volume_db(), bed - NarrationCatalog.DEFAULT_DUCK_DB, 0.01)
	player.advance()
	assert_eq(player.subtitle_label.text, "Two.")
	assert_eq(player.current_voice, "", "a slide without a clip plays none")
	assert_false(player.voice_player().playing, "the previous clip stopped with its slide")
	assert_false(player.is_music_ducked(), "music comes back between narrated slides")
	assert_near(music.target_volume_db(), bed, 0.01, "music restored to its previous level")
	player.advance()
	assert_eq(player.current_voice, CLIP_B, "a cinematic can hold several clips")
	assert_eq(player.subtitle_label.text, "Three.")
	player.queue_free()
	music.queue_free()


func test_slide_stays_until_its_clip_has_finished() -> void:
	var player := _player()
	player.play(_sequence())
	var needed := _length(CLIP_A) + CinematicPlayer.VOICE_TAIL
	assert_true(needed > 0.5, "the stand-in clip outlasts the slide's own 0.5 s")
	player.tick(0.55)
	assert_eq(player.slide_index, 0, "the clip is not cut off at the reading time")
	player.tick(needed - 0.55 + 0.01)
	assert_eq(player.slide_index, 1, "the slide moves on once the clip and its tail are done")
	player.queue_free()


func test_skip_stops_narration_and_restores_music() -> void:
	var music := _music()
	var bed := music.target_volume_db()
	var player := _player(music)
	player.play(_sequence())
	assert_eq(player.current_voice, CLIP_A)
	player.skip()
	assert_eq(_ended, [["synthetic", true]])
	assert_false(player.voice_player().playing, "skip stops the clip")
	assert_eq(player.current_voice, "")
	assert_near(music.target_volume_db(), bed, 0.01, "music restored after skip")
	player.queue_free()
	music.queue_free()


func test_leaving_the_cinematic_stops_narration() -> void:
	var music := _music()
	var bed := music.target_volume_db()
	var player := _player(music)
	player.play(_sequence())
	var voice := player.voice_player()
	tree.root.remove_child(player)
	assert_false(voice.playing, "removed from the screen: no orphan narration")
	assert_near(music.target_volume_db(), bed, 0.01, "music restored on exit")
	player.free()
	music.queue_free()


func test_narration_off_plays_subtitles_only() -> void:
	var music := _music()
	var player := CinematicPlayer.new()
	player.music = music
	player.narration_enabled = false
	tree.root.add_child(player)
	player.play(_sequence())
	assert_eq(player.subtitle_label.text, "One.")
	assert_eq(player.current_voice, "")
	assert_false(player.is_music_ducked())
	player.tick(0.51)
	assert_eq(player.slide_index, 1, "reading pace when narration is off")
	player.queue_free()
	music.queue_free()


func test_catalog_maps_validates_and_applies() -> void:
	var cinematics := CinematicCatalog.load_from_file()
	var text := JSON.stringify({"clips": {"opening/1": CLIP_A, "opening/3": CLIP_B}, "duck_db": 6})
	var catalog := NarrationCatalog.from_json_text(text)
	assert_true(catalog.is_valid(), ", ".join(catalog.errors))
	assert_eq(catalog.duck_db, 6.0)
	assert_eq(catalog.clip_for("opening", 0), CLIP_A)
	assert_eq(catalog.clip_for("opening", 1), "")
	assert_eq(catalog.apply_to(cinematics), 2)
	assert_eq(cinematics.get_sequence("opening").slides[2].voice, CLIP_B)
	assert_eq(cinematics.get_sequence("opening").slides[1].voice, "")
	var bad := NarrationCatalog.from_json_text(JSON.stringify({"clips": {"opening/1": "assets/x.ogg", "opening/2": "res://missing/clip.ogg"}}))
	assert_eq(bad.errors.size(), 2, "non-res:// and missing files are rejected")
	var stray := NarrationCatalog.from_json_text(JSON.stringify({"clips": {"opening/99": CLIP_A, "nope/1": CLIP_A}}))
	assert_eq(stray.unknown_keys(cinematics).size(), 2, "keys must name real slides")


func test_shipped_mapping_is_valid_and_covers_every_story_sequence() -> void:
	var cinematics := CinematicCatalog.load_from_file()
	var shipped := NarrationCatalog.load_from_file()
	assert_true(shipped.is_valid(), ", ".join(shipped.errors))
	assert_eq(shipped.unknown_keys(cinematics), PackedStringArray(), "every mapped clip names a real slide")
	var expected := NarrationCatalog.expected_keys(cinematics)
	assert_eq(expected.size(), cinematics.slide_count(), "one key per slide")
	var sequences := {}
	for k in expected:
		sequences[k.get_slice("/", 0)] = true
	for story in ["opening", "ch01_intro", "ch02_intro", "ch03_intro", "ch04_intro", "ch05_intro",
			"ch01_outro", "ch02_outro", "ch03_outro", "ch04_outro", "finale"]:
		assert_true(sequences.has(story), "%s can be narrated" % story)
	if shipped.status == "pending_assets":
		assert_true(shipped.clips.is_empty(), "no clips are claimed while delivery is pending")


func test_narration_volume_persists_and_validates() -> void:
	var p := ProgressData.new()
	assert_eq(p.narration_volume, 1.0, "full volume by default")
	p.narration_volume = 0.4
	var copy := ProgressData.from_dict(p.to_dict())
	assert_near(copy.narration_volume, 0.4, 0.0001)
	assert_true(copy.load_warnings.is_empty())
	var data := p.to_dict()
	(data.settings as Dictionary).erase("narration_volume")
	assert_eq(ProgressData.from_dict(data).narration_volume, 1.0, "rc1 saves load the default")
	data.settings["narration_volume"] = 3.0
	var invalid := ProgressData.from_dict(data)
	assert_eq(invalid.narration_volume, 1.0)
	assert_false(invalid.load_warnings.is_empty(), "an invalid value is reported")
	assert_true(invalid.sound_enabled and invalid.music_enabled, "other settings are unaffected")


func _boot_main() -> Node:
	if FileAccess.file_exists(TEST_SAVE):
		DirAccess.remove_absolute(ProjectSettings.globalize_path(TEST_SAVE))
	var main: Node = MainScript.new()
	main.cinematics_enabled = false
	main.save = SaveService.new(TEST_SAVE)
	tree.root.add_child(main)
	await tree.process_frame
	return main


func _free_main(main: Node) -> void:
	main.queue_free()
	await tree.process_frame
	if FileAccess.file_exists(TEST_SAVE):
		DirAccess.remove_absolute(ProjectSettings.globalize_path(TEST_SAVE))
	var bus := AudioServer.get_bus_index("Voice")
	AudioServer.set_bus_volume_db(bus, 0.0)
	AudioServer.set_bus_mute(bus, false)


func test_settings_slider_sets_voice_bus_and_saves() -> void:
	var main: Node = await _boot_main()
	var bus := AudioServer.get_bus_index("Voice")
	assert_true(bus >= 0, "the Voice bus exists")
	main._show_settings()
	await tree.process_frame
	var settings: SettingsScreen = main._settings
	assert_eq(settings.narration_slider.value, 100.0)
	assert_true(settings.narration_slider.custom_minimum_size.y >= 48.0, "comfortable touch target")
	assert_true(settings.sound_button.button_pressed and settings.music_button.button_pressed, "music and sound settings unchanged")
	settings.narration_slider.value = 30.0
	assert_near(main.progress.narration_volume, 0.3, 0.0001)
	assert_eq(settings.narration_value.text, "30%")
	assert_near(AudioServer.get_bus_volume_db(bus), linear_to_db(0.3), 0.01)
	assert_false(AudioServer.is_bus_mute(bus))
	assert_near(SaveService.new(TEST_SAVE).load_progress().narration_volume, 0.3, 0.0001, "saved")
	settings.narration_slider.value = 0.0
	assert_eq(settings.narration_value.text, "Off")
	assert_true(AudioServer.is_bus_mute(bus), "volume 0 mutes narration")
	settings.narration_slider.value = 70.0
	settings.sound_button.button_pressed = false
	assert_true(AudioServer.is_bus_mute(bus), "Sound off mutes narration too")
	settings.sound_button.button_pressed = true
	assert_false(AudioServer.is_bus_mute(bus))
	await _free_main(main)


func test_story_archive_replay_plays_narration() -> void:
	var main: Node = await _boot_main()
	main.narration.clips["opening/1"] = CLIP_A
	main.narration.apply_to(main.cinematics)
	main.progress.mark_sequence_seen("opening")
	main._show_archive()
	await tree.process_frame
	main._archive.play_requested.emit("opening")
	await tree.process_frame
	var player: CinematicPlayer = main._cinematic
	assert_true(player != null, "the archive replays through the cinematic player")
	assert_eq(player.current_voice, CLIP_A, "replay plays the narration")
	assert_true(player.is_music_ducked())
	var voice := player.voice_player()
	player.skip()
	await tree.process_frame
	assert_false(voice.playing if is_instance_valid(voice) else false, "skip stops it")
	assert_true(main._archive != null, "back in the archive")
	assert_near(main.music.target_volume_db(), main.music._bed_volume_db, 0.01, "menu music restored")
	main.progress.sound_enabled = false
	main._show_cinematic("opening", main._show_archive)
	assert_eq((main._cinematic as CinematicPlayer).current_voice, "", "Sound off: subtitles only")
	await _free_main(main)
