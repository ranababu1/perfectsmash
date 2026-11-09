"""Helix Systems (2089) component kit.
Form language: cold steel and graphite, 45-degree chamfered corners, vertical rib slots, layered
cladding with real panel gaps, cyan compute light in thin lines, orange only as warning pips."""
import math
from mathutils import Vector
import tfjkit as K

CH = "helix"


def server_rack(B, w, h, d, rng, spec):
    z0, z1 = -h / 2, h / 2
    fy = -d / 2
    post = max(0.03, min(w, d) * 0.09)
    B.box((0, 0, z0 + 0.03), (w, d, 0.06), "dark", "frame", 0.01)
    B.box((0, fy + 0.006, z0 + 0.03), (w * 0.7, 0.012, 0.03), "internal", "greeble", 0.0)  # kick recess
    B.zprism(K.chamfer_rect(w, d, 0.03), z1 - 0.05, z1, "frame", "frame", 0.006)
    B.box((0, fy + 0.03, z1 - 0.065), (w - 2 * post, 0.05, 0.03), "trim", "frame", 0.0)
    for sx in (-1, 1):
        for sy in (-1, 1):
            B.zprism(K.chamfer_rect(post, post, post * 0.3, sx * (w / 2 - post / 2), sy * (d / 2 - post / 2)),
                     z0 + 0.06, z1 - 0.05, "frame", "frame", 0.0)
    for sx in (-1, 1):
        B.side_plate_grid(-d / 2 + post, d / 2 - post, z0 + 0.07, z1 - 0.06, sx * (w / 2 - 0.02), sx, 2, 3,
                          gap=0.012, thick=0.018, slot="panel", role="cover", bevel=0.004)
        for k in range(2):
            B.box((sx * (w / 2 - 0.003), -d * 0.3 + k * 0.045, 0), (0.008, 0.016, h * 0.6), "dark", "greeble")
    B.light_strip((-w / 2 + 0.003, -d / 2 + post + 0.03, z1 - 0.26), (0.006, 0.01, 0.18), "emit")
    B.box((0, d / 2 - 0.02, 0), (w - 2 * post, 0.03, h - 0.12), "frame", "frame", 0.0)
    B.box((0, fy + 0.15, 0), (w - 2 * post, 0.02, h - 0.14), "internal", "internal", 0.0)
    for k in range(3):
        B.box((rng.uniform(-w * 0.12, w * 0.12), fy + 0.13, z0 + 0.2 + k * h * 0.27), (w * 0.5, 0.008, h * 0.16),
              "accent", "internal", 0.0)
    fw = w - 2 * post
    B.box((0, fy + 0.014, z0 + 0.075), (fw, 0.024, 0.03), "trim", "frame", 0.0)
    cols, rows = 2, max(3, int((h - 0.24) / spec.get('blade_pitch', 0.13)))
    gx = 0.012
    bw = (fw - gx * (cols + 1)) / cols
    top, bot = z1 - 0.1, z0 + 0.1
    bh = (top - bot) / rows
    for c in range(cols):
        x = -fw / 2 + gx + bw / 2 + c * (bw + gx)
        for r in range(rows):
            z = bot + (r + 0.5) * bh
            B.box((x, fy + 0.045, z), (bw, 0.06, bh - 0.012), "panel", "cover", 0.0)
            B.light_strip((x - bw * 0.22, fy + 0.0125, z + bh * 0.14), (bw * 0.34, 0.005, 0.009), "emit")
            B.box((x + bw * 0.2, fy + 0.0135, z - bh * 0.05), (bw * 0.36, 0.004, bh * 0.36), "dark", "greeble")
            B.box((x - bw * 0.22, fy + 0.0135, z - bh * 0.18), (bw * 0.34, 0.004, 0.006), "light", "greeble")
    B.light_strip((w * 0.3, fy + 0.0035, z1 - 0.065), (0.016, 0.005, 0.012), "emit2")
    B.light_strip((-w * 0.08, fy + 0.0035, z1 - 0.065), (fw * 0.45, 0.005, 0.007), "emit")
    for sx in (-1, 1):
        B.box((sx * (fw / 2 - 0.006), fy + 0.008, 0), (0.012, 0.016, h * 0.35), "trim", "greeble")


