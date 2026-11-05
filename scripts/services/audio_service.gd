class_name AudioService
extends Node
## Plays short sound effects synthesized at startup (no audio asset files, so no licensing risk).
## Noise uses a fixed seed so the generated sounds are identical every run.

const MIX_RATE := 22050
const VOICES := 8
const IMPACT_MIN_INTERVAL_MS := 70
const NOISE_SEED := 1337

var enabled := true
var _streams := {}
var _players: Array[AudioStreamPlayer] = []
var _next_voice := 0
var _last_impact_ms := -1000
var _rng := RandomNumberGenerator.new()


func _ready() -> void:
	process_mode = Node.PROCESS_MODE_ALWAYS
	_rng.seed = NOISE_SEED
	_streams = {
		"launch": _synth(0.16, func(t: float, _n: float) -> float: return sin(TAU * (300.0 + 2200.0 * t) * t) * exp(-t * 10.0) * 0.5),
		"impact": _make_impact(),
		"pop": _synth(0.22, func(t: float, n: float) -> float: return (signf(sin(TAU * (900.0 - 2500.0 * t) * t)) * 0.25 + n * 0.3) * exp(-t * 14.0)),
		"shatter": _synth(0.3, func(t: float, n: float) -> float: return (n * 0.5 + sin(TAU * 2600.0 * t) * 0.2 + sin(TAU * 3400.0 * t) * 0.15) * exp(-t * 12.0)),
		"win": _make_arpeggio([523.25, 659.25, 783.99, 1046.5]),
		"lose": _synth(0.45, func(t: float, _n: float) -> float: return sin(TAU * (420.0 - 260.0 * t) * t) * exp(-t * 4.0) * 0.4),
		"boom": _make_boom(),
		"radio": _synth(0.07, func(t: float, n: float) -> float: return (n * 0.25 + sin(TAU * 1900.0 * t) * 0.2) * exp(-t * 40.0)),
		"click": _synth(0.035, func(t: float, _n: float) -> float: return sin(TAU * 1200.0 * t) * exp(-t * 80.0) * 0.4),
	}
	for i in VOICES:
		var player := AudioStreamPlayer.new()
		add_child(player)
		_players.append(player)


func play(sound: String, volume_db: float = 0.0, pitch: float = 1.0) -> void:
	if not enabled:
		return
	if not _streams.has(sound):
		push_error("AudioService: unknown sound '%s'" % sound)
		return
	var player := _players[_next_voice]
	_next_voice = (_next_voice + 1) % _players.size()
	player.stream = _streams[sound]
	player.volume_db = volume_db
	player.pitch_scale = pitch
	player.play()


## Throttled so a collapsing structure does not stack dozens of overlapping sounds.
func play_impact(strength: float) -> void:
	var now := Time.get_ticks_msec()
	if now - _last_impact_ms < IMPACT_MIN_INTERVAL_MS:
		return
	_last_impact_ms = now
	var loudness := clampf(strength / 1500.0, 0.0, 1.0)
	play("impact", lerpf(-18.0, 0.0, loudness), randf_range(0.85, 1.15))


func _synth(duration: float, sample: Callable) -> AudioStreamWAV:
	var count := int(duration * MIX_RATE)
	var data := PackedByteArray()
	data.resize(count * 2)
	for i in count:
		var t := float(i) / MIX_RATE
		var value: float = sample.call(t, _rng.randf_range(-1.0, 1.0))
		data.encode_s16(i * 2, int(clampf(value, -1.0, 1.0) * 32767.0))
	var wav := AudioStreamWAV.new()
	wav.format = AudioStreamWAV.FORMAT_16_BITS
	wav.mix_rate = MIX_RATE
	wav.stereo = false
	wav.data = data
	return wav


func _make_impact() -> AudioStreamWAV:
	# One-pole low-pass over white noise gives a dull "thud"; a low sine adds weight.
	var state := {"y": 0.0}
	return _synth(0.14, func(t: float, n: float) -> float:
		state.y += 0.15 * (n - state.y)
		return (state.y * 1.6 + sin(TAU * 90.0 * t) * 0.6) * exp(-t * 28.0))


## Low rumble: filtered noise with a falling sub tone.
func _make_boom() -> AudioStreamWAV:
	var state := {"y": 0.0}
	return _synth(0.6, func(t: float, n: float) -> float:
		state.y += 0.08 * (n - state.y)
		return (state.y * 2.4 + sin(TAU * (70.0 - 40.0 * t) * t) * 0.7) * exp(-t * 6.0))


func _make_arpeggio(notes: Array) -> AudioStreamWAV:
	var step := 0.09
	return _synth(step * notes.size() + 0.25, func(t: float, _n: float) -> float:
		var index := mini(int(t / step), notes.size() - 1)
		var local := t - index * step
		return sin(TAU * notes[index] * t) * exp(-local * 6.0) * 0.35)
