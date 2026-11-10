extends TestCase


func _weapon(overrides: Dictionary = {}) -> Dictionary:
	var stats := {
		"launch_speed": 1000, "min_launch_speed": 1000, "gravity_scale": 0.5, "projectile_radius": 8,
		"projectile_mass": 2, "impact_damage": 50, "penetration": 0, "blast_damage": 0, "blast_radius": 0,
		"blast_impulse": 0, "blast_edge_falloff": 0, "fuse_seconds": 0, "ammunition": 10, "cooldown": 1,
		"aim_preview_seconds": 0.5,
	}
	var w := {"id": "w", "display_name": "W", "unlock_chapter": 1, "delivery": "direct", "stats": stats, "upgrades": {}}
	for key: String in overrides:
		if key == "stats":
			stats.merge(overrides.stats, true)
		else:
			w[key] = overrides[key]
	return w


func _catalog(entries: Array) -> WeaponCatalog:
	return WeaponCatalog.from_json_text(JSON.stringify({"weapons": entries}))


func test_shipped_catalog_has_exactly_two_weapons() -> void:
	var c := WeaponCatalog.load_from_file()
	assert_true(c.is_valid(), ", ".join(c.errors))
	assert_eq(c.order, ["kinetic_accelerator", "breach_charge"] as Array[String])
	assert_eq(c.unlocked_by_chapter(1).size(), 2)


func test_weapons_have_distinct_tactical_roles() -> void:
	var c := WeaponCatalog.load_from_file()
	var kinetic := c.get_weapon("kinetic_accelerator")
	var breach := c.get_weapon("breach_charge")
	assert_eq(kinetic.delivery, "direct")
	assert_eq(breach.delivery, "lobbed")
	assert_false(kinetic.has_blast(), "kinetic is single-target")
	assert_true(breach.has_blast(), "breach deals area damage")
	assert_true(kinetic.stats.impact_damage > breach.stats.impact_damage * 5.0, "kinetic carries the direct damage")
	assert_true(kinetic.stats.launch_speed > breach.stats.launch_speed, "kinetic is faster")
	assert_true(kinetic.stats.gravity_scale < breach.stats.gravity_scale, "kinetic flies flatter")
	assert_eq(kinetic.stats.min_launch_speed, kinetic.stats.launch_speed, "kinetic fires at fixed speed")
	assert_true(breach.stats.min_launch_speed < breach.stats.launch_speed, "breach power is variable")
	assert_true(breach.stats.ammunition < kinetic.stats.ammunition, "breach is limited")
	assert_true(breach.stats.cooldown > kinetic.stats.cooldown)


func test_breach_is_an_area_charge_with_contact_and_air_burst_fuse() -> void:
	var c := WeaponCatalog.load_from_file()
	var breach := c.get_weapon("breach_charge")
	var kinetic := c.get_weapon("kinetic_accelerator")
	assert_true(breach.stats.blast_radius > 0.0 and breach.stats.blast_damage > breach.stats.impact_damage * 5.0, "breach damage is the blast, not the hit")
	assert_true(breach.stats.fuse_seconds > 0.0, "breach has an air-burst fuse")
	# The fuse must outlast any lob that lands at launch height: 2 * v / g.
	var flight: float = 2.0 * breach.stats.launch_speed / (980.0 * breach.stats.gravity_scale)
	assert_true(breach.stats.fuse_seconds > flight, "fuse %.2f s outlasts a full-power lob (%.2f s)" % [breach.stats.fuse_seconds, flight])
	assert_eq(kinetic.stats.fuse_seconds, 0.0, "kinetic rounds have no fuse")


func test_fuse_and_lobbed_blast_validation() -> void:
	var too_long := _catalog([_weapon({"stats": {"blast_damage": 50, "blast_radius": 50, "fuse_seconds": 9}})])
	assert_false(too_long.is_valid(), "a fuse longer than the projectile lifetime is refused")
	var no_blast := _catalog([_weapon({"stats": {"fuse_seconds": 1}})])
	assert_false(no_blast.is_valid(), "a fuse needs a blast")
	var lobbed_no_blast := _catalog([_weapon({"delivery": "lobbed", "stats": {"min_launch_speed": 300}})])
	assert_false(lobbed_no_blast.is_valid(), "a lobbed charge needs a blast")
	var ok := _catalog([_weapon({"delivery": "lobbed", "stats": {"min_launch_speed": 300, "blast_damage": 50, "blast_radius": 50, "fuse_seconds": 2}})])
	assert_true(ok.is_valid(), ", ".join(ok.errors))


