"""Band landmarks (one per five levels, contract section 19), mid-back layer, bottom-centre origin."""
import math
from mathutils import Vector
import tfjkit as K
from env_common import outline, massing


# ---------------------------------------------------------------- Helix
def hlx_relay_array(B, rng, spec):
    B.zprism(K.chamfer_rect(7.0, 3.0, 0.4), 0, 2.4, "frame", "frame", 0.0)
    B.box((0, -1.51, 1.2), (6.0, 0.02, 0.3), "internal", "greeble", 0.0)
    B.light_strip((0, -1.525, 1.2), (5.0, 0.004, 0.06), "emit")
    for i, (x, hh) in enumerate(((-2.4, 5.5), (-0.6, 7.5), (1.4, 6.2), (2.8, 4.4))):
        B.vtruss(2.4, 2.4 + hh, x - 0.22, x + 0.22, 0, 0.05, int(hh / 0.8), "trim", "frame")
        B.vtruss(2.4, 2.4 + hh, x - 0.22, x + 0.22, 0.4, 0.05, int(hh / 0.8), "frame", "frame")
        top = 2.4 + hh
        if i % 2 == 0:
            d = B.lathe([(0, 0), (0.9, 0.25), (1.0, 0.32), (0.95, 0.34), (0, 0.1)], (0, 0, 0), 20, "panel", "frame")
            K.rotate(d, 70, "X")
            K.rotate(d, -20 + 15 * i, "Z")
            K.translate(d, (x, -0.3, top - 0.6))
        else:
            for k in range(3):
                B.box((x, -0.25, top - 0.6 - k * 0.7), (0.9, 0.08, 0.4), "panel", "cover", 0.0)
        B.light_strip((x, 0.2, top + 0.05), (0.08, 0.08, 0.08), "emit2")


def hlx_logistics_crane(B, rng, spec):
    W, H = 9.0, 6.5
    for sx in (-1, 1):
        B.vtruss(0, H, sx * W / 2 - 0.5, sx * W / 2, -0.9, 0.08, 8, "frame", "frame")
        B.vtruss(0, H, sx * W / 2 - 0.5, sx * W / 2, 0.9, 0.08, 8, "frame", "frame")
        B.box((sx * (W / 2 - 0.25), 0, 0.2), (0.9, 2.4, 0.4), "dark", "frame", 0.02)
    B.truss(-W / 2, W / 2, H, H + 1.0, -0.6, 0.08, 9, "trim", "frame")
    B.truss(-W / 2, W / 2, H, H + 1.0, 0.6, 0.08, 9, "frame", "frame")
    B.box((0, 0, H + 1.05), (W, 1.4, 0.1), "frame", "frame", 0.0)
    B.hazard_band((0, -0.7, H + 0.5), (W * 0.9, 0.02, 0.18), 18)
    tx = 1.2
    B.box((tx, 0, H - 0.3), (1.4, 1.6, 0.8), "panel", "cover", 0.02)
    for sx in (-0.15, 0.15):
        B.cyl((tx + sx, 0, H - 1.6), 0.015, 2.2, "Z", 6, "cable", "cable", 0.0)
    B.box((tx, 0, H - 2.8), (0.6, 0.4, 0.3), "trim", "frame", 0.0)
    B.box((tx, 0, 1.5), (2.2, 1.4, 1.2), "panel", "cover", 0.02)
    B.light_strip((tx, -0.72, 1.5), (1.6, 0.004, 0.05), "emit")
    B.light_strip((tx + 0.6, -0.82, H - 0.3), (0.08, 0.004, 0.08), "emit2")


