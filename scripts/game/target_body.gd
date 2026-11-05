class_name TargetBody
extends RigidBody2D
## An objective core, or (is_ally) a friendly drone that must survive. Both break the same way:
## a hard impact or jolt after arming, a fast projectile touch, or leaving the play area.

signal destroyed(at: Vector2)

var radius := 20.0
var is_ally := false
var armed := false
var _destroyed := false
var _previous_velocity := Vector2.ZERO


func _init(p_radius: float, p_ally: bool = false) -> void:
	radius = p_radius
	is_ally = p_ally
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
	add_to_group("allies" if is_ally else "targets")


func _integrate_forces(state: PhysicsDirectBodyState2D) -> void:
	if _destroyed:
		return
	var velocity_change := (state.linear_velocity - _previous_velocity).length()
	_previous_velocity = state.linear_velocity
	if DestructionRules.breaks_on_jolt(armed, velocity_change):
		destroy()
		return
	for i in state.get_contact_count():
		if DestructionRules.breaks_on_impact(armed, state.get_contact_impulse(i).length(), GameConfig.TARGET_BREAK_IMPULSE):
			destroy()
			return
		if state.get_contact_collider_object(i) is ProjectileBody:
			var relative := state.get_contact_collider_velocity_at_position(i) - state.linear_velocity
			if DestructionRules.breaks_on_projectile_hit(armed, relative.length()):
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


func _process(_delta: float) -> void:
	queue_redraw()


func _draw() -> void:
	if is_ally:
		_draw_ally()
		return
	# A slow breathing halo marks the objective without shouting.
	var pulse := 0.5 + 0.5 * sin(Time.get_ticks_msec() / 520.0 + position.x * 0.01)
	draw_circle(Vector2.ZERO, radius + 5.0 + pulse * 3.0, Color(Palette.TARGET, 0.10 + pulse * 0.06), true, -1.0, true)
	draw_circle(Vector2.ZERO, radius, Palette.TARGET, true, -1.0, true)
	draw_arc(Vector2.ZERO, radius - 1.0, 0, TAU, 40, Color(Palette.TARGET_EDGE, 0.9), 2.0, true)
	draw_arc(Vector2.ZERO, radius * 0.55, 0, TAU, 32, Color(Palette.TARGET_EDGE, 0.55), 2.0, true)
	draw_circle(Vector2.ZERO, radius * 0.22, Palette.TARGET_EDGE, true, -1.0, true)
	# Rotation-independent specular glint so tumbling still reads as a sphere.
	var glint := Vector2(-radius * 0.42, -radius * 0.42).rotated(-rotation)
	draw_circle(glint, radius * 0.14, Color(1, 1, 1, 0.45), true, -1.0, true)


## Friendly drone: blue shell, a bright visor and a small antenna; calm blink instead of a pulse.
func _draw_ally() -> void:
	var blink := 1.0 if fmod(Time.get_ticks_msec() / 1000.0 + position.x * 0.003, 3.2) > 0.12 else 0.25
	draw_circle(Vector2.ZERO, radius + 4.0, Color(Palette.ALLY, 0.12), true, -1.0, true)
	draw_circle(Vector2.ZERO, radius, Palette.ALLY, true, -1.0, true)
	draw_arc(Vector2.ZERO, radius - 1.0, 0, TAU, 40, Color(Palette.ALLY_EDGE, 0.9), 2.0, true)
	var up := Vector2.UP.rotated(-rotation)
	var side := up.orthogonal()
	var visor := up * radius * 0.1
	draw_line(visor - side * radius * 0.45, visor + side * radius * 0.45, Color(Palette.ALLY_EDGE, blink), maxf(3.0, radius * 0.22), true)
	draw_line(up * radius, up * (radius + 7.0), Palette.ALLY_EDGE, 2.0, true)
	draw_circle(up * (radius + 8.0), 2.5, Palette.ALLY_EDGE, true, -1.0, true)
