extends TestCase
## Save schema v3 (missions, Research Data, upgrades), migration from v1/v2, anti-farming and
## upgrade purchases.

var _weapons := WeaponCatalog.load_from_file()


func _score(success: bool, points: int, research: int) -> Dictionary:
	return {"success": success, "mission_points": points, "research_data": research}


func test_migrates_v2_save_without_losing_anything() -> void:
	var v2 := {
		"version": 2,
		"levels": {"L01": {"stars": 3, "best_shots": 1}},
		"settings": {"sound": false, "vibration": true, "music": false, "voice": true},
		"story": {"seen": ["opening"]},
	}
	var p := ProgressData.from_dict(v2)
	assert_true(p.load_warnings.is_empty(), ", ".join(p.load_warnings))
	assert_eq(p.loaded_version, 2)
	assert_eq(p.stars_for("L01"), 3, "legacy results kept")
	assert_false(p.sound_enabled)
	assert_false(p.music_enabled)
	assert_true(p.has_seen_sequence("opening"))
	assert_eq(p.research_data, 0)
	assert_true(p.mission_results.is_empty())
	var saved := p.to_dict()
	assert_eq(int(saved.version), 3)
	assert_eq(saved.levels.L01.stars, 3)


func test_migrates_v1_save() -> void:
	var p := ProgressData.from_dict({"version": 1, "levels": {"L05": {"stars": 2, "best_shots": 2}}, "settings": {"sound": true, "vibration": false}})
	assert_true(p.load_warnings.is_empty(), ", ".join(p.load_warnings))
	assert_eq(p.stars_for("L05"), 2)
	assert_false(p.vibration_enabled)
	assert_eq(p.weapon_upgrades, {})


func test_v3_round_trip() -> void:
	var p := ProgressData.new()
	var optional: Array[String] = ["racks"]
	p.record_mission("helix_01", _score(true, 3200, 40), 3, 42.5, optional)
	p.set_upgrade_level("kinetic_accelerator", "impact_energy", 2)
	var copy := ProgressData.from_dict(JSON.parse_string(JSON.stringify(p.to_dict())))
	assert_true(copy.load_warnings.is_empty(), ", ".join(copy.load_warnings))
	assert_true(copy.is_mission_completed("helix_01"))
	assert_eq(copy.mission_result("helix_01").best_points, 3200)
	assert_eq(copy.mission_result("helix_01").optional_completed, ["racks"] as Array[String])
	assert_near(copy.mission_result("helix_01").best_time, 42.5, 0.001)
	assert_eq(copy.research_data, 40)
	assert_eq(copy.research_data_earned, 40)
	assert_eq(copy.upgrade_level("kinetic_accelerator", "impact_energy"), 2)


func test_research_data_cannot_be_farmed() -> void:
	var p := ProgressData.new()
	var none: Array[String] = []
	assert_eq(p.record_mission("m", _score(true, 2000, 30), 5, 60.0, none), 30)
	assert_eq(p.record_mission("m", _score(true, 2100, 30), 4, 50.0, none), 0, "same result again grants nothing")
	assert_eq(p.record_mission("m", _score(true, 2500, 38), 3, 40.0, none), 8, "only the improvement is granted")
	assert_eq(p.research_data, 38)
	var best := p.mission_result("m")
	assert_eq(best.best_points, 2500)
	assert_eq(best.best_shots, 3)
	assert_near(best.best_time, 40.0, 0.001)
	assert_eq(p.record_mission("m", _score(false, 900, 0), 20, 300.0, none), 0)
	assert_eq(p.mission_result("m").best_shots, 3, "a failed run never replaces bests")
	assert_true(p.is_mission_completed("m"))