def hlx_cooling_tower(B, rng, spec):
    B.zprism(K.chamfer_rect(5.0, 3.6, 0.5), 0, 1.0, "dark", "frame", 0.0)
    B.zprism(K.chamfer_rect(4.2, 3.0, 0.5), 1.0, 7.0, "frame", "frame", 0.0, top_scale=0.86)
    for k in range(8):
        z = 1.4 + k * 0.7
        B.box((0, -1.47 + k * 0.024, z), (3.8 - k * 0.07, 0.06, 0.08), "trim", "cover", 0.0)
    B.box((0, -1.5, 4.0), (0.12, 0.02, 5.5), "internal", "greeble", 0.0)
    B.light_strip((0, -1.512, 4.2), (0.03, 0.004, 3.5), "emit")
    for sx in (-1, 1):
        B.cyl((sx * 0.9, 0, 7.15), 0.75, 0.3, "Z", 20, "dark", "frame", 0.0)
        B.ring((sx * 0.9, 0, 7.3), 0.8, 0.7, 0.1, "Z", 20, "trim", "frame", 0.0)
        for k in range(5):
            ob = B.box((sx * 0.9, 0, 7.25), (1.3, 0.12, 0.02), "frame", "greeble", 0.0)
            K.rotate(ob, k * 36, "Z", (sx * 0.9, 0, 7.25))
    B.cable_run((-2.1, -1.0, 6.0), (-2.6, -1.2, 1.2), 0.2, 0.08, 8)
    B.cyl((2.4, -0.4, 3.5), 0.18, 7.0, "Z", 10, "trim", "frame", 0.0)


def hlx_aura_core_chamber(B, rng, spec):
    """The chamber wall around AURA's core: octagonal frame, cyan rings, sealed iris window."""
    W, H = 9.0, 8.0
    B.box((0, 0.6, H / 2), (W, 0.6, H), "frame", "frame", 0.0)
    oct_r = 3.2
    B.ring((0, 0.0, 4.2), oct_r, oct_r - 0.6, 0.8, "Y", 8, "panel", "cover", 0.0)
    B.ring((0, -0.42, 4.2), oct_r - 0.6, oct_r - 0.75, 0.06, "Y", 8, "emit", "emit", 0.0)
    B.ring((0, -0.2, 4.2), 2.1, 1.7, 0.3, "Y", 32, "trim", "frame", 0.0)
    for k in range(8):
        a = k * math.pi / 4 + math.pi / 8
        c = (1.0 * math.cos(a), 0.0, 4.2 + 1.0 * math.sin(a))
        ob = B.box(c, (1.0, 0.1, 0.6), "dark", "cover", 0.0)
        K.rotate(ob, -math.degrees(a), "Y", c)
    B.cyl((0, 0.1, 4.2), 0.35, 0.2, "Y", 16, "emit_white", "core", 0.0)
    for sx in (-1, 1):
        B.zprism(K.chamfer_rect(1.0, 1.2, 0.3, sx * (W / 2 - 0.5), 0.2), 0, H, "panel", "frame", 0.0)
        for k in range(5):
            B.light_strip((sx * (W / 2 - 0.5), -0.402, 1.0 + k * 1.4), (0.5, 0.004, 0.04), "emit")
    B.box((0, 0.1, H - 0.4), (W, 1.2, 0.8), "dark", "frame", 0.0)
    B.box((0, 0, 0.25), (W, 1.4, 0.5), "dark", "frame", 0.0)


# ---------------------------------------------------------------- VITA
def vta_cleanroom_airlock(B, rng, spec):
    W, H = 6.0, 5.0
    B.prism(K.round_rect(W, H, 0.6, 4), 0.8, 0.0, "light", "frame", 0.0)
    K.translate(B.parts[-1], (0, 0, H / 2))
    B.prism(K.round_rect(2.6, 3.2, 0.5, 4), 0.1, -0.42, "internal", "internal", 0.0)
    K.translate(B.parts[-1], (0, 0, 1.75))
    B.prism(K.round_rect(3.0, 3.6, 0.6, 4), 0.06, -0.43, "frame", "frame", 0.0)
    K.translate(B.parts[-1], (0, 0, 1.85))
    for sx in (-1, 1):
        B.pane((sx * 0.62, -0.5, 1.6), 1.2, 3.0, 0.03, "glass")
    B.light_strip((0, -0.47, 3.75), (2.4, 0.004, 0.04), "emit")
    for sx in (-1, 1):
        B.light_strip((sx * 1.65, -0.47, 1.85), (0.03, 0.004, 2.6), "emit")
        B.box((sx * 2.4, -0.42, 2.2), (0.5, 0.04, 0.7), "polymer", "cover", 0.0)
        B.light_strip((sx * 2.4, -0.445, 2.35), (0.3, 0.004, 0.12), "emit")
    B.box((0, -0.45, 0.06), (W * 0.9, 0.3, 0.12), "frame", "frame", 0.0)