def support_column(B, w, h, d, rng, spec):
    z0, z1 = -h / 2, h / 2
    sw, sd = w * 0.78, d * 0.62
    base_h, cap_h = min(0.1, h * 0.08), min(0.08, h * 0.06)
    B.zprism(K.chamfer_rect(w, d * 0.9, w * 0.18), z0, z0 + base_h, "dark", "frame", 0.008)
    B.zprism(K.chamfer_rect(w * 0.92, d * 0.8, w * 0.16), z0 + base_h, z0 + base_h + 0.025, "trim", "frame", 0.0)
    B.zprism(K.chamfer_rect(w, d * 0.9, w * 0.18), z1 - cap_h, z1, "dark", "frame", 0.008)
    B.zprism(K.chamfer_rect(w * 0.92, d * 0.8, w * 0.16), z1 - cap_h - 0.025, z1 - cap_h, "trim", "frame", 0.0)
    s0, s1 = z0 + base_h + 0.025, z1 - cap_h - 0.025
    B.zprism(K.chamfer_rect(sw, sd, sw * 0.22), s0, s1, "frame", "frame", 0.0)
    # front cladding plates (stretch cleanly: equal plates, repeated)
    n = max(2, int(round((s1 - s0) / 0.42)))
    ph = (s1 - s0) / n
    for i in range(n):
        zc = s0 + (i + 0.5) * ph
        B.box((0, -sd / 2 - 0.009, zc), (sw * 0.82, 0.018, ph - 0.03), "panel", "cover", 0.004)
        B.box((-sw / 2 - 0.008, 0, zc), (0.016, sd * 0.78, ph - 0.03), "panel", "cover", 0.004)
        B.box((sw / 2 + 0.008, 0, zc), (0.016, sd * 0.78, ph - 0.03), "panel", "cover", 0.004)
        B.box((0, -sd / 2 - 0.0185, zc + ph * 0.36), (sw * 0.5, 0.002, 0.006), "light", "greeble")
    # vertical rib slot with a thin compute line
    B.box((0, -sd / 2 - 0.019, (s0 + s1) / 2), (0.014, 0.004, (s1 - s0) * 0.86), "internal", "greeble")
    if spec.get("lit", True):
        B.light_strip((0, -sd / 2 - 0.0205, (s0 + s1) / 2 + (s1 - s0) * 0.2), (0.005, 0.003, (s1 - s0) * 0.3),
                      "emit")
    for sx in (-1, 1):
        B.box((sx * w * 0.32, -d * 0.45 + 0.004, z0 + base_h * 0.55), (0.02, 0.008, 0.02), "trim", "greeble")


