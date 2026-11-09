extends TestCase
## MissionScoring: Mission Points vs Research Data, relative efficiency, failure behaviour.

var _materials := MaterialCatalog.load_from_file()
var _weapons := WeaponCatalog.load_from_file()
var _scoring := MissionScoring.load_from_file()


func _engine(rewards: Variant = null, recommended: int = 2, target_time: float = 30.0) -> MissionEngine:
	var data := {
		"id": "s", "name": "S", "chapter": 1, "width": 1600, "ground_y": 640, "operative": [100, 640],
		"recommended_shots": recommended, "target_time": target_time,
		"weapons": {"kinetic_accelerator": {"ammunition": 20}},
		"components": [
			{"id": "base", "kind": "k", "material": "concrete", "x": 800, "y": 560, "w": 40, "h": 160},
			{"id": "core", "kind": "ai_core", "material": "electronic_module", "x": 800, "y": 450, "w": 50, "h": 50, "critical_asset": true, "supports": ["base"]},
			{"id": "rack", "kind": "server_rack", "material": "electronic_module", "x": 1000, "y": 590, "w": 40, "h": 100},
		],
		"objectives": [
			{"id": "core", "type": "destroy_critical", "mandatory": true, "label": "L", "targets": ["core"]},
			{"id": "rack", "type": "destroy_components", "mandatory": false, "label": "L", "targets": ["rack"]},
		],
	}
	if rewards != null:
		data["rewards"] = rewards
	var def := MissionDefinition.from_json_text(JSON.stringify(data), _materials, _weapons)
	assert_true(def.is_valid(), ", ".join(def.errors))
	return MissionEngine.new(def, _materials, _weapons)


func _shoot(e: MissionEngine, count: int, effective: int) -> void:
	for i in count:
		e.fire(Vector2.RIGHT)
		if i < effective:
			e.record_effective_shot()
		e.tick(1.5, false)


func _kill(e: MissionEngine, id: String) -> void:
	e.apply_damage(id, 99999.0, DamageRules.TYPE_IMPACT, 0.9)


func test_shipped_scoring_is_valid() -> void:
	assert_true(_scoring.is_valid(), ", ".join(_scoring.errors))
	var helix := MissionDefinition.load_from_file("res://data/missions/helix_01.json", _materials, _weapons)
	assert_eq(helix.completion_points, 1000)
	assert_eq(helix.completion_research_data, 20)


func test_shot_factor_is_relative_to_recommended() -> void:
	assert_near(_scoring.shot_factor(3, 4), 1.0, 0.001, "under the benchmark is full credit, not more")
	assert_near(_scoring.shot_factor(4, 4), 1.0, 0.001)
	assert_near(_scoring.shot_factor(6, 4), 0.5, 0.001)
	assert_near(_scoring.shot_factor(8, 4), 0.0, 0.001)
	assert_near(_scoring.shot_factor(30, 20), 0.5, 0.001, "a 20-shot facility is judged against its own benchmark")


func test_time_factor_has_a_floor() -> void:
	assert_near(_scoring.time_factor(20.0, 30.0), 1.0, 0.001)
	assert_near(_scoring.time_factor(60.0, 30.0), 0.65, 0.001)
	assert_near(_scoring.time_factor(90.0, 30.0), 0.3, 0.001)
	assert_near(_scoring.time_factor(900.0, 30.0), 0.3, 0.001, "a slow, thoughtful clear keeps the floor")


func test_successful_efficient_mission() -> void:
	var e := _engine({"completion_points": 1200, "completion_research_data": 25, "optional_research_data": 6})
	_shoot(e, 2, 2)
	_kill(e, "core")
	_kill(e, "rack")
	e.tick(0.0, true)
	var r := _scoring.score(e)
	assert_true(r.success)
	assert_eq(r.points.completion, 1200)
	assert_eq(r.points.critical_asset, 500)
	assert_eq(r.points.optional_objective, 300)
	assert_eq(r.points.shot_efficiency, 800)
	assert_eq(r.points.time_efficiency, 300, "3 s is under the 30 s target")
	assert_eq(r.points.accuracy, 400)
	assert_near(r.accuracy, 1.0, 0.001)
	assert_eq(r.research.completion, 25)
	assert_eq(r.research.optional_objective, 6)
	assert_eq(r.research.efficiency, 15)
	assert_eq(r.research_data, 46)
	var expected: int = 1200 + 500 + r.points.destruction + 300 + 800 + 300 + 400
	assert_eq(r.mission_points, expected, "Mission Points and Research Data are separate totals")


func test_inefficient_and_slow_still_rewarded() -> void:
	var e := _engine(null, 2, 30.0)
	_shoot(e, 4, 2)  # 4 shots vs 2 recommended, half of them did nothing
	e.tick(200.0, false)
	_kill(e, "core")
	e.tick(0.0, true)
	var r := _scoring.score(e)
	assert_true(r.success)
	assert_eq(r.points.shot_efficiency, 0)
	assert_eq(r.points.time_efficiency, 90, "time floor 30%")
	assert_eq(r.points.accuracy, 200)
	assert_true(r.research_data >= 20, "completion Research Data is never lost to slowness")
	assert_true(r.mission_points > 1000)


func test_speed_is_a_minor_factor() -> void:
	var p := _scoring.points
	assert_true(p.time_efficiency < p.shot_efficiency, "time weighs less than shot efficiency")
	assert_true(p.time_efficiency < p.optional_objective + p.critical_asset)
	var max_total: float = 1000.0 + p.critical_asset + p.destruction + p.optional_objective * 3 + p.shot_efficiency + p.time_efficiency + p.accuracy
	assert_true(p.time_efficiency / max_total < 0.1, "time is under 10% of the maximum")


func test_failure_keeps_destruction_but_no_completion_or_research() -> void:
	var e := _engine()
	_shoot(e, 20, 5)
	_kill(e, "rack")
	e.tick(0.0, true)
	assert_eq(e.phase, MissionEngine.Phase.FAILED)
	var r := _scoring.score(e)
	assert_false(r.success)
	assert_eq(r.points.completion, 0)
	assert_eq(r.points.shot_efficiency, 0)
	assert_eq(r.points.optional_objective, 0)
	assert_true(r.points.destruction > 0, "experimenting is not worthless")
	assert_eq(r.research_data, 0)
	assert_eq(r.critical_destroyed, 0)


func test_rejects_invalid_rewards_and_scoring_files() -> void:
	var def := MissionDefinition.from_json_text(JSON.stringify({"id": "x", "rewards": {"completion_points": -5}}), _materials, _weapons)
	assert_true(def.errors.has("rewards.completion_points must be a whole number >= 0"), ", ".join(def.errors))
	assert_false(MissionScoring.load_from_file("res://data/missing_scoring.json").is_valid())
