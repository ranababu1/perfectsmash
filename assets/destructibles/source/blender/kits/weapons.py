"""Operative arsenal: Kinetic Accelerator and Breach Charge launcher in three upgrade tiers, their
projectiles, and concept-level blockouts of the later weapons.
Convention (contract 11): origin at the grip, barrel along +X, up +Z (Godot +Y), `muzzle` empty at the
bore exit. Front of the weapon (towards the game camera) is -Y."""
import math
from mathutils import Vector
import tfjkit as K


def _grip(B, x=0.0, z=0.0):
    """Shared operative grip (every weapon): raked chamfered rubber grip with finger ridges, a
    trigger guard bridged to the frame, the trigger and a thumb rest. Hand socket at (x, 0, z)."""
    ob = B.prism([(x - 0.034, z + 0.0), (x + 0.012, z + 0.0), (x + 0.004, z - 0.06), (x - 0.006, z - 0.125),
                  (x - 0.05, z - 0.125), (x - 0.044, z - 0.06)], 0.034, 0.0, "rubber", "frame", 0.006)
    for k in range(3):
        B.box((x - 0.002 + k * -0.003, -0.0, z - 0.03 - k * 0.028), (0.008, 0.036, 0.012), "dark", "greeble", 0.0)
    B.prism([(x + 0.012, z + 0.0), (x + 0.085, z + 0.0), (x + 0.085, z - 0.014), (x + 0.04, z - 0.058),
             (x + 0.008, z - 0.058), (x + 0.008, z - 0.046), (x + 0.034, z - 0.046), (x + 0.07, z - 0.012),
             (x + 0.012, z - 0.012)], 0.016, 0.0, "frame", "frame", 0.0)
    B.box((x + 0.03, 0, z - 0.022), (0.007, 0.01, 0.026), "trim", "greeble", 0.0)
    B.box((x - 0.03, -0.019, z + 0.012), (0.03, 0.004, 0.012), "dark", "greeble", 0.0)


