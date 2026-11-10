extends SceneTree
## Builds the CPUParticles3D preset scenes in res://assets/vfx/godot/presets/.
## Run (Godot 4.7.2): godot --headless --path <project> --script res://assets/vfx/godot/tools/build_presets.gd

const V := "res://assets/vfx/"
const OUT := "res://assets/vfx/godot/presets/"


func _mat(tex_path: String, h: int, v: int, add: bool, loop := false) -> StandardMaterial3D:
	var m := StandardMaterial3D.new()
	m.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
	m.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
	if add:
		m.blend_mode = BaseMaterial3D.BLEND_MODE_ADD
	m.billboard_mode = BaseMaterial3D.BILLBOARD_PARTICLES
	m.billboard_keep_scale = true
	m.particles_anim_h_frames = h
	m.particles_anim_v_frames = v
	m.particles_anim_loop = loop
	m.vertex_color_use_as_albedo = true
	m.albedo_texture = load(V + tex_path)
	return m


func _emitter(name: String, tex: String, h: int, v: int, add: bool, size: float, lifetime: float, amount := 1, loop_anim := false) -> CPUParticles3D:
	var p := CPUParticles3D.new()
	p.name = name
	p.amount = amount
	p.lifetime = lifetime
	p.one_shot = true
	p.explosiveness = 1.0
	p.emitting = false
	p.local_coords = false
	var q := QuadMesh.new()
	q.size = Vector2(size, size)
	p.mesh = q
	p.material_override = _mat(tex, h, v, add, loop_anim)
	p.gravity = Vector3.ZERO
	p.spread = 0.0
	p.initial_velocity_min = 0.0
	p.initial_velocity_max = 0.0
	if h * v > 1:
		p.anim_speed_min = 1.0
		p.anim_speed_max = 1.0
	return p


func _root(name: String, note: String) -> Node3D:
	var r := Node3D.new()
	r.name = name
	r.set_meta("tfj_note", note)
	return r


func _save(root: Node3D, file: String) -> void:
	for c in root.get_children():
		c.owner = root
	var ps := PackedScene.new()
	var err := ps.pack(root)
	if err != OK:
		push_error("pack failed " + file)
		return
	err = ResourceSaver.save(ps, OUT + file)
	print("PRESET ", file, " save=", err)
	root.free()


func _breach() -> void:
	var r := _root("VfxBreachExplosion", "Breach Charge detonation at base blast_radius 140 px (1.4 m). Set emitting = true on every child; scale the root by blast_radius / 140. Free after 1.2 s.")
	r.add_child(_emitter("Debris", "shared/opr_vfx_breach_debris_a.png", 4, 4, false, 3.2, 0.67))
	r.add_child(_emitter("Fireball", "shared/opr_vfx_breach_explosion_a.png", 4, 4, true, 3.1, 0.67))
	r.add_child(_emitter("Shockwave", "shared/opr_vfx_breach_shockwave_a.png", 4, 4, true, 3.2, 0.53))
	r.add_child(_emitter("Activation", "shared/opr_vfx_breach_activation_a.png", 4, 2, true, 1.4, 0.27))
	var smoke := _emitter("Smoke", "shared/shr_vfx_smoke_puff_a.png", 4, 4, false, 1.3, 1.1, 6)
	smoke.explosiveness = 0.85
	smoke.direction = Vector3.UP
	smoke.spread = 70.0
	smoke.initial_velocity_min = 0.6
	smoke.initial_velocity_max = 1.4
	smoke.damping_min = 0.8
	smoke.damping_max = 1.2
	smoke.scale_amount_min = 0.9
	smoke.scale_amount_max = 1.8
	smoke.angle_min = -180.0
	smoke.angle_max = 180.0
	smoke.emission_shape = CPUParticles3D.EMISSION_SHAPE_SPHERE
	smoke.emission_sphere_radius = 0.4
	smoke.sorting_offset = -0.2
	r.add_child(smoke)
	var sparks := _emitter("Sparks", "shared/particles/shr_vfx_particle_spark_a.png", 1, 1, true, 0.35, 0.55, 28)
	(sparks.mesh as QuadMesh).size = Vector2(0.42, 0.1)
	sparks.spread = 180.0
	sparks.direction = Vector3.UP
	sparks.initial_velocity_min = 5.0
	sparks.initial_velocity_max = 11.0
	sparks.gravity = Vector3(0, -9.8, 0)
	sparks.damping_min = 2.0
	sparks.damping_max = 4.0
	sparks.particle_flag_align_y = true
	sparks.color = Color("ffd59a")
	(sparks.material_override as StandardMaterial3D).billboard_mode = BaseMaterial3D.BILLBOARD_DISABLED
	r.add_child(sparks)
	_save(r, "vfx_breach_explosion.tscn")


func _simple(file: String, root_name: String, note: String, tex: String, h: int, v: int, add: bool, size: float, lifetime: float) -> void:
	var r := _root(root_name, note)
	var e := _emitter("Main", tex, h, v, add, size, lifetime)
	if not file.contains("metal"):
		e.angle_min = -180.0
		e.angle_max = 180.0
	r.add_child(e)
	_save(r, file)


