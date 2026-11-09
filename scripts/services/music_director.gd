class_name MusicDirector
extends Node
## Background music bed: cross-fades between two players, ducks under narration and respects the
## player's music setting. Keeps playing while the game is paused. Owns no gameplay state.
## Streams are expected to be loop-ready (Ogg Vorbis with loop enabled in its import settings).

const BED_VOLUME_DB := -12.0
const SILENT_DB := -60.0
const DEFAULT_FADE := 1.5

## The stream the director wants playing (kept while disabled, so re-enabling resumes it).
var current_stream: AudioStream
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


func stop(fade: float = DEFAULT_FADE) -> void:
	play(null, fade)


## Lowers the bed by `amount_db` (e.g. under narration); duck(0) restores it.
func duck(amount_db: float, fade: float = 0.3) -> void:
	_duck_db = -absf(amount_db)
	if _enabled and current_stream != null:
		_tween_volume(_active, target_volume_db(), fade)


func target_volume_db() -> float:
	return BED_VOLUME_DB + _duck_db


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
