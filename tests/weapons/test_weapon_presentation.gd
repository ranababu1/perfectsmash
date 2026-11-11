extends TestCase
## Presentation of every weapon in data/weapons.json: HUD icon and button, operative model,
## projectile look, blast/strike effects and sound ids. Data cases need no physics; the mission
## cases build a MissionView over a small inline mission with all six weapons.

const PHYSICS_SUITE := true
const HUD_WIDTH := 1280.0
const MIN_TOUCH := 64.0

var _materials := MaterialCatalog.load_from_file()
var _weapons := WeaponCatalog.load_from_file()
var _library := AssetLibrary.load_from_file()


static func _asset_stem(weapon_id: String) -> String:
	return weapon_id.to_upper()


func _all_ids() -> Array[String]:
	var ids: Array[String] = []
	for weapon in _weapons.weapons.values():
		ids.append(weapon.id)
	return ids


## A flat yard with a core; `weapon_ids` all get 3 rounds. Chapter 5 so every weapon is unlocked.
func _definition(weapon_ids: Array) -> MissionDefinition:
	var weapon_data := {}
	for id: String in weapon_ids:
		weapon_data[id] = {"ammunition": 3}
	var data := {
		"id": "presentation_test", "name": "Presentation test", "chapter": 5, "briefing": "test",
		"width": 1600, "ground_y": 640, "operative": [150, 640], "recommended_shots": 1, "target_time": 30,
		"rewards": {"completion_points": 100, "completion_research_data": 1, "optional_research_data": 1},
		"weapons": weapon_data, "statics": [],
		"components": [{"id": "core", "kind": "ai_core", "material": "ai_core_module", "x": 1000, "y": 610, "w": 60, "h": 60, "critical_asset": true}],
		"objectives": [{"id": "core", "type": "destroy_critical", "mandatory": true, "label": "core", "targets": ["core"]}],
	}
	return MissionDefinition.from_json_text(JSON.stringify(data), _materials, _weapons)


func _states(engine: MissionEngine) -> Array[WeaponState]:
	var states: Array[WeaponState] = []
	for id in engine.weapon_order:
		states.append(engine.weapons[id])
	return states


# --- Assets ------------------------------------------------------------------------------------

func test_every_weapon_has_an_integrated_icon_model_and_projectile_style() -> void:
	assert_true(_weapons.is_valid(), ", ".join(_weapons.errors))
	for id in _all_ids():
		var stem := _asset_stem(id)
		assert_true(_library.texture("GAM-ICN-WEAPON_%s-A" % stem) != null, "%s: HUD icon integrated and loads" % id)
		assert_eq(MissionHud.ICONS.get(id, ""), "GAM-ICN-WEAPON_%s-A" % stem, "%s: HUD maps its icon" % id)
		var model := _library.instance_piece("OPR-WPN-%s-A" % stem, "shared")
		assert_true(model != null, "%s: operative weapon model integrated" % id)
		if model != null:
			assert_true(model.find_child("muzzle", true, false) != null, "%s: model has a muzzle marker" % id)
			model.free()
		assert_eq(OperativeRig.WEAPON_MODELS.get(id, ""), "OPR-WPN-%s-A" % stem, "%s: rig mounts its model" % id)
		assert_true(ProjectileVisual.ASSETS.has(id), "%s: projectile visual style" % id)
		assert_true(MissionView.PREVIEW_COLOURS.has(id), "%s: aim-preview colour" % id)
		assert_true(MissionHud.RELOAD_COLOURS.has(id), "%s: reload bar colour" % id)


func test_projectile_visuals_build_with_body_trail_and_distinct_colours() -> void:
	var colours := {}
	for id in _all_ids():
		var spec: Dictionary = _weapons.get_weapon(id).effective_stats()
		var projectile := WeaponProjectile.new(id, spec, Vector2.ZERO, Vector2(1000.0, 0.0))
		var visual := ProjectileVisual.create(projectile, _library)
		projectile.free()
		assert_true(visual.get_child_count() >= 2, "%s: body and trail/glow parts" % id)
		assert_true(visual._trail != null, "%s: trail quad" % id)
		colours[ProjectileVisual.ASSETS[id].get("trail_tint", Color.WHITE).to_html() + str(ProjectileVisual.ASSETS[id].get("shape", id))] = id
		visual.free()
	assert_eq(colours.size(), _all_ids().size(), "every weapon has its own colour/shape look")
	var lance := ProjectileVisual.ASSETS["temporal_lance"]
	var penetrator := ProjectileVisual.ASSETS["penetrator"]
	assert_true(float(lance.trail_max) > float(ProjectileVisual.TRAIL_MAX_M), "the lance bolt is long")
	assert_true(float(penetrator.trail_height) < 0.1, "the penetrator streak is thin")
	var disruptor := WeaponProjectile.new("disruptor", _weapons.get_weapon("disruptor").effective_stats(), Vector2.ZERO, Vector2(500.0, 0.0))
	var canister := ProjectileVisual.create(disruptor, _library)
	disruptor.free()
	assert_eq(canister._arcs.size(), 2, "the disruptor canister crackles with arcs")
	assert_true(canister._tumbles, "the canister tumbles")
	canister.free()


