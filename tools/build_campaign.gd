extends SceneTree
## Builds missions L21–L100 of the campaign from the DESIGNS table below and writes them into
## data/levels.json after the 20 hand-built levels. Layouts come from parametric patterns with a
## seeded RNG, so a design + seed always produces the same level.
##
##   godot --headless -s tools/build_campaign.gd                    rebuild L21–L100 (keeps solutions of unchanged levels)
##   godot --headless --fixed-fps 60 -s tools/build_campaign.gd -- --check
##        also simulate every campaign level for 3 s without a shot; any that drifts or loses a core/ally
##        gets a new seed (variant) and is rebuilt
##   godot --headless -s tools/build_campaign.gd -- --merge=a.json,b.json
##        fold solver results (tools/solve_levels.gd --out=...) into levels.json; unsolved levels get a new
##        variant and are rebuilt without a solution, ready for the next solver pass
##
## Variants live in tools/campaign_variants.json ({id: n}); the seed is hash(id) + 7919 * n.
## A level ships only once tests/test_level_playthrough.gd verifies its stored solution.

const CatalogFormat := preload("res://tools/catalog_format.gd")
const VARIANTS_PATH := "res://tools/campaign_variants.json"
const LEVELS_PATH := "res://data/levels.json"
const HAND_BUILT := 20
const G := 640.0
const STABILITY_FRAMES := 180
const MAX_DRIFT := 3.0

