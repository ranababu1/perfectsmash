class_name TargetBody
extends RigidBody2D
## An objective object. Destroyed by a hard impact (after arming) or by leaving the play area.

signal destroyed(at: Vector2)

var radius := 20.0
var armed := false
var _destroyed := false


func _init(p_radius: float) -> void:
	radius = p_radius
	mass = GameConfig.TARGET_MASS
	angular_damp = 1.5
	var phys := PhysicsMaterial.new()
	phys.friction = 0.9
	phys.bounce = 0.1
	physics_material_override = phys
	contact_monitor = true
	max_contacts_reported = 4
	collision_layer = 1 << 2
	collision_mask = 0b1111
	var shape := CircleShape2D.new()
	shape.radius = radius
	var collider := CollisionShape2D.new()
	collider.shape = shape
	add_child(collider)
	add_to_group("targets")


func _integrate_forces(state: PhysicsDirectBodyState2D) -> void:
	if _destroyed:
		return
	for i in state.get_contact_count():
		if DestructionRules.breaks_on_impact(armed, state.get_contact_impulse(i).length(), GameConfig.TARGET_BREAK_IMPULSE):
			destroy()
			return


## Idempotent: a target can only be destroyed (and reported) once.
func destroy() -> void:
	if _destroyed:
		return
	_destroyed = true
	destroyed.emit(global_position)
	queue_free()


func is_destroyed() -> bool:
	return _destroyed


func _draw() -> void:
	draw_circle(Vector2.ZERO, radius, Palette.TARGET)
	draw_arc(Vector2.ZERO, radius - 1.5, 0, TAU, 32, Palette.TARGET_EDGE, 3.0, true)
	# Simple face so targets read as "the thing to knock out" at a glance.
	var eye := radius * 0.28
	draw_circle(Vector2(-eye, -eye * 0.6), radius * 0.13, Palette.TARGET_EDGE)
	draw_circle(Vector2(eye, -eye * 0.6), radius * 0.13, Palette.TARGET_EDGE)
	draw_line(Vector2(-eye, eye * 0.9), Vector2(eye, eye * 0.9), Palette.TARGET_EDGE, 3.0)
