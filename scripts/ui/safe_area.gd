class_name SafeArea
extends RefCounted
## Screen insets (display cutouts, rounded corners, system bars) converted to canvas units, so
## HUD and menu controls stay clear of them. Backgrounds still draw edge to edge.
## Returned as Vector4(left, top, right, bottom).

## Insets larger than this share of the screen are treated as bogus platform data.
const MAX_SHARE := 0.25


## Pure conversion, unit-tested: window-pixel safe rect -> canvas-unit insets. `canvas_size` is
## the visible canvas (the stretched viewport), which keeps the window's aspect ratio.
static func insets_for(window_size: Vector2i, safe_rect: Rect2i, canvas_size: Vector2) -> Vector4:
	if window_size.x <= 0 or window_size.y <= 0 or safe_rect.size.x <= 0 or safe_rect.size.y <= 0:
		return Vector4.ZERO
	var scale := canvas_size.x / float(window_size.x)
	var left := float(safe_rect.position.x)
	var top := float(safe_rect.position.y)
	var right := float(window_size.x - safe_rect.end.x)
	var bottom := float(window_size.y - safe_rect.end.y)
	var max_x := window_size.x * MAX_SHARE
	var max_y := window_size.y * MAX_SHARE
	return Vector4(
		clampf(left, 0.0, max_x) * scale,
		clampf(top, 0.0, max_y) * scale,
		clampf(right, 0.0, max_x) * scale,
		clampf(bottom, 0.0, max_y) * scale)


## Insets for the running app. Only phones and tablets report a meaningful safe area; on desktop
## the "safe area" is the work area beside the taskbar, which has nothing to do with the window.
static func current(viewport: Viewport) -> Vector4:
	if not OS.has_feature("mobile"):
		return Vector4.ZERO
	var window := viewport.get_window()
	if window == null:
		return Vector4.ZERO
	return insets_for(window.size, DisplayServer.get_display_safe_area(), viewport.get_visible_rect().size)
