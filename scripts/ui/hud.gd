class_name Hud
extends Control
## In-level UI: objective, shots left, pause/restart buttons, hint, and the pause/result overlays.
## The root ignores mouse input so the play area stays aimable; only real controls block touches.

signal pause_pressed
signal restart_pressed
signal resume_pressed
signal menu_pressed
signal next_pressed
signal sound_toggled(enabled: bool)
signal vibration_toggled(enabled: bool)

const MARGIN := 24.0

var _title: Label
var _objective: Label
var _shots: Label
var _hint: Label
var _overlay: Control


func _ready() -> void:
	set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	mouse_filter = Control.MOUSE_FILTER_IGNORE

	var info := VBoxContainer.new()
	info.position = Vector2(MARGIN, MARGIN * 0.6)
	info.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(info)
	_title = UiKit.label("", 30)
	_title.horizontal_alignment = HORIZONTAL_ALIGNMENT_LEFT
	_objective = UiKit.label("", 22, Palette.TEXT_DIM)
	_objective.horizontal_alignment = HORIZONTAL_ALIGNMENT_LEFT
	_shots = UiKit.label("", 24, Palette.ACCENT)
	_shots.horizontal_alignment = HORIZONTAL_ALIGNMENT_LEFT
	for l in [_title, _objective, _shots]:
		info.add_child(l)

	# Full-width strip aligned right; the strip itself ignores input so only the buttons block aiming.
	var buttons := HBoxContainer.new()
	buttons.set_anchors_preset(Control.PRESET_TOP_WIDE)
	buttons.offset_left = MARGIN
	buttons.offset_right = -MARGIN
	buttons.offset_top = MARGIN * 0.6
	buttons.alignment = BoxContainer.ALIGNMENT_END
	buttons.mouse_filter = Control.MOUSE_FILTER_IGNORE
	buttons.add_theme_constant_override("separation", 12)
	add_child(buttons)
	var restart := UiKit.button("Restart", 140)
	restart.pressed.connect(restart_pressed.emit)
	var pause := UiKit.button("Pause", 120)
	pause.pressed.connect(pause_pressed.emit)
	buttons.add_child(restart)
	buttons.add_child(pause)

	_hint = UiKit.label("", 24, Palette.TEXT)
	_hint.set_anchors_preset(Control.PRESET_BOTTOM_WIDE)
	_hint.offset_top = -56
	_hint.offset_bottom = -20
	_hint.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(_hint)


func set_level(def: LevelDefinition, number: int) -> void:
	_title.text = "%d. %s" % [number, def.name]
	if def.objective_type == LevelDefinition.OBJECTIVE_TOPPLE:
		_objective.text = "Goal: bring every block below the green line"
	else:
		_objective.text = "Goal: destroy %d red core%s" % [def.targets.size(), "" if def.targets.size() == 1 else "s"]
	_hint.text = def.hint
	_hint.modulate.a = 1.0
	hide_overlay()


func set_shots(remaining: int, budget: int) -> void:
	_shots.text = "Shots: %d / %d" % [remaining, budget]


func fade_hint() -> void:
	if _hint.modulate.a <= 0.0:
		return
	create_tween().tween_property(_hint, "modulate:a", 0.0, 0.6)


func has_overlay() -> bool:
	return _overlay != null


func hide_overlay() -> void:
	if _overlay != null:
		_overlay.queue_free()
		_overlay = null


func show_pause(sound_on: bool, vibration_on: bool) -> void:
	var box := _open_panel("Paused")
	box.add_child(_action("Resume", resume_pressed))
	box.add_child(_action("Restart", restart_pressed))
	var sound := UiKit.button("")
	_bind_toggle(sound, "Sound", sound_on, sound_toggled)
	box.add_child(sound)
	var vibration := UiKit.button("")
	_bind_toggle(vibration, "Vibration", vibration_on, vibration_toggled)
	box.add_child(vibration)
	box.add_child(_action("Levels", menu_pressed))
	box.get_child(1).grab_focus.call_deferred()


func show_result(won: bool, stars: int, shots_used: int, has_next: bool) -> void:
	var box := _open_panel("Level Clear!" if won else "Out of Shots")
	if won:
		box.add_child(StarRow.new(stars, 28.0))
		box.add_child(UiKit.label("Solved with %d shot%s" % [shots_used, "" if shots_used == 1 else "s"], 24, Palette.TEXT_DIM))
		if has_next:
			box.add_child(_action("Next Level", next_pressed))
		box.add_child(_action("Replay", restart_pressed))
	else:
		box.add_child(UiKit.label("Study the structure and try another angle.", 22, Palette.TEXT_DIM))
		box.add_child(_action("Retry", restart_pressed))
	box.add_child(_action("Levels", menu_pressed))
	for child in box.get_children():
		if child is Button:
			child.grab_focus.call_deferred()
			break


func _open_panel(title: String) -> VBoxContainer:
	hide_overlay()
	var root := Control.new()
	root.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	root.mouse_filter = Control.MOUSE_FILTER_IGNORE
	root.add_child(UiKit.overlay())
	var panel := PanelContainer.new()
	var box := VBoxContainer.new()
	box.add_theme_constant_override("separation", 14)
	box.alignment = BoxContainer.ALIGNMENT_CENTER
	box.add_child(UiKit.label(title, 40, Palette.ACCENT))
	panel.add_child(box)
	root.add_child(UiKit.centered(panel))
	add_child(root)
	_overlay = root
	return box


func _action(text: String, sig: Signal) -> Button:
	var b := UiKit.button(text, 300)
	b.pressed.connect(sig.emit)
	return b


func _bind_toggle(b: Button, title: String, initial: bool, sig: Signal) -> void:
	b.custom_minimum_size.x = 300
	b.toggle_mode = true
	b.button_pressed = initial
	b.text = "%s: %s" % [title, "On" if initial else "Off"]
	b.toggled.connect(func(on: bool) -> void:
		b.text = "%s: %s" % [title, "On" if on else "Off"]
		sig.emit(on))
