extends Node
## Cross-platform scoring check. Plays fixed, scripted input sequences on the Helix mission (no
## touch input involved) and prints one `SCORE_REPLAY` line per sequence with the full score
## breakdown, then quits. Run the same build on desktop and on a device and compare the lines.
## tests/test_mission_world.gd uses the same sequences through `play()`.
##
## Desktop:  godot_console --headless --fixed-fps 60 tools/regression/score_replay.tscn
## Android:  build an isolated copy with make_eval_project.py --main tools/regression/score_replay.tscn

const MISSION := "res://data/missions/helix_01.json"
## name -> list of [weapon_id, aim_point_in_physics_plane, frames_to_wait_after]
const SEQUENCES := {
	"kinetic_then_breach": [["kinetic_accelerator", Vector2(830, 462), 20], ["breach_charge", Vector2(760, 120), 0]],
	"breach_only": [["breach_charge", Vector2(760, 120), 0]],
	"two_kinetic_column": [["kinetic_accelerator", Vector2(830, 462), 70], ["kinetic_accelerator", Vector2(830, 462), 0]],
}
const BREACH_FULL_POWER := 760.0
const MAX_FRAMES := 1200


func _ready() -> void:
	_run.call_deferred()


func _run() -> void:
	var scoring := MissionScoring.load_from_file()
	for sequence_name: String in SEQUENCES:
		var result: Dictionary = await play(self, sequence_name)
		var engine: MissionEngine = result.engine
		print("SCORE_REPLAY %s %s" % [sequence_name, JSON.stringify(summary(scoring, engine))])
		(result.viewport as Node).queue_free()
		await get_tree().physics_frame
	get_tree().quit()


## Builds an isolated Helix world under `parent`, plays the sequence and waits for the mission
## to end. Returns {engine, world, viewport}.
static func play(parent: Node, sequence_name: String) -> Dictionary:
	var materials := MaterialCatalog.load_from_file()
	var weapons := WeaponCatalog.load_from_file()
	var def := MissionDefinition.load_from_file(MISSION, materials, weapons)
	var engine := MissionEngine.new(def, materials, weapons)
	var viewport := SubViewport.new()
	viewport.render_target_update_mode = SubViewport.UPDATE_DISABLED
	parent.add_child(viewport)
	var world := MissionWorld.new()
	viewport.add_child(world)
	world.setup(def, engine, materials)
	var tree := parent.get_tree()
	for step: Array in SEQUENCES[sequence_name]:
		engine.select_weapon(step[0])
		var offset: Vector2 = step[1] - world.muzzle_position()
		world.fire(offset, clampf(offset.length() / BREACH_FULL_POWER, 0.0, 1.0))
		for i in int(step[2]):
			await tree.physics_frame
	for i in MAX_FRAMES:
		if not engine.is_active():
			break
		await tree.physics_frame
	return {"engine": engine, "world": world, "viewport": viewport}


static func summary(scoring: MissionScoring, engine: MissionEngine) -> Dictionary:
	var s := scoring.score(engine)
	return {
		"phase": engine.phase,
		"mission_points": s.mission_points,
		"research_data": s.research_data,
		"points": s.points,
		"structural_damage": snappedf(engine.structural_damage_fraction(), 0.0001),
		"shots": engine.shots_fired(),
		"effective_shots": engine.effective_shots,
		"physics_frames": roundi(engine.elapsed * 60.0),
		"os": OS.get_name(),
		"arch": Engine.get_architecture_name(),
	}
