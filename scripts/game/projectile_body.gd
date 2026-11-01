class_name ProjectileBody
extends RigidBody2D
## The launched ball. Continuous collision detection prevents tunnelling through thin blocks.

signal impacted(strength: float, at: Vector2)


func _init() -> void:
	mass = GameConfig.PROJECTILE_MASS
	continuous_cd = RigidBody2D.CCD_MODE_CAST_SHAPE
	angular_damp = 2.0
	var phys := PhysicsMaterial.new()
	phys.friction = 0.6
	phys.bounce = 0.2
	physics_material_override = phys
	contact_monitor = true
	max_contacts_reported = 4
	collision_layer = 1 << 3
	collision_mask = 0b1111
	var shape := CircleShape2D.new()
	shape.radius = GameConfig.PROJECTILE_RADIUS
	var collider := CollisionShape2D.new()
	collider.shape = shape
	add_child(collider)


func _integrate_forces(state: PhysicsDirectBodyState2D) -> void:
	for i in state.get_contact_count():
		var strength := state.get_contact_impulse(i).length()
		if strength > GameConfig.IMPACT_SOUND_IMPULSE:
			impacted.emit(strength, global_position)
			return


func _draw() -> void:
	draw_ball(self, Vector2.ZERO, -rotation)


## Shared with the aim preview so the loaded ball and the flying ball look identical.
static func draw_ball(canvas: CanvasItem, at: Vector2, light_rotation: float = 0.0) -> void:
	var r := GameConfig.PROJECTILE_RADIUS
	canvas.draw_circle(at, r, Palette.PROJECTILE)
	canvas.draw_arc(at, r - 1.0, 0, TAU, 40, Palette.PROJECTILE_EDGE, 2.0, true)
	canvas.draw_circle(at + Vector2(-r * 0.38, -r * 0.38).rotated(light_rotation), r * 0.22, Color(1, 1, 1, 0.6))
