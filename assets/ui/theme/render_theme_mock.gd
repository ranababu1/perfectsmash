extends SceneTree
## Renders one mock screen with tfj_theme.tres applied (integration stream, 2026-11-10): the main menu
## backdrop under the theme scrim, a modal mission briefing with type roles, tabs, chips, progress bars,
## a slider, a toggle and the four button styles. Needs a display (xvfb) for the 2D renderer:
##   xvfb-run -a -s "-screen 0 1280x720x24" godot --path <project> --rendering-driver opengl3 \
##     --resolution 1280x720 --script res://assets/ui/theme/render_theme_mock.gd -- <out.png>
## Text is placeholder copy drawn as Labels and Buttons; nothing is baked into the kit textures.

const THEME := "res://assets/ui/theme/tfj_theme.tres"
const BG := "res://assets/ui/backgrounds/ui_bg_main_menu_1280x720.webp"
const ICON := "res://assets/ui/icons/png_1x/gam_icn_info_a.png"


func _init() -> void:
	var out: String = OS.get_cmdline_user_args()[0]
	var theme: Theme = load(THEME)
	var ui := Control.new()
	ui.theme = theme
	ui.size = Vector2(1280, 720)
	get_root().add_child(ui)
	var bg := TextureRect.new()
	bg.texture = load(BG)
	bg.size = Vector2(1280, 720)
	bg.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
	ui.add_child(bg)
	var scrim := ColorRect.new()
	scrim.color = theme.get_color("scrim", "TFJ")
	scrim.size = Vector2(1280, 720)
	ui.add_child(scrim)

	var modal := PanelContainer.new()
	modal.theme_type_variation = "PanelModal"
	modal.position = Vector2(250, 70)
	modal.custom_minimum_size = Vector2(780, 0)
	ui.add_child(modal)
	var col := VBoxContainer.new()
	col.add_theme_constant_override("separation", theme.get_constant("spacing_m", "TFJ"))
	modal.add_child(col)

	var header := PanelContainer.new()
	header.theme_type_variation = "PanelHeader"
	col.add_child(header)
	var hrow := HBoxContainer.new()
	header.add_child(hrow)
	var caps := _label("Chapter I  /  Helix Systems", "LabelLabelCaps", true)
	caps.add_theme_color_override("font_color", theme.get_color("cyan", "TFJ"))
	caps.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	hrow.add_child(caps)
	var chip := PanelContainer.new()
	chip.theme_type_variation = "Chip"
	chip.add_child(_label("Level 04", "LabelCaption", false))
	hrow.add_child(chip)

	col.add_child(_label("Mission briefing", "LabelTitle", true))
	var tabs := TabBar.new()
	for t in ["OBJECTIVES", "LOADOUT", "INTEL"]:
		tabs.add_tab(t)
	tabs.current_tab = 0
	tabs.custom_minimum_size.y = 48
	col.add_child(tabs)

	var inset := PanelContainer.new()
	inset.theme_type_variation = "PanelInset"
	col.add_child(inset)
	var grid := VBoxContainer.new()
	grid.add_theme_constant_override("separation", theme.get_constant("spacing_s", "TFJ"))
	inset.add_child(grid)
	var body := _label("Collapse the relay deck onto the AI core. Keep collateral below the oversight threshold.", "LabelBody", false)
	body.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	body.custom_minimum_size.x = 680
	grid.add_child(body)
	for row in [["Weapon energy", "ProgressBarEnergy", 72.0], ["Core integrity", "ProgressBarIntegrity", 38.0], ["Research", "", 55.0]]:
		var r := HBoxContainer.new()
		var l := _label(row[0], "LabelCaption", false)
		l.custom_minimum_size.x = 200
		r.add_child(l)
		var bar := ProgressBar.new()
		bar.theme_type_variation = row[1]
		bar.show_percentage = false
		bar.value = row[2]
		bar.custom_minimum_size = Vector2(440, 12)
		bar.size_flags_vertical = Control.SIZE_SHRINK_CENTER
		r.add_child(bar)
		grid.add_child(r)
	var settings := HBoxContainer.new()
	settings.add_theme_constant_override("separation", theme.get_constant("spacing_l", "TFJ"))
	var ml := _label("Music", "LabelLabelCaps", true)
	settings.add_child(ml)
	var slider := HSlider.new()
	slider.value = 65
	slider.custom_minimum_size = Vector2(260, 40)
	settings.add_child(slider)
	var toggle := CheckButton.new()
	toggle.text = "Haptics"
	toggle.button_pressed = true
	settings.add_child(toggle)
	grid.add_child(settings)

	var buttons := HBoxContainer.new()
	buttons.add_theme_constant_override("separation", theme.get_constant("spacing_m", "TFJ"))
	buttons.alignment = BoxContainer.ALIGNMENT_END
	var info := Button.new()
	info.theme_type_variation = "IconButton"
	info.icon = load(ICON)
	info.custom_minimum_size = Vector2(64, 64)
	buttons.add_child(info)
	for b in [["ABORT", "DangerButton"], ["LOADOUT", ""], ["DEPLOY", "PrimaryButton"]]:
		var btn := Button.new()
		btn.text = b[0]
		btn.theme_type_variation = b[1]
		btn.custom_minimum_size = Vector2(176, 56)
		buttons.add_child(btn)
	col.add_child(buttons)

	for i in 8:
		await process_frame
	var img := get_root().get_texture().get_image()
	img.save_png(out)
	print("THEMEMOCK saved %s %dx%d" % [out, img.get_width(), img.get_height()])
	quit()


func _label(text: String, variation: String, upper: bool) -> Label:
	var l := Label.new()
	l.text = text
	l.theme_type_variation = variation
	l.uppercase = upper
	return l