## One row per mission, in play order (L21 first). [name, pattern, shots, par, difficulty 0..1, options]
const DESIGNS := [
	# Chapter 2: Glass Quarter — supply drops, bounce pads, glass.
	["Supply Run", "supply_shelf", 3, 1, 0.0, {}],
	["Mirror Hall", "glass_towers", 3, 1, 0.1, {}],
	["Bank Shot", "bumper_shield", 3, 1, 0.0, {}],
	["Tower Drop", "supply_tower", 3, 1, 0.1, {}],
	["Glass Stilts", "glass_stilts_supply", 3, 1, 0.2, {}],
	["Overpass", "bridge", 3, 1, 0.2, {}],
	["Shelf Life", "supply_shelf", 3, 1, 0.4, {}],
	["Prism", "glass_pyramid", 3, 1, 0.3, {}],
	["Ricochet", "bumper_shield", 3, 1, 0.4, {}],
	["Arcade", "topple_glass", 3, 1, 0.3, {}],
	["Courier", "supply_tower", 3, 1, 0.5, {}],
	["Twin Drops", "twin_supply", 3, 2, 0.3, {}],
	["Skybridge", "bridge", 3, 1, 0.6, {}],
	["Hall of Glass", "glass_towers", 3, 2, 0.6, {}],
	["Long Haul", "supply_shelf", 3, 1, 0.8, {}],
	["Reflection", "bumper_shield", 3, 1, 0.8, {}],
	["Stained Glass", "glass_pyramid", 3, 1, 0.7, {}],
	["Last Delivery", "twin_supply", 3, 2, 0.7, {}],
	["Mirrorfall", "topple_glass", 3, 2, 0.8, {}],
	["Glass Quarter", "glass_towers", 3, 2, 1.0, {}],
	# Chapter 3: The Quarry — explosive crates, heavy shot.
	["Powder Keg", "powder_keg", 3, 1, 0.0, {}],
	["Short Fuse", "chain_fuse", 3, 1, 0.0, {}],
	["Dead Weight", "stone_vault", 3, 1, 0.0, {"ammo": "heavy"}],
	["Blasting Cap", "quarry_stack", 3, 1, 0.1, {}],
	["Rockfall", "explosive_topple", 3, 1, 0.2, {}],
	["Long Fuse", "chain_fuse", 3, 1, 0.3, {}],
	["Air Mail", "blast_supply", 3, 1, 0.2, {}],
	["Bedrock", "heavy_wall", 3, 1, 0.3, {"ammo": "heavy"}],
	["Seam", "powder_keg", 3, 1, 0.4, {}],
	["Quarry Lift", "quarry_stack", 3, 1, 0.4, {}],
	["Slag Heap", "explosive_topple", 3, 2, 0.5, {}],
	["Vault Door", "stone_vault", 3, 1, 0.5, {"ammo": "heavy"}],
	["Detonator", "chain_fuse", 3, 1, 0.6, {}],
	["Express Freight", "blast_supply", 3, 1, 0.6, {}],
	["Granite", "heavy_wall", 3, 1, 0.7, {"ammo": "heavy"}],
	["Powder Room", "powder_keg", 3, 1, 0.7, {}],
	["Fault Line", "explosive_topple", 3, 2, 0.8, {}],
	["Deep Cut", "quarry_stack", 3, 2, 0.8, {}],
	["Stone Heart", "stone_vault", 3, 2, 0.9, {"ammo": "heavy"}],
	["The Quarry", "chain_fuse", 3, 1, 1.0, {}],
	# Chapter 4: Juno's Kin — ally drones, blast shot.
	["First Rescue", "rescue_tower", 3, 1, 0.0, {}],
	["Steady Hands", "ally_ledge", 3, 1, 0.0, {}],
	["Breach", "blast_bunker", 3, 1, 0.0, {"ammo": "blast"}],
	["Safe Distance", "guarded_chain", 3, 1, 0.1, {}],
	["Lookout", "ally_pyramid", 3, 1, 0.2, {}],
	["Escort", "escort_supply", 3, 1, 0.2, {}],
	["Kin", "rescue_tower", 3, 1, 0.3, {}],
	["Ledge Walk", "ally_ledge", 3, 1, 0.4, {}],
	["Shaped Charge", "blast_bunker", 3, 1, 0.4, {"ammo": "blast"}],
	["Firebreak", "guarded_chain", 3, 1, 0.5, {}],
	["Watchtower", "ally_pyramid", 3, 1, 0.5, {}],
	["Lifeline", "escort_supply", 3, 1, 0.5, {}],
	["Cradle", "rescue_tower", 3, 2, 0.6, {}],
	["Bunker Hill", "blast_bunker", 3, 1, 0.6, {"ammo": "blast"}],
	["Perch", "ally_ledge", 3, 1, 0.7, {}],
	["Containment", "guarded_chain", 3, 1, 0.7, {}],
	["Sentinels", "ally_pyramid", 3, 2, 0.8, {}],
	["Homecoming", "escort_supply", 3, 1, 0.8, {}],
	["Surgical", "blast_bunker", 3, 2, 0.9, {"ammo": "blast"}],
	["Juno's Kin", "rescue_tower", 3, 2, 1.0, {}],
	# Chapter 5: The Spire — everything combined.
	["Approach", "spire", 3, 1, 0.0, {}],
	["Outer Wall", "heavy_wall", 3, 1, 0.8, {"ammo": "heavy", "ally": true}],
	["Gatehouse", "blast_bunker", 3, 1, 0.7, {"ammo": "blast", "ally": true}],
	["Supply Line", "blast_supply", 3, 1, 0.8, {"ally": true}],
	["Lower Spire", "spire", 3, 1, 0.2, {}],
	["Cascade", "chain_fuse", 3, 1, 0.9, {"ally": true}],
	["Glass Ward", "glass_towers", 3, 2, 0.9, {"ally": true}],
	["Counterweight", "stone_vault", 3, 1, 0.8, {"ammo": "heavy", "ally": true}],
	["Mid Spire", "spire", 3, 2, 0.4, {"ammo": "mixed"}],
	["Bank Vault", "bumper_shield", 3, 1, 1.0, {"ally": true}],
	["Overload", "powder_keg", 3, 1, 1.0, {"ally": true}],
	["Last Crate", "escort_supply", 3, 1, 1.0, {}],
	["High Spire", "spire", 3, 2, 0.6, {"ammo": "mixed"}],
	["Fallen Bridge", "bridge", 3, 1, 1.0, {"ally": true}],
	["Pressure", "quarry_stack", 3, 2, 1.0, {"ally": true}],
	["Collapse Protocol", "explosive_topple", 3, 2, 1.0, {}],
	["Crown", "spire", 3, 2, 0.8, {"ammo": "mixed"}],
	["Guardians", "ally_pyramid", 3, 2, 1.0, {}],
	["The Heart Gate", "blast_bunker", 3, 2, 1.0, {"ammo": "blast", "ally": true}],
	["The Heart", "spire", 3, 2, 1.0, {"ammo": "mixed", "ally": true}],
]


