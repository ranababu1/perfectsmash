class_name StarRow
extends Control
## Draws filled/empty star medals as vector shapes (no font glyph dependency).

var earned := 0
var star_size := 20.0


func _init(p_earned: int = 0, p_size: float = 20.0) -> void:
	earned = p_earned
	star_size = p_size
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	custom_minimum_size = Vector2(star_size * 2.4 * ScoreRules.MAX_STARS, star_size * 2.2)


func set_earned(value: int) -> void:
	earned = value
	queue_redraw()


func _draw() -> void:
	var spacing := star_size * 2.4
	var start_x := (size.x - spacing * ScoreRules.MAX_STARS) / 2.0 + spacing / 2.0
	for i in ScoreRules.MAX_STARS:
		var points := _star(Vector2(start_x + i * spacing, size.y / 2.0), star_size)
		if i < earned:
			draw_colored_polygon(points, Palette.ACCENT)
		else:
			points.append(points[0])
			draw_polyline(points, Color(Palette.TEXT_DIM, 0.6), 2.0, true)


static func _star(center: Vector2, radius: float) -> PackedVector2Array:
	var points := PackedVector2Array()
	for i in 10:
		var r := radius if i % 2 == 0 else radius * 0.45
		points.append(center + Vector2.UP.rotated(TAU * i / 10.0) * r)
	return points
