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
## Emitted as each result star appears, so the screen can play a sound for it.
signal star_revealed(index: int)

const MARGIN := 20.0

var _number: Label
var _title: Label
var _chapter: Label
var _objective: Label
var _shots: ShotPips
var _hint: Label
var _hint_chip: Control
var _overlay: Control


func _ready() -> void:
	set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	mouse_filter = Control.MOUSE_FILTER_IGNORE

	var info_chip := _chip()
	info_chip.position = Vector2(MARGIN, MARGIN)
	add_child(info_chip)
	var info := VBoxContainer.new()
	info.mouse_filter = Control.MOUSE_FILTER_IGNORE
	info.add_theme_constant_override("separation", 2)
	info_chip.add_child(info)
	var heading := HBoxContainer.new()
	heading.mouse_filter = Control.MOUSE_FILTER_IGNORE
	heading.add_theme_constant_override("separation", 10)
	_number = _left_label(24, Palette.TEXT_FAINT)
	_title = _left_label(24, Palette.TEXT)
	heading.add_child(_number)
	heading.add_child(_title)
	_objective = _left_label(17, Palette.TEXT_DIM)
	_shots = ShotPips.new()
	_chapter = _left_label(13, Palette.TEXT_FAINT)
	_chapter.visible = false
	info.add_child(_chapter)
	info.add_child(heading)
	info.add_child(_objective)
	info.add_child(_shots)

	# Full-width strip aligned right; the strip itself ignores input so only the buttons block aiming.
	var buttons := HBoxContainer.new()
	buttons.set_anchors_preset(Control.PRESET_TOP_WIDE)
	buttons.offset_left = MARGIN
	buttons.offset_right = -MARGIN
	buttons.offset_top = MARGIN
	buttons.alignment = BoxContainer.ALIGNMENT_END
	buttons.mouse_filter = Control.MOUSE_FILTER_IGNORE
	buttons.add_theme_constant_override("separation", 12)
	add_child(buttons)
	var restart := UiKit.icon_button("restart")
	restart.tooltip_text = "Restart"
	restart.pressed.connect(restart_pressed.emit)
	var pause := UiKit.icon_button("pause")
	pause.tooltip_text = "Pause"
	pause.pressed.connect(pause_pressed.emit)
	buttons.add_child(restart)
	buttons.add_child(pause)

	var hint_row := HBoxContainer.new()
	hint_row.set_anchors_preset(Control.PRESET_BOTTOM_WIDE)
	hint_row.offset_top = -78
	hint_row.offset_bottom = -26
	hint_row.alignment = BoxContainer.ALIGNMENT_CENTER
	hint_row.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(hint_row)
	_hint_chip = _chip()
	_hint = _left_label(19, Palette.TEXT)
	_hint_chip.add_child(_hint)
	hint_row.add_child(_hint_chip)


func set_level(def: LevelDefinition, number: int, chapter_line: String = "") -> void:
	_chapter.text = chapter_line
	_chapter.visible = chapter_line != ""
	_number.text = str(number)
	_title.text = def.name
	if def.objective_type == LevelDefinition.OBJECTIVE_TOPPLE:
		_objective.text = "Bring every block below the green line"
	else:
		var count := def.targets.size()
		_objective.text = "Knock out the red core" if count == 1 else "Knock out all %d red cores" % count
	_hint.text = def.hint
	_hint_chip.modulate.a = 1.0
	_hint_chip.visible = def.hint != ""
	hide_overlay()


func set_shots(remaining: int, budget: int) -> void:
	_shots.set_counts(remaining, budget)


func fade_hint() -> void:
	if _hint_chip.modulate.a <= 0.0:
		return
	create_tween().tween_property(_hint_chip, "modulate:a", 0.0, 0.5)


func has_overlay() -> bool:
	return _overlay != null


func hide_overlay() -> void:
	if _overlay != null:
		_overlay.queue_free()
		_overlay = null


func show_pause(sound_on: bool, vibration_on: bool) -> void:
	var box := _open_panel("Paused", "")
	var resume := UiKit.primary_button("Resume", UiKit.PANEL_WIDTH)
	resume.pressed.connect(resume_pressed.emit)
	box.add_child(resume)
	var row := _button_row()
	row.add_child(_action("Restart", restart_pressed, true))
	row.add_child(_action("Levels", menu_pressed, true))
	box.add_child(row)
	var toggles := HBoxContainer.new()
	toggles.alignment = BoxContainer.ALIGNMENT_CENTER
	toggles.add_theme_constant_override("separation", 16)
	var sound := UiKit.icon_button("sound", "sound_off")
	sound.tooltip_text = "Sound"
	sound.button_pressed = sound_on
	sound.toggled.connect(sound_toggled.emit)
	var vibration := UiKit.icon_button("vibrate", "vibrate_off")
	vibration.tooltip_text = "Vibration"
	vibration.button_pressed = vibration_on
	vibration.toggled.connect(vibration_toggled.emit)
	toggles.add_child(sound)
	toggles.add_child(vibration)
	box.add_child(_spacer(4))
	box.add_child(toggles)
	UiKit.focus_default(resume)


