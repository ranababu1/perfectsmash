extends TestCase
## StructuralDependencySystem: support relationships, cascades, validation, and how it combines
## with DamageableComponent for a critical asset.


## A small Helix-style stack:
##   core            (critical asset) rests on deck
##   deck            rests on pillar_l + pillar_r (needs both)
##   antenna         rests on deck
##   rack            rests on leg_a, leg_b, leg_c (needs 2 of 3)
func _helix() -> StructuralDependencySystem:
	return StructuralDependencySystem.from_entries([
		{"id": "pillar_l"}, {"id": "pillar_r"},
		{"id": "deck", "supports": ["pillar_l", "pillar_r"]},
		{"id": "core", "supports": ["deck"]},
		{"id": "antenna", "supports": ["deck"]},
		{"id": "leg_a"}, {"id": "leg_b"}, {"id": "leg_c"},
		{"id": "rack", "supports": ["leg_a", "leg_b", "leg_c"], "min_supports": 2},
	])


func test_valid_relationships() -> void:
	var s := _helix()
	assert_true(s.is_valid(), ", ".join(s.errors))
	assert_true(s.is_anchored("pillar_l"))
	assert_false(s.is_anchored("deck"))
	assert_eq(s.supports_of("deck"), ["pillar_l", "pillar_r"])
	assert_eq(s.dependents_of("deck"), ["core", "antenna"])
	for id: String in ["pillar_l", "deck", "core", "rack"]:
		assert_true(s.is_supported(id))


func test_cascade_in_deterministic_order() -> void:
	var s := _helix()
	var released := s.fail("pillar_r")
	assert_eq(released, ["deck", "core", "antenna"] as Array[String], "deck loses a required support; everything on it follows")
	assert_true(s.is_failed("core"))
	assert_true(s.is_supported("pillar_l"), "unrelated pieces are unaffected")
	assert_true(s.is_supported("rack"))


func test_redundant_supports() -> void:
	var s := _helix()
	assert_eq(s.fail("leg_a").size(), 0, "rack still has 2 of 3 legs")
	assert_eq(s.intact_support_count("rack"), 2)
	assert_eq(s.fail("leg_c"), ["rack"] as Array[String], "second leg lost releases it")


func test_dependency_removal_is_idempotent() -> void:
	var s := _helix()
	s.fail("deck")
	assert_eq(s.fail("deck").size(), 0, "failing twice releases nothing new")
	assert_eq(s.fail("core").size(), 0, "already released")
	assert_false(s.is_failed("pillar_l"), "supports below are not affected by what they carried")
	s.reset()
	assert_false(s.is_failed("deck"))
	assert_true(s.is_supported("core"))


func test_unknown_component_is_safe() -> void:
	var s := _helix()
	assert_eq(s.fail("ghost").size(), 0)
	assert_false(s.is_supported("ghost"))
	assert_false(s.has_component("ghost"))
	assert_eq(s.supports_of("ghost"), [])


func test_rejects_invalid_relationships() -> void:
	var s := StructuralDependencySystem.from_entries([
		{"id": "a", "supports": ["missing"]},
		{"id": "b", "supports": ["b"]},
		{"id": "c", "supports": ["a", "a"]},
		{"id": "d", "supports": ["a"], "min_supports": 3},
		{"id": "e", "supports": ["a"], "min_supports": 0},
	])
	assert_false(s.is_valid())
	assert_eq(s.errors.size(), 5, ", ".join(s.errors))
	s = StructuralDependencySystem.from_entries([{"id": "x"}, {"id": "x"}, {"supports": []}, {"id": "y", "supports": "x"}])
	assert_eq(s.errors.size(), 3, ", ".join(s.errors))


func test_rejects_cycles() -> void:
	var s := StructuralDependencySystem.from_entries([
		{"id": "ground"},
		{"id": "a", "supports": ["c"]},
		{"id": "b", "supports": ["a"]},
		{"id": "c", "supports": ["b"]},
	])
	assert_false(s.is_valid())
	assert_true(s.errors[0].begins_with("support cycle"), s.errors[0])


## Damage and structure together: destroying a support through damage releases the critical
## core above it, while the core keeps its own (undamaged) state until it is hit or falls.
func test_damage_driven_cascade_and_critical_asset_state() -> void:
	var materials := MaterialCatalog.load_from_file()
	var s := _helix()
	var pillar := DamageableComponent.new("pillar_r", materials.get_material("lightweight_alloy"))
	var core := DamageableComponent.new("core", materials.get_material("electronic_module"), 1.0, true)
	var released: Array[String] = []
	pillar.destroyed.connect(func(c: DamageableComponent) -> void: released.append_array(s.fail(c.id)))
	pillar.receive_damage(50.0, DamageRules.TYPE_IMPACT)
	assert_eq(released.size(), 0, "a damaged pillar still holds")
	assert_eq(pillar.state, DamageableComponent.State.DAMAGED)
	pillar.receive_damage(200.0, DamageRules.TYPE_IMPACT)
	assert_true(pillar.is_destroyed())
	assert_true(released.has("core"), "core lost its support")
	assert_true(core.is_critical_asset)
	assert_eq(core.state, DamageableComponent.State.INTACT, "released is not destroyed")
	core.force_destroy("fall")
	assert_true(core.is_destroyed())