def service_deck(B, w, h, d, rng, spec):
    z0, z1 = -h / 2, h / 2
    fy = -d / 2
    top_t = h * 0.32
    B.box((0, 0, z1 - top_t / 2), (w, d, top_t), "frame", "frame", 0.01)
    # top grating strips (visible from above)
    n = max(3, int(w / 0.25))
    for i in range(n):
        x = -w / 2 + (i + 0.5) * w / n
        B.box((x, 0.04, z1 + 0.002), (w / n - 0.03, d * 0.72, 0.004), "dark", "greeble")
    # front fascia: chamfered lower edge, panelled
    B.xprism([(fy, z1 - top_t), (fy, z0 + 0.03), (fy + 0.03, z0), (fy + 0.09, z0), (fy + 0.09, z1 - top_t)],
             -w / 2, w / 2, "panel", "frame", 0.0)
    m = max(2, int(w / 0.5))
    for i in range(m):
        x = -w / 2 + (i + 0.5) * w / m
        B.box((x, fy - 0.006, (z0 + z1 - top_t) / 2 + 0.01), (w / m - 0.02, 0.012, (h - top_t) * 0.62), "panel",
              "cover", 0.003)
        B.box((x - w / m * 0.3, fy - 0.013, (z0 + z1 - top_t) / 2 + 0.01), (0.02, 0.003, 0.02), "trim", "greeble")
        B.box((x + w / m * 0.3, fy - 0.013, (z0 + z1 - top_t) / 2 + 0.01), (0.02, 0.003, 0.02), "trim", "greeble")
    B.light_strip((0, fy - 0.001, z1 - top_t * 0.5), (w * 0.94, 0.004, 0.008), "emit")
    # underside ribs (read through the front at low camera pitch)
    k = max(2, int(w / 0.4))
    for i in range(k + 1):
        x = -w / 2 + 0.04 + i * (w - 0.08) / k
        B.box((x, 0.05, z0 + (h - top_t) / 2), (0.03, d * 0.8, h - top_t), "dark", "frame", 0.0)
    B.box((0, d / 2 - 0.05, (z0 + z1 - top_t) / 2), (w, 0.08, h - top_t), "frame", "frame", 0.0)
    # end caps
    for sx in (-1, 1):
        B.box((sx * (w / 2 - 0.02), 0, (z0 + z1) / 2), (0.04, d, h), "trim", "frame", 0.006)
        B.light_strip((sx * (w / 2 - 0.02), fy - 0.002, z1 - top_t * 0.5), (0.02, 0.004, 0.012), "emit2")


def core_shield(B, w, h, d, rng, spec):
    z0, z1 = -h / 2, h / 2
    B.box((0, 0, 0), (w * 0.7, d, h), "frame", "frame", 0.012)
    # stacked armour plates on both faces and sides
    n = max(2, int(h / 0.26))
    for i in range(n):
        zc = z0 + (i + 0.5) * h / n
        for sx in (-1, 1):
            B.box((sx * (w * 0.35 + 0.012), 0, zc), (0.024, d * 0.92, h / n - 0.018), "panel", "cover", 0.006)
            for k in (-1, 1):
                B.box((sx * (w * 0.35 + 0.025), k * d * 0.38, zc), (0.004, 0.02, 0.02), "trim", "greeble")
        B.box((0, -d / 2 - 0.009, zc), (w * 0.86, 0.018, h / n - 0.018), "panel", "cover", 0.004)
    B.box((0, -d / 2 - 0.0185, 0), (w * 0.3, 0.004, h * 0.8), "dark", "greeble")
    B.box((0, 0, z1 - 0.02), (w, d, 0.04), "trim", "frame", 0.008)
    B.box((0, 0, z0 + 0.02), (w, d, 0.04), "dark", "frame", 0.008)
    B.light_strip((0, -d / 2 - 0.0205, z1 - 0.07), (w * 0.3, 0.003, 0.03), "emit2")


def power_cell(B, w, h, d, rng, spec):
    z0, z1 = -h / 2, h / 2
    r = min(w, d) * 0.36
    B.box((0, 0, z0 + 0.025), (w, d, 0.05), "dark", "frame", 0.01)
    B.box((0, 0, z1 - 0.02), (w, d * 0.9, 0.04), "frame", "frame", 0.008)
    for sx in (-1, 1):
        for sy in (-1, 1):
            B.zprism(K.chamfer_rect(0.03, 0.03, 0.008, sx * (w / 2 - 0.015), sy * (d * 0.45 - 0.015)),
                     z0 + 0.05, z1 - 0.04, "frame", "frame", 0.0)
    ch = h - 0.13
    B.lathe([(0.0, -ch / 2), (r * 0.8, -ch / 2), (r, -ch / 2 + 0.02), (r, ch / 2 - 0.02), (r * 0.8, ch / 2),
             (0.0, ch / 2)], (0, 0, 0.005), 20, "panel", "cover")
    for k, zz in enumerate((-ch * 0.22, ch * 0.22)):
        B.ring((0, 0, zz), r * 1.03, r * 0.9, 0.018, "Z", 20, "emit", "emit", 0.0)
    B.ring((0, 0, 0), r * 1.06, r * 0.9, 0.05, "Z", 20, "trim", "frame", 0.0)
    B.cyl((0, 0, z1 - 0.045), r * 0.35, 0.03, "Z", 10, "trim", "greeble", 0.0)
    for sx in (-1, 1):
        B.cyl((sx * r * 0.55, 0, z1 - 0.045), 0.012, 0.03, "Z", 6, "dark", "greeble", 0.0)
    B.cable_run((-w / 2 + 0.03, -d * 0.2, z1 - 0.06), (-r * 0.9, -d * 0.1, -ch * 0.3), 0.04, 0.008, 8)
    B.box((0, -d * 0.45 + 0.003, z0 + 0.025), (w * 0.4, 0.006, 0.02), "emit2", "emit", 0.0)


