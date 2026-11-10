"""VITA Genomics (2092) component kit.
Form language: sterile white polymer over brushed alloy, generous rounded corners, glass everywhere,
recessed light seams in restrained green, capsule and vessel shapes, clean seals and gaskets."""
import math
from mathutils import Vector
import tfjkit as K

CH = "vita"


def lab_column(B, w, h, d, rng, spec):
    z0, z1 = -h / 2, h / 2
    foot = min(0.09, h * 0.07)
    B.zprism(K.round_rect(w, d * 0.86, w * 0.3, 3), z0, z0 + foot, "frame", "frame", 0.006)
    B.zprism(K.round_rect(w, d * 0.86, w * 0.3, 3), z1 - foot, z1, "frame", "frame", 0.006)
    B.zprism(K.round_rect(w * 0.86, d * 0.66, w * 0.38, 4), z0 + foot, z1 - foot, "polymer", "frame", 0.0)
    # two-piece clamshell covers with a glowing seam between
    n = max(2, int(round((h - 2 * foot) / 0.5)))
    ph = (h - 2 * foot) / n
    for i in range(n):
        zc = z0 + foot + (i + 0.5) * ph
        for sx in (-1, 1):
            B.zprism(K.round_rect(w * 0.42, d * 0.72, w * 0.16, 2, sx * w * 0.235, 0), zc - ph / 2 + 0.012,
                     zc + ph / 2 - 0.012, "light", "cover", 0.0)
    B.box((0, -d * 0.33, 0), (0.012, 0.01, h - 2 * foot - 0.03), "internal", "greeble")
    if spec.get("lit", True):
        B.light_strip((0, -d * 0.335, 0), (0.005, 0.006, (h - 2 * foot) * 0.6), "emit")
    B.box((0, -d * 0.43 + 0.002, z0 + foot * 0.5), (w * 0.5, 0.004, 0.012), "accent", "greeble")


def lab_deck(B, w, h, d, rng, spec):
    z0, z1 = -h / 2, h / 2
    fy = -d / 2
    B.xprism(K.round_rect(d, h, h * 0.42, 3), -w / 2, w / 2, "polymer", "frame", 0.0)
    # top inlay panels with gaps (visible from above)
    n = max(2, int(w / 0.6))
    for i in range(n):
        x = -w / 2 + (i + 0.5) * w / n
        B.box((x, 0.02, z1 + 0.001), (w / n - 0.03, d * 0.78, 0.004), "light", "cover", 0.0)
    # recessed light seam along the nose
    B.box((0, fy + 0.004, 0), (w * 0.96, 0.01, h * 0.22), "internal", "greeble")
    B.light_strip((0, fy + 0.0, 0), (w * 0.9, 0.004, h * 0.08), "emit")
    for sx in (-1, 1):
        B.xprism(K.round_rect(d * 1.0, h * 1.0, h * 0.45, 3), sx * w / 2 - (0.03 if sx > 0 else 0), sx * w / 2 + (0 if sx > 0 else 0.03), "frame", "frame", 0.0)
    for i in range(max(2, int(w / 0.5)) + 1):
        x = -w / 2 + 0.06 + i * (w - 0.12) / max(2, int(w / 0.5))
        B.box((x, d * 0.2, z0 + 0.01), (0.04, d * 0.4, 0.02), "frame", "frame", 0.0)


