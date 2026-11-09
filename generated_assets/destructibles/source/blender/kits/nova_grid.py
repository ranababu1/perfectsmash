"""Nova Grid (2101) component kit.
Form language: heavy graphite steel and poured concrete, bolted flanges, ribbed cooling fins,
insulator stacks, copper-wound coils, amber heat glow with electric blue arcs, hazard banding."""
import math
from mathutils import Vector
import tfjkit as K

CH = "nova_grid"


def _flange_bolts(B, x0, x1, z, y, n):
    for k in range(n):
        x = x0 + (k + 0.5) * (x1 - x0) / n
        B.cyl((x, y, z), 0.011, 0.012, "Y", 6, "trim", "greeble", 0.0)


def _insulator(B, c, n, r, pitch, axis_down=True):
    x, y, z = c
    for k in range(n):
        B.cyl((x, y, z - k * pitch), r, pitch * 0.45, "Z", 8, "polymer", "greeble", 0.0)
    B.cyl((x, y, z - (n - 1) * pitch / 2), r * 0.35, pitch * n, "Z", 6, "frame", "greeble", 0.0)


def grid_pylon(B, w, h, d, rng, spec):
    z0, z1 = -h / 2, h / 2
    B.box((0, 0, z0 + 0.04), (w, d * 0.9, 0.08), "concrete", "frame", 0.012)
    leg = max(0.035, w * 0.14)
    body_top = z1 - h * 0.16
    for sx in (-1, 1):
        B.strut((sx * w * 0.36, 0, z0 + 0.08), (sx * w * 0.16, 0, body_top), leg, "frame", "frame", 0.006)
    # cross bracing faces
    bays = max(3, int(h / 0.45))
    for k in range(bays):
        za = z0 + 0.08 + k * (body_top - z0 - 0.08) / bays
        zb = za + (body_top - z0 - 0.08) / bays
        fa = 0.36 - (0.2 * (za - z0) / (body_top - z0))
        fb = 0.36 - (0.2 * (zb - z0) / (body_top - z0))
        B.strut((-w * fa, -d * 0.2, za), (w * fb, -d * 0.2, zb), leg * 0.45, "dark", "frame")
        B.strut((w * fa, -d * 0.2, za), (-w * fb, -d * 0.2, zb), leg * 0.45, "dark", "frame")
        B.box((0, -d * 0.2, zb), (2 * w * fb + leg, leg * 0.6, leg * 0.6), "frame", "frame", 0.0)
    # cross arm with insulator strings
    B.box((0, 0, body_top + 0.03), (w, leg * 1.2, 0.06), "frame", "frame", 0.006)
    B.box((0, -leg * 0.6 - 0.006, body_top + 0.03), (w * 0.9, 0.012, 0.02), "hazard", "greeble", 0.0)
    for sx in (-1, 1):
        _insulator(B, (sx * w * 0.42, 0, body_top - 0.02), 4, 0.03, 0.045)
        B.light_strip((sx * w * 0.42, -0.02, body_top - 0.22), (0.012, 0.012, 0.03), "emit2")
    B.zprism(K.chamfer_rect(w * 0.3, leg * 1.4, 0.02), body_top + 0.06, z1, "frame", "frame", 0.006)
    _insulator(B, (0, 0, z1 - 0.02), 3, 0.025, 0.04)
    B.light_strip((0, -leg * 0.7 - 0.002, z0 + 0.04), (w * 0.4, 0.004, 0.012), "emit")


