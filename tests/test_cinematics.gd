extends TestCase
## Story sequence data: coverage of every chapter sequence, readability limits and validation.

const MAX_SUBTITLE_WORDS := 40


func test_shipped_catalog_is_valid() -> void:
	var catalog := CinematicCatalog.load_from_file()
	assert_true(catalog.is_valid(), ", ".join(catalog.errors))


func test_covers_every_chapter_sequence() -> void:
	var catalog := CinematicCatalog.load_from_file()
	for id in ChapterCatalog.load_from_file().sequence_ids():
		assert_true(catalog.has_sequence(id), "missing sequence '%s'" % id)
	# 11 game sequences plus the season-two teaser (teaser_2041), which no chapter plays yet.
	assert_true(catalog.has_sequence("teaser_2041"), "missing sequence 'teaser_2041'")
	assert_eq(catalog.order.size(), 12)


func test_slide_budget_and_readability() -> void:
	var catalog := CinematicCatalog.load_from_file()
	var slides := catalog.slide_count()
	assert_true(slides >= 40 and slides <= 50, "40-50 frames across sequences, got %d" % slides)
	for id in catalog.order:
		var sequence := catalog.get_sequence(id)
		for slide in sequence.slides:
			assert_true(slide.word_count() <= MAX_SUBTITLE_WORDS, "%s: subtitle too long (%d words)" % [id, slide.word_count()])
			for path: String in [slide.image, slide.voice]:
				assert_true(path.is_empty() or ResourceLoader.exists(path), "%s: missing asset %s" % [id, path])
	# Bible pacing: opening 65-90 s, chapter sequences under a minute.
	var opening := catalog.get_sequence("opening").estimated_seconds()
	assert_true(opening >= 65.0 and opening <= 95.0, "opening runs %.0f s" % opening)
	for id in catalog.order:
		if id != "opening" and id != "finale":
			assert_true(catalog.get_sequence(id).estimated_seconds() <= 60.0, "%s too long" % id)


func test_reading_time() -> void:
	var slide := CinematicCatalog.Slide.new()
	slide.subtitle = "Short."
	assert_near(slide.reading_seconds(), CinematicCatalog.MIN_SLIDE_SECONDS, 0.001)
	slide.subtitle = "word ".repeat(25).strip_edges()
	assert_near(slide.reading_seconds(), 25 / CinematicCatalog.READING_WORDS_PER_SECOND + CinematicCatalog.SLIDE_PADDING_SECONDS, 0.001)
	slide.duration = 2.0
	assert_near(slide.reading_seconds(), 2.0, 0.001, "explicit duration wins")


func test_rejects_invalid_sequences() -> void:
	var text := JSON.stringify({"sequences": [
		{"id": "a", "title": "A", "slides": [{"speaker": "villain", "subtitle": "x", "motion": "spin"}]},
		{"id": "a", "title": "A", "slides": [{"subtitle": "x", "image": "http://example.com/x.png"}]},
		{"id": "b", "title": "B", "theme": "nope", "slides": []},
	]})
	var catalog := CinematicCatalog.from_json_text(text)
	assert_false(catalog.is_valid())
	assert_eq(catalog.errors.size(), 6, ", ".join(catalog.errors))
	assert_false(CinematicCatalog.from_json_text("{}").is_valid())
	assert_false(CinematicCatalog.from_json_text("{\"sequences\": []}").is_valid())
