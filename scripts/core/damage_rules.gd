class_name DamageRules
extends RefCounted
## Pure, deterministic damage maths: direct impact, collision (debris, falls, crushing), blast
## damage and knockback with distance falloff, and material resistance. No node access.
## Units: damage points, px, px/s, physics impulse.

const TYPE_IMPACT := "impact"
const TYPE_BLAST := "blast"
## Collisions between structure pieces, falls and crushing.
const TYPE_STRUCTURAL := "structural"
const TYPES := [TYPE_IMPACT, TYPE_BLAST, TYPE_STRUCTURAL]

## Faster-than-reference hits deal a little extra, capped so a lucky frame cannot one-shot steel.
const MAX_SPEED_FACTOR := 1.25
## Contact impulses below this deal no structural damage (settling, resting contacts, light taps).
const COLLISION_DAMAGE_FLOOR := 150.0
const COLLISION_DAMAGE_PER_IMPULSE := 0.08
const MAX_EFFECTIVE_RESISTANCE := 0.95


## Damage of a projectile hit: weapon damage scaled by how fast the projectile was moving
## relative to its launch speed (a spent, slow round hits softly).
static func projectile_impact_damage(base_damage: float, impact_speed: float, reference_speed: float) -> float:
	if base_damage <= 0.0 or reference_speed <= 0.0:
		return 0.0
	return base_damage * clampf(impact_speed / reference_speed, 0.0, MAX_SPEED_FACTOR)


## Damage from a contact between structure pieces (or a piece and the ground).
static func collision_damage(impulse: float) -> float:
	return maxf(0.0, impulse - COLLISION_DAMAGE_FLOOR) * COLLISION_DAMAGE_PER_IMPULSE


## Damage left after the material absorbs its share. Penetration (0-0.9) reduces the absorbed
## share. Results below the material's per-hit minimum are ignored entirely.
static func resisted_damage(raw: float, resistance: float, penetration: float, min_damage: float) -> float:
	if raw <= 0.0:
		return 0.0
	var effective := clampf(resistance, 0.0, MAX_EFFECTIVE_RESISTANCE) * (1.0 - clampf(penetration, 0.0, WeaponCatalog.MAX_PENETRATION))
	var damage := raw * (1.0 - effective)
	return damage if damage >= min_damage else 0.0


static func resistance_for(material: MaterialCatalog.MaterialSpec, damage_type: String) -> float:
	if damage_type == TYPE_BLAST:
		return material.blast_resistance
	if damage_type == TYPE_STRUCTURAL:
		return material.structural_resistance
	return material.impact_resistance


## Blast strength multiplier: 1 at the centre, `edge_fraction` at the radius, 0 beyond it.
static func blast_falloff(distance: float, radius: float, edge_fraction: float) -> float:
	if radius <= 0.0 or distance > radius:
		return 0.0
	return 1.0 - (1.0 - clampf(edge_fraction, 0.0, 1.0)) * (maxf(distance, 0.0) / radius)


static func blast_damage(base_damage: float, distance: float, radius: float, edge_fraction: float) -> float:
	return base_damage * blast_falloff(distance, radius, edge_fraction)


## Knockback impulse on a piece at `point` from a blast at `center`, pushing directly away.
## A piece exactly at the centre is pushed straight up.
static func blast_impulse(base_impulse: float, center: Vector2, point: Vector2, radius: float, edge_fraction: float) -> Vector2:
	var offset := point - center
	var direction := offset.normalized() if offset.length() > 0.001 else Vector2.UP
	return direction * base_impulse * blast_falloff(offset.length(), radius, edge_fraction)


## Distance from a point to the nearest edge of a rotated rectangle (0 when inside), so a blast
## next to a long beam reaches it even if the beam's centre is far away.
static func distance_to_box(point: Vector2, box_center: Vector2, half_size: Vector2, rotation: float) -> float:
	var local := (point - box_center).rotated(-rotation)
	var outside := Vector2(maxf(absf(local.x) - half_size.x, 0.0), maxf(absf(local.y) - half_size.y, 0.0))
	return outside.length()
