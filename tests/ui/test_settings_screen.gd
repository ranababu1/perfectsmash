extends TestCase
## SettingsScreen: initial values come from ProgressData; toggles emit and never write progress.


func test_initial_values_and_toggle_signals() -> void:
	var progress := ProgressData.new()
	progress.sound_enabled = true
	progress.music_enabled = false
	progress.vibration_enabled = true
	var screen := SettingsScreen.new(progress)
	tree.root.add_child(screen)
	assert_true(screen.sound_button.button_pressed)
	assert_false(screen.music_button.button_pressed)
	assert_true(screen.vibration_button.button_pressed)
	var seen := {}
	screen.sound_toggled.connect(func(on: bool) -> void: seen["sound"] = on)
	screen.music_toggled.connect(func(on: bool) -> void: seen["music"] = on)
	screen.vibration_toggled.connect(func(on: bool) -> void: seen["vibration"] = on)
	var backs := [0]
	screen.back_pressed.connect(func() -> void: backs[0] += 1)
	screen.sound_button.button_pressed = false
	screen.music_button.button_pressed = true
	screen.vibration_button.button_pressed = false
	assert_eq(seen.get("sound"), false)
	assert_eq(seen.get("music"), true)
	assert_eq(seen.get("vibration"), false)
	assert_true(progress.sound_enabled and not progress.music_enabled, "screen never writes progress")
	(screen.find_child("BackButton", true, false) as Button).pressed.emit()
	assert_eq(backs[0], 1)
	screen.queue_free()
