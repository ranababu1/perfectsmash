class_name UiKit
extends RefCounted
## Shared theme and widget factories. Touch targets are at least 64px on the 720px canvas.
## Style: quiet translucent surfaces with hairline borders; the warm accent is reserved for the
## one primary action on screen, stars and remaining shots.

const BUTTON_HEIGHT := 64.0
const ICON_BUTTON := 64.0
const CORNER := 16
const PANEL_CORNER := 24
const PANEL_WIDTH := 440.0
## Theme type variations (set on a control's theme_type_variation).
const PRIMARY := "PrimaryButton"
const ROUND := "RoundButton"
const CHIP := "Chip"


static func make_theme() -> Theme:
	var theme := Theme.new()
	theme.default_font_size = 24

	theme.set_stylebox("normal", "Button", _box(Palette.SURFACE_RAISED, Palette.BORDER))
	theme.set_stylebox("hover", "Button", _box(Palette.SURFACE_HOVER, Palette.BORDER))
	theme.set_stylebox("pressed", "Button", _box(Palette.SURFACE_PRESSED, Palette.BORDER))
	theme.set_stylebox("hover_pressed", "Button", _box(Palette.SURFACE_HOVER, Palette.BORDER))
	theme.set_stylebox("disabled", "Button", _box(Color(1, 1, 1, 0.025), Color(1, 1, 1, 0.03)))
	theme.set_stylebox("focus", "Button", _focus_box(CORNER))
	theme.set_color("font_color", "Button", Palette.TEXT)
	theme.set_color("font_hover_color", "Button", Palette.TEXT)
	theme.set_color("font_pressed_color", "Button", Palette.TEXT)
	theme.set_color("font_hover_pressed_color", "Button", Palette.TEXT)
	theme.set_color("font_focus_color", "Button", Palette.TEXT)
	theme.set_color("font_disabled_color", "Button", Palette.TEXT_FAINT)

	theme.set_type_variation(PRIMARY, "Button")
	theme.set_stylebox("normal", PRIMARY, _box(Palette.ACCENT))
	theme.set_stylebox("hover", PRIMARY, _box(Palette.ACCENT.lightened(0.12)))
	theme.set_stylebox("pressed", PRIMARY, _box(Palette.ACCENT.darkened(0.12)))
	theme.set_stylebox("hover_pressed", PRIMARY, _box(Palette.ACCENT.darkened(0.06)))
	for state in ["font_color", "font_hover_color", "font_pressed_color", "font_hover_pressed_color", "font_focus_color"]:
		theme.set_color(state, PRIMARY, Palette.ACCENT_INK)

	theme.set_type_variation(ROUND, "Button")
	# One pixel under half the size: radii that exactly meet leave a seam artifact in StyleBoxFlat.
	var round_radius := int(ICON_BUTTON / 2.0) - 1
	theme.set_stylebox("normal", ROUND, _box(Palette.SURFACE_RAISED, Palette.BORDER, round_radius))
	theme.set_stylebox("hover", ROUND, _box(Palette.SURFACE_HOVER, Palette.BORDER, round_radius))
	theme.set_stylebox("pressed", ROUND, _box(Palette.SURFACE_PRESSED, Palette.BORDER, round_radius))
	theme.set_stylebox("hover_pressed", ROUND, _box(Palette.SURFACE_HOVER, Palette.BORDER, round_radius))
	theme.set_stylebox("focus", ROUND, _focus_box(round_radius))

	theme.set_color("font_color", "Label", Palette.TEXT)

	var panel := _box(Palette.SURFACE, Palette.BORDER, PANEL_CORNER)
	panel.set_content_margin_all(32)
	panel.shadow_color = Palette.SHADOW
	panel.shadow_size = 28
	panel.shadow_offset = Vector2(0, 10)
	theme.set_stylebox("panel", "PanelContainer", panel)

	theme.set_type_variation(CHIP, "PanelContainer")
	var chip := _box(Color(0.06, 0.08, 0.13, 0.55), Palette.BORDER, CORNER)
	chip.content_margin_left = 18
	chip.content_margin_right = 18
	chip.content_margin_top = 10
	chip.content_margin_bottom = 10
	theme.set_stylebox("panel", CHIP, chip)
	return theme


