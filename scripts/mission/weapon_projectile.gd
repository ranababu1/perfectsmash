class_name WeaponProjectile
extends RigidBody2D
## A fired round or charge. Its shape, mass and gravity come from the weapon's effective stats.
## Reports its first strike once, with the speed it had just before the impact; MissionWorld
## decides what the strike does (direct damage, or a blast for charges).
## Charges with `fuse_seconds` > 0 also go off in the air when the fuse runs out before they hit
## anything (a timed air burst); the strike then has no target.

signal struck(projectile: WeaponProjectile, target: Node, impact_speed: float)

const COLLISION_LAYER := 1 << 3
const MAX_LIFETIME := 6.0

var weapon_id := ""
var stats := {}
var age := 0.0
## Seconds after launch at which an unexploded charge bursts in the air; 0 = contact fuse only.
var fuse_seconds := 0.0
var _previous_speed := 0.0
var _has_struck := false


func _init(p_weapon_id: String, p_stats: Dictionary, start: Vector2, velocity: Vector2) -> void:
	weapon_id = p_weapon_id
	stats = p_stats
	position = start
	linear_velocity = velocity
	_previous_speed = velocity.length()
	mass = float(stats.projectile_mass)
	gravity_scale = float(stats.gravity_scale)
	fuse_seconds = float(stats.get("fuse_seconds", 0.0))
	continuous_cd = RigidBody2D.CCD_MODE_CAST_SHAPE
	contact_monitor = true
	max_contacts_reported = 2
	collision_layer = COLLISION_LAYER
	collision_mask = ComponentBody.STATIC_LAYER | ComponentBody.COLLISION_LAYER
	var phys := PhysicsMaterial.new()
	phys.friction = 0.5
	phys.bounce = 0.1
	physics_material_override = phys
	var shape := CircleShape2D.new()
	shape.radius = float(stats.projectile_radius)
	var collider := CollisionShape2D.new()
	collider.shape = shape
	add_child(collider)
	body_entered.connect(_on_body_entered)


func has_struck() -> bool:
	return _has_struck


func _physics_process(delta: float) -> void:
	age += delta
	if not _has_struck:
		_previous_speed = linear_velocity.length()
		if fuse_seconds > 0.0 and age >= fuse_seconds:
			_has_struck = true
			struck.emit(self, null, _previous_speed)


func _on_body_entered(body: Node) -> void:
	if _has_struck:
		return
	_has_struck = true
	struck.emit(self, body, _previous_speed)
