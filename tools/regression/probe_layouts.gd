extends RefCounted
## Helix layout variants for the design probes (rack-height comparison, Batch 5). Each variant
## edits a freshly loaded helix_01 definition in place; the shipped data is never changed.
##
## shipped       data/missions/helix_01.json as it is. Since the rack comparison (2026-11-10) this
##               is the chosen layout: racks 3-4 beside the right column (x 1030 / 1080) and racks
##               1-2 (40 x 100) beyond the relay mast (x 1262 / 1304), so the collapse zone is in
##               the kinetic line of fire and no single charge reaches all four racks
## one_bank      racks 1-2 at 40 x 100 next to racks 3-4 in one row behind the structure (one
##               charge there cleared all four racks and the relay mast)
## short_racks   racks 1-2 at 40 x 40 in front of the structure (the earlier test variant)
## tall_racks    racks 1-2 at 40 x 100 in front of the structure (the original layout)
## racks_70      racks 1-2 at 40 x 70 in front of the structure: a modest reduction
## core_plinth   tall_racks plus a static machinery plinth under the deck that
##               catches the deck and core part-way down, keeping the core above the racks
## shield_breaks tall_racks, core shield at half health (still stops kinetic fire
##               from the front for several rounds, but a collapse can break it)

const LAYOUTS := ["shipped", "one_bank", "short_racks", "tall_racks", "racks_70", "core_plinth", "shield_breaks"]
## Where racks 1-2 and 3-4 stood before the comparison (front cluster at x 650 / 698).
const ONE_BANK := {"rack_1": Vector2(1122, 560), "rack_2": Vector2(1164, 560), "rack_3": Vector2(1028, 560), "rack_4": Vector2(1072, 560)}
const FRONT_X := {"rack_1": 650.0, "rack_2": 698.0, "rack_3": 1030.0, "rack_4": 1080.0}


static func apply(def: MissionDefinition, layout: String) -> void:
	if layout == "shipped":
		return
	if layout == "one_bank":
		for c in def.components:
			if ONE_BANK.has(c.id):
				c.position = ONE_BANK[c.id]
		return
	for c in def.components:
		if FRONT_X.has(c.id):
			c.position = Vector2(FRONT_X[c.id], c.position.y)
		if c.id == "rack_1" or c.id == "rack_2":
			var height := _front_height(layout)
			c.size = Vector2(40, height)
			c.position = Vector2(c.position.x, 610.0 - height / 2.0)
		if layout == "shield_breaks" and c.id == "core_shield":
			c.health_scale = 0.5
	if layout == "core_plinth":
		# Plinth from the floor slab (top 610) up to 530: 80 px of machinery between the columns.
		def.statics.append({"position": Vector2(900, 570), "size": Vector2(90, 80), "rotation": 0.0})


static func _front_height(layout: String) -> float:
	return {"short_racks": 40.0, "racks_70": 70.0}.get(layout, 100.0)


## Same variants on the raw mission JSON (x, y, w, h keys), for tools that load a mission file.
static func apply_json(data: Dictionary, layout: String) -> void:
	if layout == "shipped":
		return
	if layout == "one_bank":
		for c: Dictionary in data.components:
			if ONE_BANK.has(c.id):
				c.x = ONE_BANK[c.id].x
				c.y = ONE_BANK[c.id].y
		return
	for c: Dictionary in data.components:
		if FRONT_X.has(c.id):
			c.x = FRONT_X[c.id]
		if c.id == "rack_1" or c.id == "rack_2":
			var height := _front_height(layout)
			c.h = height
			c.y = 610.0 - height / 2.0
		if layout == "shield_breaks" and c.id == "core_shield":
			c.health_scale = 0.5
	if layout == "core_plinth":
		data.statics.append({"x": 900, "y": 570, "w": 90, "h": 80})