def vta_bioreactor_bank(B, rng, spec):
    B.box((0, 0, 0.3), (9.0, 2.0, 0.6), "frame", "frame", 0.02)
    for i in range(4):
        x = -3.3 + i * 2.2
        r, hh = 0.8, 4.2
        B.lathe([(0, 0.6), (r * 1.1, 0.6), (r * 1.1, 1.0), (r, 1.1), (0, 1.1)], (x, 0, 0), 20, "polymer", "frame")
        B.lathe([(0, 1.1), (r, 1.1), (r, 1.1 + hh), (0, 1.1 + hh)], (x, 0, 0), 20, "glass", "vessel")
        B.lathe([(0, 1.15), (r * 0.9, 1.15), (r * 0.9, 1.1 + hh * (0.5 + 0.1 * i)), (0, 1.1 + hh * (0.5 + 0.1 * i))], (x, 0, 0), 16, "emit", "medium")
        B.lathe([(0, 1.1 + hh), (r * 1.1, 1.1 + hh), (r * 0.7, 1.6 + hh), (0, 1.7 + hh)], (x, 0, 0), 20, "polymer", "frame")
        B.cyl((x, 0, 2.0 + hh), 0.1, 0.6, "Z", 8, "trim", "greeble", 0.0)
    B.cyl((0, 0.3, 2.45 + 4.2), 0.12, 8.0, "X", 10, "trim", "frame", 0.0)
    B.light_strip((0, -1.002, 0.3), (8.0, 0.004, 0.05), "emit")


def vta_archive_vault(B, rng, spec):
    W, H = 8.0, 6.0
    B.box((0, 0.3, H / 2), (W, 0.6, H), "light", "frame", 0.0)
    rows, cols = 6, 9
    for j in range(rows):
        for i in range(cols):
            x = -W / 2 + 0.5 + (i + 0.5) * (W - 1.0) / cols
            z = 0.5 + (j + 0.5) * (H - 1.0) / rows
            if abs(x) < 1.3 and z < 3.6:
                continue
            B.box((x, -0.05, z), ((W - 1.0) / cols - 0.06, 0.1, (H - 1.0) / rows - 0.06), "polymer", "cover", 0.0)
            if (i * 7 + j * 3) % 5 == 0:
                B.light_strip((x, -0.102, z), (0.2, 0.004, 0.03), "emit")
    B.ring((0, -0.2, 1.75), 1.4, 1.1, 0.4, "Y", 28, "frame", "frame", 0.0)
    B.cyl((0, -0.1, 1.75), 1.1, 0.12, "Y", 28, "trim", "cover", 0.0)
    for k in range(6):
        ob = B.box((0, -0.18, 1.75), (2.0, 0.04, 0.06), "frame", "greeble", 0.0)
        K.rotate(ob, k * 30, "Y", (0, -0.18, 1.75))
    B.ring((0, -0.42, 1.75), 1.45, 1.4, 0.02, "Y", 28, "emit", "emit", 0.0)
    B.box((0, -0.4, 0.15), (3.0, 0.4, 0.3), "frame", "frame", 0.0)