def cleanroom_panel(B, w, h, d, rng, spec):
    z0, z1 = -h / 2, h / 2
    f = min(0.045, min(w, h) * 0.16)
    if w >= 0.3:
        y = 0.0
        fd = min(d * 0.5, 0.2)
        B.xprism(K.round_rect(fd, f, f * 0.45, 2), -w / 2, w / 2, "polymer", "frame", 0.0)
        for ob in B.parts[-1:]:
            K.translate(ob, (0, y, z1 - f / 2))
        B.xprism(K.round_rect(fd, f * 1.4, f * 0.45, 2), -w / 2, w / 2, "frame", "frame", 0.0)
        K.translate(B.parts[-1], (0, y, z0 + f * 0.7))
        for xx in (-w / 2 + f / 2, w / 2 - f / 2):
            B.zprism(K.round_rect(f, fd, f * 0.45, 2, xx, y), z0 + f * 1.4, z1 - f, "polymer", "frame", 0.0)
        B.pane((0, y, (z0 + f * 1.4 + z1 - f) / 2), w - 2 * f, h - f * 2.4, 0.012)
        B.box((0, y - fd / 2 - 0.003, z0 + f * 0.7), (w * 0.7, 0.006, f * 0.3), "accent", "greeble")
        B.light_strip((-w / 2 + f / 2, y - fd / 2 - 0.002, z1 - f * 2.5), (0.006, 0.004, h * 0.2), "emit")
        for sx in (-1, 1):
            B.box((sx * (w / 2 - f), 0, z0 + 0.012), (f * 1.4, d * 0.9, 0.024), "frame", "frame", 0.004)
    else:
        B.zprism(K.round_rect(w, d, w * 0.4, 3), z1 - f, z1, "polymer", "frame", 0.0)
        B.zprism(K.round_rect(w, d, w * 0.4, 3), z0, z0 + f, "frame", "frame", 0.0)
        for yy in (-d / 2 + f / 2, d / 2 - f / 2):
            B.box((0, yy, 0), (w * 0.8, f, h - 2 * f), "polymer", "frame", 0.004)
        B.box((0, 0, 0), (w * 0.2, d - 2 * f, h - 2 * f), "glass", "glass", 0.0)
        for sx in (-1, 1):
            B.pane((sx * w * 0.3, 0, 0), d - 2 * f, h - 2 * f, 0.01, "glass", "X")
        B.light_strip((0, -d / 2 + f + 0.003, 0), (0.005, 0.004, h * 0.5), "emit")


def specimen_rack(B, w, h, d, rng, spec):
    z0, z1 = -h / 2, h / 2
    fy = -d / 2
    B.zprism(K.round_rect(w, d, 0.04, 3), z0, z0 + 0.06, "frame", "frame", 0.0)
    B.zprism(K.round_rect(w, d, 0.04, 3), z1 - 0.05, z1, "polymer", "frame", 0.0)
    for sx in (-1, 1):
        B.box((sx * (w / 2 - 0.02), 0, 0), (0.04, d, h - 0.11), "polymer", "frame", 0.012)
    B.box((0, d / 2 - 0.02, 0), (w - 0.08, 0.03, h - 0.11), "light", "frame", 0.0)
    rows = max(3, int((h - 0.2) / 0.22))
    rh = (h - 0.17) / rows
    for r in range(rows):
        zc = z0 + 0.07 + (r + 0.5) * rh
        B.box((0, 0.02, zc - rh / 2 + 0.008), (w - 0.08, d * 0.86, 0.012), "light", "internal", 0.0)
        nv = max(3, min(5, int((w - 0.1) / 0.07)))
        for k in range(nv):
            x = -w / 2 + 0.06 + (k + 0.5) * (w - 0.12) / nv
            lit = (k + 2 * r) % 4 == 0
            B.cyl((x, -d * 0.18, zc - rh * 0.08), 0.014, rh * 0.6, "Z", 6, "emit" if lit else "glass", "internal", 0.0)
        B.box((0, -d * 0.18, zc + rh * 0.26), (w - 0.1, 0.05, 0.016), "frame", "internal", 0.0)
        B.box((0, fy + 0.02, zc + rh / 2 - 0.01), (w - 0.08, 0.02, 0.02), "frame", "cover", 0.0)
    B.pane((0, fy + 0.008, 0.0), w - 0.08, h - 0.12, 0.01)
    B.light_strip((w * 0.3, fy + 0.002, z1 - 0.025), (0.03, 0.004, 0.01), "emit")


