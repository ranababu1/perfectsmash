"""Shared (SHR) structural, electronic and energy kits. Chapter-neutral graphite steel; emissive kept to
small neutral status lights so the runtime can retint emit_* slots per chapter. Same 45-degree chamfer
grammar as Helix, slightly heavier proportions."""
import math
from mathutils import Vector
import tfjkit as K

CH = "shared"


# ---------------------------------------------------------------- structural
def block_alloy(B, w, h, d, rng, spec):
    """Lightweight alloy enclosure: thin-wall box with pressed panels and corner guards."""
    z0, z1 = -h / 2, h / 2
    c = min(w, h) * 0.08
    B.zprism(K.chamfer_rect(w * 0.96, d * 0.96, c), z0 + 0.012, z1 - 0.012, "panel", "frame", 0.006)
    for zz in (z0 + 0.016, z1 - 0.016):
        B.zprism(K.chamfer_rect(w, d, c * 1.2), zz - 0.016, zz + 0.016, "frame", "frame", 0.004)
    for sx in (-1, 1):
        for sz in (-1, 1):
            B.box((sx * (w / 2 - 0.03), -d / 2 + 0.002, sz * (h / 2 - 0.03)), (0.05, 0.012, 0.05), "trim", "greeble")
    # pressed front panel with stiffening ribs
    B.box((0, -d * 0.48 - 0.006, 0), (w * 0.72, 0.012, h * 0.62), "panel", "cover", 0.004)
    for k in range(3):
        B.box((0, -d * 0.48 - 0.013, -h * 0.2 + k * h * 0.2), (w * 0.6, 0.004, 0.012), "light", "greeble")
    B.box((-w * 0.48 - 0.006, 0, 0), (0.012, d * 0.7, h * 0.62), "panel", "cover", 0.004)
    B.box((w * 0.48 + 0.006, 0, 0), (0.012, d * 0.7, h * 0.62), "panel", "cover", 0.004)
    B.box((0, 0, z1 + 0.0), (w * 0.6, d * 0.6, 0.006), "panel", "cover", 0.0)
    B.light_strip((w * 0.28, -d * 0.48 - 0.002, h * 0.36), (0.02, 0.004, 0.01), "emit")


def block_steel(B, w, h, d, rng, spec):
    """Reinforced steel housing: thick walls, bolted armour plates, recessed handles."""
    z0, z1 = -h / 2, h / 2
    B.zprism(K.chamfer_rect(w * 0.9, d * 0.92, 0.05), z0 + 0.03, z1 - 0.03, "frame", "frame", 0.01)
    for zz in (z0 + 0.03, z1 - 0.03):
        B.zprism(K.chamfer_rect(w, d, 0.06), zz - 0.03, zz + 0.03, "dark", "frame", 0.008)
    for i in range(2):
        zc = z0 + 0.06 + (i + 0.5) * (h - 0.12) / 2
        ph = (h - 0.12) / 2 - 0.016
        B.box((0, -d * 0.46 - 0.012, zc), (w * 0.84, 0.024, ph), "panel", "cover", 0.008)
        for sx in (-1, 1):
            B.box((sx * w * 0.36, -d * 0.46 - 0.026, zc + ph * 0.38), (0.016, 0.006, 0.016), "trim", "greeble")
            B.box((sx * w * 0.36, -d * 0.46 - 0.026, zc - ph * 0.38), (0.016, 0.006, 0.016), "trim", "greeble")
            B.box((sx * (w * 0.45 + 0.012), 0, zc), (0.024, d * 0.84, ph), "panel", "cover", 0.008)
    B.box((0, -d * 0.46 - 0.026, 0), (w * 0.3, 0.008, 0.03), "dark", "greeble")


def block_concrete(B, w, h, d, rng, spec):
    """Precast concrete support block: chamfered arrises, lifting pockets, steel edge angles."""
    z0, z1 = -h / 2, h / 2
    c = min(w, h) * 0.07
    B.box((0, 0, 0), (w, d, h), "concrete", "frame", c, 1)
    # formwork seams (shallow grooves)
    for k in range(1, max(2, int(w / 0.3))):
        x = -w / 2 + k * w / max(2, int(w / 0.3))
        B.box((x, -d / 2 + 0.002, 0), (0.008, 0.006, h * 0.9), "dark", "greeble")
    # steel edge angles on the top arris
    B.box((0, -d / 2 + 0.01, z1 - 0.01), (w * 0.94, 0.02, 0.02), "trim", "cover", 0.0)
    B.box((-w / 2 + 0.01, 0, z1 - 0.01), (0.02, d * 0.94, 0.02), "trim", "cover", 0.0)
    for sx in (-1, 1):
        B.box((sx * w * 0.3, -d / 2 + 0.003, z1 - h * 0.2), (0.05, 0.008, 0.04), "internal", "greeble")
    # rebar ends visible only when chipped (internal)
    for k in range(3):
        B.cyl((-w * 0.3 + k * w * 0.3, -d * 0.3, 0), 0.008, h * 0.9, "Z", 6, "scorch", "internal", 0.0)


