class_name CinematicPlayer
extends Control
## Plays one CinematicCatalog.Sequence: full-screen stills with slow camera motion, cross-fades,
## subtitles in a lower band, an optional caption line and a closing end card. It only emits
## `finished`; the app decides what happens next and owns saving. Subtitles are the narration:
## the player never plays voice audio (slide.voice is ignored on purpose).
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

## Optional MusicDirector; when set, the sequence's music cue plays on start. Nothing is stopped
## or restored afterwards: the app root restores its own music.
var music: MusicDirector
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


## Shows the next slide (or the end card); finishes after the last one.
func advance() -> void:
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
	if not _playing:
		return
	_elapsed += delta
	if _elapsed >= _stage_seconds:
		advance()


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


# --- Building -----------------------------------------------------------------------------------

func _build() -> void:
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
	if slide != null:
		_stage_seconds = slide.reading_seconds()
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
	_transition_to(_load_texture(path), motion, _stage_seconds)


func _load_texture(path: String) -> Texture2D:
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
	_subtitle_tween = create_tween().set_parallel()
	_subtitle_tween.tween_property(subtitle_label, "modulate:a", 1.0, SUBTITLE_FADE_SECONDS)
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
	if _tween != null:
		_tween.kill()
	if _subtitle_tween != null:
		_subtitle_tween.kill()
	finished.emit(sequence.id, skipped)
