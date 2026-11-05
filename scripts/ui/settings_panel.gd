class_name SettingsPanel
extends Control
## Settings overlay opened from the menu: sound, vibration, aim guide, the play-test report and
## progress reset. Changes are reported through signals; the app root applies and saves them.

signal setting_changed(key: String, enabled: bool)
signal copy_report_pressed
signal reset_confirmed
signal closed

## Seconds the "tap again to reset" confirmation stays armed.
const RESET_CONFIRM_TIME := 3.0

var progress: ProgressData
var _status: Label
var _reset: Button
var _reset_armed := false


func _init(p_progress: ProgressData) -> void:
	progress = p_progress


func _ready() -> void:
	set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(UiKit.overlay())

	var panel := PanelContainer.new()
	panel.custom_minimum_size.x = UiKit.PANEL_WIDTH + 64.0
	var box := VBoxContainer.new()
	box.add_theme_constant_override("separation", 10)
	panel.add_child(box)

	var header := HBoxContainer.new()
	var title := UiKit.label("Settings", 32, Palette.TEXT)
	title.horizontal_alignment = HORIZONTAL_ALIGNMENT_LEFT
	title.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	header.add_child(title)
	var close := UiKit.icon_button("close")
	close.tooltip_text = "Close"
	close.pressed.connect(closed.emit)
	header.add_child(close)
	box.add_child(header)

	box.add_child(_toggle_row("Sound", "sound", "sound_off", "sound", progress.sound_enabled))
	box.add_child(_toggle_row("Vibration", "vibrate", "vibrate_off", "vibration", progress.vibration_enabled))
	box.add_child(_toggle_row("Aim guide", "aim", "aim_off", "aim_guide", progress.aim_guide_enabled))

	var actions := HBoxContainer.new()
	actions.add_theme_constant_override("separation", 12)
	var copy := UiKit.button("Copy play report", (UiKit.PANEL_WIDTH - 12.0) / 2.0)
	copy.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	copy.add_theme_font_size_override("font_size", 20)
	copy.pressed.connect(copy_report_pressed.emit)
	_reset = UiKit.button("Reset progress", (UiKit.PANEL_WIDTH - 12.0) / 2.0)
	_reset.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	_reset.add_theme_font_size_override("font_size", 20)
	_reset.pressed.connect(_on_reset_pressed)
	actions.add_child(copy)
	actions.add_child(_reset)
	box.add_child(actions)

	_status = UiKit.label("No data leaves this device.  ·  v%s" % ProjectSettings.get_setting("application/config/version", "?"), 16, Palette.TEXT_FAINT)
	box.add_child(_status)

	var center := UiKit.centered(panel)
	add_child(center)
	UiKit.animate_in(center)
	UiKit.focus_default(close)


## Shows a short confirmation under the buttons (e.g. "Report copied").
func show_status(text: String) -> void:
	_status.text = text
	_status.add_theme_color_override("font_color", Palette.TEXT_DIM)


func _toggle_row(text: String, on_icon: String, off_icon: String, key: String, enabled: bool) -> Control:
	var row := HBoxContainer.new()
	row.add_theme_constant_override("separation", 16)
	var label := UiKit.label(text, 24, Palette.TEXT)
	label.horizontal_alignment = HORIZONTAL_ALIGNMENT_LEFT
	label.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	row.add_child(label)
	var toggle := UiKit.icon_button(on_icon, off_icon)
	toggle.name = "Toggle_" + key
	toggle.tooltip_text = text
	toggle.button_pressed = enabled
	toggle.toggled.connect(func(on: bool) -> void: setting_changed.emit(key, on))
	row.add_child(toggle)
	return row


## Reset needs two taps: the first arms it for a few seconds, the second wipes progress.
func _on_reset_pressed() -> void:
	if _reset_armed:
		_reset_armed = false
		_reset.text = "Reset progress"
		reset_confirmed.emit()
		show_status("Progress reset.")
		return
	_reset_armed = true
	_reset.text = "Tap again to reset"
	get_tree().create_timer(RESET_CONFIRM_TIME).timeout.connect(func() -> void:
		if is_instance_valid(_reset) and _reset_armed:
			_reset_armed = false
			_reset.text = "Reset progress")
