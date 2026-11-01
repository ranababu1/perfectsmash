class_name Backdrop
extends Node2D
## Static scenery behind a level: a smooth sky gradient, a faint horizon glow and two layers of
## low-contrast hills. Drawn well beyond the 1280x720 canvas so any aspect ratio is covered.
## Purely visual and deterministic (shapes come from fixed sine sums, not RNG).

const OVERSCAN := 800.0
const TOP := -400.0


func _draw() -> void:
	var rect := Rect2(-OVERSCAN, TOP, GameConfig.WORLD_WIDTH + OVERSCAN * 2.0, GameConfig.GROUND_TOP - TOP)
	paint(self, rect, GameConfig.GROUND_TOP)


## Shared with the menu so both screens sit on the same scenery.
static func paint(canvas: CanvasItem, rect: Rect2, horizon_y: float) -> void:
	_gradient(canvas, rect, Palette.SKY_TOP, Palette.SKY_BOTTOM)
	var glow := Rect2(rect.position.x, horizon_y - 260.0, rect.size.x, 260.0)
	_gradient(canvas, glow, Color(Palette.HORIZON_GLOW, 0.0), Palette.HORIZON_GLOW)
	_hills(canvas, rect, horizon_y, 120.0, 0.004, 1.3, Palette.HILLS_FAR)
	_hills(canvas, rect, horizon_y, 70.0, 0.007, 4.1, Palette.HILLS_NEAR)


static func _gradient(canvas: CanvasItem, rect: Rect2, top: Color, bottom: Color) -> void:
	var points := PackedVector2Array([rect.position, Vector2(rect.end.x, rect.position.y), rect.end, Vector2(rect.position.x, rect.end.y)])
	canvas.draw_polygon(points, PackedColorArray([top, top, bottom, bottom]))


static func _hills(canvas: CanvasItem, rect: Rect2, base_y: float, height: float, frequency: float, phase: float, color: Color) -> void:
	var points := PackedVector2Array()
	var x := rect.position.x
	while x < rect.end.x + 24.0:
		x = minf(x, rect.end.x)
		var wave := 0.55 * sin(x * frequency + phase) + 0.3 * sin(x * frequency * 2.3 + phase * 1.7) + 0.15 * sin(x * frequency * 5.1)
		points.append(Vector2(x, base_y - height * (0.6 + 0.4 * wave)))
		if x >= rect.end.x:
			break
		x += 24.0
	points.append(Vector2(rect.end.x, base_y + 1.0))
	points.append(Vector2(rect.position.x, base_y + 1.0))
	canvas.draw_colored_polygon(points, color)
