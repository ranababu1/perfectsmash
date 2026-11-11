class_name CinematicPlayer
extends Control
## Plays one CinematicCatalog.Sequence: full-screen stills with slow camera motion, cross-fades,
## subtitles in a lower band, an optional caption line and a closing end card. It only emits
## `finished`; the app decides what happens next and owns saving.
## Narration (owner-approved 2026-11-11; data from NarrationCatalog / the narration manifest):
## a narrated sequence plays its own music bed from the first slide; each slide's voice line starts
## `voice_delay` after the slide appears (the bed pre-roll on slide 1) on the Voice bus, its
## subtitle appears at `subtitle_delay` (the manifest's sync point), and the slide holds for its
## manifest time (never less than the line plus MIN_VOICE_TAIL; never cut while the line plays).
## The bed ducks while a line speaks (attack/hold/release from the package's duck envelope).
## Tapping on fades the line out quickly and shows the next slide; Skip / back fades the voice and
## the bed out; leaving the tree stops everything. Slides without a clip play at reading pace.
## Input: tap/click/accept shows the next slide, the Skip button (top-right) and ui_cancel
## (Android back) end the sequence. Slides advance on their own after their reading time.

## `skipped` is true when the player ended the sequence early.
signal finished(sequence_id: String, skipped: bool)

const FADE_SECONDS := 0.8
const SUBTITLE_FADE_SECONDS := 0.5
## Extra scale applied to still images so motion never reveals the edges.
const ZOOM_AMOUNT := 0.12
const PAN_FRACTION := 0.04
const END_CARD_SECONDS := 4.0
## Ignore taps this soon after a slide change so a double tap cannot skip a slide unread.
const TAP_COOLDOWN := 0.35
const SKIP_SIZE := Vector2(132, 56)
const SUBTITLE_SIZE := 30
const CAPTION_SIZE := 18
const SAFE_MARGIN_MAX := 96.0
const CONTROL_TINT := Color("bfe9ff")
## Minimum silence kept after a voice line before its slide moves on (the manifest's own gaps are
## longer where the music needs them).
const MIN_VOICE_TAIL := 1.0
## A line still sounding this long after its slide time (late audio start on a slow device) no
## longer holds the slide.
const VOICE_OVERRUN_LIMIT := 3.0
## Fade of a line cut by a tap, and of the voice when the sequence is skipped.
const TAP_VOICE_FADE := 0.08
const SKIP_VOICE_FADE := 0.05
## Fade of the music bed when the sequence is skipped.
const SKIP_MUSIC_FADE := 0.8
const RESTORE_FADE := 0.8
const SILENT_DB := -60.0

## Optional MusicDirector; when set, the sequence's music cue plays on start. Nothing is stopped
## or restored afterwards: the app root restores its own music.
var music: MusicDirector
## Narration on/off (the app turns it off with Sound, or when narration is disabled). Volume is the
## Voice bus volume, set by the app from the narration volume setting.
var narration_enabled := true
var narration_bus := NarrationCatalog.DEFAULT_BUS
## Live duck under each voice line: depth (dB), attack, hold after the line, release (seconds).
var duck_db := NarrationCatalog.DEFAULT_DUCK_DB
var duck_attack := NarrationCatalog.DEFAULT_DUCK_ATTACK
var duck_hold := NarrationCatalog.DEFAULT_DUCK_HOLD
var duck_release := NarrationCatalog.DEFAULT_DUCK_RELEASE
## Slide timing follows the music bed's playback position while it plays (see _bed_clock). Tests
## that drive tick() with simulated time turn it off.
var sync_to_bed := true:
	set(value):
		sync_to_bed = value
		if not value:
			_follow_bed = false
## Path of the clip playing for the current slide ("" when none).
var current_voice := ""
var sequence: CinematicCatalog.Sequence
## Index of the stage on screen: 0..slides-1, then one more for the end card when there is one.
var slide_index := -1
var subtitle_label: Label
var caption_label: Label
var skip_button: Button

