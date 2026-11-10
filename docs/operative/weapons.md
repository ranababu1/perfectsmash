# Weapons: tuning table

Source of truth: `data/weapons.json`, computed through `WeaponCatalog.WeaponSpec.effective_stats`.
Units: speeds and radii in px (px/s for speed), cooldown and fuse in seconds, damage in the
component-damage system's units. Upgrade levels are 0 (base) to 3. One level of one attribute
is applied at a time in the tables below; attributes touch different stats and compose
independently. Upgrade costs (Research Data) are 30 / 60 / 100 for every attribute.

Values below were derived by hand from the JSON (multipliers and adds as in `effective_stats`);
they were not printed from a running game in this pass (see "Measured behaviour").

## Kinetic Accelerator (direct, unlocked chapter 1)

Base: launch speed 1700 (fixed, aim picks direction only), gravity scale 0.25, projectile radius 9,
mass 4, impact damage 90, penetration 0.0, no blast, ammunition 24 (missions override, Helix
uses 14), cooldown 1.0, aim preview 0.6.

| Upgrade (stat) | L0 | L1 | L2 | L3 |
|---|---|---|---|---|
| impact_energy (impact_damage, x) | 90 | 103.5 | 117 | 135 |
| penetration (penetration, +) | 0.0 | 0.1 | 0.2 | 0.3 |
| targeting_assistance (aim_preview_seconds, +) | 0.60 | 0.75 | 0.90 | 1.05 |
| energy_efficiency (cooldown, x) | 1.00 | 0.90 | 0.80 | 0.70 |

Role: precision, single-component pressure. Flat, fast trajectory, so it is the tool for hitting
a specific brace, joint or exposed component; it cannot clear mass on its own. Frequent shots
(1 s cooldown) and a deep magazine make it the opening and finishing weapon.

## Breach Charge launcher (lobbed, unlocked chapter 1)

Base: launch speed 950 max / 350 min (aim power 0-1 interpolates), gravity scale 1.0, projectile
radius 13, mass 3, contact impact damage 10, blast damage 160, blast radius 140, blast impulse 900,
blast edge falloff 0.25, fuse 2.5 s (air burst if nothing is hit), ammunition 3, cooldown 2.2,
aim preview 0.35.

| Upgrade (stat) | L0 | L1 | L2 | L3 |
|---|---|---|---|---|
| blast_efficiency (blast_damage, x) | 160 | 184 | 208 | 240 |
| energy_capacity (ammunition, +) | 3 | 4 | 5 | 6 |
| targeting_assistance (aim_preview_seconds, +) | 0.35 | 0.45 | 0.55 | 0.65 |
| energy_efficiency (cooldown, x) | 2.20 | 1.98 | 1.76 | 1.54 |

Capacity adds on top of the mission allowance (`WeaponState._init`).

Role: area damage and structural disruption. The arc lets it reach behind cover and drop onto
supports; the blast impulse moves debris, and the fuse lets a throw burst in the air. Scarce
ammunition (3) and a long cooldown mean each charge should be placed deliberately, usually on
a load-bearing cluster or a group of components.

## Combined feel

The Kinetic Accelerator is the cheap, accurate, fast tool; the Breach Charge is the scarce
heavy tool. The mission design intent in the data is that charges do the structural work
and kinetic rounds finish exposed components.

## Measured behaviour

Not captured in this pass: the environment for this task had no shell, so
`tools/regression/tactics_probe.gd` was not run. Command for whoever can run it (read-only,
probe belongs to performance-qa):

    godot_console --headless --fixed-fps 60 -s tools/regression/tactics_probe.gd

Per `docs/instructions.md` section 11, no balance change is proposed without measured evidence,
so there are no tuning proposals in this document. Values are unchanged from `data/weapons.json`.
