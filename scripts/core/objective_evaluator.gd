class_name ObjectiveEvaluator
extends RefCounted
## Decides a level's outcome from a settled game-state snapshot.
## Pure functions: no scene or physics access, so they can be evaluated repeatedly and tested in isolation.

enum Outcome { PENDING, MET, FAILED }


## state keys (all optional, with neutral defaults):
##   targets_remaining: int, highest_block_top: float (INF when no blocks), topple_line_y: float,
##   cargo_total: int, cargo_in_zone: int, cargo_lost: int, allies_lost: int
## A lost ally or lost cargo makes the level impossible, so it fails even with shots left.
static func evaluate(objective_type: String, state: Dictionary) -> Outcome:
	if int(state.get("allies_lost", 0)) > 0 or int(state.get("cargo_lost", 0)) > 0:
		return Outcome.FAILED
	return Outcome.MET if is_met(objective_type, state) else Outcome.PENDING


static func is_met(objective_type: String, state: Dictionary) -> bool:
	match objective_type:
		LevelDefinition.OBJECTIVE_DESTROY_TARGETS:
			return int(state.get("targets_remaining", 0)) <= 0
		LevelDefinition.OBJECTIVE_TOPPLE:
			# Screen y grows downward: a top edge below the line has a larger y.
			return float(state.get("highest_block_top", INF)) >= float(state.get("topple_line_y", 0.0))
		LevelDefinition.OBJECTIVE_DELIVER:
			var total := int(state.get("cargo_total", 0))
			return total > 0 and int(state.get("cargo_in_zone", 0)) >= total
	push_error("ObjectiveEvaluator: unknown objective '%s'" % objective_type)
	return false
