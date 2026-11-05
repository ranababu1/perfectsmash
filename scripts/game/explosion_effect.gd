class_name ExplosionEffect
extends Node2D
## Visual only (no physics): a bright flash, a fading fireball and a thick shockwave ring that grows
## to the blast radius, so explosions read clearly and match the area they affect.

const DURATION := 0.55

var radius := GameConfig.BLAST_RADIUS
var _age := 0.0


func _init(p_radius: float = GameConfig.BLAST_RADIUS) -> void:
	radius = p_radius
	# Additive blending makes the blast glow against the dark sky instead of muddying it.
	var glow := CanvasItemMaterial.new()
	glow.blend_mode = CanvasItemMaterial.BLEND_MODE_ADD
	material = glow


func _process(delta: float) -> void:
	_age += delta
	if _age >= DURATION:
		queue_free()
		return
	queue_redraw()


func _draw() -> void:
	var t := _age / DURATION
	var grow := ease(t, 0.35)
	# Fireball: warm fill shrinking in opacity as it expands.
	draw_circle(Vector2.ZERO, radius * 0.75 * grow, Color(Palette.BLAST, 0.45 * (1.0 - t)), true, -1.0, true)
	# White-hot core in the first instant.
	if t < 0.3:
		draw_circle(Vector2.ZERO, radius * 0.35 * (1.0 - t / 0.3) + 8.0, Color(1, 0.97, 0.85, 0.9 * (1.0 - t / 0.3)), true, -1.0, true)
	# Shockwave ring reaching the true blast radius.
	draw_arc(Vector2.ZERO, radius * grow, 0, TAU, 64, Color(Palette.EXPLOSIVE_EDGE, 0.8 * (1.0 - t)), 6.0 * (1.0 - t) + 1.5, true)
	# A few sparks.
	for i in 8:
		var dir := Vector2.RIGHT.rotated(TAU * i / 8.0 + 0.4)
		var p := dir * radius * 0.95 * ease(t, 0.5)
		draw_circle(p, 4.0 * (1.0 - t) + 1.0, Color(1, 0.85, 0.5, 1.0 - t), true, -1.0, true)
