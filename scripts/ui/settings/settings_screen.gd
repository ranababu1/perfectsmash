class_name SettingsScreen
extends Control
## Sound, music and vibration toggles. Reads initial values from ProgressData but never writes it:
## the caller (main.gd) applies each toggle and saves.

signal sound_toggled(enabled: bool)
signal music_toggled(enabled: bool)
signal vibration_toggled(enabled: bool)
signal back_pressed

const THEME_ID := "GAM-UI-THEME-A"
const TARGET_HEIGHT := 88.0
const SPACE_M := 16
const SPACE_XL := 32
const BACKGROUND := Color("121626")

var library: AssetLibrary
## Optional AudioService; null-safe.
var audio: AudioService
var sound_button: CheckButton
var music_button: CheckButton
var vibration_button: CheckButton

var _progress: ProgressData


func _init(progress: ProgressData = null) -> void:
	_progress = progress if progress != null else ProgressData.new()


func _ready() -> void:
	set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	var production_theme := library.resource(CampaignScreen.THEME_ID) as Theme if library != null else null
	theme = production_theme if production_theme != null else UiKit.make_theme()
	var background := ColorRect.new()
	background.color = BACKGROUND
	background.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	background.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(background)

	var margin := MarginContainer.new()
	margin.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	for side in ["left", "right", "top", "bottom"]:
		margin.add_theme_constant_override("margin_" + side, SPACE_XL)
	add_child(margin)
	var center := CenterContainer.new()
	margin.add_child(center)
	var column := VBoxContainer.new()
	column.custom_minimum_size.x = 520.0
	column.add_theme_constant_override("separation", SPACE_M)
	center.add_child(column)

	column.add_child(UiKit.label("SETTINGS", 40, Palette.TEXT))
	sound_button = _toggle(column, "Sound", "SoundToggle", _progress.sound_enabled, _on_sound)
	music_button = _toggle(column, "Music", "MusicToggle", _progress.music_enabled, _on_music)
	vibration_button = _toggle(column, "Vibration", "VibrationToggle", _progress.vibration_enabled, _on_vibration)
	var back := UiKit.button("Back", 520.0)
	back.name = "BackButton"
	back.custom_minimum_size.y = TARGET_HEIGHT
	back.pressed.connect(_on_back)
	column.add_child(back)
	UiKit.focus_default(sound_button)


func _unhandled_input(event: InputEvent) -> void:
	if event.is_action_pressed("ui_cancel"):
		_on_back()
		get_viewport().set_input_as_handled()


func _toggle(parent: Control, text: String, node_name: String, initial: bool, handler: Callable) -> CheckButton:
	var b := CheckButton.new()
	b.name = node_name
	b.text = text
	b.button_pressed = initial
	b.custom_minimum_size = Vector2(520.0, TARGET_HEIGHT)
	b.add_theme_font_size_override("font_size", 28)
	b.toggled.connect(handler)
	parent.add_child(b)
	return b


func _on_sound(on: bool) -> void:
	_sfx("ui_click")
	sound_toggled.emit(on)


func _on_music(on: bool) -> void:
	_sfx("ui_click")
	music_toggled.emit(on)


func _on_vibration(on: bool) -> void:
	_sfx("ui_click")
	vibration_toggled.emit(on)


func _on_back() -> void:
	_sfx("ui_back")
	back_pressed.emit()


func _sfx(id: String) -> void:
	if audio != null:
		audio.play(id)
