class_name DestructionRules
extends RefCounted
## Rules for when bodies break or leave play. Kept free of node access for testing.


## Breakables only take damage once armed (after the first launch), so settling jitter
## at level load can never destroy anything.
static func breaks_on_impact(armed: bool, impulse: float, threshold: float) -> bool:
	return armed and impulse > threshold


static func is_out_of_bounds(point: Vector2) -> bool:
	return not GameConfig.KILL_BOUNDS.has_point(point)