def blast_wall(B, w, h, d, rng, spec):
    z0, z1 = -h / 2, h / 2
    B.box((0, 0, 0), (w * 0.62, d, h), "frame", "frame", 0.015)
    n = max(3, int(h / 0.3))
    for i in range(n):
        zc = z0 + (i + 0.5) * h / n
        for sx in (-1, 1):
            B.box((sx * (w * 0.31 + 0.022), 0, zc), (0.044, d * 0.94, h / n - 0.02), "panel", "cover", 0.008)
            B.box((sx * (w * 0.31 + 0.046), -d * 0.3, zc), (0.004, 0.08, h / n * 0.5), "dark", "greeble")
        B.box((0, -d / 2 - 0.008, zc), (w * 0.9, 0.016, h / n - 0.02), "panel", "cover", 0.004)
    for i in range(1, n):
        zc = z0 + i * h / n
        B.box((0, 0, zc), (w, d, 0.03), "trim", "frame", 0.006)
    B.box((0, 0, z0 + 0.03), (w, d, 0.06), "dark", "frame", 0.01)
    B.box((0, 0, z1 - 0.02), (w, d, 0.04), "dark", "frame", 0.008)
    B.light_strip((0, -d / 2 - 0.0175, z1 - 0.1), (w * 0.4, 0.003, 0.02), "emit2")


def relay_mast(B, w, h, d, rng, spec):
    z0, z1 = -h / 2, h / 2
    t = max(0.012, w * 0.08)
    base_h = min(0.14, h * 0.07)
    B.zprism(K.chamfer_rect(w, d, w * 0.2), z0, z0 + base_h, "dark", "frame", 0.008)
    B.zprism(K.chamfer_rect(w * 0.7, d * 0.7, w * 0.12), z1 - 0.06, z1, "frame", "frame", 0.004)
    bays = max(3, int((h - base_h) / 0.28))
    for y in (-d * 0.32, d * 0.32):
        B.vtruss(z0 + base_h, z1 - 0.06, -w * 0.42, w * 0.42, y, t, bays, "frame", "frame", t * 1.5)
    for i in range(bays + 1):
        zz = z0 + base_h + i * (h - base_h - 0.06) / bays
        for sx in (-1, 1):
            B.box((sx * (w * 0.42 - t * 0.75), 0, zz + t / 2), (t, d * 0.64, t), "frame", "frame", 0.0)
    B.cable_run((w * 0.18, -d * 0.1, z1 - 0.1), (w * 0.18, -d * 0.1, z0 + base_h + 0.02), 0.0, 0.009, 3)
    B.light_strip((0, -d * 0.36, z1 - 0.03), (w * 0.3, 0.01, 0.02), "emit2")
    B.box((0, -d / 2 + 0.004, z0 + base_h * 0.5), (w * 0.5, 0.008, base_h * 0.3), "light", "greeble")


