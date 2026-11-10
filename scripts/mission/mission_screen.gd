class_name MissionScreen
extends Node
## One mission attempt: builds the MissionEngine (rules), MissionWorld (2D physics), MissionView
## (3D presentation + operative) and MissionHud, and maps touch input to the operative's aim.
##
## Aiming is not a slingshot: touch and hold anywhere in the play area and the operative points
## the weapon at that spot. Kinetic Accelerator: direction only. Breach Charge: the distance from
## the operative sets the throw power, and the arc preview shows the landing. Release to fire;
## release close to the operative to cancel.

signal restart_requested

const DEFAULT_MISSION := "res://data/missions/helix_01.json"
const CANCEL_DISTANCE := 70.0
## Finger distance from the muzzle (px in the physics plane) for a full-power Breach throw.
const BREACH_FULL_POWER_DISTANCE := 760.0
const RESULT_DELAY := 1.2
const IDLE_AFTER := 4.0

var mission_path := DEFAULT_MISSION
var audio: AudioService
## Set by the app root before the screen enters the tree; MissionAudio drives them.
var music: MusicDirector
var ambience: MusicDirector
var mission_audio: MissionAudio
var progress: ProgressData
var save: SaveService
var scoring: MissionScoring
## Scoring breakdown of the finished attempt and the Research Data it granted.
var last_score := {}
var last_research_granted := 0
var engine: MissionEngine
var world: MissionWorld
var view: MissionView
var hud: MissionHud
var _aiming := false
var _aim_direction := Vector2.ZERO
var _aim_power := 1.0
var _since_input := 0.0
var _result_shown := false


## `p_progress`/`p_save` may be null (e.g. tools); results are then scored but not stored.
func _init(p_audio: AudioService = null, p_progress: ProgressData = null, p_save: SaveService = null, p_mission_path: String = DEFAULT_MISSION) -> void:
	audio = p_audio
	progress = p_progress
	save = p_save
	mission_path = p_mission_path


func _ready() -> void:
	process_mode = Node.PROCESS_MODE_PAUSABLE
	var materials := MaterialCatalog.load_from_file()
	var weapons := WeaponCatalog.load_from_file()
	var definition := MissionDefinition.load_from_file(mission_path, materials, weapons)
	scoring = MissionScoring.load_from_file()
	if not materials.is_valid() or not weapons.is_valid() or not definition.is_valid() or not scoring.is_valid():
		var problems := materials.errors + weapons.errors + definition.errors + scoring.errors
		push_error("MissionScreen: invalid data: %s" % ", ".join(problems))
		var message := UiKit.label("Mission data failed to load.\n" + "\n".join(problems.slice(0, 5)), 20)
		message.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
		add_child(message)
		return
	var upgrades := UpgradeRules.levels_for_engine(weapons, progress) if progress != null else {}
	engine = MissionEngine.new(definition, materials, weapons, upgrades)
	world = MissionWorld.new()
	add_child(world)
	world.setup(definition, engine, materials)
	view = MissionView.new()
	add_child(view)
	view.setup(world)

	var layer := CanvasLayer.new()
	layer.process_mode = Node.PROCESS_MODE_ALWAYS
	add_child(layer)
	hud = MissionHud.new()
	hud.theme = UiKit.make_theme()
	layer.add_child(hud)
	var weapon_states: Array[WeaponState] = []
	for id in engine.weapon_order:
		weapon_states.append(engine.weapons[id])
	hud.set_weapons(weapon_states)
	hud.weapon_pressed.connect(select_weapon)
	hud.pause_pressed.connect(pause)
	hud.resume_pressed.connect(resume)
	hud.restart_pressed.connect(func() -> void: restart_requested.emit())

	engine.objective_changed.connect(_on_objective_changed)
	engine.critical_asset_changed.connect(func(_id: String, state: int) -> void:
		if state == DamageableComponent.State.CRITICAL:
			_play("core_critical"))
	if music != null or ambience != null:
		mission_audio = MissionAudio.new()
		add_child(mission_audio)
		mission_audio.setup(engine, music, ambience, audio.catalog if audio != null else null)
	engine.mission_finished.connect(_on_mission_finished)
	engine.component_destroyed.connect(_on_component_destroyed)
	world.blast_happened.connect(func(_c: Vector2, _r: float) -> void: _play("breach_detonate"))
	world.impact_happened.connect(_on_impact)
	hud.update_objectives.call_deferred(engine.objectives)
	view.operative.set_weapon(engine.selected_weapon_id)
	_update_hint()


func select_weapon(weapon_id: String) -> void:
	if engine.select_weapon(weapon_id):
		view.operative.set_weapon(weapon_id)
		_play("weapon_switch")
		_cancel_aim()
		_update_hint()


func pause() -> void:
	if engine == null or not engine.is_active():
		return
	_cancel_aim()
	get_tree().paused = true
	hud.show_pause()


func resume() -> void:
	get_tree().paused = false
	hud.hide_overlay()


func is_paused() -> bool:
	return get_tree().paused


## Android back: close an open panel or pause.
func handle_back() -> void:
	if hud != null and hud.has_overlay() and engine.is_active():
		resume()
	else:
		pause()


func begin_aim(screen_position: Vector2) -> void:
	if engine == null or not engine.is_active() or get_tree().paused:
		return
	_aiming = true
	_since_input = 0.0
	update_aim(screen_position)


