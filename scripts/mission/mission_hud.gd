class_name MissionHud
extends Control
## Mobile HUD for a tactical mission: objectives with progress, shots against the recommended
## benchmark, time against the target, weapon buttons with ammunition and reload, an aim hint,
## the critical-asset marker, and pause/result panels. Presentation only; MissionScreen feeds it
## state. Uses the production UI theme and icons (GAM-UI-THEME-A, GAM-ICN-*) when `library` has
## them; every value is a live Label, nothing is baked into images.

signal weapon_pressed(weapon_id: String)
signal pause_pressed
signal resume_pressed
signal restart_pressed
## Result panel: continue to the next unlocked mission (success only).
signal next_pressed
## Result panel: leave to the campaign mission list.
signal exit_pressed

const MARGIN := 24.0
const WEAPON_BUTTON := Vector2(168.0, 104.0)
const DONE := Color("7cf0a8")
const FAILED := Color("ff7a6a")
const THEME_ID := "GAM-UI-THEME-A"
const ICONS := {
	"primary": "GAM-ICN-OBJECTIVE_PRIMARY-A", "optional": "GAM-ICN-OBJECTIVE_OPTIONAL-A",
	"complete": "GAM-ICN-OBJECTIVE_COMPLETE-A", "failed": "GAM-ICN-OBJECTIVE_FAILED-A",
	"critical": "GAM-ICN-CRITICAL_ASSET-A", "shots": "GAM-ICN-SHOTS_FIRED-A", "time": "GAM-ICN-TIME_LIMIT-A",
	"ammo": "GAM-ICN-AMMO-A", "pause": "GAM-ICN-PAUSE-A", "retry": "GAM-ICN-RETRY-A",
	"kinetic_accelerator": "GAM-ICN-WEAPON_KINETIC_ACCELERATOR-A", "breach_charge": "GAM-ICN-WEAPON_BREACH_CHARGE-A",
}
const ICON_SIZE := 22.0
const MARKER_SIZE := 44.0
const MARKER_COLOR := Color("ff3b4e")

## Integrated assets (theme, icons); set before the HUD enters the tree. Null = built-in look.
var library: AssetLibrary
## The critical-asset marker (a tinted icon following the core on screen), when icons exist.
var critical_marker: TextureRect

var _objective_box: VBoxContainer
var _stats: Label
var _clock_label: Label
var _hint: Label
var _weapon_buttons := {}
var _reload_bars := {}
var _overlay: Control


func _ready() -> void:
	set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	var production_theme := library.resource(THEME_ID) as Theme if library != null else null
	theme = production_theme if production_theme != null else UiKit.make_theme()
	var marker_icon := icon("critical")
	if marker_icon != null:
		critical_marker = TextureRect.new()
		critical_marker.name = "CriticalMarker"
		critical_marker.texture = marker_icon
		critical_marker.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
		critical_marker.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_CENTERED
		critical_marker.size = Vector2.ONE * MARKER_SIZE
		critical_marker.self_modulate = MARKER_COLOR
		critical_marker.mouse_filter = Control.MOUSE_FILTER_IGNORE
		critical_marker.visible = false
		add_child(critical_marker)

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
	var stats_row := HBoxContainer.new()
	stats_row.mouse_filter = Control.MOUSE_FILTER_IGNORE
	stats_row.add_theme_constant_override("separation", 8)
	stats_chip.add_child(stats_row)
	_add_icon(stats_row, "shots")
	_stats = UiKit.label("", 18, Palette.TEXT)
	stats_row.add_child(_stats)
	_add_icon(stats_row, "time")
	_clock_label = UiKit.label("", 18, Palette.TEXT)
	stats_row.add_child(_clock_label)

	var buttons := HBoxContainer.new()
	buttons.set_anchors_and_offsets_preset(Control.PRESET_TOP_RIGHT)
	buttons.offset_left = -(UiKit.ICON_BUTTON * 2.0 + 12.0 + MARGIN)
	buttons.offset_top = MARGIN
	buttons.offset_right = -MARGIN
	buttons.add_theme_constant_override("separation", 12)
	add_child(buttons)
	var restart := _hud_icon_button("retry", "restart")
	restart.name = "RestartButton"
	restart.pressed.connect(restart_pressed.emit)
	var pause := _hud_icon_button("pause", "pause")
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
		var weapon_icon := icon(weapon.id())
		if weapon_icon != null:
			button.icon = weapon_icon
			button.expand_icon = true
			button.icon_alignment = HORIZONTAL_ALIGNMENT_LEFT
			button.add_theme_constant_override("icon_max_width", 44)
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
	if _clock_label != null:
		_stats.text = "%d / %d" % [shots, recommended] if icon("shots") != null else "SHOTS %d / %d" % [shots, recommended]
		_clock_label.text = "%s / %s" % [_clock(elapsed), _clock(target)]


