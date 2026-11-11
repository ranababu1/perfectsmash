class_name CampaignScreen
extends Control
## Main menu, chapter select and mission select in one self-contained screen. It only emits
## signals: main.gd decides what happens next and owns saving. Built against the 100-slot
## MissionCatalog, so unauthored slots show as "not yet available" until content lands.

signal mission_selected(mission_id: String)
signal settings_requested
signal upgrades_requested
signal archive_requested

enum View { MENU, CHAPTERS, MISSIONS }
enum SlotState { UNAVAILABLE, LOCKED, AVAILABLE, COMPLETED }

const THEME_ID := "GAM-UI-THEME-A"
const TITLE := "TEMPORAL: FIRST JUMP"
## Spacing scale (px on the 1280x720 base).
const SPACE_S := 8
const SPACE_M := 16
const SPACE_L := 24
const SPACE_XL := 32
## Minimum touch target height.
const TARGET_HEIGHT := 88.0
## Main-menu column width (fits two half-width buttons side by side).
const MENU_WIDTH := 560.0
const ROMAN := ["I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X"]
const BACKGROUND := Color("121626")

## Integrated assets (theme); set before entering the tree. Null = built-in look.
var library: AssetLibrary
## Optional AudioService; null-safe.
var audio: AudioService
var view := View.MENU
var current_chapter := 0

var _missions: MissionCatalog
var _chapters: ChapterCatalog
var _progress: ProgressData
var _content: Control


func _init(missions: MissionCatalog = null, chapters: ChapterCatalog = null, progress: ProgressData = null) -> void:
	_missions = missions
	_chapters = chapters
	_progress = progress if progress != null else ProgressData.new()


func _ready() -> void:
	set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	var production_theme := library.resource(THEME_ID) as Theme if library != null else null
	theme = production_theme if production_theme != null else UiKit.make_theme()
	var background := ColorRect.new()
	background.color = BACKGROUND
	background.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	background.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(background)
	show_menu()


func _unhandled_input(event: InputEvent) -> void:
	if event.is_action_pressed("ui_cancel") and go_back():
		get_viewport().set_input_as_handled()


# --- State queries (usable without building any UI) ---------------------------------------------

## Next unlocked, uncompleted authored mission in campaign order, or "".
func continue_target() -> String:
	for s in _missions.authored():
		if _missions.is_unlocked(s.id, _progress) and not _progress.is_mission_completed(s.id):
			return s.id
	return ""


func slot_state(id: String) -> SlotState:
	var s := _missions.slot(id)
	if s == null or not s.authored:
		return SlotState.UNAVAILABLE
	if _progress.is_mission_completed(id):
		return SlotState.COMPLETED
	return SlotState.AVAILABLE if _missions.is_unlocked(id, _progress) else SlotState.LOCKED


## A chapter is open once its first authored mission is unlocked.
func chapter_unlocked(chapter_number: int) -> bool:
	for s in _missions.chapter_slots(chapter_number):
		if s.authored:
			return _missions.is_unlocked(s.id, _progress)
	return false


func chapter_completed_count(chapter_number: int) -> int:
	var count := 0
	for s in _missions.chapter_slots(chapter_number):
		if _progress.is_mission_completed(s.id):
			count += 1
	return count


# --- Navigation ----------------------------------------------------------------------------------

func show_menu() -> void:
	view = View.MENU
	var box := _reset("MainMenu")
	box.add_child(UiKit.label(TITLE, 56, Palette.TEXT))
	var spacer := Control.new()
	spacer.custom_minimum_size = Vector2(0, SPACE_XL)
	box.add_child(spacer)
	var target := continue_target()
	var continue_button := _action("Continue", func() -> void: _select(target), true)
	continue_button.name = "ContinueButton"
	continue_button.disabled = target.is_empty()
	box.add_child(continue_button)
	if not target.is_empty():
		box.add_child(UiKit.label(_slot_title(_missions.slot(target)), 18, Palette.TEXT_DIM))
	var campaign := _action("Campaign", show_chapters)
	campaign.name = "CampaignButton"
	box.add_child(campaign)
	var row := HBoxContainer.new()
	row.add_theme_constant_override("separation", SPACE_M)
	box.add_child(row)
	var upgrades := _action("Upgrades", _request.bind(upgrades_requested))
	upgrades.name = "UpgradesButton"
	var archive := _action("Story Archive", _request.bind(archive_requested))
	archive.name = "ArchiveButton"
	for b: Button in [upgrades, archive]:
		# Two half-width buttons share the column (the default 420 px minimum would overflow).
		b.custom_minimum_size.x = 0.0
		b.size_flags_horizontal = Control.SIZE_EXPAND_FILL
		row.add_child(b)
	var settings := _action("Settings", _request_settings)
	settings.name = "SettingsButton"
	box.add_child(settings)
	if not continue_button.disabled:
		UiKit.focus_default(continue_button)
	else:
		UiKit.focus_default(campaign)


func show_chapters() -> void:
	_sfx("ui_click")
	view = View.CHAPTERS
	current_chapter = 0
	var column := _reset("ChapterSelect", true)
	column.add_child(_header("CHAPTERS"))
	var list := _scroll_list(column, 1)
	for chapter in _chapters.chapters:
		var unlocked := chapter_unlocked(chapter.number)
		var text := "%s   %s\n%s  ·  %d\n%s" % [
			_roman(chapter.number), chapter.title.to_upper(), chapter.organization, chapter.year,
			("%d / %d complete" % [chapter_completed_count(chapter.number), _missions.chapter_slots(chapter.number).size()])
			if unlocked else "Locked"]
		var button := _tile(text, "Chapter_%d" % chapter.number)
		button.disabled = not unlocked
		var number := chapter.number
		button.pressed.connect(func() -> void: show_missions(number))
		list.add_child(button)
	if list.get_child_count() > 0:
		UiKit.focus_default(_first_enabled(list))


