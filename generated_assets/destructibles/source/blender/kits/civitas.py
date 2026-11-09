"""Civitas (2110) component kit.
Form language: pale civic concrete and blue-grey alloy, slender angular tapering forms, louvres and
fins, glass lenses and camera heads, information screens in cold blue, red security pips."""
import math
from mathutils import Vector
import tfjkit as K

CH = "civitas"


def _lens(B, c, r, axis="Y"):
    x, y, z = c
    B.cyl((x, y, z), r * 1.25, r * 0.9, axis, 10, "frame", "greeble", 0.0)
    B.cyl((x, y - r * 0.5, z), r, r * 0.3, axis, 10, "glass_smoked", "greeble", 0.0)
    B.cyl((x, y - r * 0.62, z), r * 0.35, 0.004, axis, 6, "emit", "emit", 0.0)


def civic_column(B, w, h, d, rng, spec):
    z0, z1 = -h / 2, h / 2
    base_h = min(0.12, h * 0.08)
    B.zprism(K.chamfer_rect(w, d * 0.9, w * 0.12), z0, z0 + base_h, "concrete", "frame", 0.01)
    # tapering fluted shaft: angular faceted section
    B.zprism(K.regular(8, w * 0.42, rot=math.pi / 8, sy=d / w * 0.9), z0 + base_h, z1 - 0.06, "concrete", "frame", 0.0,
             top_scale=0.86)
    for k in (-1, 1):
        B.zprism(K.chamfer_rect(w * 0.1, d * 0.1, 0.006, k * w * 0.18, -d * 0.36), z0 + base_h, z1 - 0.06,
                 "frame", "cover", 0.0, top_scale=0.9)
    B.zprism(K.chamfer_rect(w * 1.0, d * 0.85, w * 0.15), z1 - 0.06, z1, "frame", "frame", 0.006)
    B.box((0, -d * 0.37, (z0 + base_h + z1) / 2), (0.01, 0.006, (h - base_h) * 0.7), "internal", "greeble", 0.0)
    if spec.get("lit", True):
        B.light_strip((0, -d * 0.373, (z0 + base_h + z1) / 2 + h * 0.1), (0.004, 0.004, h * 0.25), "emit")
    for k in range(max(1, int(h / 0.6))):
        z = z0 + base_h + (k + 1) * (h - base_h) / (max(1, int(h / 0.6)) + 1)
        B.box((0, -d * 0.36, z), (w * 0.62, 0.02, 0.014), "trim", "frame", 0.0)


def relay_bridge(B, w, h, d, rng, spec):
    z0, z1 = -h / 2, h / 2
    fy = -d / 2
    # angular deck profile: knife nose towards the camera
    prof = [(-d / 2 + 0.02, z1), (d / 2, z1), (d / 2, z0 + h * 0.3), (d * 0.1, z0), (-d / 2 + 0.06, z0 + h * 0.2),
            (-d / 2, z1 - h * 0.25)]
    B.xprism(prof, -w / 2, w / 2, "frame", "frame", 0.0)
    n = max(2, int(w / 0.5))
    for i in range(n):
        x = -w / 2 + (i + 0.5) * w / n
        B.box((x, 0.02, z1 + 0.002), (w / n - 0.02, d * 0.8, 0.004), "panel", "cover", 0.0)
        B.box((x, fy + 0.03, z0 + h * 0.18), (w / n - 0.04, 0.01, h * 0.12), "trim", "cover", 0.0)
    B.light_strip((0, fy + 0.004, z1 - h * 0.15), (w * 0.94, 0.004, 0.008), "emit")
    for i in range(n + 1):
        x = -w / 2 + 0.02 + i * (w - 0.04) / n
        B.box((x, fy + 0.012, z1 - h * 0.35), (0.012, 0.012, h * 0.3), "dark", "greeble", 0.0)


