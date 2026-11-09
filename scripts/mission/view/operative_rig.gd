class_name OperativeRig
extends Node3D
## Placeholder operative built from primitives: anonymous (helmet with a visor, no face), facing
## the facility (+x). It is part of play, not decoration: the weapon arm tracks the aim, the body
## recoils on each shot, lowers the weapon while reloading and reacts to the mission outcome.
## Detailed models replace the meshes later; the state machine stays.

enum State { IDLE, READY, AIM, RELOAD, VICTORY, DEFEAT }

const SHOULDER := Vector3(0.12, 1.42, 0.0)
const RECOIL_DECAY := 9.0
const BODY_COLOR := Color("2b3138")
const ARMOR_COLOR := Color("3d4650")
const VISOR_COLOR := Color("5fd4e8")

var state := State.IDLE
var aim_angle := 0.0
var weapon_id := "kinetic_accelerator"
var _time := 0.0
var _recoil := 0.0
var _torso: Node3D
var _arm: Node3D
var _weapons := {}
var _arm_angle := 0.0


func _ready() -> void:
	_torso = Node3D.new()
	add_child(_torso)
	_add_box(self, Vector3(0.16, 0.8, 0.18), Vector3(-0.07, 0.4, 0.05), BODY_COLOR)  # legs
	_add_box(self, Vector3(0.16, 0.8, 0.18), Vector3(0.07, 0.4, -0.05), BODY_COLOR)
	_add_box(_torso, Vector3(0.36, 0.55, 0.28), Vector3(0.0, 1.12, 0.0), ARMOR_COLOR)  # torso
	_add_box(_torso, Vector3(0.22, 0.42, 0.2), Vector3(-0.24, 1.15, 0.0), BODY_COLOR)  # pack
	var helmet := MeshInstance3D.new()
	var sphere := SphereMesh.new()
	sphere.radius = 0.15
	sphere.height = 0.32
	helmet.mesh = sphere
	helmet.material_override = _material(ARMOR_COLOR)
	helmet.position = Vector3(0.02, 1.58, 0.0)
	_torso.add_child(helmet)
	var visor := _add_box(_torso, Vector3(0.06, 0.07, 0.22), Vector3(0.14, 1.6, 0.0), VISOR_COLOR)
	(visor.material_override as StandardMaterial3D).emission_enabled = true
	(visor.material_override as StandardMaterial3D).emission = VISOR_COLOR
	(visor.material_override as StandardMaterial3D).emission_energy_multiplier = 1.5

	_arm = Node3D.new()
	_arm.position = SHOULDER
	_torso.add_child(_arm)
	_add_box(_arm, Vector3(0.36, 0.1, 0.1), Vector3(0.16, 0.0, 0.12), BODY_COLOR)
	# Kinetic Accelerator: long, slim rail with a cyan coil.
	var kinetic := Node3D.new()
	_add_box(kinetic, Vector3(0.62, 0.08, 0.08), Vector3(0.48, 0.02, 0.12), Color("4a535d"))
	var coil := _add_box(kinetic, Vector3(0.14, 0.11, 0.11), Vector3(0.36, 0.02, 0.12), VISOR_COLOR)
	(coil.material_override as StandardMaterial3D).emission_enabled = true
	(coil.material_override as StandardMaterial3D).emission = VISOR_COLOR
	_arm.add_child(kinetic)
	_weapons["kinetic_accelerator"] = kinetic
	# Breach Charge launcher: short, thick tube with an amber arming band.
	var breach := Node3D.new()
	_add_box(breach, Vector3(0.38, 0.16, 0.16), Vector3(0.36, 0.03, 0.12), Color("4d4a44"))
	var band := _add_box(breach, Vector3(0.06, 0.18, 0.18), Vector3(0.5, 0.03, 0.12), Color("e0a040"))
	(band.material_override as StandardMaterial3D).emission_enabled = true
	(band.material_override as StandardMaterial3D).emission = Color("e0a040")
	_arm.add_child(breach)
	_weapons["breach_charge"] = breach
	set_weapon(weapon_id)


func set_weapon(id: String) -> void:
	weapon_id = id
	for key: String in _weapons:
		(_weapons[key] as Node3D).visible = key == id


func set_state(next: State) -> void:
	state = next


## `angle` is counter-clockwise from facing straight at the facility (+x), in radians.
func set_aim(angle: float) -> void:
	aim_angle = clampf(angle, -0.6, 1.35)


func fire() -> void:
	_recoil = 1.0


func _process(delta: float) -> void:
	_time += delta
	_recoil = maxf(0.0, _recoil - delta * RECOIL_DECAY * _recoil - delta)
	var target := 0.0
	var bob := sin(_time * 1.8) * 0.012
	var lean := 0.0
	match state:
		State.IDLE:
			target = -0.9
		State.READY:
			target = -0.25
		State.AIM:
			target = aim_angle
		State.RELOAD:
			target = -0.7
			lean = 0.06
		State.VICTORY:
			target = 1.2
			bob = absf(sin(_time * 4.0)) * 0.03
		State.DEFEAT:
			target = -1.1
			lean = 0.18
	_arm_angle = lerpf(_arm_angle, target, clampf(delta * 12.0, 0.0, 1.0))
	_arm.rotation = Vector3(0.0, 0.0, _arm_angle + _recoil * 0.25)
	_arm.position = SHOULDER + Vector3(-_recoil * 0.08, 0.0, 0.0)
	_torso.position = Vector3(-_recoil * 0.05, bob, 0.0)
	_torso.rotation = Vector3(0.0, 0.0, -lean + _recoil * 0.05)


func _add_box(parent: Node3D, size: Vector3, at: Vector3, color: Color) -> MeshInstance3D:
	var mesh := MeshInstance3D.new()
	var box := BoxMesh.new()
	box.size = size
	mesh.mesh = box
	mesh.position = at
	mesh.material_override = _material(color)
	parent.add_child(mesh)
	return mesh


static func _material(color: Color) -> StandardMaterial3D:
	var material := StandardMaterial3D.new()
	material.albedo_color = color
	material.roughness = 0.7
	material.metallic = 0.3
	return material
