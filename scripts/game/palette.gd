class_name Palette
extends RefCounted
## Shared visual colors. High-contrast roles: background, structure, projectile, objective.
## The UI is a calm, low-saturation navy so the warm game pieces carry the attention.

const SKY_TOP := Color("121626")
const SKY_BOTTOM := Color("2a3252")
const HORIZON_GLOW := Color(0.55, 0.6, 0.95, 0.10)
const HILLS_FAR := Color("1f2640")
const HILLS_NEAR := Color("1a2036")
const GROUND := Color("161b2c")
const GROUND_EDGE := Color("3c4668")
const STATIC := Color("3a4462")
const STATIC_EDGE := Color("58648a")
const WOOD := Color("d99a52")
const WOOD_EDGE := Color("9a632c")
const STONE := Color("8d9bb2")
const STONE_EDGE := Color("5c697f")
const GLASS := Color(0.55, 0.88, 1.0, 0.35)
const GLASS_EDGE := Color("bdefff")
const TARGET := Color("ff5470")
const TARGET_EDGE := Color("ffd0d9")
const EXPLOSIVE := Color("ff7a3d")
const EXPLOSIVE_EDGE := Color("ffd0a8")
const CARGO := Color("4fc79a")
const CARGO_EDGE := Color("c4f5df")
const DROP_ZONE := Color("6ff0bd")
const ALLY := Color("4fb2ff")
const ALLY_EDGE := Color("d4ecff")
const BUMPER := Color("a678ff")
const BUMPER_EDGE := Color("e0d0ff")
const BLAST := Color("ffb25e")
const HEAVY := Color("c3cad8")
const HEAVY_EDGE := Color("eef1f8")
const PROJECTILE := Color("ffe08a")
const PROJECTILE_EDGE := Color("fff6d6")
const AIM := Color(1, 1, 1, 0.85)
const TOPPLE_LINE := Color("7cf0a8")
const TEXT := Color("eef1f8")
const TEXT_DIM := Color("98a1ba")
const TEXT_FAINT := Color("5d6684")
const ACCENT := Color("ffe08a")
const ACCENT_INK := Color("1d2234")

# UI surfaces
const SURFACE := Color(0.08, 0.10, 0.16, 0.94)
const SURFACE_RAISED := Color(1, 1, 1, 0.06)
const SURFACE_HOVER := Color(1, 1, 1, 0.10)
const SURFACE_PRESSED := Color(1, 1, 1, 0.03)
const BORDER := Color(1, 1, 1, 0.08)
const SCRIM := Color(0.03, 0.04, 0.08, 0.6)
const SHADOW := Color(0, 0, 0, 0.35)


static func material_fill(material_kind: String) -> Color:
	match material_kind:
		"stone":
			return STONE
		"glass":
			return GLASS
		"explosive":
			return EXPLOSIVE
		"cargo":
			return CARGO
	return WOOD


static func material_edge(material_kind: String) -> Color:
	match material_kind:
		"stone":
			return STONE_EDGE
		"glass":
			return GLASS_EDGE
		"explosive":
			return EXPLOSIVE_EDGE
		"cargo":
			return CARGO_EDGE
	return WOOD_EDGE


## Ball colors per ammo type: [fill, edge].
static func ammo_colors(ammo: String) -> Array[Color]:
	match ammo:
		"heavy":
			return [HEAVY, HEAVY_EDGE]
		"blast":
			return [BLAST, EXPLOSIVE_EDGE]
	return [PROJECTILE, PROJECTILE_EDGE]
