extends Node
## App root: owns persistence, audio and the catalogs; boots into the campaign menu
## (CampaignScreen) and routes between it, missions, settings, upgrades, the Story Archive and
## story cinematics. (The retired slingshot levels were removed from the game on 2026-11-11.)
## Handles Android back and app backgrounding (auto-pause).

const FADE_TIME := 0.22
## Music for missions comes from each mission's audio plan (data/audio.json "missions", driven by
## MissionAudio). Missions without a plan fall back to this cue.
const FALLBACK_CUE := "helix_gameplay"
## Main menu, chapter/mission select, upgrades and Story Archive.
const MENU_CUE := "menu"

var save := SaveService.new()
var progress: ProgressData
var chapters: ChapterCatalog
var missions: MissionCatalog
## Mission id to start in instead of the main menu (tests and capture tools set it before
## adding the node). Empty = boot into the campaign menu.
var boot_mission := ""
## Story cinematics play automatically (the opening on first launch, a chapter's introduction
## before its first mission, its ending once the chapter is complete). Tests switch it off.
var cinematics_enabled := true
var cinematics: CinematicCatalog
## Narration per cinematic (data/narration.json: voice lines, timings, music beds), applied onto `cinematics`.
var narration: NarrationCatalog
var _upgrades: UpgradesScreen
var _archive: StoryArchive
var _cinematic: CinematicPlayer
var audio_catalog: AudioCatalog
var audio: AudioService
var music: MusicDirector
var ambience: MusicDirector
var _mission: MissionScreen
var _campaign: CampaignScreen
var _settings: SettingsScreen
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
	chapters = ChapterCatalog.load_from_file()
	if not chapters.is_valid():
		# Chapters only drive presentation, so the game stays playable with default scenery.
		push_error("Chapter catalog invalid: %s" % ", ".join(chapters.errors))
	missions = MissionCatalog.from_chapters(chapters)
	cinematics = CinematicCatalog.load_from_file()
	if not cinematics.is_valid():
		push_error("Cinematic catalog invalid: %s" % ", ".join(cinematics.errors))
	narration = NarrationCatalog.load_from_file()
	if not narration.is_valid():
		push_error("Narration catalog invalid: %s" % ", ".join(narration.errors))
	var unknown := narration.unknown_keys(cinematics)
	if not unknown.is_empty():
		push_error("Narration for unknown or mismatched sequences: %s" % ", ".join(unknown))
	narration.apply_to(cinematics)
	_apply_narration_volume()
	_add_fade_layer()
	if not boot_mission.is_empty():
		_show_mission(boot_mission)
	elif _should_play(chapters.opening_sequence if chapters != null else "opening"):
		_show_cinematic(chapters.opening_sequence, _show_campaign)
	else:
		_show_campaign()


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
			if _mission != null:
				_mission.pause()


func _unhandled_input(event: InputEvent) -> void:
	if event.is_action_pressed("ui_cancel"):
		_handle_back()
		get_viewport().set_input_as_handled()


func _handle_back() -> void:
	if _cinematic != null:
		_cinematic.skip()
	elif _upgrades != null or _archive != null:
		_show_campaign()
	elif _settings != null:
		_show_campaign()
	elif _campaign != null:
		if not _campaign.go_back() and OS.get_name() == "Android":
			get_tree().quit()
	elif _mission != null:
		_mission.handle_back()
	elif OS.get_name() == "Android":
		get_tree().quit()


## Starts a campaign mission by id (MissionCatalog slot). An empty or unknown id falls back to
## MissionScreen's default (the Helix reference mission).
func _show_mission(mission_id: String = "") -> void:
	_clear_screens()
	var entry := missions.slot(mission_id) if missions != null else null
	var path := entry.path if entry != null and entry.authored else MissionScreen.DEFAULT_MISSION
	_mission = MissionScreen.new(audio, progress, save, path)
	_mission.music = music
	_mission.ambience = ambience
	_mission.restart_requested.connect(_show_mission.bind(mission_id))
	_mission.next_requested.connect(_show_next_mission.bind(mission_id))
	_mission.exit_requested.connect(_exit_mission.bind(mission_id))
	# Pause → Main Menu: the abandoned attempt records nothing; saved progress is untouched.
	_mission.menu_requested.connect(_show_campaign)
	add_child(_mission)
	_reveal()