func _initialize() -> void:
	_run.call_deferred()


func _run() -> void:
	var args := OS.get_cmdline_user_args()
	var variants: Dictionary = _load_json(VARIANTS_PATH, {})
	var data: Dictionary = _load_json(LEVELS_PATH, {"levels": []})
	var existing := {}
	for l: Dictionary in data.levels:
		existing[l.id] = l

	for a in args:
		if a.begins_with("--merge="):
			_merge(a.trim_prefix("--merge=").split(","), existing, variants)

	var levels: Array = data.levels.slice(0, HAND_BUILT)
	var campaign := _build_all(variants, existing)
	if args.has("--check"):
		var unstable: Array = await _check_stability(campaign)
		for id: String in unstable:
			variants[id] = int(variants.get(id, 0)) + 1
		if not unstable.is_empty():
			print("unstable, new variants: ", unstable)
			campaign = _build_all(variants, existing)
	levels.append_array(campaign)
	data.levels = levels
	_save_text(LEVELS_PATH, CatalogFormat.format_catalog(data))
	_save_text(VARIANTS_PATH, JSON.stringify(variants, "\t", true) + "\n")
	var solved := campaign.filter(func(l: Dictionary) -> bool: return not l.solution.is_empty()).size()
	print("campaign: %d levels, %d with solutions, %d need solving" % [campaign.size(), solved, campaign.size() - solved])
	var pending := campaign.filter(func(l: Dictionary) -> bool: return l.solution.is_empty()).map(func(l: Dictionary) -> String: return l.id)
	print("PENDING ", " ".join(pending))
	quit(0)


func _build_all(variants: Dictionary, existing: Dictionary) -> Array:
	var out := []
	for i in DESIGNS.size():
		var id := "L%d" % (HAND_BUILT + 1 + i)
		var level := _build(id, DESIGNS[i], int(variants.get(id, 0)))
		# Keep a stored solution only while the level is unchanged.
		var old: Dictionary = existing.get(id, {})
		if not old.is_empty() and _same_layout(old, level):
			level.solution = old.solution
		out.append(level)
	return out


func _same_layout(a: Dictionary, b: Dictionary) -> bool:
	# Round-trip both through JSON so ints and floats (180 vs 180.0) compare equal.
	var x: Dictionary = JSON.parse_string(JSON.stringify(a))
	var y: Dictionary = JSON.parse_string(JSON.stringify(b))
	# Text changes (name, hint) don't affect physics, so they keep the stored solution.
	for key in ["solution", "name", "hint"]:
		x.erase(key)
		y.erase(key)
	return JSON.stringify(x, "", true) == JSON.stringify(y, "", true)


## Solver results: solved levels get their solutions; unsolved ones move to the next variant.
func _merge(paths: PackedStringArray, existing: Dictionary, variants: Dictionary) -> void:
	for path in paths:
		var result: Dictionary = _load_json(path, {})
		for id: String in result.get("solved", {}):
			if existing.has(id):
				existing[id].solution = result.solved[id]
		for id: String in result.get("unsolved", []):
			variants[id] = int(variants.get(id, 0)) + 1
		print("merged %s: %d solved, %d unsolved" % [path, result.get("solved", {}).size(), result.get("unsolved", []).size()])


# --- Building ---------------------------------------------------------------------------------

func _build(id: String, design: Array, variant: int) -> Dictionary:
	var rng := RandomNumberGenerator.new()
	rng.seed = hash(id) + 7919 * variant
	var b := Builder.new()
	b.rng = rng
	var opts: Dictionary = design[5]
	var d: float = design[4]
	var extra: Dictionary = call("_p_" + design[1], b, d)
	if opts.get("ally", false) and b.allies.is_empty():
		b.add_far_ally()
	var level := {
		"id": id, "name": design[0], "shots": design[2], "par": design[3],
		"hint": extra.get("hint", ""),
		"launcher": [180, 540],
		"objective": extra.get("objective", {"type": "destroy_targets"}),
		"statics": b.statics, "blocks": b.blocks, "targets": b.targets,
		"solution": [],
	}
	var ammo: String = opts.get("ammo", "")
	if ammo == "mixed":
		level.ammo = ["heavy", "blast", "standard"]
	elif ammo != "":
		level.ammo = [ammo, ammo, ammo]
	if not b.allies.is_empty():
		level.allies = b.allies
	return level


