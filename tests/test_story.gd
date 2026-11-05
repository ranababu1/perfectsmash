extends TestCase
## The storyline must cover every level: a briefing and a debrief per mission, known speakers,
## chapters that tile the whole campaign in order, and chapter cards at chapter starts.

const MAX_LINE_LENGTH := 160


func test_story_loads_and_covers_every_level() -> void:
	var story := StoryCatalog.load_from_file()
	assert_true(story.is_valid(), "story valid: %s" % ", ".join(story.errors))
	var catalog := LevelCatalog.load_from_file()
	var problems := story.validate_against(catalog.ids())
	assert_true(problems.is_empty(), ", ".join(problems))
	assert_eq(story.chapters.size(), 5, "five chapters")


func test_lines_fit_the_dialogue_box() -> void:
	var story := StoryCatalog.load_from_file()
	for id: String in story.missions:
		for line in story.briefing(0, id) + story.debrief(id):
			if line.text.length() > MAX_LINE_LENGTH:
				failures.append("%s line too long (%d): %s" % [id, line.text.length(), line.text])


func test_chapter_start_opens_with_chapter_card() -> void:
	var story := StoryCatalog.load_from_file()
	var ids := LevelCatalog.load_from_file().ids()
	for c in story.chapters:
		var index: int = c.first - 1
		assert_true(story.is_chapter_start(index), "%s starts a chapter" % ids[index])
		var lines := story.briefing(index, ids[index])
		assert_eq(lines[0].speaker, "log", "chapter %s opens with the mission log" % c.title)
		assert_true(lines.size() > story.missions[ids[index]].briefing.size(), "intro added")
	assert_false(story.is_chapter_start(1), "second mission is not a chapter start")
	assert_eq(story.chapter_index(0), 0)
	assert_eq(story.chapter_index(99), 4)
	assert_eq(story.chapter_index(100), -1)


func test_fail_lines_rotate_deterministically() -> void:
	var story := StoryCatalog.load_from_file()
	var a := story.fail_line("fail", 3)
	var b := story.fail_line("fail", 3)
	assert_eq(a.text, b.text, "same pick, same line")
	assert_eq(story.fail_line("fail_ally", 0).speaker, "juno", "drone loss line")
	assert_false(story.fail_line("no_such_pool", 1).is_empty(), "unknown pool falls back")
	assert_true(story.speakers.has("architect"))


func test_rejects_bad_story() -> void:
	var story := StoryCatalog.new()
	story._parse({"speakers": {"a": {"name": "A"}}, "missions": {"X": {"briefing": [["b", "who?"]], "debrief": []}}})
	assert_false(story.is_valid(), "unknown speaker and empty debrief rejected")
	var ids: Array[String] = ["X", "Y"]
	assert_false(story.validate_against(ids).is_empty(), "missing level Y reported")
