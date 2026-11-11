class_name WeaponProjectile
extends RigidBody2D
## A fired round or charge. Its shape, mass and gravity come from the weapon's effective stats.
## Reports its first strike once, with the speed it had just before the impact; MissionWorld
## decides what the strike does (direct damage, or a blast for charges).
## Charges with `fuse_seconds` > 0 also go off in the air when the fuse runs out before they hit
## anything (a timed air burst); the strike then has no target.
## Piercing rounds (`pierce_count` > 0) report every component they hit; while pierces remain and
## MissionWorld lets them (pass_through), they keep flying with `pierce_speed_keep` of their speed.
## A round is spent (`has_struck`) on its final strike.

signal struck(projectile: WeaponProjectile, target: Node, impact_speed: float)

const COLLISION_LAYER := 1 << 3
const MAX_LIFETIME := 6.0

var weapon_id := ""
var stats := {}
var age := 0.0
## Seconds after launch at which an unexploded charge bursts in the air; 0 = contact fuse only.
var fuse_seconds := 0.0
var _previous_speed := 0.0
var _previous_velocity := Vector2.ZERO
var _has_struck := false
## Pierces left; MissionWorld spends them through pass_through().
var pierces_left := 0
## Whether this round already counted as an effective shot (a piercing round hits several times).
var counted_effective := false
var _restore_velocity := Vector2.ZERO
var _restore := false


func _init(p_weapon_id: String, p_stats: Dictionary, start: Vector2, velocity: Vector2) -> void:
	weapon_id = p_weapon_id
	stats = p_stats
	position = start
	linear_velocity = velocity
	_previous_speed = velocity.length()
	mass = float(stats.projectile_mass)
	gravity_scale = float(stats.gravity_scale)
	# No air drag: the flight must follow the aim preview's ballistic arc exactly (Godot's default
	# 2D linear damp of 0.1 made lobs land 25-50 px short of the arc the player was shown).
	linear_damp_mode = RigidBody2D.DAMP_MODE_REPLACE
	linear_damp = 0.0
	angular_damp_mode = RigidBody2D.DAMP_MODE_REPLACE
	angular_damp = 0.0
	fuse_seconds = float(stats.get("fuse_seconds", 0.0))
	pierces_left = int(stats.get("pierce_count", 0))
	_previous_velocity = velocity
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


## Lets the round continue through `body` (already damaged by the caller) at reduced speed.
func pass_through(body: PhysicsBody2D) -> void:
	pierces_left -= 1
	_has_struck = false
	add_collision_exception_with(body)
	_restore_velocity = _previous_velocity * float(stats.get("pierce_speed_keep", 0.75))
	_restore = true


func _integrate_forces(state: PhysicsDirectBodyState2D) -> void:
	if _restore:
		_restore = false
		state.linear_velocity = _restore_velocity


func _physics_process(delta: float) -> void:
	age += delta
	if not _has_struck:
		_previous_speed = linear_velocity.length()
		_previous_velocity = linear_velocity
		if fuse_seconds > 0.0 and age >= fuse_seconds:
			_has_struck = true
			struck.emit(self, null, _previous_speed)


func _on_body_entered(body: Node) -> void:
	if _has_struck:
		return
	_has_struck = true
	struck.emit(self, body, _previous_speed)
