extends TestCase
## Production assets integrated from the assets branch (data/integrated_assets.json): Godot load
## validation, ASSET_CONTRACT conformance (variant choice, physics-to-3D alignment, state nodes,
## material slots), rights metadata carried through unchanged, and the mission view using them.

const HELIX := "res://data/missions/helix_01.json"
## Tolerance for the front face against the physics rectangle (contract: 1 cm, plus bevel slack).
const FRONT_TOLERANCE_M := 0.02

var _library := AssetLibrary.load_from_file()
var _materials := MaterialCatalog.load_from_file()
var _weapons := WeaponCatalog.load_from_file()


func test_every_integrated_file_loads() -> void:
	assert_true(_library.errors.is_empty(), ", ".join(_library.errors))
	assert_true(_library.entries.size() >= 50, "integrated entries: %d" % _library.entries.size())
	for id: String in _library.entries:
		var path := _library.resource_path(id)
		assert_true(ResourceLoader.exists(path), "%s imported (%s)" % [id, path])
		var resource := load(path)
		if path.ends_with(".glb"):
			assert_true(resource is PackedScene, "%s is a scene" % id)
		elif path.ends_with(".png"):
			assert_true(resource is Texture2D, "%s is a texture" % id)


func test_rights_metadata_travels_unchanged() -> void:
	var data: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(AssetLibrary.DEFAULT_PATH))
	assert_eq(data.library, "assets/asset_manifest.json")
	assert_false(str(data.library_commit).is_empty())
	for entry: Dictionary in data.entries:
		assert_true(str(entry.path).begins_with("assets/"), "%s lives in the consolidated library" % entry.id)
		for key: String in ["id", "path", "source", "rights_status", "approval_status", "slice"]:
			assert_true(entry.has(key), "%s has %s" % [entry.get("id", "?"), key])
		assert_true(str(entry.approval_status) != "approved", "%s: development integration is not approval" % entry.id)
		assert_false(str(entry.rights_status).to_lower().begins_with("cleared"), "%s rights not marked cleared" % entry.id)


func test_every_helix_component_resolves_to_the_best_variant() -> void:
	var def := MissionDefinition.load_from_file(HELIX, _materials, _weapons)
	for c in def.components:
		var entry := _library.component_entry("helix", c.kind, c.size)
		assert_false(entry.is_empty(), "model for %s (%s)" % [c.id, c.kind])
	assert_eq(_library.component_entry("helix", "server_rack", Vector2(40, 100)).id, "HLX-CMP-SERVER_RACK-B")
	assert_eq(_library.component_entry("helix", "relay_mast", Vector2(22, 220)).id, "HLX-CMP-RELAY_MAST-B")
	assert_eq(_library.component_entry("helix", "blast_wall", Vector2(30, 90)).id, "HLX-CMP-BLAST_WALL-A")
	assert_true(_library.component_entry("helix", "unknown_kind", Vector2(10, 10)).is_empty())


func test_front_face_stays_inside_the_physics_rectangle() -> void:
	var def := MissionDefinition.load_from_file(HELIX, _materials, _weapons)
	for c in def.components:
		var model := _library.instance_component("helix", c.kind, c.size)
		var intact := model.find_child("mesh_intact", true, false) as MeshInstance3D
		assert_true(intact != null, "%s has mesh_intact" % c.id)
		var box := intact.transform * intact.get_aabb()
		var half := Vector2(c.size.x, c.size.y) / ViewMapping.PX_PER_METRE / 2.0
		var lo := Vector2(box.position.x * model.scale.x, box.position.y * model.scale.y)
		var hi := Vector2(box.end.x * model.scale.x, box.end.y * model.scale.y)
		assert_true(lo.x >= -half.x - FRONT_TOLERANCE_M and hi.x <= half.x + FRONT_TOLERANCE_M, "%s width inside the rectangle (%.3f..%.3f vs %.3f)" % [c.id, lo.x, hi.x, half.x])
		assert_true(lo.y >= -half.y - FRONT_TOLERANCE_M and hi.y <= half.y + FRONT_TOLERANCE_M, "%s height inside the rectangle (%.3f..%.3f vs %.3f)" % [c.id, lo.y, hi.y, half.y])
		assert_true(absf(box.get_center().z) <= 0.45, "%s centred on the physics plane in depth" % c.id)
		model.free()