def panel_glass(B, w, h, d, rng, spec):
    """Framed glass panel. Wide panels glaze the front; narrow ones glaze the sides (deep glass fin)."""
    z0, z1 = -h / 2, h / 2
    f = min(0.04, min(w, h) * 0.14)
    if w >= 0.3:
        y = -d * 0.15
        fd = min(d, 0.16)
        for zz in (z0 + f / 2, z1 - f / 2):
            B.box((0, y, zz), (w, fd, f), "frame", "frame", 0.006)
        for xx in (-w / 2 + f / 2, w / 2 - f / 2):
            B.box((xx, y, 0), (f, fd, h - 2 * f), "frame", "frame", 0.006)
        B.box((0, y, 0), (f * 0.6, fd * 0.8, h - 2 * f), "frame", "frame", 0.0)
        for sx in (-1, 1):
            B.pane((sx * (w / 4 - f * 0.15), y, 0), w / 2 - f * 1.3, h - 2 * f, 0.012)
        B.box((0, y - fd / 2 - 0.004, z0 + f / 2), (w * 0.9, 0.008, f * 0.4), "light", "greeble")
        # feet so it stands within the depth band
        for sx in (-1, 1):
            B.box((sx * (w / 2 - f), 0, z0 + 0.015), (f * 1.2, d * 0.9, 0.03), "dark", "frame", 0.004)
    else:
        for zz in (z0 + f / 2, z1 - f / 2):
            B.box((0, 0, zz), (w, d, f), "frame", "frame", 0.006)
        for yy in (-d / 2 + f / 2, d / 2 - f / 2):
            B.box((0, yy, 0), (w, f, h - 2 * f), "frame", "frame", 0.004)
        B.box((0, 0, 0), (w * 0.25, d - 2 * f, h - 2 * f), "glass", "glass", 0.0)
        for sx in (-1, 1):
            B.pane((sx * (w * 0.32), 0, 0), d - 2 * f, h - 2 * f, 0.012, "glass", "X")


def beam_composite(B, w, h, d, rng, spec):
    """Composite I-beam with flange caps, web lightening holes (as recessed discs) and end plates."""
    z0, z1 = -h / 2, h / 2
    ft = h * 0.22
    web = d * 0.18
    B.box((0, 0, z1 - ft / 2), (w, d * 0.7, ft), "frame", "frame", min(0.01, ft * 0.3))
    B.box((0, 0, z0 + ft / 2), (w, d * 0.7, ft), "frame", "frame", min(0.01, ft * 0.3))
    B.box((0, 0, 0), (w, web, h - 2 * ft), "panel", "frame", 0.0)
    n = max(2, int(w / 0.3))
    for i in range(n):
        x = -w / 2 + (i + 0.5) * w / n
        B.cyl((x, -web / 2 - 0.002, 0), (h - 2 * ft) * 0.3, 0.006, "Y", 12, "dark", "greeble", 0.0)
        if i < n - 1:
            B.box((x + w / n / 2, -d * 0.2, 0), (0.012, d * 0.26, h - 2 * ft), "trim", "cover", 0.0)
    for sx in (-1, 1):
        B.box((sx * (w / 2 - 0.01), 0, 0), (0.02, d * 0.72, h), "trim", "frame", 0.004)
    B.box((0, -d * 0.35 - 0.002, z1 - ft / 2), (w * 0.96, 0.004, ft * 0.3), "light", "greeble")


def frame_alloy(B, w, h, d, rng, spec):
    """X-braced alloy frame bay (SV-06 row 2): posts, rails, cross bracing, gusset plates."""
    z0, z1 = -h / 2, h / 2
    t = min(0.06, min(w, h) * 0.1)
    for y in (-d * 0.3, d * 0.3):
        for x in (-w / 2 + t / 2, w / 2 - t / 2):
            B.zprism(K.chamfer_rect(t, t, t * 0.25, x, y), z0, z1, "frame", "frame", 0.0)
        for zz in (z0 + t / 2, z1 - t / 2):
            B.box((0, y, zz), (w - 2 * t, t, t * 0.9), "frame", "frame", 0.0)
        a, b = (-w / 2 + t, y, z0 + t), (w / 2 - t, y, z1 - t)
        B.strut(a, b, t * 0.55, "panel", "cover")
        B.strut((-w / 2 + t, y, z1 - t), (w / 2 - t, y, z0 + t), t * 0.55, "panel", "cover")
        B.box((0, y - t * 0.3, 0), (t * 1.6, 0.01, t * 1.6), "trim", "greeble")
    for x in (-w / 2 + t / 2, w / 2 - t / 2):
        for zz in (z0 + t / 2, z1 - t / 2):
            B.box((x, 0, zz), (t * 0.9, d * 0.6, t * 0.8), "frame", "frame", 0.0)
            B.box((x, -d * 0.3 - t * 0.55, zz), (t * 1.3, 0.008, t * 1.3), "trim", "greeble")
    B.box((0, 0, z0 + 0.006), (w, d * 0.7, 0.012), "dark", "frame", 0.0)