def cable_bridge(B, w, h, d, rng, spec):
    z0, z1 = -h / 2, h / 2
    fy = -d / 2
    B.truss(-w / 2, w / 2, z0, z1, fy + 0.04, max(0.03, h * 0.16), max(3, int(w / 0.45)), "frame", "frame")
    B.truss(-w / 2, w / 2, z0, z1, d / 2 - 0.04, max(0.03, h * 0.16), max(3, int(w / 0.45)), "dark", "frame")
    B.box((0, 0, z1 - 0.015), (w, d * 0.95, 0.03), "panel", "cover", 0.0)
    # heavy cable bundle in trays
    for k in range(3):
        y = -d * 0.25 + k * d * 0.25
        B.cyl((0, y, z0 + h * 0.45), h * 0.12, w * 0.98, "X", 8, "cable", "cable", 0.0)
    for k in range(max(2, int(w / 0.6)) + 1):
        x = -w / 2 + 0.04 + k * (w - 0.08) / max(2, int(w / 0.6))
        B.box((x, fy + 0.01, 0), (0.05, 0.03, h), "trim", "frame", 0.0)
        B.cyl((x, fy - 0.004, z1 - 0.03), 0.01, 0.01, "Y", 6, "trim", "greeble", 0.0)
    B.box((0, fy, z0 + 0.012), (w * 0.98, 0.01, 0.014), "hazard", "greeble", 0.0)
    B.light_strip((0, fy - 0.002, z1 - 0.05), (w * 0.5, 0.004, 0.008), "emit")


def transformer(B, w, h, d, rng, spec):
    z0, z1 = -h / 2, h / 2
    fy = -d / 2
    B.box((0, 0, z0 + 0.04), (w, d, 0.08), "concrete", "frame", 0.01)
    tank_h = h * 0.62
    B.zprism(K.chamfer_rect(w * 0.78, d * 0.7, 0.04), z0 + 0.08, z0 + 0.08 + tank_h, "frame", "frame", 0.008)
    # ribbed radiator fins on the front
    n = max(6, int(w * 0.7 / 0.065))
    for k in range(n):
        x = -w * 0.36 + (k + 0.5) * w * 0.72 / n
        B.box((x, fy + d * 0.15 - 0.03, z0 + 0.08 + tank_h * 0.5), (0.012, 0.06, tank_h * 0.8), "panel", "cover", 0.0)
    B.box((0, fy + d * 0.15 - 0.065, z0 + 0.08 + tank_h * 0.92), (w * 0.74, 0.012, 0.03), "trim", "frame", 0.0)
    B.box((0, fy + d * 0.15 - 0.065, z0 + 0.08 + tank_h * 0.08), (w * 0.74, 0.012, 0.03), "trim", "frame", 0.0)
    # side coolers
    for sx in (-1, 1):
        B.cyl((sx * w * 0.44, 0, z0 + 0.08 + tank_h * 0.45), w * 0.06, tank_h * 0.8, "Z", 10, "dark", "frame", 0.0)
        for k in range(3):
            B.cyl((sx * w * 0.44, 0, z0 + 0.08 + tank_h * (0.2 + 0.25 * k)), w * 0.068, 0.02, "Z", 10,
                  "trim", "greeble", 0.0)
    # lid and HV bushings
    top = z0 + 0.08 + tank_h
    B.zprism(K.chamfer_rect(w * 0.82, d * 0.74, 0.04), top, top + 0.04, "dark", "frame", 0.006)
    for k in range(3):
        x = (k - 1) * w * 0.25
        _insulator(B, (x, 0, z1 - 0.03), min(4, max(3, int((z1 - top - 0.06) / 0.04))), 0.028, (z1 - top - 0.06) / 4)
        B.cyl((x, 0, z1 - 0.012), 0.022, 0.024, "Z", 8, "trim", "greeble", 0.0)
    B.cable_run((-w * 0.25, 0, z1 - 0.03), (w * 0.25, 0, z1 - 0.03), 0.06, 0.008, 10)
    B.hazard_band((w * 0.2, fy + d * 0.15 - 0.072, z0 + 0.08 + tank_h * 0.5), (w * 0.22, 0.006, 0.08), 5)
    B.light_strip((-w * 0.25, fy + d * 0.15 - 0.072, z0 + 0.08 + tank_h * 0.5), (0.04, 0.005, 0.06), "emit")
    B.light_strip((-w * 0.25, fy + d * 0.15 - 0.072, z0 + 0.08 + tank_h * 0.35), (0.04, 0.005, 0.02), "emit2")


