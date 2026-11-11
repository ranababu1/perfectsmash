class_name MissionAudio
extends Node
## Mission music and ambience from the mission's audio plan (data/audio.json "missions"):
## intensity steps that rise with the action (preparation -> first shot -> first destruction),
## a critical layer while a critical asset is CRITICAL, victory/defeat stingers, and an ambience
## bed. Drives the existing MusicDirector instances and owns no rules.
##
## It also holds the per-weapon sound table (`WEAPON_SOUNDS`): which data/audio.json sound ids a
## weapon uses for firing, striking, blasting and becoming ready again, with a pitch for each so
## weapons that share a file set (and the existing two) still sound apart. MissionScreen plays
## them through AudioService with `play_weapon_event`; weapon switching keeps "weapon_switch".

const STEP_FADE := 2.0
const STINGER_FADE := 0.6
## weapon id -> event -> [sound id, pitch] pairs, all played together.
## Events: "fire" (on launch), "strike" (each direct strike), "blast" (the weapon's own blast),
## "ready" (cooldown finished). Every id exists in data/audio.json `sounds`.
const WEAPON_SOUNDS := {
	"kinetic_accelerator": {"fire": [["kinetic_fire", 1.0]], "ready": [["reload_ready", 1.0]]},
	"breach_charge": {"fire": [["breach_launch", 1.0]], "blast": [["breach_detonate", 1.0]], "ready": [["reload_ready", 1.0]]},
	"penetrator": {
		"fire": [["penetrator_fire", 1.15]], "strike": [["penetrator_impact", 1.1]], "ready": [["penetrator_ready", 1.0]],
	},
	"pulse_cannon": {
		"fire": [["pulse_cannon_fire", 1.0]], "blast": [["pulse_cannon_discharge", 1.1]], "ready": [["pulse_cannon_ready", 1.0]],
	},
	"disruptor": {
		"fire": [["disruptor_fire", 0.85]], "blast": [["disruptor_emp", 1.0], ["disruptor_emp_crackle", 1.0]], "ready": [["disruptor_ready", 0.9]],
	},
	"temporal_lance": {
		"fire": [["temporal_lance_fire", 0.8]], "strike": [["temporal_lance_impact", 0.9]], "ready": [["temporal_lance_ready", 1.0]],
	},
}

var music: MusicDirector
var ambience: MusicDirector
var engine: MissionEngine
var plan := {}
## Index into plan.intensity of the cue now playing (-1 before start).
var step := -1


func setup(p_engine: MissionEngine, p_music: MusicDirector, p_ambience: MusicDirector, catalog: AudioCatalog) -> void:
	engine = p_engine
	music = p_music
	ambience = p_ambience
	plan = catalog.plan_for(engine.definition.id, engine.definition.chapter) if catalog != null else {}
	if plan.is_empty():
		return
	engine.weapon_fired.connect(func(_w: String, _v: Vector2, _s: Dictionary) -> void: raise_to(1))
	engine.component_destroyed.connect(func(_id: String) -> void: raise_to(2))
	engine.critical_asset_changed.connect(_on_critical_asset_changed)
	engine.mission_finished.connect(_on_mission_finished)
	raise_to(0)
	if ambience != null and not str(plan.ambience).is_empty():
		ambience.play_cue(plan.ambience, 2.5)


## The [sound id, pitch] pairs for a weapon event (empty when the weapon has none for it).
static func weapon_sounds(weapon_id: String, event: String) -> Array:
	return (WEAPON_SOUNDS.get(weapon_id, {}) as Dictionary).get(event, [])


## Plays a weapon event through `audio` (no-op without it or when the weapon has no such sound).
static func play_weapon_event(audio: AudioService, weapon_id: String, event: String) -> void:
	if audio == null:
		return
	for pair: Array in weapon_sounds(weapon_id, event):
		audio.play(str(pair[0]), 0.0, float(pair[1]))


## Moves the music up to intensity step `target` (never down during a mission).
func raise_to(target: int) -> void:
	var steps: Array = plan.get("intensity", [])
	if music == null or steps.is_empty():
		return
	target = mini(target, steps.size() - 1)
	if target <= step:
		return
	var keep := step >= 0
	step = target
	music.play_cue(steps[step], 2.5 if not keep else STEP_FADE, keep)


func _on_critical_asset_changed(_id: String, state: int) -> void:
	if music == null:
		return
	if state == DamageableComponent.State.CRITICAL and not str(plan.critical_layer).is_empty():
		music.set_layer(plan.critical_layer, 1.5)
	elif state == DamageableComponent.State.DESTROYED:
		music.set_layer("", 1.0)


func _on_mission_finished(success: bool) -> void:
	if music == null:
		return
	music.set_layer("", STINGER_FADE)
	var stinger: String = plan.victory if success else plan.defeat
	if not stinger.is_empty():
		music.play_cue(stinger, STINGER_FADE)