def column_steel(B, w, h, d, rng, spec):
    """Heavy steel H-column with base and cap plates, stiffeners and bolt groups."""
    z0, z1 = -h / 2, h / 2
    fl = w * 0.22
    pl = min(0.05, h * 0.04)
    B.box((0, 0, z0 + pl / 2), (w, d * 0.9, pl), "dark", "frame", 0.006)
    B.box((0, 0, z1 - pl / 2), (w, d * 0.9, pl), "dark", "frame", 0.006)
    for sx in (-1, 1):
        B.box((sx * (w / 2 - fl / 2), 0, 0), (fl, d * 0.7, h - 2 * pl), "frame", "frame", 0.006)
    B.box((0, 0, 0), (w - 2 * fl, d * 0.14, h - 2 * pl), "panel", "frame", 0.0)
    n = max(2, int(h / 0.5))
    for i in range(1, n):
        zc = z0 + i * h / n
        B.box((0, -d * 0.2, zc), (w - 2 * fl, d * 0.26, 0.02), "trim", "cover", 0.0)
        B.box((0, d * 0.2, zc), (w - 2 * fl, d * 0.26, 0.02), "trim", "cover", 0.0)
    for zz in (z0 + pl + 0.04, z1 - pl - 0.04):
        for sx in (-1, 1):
            B.box((sx * (w / 2 - fl / 2), -d * 0.35 - 0.003, zz), (0.018, 0.006, 0.018), "trim", "greeble")
    B.box((-w / 2 + 0.002, 0, 0), (0.004, d * 0.06, h * 0.8), "light", "greeble")


