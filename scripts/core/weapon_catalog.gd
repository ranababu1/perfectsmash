class_name WeaponCatalog
extends RefCounted
## Loads and validates weapon definitions and their upgrade tables (data/weapons.json), and
## computes effective stats for a set of upgrade levels through one shared function.
## Weapons describe how they are delivered and what damage they carry; how a material reacts is
## decided by MaterialCatalog data and DamageRules, never by weapon code.

const DEFAULT_PATH := "res://data/weapons.json"
const MAX_UPGRADE_LEVEL := 3
## Straight, fast, direction-only aim vs. a ballistic arc with variable launch power.
const DELIVERIES := ["direct", "lobbed"]
## Longest air-burst fuse: it must run out before a projectile expires (WeaponProjectile.MAX_LIFETIME, 6 s).
const MAX_FUSE_SECONDS := 5.0
const UPGRADE_ATTRIBUTES := [
	"impact_energy", "penetration", "blast_efficiency",
	"energy_capacity", "targeting_assistance", "energy_efficiency", "piercing",
]
const OPS := ["multiply", "add"]
const REQUIRED_STATS := [
	"launch_speed", "min_launch_speed", "gravity_scale", "projectile_radius", "projectile_mass",
	"impact_damage", "penetration", "blast_damage", "blast_radius", "blast_impulse",
	"blast_edge_falloff", "fuse_seconds", "ammunition", "cooldown", "aim_preview_seconds",
]
## Optional stats (chapter II-V weapons) and their defaults:
## pierce_count - components a round passes through after damaging them (0 = spent on first hit);
## pierce_speed_keep - share of its speed a round keeps after each pierce (0-1);
## pierce_max_resistance - a round passes through components it destroys, or whose material's
## impact resistance is at most this (0.95 = anything);
## blast_ignores_cover - 1 = the blast is not attenuated by components in between (Disruptor EMP).
const OPTIONAL_STATS := {"pierce_count": 0.0, "pierce_speed_keep": 0.75, "pierce_max_resistance": 0.95, "blast_ignores_cover": 0.0}
const INTEGER_STATS := ["ammunition", "pierce_count"]
const MAX_PENETRATION := 0.9


class WeaponSpec:
	var id := ""
	var display_name := ""
	var unlock_chapter := 1
	var delivery := "direct"
	var stats := {}
	## attribute -> {stat: String, op: String, levels: Array[float], costs: Array[int]} (3 entries each)
	var upgrades := {}
	## material id -> damage multiplier for this weapon's impact and blast damage ("*" = every
	## other material; default 1). How strongly a weapon suits a material is weapon data.
	var material_bonus := {}

	func has_blast() -> bool:
		return float(stats.get("blast_damage", 0.0)) > 0.0

	func is_lobbed() -> bool:
		return delivery == "lobbed"

	func supports_upgrade(attribute: String) -> bool:
		return upgrades.has(attribute)

	## Base stats with every upgrade level applied. `levels` maps attribute -> 0..3; unknown or
	## unsupported attributes are ignored and levels are clamped (use validate_levels to report).
	func effective_stats(levels: Dictionary = {}) -> Dictionary:
		var result := stats.duplicate()
		for attribute: Variant in levels:
			if not upgrades.has(attribute):
				continue
			var level := clampi(int(levels[attribute]), 0, MAX_UPGRADE_LEVEL)
			if level == 0:
				continue
			var upgrade: Dictionary = upgrades[attribute]
			var stat: String = upgrade.stat
			var amount: float = upgrade.levels[level - 1]
			if upgrade.op == "multiply":
				result[stat] = float(result[stat]) * amount
			else:
				result[stat] = float(result[stat]) + amount
		result["penetration"] = clampf(float(result.penetration), 0.0, MAX_PENETRATION)
		for stat: String in INTEGER_STATS:
			result[stat] = int(round(float(result[stat])))
		result["material_bonus"] = material_bonus
		return result

	func validate_levels(levels: Dictionary) -> PackedStringArray:
		var problems := PackedStringArray()
		for attribute: Variant in levels:
			if not upgrades.has(attribute):
				problems.append("%s: no upgrade '%s'" % [id, str(attribute)])
				continue
			var level: Variant = levels[attribute]
			if not level is int or level < 0 or level > MAX_UPGRADE_LEVEL:
				problems.append("%s: '%s' level must be 0-%d" % [id, attribute, MAX_UPGRADE_LEVEL])
		return problems


