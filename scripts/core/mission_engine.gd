class_name MissionEngine
extends RefCounted
## Mission rules for one attempt, independent of nodes and rendering. Composes:
##   WeaponState per available weapon (selection, ammunition, reload cooldown),
##   DamageableComponent per facility component, StructuralDependencySystem, MissionObjectives.
## The physics/presentation layer calls fire(), apply_damage(), destroy_component() and
## tick(delta, scene_settled), and reacts to the signals (spawn projectiles, release bodies,
## apply secondary blasts, update the HUD).
##
## Flow: weapons fire whenever reloaded, even while debris moves. Objectives are evaluated
## continuously. Success needs every mandatory goal complete and the scene settled; failure is a
## broken mandatory constraint, or no ammunition left once the scene has settled.

signal weapon_selected(weapon_id: String)
signal weapon_fired(weapon_id: String, velocity: Vector2, stats: Dictionary)
signal ammo_changed(weapon_id: String, ammo: int, capacity: int)
signal component_state_changed(component_id: String, previous: int, current: int)
signal component_destroyed(component_id: String)
## Components that lost their required supports; the physics layer lets them fall.
signal components_released(component_ids: Array[String])
## A destroyed component with a secondary effect (e.g. a power cell); the physics layer applies
## the blast at the component's position.
signal secondary_blast_requested(component_id: String, blast: Dictionary)
signal critical_asset_changed(component_id: String, state: int)
signal objective_changed(objective_id: String, status: int)
signal mission_finished(success: bool)
## Mandatory goals are complete and the scene has settled, but optional goals remain. Emitted at
## most once per mission; the mission stays active until continue_mission() or finish_mission().
signal decision_requested
## The last standing shield emitter of `component_id` fell: it can be damaged from now on.
signal shield_dropped(component_id: String)

enum Phase { ACTIVE, SUCCEEDED, FAILED }

var definition: MissionDefinition
var phase := Phase.ACTIVE
var elapsed := 0.0
## Shots whose impact or blast damaged at least one component (accuracy for scoring).
var effective_shots := 0
var weapons := {}
var weapon_order: Array[String] = []
var selected_weapon_id := ""
## Set when a shot used the selected weapon's last round; apply_pending_auto_select() performs the
## switch once the shot has resolved. A manual selection clears it.
var auto_select_pending := false
var components := {}
var structure: StructuralDependencySystem
var objectives: MissionObjectives
var _total_health := 0.0
## True while the decision prompt is open (the clock is held and the mission cannot finish on
## its own). The prompt is offered once; after Continue, a later finish needs finish_mission(),
## all optional goals complete, or the ammunition running out.
var awaiting_decision := false
var _decision_offered := false
## component id -> Array[String] of shield emitter ids (only shielded components are listed).
var _shields := {}


## `upgrade_levels`: weapon id -> {attribute: level}. Callers must pass a valid definition.
func _init(p_definition: MissionDefinition, materials: MaterialCatalog, weapon_catalog: WeaponCatalog, upgrade_levels: Dictionary = {}) -> void:
	definition = p_definition
	for weapon_id in definition.weapon_order:
		var spec := weapon_catalog.get_weapon(weapon_id)
		if spec == null:
			push_error("MissionEngine: unknown weapon '%s'" % weapon_id)
			continue
		weapons[weapon_id] = WeaponState.new(spec, int(definition.weapon_ammunition[weapon_id]), upgrade_levels.get(weapon_id, {}))
		weapon_order.append(weapon_id)
	selected_weapon_id = weapon_order[0] if not weapon_order.is_empty() else ""
	for c in definition.components:
		var material := materials.get_material(c.material)
		if material == null:
			push_error("MissionEngine: unknown material '%s'" % c.material)
			continue
		var component := DamageableComponent.new(c.id, material, c.health_scale, c.critical_asset)
		component.state_changed.connect(_on_component_state_changed)
		component.destroyed.connect(_on_component_destroyed)
		components[c.id] = component
		_total_health += component.max_health
	structure = StructuralDependencySystem.from_entries(definition.structure_entries())
	objectives = MissionObjectives.new(definition.objectives)
	for c in definition.components:
		if not (c.get("shielded_by", []) as Array).is_empty():
			_shields[c.id] = c.shielded_by


func is_active() -> bool:
	return phase == Phase.ACTIVE