def cooling_tower_segment(B, w, h, d, rng, spec):
    """A hyperboloid shell section cut open towards the camera, ribbed and stained."""
    z0, z1 = -h / 2, h / 2
    n = 6
    prof_o = []
    prof_i = []
    for i in range(n + 1):
        t = i / n
        r = 0.5 * w * (0.78 + 0.22 * ((2 * t - 1) ** 2)) if h > w * 0.9 else 0.5 * w * (0.92 + 0.08 * ((2 * t - 1) ** 2))
        prof_o.append((r, z0 + t * h))
        prof_i.append((r - 0.05, z0 + t * h))
    prof = prof_o + prof_i[::-1]
    ob = B.lathe(prof, (0, 0, 0), 22, "concrete", "frame")
    K.scale(ob, (1.0, d / w, 1.0))
    # ribs
    for k in range(9):
        a = math.pi + k * math.pi / 8
        rr = w * 0.5
        B.strut((rr * math.cos(a), rr * math.sin(a) * d / w, z0 + 0.04), (rr * 0.8 * math.cos(a), rr * 0.8 * math.sin(a) * d / w, z1 - 0.04 if h > w else z1 - 0.02),
                0.03, "dark", "cover")
    B.ring((0, 0, z0 + 0.03), w * 0.5 + 0.01, w * 0.44, 0.06, "Z", 22, "frame", "frame", 0.0)
    ob2 = B.parts[-1]
    K.scale(ob2, (1.0, d / w, 1.0))
    B.ring((0, 0, z1 - 0.02), w * 0.5 * (1.0 if h > w * 0.9 else 1.0), w * 0.45, 0.04, "Z", 22, "trim", "frame", 0.0)
    K.scale(B.parts[-1], (1.0, d / w, 1.0))
    B.light_strip((0, -d * 0.5 - 0.002, z0 + 0.03), (w * 0.15, 0.004, 0.012), "emit2")
    for k in range(3):
        x = (k - 1) * w * 0.22
        B.box((x, -d * 0.44, z0 + h * 0.18), (0.04, 0.03, 0.05), "trim", "greeble", 0.0)


def containment_ring_segment(B, w, h, d, rng, spec):
    """Arc of the magnetic containment ring: heavy C-section with coil packs between flanges."""
    R = w * 0.62
    zc = -h / 2 - R + h  # arc top touches the rect top
    arc_deg = math.degrees(2 * math.asin(min(0.99, (w / 2) / R)))
    a0 = 90 - arc_deg / 2
    B.ring((0, 0, zc), R, R - h * 0.55, d * 0.8, "Y", 28, "frame", "frame", 0.006, arc=(a0, a0 + arc_deg))
    B.ring((0, -d * 0.4 - 0.01, zc), R + 0.005, R - h * 0.15, 0.02, "Y", 28, "trim", "frame", 0.0, arc=(a0, a0 + arc_deg))
    ncoil = 5
    for k in range(ncoil):
        a = math.radians(a0 + (k + 0.5) * arc_deg / ncoil)
        rr = R - h * 0.3
        c = (rr * math.cos(a), 0, zc + rr * math.sin(a))
        ob = B.box(c, (h * 0.3, d * 0.92, h * 0.45), "accent", "cover", 0.0)
        K.rotate(ob, -(math.degrees(a) - 90), "Y", c)
        ob = B.box((c[0], -d * 0.47, c[2]), (h * 0.18, 0.01, h * 0.3), "emit", "emit", 0.0)
        K.rotate(ob, -(math.degrees(a) - 90), "Y", c)
    # end flanges
    for s in (-1, 1):
        a = math.radians(90 + s * arc_deg / 2)
        rr = R - h * 0.27
        c = (rr * math.cos(a), 0, zc + rr * math.sin(a))
        ob = B.box(c, (0.04, d, h * 0.62), "dark", "frame", 0.006)
        K.rotate(ob, -(math.degrees(a) - 90), "Y", c)
    B.light_strip((0, -d * 0.4 - 0.022, h / 2 - h * 0.08), (w * 0.2, 0.004, 0.008), "emit2")


