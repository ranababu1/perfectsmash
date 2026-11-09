extends SceneTree
## Renders review previews of manifest assets under the game's own camera and light
## (constants copied from scripts/mission/view/mission_view.gd, which stays untouched).
## Needs a real GL context, so run under Xvfb (software llvmpipe is fine), not --headless:
##   xvfb-run -a -s "-screen 0 1280x720x24" godot --path <project copy> --rendering-driver opengl3 \
##     --resolution 1280x720 --script res://generated_assets/tools/godot/render_previews.gd -- --out=<abs dir>
## Outputs PNGs: mission_<chapter>.png (helix_01 layout with that chapter's kit swapped in, greybox
## boxes where a kind has no mesh yet), kit_<chapter>.png (every destructible mesh of the chapter in a
## row), states_<chapter>.png (intact / light / heavy / debris strip where overlays exist), and
## props_<chapter>.png (environment, character and weapon meshes), materials_<chapter>.png (chapter
## texture sets on 1 m cubes with damage overlays). Greybox fallbacks use the chapter texture set for
## the component's physics material, and the floor uses <CH>-MAT-FLOOR-A, when those sets exist.

const MANIFEST := "res://generated_assets/asset_manifest.json"
const MISSION := "res://data/missions/helix_01.json"
const PX := 100.0
# MissionView constants (code).
const CAMERA_FOV := 40.0
const CAMERA_OFFSET := Vector3(-2.2, 2.3, 10.5)
const STATIC_DEPTH := 1.6
const KINDS := {
	"server_rack": [0.8, Color("39424c"), Color("2f8fa3"), 0.25],
	"support_column": [0.5, Color("6b737c"), null, 0.0],
	"service_deck": [1.4, Color("5a6068"), null, 0.0],
	"ai_core": [0.7, Color("d9dde2"), Color("ff3b4e"), 1.2],
	"core_shield": [0.9, Color("80878f"), null, 0.0],
	"power_cell": [0.5, Color("4a4238"), Color("ffae42"), 0.7],
	"blast_wall": [1.2, Color("717880"), null, 0.0],
	"relay_mast": [0.3, Color("5d656e"), null, 0.0],
	"relay_dish": [0.8, Color("8fb6c4"), null, 0.0],
}
## helix_01 structural roles -> the chapter kind that plays that role (ASSET_CONTRACT 5).
const ROLE_MAP := {
	"helix": {},
	"vita": {"blast_wall": "containment_cap", "server_rack": "specimen_rack", "support_column": "lab_column", "service_deck": "lab_deck", "core_shield": "cleanroom_panel", "ai_core": "gene_vault_core", "power_cell": "cryo_cell", "relay_mast": "lab_column", "relay_dish": "bioreactor"},
	"nova_grid": {"blast_wall": "containment_wall", "server_rack": "transformer", "support_column": "grid_pylon", "service_deck": "cable_bridge", "core_shield": "containment_ring_segment", "ai_core": "reactor_core", "power_cell": "capacitor_cell", "relay_mast": "grid_pylon", "relay_dish": "cooling_tower_segment"},
	"civitas": {"blast_wall": "security_wall", "server_rack": "data_exchange_rack", "support_column": "civic_column", "service_deck": "relay_bridge", "core_shield": "civic_screen", "ai_core": "surveillance_core", "power_cell": "data_exchange_rack", "relay_mast": "sensor_mast", "relay_dish": "sensor_array"},
	"meridian": {"blast_wall": "monolith_slab", "server_rack": "quantum_stabilizer", "support_column": "anchor_column", "service_deck": "convergence_deck", "core_shield": "phase_shield", "ai_core": "convergence_core", "power_cell": "temporal_cell", "relay_mast": "timeline_relay", "relay_dish": "phase_shield"},
}
const CHAPTERS := ["helix", "vita", "nova_grid", "civitas", "meridian"]
const CODES := {"helix": "HLX", "vita": "VTA", "nova_grid": "NVG", "civitas": "CVT", "meridian": "MRD", "shared": "SHR"}
const PHYSICS_MATERIALS := ["lightweight_alloy", "reinforced_steel", "composite", "glass_polymer", "concrete", "electronic_module", "ai_core_module", "energy_component"]
## Materials without their own overlay borrow a related one (ASSET_CONTRACT 7).
const MATERIAL_FALLBACK := {"ai_core_module": "electronic_module"}

