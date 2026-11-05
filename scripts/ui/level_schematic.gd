class_name LevelSchematic
extends Control
## Blueprint-style recon image of a level for the mission briefing: a faint grid, outlined
## structure pieces in their material colors, cores, drones, supply crates, the drop zone or
## topple line, and the launcher. Drawn from the LevelDefinition, so it always matches the level.

const PAD := 14.0
const GRID := 40.0
const BLUEPRINT := Color(0.42, 0.62, 1.0)

var definition: LevelDefinition


func _init(p_definition: LevelDefinition = null) -> void:
	definition = p_definition
	mouse_filter = Control.MOUSE_FILTER_IGNORE
	resized.connect(queue_redraw)


func show_level(def: LevelDefinition) -> void:
	definition = def
	queue_redraw()


## Visible world rectangle: from the launcher to the right edge, from the highest piece to the ground.
func _world_rect() -> Rect2:
	var top := GameConfig.GROUND_TOP - 260.0
	for box in definition.statics + definition.blocks:
		top = minf(top, box.position.y - box.size.y / 2.0 - 30.0)
	for t in definition.targets + definition.allies:
		top = minf(top, t.position.y - t.radius - 30.0)
	if definition.objective_type == LevelDefinition.OBJECTIVE_DELIVER:
		top = minf(top, definition.zone.position.y - 30.0)
	top = maxf(top, 0.0)
	return Rect2(definition.launcher.x - 80.0, top, GameConfig.WORLD_WIDTH - definition.launcher.x + 110.0, GameConfig.GROUND_TOP + 24.0 - top)


func _draw() -> void:
	var frame := Rect2(Vector2.ZERO, size)
	draw_rect(frame, Color(0.05, 0.08, 0.16, 0.85))
	if definition == null:
		return
	var world := _world_rect()
	var area := frame.grow(-PAD)
	var scale := minf(area.size.x / world.size.x, area.size.y / world.size.y)
	var offset := area.position + (area.size - world.size * scale) / 2.0 - world.position * scale
	var to := func(p: Vector2) -> Vector2: return offset + p * scale

	# Grid
	var x := floorf(world.position.x / GRID) * GRID
	while x < world.end.x:
		var a: Vector2 = to.call(Vector2(x, world.position.y))
		var b: Vector2 = to.call(Vector2(x, world.end.y))
		draw_line(a, b, Color(BLUEPRINT, 0.07), 1.0)
		x += GRID
	var y := floorf(world.position.y / GRID) * GRID
	while y < world.end.y:
		draw_line(to.call(Vector2(world.position.x, y)), to.call(Vector2(world.end.x, y)), Color(BLUEPRINT, 0.07), 1.0)
		y += GRID
	# Ground
	var g1: Vector2 = to.call(Vector2(world.position.x, GameConfig.GROUND_TOP))
	var g2: Vector2 = to.call(Vector2(world.end.x, GameConfig.GROUND_TOP))
	draw_line(g1, g2, Color(BLUEPRINT, 0.6), 2.0)

	match definition.objective_type:
		LevelDefinition.OBJECTIVE_TOPPLE:
			var ly := definition.topple_line_y
			draw_dashed_line(to.call(Vector2(world.position.x, ly)), to.call(Vector2(world.end.x, ly)), Palette.TOPPLE_LINE, 2.0, 8.0)
		LevelDefinition.OBJECTIVE_DELIVER:
			var z := Rect2(to.call(definition.zone.position), definition.zone.size * scale)
			draw_rect(z, Color(Palette.DROP_ZONE, 0.12))
			draw_rect(z, Color(Palette.DROP_ZONE, 0.8), false, 1.5)

	for box in definition.statics:
		var color := Palette.BUMPER if box.kind == "bumper" else Color(BLUEPRINT, 0.75)
		_box(to, scale, box, Color(color, 0.18), color)
	for box in definition.blocks:
		var edge := Palette.material_fill(box.material)
		edge.a = 1.0
		_box(to, scale, box, Color(edge, 0.22), edge)
	for t in definition.targets:
		draw_circle(to.call(t.position), t.radius * scale, Color(Palette.TARGET, 0.35), true, -1.0, true)
		draw_arc(to.call(t.position), t.radius * scale, 0, TAU, 24, Palette.TARGET, 1.5, true)
	for a in definition.allies:
		draw_circle(to.call(a.position), a.radius * scale, Color(Palette.ALLY, 0.35), true, -1.0, true)
		draw_arc(to.call(a.position), a.radius * scale, 0, TAU, 24, Palette.ALLY, 1.5, true)
	# Launcher
	var tip: Vector2 = to.call(definition.launcher)
	draw_line(tip, to.call(Vector2(definition.launcher.x, GameConfig.GROUND_TOP)), Color(BLUEPRINT, 0.7), 2.0)
	draw_circle(tip, maxf(3.0, GameConfig.PROJECTILE_RADIUS * scale), Palette.PROJECTILE, true, -1.0, true)
	draw_rect(frame, Color(BLUEPRINT, 0.35), false, 1.0)


func _box(to: Callable, _scale: float, box: Dictionary, fill: Color, edge: Color) -> void:
	var half: Vector2 = box.size / 2.0
	var pts := PackedVector2Array()
	for c in [Vector2(-half.x, -half.y), Vector2(half.x, -half.y), Vector2(half.x, half.y), Vector2(-half.x, half.y)]:
		pts.append(to.call(box.position + c.rotated(box.rotation)))
	draw_colored_polygon(pts, fill)
	pts.append(pts[0])
	draw_polyline(pts, edge, 1.5, true)
