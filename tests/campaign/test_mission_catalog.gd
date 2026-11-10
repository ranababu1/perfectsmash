extends TestCase
## MissionCatalog: the frozen campaign contract (slot naming, level numbers, linear unlocks), and
## the gate every authored mission file must pass (id and chapter agree with its slot, data valid).


func _fake(authored_ids: Array) -> MissionCatalog:
	var exists := func(path: String) -> bool: return authored_ids.has(path.get_file().get_basename())
	return MissionCatalog.from_chapters(ChapterCatalog.load_from_file(), exists)


func test_hundred_slots_named_by_chapter_theme() -> void:
	var catalog := _fake([])
	assert_true(catalog.is_valid(), ", ".join(catalog.errors))
	assert_eq(catalog.slots.size(), 100)
	assert_eq(catalog.slots[0].id, "helix_01")
	assert_eq(catalog.slots[19].id, "helix_20")
	assert_eq(catalog.slots[20].id, "vita_01")
	assert_eq(catalog.slots[20].level_number, 21)
	assert_eq(catalog.slots[40].id, "nova_grid_01")
	assert_eq(catalog.slots[60].id, "civitas_01")
	assert_eq(catalog.slots[99].id, "meridian_20")
	assert_eq(catalog.slots[99].level_number, 100)
	assert_eq(catalog.slots[99].chapter.number, 5)
	assert_eq(catalog.slot("vita_05").path, "res://data/missions/vita_05.json")
	assert_eq(catalog.chapter_slots(3).size(), 20)
	assert_eq(catalog.first_authored_id(), "")


func test_linear_unlocks_skip_unauthored_slots() -> void:
	var catalog := _fake(["helix_01", "helix_02", "vita_01"])
	var progress := ProgressData.new()
	assert_true(catalog.is_unlocked("helix_01", progress))
	assert_false(catalog.is_unlocked("helix_02", progress))
	assert_false(catalog.is_unlocked("helix_03", progress), "unauthored slots are never unlocked")
	assert_eq(catalog.next_authored_id("helix_02"), "vita_01")
	assert_eq(catalog.previous_authored_id("vita_01"), "helix_02")
	assert_eq(catalog.next_authored_id("vita_01"), "")
	progress.mission_results["helix_01"] = {"completed": true}
	assert_true(catalog.is_unlocked("helix_02", progress))
	assert_false(catalog.is_unlocked("vita_01", progress))
	progress.mission_results["helix_02"] = {"completed": true}
	assert_true(catalog.is_unlocked("vita_01", progress))
	assert_false(catalog.is_unlocked("helix_02", null), "no progress: only the first is open")


func test_invalid_chapters_make_an_invalid_catalog() -> void:
	var catalog := MissionCatalog.from_chapters(ChapterCatalog.from_json_text("{}"))
	assert_false(catalog.is_valid())
	assert_eq(catalog.slots.size(), 0)


## Gate for content work: every mission file on disk sits in a slot and agrees with it.
func test_every_authored_mission_matches_its_slot_and_is_valid() -> void:
	var catalog := MissionCatalog.load_default()
	assert_true(catalog.is_valid(), ", ".join(catalog.errors))
	assert_true(catalog.slot("helix_01").authored, "the Helix reference mission is level 1")
	var materials := MaterialCatalog.load_from_file()
	var weapons := WeaponCatalog.load_from_file()
	for s in catalog.authored():
		var definition := MissionDefinition.load_from_file(s.path, materials, weapons)
		assert_true(definition.is_valid(), "%s: %s" % [s.id, ", ".join(definition.errors)])
		assert_eq(definition.id, s.id, "%s: id must match the file name" % s.path)
		assert_eq(definition.chapter, s.chapter.number, "%s: chapter must be %d" % [s.id, s.chapter.number])
	var dir := DirAccess.open(MissionCatalog.MISSIONS_DIR)
	for file in dir.get_files():
		if file.ends_with(".json"):
			assert_true(catalog.slot(file.get_basename()) != null, "%s is not a campaign slot name" % file)