def relay_dish(B, w, h, d, rng, spec):
    """Reflector dish tilted up and toward the sky; front rectangle 0.7 x 0.24."""
    z0, z1 = -h / 2, h / 2
    R = w * 0.48
    # mount yoke
    B.box((0, 0, z0 + 0.025), (w * 0.3, d * 0.5, 0.05), "dark", "frame", 0.008)
    B.cyl((0, 0, z0 + 0.07), 0.035, 0.05, "Z", 10, "frame", "frame", 0.004)
    # dish: shallow paraboloid, axis tipped back 70 degrees (faces up and toward camera)
    prof = []
    for i in range(7):
        r = R * i / 6
        prof.append((r, r * r / (4 * R * 0.9) * 0.95))
    prof_back = [(R, prof[-1][1] - 0.012)] + [(R * 0.5, prof[3][1] - 0.02), (0.06, -0.03), (0.0, -0.03)]
    dish = B.lathe(prof + prof_back, (0, 0, 0), 28, "panel", "cover")
    feed = B.cyl((0, 0, R * 0.52), 0.022, 0.05, "Z", 8, "trim", "greeble", 0.0)
    struts = [B.strut((R * 0.8 * math.cos(a), R * 0.8 * math.sin(a), prof[5][1]), (0, 0, R * 0.5), 0.01, "frame",
                      "greeble", round_=True, verts=6) for a in (0.3, 0.3 + 2.094, 0.3 + 4.189)]
    rim = B.ring((0, 0, prof[-1][1]), R * 1.0, R * 0.95, 0.014, "Z", 28, "trim", "frame", 0.0)
    led = B.light_strip((0, 0, R * 0.55), (0.012, 0.012, 0.01), "emit")
    tilt = spec.get("tilt", 72)
    for ob in [dish, feed, rim, led] + struts:
        K.scale(ob, (1.0, 1.0, 1.0))
        K.rotate(ob, tilt, "X")
        K.translate(ob, (0, 0.06, z0 + 0.1 + R * math.sin(math.radians(90 - tilt)) * 0.0))
    # fit the tipped dish into the rectangle height
    mn, mx = K.bounds([dish, feed, rim, led] + struts)
    sz = (h - 0.1) / max(1e-3, (mx.z - mn.z))
    if sz < 1.0:
        for ob in [dish, feed, rim, led] + struts:
            K.scale(ob, (1.0, 1.0, sz), (0, 0, z0 + 0.1))
    mn, mx = K.bounds([dish, feed, rim, led] + struts)
    for ob in [dish, feed, rim, led] + struts:
        K.translate(ob, (0, -(mn.y + mx.y) / 2, (z0 + 0.1) - mn.z))
    B.strut((0, 0, z0 + 0.09), (0, (mn.y + mx.y) * -0.0, z0 + 0.12), 0.05, "frame", "frame")


def ai_core(B, w, h, d, rng, spec):
    """Helix AURA core: pale caged housing around a faceted red-lit crystal (critical-asset read)."""
    z0, z1 = -h / 2, h / 2
    R = min(w, h) * 0.5
    base_h = h * 0.2
    # octagonal plinth
    oct_ = [(R * math.cos(a), R * 0.95 * math.sin(a) * d / w) for a in [math.pi / 8 + i * math.pi / 4 for i in range(8)]]
    B.zprism(oct_, z0, z0 + base_h * 0.55, "light", "frame", 0.01)
    B.zprism([(x * 0.86, y * 0.86) for x, y in oct_], z0 + base_h * 0.55, z0 + base_h, "frame", "frame", 0.006)
    for i in range(8):
        a = math.pi / 8 + i * math.pi / 4 + math.pi / 8
        x, y = R * 0.93 * math.cos(a), R * 0.88 * math.sin(a) * d / w
        if y < 0.0:
            B.box((x, y, z0 + base_h * 0.3), (0.05, 0.01, 0.025), "internal", "greeble")
    B.light_strip((0, -R * 0.82 * d / w, z0 + base_h * 0.78), (R * 0.9, 0.006, 0.012), "emit")
    # cage ribs (pale housing) arching over the crystal
    cz = z0 + base_h + (h - base_h) * 0.47
    cr = min(R * 0.92, (h - base_h) * 0.5)
    ribs = 8
    for i in range(ribs):
        a = i * math.pi / ribs
        pts = []
        for k in range(9):
            t = -math.pi / 2 + math.pi * k / 8
            rr = cr * (1.0 if abs(t) < 1.2 else 0.95)
            pts.append(Vector((rr * math.cos(t) * math.cos(a), rr * math.cos(t) * math.sin(a) * 0.95, cz + rr * math.sin(t))))
        # each rib = chain of short chamfered segments
        for k in range(8):
            B.strut(pts[k], pts[k + 1], 0.035, "light", "cover")
    B.ring((0, 0, cz), cr * 1.04, cr * 0.9, 0.05, "Z", 24, "frame", "frame", 0.0)
    B.zprism([(x * 0.5, y * 0.5) for x, y in oct_], z1 - 0.045, z1, "light", "frame", 0.006)
    # crystal: elongated octahedron with facets + inner glow
    cry = B.sphere((0, 0, cz), cr * 0.55, 1, "emit_red", "core", (0.85, 0.85, 1.25))
    for v in cry.data.vertices:
        v.co.z = cz + (v.co.z - cz) * 1.0
    B.sphere((0, 0, cz), cr * 0.7, 1, "glass", "pane_core", (0.85, 0.85, 1.2))
    B.cyl((0, 0, z0 + base_h + 0.02), cr * 0.35, 0.04, "Z", 12, "trim", "frame", 0.0)


