extends SceneTree
## Builds the Godot Theme resource generated_assets/ui/theme/tfj_theme.tres from tfj_theme_spec.json
## (integration stream, 2026-11-10). Godot 4.7.2. Run after an import so the kit textures and fonts load:
##   godot --headless --path <project> --script res://generated_assets/ui/theme/build_theme.gd
## What it maps (spec key -> Theme item):
## - default_font / default_font_size -> Theme.default_font / default_font_size.
## - theme.<Type>.styles.<name> (StyleBoxTexture, 1x texture + 1x margins, as the spec notes advise)
##   -> StyleBoxTexture with texture_margin_*, content_margin_*, expand_margin_* and axis stretch.
## - theme.<Type>.colors / font / font_size / constants (h_separation, icon_max_width) -> the same items.
## - spacing_glyph -> a FontVariation of the type's font (Theme fonts carry no letter spacing of their own).
## - base_type -> a type variation (PrimaryButton, DangerButton, IconButton, PanelInset, PanelModal,
##   PanelHeader, Chip); set Control.theme_type_variation to use one.
## - icons -> the 1x kit PNGs. The spec lists the 2x files with a 1x display size, but CheckButton and
##   HSlider draw their icons at texel size, so the 1x files give the 1x display size directly.
## - ProgressBar.variants -> ProgressBarEnergy, ProgressBarIntegrity and ProgressBarSuccess variations.
## - CheckButton -> empty boxes (otherwise it inherits the Button frame), toggle icons from the kit.
## - Tooltip -> TooltipPanel (panel) and TooltipLabel (font size).
## - type_roles -> Label type variations named Label<Role> (LabelDisplayXl, LabelTitle, LabelBody...);
##   "uppercase" cannot live in a Theme, so set Label.uppercase on those nodes.
## - colors, chapter accents, upgrade tiers and ScrimColor -> colours on the custom type "TFJ"
##   (theme.get_color("cyan", "TFJ"), "accent_vita", "tier2", "scrim").
## Not representable in a Theme (left to code): TextureProgressBar_Cooldown textures and fill mode,
## min_height / min_size / min_tab_height (use custom_minimum_size), hud_layout, damage_numbers, motion,
## flat_equivalents.

const SPEC := "res://generated_assets/ui/theme/tfj_theme_spec.json"
const OUT := "res://generated_assets/ui/theme/tfj_theme.tres"

var theme := Theme.new()
var font_cache := {}
var report := []


func _init() -> void:
	var spec: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(SPEC))
	theme.default_font = load(spec["default_font"])
	theme.default_font_size = int(spec["default_font_size"])
	for type_name: String in spec["theme"]:
		var item: Variant = spec["theme"][type_name]
		if type_name == "ScrimColor":
			theme.set_color("scrim", "TFJ", Color(String(item)))
			continue
		if type_name == "TextureProgressBar_Cooldown":
			report.append("skipped TextureProgressBar_Cooldown (node properties, not theme items)")
			continue
		var target := type_name
		if type_name == "Tooltip":
			_apply_styles("TooltipPanel", (item as Dictionary).get("styles", {}))
			if (item as Dictionary).has("font_size"):
				theme.set_font_size("font_size", "TooltipLabel", int(item["font_size"]))
			continue
		var d: Dictionary = item
		if d.has("base_type"):
			theme.set_type_variation(target, String(d["base_type"]))
		_apply_styles(target, d.get("styles", {}))
		for c: String in d.get("colors", {}):
			theme.set_color(c, target, Color(String(d["colors"][c])))
		if d.has("font"):
			theme.set_font("font", target, _font(String(d["font"]), float(d.get("spacing_glyph", 0.0))))
		if d.has("font_size"):
			theme.set_font_size("font_size", target, int(d["font_size"]))
		for k in ["h_separation", "icon_max_width"]:
			if d.has(k):
				theme.set_constant(k, target, int(d[k]))
		for icon_name: String in d.get("icons", {}):
			var path := String(d["icons"][icon_name]).replace("/png_2x/", "/png_1x/")
			theme.set_icon(icon_name, target, load(path))
	# CheckButton would inherit the Button boxes in this theme; the toggle art carries the state, so its
	# boxes are empty (text plus toggle icon, no frame).
	for st in ["normal", "hover", "pressed", "disabled", "hover_pressed", "focus"]:
		var e := StyleBoxEmpty.new()
		e.content_margin_left = 4.0; e.content_margin_right = 4.0
		e.content_margin_top = 4.0; e.content_margin_bottom = 4.0
		theme.set_stylebox(st, "CheckButton", e)
	theme.set_constant("icon_max_width", "CheckButton", 0)  # Button's 24 px cap would shrink the 64 x 32 toggle
	# ProgressBar variants (spec ProgressBar.variants): ProgressBarEnergy, ProgressBarIntegrity, ProgressBarSuccess.
	var pb: Dictionary = spec["theme"].get("ProgressBar", {})
	var fill: Dictionary = pb.get("styles", {}).get("fill", {})
	for variant: String in pb.get("variants", {}):
		var vname := "ProgressBar" + variant.to_pascal_case()
		theme.set_type_variation(vname, "ProgressBar")
		var vs := fill.duplicate(true)
		vs["texture"] = "res://generated_assets/ui/kit/png_1x/gam_ui_%s.png" % String(pb["variants"][variant])
		_apply_styles(vname, {"fill": vs})
	# Type roles as Label variations.
	for role: String in spec["type_roles"]:
		var r: Dictionary = spec["type_roles"][role]
		var vname := "Label" + role.to_pascal_case()
		theme.set_type_variation(vname, "Label")
		theme.set_font("font", vname, _font(String(r["font"]), float(r.get("spacing_glyph", 0.0))))
		theme.set_font_size("font_size", vname, int(r["size"]))
	# Palette on the custom type "TFJ".
	for c: String in spec["colors"]:
		theme.set_color(c, "TFJ", Color(String(spec["colors"][c])))
	for ch: String in spec["chapter_accents"]:
		var a: Dictionary = spec["chapter_accents"][ch]
		theme.set_color("accent_" + ch, "TFJ", Color(String(a["accent"])))
		theme.set_color("accent2_" + ch, "TFJ", Color(String(a["accent2"])))
		theme.set_color("base_" + ch, "TFJ", Color(String(a["base"])))
	for t: String in spec["upgrade_tiers"]:
		theme.set_color(t, "TFJ", Color(String(spec["upgrade_tiers"][t]["color"])))
	for s: String in spec["spacing"]:
		theme.set_constant("spacing_" + s, "TFJ", int(spec["spacing"][s]))
	theme.set_constant("safe_margin", "TFJ", int(spec["safe_margin"]))
	theme.set_constant("touch_target_min", "TFJ", int(spec["touch_target_min"]))
	var err := ResourceSaver.save(theme, OUT)
	var types := theme.get_type_list()
	print("THEME saved %s err=%d types=%d stylebox=%d color=%d font=%d icon=%d variations=%d" % [OUT, err, types.size(),
		_count(Theme.DATA_TYPE_STYLEBOX), _count(Theme.DATA_TYPE_COLOR), _count(Theme.DATA_TYPE_FONT),
		_count(Theme.DATA_TYPE_ICON), theme.get_type_variation_list("Button").size() + theme.get_type_variation_list("PanelContainer").size() + theme.get_type_variation_list("Label").size() + theme.get_type_variation_list("ProgressBar").size()])
	for line in report:
		print("THEME ", line)
	quit(0 if err == OK else 1)