def capacitor_cell(B, w, h, d, rng, spec):
    z0, z1 = -h / 2, h / 2
    B.zprism(K.chamfer_rect(w, d, 0.03), z0, z0 + 0.05, "dark", "frame", 0.006)
    B.zprism(K.chamfer_rect(w * 0.94, d * 0.9, 0.03), z1 - 0.05, z1, "frame", "frame", 0.006)
    r = min(w / 4.4, d / 2.4)
    for i, (x, y) in enumerate(((-w * 0.25, -d * 0.2), (w * 0.25, -d * 0.2), (0, d * 0.2))):
        B.cyl((x, y, 0), r, h - 0.1, "Z", 12, "panel", "cover", 0.0)
        for k in range(2):
            B.cyl((x, y, z0 + 0.12 + k * (h - 0.24)), r * 1.06, 0.02, "Z", 12, "trim", "greeble", 0.0)
        B.box((x, y - r - 0.001, 0.0), (r * 0.3, 0.004, h * 0.45), "emit", "emit", 0.0)
    for sx in (-1, 1):
        B.box((sx * (w / 2 - 0.015), 0, 0), (0.03, d * 0.5, h - 0.1), "frame", "frame", 0.0)
    B.hazard_band((0, -d / 2 - 0.002, z0 + 0.025), (w * 0.8, 0.004, 0.03), 6)
    B.light_strip((w * 0.3, -d * 0.47 - 0.002, z1 - 0.025), (0.03, 0.004, 0.012), "emit2")


def containment_wall(B, w, h, d, rng, spec):
    z0, z1 = -h / 2, h / 2
    B.box((0, 0, 0), (w * 0.8, d * 0.75, h), "concrete", "frame", 0.012)
    B.box((0, 0, z0 + 0.06), (w, d, 0.12), "concrete", "frame", 0.012)
    B.box((0, 0, z1 - 0.04), (w * 0.9, d * 0.85, 0.08), "frame", "frame", 0.008)
    # steel rib plates bolted to the front
    n = max(2, int(h / 0.4))
    for k in range(n):
        z = z0 + 0.12 + (k + 0.5) * (h - 0.2) / n
        B.box((0, -d * 0.375 - 0.012, z), (w * 0.84, 0.024, (h - 0.2) / n - 0.03), "panel", "cover", 0.004)
        for sx in (-1, 1):
            B.cyl((sx * w * 0.33, -d * 0.375 - 0.026, z), 0.012, 0.01, "Y", 6, "trim", "greeble", 0.0)
    B.box((0, -d * 0.375 - 0.026, z0 + 0.2), (w * 0.7, 0.006, 0.03), "hazard", "greeble", 0.0)
    B.light_strip((0, -d * 0.375 - 0.027, z1 - 0.12), (w * 0.3, 0.004, 0.01), "emit2")


