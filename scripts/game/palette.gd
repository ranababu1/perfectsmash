class_name Palette
extends RefCounted
## Shared visual colors. High-contrast roles: background, structure, projectile, objective.

const SKY_TOP := Color("1b2133")
const SKY_BOTTOM := Color("2c3550")
const GROUND := Color("3b4560")
const GROUND_EDGE := Color("56627f")
const STATIC := Color("4a5572")
const STATIC_EDGE := Color("6b7896")
const WOOD := Color("d9954a")
const WOOD_EDGE := Color("8f5a24")
const STONE := Color("8c9bb0")
const STONE_EDGE := Color("566377")
const GLASS := Color(0.55, 0.88, 1.0, 0.45)
const GLASS_EDGE := Color("bff0ff")
const TARGET := Color("ff4f6d")
const TARGET_EDGE := Color("ffd3db")
const PROJECTILE := Color("ffe08a")
const PROJECTILE_EDGE := Color("fff6d6")
const AIM := Color(1, 1, 1, 0.85)
const TOPPLE_LINE := Color("7cf0a8")
const TEXT := Color("f2f4f8")
const TEXT_DIM := Color("a8b0c4")
const ACCENT := Color("ffe08a")


static func material_fill(material_kind: String) -> Color:
	match material_kind:
		"stone":
			return STONE
		"glass":
			return GLASS
	return WOOD


static func material_edge(material_kind: String) -> Color:
	match material_kind:
		"stone":
			return STONE_EDGE
		"glass":
			return GLASS_EDGE
	return WOOD_EDGE
