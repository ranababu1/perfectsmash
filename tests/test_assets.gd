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
	assert_eq(data.source_branch, "assets")
	assert_false(str(data.source_commit).is_empty())
	for entry: Dictionary in data.entries:
		for key: String in ["id", "path", "source", "rights_status", "approval_status"]:
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
			var material := mesh_instance.get_surface_override_material(surface) as StandardMaterial3D
			if material != null and material.normal_texture != null:
				bound += 1
	assert_true(bound > 0, "main slots carry the chapter normal map")
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
