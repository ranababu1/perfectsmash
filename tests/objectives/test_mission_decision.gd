extends TestCase
## Optional-objective decision flow of MissionEngine: prompt when the primary is complete but
## optional goals remain, Continue / Finish, and unchanged mandatory failure. Headless, no physics.

const Status := MissionObjectives.Status

var _materials := MaterialCatalog.load_from_file()
var _weapons := WeaponCatalog.load_from_file()


func _core_goal() -> Dictionary:
	return {"id": "core", "type": "destroy_critical", "mandatory": true, "label": "Core", "targets": ["core"]}


func _opt_a() -> Dictionary:
	return {"id": "opt_a", "type": "destroy_components", "mandatory": false, "label": "A", "targets": ["r1"]}


func _opt_b() -> Dictionary:
	return {"id": "opt_b", "type": "destroy_components", "mandatory": false, "label": "B", "targets": ["r2"]}


func _opt_shots() -> Dictionary:
	return {"id": "opt_shots", "type": "max_shots", "mandatory": false, "label": "Few shots", "limit": 8}


## Default mission: mandatory core, optional goals A (r1) and B (r2), optional max_shots.
func _engine(objectives: Array = [], ammo: int = 10) -> MissionEngine:
	if objectives.is_empty():
		objectives = [_core_goal(), _opt_a(), _opt_b(), _opt_shots()]
	var components := [
		{"id": "base", "kind": "k", "material": "concrete", "x": 800, "y": 560, "w": 40, "h": 160},
		{"id": "core", "kind": "ai_core", "material": "electronic_module", "x": 800, "y": 450, "w": 50, "h": 50, "critical_asset": true, "supports": ["base"]},
		{"id": "r1", "kind": "k", "material": "concrete", "x": 900, "y": 600, "w": 40, "h": 40},
		{"id": "r2", "kind": "k", "material": "concrete", "x": 960, "y": 600, "w": 40, "h": 40},
		{"id": "guard", "kind": "k", "material": "concrete", "x": 1020, "y": 600, "w": 40, "h": 40},
	]
	var data := {
		"id": "t", "name": "T", "chapter": 1, "width": 1600, "ground_y": 640, "operative": [100, 640],
		"recommended_shots": 1, "target_time": 30,
		"weapons": {"kinetic_accelerator": {"ammunition": ammo}},
		"components": components, "objectives": objectives,
	}
	var def := MissionDefinition.from_json_text(JSON.stringify(data), _materials, _weapons)
	assert_true(def.is_valid(), ", ".join(def.errors))
	return MissionEngine.new(def, _materials, _weapons)


func _status(e: MissionEngine, id: String) -> int:
	return e.objectives.get_objective(id).status


## Engine with the primary done and the decision prompt open; records signals into the arrays.
func _prompted(decisions: Array, finished: Array, objectives: Array = [], ammo: int = 10) -> MissionEngine:
	var e := _engine(objectives, ammo)
	e.decision_requested.connect(func() -> void: decisions.append(true))
	e.mission_finished.connect(func(ok: bool) -> void: finished.append(ok))
	e.destroy_component("core", "test")
	e.tick(0.1, true)
	return e


func test_prompt_emitted_once_when_primary_done_with_pending_optional() -> void:
	var decisions := []
	var finished := []
	var e := _prompted(decisions, finished)
	assert_eq(decisions.size(), 1, "decision_requested once")
	assert_true(e.awaiting_decision)
	assert_true(e.can_finish_early())


func test_mission_stays_active_and_clock_held_while_awaiting() -> void:
	var decisions := []
	var finished := []
	var e := _prompted(decisions, finished)
	var held := e.elapsed
	for i in 20:
		e.tick(0.5, true)
	assert_eq(e.phase, MissionEngine.Phase.ACTIVE)
	assert_eq(finished.size(), 0, "no mission_finished while pending")
	assert_near(e.elapsed, held, 0.0001, "elapsed does not advance while awaiting")
	assert_false(e.can_fire(), "cannot fire while awaiting")