def vta_growth_chamber(B, rng, spec):
    R = 4.0
    B.zprism(K.round_rect(2 * R + 0.6, 3.0, 0.8, 4), 0, 0.6, "frame", "frame", 0.0)
    # half dome of ribs and glass panes
    n = 9
    for i in range(n + 1):
        a = math.pi * i / n
        pts = []
        for k in range(9):
            t = k / 8 * math.pi / 2
            pts.append((R * math.cos(t) * math.cos(a), -R * 0.35 * math.cos(t) * math.sin(a), 0.6 + R * math.sin(t)))
        B.tube(pts, 0.06, 6, "light", "frame")
    B.uvsphere((0, 0, 0.6), R * 0.98, 18, 8, "glass", "vessel", (1.0, 0.35, 1.0))
    sph = B.parts[-1]
    # keep only the upper half
    import bmesh
    bm = bmesh.new()
    bm.from_mesh(sph.data)
    bmesh.ops.delete(bm, geom=[v for v in bm.verts if v.co.z < -0.01 or v.co.y > 0.05], context="VERTS")
    bm.to_mesh(sph.data)
    bm.free()
    for k in range(5):
        x = -2.4 + k * 1.2
        hh = 0.8 + 1.6 * abs(math.sin(k * 1.3))
        B.cyl((x, 0.0, 0.6 + hh / 2), 0.05, hh, "Z", 6, "frame", "internal", 0.0)
        B.sphere((x, 0, 0.6 + hh), 0.35, 1, "emit", "internal", (1.0, 1.0, 0.7))
    B.light_strip((0, -1.502, 0.3), (7.0, 0.004, 0.05), "emit")


# ---------------------------------------------------------------- Nova Grid
def nvg_intake_turbine(B, rng, spec):
    R = 3.0
    B.box((0, 0.4, 0.5), (8.0, 2.6, 1.0), "concrete", "frame", 0.02)
    B.ring((0, -0.2, 1.0 + R + 0.3), R + 0.4, R, 1.4, "Y", 32, "frame", "frame", 0.0)
    B.ring((0, -0.92, 1.0 + R + 0.3), R + 0.5, R + 0.3, 0.1, "Y", 32, "trim", "frame", 0.0)
    c = (0, -0.1, 1.0 + R + 0.3)
    B.cyl(c, 0.7, 1.0, "Y", 20, "dark", "frame", 0.0)
    B.cyl((0, -0.65, c[2]), 0.45, 0.2, "Y", 16, "trim", "greeble", 0.0)
    for k in range(12):
        a = k * math.pi / 6
        mid = (c[0] + 1.85 * math.cos(a), -0.2, c[2] + 1.85 * math.sin(a))
        ob = B.box(mid, (2.3, 0.05, 0.45), "panel", "cover", 0.0)
        K.rotate(ob, 25, "X", mid)
        K.rotate(ob, -math.degrees(a), "Y", mid)
    for k in range(8):
        a = k * math.pi / 4
        B.strut((c[0] + 0.7 * math.cos(a), -0.8, c[2] + 0.7 * math.sin(a)), (c[0] + R * math.cos(a), -0.8, c[2] + R * math.sin(a)), 0.08, "frame", "frame")
    B.ring((0, -0.95, c[2]), R + 0.05, R - 0.05, 0.02, "Y", 32, "emit", "emit", 0.0, arc=(200, 340))
    B.hazard_band((0, -0.92, 0.6), (6.0, 0.02, 0.3), 14)


def nvg_cooling_tower(B, rng, spec):
    H = 9.0
    prof_o, prof_i = [], []
    for i in range(9):
        t = i / 8
        r = 3.2 * (0.72 + 0.28 * ((2 * t - 1.25) ** 2) / 1.5625)
        prof_o.append((r, t * H))
        prof_i.append((r - 0.15, t * H))
    B.lathe(prof_o + prof_i[::-1], (0, 0, 0), 28, "concrete", "frame")
    K.scale(B.parts[-1], (1.0, 0.45, 1.0))
    for k in range(14):
        a = math.pi + k * math.pi / 13
        B.strut((3.3 * math.cos(a), 0.45 * 3.3 * math.sin(a), 0.0), (3.6 * math.cos(a + 0.12), 0.45 * 3.6 * math.sin(a + 0.12), 1.0), 0.12, "dark", "frame")
    B.ring((0, 0, H - 0.1), 2.85, 2.6, 0.2, "Z", 28, "trim", "frame", 0.0)
    K.scale(B.parts[-1], (1.0, 0.45, 1.0))
    for k in range(3):
        B.light_strip((-1.0 + k, -1.25 + 0.0, H - 0.6), (0.08, 0.004, 0.08), "emit2")
    B.box((0, -1.25, 5.0), (0.04, 0.02, 3.0), "internal", "greeble", 0.0)