var _playing := false
var _finished := false
var _elapsed := 0.0
var _stage_seconds := 0.0
var _front: TextureRect
var _back: TextureRect
var _stage: Control
var _tween: Tween
var _subtitle_tween: Tween
var _title_label: Label
var _margins: MarginContainer
var _pending: CinematicCatalog.Sequence
## Two voice players: a line cut by a tap fades out on one while the next starts on the other.
var _voices: Array[AudioStreamPlayer] = []
var _voice_index := 0
var _voice_fades: Array[Tween] = [null, null]
## Preloaded voice streams of the sequence (path -> AudioStream).
var _streams := {}
var _ducked := false
## Stage-relative times of the current stage (seconds; -1 = none).
var _voice_due := -1.0
var _voice_end := -1.0
var _voice_started := false
var _subtitle_due := 0.0
var _subtitle_shown := false
var _suspended := false
## The music bed this player started, and whether slide timing still follows it: while the bed
## plays and nobody has tapped ahead, the slide clock is the bed's playback position, so lines
## land on the music exactly (the beds' hits are written around the manifest timeline) and frame
## hitches cannot accumulate. A tap hands timing back to the frame clock.
var _bed: AudioStream
var _follow_bed := false
## Sequence time at which the current stage started (bed time while following the bed).
var _stage_start := 0.0
## Stills requested in the background (path -> true), so a slide change never stalls on a load.
var _requested := {}


func _ready() -> void:
	set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	mouse_filter = Control.MOUSE_FILTER_STOP
	theme = UiKit.make_theme()
	clip_contents = true
	_build()
	if _pending != null:
		var queued := _pending
		_pending = null
		play(queued)


## Starts `new_sequence` from its first slide.
func play(new_sequence: CinematicCatalog.Sequence) -> void:
	if new_sequence == null or new_sequence.slides.is_empty():
		push_warning("CinematicPlayer: nothing to play")
		return
	if not is_node_ready():
		_pending = new_sequence
		return
	sequence = new_sequence
	_finished = false
	_playing = true
	slide_index = -1
	_stage_start = 0.0
	_follow_bed = false
	_bed = null
	_preload_voices()
	_start_music()
	_show_stage(0)


## Plays the sequence `sequence_id` of `catalog`; returns false when it does not exist.
func play_id(sequence_id: String, catalog: CinematicCatalog) -> bool:
	if catalog == null or not catalog.has_sequence(sequence_id):
		push_warning("CinematicPlayer: unknown sequence '%s'" % sequence_id)
		return false
	play(catalog.get_sequence(sequence_id))
	return true


func is_playing() -> bool:
	return _playing


## True while a narration clip is playing.
func is_narrating() -> bool:
	return not current_voice.is_empty() and voice_player() != null and voice_player().playing


## The player of the current (or last) line.
func voice_player() -> AudioStreamPlayer:
	return _voices[_voice_index] if not _voices.is_empty() else null


## Seconds the current stage holds before moving on by itself.
func stage_seconds() -> float:
	return _stage_seconds


## True once the current slide's subtitle has appeared (narrated slides wait for their line).
func subtitle_visible() -> bool:
	return _subtitle_shown


## True while the music is lowered for narration.
func is_music_ducked() -> bool:
	return _ducked


## Number of stages: the slides plus the end card when the sequence has one.
func stage_count() -> int:
	if sequence == null:
		return 0
	return sequence.slides.size() + (1 if _has_end_card() else 0)


## The slide on screen, or null while the end card shows.
func current_slide() -> CinematicCatalog.Slide:
	if sequence == null or slide_index < 0 or slide_index >= sequence.slides.size():
		return null
	return sequence.slides[slide_index]


## Shows the next slide (or the end card) now, as a tap does; finishes after the last one.
## From here on the slides follow the frame clock (the bed simply runs ahead).
func advance() -> void:
	_follow_bed = false
	_next_stage()


func _next_stage() -> void:
	if not _playing:
		return
	if slide_index + 1 >= stage_count():
		_finish(false)
	else:
		_show_stage(slide_index + 1)


## Ends the whole sequence immediately, reported as skipped.
func skip() -> void:
	if _playing:
		_finish(true)


## Advances the reading clock by `delta` seconds (called from _process; tests call it directly).
func tick(delta: float) -> void:
	if not _playing or _suspended:
		return
	var clock := _bed_clock()
	if clock >= 0.0:
		_elapsed = clock - _stage_start
	else:
		_elapsed += delta
	_update_timed()
	if _elapsed < _stage_seconds:
		return
	# Never cut a line that is still speaking (late start on a slow device), within a limit.
	if is_narrating() and _elapsed < _stage_seconds + VOICE_OVERRUN_LIMIT:
		return
	_auto_advance()


## The stage time is up: the next stage starts where this one was planned to end, and the part of
## a frame that overshot carries over (on the frame clock nothing is lost between slides).
func _auto_advance() -> void:
	var carry := _elapsed - _stage_seconds
	var next_start := _stage_start + _stage_seconds
	_next_stage()
	if not _playing:
		return
	_stage_start = next_start
	_elapsed = maxf(carry, 0.0)
	_update_timed()


