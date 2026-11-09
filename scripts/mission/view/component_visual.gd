class_name ComponentVisual
extends Node3D
## The 3D look of one facility component. Follows its physics body (MissionView sets position
## and rotation every frame) and shows its damage state. Uses the integrated production model
## (AssetLibrary) when one exists for the component's kind, otherwise the greybox box: the
## physics rectangle extruded to the kind's depth. Either way the front face is the collision
## rectangle, centred on the physics plane (ASSET_CONTRACT 3).

## Physics rectangle in metres (x, y) and visual depth (z).
var size_m := Vector3.ONE
## Colour used for debris and for greybox tinting.
var base_color := Color.GRAY
## True when a production model is shown (false: greybox fallback).
var uses_model := false
## Asset id of the model, "" for the greybox.
var asset_id := ""
var _model: Node3D
var _box_material: StandardMaterial3D
var _pulse := false


## look = [depth m, colour, emission colour or null, emission energy] (MissionView.KINDS).
static func create(component: Dictionary, look: Array, library: AssetLibrary, chapter: String) -> ComponentVisual:
	var visual := ComponentVisual.new()
	visual.name = "Visual_" + str(component.id)
	visual.base_color = look[1]
	var size_px: Vector2 = component.size
	visual.size_m = ViewMapping.size_to_3d(size_px, look[0])
	visual._pulse = component.get("critical_asset", false)
	var model := library.instance_component(chapter, component.kind, size_px) if library != null else null
	if model != null:
		visual.uses_model = true
		visual.asset_id = str(library.component_entry(chapter, component.kind, size_px).id)
		visual._model = model
		visual.add_child(model)
	else:
		visual._build_box(look)
	return visual


func set_state(state: int) -> void:
	if uses_model:
		AssetLibrary.set_state_nodes(_model, state)
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
	if _pulse and _box_material != null:
		_box_material.emission_energy_multiplier = 1.0 + sin(time * 4.0) * 0.4


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
