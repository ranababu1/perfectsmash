class_name AssetLibrary
extends RefCounted
## Production assets integrated into main (data/integrated_assets.json), indexed for the mission
## view. Follows generated_assets/docs/ASSET_CONTRACT.md:
## - destructible component meshes by (chapter, component_kind), the variant whose
##   reference_size_px needs the least stretch to fit the physics rectangle (section 5);
## - meshes are scaled in X and Y to the physics rectangle, depth unchanged (sections 3 and 5);
## - state nodes mesh_intact / mesh_light / mesh_heavy, one shown at a time (section 8);
## - main surfaces `mat_<material>_<ch>[_zone]` get the chapter texture set's normal and ORM
##   maps by slot name (section 7); the slot's authored colour is kept;
## - environment pieces by asset id.
## Anything missing returns null so the caller falls back to the greybox (section 17).

const DEFAULT_PATH := "res://data/integrated_assets.json"
const CHAPTER_CODES := {"helix": "hlx", "vita": "vta", "nova_grid": "nvg", "civitas": "cvt", "meridian": "mrd"}

var entries := {}
var errors := PackedStringArray()
## "chapter/kind" -> Array of component entries (CMP)
var _components := {}
## "chapter/kind" -> Array of debris entries (DEB)
var _debris := {}
## "chapter/material" -> {albedo, normal, orm, emission, mean}
var _material_sets := {}
var _scenes := {}
var _textures := {}
var _bound_materials := {}


static func load_from_file(path: String = DEFAULT_PATH) -> AssetLibrary:
	var library := AssetLibrary.new()
	if not FileAccess.file_exists(path):
		library.errors.append("no integrated asset manifest at %s" % path)
		return library
	var data: Variant = JSON.parse_string(FileAccess.get_file_as_string(path))
	if not data is Dictionary or not data.get("entries") is Array:
		library.errors.append("integrated asset manifest is not valid")
		return library
	for entry: Variant in data.entries:
		if entry is Dictionary and entry.get("id") is String and entry.get("path") is String:
			library._index(entry)
	return library


func has_entry(asset_id: String) -> bool:
	return entries.has(asset_id)


func resource_path(asset_id: String) -> String:
	return "res://" + str(entries[asset_id].path) if entries.has(asset_id) else ""


## Best component entry for a kind at a physics size, or {} when none is integrated.
func component_entry(chapter: String, kind: String, size_px: Vector2) -> Dictionary:
	return _best_fit(_components.get(chapter + "/" + kind, []), size_px)


func debris_entry(chapter: String, kind: String, size_px: Vector2) -> Dictionary:
	return _best_fit(_debris.get(chapter + "/" + kind, []), size_px)


## Instantiates the component mesh for `kind` sized to `size_px`, or null. The returned node is
## centred on the collision rectangle (contract pivot), scaled to it, with state nodes prepared.
func instance_component(chapter: String, kind: String, size_px: Vector2) -> Node3D:
	var entry := component_entry(chapter, kind, size_px)
	if entry.is_empty():
		return null
	var root := _instance(entry)
	if root == null:
		return null
	var reference: Vector2 = Vector2(entry.reference_size_px[0], entry.reference_size_px[1])
	root.scale = Vector3(size_px.x / reference.x, size_px.y / reference.y, 1.0)
	set_state_nodes(root, 0)
	bind_materials(root, chapter)
	return root


## Instantiates an environment or prop piece by asset id (unscaled), or null.
func instance_piece(asset_id: String, chapter: String) -> Node3D:
	if not entries.has(asset_id):
		return null
	var root := _instance(entries[asset_id])
	if root != null:
		bind_materials(root, chapter)
	return root


## Shows exactly one damage-state node: 0 intact, 1 damaged (light), 2+ critical (heavy), with
## the contract's fallbacks when a node is missing.
static func set_state_nodes(root: Node, state: int) -> void:
	var intact := root.find_child("mesh_intact", true, false) as Node3D
	var light := root.find_child("mesh_light", true, false) as Node3D
	var heavy := root.find_child("mesh_heavy", true, false) as Node3D
	var show: Node3D = intact
	if state >= 1 and light != null:
		show = light
	if state >= 2 and heavy != null:
		show = heavy
	for node: Node3D in [intact, light, heavy]:
		if node != null:
			node.visible = node == show


