class_name BurstEffect
extends Node2D
## Short, non-physical pop: an expanding ring plus a few fragments. No debris bodies are created.

const DURATION := 0.45
const FRAGMENTS := 6

var color := Palette.TARGET
var max_radius := 48.0
var _age := 0.0


func _init(p_color: Color, p_radius: float) -> void:
	color = p_color
	max_radius = p_radius


func _process(delta: float) -> void:
	_age += delta
	if _age >= DURATION:
		queue_free()
		return
	queue_redraw()


func _draw() -> void:
	var t := _age / DURATION
	var fade := Color(color, 1.0 - t)
	draw_arc(Vector2.ZERO, max_radius * ease(t, 0.4), 0, TAU, 32, fade, 4.0 * (1.0 - t) + 1.0, true)
	for i in FRAGMENTS:
		var dir := Vector2.RIGHT.rotated(TAU * i / FRAGMENTS + 0.3)
		var p := dir * max_radius * 1.2 * ease(t, 0.5)
		draw_rect(Rect2(p - Vector2(4, 4), Vector2(8, 8)), fade)