def kinetic_accelerator(B, rng, spec):
    """SV-02 Kinetic Accelerator: a coilgun, not a rifle. Long angular gunmetal spine over an exposed
    electromagnetic coil stack carried between two rails, a forward bracket tying the rails to a ported
    muzzle, a skeletal thumbhole stock, cyan light lines along the lower rail and a side ammo readout.
    Tiers: B longer stack and capacitor pack, C third side rail, heat-sink fins and twin capacitors."""
    tier = spec["tier"]
    ext = 0.06 * (tier - 1)
    xc0, xc1 = 0.15, 0.44 + ext      # coil stack
    xr = xc1 + 0.07                  # rail tips
    zc = 0.088                       # bore axis
    _grip(B)
    # receiver block (side profile extruded across the width), chamfered top-front
    B.prism([(-0.13, 0.02), (0.15, 0.02), (0.15, 0.135), (0.12, 0.158), (-0.08, 0.158), (-0.13, 0.13)], 0.072, 0.0,
            "panel", "frame", 0.0)
    B.box((0.01, -0.037, 0.095), (0.16, 0.004, 0.05), "dark", "greeble", 0.0)          # side inset
    B.light_strip((0.0, -0.0395, 0.112), (0.05, 0.002, 0.016), "emit")                  # ammo readout
    for k in range(3):
        B.box((0.05 + k * 0.016, -0.0395, 0.112), (0.008, 0.002, 0.012), "light", "greeble", 0.0)
    B.box((0.02, 0, 0.165), (0.1, 0.03, 0.014), "dark", "greeble", 0.0)                 # optic block
    B.light_strip((0.06, 0, 0.1725), (0.012, 0.014, 0.002), "emit")
    # skeletal thumbhole stock: top bar, lower bar, butt plate
    B.prism([(-0.13, 0.13), (-0.13, 0.095), (-0.4, 0.09), (-0.42, 0.12)], 0.05, 0.0, "frame", "frame", 0.0)
    B.prism([(-0.06, -0.03), (-0.06, -0.06), (-0.4, -0.05), (-0.4, -0.02)], 0.04, 0.0, "frame", "frame", 0.0)
    B.prism([(-0.4, 0.13), (-0.375, 0.13), (-0.375, -0.07), (-0.4, -0.08), (-0.44, -0.08), (-0.44, 0.125)], 0.055,
            0.0, "panel", "frame", 0.0)
    B.box((-0.445, 0, 0.02), (0.012, 0.05, 0.19), "rubber", "frame", 0.0)
    B.box((-0.26, -0.026, 0.104), (0.1, 0.003, 0.005), "emit", "emit", 0.0)
    # upper spine rail and lower rail run past the coils to the bracket
    B.prism([(0.15, 0.158), (0.15, 0.124), (xr, 0.118), (xr, 0.136), (xr - 0.04, 0.148), (0.2, 0.158)], 0.06, 0.0,
            "panel", "frame", 0.0)
    B.prism([(0.15, 0.02), (xr, 0.034), (xr, 0.054), (0.15, 0.052)], 0.058, 0.0, "frame", "frame", 0.0)
    B.light_strip(((0.15 + xr) / 2, -0.03, 0.043), (xr - 0.19, 0.002, 0.005), "emit")
    for k in range(int((xr - 0.2) / 0.05)):
        B.box((0.2 + k * 0.05, -0.031, 0.14), (0.018, 0.003, 0.008), "dark", "greeble", 0.0)  # spine vents
    # exposed coil stack: bore liner, ribbed windings, end collars, glowing feed ring
    B.cyl(((xc0 + xc1) / 2, 0, zc), 0.011, xc1 - xc0 + 0.02, "X", 8, "dark", "internal", 0.0)
    n = max(10, int((xc1 - xc0) / 0.011))
    prof = [(0.0, 0.0)]
    for i in range(n + 1):
        prof.append((0.031 if i % 2 == 0 else 0.025, i * (xc1 - xc0) / n))
    prof.append((0.0, xc1 - xc0))
    B.lathe(prof, (xc0, 0, zc), 10, "accent", "internal", axis="X")
    for xx in (xc0, xc1, (xc0 + xc1) / 2):
        B.cyl((xx, 0, zc), 0.035, 0.012, "X", 10, "trim", "greeble", 0.0)
    B.ring((xc0 + 0.012, 0, zc), 0.033, 0.026, 0.004, "X", 12, "emit", "emit", 0.0)
    B.box(((xc0 + xc1) / 2, 0.026, zc), (xc1 - xc0, 0.006, 0.07), "internal", "internal", 0.0)   # back plate
    # forward bracket and ported muzzle
    B.prism([(xr - 0.035, 0.02), (xr, 0.034), (xr, 0.146), (xr - 0.035, 0.158)], 0.064, 0.0, "frame", "frame", 0.0)
    B.cyl((xr + 0.035, 0, zc), 0.02, 0.07, "X", 10, "dark", "frame", 0.0)
    B.cyl((xr + 0.075, 0, zc), 0.025, 0.03, "X", 10, "frame", "frame", 0.0)
    for k in range(3):
        B.box((xr + 0.022 + k * 0.016, -0.019, zc), (0.007, 0.004, 0.022), "internal", "greeble", 0.0)
    B.ring((xr + 0.09, 0, zc), 0.016, 0.009, 0.004, "X", 10, "emit", "emit", 0.0)
    if tier >= 2:
        B.box((-0.03, 0, 0.0), (0.16, 0.05, 0.026), "panel", "cover", 0.0)             # capacitor pack
        B.light_strip((-0.03, -0.0255, 0.0), (0.12, 0.002, 0.005), "emit")
        B.cable_run((0.06, -0.03, 0.006), (0.16, -0.026, 0.04), 0.01, 0.005, 5)
    if tier >= 3:
        for k in range(6):
            B.box((0.22 + k * 0.035, 0, 0.165), (0.008, 0.056, 0.016), "trim", "greeble", 0.0)  # heat sinks
        B.box(((0.15 + xr) / 2, -0.036, zc), (xr - 0.16, 0.008, 0.01), "frame", "frame", 0.0)    # third rail
        B.light_strip(((0.15 + xr) / 2, -0.0405, zc), (xr - 0.2, 0.002, 0.003), "emit")
        B.box((-0.2, 0, 0.0), (0.12, 0.044, 0.03), "panel", "cover", 0.0)
        B.light_strip((-0.2, -0.0225, 0.0), (0.08, 0.002, 0.006), "emit")
    for ob in B.parts:
        K.scale(ob, (0.92, 1.0, 0.95))
    return {"muzzle": ((xr + 0.092) * 0.92, 0, zc * 0.95)}