def sensor_mast(B, w, h, d, rng, spec):
    z0, z1 = -h / 2, h / 2
    B.zprism(K.chamfer_rect(w, d * 0.7, w * 0.2), z0, z0 + 0.06, "concrete", "frame", 0.006)
    head_h = min(0.22, h * 0.14)
    B.zprism(K.regular(6, w * 0.22, rot=math.pi / 6), z0 + 0.06, z1 - head_h, "frame", "frame", 0.0, top_scale=0.75)
    for k in range(int(h / 0.4)):
        z = z0 + 0.25 + k * 0.4
        if z < z1 - head_h - 0.1:
            B.box((w * 0.12, -w * 0.12, z), (w * 0.16, 0.012, 0.08), "trim", "cover", 0.0)
    # camera head: angular housing with a lens and a hood
    hz = z1 - head_h / 2
    hd = d * 0.7
    ob = B.box((0, 0.0, hz), (w * 0.95, hd, head_h * 0.55), "trim", "cover", 0.006)
    B.box((0, -hd / 2 + 0.01, hz + head_h * 0.3), (w * 0.95, 0.05, 0.012), "frame", "frame", 0.0)
    _lens(B, (w * 0.12, -hd / 2, hz - head_h * 0.02), min(0.03, head_h * 0.16))
    B.light_strip((-w * 0.3, -hd / 2 - 0.002, hz), (0.012, 0.004, 0.012), "emit2")
    B.cyl((0, 0, z1 - 0.02), 0.006, 0.05, "Z", 6, "dark", "greeble", 0.0)
    B.box((0, -0.01, hz - head_h * 0.4), (w * 0.4, 0.04, 0.04), "dark", "frame", 0.0)


def sensor_array(B, w, h, d, rng, spec):
    z0, z1 = -h / 2, h / 2
    fy = -d * 0.3
    B.box((0, 0, 0), (w, d * 0.5, h), "frame", "frame", 0.01)
    B.box((0, fy - 0.01, 0), (w * 0.92, 0.02, h * 0.88), "panel", "cover", 0.0)
    cols = max(2, int(w / 0.22))
    rows = max(1, int(h / 0.22))
    r = min(w / cols, h / rows) * 0.28
    for i in range(cols):
        for j in range(rows):
            x = -w / 2 + (i + 0.5) * w / cols
            z = z0 + (j + 0.5) * h / rows
            _lens(B, (x, fy - 0.02, z), r)
    B.box((0, fy - 0.025, z1 - 0.02), (w * 0.9, 0.04, 0.012), "trim", "frame", 0.0)
    B.light_strip((w * 0.4, fy - 0.022, z0 + 0.02), (0.02, 0.004, 0.008), "emit")


def civic_screen(B, w, h, d, rng, spec):
    z0, z1 = -h / 2, h / 2
    fy = -d * 0.2
    f = 0.03
    B.box((0, 0, 0), (w, d * 0.35, h), "frame", "frame", 0.01)
    B.box((0, fy - 0.004, 0), (w - 2 * f, 0.01, h - 2 * f), "internal", "internal", 0.0)
    # information screen: scan bands and data blocks, cold blue
    rows = max(3, int((h - 2 * f) / 0.08))
    for j in range(rows):
        z = z0 + f + (j + 0.5) * (h - 2 * f) / rows
        if j % 3 == 1:
            B.light_strip((0, fy - 0.011, z), ((w - 2 * f) * 0.9, 0.003, 0.006), "emit")
        else:
            ww = (w - 2 * f) * rng.uniform(0.25, 0.6)
            B.light_strip((-w / 2 + f + 0.02 + ww / 2, fy - 0.011, z), (ww, 0.003, (h - 2 * f) / rows * 0.45), "emit")
    B.pane((0, fy - 0.016, 0), w - 2 * f, h - 2 * f, 0.006, "glass_smoked")
    B.box((0, fy - 0.02, z1 - f / 2), (w, 0.03, f), "trim", "frame", 0.0)
    B.box((0, fy - 0.02, z0 + f / 2), (w, 0.03, f), "trim", "frame", 0.0)
    B.light_strip((w / 2 - f - 0.02, fy - 0.036, z1 - f / 2), (0.014, 0.004, 0.01), "emit2")


