class_name WeaponState
extends RefCounted
## Per-mission state of one weapon: effective (upgraded) stats, ammunition, reload cooldown and
## shots fired. Turns aim input into a launch velocity according to the weapon's delivery:
## direct weapons fire at a fixed speed (aim chooses direction only); lobbed weapons map aim
## power onto their speed range.

var spec: WeaponCatalog.WeaponSpec
var stats := {}
var ammo_capacity := 0
var ammo := 0
var cooldown_remaining := 0.0
var shots_fired := 0


## `mission_ammo` is the mission's allowance (<= 0 uses the weapon default). Capacity upgrades
## add their bonus on top of the mission allowance.
func _init(p_spec: WeaponCatalog.WeaponSpec, mission_ammo: int = 0, upgrade_levels: Dictionary = {}) -> void:
	spec = p_spec
	stats = spec.effective_stats(upgrade_levels)
	var base_ammo := int(spec.stats.ammunition)
	var upgrade_bonus := int(stats.ammunition) - base_ammo
	ammo_capacity = maxi(0, (mission_ammo if mission_ammo > 0 else base_ammo) + upgrade_bonus)
	ammo = ammo_capacity


func id() -> String:
	return spec.id


func has_ammo() -> bool:
	return ammo > 0


func can_fire() -> bool:
	return ammo > 0 and cooldown_remaining <= 0.0


## Consumes one round and starts the reload cooldown. Returns false (and changes nothing) when
## out of ammunition or still reloading.
func fire() -> bool:
	if not can_fire():
		return false
	ammo -= 1
	shots_fired += 1
	cooldown_remaining = float(stats.cooldown)
	return true


func tick(delta: float) -> void:
	cooldown_remaining = maxf(0.0, cooldown_remaining - maxf(delta, 0.0))


## 0 when ready, 1 right after firing (for the HUD reload indicator).
func cooldown_fraction() -> float:
	var total := float(stats.cooldown)
	return clampf(cooldown_remaining / total, 0.0, 1.0) if total > 0.0 else 0.0


## Launch velocity for an aim direction and a power in 0-1 (power is ignored by direct weapons).
func launch_velocity(direction: Vector2, power: float) -> Vector2:
	if direction.length() < 0.0001:
		return Vector2.ZERO
	var speed := float(stats.launch_speed)
	if spec.is_lobbed():
		speed = lerpf(float(stats.min_launch_speed), float(stats.launch_speed), clampf(power, 0.0, 1.0))
	return direction.normalized() * speed