def control_pod_glass(B, w, h, d, rng, spec):
    z0, z1 = -h / 2, h / 2
    fy = -d / 2
    B.box((0, 0, z0 + 0.04), (w, d, 0.08), "dark", "frame", 0.012)
    B.zprism(K.chamfer_rect(w, d, 0.06), z1 - 0.06, z1, "frame", "frame", 0.008)
    post = 0.035
    for sx in (-1, 1):
        for sy in (-1, 1):
            B.box((sx * (w / 2 - post / 2), sy * (d / 2 - post / 2), 0), (post, post, h - 0.14), "frame", "frame", 0.0)
    B.pane((0, fy + 0.012, 0.01), w - 2 * post, h - 0.16, 0.012)
    B.pane((-w / 2 + 0.012, 0, 0.01), d - 2 * post, h - 0.16, 0.012, "glass", "X")
    B.box((w / 2 - 0.012, 0, 0.0), (0.016, d - 2 * post, h - 0.16), "panel", "cover", 0.0)
    # console inside
    B.box((0, 0.05, z0 + 0.2), (w * 0.7, d * 0.4, 0.24), "panel", "internal", 0.008)
    B.xprism([(-d * 0.15, z0 + 0.32), (d * 0.25, z0 + 0.36), (d * 0.25, z0 + 0.32), (-d * 0.15, z0 + 0.3)],
             -w * 0.33, w * 0.33, "dark", "internal", 0.0)
    for k in range(3):
        B.light_strip((-w * 0.2 + k * w * 0.2, -d * 0.1, z0 + 0.336), (w * 0.12, 0.05, 0.004), "emit")
    B.box((0, d * 0.25, 0.1), (w * 0.6, 0.02, h * 0.35), "dark", "internal", 0.0)
    for k in range(4):
        B.light_strip((-w * 0.2, d * 0.238, 0.02 + k * h * 0.07), (w * 0.12 + 0.03 * (k % 2), 0.003, 0.008), "emit")
    B.light_strip((w * 0.12, d * 0.238, 0.12), (w * 0.2, 0.003, h * 0.18), "glass_smoked")
    B.light_strip((w * 0.3, fy + 0.002, z1 - 0.03), (0.02, 0.004, 0.012), "emit2")


