class_name MissionText
extends RefCounted
## Player-facing wording for a level's goal, constraints and ammunition, shared by the HUD and briefing.


static func objective(def: LevelDefinition) -> String:
	match def.objective_type:
		LevelDefinition.OBJECTIVE_TOPPLE:
			return "Bring every block below the green line"
		LevelDefinition.OBJECTIVE_DELIVER:
			var crates := def.cargo_count()
			return "Deliver the supply crate to the drop zone" if crates == 1 else "Deliver all %d crates to the drop zone" % crates
	var count := def.targets.size()
	return "Knock out the red core" if count == 1 else "Knock out all %d red cores" % count


## "Keep the blue drone safe", or "" when the level has no allies.
static func constraint(def: LevelDefinition) -> String:
	match def.allies.size():
		0:
			return ""
		1:
			return "Keep the blue drone safe"
	return "Keep all %d blue drones safe" % def.allies.size()


static func ammo_name(kind: String) -> String:
	match kind:
		"heavy":
			return "Heavy"
		"blast":
			return "Blast"
	return "Standard"


## "3 shots · par 1 · Heavy, Blast, Standard" (ammo listed only when not all standard).
static func shots_summary(def: LevelDefinition) -> String:
	var text := "%d shot%s  ·  par %d" % [def.shots, "" if def.shots == 1 else "s", def.par]
	var kinds := PackedStringArray()
	var special := false
	for i in def.shots:
		var kind := def.ammo_for_shot(i)
		special = special or kind != GameConfig.DEFAULT_AMMO
		kinds.append(ammo_name(kind))
	if special:
		text += "  ·  " + ", ".join(kinds)
	return text


## Short notes on the mechanics present in a level, shown in the briefing ("intel").
static func intel(def: LevelDefinition) -> PackedStringArray:
	var notes := PackedStringArray()
	match def.objective_type:
		LevelDefinition.OBJECTIVE_DELIVER:
			notes.append("The crate must come to rest inside the green zone.")
		LevelDefinition.OBJECTIVE_TOPPLE:
			notes.append("Every block must end up below the green line.")
	if not def.allies.is_empty():
		notes.append("Breaking a blue drone fails the mission.")
	if def.uses_material("explosive"):
		notes.append("Orange crates explode and set off crates nearby.")
	if def.statics.any(func(s: Dictionary) -> bool: return s.kind == "bumper"):
		notes.append("Purple pads bounce the ball back hard.")
	if def.uses_material("glass"):
		notes.append("Glass shatters on a hard hit.")
	var kinds := {}
	for i in def.shots:
		kinds[def.ammo_for_shot(i)] = true
	if kinds.has("heavy"):
		notes.append("Heavy shot: a big, heavy ball that shoves stone.")
	if kinds.has("blast"):
		notes.append("Blast shot: explodes on its first contact.")
	if notes.is_empty() and def.uses_material("stone"):
		notes.append("Stone is heavy. Let it fall on something.")
	return notes
