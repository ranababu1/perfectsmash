class_name UpgradesScreen
extends Control
## Weapon upgrades: spend Research Data on up to three levels per attribute. Built generically from
## WeaponCatalog (no weapon ids or attributes are known here). The screen mutates ProgressData only
## through UpgradeRules.purchase and announces each purchase; the app root saves.

signal purchased(weapon_id: String, attribute: String)
signal closed

const THEME_ID := "GAM-UI-THEME-A"
const BACKGROUND := Color("121626")
const SPACE_S := 8
const SPACE_M := 16
const SPACE_XL := 24
## Minimum touch target height (well above the 48 px floor).
const TARGET_HEIGHT := 64.0
const LIST_WIDTH := 340.0
const BUY_WIDTH := 170.0
const ICON_SIZE := 44.0
const ATTRIBUTE_NAMES := {
	"impact_energy": "Impact energy",
	"penetration": "Penetration",
	"blast_efficiency": "Blast efficiency",
	"energy_capacity": "Energy capacity",
	"targeting_assistance": "Targeting assistance",
	"energy_efficiency": "Energy efficiency",
}
const STAT_NAMES := {
	"launch_speed": "Launch speed",
	"min_launch_speed": "Minimum launch speed",
	"gravity_scale": "Gravity",
	"projectile_radius": "Projectile size",
	"projectile_mass": "Projectile mass",
	"impact_damage": "Impact damage",
	"penetration": "Penetration",
	"blast_damage": "Blast damage",
	"blast_radius": "Blast radius",
	"blast_impulse": "Blast force",
	"blast_edge_falloff": "Blast edge falloff",
	"fuse_seconds": "Fuse",
	"ammunition": "Ammunition",
	"cooldown": "Cooldown",
	"aim_preview_seconds": "Aim preview",
}
const SECONDS_STATS := ["fuse_seconds", "cooldown", "aim_preview_seconds"]
const PERCENT_STATS := ["penetration", "blast_edge_falloff"]

## Integrated assets (theme, weapon icons); set before entering the tree. Null = built-in look.
var library: AssetLibrary
## Optional AudioService; null-safe.
var audio: AudioService
var selected_weapon := ""
var balance_label: Label

var _catalog: WeaponCatalog
var _progress: ProgressData
var _unlocked_chapter := 1
var _weapon_list: VBoxContainer
var _detail: VBoxContainer
var _weapon_buttons := {}


func _init(catalog: WeaponCatalog = null, progress: ProgressData = null, unlocked_chapter: int = 1) -> void:
	_catalog = catalog if catalog != null else WeaponCatalog.new()
	_progress = progress if progress != null else ProgressData.new()
	_unlocked_chapter = unlocked_chapter


