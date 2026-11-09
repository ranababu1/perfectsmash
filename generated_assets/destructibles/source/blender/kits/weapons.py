"""Operative arsenal: Kinetic Accelerator and Breach Charge launcher in three upgrade tiers, their
projectiles, and concept-level blockouts of the later weapons.
Convention (contract 11): origin at the grip, barrel along +X, up +Z (Godot +Y), `muzzle` empty at the
bore exit. Front of the weapon (towards the game camera) is -Y."""
import math
from mathutils import Vector
import tfjkit as K


def _grip(B, x=0.0, z=0.0):
    ob = B.box((x - 0.012, 0, z - 0.065), (0.042, 0.034, 0.13), "rubber", "frame", 0.008)
    K.rotate(ob, -16, "Y", (x, 0, z))
    B.prism([(x + 0.02, z - 0.005), (x + 0.085, z - 0.005), (x + 0.085, z - 0.018), (x + 0.03, z - 0.06),
             (x + 0.018, z - 0.05)], 0.02, 0.0, "frame", "frame", 0.0)  # trigger guard
    B.box((x + 0.04, 0, z - 0.02), (0.008, 0.012, 0.03), "trim", "greeble", 0.0)


def kinetic_accelerator(B, rng, spec):
    """SV-02: long angular gunmetal shell, exposed ribbed coil stack in a side channel, ported muzzle,
    skeletal stock with a thumbhole, thin cyan light lines."""
    tier = spec["tier"]
    ext = 0.05 * (tier - 1)
    xf = 0.5 + ext                       # front of the shroud
    _grip(B)
    # rear receiver and stock (side profile extruded across the width)
    B.prism([(-0.44, 0.0), (-0.44, 0.115), (-0.3, 0.145), (0.06, 0.15), (0.13, 0.168), (0.13, 0.03),
             (-0.06, 0.02), (-0.2, 0.02), (-0.3, 0.06), (-0.36, 0.06), (-0.36, 0.0)], 0.07, 0.0, "panel", "frame", 0.006)
    B.prism([(-0.44, -0.1), (-0.44, 0.0), (-0.36, 0.0), (-0.36, -0.06), (-0.12, -0.012), (-0.08, -0.012),
             (-0.08, 0.02), (-0.06, 0.02), (-0.06, -0.03), (-0.13, -0.045)], 0.05, 0.0, "frame", "frame", 0.004)
    B.box((-0.445, 0, -0.01), (0.02, 0.06, 0.2), "rubber", "frame", 0.006)  # butt pad
    # upper shroud over the coils and a lower rail
    B.prism([(0.13, 0.168), (0.13, 0.12), (xf, 0.11), (xf, 0.135), (xf - 0.06, 0.155), (0.3, 0.165)], 0.075, 0.0,
            "panel", "frame", 0.004)
    B.prism([(0.13, 0.03), (xf, 0.04), (xf, 0.062), (0.13, 0.06)], 0.07, 0.0, "frame", "frame", 0.004)
    B.box(((0.13 + xf) / 2, 0.03, 0.086), (xf - 0.13, 0.012, 0.05), "dark", "internal", 0.0)  # back wall of channel
    B.box(((0.13 + xf) / 2, -0.033, 0.054), (xf - 0.16, 0.006, 0.014), "panel", "cover", 0.0)  # lower skirt
    # ribbed coil stack (one lathe with a zig-zag profile)
    n = int((xf - 0.16) / 0.012)
    prof = [(0, 0.0)]
    for i in range(n + 1):
        prof.append((0.027 if i % 2 == 0 else 0.022, i * 0.012))
    prof.append((0, n * 0.012))
    B.lathe(prof, (0.15, 0, 0.087), 10, "accent", "internal", axis="X")
    K.translate(B.parts[-1], (0, 0, 0))
    B.cyl((0.145, 0, 0.087), 0.03, 0.012, "X", 10, "trim", "greeble", 0.0)
    B.cyl((xf - 0.006, 0, 0.087), 0.03, 0.012, "X", 10, "trim", "greeble", 0.0)
    # muzzle: barrel extension with ports
    B.cyl((xf + 0.05, 0, 0.087), 0.022, 0.1, "X", 12, "dark", "frame", 0.0)
    B.cyl((xf + 0.09, 0, 0.087), 0.026, 0.035, "X", 12, "frame", "frame", 0.0)
    for k in range(3):
        B.box((xf + 0.035 + k * 0.022, -0.02, 0.087), (0.01, 0.006, 0.012), "internal", "greeble", 0.0)
    B.cyl((xf + 0.108, 0, 0.087), 0.012, 0.004, "X", 10, "emit", "emit", 0.0)
    # cyan light lines and side details
    B.light_strip((0.0, -0.036, 0.07), (0.22, 0.003, 0.005), "emit")
    B.light_strip((0.3, -0.039, 0.122), (0.12, 0.003, 0.004), "emit")
    B.box((0.02, -0.037, 0.1), (0.14, 0.004, 0.03), "dark", "greeble", 0.0)
    B.box((0.0, -0.039, 0.1), (0.03, 0.003, 0.014), "trim", "greeble", 0.0)
    B.box((-0.03, 0, 0.155), (0.12, 0.03, 0.012), "dark", "greeble", 0.0)  # top sight block
    B.light_strip((0.0, 0, 0.162), (0.02, 0.012, 0.003), "emit")
    if tier >= 2:
        B.box((-0.18, 0, 0.16), (0.16, 0.05, 0.03), "panel", "cover", 0.006)  # capacitor pack
        B.light_strip((-0.18, -0.026, 0.16), (0.12, 0.003, 0.005), "emit")
        B.light_strip((-0.2, -0.037, 0.04), (0.1, 0.003, 0.004), "emit")
    if tier >= 3:
        for k in range(5):
            B.box((0.2 + k * 0.035, 0, 0.172), (0.008, 0.06, 0.016), "trim", "greeble", 0.0)  # heat sinks
        B.box(((0.13 + xf) / 2, -0.04, 0.087), (xf - 0.2, 0.004, 0.004), "emit", "emit", 0.0)
        B.cable_run((-0.25, -0.03, 0.17), (0.1, -0.038, 0.13), 0.015, 0.005, 6)
    for ob in B.parts:
        K.scale(ob, (0.85, 1.0, 0.92))
    return {"muzzle": ((xf + 0.11) * 0.85, 0, 0.087 * 0.92)}