func test_state_nodes_show_one_at_a_time() -> void:
	var model := _library.instance_component("helix", "server_rack", Vector2(40, 100))
	var names := ["mesh_intact", "mesh_light", "mesh_heavy"]
	for state in 3:
		AssetLibrary.set_state_nodes(model, state)
		for i in 3:
			var node := model.find_child(names[i], true, false) as Node3D
			assert_eq(node.visible, i == state, "state %d: %s" % [state, names[i]])
	model.free()


func test_material_slots_bind_texture_sets() -> void:
	assert_eq(AssetLibrary.slot_material_id("mat_electronic_module_hlx", "hlx"), "electronic_module")
	assert_eq(AssetLibrary.slot_material_id("mat_ai_core_module_hlx_frame", "hlx"), "ai_core_module")
	assert_eq(AssetLibrary.slot_material_id("trim_dark_hlx", "hlx"), "")
	assert_eq(AssetLibrary.slot_material_id("mat_composite_vta", "hlx"), "")
	assert_false(_library.material_set("helix", "reinforced_steel").is_empty())
	var model := _library.instance_component("helix", "support_column", Vector2(26, 160))
	var bound := 0
	for mesh_instance: MeshInstance3D in model.find_children("*", "MeshInstance3D", true, false):
		for surface in mesh_instance.mesh.get_surface_count():
			var material := mesh_instance.get_active_material(surface) as StandardMaterial3D
			if material != null and material.normal_texture != null:
				bound += 1
	assert_true(bound > 0, "surfaces carry texture-set normal maps (authored or bound by slot)")
	model.free()


func test_mission_view_uses_production_models_and_set() -> void:
	var screen := MissionScreen.new()
	tree.root.add_child(screen)
	await wait_physics_frames(2)
	var view := screen.view
	assert_eq(view.chapter, "helix")
	for id: String in view._meshes:
		var visual: ComponentVisual = view._meshes[id]
		assert_true(visual.uses_model, "%s uses its production model (%s)" % [id, visual.asset_id])
	assert_true(view.placed_pieces.has("HLX-ENV-BACK_WALL-A"))
	assert_true(view.placed_pieces.has("HLX-ENV-LEDGE_STATIC-A"), "static slab uses the kit ledge")
	assert_true(view.placed_pieces.has("HLX-PRP-RELAY_ARRAY-A"), "band 1 landmark")
	screen.engine.apply_damage("rack_1", 30.0, DamageRules.TYPE_IMPACT)
	await wait_physics_frames(1)
	var rack: ComponentVisual = view._meshes["rack_1"]
	assert_true((rack.find_child("mesh_light", true, false) as Node3D).visible, "damaged rack shows its light-damage node")
	screen.queue_free()
	await wait_physics_frames(1)


func test_textures_referenced_by_models_are_integrated() -> void:
	var data: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(AssetLibrary.DEFAULT_PATH))
	var paths := {}
	for entry: Dictionary in data.entries:
		paths[entry.path] = entry
	for entry: Dictionary in data.entries:
		if entry.get("slice") == "dependency":
			assert_false((entry.get("required_by", []) as Array).is_empty(), "%s records which models need it" % entry.id)
			for model_id: String in entry.required_by:
				assert_true(_library.has_entry(model_id), "%s is required by an integrated model" % entry.id)
	assert_true(paths.has("assets/materials/shared/shr_mat_gunmetal_a_albedo.png"), "shared sets used by the kits ship with them")


