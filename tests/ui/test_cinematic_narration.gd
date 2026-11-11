extends TestCase
## Story narration with the delivered package (assets/audio/voice/, assets/audio/music/cinematic/,
## data/narration.json generated from the narration manifest): data integrity, the Voice bus,
## per-slide voice and subtitle timing, the cinematic's own music bed and its duck, tap / skip /
## leave behaviour, the narration volume setting and Story Archive replays.

const TEST_SAVE := "user://test_cinematic_narration_progress.json"
const MainScript := preload("res://scripts/main.gd")
const STORY := ["opening", "ch01_intro", "ch01_outro", "ch02_intro", "ch02_outro", "ch03_intro",
		"ch03_outro", "ch04_intro", "ch04_outro", "ch05_intro", "finale"]

var _ended: Array = []


func _narrated() -> CinematicCatalog:
	var cinematics := CinematicCatalog.load_from_file()
	NarrationCatalog.load_from_file().apply_to(cinematics)
	return cinematics


func _music() -> MusicDirector:
	var music := MusicDirector.new()
	tree.root.add_child(music)
	return music


func _player(music: MusicDirector = null, narration := true) -> CinematicPlayer:
	var player := CinematicPlayer.new()
	player.music = music
	player.narration_enabled = narration
	tree.root.add_child(player)
	_ended = []
	player.finished.connect(func(id: String, skipped: bool) -> void: _ended.append([id, skipped]))
	return player


func _length(path: String) -> float:
	return (load(path) as AudioStream).get_length()


func _wait(seconds: float) -> void:
	await tree.create_timer(seconds).timeout


# --- Data ---------------------------------------------------------------------------------------

func test_shipped_narration_covers_every_slide_of_every_story_sequence() -> void:
	var cinematics := CinematicCatalog.load_from_file()
	var narration := NarrationCatalog.load_from_file()
	assert_true(narration.is_valid(), ", ".join(narration.errors))
	assert_eq(narration.status, "integrated")
	assert_eq(narration.unknown_keys(cinematics), PackedStringArray(), "every narrated sequence matches its slides")
	for id in STORY + ["teaser_2041"]:
		assert_true(narration.sequences.has(id), "%s is narrated" % id)
		if narration.sequences.has(id):
			assert_eq((narration.sequences[id] as NarrationCatalog.SequenceNarration).slides.size(), cinematics.get_sequence(id).slides.size(), "%s: one line per slide" % id)
	assert_eq(narration.voiced_slide_count(), 50)


func test_every_voice_line_and_bed_loads_without_looping() -> void:
	var narration := NarrationCatalog.load_from_file()
	for id: String in narration.sequences:
		var entry: NarrationCatalog.SequenceNarration = narration.sequences[id]
		var bed := load(entry.bed) as AudioStreamOggVorbis
		assert_true(bed != null and not bed.loop, "%s bed loads, loop off" % id)
		for i in entry.slides.size():
			var stream := load(entry.slides[i].voice) as AudioStreamOggVorbis
			assert_true(stream != null and not stream.loop, "%s/%d voice loads, loop off" % [id, i + 1])
			if stream != null:
				assert_near(stream.get_length(), entry.slides[i].duration, 0.1, "%s/%d length matches the manifest" % [id, i + 1])


func test_every_voiced_slide_holds_for_its_line_plus_a_tail() -> void:
	var cinematics := _narrated()
	for id in STORY:
		var sequence := cinematics.get_sequence(id)
		assert_false(sequence.music.is_empty(), "%s has its own music bed" % id)
		for i in sequence.slides.size():
			var slide := sequence.slides[i]
			var needed := slide.voice_delay + _length(slide.voice) + CinematicPlayer.MIN_VOICE_TAIL - 0.01
			assert_true(slide.reading_seconds() >= needed, "%s/%d holds %.2f s >= line + tail %.2f s" % [id, i + 1, slide.reading_seconds(), needed])
			assert_near(slide.subtitle_delay, slide.voice_delay, 0.3, "%s/%d subtitle appears with its line" % [id, i + 1])


func test_narration_never_changes_story_text() -> void:
	var plain := CinematicCatalog.load_from_file()
	var narrated := _narrated()
	for id: String in plain.order:
		for i in plain.get_sequence(id).slides.size():
			var a := plain.get_sequence(id).slides[i]
			var b := narrated.get_sequence(id).slides[i]
			assert_eq([b.subtitle, b.caption, b.speaker, b.image], [a.subtitle, a.caption, a.speaker, a.image], "%s/%d unchanged" % [id, i + 1])