func selected_weapon() -> WeaponState:
	return weapons.get(selected_weapon_id)


## Selects `weapon_id`. An empty weapon is never left selected while another has ammunition:
## asking for one selects usable_weapon_after(weapon_id) instead. Returns true when a weapon with
## ammunition is selected afterwards (the requested one or its fallback); false for an unknown
## weapon, an inactive mission, or when no weapon has ammunition (the selection is then kept and
## the normal out-of-ammunition failure applies).
func select_weapon(weapon_id: String) -> bool:
	if not weapons.has(weapon_id) or not is_active():
		return false
	var target := weapon_id if (weapons[weapon_id] as WeaponState).has_ammo() else usable_weapon_after(weapon_id)
	if target.is_empty():
		return false
	auto_select_pending = false
	_set_selected(target)
	return true


## The weapon that replaces `weapon_id` when it is empty: the first weapon with ammunition in
## mission weapon order, starting after `weapon_id` and wrapping around (deterministic). Reload
## cooldowns do not matter: a reloading weapon with ammunition is still usable. "" when no
## other weapon has ammunition.
func usable_weapon_after(weapon_id: String) -> String:
	var start := weapon_order.find(weapon_id)
	for step in range(1, weapon_order.size() + 1):
		var id := weapon_order[(start + step) % weapon_order.size()]
		if id != weapon_id and (weapons[id] as WeaponState).has_ammo():
			return id
	return ""


## True when the selected weapon is out of ammunition and another weapon can replace it.
func needs_fallback() -> bool:
	var weapon := selected_weapon()
	return is_active() and weapon != null and not weapon.has_ammo() and not usable_weapon_after(selected_weapon_id).is_empty()


## Applies the automatic switch that fire() scheduled when it used the selected weapon's last
## round. The physics layer calls it once that shot has resolved (no round in flight), so the
## selection never changes mid-shot. Returns the newly selected weapon id, or "".
func apply_pending_auto_select() -> String:
	if not auto_select_pending:
		return ""
	auto_select_pending = false
	if not needs_fallback():
		return ""
	var target := usable_weapon_after(selected_weapon_id)
	_set_selected(target)
	return target


func _set_selected(weapon_id: String) -> void:
	if weapon_id != selected_weapon_id:
		selected_weapon_id = weapon_id
		weapon_selected.emit(weapon_id)


func can_fire() -> bool:
	return is_active() and not awaiting_decision and selected_weapon() != null and selected_weapon().can_fire()


## Fires the selected weapon. Returns the launch velocity, or Vector2.ZERO when the shot is
## refused (mission over, reloading, out of ammunition or no aim direction).
func fire(direction: Vector2, power: float = 1.0) -> Vector2:
	var weapon := selected_weapon()
	if not can_fire():
		return Vector2.ZERO
	var velocity := weapon.launch_velocity(direction, power)
	if velocity == Vector2.ZERO or not weapon.fire():
		return Vector2.ZERO
	weapon_fired.emit(weapon.id(), velocity, weapon.stats)
	ammo_changed.emit(weapon.id(), weapon.ammo, weapon.ammo_capacity)
	# The last round: switch to the next usable weapon once this shot has resolved.
	if not weapon.has_ammo():
		auto_select_pending = true
	_evaluate(false)
	return velocity


func record_effective_shot() -> void:
	if is_active():
		effective_shots += 1


func shots_fired() -> int:
	var total := 0
	for weapon: WeaponState in weapons.values():
		total += weapon.shots_fired
	return total


func has_ammo_left() -> bool:
	return weapons.values().any(func(w: WeaponState) -> bool: return w.has_ammo())


## Advances cooldowns and the mission clock, then re-evaluates. `scene_settled` comes from the
## physics layer (no projectile in flight, nothing moving).
func tick(delta: float, scene_settled: bool) -> void:
	if not is_active():
		return
	if not awaiting_decision:
		elapsed += maxf(delta, 0.0)
	for weapon: WeaponState in weapons.values():
		weapon.tick(delta)
	_evaluate(scene_settled)