func test_every_helix_component_has_a_debris_set() -> void:
	var def := MissionDefinition.load_from_file(HELIX, _materials, _weapons)
	for c in def.components:
		var entry := _library.debris_entry("helix", c.kind, c.size)
		assert_false(entry.is_empty(), "debris set for %s (%s)" % [c.id, c.kind])
		assert_eq(str(entry.get("component_kind", "")), c.kind, "%s debris matches its kind" % c.id)
		var model := _library.instance_debris("helix", c.kind, c.size)
		var fragments := model.find_children("*", "MeshInstance3D", true, false).size()
		# Contract 8: 4-10 closed fragments (the husk counts as one).
		assert_true(fragments >= 4 and fragments <= 11, "%s: %d fragments" % [entry.id, fragments])
		model.free()
	assert_eq(_library.debris_entry("helix", "server_rack", Vector2(40, 100)).id, "HLX-DEB-SERVER_RACK-B")


func test_debris_motion_is_seeded_and_lands_on_the_floor() -> void:
	var holder := Node3D.new()
	tree.root.add_child(holder)
	var first := DebrisSet.create(_library.instance_debris("helix", "server_rack", Vector2(40, 100)), Vector3(10.0, 0.5, 0.0), 0.2, "rack_1", "HLX-DEB-SERVER_RACK-B")
	var second := DebrisSet.create(_library.instance_debris("helix", "server_rack", Vector2(40, 100)), Vector3(10.0, 0.5, 0.0), 0.2, "rack_1", "HLX-DEB-SERVER_RACK-B")
	holder.add_child(first)
	holder.add_child(second)
	assert_true(first.fragment_count() >= 4)
	for i in first.fragment_count():
		assert_eq(first._fragments[i].velocity, second._fragments[i].velocity, "same component, same throw (%d)" % i)
	# Step well past the landing time (not past REST_TIME, so nothing shrinks yet).
	for step in 90:
		first._process(1.0 / 60.0)
	for fragment: Dictionary in first._fragments:
		var node: MeshInstance3D = fragment.node
		assert_true(node.global_position.y >= float(fragment.rest_y) - 0.001, "%s rests on or above the floor" % node.name)
		assert_true(absf(node.global_position.z) < 1.2, "%s stays near the physics plane" % node.name)
	holder.free()


func test_damage_overlays_cover_every_helix_material() -> void:
	var def := MissionDefinition.load_from_file(HELIX, _materials, _weapons)
	for c in def.components:
		for level in [1, 2]:
			assert_true(_library.damage_overlay(c.material, level) != null, "%s overlay level %d for %s" % [c.material, level, c.id])
	assert_true(_library.damage_overlay("unknown_material", 1) == null)


func test_damaged_material_adds_a_shared_overlay_pass() -> void:
	var source := StandardMaterial3D.new()
	source.resource_name = "mat_electronic_module_hlx"
	source.albedo_color = Color(0.8, 0.8, 0.8)
	assert_eq(_library.damaged_material(source, "electronic_module", 0), source, "intact keeps the source")
	var light := _library.damaged_material(source, "electronic_module", 1)
	var heavy := _library.damaged_material(source, "electronic_module", 2)
	assert_true(light != source and heavy != light)
	assert_eq(_library.damaged_material(source, "electronic_module", 1), light, "shared per source and level")
	var overlay := light.next_pass as StandardMaterial3D
	assert_true(overlay != null, "overlay as next pass")
	assert_true(overlay.uv1_triplanar and not overlay.uv1_world_triplanar, "object-space triplanar (contract 8)")
	assert_eq(overlay.transparency, BaseMaterial3D.TRANSPARENCY_ALPHA)
	assert_true(heavy.albedo_color.r < light.albedo_color.r and light.albedo_color.r < source.albedo_color.r, "darker with damage")
	assert_eq(_library.damaged_material(source, "no_overlay_material", 2), source, "no overlay: unchanged")


func test_vfx_presets_load_with_their_textures() -> void:
	for preset: String in MissionVfx.POOLS:
		var scene := _library.preset_scene(preset)
		assert_true(scene != null, "preset %s integrated" % preset)
		var node := scene.instantiate()
		assert_true(node.find_children("*", "CPUParticles3D", true, false).size() > 0, "%s has particles" % preset)
		node.free()
	assert_true(_library.preset_scene(MissionVfx.CORE_IDLE) != null)
	for material_id: String in MissionVfx.IMPACT_BY_MATERIAL:
		assert_true(MissionVfx.POOLS.has(MissionVfx.IMPACT_BY_MATERIAL[material_id]), "%s impact preset is pooled" % material_id)