func _kinetic() -> void:
	_simple("vfx_kinetic_impact.tscn", "VfxKineticImpact", "Kinetic slug hit flash (any material). Add the material preset as a sibling.",
		"shared/opr_vfx_kinetic_impact_a.png", 4, 4, true, 1.2, 0.53)
	var r := _root("VfxKineticMuzzle", "Muzzle flash; parent to the weapon socket, rotate to the aim angle (quad faces +Z, flash points +X).")
	var e := _emitter("Main", "shared/opr_vfx_kinetic_muzzle_a.png", 4, 2, true, 0.6, 0.27)
	e.local_coords = true
	e.position = Vector3(0.6 * 0.34, 0, 0)  # pivot u = 0.16: shift the quad so the barrel tip sits at the node origin (aim right; for other angles set angle_min = angle_max = -aim_degrees and offset along the aim)
	r.add_child(e)
	_save(r, "vfx_kinetic_muzzle.tscn")
	_simple("vfx_impact_metal.tscn", "VfxImpactMetal", "Metal impact sparks; rotate the root so +Y is the surface normal (sheet origin at v = 0.65).",
		"shared/shr_vfx_impact_metal_a.png", 4, 4, true, 1.4, 0.53)
	_simple("vfx_impact_glass.tscn", "VfxImpactGlass", "Glass impact crack and shards.", "shared/shr_vfx_impact_glass_a.png", 4, 4, true, 1.2, 0.53)
	_simple("vfx_impact_electric.tscn", "VfxImpactElectric", "Electronic impact arcs.", "shared/shr_vfx_impact_electric_a.png", 4, 4, true, 1.2, 0.53)
	_simple("vfx_impact_concrete.tscn", "VfxImpactConcrete", "Concrete / composite impact dust (alpha blend).", "shared/shr_vfx_dust_concrete_a.png", 4, 4, false, 1.1, 0.8)


func _component() -> void:
	var r := _root("VfxComponentCollapse", "Component removed / toppled at ground level: collapse dust plus small chips. Scale the root by component width / 1.6 m.")
	var dust := _emitter("Dust", "shared/shr_vfx_dust_collapse_a.png", 4, 4, false, 4.0, 1.0)
	dust.position = Vector3(0, 4.0 * (0.5 - 0.14), 0)  # ground at v = 0.86
	r.add_child(dust)
	var chips := _emitter("Chips", "shared/shr_vfx_debris_chip_small_a.png", 4, 4, false, 0.16, 1.0, 18)
	chips.anim_speed_min = 0.0
	chips.anim_speed_max = 0.0
	chips.anim_offset_min = 0.0
	chips.anim_offset_max = 1.0
	chips.direction = Vector3.UP
	chips.spread = 65.0
	chips.initial_velocity_min = 2.0
	chips.initial_velocity_max = 4.5
	chips.gravity = Vector3(0, -9.8, 0)
	chips.angle_min = -180.0
	chips.angle_max = 180.0
	chips.angular_velocity_min = -360.0
	chips.angular_velocity_max = 360.0
	chips.scale_amount_min = 0.6
	chips.scale_amount_max = 1.4
	chips.emission_shape = CPUParticles3D.EMISSION_SHAPE_BOX
	chips.emission_box_extents = Vector3(0.6, 0.3, 0.1)
	chips.position = Vector3(0, 0.3, 0)
	r.add_child(chips)
	_save(r, "vfx_component_collapse.tscn")

	var f := _root("VfxBurningLoop", "Looping fire with smoke for burning components. Leave emitting on; stop by setting emitting = false.")
	var fire := _emitter("Fire", "shared/shr_vfx_fire_loop_a.png", 4, 4, true, 1.2, 0.8, 1, true)
	fire.one_shot = false
	fire.position = Vector3(0, 1.2 * 0.44, 0)
	f.add_child(fire)
	var smoke := _emitter("Smoke", "shared/shr_vfx_smoke_loop_a.png", 4, 4, false, 2.0, 1.33, 1, true)
	smoke.one_shot = false
	smoke.position = Vector3(0, 0.9 + 2.0 * 0.45, -0.05)
	f.add_child(smoke)
	_save(f, "vfx_burning_loop.tscn")


func _critical() -> void:
	var r := _root("VfxCriticalCoreDestroyed", "Critical asset destroyed (mission win). Set emitting = true on every child. Free after 1.5 s.")
	r.add_child(_emitter("Burst", "shared/shr_vfx_critical_core_destruction_a.png", 4, 4, true, 3.6, 0.67))
	r.add_child(_emitter("Discharge", "shared/shr_vfx_energy_discharge_a.png", 4, 4, true, 2.2, 0.67))
	var smoke := _emitter("Smoke", "shared/shr_vfx_smoke_puff_a.png", 4, 4, false, 1.4, 1.2, 5)
	smoke.direction = Vector3.UP
	smoke.spread = 80.0
	smoke.initial_velocity_min = 0.5
	smoke.initial_velocity_max = 1.2
	smoke.angle_min = -180.0
	smoke.angle_max = 180.0
	smoke.sorting_offset = -0.2
	r.add_child(smoke)
	_save(r, "vfx_critical_core_destroyed.tscn")
	var idle := _root("VfxCriticalCoreIdle", "Looping red core glow; place on the critical asset core until destroyed.")
	var e := _emitter("Glow", "shared/shr_vfx_critical_core_idle_a.png", 4, 4, true, 1.1, 1.0, 1, true)
	e.one_shot = false
	idle.add_child(e)
	_save(idle, "vfx_critical_core_idle.tscn")


func _init() -> void:
	DirAccess.make_dir_recursive_absolute(ProjectSettings.globalize_path(OUT))
	_breach()
	_kinetic()
	_component()
	_critical()
	quit()