## Bed playback position (seconds) while slides follow the bed, else -1. A bed that is not
## actually advancing (no audio output, e.g. headless) leaves timing on the frame clock.
func _bed_clock() -> float:
	if not _follow_bed or music == null or not is_instance_valid(music) or _bed == null:
		return -1.0
	var bed_player := music.active_player()
	if bed_player.stream != _bed or not bed_player.playing:
		return -1.0
	# Time since the last mix refines the position between mixes; it grows without bound when the
	# driver does not mix (headless, a stalled device), so it only counts while it is small.
	var since_mix := AudioServer.get_time_since_last_mix()
	var position := bed_player.get_playback_position() + (since_mix if since_mix < 0.1 else 0.0)
	return position if position > 0.05 else -1.0


func _process(delta: float) -> void:
	tick(delta)


func _gui_input(event: InputEvent) -> void:
	var click := event as InputEventMouseButton
	var tapped: bool = click != null and click.pressed and click.button_index == MOUSE_BUTTON_LEFT
	if tapped and _playing and _elapsed >= TAP_COOLDOWN:
		accept_event()
		advance()


func _unhandled_input(event: InputEvent) -> void:
	if not _playing:
		return
	if event.is_action_pressed("ui_cancel"):
		get_viewport().set_input_as_handled()
		skip()
	elif event.is_action_pressed("ui_accept") and _elapsed >= TAP_COOLDOWN:
		get_viewport().set_input_as_handled()
		advance()


func _notification(what: int) -> void:
	if what == NOTIFICATION_RESIZED and _margins != null:
		_apply_safe_area()
	elif what == NOTIFICATION_EXIT_TREE:
		# Leaving by any route (the app changes screen, the node is freed): no orphan narration and
		# no music left ducked.
		_stop_all_voices()
		_restore_music(RESTORE_FADE)
	elif what == NOTIFICATION_APPLICATION_PAUSED:
		_suspend(true)
	elif what == NOTIFICATION_APPLICATION_RESUMED:
		_suspend(false)


# --- Building -----------------------------------------------------------------------------------

func _build() -> void:
	for i in 2:
		var voice := AudioStreamPlayer.new()
		voice.name = "Narration%d" % i
		voice.bus = narration_bus if AudioServer.get_bus_index(narration_bus) >= 0 else "Master"
		add_child(voice)
		_voices.append(voice)
	var black := ColorRect.new()
	black.color = Color.BLACK
	black.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	black.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(black)
	_stage = Control.new()
	_stage.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	_stage.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_stage.clip_contents = true
	add_child(_stage)
	_back = _make_layer()
	_front = _make_layer()
	var scrim := TextureRect.new()
	scrim.texture = _scrim_texture()
	scrim.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	scrim.stretch_mode = TextureRect.STRETCH_SCALE
	scrim.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
	scrim.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(scrim)

	_margins = MarginContainer.new()
	_margins.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	_margins.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(_margins)
	var column := VBoxContainer.new()
	column.mouse_filter = Control.MOUSE_FILTER_IGNORE
	column.add_theme_constant_override("separation", 8)
	_margins.add_child(column)

	var top := HBoxContainer.new()
	top.mouse_filter = Control.MOUSE_FILTER_IGNORE
	column.add_child(top)
	var top_spacer := Control.new()
	top_spacer.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	top_spacer.mouse_filter = Control.MOUSE_FILTER_IGNORE
	top.add_child(top_spacer)
	skip_button = UiKit.button("Skip", SKIP_SIZE.x)
	skip_button.name = "SkipButton"
	skip_button.custom_minimum_size = SKIP_SIZE
	skip_button.focus_mode = Control.FOCUS_NONE
	for state in ["normal", "hover", "pressed", "focus"]:
		var box := StyleBoxFlat.new()
		box.bg_color = Color(0.03, 0.04, 0.08, 0.72 if state != "pressed" else 0.9)
		box.border_color = Color(1, 1, 1, 0.35)
		box.set_border_width_all(1)
		box.set_corner_radius_all(UiKit.CORNER)
		skip_button.add_theme_stylebox_override(state, box)
	skip_button.add_theme_color_override("font_color", Color.WHITE)
	skip_button.pressed.connect(skip)
	top.add_child(skip_button)

	_title_label = UiKit.label("", 56, Palette.TEXT)
	_title_label.name = "EndCardTitle"
	_title_label.size_flags_vertical = Control.SIZE_EXPAND_FILL
	_title_label.vertical_alignment = VERTICAL_ALIGNMENT_CENTER
	_title_label.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	_style_outline(_title_label, 8)
	column.add_child(_title_label)

	caption_label = UiKit.label("", CAPTION_SIZE, Palette.ACCENT)
	caption_label.name = "Caption"
	_style_outline(caption_label, 4)
	column.add_child(caption_label)
	subtitle_label = UiKit.label("", SUBTITLE_SIZE, Palette.TEXT)
	subtitle_label.name = "Subtitle"
	subtitle_label.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	subtitle_label.custom_minimum_size = Vector2(0, 96)
	subtitle_label.vertical_alignment = VERTICAL_ALIGNMENT_TOP
	_style_outline(subtitle_label, 6)
	column.add_child(subtitle_label)
	_apply_safe_area()