func test_upgrade_calculations() -> void:
	var kinetic := WeaponCatalog.load_from_file().get_weapon("kinetic_accelerator")
	var base := kinetic.effective_stats()
	assert_near(base.impact_damage, 90.0, 0.001)
	var up := kinetic.effective_stats({"impact_energy": 3, "penetration": 2, "energy_efficiency": 1})
	assert_near(up.impact_damage, 135.0, 0.001)
	assert_near(up.penetration, 0.2, 0.001)
	assert_near(up.cooldown, 0.9, 0.001)
	assert_near(kinetic.stats.impact_damage, 90.0, 0.001, "base stats are not mutated")
	var breach := WeaponCatalog.load_from_file().get_weapon("breach_charge")
	var b := breach.effective_stats({"energy_capacity": 2, "blast_efficiency": 1})
	assert_eq(b.ammunition, 5)
	assert_true(b.ammunition is int, "ammunition stays a whole number")
	assert_near(b.blast_damage, 184.0, 0.001)


func test_upgrade_levels_are_clamped_and_reported() -> void:
	var kinetic := WeaponCatalog.load_from_file().get_weapon("kinetic_accelerator")
	assert_near(kinetic.effective_stats({"impact_energy": 9}).impact_damage, 135.0, 0.001, "clamped to level 3")
	assert_near(kinetic.effective_stats({"impact_energy": -2}).impact_damage, 90.0, 0.001)
	assert_near(kinetic.effective_stats({"blast_efficiency": 3}).blast_damage, 0.0, 0.001, "unsupported attribute ignored")
	assert_eq(kinetic.validate_levels({"impact_energy": 2}).size(), 0)
	assert_eq(kinetic.validate_levels({"impact_energy": 4, "blast_efficiency": 1, "penetration": 1.5}).size(), 3)


func test_penetration_is_capped() -> void:
	var c := _catalog([_weapon({"stats": {"penetration": 0.8}, "upgrades": {"penetration": {"stat": "penetration", "op": "add", "levels": [0.1, 0.2, 0.5], "costs": [1, 2, 3]}}})])
	assert_true(c.is_valid(), ", ".join(c.errors))
	assert_near(c.get_weapon("w").effective_stats({"penetration": 3}).penetration, WeaponCatalog.MAX_PENETRATION, 0.001)


func test_rejects_invalid_weapons() -> void:
	var c := _catalog([
		_weapon({"id": "a", "delivery": "teleport"}),
		_weapon({"id": "b", "stats": {"min_launch_speed": 500}}),
		_weapon({"id": "c", "stats": {"blast_damage": 50}}),
		_weapon({"id": "d", "stats": {"impact_damage": 0}}),
		_weapon({"id": "e", "stats": {"ammunition": 2.5}}),
		_weapon({"id": "f", "stats": {"cooldown": 0}}),
	])
	assert_false(c.is_valid())
	assert_eq(c.errors.size(), 6, ", ".join(c.errors))


func test_rejects_invalid_upgrades_and_roots() -> void:
	var c := _catalog([_weapon({"upgrades": {
		"luck": {"stat": "impact_damage", "op": "add", "levels": [1, 2, 3], "costs": [1, 2, 3]},
		"impact_energy": {"stat": "charisma", "op": "power", "levels": [1, 2]},
		"energy_efficiency": {"stat": "cooldown", "op": "multiply", "levels": [0.9, 0, 0.7], "costs": [1, 2, 3]},
	}})])
	# luck: unknown attribute; impact_energy: stat, op, levels, missing costs; energy_efficiency: zero multiplier.
	assert_eq(c.errors.size(), 6, ", ".join(c.errors))
	assert_false(_catalog([_weapon(), _weapon()]).is_valid(), "duplicate id")
	assert_false(_catalog([{"display_name": "x"}]).is_valid(), "missing id")
	assert_false(_catalog([_weapon({"stats": {"launch_speed": "fast"}})]).is_valid())
	assert_false(_catalog([]).is_valid())
	assert_false(WeaponCatalog.from_json_text("{\"weapons\": 3}").is_valid())
	assert_true(WeaponCatalog.load_from_file().get_weapon("railgun") == null)
