class_name ChapterAtmosphere
extends RefCounted
## Lighting and atmosphere per chapter (data/atmospheres.json): background, ambient fill,
## reflection sky, depth fog, key sun and an accent rim light. MissionView applies it so each
## chapter reads as its own world while the camera, HUD and contrast rules stay the same.

const DEFAULT_PATH := "res://data/atmospheres.json"
const FALLBACK := "helix"

var theme := FALLBACK
var data := {}


## The atmosphere for a chapter theme ("helix", "vita", ...); unknown themes get Helix.
static func for_theme(chapter_theme: String, path: String = DEFAULT_PATH) -> ChapterAtmosphere:
	var atmosphere := ChapterAtmosphere.new()
	var all: Variant = JSON.parse_string(FileAccess.get_file_as_string(path)) if FileAccess.file_exists(path) else null
	if all is Dictionary:
		var key := chapter_theme if (all as Dictionary).has(chapter_theme) else FALLBACK
		atmosphere.theme = key
		atmosphere.data = (all as Dictionary).get(key, {})
	return atmosphere


static func themes(path: String = DEFAULT_PATH) -> Array[String]:
	var result: Array[String] = []
	var all: Variant = JSON.parse_string(FileAccess.get_file_as_string(path)) if FileAccess.file_exists(path) else null
	if all is Dictionary:
		for key: String in all:
			if not key.begins_with("_"):
				result.append(key)
	return result


func color(section: String, key: String, fallback: Color) -> Color:
	var value: Variant = (data.get(section, {}) as Dictionary).get(key) if section != "" else data.get(key)
	return Color(str(value)) if value is String and Color.html_is_valid(str(value)) else fallback


func number(section: String, key: String, fallback: float) -> float:
	var value: Variant = (data.get(section, {}) as Dictionary).get(key)
	return float(value) if value is float or value is int else fallback


## Configures a production-set environment (sky reflections + depth fog), as slice E did for Helix.
func apply_environment(env: Environment) -> void:
	env.background_color = color("", "background", Color("15191e"))
	env.ambient_light_color = color("ambient", "color", Color("6c7a88"))
	env.ambient_light_energy = number("ambient", "energy", 0.42)
	var sky_material := ProceduralSkyMaterial.new()
	sky_material.sky_top_color = color("sky", "top", Color("4a5866"))
	sky_material.sky_horizon_color = color("sky", "horizon", Color("8090a0"))
	sky_material.ground_horizon_color = color("sky", "ground_horizon", Color("3a4048"))
	sky_material.ground_bottom_color = color("sky", "ground_bottom", Color("1b2026"))
	var sky := Sky.new()
	sky.sky_material = sky_material
	env.sky = sky
	env.reflected_light_source = Environment.REFLECTION_SOURCE_SKY
	env.fog_light_color = color("fog", "color", Color("0e131a"))
	env.fog_density = number("fog", "density", 0.85)


func apply_sun(sun: DirectionalLight3D) -> void:
	sun.light_color = color("sun", "color", Color("dfe8f0"))
	sun.light_energy = number("sun", "energy", 1.0)
	sun.rotation_degrees = Vector3(number("sun", "pitch", -36.0), number("sun", "yaw", -30.0), 0.0)


## An unshadowed accent light from behind the facility, or null when the chapter has none.
func make_rim() -> DirectionalLight3D:
	var energy := number("rim", "energy", 0.0)
	if energy <= 0.0:
		return null
	var rim := DirectionalLight3D.new()
	rim.name = "RimLight"
	rim.light_color = color("rim", "color", Color.WHITE)
	rim.light_energy = energy
	rim.shadow_enabled = false
	# From behind and above the set, towards the camera, to edge-light silhouettes.
	rim.rotation_degrees = Vector3(-30.0, 160.0, 0.0)
	return rim
