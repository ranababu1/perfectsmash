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