def bioreactor(B, w, h, d, rng, spec):
    z0, z1 = -h / 2, h / 2
    r = min(w, d) * 0.43
    base_h, cap_h = h * 0.16, h * 0.12
    B.lathe([(0, z0), (r * 1.15, z0), (r * 1.15, z0 + base_h * 0.6), (r * 1.05, z0 + base_h), (0, z0 + base_h)],
            (0, 0, 0), 28, "polymer", "frame")
    B.lathe([(0, z1 - cap_h), (r * 1.05, z1 - cap_h), (r * 1.12, z1 - cap_h * 0.5), (r * 0.8, z1), (0, z1)],
            (0, 0, 0), 28, "polymer", "frame")
    B.ring((0, 0, z0 + base_h + 0.012), r * 1.06, r * 0.98, 0.024, "Z", 28, "frame", "frame", 0.0)
    B.ring((0, 0, z1 - cap_h - 0.012), r * 1.06, r * 0.98, 0.024, "Z", 28, "frame", "frame", 0.0)
    gh = h - base_h - cap_h - 0.05
    gz = (z0 + base_h + z1 - cap_h) / 2
    B.lathe([(0, -gh / 2), (r, -gh / 2), (r, gh / 2), (0, gh / 2)], (0, 0, gz), 28, "glass", "vessel")
    # culture medium and a suspended growth lattice
    B.lathe([(0, -gh / 2 + 0.01), (r * 0.9, -gh / 2 + 0.01), (r * 0.9, gh * 0.25), (0, gh * 0.25)], (0, 0, gz), 20,
            "emit", "medium")
    for k in range(3):
        B.cyl((0, 0, gz), 0.01, gh * 0.9, "Z", 6, "frame", "internal", 0.0)
        a = k * 2.094
        B.strut((r * 0.5 * math.cos(a), r * 0.5 * math.sin(a), gz - gh * 0.4),
                (r * 0.5 * math.cos(a + 1.5), r * 0.5 * math.sin(a + 1.5), gz + gh * 0.4), 0.012, "light", "internal",
                round_=True, verts=6)
    for k in range(4):
        a = math.pi / 4 + k * math.pi / 2
        B.box((r * 1.02 * math.cos(a), r * 1.02 * math.sin(a), gz), (0.022, 0.022, gh), "frame", "frame", 0.0)
    B.light_strip((0, -r * 1.15 - 0.002, z0 + base_h * 0.4), (r * 0.6, 0.004, 0.012), "emit")
    B.cable_run((r * 0.9, 0, z1 - 0.01), (w / 2 - 0.02, -0.05, z0 + base_h + 0.04), 0.03, 0.012, 8)


def containment_cap(B, w, h, d, rng, spec):
    z0, z1 = -h / 2, h / 2
    B.xprism(K.round_rect(d, h, h * 0.22, 2), -w / 2, w / 2, "concrete", "frame", 0.0)
    B.box((0, -d / 2 + 0.004, z0 + h * 0.3), (w * 0.94, 0.012, 0.016), "frame", "cover", 0.0)
    B.box((0, -d / 2 + 0.004, z1 - h * 0.25), (w * 0.94, 0.012, 0.012), "light", "cover", 0.0)
    for k in range(max(2, int(w / 0.4))):
        x = -w / 2 + (k + 0.5) * w / max(2, int(w / 0.4))
        B.cyl((x, -d / 2 + 0.002, 0), 0.02, 0.008, "Y", 10, "frame", "greeble", 0.0)
    B.light_strip((w * 0.38, -d / 2 + 0.002, z1 - h * 0.25), (0.04, 0.004, 0.008), "emit")
    for k in range(3):
        B.cyl(((k - 1) * w * 0.3, 0, 0), 0.01, h * 0.7, "Z", 6, "scorch", "internal", 0.0)


def cryo_cell(B, w, h, d, rng, spec):
    z0, z1 = -h / 2, h / 2
    r = min(w, d) * 0.38
    B.zprism(K.round_rect(w, d, 0.05, 3), z0, z0 + 0.05, "frame", "frame", 0.0)
    B.zprism(K.round_rect(w * 0.9, d * 0.9, 0.05, 3), z1 - 0.04, z1, "polymer", "frame", 0.0)
    ch = h - 0.11
    B.lathe([(0, -ch / 2), (r * 0.7, -ch / 2), (r, -ch / 2 + 0.04), (r, ch / 2 - 0.04), (r * 0.7, ch / 2), (0, ch / 2)],
            (0, 0, z0 + 0.05 + ch / 2 + 0.005), 22, "glass_frost", "vessel")
    B.lathe([(0, -ch * 0.4), (r * 0.6, -ch * 0.4), (r * 0.6, ch * 0.4), (0, ch * 0.4)], (0, 0, z0 + 0.05 + ch / 2),
            16, "emit", "medium")
    for sx in (-1, 1):
        B.zprism(K.round_rect(0.04, d * 0.6, 0.015, 2, sx * (w / 2 - 0.02), 0), z0 + 0.05, z1 - 0.04, "polymer", "frame", 0.0)
    for zz in (z0 + 0.05 + ch * 0.2, z0 + 0.05 + ch * 0.8):
        B.ring((0, 0, zz), r * 1.08, r * 0.98, 0.03, "Z", 22, "frame", "cover", 0.0)
    B.light_strip((0, -d * 0.45 - 0.002, z0 + 0.025), (w * 0.4, 0.004, 0.01), "emit")