func _make_layer() -> TextureRect:
	var layer := TextureRect.new()
	layer.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	layer.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
	layer.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_COVERED
	layer.mouse_filter = Control.MOUSE_FILTER_IGNORE
	layer.modulate.a = 0.0
	_stage.add_child(layer)
	return layer


func _style_outline(label: Label, outline: int) -> void:
	label.add_theme_constant_override("outline_size", outline)
	label.add_theme_color_override("font_outline_color", Color(0, 0, 0, 0.9))
	label.add_theme_constant_override("line_spacing", 4)


func _scrim_texture() -> GradientTexture2D:
	var gradient := Gradient.new()
	gradient.offsets = PackedFloat32Array([0.0, 0.5, 1.0])
	gradient.colors = PackedColorArray([Color(0, 0, 0, 0.0), Color(0, 0, 0, 0.0), Color(0, 0, 0, 0.82)])
	var texture := GradientTexture2D.new()
	texture.gradient = gradient
	texture.fill_from = Vector2(0, 0)
	texture.fill_to = Vector2(0, 1)
	texture.width = 4
	texture.height = 64
	return texture


## Dark placeholder plate used when a still is missing or fails to load.
func _fallback_texture() -> GradientTexture2D:
	var colors := ChapterTheme.for_key(sequence.theme if sequence != null else ChapterTheme.DEFAULT_KEY)
	var gradient := Gradient.new()
	gradient.offsets = PackedFloat32Array([0.0, 1.0])
	gradient.colors = PackedColorArray([colors.sky_top.darkened(0.4), colors.sky_bottom.darkened(0.4)])
	var texture := GradientTexture2D.new()
	texture.gradient = gradient
	texture.fill_from = Vector2(0, 0)
	texture.fill_to = Vector2(0, 1)
	texture.width = 16
	texture.height = 16
	return texture


func _apply_safe_area() -> void:
	var left := 48.0
	var right := 48.0
	var top := 24.0
	var bottom := 28.0
	var safe := DisplayServer.get_display_safe_area()
	var window := DisplayServer.window_get_size()
	if safe.size.x > 0 and safe.size.y > 0 and window.x > 0 and window.y > 0 and size.x > 0 and size.y > 0:
		var sx := size.x / window.x
		var sy := size.y / window.y
		left += minf(maxf(safe.position.x * sx, 0.0), SAFE_MARGIN_MAX)
		top += minf(maxf(safe.position.y * sy, 0.0), SAFE_MARGIN_MAX)
		right += minf(maxf(float(window.x - safe.end.x) * sx, 0.0), SAFE_MARGIN_MAX)
		bottom += minf(maxf(float(window.y - safe.end.y) * sy, 0.0), SAFE_MARGIN_MAX)
	_margins.add_theme_constant_override("margin_left", int(left))
	_margins.add_theme_constant_override("margin_right", int(right))
	_margins.add_theme_constant_override("margin_top", int(top))
	_margins.add_theme_constant_override("margin_bottom", int(bottom))


# --- Playback -----------------------------------------------------------------------------------

func _has_end_card() -> bool:
	return sequence != null and not (sequence.end_title.is_empty() and sequence.end_subtitle.is_empty())


func _start_music() -> void:
	if music == null:
		return
	# A narrated sequence has its own bed, written around the narration timeline.
	if not sequence.music.is_empty() and ResourceLoader.exists(sequence.music):
		_bed = load(sequence.music) as AudioStream
		music.play_track(_bed, sequence.music_volume_db)
		_follow_bed = _bed != null and sync_to_bed
		return
	var cue := sequence.music_cue
	if cue.is_empty():
		cue = "%s_theme" % sequence.theme
	music.play_cue(cue)