func test_sound_ids_resolve_to_existing_files_for_every_weapon_event() -> void:
	var catalog := AudioCatalog.load_from_file()
	assert_true(catalog.is_valid(), ", ".join(catalog.errors))
	var fire_sets := {}
	for id in _all_ids():
		var stats := _weapons.get_weapon(id).effective_stats()
		var events := ["fire", "ready"]
		if float(stats.blast_damage) > 0.0:
			events.append("blast")
		for event: String in events:
			var pairs := MissionAudio.weapon_sounds(id, event)
			assert_false(pairs.is_empty(), "%s has a %s sound" % [id, event])
			for pair: Array in pairs:
				var spec := catalog.get_sound(str(pair[0]))
				assert_true(spec != null, "%s %s: sound '%s' is in data/audio.json" % [id, event, pair[0]])
				if spec == null:
					continue
				assert_false(spec.files.is_empty(), "%s: has files" % pair[0])
				for path in spec.files:
					assert_true(ResourceLoader.exists(path), "%s: %s exists" % [pair[0], path])
		var fire: Array = MissionAudio.weapon_sounds(id, "fire")
		if not fire.is_empty():
			fire_sets[str(catalog.get_sound(str(fire[0][0])).files)] = id
	assert_eq(fire_sets.size(), _all_ids().size(), "every weapon fires with its own file set")
	for id in ["penetrator", "temporal_lance"]:
		assert_false(MissionAudio.weapon_sounds(id, "strike").is_empty(), "%s has a strike sound" % id)
	assert_true(MissionAudio.weapon_sounds("nope", "fire").is_empty())


# --- HUD ---------------------------------------------------------------------------------------

func _hud_for(weapon_ids: Array) -> MissionHud:
	var def := _definition(weapon_ids)
	assert_true(def.is_valid(), ", ".join(def.errors))
	var engine := MissionEngine.new(def, _materials, _weapons)
	var hud := MissionHud.new()
	hud.library = _library
	hud.size = Vector2(HUD_WIDTH, 720.0)
	tree.root.add_child(hud)
	hud.set_weapons(_states(engine))
	hud.update_weapons(engine.weapons, engine.selected_weapon_id)
	return hud


func test_hud_shows_one_icon_button_per_weapon_that_fits_the_bar() -> void:
	var all := _all_ids()
	for count in range(1, all.size() + 1):
		var hud := _hud_for(all.slice(0, count))
		var buttons := hud.find_children("Weapon_*", "Button", true, false)
		assert_eq(buttons.size(), count, "%d-weapon mission shows %d buttons" % [count, count])
		var row := hud.find_child("WeaponRow", true, false) as HBoxContainer
		for button: Button in buttons:
			assert_true(button.custom_minimum_size.x >= MIN_TOUCH and button.custom_minimum_size.y >= MIN_TOUCH, "%s touch target >= 64 px" % button.name)
			assert_true(button.icon != null, "%s shows its icon" % button.name)
			assert_true(button.text.contains("/"), "%s shows ammunition" % button.name)
		await tree.process_frame
		await tree.process_frame
		var width := row.size.x
		assert_true(width + MissionHud.MARGIN * 2.0 + MissionHud.HINT_MIN_WIDTH <= HUD_WIDTH, "%d buttons (%.0f px) leave room for the hint at 1280 px" % [count, width])
		assert_near(row.position.x + row.size.x, HUD_WIDTH - MissionHud.MARGIN, 0.5, "the bar is anchored bottom-right")
		var hint: Label = hud._hint
		assert_true(hint.offset_right <= -(width + MissionHud.MARGIN), "the hint stays left of the weapon bar")
		hud.queue_free()
	var narrow := _hud_for(all)
	var titles := PackedStringArray()
	for button: Button in narrow.find_children("Weapon_*", "Button", true, false):
		titles.append(button.text.get_slice("\n", 0))
	titles.sort()
	assert_eq(titles, PackedStringArray(["BREACH", "DISRUPTOR", "KINETIC", "LANCE", "PENETRATOR", "PULSE"]))
	narrow.queue_free()