def nvg_transformer_yard(B, rng, spec):
    B.box((0, 0, 0.15), (10.0, 3.0, 0.3), "concrete", "frame", 0.0)
    for i, x in enumerate((-3.2, 0.0, 3.2)):
        B.zprism(K.chamfer_rect(2.0, 1.6, 0.15, x, 0), 0.3, 2.4, "frame", "frame", 0.0)
        for k in range(8):
            B.box((x - 0.8 + k * 0.23, -0.85, 1.35), (0.04, 0.14, 1.8), "panel", "cover", 0.0)
        for k in range(3):
            bx = x - 0.6 + k * 0.6
            for j in range(4):
                B.cyl((bx, 0, 2.5 + j * 0.18), 0.1 - 0.01 * (j % 2), 0.1, "Z", 8, "polymer", "greeble", 0.0)
        B.light_strip((x + 0.6, -0.93, 2.0), (0.15, 0.004, 0.08), "emit")
    for x in (-4.8, 4.8):
        B.vtruss(0.3, 7.0, x - 0.3, x + 0.3, 0, 0.08, 8, "frame", "frame")
        B.box((x, 0, 6.5), (2.2, 0.16, 0.16), "frame", "frame", 0.0)
    for y in (-0.3, 0.3):
        B.cable_run((-4.8, y, 6.4), (4.8, y, 6.4), 1.1, 0.03, 14)
    for x in (-3.2, 0.0, 3.2):
        B.cable_run((x, 0, 3.2), (x + 0.8, 0, 6.0 - 0.9 * (1 - (x / 4.8) ** 2)), 0.2, 0.025, 6)


def nvg_reactor_ring(B, rng, spec):
    R = 4.2
    c = (0, 0, R * 0.55)
    B.ring(c, R, R - 0.9, 1.2, "Y", 36, "frame", "frame", 0.0, arc=(-15, 195))
    B.ring((0, -0.62, c[2]), R + 0.08, R - 0.15, 0.06, "Y", 36, "trim", "frame", 0.0, arc=(-15, 195))
    for k in range(9):
        a = math.radians(-5 + k * 22.5)
        m = (c[0] + (R - 0.45) * math.cos(a), -0.1, c[2] + (R - 0.45) * math.sin(a))
        ob = B.box(m, (0.7, 1.5, 1.1), "panel", "cover", 0.0)
        K.rotate(ob, -(math.degrees(a) - 90), "Y", m)
        ob = B.box((m[0], -0.86, m[2]), (0.4, 0.02, 0.7), "emit", "emit", 0.0)
        K.rotate(ob, -(math.degrees(a) - 90), "Y", (m[0], -0.86, m[2]))
    for sx in (-1, 1):
        B.zprism(K.chamfer_rect(1.6, 2.0, 0.2, sx * (R - 0.4), 0), 0, c[2] - 0.6, "concrete", "frame", 0.0)
    B.cyl((0, 0.5, c[2] + 0.2), 0.7, 2.4, "Z", 16, "dark", "frame", 0.0)
    B.ring((0, 0.5, c[2] + 0.2), 0.78, 0.7, 0.2, "Z", 16, "emit2", "emit", 0.0)


