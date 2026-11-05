class_name DialogueBox
extends PanelContainer
## Radio-style transcript: lines appear one at a time with a typewriter effect, a speaker badge and
## a radio blip, optionally spoken aloud by the Narrator. Tap to finish the current line early;
## earlier lines stay readable above. Used by the briefing and the debrief.

signal all_shown

const CHARS_PER_SECOND := 55.0
## Pause after a line finishes typing when it is not being spoken (seconds, plus per character).
const HOLD_BASE := 0.7
const HOLD_PER_CHAR := 0.022
## Safety cap so a TTS engine that never reports "done" cannot stall the briefing.
const SPEECH_TIMEOUT_PER_CHAR := 0.12

var narrator: Narrator
var audio: AudioService
var _lines: Array[Dictionary] = []
var _index := -1
var _label: Label
var _typed := 0.0
var _hold := 0.0
var _waiting_speech := false
var _speech_wait := 0.0
var _done := true
var _scroll: ScrollContainer
var _list: VBoxContainer


func _init(p_narrator: Narrator = null, p_audio: AudioService = null) -> void:
	narrator = p_narrator
	audio = p_audio


func _ready() -> void:
	process_mode = Node.PROCESS_MODE_ALWAYS
	mouse_filter = Control.MOUSE_FILTER_STOP
	_scroll = ScrollContainer.new()
	_scroll.horizontal_scroll_mode = ScrollContainer.SCROLL_MODE_DISABLED
	_scroll.mouse_filter = Control.MOUSE_FILTER_PASS
	add_child(_scroll)
	_list = VBoxContainer.new()
	_list.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	_list.add_theme_constant_override("separation", 14)
	_scroll.add_child(_list)
	if narrator != null:
		narrator.line_finished.connect(_on_speech_done)


func play(lines: Array[Dictionary]) -> void:
	_lines = lines
	_index = -1
	_done = lines.is_empty()
	for child in _list.get_children():
		child.queue_free()
	if _done:
		all_shown.emit()
		return
	_next_line()


func is_done() -> bool:
	return _done


## Shows every remaining line at once and stops speech (the "Skip" button).
func finish_all() -> void:
	if _done:
		return
	if narrator != null:
		narrator.stop()
	if _label != null:
		_label.visible_ratio = 1.0
	while _index < _lines.size() - 1:
		_index += 1
		_label = _add_row(_lines[_index])
		_label.visible_ratio = 1.0
	_finish()


## Tap: completes the line being typed, or moves to the next one.
func advance() -> void:
	if _done:
		return
	if _label != null and _label.visible_ratio < 1.0:
		_label.visible_ratio = 1.0
		_typed = _label.text.length()
		_start_hold()
		return
	if narrator != null:
		narrator.stop()
	_next_line()


func _gui_input(event: InputEvent) -> void:
	if event is InputEventMouseButton and event.pressed and event.button_index == MOUSE_BUTTON_LEFT:
		advance()
		accept_event()


func _next_line() -> void:
	_index += 1
	if _index >= _lines.size():
		_finish()
		return
	var line := _lines[_index]
	_label = _add_row(line)
	_label.visible_characters = 0
	_typed = 0.0
	_hold = -1.0
	_waiting_speech = false
	if audio != null:
		audio.play("radio", -8.0)
	if narrator != null and narrator.speak(line.text, line.pitch):
		_waiting_speech = true
		_speech_wait = 0.0


func _process(delta: float) -> void:
	if _done or _label == null:
		return
	if _label.visible_ratio < 1.0:
		_typed += delta * CHARS_PER_SECOND
		_label.visible_characters = int(_typed)
		if _typed >= _label.text.length():
			_label.visible_ratio = 1.0
			_start_hold()
		return
	if _waiting_speech:
		_speech_wait += delta
		if _speech_wait > _label.text.length() * SPEECH_TIMEOUT_PER_CHAR + 2.0:
			_waiting_speech = false
		return
	if _hold >= 0.0:
		_hold -= delta
		if _hold < 0.0:
			_next_line()


func _start_hold() -> void:
	_hold = HOLD_BASE + _label.text.length() * HOLD_PER_CHAR


func _on_speech_done() -> void:
	if _waiting_speech:
		_waiting_speech = false
		_hold = minf(_hold, 0.35) if _hold >= 0.0 else 0.35


func _finish() -> void:
	_done = true
	_label = null
	all_shown.emit()


func _add_row(line: Dictionary) -> Label:
	var row := HBoxContainer.new()
	row.add_theme_constant_override("separation", 14)
	row.mouse_filter = Control.MOUSE_FILTER_IGNORE
	var badge := SpeakerBadge.new(line.name, line.color)
	row.add_child(badge)
	var col := VBoxContainer.new()
	col.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	col.add_theme_constant_override("separation", 2)
	col.mouse_filter = Control.MOUSE_FILTER_IGNORE
	var name_label := UiKit.label(line.name, 15, line.color)
	name_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_LEFT
	var text := UiKit.label(line.text, 21, Palette.TEXT if line.speaker != "log" else Palette.TEXT_DIM)
	text.horizontal_alignment = HORIZONTAL_ALIGNMENT_LEFT
	text.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	text.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	# A wrapping label needs a minimum width or it measures one word per line.
	text.custom_minimum_size.x = 200.0
	text.mouse_filter = Control.MOUSE_FILTER_IGNORE
	col.add_child(name_label)
	col.add_child(text)
	row.add_child(col)
	_list.add_child(row)
	_scroll_to_end.call_deferred()
	return text


func _scroll_to_end() -> void:
	await get_tree().process_frame
	if is_instance_valid(_scroll):
		_scroll.scroll_vertical = int(_scroll.get_v_scroll_bar().max_value)


## Round badge with the speaker's initial in their color; the mission log gets a dash.
class SpeakerBadge extends Control:
	var initial := ""
	var color := Color.WHITE

	func _init(p_name: String, p_color: Color) -> void:
		initial = "—" if p_name == "MISSION LOG" else p_name.substr(0, 1)
		color = p_color
		custom_minimum_size = Vector2(40, 40)
		size_flags_vertical = Control.SIZE_SHRINK_BEGIN
		mouse_filter = Control.MOUSE_FILTER_IGNORE

	func _draw() -> void:
		var c := Vector2(20, 20)
		draw_circle(c, 19.0, Color(color, 0.16), true, -1.0, true)
		draw_arc(c, 18.5, 0, TAU, 40, Color(color, 0.8), 2.0, true)
		var font := ThemeDB.fallback_font
		var size := 20
		var w := font.get_string_size(initial, HORIZONTAL_ALIGNMENT_LEFT, -1, size).x
		draw_string(font, Vector2(20.0 - w / 2.0, 27.0), initial, HORIZONTAL_ALIGNMENT_LEFT, -1, size, color)
