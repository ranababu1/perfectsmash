class_name ComponentBody
extends RigidBody2D
## Physics body of one facility component. Starts frozen (static) so a facility stands exactly as
## authored and costs almost nothing to simulate. MissionWorld releases it to physics when it
## loses its supports, becomes unstable, or is pushed by a blast.
##
## Collision damage comes from impacts, measured as the body's sudden velocity change with the
## expected gravity change and one step of support removed, so resting contacts and free fall
## deal nothing.

## A hard impact on this (dynamic) body. `others` are the bodies touched in that step.
signal impacted(body: ComponentBody, impulse: float, others: Array)

const COLLISION_LAYER := 1 << 1
## Ground and static facility geometry (StaticBox uses layer 1).
const STATIC_LAYER := 1 << 0

var component_id := ""
var kind := ""
var size := Vector2.ONE
var material_id := ""
var _previous_velocity := Vector2.ZERO
var _released := false


func _init(component: Dictionary, material: MaterialCatalog.MaterialSpec) -> void:
	component_id = component.id
	kind = component.kind
	size = component.size
	material_id = component.material
	position = component.position
	rotation = component.rotation
	mass = maxf(material.mass_for(size), 0.05)
	var phys := PhysicsMaterial.new()
	phys.friction = material.friction
	phys.bounce = material.bounce
	physics_material_override = phys
	freeze_mode = RigidBody2D.FREEZE_MODE_STATIC
	freeze = true
	contact_monitor = true
	max_contacts_reported = 6
	collision_layer = COLLISION_LAYER
	collision_mask = STATIC_LAYER | COLLISION_LAYER | WeaponProjectile.COLLISION_LAYER
	var shape := RectangleShape2D.new()
	shape.size = size
	var collider := CollisionShape2D.new()
	collider.shape = shape
	add_child(collider)
	name = "Component_%s" % component_id


func is_released() -> bool:
	return _released


## Hands the body to the physics simulation (deferred: safe to call from physics callbacks).
func release() -> void:
	if _released:
		return
	_released = true
	set_deferred("freeze", false)


## Releases the body and applies an impulse once it is dynamic.
func push(impulse: Vector2) -> void:
	release()
	_apply_push.call_deferred(impulse)


func _apply_push(impulse: Vector2) -> void:
	if is_inside_tree() and not freeze:
		apply_central_impulse(impulse)


func _physics_process(delta: float) -> void:
	if freeze:
		_previous_velocity = Vector2.ZERO
		return
	var gravity_step := get_gravity() * gravity_scale * delta
	# A supporting contact cancels one gravity step every frame; that is resting, not an impact.
	# Without this allowance a heavy body at rest (blast wall: mass 9.45 x 16.3 px/s = 154)
	# reported an "impact" every frame, which also kept the scene from ever settling.
	var jolt := maxf(0.0, (linear_velocity - (_previous_velocity + gravity_step)).length() - gravity_step.length())
	_previous_velocity = linear_velocity
	var impulse := mass * jolt
	if impulse <= DamageRules.COLLISION_DAMAGE_FLOOR:
		return
	var others := get_colliding_bodies()
	# A projectile's own damage already covers the hit; don't count its momentum twice.
	if others.any(func(b: Node) -> bool: return b is WeaponProjectile):
		return
	impacted.emit(self, impulse, others)
