extends TestCase


func _valid_level() -> Dictionary:
	return {
		"id": "T01", "name": "Test", "shots": 2, "par": 1,
		"launcher": [180, 560],
		"objective": {"type": "destroy_targets"},
		"statics": [{"x": 900, "y": 600, "w": 100, "h": 40}],
		"blocks": [{"x": 900, "y": 540, "w": 20, "h": 80, "material": "stone", "rot": 90}],
		"targets": [{"x": 900, "y": 480, "r": 20}],
		"solution": [[600, -400]],
	}


func test_parses_valid_level() -> void:
	var def := LevelDefinition.from_dict(_valid_level())
	assert_true(def.is_valid(), "valid level rejected: %s" % ", ".join(def.errors))
	assert_eq(def.shots, 2)
	assert_eq(def.blocks[0].material, "stone")
	assert_near(def.blocks[0].rotation, PI / 2.0, 0.0001, "rotation converted to radians")
	assert_eq(def.solution[0], Vector2(600, -400))


func test_rejects_non_dictionary() -> void:
	assert_false(LevelDefinition.from_dict([1, 2]).is_valid())


func test_rejects_missing_fields() -> void:
	var data := _valid_level()
	data.erase("id")
	data.erase("launcher")
	var def := LevelDefinition.from_dict(data)
	assert_false(def.is_valid())
	assert_true(def.errors.size() >= 2, "reports each missing field")


func test_rejects_par_above_shots() -> void:
	var data := _valid_level()
	data.par = 3
	assert_false(LevelDefinition.from_dict(data).is_valid())


func test_rejects_shot_budget_bounds() -> void:
	var data := _valid_level()
	data.shots = 0
	assert_false(LevelDefinition.from_dict(data).is_valid(), "zero shots")
	data.shots = LevelDefinition.MAX_SHOTS + 1
	data.par = 1
	assert_false(LevelDefinition.from_dict(data).is_valid(), "too many shots")


func test_rejects_fractional_shots() -> void:
	var data := _valid_level()
	data.shots = 1.5
	assert_false(LevelDefinition.from_dict(data).is_valid())


func test_rejects_unknown_material_and_objective() -> void:
	var data := _valid_level()
	data.blocks[0].material = "jelly"
	assert_false(LevelDefinition.from_dict(data).is_valid(), "material")
	data = _valid_level()
	data.objective = {"type": "explode_everything"}
	assert_false(LevelDefinition.from_dict(data).is_valid(), "objective")


func test_destroy_objective_requires_targets() -> void:
	var data := _valid_level()
	data.targets = []
	assert_false(LevelDefinition.from_dict(data).is_valid())


func test_topple_objective_validates_line() -> void:
	var data := _valid_level()
	data.objective = {"type": "topple", "line_y": 500}
	var def := LevelDefinition.from_dict(data)
	assert_true(def.is_valid(), "valid topple: %s" % ", ".join(def.errors))
	assert_near(def.topple_line_y, 500.0, 0.001)
	data.objective = {"type": "topple", "line_y": GameConfig.GROUND_TOP + 10}
	assert_false(LevelDefinition.from_dict(data).is_valid(), "line below ground")


func test_rejects_out_of_world_objects() -> void:
	var data := _valid_level()
	data.targets[0].x = -50
	assert_false(LevelDefinition.from_dict(data).is_valid())


func test_rejects_overpowered_solution() -> void:
	var data := _valid_level()
	data.solution = [[GameConfig.MAX_LAUNCH_SPEED * 2.0, 0]]
	assert_false(LevelDefinition.from_dict(data).is_valid())


func test_catalog_detects_duplicates_and_bad_json() -> void:
	var dup := JSON.stringify({"levels": [_valid_level(), _valid_level()]})
	assert_false(LevelCatalog.from_json_text(dup).is_valid(), "duplicate ids")
	assert_false(LevelCatalog.from_json_text("{not json").is_valid(), "bad json")
	assert_false(LevelCatalog.from_json_text("{\"levels\": []}").is_valid(), "empty")


func test_shipped_catalog_is_valid() -> void:
	var catalog := LevelCatalog.load_from_file()
	assert_true(catalog.is_valid(), "catalog errors: %s" % ", ".join(catalog.errors))
	assert_true(catalog.levels.size() >= 20, "expected at least 20 levels, got %d" % catalog.levels.size())
	for def in catalog.levels:
		assert_false(def.solution.is_empty(), "level %s has no verified solution" % def.id)