## Small geometry helpers. Every dynamic piece rests on the ground (y = 640) or on another piece.
class Builder:
	var rng: RandomNumberGenerator
	var statics := []
	var blocks := []
	var targets := []
	var allies := []

	func jitter(amount: float) -> float:
		return roundf(rng.randf_range(-amount, amount))

	## A block standing on `base`; returns its top y.
	func block(x: float, base: float, w: float, h: float, mat: String) -> float:
		blocks.append({"x": roundf(x), "y": base - h / 2.0, "w": w, "h": h, "material": mat})
		return base - h

	func wall(x: float, y: float, w: float, h: float, kind: String = "wall") -> void:
		var s := {"x": roundf(x), "y": roundf(y), "w": w, "h": h}
		if kind != "wall":
			s.kind = kind
		statics.append(s)

	## A static ledge whose top surface is at `top`; returns `top`.
	func ledge(x: float, top: float, w: float) -> float:
		wall(x, top + 10.0, w, 20.0)
		return top

	func core(x: float, base: float, r: float) -> void:
		targets.append({"x": roundf(x), "y": base - r, "r": r})

	func ally(x: float, base: float, r: float = 18.0) -> void:
		allies.append({"x": roundf(x), "y": base - r, "r": r})

	## Two columns and a slab; returns the slab's top y.
	func tower(x: float, base: float, span: float, col_h: float, col_mat: String, slab_mat: String, col_w: float = 20.0) -> float:
		block(x - span / 2.0 + col_w / 2.0, base, col_w, col_h, col_mat)
		block(x + span / 2.0 - col_w / 2.0, base, col_w, col_h, col_mat)
		return block(x, base - col_h, span, 20.0, slab_mat)

	func pyramid(x: float, base: float, rows: int, size: float, mat: String) -> float:
		var top := base
		for row in rows:
			var count := rows - row
			for i in count:
				block(x + (i - (count - 1) / 2.0) * size, top, size, size, mat)
			top -= size
		return top

	## A drone on a static perch at the far right, well away from the action.
	func add_far_ally() -> void:
		var top := ledge(1200.0, 470.0 + jitter(30.0), 90.0)
		ally(1200.0, top)


# --- Patterns: each fills the builder and returns {objective?, hint} --------------------------

func _zone(x: float, w: float, top: float = G) -> Dictionary:
	return {"type": "deliver", "zone": {"x": roundf(x), "y": top - 45.0, "w": w, "h": 90}}


func _p_supply_shelf(b: Builder, d: float) -> Dictionary:
	var x := 640.0 + b.jitter(40.0) + 60.0 * d
	# Low shelf and a big crate early on: a floating crate is a thin target, so most shots would miss it.
	var top := b.ledge(x, 570.0 - 160.0 * d + b.jitter(10.0), 120.0)
	var crate := 56.0 - 12.0 * d
	b.block(x, top, crate, crate, "cargo")
	# Wide zone starting near the ledge: knocked crates scatter, so a narrow zone needs pixel aim.
	return {"objective": _zone(x + 150.0 + 70.0 * d, 300.0 - 80.0 * d), "hint": "Knock the supply crate into the drop zone."}


func _p_supply_tower(b: Builder, d: float) -> Dictionary:
	var x := 760.0 + b.jitter(40.0)
	var top := b.tower(x, G, 120.0, 100.0 + 40.0 * d, "wood", "wood")
	if d > 0.4:
		top = b.tower(x, top, 100.0, 80.0, "wood", "wood")
	b.block(x, top, 40.0, 40.0, "cargo")
	return {"objective": _zone(x + 190.0 + 40.0 * d, 170.0 - 30.0 * d), "hint": "Bring the tower down so the crate lands in the zone."}


