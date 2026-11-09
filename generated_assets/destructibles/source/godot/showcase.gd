extends SceneTree
## Premium showcase renderer (3d-kits uplift pass). Builds a composed scene from a layout JSON under the
## exact MissionView camera (FOV 40, offset (-2.2, 2.3, 10.5), look 0.4 m below the focus) and renders it
## with GL Compatibility. Applies the ASSET_CONTRACT loader rules to every imported glb (one state node
## visible, COLOR_0 as albedo multiplier, emission maps as masks with EMISSION_OP_MULTIPLY).
## Usage: godot --path <project> --rendering-driver opengl3 --script showcase.gd -- <layout.json> <out.png> [asis|showcase]
## Layout: {"ga": "<generated_assets dir>", "focus": [x,y,z], "items": [{"f": "destructibles/helix/x.glb",
##   "p": [x,y,z], "r": deg_y, "s": scale, "state": "mesh_intact", "anim": "aim_pose", "t": 0.5,
##   "mount": {"f": "...", "socket": "weapon_socket"}}], "lights": [{"type": "omni", "p": [..], "c": "hex",
##   "e": energy, "r": range}]}
## Modes: "asis" = MissionView exactly as the game ships it today (no sky, no glow, no fog);
## "showcase" = the contract's proposed reflection sky plus rim light, glow, depth fog and local lights.

var root3d: Node3D
var ga: String


func _init() -> void:
	await process_frame
	var a := OS.get_cmdline_user_args()
	var layout: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(a[0]))
	var out: String = a[1]
	var mode: String = a[2] if a.size() > 2 else "showcase"
	ga = layout["ga"]
	root3d = Node3D.new()
	get_root().add_child(root3d)
	_environment(mode, layout)
	if mode == "showcase":  # graded frames only: optional emission trim so cyan does not clip to white under ACES
		emit_scale = float(layout.get("emission_scale", 1.0))
	for it in layout["items"]:
		_place(it)
	if mode == "showcase":
		for l in layout.get("lights", []):
			_light(l)
	var focus := _v3(layout.get("focus", [0, 1.6, 0]))
	var cam := Camera3D.new()
	cam.fov = 40.0
	cam.far = 200.0
	root3d.add_child(cam)
	cam.position = focus + Vector3(-2.2, 2.3, 10.5) * float(layout.get("zoom", 1.0))
	cam.look_at(focus + Vector3(0.0, -0.4, 0.0), Vector3.UP)
	cam.current = true
	for i in 16:
		await process_frame
	get_root().get_texture().get_image().save_png(out)
	print("WROTE ", out)
	quit()


func _v3(p) -> Vector3:
	return Vector3(float(p[0]), float(p[1]), float(p[2]))


func _environment(mode: String, layout: Dictionary) -> void:
	var env := Environment.new()
	env.background_mode = Environment.BG_COLOR
	env.background_color = Color("15191e")
	env.ambient_light_source = Environment.AMBIENT_SOURCE_COLOR
	env.ambient_light_color = Color("8090a0")
	env.ambient_light_energy = 0.55
	env.tonemap_mode = Environment.TONE_MAPPER_FILMIC
	if mode == "showcase":
		# ASSET_CONTRACT 9 proposed reflection source (sky only for reflections; background stays flat)
		var sky_mat := ProceduralSkyMaterial.new()
		sky_mat.sky_top_color = Color("4a5866")
		sky_mat.sky_horizon_color = Color("8090a0")
		sky_mat.ground_horizon_color = Color("3a4048")
		sky_mat.ground_bottom_color = Color("1b2026")
		sky_mat.energy_multiplier = float(layout.get("sky_energy", 0.6))
		var sky := Sky.new()
		sky.sky_material = sky_mat
		env.sky = sky
		env.reflected_light_source = Environment.REFLECTION_SOURCE_SKY
		env.ambient_light_energy = float(layout.get("ambient", 0.45))
		env.tonemap_mode = Environment.TONE_MAPPER_ACES
		env.tonemap_exposure = float(layout.get("exposure", 1.05))
		env.glow_enabled = true
		env.glow_intensity = float(layout.get("glow", 0.9))
		env.glow_strength = 1.0
		env.glow_bloom = 0.02
		env.glow_hdr_threshold = 0.85
		env.glow_blend_mode = Environment.GLOW_BLEND_MODE_SCREEN
		env.set_glow_level(1, 1.0)
		env.set_glow_level(2, 1.0)
		env.set_glow_level(3, 0.6)
		env.set_glow_level(4, 0.3)
		env.fog_enabled = true
		env.fog_mode = Environment.FOG_MODE_DEPTH
		env.fog_light_color = Color("1c2530")
		env.fog_density = 1.0
		env.fog_sky_affect = 0.0
		env.fog_depth_begin = float(layout.get("fog_begin", 14.0))
		env.fog_depth_end = float(layout.get("fog_end", 42.0))
		env.fog_depth_curve = 1.4
		env.adjustment_enabled = true
		env.adjustment_contrast = 1.08
		env.adjustment_saturation = 1.05
	if mode != "showcase" and layout.has("asis_exposure"):
		# presentation lift for phone screens (layout opt-in); the strict MissionView test frame omits it
		env.tonemap_exposure = float(layout["asis_exposure"])
		env.ambient_light_energy = float(layout.get("asis_ambient", 0.55))
	var we := WorldEnvironment.new()
	we.environment = env
	root3d.add_child(we)
	var sun := DirectionalLight3D.new()
	sun.rotation_degrees = Vector3(-52.0, -38.0, 0.0)
	sun.light_energy = 1.15
	sun.light_color = Color("dfe8f0")
	sun.shadow_enabled = true
	sun.directional_shadow_max_distance = 40.0
	root3d.add_child(sun)
	if layout.has("fill"):  # soft camera-side fill, no shadow, keeps the low-key mood
		var fill := DirectionalLight3D.new()
		fill.rotation_degrees = Vector3(-18.0, -8.0, 0.0)
		fill.light_energy = float(layout["fill"])
		fill.light_color = Color("cfdcea")
		fill.light_specular = 0.3
		root3d.add_child(fill)
	if mode == "showcase":
		var rim := DirectionalLight3D.new()  # cool back rim from behind-right, no shadow
		rim.rotation_degrees = Vector3(-28.0, 150.0, 0.0)
		rim.light_energy = float(layout.get("rim", 0.9))
		rim.light_color = Color("8fc4ff")
		rim.light_specular = 1.4
		root3d.add_child(rim)