func test_continue_dismisses_prompt_and_keeps_mission_active() -> void:
	var decisions := []
	var finished := []
	var e := _prompted(decisions, finished)
	e.continue_mission()
	assert_false(e.awaiting_decision)
	assert_eq(e.phase, MissionEngine.Phase.ACTIVE)
	assert_true(e.can_fire(), "firing is possible again")
	e.tick(0.5, true)
	assert_true(e.is_active())
	assert_eq(finished.size(), 0)


func test_optional_goal_completes_after_continue() -> void:
	var decisions := []
	var finished := []
	var e := _prompted(decisions, finished)
	e.continue_mission()
	assert_eq(_status(e, "opt_a"), Status.PENDING)
	e.destroy_component("r1", "test")
	assert_eq(_status(e, "opt_a"), Status.COMPLETE)
	assert_true(e.is_active(), "one optional goal left")


func test_completing_all_optional_goals_after_continue_succeeds_on_settled_tick() -> void:
	var decisions := []
	var finished := []
	var e := _prompted(decisions, finished)
	e.continue_mission()
	e.destroy_component("r1", "test")
	e.destroy_component("r2", "test")
	assert_true(e.is_active(), "success waits for a settled tick")
	e.tick(0.1, false)
	assert_true(e.is_active(), "not settled yet")
	e.tick(0.1, true)
	assert_eq(e.phase, MissionEngine.Phase.SUCCEEDED)
	assert_eq(finished, [true])
	assert_eq(decisions.size(), 1, "no second prompt")


func test_finish_mission_ends_successfully() -> void:
	var decisions := []
	var finished := []
	var e := _prompted(decisions, finished)
	assert_true(e.finish_mission())
	assert_eq(e.phase, MissionEngine.Phase.SUCCEEDED)
	assert_eq(finished, [true])
	assert_false(e.awaiting_decision)


func test_finish_mission_fails_unfinished_optional_and_keeps_completed_ones() -> void:
	var decisions := []
	var finished := []
	var e := _prompted(decisions, finished)
	e.continue_mission()
	e.destroy_component("r1", "test")
	assert_true(e.finish_mission())
	assert_eq(_status(e, "opt_a"), Status.COMPLETE, "completed optional stays complete")
	assert_eq(_status(e, "opt_b"), Status.FAILED, "unfinished optional fails")
	assert_eq(_status(e, "opt_shots"), Status.COMPLETE, "unbroken max_shots constraint completes")
	assert_eq(_status(e, "core"), Status.COMPLETE)


func test_no_prompt_when_only_constraints_besides_primary() -> void:
	var decisions := []
	var finished := []
	var e := _prompted(decisions, finished, [_core_goal(), _opt_shots()])
	assert_eq(decisions.size(), 0, "constraints never trigger the prompt")
	assert_false(e.awaiting_decision)
	assert_eq(e.phase, MissionEngine.Phase.SUCCEEDED)
	assert_eq(finished, [true])


func test_no_prompt_when_no_optional_objectives_at_all() -> void:
	var decisions := []
	var finished := []
	var e := _prompted(decisions, finished, [_core_goal()])
	assert_eq(decisions.size(), 0)
	assert_eq(e.phase, MissionEngine.Phase.SUCCEEDED)
	assert_eq(finished, [true])


func test_no_prompt_when_all_optional_goals_already_complete() -> void:
	var decisions := []
	var finished := []
	var e := _engine()
	e.decision_requested.connect(func() -> void: decisions.append(true))
	e.mission_finished.connect(func(ok: bool) -> void: finished.append(ok))
	e.destroy_component("r1", "test")
	e.destroy_component("r2", "test")
	e.destroy_component("core", "test")
	e.tick(0.1, true)
	assert_eq(decisions.size(), 0)
	assert_false(e.awaiting_decision)
	assert_eq(e.phase, MissionEngine.Phase.SUCCEEDED)
	assert_eq(finished, [true])


