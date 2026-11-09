extends SceneTree
## Loads every file listed in generated_assets/asset_manifest.json through Godot's resource
## loader (after `--import`) and reports what Godot actually made of it. Run headless:
##   godot --headless --path <project copy> --script res://generated_assets/tools/godot/load_check.gd -- --report=<abs path>
## Exit code 0 = every loadable entry loaded; 1 = at least one failure.

const MANIFEST := "res://generated_assets/asset_manifest.json"
const LOADABLE := ["glb", "gltf", "png", "webp", "jpg", "jpeg", "svg", "ogg", "wav", "mp3", "ttf", "otf", "woff2", "woff", "ogv"]


func _initialize() -> void:
	var report_path := ""
	for arg in OS.get_cmdline_user_args():
		if arg.begins_with("--report="):
			report_path = arg.trim_prefix("--report=")
	var text := FileAccess.get_file_as_string(MANIFEST)
	var data: Variant = JSON.parse_string(text)
	if typeof(data) != TYPE_DICTIONARY:
		printerr("LOADCHECK FAIL: cannot parse ", MANIFEST)
		quit(1)
		return
	var results := []
	var failures := 0
	var counts := {}
	for entry: Dictionary in data.get("entries", []):
		var path: String = entry.get("path", "")
		var ext := path.get_extension().to_lower()
		if path == "" or not LOADABLE.has(ext):
			continue
		var res_path := "res://" + path
		var r := {"id": entry.get("id", ""), "path": path, "ok": false}
		var t0 := Time.get_ticks_usec()
		var resource: Resource = ResourceLoader.load(res_path)
		r["load_ms"] = (Time.get_ticks_usec() - t0) / 1000.0
		if resource == null:
			r["error"] = "ResourceLoader.load returned null"
		else:
			r["type"] = resource.get_class()
			_describe(resource, r)
		results.append(r)
		var key: String = r.get("type", "FAILED")
		counts[key] = int(counts.get(key, 0)) + 1
		if not r["ok"]:
			failures += 1
			printerr("LOADCHECK FAIL: %s %s: %s" % [r["id"], path, r.get("error", "?")])
	print("LOADCHECK loaded %d entries, %d failed, by type %s" % [results.size(), failures, JSON.stringify(counts)])
	if report_path != "":
		var f := FileAccess.open(report_path, FileAccess.WRITE)
		f.store_string(JSON.stringify({"engine": Engine.get_version_info().string, "failures": failures, "counts": counts, "results": results}, "\t"))
		f.close()
	quit(1 if failures > 0 else 0)


func _describe(resource: Resource, r: Dictionary) -> void:
	if resource is PackedScene:
		var node: Node = (resource as PackedScene).instantiate()
		if node == null:
			r["error"] = "PackedScene.instantiate failed"
			return
		var meshes := 0
		var surfaces := 0
		var tris := 0
		var materials := {}
		var aabb := AABB()
		var first := true
		var stack: Array[Node] = [node]
		var players := []
		while not stack.is_empty():
			var n: Node = stack.pop_back()
			for c in n.get_children():
				stack.append(c)
			if n is AnimationPlayer:
				players.append_array((n as AnimationPlayer).get_animation_list())
			if n is MeshInstance3D and (n as MeshInstance3D).mesh != null:
				var mi := n as MeshInstance3D
				meshes += 1
				var mesh := mi.mesh
				for s in mesh.get_surface_count():
					surfaces += 1
					var arrays := mesh.surface_get_arrays(s)
					var idx: Variant = arrays[Mesh.ARRAY_INDEX]
					if idx != null and (idx as PackedInt32Array).size() > 0:
						tris += (idx as PackedInt32Array).size() / 3
					else:
						tris += (arrays[Mesh.ARRAY_VERTEX] as PackedVector3Array).size() / 3
					var mat := mesh.surface_get_material(s)
					if mat != null:
						materials[mat.resource_name if mat.resource_name != "" else mat.get_class()] = true
				var local := _global_xform(mi, node) * mesh.get_aabb()
				aabb = local if first else aabb.merge(local)
				first = false
		r["root"] = node.name
		r["mesh_instances"] = meshes
		r["surfaces"] = surfaces
		r["tris"] = tris
		r["materials"] = materials.keys()
		r["animations"] = players
		r["aabb_position"] = [snappedf(aabb.position.x, 0.001), snappedf(aabb.position.y, 0.001), snappedf(aabb.position.z, 0.001)]
		r["aabb_size"] = [snappedf(aabb.size.x, 0.001), snappedf(aabb.size.y, 0.001), snappedf(aabb.size.z, 0.001)]
		node.free()
		if meshes == 0:
			r["error"] = "scene has no MeshInstance3D"
			return
		r["ok"] = true
	elif resource is Texture2D:
		var tex := resource as Texture2D
		r["size"] = [tex.get_width(), tex.get_height()]
		r["ok"] = tex.get_width() > 0
		if not r["ok"]:
			r["error"] = "zero-size texture"
	elif resource is AudioStream:
		var stream := resource as AudioStream
		r["length_s"] = snappedf(stream.get_length(), 0.001)
		if "loop" in stream:
			r["loop"] = stream.get("loop")
		r["ok"] = stream.get_length() > 0.0
		if not r["ok"]:
			r["error"] = "zero-length audio stream"
	elif resource is Font:
		var font := resource as Font
		r["font_name"] = font.get_font_name()
		r["ok"] = font.get_font_name() != "" or font.get_height(16) > 0
	elif resource is VideoStream:
		r["ok"] = true
	else:
		r["ok"] = true


static func _global_xform(n: Node, root: Node) -> Transform3D:
	var xf := Transform3D.IDENTITY
	var cur := n
	while cur != null and cur != root:
		if cur is Node3D:
			xf = (cur as Node3D).transform * xf
		cur = cur.get_parent()
	if root is Node3D:
		xf = (root as Node3D).transform * xf
	return xf
