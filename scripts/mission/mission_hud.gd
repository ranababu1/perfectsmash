class_name MissionHud
extends Control
## Mobile HUD for a tactical mission: objectives with progress, shots against the recommended
## benchmark, time against the target, weapon buttons with ammunition and reload, an aim hint,
## and pause/result panels. Presentation only; MissionScreen feeds it state.

signal weapon_pressed(weapon_id: String)
signal pause_pressed
signal resume_pressed
signal restart_pressed

const MARGIN := 24.0
const WEAPON_BUTTON := Vector2(168.0, 104.0)
const DONE := Color("7cf0a8")
const FAILED := Color("ff7a6a")

var _objective_box: VBoxContainer
var _stats: Label
var _hint: Label
var _weapon_buttons := {}
var _reload_bars := {}
var _overlay: Control


func _ready() -> void:
	set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	mouse_filter = Control.MOUSE_FILTER_IGNORE

	var objectives := _chip()
	objectives.position = Vector2(MARGIN, MARGIN)
	add_child(objectives)
	_objective_box = VBoxContainer.new()
	_objective_box.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_objective_box.add_theme_constant_override("separation", 4)
	objectives.add_child(_objective_box)

	var stats_chip := _chip()
	stats_chip.set_anchors_preset(Control.PRESET_CENTER_TOP)
	stats_chip.position = Vector2(-120.0, MARGIN)
	add_child(stats_chip)
	_stats = UiKit.label("", 18, Palette.TEXT)
	stats_chip.add_child(_stats)

	var buttons := HBoxContainer.new()
	buttons.set_anchors_and_offsets_preset(Control.PRESET_TOP_RIGHT)
	buttons.offset_left = -(UiKit.ICON_BUTTON * 2.0 + 12.0 + MARGIN)
	buttons.offset_top = MARGIN
	buttons.offset_right = -MARGIN
	buttons.add_theme_constant_override("separation", 12)
	add_child(buttons)
	var restart := UiKit.icon_button("restart")
	restart.name = "RestartButton"
	restart.pressed.connect(restart_pressed.emit)
	var pause := UiKit.icon_button("pause")
	pause.name = "PauseButton"
	pause.pressed.connect(pause_pressed.emit)
	buttons.add_child(restart)
	buttons.add_child(pause)

	_hint = UiKit.label("", 17, Palette.TEXT_DIM)
	_hint.set_anchors_and_offsets_preset(Control.PRESET_CENTER_BOTTOM)
	_hint.offset_top = -MARGIN - 30.0
	_hint.offset_left = -300.0
	_hint.offset_right = 300.0
	_hint.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(_hint)


## Creates one large button per weapon (bottom right), in mission order.
func set_weapons(weapons: Array[WeaponState]) -> void:
	var row := HBoxContainer.new()
	row.set_anchors_and_offsets_preset(Control.PRESET_BOTTOM_RIGHT)
	row.add_theme_constant_override("separation", 12)
	row.offset_left = -(WEAPON_BUTTON.x * weapons.size() + 12.0 * (weapons.size() - 1) + MARGIN)
	row.offset_top = -(WEAPON_BUTTON.y + MARGIN)
	row.offset_right = -MARGIN
	row.offset_bottom = -MARGIN
	row.grow_horizontal = Control.GROW_DIRECTION_BEGIN
	row.grow_vertical = Control.GROW_DIRECTION_BEGIN
	add_child(row)
	for weapon in weapons:
		var button := UiKit.button("", WEAPON_BUTTON.x)
		button.name = "Weapon_%s" % weapon.id()
		button.custom_minimum_size = WEAPON_BUTTON
		button.add_theme_font_size_override("font_size", 17)
		button.pressed.connect(weapon_pressed.emit.bind(weapon.id()))
		var bar := ColorRect.new()
		bar.color = Color(0.75, 0.93, 1.0, 0.5)
		bar.mouse_filter = Control.MOUSE_FILTER_IGNORE
		bar.set_anchors_and_offsets_preset(Control.PRESET_BOTTOM_WIDE)
		bar.offset_top = -6.0
		button.add_child(bar)
		row.add_child(button)
		_weapon_buttons[weapon.id()] = button
		_reload_bars[weapon.id()] = bar


func update_weapons(weapons: Dictionary, selected_id: String) -> void:
	for id: String in _weapon_buttons:
		var weapon: WeaponState = weapons[id]
		var button: Button = _weapon_buttons[id]
		# Short label so the button never outgrows its slot on phones.
		var title := weapon.spec.display_name.get_slice(" ", 0).to_upper()
		button.text = "%s\n%d / %d" % [title, weapon.ammo, weapon.ammo_capacity]
		button.theme_type_variation = UiKit.PRIMARY if id == selected_id else ""
		button.disabled = not weapon.has_ammo()
		var bar: ColorRect = _reload_bars[id]
		bar.anchor_right = weapon.cooldown_fraction()
		bar.offset_right = 0.0