func test_voice_bus_exists_and_sends_to_master() -> void:
	var bus := AudioServer.get_bus_index("Voice")
	assert_true(bus >= 0, "Voice bus")
	assert_eq(String(AudioServer.get_bus_send(bus)), "Master")


func test_catalog_rejects_bad_data() -> void:
	var bad := NarrationCatalog.from_json_text(JSON.stringify({"sequences": {"opening": {"slides": [
		{"voice": "assets/x.ogg", "hold": 5.0},
		{"voice": "res://missing/clip.ogg", "hold": 5.0},
		{"voice": "res://assets/audio/voice/opening/gam_vo_opening_01.ogg", "duration": 14.0, "voice_at": 4.0, "hold": 10.0},
	]}}}))
	assert_eq(bad.errors.size(), 3, "non-res:// path, missing file and a hold that cuts the line")
	var stray := NarrationCatalog.from_json_text(JSON.stringify({"sequences": {"nope": {"slides": [
		{"voice": "res://assets/audio/voice/opening/gam_vo_opening_01.ogg", "duration": 1.0, "hold": 2.0}]}}}))
	assert_eq(stray.unknown_keys(CinematicCatalog.load_from_file()), PackedStringArray(["nope"]))


# --- Playback -----------------------------------------------------------------------------------

func test_opening_bed_pre_roll_then_voice_subtitle_and_duck_together() -> void:
	var music := _music()
	var player := _player(music)
	var opening := _narrated().get_sequence("opening")
	player.play(opening)
	assert_eq(music.current_stream.resource_path, opening.music, "the cinematic's own bed plays")
	var bed_db := opening.music_volume_db
	assert_eq(player.current_voice, "", "bed pre-roll: no voice yet")
	assert_false(player.subtitle_visible(), "no subtitle before its line")
	player.tick(opening.slides[0].voice_delay - 0.05)
	assert_eq(player.current_voice, "")
	player.tick(0.06)
	assert_eq(player.current_voice, opening.slides[0].voice, "line 1 starts after the pre-roll")
	assert_true(player.subtitle_visible(), "its subtitle appears with it")
	assert_eq(player.subtitle_label.text, opening.slides[0].subtitle, "verbatim subtitle")
	assert_near(music.target_volume_db(), bed_db - 9.0, 0.01, "bed ducked 9 dB under the voice")
	var line_end := opening.slides[0].voice_delay + _length(opening.slides[0].voice)
	player.tick(line_end - player._elapsed + 0.1)
	assert_true(player.is_music_ducked(), "the duck holds briefly after the line")
	player.tick(0.2)
	assert_false(player.is_music_ducked(), "and releases in the gap")
	assert_near(music.target_volume_db(), bed_db, 0.01)
	assert_eq(player.slide_index, 0, "the slide is still up in the gap")
	player.tick(player.stage_seconds() - player._elapsed + 0.01)
	if player.slide_index == 0:
		player.voice_player().stop()
		player.tick(0.01)
	assert_eq(player.slide_index, 1, "next slide after the line and its gap")
	assert_eq(player.current_voice, opening.slides[1].voice, "its line starts with it")
	player.queue_free()
	music.queue_free()


func test_slide_never_advances_before_its_line_ends() -> void:
	var player := _player()
	var intro := _narrated().get_sequence("ch01_intro")
	player.play(intro)
	var line_end := intro.slides[0].voice_delay + _length(intro.slides[0].voice)
	assert_true(player.stage_seconds() >= line_end + CinematicPlayer.MIN_VOICE_TAIL - 0.01)
	player.tick(line_end)
	assert_eq(player.slide_index, 0, "not before the line has ended")
	player.queue_free()


func test_tap_fades_the_line_and_starts_the_next() -> void:
	var player := _player()
	var intro := _narrated().get_sequence("ch01_intro")
	player.play(intro)
	player.tick(intro.slides[0].voice_delay + 1.0)
	var first := player.voice_player()
	assert_eq(player.current_voice, intro.slides[0].voice)
	player.advance()
	assert_eq(player.slide_index, 1)
	assert_eq(player.current_voice, intro.slides[1].voice, "next line starts at once")
	assert_true(player.voice_player() != first, "on the other voice player")
	await _wait(CinematicPlayer.TAP_VOICE_FADE + 0.15)
	assert_false(first.playing, "the cut line faded out and stopped")
	player.queue_free()