func update_aim(screen_position: Vector2) -> void:
	if not _aiming:
		return
	var point: Variant = view.screen_to_plane(screen_position)
	if point == null:
		return
	var offset: Vector2 = point - world.muzzle_position()
	_aim_direction = offset
	_aim_power = clampf(offset.length() / BREACH_FULL_POWER_DISTANCE, 0.0, 1.0)
	if offset.length() < CANCEL_DISTANCE:
		view.hide_preview()
		return
	var weapon := engine.selected_weapon()
	view.operative.set_aim(ViewMapping.direction_angle(offset))
	view.show_preview(world.muzzle_position(), weapon.launch_velocity(offset, _aim_power), float(weapon.stats.gravity_scale), float(weapon.stats.aim_preview_seconds))


## Fires on release when the aim is valid and the weapon is ready. Returns true if it fired.
func release_aim() -> bool:
	if not _aiming:
		return false
	_aiming = false
	view.hide_preview()
	if _aim_direction.length() < CANCEL_DISTANCE:
		return false
	if not engine.can_fire():
		hud.set_hint("Reloading..." if engine.selected_weapon().has_ammo() else "Out of ammunition: switch weapon")
		return false
	var projectile := world.fire(_aim_direction, _aim_power)
	if projectile == null:
		return false
	view.operative.fire()
	_play("breach_launch" if engine.selected_weapon().spec.is_lobbed() else "kinetic_fire")
	_update_hint()
	return true


func _cancel_aim() -> void:
	_aiming = false
	if view != null:
		view.hide_preview()


func _unhandled_input(event: InputEvent) -> void:
	if engine == null:
		return
	if event is InputEventMouseButton and event.button_index == MOUSE_BUTTON_LEFT:
		if event.pressed:
			begin_aim(event.position)
		else:
			release_aim()
		get_viewport().set_input_as_handled()
	elif event is InputEventMouseMotion and _aiming:
		update_aim(event.position)
		get_viewport().set_input_as_handled()


func _process(delta: float) -> void:
	if engine == null:
		return
	_since_input += delta
	hud.update_weapons(engine.weapons, engine.selected_weapon_id)
	hud.update_stats(engine.shots_fired(), engine.definition.recommended_shots, engine.elapsed, engine.definition.target_time)
	var rig := view.operative
	if engine.phase == MissionEngine.Phase.SUCCEEDED:
		rig.set_state(OperativeRig.State.VICTORY)
	elif engine.phase == MissionEngine.Phase.FAILED:
		rig.set_state(OperativeRig.State.DEFEAT)
	elif _aiming:
		rig.set_state(OperativeRig.State.AIM)
	elif engine.selected_weapon().cooldown_remaining > 0.0:
		rig.set_state(OperativeRig.State.RELOAD)
	elif _since_input > IDLE_AFTER:
		rig.set_state(OperativeRig.State.IDLE)
	else:
		rig.set_state(OperativeRig.State.READY)


func _update_hint() -> void:
	if engine.selected_weapon().spec.is_lobbed():
		hud.set_hint("Breach Charge: touch where to throw · farther = stronger · release to fire")
	else:
		hud.set_hint("Kinetic Accelerator: touch the target · release to fire")


func _on_mission_finished(success: bool) -> void:
	_cancel_aim()
	_play("mission_success" if success else "mission_fail")
	_record_result()
	await get_tree().create_timer(RESULT_DELAY).timeout
	if is_inside_tree() and not _result_shown:
		_result_shown = true
		var balance := progress.research_data if progress != null else 0
		hud.show_result(success, engine, last_score, last_research_granted, balance)


## Scores the attempt and stores bests / Research Data (only improvements are granted).
func _record_result() -> void:
	last_score = scoring.score(engine)
	last_research_granted = 0
	if progress == null:
		return
	var optional: Array[String] = []
	for o in engine.objectives.objectives:
		if not o.mandatory and o.status == MissionObjectives.Status.COMPLETE:
			optional.append(o.id)
	last_research_granted = progress.record_mission(engine.definition.id, last_score, engine.shots_fired(), engine.elapsed, optional)
	if save != null:
		var err := save.save_progress(progress)
		if err != OK:
			push_error("MissionScreen: could not save mission result (error %d)" % err)


## Destruction moves goal progress without changing objective status, so refresh here too.
func _on_component_destroyed(component_id: String) -> void:
	if engine.definition.critical_asset_ids().has(component_id):
		_play("core_destroyed")
	elif audio != null:
		audio.play_destroyed(str(engine.definition.component(component_id).get("material", "")))
	hud.update_objectives.call_deferred(engine.objectives)


func _on_impact(_at: Vector2, strength: float, component_id: String) -> void:
	if audio != null:
		audio.play_impact(strength, str(engine.definition.component(component_id).get("material", "")))


func _on_objective_changed(objective_id: String, status: int) -> void:
	hud.update_objectives(engine.objectives)
	var objective := engine.objectives.get_objective(objective_id)
	# Optional goals completed mid-mission get a cue; the mission result has its own stinger.
	if status == MissionObjectives.Status.COMPLETE and engine.is_active() and objective != null and not objective.mandatory:
		_play("objective_complete")


func _play(sound: String) -> void:
	if audio != null:
		audio.play(sound)