def breach_launcher(B, rng, spec):
    """SV-03: blocky chamfered body, octagonal side drum with an amber-ringed core, front loop bracket
    with amber light slots, carry handle, hazard-striped side panel, short muzzle."""
    tier = spec["tier"]
    _grip(B, -0.04, 0.0)
    B.xprism(K.chamfer_rect(0.12, 0.15, 0.025), -0.26, 0.3, "panel", "frame", 0.0)
    K.translate(B.parts[-1], (0, 0, 0.075))
    B.xprism(K.chamfer_rect(0.14, 0.17, 0.03), -0.34, -0.24, "frame", "frame", 0.0)
    K.translate(B.parts[-1], (0, 0, 0.075))
    B.box((-0.345, 0, 0.075), (0.012, 0.1, 0.12), "rubber", "frame", 0.0)
    # side drum
    dx = 0.1
    B.cyl((dx, -0.06, 0.075), 0.085, 0.03, "Y", 8, "frame", "frame", 0.0)
    B.cyl((dx, -0.078, 0.075), 0.06, 0.012, "Y", 8, "panel", "cover", 0.0)
    B.ring((dx, -0.086, 0.075), 0.04, 0.03, 0.008, "Y", 16, "emit", "emit", 0.0)
    B.cyl((dx, -0.084, 0.075), 0.03, 0.006, "Y", 12, "internal", "greeble", 0.0)
    for k in range(8):
        a = k * math.pi / 4 + math.pi / 8
        B.cyl((dx + 0.072 * math.cos(a), -0.077, 0.075 + 0.072 * math.sin(a)), 0.006, 0.006, "Y", 6, "trim", "greeble", 0.0)
    # front loop bracket with light slots
    B.ring((0.36, 0, 0.075), 0.1, 0.07, 0.12, "Y", 8, "frame", "frame", 0.0)
    K.scale(B.parts[-1], (0.7, 1.0, 1.0), (0.36, 0, 0.075))
    for sx in (-1, 1):
        B.light_strip((0.36 + sx * 0.058, -0.061, 0.075), (0.008, 0.004, 0.07), "emit")
    B.cyl((0.42, 0, 0.075), 0.03, 0.06, "X", 12, "dark", "frame", 0.0)
    B.cyl((0.445, 0, 0.075), 0.034, 0.016, "X", 12, "trim", "frame", 0.0)
    # hazard panel and amber strip
    B.hazard_band((-0.1, -0.06, 0.06), (0.22, 0.006, 0.05), 6)
    B.light_strip((-0.1, -0.063, 0.115), (0.16, 0.004, 0.008), "emit")
    B.light_strip((-0.33, -0.071, 0.075), (0.008, 0.004, 0.08), "emit")
    # carry handle
    for x in (-0.18, 0.2):
        B.box((x, 0, 0.175), (0.03, 0.03, 0.05), "frame", "frame", 0.0)
    B.box((0.01, 0, 0.205), (0.42, 0.03, 0.024), "frame", "frame", 0.0)
    for k in range(4):
        B.box((-0.25 + k * 0.03, -0.061, 0.03), (0.012, 0.004, 0.03), "dark", "greeble", 0.0)  # vents
    if tier >= 2:
        B.box((0.08, 0, 0.162), (0.2, 0.08, 0.03), "panel", "cover", 0.006)
        B.light_strip((0.08, -0.041, 0.162), (0.14, 0.003, 0.006), "emit")
    if tier >= 3:
        B.ring((0.42, 0, 0.075), 0.04, 0.032, 0.012, "X", 12, "emit", "emit", 0.0)
        B.box((-0.29, 0, 0.17), (0.08, 0.1, 0.05), "panel", "cover", 0.006)
        B.light_strip((-0.29, -0.051, 0.17), (0.05, 0.003, 0.02), "emit")
    return {"muzzle": (0.455, 0, 0.075)}


