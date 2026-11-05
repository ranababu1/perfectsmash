class_name SessionRules
extends RefCounted
## Turn state machine for one level attempt: shot budget and win/loss transitions.
## READY --launch--> SIMULATING --settled--> READY | WON | LOST

enum Phase { READY, SIMULATING, WON, LOST }

var shots_budget := 1
var shots_used := 0
var phase := Phase.READY


func _init(budget: int) -> void:
	shots_budget = maxi(budget, 1)


func shots_remaining() -> int:
	return shots_budget - shots_used


func can_launch() -> bool:
	return phase == Phase.READY and shots_used < shots_budget


func register_launch() -> bool:
	if not can_launch():
		return false
	shots_used += 1
	phase = Phase.SIMULATING
	return true


## `failed` ends the attempt immediately (an ally or cargo was lost), even with shots left.
func register_settled(objective_met: bool, failed: bool = false) -> Phase:
	if phase != Phase.SIMULATING:
		push_error("SessionRules: register_settled called outside a simulation")
		return phase
	if failed:
		phase = Phase.LOST
	elif objective_met:
		phase = Phase.WON
	elif shots_used >= shots_budget:
		phase = Phase.LOST
	else:
		phase = Phase.READY
	return phase


func is_finished() -> bool:
	return phase == Phase.WON or phase == Phase.LOST
