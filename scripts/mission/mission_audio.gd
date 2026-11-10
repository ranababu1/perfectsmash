class_name MissionAudio
extends Node
## Mission music and ambience from the mission's audio plan (data/audio.json "missions"):
## intensity steps that rise with the action (preparation -> first shot -> first destruction),
## a critical layer while a critical asset is CRITICAL, victory/defeat stingers, and an ambience
## bed. Drives the existing MusicDirector instances; plays nothing itself and owns no rules.

const STEP_FADE := 2.0
const STINGER_FADE := 0.6

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