## Routes damage to a component. Returns the damage applied after resistance.
## `source` is the weapon id that caused the damage ("" for collisions and secondary blasts).
## Shielded components and materials restricted by `vulnerable_to` ignore damage they don't accept.
func apply_damage(component_id: String, raw: float, damage_type: String, penetration: float = 0.0, source: String = "") -> float:
	var component: DamageableComponent = components.get(component_id)
	if component == null:
		push_warning("MissionEngine: damage for unknown component '%s'" % component_id)
		return 0.0
	if not is_active() or is_shielded(component_id) or not component.material.accepts_damage_from(source):
		return 0.0
	return component.receive_damage(raw, damage_type, penetration)


## True while at least one of the component's shield emitters is not destroyed.
func is_shielded(component_id: String) -> bool:
	for emitter: String in _shields.get(component_id, []):
		if component_state(emitter) != DamageableComponent.State.DESTROYED:
			return true
	return false


## Components currently protected by a standing shield emitter.
func shielded_components() -> Array[String]:
	var ids: Array[String] = []
	for id: String in _shields:
		if is_shielded(id) and component_state(id) != DamageableComponent.State.DESTROYED:
			ids.append(id)
	return ids


## Destroys a component outright (e.g. it fell out of the mission area).
func destroy_component(component_id: String, cause: String) -> void:
	var component: DamageableComponent = components.get(component_id)
	if component != null and is_active():
		component.force_destroy(cause)


func component_state(component_id: String) -> int:
	var component: DamageableComponent = components.get(component_id)
	return component.state if component != null else -1


func critical_asset_states() -> Dictionary:
	var states := {}
	for component: DamageableComponent in components.values():
		if component.is_critical_asset:
			states[component.id] = component.state
	return states


## Share of the facility's total health that has been destroyed (0-1).
func structural_damage_fraction() -> float:
	if _total_health <= 0.0:
		return 0.0
	var lost := 0.0
	for component: DamageableComponent in components.values():
		lost += component.max_health - component.health
	return clampf(lost / _total_health, 0.0, 1.0)


func _snapshot() -> Dictionary:
	var destroyed := {}
	for component: DamageableComponent in components.values():
		if component.is_destroyed():
			destroyed[component.id] = true
	return {
		"destroyed": destroyed,
		"structural_damage": structural_damage_fraction(),
		"shots": shots_fired(),
		"elapsed": elapsed,
	}


func _evaluate(scene_settled: bool) -> void:
	if not is_active():
		return
	for o in objectives.update(_snapshot()):
		objective_changed.emit(o.id, o.status)
	if objectives.mandatory_failed():
		_finish(false)
	elif objectives.mandatory_goals_complete():
		if not scene_settled or awaiting_decision:
			return
		if objectives.pending_optional_goals().is_empty() or (_decision_offered and not has_ammo_left()):
			_finish(true)
		elif not _decision_offered:
			_decision_offered = true
			awaiting_decision = true
			decision_requested.emit()
	elif scene_settled and not has_ammo_left():
		_finish(false)


## True once the primary objective is done, so the player may end the mission early.
func can_finish_early() -> bool:
	return is_active() and objectives.mandatory_goals_complete()


## Decision prompt: Continue. Keeps the mission active; the prompt is not offered again.
func continue_mission() -> void:
	awaiting_decision = false


## Decision prompt (or a later Finish action): ends the mission successfully. Unfinished optional
## goals fail (finalize). Returns false when the primary objective is not complete.
func finish_mission() -> bool:
	if not can_finish_early():
		return false
	awaiting_decision = false
	_finish(true)
	return true


func _finish(success: bool) -> void:
	phase = Phase.SUCCEEDED if success else Phase.FAILED
	for o in objectives.finalize(success):
		objective_changed.emit(o.id, o.status)
	mission_finished.emit(success)


func _on_component_state_changed(component: DamageableComponent, previous: int, current: int) -> void:
	component_state_changed.emit(component.id, previous, current)
	if component.is_critical_asset:
		critical_asset_changed.emit(component.id, current)


func _on_component_destroyed(component: DamageableComponent) -> void:
	component_destroyed.emit(component.id)
	for shielded: String in _shields:
		if (_shields[shielded] as Array).has(component.id) and not is_shielded(shielded):
			shield_dropped.emit(shielded)
	var released := structure.fail(component.id)
	if not released.is_empty():
		components_released.emit(released)
	var blast := component.secondary_blast()
	if not blast.is_empty():
		secondary_blast_requested.emit(component.id, blast)
	_evaluate(false)
