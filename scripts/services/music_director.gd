class_name MusicDirector
extends Node
## Background music bed: cross-fades between two players, ducks under narration and respects the
## player's music setting. Keeps playing while the game is paused. Owns no gameplay state.
## Streams may be loop-ready (loop enabled on import) or a track with its own fade-in and fade-out:
## for the latter, set `loop_overlap` and the director restarts the track on the other player that
## many seconds before the end, so the track's own fades overlap into a seamless cycle.
## Named cues (data/audio.json "music", or "ambience" when `cue_source` is "ambience") set the
## track, volume, bus and loop overlap in one call. Same-length tracks of one score (the Helix
## intensity steps) cross-fade at the same playback position so the music changes intensity
## without restarting. A separate layer player adds an overlay track (the critical layer) in sync
## with the current track.

const BED_VOLUME_DB := -12.0
const SILENT_DB := -60.0
const DEFAULT_FADE := 1.5

## The stream the director wants playing (kept while disabled, so re-enabling resumes it).
var current_stream: AudioStream
## Seconds before the end of a non-looping track at which the next cycle starts (0 = no handoff).
var loop_overlap := 0.0
## Music cues; assign before calling play_cue (loaded on first use otherwise).
var catalog: AudioCatalog
## The cue last started with play_cue ("" for streams played directly).
var current_cue := ""
## "music" or "ambience": which catalog block play_cue reads.
var cue_source := "music"
## The layer cue playing over the current track ("" when none).
var current_layer := ""
var _bed_volume_db := BED_VOLUME_DB
var _layer: AudioStreamPlayer
var _layer_volume_db := BED_VOLUME_DB
var _layer_tween: Tween
var _enabled := true
var _duck_db := 0.0
var _players: Array[AudioStreamPlayer] = []
var _active := 0
var _tweens: Array[Tween] = [null, null]


func _init() -> void:
	process_mode = Node.PROCESS_MODE_ALWAYS
	for i in 2:
		var player := AudioStreamPlayer.new()
		player.volume_db = SILENT_DB
		add_child(player)
		_players.append(player)
	_layer = AudioStreamPlayer.new()
	_layer.volume_db = SILENT_DB
	add_child(_layer)


## Audio bus for every player of this director ("Music", "Ambience").
var bus: String = "Master":
	set(value):
		bus = value
		for player in _players + [_layer]:
			player.bus = value if AudioServer.get_bus_index(value) >= 0 else "Master"


var enabled: bool:
	get:
		return _enabled
	set(value):
		if value == _enabled:
			return
		_enabled = value
		if _enabled and current_stream != null:
			_start_on(_active, current_stream, DEFAULT_FADE * 0.5)
		elif not _enabled:
			_fade_out(_active, DEFAULT_FADE * 0.5)
			set_layer("", DEFAULT_FADE * 0.5)


## Cross-fades to `stream`. Calling again with the stream already requested does nothing;
## null fades the music out.
func play(stream: AudioStream, fade: float = DEFAULT_FADE) -> void:
	if stream == current_stream:
		return
	current_stream = stream
	if stream == null:
		_fade_out(_active, fade)
		return
	if not _enabled:
		return
	var previous := _active
	_active = 1 - _active
	_fade_out(previous, fade)
	_start_on(_active, stream, fade)


## Plays a track that is not a catalog cue (a cinematic's music bed) once, at `volume_db`, from
## the start. The next play_cue() cross-fades away from it as usual.
func play_track(stream: AudioStream, volume_db: float, fade: float = 0.3) -> void:
	if stream == null:
		return
	current_cue = ""
	set_layer("", fade)
	loop_overlap = 0.0
	_bed_volume_db = volume_db
	if stream == current_stream:
		# Same bed again (Story Archive replay): restart it so its hits line up with the slides.
		current_stream = null
	play(stream, fade)


func stop(fade: float = DEFAULT_FADE) -> void:
	current_cue = ""
	set_layer("", fade)
	play(null, fade)


## Starts a named cue from the audio catalog. Returns false (and keeps the current music) when
## the cue is unknown or has no track yet. With `keep_position`, the new track starts where the
## current one is (same-length tracks of one score change intensity in place).
func play_cue(cue_id: String, fade: float = DEFAULT_FADE, keep_position: bool = false) -> bool:
	var cue := _cue(cue_id)
	if cue == null:
		push_warning("MusicDirector: unknown music cue '%s'" % cue_id)
		return false
	if cue.file.is_empty() or not ResourceLoader.exists(cue.file):
		push_warning("MusicDirector: music cue '%s' has no track yet (%s)" % [cue_id, cue.file])
		return false
	if cue_id == current_cue:
		return true
	var position := active_player().get_playback_position() if keep_position and active_player().playing else 0.0
	current_cue = cue_id
	loop_overlap = cue.loop_overlap
	_bed_volume_db = cue.volume_db
	play(load(cue.file) as AudioStream, fade)
	if position > 0.0 and _enabled:
		var stream := current_stream
		if stream != null and position < stream.get_length():
			active_player().seek(position)
	return true


