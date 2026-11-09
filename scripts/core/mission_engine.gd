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

enum Phase { ACTIVE, SUCCEEDED, FAILED }

var definition: MissionDefinition
var phase := Phase.ACTIVE
var elapsed := 0.0
var weapons := {}
var weapon_order: Array[String] = []
var selected_weapon_id := ""
var components := {}
var structure: StructuralDependencySystem
var objectives: MissionObjectives
var _total_health := 0.0


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


func is_active() -> bool:
	return phase == Phase.ACTIVE


func selected_weapon() -> WeaponState:
	return weapons.get(selected_weapon_id)


func select_weapon(weapon_id: String) -> bool:
	if not weapons.has(weapon_id) or not is_active():
		return false
	if weapon_id != selected_weapon_id:
		selected_weapon_id = weapon_id
		weapon_selected.emit(weapon_id)
	return true


func can_fire() -> bool:
	return is_active() and selected_weapon() != null and selected_weapon().can_fire()


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
	_evaluate(false)
	return velocity


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
	elapsed += maxf(delta, 0.0)
	for weapon: WeaponState in weapons.values():
		weapon.tick(delta)
	_evaluate(scene_settled)


## Routes damage to a component. Returns the damage applied after resistance.
func apply_damage(component_id: String, raw: float, damage_type: String, penetration: float = 0.0) -> float:
	var component: DamageableComponent = components.get(component_id)
	if component == null:
		push_warning("MissionEngine: damage for unknown component '%s'" % component_id)
		return 0.0
	if not is_active():
		return 0.0
	return component.receive_damage(raw, damage_type, penetration)


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
		if scene_settled:
			_finish(true)
	elif scene_settled and not has_ammo_left():
		_finish(false)


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
	var released := structure.fail(component.id)
	if not released.is_empty():
		components_released.emit(released)
	var blast := component.secondary_blast()
	if not blast.is_empty():
		secondary_blast_requested.emit(component.id, blast)
	_evaluate(false)
