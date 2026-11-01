class_name MenuScreen
extends Control
## Title and level select. Levels unlock in order; each shows its best star medal.

signal level_selected(index: int)
signal sound_toggled(enabled: bool)
signal vibration_toggled(enabled: bool)

const COLUMNS := 5
const TILE_SIZE := Vector2(132, 88)

var catalog: LevelCatalog
var progress: ProgressData


func _init(p_catalog: LevelCatalog, p_progress: ProgressData) -> void:
	catalog = p_catalog
	progress = p_progress


func _ready() -> void:
	set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	var background := ColorRect.new()
	background.color = Palette.SKY_TOP
	background.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	add_child(background)

	var column := VBoxContainer.new()
	column.add_theme_constant_override("separation", 12)
	column.alignment = BoxContainer.ALIGNMENT_CENTER
	add_child(UiKit.centered(column))

	column.add_child(UiKit.label("SMASH THEORY", 64, Palette.ACCENT))
	column.add_child(UiKit.label("One smart hit. A spectacular chain reaction.", 22, Palette.TEXT_DIM))
	var total_possible := catalog.levels.size() * ScoreRules.MAX_STARS
	column.add_child(UiKit.label("Stars: %d / %d" % [progress.total_stars(), total_possible], 24))

	var grid := GridContainer.new()
	grid.columns = COLUMNS
	grid.add_theme_constant_override("h_separation", 12)
	grid.add_theme_constant_override("v_separation", 12)
	var ids := catalog.ids()
	var first_focus: Button = null
	for i in catalog.levels.size():
		var tile := _level_tile(i, progress.is_unlocked(ids, i), progress.stars_for(ids[i]))
		grid.add_child(tile)
		if first_focus == null and not tile.disabled and progress.stars_for(ids[i]) == 0:
			first_focus = tile
	column.add_child(grid)

	var settings := HBoxContainer.new()
	settings.alignment = BoxContainer.ALIGNMENT_CENTER
	settings.add_theme_constant_override("separation", 16)
	settings.add_child(_toggle("Sound", progress.sound_enabled, sound_toggled))
	settings.add_child(_toggle("Vibration", progress.vibration_enabled, vibration_toggled))
	column.add_child(settings)
	if first_focus != null:
		first_focus.grab_focus.call_deferred()


func _level_tile(index: int, unlocked: bool, stars: int) -> Button:
	var tile := Button.new()
	tile.custom_minimum_size = TILE_SIZE
	tile.disabled = not unlocked
	tile.text = str(index + 1) if unlocked else "Locked"
	tile.add_theme_font_size_override("font_size", 30 if unlocked else 20)
	if unlocked:
		var row := StarRow.new(stars, 9.0)
		row.set_anchors_preset(Control.PRESET_BOTTOM_WIDE)
		row.offset_top = -30
		row.offset_bottom = -6
		tile.add_child(row)
		tile.alignment = HORIZONTAL_ALIGNMENT_CENTER
		tile.pressed.connect(level_selected.emit.bind(index))
	return tile


func _toggle(title: String, initial: bool, sig: Signal) -> Button:
	var b := UiKit.button("", 220)
	b.toggle_mode = true
	b.button_pressed = initial
	b.text = "%s: %s" % [title, "On" if initial else "Off"]
	b.toggled.connect(func(on: bool) -> void:
		b.text = "%s: %s" % [title, "On" if on else "Off"]
		sig.emit(on))
	return b
