extends TestCase
## MissionHud decision panel and the persistent Finish button.


func _hud() -> MissionHud:
	var hud := MissionHud.new()
	tree.root.add_child(hud)
	return hud


func _texts(hud: MissionHud) -> PackedStringArray:
	var texts := PackedStringArray()
	for node in hud.find_children("*", "Label", true, false):
		texts.append((node as Label).text)
	return texts


func test_decision_panel_copy_and_buttons() -> void:
	var hud := _hud()
	assert_false(hud.has_overlay())
	hud.show_decision()
	assert_true(hud.has_overlay(), "decision opens an overlay")
	var texts := _texts(hud)
	assert_true(texts.has("Primary objective complete"), "title text")
	assert_true(texts.has("Optional objectives remain. What next?"), "subtitle text")
	var keep_going: Button = hud.find_child("DecisionContinueButton", true, false)
	var finish: Button = hud.find_child("DecisionFinishButton", true, false)
	assert_true(keep_going != null and finish != null, "both buttons exist")
	if keep_going != null and finish != null:
		assert_eq(keep_going.text, "Continue")
		assert_eq(finish.text, "Finish")
	hud.hide_overlay()
	assert_false(hud.has_overlay(), "hide_overlay closes it")
	hud.queue_free()


func test_continue_emits_once_and_closes() -> void:
	var hud := _hud()
	var counts := {"continue": 0, "finish": 0}
	hud.continue_pressed.connect(func() -> void: counts["continue"] += 1)
	hud.finish_pressed.connect(func() -> void: counts["finish"] += 1)
	hud.show_decision()
	var keep_going: Button = hud.find_child("DecisionContinueButton", true, false)
	keep_going.pressed.emit()
	assert_eq(counts["continue"], 1, "continue emitted once")
	assert_eq(counts["finish"], 0, "finish not emitted")
	assert_false(hud.has_overlay(), "panel closed")
	hud.queue_free()


func test_decision_finish_emits_once_and_closes() -> void:
	var hud := _hud()
	var counts := {"continue": 0, "finish": 0}
	hud.continue_pressed.connect(func() -> void: counts["continue"] += 1)
	hud.finish_pressed.connect(func() -> void: counts["finish"] += 1)
	hud.show_decision()
	var finish: Button = hud.find_child("DecisionFinishButton", true, false)
	finish.pressed.emit()
	assert_eq(counts["finish"], 1, "finish emitted once")
	assert_eq(counts["continue"], 0, "continue not emitted")
	assert_false(hud.has_overlay(), "panel closed")
	hud.queue_free()


func test_finish_button_visibility_and_signal() -> void:
	var hud := _hud()
	var count := [0]
	hud.finish_pressed.connect(func() -> void: count[0] += 1)
	var button: Button = hud.find_child("FinishButton", true, false)
	assert_true(button != null, "FinishButton exists")
	if button == null:
		hud.queue_free()
		return
	assert_eq(button.text, "Finish")
	assert_false(button.visible, "hidden by default")
	hud.set_finish_available(true)
	assert_true(button.visible, "visible when available")
	button.pressed.emit()
	assert_eq(count[0], 1, "finish emitted")
	hud.set_finish_available(false)
	assert_false(button.visible, "hidden again")
	hud.queue_free()