func test_hud_weapon_button_width_shrinks_only_when_needed() -> void:
	assert_eq(MissionHud.weapon_button_width(2), MissionHud.WEAPON_BUTTON.x)
	assert_eq(MissionHud.weapon_button_width(4), MissionHud.WEAPON_BUTTON.x)
	assert_true(MissionHud.weapon_button_width(6) < MissionHud.WEAPON_BUTTON.x)
	assert_true(MissionHud.weapon_button_width(6) >= MissionHud.WEAPON_BUTTON_MIN_WIDTH)
	assert_true(MissionHud.weapon_button_width(20) >= MissionHud.WEAPON_BUTTON_MIN_WIDTH)


# --- Mission view ------------------------------------------------------------------------------

func _view_for(weapon_ids: Array) -> Dictionary:
	var def := _definition(weapon_ids)
	assert_true(def.is_valid(), ", ".join(def.errors))
	var engine := MissionEngine.new(def, _materials, _weapons)
	var viewport := SubViewport.new()
	viewport.render_target_update_mode = SubViewport.UPDATE_DISABLED
	tree.root.add_child(viewport)
	var world := MissionWorld.new()
	viewport.add_child(world)
	world.setup(def, engine, _materials)
	var view := MissionView.new()
	viewport.add_child(view)
	view.setup(world)
	return {"viewport": viewport, "world": world, "view": view, "engine": engine}


func test_operative_swaps_to_the_selected_weapon_model() -> void:
	var all := _all_ids()
	var made := _view_for(all)
	var view: MissionView = made.view
	var engine: MissionEngine = made.engine
	await wait_physics_frames(6)
	var rig := view.operative
	assert_true(rig.uses_model, "production operative")
	for id in all:
		assert_true(engine.select_weapon(id), "select %s" % id)
		assert_eq(rig.weapon_id, id, "rig follows weapon_selected without MissionScreen")
		for other: String in rig._weapons:
			assert_eq((rig._weapons[other] as Node3D).visible, other == id, "%s visible while %s is selected" % [other, id])
		assert_true(rig.muzzle != null, "%s: muzzle marker for the flash" % id)
	(made.viewport as SubViewport).queue_free()
	await wait_physics_frames(1)


func test_view_shows_strikes_blasts_and_preview_per_weapon() -> void:
	var all := _all_ids()
	var made := _view_for(all)
	var view: MissionView = made.view
	var world: MissionWorld = made.world
	await wait_physics_frames(6)
	var vfx := view.vfx
	for sheet in ["discharge", "electric", "spark", "flash", "ring", "emp_shell"]:
		assert_false((vfx._fx.get(sheet, []) as Array).is_empty(), "pooled %s effect" % sheet)
	assert_true(vfx.emp_burst(Vector3(5, 1, 0.3), 170.0), "EMP burst")
	assert_true(vfx.pulse_discharge(Vector3(5, 1, 0.3), 75.0), "pulse discharge")
	assert_true(vfx.lance_strike(Vector3(5, 1, 0.3)), "lance strike")
	assert_true(vfx.pierce_spark(Vector3(5, 1, 0.3)), "pierce spark")
	for id in all:
		assert_true(vfx.weapon_muzzle(id, Vector3(2, 1, 0.3), 0.1), "%s muzzle flash" % id)
	for i in 80:
		await tree.process_frame
	assert_true(vfx._running.is_empty(), "every timed effect finished and hid itself")
	# A blast names its weapon by the projectile sitting at its centre.
	var stats: Dictionary = world.engine.weapons["disruptor"].stats
	var projectile := world.spawn_projectile("disruptor", stats, Vector2(400, 300), Vector2.ZERO)
	await wait_physics_frames(2)
	view._on_blast(Vector2(400, 300), float(stats.blast_radius))
	assert_eq(view.last_blast_weapon, "disruptor")
	assert_false((vfx._running as Array).is_empty(), "EMP effects are running")
	var pulse_stats: Dictionary = world.engine.weapons["pulse_cannon"].stats
	view._on_blast(Vector2(900, 100), float(pulse_stats.blast_radius))
	assert_eq(view.last_blast_weapon, "pulse_cannon", "found by radius when no projectile is at the centre")
	view._on_blast(Vector2(900, 100), 55.0)
	assert_eq(view.last_blast_weapon, "", "a chain blast belongs to no weapon")
	# The preview dots take the selected weapon's colour.
	for id in all:
		world.engine.select_weapon(id)
		view.show_preview(Vector2(150, 600), Vector2(1000, -200), 0.1, 0.5)
		var material := view._preview.material_override as StandardMaterial3D
		assert_eq(material.albedo_color, MissionView.PREVIEW_COLOURS[id], "%s preview colour" % id)
	assert_true(is_instance_valid(projectile))
	(made.viewport as SubViewport).queue_free()
	await wait_physics_frames(1)
