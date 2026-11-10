extends SceneTree
## Loads kit glb files with Godot's own glTF importer (GLTFDocument, the code path the editor import uses)
## and renders them under the MissionView camera direction, sun and environment (ASSET_CONTRACT 9).
## Usage (needs a display, e.g. xvfb-run, and the GL Compatibility renderer):
##   godot --path <any project> --rendering-driver opengl3 --script kit_lineup.gd -- <out.png> <mode> <files...>
## mode "lineup": every file's mesh_intact side by side (other mesh_* nodes hidden).
## mode "states": first file is a component, second its debris set: intact | light | heavy | destroyed.
## Prints one CHECK line per file (nodes, surfaces, materials, vertex colours) so the run doubles as a test.

const CAMERA_OFFSET := Vector3(-2.2, 2.3, 10.5)

func _init() -> void:
	await process_frame
	var args := OS.get_cmdline_user_args()
	var out: String = args[0]
	var mode: String = args[1]
	var files := args.slice(2)
	var root3d := Node3D.new()
	get_root().add_child(root3d)
	_environment(root3d)
	var items: Array[Node3D] = []
	if mode == "states":
		var comp := _load(files[0])
		var deb := _load(files[1]) if files.size() > 1 else null
		for state in ["mesh_intact", "mesh_light", "mesh_heavy"]:
			var inst := comp.duplicate() as Node3D
			_show_only(inst, state)
			items.append(inst)
		if deb:
			items.append(deb)
		comp.free()
	else:
		for f in files:
			var n := _load(f)
			if n:
				_show_only(n, "mesh_intact")
				items.append(n)
	var x := 0.0
	var top := 0.0
	var gap := 0.35
	for n in items:
		root3d.add_child(n)
		var b := _aabb(n)
		n.position = Vector3(x - b.position.x, -b.position.y, -(b.position.z + b.size.z / 2.0))
		x += b.size.x + gap
		top = maxf(top, b.size.y)
	var width := x - gap
	var focus := Vector3(width / 2.0, top * 0.5, 0.0)
	var hfov := 2.0 * atan(tan(deg_to_rad(20.0)) * 16.0 / 9.0)
	var dist := (1.2 if mode == "states" else 1.0) * maxf((width * 0.56) / tan(hfov / 2.0), (top * 0.62) / tan(deg_to_rad(20.0)))
	var k := dist / CAMERA_OFFSET.length()
	var cam := Camera3D.new()
	cam.fov = 40.0
	root3d.add_child(cam)
	# same angles as MissionView (offset and look-at drop scaled together), centred on the row
	cam.position = focus + Vector3(0.0, 0.4 * k, 0.0) + CAMERA_OFFSET * k
	cam.look_at(focus, Vector3.UP)
	cam.current = true
	for i in 10:
		await process_frame
	get_root().get_texture().get_image().save_png(out)
	print("WROTE ", out)
	quit()


func _environment(parent: Node3D) -> void:
	var env := Environment.new()
	env.background_mode = Environment.BG_COLOR
	env.background_color = Color("15191e")
	env.ambient_light_source = Environment.AMBIENT_SOURCE_COLOR
	env.ambient_light_color = Color("8090a0")
	env.ambient_light_energy = 0.55
	env.tonemap_mode = Environment.TONE_MAPPER_FILMIC
	var we := WorldEnvironment.new()
	we.environment = env
	parent.add_child(we)
	var sun := DirectionalLight3D.new()
	sun.rotation_degrees = Vector3(-52.0, -38.0, 0.0)
	sun.light_energy = 1.15
	sun.light_color = Color("dfe8f0")
	sun.shadow_enabled = true
	sun.directional_shadow_max_distance = 40.0
	parent.add_child(sun)
	var floor_mesh := MeshInstance3D.new()
	var box := BoxMesh.new()
	box.size = Vector3(60.0, 0.4, 20.0)
	floor_mesh.mesh = box
	floor_mesh.position = Vector3(10.0, -0.2, -2.0)
	var mat := StandardMaterial3D.new()
	mat.albedo_color = Color("23282e")
	floor_mesh.material_override = mat
	parent.add_child(floor_mesh)


func _load(path: String) -> Node3D:
	var doc := GLTFDocument.new()
	var state := GLTFState.new()
	var err := doc.append_from_file(path, state)
	if err != OK:
		print("CHECK FAIL ", path, " load error ", err)
		return null
	var scene := doc.generate_scene(state) as Node3D
	var names: Array[String] = []
	var surfaces := 0
	var mats := {}
	var vcol := true
	for m in scene.find_children("*", "MeshInstance3D", true, false):
		var mi := m as MeshInstance3D
		names.append(mi.name)
		for s in mi.mesh.get_surface_count():
			surfaces += 1
			var mat := mi.mesh.surface_get_material(s) as StandardMaterial3D
			if mat:
				mats[mat.resource_name] = true
				if OS.has_environment("TFJ_METAL_SCALE"):
					mat.metallic *= float(OS.get_environment("TFJ_METAL_SCALE"))
				if mi.mesh.surface_get_format(s) & Mesh.ARRAY_FORMAT_COLOR:
					mat.vertex_color_use_as_albedo = true  # Godot 4.7.2 importer bug #120625
				else:
					vcol = false
	var empties := scene.find_children("fx_*", "Node3D", true, false).size() + scene.find_children("muzzle", "", true, false).size()
	print("CHECK OK ", path.get_file(), " root=", scene.name, " meshes=", names, " surfaces=", surfaces, " materials=", mats.keys(), " colour0=", vcol, " markers=", empties)
	return scene


func _show_only(n: Node, keep: String) -> void:
	var has := n.find_children(keep, "MeshInstance3D", true, false).size() > 0
	if not has:
		return
	for m in n.find_children("mesh_*", "MeshInstance3D", true, false):
		(m as MeshInstance3D).visible = (m as MeshInstance3D).name == keep


func _aabb(n: Node3D) -> AABB:
	var box := AABB()
	var first := true
	for m in n.find_children("*", "MeshInstance3D", true, false):
		var mi := m as MeshInstance3D
		if not mi.visible:
			continue
		var t := Transform3D.IDENTITY
		var p: Node = mi
		while p != null and p != n:
			t = (p as Node3D).transform * t if p is Node3D else t
			p = p.get_parent()
		var b := t * mi.get_aabb()
		box = b if first else box.merge(b)
		first = false
	return box