func _p_glass_stilts_supply(b: Builder, d: float) -> Dictionary:
	var x := 820.0 + b.jitter(40.0)
	var top := b.tower(x, G, 110.0, 120.0 + 50.0 * d, "glass", "wood")
	b.block(x, top, 40.0, 40.0, "cargo")
	return {"objective": _zone(x + 20.0, 220.0 - 60.0 * d), "hint": "Glass legs. Break them and the crate drops."}


func _p_twin_supply(b: Builder, d: float) -> Dictionary:
	var x1 := 600.0 + b.jitter(30.0)
	var x2 := 820.0 + b.jitter(30.0)
	b.block(x1, b.ledge(x1, 500.0 - 60.0 * d, 100.0), 40.0, 40.0, "cargo")
	b.block(x2, b.ledge(x2, 440.0 - 80.0 * d, 100.0), 40.0, 40.0, "cargo")
	return {"objective": _zone(1020.0, 260.0 - 40.0 * d), "hint": "Two crates, one zone."}


func _p_glass_towers(b: Builder, d: float) -> Dictionary:
	var count := 2 if d < 0.5 else 3
	for i in count:
		var x := 640.0 + i * 190.0 + b.jitter(20.0)
		var top := b.tower(x, G, 90.0, 90.0 + 40.0 * d + b.jitter(10.0), "glass", "glass" if i % 2 == 0 else "wood")
		b.core(x, top, 20.0)
	return {"hint": "Glass breaks. Cores fall."}


func _p_glass_pyramid(b: Builder, d: float) -> Dictionary:
	var x := 860.0 + b.jitter(40.0)
	var top := b.pyramid(x, G, 3 if d < 0.5 else 4, 50.0, "glass")
	b.core(x, top, 22.0)
	if d > 0.5:
		b.core(x + 140.0, G, 22.0)
	return {"hint": "A pyramid of glass. Find the keystone."}


func _p_bumper_shield(b: Builder, d: float) -> Dictionary:
	var shield_x := 760.0 + b.jitter(20.0)
	b.block(shield_x, G, 40.0, 160.0 + 100.0 * d, "stone")
	var core_x := shield_x + 120.0 + b.jitter(20.0)
	b.core(core_x, G, 24.0 - 4.0 * d)
	b.wall(shield_x + 60.0, 230.0 - 40.0 * d, 360.0, 20.0, "bumper")
	return {"hint": "The purple pad bounces. Bank the shot over the shield."}


func _p_bridge(b: Builder, d: float) -> Dictionary:
	var x := 820.0 + b.jitter(30.0)
	var gap := 200.0 + 60.0 * d
	var pillar_h := 140.0 + 60.0 * d
	b.wall(x - gap / 2.0, G - pillar_h / 2.0, 40.0, pillar_h)
	b.wall(x + gap / 2.0, G - pillar_h / 2.0, 40.0, pillar_h)
	var deck := b.block(x, G - pillar_h, gap + 40.0, 20.0, "wood")
	b.core(x - 50.0, deck, 20.0)
	b.core(x + 50.0, deck, 20.0)
	return {"hint": "Knock both cores off the bridge."}


func _p_topple_glass(b: Builder, d: float) -> Dictionary:
	var x := 760.0
	for i in 3 + int(d * 2.0):
		var h := 120.0 + 30.0 * (i % 2) + 40.0 * d
		b.block(x + i * 70.0, G, 24.0, h, "glass" if i % 2 == 0 else "wood")
	return {"objective": {"type": "topple", "line_y": 560}, "hint": "Bring every pane below the line."}


func _p_powder_keg(b: Builder, d: float) -> Dictionary:
	var x := 860.0 + b.jitter(30.0)
	b.block(x - 90.0, G, 40.0, 40.0, "explosive")
	var top := b.tower(x, G, 120.0, 110.0 + 30.0 * d, "wood", "stone" if d > 0.5 else "wood")
	if d > 0.6:
		top = b.tower(x, top, 100.0, 80.0, "wood", "wood")
	b.core(x, top, 20.0)
	return {"hint": "Orange crates explode. Light the fuse."}


func _p_chain_fuse(b: Builder, d: float) -> Dictionary:
	var n := 2 + int(d * 3.0)
	var x := 560.0
	var spacing := 120.0 + 20.0 * d
	for i in n:
		b.block(x + i * spacing, G, 36.0, 36.0, "explosive")
	var end := x + (n - 1) * spacing + 90.0
	var top := b.tower(end, G, 80.0, 60.0 + 40.0 * d, "stone", "stone")
	b.core(end, top, 18.0)
	return {"hint": "Set off the first crate and let the chain do the rest."}