var out_dir := "/tmp/tfj-previews"
var only := ""
var entries: Array = []
var stage: Node3D
var log_lines: Array[String] = []
var material_cache := {}
## When true, _new_stage adds the proposed reflection source (ASSET_CONTRACT 9): a dark procedural
## sky used only for reflected light, background and ambient unchanged. Off = the game as it is.
var proposed_env := false


func _initialize() -> void:
	for arg in OS.get_cmdline_user_args():
		if arg.begins_with("--out="):
			out_dir = arg.trim_prefix("--out=")
		elif arg.begins_with("--only="):
			only = arg.trim_prefix("--only=")
	DirAccess.make_dir_recursive_absolute(out_dir)
	var data: Variant = JSON.parse_string(FileAccess.get_file_as_string(MANIFEST))
	entries = (data as Dictionary).get("entries", [])
	_run.call_deferred()


func _run() -> void:
	var mission: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(MISSION))
	for chapter: String in CHAPTERS:
		if only != "" and not only.contains(chapter):
			continue
		await _render_mission(chapter, mission)
		var kit := _meshes_for(chapter, "destructibles")
		if not kit.is_empty():
			await _render_row("kit_" + chapter, chapter, kit)
		var props := _meshes_for(chapter, "environments") + _meshes_for(chapter, "characters") + _meshes_for(chapter, "weapons")
		if chapter == "helix":
			props += _meshes_for("shared", "characters") + _meshes_for("shared", "weapons") + _meshes_for("", "characters") + _meshes_for("", "weapons")
		if not props.is_empty():
			await _render_row("props_" + chapter, chapter, props)
		await _render_states(chapter, kit)
		await _render_materials(chapter)
		proposed_env = true
		await _render_materials(chapter)
		await _render_mission(chapter, mission, "_proposed_env")
		proposed_env = false
	var f := FileAccess.open(out_dir.path_join("render_log.txt"), FileAccess.WRITE)
	f.store_string("\n".join(log_lines) + "\n")
	f.close()
	print("PREVIEWS done: ", out_dir)
	quit()


# ------------------------------------------------------------------ manifest lookups

func _meshes_for(chapter: String, category: String) -> Array:
	var out := []
	for e: Dictionary in entries:
		var p: String = e.get("path", "")
		if not (p.ends_with(".glb") or p.ends_with(".gltf")):
			continue
		if e.get("category", "") != category:
			continue
		if str(e.get("chapter", "")) != chapter:
			continue
		if String(e.get("id", "")).contains("-DEB-"):
			continue
		out.append(e)
	return out


## The variant of `kind` whose reference size needs the least stretching to fit `size_px`.
func _kind_entry(chapter: String, kind: String, size_px: Vector2 = Vector2.ZERO) -> Variant:
	var best: Variant = null
	var best_cost := INF
	for e: Dictionary in entries:
		if e.get("component_kind", "") == kind and str(e.get("chapter", "")) == chapter and e.get("category", "") == "destructibles" and String(e.get("path", "")).ends_with(".glb") and not String(e.get("id", "")).contains("-DEB-"):
			var cost := 0.0
			var ref: Variant = e.get("reference_size_px")
			if size_px != Vector2.ZERO and ref is Array and (ref as Array).size() == 2:
				cost = absf(log(size_px.x / float(ref[0]))) + absf(log(size_px.y / float(ref[1])))
			if cost < best_cost:
				best_cost = cost
				best = e
	return best


func _debris_entry(chapter: String, kind: String) -> Variant:
	for e: Dictionary in entries:
		if e.get("component_kind", "") == kind and str(e.get("chapter", "")) == chapter and String(e.get("id", "")).contains("-DEB-"):
			return e
	return null


func _overlay(material_id: String, state: String) -> Texture2D:
	for m: String in [material_id, str(MATERIAL_FALLBACK.get(material_id, ""))]:
		if m == "":
			continue
		var want := "-DMG-%s-%s" % [m.to_upper(), state.to_upper()]
		for e: Dictionary in entries:
			if String(e.get("id", "")).contains(want) and String(e.get("path", "")).get_extension() in ["png", "webp"]:
				return load("res://" + e["path"])
	return null


func _entry_by_id(id: String) -> Variant:
	for e: Dictionary in entries:
		if e.get("id", "") == id:
			return e
	return null


