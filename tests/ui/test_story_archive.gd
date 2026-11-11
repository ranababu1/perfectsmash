extends TestCase
## StoryArchive: story-order list, locking by seen sequences, play and back signals.

var _requested := ""
var _closed := 0


func _make(progress: ProgressData) -> StoryArchive:
	var archive := StoryArchive.new(CinematicCatalog.load_from_file(), progress)
	tree.root.add_child(archive)
	_requested = ""
	_closed = 0
	archive.play_requested.connect(func(id: String) -> void: _requested = id)
	archive.closed.connect(func() -> void: _closed += 1)
	return archive


func _entry(archive: StoryArchive, id: String) -> Button:
	return archive.find_child("Entry_" + id, true, false) as Button


func test_lists_story_in_order_without_teaser() -> void:
	var archive := _make(ProgressData.new())
	var ids := archive.entry_ids()
	assert_eq(ids.size(), 11)
	assert_eq(ids[0], "opening")
	assert_eq(ids[1], "ch01_intro")
	assert_eq(ids[2], "ch01_outro")
	assert_eq(ids[ids.size() - 1], "finale")
	assert_false(ids.has("teaser_2041"))
	for id in ids:
		assert_true(_entry(archive, id) != null, "entry for %s" % id)
	archive.queue_free()


func test_locked_and_unlocked() -> void:
	var progress := ProgressData.new()
	var archive := _make(progress)
	assert_false(_entry(archive, "opening").disabled, "opening always available")
	assert_true(_entry(archive, "ch01_intro").disabled)
	assert_true(_entry(archive, "ch01_intro").text.contains("Locked"))
	progress.mark_sequence_seen("ch01_intro")
	archive.refresh()
	await wait_process_frames(2)
	assert_false(_entry(archive, "ch01_intro").disabled)
	assert_false(_entry(archive, "ch01_intro").text.contains("Locked"))
	assert_true(_entry(archive, "ch01_outro").disabled)
	archive.queue_free()


func test_play_requested_only_for_available() -> void:
	var progress := ProgressData.new()
	progress.mark_sequence_seen("ch01_intro")
	var archive := _make(progress)
	_entry(archive, "ch01_intro").pressed.emit()
	assert_eq(_requested, "ch01_intro")
	_requested = ""
	_entry(archive, "finale").pressed.emit()
	assert_eq(_requested, "", "locked entries emit nothing")
	_entry(archive, "opening").pressed.emit()
	assert_eq(_requested, "opening")
	archive.queue_free()


func test_back_button_and_cancel_emit_closed() -> void:
	var archive := _make(ProgressData.new())
	(archive.find_child("BackButton", true, false) as Button).pressed.emit()
	assert_eq(_closed, 1)
	var cancel := InputEventAction.new()
	cancel.action = "ui_cancel"
	cancel.pressed = true
	archive._unhandled_input(cancel)
	assert_eq(_closed, 2)
	archive.queue_free()