func _p_stone_vault(b: Builder, d: float) -> Dictionary:
	var x := 860.0 + b.jitter(30.0)
	var h := 90.0 + 30.0 * d
	b.block(x - 60.0, G, 30.0, h, "stone")
	b.block(x + 60.0, G, 30.0, h, "stone")
	b.block(x, G - h, 160.0, 24.0, "stone")
	b.core(x, G, 22.0)
	if d > 0.8:
		b.core(x + 160.0, G, 20.0)
	return {"hint": "Stone. A heavy shot hits harder."}


func _p_heavy_wall(b: Builder, d: float) -> Dictionary:
	var x := 820.0 + b.jitter(30.0)
	b.block(x, G, 50.0, 150.0 + 70.0 * d, "stone")
	b.core(x + 70.0, G, 22.0)
	return {"hint": "Push the stone slab onto the core."}


func _p_quarry_stack(b: Builder, d: float) -> Dictionary:
	var x := 880.0 + b.jitter(30.0)
	var floor1 := b.tower(x, G, 140.0, 100.0, "stone", "wood")
	b.block(x, G, 36.0, 36.0, "explosive")
	var floor2 := b.tower(x, floor1, 120.0, 90.0, "wood", "stone" if d > 0.5 else "wood")
	b.core(x, floor2, 20.0)
	if d > 0.7:
		# Centred: the upper floor's columns stand at ±50 on this slab.
		b.core(x, floor1, 18.0)
	return {"hint": "A charge sits in the foundations."}


func _p_explosive_topple(b: Builder, d: float) -> Dictionary:
	var x := 780.0
	for i in 3 + int(d * 2.0):
		b.block(x + i * 80.0, G, 30.0, 140.0 + 30.0 * d, "stone")
	b.block(x + 40.0, G, 34.0, 34.0, "explosive")
	if d > 0.5:
		b.block(x + 200.0, G, 34.0, 34.0, "explosive")
	return {"objective": {"type": "topple", "line_y": 550}, "hint": "Bring every column below the line."}


func _p_blast_supply(b: Builder, d: float) -> Dictionary:
	var x := 700.0 + b.jitter(30.0)
	var top := b.ledge(x, 520.0 - 60.0 * d, 160.0)
	b.block(x - 40.0, top, 36.0, 36.0, "explosive")
	b.block(x + 30.0, top, 40.0, 40.0, "cargo")
	return {"objective": _zone(x + 260.0 + 60.0 * d, 200.0 - 40.0 * d), "hint": "Let the blast throw the crate into the zone."}


func _p_rescue_tower(b: Builder, d: float) -> Dictionary:
	var x := 860.0 + b.jitter(30.0)
	var top := b.tower(x, G, 120.0, 110.0 + 30.0 * d, "wood", "wood")
	if d > 0.5:
		top = b.tower(x, top, 100.0, 80.0, "wood", "wood")
	b.core(x, top, 20.0)
	b.ally(x - 200.0 + b.jitter(10.0), G)
	if d > 0.8:
		b.ally(x + 220.0, G)
	return {"hint": "Blue drones are friends. Don't break them."}


func _p_ally_ledge(b: Builder, d: float) -> Dictionary:
	var x := 760.0 + b.jitter(30.0)
	var top := b.ledge(x, 470.0 - 60.0 * d, 200.0)
	b.core(x + 50.0, top, 20.0 - 2.0 * d)
	b.ally(x - 60.0, top)
	return {"hint": "Precision: the drone shares the ledge."}


func _p_blast_bunker(b: Builder, d: float) -> Dictionary:
	var x := 860.0 + b.jitter(30.0)
	var h := 100.0 + 30.0 * d
	b.block(x - 70.0, G, 30.0, h, "stone")
	b.block(x + 70.0, G, 30.0, h, "stone")
	b.block(x, G - h, 180.0, 24.0, "stone")
	b.core(x, G, 22.0)
	b.ally(x - 260.0, G)
	return {"hint": "Blast shots explode on contact. Keep them away from the drone."}


