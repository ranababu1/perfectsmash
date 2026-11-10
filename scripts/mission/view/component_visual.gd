class_name ComponentVisual
extends Node3D
## The 3D look of one facility component. Follows its physics body (MissionView sets position
## and rotation every frame) and shows its damage state. Uses the integrated production model
## (AssetLibrary) when one exists for the component's kind, otherwise the greybox box: the
## physics rectangle extruded to the kind's depth. Either way the front face is the collision
## rectangle, centred on the physics plane (ASSET_CONTRACT 3). Damaged and critical states also
## swap the main surfaces to darkened copies carrying the material's damage overlay (contract 8).

## Physics rectangle in metres (x, y) and visual depth (z).
var size_m := Vector3.ONE
## Colour used for debris and for greybox tinting.
var base_color := Color.GRAY
## True when a production model is shown (false: greybox fallback).
var uses_model := false
## Asset id of the model, "" for the greybox.
var asset_id := ""
## Physics material id (data/materials.json); selects the damage overlay.
var material_id := ""
## Component kind and physics size, so the view can spawn the matching debris set.
var kind := ""
var size_px := Vector2.ONE
## Damage overlay level shown on the main surfaces (0 none, 1 light, 2 heavy).
var overlay_level := 0
var _library: AssetLibrary
## Main-material surfaces of the model: [MeshInstance3D, surface index, base material].
var _main_surfaces := []
var _model: Node3D
var _box_material: StandardMaterial3D
var _pulse := false
var _state := 0
## Frames left showing every state node (shader warm-up), then the real state is applied.
var _warm_frames := 0
const WARM_FRAMES := 2


## look = [depth m, colour, emission colour or null, emission energy] (MissionView.KINDS).
static func create(component: Dictionary, look: Array, library: AssetLibrary, chapter: String) -> ComponentVisual:
	var visual := ComponentVisual.new()
	visual.name = "Visual_" + str(component.id)
	visual.base_color = look[1]
	var size_px: Vector2 = component.size
	visual.size_px = size_px
	visual.kind = str(component.kind)
	visual.material_id = str(component.get("material", ""))
	visual._library = library
	visual.size_m = ViewMapping.size_to_3d(size_px, look[0])
	visual._pulse = component.get("critical_asset", false)
	var model := library.instance_component(chapter, component.kind, size_px) if library != null else null
	if model != null:
		visual.uses_model = true
		visual.asset_id = str(library.component_entry(chapter, component.kind, size_px).id)
		visual._model = model
		visual.add_child(model)
		visual._collect_main_surfaces(AssetLibrary.CHAPTER_CODES.get(chapter, ""))
		# Draw every state node for the first frames so their shaders compile while the mission
		# loads; first showing mesh_light/mesh_heavy mid-play stalled 1.7 s on the emulator.
		for node_name: String in ["mesh_intact", "mesh_light", "mesh_heavy"]:
			var node := model.find_child(node_name, true, false) as Node3D
			if node != null:
				node.visible = true
		# The heavy overlay pass is drawn during warm-up too, so its transparent triplanar shader
		# compiles with the mission instead of on the first hit.
		visual._apply_overlay(2)
		visual._warm_frames = WARM_FRAMES
	else:
		visual._build_box(look)
	return visual


func set_state(state: int) -> void:
	_state = state
	if uses_model:
		if _warm_frames <= 0:
			AssetLibrary.set_state_nodes(_model, state)
			_apply_overlay(_overlay_level_for(state))
		return
	match state:
		DamageableComponent.State.DAMAGED:
			_box_material.albedo_color = base_color.darkened(0.25)
		DamageableComponent.State.CRITICAL:
			_box_material.albedo_color = base_color.darkened(0.45)
			_box_material.emission = Color("ff4a30")
			_box_material.emission_energy_multiplier = 0.8


## Per-frame emphasis for critical assets (greybox: pulsing emission).
func animate(time: float) -> void:
	if _warm_frames > 0:
		_warm_frames -= 1
		if _warm_frames == 0:
			AssetLibrary.set_state_nodes(_model, _state)
			_apply_overlay(_overlay_level_for(_state))
	if _pulse and _box_material != null:
		_box_material.emission_energy_multiplier = 1.0 + sin(time * 4.0) * 0.4


## Overlay level per damage state: light when DAMAGED, heavy from CRITICAL on.
static func _overlay_level_for(state: int) -> int:
	if state >= DamageableComponent.State.CRITICAL:
		return 2
	if state >= DamageableComponent.State.DAMAGED:
		return 1
	return 0


## Surfaces in a `mat_<material>_<ch>[_zone]` slot (contract 7), across every state node.
func _collect_main_surfaces(code: String) -> void:
	for mesh_instance: MeshInstance3D in _model.find_children("*", "MeshInstance3D", true, false):
		var mesh := mesh_instance.mesh
		if mesh == null:
			continue
		for surface in mesh.get_surface_count():
			var base := mesh_instance.get_surface_override_material(surface) as BaseMaterial3D
			if base == null:
				base = mesh.surface_get_material(surface) as BaseMaterial3D
			if base == null or AssetLibrary.slot_material_id(base.resource_name, code).is_empty():
				continue
			_main_surfaces.append([mesh_instance, surface, base])


func _apply_overlay(level: int) -> void:
	if _library == null or material_id.is_empty():
		return
	overlay_level = level
	for entry: Array in _main_surfaces:
		var mesh_instance: MeshInstance3D = entry[0]
		mesh_instance.set_surface_override_material(entry[1], _library.damaged_material(entry[2], material_id, level))


func _build_box(look: Array) -> void:
	var material := StandardMaterial3D.new()
	material.albedo_color = look[1]
	material.roughness = 0.75
	material.metallic = 0.25
	# Emission stays enabled (black when unlit) so turning CRITICAL later only changes values,
	# not the shader variant: a variant switch mid-play costs a shader compile.
	material.emission_enabled = true
	material.emission = look[2] if look[2] != null else Color.BLACK
	material.emission_energy_multiplier = look[3] if look[2] != null else 0.0
	var box := BoxMesh.new()
	box.size = size_m
	var mesh := MeshInstance3D.new()
	mesh.mesh = box
	mesh.material_override = material
	add_child(mesh)
	_box_material = material