var weapons := {}
var order: Array[String] = []
var errors := PackedStringArray()


static func load_from_file(path: String = DEFAULT_PATH) -> WeaponCatalog:
	var file := FileAccess.open(path, FileAccess.READ)
	if file == null:
		var catalog := WeaponCatalog.new()
		catalog.errors.append("cannot open %s (error %d)" % [path, FileAccess.get_open_error()])
		return catalog
	return from_json_text(file.get_as_text())


static func from_json_text(text: String) -> WeaponCatalog:
	var catalog := WeaponCatalog.new()
	var json := JSON.new()
	if json.parse(text) != OK:
		catalog.errors.append("invalid JSON at line %d: %s" % [json.get_error_line(), json.get_error_message()])
		return catalog
	var root: Variant = json.data
	if not root is Dictionary or not root.get("weapons") is Array:
		catalog.errors.append("root must be an object with a 'weapons' array")
		return catalog
	for entry: Variant in root.weapons:
		catalog._add(entry)
	if catalog.order.is_empty():
		catalog.errors.append("catalog contains no weapons")
	return catalog


func is_valid() -> bool:
	return errors.is_empty()


func has_weapon(weapon_id: String) -> bool:
	return weapons.has(weapon_id)


func get_weapon(weapon_id: String) -> WeaponSpec:
	return weapons.get(weapon_id)


## Damage multiplier of a weapon (its effective stats) against a material.
static func material_multiplier(stats: Dictionary, material_id: String) -> float:
	var bonus: Dictionary = stats.get("material_bonus", {})
	if bonus.is_empty():
		return 1.0
	return float(bonus.get(material_id, bonus.get("*", 1.0)))


## Weapons available in a chapter (automatic technology unlocks), in catalog order.
func unlocked_by_chapter(chapter_number: int) -> Array[String]:
	var ids: Array[String] = []
	for id in order:
		if (weapons[id] as WeaponSpec).unlock_chapter <= chapter_number:
			ids.append(id)
	return ids


func _add(entry: Variant) -> void:
	if not entry is Dictionary:
		errors.append("weapon entry is not an object")
		return
	var spec := WeaponSpec.new()
	var raw_id: Variant = entry.get("id")
	if not raw_id is String or raw_id.is_empty():
		errors.append("weapon without a string 'id'")
		return
	spec.id = raw_id
	var prefix := "weapon '%s': " % spec.id
	var name: Variant = entry.get("display_name")
	if name is String and not name.is_empty():
		spec.display_name = name
	else:
		errors.append(prefix + "missing display_name")
	var chapter: Variant = entry.get("unlock_chapter")
	if chapter is float and chapter == floorf(chapter) and chapter >= 1:
		spec.unlock_chapter = int(chapter)
	else:
		errors.append(prefix + "unlock_chapter must be a whole number >= 1")
	spec.delivery = str(entry.get("delivery", ""))
	if not DELIVERIES.has(spec.delivery):
		errors.append(prefix + "delivery must be one of %s" % ", ".join(DELIVERIES))
	_parse_stats(spec, entry.get("stats"), prefix)
	_parse_upgrades(spec, entry.get("upgrades", {}), prefix)
	var bonus: Variant = entry.get("material_bonus", {})
	if bonus is Dictionary and bonus.values().all(func(v: Variant) -> bool: return (v is float or v is int) and v >= 0.0):
		for key: Variant in bonus:
			spec.material_bonus[str(key)] = float(bonus[key])
	else:
		errors.append(prefix + "material_bonus must map material ids to numbers >= 0")
	if weapons.has(spec.id):
		errors.append(prefix + "duplicate id")
		return
	weapons[spec.id] = spec
	order.append(spec.id)