func _show_stage(index: int) -> void:
	slide_index = index
	_elapsed = 0.0
	var slide := current_slide()
	var path := ""
	var motion := "push_in"
	_fade_out_voice(TAP_VOICE_FADE)
	_voice_due = -1.0
	_voice_end = -1.0
	_voice_started = false
	_subtitle_due = 0.0
	_subtitle_shown = false
	if slide != null:
		_stage_seconds = slide.reading_seconds()
		var stream := _voice_stream(slide.voice)
		if stream != null:
			_voice_due = slide.voice_delay
			_voice_end = slide.voice_delay + stream.get_length()
			_stage_seconds = maxf(_stage_seconds, _voice_end + MIN_VOICE_TAIL)
		_subtitle_due = slide.subtitle_delay
		path = slide.image
		motion = slide.motion
		subtitle_label.text = slide.subtitle
		subtitle_label.add_theme_color_override("font_color", CONTROL_TINT if slide.speaker == CinematicCatalog.SPEAKER_CONTROL else Palette.TEXT)
		caption_label.text = slide.caption
		_title_label.text = ""
	else:
		_stage_seconds = END_CARD_SECONDS
		path = sequence.end_image
		motion = "static"
		subtitle_label.text = sequence.end_subtitle
		subtitle_label.add_theme_color_override("font_color", Palette.ACCENT)
		caption_label.text = ""
		_title_label.text = sequence.end_title
	# The music stays ducked only when the next line starts straight away.
	if _voice_due != 0.0:
		_restore_music(duck_release)
	_transition_to(_load_texture(path), motion, _stage_seconds)
	_update_timed()
	_prefetch_still(index + 1)


## Starts loading the still of stage `index` in the background.
func _prefetch_still(index: int) -> void:
	if sequence == null or index >= stage_count():
		return
	var path := sequence.slides[index].image if index < sequence.slides.size() else sequence.end_image
	if path.is_empty() or _requested.has(path) or not ResourceLoader.exists(path):
		return
	if ResourceLoader.load_threaded_request(path) == OK:
		_requested[path] = true


func _load_texture(path: String) -> Texture2D:
	if _requested.has(path):
		_requested.erase(path)
		var prefetched := ResourceLoader.load_threaded_get(path) as Texture2D
		if prefetched != null:
			return prefetched
	if not path.is_empty() and ResourceLoader.exists(path):
		var texture := load(path) as Texture2D
		if texture != null:
			return texture
	push_warning("CinematicPlayer: no usable image '%s', using plate" % path)
	return _fallback_texture()


func _transition_to(texture: Texture2D, motion: String, seconds: float) -> void:
	if _tween != null:
		_tween.kill()
	var outgoing := _front
	_front = _back
	_back = outgoing
	_front.texture = texture
	_stage.move_child(_front, -1)
	_front.modulate.a = 0.0
	var stage_size := _stage.size
	_front.pivot_offset = stage_size * 0.5
	var start_scale := 1.0
	var end_scale := 1.0
	var start_x := 0.0
	var end_x := 0.0
	var pan := stage_size.x * PAN_FRACTION
	match motion:
		"static":
			pass
		"pull_back":
			start_scale = 1.0 + ZOOM_AMOUNT
		"pan_left":
			start_scale = 1.0 + ZOOM_AMOUNT * 0.8
			end_scale = start_scale
			start_x = -pan
			end_x = pan
		"pan_right":
			start_scale = 1.0 + ZOOM_AMOUNT * 0.8
			end_scale = start_scale
			start_x = pan
			end_x = -pan
		_:
			end_scale = 1.0 + ZOOM_AMOUNT
	_front.scale = Vector2(start_scale, start_scale)
	_front.position = Vector2(start_x, 0.0)
	var duration := maxf(seconds + FADE_SECONDS, 0.1)
	_tween = create_tween().set_parallel()
	_tween.tween_property(_front, "modulate:a", 1.0, FADE_SECONDS)
	_tween.tween_property(_front, "scale", Vector2(end_scale, end_scale), duration)
	_tween.tween_property(_front, "position:x", end_x, duration)
	# The outgoing still stays under the incoming one until the cross-fade is complete.
	_tween.tween_callback(_clear_layer.bind(outgoing)).set_delay(FADE_SECONDS)
	if _subtitle_tween != null:
		_subtitle_tween.kill()
	subtitle_label.modulate.a = 0.0
	caption_label.modulate.a = 0.0
	# The caption comes with the still; the subtitle comes with its line (_update_timed).
	_subtitle_tween = create_tween()
	_subtitle_tween.tween_property(caption_label, "modulate:a", 1.0, SUBTITLE_FADE_SECONDS)