## Chapter texture set `<CH>-MAT-<NAME>-A` (ASSET_CONTRACT 7) as the proposed StandardMaterial3D:
## albedo sRGB, OpenGL normal, ORM packed (R occlusion, G roughness, B metallic), optional emission,
## object-space triplanar at the tile size stated in the entry purpose ("<n> m per tile", default 1 m).
## Returns null when the set is not in the manifest.
func _material_set(chapter: String, name: String) -> Variant:
	var id := "%s-MAT-%s-A" % [CODES.get(chapter, "SHR"), name.to_upper()]
	if material_cache.has(id):
		return material_cache[id]
	var base: Variant = _entry_by_id(id)
	var mat: Variant = null
	if base != null:
		var m := StandardMaterial3D.new()
		m.resource_name = id
		m.albedo_texture = load("res://" + String(base["path"]))
		var tile := 1.0
		var rx := RegEx.create_from_string("([0-9.]+) m per tile")
		var hit := rx.search(String(base.get("purpose", "")))
		if hit != null:
			tile = maxf(0.1, hit.get_string(1).to_float())
		m.uv1_triplanar = true
		m.uv1_world_triplanar = false
		m.uv1_scale = Vector3.ONE / tile
		var nrm: Variant = _entry_by_id(id + "-NORMAL")
		if nrm != null:
			m.normal_enabled = true
			m.normal_texture = load("res://" + String(nrm["path"]))
		var orm: Variant = _entry_by_id(id + "-ORM")
		if orm != null:
			var t: Texture2D = load("res://" + String(orm["path"]))
			m.ao_enabled = true
			m.ao_texture = t
			m.ao_texture_channel = BaseMaterial3D.TEXTURE_CHANNEL_RED
			m.roughness = 1.0
			m.roughness_texture = t
			m.roughness_texture_channel = BaseMaterial3D.TEXTURE_CHANNEL_GREEN
			m.metallic = 1.0
			m.metallic_texture = t
			m.metallic_texture_channel = BaseMaterial3D.TEXTURE_CHANNEL_BLUE
		var emi: Variant = _entry_by_id(id + "-EMISSION")
		if emi != null:
			m.emission_enabled = true
			m.emission_texture = load("res://" + String(emi["path"]))
			# Godot's default emission operator is ADD (colour + texture), which turns the whole
			# surface white with a white colour; MULTIPLY makes the map the emission mask.
			m.emission_operator = BaseMaterial3D.EMISSION_OP_MULTIPLY
			m.emission = Color.WHITE
			m.emission_energy_multiplier = 1.0
		if name == "glass_polymer":
			m.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
		mat = m
	material_cache[id] = mat
	return mat


# ------------------------------------------------------------------ scene building

func _new_stage(chapter: String, width_m: float, focus_x: float, cam_scale: float = 1.0, seed_id: String = "") -> void:
	if stage != null:
		stage.queue_free()
		await process_frame
	stage = Node3D.new()
	root.add_child(stage)
	var env := Environment.new()
	env.background_mode = Environment.BG_COLOR
	env.background_color = Color("15191e")
	env.ambient_light_source = Environment.AMBIENT_SOURCE_COLOR
	env.ambient_light_color = Color("8090a0")
	env.ambient_light_energy = 0.55
	env.tonemap_mode = Environment.TONE_MAPPER_FILMIC
	if proposed_env:
		var sky_mat := ProceduralSkyMaterial.new()
		sky_mat.sky_top_color = Color("4a5866")
		sky_mat.sky_horizon_color = Color("8090a0")
		sky_mat.ground_horizon_color = Color("3a4048")
		sky_mat.ground_bottom_color = Color("1b2026")
		var sky := Sky.new()
		sky.sky_material = sky_mat
		env.sky = sky
		env.reflected_light_source = Environment.REFLECTION_SOURCE_SKY
	var we := WorldEnvironment.new()
	we.environment = env
	stage.add_child(we)
	var sun := DirectionalLight3D.new()
	sun.rotation_degrees = Vector3(-52.0, -38.0, 0.0)
	sun.light_energy = 1.15
	sun.light_color = Color("dfe8f0")
	sun.shadow_enabled = true
	sun.directional_shadow_max_distance = 40.0 * cam_scale
	stage.add_child(sun)
	var floor_mat: Variant = _material_set(chapter, "floor")
	_box(Vector3(width_m + 30.0, 0.4, 14.0), floor_mat if floor_mat != null else _flat(Color("23282e")), Vector3(width_m / 2.0, -0.2, -2.0))
	_box(Vector3(width_m + 30.0, 9.0, 0.4), _flat(Color("1b2026")), Vector3(width_m / 2.0, 4.5, -6.0))
	if seed_id != "":
		# Same seeded distant blocks as MissionView._build_environment.
		var rng := RandomNumberGenerator.new()
		rng.seed = hash(seed_id)
		for i in 9:
			var w := rng.randf_range(1.2, 3.0)
			var h := rng.randf_range(2.0, 6.5)
			_box(Vector3(w, h, 1.0), _flat(Color("20262c")), Vector3(rng.randf_range(-2.0, width_m + 2.0), h / 2.0, -5.0))
	var cam := Camera3D.new()
	cam.fov = CAMERA_FOV
	var focus := Vector3(focus_x, 1.6 * cam_scale, 0.0)
	cam.position = focus + CAMERA_OFFSET * cam_scale
	stage.add_child(cam)
	cam.look_at(focus + Vector3(0.0, -0.4 * cam_scale, 0.0), Vector3.UP)
	cam.current = true


