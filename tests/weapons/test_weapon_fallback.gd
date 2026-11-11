extends TestCase
## Automatic weapon fallback (owner report, rc2): an empty weapon never stays selected while
## another weapon has ammunition. Rules live in MissionEngine; the screen, HUD and operative follow
## engine.weapon_selected. The last screen test runs the real app with physics.

const PHYSICS_SUITE := true
const TEST_SAVE := "user://test_weapon_fallback_progress.json"
const MainScript := preload("res://scripts/main.gd")

var _materials := MaterialCatalog.load_from_file()
var _weapons := WeaponCatalog.load_from_file()


## `loadout`: Array of [weapon id, ammunition] in mission order.
func _engine(loadout: Array) -> MissionEngine:
	var weapons := {}
	for entry: Array in loadout:
		weapons[entry[0]] = {"ammunition": entry[1]}
	var data := {
		"id": "t", "name": "T", "chapter": 5, "width": 1600, "ground_y": 640, "operative": [100, 640],
		"recommended_shots": 1, "target_time": 30, "weapons": weapons,
		"components": [
			{"id": "base", "kind": "k", "material": "concrete", "x": 800, "y": 560, "w": 40, "h": 160},
			{"id": "core", "kind": "ai_core", "material": "electronic_module", "x": 800, "y": 450, "w": 50, "h": 50, "critical_asset": true, "supports": ["base"]},
		],
		"objectives": [{"id": "core", "type": "destroy_critical", "mandatory": true, "label": "L", "targets": ["core"]}],
	}
	var def := MissionDefinition.from_json_text(JSON.stringify(data, "", false), _materials, _weapons)
	assert_true(def.is_valid(), ", ".join(def.errors))
	return MissionEngine.new(def, _materials, _weapons)


## Fires the selected weapon and lets its reload finish (no physics: the shot "resolves" at once).
func _shoot(e: MissionEngine) -> void:
	var weapon := e.selected_weapon()
	assert_true(e.fire(Vector2(1, -0.2), 1.0) != Vector2.ZERO, "%s fires" % weapon.id())
	e.tick(float(weapon.stats.cooldown) + 0.01, false)


func test_last_round_switches_once_the_shot_resolves() -> void:
	var e := _engine([["kinetic_accelerator", 1], ["breach_charge", 2]])
	var selected := []
	e.weapon_selected.connect(func(id: String) -> void: selected.append(id))
	assert_true(e.fire(Vector2.RIGHT) != Vector2.ZERO)
	assert_eq(e.selected_weapon_id, "kinetic_accelerator", "no switch in the middle of the shot")
	assert_true(e.auto_select_pending, "the switch waits for the shot to resolve")
	assert_eq(e.apply_pending_auto_select(), "breach_charge")
	assert_eq(e.selected_weapon_id, "breach_charge")
	assert_false(e.auto_select_pending)
	assert_eq(selected, ["breach_charge"], "one selection signal, no recursion")
	assert_eq(e.apply_pending_auto_select(), "", "applying twice does nothing")


func test_fallback_order_is_deterministic_and_wraps() -> void:
	var e := _engine([["kinetic_accelerator", 2], ["breach_charge", 1], ["penetrator", 1], ["temporal_lance", 1]])
	assert_eq(e.usable_weapon_after("breach_charge"), "penetrator", "next in mission order")
	assert_eq(e.usable_weapon_after("temporal_lance"), "kinetic_accelerator", "wraps to the start")
	assert_true(e.select_weapon("penetrator"))
	_shoot(e)
	assert_eq(e.apply_pending_auto_select(), "temporal_lance", "after penetrator comes the lance")
	_shoot(e)
	assert_eq(e.apply_pending_auto_select(), "kinetic_accelerator", "after the last weapon, wrap to the first")
	assert_eq(e.usable_weapon_after("kinetic_accelerator"), "breach_charge", "empty weapons are skipped, usable ones kept")


func test_manual_selection_of_an_empty_weapon_falls_back() -> void:
	var e := _engine([["kinetic_accelerator", 3], ["breach_charge", 1], ["penetrator", 2]])
	assert_true(e.select_weapon("breach_charge"))
	_shoot(e)
	e.apply_pending_auto_select()
	assert_eq(e.selected_weapon_id, "penetrator")
	assert_true(e.select_weapon("kinetic_accelerator"), "a weapon with ammunition is selected as asked")
	assert_eq(e.selected_weapon_id, "kinetic_accelerator", "the player's choice is kept while it has ammunition")
	assert_true(e.select_weapon("breach_charge"), "asking for the empty weapon still selects a usable one")
	assert_eq(e.selected_weapon_id, "penetrator", "the next usable weapon after the empty one")
	assert_true(e.selected_weapon().has_ammo(), "an empty weapon never stays selected")


