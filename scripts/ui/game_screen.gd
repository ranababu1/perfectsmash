class_name GameScreen
extends Node2D
## Hosts one level: backdrop, physics session, aiming, effects, HUD and pause/result flow.

signal exit_requested
signal next_requested
signal level_won(level_id: String, stars: int, shots_used: int)
signal sound_toggled(enabled: bool)
signal vibration_toggled(enabled: bool)

const RESULT_DELAY := 0.5
const VIBRATE_TARGET_MS := 35
const VIBRATE_WIN_MS := 90

var audio: AudioService
var progress: ProgressData
var session: GameSession
var aim: AimController
var hud: Hud
var _effects: Node2D
var _has_next := false
## Incremented on every (re)start so delayed result popups from a previous attempt are ignored.
var _attempt := 0


func _init(p_audio: AudioService, p_progress: ProgressData) -> void:
	audio = p_audio
	progress = p_progress


func _ready() -> void:
	# The app root keeps running while paused (for back handling); gameplay must not.
	process_mode = Node.PROCESS_MODE_PAUSABLE
	var camera := Camera2D.new()
	camera.position = Vector2(GameConfig.WORLD_WIDTH, GameConfig.WORLD_HEIGHT) / 2.0
	add_child(camera)
	add_child(Backdrop.new())

	session = GameSession.new()
	add_child(session)
	_effects = Node2D.new()
	add_child(_effects)
	aim = AimController.new()
	aim.session = session
	add_child(aim)

	var layer := CanvasLayer.new()
	layer.process_mode = Node.PROCESS_MODE_ALWAYS
	add_child(layer)
	hud = Hud.new()
	hud.theme = UiKit.make_theme()
	layer.add_child(hud)

	aim.launch_requested.connect(func(v: Vector2) -> void: session.launch(v))
	session.launched.connect(_on_launched)
	session.shots_changed.connect(hud.set_shots)
	session.target_destroyed.connect(_on_target_destroyed)
	session.block_shattered.connect(_on_block_shattered)
	session.impact.connect(func(strength: float, _at: Vector2) -> void: audio.play_impact(strength))
	session.finished.connect(_on_finished)
	hud.pause_pressed.connect(pause)
	hud.resume_pressed.connect(resume)
	hud.restart_pressed.connect(restart)
	hud.menu_pressed.connect(_on_menu)
	hud.next_pressed.connect(_on_next)
	hud.sound_toggled.connect(sound_toggled.emit)
	hud.vibration_toggled.connect(vibration_toggled.emit)
	for b in [hud.pause_pressed, hud.resume_pressed, hud.restart_pressed, hud.menu_pressed, hud.next_pressed]:
		b.connect(func() -> void: audio.play("click"))


func start(def: LevelDefinition, number: int, has_next: bool) -> void:
	_has_next = has_next
	_attempt += 1
	get_tree().paused = false
	session.setup(def)
	hud.set_level(def, number)
	aim.cancel()
	_clear_effects()


func restart() -> void:
	_attempt += 1
	get_tree().paused = false
	hud.hide_overlay()
	aim.cancel()
	_clear_effects()
	session.restart()


func pause() -> void:
	if session.rules == null or session.rules.is_finished() or hud.has_overlay():
		return
	aim.cancel()
	get_tree().paused = true
	hud.show_pause(progress.sound_enabled, progress.vibration_enabled)


func resume() -> void:
	get_tree().paused = false
	hud.hide_overlay()


## Back button / Escape: close an open pause menu, otherwise open it.
func handle_back() -> void:
	if get_tree().paused:
		resume()
	elif not hud.has_overlay():
		pause()
	else:
		_on_menu()


func _on_launched(_velocity: Vector2) -> void:
	audio.play("launch")
	hud.fade_hint()


func _on_target_destroyed(at: Vector2) -> void:
	audio.play("pop")
	_vibrate(VIBRATE_TARGET_MS)
	_spawn_burst.call_deferred(at, Palette.TARGET, 56.0)


func _on_block_shattered(at: Vector2) -> void:
	audio.play("shatter")
	_spawn_burst.call_deferred(at, Palette.GLASS_EDGE, 44.0)


func _on_finished(won: bool, stars: int, shots_used: int) -> void:
	var attempt := _attempt
	if won:
		level_won.emit(session.definition.id, stars, shots_used)
	await get_tree().create_timer(RESULT_DELAY).timeout
	if attempt != _attempt or not is_inside_tree():
		return
	audio.play("win" if won else "lose")
	if won:
		_vibrate(VIBRATE_WIN_MS)
	hud.show_result(won, stars, shots_used, _has_next)


func _on_menu() -> void:
	get_tree().paused = false
	exit_requested.emit()


func _on_next() -> void:
	get_tree().paused = false
	next_requested.emit()


func _spawn_burst(at: Vector2, color: Color, radius: float) -> void:
	var burst := BurstEffect.new(color, radius)
	burst.position = at
	_effects.add_child(burst)


func _clear_effects() -> void:
	for child in _effects.get_children():
		child.queue_free()


func _vibrate(ms: int) -> void:
	if progress.vibration_enabled:
		Input.vibrate_handheld(ms)

