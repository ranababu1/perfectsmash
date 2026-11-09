extends TestCase
## MusicDirector behaviour with short generated silent loops (no audio assets needed).


func _stream() -> AudioStreamWAV:
	var wav := AudioStreamWAV.new()
	wav.format = AudioStreamWAV.FORMAT_16_BITS
	wav.mix_rate = 8000
	wav.data = PackedByteArray()
	wav.data.resize(8000 * 2)
	wav.loop_mode = AudioStreamWAV.LOOP_FORWARD
	wav.loop_end = 8000
	return wav


func _make() -> MusicDirector:
	var director := MusicDirector.new()
	tree.root.add_child(director)
	return director


func _wait(seconds: float) -> void:
	await tree.create_timer(seconds).timeout


func test_play_fades_in_to_bed_volume() -> void:
	var director := _make()
	var a := _stream()
	director.play(a, 0.05)
	assert_true(director.active_player().stream == a)
	assert_true(director.active_player().playing)
	await _wait(0.15)
	assert_near(director.active_player().volume_db, MusicDirector.BED_VOLUME_DB, 0.01)
	director.free()


func test_crossfade_switches_player_and_stops_old() -> void:
	var director := _make()
	var a := _stream()
	var b := _stream()
	director.play(a, 0.05)
	var first := director.active_player()
	director.play(a, 0.05)
	assert_true(director.active_player() == first, "same stream again is a no-op")
	director.play(b, 0.05)
	assert_true(director.active_player() != first, "cross-fade uses the other player")
	assert_true(director.active_player().stream == b)
	await _wait(0.15)
	assert_false(first.playing, "old player stopped after its fade")
	director.free()


func test_disabled_remembers_stream_and_resumes() -> void:
	var director := _make()
	var a := _stream()
	director.enabled = false
	director.play(a, 0.05)
	assert_true(director.current_stream == a)
	assert_false(director.active_player().playing, "nothing plays while disabled")
	director.enabled = true
	assert_true(director.active_player().playing, "re-enabling resumes the requested stream")
	director.enabled = false
	await _wait(1.0)
	assert_false(director.active_player().playing, "disabling fades out and stops")
	director.free()


func test_duck_and_stop() -> void:
	var director := _make()
	director.play(_stream(), 0.01)
	director.duck(10.0, 0.01)
	await _wait(0.1)
	assert_near(director.active_player().volume_db, MusicDirector.BED_VOLUME_DB - 10.0, 0.01)
	director.duck(0.0, 0.01)
	await _wait(0.1)
	assert_near(director.active_player().volume_db, MusicDirector.BED_VOLUME_DB, 0.01)
	director.stop(0.01)
	assert_true(director.current_stream == null)
	await _wait(0.1)
	assert_false(director.active_player().playing)
	director.free()


func test_loop_handoff_window() -> void:
	var director := _make()
	assert_false(director.needs_loop_handoff(195.0, 198.0), "disabled by default")
	director.loop_overlap = 4.5
	assert_false(director.needs_loop_handoff(190.0, 198.0))
	assert_true(director.needs_loop_handoff(193.5, 198.0))
	assert_false(director.needs_loop_handoff(1.0, 6.0), "tracks shorter than two overlaps never hand off")
	director.free()


func test_loop_handoff_restarts_on_other_player() -> void:
	var director := _make()
	var a := _stream()
	director.play(a, 0.01)
	await _wait(0.05)
	var first := director.active_player()
	director.loop_handoff()
	var second := director.active_player()
	assert_true(second != first, "next cycle uses the other player")
	assert_true(second.stream == a and second.playing)
	assert_true(first.playing, "outgoing tail keeps playing")
	assert_near(second.volume_db, MusicDirector.BED_VOLUME_DB, 0.01)
	director.free()
