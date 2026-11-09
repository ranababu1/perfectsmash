class_name MissionScoring
extends RefCounted
## Mission Points (performance and future rankings) and Research Data (upgrade currency) for a
## finished mission, from data/scoring.json plus the mission's own rewards, recommended shots
## and target time. Pure and deterministic.
##
## Efficiency is relative to each mission: at or under the recommended shots / target time is
## full credit. Shot credit falls to zero at `zero_at_multiple` x recommended. Time credit never
## drops below `floor`, so a slow, thoughtful clear still earns most of the score; time is the
## smallest weight. Failure keeps destruction and accuracy points (experimenting is not punished)
## but earns no completion, efficiency or Research Data.

const DEFAULT_PATH := "res://data/scoring.json"
const POINT_KEYS := ["critical_asset", "destruction", "optional_objective", "shot_efficiency", "time_efficiency", "accuracy"]

var points := {}
var research_efficiency_max := 0.0
var research_shot_weight := 0.7
var shot_zero_multiple := 2.0
var time_floor := 0.3
var time_floor_multiple := 3.0
var errors := PackedStringArray()


static func load_from_file(path: String = DEFAULT_PATH) -> MissionScoring:
	var scoring := MissionScoring.new()
	var file := FileAccess.open(path, FileAccess.READ)
	if file == null:
		scoring.errors.append("cannot open %s (error %d)" % [path, FileAccess.get_open_error()])
		return scoring
	var data: Variant = JSON.parse_string(file.get_as_text())
	if not data is Dictionary:
		scoring.errors.append("scoring root must be an object")
		return scoring
	scoring._parse(data)
	return scoring


func is_valid() -> bool:
	return errors.is_empty()


## 1 at or under the recommended shots, falling linearly to 0 at zero_at_multiple x recommended.
func shot_factor(shots: int, recommended: int) -> float:
	if recommended <= 0 or shots <= recommended:
		return 1.0
	var span := float(recommended) * (shot_zero_multiple - 1.0)
	return clampf(1.0 - float(shots - recommended) / span, 0.0, 1.0)


## 1 at or under the target time, falling linearly to `floor` at floor_at_multiple x target.
func time_factor(elapsed: float, target: float) -> float:
	if target <= 0.0 or elapsed <= target:
		return 1.0
	var span := target * (time_floor_multiple - 1.0)
	return clampf(1.0 - (1.0 - time_floor) * (elapsed - target) / span, time_floor, 1.0)


## Scores a finished MissionEngine. Returns a breakdown dictionary:
## {success, mission_points, research_data, points: {source: int}, research: {source: int},
##  shot_factor, time_factor, accuracy}
func score(engine: MissionEngine) -> Dictionary:
	var def := engine.definition
	var success := engine.phase == MissionEngine.Phase.SUCCEEDED
	var shots := engine.shots_fired()
	var accuracy := float(engine.effective_shots) / shots if shots > 0 else 0.0
	var s_factor := shot_factor(shots, def.recommended_shots)
	var t_factor := time_factor(engine.elapsed, def.target_time)

	var critical_total := def.critical_asset_ids().size()
	var critical_destroyed := def.critical_asset_ids().filter(func(id: String) -> bool:
		return engine.component_state(id) == DamageableComponent.State.DESTROYED).size()
	var optional_done := engine.objectives.completed_optional_count()

	var p := {
		"completion": def.completion_points if success else 0,
		"critical_asset": roundi(points.critical_asset * critical_destroyed),
		"destruction": roundi(points.destruction * engine.structural_damage_fraction()),
		"optional_objective": roundi(points.optional_objective * optional_done) if success else 0,
		"shot_efficiency": roundi(points.shot_efficiency * s_factor) if success else 0,
		"time_efficiency": roundi(points.time_efficiency * t_factor) if success else 0,
		"accuracy": roundi(points.accuracy * accuracy),
	}
	var r := {"completion": 0, "optional_objective": 0, "efficiency": 0}
	if success:
		r.completion = def.completion_research_data
		r.optional_objective = def.optional_research_data * optional_done
		var blend := research_shot_weight * s_factor + (1.0 - research_shot_weight) * t_factor
		r.efficiency = roundi(research_efficiency_max * blend)
	var total_points := 0
	for v: int in p.values():
		total_points += v
	var total_research := 0
	for v: int in r.values():
		total_research += v
	return {
		"success": success,
		"mission_points": total_points,
		"research_data": total_research,
		"points": p,
		"research": r,
		"shot_factor": s_factor,
		"time_factor": t_factor,
		"accuracy": accuracy,
		"critical_destroyed": critical_destroyed,
		"critical_total": critical_total,
	}


func _parse(data: Dictionary) -> void:
	var mp: Variant = data.get("mission_points")
	if mp is Dictionary:
		for key: String in POINT_KEYS:
			var v: Variant = mp.get(key)
			if (v is float or v is int) and v >= 0:
				points[key] = float(v)
			else:
				errors.append("mission_points.%s must be a non-negative number" % key)
				points[key] = 0.0
	else:
		errors.append("missing 'mission_points'")
	var rd: Variant = data.get("research_data", {})
	research_efficiency_max = _num(rd, "efficiency_max", 0.0, INF)
	research_shot_weight = _num(rd, "efficiency_shot_weight", 0.0, 1.0)
	shot_zero_multiple = _num(data.get("shot_factor", {}), "zero_at_multiple", 1.01, INF)
	time_floor = _num(data.get("time_factor", {}), "floor", 0.0, 1.0)
	time_floor_multiple = _num(data.get("time_factor", {}), "floor_at_multiple", 1.01, INF)


func _num(section: Variant, key: String, low: float, high: float) -> float:
	var v: Variant = section.get(key) if section is Dictionary else null
	if (v is float or v is int) and v >= low and v <= high:
		return float(v)
	errors.append("'%s' must be a number in [%s, %s]" % [key, low, high])
	return low