def reactor_core(B, w, h, d, rng, spec):
    """Nova Grid critical asset: fusion reactor core. White pressure housing on a graphite plinth,
    a red-lit plasma column visible through a slotted window, magnetic ring collars, cable feeds."""
    z0, z1 = -h / 2, h / 2
    r = min(w, d) * 0.36
    B.zprism(K.regular(8, w * 0.5 / math.cos(math.pi / 8), rot=math.pi / 8, sy=d / w), z0, z0 + h * 0.1, "dark", "frame", 0.01)
    B.lathe([(0, z0 + h * 0.1), (r * 1.2, z0 + h * 0.1), (r * 1.2, z0 + h * 0.2), (r * 1.05, z0 + h * 0.24),
             (r, z0 + h * 0.24), (0, z0 + h * 0.24)], (0, 0, 0), 20, "polymer", "frame")
    B.lathe([(0, z1 - h * 0.22), (r, z1 - h * 0.22), (r * 1.1, z1 - h * 0.18), (r * 1.1, z1 - h * 0.08),
             (r * 0.55, z1), (0, z1)], (0, 0, 0), 20, "polymer", "frame")
    mid0, mid1 = z0 + h * 0.24, z1 - h * 0.22
    B.cyl((0, 0, (mid0 + mid1) / 2), r * 0.45, mid1 - mid0, "Z", 14, "emit_red", "core", 0.0)
    for k in range(6):
        a = k * math.pi / 3 + math.pi / 6
        c = (r * 0.92 * math.cos(a), r * 0.92 * math.sin(a), (mid0 + mid1) / 2)
        ob = B.box(c, (r * 0.36, r * 0.16, mid1 - mid0), "polymer", "cover", 0.0)
        K.rotate(ob, math.degrees(a) + 90, "Z", c)
    B.lathe([(0, -(mid1 - mid0) / 2), (r * 0.82, -(mid1 - mid0) / 2), (r * 0.82, (mid1 - mid0) / 2), (0, (mid1 - mid0) / 2)],
            (0, 0, (mid0 + mid1) / 2), 18, "glass_smoked", "vessel")
    for zz in (mid0 + (mid1 - mid0) * 0.3, mid0 + (mid1 - mid0) * 0.7):
        B.ring((0, 0, zz), r * 1.28, r * 0.96, 0.06, "Z", 20, "frame", "frame", 0.0)
        B.ring((0, 0, zz), r * 1.3, r * 1.26, 0.02, "Z", 20, "emit_red", "emit", 0.0)
    for sx in (-1, 1):
        B.cable_run((sx * r * 1.2, -0.05, z0 + h * 0.16), (sx * w * 0.47, -d * 0.1, z0 + h * 0.1), 0.05, 0.022, 8)
    B.hazard_band((0, -d * 0.5 - 0.002, z0 + h * 0.05), (w * 0.6, 0.004, h * 0.05), 8)


def S(kind, var, mat, w_px, h_px, depth, fn, **kw):
    sid = f"NVG-CMP-{kind.upper()}-{var}"
    d = dict(id=sid, kind=kind, chapter=CH, material=mat, w=w_px / 100.0, h=h_px / 100.0, d=depth, build=fn,
             emit="amber", emit2="blue", ref_px=[w_px, h_px], kit="nova_grid")
    d.update(kw)
    return d


SPECS = [
    S("grid_pylon", "A", "reinforced_steel", 40, 200, 0.5, grid_pylon),
    S("grid_pylon", "B", "reinforced_steel", 50, 260, 0.6, grid_pylon),
    S("cable_bridge", "A", "composite", 160, 24, 1.2, cable_bridge),
    S("cable_bridge", "B", "composite", 240, 30, 1.2, cable_bridge),
    S("transformer", "A", "electronic_module", 80, 100, 0.8, transformer),
    S("transformer", "B", "electronic_module", 60, 80, 0.8, transformer),
    S("cooling_tower_segment", "A", "concrete", 80, 120, 0.8, cooling_tower_segment),
    S("cooling_tower_segment", "B", "concrete", 120, 80, 0.8, cooling_tower_segment),
    S("containment_ring_segment", "A", "reinforced_steel", 120, 50, 0.6, containment_ring_segment),
    S("capacitor_cell", "A", "energy_component", 40, 60, 0.5, capacitor_cell, emit="blue", emit2="amber"),
    S("containment_wall", "A", "concrete", 40, 160, 1.0, containment_wall),
    S("containment_wall", "B", "concrete", 60, 120, 1.0, containment_wall),
    S("reactor_core", "A", "energy_component", 80, 120, 0.8, reactor_core, critical=True, emit2="red"),
]
