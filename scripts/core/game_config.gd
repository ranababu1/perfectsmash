class_name GameConfig
extends RefCounted
## Central tuning values shared by gameplay rules, the physics session and tests.
## Units: pixels, seconds, Godot physics mass units.

# World layout (logical 1280x720 landscape canvas).
const WORLD_WIDTH := 1280.0
const WORLD_HEIGHT := 720.0
const GROUND_TOP := 640.0
## Bodies outside these bounds are removed; targets removed this way count as destroyed.
const KILL_BOUNDS := Rect2(-300.0, -2000.0, 1880.0, 2900.0)

# Launching.
const MAX_LAUNCH_SPEED := 1300.0
const MAX_DRAG_DISTANCE := 200.0
const MIN_DRAG_DISTANCE := 24.0
## Seconds of flight shown by the partial trajectory preview (not a full solve aid).
const PREVIEW_DURATION := 0.3
const PREVIEW_DOTS := 7
const PROJECTILE_RADIUS := 18.0
const PROJECTILE_MASS := 6.0

# Materials: density is mass per square pixel.
const MATERIALS := {
	"wood": {"density": 0.0010, "friction": 0.8, "bounce": 0.05},
	"stone": {"density": 0.0030, "friction": 0.9, "bounce": 0.0},
	"glass": {"density": 0.0008, "friction": 0.4, "bounce": 0.1},
}
const TARGET_MASS := 1.0

# Destruction: contact impulse above which a body breaks (once armed by the first launch).
const TARGET_BREAK_IMPULSE := 220.0
const GLASS_BREAK_IMPULSE := 300.0
const IMPACT_SOUND_IMPULSE := 120.0
## Relative speed (px/s) at which a projectile touching a target pops it.
const TARGET_PROJECTILE_HIT_SPEED := 200.0
## Velocity change in one physics step (px/s) that breaks a target. A free fall from about
## 80px reaches this, so a target knocked off a pedestal of that height breaks on landing.
const TARGET_BREAK_VELOCITY_CHANGE := 400.0

# Simulation settling (see SimulationMonitor).
const SETTLE_LINEAR_SPEED := 6.0
const SETTLE_ANGULAR_SPEED := 0.12
const SETTLE_HOLD_TIME := 0.5
const SETTLE_MIN_TIME := 0.6
const SIMULATION_TIMEOUT := 10.0
