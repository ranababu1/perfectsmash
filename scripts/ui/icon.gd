class_name Icon
extends Control
## Small vector icons drawn with primitives, so the UI needs no image assets or icon font.
## Drawn in a 24x24 design grid and scaled to the control's size.

var kind := ""
var color := Palette.TEXT
## Drawn size; the icon stays this size and centered even when the control is stretched.
var icon_size := 28.0


func _init(p_kind: String = "", p_size: float = 28.0, p_color: Color = Palette.TEXT) -> void:
	kind = p_kind
	color = p_color
	icon_size = p_size
	custom_minimum_size = Vector2(p_size, p_size)
	mouse_filter = Control.MOUSE_FILTER_IGNORE


func set_kind(value: String) -> void:
	kind = value
	queue_redraw()


func set_color(value: Color) -> void:
	color = value
	queue_redraw()


func _draw() -> void:
	var s := minf(icon_size, minf(size.x, size.y)) / 24.0
	var o := (size - Vector2(24, 24) * s) / 2.0
	var p := func(x: float, y: float) -> Vector2: return o + Vector2(x, y) * s
	var w := 2.0 * s
	match kind:
		"pause":
			draw_line(p.call(8.5, 6), p.call(8.5, 18), color, 2.6 * s, true)
			draw_line(p.call(15.5, 6), p.call(15.5, 18), color, 2.6 * s, true)
		"play", "next":
			draw_colored_polygon(PackedVector2Array([p.call(8, 5), p.call(19, 12), p.call(8, 19)]), color)
			if kind == "next":
				draw_rect(Rect2(p.call(19, 5), Vector2(2.5, 14) * s), color)
		"restart":
			draw_arc(p.call(12, 12), 7.0 * s, deg_to_rad(-60), deg_to_rad(230), 24, color, w, true)
			var tip: Vector2 = p.call(12, 12) + Vector2.from_angle(deg_to_rad(-60)) * 7.0 * s
			draw_colored_polygon(PackedVector2Array([tip + Vector2(-4.5, -2.5) * s, tip + Vector2(2.5, -4.0) * s, tip + Vector2(1.0, 3.5) * s]), color)
		"levels":
			for row in 2:
				for col in 2:
					var box := StyleBoxFlat.new()
					box.bg_color = color
					box.set_corner_radius_all(int(2 * s))
					draw_style_box(box, Rect2(p.call(5 + col * 8, 5 + row * 8), Vector2(6, 6) * s))
		"lock":
			draw_arc(p.call(12, 10), 4.0 * s, PI, TAU, 16, color, w, true)
			draw_line(p.call(8, 10), p.call(8, 12), color, w)
			draw_line(p.call(16, 10), p.call(16, 12), color, w)
			var body := StyleBoxFlat.new()
			body.bg_color = color
			body.set_corner_radius_all(int(2 * s))
			draw_style_box(body, Rect2(p.call(6, 11), Vector2(12, 9) * s))
		"sound", "sound_off":
			draw_colored_polygon(PackedVector2Array([p.call(4, 9), p.call(8, 9), p.call(13, 5), p.call(13, 19), p.call(8, 15), p.call(4, 15)]), color)
			if kind == "sound":
				draw_arc(p.call(13, 12), 4.0 * s, -0.9, 0.9, 12, color, w * 0.9, true)
				draw_arc(p.call(13, 12), 7.5 * s, -0.9, 0.9, 16, color, w * 0.9, true)
			else:
				draw_line(p.call(16, 9), p.call(21, 15), color, w, true)
				draw_line(p.call(21, 9), p.call(16, 15), color, w, true)
		"vibrate", "vibrate_off":
			var phone := StyleBoxFlat.new()
			phone.draw_center = false
			phone.border_color = color
			phone.set_border_width_all(int(maxf(1.0, w)))
			phone.set_corner_radius_all(int(2.5 * s))
			draw_style_box(phone, Rect2(p.call(8, 4), Vector2(8, 16) * s))
			if kind == "vibrate":
				for side: float in [-1.0, 1.0]:
					var x := 12.0 + side * 7.0
					draw_polyline(PackedVector2Array([p.call(x, 8), p.call(x + side * 1.5, 10), p.call(x, 12), p.call(x + side * 1.5, 14), p.call(x, 16)]), color, w * 0.8, true)
			else:
				draw_line(p.call(4, 4), p.call(20, 20), color, w, true)
		"star":
			draw_colored_polygon(_star_points(p.call(12, 12.5), 9.0 * s), color)


## Five-pointed star outline (was StarRow.star_points, retired with the legacy HUD).
static func _star_points(center: Vector2, radius: float) -> PackedVector2Array:
	var points := PackedVector2Array()
	for i in 10:
		var r := radius if i % 2 == 0 else radius * 0.47
		points.append(center + Vector2.UP.rotated(TAU * i / 10.0) * r)
	return points
