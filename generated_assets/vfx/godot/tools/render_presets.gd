extends SceneTree
## Renders every preset under the MissionView camera, environment and light to PNG frames.
## xvfb-run -a -s "-screen 0 1280x720x24" godot --path <project> --rendering-driver opengl3 --resolution 1280x720 --fixed-fps 30 \
##   --script res://generated_assets/vfx/godot/tools/render_presets.gd -- --out=/tmp/tfj-vfx-render

const PRESETS := "res://generated_assets/vfx/godot/presets/"
const FRAMES := 36

var out_dir := "/tmp/tfj-vfx-render"
var list: Array[String] = []
var idx := -1
var frame := 0
var current: Node3D
var world: Node3D


func _initialize() -> void:
	for a in OS.get_cmdline_user_args():
		if a.begins_with("--out="):
			out_dir = a.substr(6)
	DirAccess.make_dir_recursive_absolute(out_dir)
	for f in DirAccess.get_files_at(PRESETS):
		if f.ends_with(".tscn"):
			list.append(f)
	list.sort()
	world = Node3D.new()
	root.add_child(world)
	var env := Environment.new()
	env.background_mode = Environment.BG_COLOR
	env.background_color = Color("15191e")
	env.ambient_light_source = Environment.AMBIENT_SOURCE_COLOR
	env.ambient_light_color = Color("8090a0")
	env.ambient_light_energy = 0.55
	env.tonemap_mode = Environment.TONE_MAPPER_FILMIC
	var we := WorldEnvironment.new()
	we.environment = env
	world.add_child(we)
	var sun := DirectionalLight3D.new()
	sun.rotation_degrees = Vector3(-52.0, -38.0, 0.0)
	sun.light_energy = 1.15
	sun.light_color = Color("dfe8f0")
	world.add_child(sun)
	_box(Vector3(40, 0.4, 14), Color("23282e"), Vector3(0, -0.2, -2))
	_box(Vector3(40, 9, 0.4), Color("1b2026"), Vector3(0, 4.5, -6))
	_box(Vector3(1.6, 3.2, 1.0), Color("20262c"), Vector3(-3.2, 1.6, -5))
	_box(Vector3(2.4, 5.0, 1.0), Color("20262c"), Vector3(3.4, 2.5, -5))
	var cam := Camera3D.new()
	cam.fov = 40.0
	var focus := Vector3(0, 1.6, 0)
	world.add_child(cam)
	cam.look_at_from_position(focus + Vector3(-2.2, 2.3, 10.5), focus + Vector3(0, -0.4, 0), Vector3.UP)
	cam.current = true
	print("RENDER presets: ", list.size())
	print("RENDER adapter: ", RenderingServer.get_video_adapter_name(), " | ", RenderingServer.get_video_adapter_api_version())


func _box(size: Vector3, c: Color, at: Vector3) -> void:
	var m := MeshInstance3D.new()
	var b := BoxMesh.new()
	b.size = size
	m.mesh = b
	var mat := StandardMaterial3D.new()
	mat.albedo_color = c
	mat.roughness = 0.9
	m.material_override = mat
	m.position = at
	world.add_child(m)


func _start(i: int) -> void:
	if current:
		current.queue_free()
	var ps: PackedScene = load(PRESETS + list[i])
	if ps == null:
		print("RENDER ERROR cannot load ", list[i])
		return
	current = ps.instantiate()
	var ground := list[i].contains("collapse") or list[i].contains("burning")
	current.position = Vector3(0, 0.0 if ground else 1.3, 0)
	world.add_child(current)
	var n := 0
	for c in current.get_children():
		if c is CPUParticles3D:
			(c as CPUParticles3D).restart()
			(c as CPUParticles3D).emitting = true
			n += 1
	print("RENDER start ", list[i], " emitters=", n)


func _process(_delta: float) -> bool:
	if idx >= 0 and frame >= 2:
		var img := root.get_texture().get_image()
		img.save_png("%s/%s_%02d.png" % [out_dir, list[idx].get_basename(), frame - 2])
	if idx < 0 or frame >= FRAMES + 2:
		idx += 1
		frame = 0
		if idx >= list.size():
			print("RENDER done")
			return true
		_start(idx)
	frame += 1
	return false