func test_skip_fades_voice_and_bed_out() -> void:
	var music := _music()
	var player := _player(music)
	var finale := _narrated().get_sequence("finale")
	player.play(finale)
	player.tick(finale.slides[0].voice_delay + 0.5)
	var voice := player.voice_player()
	player.skip()
	assert_eq(_ended, [["finale", true]])
	assert_eq(player.current_voice, "")
	assert_false(player.is_music_ducked(), "duck released")
	assert_eq(music.current_stream, null, "the bed is fading out")
	await _wait(CinematicPlayer.SKIP_VOICE_FADE + 0.15)
	assert_false(voice.playing, "the line stopped")
	player.queue_free()
	music.queue_free()


func test_natural_end_leaves_the_bed_for_the_next_screen() -> void:
	var music := _music()
	var player := _player(music)
	var intro := _narrated().get_sequence("ch03_intro")
	player.play(intro)
	for stage in player.stage_count():
		player.tick(player.stage_seconds() + 0.01)
		if player.is_playing() and player.slide_index == stage:
			player.voice_player().stop()
			player.tick(0.01)
	assert_eq(_ended, [["ch03_intro", false]])
	assert_eq(music.current_stream.resource_path, intro.music, "the bed tail rings into the next screen's cross-fade")
	assert_false(player.is_music_ducked())
	player.queue_free()
	music.queue_free()


func test_leaving_the_cinematic_stops_narration() -> void:
	var music := _music()
	var player := _player(music)
	var opening := _narrated().get_sequence("opening")
	player.play(opening)
	player.tick(opening.slides[0].voice_delay + 0.1)
	var voice := player.voice_player()
	tree.root.remove_child(player)
	assert_false(voice.playing, "no orphan narration")
	assert_near(music.target_volume_db(), opening.music_volume_db, 0.01, "music restored on exit")
	player.free()
	music.queue_free()


func test_narration_off_keeps_bed_and_timing_without_voice() -> void:
	var music := _music()
	var player := _player(music, false)
	var opening := _narrated().get_sequence("opening")
	player.play(opening)
	assert_eq(music.current_stream.resource_path, opening.music, "the bed still plays")
	player.tick(opening.slides[0].voice_delay + 0.1)
	assert_eq(player.current_voice, "")
	assert_true(player.subtitle_visible(), "subtitles still appear on the narrated timing")
	assert_false(player.is_music_ducked())
	assert_near(player.stage_seconds(), opening.slides[0].reading_seconds(), 0.001, "manifest timing")
	player.queue_free()
	music.queue_free()


# --- Settings and app ---------------------------------------------------------------------------

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


func test_app_cinematics_and_story_archive_replay_are_narrated() -> void:
	var main: Node = await _boot_main()
	var opening: CinematicCatalog.Sequence = main.cinematics.get_sequence("opening")
	assert_eq(opening.slides[0].voice, "res://assets/audio/voice/opening/gam_vo_opening_01.ogg", "the app applies the narration")
	main.progress.mark_sequence_seen("opening")
	main._show_archive()
	await tree.process_frame
	main._archive.play_requested.emit("opening")
	await tree.process_frame
	var player: CinematicPlayer = main._cinematic
	assert_true(player != null, "the archive replays through the cinematic player")
	assert_eq(main.music.current_stream.resource_path, opening.music, "with the opening's bed")
	player.tick(opening.slides[0].voice_delay + 0.05)
	assert_eq(player.current_voice, opening.slides[0].voice, "and its narration")
	assert_true(player.is_music_ducked())
	player.skip()
	await tree.process_frame
	assert_true(main._archive != null, "back in the archive")
	assert_eq(main.music.current_cue, MainScript.MENU_CUE, "menu music comes back")
	main.progress.narration_volume = 0.0
	main._show_cinematic("opening", main._show_archive)
	(main._cinematic as CinematicPlayer).tick(opening.slides[0].voice_delay + 0.05)
	assert_eq((main._cinematic as CinematicPlayer).current_voice, "", "volume 0: subtitles only")
	await _free_main(main)
