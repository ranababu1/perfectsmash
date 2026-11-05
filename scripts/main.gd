extends Node
## App root: owns persistence, audio, narration, the level catalog and the story; switches between
## the menu, mission briefings and the game. Handles Android back and app backgrounding (auto-pause).

const FADE_TIME := 0.22

var save := SaveService.new()
var progress: ProgressData
var catalog: LevelCatalog
var audio: AudioService
var narrator: Narrator
## Null when data/story.json is missing or invalid: the game then plays without briefings.
var story: StoryCatalog
var _menu: MenuScreen
var _game: GameScreen
var _settings: SettingsPanel
var _briefing: BriefingScreen
var _briefing_layer: CanvasLayer
var _level_index := -1
var _fade: ColorRect


func _ready() -> void:
	process_mode = Node.PROCESS_MODE_ALWAYS
	progress = save.load_progress()
	audio = AudioService.new()
	audio.enabled = progress.sound_enabled
	add_child(audio)
	narrator = Narrator.new()
	narrator.enabled = progress.narration_enabled
	add_child(narrator)
	catalog = LevelCatalog.load_from_file()
	if not catalog.is_valid():
		push_error("Level catalog invalid: %s" % ", ".join(catalog.errors))
		var message := UiKit.label("Level data failed to load.\n" + "\n".join(catalog.errors.slice(0, 5)), 22)
		message.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
		add_child(message)
		return
	story = StoryCatalog.load_from_file()
	var story_problems := story.errors + story.validate_against(catalog.ids())
	if not story_problems.is_empty():
		push_error("Story disabled: %s" % ", ".join(story_problems.slice(0, 5)))
		story = null
	_add_fade_layer()
	_show_menu()


## A full-screen veil that fades out after every screen change. It never takes input.
func _add_fade_layer() -> void:
	var layer := CanvasLayer.new()
	layer.layer = 100
	add_child(layer)
	_fade = ColorRect.new()
	_fade.color = Palette.SKY_TOP
	_fade.mouse_filter = Control.MOUSE_FILTER_IGNORE
	_fade.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	layer.add_child(_fade)


func _reveal() -> void:
	if _fade == null:
		return
	_fade.modulate.a = 1.0
	_fade.create_tween().tween_property(_fade, "modulate:a", 0.0, FADE_TIME)


func _notification(what: int) -> void:
	match what:
		NOTIFICATION_WM_GO_BACK_REQUEST:
			_handle_back()
		NOTIFICATION_APPLICATION_PAUSED, NOTIFICATION_APPLICATION_FOCUS_OUT:
			narrator.stop()
			if _game != null and _briefing == null:
				_game.pause()


func _unhandled_input(event: InputEvent) -> void:
	if event.is_action_pressed("ui_cancel"):
		_handle_back()
		get_viewport().set_input_as_handled()


func _handle_back() -> void:
	if close_settings():
		return
	if _briefing != null:
		_show_menu()
		return
	if _game != null:
		_game.handle_back()
	elif OS.get_name() == "Android":
		get_tree().quit()


func _show_menu() -> void:
	_clear_screens()
	_menu = MenuScreen.new(catalog, progress, story)
	_menu.theme = UiKit.make_theme()
	_menu.level_selected.connect(_start_level)
	_menu.settings_pressed.connect(_open_settings)
	add_child(_menu)
	_reveal()


func _open_settings() -> void:
	if _menu == null or _settings != null:
		return
	audio.play("click")
	_settings = SettingsPanel.new(progress)
	_settings.narration_available = narrator.is_available()
	_settings.theme = _menu.theme
	_settings.setting_changed.connect(_apply_setting)
	_settings.copy_report_pressed.connect(_copy_report)
	_settings.reset_confirmed.connect(_reset_progress)
	_settings.closed.connect(close_settings)
	_menu.add_child(_settings)


## Returns true if a settings panel was open (used by the back button).
func close_settings() -> bool:
	if _settings == null:
		return false
	_settings.queue_free()
	_settings = null
	audio.play("click")
	return true


func _apply_setting(key: String, enabled: bool) -> void:
	match key:
		"sound":
			_set_sound(enabled)
		"vibration":
			_set_vibration(enabled)
		"aim_guide":
			_set_aim_guide(enabled)
		"narration":
			progress.narration_enabled = enabled
			narrator.enabled = enabled
			if not enabled:
				narrator.stop()
			save.save_progress(progress)
		_:
			push_error("Unknown setting '%s'" % key)


func _copy_report() -> void:
	var version := str(ProjectSettings.get_setting("application/config/version", "?"))
	DisplayServer.clipboard_set(progress.playtest_report(catalog.ids(), version))
	if _settings != null:
		_settings.show_status("Report copied. Paste it into a message to the developer.")


func _reset_progress() -> void:
	progress.reset_progress()
	save.save_progress(progress)
	_show_menu()


## Loads a level and, when the story is available, shows its briefing on top while the
## structure settles underneath.
func _start_level(index: int, brief: bool = true) -> void:
	audio.play("click")
	_close_briefing()
	if _game == null:
		_clear_screens()
		_game = GameScreen.new(audio, progress)
		_game.story = story
		_game.narrator = narrator
		_game.exit_requested.connect(_show_menu)
		_game.next_requested.connect(func() -> void: _start_level(_level_index + 1))
		_game.level_won.connect(_on_level_won)
		_game.sound_toggled.connect(_set_sound)
		_game.vibration_toggled.connect(_set_vibration)
		_game.aim_guide_toggled.connect(_set_aim_guide)
		_game.stat_counted.connect(_count_stat)
		add_child(_game)
	_level_index = index
	_game.start(catalog.levels[index], index + 1, index + 1 < catalog.levels.size())
	if brief and story != null:
		_show_briefing(index)
	_reveal()


func _show_briefing(index: int) -> void:
	var def: LevelDefinition = catalog.levels[index]
	var chapter := story.chapter_index(index)
	var chapter_name := "Chapter %d  ·  %s" % [chapter + 1, story.chapters[chapter].title] if chapter >= 0 else ""
	_briefing_layer = CanvasLayer.new()
	_briefing_layer.layer = 50
	add_child(_briefing_layer)
	_briefing = BriefingScreen.new(def, index + 1, chapter_name, story.briefing(index, def.id), narrator, audio)
	_briefing.theme = UiKit.make_theme()
	_briefing.begin_pressed.connect(func() -> void:
		audio.play("click")
		_close_briefing())
	_briefing.back_pressed.connect(_show_menu)
	_briefing_layer.add_child(_briefing)


func _close_briefing() -> void:
	narrator.stop()
	if _briefing_layer != null:
		_briefing_layer.queue_free()
	_briefing_layer = null
	_briefing = null


func _on_level_won(level_id: String, stars: int, shots_used: int) -> void:
	if progress.record_win(level_id, stars, shots_used):
		save.save_progress(progress)


func _count_stat(level_id: String, key: String) -> void:
	progress.count_stat(level_id, key)
	save.save_progress(progress)


func _set_aim_guide(enabled: bool) -> void:
	progress.aim_guide_enabled = enabled
	save.save_progress(progress)


func _set_sound(enabled: bool) -> void:
	progress.sound_enabled = enabled
	audio.enabled = enabled
	save.save_progress(progress)


func _set_vibration(enabled: bool) -> void:
	progress.vibration_enabled = enabled
	save.save_progress(progress)


func _clear_screens() -> void:
	get_tree().paused = false
	_close_briefing()
	for screen: Node in [_menu, _game]:
		if screen != null:
			remove_child(screen)
			screen.queue_free()
	_menu = null
	_game = null
	_settings = null
