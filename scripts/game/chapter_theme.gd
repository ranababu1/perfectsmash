class_name ChapterTheme
extends RefCounted
## Scenery colours for one chapter environment (sky, horizon glow, hills, ground). Interactive pieces
## (blocks, targets, projectile, aim) keep their shared Palette colours in every chapter so the
## puzzle reads the same everywhere. Scenery stays dark and low-contrast behind the structures,
## following docs/visual-audio-production-guide.md.

const DEFAULT_KEY := "default"

var key := DEFAULT_KEY
var sky_top := Palette.SKY_TOP
var sky_bottom := Palette.SKY_BOTTOM
var horizon_glow := Palette.HORIZON_GLOW
var hills_far := Palette.HILLS_FAR
var hills_near := Palette.HILLS_NEAR
var ground := Palette.GROUND
var ground_edge := Palette.GROUND_EDGE

## key -> [sky_top, sky_bottom, horizon_glow, hills_far, hills_near, ground, ground_edge]
const THEMES := {
	# Helix: steel and glass, cold cyan.
	"helix": ["0f1418", "25303a", Color(0.45, 0.75, 0.85, 0.08), "1b242c", "161d24", "12171c", "3a4a56"],
	# VITA: sterile teal / pale green.
	"vita": ["0f1615", "23302d", Color(0.55, 0.85, 0.75, 0.08), "1a2522", "151e1c", "111816", "3a504a"],
	# Nova Grid: dark steel with restrained amber.
	"nova_grid": ["141210", "2d2721", Color(0.95, 0.65, 0.3, 0.07), "231e19", "1c1814", "15120f", "54473a"],
	# Civitas: desaturated blue-grey city light.
	"civitas": ["111419", "292e36", Color(0.75, 0.8, 0.9, 0.07), "20242b", "1a1e24", "14171c", "464e5a"],
	# Meridian: near-black charcoal, deep cyan.
	"meridian": ["0b0e11", "1b2328", Color(0.25, 0.65, 0.75, 0.08), "151b1f", "111619", "0e1215", "34424a"],
}


static func for_key(theme_key: String) -> ChapterTheme:
	var theme := ChapterTheme.new()
	if not THEMES.has(theme_key):
		return theme
	var c: Array = THEMES[theme_key]
	theme.key = theme_key
	theme.sky_top = Color(c[0])
	theme.sky_bottom = Color(c[1])
	theme.horizon_glow = c[2]
	theme.hills_far = Color(c[3])
	theme.hills_near = Color(c[4])
	theme.ground = Color(c[5])
	theme.ground_edge = Color(c[6])
	return theme


static func has_key(theme_key: String) -> bool:
	return theme_key == DEFAULT_KEY or THEMES.has(theme_key)