func test_prompt_does_not_repeat_after_continue() -> void:
	var decisions := []
	var finished := []
	var e := _prompted(decisions, finished)
	e.continue_mission()
	for i in 10:
		e.tick(0.5, true)
	e.destroy_component("r1", "test")
	for i in 10:
		e.tick(0.5, true)
	assert_eq(decisions.size(), 1, "offered only once")
	assert_false(e.awaiting_decision)
	assert_true(e.is_active(), "opt_b still pending, mission continues")
	assert_eq(finished.size(), 0)


func test_running_out_of_ammo_after_continue_succeeds() -> void:
	var decisions := []
	var finished := []
	var e := _prompted(decisions, finished, [], 1)
	e.continue_mission()
	assert_true(e.fire(Vector2.RIGHT) != Vector2.ZERO)
	assert_false(e.has_ammo_left())
	assert_true(e.is_active(), "last shot may still land")
	e.tick(0.1, true)
	assert_eq(e.phase, MissionEngine.Phase.SUCCEEDED)
	assert_eq(finished, [true])


func test_finish_mission_refused_before_primary_complete() -> void:
	var e := _engine()
	assert_false(e.can_finish_early())
	assert_false(e.finish_mission())
	assert_true(e.is_active())
	assert_eq(_status(e, "opt_a"), Status.PENDING, "nothing was finalized")


func test_pending_optional_goals_excludes_constraints() -> void:
	var e := _engine()
	var ids := e.objectives.pending_optional_goals().map(func(o: MissionObjectives.Objective) -> String: return o.id)
	assert_eq(ids, ["opt_a", "opt_b"])


func test_mandatory_protect_still_fails_mission() -> void:
	var finished := []
	var objectives := [_core_goal(), _opt_a(), {"id": "p", "type": "protect", "mandatory": true, "label": "Spare", "targets": ["guard"]}]
	var e := _engine(objectives)
	e.mission_finished.connect(func(ok: bool) -> void: finished.append(ok))
	e.destroy_component("guard", "test")
	assert_eq(e.phase, MissionEngine.Phase.FAILED)
	assert_eq(finished, [false])
	assert_false(e.awaiting_decision)


func test_mandatory_max_shots_exceeded_still_fails_mission() -> void:
	var finished := []
	var objectives := [_core_goal(), _opt_a(), {"id": "m", "type": "max_shots", "mandatory": true, "label": "One shot", "limit": 1}]
	var e := _engine(objectives)
	e.mission_finished.connect(func(ok: bool) -> void: finished.append(ok))
	e.fire(Vector2.RIGHT)
	e.tick(2.0, false)
	assert_true(e.is_active(), "one shot is within the limit")
	e.fire(Vector2.RIGHT)
	assert_eq(e.phase, MissionEngine.Phase.FAILED)
	assert_eq(finished, [false])


func test_mandatory_failure_wins_over_prompt() -> void:
	var decisions := []
	var finished := []
	var objectives := [_core_goal(), _opt_a(), {"id": "p", "type": "protect", "mandatory": true, "label": "Spare", "targets": ["guard"]}]
	var e := _prompted(decisions, finished, objectives)
	assert_true(e.awaiting_decision, "prompt open with the primary done")
	e.destroy_component("guard", "test")
	assert_eq(e.phase, MissionEngine.Phase.FAILED)
	assert_eq(finished, [false])


func test_out_of_ammo_with_primary_incomplete_still_fails() -> void:
	var decisions := []
	var finished := []
	var e := _engine([], 1)
	e.decision_requested.connect(func() -> void: decisions.append(true))
	e.mission_finished.connect(func(ok: bool) -> void: finished.append(ok))
	e.fire(Vector2.RIGHT)
	e.destroy_component("r1", "test")
	e.tick(0.5, false)
	assert_true(e.is_active())
	e.tick(0.5, true)
	assert_eq(e.phase, MissionEngine.Phase.FAILED)
	assert_eq(finished, [false])
	assert_eq(decisions.size(), 0, "no prompt without the primary")