func _light(l: Dictionary) -> void:
	var n: Light3D
	if l.get("type", "omni") == "spot":
		var s := SpotLight3D.new()
		s.spot_range = float(l.get("r", 6.0))
		s.spot_angle = float(l.get("angle", 40.0))
		n = s
	else:
		var o := OmniLight3D.new()
		o.omni_range = float(l.get("r", 4.0))
		o.omni_attenuation = float(l.get("att", 1.4))
		n = o
	n.light_color = Color(l.get("c", "5fd4e8"))
	n.light_energy = float(l.get("e", 1.5))
	n.shadow_enabled = bool(l.get("shadow", false))
	root3d.add_child(n)
	n.position = _v3(l["p"])
	if l.has("look"):
		n.look_at(_v3(l["look"]), Vector3.UP)


var emit_scale := 1.0


func loader_rules(n: Node, state: String) -> void:
	for m in n.find_children("*", "MeshInstance3D", true, false):
		var mi := m as MeshInstance3D
		if mi.name.begins_with("mesh_") and mi.name != state:
			mi.visible = false
		for s in mi.mesh.get_surface_count():
			var mat := mi.mesh.surface_get_material(s) as StandardMaterial3D
			if mat == null:
				continue
			if mi.mesh.surface_get_format(s) & Mesh.ARRAY_FORMAT_COLOR:
				mat.vertex_color_use_as_albedo = true
			if mat.emission_enabled and mat.emission_texture:
				mat.emission_operator = BaseMaterial3D.EMISSION_OP_MULTIPLY
			if mat.emission_enabled and emit_scale != 1.0:
				mat.emission_energy_multiplier *= emit_scale


func _load(f: String) -> Node3D:
	var path := ga + "/" + f
	if not FileAccess.file_exists(path):
		print("MISSING ", path)
		return null
	var doc := GLTFDocument.new()
	var st := GLTFState.new()
	if doc.append_from_file(path, st) != OK:
		print("LOADFAIL ", path)
		return null
	return doc.generate_scene(st) as Node3D


func _place(it: Dictionary) -> void:
	var n := _load(it["f"])
	if n == null:
		return
	loader_rules(n, it.get("state", "mesh_intact"))
	n.position = _v3(it.get("p", [0, 0, 0]))
	n.rotation_degrees.y = float(it.get("r", 0.0))
	var sc = it.get("s", 1.0)
	n.scale = _v3(sc) if sc is Array else Vector3.ONE * float(sc)
	root3d.add_child(n)
	if it.has("anim"):
		var ap := n.find_children("*", "AnimationPlayer", true, false)
		if ap.size() > 0:
			var p := ap[0] as AnimationPlayer
			p.play(it["anim"])
			p.seek(float(it.get("t", 0.0)), true)
			p.pause()
	if it.has("mount"):
		var mt: Dictionary = it["mount"]
		var sock := n.find_child(mt.get("socket", "weapon_socket"), true, false)
		var w := _load(mt["f"])
		if sock and w:
			loader_rules(w, "mesh_intact")
			sock.add_child(w)
