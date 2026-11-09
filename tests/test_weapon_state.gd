extends TestCase

var _weapons := WeaponCatalog.load_from_file()


func _state(id: String, mission_ammo: int = 0, levels: Dictionary = {}) -> WeaponState:
	return WeaponState.new(_weapons.get_weapon(id), mission_ammo, levels)


func test_ammunition_from_mission_or_default() -> void:
	assert_eq(_state("kinetic_accelerator", 14).ammo, 14, "mission allowance")
	assert_eq(_state("kinetic_accelerator").ammo, 24, "weapon default when the mission sets none")
	assert_eq(_state("breach_charge", 3, {"energy_capacity": 2}).ammo, 5, "capacity upgrade adds to the mission allowance")


func test_fire_consumes_ammo_and_starts_cooldown() -> void:
	var w := _state("breach_charge", 2)
	assert_true(w.can_fire())
	assert_true(w.fire())
	assert_eq(w.ammo, 1)
	assert_eq(w.shots_fired, 1)
	assert_false(w.can_fire(), "reloading")
	assert_false(w.fire(), "cannot fire during cooldown")
	assert_eq(w.ammo, 1, "a refused shot costs nothing")
	assert_near(w.cooldown_fraction(), 1.0, 0.001)
	w.tick(1.1)
	assert_near(w.cooldown_fraction(), 0.5, 0.001)
	w.tick(5.0)
	assert_true(w.can_fire())
	assert_true(w.fire())
	w.tick(10.0)
	assert_false(w.has_ammo())
	assert_false(w.fire(), "out of ammunition")
	w.tick(-3.0)
	assert_near(w.cooldown_remaining, 0.0, 0.001, "negative delta ignored")


func test_upgraded_cooldown() -> void:
	var w := _state("kinetic_accelerator", 10, {"energy_efficiency": 3})
	w.fire()
	assert_near(w.cooldown_remaining, 0.7, 0.001)


func test_direct_weapon_ignores_power() -> void:
	var w := _state("kinetic_accelerator")
	var full := w.launch_velocity(Vector2(1, -1), 1.0)
	var weak := w.launch_velocity(Vector2(1, -1), 0.1)
	assert_near(full.length(), 1700.0, 0.01)
	assert_near(weak.length(), 1700.0, 0.01, "fixed muzzle speed")
	assert_eq(w.launch_velocity(Vector2.ZERO, 1.0), Vector2.ZERO)


func test_lobbed_weapon_maps_power_to_speed() -> void:
	var w := _state("breach_charge")
	assert_near(w.launch_velocity(Vector2.RIGHT, 0.0).length(), 350.0, 0.01)
	assert_near(w.launch_velocity(Vector2.RIGHT, 0.5).length(), 650.0, 0.01)
	assert_near(w.launch_velocity(Vector2.RIGHT, 7.0).length(), 950.0, 0.01, "power clamped")