func _p_guarded_chain(b: Builder, d: float) -> Dictionary:
	var n := 2 + int(d * 2.0)
	for i in n:
		b.block(620.0 + i * 120.0, G, 36.0, 36.0, "explosive")
	var end := 620.0 + (n - 1) * 120.0 + 90.0
	b.core(end, G, 20.0)
	var perch := b.ledge(560.0, 360.0, 80.0)
	b.ally(560.0, perch)
	return {"hint": "A chain reaction, but the drone above must stay clear."}


func _p_ally_pyramid(b: Builder, d: float) -> Dictionary:
	var x := 820.0 + b.jitter(30.0)
	var top := b.pyramid(x, G, 3, 50.0, "wood")
	b.core(x, top, 20.0)
	b.ally(x + 230.0 + b.jitter(10.0), G)
	if d > 0.7:
		b.core(x + 120.0, G, 18.0)
	return {"hint": "Topple the pyramid away from the drone."}


func _p_escort_supply(b: Builder, d: float) -> Dictionary:
	var x := 660.0 + b.jitter(30.0)
	var top := b.ledge(x, 560.0 - 110.0 * d, 120.0)
	b.block(x, top, 52.0, 52.0, "cargo")
	var zone_x := x + 160.0 + 50.0 * d
	var zone_w := 280.0 - 60.0 * d
	b.ally(zone_x + zone_w / 2.0 + 110.0, G)
	return {"objective": _zone(zone_x, zone_w), "hint": "Deliver the crate. Mind the drone beside the zone."}


func _p_spire(b: Builder, d: float) -> Dictionary:
	var x := 900.0 + b.jitter(20.0)
	var floors := 2 + int(d * 2.0)
	var top := G
	var mats := ["stone", "wood", "glass", "wood"]
	b.block(x - 100.0, G, 36.0, 36.0, "explosive")
	for f in floors:
		var span := 150.0 - f * 16.0
		top = b.tower(x, top, span, 90.0 - f * 6.0, mats[f % mats.size()], "wood" if f < floors - 1 else "stone")
		if f % 2 == 1 or f == floors - 1:
			# Centred, between the next floor's columns.
			b.core(x, top, 18.0)
	return {"hint": "The spire. Cores hide between its floors."}


# --- Stability check ----------------------------------------------------------------------------

## Simulates every level for STABILITY_FRAMES with no shot. Returns ids that drift or lose a core/ally.
func _check_stability(levels: Array) -> Array:
	var runs := []
	for level: Dictionary in levels:
		var def := LevelDefinition.from_dict(level)
		if not def.is_valid():
			printerr("%s invalid: %s" % [level.id, ", ".join(def.errors)])
			continue
		var viewport := SubViewport.new()
		viewport.render_target_update_mode = SubViewport.UPDATE_DISABLED
		root.add_child(viewport)
		var session := GameSession.new()
		viewport.add_child(session)
		session.setup(def)
		runs.append({"id": level.id, "viewport": viewport, "session": session, "start": _positions(session)})
	for i in STABILITY_FRAMES:
		await physics_frame
	var bad := []
	for run: Dictionary in runs:
		var now := _positions(run.session)
		var drift := 0.0
		if now.size() != run.start.size():
			drift = INF
		else:
			for k in now.size():
				drift = maxf(drift, now[k].distance_to(run.start[k]))
		if drift > MAX_DRIFT:
			bad.append(run.id)
			print("%s drifted %.1f px" % [run.id, drift])
		run.viewport.queue_free()
	await process_frame
	return bad


func _positions(session: GameSession) -> Array:
	var list := []
	for node in session.get_child(0).get_children():
		if node is RigidBody2D:
			list.append(node.global_position)
	return list


func _load_json(path: String, fallback: Variant) -> Variant:
	if not FileAccess.file_exists(path):
		return fallback
	var parsed: Variant = JSON.parse_string(FileAccess.get_file_as_string(path))
	return parsed if parsed != null else fallback


func _save_text(path: String, text: String) -> void:
	var file := FileAccess.open(path, FileAccess.WRITE)
	if file == null:
		printerr("cannot write ", path)
		return
	file.store_string(text)