def column_concrete(B, w, h, d, rng, spec):
    z0, z1 = -h / 2, h / 2
    cap = min(0.12, h * 0.08)
    B.box((0, 0, z0 + cap / 2), (w, d, cap), "concrete", "frame", 0.012)
    B.box((0, 0, z1 - cap / 2), (w, d, cap), "concrete", "frame", 0.012)
    B.box((0, 0, 0), (w * 0.84, d * 0.84, h - 2 * cap), "concrete", "frame", 0.02, 1)
    n = max(2, int((h - 2 * cap) / 0.6))
    for i in range(1, n):
        B.box((0, -d * 0.42 - 0.002, z0 + cap + i * (h - 2 * cap) / n), (w * 0.84, 0.008, 0.012), "dark", "greeble")
    B.box((0, -d * 0.42 - 0.004, z0 + cap + 0.15), (w * 0.5, 0.008, 0.2), "hazard" if False else "trim", "cover", 0.0)
    for k in range(4):
        B.cyl(((k % 2 - 0.5) * w * 0.4, (k // 2 - 0.5) * d * 0.4, 0), 0.01, h - 2 * cap, "Z", 6, "scorch", "internal", 0.0)


def platform_composite(B, w, h, d, rng, spec):
    """Composite walkway platform: tread grating on top, C-channel fascia, kick plates."""
    z0, z1 = -h / 2, h / 2
    B.box((0, 0, z1 - h * 0.2), (w, d * 0.9, h * 0.4), "frame", "frame", 0.006)
    n = max(4, int(w / 0.12))
    for i in range(n):
        x = -w / 2 + (i + 0.5) * w / n
        B.box((x, 0, z1 - 0.002), (w / n * 0.55, d * 0.82, 0.004), "dark", "greeble")
    B.xprism([(-d / 2, z1 - h * 0.1), (-d / 2, z0 + 0.01), (-d / 2 + 0.02, z0), (-d / 2 + 0.05, z0),
              (-d / 2 + 0.05, z1 - h * 0.1)], -w / 2, w / 2, "panel", "frame", 0.0)
    m = max(2, int(w / 0.6))
    for i in range(m):
        x = -w / 2 + (i + 0.5) * w / m
        B.box((x, -d / 2 - 0.005, (z0 + z1) / 2 - 0.01), (w / m - 0.03, 0.01, h * 0.4), "panel", "cover", 0.0)
    for i in range(m + 1):
        x = -w / 2 + 0.02 + i * (w - 0.04) / m
        B.box((x, 0, z0 + h * 0.3), (0.025, d * 0.8, h * 0.6), "dark", "frame", 0.0)
    B.box((0, d / 2 - 0.03, (z0 + z1) / 2), (w, 0.05, h), "frame", "frame", 0.0)


def panel_reinforced(B, w, h, d, rng, spec):
    """Reinforced armour panel: thick core, horizontal stiffener ribs, overlapping plates on the faces."""
    z0, z1 = -h / 2, h / 2
    B.box((0, 0, 0), (w * 0.6, d, h), "frame", "frame", 0.012)
    n = max(3, int(h / 0.28))
    for i in range(n):
        zc = z0 + (i + 0.5) * h / n
        for sx in (-1, 1):
            B.box((sx * (w * 0.3 + 0.02), 0.0, zc), (0.04, d * 0.94, h / n - 0.02), "panel", "cover", 0.008)
        B.box((0, -d / 2 - 0.007, zc), (w * 0.88, 0.014, h / n - 0.02), "panel", "cover", 0.004)
        B.box((0, -d / 2 - 0.0155, zc), (w * 0.12, 0.003, h / n * 0.5), "dark", "greeble")
    B.box((0, 0, z0 + 0.025), (w, d, 0.05), "dark", "frame", 0.008)
    B.box((0, 0, z1 - 0.02), (w, d, 0.04), "trim", "frame", 0.008)


def wall_industrial(B, w, h, d, rng, spec):
    """Industrial wall segment: steel post-and-rail frame infilled with ribbed sheet and a service duct."""
    z0, z1 = -h / 2, h / 2
    t = 0.06
    for x in (-w / 2 + t / 2, w / 2 - t / 2):
        B.box((x, 0, 0), (t, d, h), "frame", "frame", 0.008)
    B.box((0, 0, z0 + 0.04), (w, d, 0.08), "dark", "frame", 0.008)
    B.box((0, 0, z1 - 0.03), (w, d, 0.06), "frame", "frame", 0.008)
    B.box((0, 0.02, 0), (w - 2 * t, d * 0.3, h - 0.14), "panel", "frame", 0.0)
    n = max(3, int((w - 2 * t) / 0.1))
    for i in range(n):
        x = -w / 2 + t + (i + 0.5) * (w - 2 * t) / n
        B.box((x, -d * 0.15 + 0.02 - 0.012, 0), ((w - 2 * t) / n * 0.5, 0.024, h - 0.16), "panel", "cover", 0.0)
    B.box((0, 0, z0 + h * 0.62), (w - 2 * t, d * 0.9, 0.05), "trim", "frame", 0.006)
    B.cyl((0, -d * 0.36, z1 - 0.16), 0.05, w - 2 * t, "X", 12, "dark", "greeble", 0.004)
    B.light_strip((w * 0.3, -d / 2 + 0.002, z0 + h * 0.62), (0.03, 0.004, 0.012), "emit")


def joint_steel(B, w, h, d, rng, spec):
    """Structural connector node: cast hub with four socket stubs and bolt rings."""
    s = min(w, h)
    B.zprism(K.chamfer_rect(s * 0.7, d * 0.7, s * 0.2), -s * 0.35, s * 0.35, "frame", "frame", 0.006)
    for ax, (dx, dz) in (("X", (1, 0)), ("X", (-1, 0)), ("Z", (0, 1)), ("Z", (0, -1))):
        c = (dx * s * 0.42, 0, dz * s * 0.42)
        B.cyl(c, s * 0.16, s * 0.16, ax, 10, "panel", "cover", 0.004)
    B.cyl((0, -d * 0.35 - 0.004, 0), s * 0.2, 0.012, "Y", 12, "trim", "greeble", 0.0)
    for k in range(6):
        a = k * math.pi / 3
        B.cyl((math.cos(a) * s * 0.16, -d * 0.35 - 0.01, math.sin(a) * s * 0.16), 0.008, 0.01, "Y", 6, "light", "greeble", 0.0)


def panel_polymer(B, w, h, d, rng, spec):
    """Moulded polymer cover panel: rounded edges, recessed grip channel, clip tabs."""
    z0, z1 = -h / 2, h / 2
    B.box((0, 0, 0), (w, d * 0.9, h), "polymer", "frame", min(w, h) * 0.12, 2)
    B.box((0, -d * 0.45 - 0.003, 0), (w * 0.7, 0.008, max(0.02, h * 0.06)), "dark", "greeble")
    for sz in (-1, 1):
        B.box((0, -d * 0.45 - 0.004, sz * h * 0.38), (w * 0.4, 0.008, 0.02), "panel", "cover", 0.0)
    B.box((-w / 2 - 0.0, 0, 0), (0.008, d * 0.6, h * 0.5), "panel", "cover", 0.0)


def casing_reactor(B, w, h, d, rng, spec):
    """Heavy reactor casing segment: thick cylindrical shell in a steel cradle, banded and bolted."""
    z0, z1 = -h / 2, h / 2
    r = min(w, d) * 0.46
    B.box((0, 0, z0 + 0.04), (w, d, 0.08), "dark", "frame", 0.01)
    B.lathe([(0, z0 + 0.08), (r * 0.9, z0 + 0.08), (r, z0 + 0.12), (r, z1 - 0.1), (r * 0.85, z1 - 0.04), (r * 0.3, z1),
             (0, z1)], (0, 0, 0), 24, "frame", "frame")
    n = 3
    for i in range(n):
        zc = z0 + 0.14 + i * (h - 0.26) / (n - 1)
        B.ring((0, 0, zc), r * 1.04, r * 0.95, 0.04, "Z", 24, "trim", "cover", 0.0)
    for k in range(6):
        a = -math.pi / 2 + (k - 2.5) * 0.45
        B.box((math.cos(a) * r * 1.0, math.sin(a) * r * 1.0, 0), (0.04, 0.04, h - 0.3), "panel", "cover", 0.004)
    B.cyl((0, 0, z1 - 0.02), r * 0.25, 0.04, "Z", 12, "trim", "greeble", 0.0)
    B.light_strip((0, -r * 1.02, z1 - 0.14), (r * 0.5, 0.006, 0.012), "emit2")


# ---------------------------------------------------------------- electronic
def server_cabinet(B, w, h, d, rng, spec):
    import helix
    helix.server_rack(B, w, h, d, rng, spec)


def control_module(B, w, h, d, rng, spec):
    """Control console module: angled screen deck, keypad, side vents."""
    z0, z1 = -h / 2, h / 2
    fy = -d / 2
    B.box((0, 0.05, z0 + h * 0.3), (w, d - 0.1, h * 0.6), "frame", "frame", 0.012)
    B.box((0, fy + 0.05, z0 + h * 0.3), (w * 0.92, 0.1, h * 0.5), "panel", "cover", 0.008)
    B.xprism([(fy + 0.02, z0 + h * 0.6), (fy + 0.02, z0 + h * 0.66), (d * 0.3, z1), (d / 2, z1),
              (d / 2, z0 + h * 0.6)], -w / 2, w / 2, "frame", "frame", 0.006)
    B.xprism([(fy + 0.06, z0 + h * 0.665), (d * 0.28, z1 - 0.03), (d * 0.28, z1 - 0.022), (fy + 0.06, z0 + h * 0.673)],
             -w * 0.42, w * 0.42, "glass_smoked", "glass", 0.0)
    for k in range(3):
        B.xprism([(fy + 0.09 + k * 0.04, z0 + h * 0.69 + k * 0.03), (fy + 0.12 + k * 0.04, z0 + h * 0.71 + k * 0.03),
                  (fy + 0.12 + k * 0.04, z0 + h * 0.714 + k * 0.03), (fy + 0.09 + k * 0.04, z0 + h * 0.694 + k * 0.03)],
                 -w * 0.35, -w * 0.35 + w * (0.25 + 0.15 * k), "emit", "emit", 0.0)
    B.vent(w * 0.25, z0 + h * 0.33, w * 0.3, h * 0.18, fy - 0.0, 4)
    for k in range(4):
        B.box((-w * 0.28 + (k % 2) * 0.05, fy - 0.004, z0 + h * 0.38 - (k // 2) * 0.05), (0.03, 0.008, 0.03), "light", "greeble")
    B.box((0, 0, z0 + 0.02), (w, d, 0.04), "dark", "frame", 0.006)


def data_node(B, w, h, d, rng, spec):
    """Data storage node: stacked drive sleds behind a smoked window, status column."""
    z0, z1 = -h / 2, h / 2
    B.zprism(K.chamfer_rect(w, d, min(w, d) * 0.12), z0, z1, "frame", "frame", 0.01)
    fy = -d / 2
    B.box((0, fy - 0.004, 0.0), (w * 0.78, 0.01, h * 0.78), "dark", "greeble")
    n = max(3, int(h * 0.78 / 0.06))
    for i in range(n):
        zc = -h * 0.36 + (i + 0.5) * h * 0.72 / n
        B.box((-w * 0.06, fy - 0.01, zc), (w * 0.56, 0.012, h * 0.72 / n - 0.008), "panel", "cover", 0.0)
        B.box((-w * 0.32, fy - 0.017, zc), (0.006, 0.004, 0.006), "emit" if i % 3 else "emit2", "emit", 0.0)
    B.box((w * 0.3, fy - 0.012, 0), (0.02, 0.012, h * 0.7), "trim", "frame", 0.0)
    B.light_strip((w * 0.3, fy - 0.0185, h * 0.1), (0.008, 0.003, h * 0.4), "emit")
    B.pane((0, fy - 0.022, 0), w * 0.82, h * 0.82, 0.006, "glass_smoked")


def relay_unit(B, w, h, d, rng, spec):
    """Relay unit: switching box with ribbed heat sink, insulated terminals and an antenna stub."""
    z0, z1 = -h / 2, h / 2
    bh = h * 0.72
    B.box((0, 0, z0 + bh / 2), (w, d, bh), "frame", "frame", 0.01)
    n = max(4, int(w / 0.04))
    for i in range(n):
        x = -w / 2 + 0.02 + i * (w - 0.04) / (n - 1)
        B.box((x, 0, z0 + bh + 0.002), (0.008, d * 0.7, 0.03), "trim", "cover", 0.0)
    B.box((0, -d / 2 - 0.008, z0 + bh * 0.5), (w * 0.8, 0.016, bh * 0.6), "panel", "cover", 0.004)
    for k in range(3):
        x = -w * 0.25 + k * w * 0.25
        B.cyl((x, -d * 0.1, z0 + bh + 0.06), 0.02, 0.09, "Z", 10, "polymer", "greeble", 0.0)
        B.cyl((x, -d * 0.1, z0 + bh + 0.11), 0.026, 0.012, "Z", 10, "polymer", "greeble", 0.0)
    B.cyl((w * 0.38, d * 0.2, z1 - (h - bh) / 2), 0.006, h - bh, "Z", 6, "trim", "greeble", 0.0)
    B.light_strip((-w * 0.3, -d / 2 - 0.017, z0 + bh * 0.7), (0.03, 0.003, 0.01), "emit")
    B.light_strip((-w * 0.2, -d / 2 - 0.017, z0 + bh * 0.7), (0.01, 0.003, 0.01), "emit2")


def circuit_module(B, w, h, d, rng, spec):
    """Circuit module: open-frame card cage with exposed boards and a fan, thin perforated covers."""
    z0, z1 = -h / 2, h / 2
    t = 0.025
    for sx in (-1, 1):
        B.box((sx * (w / 2 - t / 2), 0, 0), (t, d, h), "frame", "frame", 0.004)
    B.box((0, 0, z0 + t / 2), (w, d, t), "frame", "frame", 0.004)
    B.box((0, 0, z1 - t / 2), (w, d, t), "frame", "frame", 0.004)
    n = max(3, int((w - 2 * t) / 0.05))
    for i in range(n):
        x = -w / 2 + t + (i + 0.5) * (w - 2 * t) / n
        B.box((x, 0.02, 0), (0.006, d * 0.8, h - 2 * t - 0.02), "accent", "internal", 0.0)
        B.box((x, -d * 0.38, h * 0.2), (0.012, 0.02, 0.03), "dark", "internal", 0.0)
        if i % 2 == 0:
            B.box((x + 0.004, -d * 0.39, -h * 0.2), (0.004, 0.006, 0.01), "emit", "emit", 0.0)
    B.box((0, -d / 2 + 0.006, h * 0.25), (w - 2 * t, 0.012, h * 0.4), "panel", "cover", 0.0)
    B.box((0, -d / 2 + 0.006, -h * 0.25), (w - 2 * t, 0.012, h * 0.3), "panel", "cover", 0.0)
    B.ring((0, -d / 2 + 0.002, -h * 0.25), min(w, h) * 0.16, min(w, h) * 0.13, 0.01, "Y", 16, "trim", "greeble", 0.0)


def comms_array(B, w, h, d, rng, spec):
    """Comms array: mast with stacked panel antennas and a dish stub."""
    z0, z1 = -h / 2, h / 2
    B.box((0, 0, z0 + 0.04), (w, d, 0.08), "dark", "frame", 0.008)
    B.zprism(K.chamfer_rect(w * 0.3, d * 0.3, 0.01), z0 + 0.08, z1 - 0.02, "frame", "frame", 0.0)
    n = 3
    for i in range(n):
        zc = z0 + h * 0.45 + i * h * 0.16
        for sx in (-1, 1):
            B.box((sx * w * 0.32, -d * 0.1, zc), (w * 0.28, 0.03, h * 0.13), "polymer", "cover", 0.006)
            B.box((sx * w * 0.18, -d * 0.1, zc), (w * 0.06, 0.02, 0.02), "trim", "greeble")
    B.cyl((0, -d * 0.2, z0 + h * 0.3), w * 0.2, 0.03, "Y", 16, "panel", "cover", 0.004)
    B.light_strip((0, -d * 0.15, z1 - 0.03), (0.02, 0.02, 0.02), "emit2")
    B.box((0, -d * 0.16, z0 + 0.06), (w * 0.4, 0.008, 0.03), "light", "greeble")


# ---------------------------------------------------------------- energy
def energy_cell(B, w, h, d, rng, spec):
    import helix
    helix.power_cell(B, w, h, d, rng, spec)


def transformer_unit(B, w, h, d, rng, spec):
    """Dry transformer: core and coil block, radiator fins on the sides, HV bushings on top."""
    z0, z1 = -h / 2, h / 2
    bh = h * 0.7
    B.box((0, 0, z0 + 0.03), (w, d, 0.06), "dark", "frame", 0.008)
    B.box((0, 0, z0 + 0.06 + bh / 2), (w * 0.7, d * 0.8, bh), "frame", "frame", 0.012)
    n = 5
    for i in range(n):
        y = -d * 0.32 + i * d * 0.16
        for sx in (-1, 1):
            B.box((sx * w * 0.42, y, z0 + 0.06 + bh / 2), (w * 0.14, 0.012, bh * 0.85), "panel", "cover", 0.0)
    B.box((0, -d * 0.4 - 0.008, z0 + 0.06 + bh * 0.5), (w * 0.6, 0.016, bh * 0.7), "panel", "cover", 0.006)
    for k in range(3):
        x = -w * 0.22 + k * w * 0.22
        B.lathe([(0, 0), (0.035, 0), (0.035, 0.02), (0.026, 0.03), (0.034, 0.045), (0.024, 0.06), (0.032, 0.075),
                 (0.018, 0.09), (0.012, h - bh - 0.07), (0, h - bh - 0.07)], (x, 0, z0 + 0.06 + bh), 12, "polymer", "greeble")
    B.light_strip((w * 0.2, -d * 0.4 - 0.017, z0 + 0.06 + bh * 0.82), (0.03, 0.003, 0.012), "emit2")
    B.box((0, -d * 0.4 - 0.017, z0 + 0.06 + bh * 0.3), (w * 0.3, 0.003, 0.04), "light", "greeble")


def power_conduit(B, w, h, d, rng, spec):
    """Armoured power conduit run (horizontal or vertical by aspect) with clamp rings and junction box."""
    horiz = w >= h
    L = w if horiz else h
    r = min(w, h) * 0.32
    ax = "X" if horiz else "Z"
    B.cyl((0, 0, 0), r, L * 0.98, ax, 14, "frame", "frame", 0.004)
    n = max(2, int(L / 0.35))
    for i in range(n + 1):
        p = -L / 2 + 0.04 + i * (L - 0.08) / n
        c = (p, 0, 0) if horiz else (0, 0, p)
        B.cyl(c, r * 1.25, 0.03, ax, 14, "trim", "cover", 0.0)
    for k in (-1, 1):
        c = (k * r * 0.95, -r * 0.2, 0) if not horiz else (0, -r * 0.2, k * r * 0.95)
        B.cyl(c, r * 0.3, L * 0.96, ax, 8, "cable", "cable", 0.0)
    jb = min(w, h) * 0.9
    B.box((0, -r * 0.3, 0), (jb if horiz else jb, d * 0.6, jb), "panel", "cover", 0.006)
    B.light_strip((0, -r * 0.3 - d * 0.3 - 0.002, 0), (jb * 0.4, 0.004, 0.01), "emit2")


def reactor_module(B, w, h, d, rng, spec):
    """Compact reactor module: shielded drum with a glowing sight window and coolant ports."""
    z0, z1 = -h / 2, h / 2
    r = min(w, d) * 0.44
    B.box((0, 0, z0 + 0.04), (w, d, 0.08), "dark", "frame", 0.01)
    B.lathe([(0, z0 + 0.08), (r * 0.95, z0 + 0.08), (r, z0 + 0.12), (r, z1 - 0.12), (r * 0.8, z1 - 0.04),
             (r * 0.5, z1), (0, z1)], (0, 0, 0), 24, "frame", "frame")
    B.box((0, -r * 0.92, 0.0), (r * 0.7, 0.04, h * 0.36), "trim", "frame", 0.008)
    B.box((0, -r * 0.94 - 0.006, 0.0), (r * 0.5, 0.012, h * 0.26), "emit", "emit", 0.0)
    B.pane((0, -r * 0.94 - 0.018, 0.0), r * 0.54, h * 0.3, 0.006)
    for sx in (-1, 1):
        B.cyl((sx * r * 0.95, 0, z0 + h * 0.3), 0.04, 0.08, "X", 10, "trim", "greeble", 0.004)
        B.cable_run((sx * r * 1.0, -0.02, z0 + h * 0.3), (sx * (w / 2 - 0.02), -0.05, z0 + 0.1), 0.02, 0.016, 6)
    for i in range(2):
        B.ring((0, 0, z0 + h * (0.28 + 0.44 * i)), r * 1.05, r * 0.96, 0.04, "Z", 24, "trim", "cover", 0.0)


def cooling_unit(B, w, h, d, rng, spec):
    import helix
    helix.cooling_stack(B, w, h, d, rng, spec)


def S(kind, var, mat, w_px, h_px, depth, fn, kit="structural", **kw):
    sid = f"SHR-CMP-{kind.upper()}-{var}"
    d = dict(id=sid, kind=kind, chapter=CH, material=mat, w=w_px / 100.0, h=h_px / 100.0, d=depth, build=fn,
             emit="white", emit2="orange", ref_px=[w_px, h_px], kit=kit)
    d.update(kw)
    return d


SPECS = [
    # structural
    S("generic_block_alloy", "A", "lightweight_alloy", 50, 50, 0.8, block_alloy),
    S("generic_block_alloy", "B", "lightweight_alloy", 40, 80, 0.8, block_alloy),
    S("generic_block_steel", "A", "reinforced_steel", 50, 50, 0.8, block_steel),
    S("generic_block_steel", "B", "reinforced_steel", 60, 80, 0.8, block_steel),
    S("generic_block_concrete", "A", "concrete", 50, 50, 0.8, block_concrete),
    S("generic_block_concrete", "B", "concrete", 120, 60, 0.8, block_concrete),
    S("generic_block_concrete", "C", "concrete", 60, 60, 0.8, block_concrete),
    S("generic_panel_glass", "A", "glass_polymer", 14, 90, 0.8, panel_glass),
    S("generic_panel_glass", "B", "glass_polymer", 60, 80, 0.8, panel_glass),
    S("generic_panel_glass", "C", "glass_polymer", 100, 80, 0.8, panel_glass),
    S("generic_beam_composite", "A", "composite", 130, 20, 0.8, beam_composite),
    S("generic_beam_composite", "B", "composite", 170, 20, 0.8, beam_composite),
    S("generic_beam_composite", "C", "composite", 240, 20, 0.8, beam_composite),
    S("generic_frame_alloy", "A", "lightweight_alloy", 60, 60, 0.8, frame_alloy, cover_loss=0.5),
    S("generic_frame_alloy", "B", "lightweight_alloy", 100, 80, 0.8, frame_alloy, cover_loss=0.5),
    S("generic_column_steel", "A", "reinforced_steel", 30, 140, 0.6, column_steel),
    S("generic_column_steel", "B", "reinforced_steel", 40, 200, 0.6, column_steel),
    S("generic_column_concrete", "A", "concrete", 30, 90, 0.6, column_concrete),
    S("generic_column_concrete", "B", "concrete", 40, 180, 0.6, column_concrete),
    S("generic_column_concrete", "C", "concrete", 60, 260, 0.8, column_concrete),
    S("generic_platform_composite", "A", "composite", 160, 20, 1.2, platform_composite),
    S("generic_platform_composite", "B", "composite", 220, 20, 1.2, platform_composite),
    S("generic_platform_composite", "C", "composite", 400, 20, 1.2, platform_composite),
    S("generic_panel_reinforced", "A", "reinforced_steel", 30, 120, 1.0, panel_reinforced),
    S("generic_panel_reinforced", "B", "reinforced_steel", 20, 100, 1.0, panel_reinforced),
    S("generic_wall_industrial", "A", "reinforced_steel", 60, 120, 0.6, wall_industrial),
    S("generic_wall_industrial", "B", "reinforced_steel", 120, 120, 0.6, wall_industrial),
    S("generic_joint_steel", "A", "reinforced_steel", 20, 20, 0.4, joint_steel),
    S("generic_joint_steel", "B", "reinforced_steel", 30, 30, 0.5, joint_steel),
    S("generic_panel_polymer", "A", "composite", 50, 50, 0.6, panel_polymer),
    S("generic_panel_polymer", "B", "composite", 16, 110, 0.6, panel_polymer),
    S("generic_casing_reactor", "A", "reinforced_steel", 60, 80, 0.8, casing_reactor, emit2="orange"),
    # electronic
    S("server_cabinet", "A", "electronic_module", 40, 100, 0.8, server_cabinet, kit="electronic", emit="cyan"),
    S("control_module", "A", "electronic_module", 60, 60, 0.8, control_module, kit="electronic", emit="cyan"),
    S("control_module", "B", "electronic_module", 80, 50, 0.8, control_module, kit="electronic", emit="cyan"),
    S("data_node", "A", "electronic_module", 30, 40, 0.6, data_node, kit="electronic", emit="cyan"),
    S("data_node", "B", "electronic_module", 40, 50, 0.6, data_node, kit="electronic", emit="cyan"),
    S("relay_unit", "A", "electronic_module", 40, 40, 0.6, relay_unit, kit="electronic", emit="cyan"),
    S("circuit_module", "A", "electronic_module", 40, 40, 0.6, circuit_module, kit="electronic", emit="cyan"),
    S("comms_array", "A", "lightweight_alloy", 30, 120, 0.5, comms_array, kit="electronic", emit="cyan"),
    # energy
    S("energy_cell", "A", "energy_component", 36, 40, 0.5, energy_cell, kit="energy", emit="orange"),
    S("energy_cell", "B", "energy_component", 30, 60, 0.5, energy_cell, kit="energy", emit="orange"),
    S("transformer_unit", "A", "electronic_module", 60, 80, 0.8, transformer_unit, kit="energy", emit="cyan"),
    S("power_conduit", "A", "composite", 120, 20, 0.5, power_conduit, kit="energy", emit="cyan"),
    S("power_conduit", "B", "composite", 20, 120, 0.5, power_conduit, kit="energy", emit="cyan"),
    S("reactor_module", "A", "energy_component", 60, 80, 0.8, reactor_module, kit="energy", emit="orange"),
    S("cooling_unit", "A", "composite", 40, 120, 0.8, cooling_unit, kit="energy", emit="cyan"),
]
