extends SceneTree
## Assembles a test mission frame from one chapter's kit with the exact MissionView camera, sun and
## environment (ASSET_CONTRACT 9 and 10) and saves a screenshot. Loads glb files at runtime with
## GLTFDocument. Usage:
##   godot --path <project> --rendering-driver opengl3 --script kit_scene.gd -- <out.png> <generated_assets dir> <chapter> <code>

var ga: String
var ch: String
var code: String
var root3d: Node3D


func _init() -> void:
	await process_frame
	var a := OS.get_cmdline_user_args()
	var out: String = a[0]
	ga = a[1]
	ch = a[2]
	code = a[3]
	root3d = Node3D.new()
	get_root().add_child(root3d)
	var env := Environment.new()
	env.background_mode = Environment.BG_COLOR
	env.background_color = Color("15191e")
	env.ambient_light_source = Environment.AMBIENT_SOURCE_COLOR
	env.ambient_light_color = Color("8090a0")
	env.ambient_light_energy = 0.55
	env.tonemap_mode = Environment.TONE_MAPPER_FILMIC
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
	var e := ga + "/environments/" + ch + "/" + code + "_"
	# floor: 4 x 4 m tiles, x -12 .. 20, z -9 .. +5 (tile depth centred on its origin)
	for ix in range(-3, 5):
		for iz in range(0, 4):
			var f := "env_floor_trench_a" if (iz == 1 and ix % 3 == 0) else "env_floor_tile_b"
			_place(e + f + ".glb", Vector3(ix * 4.0, 0.0, 3.0 - iz * 4.0))
	# mid back: wall modules at z -6 with pillars, windows every third module
	var lm := OS.get_environment("TFJ_LANDMARK")
	for ix in range(-3, 6):
		if lm != "" and ix >= -1 and ix <= 0:
			continue
		var w := "env_back_wall_b" if ix % 3 == 1 else "env_back_wall_a"
		_place(e + w + ".glb", Vector3(ix * 4.0 - 2.0, 0.0, -6.3))
	for ix in range(-3, 6, 2):
		_place(e + "env_pillar_a.glb", Vector3(ix * 4.0, 0.0, -5.4))
	_place(e + "env_massing_block_a.glb", Vector3(-7.0, 0.0, -10.0))
	_place(e + "env_massing_tower_b.glb", Vector3(17.0, 0.0, -11.0))
	_place(e + "env_catwalk_a.glb", Vector3(10.0, 2.8, -4.6))
	_place(e + "env_catwalk_a.glb", Vector3(14.0, 2.8, -4.6))
	_place(e + "env_ceiling_truss_a.glb", Vector3(4.0, 7.2, -3.0))
	if lm != "":
		_place(e + "prp_" + lm + "_a.glb", Vector3(-2.0, 0.0, -7.2))
	# near back dressing (z -2.5 .. -4)
	_place(e + "env_low_wall_a.glb", Vector3(-6.0, 0.0, -3.2))
	_place(e + "prp_console_a.glb", Vector3(9.0, 0.0, -3.0))
	_place(e + "prp_crate_stack_a.glb", Vector3(-1.0, 0.0, -3.3))
	_place(e + "prp_pipe_run_a.glb", Vector3(13.0, 0.0, -3.6))
	_place(e + "prp_tank_a.glb", Vector3(-9.5, 0.0, -3.4))
	# gameplay band: statics and components, pivots at the centre of the collision rect
	_place(e + "env_ledge_static_a.glb", Vector3(2.0, 2.0, 0.0))
	_place(e + "env_plinth_static_a.glb", Vector3(7.5, 0.3, 0.0))
	var comps := OS.get_environment("TFJ_COMPONENTS").split(",", false)
	var x := 1.0
	for c in comps:
		var parts := c.split(":")
		var n := _place(ga + "/destructibles/" + ch + "/" + parts[0] + ".glb", Vector3.ZERO)
		if n == null:
			continue
		var hh := float(parts[1])
		var ww := float(parts[2])
		n.position = Vector3(x + ww / 2.0, hh / 2.0 + (0.6 if parts[0].contains("_core_") else 0.0), 0.0)
		x += ww + float(parts[3]) if parts.size() > 3 else ww + 0.6
	var focus := Vector3(4.0, 1.6, 0.0)
	var cam := Camera3D.new()
	cam.fov = 40.0
	root3d.add_child(cam)
	cam.position = focus + Vector3(-2.2, 2.3, 10.5)
	cam.look_at(focus + Vector3(0.0, -0.4, 0.0), Vector3.UP)
	cam.current = true
	for i in 12:
		await process_frame
	get_root().get_texture().get_image().save_png(out)
	print("WROTE ", out)
	quit()


func _place(path: String, pos: Vector3) -> Node3D:
	if not FileAccess.file_exists(path):
		print("MISSING ", path)
		return null
	var doc := GLTFDocument.new()
	var st := GLTFState.new()
	if doc.append_from_file(path, st) != OK:
		print("LOADFAIL ", path)
		return null
	var n := doc.generate_scene(st) as Node3D
	for m in n.find_children("*", "MeshInstance3D", true, false):
		var mi := m as MeshInstance3D
		if mi.name != "mesh_intact" and mi.name.begins_with("mesh_"):
			mi.visible = false
		for s in mi.mesh.get_surface_count():
			var mat := mi.mesh.surface_get_material(s) as StandardMaterial3D
			if mat and (mi.mesh.surface_get_format(s) & Mesh.ARRAY_FORMAT_COLOR):
				mat.vertex_color_use_as_albedo = true
	n.position = pos
	root3d.add_child(n)
	return n
