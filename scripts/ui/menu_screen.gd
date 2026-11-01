class_name MenuScreen
extends Control
## Title and level select. Levels unlock in order; each shows its best star medal.
## The next level to play is highlighted and reachable in one tap via "Continue".

signal level_selected(index: int)
signal sound_toggled(enabled: bool)
signal vibration_toggled(enabled: bool)

const COLUMNS := 5
const TILE_SIZE := Vector2(136, 92)
const MARGIN := 32.0
const TILE := "LevelTile"
const TILE_CURRENT := "LevelTileCurrent"

var catalog: LevelCatalog
var progress: ProgressData


func _init(p_catalog: LevelCatalog, p_progress: ProgressData) -> void:
	catalog = p_catalog
	progress = p_progress


func _ready() -> void:
	set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	_add_tile_styles()
	add_child(Scenery.new())

	var content := Control.new()
	content.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	content.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(content)
	content.add_child(_top_bar())

	var column := VBoxContainer.new()
	column.add_theme_constant_override("separation", 22)
	column.alignment = BoxContainer.ALIGNMENT_CENTER
	column.mouse_filter = Control.MOUSE_FILTER_IGNORE
	var center := UiKit.centered(column)
	center.offset_top = 70.0
	content.add_child(center)

	var grid := GridContainer.new()
	grid.columns = COLUMNS
	grid.add_theme_constant_override("h_separation", 14)
	grid.add_theme_constant_override("v_separation", 14)
	var ids := catalog.ids()
	var current := _current_index()
	for i in catalog.levels.size():
		grid.add_child(_level_tile(i, progress.is_unlocked(ids, i), progress.stars_for(ids[i]), i == current))
	column.add_child(grid)

	if current >= 0:
		var started := progress.is_completed(ids[0])
		var play := UiKit.primary_button("%s  ·  Level %d" % ["Continue" if started else "Play", current + 1], 320)
		play.pressed.connect(level_selected.emit.bind(current))
		var row := HBoxContainer.new()
		row.alignment = BoxContainer.ALIGNMENT_CENTER
		row.add_child(play)
		column.add_child(row)
		UiKit.focus_default(play)
	UiKit.animate_in(content, 10.0)


## First unlocked level without a star, or -1 when everything is cleared.
func _current_index() -> int:
	var ids := catalog.ids()
	for i in catalog.levels.size():
		if progress.is_unlocked(ids, i) and progress.stars_for(ids[i]) == 0:
			return i
	return -1


func _top_bar() -> Control:
	var bar := HBoxContainer.new()
	bar.set_anchors_preset(Control.PRESET_TOP_WIDE)
	bar.offset_left = MARGIN
	bar.offset_right = -MARGIN
	bar.offset_top = MARGIN - 4.0
	bar.mouse_filter = Control.MOUSE_FILTER_IGNORE
	bar.add_theme_constant_override("separation", 12)

	var titles := VBoxContainer.new()
	titles.mouse_filter = Control.MOUSE_FILTER_IGNORE
	titles.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	titles.add_theme_constant_override("separation", 0)
	var title := UiKit.label("PERFECT SMASH", 40, Palette.TEXT)
	title.horizontal_alignment = HORIZONTAL_ALIGNMENT_LEFT
	title.add_theme_font_override("font", _spaced_font(4))
	var tagline := UiKit.label("One smart hit. A spectacular chain reaction.", 18, Palette.TEXT_DIM)
	tagline.horizontal_alignment = HORIZONTAL_ALIGNMENT_LEFT
	titles.add_child(title)
	titles.add_child(tagline)
	bar.add_child(titles)

	var stars := PanelContainer.new()
	stars.theme_type_variation = UiKit.CHIP
	stars.mouse_filter = Control.MOUSE_FILTER_IGNORE
	stars.size_flags_vertical = Control.SIZE_SHRINK_CENTER
	var star_row := HBoxContainer.new()
	star_row.add_theme_constant_override("separation", 8)
	star_row.add_child(Icon.new("star", 28.0, Palette.ACCENT))
	var total := catalog.levels.size() * ScoreRules.MAX_STARS
	star_row.add_child(UiKit.label("%d / %d" % [progress.total_stars(), total], 20))
	stars.add_child(star_row)
	bar.add_child(stars)

	var sound := UiKit.icon_button("sound", "sound_off")
	sound.tooltip_text = "Sound"
	sound.button_pressed = progress.sound_enabled
	sound.toggled.connect(sound_toggled.emit)
	var vibration := UiKit.icon_button("vibrate", "vibrate_off")
	vibration.tooltip_text = "Vibration"
	vibration.button_pressed = progress.vibration_enabled
	vibration.toggled.connect(vibration_toggled.emit)
	for b: Button in [sound, vibration]:
		b.size_flags_vertical = Control.SIZE_SHRINK_CENTER
		bar.add_child(b)
	return bar


func _level_tile(index: int, unlocked: bool, stars: int, current: bool) -> Button:
	var tile := Button.new()
	tile.custom_minimum_size = TILE_SIZE
	tile.disabled = not unlocked
	tile.theme_type_variation = TILE_CURRENT if current else TILE
	if not unlocked:
		var lock := Icon.new("lock", 30.0, Palette.TEXT_FAINT)
		lock.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
		tile.add_child(lock)
		return tile
	var number := UiKit.label(str(index + 1), 30, Palette.TEXT)
	number.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	number.offset_bottom = -22.0
	number.vertical_alignment = VERTICAL_ALIGNMENT_CENTER
	number.mouse_filter = Control.MOUSE_FILTER_IGNORE
	tile.add_child(number)
	var row := StarRow.new(stars, 8.0)
	row.set_anchors_preset(Control.PRESET_BOTTOM_WIDE)
	row.offset_top = -32
	row.offset_bottom = -12
	tile.add_child(row)
	tile.pressed.connect(level_selected.emit.bind(index))
	UiKit.add_press_feedback(tile)
	return tile


func _add_tile_styles() -> void:
	var t := theme if theme != null else UiKit.make_theme()
	theme = t
	t.set_type_variation(TILE, "Button")
	t.set_type_variation(TILE_CURRENT, "Button")
	var current := t.get_stylebox("normal", "Button").duplicate() as StyleBoxFlat
	current.bg_color = Color(Palette.ACCENT, 0.10)
	current.border_color = Color(Palette.ACCENT, 0.75)
	current.set_border_width_all(2)
	t.set_stylebox("normal", TILE_CURRENT, current)
	var hover := current.duplicate() as StyleBoxFlat
	hover.bg_color = Color(Palette.ACCENT, 0.16)
	t.set_stylebox("hover", TILE_CURRENT, hover)


static func _spaced_font(spacing: int) -> Font:
	var font := FontVariation.new()
	font.base_font = ThemeDB.fallback_font
	font.spacing_glyph = spacing
	font.variation_embolden = 0.4
	return font


## The same sky and hills as the levels, so the app feels like one place.
class Scenery extends Control:
	func _ready() -> void:
		set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
		mouse_filter = Control.MOUSE_FILTER_IGNORE
		resized.connect(queue_redraw)

	func _draw() -> void:
		var horizon := size.y * (GameConfig.GROUND_TOP / GameConfig.WORLD_HEIGHT)
		Backdrop.paint(self, Rect2(Vector2.ZERO, Vector2(size.x, horizon)), horizon)
		draw_rect(Rect2(0, horizon, size.x, size.y - horizon), Palette.GROUND)
		draw_line(Vector2(0, horizon), Vector2(size.x, horizon), Palette.GROUND_EDGE, 2.0)
