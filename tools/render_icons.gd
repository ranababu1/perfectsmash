extends SceneTree
## Renders the app icon SVG layers in assets/icon/ to the PNGs Android and Google Play need,
## plus a review sheet (tests/output/icon_preview.png) showing launcher masks at real sizes.
##   godot_console --headless -s tools/render_icons.gd
##
## Layers use Android's 108dp adaptive grid. Launchers show only the centre 72dp, so the flat
## icons (Play Store, legacy launcher, project icon) are cropped to that same centre region.

const DIR := "res://assets/icon/"
const LAYER_SIZE := 432
const VISIBLE_FRACTION := 72.0 / 108.0
const PREVIEW_SIZES: Array[int] = [192, 96, 48]


func _initialize() -> void:
	var background := _render("icon_background.svg", LAYER_SIZE)
	var foreground := _render("icon_foreground.svg", LAYER_SIZE)
	var monochrome := _render("icon_monochrome.svg", LAYER_SIZE)
	if background == null or foreground == null or monochrome == null:
		quit(1)
		return
	_save(background, "adaptive_background_432.png")
	_save(foreground, "adaptive_foreground_432.png")
	_save(monochrome, "adaptive_monochrome_432.png")
	_save(_flat(512), "play_store_512.png")
	_save(_flat(192), "main_192.png")
	_save(_flat(256), "project_256.png")
	_save_preview()
	quit(0)


## Background + foreground composited, cropped to the launcher-visible centre and resized.
func _flat(size: int) -> Image:
	var full := ceili(size / VISIBLE_FRACTION)
	var image := _render("icon_background.svg", full)
	var top := _render("icon_foreground.svg", full)
	image.blend_rect(top, Rect2i(Vector2i.ZERO, top.get_size()), Vector2i.ZERO)
	var offset := (full - size) / 2
	return image.get_region(Rect2i(offset, offset, size, size))


func _render(file: String, size: int) -> Image:
	var text := FileAccess.get_file_as_string(DIR + file)
	if text.is_empty():
		push_error("missing %s" % file)
		return null
	var image := Image.new()
	var err := image.load_svg_from_string(text, size / float(LAYER_SIZE))
	if err != OK:
		push_error("cannot render %s (error %d)" % [file, err])
		return null
	image.convert(Image.FORMAT_RGBA8)
	return image


func _save(image: Image, file: String) -> void:
	var path := ProjectSettings.globalize_path(DIR + file)
	if image.save_png(path) != OK:
		push_error("cannot save " + path)
	else:
		print("wrote ", file)


## Circle and squircle masks at several sizes on light and dark wallpapers, plus the themed icon.
func _save_preview() -> void:
	var cell := 220
	var sheet := Image.create(cell * (PREVIEW_SIZES.size() * 2 + 1), cell * 2, false, Image.FORMAT_RGBA8)
	var walls: Array[Color] = [Color("e9edf5"), Color("1b1f2a")]
	for row in 2:
		sheet.fill_rect(Rect2i(0, row * cell, sheet.get_width(), cell), walls[row])
		var col := 0
		for size in PREVIEW_SIZES:
			for squircle in [false, true]:
				var icon := _masked(_flat(size), squircle)
				var at := Vector2i(col * cell + (cell - size) / 2, row * cell + (cell - size) / 2)
				sheet.blend_rect(icon, Rect2i(Vector2i.ZERO, icon.get_size()), at)
				col += 1
		# Themed icon: the launcher tints the monochrome layer over a tonal background.
		var tones: Array[Color] = [Color("d6e2ff"), Color("2c3a63")]
		var inks: Array[Color] = [Color("1f3a8a"), Color("cddaff")]
		var themed := _themed(PREVIEW_SIZES[0], tones[row], inks[row])
		var spot := Vector2i(col * cell + (cell - PREVIEW_SIZES[0]) / 2, row * cell + (cell - PREVIEW_SIZES[0]) / 2)
		sheet.blend_rect(themed, Rect2i(Vector2i.ZERO, themed.get_size()), spot)
	DirAccess.make_dir_recursive_absolute(ProjectSettings.globalize_path("res://tests/output"))
	sheet.save_png(ProjectSettings.globalize_path("res://tests/output/icon_preview.png"))
	print("wrote tests/output/icon_preview.png")


func _themed(size: int, tone: Color, ink: Color) -> Image:
	var full := ceili(size / VISIBLE_FRACTION)
	var mono := _render("icon_monochrome.svg", full)
	var offset := (full - size) / 2
	mono = mono.get_region(Rect2i(offset, offset, size, size))
	var image := Image.create(size, size, false, Image.FORMAT_RGBA8)
	image.fill(tone)
	for y in size:
		for x in size:
			var a := mono.get_pixel(x, y).a
			image.set_pixel(x, y, tone.lerp(ink, a))
	return _masked(image, false)


func _masked(image: Image, squircle: bool) -> Image:
	var size := image.get_width()
	var half := size / 2.0
	for y in size:
		for x in size:
			var p := (Vector2(x, y) + Vector2(0.5, 0.5) - Vector2(half, half)) / half
			# Superellipse n=4 approximates the common "squircle" launcher shape.
			var d := pow(pow(absf(p.x), 4.0) + pow(absf(p.y), 4.0), 0.25) if squircle else p.length()
			var alpha := clampf((1.0 - d) * half, 0.0, 1.0)
			var c := image.get_pixel(x, y)
			c.a *= alpha
			image.set_pixel(x, y, c)
	return image
