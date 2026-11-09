extends Node
## App root: owns persistence, audio and the level catalog; switches between menu and game.
## Handles Android back and app backgrounding (auto-pause).

const FADE_TIME := 0.22

var save := SaveService.new()
var progress: ProgressData
var catalog: LevelCatalog
var audio: AudioService
var music: MusicDirector
var _menu: MenuScreen
var _game: GameScreen
var _level_index := -1
var _fade: ColorRect


func _ready() -> void:
	process_mode = Node.PROCESS_MODE_ALWAYS
	progress = save.load_progress()
	audio = AudioService.new()
	audio.enabled = progress.sound_enabled
	add_child(audio)
	music = MusicDirector.new()
	music.enabled = progress.music_enabled
	add_child(music)
	catalog = LevelCatalog.load_from_file()
	if not catalog.is_valid():
		push_error("Level catalog invalid: %s" % ", ".join(catalog.errors))
		var message := UiKit.label("Level data failed to load.\n" + "\n".join(catalog.errors.slice(0, 5)), 22)
		message.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
		add_child(message)
		return
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
			if _game != null:
				_game.pause()


func _unhandled_input(event: InputEvent) -> void:
	if event.is_action_pressed("ui_cancel"):
		_handle_back()
		get_viewport().set_input_as_handled()


func _handle_back() -> void:
	if _game != null:
		_game.handle_back()
	elif OS.get_name() == "Android":
		get_tree().quit()


func _show_menu() -> void:
	_clear_screens()
	_menu = MenuScreen.new(catalog, progress)
	_menu.theme = UiKit.make_theme()
	_menu.level_selected.connect(_start_level)
	_menu.sound_toggled.connect(_set_sound)
	_menu.vibration_toggled.connect(_set_vibration)
	add_child(_menu)
	_reveal()


func _start_level(index: int) -> void:
	audio.play("click")
	if _game == null:
		_clear_screens()
		_game = GameScreen.new(audio, progress)
		_game.exit_requested.connect(_show_menu)
		_game.next_requested.connect(func() -> void: _start_level(_level_index + 1))
		_game.level_won.connect(_on_level_won)
		_game.sound_toggled.connect(_set_sound)
		_game.vibration_toggled.connect(_set_vibration)
		add_child(_game)
	_level_index = index
	_game.start(catalog.levels[index], index + 1, index + 1 < catalog.levels.size())
	_reveal()


func _on_level_won(level_id: String, stars: int, shots_used: int) -> void:
	if progress.record_win(level_id, stars, shots_used):
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
	for screen: Node in [_menu, _game]:
		if screen != null:
			remove_child(screen)
			screen.queue_free()
	_menu = null
	_game = null
