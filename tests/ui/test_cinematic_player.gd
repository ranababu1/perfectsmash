extends TestCase
## CinematicPlayer: image resolution, slide advance, tap/skip/natural end, subtitles, no voice.

var _ended: Array = []


func _catalog() -> CinematicCatalog:
	return CinematicCatalog.load_from_file()


func _player() -> CinematicPlayer:
	var player := CinematicPlayer.new()
	tree.root.add_child(player)
	_ended = []
	player.finished.connect(func(id: String, skipped: bool) -> void: _ended.append([id, skipped]))
	return player


func test_every_sequence_resolves_to_images() -> void:
	var catalog := _catalog()
	assert_true(catalog.is_valid(), ", ".join(catalog.errors))
	for id in catalog.order:
		if id == "teaser_2041":
			continue
		var sequence := catalog.get_sequence(id)
		for slide in sequence.slides:
			assert_true(not slide.image.is_empty() and ResourceLoader.exists(slide.image), "%s: image %s" % [id, slide.image])
			assert_true(load(slide.image) is Texture2D, "%s: loads %s" % [id, slide.image])
		assert_true(ResourceLoader.exists(sequence.end_image), "%s: end image" % id)
		assert_false(sequence.music_cue.is_empty(), "%s: music cue" % id)


func test_music_cues_exist_in_audio_catalog() -> void:
	var audio: Dictionary = JSON.parse_string(FileAccess.get_file_as_string("res://data/audio.json"))
	var music: Dictionary = audio.get("music", {})
	var catalog := _catalog()
	for id in catalog.order:
		var cue := catalog.get_sequence(id).music_cue
		assert_true(music.has(cue), "%s: cue '%s' in data/audio.json" % [id, cue])


func test_play_shows_first_slide_and_advances() -> void:
	var catalog := _catalog()
	var player := _player()
	assert_true(player.play_id("ch02_intro", catalog))
	var sequence := catalog.get_sequence("ch02_intro")
	assert_eq(player.slide_index, 0)
	assert_eq(player.subtitle_label.text, sequence.slides[0].subtitle)
	assert_eq(player.caption_label.text, sequence.slides[0].caption)
	player.advance()
	assert_eq(player.slide_index, 1)
	assert_eq(player.subtitle_label.text, sequence.slides[1].subtitle)
	player.queue_free()


func test_auto_advance_after_reading_time() -> void:
	var catalog := _catalog()
	var player := _player()
	player.play_id("ch01_intro", catalog)
	var first := catalog.get_sequence("ch01_intro").slides[0].reading_seconds()
	player.tick(first - 0.5)
	assert_eq(player.slide_index, 0)
	player.tick(0.6)
	assert_eq(player.slide_index, 1)
	player.queue_free()


func test_tap_advances() -> void:
	var player := _player()
	player.play_id("ch01_intro", _catalog())
	player.tick(CinematicPlayer.TAP_COOLDOWN + 0.01)
	var click := InputEventMouseButton.new()
	click.button_index = MOUSE_BUTTON_LEFT
	click.pressed = true
	player._gui_input(click)
	assert_eq(player.slide_index, 1)
	player._gui_input(click)
	assert_eq(player.slide_index, 1, "tap right after a slide change is ignored")
	player.queue_free()


func test_skip_button_emits_skipped() -> void:
	var player := _player()
	player.play_id("opening", _catalog())
	assert_true(player.skip_button.custom_minimum_size.x >= 48.0 and player.skip_button.custom_minimum_size.y >= 48.0)
	player.skip_button.pressed.emit()
	assert_eq(_ended, [["opening", true]])
	player.skip()
	assert_eq(_ended.size(), 1, "finishes only once")
	assert_false(player.is_playing())
	player.queue_free()


func test_cancel_skips() -> void:
	var player := _player()
	player.play_id("finale", _catalog())
	var cancel := InputEventAction.new()
	cancel.action = "ui_cancel"
	cancel.pressed = true
	player._unhandled_input(cancel)
	assert_eq(_ended, [["finale", true]])
	player.queue_free()


func test_natural_end_includes_end_card() -> void:
	var catalog := _catalog()
	var sequence := catalog.get_sequence("ch01_outro")
	var player := _player()
	player.play(sequence)
	for i in sequence.slides.size():
		player.advance()
	assert_eq(player.slide_index, sequence.slides.size(), "end card follows the last slide")
	assert_true(_ended.is_empty())
	assert_eq(player.subtitle_label.text, sequence.end_subtitle)
	player.tick(CinematicPlayer.END_CARD_SECONDS + 0.1)
	assert_eq(_ended, [["ch01_outro", false]])
	player.queue_free()


func test_missing_image_and_unknown_motion_do_not_crash() -> void:
	var slide := CinematicCatalog.Slide.new()
	slide.subtitle = "Plate only."
	slide.image = "res://does/not/exist.webp"
	slide.motion = "spin"
	slide.voice = "res://does/not/exist.ogg"
	var sequence := CinematicCatalog.Sequence.new()
	sequence.id = "synthetic"
	sequence.slides.append(slide)
	var player := _player()
	player.play(sequence)
	assert_eq(player.subtitle_label.text, "Plate only.")
	player.tick(slide.reading_seconds() + 0.1)
	assert_eq(_ended, [["synthetic", false]])
	player.queue_free()


func test_plays_music_cue_but_never_voice() -> void:
	var music := MusicDirector.new()
	tree.root.add_child(music)
	var player := _player()
	player.music = music
	player.play_id("opening", _catalog())
	assert_eq(music.current_cue, "cinematic")
	assert_true(player.find_children("*", "AudioStreamPlayer", true, false).is_empty(), "the player owns no audio players")
	player.queue_free()
	music.queue_free()
