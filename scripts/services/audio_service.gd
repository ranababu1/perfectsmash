class_name AudioService
extends Node
## Plays the game's sound effects. Sound ids, their file variants and their procedural fallbacks
## come from data/audio.json (AudioCatalog): a sound plays a random approved file variant when
## one exists, otherwise a sound synthesized at startup (no asset files, so no licensing risk).
## The procedural names ("click", "launch", ...) remain playable directly for the legacy screens.
## Noise uses a fixed seed so the generated sounds are identical every run.

const MIX_RATE := 22050
const VOICES := 8
const IMPACT_MIN_INTERVAL_MS := 70
## One event, one sound: the same sound id does not retrigger within this window (a blast that
## destroys three racks plays one destruction sound, not three on top of each other).
const SAME_SOUND_MIN_INTERVAL_MS := 90
const NOISE_SEED := 1337

var enabled := true
## Sound ids, variants and fallbacks. Loaded in _ready unless assigned before.
var catalog: AudioCatalog
var _streams := {}
## sound id -> Array[AudioStream] of the file variants that exist.
var _variants := {}
var _players: Array[AudioStreamPlayer] = []
var _next_voice := 0
var _last_impact_ms := -1000
## sound id -> last play time (ms)
var _last_played := {}
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
		"click": _synth(0.035, func(t: float, _n: float) -> float: return sin(TAU * 1200.0 * t) * exp(-t * 80.0) * 0.4),
	}
	for i in VOICES:
		var player := AudioStreamPlayer.new()
		add_child(player)
		_players.append(player)
	if catalog == null:
		catalog = AudioCatalog.load_from_file()
	if not catalog.is_valid():
		push_error("AudioService: audio catalog invalid: %s" % ", ".join(catalog.errors))
	_load_variants()


## Plays a catalog sound id (file variant or its procedural fallback) or, for the legacy
## screens, a procedural sound by name. `volume_db` is added to the sound's own volume.
func play(sound: String, volume_db: float = 0.0, pitch: float = 1.0) -> void:
	if not enabled:
		return
	var spec := catalog.get_sound(sound) if catalog != null else null
	if spec != null:
		var now := Time.get_ticks_msec()
		if now - int(_last_played.get(sound, -100000)) < SAME_SOUND_MIN_INTERVAL_MS:
			return
		_last_played[sound] = now
		var variants: Array = _variants.get(sound, [])
		var stream: AudioStream = variants.pick_random() if not variants.is_empty() else _streams.get(spec.fallback)
		var spread := randf_range(-spec.pitch_variance, spec.pitch_variance)
		_play_stream(stream, spec.volume_db + volume_db, pitch * (1.0 + spread), spec.bus)
		return
	if not _streams.has(sound):
		push_error("AudioService: unknown sound '%s'" % sound)
		return
	_play_stream(_streams[sound], volume_db, pitch, "SFX")


## What `sound` currently plays: "file" when an approved variant is loaded, "procedural:<name>"
## for a fallback or a legacy name, "" when unknown.
func source_for(sound: String) -> String:
	var spec := catalog.get_sound(sound) if catalog != null else null
	if spec != null:
		return "file" if not (_variants.get(sound, []) as Array).is_empty() else "procedural:" + spec.fallback
	return "procedural:" + sound if _streams.has(sound) else ""


## Throttled so a collapsing structure does not stack dozens of overlapping sounds. The sound
## follows the material that was hit (data/audio.json impact_by_material).
func play_impact(strength: float, material_id: String = "") -> void:
	var now := Time.get_ticks_msec()
	if now - _last_impact_ms < IMPACT_MIN_INTERVAL_MS:
		return
	_last_impact_ms = now
	var loudness := clampf(strength / 1500.0, 0.0, 1.0)
	play(impact_sound_for(material_id), lerpf(-18.0, 0.0, loudness), randf_range(0.92, 1.08))


## The destruction sound of a component made of `material_id` (data/audio.json).
func play_destroyed(material_id: String) -> void:
	var sound := catalog.destroyed_sound_for(material_id) if catalog != null and catalog.is_valid() else "pop"
	if not sound.is_empty():
		play(sound)


func impact_sound_for(material_id: String) -> String:
	return catalog.impact_sound_for(material_id) if catalog != null and catalog.is_valid() else "impact"


func _play_stream(stream: AudioStream, volume_db: float, pitch: float, bus: String = "SFX") -> void:
	if stream == null:
		return
	var player := _players[_next_voice]
	_next_voice = (_next_voice + 1) % _players.size()
	player.bus = bus if AudioServer.get_bus_index(bus) >= 0 else "Master"
	player.stream = stream
	player.volume_db = volume_db
	player.pitch_scale = maxf(pitch, 0.05)
	player.play()


func _load_variants() -> void:
	_variants.clear()
	if catalog == null:
		return
	for spec: AudioCatalog.SoundSpec in catalog.sounds.values():
		var loaded: Array[AudioStream] = []
		for path in spec.files:
			if ResourceLoader.exists(path):
				var stream := load(path) as AudioStream
				if stream != null:
					loaded.append(stream)
			else:
				push_warning("AudioService: '%s' file missing, using the procedural fallback: %s" % [spec.id, path])
		_variants[spec.id] = loaded


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


func _make_arpeggio(notes: Array) -> AudioStreamWAV:
	var step := 0.09
	return _synth(step * notes.size() + 0.25, func(t: float, _n: float) -> float:
		var index := mini(int(t / step), notes.size() - 1)
		var local := t - index * step
		return sin(TAU * notes[index] * t) * exp(-local * 6.0) * 0.35)