func _box(size: Vector3, material: Material, at: Vector3, rot_z: float = 0.0) -> MeshInstance3D:
	var mi := MeshInstance3D.new()
	var b := BoxMesh.new()
	b.size = size
	mi.mesh = b
	mi.material_override = material
	mi.position = at
	mi.rotation = Vector3(0, 0, rot_z)
	stage.add_child(mi)
	return mi


static func _flat(color: Color) -> StandardMaterial3D:
	var m := StandardMaterial3D.new()
	m.albedo_color = color
	m.roughness = 0.75
	m.metallic = 0.25
	return m


func _instance(entry: Dictionary) -> Node3D:
	var res: Resource = load("res://" + String(entry["path"]))
	if not (res is PackedScene):
		log_lines.append("LOAD FAIL %s" % entry["path"])
		return null
	var n := (res as PackedScene).instantiate() as Node3D
	_show_damage_geometry(n, 0)
	return n


func _has_state_geometry(entry: Dictionary) -> bool:
	var n := _instance(entry)
	if n == null:
		return false
	var has := n.find_child("mesh_light", true, false) != null or n.find_child("mesh_heavy", true, false) != null
	n.free()
	return has


## glTF carries no visibility, so every state mesh imports visible. The proposed loader hook
## (ASSET_CONTRACT 8) shows exactly one of mesh_intact / mesh_light / mesh_heavy:
## state 0 intact, 1 light (else intact), 2 heavy (else light, else intact).
func _show_damage_geometry(n: Node, state: int) -> void:
	var nodes := {}
	for name in ["mesh_intact", "mesh_light", "mesh_heavy"]:
		var found := n.find_child(name, true, false)
		if found is Node3D:
			nodes[name] = found
	if nodes.is_empty():
		return
	var order: Array = [["mesh_intact"], ["mesh_light", "mesh_intact"], ["mesh_heavy", "mesh_light", "mesh_intact"]][state]
	var pick := ""
	for name: String in order:
		if nodes.has(name):
			pick = name
			break
	for name: String in nodes:
		(nodes[name] as Node3D).visible = name == pick or pick == ""


func _aabb(node: Node) -> AABB:
	var out := AABB()
	var first := true
	var stack: Array = [[node, Transform3D.IDENTITY]]
	while not stack.is_empty():
		var item: Array = stack.pop_back()
		var n: Node = item[0]
		var xf: Transform3D = item[1]
		if n is Node3D and not (n as Node3D).visible:
			continue
		if n is Node3D and n != node:
			xf = xf * (n as Node3D).transform
		if n is MeshInstance3D and (n as MeshInstance3D).mesh != null:
			var bb: AABB = xf * (n as MeshInstance3D).mesh.get_aabb()
			out = bb if first else out.merge(bb)
			first = false
		for c in n.get_children():
			stack.append([c, xf])
	return out


