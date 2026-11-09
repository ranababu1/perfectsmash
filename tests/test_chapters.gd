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


func test_every_chapter_theme_exists() -> void:
	for chapter in ChapterCatalog.load_from_file().chapters:
		assert_true(ChapterTheme.has_key(chapter.theme), "missing theme '%s'" % chapter.theme)
		assert_eq(ChapterTheme.for_key(chapter.theme).key, chapter.theme)
	assert_eq(ChapterTheme.for_key("nope").key, ChapterTheme.DEFAULT_KEY, "unknown key falls back")


## Readability rule: scenery stays dark so blocks, targets and the projectile stand out.
func test_scenery_is_darker_than_gameplay_pieces() -> void:
	var pieces := [Palette.WOOD, Palette.STONE, Palette.TARGET, Palette.PROJECTILE]
	var darkest_piece := 1.0
	for c: Color in pieces:
		darkest_piece = minf(darkest_piece, c.get_luminance())
	for key: String in ChapterTheme.THEMES:
		var t := ChapterTheme.for_key(key)
		for c: Color in [t.sky_top, t.sky_bottom, t.hills_far, t.hills_near, t.ground]:
			assert_true(c.get_luminance() < 0.25, "%s scenery too bright: %s" % [key, c])
			assert_true(darkest_piece - c.get_luminance() > 0.2, "%s scenery too close to piece colours" % key)


func test_chapter_caption() -> void:
	var main_script := preload("res://scripts/main.gd")
	var chapter := ChapterCatalog.load_from_file().chapter_for_level(41)
	assert_eq(main_script.chapter_caption(chapter), "CHAPTER III  ·  NOVA GRID  ·  2096")
	assert_eq(main_script.chapter_caption(null), "")
