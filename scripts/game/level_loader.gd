class_name LevelLoader
extends RefCounted
## Instantiates a validated LevelDefinition into a fresh node tree of physics bodies.
## Building from the definition every time guarantees restart restores the exact initial setup.
##
## Collision layers (all bodies collide with all layers):
##   1 = static world, 2 = blocks, 3 = targets, 4 = projectile.

const GROUND_MARGIN := 600.0
## Deep enough to fill the screen bottom on tall (4:3) displays with the expand aspect.
const GROUND_DEPTH := 400.0


static func build(def: LevelDefinition) -> Node2D:
	var world := Node2D.new()
	world.name = "World"
	var ground_width := GameConfig.WORLD_WIDTH + GROUND_MARGIN * 2.0
	var ground := StaticBox.new(Vector2(ground_width, GROUND_DEPTH), Palette.GROUND, Palette.GROUND_EDGE)
	ground.name = "Ground"
	ground.position = Vector2(GameConfig.WORLD_WIDTH / 2.0, GameConfig.GROUND_TOP + GROUND_DEPTH / 2.0)
	world.add_child(ground)

	for box in def.statics:
		var body := StaticBox.new(box.size)
		body.position = box.position
		body.rotation = box.rotation
		world.add_child(body)
	for box in def.blocks:
		var block := BlockBody.new(box.size, box.material)
		block.position = box.position
		block.rotation = box.rotation
		world.add_child(block)
	for spec in def.targets:
		var target := TargetBody.new(spec.radius)
		target.position = spec.position
		world.add_child(target)
	return world
