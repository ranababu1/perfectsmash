extends TestCase
## UpgradesScreen: balance, locked weapons, purchases, max level, funds, signals.

const LOCKED_JSON := """{"weapons": [
	{"id": "alpha", "display_name": "Alpha", "unlock_chapter": 1, "delivery": "direct",
	 "stats": {"launch_speed": 800, "min_launch_speed": 800, "gravity_scale": 1, "projectile_radius": 10,
		"projectile_mass": 2, "impact_damage": 90, "penetration": 0.1, "blast_damage": 0, "blast_radius": 0,
		"blast_impulse": 0, "blast_edge_falloff": 0, "fuse_seconds": 0, "ammunition": 5, "cooldown": 1.0,
		"aim_preview_seconds": 0.5},
	 "upgrades": {"impact_energy": {"stat": "impact_damage", "op": "multiply", "levels": [1.2, 1.4, 1.6], "costs": [10, 20, 30]},
		"energy_capacity": {"stat": "ammunition", "op": "add", "levels": [1, 2, 3], "costs": [5, 5, 5]}}},
	{"id": "beta", "display_name": "Beta", "unlock_chapter": 3, "delivery": "direct",
	 "stats": {"launch_speed": 800, "min_launch_speed": 800, "gravity_scale": 1, "projectile_radius": 10,
		"projectile_mass": 2, "impact_damage": 50, "penetration": 0.0, "blast_damage": 0, "blast_radius": 0,
		"blast_impulse": 0, "blast_edge_falloff": 0, "fuse_seconds": 0, "ammunition": 4, "cooldown": 1.0,
		"aim_preview_seconds": 0.5},
	 "upgrades": {"impact_energy": {"stat": "impact_damage", "op": "multiply", "levels": [1.2, 1.4, 1.6], "costs": [10, 20, 30]}}}
]}"""


func _make(progress: ProgressData, chapter: int = 1, catalog: WeaponCatalog = null) -> UpgradesScreen:
	var screen := UpgradesScreen.new(catalog if catalog != null else WeaponCatalog.from_json_text(LOCKED_JSON), progress, chapter)
	tree.root.add_child(screen)
	return screen


func _buy_button(screen: UpgradesScreen, attribute: String) -> Button:
	return screen.find_child("Buy_" + attribute, true, false) as Button


func test_data_catalog_builds_a_row_per_upgrade() -> void:
	var catalog := WeaponCatalog.load_from_file()
	assert_true(catalog.is_valid(), "weapons.json valid: %s" % ", ".join(catalog.errors))
	var progress := ProgressData.new()
	progress.research_data = 500
	var screen := _make(progress, 99, catalog)
	for id in catalog.order:
		assert_true(screen.find_child("Weapon_" + id, true, false) != null, "button for " + id)
		screen.select_weapon(id)
		assert_eq(screen.selected_weapon, id)
		for attribute: String in catalog.get_weapon(id).upgrades:
			assert_true(_buy_button(screen, attribute) != null, "%s/%s row" % [id, attribute])
			assert_true(screen.next_effect_text(id, attribute) != "", "effect text for %s/%s" % [id, attribute])
	screen.queue_free()


func test_balance_and_effect_text() -> void:
	var progress := ProgressData.new()
	progress.research_data = 42
	var screen := _make(progress)
	assert_true(screen.balance_label.text.contains("42"), "balance shown")
	assert_eq(screen.next_effect_text("alpha", "impact_energy"), "Impact damage 90 → 108")
	assert_eq(screen.next_effect_text("alpha", "energy_capacity"), "Ammunition 5 → 6")
	assert_eq(_buy_button(screen, "impact_energy").text, "Buy  10")
	screen.queue_free()


func test_locked_weapon_is_visible_but_not_purchasable() -> void:
	var progress := ProgressData.new()
	progress.research_data = 1000
	var screen := _make(progress, 1)
	var beta := screen.find_child("Weapon_beta", true, false) as Button
	assert_true(beta.disabled)
	assert_true(beta.text.contains("Unlocks in Chapter 3"))
	screen.select_weapon("beta")
	assert_eq(screen.selected_weapon, "alpha", "locked weapon cannot be selected")
	var seen := [0]
	screen.purchased.connect(func(_w: String, _a: String) -> void: seen[0] += 1)
	assert_false(screen.buy("beta", "impact_energy"))
	assert_eq(progress.research_data, 1000)
	assert_eq(progress.upgrade_level("beta", "impact_energy"), 0)
	assert_eq(seen[0], 0)
	screen.queue_free()


func test_buying_deducts_levels_up_and_signals() -> void:
	var progress := ProgressData.new()
	progress.research_data = 100
	var screen := _make(progress)
	var seen := []
	screen.purchased.connect(func(w: String, a: String) -> void: seen.append([w, a]))
	_buy_button(screen, "impact_energy").pressed.emit()
	assert_eq(progress.research_data, 90)
	assert_eq(progress.upgrade_level("alpha", "impact_energy"), 1)
	assert_eq(seen, [["alpha", "impact_energy"]])
	assert_true(screen.balance_label.text.contains("90"), "balance refreshed")
	assert_eq(screen.next_effect_text("alpha", "impact_energy"), "Impact damage 108 → 126")
	assert_eq(_buy_button(screen, "impact_energy").text, "Buy  20", "next cost shown")
	screen.queue_free()


func test_max_level_and_insufficient_funds() -> void:
	var progress := ProgressData.new()
	progress.research_data = 25
	var screen := _make(progress)
	assert_true(screen.buy("alpha", "impact_energy"))
	assert_true(_buy_button(screen, "impact_energy").disabled, "20 needed, 15 left")
	assert_false(screen.buy("alpha", "impact_energy"))
	assert_eq(progress.upgrade_level("alpha", "impact_energy"), 1)
	assert_eq(progress.research_data, 15)
	progress.research_data = 100
	for i in 3:
		screen.buy("alpha", "energy_capacity")
	assert_eq(progress.upgrade_level("alpha", "energy_capacity"), 3)
	var button := _buy_button(screen, "energy_capacity")
	assert_eq(button.text, "Max")
	assert_true(button.disabled)
	var before := progress.research_data
	assert_false(screen.buy("alpha", "energy_capacity"))
	assert_eq(progress.research_data, before)
	assert_eq(screen.next_effect_text("alpha", "energy_capacity"), "")
	screen.queue_free()


func test_back_button_and_cancel_emit_closed() -> void:
	var screen := _make(ProgressData.new())
	var closes := [0]
	screen.closed.connect(func() -> void: closes[0] += 1)
	(screen.find_child("BackButton", true, false) as Button).pressed.emit()
	assert_eq(closes[0], 1)
	var cancel := InputEventAction.new()
	cancel.action = "ui_cancel"
	cancel.pressed = true
	screen._unhandled_input(cancel)
	assert_eq(closes[0], 2)
	screen.queue_free()