func test_failed_first_attempt_is_not_completed() -> void:
	var p := ProgressData.new()
	var optional: Array[String] = ["racks"]
	p.record_mission("m", _score(false, 800, 0), 9, 80.0, optional)
	assert_false(p.is_mission_completed("m"))
	assert_eq(p.mission_result("m").best_points, 800, "destruction points still recorded")
	assert_eq(p.mission_result("m").optional_completed, [] as Array[String], "optional credit needs a successful run")
	assert_eq(p.mission_result("m").best_shots, 0)


func test_drops_invalid_v3_fields() -> void:
	var p := ProgressData.from_dict({
		"version": 3, "levels": {},
		"missions": {"ok": {"completed": true, "best_points": 1, "best_research_data": 1, "best_shots": 1, "best_time": 1.0, "optional_completed": []},
			"bad": {"completed": "yes"}},
		"research": {"balance": 50, "earned": 10},
		"upgrades": {"kinetic_accelerator": {"impact_energy": 7, "penetration": 1}, "x": 3},
	})
	assert_true(p.mission_results.has("ok"))
	assert_false(p.mission_results.has("bad"))
	assert_eq(p.research_data, 0, "balance above lifetime earnings is not trusted")
	assert_eq(p.upgrade_level("kinetic_accelerator", "impact_energy"), 0)
	assert_eq(p.upgrade_level("kinetic_accelerator", "penetration"), 1)
	assert_eq(p.load_warnings.size(), 4, ", ".join(p.load_warnings))
	assert_false(ProgressData.from_dict({"version": 4}).load_warnings.is_empty(), "newer versions rejected")


func test_upgrade_purchase_rules() -> void:
	var p := ProgressData.new()
	assert_eq(UpgradeRules.next_cost(_weapons, p, "kinetic_accelerator", "impact_energy"), 30)
	assert_false(UpgradeRules.purchase(_weapons, p, "kinetic_accelerator", "impact_energy"), "cannot afford")
	var none: Array[String] = []
	p.record_mission("m", _score(true, 1, 200), 1, 1.0, none)
	assert_true(UpgradeRules.purchase(_weapons, p, "kinetic_accelerator", "impact_energy"))
	assert_true(UpgradeRules.purchase(_weapons, p, "kinetic_accelerator", "impact_energy"))
	assert_eq(p.research_data, 110)
	assert_eq(p.upgrade_level("kinetic_accelerator", "impact_energy"), 2)
	assert_true(UpgradeRules.purchase(_weapons, p, "kinetic_accelerator", "impact_energy"))
	assert_eq(p.research_data, 10)
	assert_eq(UpgradeRules.next_cost(_weapons, p, "kinetic_accelerator", "impact_energy"), -1, "maxed at level 3")
	assert_false(UpgradeRules.purchase(_weapons, p, "kinetic_accelerator", "impact_energy"))
	assert_eq(UpgradeRules.next_cost(_weapons, p, "kinetic_accelerator", "blast_efficiency"), -1, "kinetic has no blast upgrade")
	assert_eq(UpgradeRules.next_cost(_weapons, p, "railgun", "impact_energy"), -1)
	assert_false(p.spend_research_data(-5))


func test_upgrades_flow_into_effective_stats() -> void:
	var p := ProgressData.new()
	p.set_upgrade_level("breach_charge", "energy_capacity", 2)
	p.set_upgrade_level("ghost_weapon", "impact_energy", 3)
	p.set_upgrade_level("kinetic_accelerator", "made_up", 2)
	var levels := UpgradeRules.levels_for_engine(_weapons, p)
	assert_false(levels.has("ghost_weapon"), "unknown weapons filtered")
	assert_false(levels.get("kinetic_accelerator", {}).has("made_up"), "unknown attributes filtered")
	var materials := MaterialCatalog.load_from_file()
	var def := MissionDefinition.load_from_file("res://data/missions/helix_01.json", materials, _weapons)
	var engine := MissionEngine.new(def, materials, _weapons, levels)
	assert_eq(engine.weapons.breach_charge.ammo, 5, "3 mission charges + 2 capacity")
