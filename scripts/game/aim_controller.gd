class_name AimController
extends Node2D
## Drag-back slingshot aiming. Press anywhere in the play area, pull away from the target
## direction and release. Uses _unhandled_input so touches on UI controls never fire a shot.
## The pull is measured in screen space (the camera never zooms), so camera updates between
## press and release cannot distort it.

signal launch_requested(velocity: Vector2)

const BAND_COLOR := Color(1, 1, 1, 0.5)
const BAND_WIDTH := 4.0
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
	if pull.length() >= GameConfig.MIN_DRAG_DISTANCE:
		draw_line(fork_left, ball, BAND_COLOR, BAND_WIDTH)
		_draw_preview(origin, velocity_for_pull(pull))
	draw_circle(ball, GameConfig.PROJECTILE_RADIUS, Palette.PROJECTILE)
	draw_arc(ball, GameConfig.PROJECTILE_RADIUS - 1.5, 0, TAU, 32, Palette.PROJECTILE_EDGE, 3.0, true)
	if pull.length() >= GameConfig.MIN_DRAG_DISTANCE:
		draw_line(fork_right, ball, BAND_COLOR, BAND_WIDTH)
		_draw_power(origin, pull.length() / GameConfig.MAX_DRAG_DISTANCE)


## Short partial arc: shows the launch direction and early curve without solving the puzzle.
func _draw_preview(origin: Vector2, velocity: Vector2) -> void:
	var gravity := float(ProjectSettings.get_setting("physics/2d/default_gravity", 980.0))
	for i in range(1, GameConfig.PREVIEW_DOTS + 1):
		var t := GameConfig.PREVIEW_DURATION * i / GameConfig.PREVIEW_DOTS
		var p := origin + velocity * t + Vector2(0, 0.5 * gravity * t * t)
		var alpha := 1.0 - float(i) / (GameConfig.PREVIEW_DOTS + 1)
		draw_circle(p, DOT_RADIUS, Color(Palette.AIM, alpha * Palette.AIM.a))


func _draw_power(origin: Vector2, ratio: float) -> void:
	var center := origin + Vector2(0, 60)
	draw_arc(center, 22, -PI / 2.0, -PI / 2.0 + TAU, 32, Color(1, 1, 1, 0.15), 6.0, true)
	draw_arc(center, 22, -PI / 2.0, -PI / 2.0 + TAU * ratio, 32, Palette.ACCENT, 6.0, true)
