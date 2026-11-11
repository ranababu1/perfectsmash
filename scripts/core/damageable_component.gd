class_name DamageableComponent
extends RefCounted
## Health and progressive damage state of one structural component (a server rack, a support
## beam, the AI core...). Node-free: a physics body or mission layer owns one of these, feeds it
## damage and reacts to its signals (show damage, unfreeze when unstable, remove when destroyed).
##
## States: INTACT -> DAMAGED (below 75%) -> CRITICAL (below 35%: unstable, the physics layer lets
## it move) -> DESTROYED (0). States only ever advance.

signal state_changed(component: DamageableComponent, previous: State, current: State)
signal destroyed(component: DamageableComponent)

enum State { INTACT, DAMAGED, CRITICAL, DESTROYED }

const DAMAGED_BELOW := 0.75
const CRITICAL_BELOW := 0.35

var id := ""
var material: MaterialCatalog.MaterialSpec
var max_health := 1.0
var health := 1.0
## Mission-critical asset (e.g. the AI core). Its objective state lives in the mission layer;
## this flag only identifies it.
var is_critical_asset := false
var state := State.INTACT
var last_damage_type := ""


## `health_scale` lets a level make one piece sturdier or weaker than its material default.
func _init(p_id: String, p_material: MaterialCatalog.MaterialSpec, health_scale: float = 1.0, critical_asset: bool = false) -> void:
	id = p_id
	material = p_material
	max_health = maxf(1.0, p_material.health * maxf(health_scale, 0.01))
	health = max_health
	is_critical_asset = critical_asset


## Applies `raw` damage of a DamageRules type after material resistance. Returns the damage
## actually applied (0 when resisted, below the material minimum, or already destroyed).
func receive_damage(raw: float, damage_type: String, penetration: float = 0.0) -> float:
	if state == State.DESTROYED:
		return 0.0
	if not DamageRules.TYPES.has(damage_type):
		push_error("DamageableComponent %s: unknown damage type '%s'" % [id, damage_type])
		return 0.0
	var resistance := DamageRules.resistance_for(material, damage_type)
	var amount := DamageRules.resisted_damage(raw, resistance, penetration, material.min_damage)
	# A critical asset is never finished by a collapse alone: falls and debris leave it at 1 health
	# (critical, exposed); a weapon hit or a blast must finish it (approved Batch 5 rule, applied to
	# every chapter on 2026-11-11). Leaving the mission area still destroys it (force_destroy).
	if is_critical_asset and damage_type == DamageRules.TYPE_STRUCTURAL:
		amount = minf(amount, health - 1.0)
	if amount <= 0.0:
		return 0.0
	var applied := minf(amount, health)
	health -= applied
	last_damage_type = damage_type
	_update_state()
	return applied


## Destroys the component regardless of health (e.g. it fell out of the play area).
func force_destroy(cause: String) -> void:
	if state == State.DESTROYED:
		return
	health = 0.0
	last_damage_type = cause
	_update_state()


func health_fraction() -> float:
	return health / max_health


func is_destroyed() -> bool:
	return state == State.DESTROYED


## Unstable components are still standing but should be released to physics.
func is_unstable() -> bool:
	return state == State.CRITICAL


## The secondary blast this component causes now that it is destroyed, or {} if none.
func secondary_blast() -> Dictionary:
	if state != State.DESTROYED or not material.has_secondary_blast():
		return {}
	return {
		"damage": material.secondary_blast_damage,
		"radius": material.secondary_blast_radius,
		"impulse": material.secondary_blast_impulse,
	}


static func state_for_fraction(fraction: float) -> State:
	if fraction <= 0.0:
		return State.DESTROYED
	if fraction < CRITICAL_BELOW:
		return State.CRITICAL
	if fraction < DAMAGED_BELOW:
		return State.DAMAGED
	return State.INTACT


func _update_state() -> void:
	var next := state_for_fraction(health_fraction())
	if next <= state:
		return
	var previous := state
	state = next
	state_changed.emit(self, previous, next)
	if next == State.DESTROYED:
		destroyed.emit(self)