## Gives every main-material surface its chapter texture set's normal and ORM maps (shared
## per source material, so bound once). Other slots keep their imported material.
func bind_materials(root: Node, chapter: String) -> void:
	var code: String = CHAPTER_CODES.get(chapter, "")
	for mesh_instance: MeshInstance3D in root.find_children("*", "MeshInstance3D", true, false):
		var mesh := mesh_instance.mesh
		if mesh == null:
			continue
		for surface in mesh.get_surface_count():
			var material := mesh.surface_get_material(surface) as StandardMaterial3D
			if material == null:
				continue
			var material_id := slot_material_id(material.resource_name, code)
			if material_id.is_empty():
				continue
			var bound := _bound_material(material, chapter, material_id)
			if bound != null:
				mesh_instance.set_surface_override_material(surface, bound)


## `mat_<material>_<code>` or `mat_<material>_<code>_<zone>` -> material id ("" otherwise).
static func slot_material_id(slot: String, code: String) -> String:
	if not slot.begins_with("mat_") or code.is_empty():
		return ""
	var marker := "_" + code
	var at := slot.rfind(marker)
	if at <= 4:
		return ""
	var rest := slot.substr(at + marker.length())
	if not rest.is_empty() and not rest.begins_with("_"):
		return ""
	return slot.substr(4, at - 4)


func material_set(chapter: String, material_id: String) -> Dictionary:
	return _material_sets.get(chapter + "/" + material_id, {})


func _bound_material(source: StandardMaterial3D, chapter: String, material_id: String) -> StandardMaterial3D:
	var key := "%s|%s" % [source.get_instance_id(), chapter]
	if _bound_materials.has(key):
		return _bound_materials[key]
	var set := material_set(chapter, material_id)
	# The core housing has no chapter set of its own; the contract falls back to electronics.
	if set.is_empty() and material_id == "ai_core_module":
		set = material_set(chapter, "electronic_module")
	if set.is_empty():
		_bound_materials[key] = null
		return null
	var material := source.duplicate() as StandardMaterial3D
	var normal := _texture(set.get("normal", ""))
	if normal != null:
		material.normal_enabled = true
		material.normal_texture = normal
		material.normal_scale = 0.8
	var orm := _texture(set.get("orm", ""))
	if orm != null:
		material.roughness_texture = orm
		material.roughness_texture_channel = BaseMaterial3D.TEXTURE_CHANNEL_GREEN
		material.metallic_texture = orm
		material.metallic_texture_channel = BaseMaterial3D.TEXTURE_CHANNEL_BLUE
		material.ao_enabled = true
		material.ao_texture = orm
		material.ao_texture_channel = BaseMaterial3D.TEXTURE_CHANNEL_RED
	_bound_materials[key] = material
	return material


func _texture(asset_path: String) -> Texture2D:
	if asset_path.is_empty():
		return null
	if not _textures.has(asset_path):
		_textures[asset_path] = load(asset_path) if ResourceLoader.exists(asset_path) else null
	return _textures[asset_path]


func _instance(entry: Dictionary) -> Node3D:
	var path := "res://" + str(entry.path)
	if not _scenes.has(path):
		_scenes[path] = load(path) if ResourceLoader.exists(path) else null
	var scene: PackedScene = _scenes[path]
	if scene == null:
		errors.append("cannot load %s" % path)
		return null
	return scene.instantiate() as Node3D


func _best_fit(candidates: Array, size_px: Vector2) -> Dictionary:
	var best := {}
	var best_cost := INF
	for entry: Dictionary in candidates:
		var reference: Array = entry.get("reference_size_px", [])
		if reference.size() != 2:
			continue
		var cost := absf(log(size_px.x / float(reference[0]))) + absf(log(size_px.y / float(reference[1])))
		if cost < best_cost:
			best_cost = cost
			best = entry
	return best


func _index(entry: Dictionary) -> void:
	var id: String = entry.id
	entries[id] = entry
	var chapter := str(entry.get("chapter", ""))
	if entry.get("category") == "destructibles" and str(entry.path).ends_with(".glb"):
		var key := chapter + "/" + str(entry.get("component_kind", ""))
		var bucket: Dictionary = _debris if "-DEB-" in id else _components
		if not bucket.has(key):
			bucket[key] = []
		bucket[key].append(entry)
	if "-MAT-" in id and str(entry.path).ends_with(".png"):
		# HLX-MAT-REINFORCED_STEEL-A, ...-A-NORMAL, -A-ORM, -A-EMISSION
		var parts := id.split("-")
		if parts.size() >= 4:
			var material_id := parts[2].to_lower()
			var role := parts[4].to_lower() if parts.size() >= 5 else "albedo"
			var key := chapter + "/" + material_id
			if not _material_sets.has(key):
				_material_sets[key] = {}
			_material_sets[key][role] = "res://" + str(entry.path)
			if entry.has("albedo_mean_linear"):
				_material_sets[key]["mean"] = entry.albedo_mean_linear