func update_stats(shots: int, recommended: int, elapsed: float, target: float) -> void:
	_stats.text = "SHOTS %d / %d   ·   %s / %s" % [shots, recommended, _clock(elapsed), _clock(target)]


func update_objectives(objectives: MissionObjectives) -> void:
	for child in _objective_box.get_children():
		child.queue_free()
	for o in objectives.objectives:
		var marker := "■" if o.mandatory else "□"
		var color := Palette.TEXT if o.mandatory else Palette.TEXT_DIM
		var suffix := ""
		match o.status:
			MissionObjectives.Status.COMPLETE:
				color = DONE
				suffix = "  ✓"
			MissionObjectives.Status.FAILED:
				color = FAILED
				suffix = "  ✗"
			_:
				if o.is_goal() and o.progress > 0.0:
					suffix = "  %d%%" % int(o.progress * 100.0)
		var line := UiKit.label("%s  %s%s" % [marker, o.label, suffix], 16 if o.mandatory else 15, color)
		line.horizontal_alignment = HORIZONTAL_ALIGNMENT_LEFT
		line.mouse_filter = Control.MOUSE_FILTER_IGNORE
		_objective_box.add_child(line)


func set_hint(text: String) -> void:
	_hint.text = text


func has_overlay() -> bool:
	return _overlay != null


func show_pause() -> void:
	var box := _open_panel("PAUSED", "")
	box.add_child(_action("Resume", resume_pressed, true))
	box.add_child(_action("Restart mission", restart_pressed))


## `score` is a MissionScoring breakdown; `granted` the Research Data actually added this run.
func show_result(success: bool, engine: MissionEngine, score: Dictionary = {}, granted: int = 0, balance: int = 0) -> void:
	var title := "FACILITY NEUTRALISED" if success else "MISSION FAILED"
	var detail := "Shots %d (recommended %d)  ·  %s (target %s)" % [
		engine.shots_fired(), engine.definition.recommended_shots, _clock(engine.elapsed), _clock(engine.definition.target_time)]
	var box := _open_panel(title, detail)
	for o in engine.objectives.objectives:
		var ok := o.status == MissionObjectives.Status.COMPLETE
		var line := UiKit.label("%s  %s" % ["✓" if ok else "✗", o.label], 16, DONE if ok else Palette.TEXT_FAINT)
		box.add_child(line)
	if not score.is_empty():
		var points := UiKit.label("MISSION POINTS  %d" % int(score.mission_points), 24, Palette.ACCENT)
		points.name = "MissionPoints"
		box.add_child(points)
		var p: Dictionary = score.points
		var breakdown := "Destruction %d · Critical %d · Efficiency %d · Accuracy %d" % [
			p.destruction, p.critical_asset, int(p.shot_efficiency) + int(p.time_efficiency), p.accuracy]
		box.add_child(UiKit.label(breakdown, 15, Palette.TEXT_DIM))
		var research := "RESEARCH DATA  +%d   (balance %d)" % [granted, balance]
		if success and granted == 0 and int(score.research_data) > 0:
			research += "  · beat your best to earn more"
		var research_label := UiKit.label(research, 18, Color("8fe3f5"))
		research_label.name = "ResearchData"
		box.add_child(research_label)
	box.add_child(_action("Run it again" if success else "Retry", restart_pressed, true))


func hide_overlay() -> void:
	if _overlay != null:
		_overlay.queue_free()
		_overlay = null


func _open_panel(title: String, subtitle: String) -> VBoxContainer:
	hide_overlay()
	_overlay = UiKit.overlay()
	add_child(_overlay)
	var panel := PanelContainer.new()
	panel.custom_minimum_size = Vector2(UiKit.PANEL_WIDTH + 80.0, 0.0)
	var box := VBoxContainer.new()
	box.add_theme_constant_override("separation", 12)
	panel.add_child(box)
	box.add_child(UiKit.label(title, 32, Palette.TEXT))
	if subtitle != "":
		box.add_child(UiKit.label(subtitle, 17, Palette.TEXT_DIM))
	_overlay.add_child(UiKit.centered(panel))
	UiKit.animate_in(panel)
	return box


func _action(text: String, sig: Signal, primary: bool = false) -> Button:
	var b := UiKit.primary_button(text, 280.0) if primary else UiKit.button(text, 280.0)
	b.pressed.connect(sig.emit)
	return b


func _chip() -> PanelContainer:
	var chip := PanelContainer.new()
	chip.theme_type_variation = UiKit.CHIP
	chip.mouse_filter = Control.MOUSE_FILTER_IGNORE
	return chip


static func _clock(seconds: float) -> String:
	var s := int(seconds)
	return "%d:%02d" % [s / 60, s % 60]
