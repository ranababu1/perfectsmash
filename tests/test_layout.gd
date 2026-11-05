extends TestCase
## Plan M4 "usable on multiple screen sizes": lays out the menu, settings, HUD, pause and result
## screens at the canvas sizes common phone and tablet shapes produce (stretch mode "expand" keeps
## 720 units of height on wide screens and 1280 of width on tall ones), and checks that every
## button is on screen, large enough to touch, and not overlapping another.

## Aspect name -> visible canvas size in units.
const CANVASES := {
	"16:9": Vector2i(1280, 720),
	"19.5:9": Vector2i(1560, 720),
	"20:9": Vector2i(1600, 720),
	"21:9": Vector2i(1680, 720),
	"16:10 tablet": Vector2i(1280, 800),
	"4:3 tablet": Vector2i(1280, 960),
}
const MIN_TOUCH := 60.0
## Animations rise into place by up to 16 units; allow that while they finish.
const SETTLE_SECONDS := 0.45


func _host(size: Vector2i) -> SubViewport:
	var viewport := SubViewport.new()
	viewport.size = size
	viewport.render_target_update_mode = SubViewport.UPDATE_DISABLED
	tree.root.add_child(viewport)
	return viewport


func _settle() -> void:
	await tree.create_timer(SETTLE_SECONDS).timeout


func _buttons(root: Node) -> Array[Button]:
	var list: Array[Button] = []
	for node in root.find_children("*", "Button", true, false):
		var b := node as Button
		if b.is_visible_in_tree():
			list.append(b)
	return list


func _check_buttons(buttons: Array[Button], bounds: Rect2, label: String) -> void:
	for i in buttons.size():
		var r := buttons[i].get_global_rect()
		if not bounds.grow(0.5).encloses(r):
			failures.append("%s: button '%s' %s outside %s" % [label, buttons[i].text, r, bounds])
		if minf(r.size.x, r.size.y) < MIN_TOUCH:
			failures.append("%s: button '%s' too small %s" % [label, buttons[i].text, r.size])
		for j in range(i + 1, buttons.size()):
			var other := buttons[j].get_global_rect()
			if r.intersects(other.grow(-0.5)):
				failures.append("%s: buttons '%s' and '%s' overlap" % [label, buttons[i].text, buttons[j].text])


func _progress(catalog: LevelCatalog) -> ProgressData:
	var progress := ProgressData.new()
	for i in catalog.levels.size() - 1:
		progress.record_win(catalog.levels[i].id, 1 + i % 3, 2)
	return progress


func test_menu_and_settings_fit_every_canvas() -> void:
	var catalog := LevelCatalog.load_from_file()
	for aspect: String in CANVASES:
		var size: Vector2i = CANVASES[aspect]
		var viewport := _host(size)
		var menu := MenuScreen.new(catalog, _progress(catalog))
		menu.theme = UiKit.make_theme()
		viewport.add_child(menu)
		await _settle()
		var bounds := Rect2(Vector2.ZERO, Vector2(size))
		_check_buttons(_buttons(menu), bounds, "menu " + aspect)
		var bar: Control = menu.find_child("TopBar", true, false)
		var grid: Control = menu.find_child("LevelGrid", true, false)
		assert_false(bar.get_global_rect().intersects(grid.get_global_rect()), "menu %s: top bar overlaps level grid" % aspect)

		var settings := SettingsPanel.new(ProgressData.new())
		menu.add_child(settings)
		await _settle()
		_check_buttons(_buttons(settings), bounds, "settings " + aspect)
		tree.root.remove_child(viewport)
		viewport.queue_free()


func test_hud_overlays_fit_every_canvas() -> void:
	var def: LevelDefinition = LevelCatalog.load_from_file().levels[0]
	for aspect: String in CANVASES:
		var size: Vector2i = CANVASES[aspect]
		var bounds := Rect2(Vector2.ZERO, Vector2(size))
		var viewport := _host(size)
		var hud := Hud.new()
		hud.theme = UiKit.make_theme()
		viewport.add_child(hud)
		hud.set_level(def, 20)
		hud.set_shots(3, 3)
		await _settle()
		_check_buttons(_buttons(hud), bounds, "hud " + aspect)
		hud.show_pause(true, true, true)
		await _settle()
		_check_buttons(_buttons(hud._overlay), bounds, "pause " + aspect)
		hud.show_result(true, 2, 2, true, 1)
		await _settle()
		_check_buttons(_buttons(hud._overlay), bounds, "win " + aspect)
		hud.show_result(false, 0, 3, true)
		await _settle()
		_check_buttons(_buttons(hud._overlay), bounds, "lose " + aspect)
		tree.root.remove_child(viewport)
		viewport.queue_free()


## A phone with a camera cutout on the left in landscape: corner controls move clear of it.
func test_hud_respects_safe_area_insets() -> void:
	var viewport := _host(Vector2i(1600, 720))
	var hud := Hud.new()
	hud.theme = UiKit.make_theme()
	viewport.add_child(hud)
	hud.set_level(LevelCatalog.load_from_file().levels[0], 1)
	var insets := Vector4(90, 0, 40, 24)
	hud.apply_insets(insets)
	await _settle()
	assert_true(hud._info_chip.get_global_rect().position.x >= insets.x, "info chip clear of the left cutout")
	for b in _buttons(hud):
		assert_true(b.get_global_rect().end.x <= 1600 - insets.z + 0.5, "button clear of the right inset")
	assert_true(hud._hint_row.get_global_rect().end.y <= 720 - insets.w, "hint clear of the bottom inset")
	tree.root.remove_child(viewport)
	viewport.queue_free()


func test_safe_area_conversion() -> void:
	# 2400x1080 phone, 100px cutout on the left, canvas 1600x720 (scale 2/3).
	var insets := SafeArea.insets_for(Vector2i(2400, 1080), Rect2i(100, 0, 2300, 1080), Vector2(1600, 720))
	assert_near(insets.x, 66.667, 0.01, "left")
	assert_near(insets.z, 0.0, 0.001, "right")
	assert_eq(SafeArea.insets_for(Vector2i(2400, 1080), Rect2i(0, 0, 2400, 1080), Vector2(1600, 720)), Vector4.ZERO, "no cutout")
	assert_eq(SafeArea.insets_for(Vector2i.ZERO, Rect2i(), Vector2(1280, 720)), Vector4.ZERO, "no window")
	var bogus := SafeArea.insets_for(Vector2i(2400, 1080), Rect2i(2000, 0, 400, 1080), Vector2(1600, 720))
	assert_near(bogus.x, 2400 * SafeArea.MAX_SHARE * (1600.0 / 2400.0), 0.01, "huge inset capped")
