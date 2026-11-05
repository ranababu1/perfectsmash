class_name ProjectileBody
extends RigidBody2D
## The launched ball. Continuous collision detection prevents tunnelling through thin blocks.
## Ammo "heavy" is a bigger, heavier ball; "blast" detonates on its first contact.

signal impacted(strength: float, at: Vector2)
signal detonated(at: Vector2)

var ammo := GameConfig.DEFAULT_AMMO
var _spent := false


func _init(p_ammo: String = GameConfig.DEFAULT_AMMO) -> void:
	ammo = p_ammo
	var spec: Dictionary = GameConfig.AMMO[ammo]
	mass = spec.mass
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
	shape.radius = spec.radius
	var collider := CollisionShape2D.new()
	collider.shape = shape
	add_child(collider)


func _integrate_forces(state: PhysicsDirectBodyState2D) -> void:
	if ammo == "blast" and not _spent and state.get_contact_count() > 0:
		_spent = true
		detonated.emit(global_position)
		return
	for i in state.get_contact_count():
		var strength := state.get_contact_impulse(i).length()
		if strength > GameConfig.IMPACT_SOUND_IMPULSE:
			impacted.emit(strength, global_position)
			return


func is_spent() -> bool:
	return _spent


func _draw() -> void:
	draw_ball(self, Vector2.ZERO, -rotation, ammo)


static func radius_for(ammo_kind: String) -> float:
	return float(GameConfig.AMMO.get(ammo_kind, GameConfig.AMMO[GameConfig.DEFAULT_AMMO]).radius)


## Shared with the aim preview so the loaded ball and the flying ball look identical.
static func draw_ball(canvas: CanvasItem, at: Vector2, light_rotation: float = 0.0, ammo_kind: String = GameConfig.DEFAULT_AMMO) -> void:
	var r := radius_for(ammo_kind)
	var colors := Palette.ammo_colors(ammo_kind)
	canvas.draw_circle(at, r, colors[0], true, -1.0, true)
	canvas.draw_arc(at, r - 1.0, 0, TAU, 40, colors[1], 2.0, true)
	if ammo_kind == "heavy":
		canvas.draw_arc(at, r * 0.55, 0, TAU, 28, Color(0.2, 0.24, 0.32, 0.5), 2.0, true)
	elif ammo_kind == "blast":
		# A short fuse spark on top.
		var spark := 0.6 + 0.4 * sin(Time.get_ticks_msec() / 60.0)
		canvas.draw_line(at + Vector2(0, -r), at + Vector2(3, -r - 6), colors[1], 2.0, true)
		canvas.draw_circle(at + Vector2(4, -r - 7), 3.0 * spark, Color(1, 0.95, 0.6, spark), true, -1.0, true)
	canvas.draw_circle(at + Vector2(-r * 0.38, -r * 0.38).rotated(light_rotation), r * 0.22, Color(1, 1, 1, 0.6), true, -1.0, true)