## Fades a layer cue in over the current track, starting at the current track's position so
## the two stay in time; "" fades the layer out.
func set_layer(cue_id: String, fade: float = DEFAULT_FADE) -> bool:
	if _layer_tween != null and _layer_tween.is_valid():
		_layer_tween.kill()
	if cue_id.is_empty():
		current_layer = ""
		if _layer.playing:
			_layer_tween = create_tween()
			_layer_tween.tween_property(_layer, "volume_db", SILENT_DB, maxf(fade, 0.01))
			_layer_tween.tween_callback(_layer.stop)
		return true
	var cue := _cue(cue_id)
	if cue == null or cue.file.is_empty() or not ResourceLoader.exists(cue.file):
		return false
	if cue_id == current_layer:
		return true
	current_layer = cue_id
	_layer_volume_db = cue.volume_db
	if not _enabled:
		return true
	_layer.stream = load(cue.file) as AudioStream
	_layer.volume_db = SILENT_DB
	var position := active_player().get_playback_position() if active_player().playing else 0.0
	_layer.play(position if position < _layer.stream.get_length() else 0.0)
	_layer_tween = create_tween()
	_layer_tween.tween_property(_layer, "volume_db", _layer_volume_db + _duck_db, maxf(fade, 0.01))
	return true


func layer_player() -> AudioStreamPlayer:
	return _layer


func _cue(cue_id: String) -> AudioCatalog.MusicCue:
	if catalog == null:
		catalog = AudioCatalog.load_from_file()
	return catalog.get_ambience(cue_id) if cue_source == "ambience" else catalog.get_cue(cue_id)


## Lowers the bed by `amount_db` (e.g. under narration); duck(0) restores it.
func duck(amount_db: float, fade: float = 0.3) -> void:
	_duck_db = -absf(amount_db)
	if _enabled and current_stream != null:
		_tween_volume(_active, target_volume_db(), fade)


func _process(_delta: float) -> void:
	var player := active_player()
	if not _enabled or current_stream == null or not player.playing or player.stream != current_stream:
		return
	if needs_loop_handoff(player.get_playback_position(), current_stream.get_length()):
		loop_handoff()


## True once playback has reached the overlap window of a finite, non-looping track.
func needs_loop_handoff(position: float, length: float) -> bool:
	return loop_overlap > 0.0 and length > loop_overlap * 2.0 and position >= length - loop_overlap


## Starts the next cycle on the other player at full bed volume; the outgoing player keeps
## playing its own fade-out and stops by itself at the end of the stream.
func loop_handoff() -> void:
	var outgoing := active_player()
	_active = 1 - _active
	var incoming := active_player()
	if _tweens[_active] != null and _tweens[_active].is_valid():
		_tweens[_active].kill()
	incoming.stream = current_stream
	incoming.volume_db = target_volume_db()
	incoming.play()
	# Keep the outgoing tail at the bed level; it is the track's own fade-out.
	if _tweens[1 - _active] != null and _tweens[1 - _active].is_valid():
		_tweens[1 - _active].kill()
	outgoing.volume_db = target_volume_db()


func target_volume_db() -> float:
	return _bed_volume_db + _duck_db


func active_player() -> AudioStreamPlayer:
	return _players[_active]


func _start_on(index: int, stream: AudioStream, fade: float) -> void:
	var player := _players[index]
	if player.stream != stream or not player.playing:
		player.stream = stream
		player.volume_db = SILENT_DB
		player.play()
	_tween_volume(index, target_volume_db(), fade)


func _fade_out(index: int, fade: float) -> void:
	var player := _players[index]
	if not player.playing:
		player.volume_db = SILENT_DB
		return
	var tween := _tween_volume(index, SILENT_DB, fade)
	tween.tween_callback(player.stop)


func _tween_volume(index: int, volume_db: float, fade: float) -> Tween:
	if _tweens[index] != null and _tweens[index].is_valid():
		_tweens[index].kill()
	var tween := create_tween()
	tween.tween_property(_players[index], "volume_db", volume_db, maxf(fade, 0.01))
	_tweens[index] = tween
	return tween