func show_result(won: bool, stars: int, shots_used: int, has_next: bool, par: int = 0) -> void:
	var box: VBoxContainer
	var first: Button
	if won:
		box = _open_panel("Level clear", "")
		var row_stars := StarRow.new(stars, 30.0)
		box.add_child(row_stars)
		row_stars.reveal(star_revealed.emit)
		var detail := "Solved in %d shot%s" % [shots_used, "" if shots_used == 1 else "s"]
		if par > 0 and stars < ScoreRules.MAX_STARS:
			detail += "  ·  par %d" % par
		box.add_child(UiKit.label(detail, 19, Palette.TEXT_DIM))
		box.add_child(_spacer(6))
		if has_next:
			first = UiKit.primary_button("Next level", UiKit.PANEL_WIDTH)
			first.pressed.connect(next_pressed.emit)
			box.add_child(first)
		var row := _button_row()
		row.add_child(_action("Replay", restart_pressed, true))
		row.add_child(_action("Levels", menu_pressed, true))
		box.add_child(row)
		if first == null:
			first = row.get_child(0)
	else:
		box = _open_panel("Out of shots", "Study the structure and try another angle.")
		box.add_child(_spacer(6))
		first = UiKit.primary_button("Retry", UiKit.PANEL_WIDTH)
		first.pressed.connect(restart_pressed.emit)
		box.add_child(first)
		box.add_child(_action("Levels", menu_pressed))
	UiKit.focus_default(first)


func _open_panel(title: String, subtitle: String) -> VBoxContainer:
	hide_overlay()
	var root := Control.new()
	root.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	root.mouse_filter = Control.MOUSE_FILTER_IGNORE
	var dim := UiKit.overlay()
	root.add_child(dim)
	var panel := PanelContainer.new()
	panel.custom_minimum_size.x = UiKit.PANEL_WIDTH + 64.0
	var box := VBoxContainer.new()
	box.add_theme_constant_override("separation", 12)
	box.alignment = BoxContainer.ALIGNMENT_CENTER
	box.add_child(UiKit.label(title, 36, Palette.TEXT))
	if subtitle != "":
		var sub := UiKit.label(subtitle, 19, Palette.TEXT_DIM)
		sub.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
		# A wrapping label needs a width up front, or it reports one word per line as its height.
		sub.custom_minimum_size.x = UiKit.PANEL_WIDTH
		box.add_child(sub)
	panel.add_child(box)
	var center := UiKit.centered(panel)
	root.add_child(center)
	add_child(root)
	_overlay = root
	UiKit.animate_in(center)
	dim.modulate.a = 0.0
	dim.create_tween().tween_property(dim, "modulate:a", 1.0, 0.2)
	return box


func _action(text: String, sig: Signal, half: bool = false) -> Button:
	var b := UiKit.button(text, (UiKit.PANEL_WIDTH - 12.0) / 2.0 if half else UiKit.PANEL_WIDTH)
	b.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	b.pressed.connect(sig.emit)
	return b


func _button_row() -> HBoxContainer:
	var row := HBoxContainer.new()
	row.add_theme_constant_override("separation", 12)
	return row


func _spacer(height: float) -> Control:
	var c := Control.new()
	c.custom_minimum_size.y = height
	c.mouse_filter = Control.MOUSE_FILTER_IGNORE
	return c


func _chip() -> PanelContainer:
	var chip := PanelContainer.new()
	chip.theme_type_variation = UiKit.CHIP
	chip.mouse_filter = Control.MOUSE_FILTER_IGNORE
	return chip


func _left_label(font_size: int, color: Color) -> Label:
	var l := UiKit.label("", font_size, color)
	l.horizontal_alignment = HORIZONTAL_ALIGNMENT_LEFT
	l.mouse_filter = Control.MOUSE_FILTER_IGNORE
	return l


## Remaining shots as a row of small balls: filled = available, hollow = spent.
class ShotPips extends Control:
	const PIP := 7.0
	const GAP := 8.0
	var remaining := 0
	var budget := 0

	func _init() -> void:
		mouse_filter = Control.MOUSE_FILTER_IGNORE
		custom_minimum_size = Vector2(0, PIP * 2.0 + 10.0)

	func set_counts(p_remaining: int, p_budget: int) -> void:
		remaining = p_remaining
		budget = p_budget
		queue_redraw()

	func _draw() -> void:
		for i in budget:
			var center := Vector2(PIP + 1.0 + i * (PIP * 2.0 + GAP), size.y / 2.0 + 2.0)
			if i < remaining:
				draw_circle(center, PIP, Palette.PROJECTILE, true, -1.0, true)
			else:
				draw_arc(center, PIP - 1.0, 0, TAU, 24, Palette.TEXT_FAINT, 1.5, true)