func _show_next_mission(after_id: String) -> void:
	var outro := _chapter_outro_due(after_id)
	if not outro.is_empty():
		_show_cinematic(outro, _show_next_mission.bind(after_id))
		return
	var next := missions.next_authored_id(after_id) if missions != null else ""
	if not next.is_empty() and _chapter_of(next) != _chapter_of(after_id) and missions.is_unlocked(next, progress):
		_select_mission(next)
		return
	if next.is_empty() or not missions.is_unlocked(next, progress):
		_show_campaign(_chapter_of(after_id))
	else:
		_show_mission(next)


## Results → Missions: a just-completed chapter plays its ending first.
func _exit_mission(mission_id: String) -> void:
	var outro := _chapter_outro_due(mission_id)
	if outro.is_empty():
		_show_campaign(_chapter_of(mission_id))
	else:
		_show_cinematic(outro, _show_campaign.bind(_chapter_of(mission_id)))


func _chapter_of(mission_id: String) -> int:
	var entry := missions.slot(mission_id) if missions != null else null
	return entry.chapter.number if entry != null else 0


## Main menu / chapter select / mission select. `chapter` > 0 opens that chapter's mission list.
func _show_campaign(chapter: int = 0) -> void:
	_clear_screens()
	_campaign = CampaignScreen.new(missions, chapters, progress)
	_campaign.library = MissionView.assets()
	_campaign.audio = audio
	_campaign.mission_selected.connect(_select_mission)
	_campaign.settings_requested.connect(_show_settings)
	_campaign.upgrades_requested.connect(_show_upgrades)
	_campaign.archive_requested.connect(_show_archive)
	add_child(_campaign)
	if chapter > 0:
		_campaign.show_missions(chapter)
	_play_menu_music()
	_reveal()


func _play_menu_music() -> void:
	if music != null:
		music.play_cue(MENU_CUE, 1.5)
	if ambience != null:
		ambience.stop(1.0)


## A mission chosen in the menu: its chapter's introduction plays first the first time.
func _select_mission(mission_id: String) -> void:
	var entry := missions.slot(mission_id) if missions != null else null
	var intro := entry.chapter.intro_sequence if entry != null else ""
	if _should_play(intro):
		_show_cinematic(intro, _show_mission.bind(mission_id))
	else:
		_show_mission(mission_id)


## True when automatic cinematics are on and `sequence_id` exists and has not been seen.
func _should_play(sequence_id: String) -> bool:
	return cinematics_enabled and cinematics != null and not sequence_id.is_empty() \
			and cinematics.has_sequence(sequence_id) and not progress.has_seen_sequence(sequence_id)


## Plays a story sequence full screen, marks it seen (unlocking it in the Story Archive) and
## calls `then` when it ends or is skipped.
func _show_cinematic(sequence_id: String, then: Callable) -> void:
	_clear_screens()
	_cinematic = CinematicPlayer.new()
	_cinematic.music = music
	# Volume 0 counts as narration off: no line plays and the music is not ducked (the slides keep
	# their narrated timing, so subtitles still match the music).
	_cinematic.narration_enabled = progress.sound_enabled and progress.voice_enabled and progress.narration_volume > 0.0
	if narration != null:
		_cinematic.narration_bus = narration.bus
		_cinematic.duck_db = narration.duck_db
		_cinematic.duck_attack = narration.duck_attack
		_cinematic.duck_hold = narration.duck_hold
		_cinematic.duck_release = narration.duck_release
	if ambience != null:
		ambience.stop(0.6)
	add_child(_cinematic)
	_cinematic.finished.connect(func(id: String, _skipped: bool) -> void:
		if progress.mark_sequence_seen(id):
			save.save_progress(progress)
		then.call(), CONNECT_ONE_SHOT | CONNECT_DEFERRED)
	if not _cinematic.play_id(sequence_id, cinematics):
		_cinematic.finished.emit(sequence_id, true)
	_reveal()


