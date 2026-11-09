extends SceneTree
## Loads and instantiates every preset; checks emitters, textures and animation frame counts.
const PRESETS := "res://generated_assets/vfx/godot/presets/"

func _init() -> void:
	var ok := 0
	var files := DirAccess.get_files_at(PRESETS)
	for f in files:
		if not f.ends_with(".tscn"):
			continue
		var ps: PackedScene = load(PRESETS + f)
		if ps == null:
			print("LOAD FAIL ", f)
			continue
		var n: Node = ps.instantiate()
		var em := 0
		var bad := 0
		for c in n.get_children():
			if c is CPUParticles3D:
				em += 1
				var m := (c as CPUParticles3D).material_override as StandardMaterial3D
				if m == null or m.albedo_texture == null:
					bad += 1
				else:
					var t := m.albedo_texture
					if t.get_width() % m.particles_anim_h_frames != 0 or t.get_height() % m.particles_anim_v_frames != 0:
						bad += 1
		print("LOAD ", f, " emitters=", em, " problems=", bad)
		if bad == 0 and em > 0:
			ok += 1
		n.free()
	print("LOAD summary ", ok, "/", files.size(), " ok")
	quit()