def data_exchange_rack(B, w, h, d, rng, spec):
    z0, z1 = -h / 2, h / 2
    fy = -d / 2
    B.box((0, 0, z0 + 0.03), (w, d, 0.06), "dark", "frame", 0.008)
    B.zprism(K.chamfer_rect(w, d, 0.05), z1 - 0.06, z1, "trim", "frame", 0.006)
    for sx in (-1, 1):
        B.box((sx * (w / 2 - 0.02), 0, 0), (0.04, d, h - 0.12), "frame", "frame", 0.008)
    B.box((0, d * 0.3, 0), (w - 0.08, d * 0.3, h - 0.12), "internal", "internal", 0.0)
    # angled louvre fins in front of modules
    n = max(5, int((h - 0.2) / 0.06))
    for k in range(n):
        z = z0 + 0.1 + (k + 0.5) * (h - 0.2) / n
        ob = B.box((0, fy + 0.04, z), (w - 0.08, 0.05, 0.008), "panel", "cover", 0.0)
        K.rotate(ob, -30, "X", (0, fy + 0.04, z))
        if k % 2 == 0:
            B.light_strip((-w * 0.2 + rng.uniform(-0.05, 0.05), fy + 0.08, z), (w * 0.35, 0.004, 0.006), "emit")
    B.box((0, fy + 0.012, z1 - 0.09), (w - 0.08, 0.02, 0.04), "trim", "frame", 0.0)
    B.light_strip((w * 0.3, fy + 0.0, z1 - 0.09), (0.02, 0.004, 0.012), "emit2")
    B.light_strip((-w * 0.1, fy + 0.0, z1 - 0.09), (w * 0.4, 0.004, 0.006), "emit")


def security_wall(B, w, h, d, rng, spec):
    z0, z1 = -h / 2, h / 2
    B.box((0, 0, z0 + 0.05), (w, d, 0.1), "concrete", "frame", 0.01)
    B.zprism(K.chamfer_rect(w * 0.7, d * 0.6, 0.04), z0 + 0.1, z1 - 0.05, "frame", "frame", 0.006, top_scale=0.92)
    n = max(3, int(h / 0.3))
    for k in range(n):
        z = z0 + 0.12 + (k + 0.5) * (h - 0.2) / n
        ob = B.box((0, -d * 0.32, z), (w * 0.82, 0.03, (h - 0.2) / n * 0.7), "panel", "cover", 0.0)
        K.rotate(ob, 12, "X", (0, -d * 0.32, z))
    B.box((0, 0, z1 - 0.025), (w * 0.85, d * 0.7, 0.05), "trim", "frame", 0.006)
    B.light_strip((0, -d * 0.35 - 0.003, z1 - 0.025), (w * 0.5, 0.004, 0.01), "emit2")
    B.light_strip((0, -d * 0.5 - 0.002, z0 + 0.05), (w * 0.5, 0.004, 0.008), "emit")


def surveillance_core(B, w, h, d, rng, spec):
    """Civitas critical asset: the surveillance core. White angular housing holding a great red-lit
    lens eye with an iris ring, flanked by data spines and a hexagonal plinth."""
    z0, z1 = -h / 2, h / 2
    B.zprism(K.regular(6, w * 0.5 / math.cos(math.pi / 6), rot=math.pi / 6, sy=d / w * 0.86), z0, z0 + h * 0.12, "dark", "frame", 0.01)
    B.zprism(K.regular(6, w * 0.36, rot=0, sy=d / w * 1.1), z0 + h * 0.12, z0 + h * 0.3, "polymer", "frame", 0.006,
             top_scale=0.8)
    ec = (0, 0, z0 + h * 0.62)
    R = min(w * 0.3, h * 0.3)
    B.ring(ec, R * 1.25, R * 0.95, d * 0.5, "Y", 6, "polymer", "frame", 0.006)
    for k in range(6):
        a = k * math.pi / 3
        c = (ec[0] + R * 1.2 * math.cos(a), -d * 0.05, ec[2] + R * 1.2 * math.sin(a))
        ob = B.box(c, (R * 0.4, d * 0.55, R * 0.2), "polymer", "cover", 0.0)
        K.rotate(ob, -math.degrees(a), "Y", c)
    B.uvsphere(ec, R * 0.92, 20, 10, "frame", "frame", (1.0, 0.6, 1.0))
    B.cyl((0, -d * 0.2, ec[2]), R * 0.7, 0.04, "Y", 20, "glass_smoked", "greeble", 0.0)
    B.cyl((0, -d * 0.23, ec[2]), R * 0.45, 0.02, "Y", 20, "emit_red", "core", 0.0)
    B.ring((0, -d * 0.24, ec[2]), R * 0.62, R * 0.52, 0.02, "Y", 20, "trim", "frame", 0.0)
    B.cyl((0, -d * 0.25, ec[2]), R * 0.14, 0.01, "Y", 10, "internal", "greeble", 0.0)
    for sx in (-1, 1):
        B.zprism(K.chamfer_rect(w * 0.08, d * 0.3, 0.01, sx * w * 0.44, 0), z0 + h * 0.12, z1 - h * 0.06, "frame",
                 "frame", 0.0, top_scale=0.7)
        for k in range(4):
            B.light_strip((sx * w * 0.44, -d * 0.15 - 0.002, z0 + h * (0.25 + 0.15 * k)), (0.02, 0.004, 0.03), "emit_red")
    B.box((0, 0, z1 - 0.02), (w * 0.3, d * 0.3, 0.04), "trim", "frame", 0.0)


