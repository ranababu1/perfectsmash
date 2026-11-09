extends TestCase

const IDS := ["lightweight_alloy", "reinforced_steel", "composite", "glass_polymer", "concrete", "electronic_module", "energy_component"]


func _material(overrides: Dictionary = {}) -> Dictionary:
	var m := {"id": "m", "density": 0.001, "friction": 0.5, "bounce": 0.0, "health": 100,
		"impact_resistance": 0.2, "blast_resistance": 0.1, "min_damage": 2}
	m.merge(overrides, true)
	return m


func _catalog(entries: Array) -> MaterialCatalog:
	return MaterialCatalog.from_json_text(JSON.stringify({"materials": entries}))


func test_shipped_catalog_is_valid() -> void:
	var catalog := MaterialCatalog.load_from_file()
	assert_true(catalog.is_valid(), ", ".join(catalog.errors))
	for id: String in IDS:
		assert_true(catalog.has_material(id), "missing %s" % id)
	assert_eq(catalog.order.size(), IDS.size())


func test_relative_resistances() -> void:
	var c := MaterialCatalog.load_from_file()
	var steel := c.get_material("reinforced_steel")
	var glass := c.get_material("glass_polymer")
	var concrete := c.get_material("concrete")
	assert_true(steel.impact_resistance > glass.impact_resistance, "steel resists impacts better than glass")
	assert_true(steel.health > glass.health)
	assert_true(concrete.blast_resistance > concrete.impact_resistance, "concrete is blast-resistant but chips under impacts")
	assert_true(c.get_material("electronic_module").blast_resistance < steel.blast_resistance)
	assert_true(c.get_material("energy_component").has_secondary_blast(), "energy components explode")
	assert_false(steel.has_secondary_blast())
	assert_near(steel.mass_for(Vector2(10, 20)), 200 * steel.density, 0.0001)


func test_missing_definition_returns_null() -> void:
	var c := MaterialCatalog.load_from_file()
	assert_true(c.get_material("unobtanium") == null)
	assert_false(c.has_material(""))


func test_rejects_invalid_values() -> void:
	var c := _catalog([
		_material({"id": "a", "density": 0}),
		_material({"id": "b", "impact_resistance": 0.99}),
		_material({"id": "c", "health": -5}),
		_material({"id": "d", "friction": "high"}),
	])
	assert_false(c.is_valid())
	assert_eq(c.errors.size(), 4, ", ".join(c.errors))


func test_rejects_duplicates_bad_secondary_and_bad_roots() -> void:
	var c := _catalog([_material(), _material(), _material({"id": "x", "on_destroyed": 5})])
	assert_eq(c.errors.size(), 2, ", ".join(c.errors))
	c = _catalog([_material({"id": "y", "on_destroyed": {"blast_damage": 10}})])
	assert_false(c.is_valid(), "secondary blast needs a radius")
	assert_false(_catalog([{"density": 1}]).is_valid(), "missing id")
	assert_false(_catalog([]).is_valid())
	assert_false(MaterialCatalog.from_json_text("[]").is_valid())
	assert_false(MaterialCatalog.from_json_text("{bad").is_valid())
	assert_false(MaterialCatalog.load_from_file("res://data/does_not_exist.json").is_valid())
