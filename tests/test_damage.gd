extends TestCase
## DamageRules maths and DamageableComponent health/state behaviour.

var _materials := MaterialCatalog.load_from_file()


func _component(material_id: String, scale: float = 1.0, critical: bool = false) -> DamageableComponent:
	return DamageableComponent.new("c", _materials.get_material(material_id), scale, critical)


func test_projectile_impact_scales_with_speed() -> void:
	assert_near(DamageRules.projectile_impact_damage(90.0, 1700.0, 1700.0), 90.0, 0.001)
	assert_near(DamageRules.projectile_impact_damage(90.0, 850.0, 1700.0), 45.0, 0.001, "spent round hits softer")
	assert_near(DamageRules.projectile_impact_damage(90.0, 9000.0, 1700.0), 90.0 * DamageRules.MAX_SPEED_FACTOR, 0.001, "capped")
	assert_near(DamageRules.projectile_impact_damage(90.0, 100.0, 0.0), 0.0, 0.001, "invalid reference")
	assert_near(DamageRules.projectile_impact_damage(0.0, 1700.0, 1700.0), 0.0, 0.001)


func test_collision_damage_ignores_light_contacts() -> void:
	assert_near(DamageRules.collision_damage(0.0), 0.0, 0.001)
	assert_near(DamageRules.collision_damage(DamageRules.COLLISION_DAMAGE_FLOOR), 0.0, 0.001)
	assert_near(DamageRules.collision_damage(DamageRules.COLLISION_DAMAGE_FLOOR + 100.0), 100.0 * DamageRules.COLLISION_DAMAGE_PER_IMPULSE, 0.001)


func test_material_resistance_and_penetration() -> void:
	assert_near(DamageRules.resisted_damage(100.0, 0.6, 0.0, 0.0), 40.0, 0.001)
	assert_near(DamageRules.resisted_damage(100.0, 0.6, 0.5, 0.0), 70.0, 0.001, "penetration halves the absorbed share")
	assert_near(DamageRules.resisted_damage(100.0, 2.0, 0.0, 0.0), 5.0, 0.001, "resistance capped at 95%")
	assert_near(DamageRules.resisted_damage(10.0, 0.6, 0.0, 15.0), 0.0, 0.001, "below per-hit minimum is ignored")
	assert_near(DamageRules.resisted_damage(-5.0, 0.0, 0.0, 0.0), 0.0, 0.001)


func test_blast_falloff_and_damage() -> void:
	assert_near(DamageRules.blast_falloff(0.0, 140.0, 0.25), 1.0, 0.001)
	assert_near(DamageRules.blast_falloff(70.0, 140.0, 0.25), 0.625, 0.001)
	assert_near(DamageRules.blast_falloff(140.0, 140.0, 0.25), 0.25, 0.001, "edge fraction at the radius")
	assert_near(DamageRules.blast_falloff(140.1, 140.0, 0.25), 0.0, 0.001, "nothing beyond the radius")
	assert_near(DamageRules.blast_falloff(10.0, 0.0, 0.25), 0.0, 0.001, "zero radius")
	assert_near(DamageRules.blast_damage(160.0, 70.0, 140.0, 0.25), 100.0, 0.001)
	var near := DamageRules.blast_damage(160.0, 20.0, 140.0, 0.25)
	var far := DamageRules.blast_damage(160.0, 120.0, 140.0, 0.25)
	assert_true(near > far, "closer pieces take more damage")


func test_blast_knockback_direction_and_falloff() -> void:
	var push := DamageRules.blast_impulse(900.0, Vector2(100, 100), Vector2(170, 100), 140.0, 0.25)
	assert_near(push.x, 900.0 * 0.625, 0.01)
	assert_near(push.y, 0.0, 0.001, "pushed straight away from the blast")
	var up := DamageRules.blast_impulse(900.0, Vector2(5, 5), Vector2(5, 5), 140.0, 0.25)
	assert_true(up.y < 0.0 and is_zero_approx(up.x), "piece at the centre is thrown upward")
	assert_eq(DamageRules.blast_impulse(900.0, Vector2.ZERO, Vector2(500, 0), 140.0, 0.25), Vector2.ZERO)


func test_distance_to_rotated_box() -> void:
	assert_near(DamageRules.distance_to_box(Vector2(0, 0), Vector2(0, 0), Vector2(50, 10), 0.0), 0.0, 0.001, "inside")
	assert_near(DamageRules.distance_to_box(Vector2(80, 0), Vector2(0, 0), Vector2(50, 10), 0.0), 30.0, 0.001)
	assert_near(DamageRules.distance_to_box(Vector2(0, 80), Vector2(0, 0), Vector2(50, 10), PI / 2.0), 30.0, 0.001, "rotated beam")