func _place_component(chapter: String, c: Dictionary, ground_y: float) -> void:
	var kind: String = c["kind"]
	var mapped: String = (ROLE_MAP[chapter] as Dictionary).get(kind, kind)
	var size := Vector2(float(c["w"]), float(c["h"]))
	var at := Vector3(float(c["x"]) / PX, (ground_y - float(c["y"])) / PX, 0.0)
	var entry: Variant = _kind_entry(chapter, mapped, size)
	if entry != null:
		var node := _instance(entry)
		if node != null:
			var ref: Variant = (entry as Dictionary).get("reference_size_px")
			if ref is Array and (ref as Array).size() == 2:
				node.scale = Vector3(size.x / float(ref[0]), size.y / float(ref[1]), 1.0)
			node.position = at
			stage.add_child(node)
			log_lines.append("%s %s -> %s (%s) scale %s" % [chapter, c["id"], mapped, (entry as Dictionary)["id"], node.scale])
			return
	var look: Array = KINDS.get(kind, [0.8, Color("5a6068"), null, 0.0])
	var m: StandardMaterial3D = _flat(look[1])
	var set_name := str(c.get("material", ""))
	# Code rule: the critical target keeps a white housing with red emission in every chapter,
	# so the ai_core greybox stays flat; other kinds use the chapter texture set (ASSET_CONTRACT 7).
	var textured: Variant = _material_set(chapter, set_name) if set_name != "" and kind != "ai_core" else null
	if textured != null:
		m = (textured as StandardMaterial3D).duplicate()
	if look[2] != null and not m.emission_enabled:
		m.emission_enabled = true
		m.emission = look[2]
		m.emission_energy_multiplier = look[3]
	_box(Vector3(size.x / PX, size.y / PX, look[0]), m, at)
	log_lines.append("%s %s -> %s greybox%s (no mesh yet)" % [chapter, c["id"], mapped, (" textured " + (textured as Material).resource_name) if textured != null else ""])


func _render_mission(chapter: String, mission: Dictionary, suffix: String = "") -> void:
	var ground_y := float(mission["ground_y"])
	var left := INF
	var right := -INF
	for c: Dictionary in mission["components"]:
		left = minf(left, float(c["x"]) - float(c["w"]) / 2.0)
		right = maxf(right, float(c["x"]) + float(c["w"]) / 2.0)
	var op: Array = mission["operative"]
	left = minf(left, float(op[0]))
	await _new_stage(chapter, float(mission["width"]) / PX, (left + right) / 2.0 / PX, 1.0, String(mission["id"]))
	for s: Dictionary in mission["statics"]:
		_box(Vector3(float(s["w"]) / PX, float(s["h"]) / PX, STATIC_DEPTH), _flat(Color("4b5158")), Vector3(float(s["x"]) / PX, (ground_y - float(s["y"])) / PX, 0.0))
	for c: Dictionary in mission["components"]:
		_place_component(chapter, c, ground_y)
		if c.get("critical_asset", false):
			# MissionView's floating red target marker, 0.75 m above the critical asset.
			var marker := MeshInstance3D.new()
			var prism := PrismMesh.new()
			prism.size = Vector3(0.28, 0.3, 0.28)
			marker.mesh = prism
			marker.rotation = Vector3(PI, 0.0, 0.0)
			var mm := StandardMaterial3D.new()
			mm.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
			mm.albedo_color = Color("ff3b4e")
			marker.material_override = mm
			marker.position = Vector3(float(c["x"]) / PX, (ground_y - float(c["y"])) / PX + float(c["h"]) / PX / 2.0 + 0.75, 0.0)
			stage.add_child(marker)
	var operative: Node3D = null
	for e: Dictionary in entries:
		if e.get("category", "") == "characters" and String(e.get("path", "")).ends_with(".glb") and String(e.get("id", "")).contains("-CHR-OPERATIVE"):
			operative = _instance(e)
			break
	if operative == null:
		operative = (load("res://scripts/mission/view/operative_rig.gd") as GDScript).new()
	operative.position = Vector3(float(op[0]) / PX, (ground_y - float(op[1])) / PX, 0.3)
	stage.add_child(operative)
	await _shot("mission_" + chapter + suffix)


func _render_row(shot_name: String, chapter: String, list: Array) -> void:
	var nodes := []
	var x := 0.0
	var gap := 0.45
	var max_h := 0.0
	for e: Dictionary in list:
		var n := _instance(e)
		if n == null:
			continue
		var bb := _aabb(n)
		nodes.append([n, bb])
		x += bb.size.x + gap
		max_h = maxf(max_h, bb.size.y)
	if nodes.is_empty():
		return
	var total := x - gap
	var cam_scale := maxf(1.0, maxf(total * 1.12 / 13.9, max_h * 1.25 / 4.6))
	await _new_stage(chapter, total, total / 2.0, cam_scale)
	x = 0.0
	for pair: Array in nodes:
		var n: Node3D = pair[0]
		var bb: AABB = pair[1]
		n.position = Vector3(x - bb.position.x, -bb.position.y, -(bb.position.z + bb.size.z / 2.0))
		stage.add_child(n)
		x += bb.size.x + gap
	await _shot(shot_name)


