extends SceneTree
## Plays narrated cinematics through the real CinematicPlayer and MusicDirector, in real time, and
## records what actually comes out so voice, music and subtitles can be checked against the
## narration manifest. Needs a window and a real audio driver (headless mutes audio):
##   godot_console --resolution 1280x720 -s tools/audio/narration_sync_check.gd -- <out dir> <id> [<id> ...]
## Master is turned down to -80 dB so nothing is audible; the Voice and Music buses are recorded
## before it (AudioEffectRecord). Per sequence it writes <id>_voice.wav, <id>_music.wav,
## <id>_events.json (slide / line / subtitle times on the player clock, and the bed's playback
## position when each line started) and a screenshot per slide (<id>_slide_NN.png).
## Analyse with tools/audio/narration_sync_report.py.

const PLAYER_PREROLL_FRAMES := 10

var _out := ""


func _initialize() -> void:
	_run.call_deferred()


func _run() -> void:
	var args := OS.get_cmdline_user_args()
	if args.size() < 2:
		printerr("usage: -- <out dir> <sequence id> [...]")
		quit(2)
		return
	_out = args[0]
	DirAccess.make_dir_recursive_absolute(_out)
	var cinematics := CinematicCatalog.load_from_file()
	var narration := NarrationCatalog.load_from_file()
	if not narration.is_valid():
		printerr("narration invalid: ", ", ".join(narration.errors))
		quit(1)
		return
	narration.apply_to(cinematics)
	AudioServer.set_bus_volume_db(0, -80.0)
	var records := {}
	for bus_name in ["Voice", "Music"]:
		var effect := AudioEffectRecord.new()
		AudioServer.add_bus_effect(AudioServer.get_bus_index(bus_name), effect)
		records[bus_name] = effect
	var music := MusicDirector.new()
	music.bus = "Music"
	root.add_child(music)
	for i in range(1, args.size()):
		await _check(args[i], cinematics, narration, music, records)
	quit()


func _check(id: String, cinematics: CinematicCatalog, narration: NarrationCatalog, music: MusicDirector, records: Dictionary) -> void:
	var sequence := cinematics.get_sequence(id)
	if sequence == null:
		printerr("unknown sequence ", id)
		return
	music.stop(0.01)
	await _frames(PLAYER_PREROLL_FRAMES)
	var player := CinematicPlayer.new()
	player.music = music
	player.duck_db = narration.duck_db
	player.duck_attack = narration.duck_attack
	player.duck_hold = narration.duck_hold
	player.duck_release = narration.duck_release
	root.add_child(player)
	var done := [false]
	player.finished.connect(func(_id: String, _skipped: bool) -> void: done[0] = true)
	for effect: AudioEffectRecord in records.values():
		effect.set_recording_active(true)
	var start := Time.get_ticks_usec()
	player.play(sequence)
	var events := []
	var last_stage := -1
	var last_voice := ""
	var last_subtitle := false
	while not done[0]:
		# Read every timing first: the screenshot below takes long enough to skew a later reading.
		var t := (Time.get_ticks_usec() - start) / 1000000.0
		var bed_position := music.active_player().get_playback_position() + minf(AudioServer.get_time_since_last_mix(), 0.1)
		var new_stage := player.slide_index != last_stage
		if new_stage:
			last_stage = player.slide_index
			last_subtitle = false
			events.append({"t": t, "event": "stage", "index": last_stage})
		if player.subtitle_visible() and not last_subtitle:
			last_subtitle = true
			events.append({"t": t, "event": "subtitle", "index": player.slide_index, "text": player.subtitle_label.text})
		if player.current_voice != last_voice:
			last_voice = player.current_voice
			if not last_voice.is_empty():
				events.append({"t": t, "event": "voice", "index": player.slide_index, "path": last_voice, "bed_position": bed_position})
		if new_stage:
			await RenderingServer.frame_post_draw
			root.get_texture().get_image().save_png(_out.path_join("%s_slide_%02d.png" % [id, last_stage + 1]))
		await process_frame
	var total := (Time.get_ticks_usec() - start) / 1000000.0
	await _frames(30)
	for bus_name: String in records:
		var effect: AudioEffectRecord = records[bus_name]
		effect.set_recording_active(false)
		var wav := effect.get_recording()
		if wav != null:
			wav.save_to_wav(_out.path_join("%s_%s.wav" % [id, bus_name.to_lower()]))
	var file := FileAccess.open(_out.path_join("%s_events.json" % id), FileAccess.WRITE)
	file.store_string(JSON.stringify({"id": id, "seconds": total, "mix_rate": AudioServer.get_mix_rate(), "events": events}, "\t"))
	file.close()
	print("%s: %.1f s, %d events" % [id, total, events.size()])
	player.queue_free()
	await _frames(5)


func _frames(count: int) -> void:
	for i in count:
		await process_frame
