extends SceneTree
## Loads the operative glb with GLTFDocument, lists nodes and animations, mounts a weapon glb on
## weapon_socket, poses one instance per animation (seek to a given time) under the MissionView
## camera and lighting, and saves a screenshot.
## Usage: godot --path <project> --rendering-driver opengl3 --script char_check.gd -- <out.png> <operative.glb> <weapon.glb> anim:time ...

func _init() -> void:
	await process_frame
	var a := OS.get_cmdline_user_args()
	var out: String = a[0]
	var chr: String = a[1]
	var wpn: String = a[2]
	var shots := a.slice(3)
	var root3d := Node3D.new()
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
	root3d.add_child(sun)
	var fl := MeshInstance3D.new()
	var bm := BoxMesh.new()
	bm.size = Vector3(40, 0.2, 10)
	fl.mesh = bm
	fl.position = Vector3(5, -0.1, 0)
	var fm := StandardMaterial3D.new()
	fm.albedo_color = Color("23282e")
	fl.material_override = fm
	root3d.add_child(fl)
	var x := 0.0
	for s in shots:
		var p := s.split(":")
		var n := _load(chr)
		root3d.add_child(n)
		n.position = Vector3(x, 0, 0)
		var sock := n.find_child("weapon_socket", true, false) as Node3D
		if sock and wpn != "-":
			sock.add_child(_load(wpn))
		var ap := n.find_child("AnimationPlayer", true, false) as AnimationPlayer
		if x == 0.0:
			print("NODES ", _names(n))
			print("ANIMS ", ap.get_animation_list() if ap else "none")
		if ap and p[0] != "rest":
			ap.play(p[0])
			ap.seek(float(p[1]), true)
			ap.pause()
		x += 1.3
	var focus := Vector3((x - 1.3) / 2.0, 1.0, 0.0)
	var k := maxf(0.6, (x * 0.55) / 6.0)
	var cam := Camera3D.new()
	cam.fov = 40.0
	root3d.add_child(cam)
	cam.position = focus + Vector3(0, 0.4 * k, 0) + Vector3(-2.2, 2.3, 10.5) * k
	cam.look_at(focus, Vector3.UP)
	cam.current = true
	for i in 10:
		await process_frame
	get_root().get_texture().get_image().save_png(out)
	print("WROTE ", out)
	quit()


func _names(n: Node) -> Array:
	var r := []
	for c in n.find_children("*", "Node3D", true, false):
		r.append(c.name)
	return r


func _load(path: String) -> Node3D:
	var doc := GLTFDocument.new()
	var st := GLTFState.new()
	doc.append_from_file(path, st)
	var n := doc.generate_scene(st) as Node3D
	for m in n.find_children("*", "MeshInstance3D", true, false):
		var mi := m as MeshInstance3D
		for s in mi.mesh.get_surface_count():
			var mat := mi.mesh.surface_get_material(s) as StandardMaterial3D
			if mat and (mi.mesh.surface_get_format(s) & Mesh.ARRAY_FORMAT_COLOR):
				mat.vertex_color_use_as_albedo = true
	return n
