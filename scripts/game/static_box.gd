class_name StaticBox
extends StaticBody2D
## An immovable surface: ground, ledges, ramps.

var size := Vector2.ONE
var fill := Palette.STATIC
var edge := Palette.STATIC_EDGE


var is_bumper := false


func _init(p_size: Vector2, p_fill: Color = Palette.STATIC, p_edge: Color = Palette.STATIC_EDGE, p_bumper: bool = false) -> void:
	size = p_size
	fill = p_fill
	edge = p_edge
	is_bumper = p_bumper
	collision_layer = 1 << 0
	collision_mask = 0
	var phys := PhysicsMaterial.new()
	phys.friction = 0.2 if is_bumper else 0.9
	phys.bounce = GameConfig.BUMPER_BOUNCE if is_bumper else 0.0
	physics_material_override = phys
	var shape := RectangleShape2D.new()
	shape.size = size
	var collider := CollisionShape2D.new()
	collider.shape = shape
	add_child(collider)


func _draw() -> void:
	var rect := Rect2(-size / 2.0, size)
	var box := StyleBoxFlat.new()
	box.bg_color = fill
	box.set_corner_radius_all(3 if size.x < 1000.0 else 0)
	box.anti_aliasing = true
	box.draw(get_canvas_item(), rect)
	draw_line(rect.position + Vector2(1, 1), Vector2(rect.end.x - 1, rect.position.y + 1), edge, 2.0, true)
	if is_bumper:
		# Chevrons along the long axis mark a springy surface.
		var long_x := size.x >= size.y
		var length := size.x if long_x else size.y
		var t := -length / 2.0 + 10.0
		while t < length / 2.0 - 6.0:
			var c := Vector2(t, 0) if long_x else Vector2(0, t)
			var a := Vector2(0, -size.y * 0.25) if long_x else Vector2(-size.x * 0.25, 0)
			var b := Vector2(4, 0) if long_x else Vector2(0, 4)
			draw_polyline(PackedVector2Array([c + a, c + b, c - a]), Color(edge, 0.7), 1.5, true)
			t += 12.0