func _ready() -> void:
	set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	var production_theme := library.resource(THEME_ID) as Theme if library != null else null
	theme = production_theme if production_theme != null else UiKit.make_theme()
	var background := ColorRect.new()
	background.color = BACKGROUND
	background.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	background.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(background)

	var margin := MarginContainer.new()
	margin.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	for side in ["left", "right", "top", "bottom"]:
		margin.add_theme_constant_override("margin_" + side, SPACE_XL)
	add_child(margin)
	var root := VBoxContainer.new()
	root.add_theme_constant_override("separation", SPACE_M)
	margin.add_child(root)

	var top := HBoxContainer.new()
	top.add_theme_constant_override("separation", SPACE_M)
	root.add_child(top)
	var back := UiKit.button("Back", 160.0)
	back.name = "BackButton"
	back.pressed.connect(_on_back)
	top.add_child(back)
	var title := UiKit.label("UPGRADES", 40, Palette.TEXT)
	title.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	top.add_child(title)
	var chip := PanelContainer.new()
	chip.theme_type_variation = UiKit.CHIP
	chip.custom_minimum_size.y = TARGET_HEIGHT
	top.add_child(chip)
	balance_label = UiKit.label("", 26, Palette.ACCENT)
	balance_label.name = "Balance"
	balance_label.vertical_alignment = VERTICAL_ALIGNMENT_CENTER
	chip.add_child(balance_label)

	var body := HBoxContainer.new()
	body.size_flags_vertical = Control.SIZE_EXPAND_FILL
	body.add_theme_constant_override("separation", SPACE_XL)
	root.add_child(body)
	var list_scroll := _scroll(LIST_WIDTH)
	body.add_child(list_scroll)
	_weapon_list = VBoxContainer.new()
	_weapon_list.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	_weapon_list.add_theme_constant_override("separation", SPACE_S)
	list_scroll.add_child(_weapon_list)
	var detail_scroll := _scroll(0.0)
	detail_scroll.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	body.add_child(detail_scroll)
	_detail = VBoxContainer.new()
	_detail.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	_detail.add_theme_constant_override("separation", SPACE_M)
	detail_scroll.add_child(_detail)

	_build_weapon_list()
	var first := _first_unlocked()
	if not first.is_empty():
		select_weapon(first)
	else:
		_refresh()
	if not first.is_empty() and not DisplayServer.is_touchscreen_available():
		_focus_later(_weapon_buttons[first])


func _unhandled_input(event: InputEvent) -> void:
	if event.is_action_pressed("ui_cancel"):
		_on_back()
		if is_inside_tree():
			get_viewport().set_input_as_handled()


# --- Queries -------------------------------------------------------------------------------------

func is_weapon_unlocked(weapon_id: String) -> bool:
	var spec := _catalog.get_weapon(weapon_id)
	return spec != null and spec.unlock_chapter <= _unlocked_chapter


func can_buy(weapon_id: String, attribute: String) -> bool:
	return is_weapon_unlocked(weapon_id) and UpgradeRules.can_purchase(_catalog, _progress, weapon_id, attribute)


## "Impact damage 90 → 104" for the next level, or "" when maxed or unsupported.
func next_effect_text(weapon_id: String, attribute: String) -> String:
	var spec := _catalog.get_weapon(weapon_id)
	if spec == null or not spec.supports_upgrade(attribute):
		return ""
	var level := _progress.upgrade_level(weapon_id, attribute)
	if level >= WeaponCatalog.MAX_UPGRADE_LEVEL:
		return ""
	var levels := _levels_of(spec)
	var stat: String = spec.upgrades[attribute].stat
	var before: float = float(spec.effective_stats(levels)[stat])
	levels[attribute] = level + 1
	var after: float = float(spec.effective_stats(levels)[stat])
	return "%s %s → %s" % [STAT_NAMES.get(stat, _humanize(stat)), _format_stat(stat, before), _format_stat(stat, after)]


static func attribute_title(attribute: String) -> String:
	return ATTRIBUTE_NAMES.get(attribute, _humanize(attribute))


# --- Actions -------------------------------------------------------------------------------------

## Selects an unlocked weapon and shows its upgrades. Locked or unknown weapons are ignored.
func select_weapon(weapon_id: String) -> void:
	if not is_weapon_unlocked(weapon_id):
		return
	selected_weapon = weapon_id
	_refresh()


## Buys the next level of an attribute on an unlocked weapon. Emits `purchased` on success.
func buy(weapon_id: String, attribute: String) -> bool:
	if not is_weapon_unlocked(weapon_id):
		return false
	if not UpgradeRules.purchase(_catalog, _progress, weapon_id, attribute):
		_sfx("ui_back")
		return false
	_sfx("ui_click")
	_refresh()
	_refocus(attribute)
	purchased.emit(weapon_id, attribute)
	return true


# --- Building ------------------------------------------------------------------------------------

