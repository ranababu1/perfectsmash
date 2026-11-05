class_name GameScreen
extends Node2D
## Hosts one level: backdrop, physics session, aiming, effects, HUD and pause/result flow.

signal exit_requested
signal next_requested
signal level_won(level_id: String, stars: int, shots_used: int)
signal sound_toggled(enabled: bool)
signal vibration_toggled(enabled: bool)
signal aim_guide_toggled(enabled: bool)
## A play-test counter changed for the current level (key is one of ProgressData.STAT_KEYS).
signal stat_counted(level_id: String, key: String)

const RESULT_DELAY := 0.5
const VIBRATE_TARGET_MS := 35
const VIBRATE_WIN_MS := 90
const VIBRATE_BLAST_MS := 60
const SHAKE_TIME := 0.22
const SHAKE_PIXELS := 6.0

var audio: AudioService
var progress: ProgressData
## Optional: when set, results show the mission debrief / failure line.
var story: StoryCatalog
var narrator: Narrator
var session: GameSession
var aim: AimController
var hud: Hud
var _effects: Node2D
var _camera: Camera2D
var _shake := 0.0
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
	_camera = camera
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
	session.exploded.connect(_on_exploded)
	session.ally_lost.connect(_on_ally_lost)
	session.impact.connect(func(strength: float, _at: Vector2) -> void: audio.play_impact(strength))
	session.finished.connect(_on_finished)
	hud.pause_pressed.connect(pause)
	hud.resume_pressed.connect(resume)
	hud.restart_pressed.connect(restart)
	hud.menu_pressed.connect(_on_menu)
	hud.next_pressed.connect(_on_next)
	hud.sound_toggled.connect(sound_toggled.emit)
	hud.vibration_toggled.connect(vibration_toggled.emit)
	hud.aim_guide_toggled.connect(_on_aim_guide_toggled)
	session.shot_resolved.connect(_on_shot_resolved)
	hud.star_revealed.connect(func(_i: int) -> void: audio.play("click"))
	for b in [hud.pause_pressed, hud.resume_pressed, hud.restart_pressed, hud.menu_pressed, hud.next_pressed]:
		b.connect(func() -> void: audio.play("click"))


func start(def: LevelDefinition, number: int, has_next: bool) -> void:
	_has_next = has_next
	_attempt += 1
	get_tree().paused = false
	session.setup(def)
	hud.set_level(def, number)
	aim.cancel()
	aim.show_guide = progress.aim_guide_enabled
	_clear_effects()
	stat_counted.emit(def.id, "attempts")


func restart() -> void:
	if narrator != null:
		narrator.stop()
	_attempt += 1
	get_tree().paused = false
	hud.hide_overlay()
	aim.cancel()
	_clear_effects()
	session.restart()
	stat_counted.emit(session.definition.id, "attempts")


func pause() -> void:
	if session.rules == null or session.rules.is_finished() or hud.has_overlay():
		return
	aim.cancel()
	get_tree().paused = true
	hud.show_pause(progress.sound_enabled, progress.vibration_enabled, progress.aim_guide_enabled)


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


func _on_exploded(at: Vector2) -> void:
	audio.play("boom")
	_vibrate(VIBRATE_BLAST_MS)
	_spawn_explosion.call_deferred(at)
	_shake = SHAKE_TIME


func _spawn_explosion(at: Vector2) -> void:
	var effect := ExplosionEffect.new()
	effect.position = at
	_effects.add_child(effect)


## Brief, small camera shake after explosions (purely visual; physics is unaffected).
func _process(delta: float) -> void:
	if _camera == null:
		return
	if _shake > 0.0:
		_shake = maxf(_shake - delta, 0.0)
		var strength := SHAKE_PIXELS * (_shake / SHAKE_TIME)
		_camera.offset = Vector2(sin(_shake * 91.0), cos(_shake * 77.0)) * strength
	elif _camera.offset != Vector2.ZERO:
		_camera.offset = Vector2.ZERO


func _on_ally_lost(at: Vector2) -> void:
	audio.play("lose", -6.0, 1.4)
	_spawn_burst.call_deferred(at, Palette.ALLY, 50.0)


func _on_block_shattered(at: Vector2) -> void:
	audio.play("shatter")
	_spawn_burst.call_deferred(at, Palette.GLASS_EDGE, 44.0)


func _on_aim_guide_toggled(enabled: bool) -> void:
	aim.show_guide = enabled
	aim_guide_toggled.emit(enabled)


func _on_shot_resolved(timed_out: bool) -> void:
	if timed_out:
		stat_counted.emit(session.definition.id, "timeouts")


func _on_finished(won: bool, stars: int, shots_used: int) -> void:
	var attempt := _attempt
	stat_counted.emit(session.definition.id, "wins" if won else "losses")
	if won:
		level_won.emit(session.definition.id, stars, shots_used)
	await get_tree().create_timer(RESULT_DELAY).timeout
	if attempt != _attempt or not is_inside_tree():
		return
	audio.play("win" if won else "lose")
	if won:
		_vibrate(VIBRATE_WIN_MS)
	var lines: Array[Dictionary] = []
	var reason := ""
	if story != null:
		var id := session.definition.id
		if won:
			lines = story.debrief(id)
		else:
			var kind := "fail"
			reason = "Out of shots."
			if session.allies_lost > 0:
				kind = "fail_ally"
				reason = "A blue drone was lost."
			elif session.cargo_lost > 0:
				kind = "fail_cargo"
				reason = "The supply crate was lost."
			var line := story.fail_line(kind, progress.stat(id, "losses") + _attempt)
			if not line.is_empty():
				lines.append(line)
	hud.show_result(won, stars, shots_used, _has_next, session.definition.par, lines, narrator, audio, reason)


func _on_menu() -> void:
	get_tree().paused = false
	if narrator != null:
		narrator.stop()
	exit_requested.emit()


func _on_next() -> void:
	get_tree().paused = false
	if narrator != null:
		narrator.stop()
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