def kinetic_slug(B, rng, spec):
    B.cyl((0, 0, 0), 0.012, 0.06, "X", 10, "trim", "frame", 0.0, radius2=0.004)
    B.cyl((-0.02, 0, 0), 0.014, 0.03, "X", 10, "emit", "emit", 0.0)
    B.ring((0.0, 0, 0), 0.02, 0.014, 0.006, "X", 10, "emit", "emit", 0.0)


def breach_canister(B, rng, spec):
    """SV-03 canister: barrel capsule, chamfered end caps, banded hazard middle, amber ring lights."""
    L, r = 0.2, 0.058
    B.lathe([(0, -L / 2), (r * 0.6, -L / 2), (r * 0.9, -L / 2 + 0.015), (r, -L / 2 + 0.035), (r, -0.045),
             (r * 0.94, -0.04), (0, -0.04)], (0, 0, 0), 12, "frame", "frame", axis="X")
    B.lathe([(0, 0.04), (r * 0.94, 0.04), (r, 0.045), (r, L / 2 - 0.035), (r * 0.9, L / 2 - 0.015),
             (r * 0.6, L / 2), (0, L / 2)], (0, 0, 0), 12, "frame", "frame", axis="X")
    for k in range(6):
        B.cyl((-0.035 + k * 0.014, 0, 0), r * 0.97, 0.013, "X", 12, "hazard" if k % 2 == 0 else "rubber", "cover", 0.0)
    for x in (-0.043, 0.043):
        B.cyl((x, 0, 0), r * 1.005, 0.006, "X", 12, "emit", "emit", 0.0)
    for x in (-L / 2 - 0.001, L / 2 + 0.001):
        B.cyl((x, 0, 0), r * 0.25, 0.004, "X", 8, "emit", "emit", 0.0)
    for k in range(4):
        a = k * math.pi / 2
        for x in (-0.07, 0.07):
            B.box((x, r * math.cos(a), r * math.sin(a)), (0.03, 0.012, 0.012), "dark", "greeble", 0.0)


# ---------- concept-level blockouts (simple massing only) ----------
def penetrator(B, rng, spec):
    _grip(B)
    B.xprism(K.chamfer_rect(0.06, 0.08, 0.02), -0.25, 0.2, "panel", "frame", 0.0)
    K.translate(B.parts[-1], (0, 0, 0.05))
    B.cyl((0.5, 0, 0.05), 0.01, 0.6, "X", 8, "trim", "frame", 0.0)
    B.box((0.45, 0, 0.05), (0.5, 0.012, 0.05), "frame", "frame", 0.0)
    B.light_strip((0.45, -0.007, 0.05), (0.45, 0.003, 0.008), "emit")
    return {"muzzle": (0.8, 0, 0.05)}


