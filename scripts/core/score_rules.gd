class_name ScoreRules
extends RefCounted
## Star medals for a completed level, based on shots used relative to par.

const MAX_STARS := 3


static func stars_for(shots_used: int, par: int) -> int:
	if shots_used <= par:
		return 3
	if shots_used == par + 1:
		return 2
	return 1
