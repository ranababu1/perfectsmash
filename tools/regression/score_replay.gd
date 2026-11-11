extends Node
## Cross-platform scoring check. Plays fixed, scripted input sequences on the Helix mission (no
## touch input involved) and prints one `SCORE_REPLAY` line per sequence with the full score
## breakdown, then quits. Run the same build on desktop and on a device and compare the lines.
## tests/test_mission_world.gd uses the same sequences through `play()`.
##
## Desktop:  godot_console --headless --fixed-fps 60 tools/regression/score_replay.tscn
## Android:  build an isolated copy with make_eval_project.py --main tools/regression/score_replay.tscn

const MISSION := "res://data/missions/helix_01.json"
const ProbeAim := preload("res://tools/regression/probe_aim.gd")
## name -> list of [weapon_id, aim, frames_to_wait_after]. `aim` is a point in the physics plane,
## or "core": aim at wherever the AI core rests, the way a player uses the arc preview (so a
## tiny cross-platform difference in where it landed cannot turn a hit into a miss).
## frames_to_wait_after = SETTLE waits until the scene has settled (up to MAX_SETTLE_FRAMES).
const SETTLE := -1
const MAX_SETTLE_FRAMES := 600
const SEQUENCES := {
	# Kinetic route: two rounds break the left column, the collapse leaves the core critical, one finishing round.
	"kinetic_collapse_finish": [["kinetic_accelerator", Vector2(826, 512), 70], ["kinetic_accelerator", Vector2(826, 512), SETTLE], ["kinetic_accelerator", "core", 0]],
	# Expert line: one charge against the left column (30 degrees, 90% power), one finishing round.
	"column_breach_finish": [["breach_charge", Vector2(818, 170), SETTLE], ["kinetic_accelerator", "core", 0]],
	# A charge lobbed over the deck: damages without clearing the mission (runs to MAX_FRAMES).
	"breach_over_deck": [["breach_charge", Vector2(760, 120), 0]],
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
		if not engine.is_active():
			break
		engine.select_weapon(step[0])
		while not engine.can_fire():
			await tree.physics_frame
		var offset: Vector2
		if step[1] is String:
			var core := world.body_for("aura_core")
			if core == null:
				break
			offset = ProbeAim.aim(world, core).direction
			if offset == Vector2.ZERO:
				offset = core.global_position - world.muzzle_position()
		else:
			offset = (step[1] as Vector2) - world.muzzle_position()
		world.fire(offset, clampf(offset.length() / BREACH_FULL_POWER, 0.0, 1.0))
		if int(step[2]) == SETTLE:
			for i in MAX_SETTLE_FRAMES:
				if i > 30 and world.projectiles.is_empty() and world.is_settled():
					break
				await tree.physics_frame
		else:
			for i in int(step[2]):
				await tree.physics_frame
	for i in MAX_FRAMES:
		if not engine.is_active() or engine.awaiting_decision:
			break
		await tree.physics_frame
	# Optional goals still open: the scripted player chooses Finish at the decision prompt.
	if engine.awaiting_decision:
		engine.finish_mission()
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
