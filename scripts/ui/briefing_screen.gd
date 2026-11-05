class_name BriefingScreen
extends Control
## Mission briefing shown before every level: chapter and mission header, the radio dialogue,
## a blueprint of the structure and the objective card. The level is already loaded and settling
## underneath; "Begin mission" simply removes this overlay.

signal begin_pressed
signal back_pressed

const MARGIN := 32.0

var definition: LevelDefinition
var number := 1
var chapter_title := ""
var lines: Array[Dictionary] = []
var narrator: Narrator
var audio: AudioService
var dialogue: DialogueBox
var _skip: Button
var _begin: Button


func _init(p_def: LevelDefinition, p_number: int, p_chapter: String, p_lines: Array[Dictionary], p_narrator: Narrator, p_audio: AudioService) -> void:
	definition = p_def
	number = p_number
	chapter_title = p_chapter
	lines = p_lines
	narrator = p_narrator
	audio = p_audio


func _ready() -> void:
	set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	mouse_filter = Control.MOUSE_FILTER_STOP
	process_mode = Node.PROCESS_MODE_ALWAYS
	var dim := ColorRect.new()
	dim.color = Color(0.03, 0.04, 0.09, 0.9)
	dim.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	dim.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(dim)

	var root := VBoxContainer.new()
	root.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	var insets := SafeArea.current(get_viewport())
	root.offset_left = MARGIN + insets.x
	root.offset_right = -MARGIN - insets.z
	root.offset_top = MARGIN - 6.0 + insets.y
	root.offset_bottom = -MARGIN + 8.0 - insets.w
	root.add_theme_constant_override("separation", 16)
	root.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(root)

	# Header: chapter line, mission number and name, a back button on the right.
	var header := HBoxContainer.new()
	header.mouse_filter = Control.MOUSE_FILTER_IGNORE
	var titles := VBoxContainer.new()
	titles.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	titles.add_theme_constant_override("separation", 0)
	titles.mouse_filter = Control.MOUSE_FILTER_IGNORE
	var chapter := UiKit.label(chapter_title.to_upper(), 16, Palette.TEXT_DIM)
	chapter.horizontal_alignment = HORIZONTAL_ALIGNMENT_LEFT
	chapter.add_theme_font_override("font", MenuScreen._spaced_font(3))
	var mission := HBoxContainer.new()
	mission.add_theme_constant_override("separation", 14)
	mission.mouse_filter = Control.MOUSE_FILTER_IGNORE
	var num := UiKit.label("MISSION %d" % number, 30, Palette.ACCENT)
	num.add_theme_font_override("font", MenuScreen._spaced_font(2))
	var name_label := UiKit.label(definition.name, 30, Palette.TEXT)
	mission.add_child(num)
	mission.add_child(name_label)
	titles.add_child(chapter)
	titles.add_child(mission)
	header.add_child(titles)
	var back := UiKit.icon_button("levels")
	back.name = "BackButton"
	back.tooltip_text = "Missions"
	back.size_flags_vertical = Control.SIZE_SHRINK_CENTER
	back.pressed.connect(back_pressed.emit)
	header.add_child(back)
	root.add_child(header)

	# Body: dialogue on the left; recon image and objective on the right.
	var body := HBoxContainer.new()
	body.size_flags_vertical = Control.SIZE_EXPAND_FILL
	body.add_theme_constant_override("separation", 20)
	body.mouse_filter = Control.MOUSE_FILTER_IGNORE
	dialogue = DialogueBox.new(narrator, audio)
	dialogue.name = "Dialogue"
	dialogue.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	dialogue.size_flags_stretch_ratio = 1.15
	dialogue.theme_type_variation = UiKit.CHIP
	body.add_child(dialogue)

	var side := VBoxContainer.new()
	side.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	side.add_theme_constant_override("separation", 12)
	side.mouse_filter = Control.MOUSE_FILTER_IGNORE
	var schematic := LevelSchematic.new(definition)
	schematic.name = "Schematic"
	schematic.size_flags_vertical = Control.SIZE_EXPAND_FILL
	schematic.custom_minimum_size = Vector2(300, 150)
	side.add_child(schematic)
	side.add_child(_objective_card())
	body.add_child(side)
	root.add_child(body)

	# Footer
	var footer := HBoxContainer.new()
	footer.alignment = BoxContainer.ALIGNMENT_END
	footer.add_theme_constant_override("separation", 12)
	footer.mouse_filter = Control.MOUSE_FILTER_IGNORE
	var tip := UiKit.label("Tap the transcript to speed it up.", 16, Palette.TEXT_DIM)
	tip.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	tip.horizontal_alignment = HORIZONTAL_ALIGNMENT_LEFT
	footer.add_child(tip)
	_skip = UiKit.button("Skip", 160)
	_skip.name = "SkipButton"
	_skip.pressed.connect(func() -> void: dialogue.finish_all())
	_begin = UiKit.primary_button("Begin mission", 260)
	_begin.name = "BeginButton"
	_begin.pressed.connect(_on_begin)
	footer.add_child(_skip)
	footer.add_child(_begin)
	root.add_child(footer)

	dialogue.all_shown.connect(func() -> void: _skip.visible = false)
	UiKit.animate_in(root, 12.0)
	UiKit.focus_default(_begin)
	dialogue.play.call_deferred(lines)


func _objective_card() -> Control:
	var card := PanelContainer.new()
	card.theme_type_variation = UiKit.CHIP
	card.mouse_filter = Control.MOUSE_FILTER_IGNORE
	var box := VBoxContainer.new()
	box.add_theme_constant_override("separation", 4)
	box.mouse_filter = Control.MOUSE_FILTER_IGNORE
	var heading := UiKit.label("OBJECTIVE", 14, Palette.TEXT_DIM)
	heading.horizontal_alignment = HORIZONTAL_ALIGNMENT_LEFT
	heading.add_theme_font_override("font", MenuScreen._spaced_font(3))
	box.add_child(heading)
	for text in [MissionText.objective(definition), MissionText.constraint(definition)]:
		if text == "":
			continue
		var l := UiKit.label(text, 20, Palette.TEXT if text != MissionText.constraint(definition) else Palette.ALLY)
		l.horizontal_alignment = HORIZONTAL_ALIGNMENT_LEFT
		l.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
		l.custom_minimum_size.x = 260
		box.add_child(l)
	var shots := UiKit.label(MissionText.shots_summary(definition), 17, Palette.TEXT_DIM)
	shots.horizontal_alignment = HORIZONTAL_ALIGNMENT_LEFT
	box.add_child(shots)
	card.add_child(box)
	return card


func _on_begin() -> void:
	if narrator != null:
		narrator.stop()
	begin_pressed.emit()