def gene_vault_core(B, w, h, d, rng, spec):
    """VITA critical asset: the central bioreactor vault. White housing, glass vessel, a suspended
    double-helix lattice lit red (critical read), sealing rings and service arms."""
    z0, z1 = -h / 2, h / 2
    r = min(w, d) * 0.42
    base_h, cap_h = h * 0.17, h * 0.13
    B.lathe([(0, z0), (r * 1.18, z0), (r * 1.18, z0 + base_h * 0.5), (r * 1.08, z0 + base_h * 0.62), (r * 1.08, z0 + base_h),
             (0, z0 + base_h)], (0, 0, 0), 32, "polymer", "frame")
    B.lathe([(0, z1 - cap_h), (r * 1.08, z1 - cap_h), (r * 1.15, z1 - cap_h * 0.6), (r * 0.9, z1 - cap_h * 0.1),
             (r * 0.5, z1), (0, z1)], (0, 0, 0), 32, "polymer", "frame")
    for zz in (z0 + base_h + 0.015, z1 - cap_h - 0.015):
        B.ring((0, 0, zz), r * 1.09, r * 0.99, 0.03, "Z", 32, "frame", "frame", 0.0)
    gh = h - base_h - cap_h - 0.06
    gz = (z0 + base_h + z1 - cap_h) / 2
    B.lathe([(0, -gh / 2), (r, -gh / 2), (r, gh / 2), (0, gh / 2)], (0, 0, gz), 32, "glass", "vessel")
    # double helix
    turns, n = 2.2, 22
    for s in (0, math.pi):
        pts = []
        for i in range(n + 1):
            t = i / n
            a = s + t * turns * 2 * math.pi
            pts.append((r * 0.5 * math.cos(a), r * 0.5 * math.sin(a), gz - gh * 0.42 + t * gh * 0.84))
        B.tube(pts, 0.016, 6, "emit_red", "core")
    for i in range(0, n + 1, 2):
        t = i / n
        a = t * turns * 2 * math.pi
        p = Vector((r * 0.5 * math.cos(a), r * 0.5 * math.sin(a), gz - gh * 0.42 + t * gh * 0.84))
        B.strut(p, Vector((-p.x, -p.y, p.z)), 0.01, "light", "internal", round_=True, verts=6)
    for k in range(4):
        a = k * math.pi / 2 + math.pi / 4
        B.box((r * 1.03 * math.cos(a), r * 1.03 * math.sin(a), gz), (0.03, 0.03, gh), "frame", "cover", 0.0)
    B.light_strip((0, -r * 1.18 - 0.002, z0 + base_h * 0.25), (r * 0.8, 0.004, 0.012), "emit")
    B.cyl((0, 0, z0 + base_h + 0.03), r * 0.35, 0.03, "Z", 16, "frame", "internal", 0.0)


def S(kind, var, mat, w_px, h_px, depth, fn, **kw):
    sid = f"VTA-CMP-{kind.upper()}-{var}"
    d = dict(id=sid, kind=kind, chapter=CH, material=mat, w=w_px / 100.0, h=h_px / 100.0, d=depth, build=fn,
             emit="green", emit2="orange", ref_px=[w_px, h_px], kit="vita")
    d.update(kw)
    return d


SPECS = [
    S("lab_column", "A", "lightweight_alloy", 26, 100, 0.5, lab_column),
    S("lab_column", "B", "lightweight_alloy", 26, 160, 0.5, lab_column),
    S("lab_column", "C", "lightweight_alloy", 30, 240, 0.5, lab_column, lit=False),
    S("lab_deck", "A", "composite", 120, 24, 1.2, lab_deck),
    S("lab_deck", "B", "composite", 200, 24, 1.2, lab_deck),
    S("lab_deck", "C", "composite", 320, 24, 1.2, lab_deck),
    S("cleanroom_panel", "A", "glass_polymer", 14, 90, 0.8, cleanroom_panel),
    S("cleanroom_panel", "B", "glass_polymer", 60, 120, 0.8, cleanroom_panel),
    S("cleanroom_panel", "C", "glass_polymer", 100, 80, 0.8, cleanroom_panel),
    S("specimen_rack", "A", "electronic_module", 40, 100, 0.8, specimen_rack),
    S("specimen_rack", "B", "electronic_module", 50, 140, 0.8, specimen_rack),
    S("bioreactor", "A", "glass_polymer", 50, 100, 0.6, bioreactor),
    S("bioreactor", "B", "glass_polymer", 60, 140, 0.7, bioreactor),
    S("containment_cap", "A", "concrete", 120, 30, 1.0, containment_cap),
    S("containment_cap", "B", "concrete", 80, 40, 1.0, containment_cap),
    S("cryo_cell", "A", "energy_component", 36, 50, 0.5, cryo_cell, emit="white"),
    S("gene_vault_core", "A", "ai_core_module", 70, 110, 0.8, gene_vault_core, critical=True, emit2="red"),
]


