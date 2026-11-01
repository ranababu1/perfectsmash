class_name AimController
extends Node2D
## Drag-back slingshot aiming. Press anywhere in the play area, pull away from the target
## direction and release. Uses _unhandled_input so touches on UI controls never fire a shot.
## The pull is measured in screen space (the camera never zooms), so camera updates between
## press and release cannot distort it.

signal launch_requested(velocity: Vector2)

const BAND_COLOR := Color(1, 1, 1, 0.45)
const BAND_WIDTH := 3.0
const DOT_RADIUS := 5.0
## The drawn ball moves this fraction of the pull, so the visual stays near the launcher.
const BALL_PULL_FACTOR := 0.35

var session: GameSession
var _dragging := false
var _drag_start := Vector2.ZERO
var _drag_current := Vector2.ZERO


func cancel() -> void:
	_dragging = false
	queue_redraw()


func is_dragging() -> bool:
	return _dragging


## Launch velocity for a pull vector (drag start minus current point), in canvas units.
static func velocity_for_pull(pull: Vector2) -> Vector2:
	var clamped := pull.limit_length(GameConfig.MAX_DRAG_DISTANCE)
	return clamped / GameConfig.MAX_DRAG_DISTANCE * GameConfig.MAX_LAUNCH_SPEED


func _pull() -> Vector2:
	return _drag_start - _drag_current


func _unhandled_input(event: InputEvent) -> void:
	if session == null or not session.can_launch():
		if _dragging:
			cancel()
		return
	if event is InputEventMouseButton and event.button_index == MOUSE_BUTTON_LEFT:
		if event.pressed:
			_dragging = true
			_drag_start = event.position
			_drag_current = _drag_start
		elif _dragging:
			_drag_current = event.position
			_dragging = false
			if _pull().length() >= GameConfig.MIN_DRAG_DISTANCE:
				launch_requested.emit(velocity_for_pull(_pull()))
		get_viewport().set_input_as_handled()
		queue_redraw()
	elif event is InputEventMouseMotion and _dragging:
		_drag_current = event.position
		get_viewport().set_input_as_handled()
		queue_redraw()


func _process(_delta: float) -> void:
	# Redraw when the session becomes ready again so the loaded ball appears.
	queue_redraw()


func _draw() -> void:
	if session == null or session.definition == null or not session.can_launch():
		return
	var origin := session.launcher_position()
	var pull := _pull().limit_length(GameConfig.MAX_DRAG_DISTANCE) if _dragging else Vector2.ZERO
	var ball := origin - pull * BALL_PULL_FACTOR
	var fork_left := origin + Vector2(-14, 6)
	var fork_right := origin + Vector2(14, 6)
	var aiming := pull.length() >= GameConfig.MIN_DRAG_DISTANCE
	if aiming:
		draw_line(fork_left, ball, BAND_COLOR, BAND_WIDTH, true)
		_draw_preview(origin, velocity_for_pull(pull))
	ProjectileBody.draw_ball(self, ball)
	if aiming:
		draw_line(fork_right, ball, BAND_COLOR, BAND_WIDTH, true)
		_draw_power(ball, pull.length() / GameConfig.MAX_DRAG_DISTANCE)
	elif not _dragging:
		# Idle hint ring: a slow, faint pulse says "grab here" without any text.
		var t := fmod(Time.get_ticks_msec() / 1400.0, 1.0)
		draw_arc(ball, GameConfig.PROJECTILE_RADIUS + 4.0 + t * 14.0, 0, TAU, 40, Color(Palette.ACCENT, 0.35 * (1.0 - t)), 2.0, true)


## Short partial arc: shows the launch direction and early curve without solving the puzzle.
func _draw_preview(origin: Vector2, velocity: Vector2) -> void:
	var gravity := float(ProjectSettings.get_setting("physics/2d/default_gravity", 980.0))
	for i in range(1, GameConfig.PREVIEW_DOTS + 1):
		var t := GameConfig.PREVIEW_DURATION * i / GameConfig.PREVIEW_DOTS
		var p := origin + velocity * t + Vector2(0, 0.5 * gravity * t * t)
		var fade := 1.0 - float(i) / (GameConfig.PREVIEW_DOTS + 1)
		draw_circle(p, DOT_RADIUS * (0.55 + 0.45 * fade), Color(Palette.AIM, fade * Palette.AIM.a), true, -1.0, true)


## Thin power arc hugging the ball; turns fully accent-colored at max pull.
func _draw_power(center: Vector2, ratio: float) -> void:
	var r := GameConfig.PROJECTILE_RADIUS + 9.0
	draw_arc(center, r, 0, TAU, 48, Color(1, 1, 1, 0.12), 3.0, true)
	draw_arc(center, r, -PI / 2.0, -PI / 2.0 + TAU * ratio, 48, Color(Palette.ACCENT, 0.6 + 0.4 * ratio), 3.0, true)