func _build_weapon_list() -> void:
	for id in _catalog.order:
		var spec := _catalog.get_weapon(id)
		var unlocked := is_weapon_unlocked(id)
		var button := Button.new()
		button.name = "Weapon_" + id
		button.toggle_mode = true
		button.disabled = not unlocked
		button.alignment = HORIZONTAL_ALIGNMENT_LEFT
		button.custom_minimum_size = Vector2(0, 96.0)
		button.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
		button.text = spec.display_name if unlocked else "%s\nUnlocks in Chapter %d" % [spec.display_name, spec.unlock_chapter]
		button.icon = _icon_texture(id)
		button.expand_icon = true
		button.add_theme_constant_override("icon_max_width", int(ICON_SIZE))
		button.add_theme_font_size_override("font_size", 18)
		UiKit.add_press_feedback(button)
		button.pressed.connect(func() -> void:
			_sfx("ui_click")
			select_weapon(id))
		_weapon_list.add_child(button)
		_weapon_buttons[id] = button
	if _catalog.order.is_empty():
		_weapon_list.add_child(UiKit.label("No weapons available", 20, Palette.TEXT_DIM))


func _refresh() -> void:
	balance_label.text = "Research Data  %d" % _progress.research_data
	for id: String in _weapon_buttons:
		(_weapon_buttons[id] as Button).set_pressed_no_signal(id == selected_weapon)
	for child in _detail.get_children():
		_detail.remove_child(child)
		child.queue_free()
	var spec := _catalog.get_weapon(selected_weapon)
	if spec == null:
		_detail.add_child(UiKit.label("Select an unlocked weapon", 24, Palette.TEXT_DIM))
		return
	_detail.add_child(_weapon_header(spec))
	for attribute: String in spec.upgrades:
		_detail.add_child(_attribute_row(spec, attribute))
	if spec.upgrades.is_empty():
		_detail.add_child(UiKit.label("This weapon has no upgrades", 22, Palette.TEXT_DIM))
	var note := UiKit.label("Upgrades make destruction more efficient. They are never required.", 18, Palette.TEXT_DIM)
	note.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	_detail.add_child(note)


func _weapon_header(spec: WeaponCatalog.WeaponSpec) -> Control:
	var row := HBoxContainer.new()
	row.name = "WeaponHeader"
	row.add_theme_constant_override("separation", SPACE_M)
	var texture := _icon_texture(spec.id)
	if texture != null:
		var icon := TextureRect.new()
		icon.texture = texture
		icon.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
		icon.stretch_mode = TextureRect.STRETCH_KEEP_ASPECT_CENTERED
		icon.custom_minimum_size = Vector2(ICON_SIZE, ICON_SIZE)
		row.add_child(icon)
	else:
		var badge := PanelContainer.new()
		badge.name = "IconBadge"
		badge.theme_type_variation = UiKit.CHIP
		badge.custom_minimum_size = Vector2(ICON_SIZE, ICON_SIZE)
		var letter := UiKit.label(spec.display_name.left(1).to_upper(), 24, Palette.ACCENT)
		letter.vertical_alignment = VERTICAL_ALIGNMENT_CENTER
		badge.add_child(letter)
		row.add_child(badge)
	var name_label := UiKit.label(spec.display_name, 32, Palette.TEXT)
	name_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_LEFT
	name_label.vertical_alignment = VERTICAL_ALIGNMENT_CENTER
	row.add_child(name_label)
	return row


