extends TestCase
## Quality gate for every authored campaign mission (data/missions/*.json), whatever the chapter:
## valid data, chapter-correct weapons, set dressing with the chapter's kit, every component kind
## available as a 3D model for its chapter, a recorded solution whose intended line fits the
## recommended shots, the facility standing untouched, and the intended solution winning.
## Run one chapter while authoring: `-- --only campaign_missions` with CAMPAIGN_FILTER, or the
## probe (tools/levels/probe_missions.gd) for replays.

const PHYSICS_SUITE := true
const Solver := preload("res://tools/levels/mission_solver.gd")
const SolutionBook := preload("res://tools/levels/solution_book.gd")
## Kinds every chapter can use without a chapter-specific model.
const SHARED_KINDS := []

var _materials := MaterialCatalog.load_from_file()
var _weapons := WeaponCatalog.load_from_file()
var _solutions: Dictionary = SolutionBook.load_all()


## Authored mission ids, optionally limited by the CAMPAIGN_FILTER environment variable
## (a chapter theme such as "vita", or one id).
func _ids() -> Array[String]:
	var ids: Array[String] = []
	var filter := OS.get_environment("CAMPAIGN_FILTER")
	for s in MissionCatalog.load_default().authored():
		if filter.is_empty() or s.id == filter or s.id.begins_with(filter + "_"):
			ids.append(s.id)
	return ids


func _definition(id: String) -> MissionDefinition:
	return MissionDefinition.load_from_file("res://data/missions/%s.json" % id, _materials, _weapons)


func test_every_mission_is_valid_with_chapter_weapons_and_a_solution() -> void:
	for id in _ids():
		var def := _definition(id)
		assert_true(def.is_valid(), "%s: %s" % [id, ", ".join(def.errors)])
		assert_true(_solutions.has(id) and not (_solutions[id] as Array).is_empty(), "%s has a recorded solution" % id)
		if not _solutions.has(id) or (_solutions[id] as Array).is_empty():
			continue
		var intended: Array = (_solutions[id] as Array)[0].steps
		for step: Dictionary in intended:
			assert_true(def.weapon_order.has(str(step.weapon)), "%s: solution uses unavailable %s" % [id, step.weapon])


func test_every_mission_has_set_dressing_and_chapter_models() -> void:
	var library := MissionView.assets()
	var chapters := ChapterCatalog.load_from_file()
	for id in _ids():
		var def := _definition(id)
		var env_path := "res://data/environments/%s.json" % id
		assert_true(FileAccess.file_exists(env_path), "%s has set dressing" % id)
		if not FileAccess.file_exists(env_path):
			continue
		var env: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(env_path))
		var theme := chapters.chapters[def.chapter - 1].theme
		assert_eq(str(env.get("chapter", "")), theme, "%s set dressing uses the %s kit" % [id, theme])
		for piece: Dictionary in env.get("pieces", []):
			assert_true(library.has_entry(str(piece.id)), "%s: set piece %s is integrated" % [id, piece.id])
		for c in def.components:
			var entry := library.component_entry(theme, c.kind, c.size)
			assert_false(entry.is_empty(), "%s: %s has a %s model for '%s'" % [id, c.id, theme, c.kind])
			if entry.is_empty():
				continue
			# The model is scaled to the physics box: stay inside its authored scale range (+10%).
			var reference: Array = entry.get("reference_size_px", [1, 1])
			var scale_range: Array = entry.get("scale_range", [0.5, 2.0])
			for axis in 2:
				var ratio := float(c.size[axis]) / float(reference[axis])
				assert_true(ratio >= float(scale_range[0]) * 0.9 and ratio <= float(scale_range[1]) * 1.1,
						"%s: %s (%s %s) is %.2fx its model on %s (allowed %s)" % [id, c.id, c.kind, c.size, ratio, "xy"[axis], scale_range])


func test_every_facility_stands_until_attacked() -> void:
	for id in _ids():
		var made: Dictionary = Solver.make_world(tree, "res://data/missions/%s.json" % id)
		if made.has("error"):
			continue
		var moved: Array[String] = await Solver.stand_check(tree, made.world)
		assert_eq(moved, [] as Array[String], "%s: components moved or took damage untouched" % id)
		Solver.free_world(tree, made)
		await tree.process_frame


func test_every_intended_solution_wins() -> void:
	for id in _ids():
		if not _solutions.has(id) or (_solutions[id] as Array).is_empty():
			continue
		var made: Dictionary = Solver.make_world(tree, "res://data/missions/%s.json" % id)
		if made.has("error"):
			continue
		var plan: Dictionary = (_solutions[id] as Array)[0]
		var result: Dictionary = await Solver.play(tree, made.world, plan.steps)
		assert_true(result.success, "%s '%s': %s %s" % [id, plan.get("name", ""), result.blocked, result.log])
		# Convention: the first recorded solution is the intended efficient line.
		assert_true(result.shots <= int(made.world.definition.recommended_shots), "%s: intended line took %d shots, recommended %d" % [id, result.shots, made.world.definition.recommended_shots])
		Solver.free_world(tree, made)
		await tree.process_frame