func _count(data_type: int) -> int:
	var n := 0
	for t in theme.get_type_list():
		n += theme.get_theme_item_list(data_type, t).size()
	return n


func _font(path: String, spacing: float) -> Font:
	var key := "%s|%s" % [path, spacing]
	if font_cache.has(key):
		return font_cache[key]
	var base: FontFile = load(path)
	var f: Font = base
	if absf(spacing) > 0.001:
		var v := FontVariation.new()
		v.base_font = base
		v.spacing_glyph = roundi(spacing)
		f = v
	font_cache[key] = f
	return f


func _apply_styles(type_name: String, styles: Dictionary) -> void:
	for sname: String in styles:
		var s: Dictionary = styles[sname]
		if String(s.get("type", "")) != "StyleBoxTexture":
			report.append("skipped %s/%s type %s" % [type_name, sname, s.get("type")])
			continue
		var sb := StyleBoxTexture.new()
		sb.texture = load(String(s["texture"]))
		var tm: Dictionary = s.get("texture_margin", {})
		sb.texture_margin_left = float(tm.get("left", 0)); sb.texture_margin_top = float(tm.get("top", 0))
		sb.texture_margin_right = float(tm.get("right", 0)); sb.texture_margin_bottom = float(tm.get("bottom", 0))
		var cm: Dictionary = s.get("content_margin", {})
		if not cm.is_empty():
			sb.content_margin_left = float(cm.get("left", -1)); sb.content_margin_top = float(cm.get("top", -1))
			sb.content_margin_right = float(cm.get("right", -1)); sb.content_margin_bottom = float(cm.get("bottom", -1))
		var em: Dictionary = s.get("expand_margin", {})
		sb.expand_margin_left = float(em.get("left", 0)); sb.expand_margin_top = float(em.get("top", 0))
		sb.expand_margin_right = float(em.get("right", 0)); sb.expand_margin_bottom = float(em.get("bottom", 0))
		sb.axis_stretch_horizontal = _stretch(String(s.get("axis_stretch_horizontal", "stretch")))
		sb.axis_stretch_vertical = _stretch(String(s.get("axis_stretch_vertical", "stretch")))
		theme.set_stylebox(sname, type_name, sb)


func _stretch(v: String) -> StyleBoxTexture.AxisStretchMode:
	match v:
		"tile":
			return StyleBoxTexture.AXIS_STRETCH_MODE_TILE
		"tile_fit":
			return StyleBoxTexture.AXIS_STRETCH_MODE_TILE_FIT
	return StyleBoxTexture.AXIS_STRETCH_MODE_STRETCH