def pulse_cannon(B, rng, spec):
    _grip(B)
    B.cyl((0.18, 0, 0.07), 0.07, 0.5, "X", 16, "panel", "frame", 0.0)
    for k in range(3):
        B.ring((0.05 + k * 0.12, 0, 0.07), 0.08, 0.068, 0.03, "X", 16, "emit", "emit", 0.0)
    B.cyl((0.44, 0, 0.07), 0.05, 0.03, "X", 16, "emit", "emit", 0.0)
    return {"muzzle": (0.46, 0, 0.07)}


def disruptor(B, rng, spec):
    _grip(B)
    B.box((0.08, 0, 0.06), (0.3, 0.07, 0.07), "panel", "frame", 0.01)
    for sz in (-1, 1):
        ob = B.box((0.34, 0, 0.06 + sz * 0.04), (0.22, 0.03, 0.012), "frame", "frame", 0.0)
        K.rotate(ob, -sz * 10, "Y", (0.24, 0, 0.06))
    B.sphere((0.3, 0, 0.06), 0.025, 1, "emit", "emit")
    return {"muzzle": (0.46, 0, 0.06)}


def temporal_lance(B, rng, spec):
    _grip(B)
    B.xprism(K.chamfer_rect(0.06, 0.06, 0.02), -0.3, 0.1, "panel", "frame", 0.0)
    K.translate(B.parts[-1], (0, 0, 0.05))
    B.cyl((0.45, 0, 0.05), 0.015, 0.7, "X", 8, "trim", "frame", 0.0)
    for k in range(4):
        B.ring((0.2 + k * 0.14, 0, 0.05), 0.04 - k * 0.005, 0.032 - k * 0.005, 0.01, "X", 16, "emit", "emit", 0.0)
    return {"muzzle": (0.8, 0, 0.05)}


def W(name, var, fn, purpose, emit="cyan", emit2="amber", typ="WPN", **kw):
    d = dict(id=f"OPR-{typ}-{name}-{var}", chapter="arsenal", folder="shared", category="weapons",
             material="lightweight_alloy", build=fn, emit=emit, emit2=emit2, budget=2500, purpose=purpose,
             kind=name.lower(), ao_dist=0.03, value=1.0, floor=True, frame=1.2, layer="weapon", origin="grip")
    d.update(kw)
    return d


SPECS = [
    W("KINETIC_ACCELERATOR", "A", kinetic_accelerator, "Kinetic Accelerator, tier 1 (base): electromagnetic rail with cyan coil stack", tier=1),
    W("KINETIC_ACCELERATOR", "B", kinetic_accelerator, "Kinetic Accelerator, tier 2: longer rail, more coils, heat sinks", tier=2),
    W("KINETIC_ACCELERATOR", "C", kinetic_accelerator, "Kinetic Accelerator, tier 3: third rail, twin capacitors", tier=3),
    W("BREACH_CHARGE", "A", breach_launcher, "Breach Charge launcher, tier 1: lobbed-canister tube, amber arming band", emit="amber", emit2="amber", tier=1),
    W("BREACH_CHARGE", "B", breach_launcher, "Breach Charge launcher, tier 2: larger drum, sight rail", emit="amber", emit2="amber", tier=2),
    W("BREACH_CHARGE", "C", breach_launcher, "Breach Charge launcher, tier 3: second arming ring, booster cell", emit="amber", emit2="amber", tier=3),
    W("KINETIC_SLUG", "A", kinetic_slug, "Kinetic Accelerator projectile, 0.09 m envelope", typ="PRJ", budget=400, origin="centre"),
    W("BREACH_CANISTER", "A", breach_canister, "Breach Charge canister projectile, 0.13 m envelope", emit="amber", typ="PRJ", budget=600, origin="centre"),
    W("PENETRATOR", "A", penetrator, "Concept blockout only: Penetrator (future weapon)", blockout=True),
    W("PULSE_CANNON", "A", pulse_cannon, "Concept blockout only: Pulse Cannon (future weapon)", blockout=True),
    W("DISRUPTOR", "A", disruptor, "Concept blockout only: Disruptor (future weapon)", emit="white", blockout=True),
    W("TEMPORAL_LANCE", "A", temporal_lance, "Concept blockout only: Temporal Lance (future weapon)", emit="white", blockout=True),
]
