extends TestCase
## WeaponState.reload_completed fires exactly once per finished cooldown.

var _weapons := WeaponCatalog.load_from_file()


func _state(id: String, mission_ammo: int = 5) -> WeaponState:
	return WeaponState.new(_weapons.get_weapon(id), mission_ammo)


func test_fires_once_when_cooldown_finishes() -> void:
	var w := _state("breach_charge")
	var events: Array = []
	w.reload_completed.connect(func(id: String) -> void: events.append(id))
	w.fire()
	w.tick(0.5)
	assert_eq(events.size(), 0, "still reloading")
	w.tick(100.0)
	assert_eq(events.size(), 1, "fires when the cooldown ends")
	assert_eq(events[0], "breach_charge", "carries the weapon id")
	w.tick(1.0)
	w.tick(1.0)
	assert_eq(events.size(), 1, "idle ticks do not re-emit")


func test_never_fires_without_a_shot_or_on_refused_fire() -> void:
	var w := _state("kinetic_accelerator")
	var events: Array = []
	w.reload_completed.connect(func(id: String) -> void: events.append(id))
	w.tick(5.0)
	assert_eq(events.size(), 0, "ready weapon ticking emits nothing")
	w.fire()
	w.fire()
	w.tick(100.0)
	assert_eq(events.size(), 1, "a refused shot does not queue a second reload")


func test_negative_delta_does_not_complete_and_each_cycle_emits() -> void:
	var w := _state("kinetic_accelerator")
	var events: Array = []
	w.reload_completed.connect(func(id: String) -> void: events.append(id))
	w.fire()
	w.tick(-1.0)
	assert_eq(events.size(), 0, "negative delta ignored")
	w.tick(100.0)
	w.fire()
	w.tick(100.0)
	assert_eq(events.size(), 2, "one event per cooldown cycle")


func test_last_round_still_reports_reload_complete() -> void:
	var w := _state("breach_charge", 1)
	var events: Array = []
	w.reload_completed.connect(func(id: String) -> void: events.append(id))
	w.fire()
	w.tick(100.0)
	assert_eq(events.size(), 1, "cooldown completes even with no ammo left")
	assert_false(w.has_ammo())
