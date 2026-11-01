class_name DestructionRules
extends RefCounted
## Rules for when bodies break or leave play. Kept free of node access for testing.


## Breakables only take damage once armed (after the first launch), so settling jitter
## at level load can never destroy anything.
static func breaks_on_impact(armed: bool, impulse: float, threshold: float) -> bool:
	return armed and impulse > threshold


## A direct touch from the projectile at speed always pops a target: players read a visible
## hit as a hit, even when the engine resolves it as a shove with a small reported impulse.
static func breaks_on_projectile_hit(armed: bool, relative_speed: float) -> bool:
	return armed and relative_speed > GameConfig.TARGET_PROJECTILE_HIT_SPEED


## A sudden velocity change (being shoved or knocked hard) breaks a target.
static func breaks_on_jolt(armed: bool, velocity_change: float) -> bool:
	return armed and velocity_change > GameConfig.TARGET_BREAK_VELOCITY_CHANGE


static func is_out_of_bounds(point: Vector2) -> bool:
	return not GameConfig.KILL_BOUNDS.has_point(point)
