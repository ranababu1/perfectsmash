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
    """SV-02 Kinetic Accelerator, second premium pass: an open electromagnetic coil and rail accelerator,
    not a rifle. A compact angular power-cell receiver sits over the shared grip (no rifle stock, only a
    short rubber brace on the cell), and the dominant silhouette is a large exposed coil stack carried
    between two heavy rails with a cyan energy core running through the gaps, cyan strips on the rail
    inner faces and forked rail prongs past the muzzle bracket.
    Tiers differ in coil count and shroud: A 4 coils fully open, B 6 coils with a vented top shroud and
    capacitor pack, C 8 coils with an armoured top shroud, shroud bands, heat-sink fins, a side rail
    and twin capacitors."""
    tier = spec["tier"]
    ncoil = {1: 4, 2: 6, 3: 8}[tier]
    pitch, clen, rc = 0.052, 0.034, 0.066
    zc = 0.1                                   # bore axis
    xc0 = 0.15                                 # first coil face
    xc1 = xc0 + ncoil * pitch                  # end of stack
    xb = xc1 + 0.03                            # forward bracket centre
    zt, zb = zc + rc + 0.016, zc - rc - 0.016  # rail centre heights
    _grip(B)
    # compact power-cell receiver, chamfered, layered side plate and readout
    # receiver wedge: tall at the coil mount, sloping down to the rear so the coils lead the silhouette
    B.prism([(-0.17, 0.0), (0.15, 0.0), (0.15, 0.196), (0.07, 0.204), (-0.1, 0.168), (-0.17, 0.13)], 0.078, 0.0,
            "panel", "frame", 0.004)
    B.prism([(-0.13, 0.025), (0.125, 0.025), (0.125, 0.172), (0.06, 0.178), (-0.08, 0.15), (-0.13, 0.12)], 0.004,
            -0.04, "frame", "cover", 0.0)                                               # layered side plate
    B.box((0.02, -0.0425, 0.1), (0.1, 0.003, 0.04), "dark", "greeble", 0.0)            # readout bezel
    B.light_strip((0.005, -0.0445, 0.104), (0.05, 0.002, 0.014), "emit")
    for k in range(3):
        B.box((0.045 + k * 0.014, -0.0445, 0.104), (0.007, 0.002, 0.01), "light", "greeble", 0.0)
    for k in range(3):
        B.box((-0.1 + k * 0.028, -0.0425, 0.06), (0.012, 0.003, 0.03), "dark", "greeble", 0.0)  # vents
    B.box((0.06, 0, 0.214), (0.09, 0.03, 0.02), "dark", "greeble", 0.003)               # optic block
    B.light_strip((0.1, 0, 0.2245), (0.01, 0.014, 0.002), "emit")
    # rear energy cell (replaces the stock): small angled block, cyan window, short rubber brace
    B.prism([(-0.17, 0.13), (-0.17, 0.0), (-0.2, 0.025), (-0.225, 0.06), (-0.225, 0.115)], 0.066, 0.0,
            "frame", "frame", 0.004)
    B.light_strip((-0.198, -0.0335, 0.075), (0.03, 0.002, 0.008), "emit")
    B.box((-0.232, 0, 0.088), (0.012, 0.056, 0.06), "rubber", "frame", 0.003)
    # heavy upper and lower rails, cyan inner faces, forked prongs past the bracket
    for z, sgn in ((zt, -1), (zb, 1)):
        B.box(((0.13 + xb + 0.09) / 2, 0, z), (xb + 0.09 - 0.13, 0.03, 0.024), "frame", "frame", 0.004)
        B.light_strip(((0.15 + xb + 0.08) / 2, 0, z + sgn * 0.0125), (xb + 0.08 - 0.15, 0.012, 0.002), "emit")
        B.box(((0.15 + xb) / 2, -0.0155, z), (xb - 0.18, 0.002, 0.006), "dark", "greeble", 0.0)   # rail seam
    # exposed coil stack: chamfered windings, emissive core showing through every gap
    B.cyl(((xc0 + xc1) / 2, 0, zc), 0.022, xc1 - xc0 + 0.04, "X", 8, "emit", "emit", 0.0)
    prof = [(0.0, 0.0), (rc - 0.012, 0.0), (rc, 0.006), (rc, clen - 0.006), (rc - 0.012, clen), (0.0, clen)]
    for i in range(ncoil):
        x = xc0 + 0.009 + i * pitch
        B.lathe(prof, (x, 0, zc), 10, "dark", "internal", axis="X")                         # dark ribbed winding
        B.cyl((x + clen + 0.009, 0, zc), 0.042, 0.012, "X", 8, "emit", "emit", 0.0)          # cyan energy band
    # forward bracket tying the rails, muzzle projector
    B.prism([(xb - 0.022, zb - 0.012), (xb + 0.022, zb - 0.012), (xb + 0.022, zt + 0.012), (xb - 0.022, zt + 0.012)],
            0.05, 0.0, "panel", "frame", 0.004)
    B.ring((xb - 0.0255, 0, zc), 0.05, 0.03, 0.004, "X", 12, "emit", "emit", 0.0)
    B.cyl((xb + 0.04, 0, zc), 0.026, 0.06, "X", 10, "dark", "frame", 0.0)
    B.ring((xb + 0.072, 0, zc), 0.032, 0.016, 0.01, "X", 10, "frame", "frame", 0.0)
    B.ring((xb + 0.078, 0, zc), 0.016, 0.01, 0.003, "X", 10, "emit", "emit", 0.0)
    # rear coil mount ring at the receiver face
    B.cyl((xc0 - 0.004, 0, zc), rc + 0.008, 0.012, "X", 12, "frame", "frame", 0.0)
    if tier >= 2:
        L = (xc1 - xc0) * (0.55 if tier == 2 else 1.0)
        B.prism([(0.13, zt + 0.012), (xc0 + L, zt + 0.012), (xc0 + L - 0.03, zt + 0.04), (0.15, zt + 0.04)], 0.044,
                0.0, "panel", "cover", 0.003)                                           # top shroud
        for k in range(int(L / 0.05)):
            B.box((xc0 + 0.03 + k * 0.05, -0.0225, zt + 0.026), (0.022, 0.003, 0.01), "dark", "greeble", 0.0)
        B.box((-0.05, 0, -0.018), (0.2, 0.05, 0.03), "panel", "cover", 0.003)           # capacitor pack
        B.light_strip((-0.05, -0.0255, -0.018), (0.15, 0.002, 0.006), "emit")
        B.cable_run((0.05, -0.028, -0.01), (0.15, -0.02, zb), 0.012, 0.005, 5)
    if tier >= 3:
        for k in range(5):
            B.box((xc0 + 0.04 + k * 0.075, 0, zt + 0.05), (0.012, 0.05, 0.02), "trim", "greeble", 0.0)  # fins
        for i in (1, 4, 7):
            B.box((xc0 + i * pitch, 0.0, zc), (0.012, 0.034, zt - zb), "frame", "frame", 0.002)       # shroud bands
            B.box((xc0 + i * pitch, -0.018, zc), (0.012, 0.004, zt - zb - 0.03), "dark", "greeble", 0.0)
        B.box(((xc0 + xb) / 2, -0.074, zc - 0.03), (xb - xc0, 0.01, 0.012), "frame", "frame", 0.0)   # side rail
        B.light_strip(((xc0 + xb) / 2, -0.0795, zc - 0.03), (xb - xc0 - 0.04, 0.002, 0.004), "emit")
        for x in (xc0 + 0.05, xb - 0.05):
            B.box((x, -0.05, zc - 0.03), (0.012, 0.04, 0.012), "frame", "greeble", 0.0)
        B.box((-0.21, 0, -0.018), (0.1, 0.046, 0.03), "panel", "cover", 0.003)          # twin capacitor
        B.light_strip((-0.21, -0.0235, -0.018), (0.07, 0.002, 0.006), "emit")
    for ob in B.parts:
        K.scale(ob, (0.92, 1.0, 0.95))
    return {"muzzle": ((xb + 0.083) * 0.92, 0, zc * 0.95)}


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
             (r * 0.94, -0.04), (0, -0.04)], (0, 0, 0), 12, "dark", "frame", axis="X")
    B.lathe([(0, 0.04), (r * 0.94, 0.04), (r, 0.045), (r, L / 2 - 0.035), (r * 0.9, L / 2 - 0.015),
             (r * 0.6, L / 2), (0, L / 2)], (0, 0, 0), 12, "dark", "frame", axis="X")
    B.cyl((0, 0, 0), r * 0.96, 0.08, "X", 12, "internal", "cover", 0.0)
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
            B.box((x, r * math.cos(a) * 0.98, r * math.sin(a) * 0.98), (0.034, 0.014, 0.014), "frame", "greeble", 0.0)


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
    W("KINETIC_ACCELERATOR", "A", kinetic_accelerator, "Kinetic Accelerator, tier 1 (base): open coil and rail accelerator, 4 exposed coils", tier=1),
    W("KINETIC_ACCELERATOR", "B", kinetic_accelerator, "Kinetic Accelerator, tier 2: 6 coils, vented top shroud, capacitor pack", tier=2),
    W("KINETIC_ACCELERATOR", "C", kinetic_accelerator, "Kinetic Accelerator, tier 3: 8 coils, armoured shroud and bands, side rail, heat sinks, twin capacitors", tier=3),
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
