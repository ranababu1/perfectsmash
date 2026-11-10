extends Node
## App root: owns persistence, audio and the level catalogs; boots into the Helix tactical
## mission (the new game). The legacy menu/levels remain reachable only through their old code
## paths, for regression reference.
## Handles Android back and app backgrounding (auto-pause).

const FADE_TIME := 0.22
## Music for missions comes from each mission's audio plan (data/audio.json "missions", driven by
## MissionAudio). Missions without a plan fall back to this cue.
const FALLBACK_CUE := "legacy_bed"

var save := SaveService.new()
var progress: ProgressData
var catalog: LevelCatalog
var chapters: ChapterCatalog
var audio_catalog: AudioCatalog
var audio: AudioService
var music: MusicDirector
var ambience: MusicDirector
var _menu: MenuScreen
var _game: GameScreen
var _mission: MissionScreen
var _level_index := -1
var _fade: ColorRect


func _ready() -> void:
	process_mode = Node.PROCESS_MODE_ALWAYS
	progress = save.load_progress()
	audio_catalog = AudioCatalog.load_from_file()
	if not audio_catalog.is_valid():
		push_error("Audio catalog invalid: %s" % ", ".join(audio_catalog.errors))
	audio = AudioService.new()
	audio.catalog = audio_catalog
	audio.enabled = progress.sound_enabled
	add_child(audio)
	music = MusicDirector.new()
	music.catalog = audio_catalog
	music.bus = "Music"
	music.enabled = progress.sound_enabled and progress.music_enabled
	add_child(music)
	ambience = MusicDirector.new()
	ambience.name = "Ambience"
	ambience.catalog = audio_catalog
	ambience.cue_source = "ambience"
	ambience.bus = "Ambience"
	ambience.enabled = progress.sound_enabled
	add_child(ambience)
	catalog = LevelCatalog.load_from_file()
	if not catalog.is_valid():
		push_error("Level catalog invalid: %s" % ", ".join(catalog.errors))
		var message := UiKit.label("Level data failed to load.\n" + "\n".join(catalog.errors.slice(0, 5)), 22)
		message.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
		add_child(message)
		return
	chapters = ChapterCatalog.load_from_file()
	if not chapters.is_valid():
		# Chapters only drive presentation, so the game stays playable with default scenery.
		push_error("Chapter catalog invalid: %s" % ", ".join(chapters.errors))
	_add_fade_layer()
	_show_mission()


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


func _exit_tree() -> void:
	MissionView.release_cached_set()


func _notification(what: int) -> void:
	match what:
		NOTIFICATION_WM_GO_BACK_REQUEST:
			_handle_back()
		NOTIFICATION_APPLICATION_PAUSED, NOTIFICATION_APPLICATION_FOCUS_OUT:
			if _game != null:
				_game.pause()
			if _mission != null:
				_mission.pause()


func _unhandled_input(event: InputEvent) -> void:
	if event.is_action_pressed("ui_cancel"):
		_handle_back()
		get_viewport().set_input_as_handled()


func _handle_back() -> void:
	if _mission != null:
		_mission.handle_back()
	elif _game != null:
		_game.handle_back()
	elif OS.get_name() == "Android":
		get_tree().quit()


func _show_mission() -> void:
	_clear_screens()
	_mission = MissionScreen.new(audio, progress, save)
	_mission.music = music
	_mission.ambience = ambience
	_mission.restart_requested.connect(_show_mission)
	add_child(_mission)
	_reveal()


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
	var chapter := chapters.chapter_for_level(index + 1) if chapters.is_valid() else null
	var theme := ChapterTheme.for_key(chapter.theme) if chapter != null else ChapterTheme.new()
	var caption := chapter_caption(chapter)
	_game.start(catalog.levels[index], index + 1, index + 1 < catalog.levels.size(), theme, caption)
	_reveal()


## e.g. "CHAPTER I  ·  HELIX SYSTEMS  ·  2089"
static func chapter_caption(chapter: ChapterCatalog.Chapter) -> String:
	if chapter == null:
		return ""
	const NUMERALS := ["", "I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X"]
	var numeral: String = NUMERALS[chapter.number] if chapter.number < NUMERALS.size() else str(chapter.number)
	return "CHAPTER %s  ·  %s  ·  %d" % [numeral, chapter.organization.to_upper(), chapter.year]


func _on_level_won(level_id: String, stars: int, shots_used: int) -> void:
	if progress.record_win(level_id, stars, shots_used):
		save.save_progress(progress)


func _start_music() -> void:
	music.play_cue(FALLBACK_CUE, 2.5)


## Until the new HUD has its own music control, the sound toggle mutes music too;
## the separate `music_enabled` setting is kept for that future control.
func _set_sound(enabled: bool) -> void:
	progress.sound_enabled = enabled
	audio.enabled = enabled
	music.enabled = enabled and progress.music_enabled
	ambience.enabled = enabled
	save.save_progress(progress)


func _set_vibration(enabled: bool) -> void:
	progress.vibration_enabled = enabled
	save.save_progress(progress)


func _clear_screens() -> void:
	get_tree().paused = false
	for screen: Node in [_menu, _game, _mission]:
		if screen != null:
			remove_child(screen)
			screen.queue_free()
	_menu = null
	_game = null
	_mission = null