def S(kind, var, mat, w_px, h_px, depth, fn, **kw):
    sid = f"CVT-CMP-{kind.upper()}-{var}"
    d = dict(id=sid, kind=kind, chapter=CH, material=mat, w=w_px / 100.0, h=h_px / 100.0, d=depth, build=fn,
             emit="blue", emit2="red", ref_px=[w_px, h_px], kit="civitas")
    d.update(kw)
    return d


SPECS = [
    S("civic_column", "A", "concrete", 30, 120, 0.5, civic_column),
    S("civic_column", "B", "concrete", 40, 200, 0.6, civic_column),
    S("civic_column", "C", "concrete", 40, 280, 0.6, civic_column, lit=False),
    S("relay_bridge", "A", "composite", 160, 24, 1.2, relay_bridge),
    S("relay_bridge", "B", "composite", 240, 24, 1.2, relay_bridge),
    S("sensor_mast", "A", "lightweight_alloy", 22, 160, 0.3, sensor_mast),
    S("sensor_mast", "B", "lightweight_alloy", 22, 240, 0.3, sensor_mast),
    S("sensor_array", "A", "glass_polymer", 60, 40, 0.5, sensor_array),
    S("sensor_array", "B", "glass_polymer", 90, 60, 0.5, sensor_array),
    S("civic_screen", "A", "glass_polymer", 60, 100, 0.5, civic_screen),
    S("civic_screen", "B", "glass_polymer", 120, 70, 0.5, civic_screen),
    S("data_exchange_rack", "A", "electronic_module", 40, 120, 0.8, data_exchange_rack),
    S("data_exchange_rack", "B", "electronic_module", 50, 90, 0.8, data_exchange_rack),
    S("security_wall", "A", "reinforced_steel", 30, 140, 1.0, security_wall),
    S("security_wall", "B", "reinforced_steel", 40, 200, 1.0, security_wall),
    S("surveillance_core", "A", "ai_core_module", 70, 110, 0.8, surveillance_core, critical=True),
]


# ---------------------------------------------------------------- premium pass (2026-11-10): secondary detail
import tfjdetail as Dt


def _p_column(B, w, h, d, rng, spec):
    base_h = min(0.12, h * 0.08)
    Dt.bolts(B, [(sx * w * 0.3, -h / 2 + base_h / 2) for sx in (-1, 1)], -d * 0.45 - 0.001, 0.014)  # plinth bolts
    Dt.top_hatch(B, 0, 0, h / 2, w * 0.6, d * 0.45, "panel")
    Dt.status_leds(B, -0.02, h / 2 - 0.1, -d * 0.425 - 0.002, 2, 0.022, (0.012, 0.006), "emit", "emit2", rng)


def _p_bridge(B, w, h, d, rng, spec):
    z0 = -h / 2
    Dt.loom(B, (-w / 2 + 0.1, -d * 0.05, z0 + 0.03), (w / 2 - 0.1, -d * 0.05, z0 + 0.03), 2, 0.012, 0.03, 0.03,
            (0, 1, 0), seg=6)
    n = max(2, int(w / 0.5))
    Dt.bolts(B, [(-w / 2 + (i + 0.5) * w / n + sx * (w / n / 2 - 0.05), h / 2 - h * 0.15) for i in range(n) for sx in (-1, 1)],
             -d / 2 + 0.002, 0.012)