# ---------------------------------------------------------------- Civitas
def cvt_sensor_tower(B, rng, spec):
    H = 10.0
    B.zprism(K.regular(6, 1.6, rot=math.pi / 6), 0, 0.8, "concrete", "frame", 0.0)
    B.zprism(K.regular(6, 0.8, rot=math.pi / 6), 0.8, H - 2.0, "frame", "frame", 0.0, top_scale=0.6)
    for k in range(6):
        z = 1.5 + k * 1.2
        B.box((0, -0.62 + k * 0.05, z), (0.9 - k * 0.05, 0.04, 0.06), "trim", "cover", 0.0)
    B.zprism(K.regular(8, 1.5, rot=math.pi / 8), H - 2.0, H - 1.4, "panel", "frame", 0.0, top_scale=1.2)
    for k in range(8):
        a = k * math.pi / 4 + math.pi / 8
        x, y = 1.55 * math.cos(a), 1.55 * math.sin(a)
        if y > 0.6:
            continue
        B.cyl((x, y, H - 1.7), 0.14, 0.2, "Y", 10, "glass_smoked", "greeble", 0.0)
        B.cyl((x, y - 0.11, H - 1.7), 0.05, 0.02, "Y", 8, "emit2", "emit", 0.0)
    B.ring((0, 0, H - 1.25), 1.9, 1.7, 0.08, "Z", 24, "trim", "frame", 0.0)
    B.light_strip((0, 0, H - 1.25), (3.6, 0.04, 0.02), "emit")
    B.cyl((0, 0, H - 0.6), 0.06, 1.2, "Z", 6, "frame", "greeble", 0.0)
    B.light_strip((0, 0, H), (0.1, 0.1, 0.1), "emit2")


def cvt_screen_wall(B, rng, spec):
    W, H = 10.0, 6.0
    B.box((0, 0.3, H / 2), (W, 0.6, H), "frame", "frame", 0.0)
    cols, rows = 5, 3
    for i in range(cols):
        for j in range(rows):
            x = -W / 2 + 0.3 + (i + 0.5) * (W - 0.6) / cols
            z = 0.6 + (j + 0.5) * (H - 1.0) / rows
            sw, sh = (W - 0.6) / cols - 0.12, (H - 1.0) / rows - 0.12
            B.box((x, -0.04, z), (sw, 0.08, sh), "dark", "frame", 0.0)
            lit = (i + j * 2) % 3 != 1
            if lit:
                for k in range(4):
                    ww = sw * (0.3 + 0.6 * abs(math.sin(i * 3 + j * 5 + k)))
                    B.light_strip((x - sw / 2 + 0.1 + ww / 2, -0.083, z + sh * 0.35 - k * sh * 0.22), (ww, 0.003, sh * 0.1), "emit")
            else:
                # dark standby screen: thin cold-blue status bar, red security pip only on a few (palette: red sparingly)
                B.light_strip((x, -0.083, z - sh * 0.38), (sw * 0.6, 0.003, sh * 0.04), "emit")
                if (i * 7 + j) % 4 == 0:
                    B.light_strip((x + sw * 0.4, -0.083, z + sh * 0.38), (sw * 0.06, 0.003, sh * 0.06), "emit2")
    B.box((0, -0.1, 0.3), (W, 0.4, 0.6), "trim", "frame", 0.0)
    B.box((0, -0.05, H - 0.2), (W, 0.5, 0.4), "trim", "frame", 0.0)