func show_missions(chapter_number: int) -> void:
	_sfx("ui_click")
	view = View.MISSIONS
	current_chapter = chapter_number
	var chapter := _chapters.chapters[chapter_number - 1]
	var column := _reset("MissionSelect", true)
	column.add_child(_header("%s  %s" % [_roman(chapter_number), chapter.title.to_upper()]))
	var grid := _scroll_list(column, 2)
	for s in _missions.chapter_slots(chapter_number):
		var state := slot_state(s.id)
		var button := _tile(_slot_text(s, state), "Mission_%s" % s.id)
		button.disabled = state == SlotState.LOCKED or state == SlotState.UNAVAILABLE
		if state == SlotState.AVAILABLE:
			button.theme_type_variation = UiKit.PRIMARY
		var id: String = s.id
		button.pressed.connect(func() -> void: _select(id))
		grid.add_child(button)
	UiKit.focus_default(_first_enabled(grid))


## Steps back one level; returns false at the main menu (nothing to go back to).
func go_back() -> bool:
	match view:
		View.MISSIONS:
			_sfx("ui_back")
			show_chapters_silent()
			return true
		View.CHAPTERS:
			_sfx("ui_back")
			show_menu()
			return true
	return false


func show_chapters_silent() -> void:
	var saved := audio
	audio = null
	show_chapters()
	audio = saved


# --- Building blocks -----------------------------------------------------------------------------

## Clears the content area. `with_back` adds a left-aligned Back button above the content and
## returns the content column; otherwise returns a centered column (main menu).
func _reset(node_name: String, with_back: bool = false) -> VBoxContainer:
	if _content != null:
		remove_child(_content)
		_content.queue_free()
	var margin := MarginContainer.new()
	margin.name = node_name
	margin.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	for side in ["left", "right", "top", "bottom"]:
		margin.add_theme_constant_override("margin_" + side, SPACE_XL)
	add_child(margin)
	_content = margin
	var column := VBoxContainer.new()
	column.add_theme_constant_override("separation", SPACE_M)
	if with_back:
		margin.add_child(column)
		var back := UiKit.button("Back", 160.0)
		back.name = "BackButton"
		back.custom_minimum_size.y = TARGET_HEIGHT
		back.size_flags_horizontal = Control.SIZE_SHRINK_BEGIN
		back.pressed.connect(go_back)
		column.add_child(back)
		return column
	var center := CenterContainer.new()
	margin.add_child(center)
	column.custom_minimum_size.x = MENU_WIDTH
	center.add_child(column)
	return column


func _header(text: String) -> Label:
	var l := UiKit.label(text, 32, Palette.TEXT)
	l.horizontal_alignment = HORIZONTAL_ALIGNMENT_LEFT
	return l


## Scrolling grid that fills the rest of the column; vertical scroll only, so 20 slots or a
## narrow window never push content off screen.
func _scroll_list(column: VBoxContainer, columns: int) -> GridContainer:
	var scroll := ScrollContainer.new()
	scroll.name = "Scroll"
	scroll.size_flags_vertical = Control.SIZE_EXPAND_FILL
	scroll.horizontal_scroll_mode = ScrollContainer.SCROLL_MODE_DISABLED
	column.add_child(scroll)
	var grid := GridContainer.new()
	grid.name = "List"
	grid.columns = columns
	grid.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	grid.add_theme_constant_override("h_separation", SPACE_M)
	grid.add_theme_constant_override("v_separation", SPACE_M)
	scroll.add_child(grid)
	return grid


func _tile(text: String, node_name: String) -> Button:
	var b := UiKit.button(text, 0.0)
	b.name = node_name
	b.custom_minimum_size = Vector2(0.0, TARGET_HEIGHT)
	b.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	b.alignment = HORIZONTAL_ALIGNMENT_LEFT
	b.clip_text = true
	b.add_theme_font_size_override("font_size", 20)
	return b


func _action(text: String, on_press: Callable, primary: bool = false) -> Button:
	var b := UiKit.primary_button(text, MENU_WIDTH) if primary else UiKit.button(text, MENU_WIDTH)
	b.custom_minimum_size.y = TARGET_HEIGHT
	b.pressed.connect(on_press)
	return b


func _first_enabled(parent: Control) -> Control:
	for child in parent.get_children():
		if child is Button and not (child as Button).disabled:
			return child
	return parent.get_child(0)


func _select(id: String) -> void:
	if id.is_empty():
		return
	_sfx("ui_confirm")
	mission_selected.emit(id)


func _request_settings() -> void:
	_sfx("ui_click")
	settings_requested.emit()


func _request(which: Signal) -> void:
	_sfx("ui_click")
	which.emit()


func _sfx(id: String) -> void:
	if audio != null:
		audio.play(id)


func _slot_title(s: MissionCatalog.Slot) -> String:
	return "%s  ·  Mission %02d" % [s.chapter.title, s.index]


func _slot_text(s: MissionCatalog.Slot, state: SlotState) -> String:
	var title := s.display_name()
	var head := "%02d" % s.index if title.is_empty() else "%02d  %s" % [s.index, title]
	match state:
		SlotState.COMPLETED:
			return "%s  ✓\nBest %d pts" % [head, int(_progress.mission_result(s.id).get("best_points", 0))]
		SlotState.AVAILABLE:
			return "%s\nReady" % head
		SlotState.LOCKED:
			return "%s\nLocked" % head
	return "%s\nNot yet available" % head


func _roman(n: int) -> String:
	return ROMAN[n - 1] if n >= 1 and n <= ROMAN.size() else str(n)