func test_mission_view_spawns_debris_overlays_and_effects() -> void:
	var screen := MissionScreen.new()
	tree.root.add_child(screen)
	await wait_physics_frames(4)
	await wait_process_frames(ComponentVisual.WARM_FRAMES + 1)
	var view := screen.view
	for preset: String in MissionVfx.POOLS:
		assert_true(view.vfx.has_preset(preset), "pool %s" % preset)
	assert_true(view.vfx._idle.has("aura_core"), "the critical core carries its idle glow")
	var rack: ComponentVisual = view._meshes["rack_1"]
	assert_eq(rack.overlay_level, 0, "intact rack after warm-up has no overlay")
	screen.engine.apply_damage("rack_1", 30.0, DamageRules.TYPE_IMPACT)
	await wait_physics_frames(1)
	assert_eq(rack.overlay_level, 1, "damaged rack shows the light overlay")
	screen.engine.destroy_component("rack_1", "test")
	await wait_physics_frames(2)
	assert_true(view.debris_spawned.has("HLX-DEB-SERVER_RACK-B"), "destroyed rack leaves its debris set")
	screen.queue_free()
	await wait_physics_frames(1)


func test_restart_reuses_the_mission_set() -> void:
	MissionView.release_cached_set()
	var first := MissionScreen.new()
	tree.root.add_child(first)
	await wait_process_frames(2)
	assert_false(first.view.reused_set, "the first attempt builds the set")
	var built := first.view.set_root
	var pieces := first.view.placed_pieces.duplicate()
	var env := built.find_children("*", "WorldEnvironment", false, false)[0] as WorldEnvironment
	assert_eq(env.environment.fog_mode, Environment.FOG_MODE_DEPTH, "depth fog keeps the gameplay plane clear")
	assert_true(env.environment.fog_depth_begin > MissionView.CAMERA_OFFSET.z, "fog starts behind the facility")
	# The app root's restart: remove the old screen, queue it for deletion, add the next one.
	tree.root.remove_child(first)
	first.queue_free()
	var second := MissionScreen.new()
	tree.root.add_child(second)
	assert_true(second.view.reused_set, "a restart reuses the set")
	assert_true(second.view.set_root == built, "the same set node")
	assert_eq(built.get_parent(), second.view)
	assert_eq(second.view.placed_pieces, pieces)
	assert_eq(second.view.chapter, "helix")
	await wait_process_frames(2)
	assert_true(is_instance_valid(built) and built.get_parent() == second.view, "deleting the old screen keeps it")
	second.queue_free()
	await wait_process_frames(1)
	MissionView.release_cached_set()
	assert_false(is_instance_valid(built), "released on leaving")


func test_projectiles_and_hidden_weapon_are_warmed_at_load() -> void:
	var screen := MissionScreen.new()
	tree.root.add_child(screen)
	var warm_ids := screen.view._warm_nodes.map(func(n: Node3D) -> String: return n.name)
	assert_true(screen.view._warm_nodes.size() >= MissionView.PROJECTILE_MODELS.size(), "projectile models drawn at load: %s" % [warm_ids])
	await wait_process_frames(1)
	var rig := screen.view.operative
	assert_true(rig.uses_model)
	for id: String in rig._weapons:
		assert_true((rig._weapons[id] as Node3D).visible, "%s drawn during warm-up" % id)
	await wait_process_frames(OperativeRig.WARM_FRAMES + 1)
	assert_true((rig._weapons[rig.weapon_id] as Node3D).visible)
	assert_false((rig._weapons["breach_charge"] as Node3D).visible, "then only the selected weapon shows")
	assert_true(screen.view._warm_nodes.is_empty())
	screen.queue_free()
	await wait_process_frames(1)
