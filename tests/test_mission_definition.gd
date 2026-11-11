extends TestCase

const HELIX := "res://data/missions/helix_08.json"

var _materials := MaterialCatalog.load_from_file()
var _weapons := WeaponCatalog.load_from_file()


func _mission(overrides: Dictionary = {}) -> Dictionary:
	var m := {
		"id": "m", "name": "M", "chapter": 1, "width": 1600, "ground_y": 640, "operative": [100, 640],
		"recommended_shots": 4, "target_time": 60,
		"weapons": {"kinetic_accelerator": {"ammunition": 10}},
		"statics": [],
		"components": [
			{"id": "base", "kind": "support_column", "material": "concrete", "x": 800, "y": 560, "w": 40, "h": 160},
			{"id": "core", "kind": "ai_core", "material": "electronic_module", "x": 800, "y": 450, "w": 50, "h": 50, "critical_asset": true, "supports": ["base"]},
		],
		"objectives": [{"id": "o", "type": "destroy_critical", "mandatory": true, "label": "L", "targets": ["core"]}],
	}
	m.merge(overrides, true)
	return m


func _parse(data: Dictionary) -> MissionDefinition:
	return MissionDefinition.from_json_text(JSON.stringify(data), _materials, _weapons)


func test_helix_mission_is_valid() -> void:
	var def := MissionDefinition.load_from_file(HELIX, _materials, _weapons)
	assert_true(def.is_valid(), ", ".join(def.errors))
	assert_eq(def.critical_asset_ids(), ["aura_core"] as Array[String])
	assert_eq(def.weapon_order, ["kinetic_accelerator", "breach_charge"] as Array[String])
	assert_eq(def.weapon_ammunition.breach_charge, 3)
	assert_true(def.recommended_shots > 5 or def.weapon_ammunition.kinetic_accelerator > 5, "no legacy five-shot ceiling")
	assert_eq(def.component("deck").supports, ["pillar_l", "pillar_r"] as Array[String])
	var structure := StructuralDependencySystem.from_entries(def.structure_entries())
	assert_true(structure.is_valid())
	assert_eq(structure.fail("pillar_l"), ["deck", "core_shield", "aura_core", "power_cell"] as Array[String])


func test_minimal_mission_is_valid() -> void:
	var def := _parse(_mission())
	assert_true(def.is_valid(), ", ".join(def.errors))


func test_rejects_unknown_references() -> void:
	var def := _parse(_mission({
		"weapons": {"plasma_rifle": {"ammunition": 5}, "kinetic_accelerator": {"ammunition": 10}},
		"components": [
			{"id": "base", "kind": "k", "material": "adamantium", "x": 800, "y": 560, "w": 40, "h": 160},
			{"id": "core", "kind": "k", "material": "electronic_module", "x": 800, "y": 450, "w": 50, "h": 50, "critical_asset": true, "supports": ["ghost"]},
		],
	}))
	assert_eq(def.errors.size(), 3, ", ".join(def.errors))


func test_rejects_bad_objectives() -> void:
	var def := _parse(_mission({"objectives": [
		{"id": "a", "type": "destroy_critical", "mandatory": false, "label": "L", "targets": ["base"]},
		{"id": "b", "type": "destroy_components", "mandatory": false, "label": "L", "targets": ["base"], "count": 3},
		{"id": "c", "type": "structural_damage", "mandatory": false, "label": "L", "fraction": 1.5},
		{"id": "d", "type": "max_shots", "mandatory": false, "label": "L"},
		{"id": "e", "type": "teleport", "mandatory": false, "label": "L"},
		{"id": "f", "type": "protect", "mandatory": false, "label": "L", "targets": []},
	]}))
	# a: base not critical; b: count; c: fraction; d: limit; e: type; f: targets;
	# + no mandatory goal + core has no destroy_critical objective.
	assert_eq(def.errors.size(), 8, ", ".join(def.errors))


func test_rejects_bad_geometry_ammo_and_benchmarks() -> void:
	# Parse errors (bad ammunition) stop before cross-validation.
	var def := _parse(_mission({"weapons": {"kinetic_accelerator": {"ammunition": 0}}}))
	assert_eq(def.errors.size(), 1, ", ".join(def.errors))
	def = _parse(_mission({
		"operative": [9000, 640],
		"recommended_shots": 50,
		"target_time": 0,
		"statics": [{"x": 100, "y": 600, "w": -5, "h": 10}],
	}))
	# operative outside, ammo (10) below recommended (50), target_time, static size.
	assert_eq(def.errors.size(), 4, ", ".join(def.errors))


func test_rejects_structural_cycles_and_missing_files() -> void:
	var def := _parse(_mission({"components": [
		{"id": "a", "kind": "k", "material": "concrete", "x": 800, "y": 560, "w": 40, "h": 40, "supports": ["b"]},
		{"id": "b", "kind": "k", "material": "concrete", "x": 800, "y": 520, "w": 40, "h": 40, "supports": ["a"]},
		{"id": "core", "kind": "ai_core", "material": "electronic_module", "x": 800, "y": 450, "w": 50, "h": 50, "critical_asset": true},
	]}))
	assert_false(def.is_valid())
	assert_true(def.errors.has("mission 'm': support cycle: a -> b -> a") or def.errors.has("mission 'm': support cycle: b -> a -> b"), ", ".join(def.errors))
	assert_false(MissionDefinition.load_from_file("res://data/missions/none.json", _materials, _weapons).is_valid())
	assert_false(MissionDefinition.from_json_text("[]", _materials, _weapons).is_valid())
	assert_false(MissionDefinition.from_json_text("{oops", _materials, _weapons).is_valid())
