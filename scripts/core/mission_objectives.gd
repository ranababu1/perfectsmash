class_name MissionObjectives
extends RefCounted
## Objective states for one mission, evaluated from a plain snapshot of the mission state.
## Goals (destroy_critical, destroy_components, structural_damage) complete during play and stay
## complete. Constraints (protect, max_shots, within_time) fail as soon as they are broken and
## otherwise complete when the mission succeeds. finalize() resolves everything still pending.

enum Status { PENDING, COMPLETE, FAILED }


class Objective:
	var id := ""
	var type := ""
	var mandatory := false
	var label := ""
	var targets: Array[String] = []
	var count := 0
	var fraction := 0.0
	var limit := 0.0
	var status := Status.PENDING
	## 0-1 for goals (for the HUD); constraints report 1 while intact.
	var progress := 0.0

	func is_goal() -> bool:
		return MissionDefinition.GOAL_TYPES.has(type)


var objectives: Array[Objective] = []


func _init(definitions: Array[Dictionary]) -> void:
	for d in definitions:
		var o := Objective.new()
		o.id = d.id
		o.type = d.type
		o.mandatory = d.mandatory
		o.label = d.label
		o.targets.assign(d.targets)
		o.count = d.count
		o.fraction = d.fraction
		o.limit = d.limit
		o.progress = 0.0 if o.is_goal() else 1.0
		objectives.append(o)


func get_objective(objective_id: String) -> Objective:
	for o in objectives:
		if o.id == objective_id:
			return o
	return null


## Snapshot keys: destroyed (Dictionary id -> true), structural_damage (0-1), shots (int),
## elapsed (seconds). Returns the objectives whose status changed.
func update(snapshot: Dictionary) -> Array[Objective]:
	var changed: Array[Objective] = []
	var destroyed: Dictionary = snapshot.get("destroyed", {})
	for o in objectives:
		if o.status != Status.PENDING:
			continue
		var next := Status.PENDING
		match o.type:
			MissionDefinition.OBJECTIVE_DESTROY_CRITICAL, MissionDefinition.OBJECTIVE_DESTROY_COMPONENTS:
				var needed := o.targets.size() if o.type == MissionDefinition.OBJECTIVE_DESTROY_CRITICAL else o.count
				var done := o.targets.filter(func(t: String) -> bool: return destroyed.has(t)).size()
				o.progress = clampf(float(done) / maxf(needed, 1), 0.0, 1.0)
				if done >= needed:
					next = Status.COMPLETE
			MissionDefinition.OBJECTIVE_STRUCTURAL_DAMAGE:
				var damage := float(snapshot.get("structural_damage", 0.0))
				o.progress = clampf(damage / o.fraction, 0.0, 1.0)
				if damage >= o.fraction:
					next = Status.COMPLETE
			MissionDefinition.OBJECTIVE_PROTECT:
				if o.targets.any(func(t: String) -> bool: return destroyed.has(t)):
					next = Status.FAILED
			MissionDefinition.OBJECTIVE_MAX_SHOTS:
				if int(snapshot.get("shots", 0)) > int(o.limit):
					next = Status.FAILED
			MissionDefinition.OBJECTIVE_WITHIN_TIME:
				if float(snapshot.get("elapsed", 0.0)) > o.limit:
					next = Status.FAILED
		if next != Status.PENDING:
			o.status = next
			if next == Status.FAILED:
				o.progress = 0.0
			changed.append(o)
	return changed


func mandatory_goals_complete() -> bool:
	return objectives.all(func(o: Objective) -> bool: return not (o.mandatory and o.is_goal()) or o.status == Status.COMPLETE)


func mandatory_failed() -> bool:
	return objectives.any(func(o: Objective) -> bool: return o.mandatory and o.status == Status.FAILED)


func completed_optional_count() -> int:
	return objectives.filter(func(o: Objective) -> bool: return not o.mandatory and o.status == Status.COMPLETE).size()


## Resolves pending objectives at mission end: intact constraints complete on success; anything
## else still pending fails. Returns the objectives whose status changed.
func finalize(success: bool) -> Array[Objective]:
	var changed: Array[Objective] = []
	for o in objectives:
		if o.status != Status.PENDING:
			continue
		o.status = Status.COMPLETE if (success and not o.is_goal()) else Status.FAILED
		changed.append(o)
	return changed