func test_progressive_states() -> void:
	var c := _component("glass_polymer")  # 50 health, no resistance, min 3
	var seen := []
	c.state_changed.connect(func(_c: DamageableComponent, _from: int, to: int) -> void: seen.append(to))
	assert_eq(c.state, DamageableComponent.State.INTACT)
	c.receive_damage(15.0, DamageRules.TYPE_IMPACT)
	assert_eq(c.state, DamageableComponent.State.DAMAGED, "70% -> damaged")
	c.receive_damage(20.0, DamageRules.TYPE_IMPACT)
	assert_eq(c.state, DamageableComponent.State.CRITICAL, "30% -> critical/unstable")
	assert_true(c.is_unstable())
	c.receive_damage(100.0, DamageRules.TYPE_IMPACT)
	assert_true(c.is_destroyed())
	assert_eq(seen, [DamageableComponent.State.DAMAGED, DamageableComponent.State.CRITICAL, DamageableComponent.State.DESTROYED])


func test_health_boundaries_and_skipped_states() -> void:
	var c := _component("glass_polymer")
	var destroyed_count := [0]
	c.destroyed.connect(func(_c: DamageableComponent) -> void: destroyed_count[0] += 1)
	assert_near(c.receive_damage(500.0, DamageRules.TYPE_IMPACT), 50.0, 0.001, "applied damage never exceeds health")
	assert_near(c.health, 0.0, 0.001)
	assert_true(c.is_destroyed(), "one huge hit jumps straight to destroyed")
	assert_near(c.receive_damage(10.0, DamageRules.TYPE_IMPACT), 0.0, 0.001, "no damage after destruction")
	c.force_destroy("out_of_bounds")
	assert_eq(destroyed_count[0], 1, "destroyed emitted once")
	assert_eq(DamageableComponent.state_for_fraction(0.75), DamageableComponent.State.INTACT)
	assert_eq(DamageableComponent.state_for_fraction(0.749), DamageableComponent.State.DAMAGED)
	assert_eq(DamageableComponent.state_for_fraction(0.35), DamageableComponent.State.DAMAGED)
	assert_eq(DamageableComponent.state_for_fraction(0.0), DamageableComponent.State.DESTROYED)


func test_material_resistance_per_damage_type() -> void:
	var steel := _component("reinforced_steel")  # 400 hp, impact 0.6, blast 0.4, min 15
	assert_near(steel.receive_damage(100.0, DamageRules.TYPE_IMPACT), 40.0, 0.001)
	assert_near(steel.receive_damage(100.0, DamageRules.TYPE_BLAST), 60.0, 0.001)
	assert_near(steel.receive_damage(30.0, DamageRules.TYPE_IMPACT), 0.0, 0.001, "12 < steel minimum 15")
	assert_near(steel.receive_damage(100.0, DamageRules.TYPE_IMPACT, 0.5), 70.0, 0.001, "penetration")
	assert_near(steel.receive_damage(100.0, "magic"), 0.0, 0.001, "unknown type rejected")
	var concrete := _component("concrete")
	var electronics := _component("electronic_module")
	assert_true(concrete.receive_damage(100.0, DamageRules.TYPE_BLAST) < electronics.receive_damage(100.0, DamageRules.TYPE_BLAST), "blast wrecks electronics, not concrete")


func test_destruction_threshold_with_health_scale() -> void:
	var sturdy := _component("lightweight_alloy", 2.0)
	assert_near(sturdy.max_health, 240.0, 0.001)
	var core := _component("electronic_module", 1.0, true)
	assert_true(core.is_critical_asset)
	core.receive_damage(80.0 / 0.9 + 1.0, DamageRules.TYPE_IMPACT)
	assert_true(core.is_destroyed(), "just over effective health destroys it")


func test_secondary_blast_only_after_destruction() -> void:
	var cell := _component("energy_component")
	assert_eq(cell.secondary_blast(), {}, "no secondary effect while intact")
	cell.force_destroy("test")
	var blast := cell.secondary_blast()
	assert_near(blast.damage, 70.0, 0.001)
	assert_near(blast.radius, 110.0, 0.001)
	var rack := _component("electronic_module")
	rack.force_destroy("test")
	assert_eq(rack.secondary_blast(), {}, "plain electronics do not explode")