## The chapter's ending (the finale for the last chapter) once all its missions are complete.
func _chapter_outro_due(mission_id: String) -> String:
	var entry := missions.slot(mission_id) if missions != null else null
	if entry == null or not progress.is_mission_completed(mission_id):
		return ""
	for s in missions.chapter_slots(entry.chapter.number):
		if not progress.is_mission_completed(s.id):
			return ""
	var outro := entry.chapter.outro_sequence
	return outro if _should_play(outro) else ""


func _show_upgrades() -> void:
	_clear_screens()
	var unlocked := _highest_unlocked_chapter()
	_upgrades = UpgradesScreen.new(WeaponCatalog.load_from_file(), progress, unlocked)
	_upgrades.library = MissionView.assets()
	_upgrades.audio = audio
	_upgrades.purchased.connect(func(_w: String, _a: String) -> void: save.save_progress(progress))
	_upgrades.closed.connect(_show_campaign)
	add_child(_upgrades)
	_reveal()


func _highest_unlocked_chapter() -> int:
	var best := 1
	if missions == null or chapters == null:
		return best
	for chapter in chapters.chapters:
		var first := missions.chapter_slots(chapter.number)
		if not first.is_empty() and missions.is_unlocked(first[0].id, progress):
			best = maxi(best, chapter.number)
	return best


func _show_archive() -> void:
	_clear_screens()
	_archive = StoryArchive.new(cinematics, progress)
	_archive.library = MissionView.assets()
	_archive.play_requested.connect(func(id: String) -> void: _show_cinematic(id, _show_archive))
	_archive.closed.connect(_show_campaign)
	add_child(_archive)
	_play_menu_music()
	_reveal()


func _show_settings() -> void:
	_clear_screens()
	_settings = SettingsScreen.new(progress)
	_settings.library = MissionView.assets()
	_settings.audio = audio
	_settings.sound_toggled.connect(_set_sound)
	_settings.music_toggled.connect(_set_music)
	_settings.vibration_toggled.connect(_set_vibration)
	_settings.narration_volume_changed.connect(_set_narration_volume)
	_settings.back_pressed.connect(_show_campaign)
	add_child(_settings)
	_reveal()


## e.g. "CHAPTER I  ·  HELIX SYSTEMS  ·  2089"
static func chapter_caption(chapter: ChapterCatalog.Chapter) -> String:
	if chapter == null:
		return ""
	const NUMERALS := ["", "I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X"]
	var numeral: String = NUMERALS[chapter.number] if chapter.number < NUMERALS.size() else str(chapter.number)
	return "CHAPTER %s  ·  %s  ·  %d" % [numeral, chapter.organization.to_upper(), chapter.year]


## Until the new HUD has its own music control, the sound toggle mutes music too;
## the separate `music_enabled` setting is kept for that future control.
func _set_sound(enabled: bool) -> void:
	progress.sound_enabled = enabled
	audio.enabled = enabled
	music.enabled = enabled and progress.music_enabled
	ambience.enabled = enabled
	_apply_narration_volume()
	save.save_progress(progress)


func _set_music(enabled: bool) -> void:
	progress.music_enabled = enabled
	music.enabled = progress.sound_enabled and enabled
	save.save_progress(progress)


func _set_narration_volume(volume: float) -> void:
	progress.narration_volume = clampf(volume, 0.0, 1.0)
	_apply_narration_volume()
	save.save_progress(progress)


## Narration volume lives on the Voice bus; Sound off, narration off or volume 0 mutes it.
func _apply_narration_volume() -> void:
	var bus := AudioServer.get_bus_index(narration.bus if narration != null else NarrationCatalog.DEFAULT_BUS)
	if bus < 0:
		return
	var volume := clampf(progress.narration_volume, 0.0, 1.0)
	AudioServer.set_bus_volume_db(bus, linear_to_db(maxf(volume, 0.0001)))
	AudioServer.set_bus_mute(bus, volume <= 0.0 or not progress.sound_enabled or not progress.voice_enabled)


func _set_vibration(enabled: bool) -> void:
	progress.vibration_enabled = enabled
	save.save_progress(progress)


func _clear_screens() -> void:
	get_tree().paused = false
	for screen: Node in [_mission, _campaign, _settings, _upgrades, _archive, _cinematic]:
		if screen != null:
			remove_child(screen)
			screen.queue_free()
	_upgrades = null
	_archive = null
	_cinematic = null
	_mission = null
	_campaign = null
	_settings = null
