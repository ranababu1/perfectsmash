class_name BlockBody
extends RigidBody2D
## A dynamic rectangular structure piece. Glass blocks shatter on hard impacts once armed.

signal impacted(strength: float, at: Vector2)
signal shattered(at: Vector2)

var size := Vector2.ONE
var material_kind := "wood"
var armed := false
var _broken := false


func _init(p_size: Vector2, p_material: String) -> void:
	size = p_size
	material_kind = p_material
	var props: Dictionary = GameConfig.MATERIALS[material_kind]
	mass = size.x * size.y * float(props.density)
	var phys := PhysicsMaterial.new()
	phys.friction = props.friction
	phys.bounce = props.bounce
	physics_material_override = phys
	contact_monitor = true
	max_contacts_reported = 4
	collision_layer = 1 << 1
	collision_mask = 0b1111
	var shape := RectangleShape2D.new()
	shape.size = size
	var collider := CollisionShape2D.new()
	collider.shape = shape
	add_child(collider)
	add_to_group("blocks")


func top_y() -> float:
	var half := size / 2.0
	var top := INF
	for corner in [Vector2(-half.x, -half.y), Vector2(half.x, -half.y), Vector2(half.x, half.y), Vector2(-half.x, half.y)]:
		top = minf(top, (global_transform * corner).y)
	return top


func _integrate_forces(state: PhysicsDirectBodyState2D) -> void:
	if _broken:
		return
	var strongest := 0.0
	for i in state.get_contact_count():
		strongest = maxf(strongest, state.get_contact_impulse(i).length())
	if strongest > GameConfig.IMPACT_SOUND_IMPULSE:
		impacted.emit(strongest, global_position)
	if material_kind == "glass" and DestructionRules.breaks_on_impact(armed, strongest, GameConfig.GLASS_BREAK_IMPULSE):
		_broken = true
		shattered.emit(global_position)
		queue_free()


func is_broken() -> bool:
	return _broken


func _draw() -> void:
	var rect := Rect2(-size / 2.0, size)
	_style_for(material_kind).draw(get_canvas_item(), rect)
	# A soft bevel along one face gives the pieces a little volume without textures.
	var inset := minf(5.0, minf(size.x, size.y) * 0.2)
	var bevel := Rect2(rect.position + Vector2(inset, inset), Vector2(size.x - inset * 2.0, 2.0))
	draw_rect(bevel, Color(1, 1, 1, 0.22 if material_kind != "glass" else 0.4))
	if material_kind == "wood":
		# A single grain line along the long axis keeps orientation readable while tumbling.
		var horizontal := size.x >= size.y
		var a := Vector2(-size.x * 0.28, 0) if horizontal else Vector2(0, -size.y * 0.28)
		draw_line(a, -a, Color(Palette.WOOD_EDGE, 0.55), 2.0, true)
	elif material_kind == "glass":
		draw_line(Vector2(-size.x * 0.25, size.y * 0.3), Vector2(size.x * 0.05, -size.y * 0.3), Color(Palette.GLASS_EDGE, 0.7), 2.0, true)


static var _styles := {}


static func _style_for(kind: String) -> StyleBoxFlat:
	if not _styles.has(kind):
		var box := StyleBoxFlat.new()
		box.bg_color = Palette.material_fill(kind)
		box.border_color = Palette.material_edge(kind)
		box.set_border_width_all(2)
		box.set_corner_radius_all(4)
		box.anti_aliasing = true
		_styles[kind] = box
	return _styles[kind]
