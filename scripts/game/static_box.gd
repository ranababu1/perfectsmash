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
	draw_rect(rect, fill)
	draw_line(rect.position, Vector2(rect.end.x, rect.position.y), edge, 4.0)
