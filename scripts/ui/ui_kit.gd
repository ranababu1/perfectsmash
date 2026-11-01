class_name UiKit
extends RefCounted
## Shared theme and widget factories. Touch targets are at least 72px tall on the 720px canvas.

const BUTTON_HEIGHT := 72.0
const CORNER := 14


static func make_theme() -> Theme:
	var theme := Theme.new()
	theme.default_font_size = 26
	theme.set_stylebox("normal", "Button", _box(Color("2f3a56")))
	theme.set_stylebox("hover", "Button", _box(Color("3d4a6c")))
	theme.set_stylebox("pressed", "Button", _box(Color("232b40")))
	theme.set_stylebox("disabled", "Button", _box(Color("222838")))
	var focus := _box(Color(0, 0, 0, 0))
	focus.border_color = Palette.ACCENT
	focus.set_border_width_all(3)
	theme.set_stylebox("focus", "Button", focus)
	theme.set_color("font_color", "Button", Palette.TEXT)
	theme.set_color("font_hover_color", "Button", Palette.TEXT)
	theme.set_color("font_pressed_color", "Button", Palette.ACCENT)
	theme.set_color("font_disabled_color", "Button", Color(Palette.TEXT_DIM, 0.5))
	theme.set_color("font_color", "Label", Palette.TEXT)
	var panel := _box(Color(0.09, 0.11, 0.17, 0.97))
	panel.set_content_margin_all(36)
	panel.border_color = Color("3d4a6c")
	panel.set_border_width_all(2)
	theme.set_stylebox("panel", "PanelContainer", panel)
	return theme


static func _box(color: Color) -> StyleBoxFlat:
	var box := StyleBoxFlat.new()
	box.bg_color = color
	box.set_corner_radius_all(CORNER)
	box.set_content_margin_all(12)
	return box


static func button(text: String, min_width: float = 240.0) -> Button:
	var b := Button.new()
	b.text = text
	b.custom_minimum_size = Vector2(min_width, BUTTON_HEIGHT)
	return b


static func label(text: String, font_size: int = 26, color: Color = Palette.TEXT) -> Label:
	var l := Label.new()
	l.text = text
	l.add_theme_font_size_override("font_size", font_size)
	l.add_theme_color_override("font_color", color)
	l.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	return l


## Full-screen dimmer that also blocks input from reaching the play area behind it.
static func overlay() -> ColorRect:
	var dim := ColorRect.new()
	dim.color = Color(0, 0, 0, 0.55)
	dim.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	dim.mouse_filter = Control.MOUSE_FILTER_STOP
	return dim


static func centered(child: Control) -> CenterContainer:
	var center := CenterContainer.new()
	center.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	center.mouse_filter = Control.MOUSE_FILTER_IGNORE
	center.add_child(child)
	return center