def cvt_prediction_room(B, rng, spec):
    W, H, D = 8.0, 4.5, 3.0
    B.box((0, 0, 0.2), (W, D, 0.4), "concrete", "frame", 0.0)
    B.box((0, 0, H - 0.2), (W + 0.3, D + 0.3, 0.4), "frame", "frame", 0.0)
    B.box((0, D / 2 - 0.1, H / 2), (W, 0.2, H), "panel", "frame", 0.0)
    for k in range(6):
        x = -W / 2 + k * W / 5
        ob = B.box((x, -D / 2 + 0.05, H / 2), (0.1, 0.1, H - 0.8), "trim", "frame", 0.0)
        K.rotate(ob, 8, "Y", (x, 0, H / 2))
    B.pane((0, -D / 2 + 0.1, H / 2), W - 0.2, H - 0.8, 0.03, "glass")
    B.cyl((0, 0, 0.8), 1.2, 0.8, "Z", 20, "frame", "frame", 0.0)
    B.cyl((0, 0, 1.22), 1.25, 0.04, "Z", 20, "emit", "emit", 0.0)
    for k in range(3):
        B.ring((0, 0, 1.6 + k * 0.45), 0.9 - k * 0.2, 0.86 - k * 0.2, 0.02, "Z", 20, "emit", "emit", 0.0)
    for x in (-2.8, 2.8):
        B.box((x, 0.6, 1.0), (1.2, 0.6, 1.2), "frame", "frame", 0.0)
        B.light_strip((x, 0.29, 1.3), (0.9, 0.004, 0.3), "emit")
    B.light_strip((2.8, -D / 2 + 0.06, H - 0.55), (0.12, 0.004, 0.06), "emit2")


def cvt_relay_spire(B, rng, spec):
    H = 11.0
    B.zprism(K.regular(4, 2.0, rot=math.pi / 4), 0, 0.6, "concrete", "frame", 0.0)
    B.zprism(K.regular(4, 1.2, rot=math.pi / 4), 0.6, H, "frame", "frame", 0.0, top_scale=0.04)
    for k in range(5):
        z = 1.2 + k * 1.7
        s = 1.0 - (z - 0.6) / (H - 0.6)
        B.zprism(K.regular(4, 1.3 * s + 0.05, rot=math.pi / 4), z, z + 0.12, "trim", "cover", 0.0)
        B.light_strip((0, -(0.92 * s + 0.04), z + 0.3), (0.06, 0.004, 0.4), "emit")
    for sx in (-1, 1):
        ob = B.box((sx * 0.9, 0, 4.5), (0.08, 0.08, 4.0), "trim", "frame", 0.0)
        K.rotate(ob, sx * 6, "Y", (sx * 0.9, 0, 2.5))
    B.light_strip((0, 0, H - 0.2), (0.08, 0.08, 0.2), "emit2")


# ---------------------------------------------------------------- Meridian
def mrd_hybrid_stack(B, rng, spec):
    """Strata of the earlier facilities fused into one stack: Helix chamfers at the base, VITA
    rounded white band, Nova ribs, Civitas fins, Meridian stone crown with violet seams."""
    z = 0.0
    W = 7.0
    bands = [("dark", 1.6, "chamfer"), ("polymer", 1.1, "round"), ("frame", 1.4, "rib"), ("trim", 1.0, "fin"), ("panel", 1.8, "stone")]
    for i, (slot, hh, kind) in enumerate(bands):
        w = W * (1.0 - 0.07 * i)
        if kind == "round":
            B.zprism(K.round_rect(w, 2.6, 0.5, 3), z, z + hh, slot, "frame", 0.0)
        else:
            B.zprism(K.chamfer_rect(w, 2.8, 0.35), z, z + hh, slot, "frame", 0.0)
        if kind == "rib":
            for k in range(8):
                B.box((-w / 2 + 0.4 + k * (w - 0.8) / 7, -1.45, z + hh / 2), (0.14, 0.1, hh - 0.1), "dark", "cover", 0.0)
        if kind == "fin":
            for k in range(10):
                ob = B.box((-w / 2 + 0.3 + k * (w - 0.6) / 9, -1.45, z + hh / 2), (0.04, 0.14, hh - 0.1), "frame", "cover", 0.0)
                K.rotate(ob, 25, "Z", K.center_of(ob))
        if kind == "chamfer":
            B.light_strip((0, -1.405, z + hh * 0.6), (w * 0.7, 0.004, 0.04), "emit_cyan")
        B.light_strip((0, -1.42, z + hh + 0.03), (w * 0.95, 0.004, 0.03), "emit")
        z += hh + 0.06
    B.zprism(K.chamfer_rect(3.0, 1.6, 0.3), z, z + 1.0, "panel", "frame", 0.0, top_scale=0.6)