## Moves the critical-asset marker to a screen position (null hides it).
func place_critical_marker(at: Variant) -> void:
	if critical_marker == null:
		return
	critical_marker.visible = at != null and not has_overlay()
	if at != null:
		critical_marker.position = (at as Vector2) - critical_marker.size / 2.0 + Vector2(0.0, sin(Time.get_ticks_msec() / 320.0) * 4.0)


## An integrated icon texture by key (ICONS), or null.
func icon(key: String) -> Texture2D:
	return library.texture(ICONS[key]) if library != null and ICONS.has(key) else null


func update_objectives(objectives: MissionObjectives) -> void:
	for child in _objective_box.get_children():
		child.queue_free()
	for o in objectives.objectives:
		var marker := "■" if o.mandatory else "□"
		var icon_key := "primary" if o.mandatory else "optional"
		var color := Palette.TEXT if o.mandatory else Palette.TEXT_DIM
		var suffix := ""
		match o.status:
			MissionObjectives.Status.COMPLETE:
				color = DONE
				suffix = "  ✓"
				icon_key = "complete"
			MissionObjectives.Status.FAILED:
				color = FAILED
				suffix = "  ✗"
				icon_key = "failed"
			_:
				if o.is_goal() and o.progress > 0.0:
					suffix = "  %d%%" % int(o.progress * 100.0)
		var row := HBoxContainer.new()
		row.mouse_filter = Control.MOUSE_FILTER_IGNORE
		row.add_theme_constant_override("separation", 8)
		var with_icon := _add_icon(row, icon_key, color)
		# The state icon already says complete/failed; keep only the progress figure beside it.
		if with_icon and o.status != MissionObjectives.Status.PENDING:
			suffix = ""
		var text := ("%s%s" % [o.label, suffix]) if with_icon else ("%s  %s%s" % [marker, o.label, suffix])
		var line := UiKit.label(text, 16 if o.mandatory else 15, color)
		line.horizontal_alignment = HORIZONTAL_ALIGNMENT_LEFT
		line.mouse_filter = Control.MOUSE_FILTER_IGNORE
		row.add_child(line)
		_objective_box.add_child(row)


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
	if success:
		var next := _action("Next mission", next_pressed, true)
		next.name = "NextButton"
		box.add_child(next)
	var again := _action("Run it again" if success else "Retry", restart_pressed, not success)
	again.name = "RetryButton"
	box.add_child(again)
	var missions := _action("Missions", exit_pressed)
	missions.name = "MissionsButton"
	box.add_child(missions)


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


## Adds an icon (tinted) to `parent`; returns false when the icon is not integrated.
func _add_icon(parent: Control, key: String, tint: Color = Palette.TEXT) -> bool:
	var texture := icon(key)
	if texture == null:
		return false
	var rect := TextureRect.new()
	rect.texture = texture
	rect.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
	rect.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_CENTERED
	rect.custom_minimum_size = Vector2.ONE * ICON_SIZE
	rect.self_modulate = tint
	rect.mouse_filter = Control.MOUSE_FILTER_IGNORE
	parent.add_child(rect)
	return true


func _hud_icon_button(key: String, fallback: String) -> Button:
	var texture := icon(key)
	if texture == null:
		return UiKit.icon_button(fallback)
	var button := Button.new()
	button.theme_type_variation = "IconButton"
	button.icon = texture
	button.expand_icon = true
	button.icon_alignment = HORIZONTAL_ALIGNMENT_CENTER
	button.custom_minimum_size = Vector2.ONE * UiKit.ICON_BUTTON
	button.add_theme_constant_override("icon_max_width", 30)
	return button


func _chip() -> PanelContainer:
	var chip := PanelContainer.new()
	chip.theme_type_variation = UiKit.CHIP
	chip.mouse_filter = Control.MOUSE_FILTER_IGNORE
	return chip


static func _clock(seconds: float) -> String:
	var s := int(seconds)
	return "%d:%02d" % [s / 60, s % 60]