func _attribute_row(spec: WeaponCatalog.WeaponSpec, attribute: String) -> Control:
	var level := _progress.upgrade_level(spec.id, attribute)
	var maxed := level >= WeaponCatalog.MAX_UPGRADE_LEVEL
	var panel := PanelContainer.new()
	panel.name = "Row_" + attribute
	panel.theme_type_variation = UiKit.CHIP
	var row := HBoxContainer.new()
	row.add_theme_constant_override("separation", SPACE_M)
	panel.add_child(row)

	var text := VBoxContainer.new()
	text.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	row.add_child(text)
	var title := UiKit.label(attribute_title(attribute), 24, Palette.TEXT)
	title.horizontal_alignment = HORIZONTAL_ALIGNMENT_LEFT
	text.add_child(title)
	var effect := UiKit.label("Fully upgraded" if maxed else next_effect_text(spec.id, attribute), 20, Palette.TEXT_DIM)
	effect.name = "Effect_" + attribute
	effect.horizontal_alignment = HORIZONTAL_ALIGNMENT_LEFT
	effect.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	text.add_child(effect)

	var pips := HBoxContainer.new()
	pips.name = "Pips_" + attribute
	pips.add_theme_constant_override("separation", 6)
	pips.alignment = BoxContainer.ALIGNMENT_CENTER
	for i in WeaponCatalog.MAX_UPGRADE_LEVEL:
		var pip := ColorRect.new()
		pip.custom_minimum_size = Vector2(22, 12)
		pip.color = Palette.ACCENT if i < level else Color(1, 1, 1, 0.14)
		pip.mouse_filter = Control.MOUSE_FILTER_IGNORE
		pips.add_child(pip)
	var pip_box := VBoxContainer.new()
	pip_box.alignment = BoxContainer.ALIGNMENT_CENTER
	pip_box.add_child(pips)
	row.add_child(pip_box)

	var cost := UpgradeRules.next_cost(_catalog, _progress, spec.id, attribute)
	var buy_button := UiKit.button("Max" if maxed else "Buy  %d" % cost, BUY_WIDTH)
	buy_button.name = "Buy_" + attribute
	buy_button.disabled = maxed or not can_buy(spec.id, attribute)
	var id := spec.id
	buy_button.pressed.connect(func() -> void: buy(id, attribute))
	row.add_child(buy_button)
	return panel


# --- Helpers -------------------------------------------------------------------------------------

func _icon_texture(weapon_id: String) -> Texture2D:
	return library.texture("GAM-ICN-WEAPON_%s-A" % weapon_id.to_upper()) if library != null else null


func _scroll(min_width: float) -> ScrollContainer:
	var scroll := ScrollContainer.new()
	scroll.custom_minimum_size.x = min_width
	scroll.horizontal_scroll_mode = ScrollContainer.SCROLL_MODE_DISABLED
	scroll.size_flags_vertical = Control.SIZE_EXPAND_FILL
	return scroll


func _levels_of(spec: WeaponCatalog.WeaponSpec) -> Dictionary:
	var levels := {}
	for attribute: String in spec.upgrades:
		levels[attribute] = _progress.upgrade_level(spec.id, attribute)
	return levels


func _first_unlocked() -> String:
	for id in _catalog.order:
		if is_weapon_unlocked(id):
			return id
	return ""


func _refocus(attribute: String) -> void:
	if DisplayServer.is_touchscreen_available() or not is_inside_tree():
		return
	var target: Control = _detail.find_child("Buy_" + attribute, true, false)
	if target == null or (target as Button).disabled:
		target = _weapon_buttons.get(selected_weapon)
	if target != null:
		_focus_later(target)


func _focus_later(target: Control) -> void:
	(func() -> void:
		if is_instance_valid(target) and target.is_inside_tree():
			target.grab_focus()).call_deferred()


func _format_stat(stat: String, value: float) -> String:
	if PERCENT_STATS.has(stat):
		return "%s%%" % _number(value * 100.0)
	if SECONDS_STATS.has(stat):
		return "%s s" % _number(value)
	return _number(value)


static func _number(value: float) -> String:
	var text := "%.2f" % value
	if text.contains("."):
		text = text.rstrip("0").rstrip(".")
	return text


static func _humanize(id: String) -> String:
	var text := id.replace("_", " ")
	return text.left(1).to_upper() + text.substr(1)


func _on_back() -> void:
	_sfx("ui_back")
	closed.emit()


func _sfx(id: String) -> void:
	if audio != null:
		audio.play(id)