def logistics_gantry(B, w, h, d, rng, spec):
    z0, z1 = -h / 2, h / 2
    leg = 0.07
    for sx in (-1, 1):
        x = sx * (w / 2 - leg / 2)
        B.box((x, 0, z0 + 0.03), (leg * 1.6, d, 0.06), "dark", "frame", 0.008)
        for y in (-d * 0.35, d * 0.35):
            B.zprism(K.chamfer_rect(leg, leg, 0.015, x, y), z0 + 0.06, z1 - 0.12, "frame", "frame", 0.0)
        B.strut((x, -d * 0.35, z0 + 0.12), (x, d * 0.35, z1 - 0.2), 0.03, "frame", "frame")
    for y in (-d * 0.35, d * 0.35):
        B.truss(-w / 2, w / 2, z1 - 0.14, z1, y, 0.022, max(3, int(w / 0.3)), "frame", "frame", "/", 0.03)
    B.box((0, 0, z1 - 0.01), (w, d * 0.8, 0.02), "panel", "cover", 0.004)
    # hoist trolley
    hx = rng.uniform(-w * 0.2, w * 0.2)
    B.box((hx, 0, z1 - 0.2), (0.16, d * 0.5, 0.1), "panel", "cover", 0.01)
    B.light_strip((hx, -d * 0.25 - 0.002, z1 - 0.2), (0.1, 0.004, 0.01), "emit2")
    B.strut((hx, 0, z1 - 0.25), (hx, 0, z0 + h * 0.4), 0.008, "cable", "cable", round_=True, verts=6)
    B.box((hx, 0, z0 + h * 0.38), (0.06, 0.04, 0.04), "trim", "greeble")


def cooling_stack(B, w, h, d, rng, spec):
    z0, z1 = -h / 2, h / 2
    B.box((0, 0, z0 + 0.03), (w, d, 0.06), "dark", "frame", 0.01)
    n = max(2, int((h - 0.1) / 0.36))
    mh = (h - 0.1) / n
    for i in range(n):
        zc = z0 + 0.06 + (i + 0.5) * mh
        B.zprism(K.chamfer_rect(w, d, 0.04), zc - mh / 2 + 0.006, zc + mh / 2 - 0.006, "panel", "cover", 0.006)
        # fan grille on the front
        B.ring((0, -d / 2 - 0.004, zc), min(w, mh) * 0.4, min(w, mh) * 0.34, 0.012, "Y", 20, "trim", "greeble", 0.0)
        B.cyl((0, -d / 2 + 0.003, zc), min(w, mh) * 0.34, 0.01, "Y", 20, "internal", "greeble", 0.0)
        for k in range(3):
            a = k * 2.094 + i
            B.strut((0, -d / 2 - 0.004, zc), (math.cos(a) * min(w, mh) * 0.33, -d / 2 - 0.004,
                                               zc + math.sin(a) * min(w, mh) * 0.33), 0.012, "dark", "greeble")
        # fins on the sides
        for f in range(3):
            for sx in (-1, 1):
                B.box((sx * (w / 2 - 0.004), d * (-0.25 + f * 0.25), zc), (0.012, 0.012, mh * 0.7), "trim", "greeble")
        B.light_strip((w * 0.36, -d / 2 - 0.002, zc + mh * 0.38), (0.02, 0.004, 0.008), "emit")
    B.box((0, 0, z1 - 0.02), (w * 0.9, d * 0.9, 0.04), "frame", "frame", 0.008)


def data_crate(B, w, h, d, rng, spec):
    z0, z1 = -h / 2, h / 2
    B.zprism(K.chamfer_rect(w * 0.94, d * 0.94, 0.04), z0 + 0.02, z1 - 0.02, "panel", "frame", 0.008)
    for zz in (z0 + 0.03, z1 - 0.03):
        B.zprism(K.chamfer_rect(w, d, 0.05), zz - 0.03, zz + 0.03, "frame", "frame", 0.006)
    for sx in (-1, 1):
        B.box((sx * w * 0.3, -d * 0.47 - 0.006, 0), (w * 0.08, 0.012, h - 0.14), "frame", "cover", 0.0)
        B.box((sx * w * 0.3, -d * 0.47 - 0.014, z1 - 0.11), (0.04, 0.008, 0.05), "trim", "greeble")
        B.box((-w * 0.47 - 0.006, sx * d * 0.25, 0), (0.012, d * 0.08, h - 0.14), "frame", "cover", 0.0)
    B.box((0, -d * 0.47 - 0.004, 0.0), (w * 0.34, 0.008, h * 0.3), "dark", "cover", 0.0)
    B.light_strip((0, -d * 0.47 - 0.009, h * 0.08), (w * 0.24, 0.003, 0.012), "emit")
    B.box((0, -d * 0.47 - 0.009, -h * 0.06), (w * 0.24, 0.003, 0.006), "light", "greeble")