def mrd_foundation_pillars(B, rng, spec):
    B.box((0, 0, 0.3), (11.0, 3.0, 0.6), "frame", "frame", 0.0)
    for i in range(4):
        x = -4.2 + i * 2.8
        hh = 7.5 - abs(i - 1.5) * 0.6
        n = 5
        for k in range(n):
            za = 0.6 + k * hh / n
            sc = 1.0 - 0.05 * k
            B.zprism(K.chamfer_rect(1.4 * sc, 1.4 * sc, 0.3), za + 0.06, za + hh / n - 0.06, "panel", "cover", 0.0)
            B.zprism(K.chamfer_rect(0.8, 0.8, 0.15, x, 0), za - 0.06, za + 0.06, "emit", "emit", 0.0)
            K.translate(B.parts[-2], (x, 0, 0))
        B.zprism(K.chamfer_rect(1.7, 1.7, 0.35, x, 0), 0.6 + hh, 0.9 + hh, "trim", "frame", 0.0)
    B.box((0, 0, 8.2), (11.0, 1.6, 0.6), "frame", "frame", 0.0)


def mrd_temporal_anchor(B, rng, spec):
    B.zprism(K.regular(12, 2.6, sy=0.6), 0, 0.5, "frame", "frame", 0.0)
    B.zprism(K.chamfer_rect(1.0, 1.0, 0.25), 0.5, 4.5, "panel", "frame", 0.0, top_scale=0.7)
    c = (0, 0, 6.2)
    for k, (ang, ax) in enumerate(((0, "X"), (55, "X"), (90, "Z"))):
        ob = B.ring(c, 2.4 - 0.3 * k, 2.2 - 0.3 * k, 0.16, "Y", 32, "trim" if k != 1 else "panel", "cover", 0.0)
        K.rotate(ob, ang, ax, c)
    B.uvsphere(c, 0.6, 18, 9, "emit", "core")
    for k in range(4):
        a = k * math.pi / 2 + math.pi / 4
        p = Vector((2.9 * math.cos(a), 0, c[2] + 2.9 * math.sin(a)))
        ob = B.box(p, (0.5, 0.3, 0.9), "panel", "cover", 0.0)
        K.rotate(ob, -math.degrees(a) + 90, "Y", p)
        B.light_strip((p.x, -0.16, p.z), (0.1, 0.004, 0.5), "emit2")
    B.light_strip((0, -0.51, 2.5), (0.06, 0.004, 3.0), "emit")


def mrd_convergence_chamber(B, rng, spec):
    R = 4.5
    c = (0, 0.4, R + 0.6)
    B.zprism(K.chamfer_rect(10.5, 3.0, 0.4), 0, 0.6, "frame", "frame", 0.0)
    nseg = 16
    for k in range(nseg):
        a0 = k * 360 / nseg + 2.5
        a1 = (k + 1) * 360 / nseg - 2.5
        if 255 < (a0 + a1) / 2 < 285:
            continue
        drift = 0.12 * math.sin(k * 1.9)
        ob = B.ring((c[0], c[1], c[2]), R + drift, R - 0.7 + drift, 0.9, "Y", 32, "panel", "cover", 0.0, arc=(a0, a1))
    B.ring(c, R - 0.75, R - 0.82, 0.06, "Y", 48, "emit", "emit", 0.0)
    B.ring((0, -0.1, c[2]), R + 0.35, R + 0.25, 0.1, "Y", 48, "trim", "frame", 0.0)
    B.ring((0, 0.9, c[2]), R - 1.4, R - 1.6, 0.1, "Y", 32, "emit2", "emit", 0.0)
    for sx in (-1, 1):
        B.zprism(K.chamfer_rect(1.2, 1.6, 0.3, sx * (R + 0.2), 0.4), 0.6, 3.2, "frame", "frame", 0.0, top_scale=0.8)