def breach_launcher(B, rng, spec):
    """SV-03 Breach launcher: blocky chamfered gunmetal body in layered plates, a looped front bracket
    with amber light slots, an octagonal side drum with a bolted bezel and an amber-ringed core, a
    carry handle, a muted hazard inlay, louvres along the belly and a short stepped muzzle. Amber is
    held to the light slots and the core ring (less orange than tier 1 of the first pass)."""
    tier = spec["tier"]
    _grip(B, -0.04, 0.0)
    B.xprism(K.chamfer_rect(0.12, 0.15, 0.026), -0.26, 0.3, "panel", "frame", 0.0)
    K.translate(B.parts[-1], (0, 0, 0.075))
    B.xprism(K.chamfer_rect(0.128, 0.11, 0.02), -0.2, 0.22, "frame", "frame", 0.0)        # top deck plate
    K.translate(B.parts[-1], (0, 0, 0.096))
    B.xprism(K.chamfer_rect(0.15, 0.17, 0.032), -0.34, -0.24, "frame", "frame", 0.0)       # rear block
    K.translate(B.parts[-1], (0, 0, 0.075))
    B.box((-0.345, 0, 0.075), (0.012, 0.1, 0.12), "rubber", "frame", 0.0)
    for sx in (-1, 1):
        B.box((-0.29, sx * 0.076, 0.075), (0.05, 0.012, 0.1), "dark", "greeble", 0.0)
    B.light_strip((-0.33, -0.086, 0.075), (0.006, 0.002, 0.07), "emit")
    # side drum: octagon, bolted bezel, amber-ringed core
    dx = 0.1
    B.cyl((dx, -0.062, 0.075), 0.088, 0.028, "Y", 8, "frame", "frame", 0.0)
    B.cyl((dx, -0.079, 0.075), 0.066, 0.01, "Y", 8, "panel", "cover", 0.0)
    B.ring((dx, -0.086, 0.075), 0.042, 0.031, 0.008, "Y", 16, "emit", "emit", 0.0)
    B.cyl((dx, -0.085, 0.075), 0.031, 0.006, "Y", 12, "internal", "greeble", 0.0)
    B.cyl((dx, -0.089, 0.075), 0.016, 0.004, "Y", 8, "trim", "greeble", 0.0)
    for k in range(8):
        a = k * math.pi / 4 + math.pi / 8
        B.box((dx + 0.076 * math.cos(a), -0.078, 0.075 + 0.076 * math.sin(a)), (0.01, 0.006, 0.01), "trim", "greeble",
              0.0)
    # front loop bracket with amber slots, stepped muzzle
    B.ring((0.36, 0, 0.075), 0.1, 0.072, 0.12, "Y", 8, "frame", "frame", 0.0)
    K.scale(B.parts[-1], (0.7, 1.0, 1.0), (0.36, 0, 0.075))
    for sx in (-1, 1):
        B.light_strip((0.36 + sx * 0.058, -0.061, 0.075), (0.007, 0.003, 0.064), "emit")
    B.cyl((0.42, 0, 0.075), 0.03, 0.06, "X", 12, "dark", "frame", 0.0)
    B.cyl((0.447, 0, 0.075), 0.034, 0.016, "X", 12, "trim", "frame", 0.0)
    B.cyl((0.458, 0, 0.075), 0.022, 0.008, "X", 12, "internal", "greeble", 0.0)
    # muted hazard inlay (two short stripes) and a seam line
    B.hazard_band((-0.12, -0.061, 0.05), (0.14, 0.004, 0.03), 3)
    B.box((0.02, -0.0615, 0.11), (0.5, 0.003, 0.004), "dark", "greeble", 0.0)
    # carry handle on two posts
    for x in (-0.18, 0.2):
        B.box((x, 0, 0.18), (0.03, 0.03, 0.05), "frame", "frame", 0.0)
    B.box((0.01, 0, 0.21), (0.42, 0.034, 0.024), "frame", "frame", 0.004)
    B.box((0.01, 0, 0.198), (0.34, 0.036, 0.006), "rubber", "greeble", 0.0)
    for k in range(5):
        B.box((-0.2 + k * 0.035, -0.061, 0.02), (0.014, 0.004, 0.022), "dark", "greeble", 0.0)  # belly louvres
    if tier >= 2:
        B.box((0.08, 0, 0.165), (0.2, 0.08, 0.028), "panel", "cover", 0.0)
        B.box((0.08, -0.041, 0.165), (0.14, 0.002, 0.005), "emit", "emit", 0.0)
    if tier >= 3:
        B.ring((0.42, 0, 0.075), 0.04, 0.032, 0.012, "X", 12, "emit", "emit", 0.0)
        B.box((-0.29, 0, 0.172), (0.08, 0.1, 0.05), "panel", "cover", 0.0)
        B.box((-0.29, -0.051, 0.172), (0.05, 0.002, 0.018), "emit", "emit", 0.0)
    return {"muzzle": (0.462, 0, 0.075)}


