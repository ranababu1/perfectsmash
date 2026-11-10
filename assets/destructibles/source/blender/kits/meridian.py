"""Meridian (2140) component kit.
Form language: monumental dark stone and polished pale alloy, rings and arcs, segments that float
apart on thin glowing seams, layered strata from earlier chapters, violet and cyan temporal light."""
import math
from mathutils import Vector
import tfjkit as K

CH = "meridian"


def anchor_column(B, w, h, d, rng, spec):
    z0, z1 = -h / 2, h / 2
    base_h = min(0.16, h * 0.08)
    B.zprism(K.chamfer_rect(w, d * 0.9, w * 0.25), z0, z0 + base_h, "frame", "frame", 0.01)
    B.zprism(K.chamfer_rect(w * 0.9, d * 0.82, w * 0.22), z1 - 0.08, z1, "trim", "frame", 0.008)
    # stacked stone segments separated by glowing temporal seams
    n = max(3, int(round((h - base_h - 0.08) / 0.38)))
    seg = (h - base_h - 0.08) / n
    for i in range(n):
        za = z0 + base_h + i * seg
        sc = 0.78 + 0.08 * math.sin(i * 1.7)
        B.zprism(K.chamfer_rect(w * sc, d * 0.7 * sc, w * 0.2), za + 0.012, za + seg - 0.012, "panel", "cover", 0.006)
        B.zprism(K.chamfer_rect(w * 0.5, d * 0.45, w * 0.1), za - 0.012, za + 0.012, "emit", "emit", 0.0)
        B.box((0, -d * 0.35 * sc - 0.002, za + seg * 0.5), (w * sc * 0.6, 0.004, 0.008), "trim", "greeble", 0.0)
    B.zprism(K.chamfer_rect(w * 0.3, d * 0.3, w * 0.06), z0 + base_h, z1 - 0.08, "internal", "internal", 0.0)
    for k in range(max(1, n // 2)):
        zc = z0 + base_h + (2 * k + 1) * seg
        B.ring((0, 0, zc), w * 0.5, w * 0.43, 0.03, "Z", 16, "trim", "frame", 0.0)
        K.scale(B.parts[-1], (1.0, d / w * 0.9, 1.0), (0, 0, zc))


def convergence_deck(B, w, h, d, rng, spec):
    z0, z1 = -h / 2, h / 2
    fy = -d / 2
    prof = [(-d / 2, z1 - h * 0.15), (-d / 2 + h * 0.15, z1), (d / 2, z1), (d / 2, z0), (-d / 2 + h * 0.35, z0)]
    B.xprism(prof, -w / 2, w / 2, "frame", "frame", 0.0)
    n = max(2, int(w / 0.8))
    for i in range(n):
        x = -w / 2 + (i + 0.5) * w / n
        B.box((x, 0.02, z1 + 0.002), (w / n - 0.04, d * 0.82, 0.004), "panel", "cover", 0.0)
        B.ring((x, 0.02, z1 + 0.004), min(w / n, d) * 0.36, min(w / n, d) * 0.33, 0.004, "Z", 24, "emit", "emit", 0.0)
        B.box((x, fy + h * 0.12, z0 + h * 0.3), (w / n - 0.08, 0.012, h * 0.26), "trim", "cover", 0.0)
    B.light_strip((0, fy + 0.002, z1 - h * 0.3), (w * 0.96, 0.004, 0.006), "emit")
    for sx in (-1, 1):
        B.box((sx * (w / 2 - 0.03), 0, 0), (0.06, d, h), "trim", "frame", 0.006)


def phase_shield(B, w, h, d, rng, spec):
    z0, z1 = -h / 2, h / 2
    f = min(0.05, w * 0.2)
    B.box((0, 0, z0 + f / 2), (w, min(d, 0.3), f), "frame", "frame", 0.008)
    B.box((0, 0, z1 - f / 2), (w, min(d, 0.3), f), "frame", "frame", 0.008)
    for sx in (-1, 1):
        B.box((sx * (w / 2 - f / 4), 0, 0), (f / 2, min(d, 0.3) * 0.8, h - 2 * f), "trim", "frame", 0.0)
    if w >= 0.3:
        # segmented energy-glass, floating plates with seams
        n = max(2, int(h / 0.35))
        for k in range(n):
            z = z0 + f + (k + 0.5) * (h - 2 * f) / n
            B.pane((0, 0, z), w - f * 1.2, (h - 2 * f) / n - 0.02, 0.014, "glass")
            B.light_strip((0, -0.012, z + (h - 2 * f) / n / 2 - 0.005), (w - f * 1.4, 0.004, 0.004), "emit")
    else:
        B.pane((0, 0, 0), min(d, 0.3) * 0.7, h - 2 * f, 0.014, "glass", "X")
        B.pane((0, 0, 0), w * 0.5, h - 2 * f, 0.012, "glass")
        B.light_strip((0, -0.012, 0), (0.004, 0.004, h * 0.6), "emit")
    B.light_strip((0, -min(d, 0.3) / 2 - 0.002, z0 + f / 2), (w * 0.5, 0.004, 0.008), "emit2")


def quantum_stabilizer(B, w, h, d, rng, spec):
    z0, z1 = -h / 2, h / 2
    B.zprism(K.regular(8, w * 0.5 / math.cos(math.pi / 8), rot=math.pi / 8, sy=d / w), z0, z0 + h * 0.12, "frame", "frame", 0.008)
    B.zprism(K.regular(8, w * 0.3, rot=math.pi / 8, sy=d / w), z0 + h * 0.12, z0 + h * 0.2, "trim", "frame", 0.006)
    c = (0, 0, z0 + h * 0.58)
    R = min(w * 0.46, h * 0.36)
    # gimbal rings at different angles (frozen mid-rotation)
    for k, (ax, ang) in enumerate((("X", 0), ("X", 50), ("Z", 70))):
        ob = B.ring(c, R * (1.0 - 0.14 * k), R * (0.9 - 0.14 * k), 0.03, "Y", 28, "trim" if k != 1 else "panel", "cover", 0.0)
        K.rotate(ob, ang, ax, c)
    B.uvsphere(c, R * 0.36, 16, 8, "emit", "core")
    B.uvsphere(c, R * 0.44, 16, 8, "glass", "greeble")
    B.cyl((0, 0, (z0 + h * 0.2 + c[2] - R * 0.44) / 2), 0.02, c[2] - R * 0.44 - z0 - h * 0.2, "Z", 8, "frame", "frame", 0.0)
    B.box((0, 0, c[2] + R + 0.02), (w * 0.2, d * 0.2, 0.03), "trim", "frame", 0.0)
    B.cyl((0, 0, (c[2] + R + 0.035 + z1) / 2), 0.015, max(0.02, z1 - c[2] - R - 0.035), "Z", 8, "frame", "frame", 0.0)
    B.light_strip((0, -d * 0.45 - 0.002, z0 + h * 0.06), (w * 0.3, 0.004, 0.01), "emit2")


def temporal_cell(B, w, h, d, rng, spec):
    z0, z1 = -h / 2, h / 2
    r = min(w, d) * 0.34
    B.zprism(K.chamfer_rect(w, d, w * 0.2), z0, z0 + 0.05, "frame", "frame", 0.006)
    B.zprism(K.chamfer_rect(w * 0.8, d * 0.8, w * 0.18), z1 - 0.04, z1, "trim", "frame", 0.006)
    ch = h - 0.09
    zc = z0 + 0.05 + ch / 2
    B.lathe([(0, -ch / 2), (r, -ch / 2 + 0.03), (r, ch / 2 - 0.03), (0, ch / 2)], (0, 0, zc), 18, "glass", "vessel")
    B.lathe([(0, -ch * 0.32), (r * 0.45, -ch * 0.2), (r * 0.45, ch * 0.2), (0, ch * 0.32)], (0, 0, zc), 12, "emit", "medium")
    for k, zz in enumerate((zc - ch * 0.25, zc, zc + ch * 0.25)):
        B.ring((0, 0, zz), r * 1.2, r * 1.05, 0.018, "Z", 20, "trim", "cover", 0.0)
    for sx in (-1, 1):
        B.box((sx * (w / 2 - 0.02), 0, zc), (0.03, d * 0.4, ch), "frame", "frame", 0.0)


def monolith_slab(B, w, h, d, rng, spec):
    z0, z1 = -h / 2, h / 2
    tall = h >= w
    B.box((0, 0, 0), (w * 0.96, d * 0.7, h * 0.98), "panel", "frame", 0.012)
    B.box((0, 0, z0 + 0.03), (w, d * 0.8, 0.06), "frame", "frame", 0.008)
    # carved channels with violet light, plus strata bands echoing earlier eras
    if tall:
        B.box((0, -d * 0.35 - 0.001, 0), (0.03, 0.01, h * 0.8), "internal", "greeble", 0.0)
        B.light_strip((0, -d * 0.35 - 0.007, h * 0.05), (0.008, 0.004, h * 0.5), "emit")
        for k in range(3):
            z = z0 + h * (0.2 + 0.3 * k)
            B.box((0, -d * 0.35 - 0.003, z), (w * 0.9, 0.006, 0.016), "trim", "cover", 0.0)
    else:
        B.box((0, -d * 0.35 - 0.001, 0), (w * 0.85, 0.01, 0.03), "internal", "greeble", 0.0)
        B.light_strip((0, -d * 0.35 - 0.007, 0), (w * 0.7, 0.004, 0.008), "emit")
        for k in range(max(2, int(w / 0.4))):
            x = -w / 2 + (k + 0.5) * w / max(2, int(w / 0.4))
            B.box((x, -d * 0.35 - 0.003, z1 - h * 0.25), (0.016, 0.006, h * 0.3), "trim", "cover", 0.0)


def timeline_relay(B, w, h, d, rng, spec):
    z0, z1 = -h / 2, h / 2
    B.zprism(K.chamfer_rect(w, d, w * 0.25), z0, z0 + 0.07, "frame", "frame", 0.006)
    B.cyl((0, 0, 0), w * 0.12, h - 0.1, "Z", 10, "trim", "frame", 0.0)
    n = max(3, int(h / 0.35))
    for k in range(n):
        z = z0 + 0.2 + k * (h - 0.35) / max(1, n - 1)
        rr = w * (0.46 - 0.18 * k / max(1, n - 1))
        ob = B.ring((0, 0, z), rr, rr * 0.8, 0.02, "Z", 18, "panel", "cover", 0.0)
        K.rotate(ob, rng.uniform(-14, 14), "X", (0, 0, z))
        B.light_strip((0, -w * 0.12 - 0.002, z), (0.01, 0.004, 0.03), "emit")
    B.uvsphere((0, 0, z1 - 0.04), w * 0.18, 12, 6, "emit2", "core")


def convergence_core(B, w, h, d, rng, spec):
    """Meridian critical asset: the temporal stabiliser at the convergence. White alloy gyroscope of
    nested rings around a red singular core, held by three anchor arms over a stepped dais."""
    z0, z1 = -h / 2, h / 2
    B.zprism(K.regular(12, w * 0.5, sy=d / w), z0, z0 + h * 0.06, "frame", "frame", 0.008)
    B.zprism(K.regular(12, w * 0.4, sy=d / w), z0 + h * 0.06, z0 + h * 0.12, "trim", "frame", 0.006)
    c = (0, 0, z0 + h * 0.56)
    R = min(w * 0.47, (z1 - z0) * 0.42)
    for k, ang in enumerate((0, 60, -60, 90)):
        rr = R * (1.0 - 0.13 * k)
        ob = B.ring(c, rr, rr * 0.9, 0.04, "Y", 32, "polymer" if k % 2 == 0 else "trim", "cover", 0.0)
        K.rotate(ob, ang, "Z" if k == 3 else "X", c)
    B.uvsphere(c, R * 0.28, 18, 9, "emit_red", "core")
    B.uvsphere(c, R * 0.36, 18, 9, "glass", "greeble")
    for k in range(3):
        a = math.radians(210 + k * 60)
        p0 = Vector((w * 0.42 * math.cos(a), 0, z0 + h * 0.12))
        p0.x = w * 0.42 * (k - 1)
        p1 = Vector((R * 1.02 * math.cos(math.radians(200 + 70 * k)), 0, c[2] + R * 1.02 * math.sin(math.radians(200 + 70 * k))))
        if p1.z < c[2]:
            B.strut(p0, p1, 0.04, "polymer", "frame", 0.006)
    B.cyl((0, 0, z1 - 0.03), R * 0.15, 0.06, "Z", 12, "trim", "frame", 0.0)
    B.light_strip((0, -d * 0.5 * 0.97, z0 + h * 0.03), (w * 0.5, 0.004, 0.012), "emit_red")


def S(kind, var, mat, w_px, h_px, depth, fn, **kw):
    sid = f"MRD-CMP-{kind.upper()}-{var}"
    d = dict(id=sid, kind=kind, chapter=CH, material=mat, w=w_px / 100.0, h=h_px / 100.0, d=depth, build=fn,
             emit="violet", emit2="cyan", ref_px=[w_px, h_px], kit="meridian")
    d.update(kw)
    return d


SPECS = [
    S("anchor_column", "A", "reinforced_steel", 30, 160, 0.6, anchor_column),
    S("anchor_column", "B", "reinforced_steel", 40, 260, 0.7, anchor_column),
    S("convergence_deck", "A", "composite", 200, 24, 1.2, convergence_deck),
    S("convergence_deck", "B", "composite", 320, 30, 1.2, convergence_deck),
    S("phase_shield", "A", "glass_polymer", 20, 120, 0.6, phase_shield),
    S("phase_shield", "B", "glass_polymer", 80, 120, 0.6, phase_shield),
    S("quantum_stabilizer", "A", "electronic_module", 50, 80, 0.6, quantum_stabilizer),
    S("temporal_cell", "A", "energy_component", 36, 50, 0.5, temporal_cell),
    S("monolith_slab", "A", "concrete", 60, 160, 0.8, monolith_slab),
    S("monolith_slab", "B", "concrete", 140, 40, 0.8, monolith_slab),
    S("timeline_relay", "A", "lightweight_alloy", 24, 200, 0.4, timeline_relay),
    S("convergence_core", "A", "energy_component", 80, 120, 0.8, convergence_core, critical=True, emit2="red"),
]


# ---------------------------------------------------------------- premium pass (2026-11-10): secondary detail
# Meridian restraint: chiselled grooves, bronze-dark pins and short violet glyph pips, no clutter.
import tfjdetail as Dt


def _glyphs(B, x0, z, fy, n=3, rng=None):
    for i in range(n):
        ww = 0.01 + 0.012 * ((i * 7) % 3)
        B.light_strip((x0 + i * 0.03, fy - 0.002, z), (ww, 0.004, 0.006), "emit")


def _p_anchor(B, w, h, d, rng, spec):
    z0, z1 = -h / 2, h / 2
    base_h = min(0.16, h * 0.08)
    Dt.bolts(B, [(sx * w * 0.32, z0 + base_h / 2) for sx in (-1, 1)], -d * 0.45 - 0.001, 0.016)
    _glyphs(B, -0.03, z0 + base_h * 0.5, -d * 0.45, 3, rng)
    Dt.top_hatch(B, 0, 0, z1, w * 0.5, d * 0.4, "panel")


def _p_deck(B, w, h, d, rng, spec):
    z0, z1 = -h / 2, h / 2
    n = max(2, int(w / 0.8))
    Dt.bolts(B, [(-w / 2 + (i + 0.5) * w / n + sx * (w / n / 2 - 0.07), z0 + h * 0.3) for i in range(n) for sx in (-1, 1)],
             -d / 2 + h * 0.12 - 0.006, 0.012)
    for i in range(n - 1):
        B.box((-w / 2 + (i + 1) * w / n, -d / 2 + h * 0.07, 0), (0.008, 0.01, h * 0.6), "internal", "greeble", 0.0)


def _p_shield(B, w, h, d, rng, spec):
    f = min(0.05, w * 0.2)
    dd = min(d, 0.3)
    Dt.bolts(B, [(sx * (w / 2 - f * 0.8), zz) for sx in (-1, 1) for zz in (-h / 2 + f / 2, h / 2 - f / 2)], -dd / 2 - 0.001, 0.012)
    if w >= 0.3:
        Dt.top_hatch(B, 0, 0, h / 2, w * 0.4, dd * 0.5, "panel")


def _p_stabilizer(B, w, h, d, rng, spec):
    z0 = -h / 2
    Dt.bolts(B, [(x, z0 + h * 0.06) for x in (-w * 0.3, w * 0.3)], -d * 0.46 - 0.001, 0.014)
    _glyphs(B, -w * 0.32, z0 + h * 0.1, -d * 0.46, 2, rng)


def _p_cell(B, w, h, d, rng, spec):
    z0, z1 = -h / 2, h / 2
    Dt.bolts(B, [(sx * w * 0.32, z0 + 0.025) for sx in (-1, 1)], -d / 2 - 0.001, 0.012)
    Dt.top_hatch(B, 0, 0, z1, w * 0.4, d * 0.4, "panel")


def _p_slab(B, w, h, d, rng, spec):
    z0, z1 = -h / 2, h / 2
    fy = -d * 0.35
    Dt.bolts(B, [(sx * (w * 0.48 - 0.04), zz) for sx in (-1, 1) for zz in (z0 + 0.1, z1 - 0.06)], fy - 0.001, 0.016)
    for k in range(2):  # chiselled strata grooves
        z = z0 + h * (0.35 + 0.3 * k)
        B.box((0, fy - 0.001, z), (w * 0.92, 0.004, 0.008), "internal", "greeble", 0.0)
    _glyphs(B, w * 0.18, z0 + 0.12, fy, 3, rng)
    Dt.top_hatch(B, 0, 0, z1 - h * 0.01, w * 0.4, d * 0.35, "panel")


def _p_relay(B, w, h, d, rng, spec):
    z0 = -h / 2
    Dt.bolts(B, [(sx * w * 0.36, z0 + 0.035) for sx in (-1, 1)], -d / 2 - 0.001, 0.012)
    B.cyl((w * 0.16, 0, 0), 0.008, h - 0.3, "Z", 6, "cable", "cable", 0.0)


def _p_core(B, w, h, d, rng, spec):
    z0 = -h / 2
    Dt.bolts(B, [(x, z0 + h * 0.05) for x in (-w * 0.3, -w * 0.1, w * 0.1, w * 0.3)], -d * 0.45 - 0.001, 0.016)


PREMIUM = {"anchor_column": _p_anchor, "convergence_deck": _p_deck, "phase_shield": _p_shield,
           "quantum_stabilizer": _p_stabilizer, "temporal_cell": _p_cell, "monolith_slab": _p_slab,
           "timeline_relay": _p_relay, "convergence_core": _p_core}


def _wrap(fn, extra):
    def build(B, w, h, d, rng, spec):
        fn(B, w, h, d, rng, spec)
        extra(B, w, h, d, rng, spec)
    return build


for _s in SPECS:
    if _s["kind"] in PREMIUM and not _s.get("_premium"):
        _s["build"] = _wrap(_s["build"], PREMIUM[_s["kind"]])
        _s["_premium"] = True