func test_manual_choice_cancels_a_pending_switch() -> void:
	var e := _engine([["kinetic_accelerator", 1], ["breach_charge", 2], ["penetrator", 2]])
	e.fire(Vector2.RIGHT)
	assert_true(e.auto_select_pending)
	assert_true(e.select_weapon("penetrator"))
	assert_false(e.auto_select_pending, "the player chose; no automatic override")
	assert_eq(e.apply_pending_auto_select(), "")
	assert_eq(e.selected_weapon_id, "penetrator")


func test_single_usable_weapon_stays_selected() -> void:
	var e := _engine([["kinetic_accelerator", 3], ["breach_charge", 1]])
	assert_true(e.select_weapon("breach_charge"))
	_shoot(e)
	assert_eq(e.apply_pending_auto_select(), "kinetic_accelerator")
	var selected := []
	e.weapon_selected.connect(func(id: String) -> void: selected.append(id))
	assert_true(e.select_weapon("breach_charge"), "the only usable weapon is kept")
	assert_eq(e.selected_weapon_id, "kinetic_accelerator")
	assert_eq(selected, [], "no selection change, no switch sound")


func test_reloading_weapon_with_ammunition_is_a_valid_fallback() -> void:
	var e := _engine([["kinetic_accelerator", 1], ["breach_charge", 2]])
	assert_true(e.select_weapon("breach_charge"))
	e.fire(Vector2(1, -1), 0.5)
	assert_true(e.select_weapon("kinetic_accelerator"))
	e.fire(Vector2.RIGHT)
	var reload: float = e.weapons.breach_charge.cooldown_remaining
	assert_true(reload > 0.0, "breach is still reloading")
	assert_eq(e.apply_pending_auto_select(), "breach_charge")
	assert_eq(e.weapons.breach_charge.cooldown_remaining, reload, "switching never skips a reload")
	assert_false(e.can_fire(), "it fires once reloaded, not before")


func test_all_weapons_empty_keeps_failure_logic() -> void:
	var e := _engine([["kinetic_accelerator", 1], ["breach_charge", 1]])
	_shoot(e)
	e.apply_pending_auto_select()
	assert_eq(e.selected_weapon_id, "breach_charge")
	_shoot(e)
	assert_eq(e.apply_pending_auto_select(), "", "nothing to switch to")
	assert_eq(e.selected_weapon_id, "breach_charge", "the selection is kept when every weapon is empty")
	assert_false(e.select_weapon("kinetic_accelerator"), "no usable weapon to select")
	e.tick(0.1, true)
	assert_eq(e.phase, MissionEngine.Phase.FAILED, "out of ammunition once settled still fails the mission")


func test_screen_hud_and_operative_follow_the_automatic_switch() -> void:
	if FileAccess.file_exists(TEST_SAVE):
		DirAccess.remove_absolute(ProjectSettings.globalize_path(TEST_SAVE))
	var main: Node = MainScript.new()
	main.cinematics_enabled = false
	main.save = SaveService.new(TEST_SAVE)
	main.boot_mission = "helix_08"
	tree.root.add_child(main)
	await tree.process_frame
	var screen: MissionScreen = main._mission
	var engine := screen.engine
	screen.select_weapon("breach_charge")
	assert_eq(screen.view.operative.weapon_id, "breach_charge")
	engine.weapons.breach_charge.ammo = 1
	assert_true(screen.world.fire(Vector2(1, -1), 0.6) != null, "the last breach charge is thrown")
	assert_eq(engine.selected_weapon_id, "breach_charge", "still selected while the charge is in the air")
	for i in 600:
		if screen.world.projectiles.is_empty():
			break
		await tree.physics_frame
	await tree.physics_frame
	await tree.process_frame
	assert_eq(engine.selected_weapon_id, "kinetic_accelerator", "switched once the charge resolved")
	assert_eq(screen.view.operative.weapon_id, "kinetic_accelerator", "operative holds the new weapon")
	var kinetic: Button = screen.hud._weapon_buttons["kinetic_accelerator"]
	var breach: Button = screen.hud._weapon_buttons["breach_charge"]
	assert_eq(String(kinetic.theme_type_variation), UiKit.PRIMARY, "HUD highlights the engine's selection")
	assert_true(breach.disabled, "the empty weapon's button is disabled")
	assert_true(screen.hud._hint.text.begins_with("Kinetic"), "the hint describes the new weapon")
	screen.select_weapon("breach_charge")
	assert_eq(engine.selected_weapon_id, "kinetic_accelerator", "pressing the empty weapon keeps a usable one")
	tree.paused = false
	main.queue_free()
	await tree.process_frame
	if FileAccess.file_exists(TEST_SAVE):
		DirAccess.remove_absolute(ProjectSettings.globalize_path(TEST_SAVE))
