class_name UpgradeRules
extends RefCounted
## Player-selected weapon upgrades paid with Research Data. Costs and effects come from
## data/weapons.json; levels are stored in ProgressData. No UI yet: this is the purchase rule and
## the source of upgrade levels for MissionEngine. Chapter technology unlocks are separate
## (WeaponCatalog.unlocked_by_chapter).


## Research Data cost of the next level, or -1 when maxed or not upgradable.
static func next_cost(catalog: WeaponCatalog, progress: ProgressData, weapon_id: String, attribute: String) -> int:
	var spec := catalog.get_weapon(weapon_id)
	if spec == null or not spec.supports_upgrade(attribute):
		return -1
	var level := progress.upgrade_level(weapon_id, attribute)
	if level >= WeaponCatalog.MAX_UPGRADE_LEVEL:
		return -1
	return int(spec.upgrades[attribute].costs[level])


static func can_purchase(catalog: WeaponCatalog, progress: ProgressData, weapon_id: String, attribute: String) -> bool:
	var cost := next_cost(catalog, progress, weapon_id, attribute)
	return cost > 0 and progress.research_data >= cost


## Buys the next level. Returns false (and changes nothing) when it is not affordable or possible.
static func purchase(catalog: WeaponCatalog, progress: ProgressData, weapon_id: String, attribute: String) -> bool:
	if not can_purchase(catalog, progress, weapon_id, attribute):
		return false
	var cost := next_cost(catalog, progress, weapon_id, attribute)
	if not progress.spend_research_data(cost):
		return false
	progress.set_upgrade_level(weapon_id, attribute, progress.upgrade_level(weapon_id, attribute) + 1)
	return true


## Upgrade levels for MissionEngine, filtered to weapons/attributes that exist in the catalog
## (so a save from a different content version can never inject unknown stats).
static func levels_for_engine(catalog: WeaponCatalog, progress: ProgressData) -> Dictionary:
	var result := {}
	for weapon_id: String in progress.weapon_upgrades:
		var spec := catalog.get_weapon(weapon_id)
		if spec == null:
			continue
		var levels := {}
		for attribute: String in progress.weapon_upgrades[weapon_id]:
			if spec.supports_upgrade(attribute):
				levels[attribute] = progress.upgrade_level(weapon_id, attribute)
		result[weapon_id] = levels
	return result
