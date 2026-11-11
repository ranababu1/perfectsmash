class_name StoryArchive
extends Control
## Story Archive: replay the story sequences the player has already seen. Entries follow story
## order; unseen ones stay visible but disabled ("Locked"). The opening is always available. It
## only emits signals: the app root plays the sequence and owns saving.

signal play_requested(sequence_id: String)
signal closed

const OPENING_ID := "opening"
## Sequences that exist in the catalog but are not part of the playable story.
const HIDDEN_IDS := ["teaser_2041"]
const TITLE := "Story Archive"
const BACKGROUND := Color("121626")
const ENTRY_HEIGHT := 80.0
const SPACE_M := 16
const SPACE_XL := 32

var _catalog: CinematicCatalog
var _progress: ProgressData
## Integrated assets (production UI theme, like CampaignScreen); set before entering the tree.
var library: AssetLibrary
var _list: VBoxContainer
var _back_button: Button


func _init(catalog: CinematicCatalog = null, progress: ProgressData = null) -> void:
	_catalog = catalog if catalog != null else CinematicCatalog.new()
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
	var column := VBoxContainer.new()
	column.add_theme_constant_override("separation", SPACE_M)
	margin.add_child(column)
	var header := HBoxContainer.new()
	header.add_theme_constant_override("separation", SPACE_M)
	column.add_child(header)
	_back_button = UiKit.button("Back", 160)
	_back_button.name = "BackButton"
	_back_button.pressed.connect(_close)
	header.add_child(_back_button)
	var title := UiKit.label(TITLE, 40, Palette.TEXT)
	title.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	header.add_child(title)
	var balance := Control.new()
	balance.custom_minimum_size = Vector2(160, 0)
	header.add_child(balance)
	var scroll := ScrollContainer.new()
	scroll.size_flags_vertical = Control.SIZE_EXPAND_FILL
	scroll.horizontal_scroll_mode = ScrollContainer.SCROLL_MODE_DISABLED
	column.add_child(scroll)
	_list = VBoxContainer.new()
	_list.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	_list.add_theme_constant_override("separation", 12)
	scroll.add_child(_list)
	refresh()
	_focus_first.call_deferred()


func _unhandled_input(event: InputEvent) -> void:
	if event.is_action_pressed("ui_cancel"):
		get_viewport().set_input_as_handled()
		_close()


## Sequence ids shown in the archive, in story order.
func entry_ids() -> Array[String]:
	var ids: Array[String] = []
	for id in _catalog.order:
		if not HIDDEN_IDS.has(id):
			ids.append(id)
	return ids


## True when the player may replay `sequence_id` (seen before, or the opening).
func is_available(sequence_id: String) -> bool:
	return sequence_id == OPENING_ID or _progress.has_seen_sequence(sequence_id)


## Rebuilds the list from the current progress (call after a sequence was marked seen).
func refresh() -> void:
	if _list == null:
		return
	for child in _list.get_children():
		_list.remove_child(child)
		child.queue_free()
	for id in entry_ids():
		_list.add_child(_make_entry(id))


func _make_entry(id: String) -> Button:
	var sequence := _catalog.get_sequence(id)
	var available := is_available(id)
	var detail := _duration_text(sequence.estimated_seconds()) if available else "Locked"
	var button := UiKit.button("%s      %s" % [sequence.title, detail], 400)
	button.name = "Entry_" + id
	button.custom_minimum_size = Vector2(0, ENTRY_HEIGHT)
	button.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	button.alignment = HORIZONTAL_ALIGNMENT_LEFT
	button.disabled = not available
	if available:
		button.pressed.connect(func() -> void: play_requested.emit(id))
	return button


func _focus_first() -> void:
	if is_inside_tree():
		UiKit.focus_default(_first_available_button())


func _first_available_button() -> Control:
	for child in _list.get_children():
		if child is Button and not child.disabled:
			return child
	return _back_button


func _duration_text(seconds: float) -> String:
	var total := int(round(seconds))
	return "%d:%02d" % [total / 60, total % 60]


func _close() -> void:
	closed.emit()