func _clear_layer(layer: TextureRect) -> void:
	if layer != _front:
		layer.modulate.a = 0.0
		layer.texture = null


func _finish(skipped: bool) -> void:
	if _finished:
		return
	_finished = true
	_playing = false
	if skipped:
		# Skip fades everything out: the line quickly, the bed over SKIP_MUSIC_FADE (the next screen
		# then brings in its own music).
		_fade_out_voice(SKIP_VOICE_FADE)
		_restore_music(SKIP_VOICE_FADE)
		if music != null and is_instance_valid(music) and not sequence.music.is_empty():
			music.stop(SKIP_MUSIC_FADE)
	else:
		_fade_out_voice(TAP_VOICE_FADE)
		_restore_music(RESTORE_FADE)
	if _tween != null:
		_tween.kill()
	if _subtitle_tween != null:
		_subtitle_tween.kill()
	finished.emit(sequence.id, skipped)


# --- Narration ----------------------------------------------------------------------------------

## Loads every voice line of the sequence before the first slide, so no clip streams from disk
## mid-slide (low-end Android).
func _preload_voices() -> void:
	_streams.clear()
	if not narration_enabled:
		return
	for slide in sequence.slides:
		if slide.voice.is_empty() or _streams.has(slide.voice):
			continue
		var stream: AudioStream = load(slide.voice) as AudioStream if ResourceLoader.exists(slide.voice) else null
		if stream == null:
			push_warning("CinematicPlayer: narration clip missing '%s'" % slide.voice)
			continue
		_streams[slide.voice] = stream


func _voice_stream(path: String) -> AudioStream:
	if path.is_empty() or not narration_enabled:
		return null
	return _streams.get(path)


## Shows the subtitle, starts the line and moves the duck at their stage times.
func _update_timed() -> void:
	if slide_index < 0 or current_slide() == null:
		return
	if not _subtitle_shown and _elapsed >= _subtitle_due:
		_subtitle_shown = true
		_fade_in_subtitle()
	if _voice_due >= 0.0 and not _voice_started and _elapsed >= _voice_due:
		_voice_started = true
		_play_line(current_slide().voice)
	if _ducked and _voice_started and _elapsed >= _voice_end + duck_hold:
		_restore_music(duck_release)


func _fade_in_subtitle() -> void:
	var tween := create_tween()
	tween.tween_property(subtitle_label, "modulate:a", 1.0, SUBTITLE_FADE_SECONDS)


func _play_line(path: String) -> void:
	var stream := _voice_stream(path)
	if stream == null:
		return
	_voice_index = 1 - _voice_index
	var voice := _voices[_voice_index]
	if _voice_fades[_voice_index] != null and _voice_fades[_voice_index].is_valid():
		_voice_fades[_voice_index].kill()
	voice.stream = stream
	voice.volume_db = 0.0
	voice.play()
	current_voice = path
	_duck_music()


## Fades the current line out over `fade` seconds and stops it (a tap or skip, never a natural end).
func _fade_out_voice(fade: float) -> void:
	current_voice = ""
	if _voices.is_empty():
		return
	var voice := _voices[_voice_index]
	if not voice.playing:
		return
	if not is_inside_tree():
		voice.stop()
		return
	var tween := create_tween()
	tween.tween_property(voice, "volume_db", SILENT_DB, fade)
	tween.tween_callback(voice.stop)
	_voice_fades[_voice_index] = tween


func _stop_all_voices() -> void:
	current_voice = ""
	for i in _voices.size():
		if _voice_fades[i] != null and _voice_fades[i].is_valid():
			_voice_fades[i].kill()
		_voices[i].stop()


## App backgrounded: voice, bed and the slide clock wait together.
func _suspend(on: bool) -> void:
	if not _playing or on == _suspended:
		return
	_suspended = on
	for voice in _voices:
		voice.stream_paused = on
	if music != null and is_instance_valid(music):
		music.active_player().stream_paused = on


func _duck_music() -> void:
	if music != null and is_instance_valid(music) and not _ducked:
		music.duck(duck_db, duck_attack)
	_ducked = true


func _restore_music(fade: float) -> void:
	if not _ducked:
		return
	_ducked = false
	if music != null and is_instance_valid(music):
		music.duck(0.0, fade)
