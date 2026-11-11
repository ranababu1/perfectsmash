extends TestCase

const IDS := ["lightweight_alloy", "reinforced_steel", "composite", "glass_polymer", "concrete", "electronic_module", "ai_core_module", "energy_component", "reactor_housing", "temporal_crystal"]


func _material(overrides: Dictionary = {}) -> Dictionary:
	var m := {"id": "m", "density": 0.001, "friction": 0.5, "bounce": 0.0, "health": 100,
		"impact_resistance": 0.2, "blast_resistance": 0.1, "min_damage": 2, "blast_transmission": 0.5}
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


func test_blast_transmission_comes_from_data() -> void:
	var c := MaterialCatalog.load_from_file()
	var steel := c.get_material("reinforced_steel")
	var glass := c.get_material("glass_polymer")
	assert_true(steel.blast_transmission < c.get_material("lightweight_alloy").blast_transmission, "steel shields better than alloy")
	assert_true(c.get_material("concrete").blast_transmission <= steel.blast_transmission, "concrete shields best")
	assert_true(glass.blast_transmission > steel.blast_transmission)
	for id: String in IDS:
		var t := c.get_material(id).blast_transmission
		assert_true(t >= MaterialCatalog.MIN_BLAST_TRANSMISSION and t <= 1.0, "%s transmission %.2f in range" % [id, t])
	var custom := _catalog([_material({"id": "screen", "blast_transmission": 0.3})])
	assert_near(custom.get_material("screen").blast_transmission, 0.3, 0.0001)
	var bad := _catalog([_material({"id": "low", "blast_transmission": 0.01}), _material({"id": "high", "blast_transmission": 1.5})])
	assert_eq(bad.errors.size(), 2, ", ".join(bad.errors))
	var missing := _material({"id": "none"})
	missing.erase("blast_transmission")
	assert_false(_catalog([missing]).is_valid(), "blast_transmission is required")


func test_structural_resistance_defaults_to_impact_and_can_differ() -> void:
	var c := MaterialCatalog.load_from_file()
	var steel := c.get_material("reinforced_steel")
	assert_near(steel.structural_resistance, steel.impact_resistance, 0.0001, "defaults to impact resistance")
	var core := c.get_material("ai_core_module")
	var electronics := c.get_material("electronic_module")
	assert_near(core.impact_resistance, electronics.impact_resistance, 0.0001, "the core is as soft to weapon fire as other electronics")
	assert_near(core.blast_resistance, electronics.blast_resistance, 0.0001)
	assert_true(core.structural_resistance > electronics.structural_resistance, "but its housing survives falls better")
	assert_near(DamageRules.resistance_for(core, DamageRules.TYPE_STRUCTURAL), core.structural_resistance, 0.0001)
	assert_near(DamageRules.resistance_for(core, DamageRules.TYPE_IMPACT), core.impact_resistance, 0.0001)
	var custom := _catalog([_material({"id": "s", "structural_resistance": 0.5})])
	assert_near(custom.get_material("s").structural_resistance, 0.5, 0.0001)
	assert_false(_catalog([_material({"id": "t", "structural_resistance": 0.99})]).is_valid())


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