static func _box(color: Color, border: Color = Color(0, 0, 0, 0), radius: int = CORNER) -> StyleBoxFlat:
	var box := StyleBoxFlat.new()
	box.bg_color = color
	box.set_corner_radius_all(radius)
	box.set_content_margin_all(12)
	box.anti_aliasing = true
	if border.a > 0.0:
		box.border_color = border
		box.set_border_width_all(1)
	return box


static func _focus_box(radius: int) -> StyleBoxFlat:
	var focus := _box(Color(0, 0, 0, 0), Color(Palette.ACCENT, 0.7), radius)
	focus.set_border_width_all(2)
	focus.set_expand_margin_all(3)
	return focus


static func button(text: String, min_width: float = 200.0) -> Button:
	var b := Button.new()
	b.text = text
	b.custom_minimum_size = Vector2(min_width, BUTTON_HEIGHT)
	add_press_feedback(b)
	return b


static func primary_button(text: String, min_width: float = 200.0) -> Button:
	var b := button(text, min_width)
	b.theme_type_variation = PRIMARY
	return b


## Round button showing a vector icon. Pass `toggled_kind` for a two-state toggle icon.
static func icon_button(kind: String, toggled_kind: String = "") -> Button:
	var b := Button.new()
	b.theme_type_variation = ROUND
	b.custom_minimum_size = Vector2(ICON_BUTTON, ICON_BUTTON)
	var icon := Icon.new(kind, 34.0, Palette.TEXT)
	icon.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	b.add_child(icon)
	if toggled_kind != "":
		b.toggle_mode = true
		var refresh := func(on: bool) -> void:
			icon.set_kind(kind if on else toggled_kind)
			icon.set_color(Palette.TEXT if on else Palette.TEXT_FAINT)
		b.toggled.connect(refresh)
		(func() -> void: refresh.call(b.button_pressed)).call_deferred()
	add_press_feedback(b)
	return b


## Small scale dip on press: tactile, but quick enough to never delay the action.
static func add_press_feedback(b: Button) -> void:
	b.resized.connect(func() -> void: b.pivot_offset = b.size / 2.0)
	b.button_down.connect(func() -> void: b.create_tween().tween_property(b, "scale", Vector2(0.96, 0.96), 0.06))
	b.button_up.connect(func() -> void: b.create_tween().tween_property(b, "scale", Vector2.ONE, 0.12))


## Gives keyboard/gamepad users a starting focus; skipped on touch screens, where a focus ring
## on a button nobody touched just looks like a stray highlight.
static func focus_default(b: Control) -> void:
	if not DisplayServer.is_touchscreen_available():
		b.grab_focus.call_deferred()


static func label(text: String, font_size: int = 24, color: Color = Palette.TEXT) -> Label:
	var l := Label.new()
	l.text = text
	l.add_theme_font_size_override("font_size", font_size)
	l.add_theme_color_override("font_color", color)
	l.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	return l


## Full-screen dimmer that also blocks input from reaching the play area behind it.
static func overlay() -> ColorRect:
	var dim := ColorRect.new()
	dim.color = Palette.SCRIM
	dim.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	dim.mouse_filter = Control.MOUSE_FILTER_STOP
	return dim


static func centered(child: Control) -> CenterContainer:
	var center := CenterContainer.new()
	center.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	center.mouse_filter = Control.MOUSE_FILTER_IGNORE
	center.add_child(child)
	return center


## Fade in with a slight rise; used for panels and screens.
static func animate_in(node: Control, rise: float = 16.0, duration: float = 0.28) -> void:
	node.modulate.a = 0.0
	# Inside a container (e.g. CenterContainer) the resting position is only known after the
	# container lays the node out; reading it earlier pinned centred panels to the top edge.
	if rise != 0.0 and node.is_inside_tree() and node.get_parent() is Container:
		await node.get_tree().process_frame
		if not is_instance_valid(node) or not node.is_inside_tree():
			return
	var tween := node.create_tween().set_parallel().set_trans(Tween.TRANS_CUBIC).set_ease(Tween.EASE_OUT)
	tween.tween_property(node, "modulate:a", 1.0, duration)
	if rise != 0.0:
		var final_y := node.position.y
		node.position.y += rise
		tween.tween_property(node, "position:y", final_y, duration)
