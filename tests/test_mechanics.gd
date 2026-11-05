extends TestCase
## Campaign mechanics through the real GameSession with synthetic levels: explosive chains,
## blast and heavy shots, ally drones, cargo delivery and bounce pads.

const MAX_FRAMES := int(GameConfig.SIMULATION_TIMEOUT * 60.0) + 120
## Fired backwards, away from everything: arms the level without touching it.
const MISS := Vector2(-500, -300)


func _def(extra: Dictionary) -> LevelDefinition:
	var data := {
		"id": "M01", "name": "Mechanics", "shots": 3, "par": 1,
		"launcher": [180, 540],
		"objective": {"type": "destroy_targets"},
	}
	data.merge(extra, true)
	var def := LevelDefinition.from_dict(data)
	assert_true(def.is_valid(), "synthetic level valid: %s" % ", ".join(def.errors))
	return def


func _wait_resolved(session: GameSession) -> void:
	var frames := 0
	while session.rules.phase == SessionRules.Phase.SIMULATING and frames < MAX_FRAMES:
		await tree.physics_frame
		frames += 1
	assert_true(frames < MAX_FRAMES, "shot resolved")


func _blocks(session: GameSession, material: String) -> Array:
	return session.get_child(0).get_children().filter(func(n: Node) -> bool:
		return n is BlockBody and n.material_kind == material and not n.is_queued_for_deletion())


func test_explosive_chain_reaches_the_core() -> void:
	var session: GameSession = await make_session(_def({
		"blocks": [
			{"x": 700, "y": 620, "w": 40, "h": 40, "material": "explosive"},
			{"x": 820, "y": 620, "w": 40, "h": 40, "material": "explosive"},
		],
		"targets": [{"x": 900, "y": 616, "r": 22}],
	}))
	await wait_physics_frames(60)
	var blasts := []
	session.exploded.connect(func(at: Vector2) -> void: blasts.append(at))
	session.launch(MISS)
	await wait_physics_frames(2)
	var first: BlockBody = _blocks(session, "explosive")[0]
	first.detonate()
	await _wait_resolved(session)
	assert_eq(blasts.size(), 2, "the first blast set off the second crate")
	assert_eq(_blocks(session, "explosive").size(), 0, "both crates gone")
	assert_eq(session.targets_remaining, 0, "second blast broke the core")
	assert_eq(session.rules.phase, SessionRules.Phase.WON)
	free_session(session)


func test_blast_shot_explodes_on_first_contact() -> void:
	var session: GameSession = await make_session(_def({
		"ammo": ["blast"],
		"targets": [{"x": 260, "y": 616, "r": 22}],
	}))
	await wait_physics_frames(60)
	assert_eq(session.current_ammo(), "blast")
	var blasts := []
	session.exploded.connect(func(at: Vector2) -> void: blasts.append(at))
	session.launch(Vector2(0, 400))
	await _wait_resolved(session)
	assert_eq(blasts.size(), 1, "detonated when it hit the ground")
	assert_eq(session.targets_remaining, 0, "nearby core broken by the blast")
	assert_eq(session.current_ammo(), "standard", "shots past the ammo list are standard")
	free_session(session)


func test_heavy_shot_is_heavier_and_bigger() -> void:
	var heavy := ProjectileBody.new("heavy")
	var standard := ProjectileBody.new()
	assert_true(heavy.mass > standard.mass * 2.0, "heavy shot mass")
	assert_true(ProjectileBody.radius_for("heavy") > ProjectileBody.radius_for("standard"))
	heavy.free()
	standard.free()


func test_lost_ally_fails_with_shots_left() -> void:
	var session: GameSession = await make_session(_def({
		"ammo": ["blast"],
		"targets": [{"x": 1100, "y": 616, "r": 22}],
		"allies": [{"x": 260, "y": 616, "r": 20}],
	}))
	await wait_physics_frames(60)
	var lost := []
	session.ally_lost.connect(func(at: Vector2) -> void: lost.append(at))
	session.launch(Vector2(0, 400))
	await _wait_resolved(session)
	assert_eq(lost.size(), 1, "ally broken by the blast")
	assert_eq(session.rules.phase, SessionRules.Phase.LOST, "mission failed at once")
	assert_eq(session.rules.shots_remaining(), 2)
	free_session(session)


func test_cargo_in_zone_wins_and_lost_cargo_fails() -> void:
	var data := {
		"objective": {"type": "deliver", "zone": {"x": 900, "y": 600, "w": 140, "h": 80}},
		"blocks": [{"x": 900, "y": 620, "w": 40, "h": 40, "material": "cargo"}],
	}
	var session: GameSession = await make_session(_def(data))
	await wait_physics_frames(60)
	session.launch(MISS)
	await _wait_resolved(session)
	assert_eq(session.rules.phase, SessionRules.Phase.WON, "crate resting in the zone wins")
	free_session(session)

	session = await make_session(_def(data))
	await wait_physics_frames(60)
	session.launch(MISS)
	await wait_physics_frames(2)
	var crate: BlockBody = _blocks(session, "cargo")[0]
	PhysicsServer2D.body_set_state(crate.get_rid(), PhysicsServer2D.BODY_STATE_TRANSFORM, Transform2D(0, Vector2(5000, 600)))
	await _wait_resolved(session)
	assert_eq(session.cargo_lost, 1)
	assert_eq(session.rules.phase, SessionRules.Phase.LOST, "lost cargo fails the mission")
	free_session(session)


func test_bumper_is_bouncy() -> void:
	var def := _def({"targets": [{"x": 900, "y": 616, "r": 22}],
		"statics": [{"x": 640, "y": 300, "w": 200, "h": 20, "kind": "bumper"}, {"x": 640, "y": 200, "w": 200, "h": 20}]})
	var world := LevelLoader.build(def)
	var boxes := world.get_children().filter(func(n: Node) -> bool: return n is StaticBox and n.name != "Ground")
	assert_eq(boxes.size(), 2)
	assert_true(boxes[0].is_bumper and boxes[0].physics_material_override.bounce > 0.9, "bumper bounces")
	assert_false(boxes[1].is_bumper, "default static kind is a wall")
	world.free()


func test_definition_rejects_bad_campaign_data() -> void:
	var bad := LevelDefinition.from_dict({
		"id": "B", "name": "Bad", "shots": 1, "par": 1, "launcher": [180, 540],
		"objective": {"type": "deliver", "zone": {"x": 900, "y": 600, "w": 100, "h": 50}},
		"blocks": [{"x": 900, "y": 620, "w": 40, "h": 40, "material": "wood"}],
		"statics": [{"x": 500, "y": 300, "w": 50, "h": 10, "kind": "trampoline"}],
		"ammo": ["standard", "laser"],
	})
	var text := ", ".join(bad.errors)
	assert_true(text.contains("cargo"), "deliver without cargo rejected: " + text)
	assert_true(text.contains("static kind"), "unknown static kind rejected")
	assert_true(text.contains("more ammo"), "ammo longer than shots rejected")
	assert_true(text.contains("unknown ammo"), "unknown ammo rejected")