## materials_<chapter>.png: one 1 m cube per chapter texture set (physics materials, then floor),
## each with its light and heavy damage overlay beside it when the shared overlays exist.
func _render_materials(chapter: String) -> void:
	var names: Array = PHYSICS_MATERIALS + ["floor"]
	var cells := []
	for name: String in names:
		var m: Variant = _material_set(chapter, name)
		if m == null:
			continue
		cells.append([m, null])
		if name != "floor":
			for state in ["light", "heavy"]:
				var ov := _overlay(name, state)
				if ov != null:
					cells.append([m, ov])
	if cells.is_empty():
		return
	var gap := 0.25
	var width := cells.size() * (1.0 + gap)
	await _new_stage(chapter, width, width / 2.0, maxf(1.0, width * 1.12 / 13.9))
	var x := 0.5
	for cell: Array in cells:
		var mat := (cell[0] as StandardMaterial3D).duplicate() as StandardMaterial3D
		if cell[1] != null:
			var pass_mat := StandardMaterial3D.new()
			pass_mat.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
			pass_mat.albedo_texture = cell[1]
			pass_mat.uv1_triplanar = true
			pass_mat.uv1_world_triplanar = false
			pass_mat.roughness = 0.9
			mat.next_pass = pass_mat
		_box(Vector3(1.0, 1.0, 1.0), mat, Vector3(x, 0.5, 0.0))
		x += 1.0 + gap
	log_lines.append("%s materials: %d cells%s" % [chapter, cells.size(), " (proposed env)" if proposed_env else ""])
	await _shot("materials_" + chapter + ("_proposed_env" if proposed_env else ""))


func _render_states(chapter: String, kit: Array) -> void:
	var rows := []
	for e: Dictionary in kit:
		var mat := str(e.get("material", ""))
		var light: Variant = _overlay(mat, "light") if mat != "" else null
		var heavy: Variant = _overlay(mat, "heavy") if mat != "" else null
		var deb: Variant = _debris_entry(chapter, str(e.get("component_kind", "")))
		if light == null and heavy == null and deb == null and not _has_state_geometry(e):
			continue
		rows.append([e, light, heavy, deb])
		if rows.size() >= 3:
			break
	if rows.is_empty():
		return
	var cells := []
	var width := 0.0
	for r: Array in rows:
		var e: Dictionary = r[0]
		for state in 4:
			var n: Node3D = null
			if state == 3:
				if r[3] != null:
					n = _instance(r[3])
			else:
				n = _instance(e)
				if n != null and state > 0:
					_show_damage_geometry(n, state)
					_apply_state(n, r[state] as Texture2D)
			if n == null:
				continue
			var bb := _aabb(n)
			cells.append([n, bb])
			width += bb.size.x + 0.35
		width += 0.6
	await _new_stage(chapter, width, width / 2.0, maxf(1.0, width * 1.12 / 13.9))
	var x := 0.0
	for pair: Array in cells:
		var n: Node3D = pair[0]
		var bb: AABB = pair[1]
		n.position = Vector3(x - bb.position.x, -bb.position.y, -(bb.position.z + bb.size.z / 2.0))
		stage.add_child(n)
		x += bb.size.x + 0.35
	await _shot("states_" + chapter)


## The proposed damage hook from ASSET_CONTRACT 8: overlay as next_pass with object-space triplanar,
## and mesh_light / mesh_heavy geometry swapped in by _show_damage_geometry.
func _apply_state(n: Node, overlay: Texture2D) -> void:
	var stack: Array[Node] = [n]
	while not stack.is_empty():
		var cur: Node = stack.pop_back()
		for c in cur.get_children():
			stack.append(c)
		if cur is MeshInstance3D and overlay != null:
			var mi := cur as MeshInstance3D
			for s in mi.mesh.get_surface_count():
				var base: Material = mi.get_active_material(s)
				if base == null:
					continue
				var m: Material = base.duplicate()
				var pass_mat := StandardMaterial3D.new()
				pass_mat.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
				pass_mat.albedo_texture = overlay
				pass_mat.uv1_triplanar = true
				pass_mat.uv1_world_triplanar = false
				pass_mat.roughness = 0.9
				m.next_pass = pass_mat
				mi.set_surface_override_material(s, m)


func _shot(shot_name: String) -> void:
	for i in 6:
		await process_frame
	await RenderingServer.frame_post_draw
	var path := out_dir.path_join(shot_name + ".png")
	var err := root.get_texture().get_image().save_png(path)
	log_lines.append("%s %s" % ["saved" if err == OK else "SAVE FAIL", path])
	print("PREVIEW ", path)
