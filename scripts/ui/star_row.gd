class_name StarRow
extends Control
## Draws filled/empty star medals as vector shapes (no font glyph dependency).
## `reveal()` pops earned stars in one at a time for the result screen.

const REVEAL_STEP := 0.18

var earned := 0
var star_size := 20.0
## Per-star display scale, animated by reveal(); 1.0 = fully shown.
var _scales: Array[float] = []


func _init(p_earned: int = 0, p_size: float = 20.0) -> void:
	earned = p_earned
	star_size = p_size
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	custom_minimum_size = Vector2(star_size * 2.4 * ScoreRules.MAX_STARS, star_size * 2.2)
	for i in ScoreRules.MAX_STARS:
		_scales.append(1.0)


func set_earned(value: int) -> void:
	earned = value
	queue_redraw()


func reveal(on_star: Callable = Callable()) -> void:
	for i in earned:
		_scales[i] = 0.0
	var tween := create_tween()
	for i in earned:
		tween.tween_interval(REVEAL_STEP if i > 0 else 0.15)
		if on_star.is_valid():
			tween.tween_callback(on_star.bind(i))
		tween.tween_method(_set_scale.bind(i), 0.0, 1.0, 0.32).set_trans(Tween.TRANS_BACK).set_ease(Tween.EASE_OUT)


func _set_scale(value: float, index: int) -> void:
	_scales[index] = value
	queue_redraw()


func _draw() -> void:
	var spacing := star_size * 2.4
	var start_x := (size.x - spacing * ScoreRules.MAX_STARS) / 2.0 + spacing / 2.0
	for i in ScoreRules.MAX_STARS:
		var center := Vector2(start_x + i * spacing, size.y / 2.0)
		draw_colored_polygon(star_points(center, star_size), Color(1, 1, 1, 0.07))
		if i < earned and _scales[i] > 0.01:
			draw_colored_polygon(star_points(center, star_size * _scales[i]), Palette.ACCENT)


static func star_points(center: Vector2, radius: float) -> PackedVector2Array:
	var points := PackedVector2Array()
	for i in 10:
		var r := radius if i % 2 == 0 else radius * 0.47
		points.append(center + Vector2.UP.rotated(TAU * i / 10.0) * r)
	return points
