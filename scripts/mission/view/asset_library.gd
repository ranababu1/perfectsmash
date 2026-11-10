class_name AssetLibrary
extends RefCounted
## Production assets integrated into main (data/integrated_assets.json), indexed for the mission
## view. Follows assets/docs/ASSET_CONTRACT.md:
## - destructible component meshes by (chapter, component_kind), the variant whose
##   reference_size_px needs the least stretch to fit the physics rectangle (section 5);
## - meshes are scaled in X and Y to the physics rectangle, depth unchanged (sections 3 and 5);
## - state nodes mesh_intact / mesh_light / mesh_heavy, one shown at a time (section 8);
## - main surfaces `mat_<material>_<ch>[_zone]` without textures of their own get the chapter
##   texture set's normal and ORM maps by slot name (section 7); surfaces the model already
##   textures (external glTF images, current kit exports) keep the authored binding;
## - environment pieces by asset id;
## - debris sets (`<CH>-DEB-<KIND>`) for the destroyed state, scaled like their component;
## - damage overlays `SHR-DMG-<MATERIAL>-LIGHT|HEAVY` as a transparent object-space triplanar
##   next pass on the main surfaces (section 8), one shared material per source surface and level;
## - the ui-vfx CPUParticles3D presets by name (`presets` in the integration manifest).
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
## "material_id/light|heavy" -> overlay texture path
var _overlays := {}
## preset name -> res:// path of the .tscn
var presets := {}
var _overlay_materials := {}
var _damaged_materials := {}

## Albedo multiplier for the damaged and critical surface (contract 8: about 15% darker when
## damaged; critical darker still so the state reads at phone size).
const DAMAGE_DARKEN := [1.0, 0.85, 0.72]
## Overlay tiling: one tile per metre in object space (contract 8). Models are authored in
## metres, so an object-space scale of 1 is one tile per metre before the X/Y fit.
const OVERLAY_TILES_PER_METRE := 1.0


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
	var preset_paths: Variant = data.get("presets", {})
	if preset_paths is Dictionary:
		for name: Variant in preset_paths:
			library.presets[str(name)] = "res://" + str(preset_paths[name])
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


## Instantiates the debris set for `kind` sized like the component it replaces, or null. Fragments
## sit around the root in their intact positions (contract 4), so placing the root where the
## component was reads as the component breaking apart.
func instance_debris(chapter: String, kind: String, size_px: Vector2) -> Node3D:
	var entry := debris_entry(chapter, kind, size_px)
	if entry.is_empty():
		return null
	var root := _instance(entry)
	if root == null:
		return null
	var reference: Vector2 = Vector2(entry.reference_size_px[0], entry.reference_size_px[1])
	root.scale = Vector3(size_px.x / reference.x, size_px.y / reference.y, 1.0)
	bind_materials(root, chapter)
	return root


## A CPUParticles3D preset scene by name (see data/integrated_assets.json `presets`), or null.
func preset_scene(name: String) -> PackedScene:
	var path: String = presets.get(name, "")
	if path.is_empty():
		return null
	if not _scenes.has(path):
		_scenes[path] = load(path) if ResourceLoader.exists(path) else null
	return _scenes[path]


## Overlay texture for a physics material at a damage level (1 light, 2 heavy), or null. The core
## housing falls back to the electronics overlays when it has none of its own (contract 7).
func damage_overlay(material_id: String, level: int) -> Texture2D:
	var suffix := "light" if level <= 1 else "heavy"
	var path: String = _overlays.get(material_id + "/" + suffix, "")
	if path.is_empty() and material_id == "ai_core_module":
		path = _overlays.get("electronic_module/" + suffix, "")
	return _texture(path)


## The surface material to show at a damage level: `source` itself when intact, otherwise a
## darkened copy with the material's overlay as next pass. Shared per (source, material, level),
## so every rack of the same model uses one material per state. Returns `source` when no overlay
## is integrated for the material.
func damaged_material(source: BaseMaterial3D, material_id: String, level: int) -> BaseMaterial3D:
	if level <= 0 or source == null:
		return source
	level = mini(level, 2)
	var key := "%s|%s|%d" % [source.get_instance_id(), material_id, level]
	if _damaged_materials.has(key):
		return _damaged_materials[key]
	var overlay := _overlay_material(material_id, level)
	if overlay == null:
		_damaged_materials[key] = source
		return source
	var material := source.duplicate() as BaseMaterial3D
	material.albedo_color = Color(source.albedo_color * float(DAMAGE_DARKEN[level]), source.albedo_color.a)
	material.next_pass = overlay
	_damaged_materials[key] = material
	return material


func _overlay_material(material_id: String, level: int) -> StandardMaterial3D:
	var key := "%s/%d" % [material_id, level]
	if _overlay_materials.has(key):
		return _overlay_materials[key]
	var texture := damage_overlay(material_id, level)
	var overlay: StandardMaterial3D = null
	if texture != null:
		overlay = StandardMaterial3D.new()
		overlay.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
		overlay.albedo_texture = texture
		overlay.uv1_triplanar = true
		overlay.uv1_world_triplanar = false
		overlay.uv1_scale = Vector3.ONE * OVERLAY_TILES_PER_METRE
		overlay.roughness = 0.9
		# Drawn over the surface it decorates, never hidden by it.
		overlay.render_priority = 1
	_overlay_materials[key] = overlay
	return overlay


## A texture by asset id (icons, UI art), or null.
func texture(asset_id: String) -> Texture2D:
	return _texture(resource_path(asset_id)) if entries.has(asset_id) else null


## A Godot resource by asset id (themes), or null.
func resource(asset_id: String) -> Resource:
	var path := resource_path(asset_id)
	return load(path) if not path.is_empty() and ResourceLoader.exists(path) else null


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
			# Models that bind their own texture sets (glTF image URIs) keep the authored look.
			if material == null or material.albedo_texture != null or material.normal_texture != null:
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
	if id.begins_with("SHR-DMG-") and str(entry.path).ends_with(".png"):
		# SHR-DMG-REINFORCED_STEEL-LIGHT
		var dmg := id.split("-")
		if dmg.size() == 4:
			_overlays[dmg[2].to_lower() + "/" + dmg[3].to_lower()] = "res://" + str(entry.path)
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
