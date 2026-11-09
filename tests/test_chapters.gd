extends TestCase


func test_shipped_catalog_is_valid() -> void:
	var catalog := ChapterCatalog.load_from_file()
	assert_true(catalog.is_valid(), ", ".join(catalog.errors))
	assert_eq(catalog.chapters.size(), 5)
	assert_eq(catalog.total_levels(), 100)
	assert_eq(catalog.chapters[0].organization, "Helix Systems")
	assert_eq(catalog.chapters[0].year, 2089)
	assert_eq(catalog.chapters[4].title, "The Convergence")
	assert_eq(catalog.chapters[4].year, 2104)


func test_chapter_for_level_boundaries() -> void:
	var catalog := ChapterCatalog.load_from_file()
	assert_eq(catalog.chapter_for_level(1).id, "ch01")
	assert_eq(catalog.chapter_for_level(20).id, "ch01")
	assert_eq(catalog.chapter_for_level(21).id, "ch02")
	assert_eq(catalog.chapter_for_level(60).id, "ch03")
	assert_eq(catalog.chapter_for_level(61).id, "ch04")
	assert_eq(catalog.chapter_for_level(100).id, "ch05")
	assert_true(catalog.chapter_for_level(0) == null)
	assert_true(catalog.chapter_for_level(101) == null)


func test_every_shipped_level_has_a_chapter() -> void:
	var levels := LevelCatalog.load_from_file()
	var chapters := ChapterCatalog.load_from_file()
	for i in levels.levels.size():
		assert_true(chapters.chapter_for_level(i + 1) != null, "level %d has no chapter" % (i + 1))


func test_sequence_ids_are_unique_and_ordered() -> void:
	var ids := ChapterCatalog.load_from_file().sequence_ids()
	assert_eq(ids.size(), 11, "opening + 5 intros + 5 outros/finale")
	assert_eq(ids[0], "opening")
	assert_eq(ids[-1], "finale")
	var unique := {}
	for id in ids:
		unique[id] = true
	assert_eq(unique.size(), ids.size())


func test_rejects_gaps_and_duplicates() -> void:
	var text := JSON.stringify({"chapters": [
		_chapter("a", 1, 10, "a_in", "a_out"),
		_chapter("b", 12, 20, "a_in", "b_out"),
	]})
	var catalog := ChapterCatalog.from_json_text(text)
	assert_false(catalog.is_valid())
	assert_eq(catalog.errors.size(), 2, ", ".join(catalog.errors))


func test_rejects_missing_fields_and_bad_root() -> void:
	assert_false(ChapterCatalog.from_json_text("{\"chapters\": [{\"id\": \"x\"}]}").is_valid())
	assert_false(ChapterCatalog.from_json_text("[]").is_valid())
	assert_false(ChapterCatalog.from_json_text("{broken").is_valid())
	assert_false(ChapterCatalog.from_json_text("{\"chapters\": []}").is_valid())


func _chapter(id: String, first: int, last: int, intro: String, outro: String) -> Dictionary:
	return {
		"id": id, "title": "T", "organization": "O", "year": 2089, "theme": "t",
		"first_level": first, "last_level": last, "intro_sequence": intro, "outro_sequence": outro,
	}
