class_name StaticBox
extends StaticBody2D
## An immovable surface: ground, ledges, ramps.

var size := Vector2.ONE
var fill := Palette.STATIC
var edge := Palette.STATIC_EDGE


func _init(p_size: Vector2, p_fill: Color = Palette.STATIC, p_edge: Color = Palette.STATIC_EDGE) -> void:
	size = p_size
	fill = p_fill
	edge = p_edge
	collision_layer = 1 << 0
	collision_mask = 0
	var phys := PhysicsMaterial.new()
	phys.friction = 0.9
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