# ---------------------------------------------------------------- premium pass (2026-11-10): secondary detail
# VITA restraint: gasket lines, flush fasteners, small green status pips, hoses and clean control panels.
import tfjdetail as Dt


def _p_column(B, w, h, d, rng, spec):
    z0, z1 = -h / 2, h / 2
    foot = min(0.09, h * 0.07)
    Dt.status_leds(B, -0.011, z0 + foot * 0.5, -d * 0.43, 2, 0.022, (0.01, 0.005), "emit", None, rng)
    Dt.top_hatch(B, 0, 0, z1, w * 0.5, d * 0.4, "light")


def _p_deck(B, w, h, d, rng, spec):
    z0, z1 = -h / 2, h / 2
    n = max(2, int(w / 0.6))
    for i in range(n + 1):
        x = -w / 2 + 0.05 + i * (w - 0.1) / n
        B.cyl((x, -d / 2 + 0.004, z0 + h * 0.25), 0.01, 0.006, "Y", 8, "frame", "greeble", 0.0)
    B.cyl((0, d * 0.1, z0 - 0.015), 0.014, w * 0.85, "X", 8, "cable", "cable", 0.0)


def _p_panel(B, w, h, d, rng, spec):
    if w >= 0.3:
        f = min(0.045, min(w, h) * 0.16)
        fd = min(d * 0.5, 0.2)
        Dt.bolts(B, [(sx * (w / 2 - f / 2), zz) for sx in (-1, 1) for zz in (-h / 2 + f * 0.7, h / 2 - f / 2)],
                 -fd / 2 - 0.001, 0.01, "frame")


def _p_rack(B, w, h, d, rng, spec):
    Dt.top_hatch(B, 0, 0, h / 2, w * 0.6, d * 0.5, "light")
    Dt.side_seams(B, -d / 2 + 0.06, d / 2 - 0.06, -h / 2 + 0.08, h / 2 - 0.08, -w / 2, -1, 2, max(2, int(h / 0.4)), "light")


def _p_reactor(B, w, h, d, rng, spec):
    z0 = -h / 2
    r = min(w, d) * 0.43
    base_h = h * 0.16
    Dt.screen(B, -r * 0.5, z0 + base_h * 0.55, min(0.12, r * 0.6), base_h * 0.4, -r * 1.15 - 0.004, "emit", "frame", 2, rng)
    Dt.loom(B, (-r * 0.9, -r * 0.3, z0 + base_h + 0.03), (-w / 2 + 0.02, -r * 0.6, z0 + 0.04), 2, 0.01, 0.03, 0.022,
            (0, 1, 0), seg=6)


def _p_cap(B, w, h, d, rng, spec):
    z0, z1 = -h / 2, h / 2
    n = max(2, int(w / 0.4))
    for i in range(n - 1):
        B.box((-w / 2 + (i + 1) * w / n, -d / 2 + 0.002, 0), (0.006, 0.006, h * 0.7), "internal", "greeble", 0.0)
    Dt.screen(B, -w * 0.3, z0 + h * 0.6, min(0.14, w * 0.2), h * 0.25, -d / 2 + 0.0, "emit", "frame", 2, rng)


def _p_cryo(B, w, h, d, rng, spec):
    z0, z1 = -h / 2, h / 2
    Dt.status_leds(B, -w * 0.2, z0 + 0.025, -d * 0.45 - 0.002, 3, 0.02, (0.01, 0.005), "emit", "emit2", rng)
    Dt.top_hatch(B, 0, 0, z1, w * 0.4, d * 0.4, "light")


def _p_core(B, w, h, d, rng, spec):
    z0 = -h / 2
    r = min(w, d) * 0.42
    base_h = h * 0.17
    Dt.screen(B, r * 0.55, z0 + base_h * 0.55, min(0.12, r * 0.5), base_h * 0.35, -r * 1.18 - 0.004, "emit", "frame", 2, rng)


PREMIUM = {"lab_column": _p_column, "lab_deck": _p_deck, "cleanroom_panel": _p_panel, "specimen_rack": _p_rack,
           "bioreactor": _p_reactor, "containment_cap": _p_cap, "cryo_cell": _p_cryo, "gene_vault_core": _p_core}


def _wrap(fn, extra):
    def build(B, w, h, d, rng, spec):
        fn(B, w, h, d, rng, spec)
        extra(B, w, h, d, rng, spec)
    return build


for _s in SPECS:
    if _s["kind"] in PREMIUM and not _s.get("_premium"):
        _s["build"] = _wrap(_s["build"], PREMIUM[_s["kind"]])
        _s["_premium"] = True