def S(kind, var, mat, w_px, h_px, depth, fn, **kw):
    sid = f"HLX-CMP-{kind.upper()}-{var}"
    d = dict(id=sid, kind=kind, chapter=CH, material=mat, w=w_px / 100.0, h=h_px / 100.0, d=depth, build=fn,
             emit="cyan", emit2="orange", ref_px=[w_px, h_px])
    d.update(kw)
    return d


SPECS = [
    S("server_rack", "A", "electronic_module", 40, 40, 0.8, server_rack, scale=[0.8, 1.4]),  # helix_01 short rack (v1.5)
    S("server_rack", "B", "electronic_module", 40, 100, 0.8, server_rack, scale=[0.75, 1.5]),
    S("server_rack", "C", "electronic_module", 50, 160, 0.8, server_rack, scale=[0.8, 1.3], blade_pitch=0.17),
    S("support_column", "A", "lightweight_alloy", 26, 100, 0.5, support_column, scale=[0.7, 1.3]),
    S("support_column", "B", "lightweight_alloy", 26, 160, 0.5, support_column, scale=[0.7, 1.3]),
    S("support_column", "C", "lightweight_alloy", 30, 240, 0.5, support_column, scale=[0.7, 1.3], lit=False),
    S("service_deck", "A", "composite", 120, 24, 1.4, service_deck, scale=[0.75, 1.3]),
    S("service_deck", "B", "composite", 200, 24, 1.4, service_deck, scale=[0.75, 1.3]),
    S("service_deck", "C", "composite", 320, 24, 1.4, service_deck, scale=[0.75, 1.3]),
    S("core_shield", "A", "reinforced_steel", 16, 80, 0.9, core_shield, scale=[0.8, 1.6]),
    S("power_cell", "A", "energy_component", 36, 40, 0.5, power_cell, scale=[0.8, 1.3], emit="orange",
      emit2="orange"),
    S("blast_wall", "A", "reinforced_steel", 30, 90, 1.2, blast_wall, scale=[0.8, 1.3]),
    S("blast_wall", "B", "reinforced_steel", 30, 140, 1.2, blast_wall, scale=[0.8, 1.3]),
    S("blast_wall", "C", "reinforced_steel", 40, 200, 1.2, blast_wall, scale=[0.8, 1.3]),
    S("relay_mast", "A", "lightweight_alloy", 22, 140, 0.3, relay_mast, scale=[0.8, 1.3]),
    S("relay_mast", "B", "lightweight_alloy", 22, 220, 0.3, relay_mast, scale=[0.8, 1.3]),
    S("relay_dish", "A", "glass_polymer", 70, 24, 0.8, relay_dish, scale=[0.8, 1.25], cover_loss=0.0),
    S("ai_core", "A", "ai_core_module", 60, 60, 0.7, ai_core, scale=[0.85, 1.25], emit="cyan", emit2="red",
      critical=True),
    S("control_pod_glass", "A", "glass_polymer", 60, 80, 0.8, control_pod_glass, scale=[0.8, 1.3]),
    S("logistics_gantry", "A", "lightweight_alloy", 120, 100, 0.8, logistics_gantry, scale=[0.75, 1.3]),
    S("cooling_stack", "A", "composite", 40, 120, 0.8, cooling_stack, scale=[0.8, 1.3]),
    S("data_crate", "A", "composite", 50, 50, 0.8, data_crate, scale=[0.8, 1.3]),
]