func _parse_stats(spec: WeaponSpec, raw: Variant, prefix: String) -> void:
	if not raw is Dictionary:
		errors.append(prefix + "stats must be an object")
		return
	for key: String in REQUIRED_STATS:
		var value: Variant = raw.get(key)
		if not (value is float or value is int) or float(value) < 0.0:
			errors.append(prefix + "stat '%s' must be a non-negative number" % key)
			spec.stats[key] = 0.0
		else:
			spec.stats[key] = float(value)
	for key: String in OPTIONAL_STATS:
		var optional: Variant = raw.get(key, OPTIONAL_STATS[key])
		if not (optional is float or optional is int) or float(optional) < 0.0:
			errors.append(prefix + "stat '%s' must be a non-negative number" % key)
			optional = OPTIONAL_STATS[key]
		spec.stats[key] = float(optional)
	var s := spec.stats
	if s.pierce_speed_keep > 1.0 or s.pierce_count != floorf(s.pierce_count):
		errors.append(prefix + "pierce_count must be whole and pierce_speed_keep at most 1")
	if s.launch_speed <= 0.0 or s.min_launch_speed <= 0.0 or s.min_launch_speed > s.launch_speed:
		errors.append(prefix + "need 0 < min_launch_speed <= launch_speed")
	if s.projectile_radius <= 0.0 or s.projectile_mass <= 0.0:
		errors.append(prefix + "projectile radius and mass must be positive")
	if s.cooldown <= 0.0:
		errors.append(prefix + "cooldown must be positive")
	if s.ammunition < 1.0 or s.ammunition != floorf(s.ammunition):
		errors.append(prefix + "ammunition must be a whole number >= 1")
	if s.penetration > MAX_PENETRATION:
		errors.append(prefix + "penetration must be <= %s" % MAX_PENETRATION)
	if s.impact_damage <= 0.0 and s.blast_damage <= 0.0:
		errors.append(prefix + "weapon deals no damage")
	if s.blast_damage > 0.0 and (s.blast_radius <= 0.0 or s.blast_edge_falloff > 1.0):
		errors.append(prefix + "blast needs radius > 0 and edge falloff in 0-1")
	if spec.delivery == "direct" and s.min_launch_speed != s.launch_speed:
		errors.append(prefix + "direct weapons fire at a fixed speed (min_launch_speed == launch_speed)")
	if s.fuse_seconds > MAX_FUSE_SECONDS:
		errors.append(prefix + "fuse_seconds must be 0 (contact only) or at most %s s" % MAX_FUSE_SECONDS)
	if spec.delivery == "lobbed" and s.blast_damage <= 0.0:
		errors.append(prefix + "lobbed charges must have a blast (area damage)")
	if s.fuse_seconds > 0.0 and s.blast_damage <= 0.0:
		errors.append(prefix + "only blast weapons can have a fuse")


func _parse_upgrades(spec: WeaponSpec, raw: Variant, prefix: String) -> void:
	if not raw is Dictionary:
		errors.append(prefix + "upgrades must be an object")
		return
	for attribute: Variant in raw:
		var upgrade: Variant = raw[attribute]
		var where := prefix + "upgrade '%s': " % str(attribute)
		if not UPGRADE_ATTRIBUTES.has(attribute):
			errors.append(where + "unknown attribute")
			continue
		if not upgrade is Dictionary:
			errors.append(where + "must be an object")
			continue
		var stat: Variant = upgrade.get("stat")
		var op: Variant = upgrade.get("op")
		var levels: Variant = upgrade.get("levels")
		var costs: Variant = upgrade.get("costs")
		var ok := true
		if not costs is Array or costs.size() != MAX_UPGRADE_LEVEL 				or not costs.all(func(v: Variant) -> bool: return (v is float or v is int) and v >= 1 and v == floorf(v)):
			errors.append(where + "needs %d whole Research Data costs >= 1" % MAX_UPGRADE_LEVEL)
			ok = false
		if not REQUIRED_STATS.has(stat) and not OPTIONAL_STATS.has(stat):
			errors.append(where + "unknown stat '%s'" % str(stat))
			ok = false
		if not OPS.has(op):
			errors.append(where + "op must be multiply or add")
			ok = false
		if not levels is Array or levels.size() != MAX_UPGRADE_LEVEL \
				or not levels.all(func(v: Variant) -> bool: return v is float or v is int):
			errors.append(where + "needs exactly %d numeric levels" % MAX_UPGRADE_LEVEL)
			ok = false
		elif op == "multiply" and not levels.all(func(v: Variant) -> bool: return float(v) > 0.0):
			errors.append(where + "multipliers must be positive")
			ok = false
		if ok:
			var values: Array[float] = []
			for v: Variant in levels:
				values.append(float(v))
			var prices: Array[int] = []
			for v: Variant in costs:
				prices.append(int(v))
			spec.upgrades[attribute] = {"stat": stat, "op": op, "levels": values, "costs": prices}