def _p_mast(B, w, h, d, rng, spec):
    z0, z1 = -h / 2, h / 2
    B.cyl((-w * 0.2, w * 0.05, 0), 0.008, h - 0.4, "Z", 6, "cable", "cable", 0.0)
    Dt.bolts(B, [(sx * w * 0.32, z0 + 0.03) for sx in (-1, 1)], -d * 0.35 - 0.002, 0.012)
    Dt.top_hatch(B, 0, 0, z1 - min(0.22, h * 0.14) / 2 + min(0.22, h * 0.14) * 0.275, w * 0.6, d * 0.4, "panel")


def _p_array(B, w, h, d, rng, spec):
    Dt.dress(B, CH, w, h, d, -d * 0.25, rng, leds=False, top_d=0.0, inset=0.02)
    Dt.louvre(B, 0, 0.0, w * 0.5, d * 0.2, h / 2, 4, "dark", "internal", normal="+Z")


def _p_screen(B, w, h, d, rng, spec):
    Dt.dress(B, CH, w, h, d, -d * 0.175, rng, leds=False, screen=False, inset=0.012)
    Dt.status_leds(B, -w / 2 + 0.05, -h / 2 + 0.015, -d * 0.2 - 0.025, 3, 0.022, (0.012, 0.006), "emit", "emit2", rng)


def _p_rack(B, w, h, d, rng, spec):
    Dt.top_hatch(B, 0, 0, h / 2, w * 0.6, d * 0.5, "panel")
    Dt.side_seams(B, -d / 2 + 0.06, d / 2 - 0.06, -h / 2 + 0.08, h / 2 - 0.08, -w / 2, -1, 2, max(2, int(h / 0.4)))
    Dt.bolts(B, [(sx * (w / 2 - 0.02), zz) for sx in (-1, 1) for zz in (-h / 2 + 0.1, h / 2 - 0.1)], -d / 2 - 0.0, 0.012)


def _p_wall(B, w, h, d, rng, spec):
    n = max(3, int(h / 0.3))
    pts = []
    for k in range(n):
        z = -h / 2 + 0.12 + (k + 0.5) * (h - 0.2) / n
        pts += [(sx * w * 0.36, z) for sx in (-1, 1)]
    Dt.bolts(B, pts, -d * 0.32 - 0.02, 0.014)
    Dt.top_hatch(B, 0, 0, h / 2, w * 0.6, d * 0.4, "panel")
    Dt.side_seams(B, -d * 0.3, d * 0.3, -h / 2 + 0.15, h / 2 - 0.1, -w * 0.35, -1, 2, max(2, int(h / 0.5)))


def _p_core(B, w, h, d, rng, spec):
    z0 = -h / 2
    Dt.bolts(B, [(x, z0 + h * 0.06) for x in (-w * 0.3, -w * 0.1, w * 0.1, w * 0.3)], -d * 0.43 - 0.002, 0.016)
    for sx in (-1, 1):
        Dt.loom(B, (sx * w * 0.44, 0.0, z0 + h * 0.2), (sx * w * 0.2, 0.0, z0 + h * 0.3), 2, 0.008, 0.02, 0.02,
                (0, 1, 0), seg=5)


PREMIUM = {"civic_column": _p_column, "relay_bridge": _p_bridge, "sensor_mast": _p_mast, "sensor_array": _p_array,
           "civic_screen": _p_screen, "data_exchange_rack": _p_rack, "security_wall": _p_wall,
           "surveillance_core": _p_core}


def _wrap(fn, extra):
    def build(B, w, h, d, rng, spec):
        fn(B, w, h, d, rng, spec)
        extra(B, w, h, d, rng, spec)
    return build


for _s in SPECS:
    if _s["kind"] in PREMIUM and not _s.get("_premium"):
        _s["build"] = _wrap(_s["build"], PREMIUM[_s["kind"]])
        _s["_premium"] = True