def kinetic_slug(B, rng, spec):
    B.cyl((0, 0, 0), 0.012, 0.06, "X", 10, "trim", "frame", 0.0, radius2=0.004)
    B.cyl((-0.02, 0, 0), 0.014, 0.03, "X", 10, "emit", "emit", 0.0)
    B.ring((0.0, 0, 0), 0.02, 0.014, 0.006, "X", 10, "emit", "emit", 0.0)


def breach_canister(B, rng, spec):
    """SV-03 canister: barrel capsule with armoured chamfered end caps carrying panel blocks and a
    small amber eye, a dark-and-brass banded middle (muted, not orange), and two amber ring slits."""
    L, r = 0.2, 0.058
    B.lathe([(0, -L / 2), (r * 0.6, -L / 2), (r * 0.9, -L / 2 + 0.015), (r, -L / 2 + 0.035), (r, -0.045),
             (r * 0.94, -0.04), (0, -0.04)], (0, 0, 0), 12, "frame", "frame", axis="X")
    B.lathe([(0, 0.04), (r * 0.94, 0.04), (r, 0.045), (r, L / 2 - 0.035), (r * 0.9, L / 2 - 0.015),
             (r * 0.6, L / 2), (0, L / 2)], (0, 0, 0), 12, "frame", "frame", axis="X")
    B.cyl((0, 0, 0), r * 0.96, 0.08, "X", 12, "dark", "cover", 0.0)
    for k in range(3):
        ob = B.cyl((-0.026 + k * 0.026, 0, 0), r * 0.975, 0.01, "X", 12, "hazard", "cover", 0.0)
        K.rotate(ob, 18, "Z", (-0.026 + k * 0.026, 0, 0))
    for x in (-0.043, 0.043):
        B.cyl((x, 0, 0), r * 1.005, 0.005, "X", 12, "emit", "emit", 0.0)
    for x in (-L / 2 - 0.001, L / 2 + 0.001):
        B.cyl((x, 0, 0), r * 0.2, 0.004, "X", 8, "emit", "emit", 0.0)
    for k in range(4):
        a = k * math.pi / 2 + math.pi / 4
        for x in (-0.072, 0.072):
            B.box((x, r * math.cos(a) * 0.98, r * math.sin(a) * 0.98), (0.034, 0.014, 0.014), "panel", "greeble", 0.0)


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
             kind=name.lower(), ao_dist=0.03, value=1.0, floor=True, frame=1.2, layer="weapon", origin="grip",
             bake=512, high_bevel=0.0018, cage=0.004)
    d.update(kw)
    return d


SPECS = [
    W("KINETIC_ACCELERATOR", "A", kinetic_accelerator, "Kinetic Accelerator, tier 1 (base): electromagnetic rail with cyan coil stack", tier=1),
    W("KINETIC_ACCELERATOR", "B", kinetic_accelerator, "Kinetic Accelerator, tier 2: longer rail, more coils, heat sinks", tier=2),
    W("KINETIC_ACCELERATOR", "C", kinetic_accelerator, "Kinetic Accelerator, tier 3: third rail, twin capacitors", tier=3),
    W("BREACH_CHARGE", "A", breach_launcher, "Breach Charge launcher, tier 1: lobbed-canister tube, amber arming band", emit="amber", emit2="amber", tier=1),
    W("BREACH_CHARGE", "B", breach_launcher, "Breach Charge launcher, tier 2: larger drum, sight rail", emit="amber", emit2="amber", tier=2),
    W("BREACH_CHARGE", "C", breach_launcher, "Breach Charge launcher, tier 3: second arming ring, booster cell", emit="amber", emit2="amber", tier=3),
    W("KINETIC_SLUG", "A", kinetic_slug, "Kinetic Accelerator projectile, 0.09 m envelope", typ="PRJ", budget=400, origin="centre", bake=256),
    W("BREACH_CANISTER", "A", breach_canister, "Breach Charge canister projectile, 0.13 m envelope", emit="amber", typ="PRJ", budget=600, origin="centre", bake=256),
    W("PENETRATOR", "A", penetrator, "Concept blockout only: Penetrator (future weapon)", blockout=True),
    W("PULSE_CANNON", "A", pulse_cannon, "Concept blockout only: Pulse Cannon (future weapon)", blockout=True),
    W("DISRUPTOR", "A", disruptor, "Concept blockout only: Disruptor (future weapon)", emit="white", blockout=True),
    W("TEMPORAL_LANCE", "A", temporal_lance, "Concept blockout only: Temporal Lance (future weapon)", emit="white", blockout=True),
]
