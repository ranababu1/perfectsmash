class_name ObjectiveEvaluator
extends RefCounted
## Decides whether a level objective is met from a settled game-state snapshot.
## Pure function: no scene or physics access, so it can be evaluated repeatedly and tested in isolation.


## highest_block_top: smallest y of any remaining block's top edge (INF when no blocks remain).
static func is_met(objective_type: String, targets_remaining: int, highest_block_top: float, topple_line_y: float) -> bool:
	match objective_type:
		LevelDefinition.OBJECTIVE_DESTROY_TARGETS:
			return targets_remaining <= 0
		LevelDefinition.OBJECTIVE_TOPPLE:
			# Screen y grows downward: a top edge below the line has a larger y.
			return highest_block_top >= topple_line_y
	push_error("ObjectiveEvaluator: unknown objective '%s'" % objective_type)
	return false
