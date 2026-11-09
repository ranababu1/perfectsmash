"""Helix Systems (2089) component kit.
Form language: cold steel and graphite, 45-degree chamfered corners, vertical rib slots, layered
cladding with real panel gaps, cyan compute light in thin lines, orange only as warning pips."""
import math
from mathutils import Vector
import tfjkit as K
import tfjdetail as Dt

CH = "helix"


def server_rack(B, w, h, d, rng, spec):
    """SV-04 / SV-06 rack: heavy chamfered corner posts with amber caps, a stack of rack units
    (chapter electronic_module texture, status lights in the emission mask) behind a bezel,
    seamed and vented side cladding, top hatch and vent, plinth with kick louvre."""
    z0, z1 = -h / 2, h / 2
    fy = -d / 2
    post = max(0.036, min(w, d) * 0.11)
    base_h, cap_h = 0.07, 0.06
    # plinth and top cap
    B.zprism(K.chamfer_rect(w * 0.96, d * 0.96, 0.025), z0, z0 + base_h, "dark", "frame", 0.006)
    Dt.louvre(B, 0, z0 + base_h * 0.5, w * 0.5, base_h * 0.5, fy + 0.02 + 0.006, 3)
    B.zprism(K.chamfer_rect(w, d, 0.035), z1 - cap_h, z1, "frame", "frame", 0.008)
    B.zprism(K.chamfer_rect(w * 0.9, d * 0.9, 0.03), z1 - cap_h - 0.018, z1 - cap_h, "dark", "frame", 0.0)
    Dt.top_hatch(B, 0, d * 0.18, z1, w * 0.55, d * 0.3, "panel")
    Dt.louvre(B, 0, -d * 0.2, w * 0.55, d * 0.22, z1, 5, normal="Z")
    Dt.corner_posts(B, w, d, z0 + base_h, z1 - cap_h, post, "frame", accent=True)
    # body shell behind the posts
    B.box((0, 0.01, 0), (w - post * 1.2, d - post * 1.2, h - base_h - cap_h), "frame", "frame", 0.0)
    # front: rack units in a bezel
    fw = w - 2 * post - 0.01
    bot, top = z0 + base_h + 0.03, z1 - cap_h - 0.035
    B.box((0, fy + 0.006, top + 0.012), (fw + 0.008, 0.016, 0.022), "trim", "frame", 0.0)
    B.box((0, fy + 0.006, bot - 0.012), (fw + 0.008, 0.016, 0.022), "trim", "frame", 0.0)
    cols = 2 if fw > 0.5 else 1
    unit_h = min(0.16, max(0.085, fw / cols / 3.0))
    rows = max(2, int(round((top - bot) / unit_h)))
    uh = (top - bot) / rows
    cw = fw / cols
    for c in range(cols):
        x0 = -fw / 2 + c * cw
        for r in range(rows):
            za = bot + r * uh
            Dt.module_face(B, x0 + 0.004, x0 + cw - 0.004, za + 0.004, za + uh - 0.004, fy + 0.012, 0.02,
                           unit=rng.randrange(3))
            # bright status block on most units (the concept's dense blue read)
            if rng.random() < 0.9:
                B.light_strip((x0 + cw * 0.8, fy + 0.0095, za + uh * 0.5), (cw * 0.13, 0.003, uh * 0.2),
                              "emit2" if rng.random() < 0.07 else "emit")
                if r % (2 if rows <= 9 else 3) == 0 or rows <= 6:
                    Dt.status_leds(B, x0 + cw * 0.36, za + uh * 0.28, fy + 0.012, 3, cw * 0.07, (cw * 0.04, uh * 0.09))
    # door frame verticals and a handle
    for sx in (-1, 1):
        B.box((sx * (fw / 2 + 0.004), fy + 0.008, (bot + top) / 2), (0.01, 0.018, top - bot), "trim", "frame", 0.0)
    B.box((fw / 2 - 0.012, fy - 0.006, (bot + top) / 2), (0.012, 0.014, min(0.22, (top - bot) * 0.3)), "trim",
          "greeble", 0.0)
    # sides: seamed cladding, one vent, bolts, a cable loom feeding the top
    rows_s = max(1, int(round((h - 0.2) / 0.5)))
    for sx in (-1, 1):  # the camera sees the -X side; the +X side gets one plate per column
        Dt.side_seams(B, -d / 2 + post, d / 2 - post, z0 + base_h + 0.01, z1 - cap_h - 0.01, sx * (w / 2 - 0.016), sx,
                      2, rows_s if sx < 0 else 1)
        Dt.bolts(B, [(-d / 2 + post + 0.03, z1 - cap_h - 0.04), (d / 2 - post - 0.03, z1 - cap_h - 0.04)],
                 sx * (w / 2 + 0.0), normal="+X" if sx > 0 else "-X")
    B.box((-w / 2 - 0.0, d * 0.1, z0 + base_h + (h - base_h - cap_h) * 0.3), (0.008, d * 0.3, min(0.16, h * 0.15)),
          "internal", "greeble", 0.0)
    for k in range(2 if h > 1.2 else 4):
        B.box((-w / 2 - 0.004, d * 0.1, z0 + base_h + (h - base_h - cap_h) * 0.3 - min(0.06, h * 0.05) + k * min(0.04, h * 0.035)),
              (0.006, d * 0.28, 0.008), "dark", "greeble", 0.0)
    if h > 0.7:
        Dt.loom(B, (w / 2 - 0.006, d * 0.3, z1 - cap_h - 0.02), (w / 2 - 0.006, -d * 0.1, z0 + base_h + 0.1), 2,
                0.008, 0.0, 0.02, (0, 1, 0), seg=2)


def support_column(B, w, h, d, rng, spec):
    """Load-bearing column: chamfered shaft, plinth and capital with amber corner blocks, seamed
    and bolted cladding, a recessed compute line, a cable loom up one side and a base louvre."""
    z0, z1 = -h / 2, h / 2
    sw, sd = w * 0.8, d * 0.64
    base_h, cap_h = min(0.11, h * 0.08), min(0.09, h * 0.06)
    B.zprism(K.chamfer_rect(w, d * 0.92, w * 0.2), z0, z0 + base_h, "dark", "frame", 0.0)
    B.zprism(K.chamfer_rect(w * 0.9, d * 0.8, w * 0.16), z0 + base_h, z0 + base_h + 0.03, "frame", "frame", 0.0)
    B.zprism(K.chamfer_rect(w, d * 0.92, w * 0.2), z1 - cap_h, z1, "dark", "frame", 0.0)
    B.zprism(K.chamfer_rect(w * 0.9, d * 0.8, w * 0.16), z1 - cap_h - 0.03, z1 - cap_h, "frame", "frame", 0.0)
    for sx in (-1, 1):
        for zz in (z0 + base_h * 0.5, z1 - cap_h * 0.5):
            B.box((sx * (w / 2 - 0.02), -d * 0.46 + 0.012, zz), (0.036, 0.03, 0.036), "accent", "frame", 0.004)
    s0, s1 = z0 + base_h + 0.03, z1 - cap_h - 0.03
    B.zprism(K.chamfer_rect(sw, sd, sw * 0.24), s0, s1, "frame", "frame", 0.0)
    n = max(2, int(round((s1 - s0) / 0.4)))
    Dt.seam_grid(B, -sw * 0.42, sw * 0.42, s0 + 0.02, s1 - 0.02, -sd / 2, 1, n, gap=0.014, thick=0.018, slot="panel")
    for sx in (-1, 1):
        Dt.side_seams(B, -sd * 0.38, sd * 0.38, s0 + 0.02, s1 - 0.02, sx * sw / 2, sx, 1, n, thick=0.016)
    B.box((0, -sd / 2 - 0.02, (s0 + s1) / 2), (0.018, 0.006, (s1 - s0) * 0.84), "internal", "greeble", 0.0)
    if spec.get("lit", True):
        B.light_strip((0, -sd / 2 - 0.0235, (s0 + s1) / 2 + (s1 - s0) * 0.18), (0.006, 0.003, (s1 - s0) * 0.34),
                      "emit")
    Dt.louvre(B, 0, s0 + 0.09, sw * 0.5, 0.06, -sd / 2 - 0.018, 3)
    Dt.loom(B, (sw / 2 + 0.012, -sd * 0.15, s1 - 0.02), (sw / 2 + 0.012, -sd * 0.15, s0 + 0.02), 2, 0.008, 0.0,
            0.02, (0, 1, 0), seg=3)
    Dt.status_leds(B, -sw * 0.2, s1 - 0.06, -sd / 2 - 0.018, 3, 0.022, (0.01, 0.006), "emit", "emit2", rng)


def service_deck(B, w, h, d, rng, spec):
    """Raised service deck: tread-plate top in seamed panels (the camera sees it), chamfered front
    fascia with louvres and bolts, a compute line, amber end blocks and under-deck ribs."""
    z0, z1 = -h / 2, h / 2
    fy = -d / 2
    top_t = h * 0.34
    B.box((0, 0, z1 - top_t / 2), (w, d, top_t), "frame", "frame", 0.0)
    n = max(3, int(w / 0.4))
    for i in range(n):
        x = -w / 2 + (i + 0.5) * w / n
        B.box((x, 0.0, z1 + 0.004), (w / n - 0.016, d * 0.86, 0.008), "tread", "cover", 0.0)
    B.box((0, fy + 0.04, z1 + 0.006), (w * 0.98, 0.03, 0.012), "trim", "frame", 0.0)
    B.xprism([(fy, z1 - top_t), (fy, z0 + 0.03), (fy + 0.03, z0), (fy + 0.09, z0), (fy + 0.09, z1 - top_t)],
             -w / 2 + 0.05, w / 2 - 0.05, "panel", "frame", 0.0)
    m = max(2, int(w / 0.5))
    for i in range(m):
        x = -w / 2 + (i + 0.5) * w / m
        if i % 2 == 0:
            Dt.louvre(B, x, (z0 + z1 - top_t) / 2 + 0.005, w / m * 0.5, (h - top_t) * 0.45, fy - 0.001, 3)
        else:
            B.box((x, fy - 0.005, (z0 + z1 - top_t) / 2 + 0.005), (w / m - 0.04, 0.01, (h - top_t) * 0.6), "panel",
                  "cover", 0.0)
        Dt.bolts(B, [(x - w / m * 0.42, (z0 + z1 - top_t) / 2), (x + w / m * 0.42, (z0 + z1 - top_t) / 2)], fy - 0.002)
    B.light_strip((0, fy - 0.002, z1 - top_t * 0.5), (w * 0.9, 0.004, 0.008), "emit")
    k = max(2, int(w / 0.4))
    for i in range(k + 1):
        x = -w / 2 + 0.05 + i * (w - 0.1) / k
        B.box((x, 0.05, z0 + (h - top_t) / 2), (0.03, d * 0.8, h - top_t), "dark", "frame", 0.0)
    B.box((0, d / 2 - 0.05, (z0 + z1 - top_t) / 2), (w, 0.08, h - top_t), "frame", "frame", 0.0)
    for sx in (-1, 1):
        B.box((sx * (w / 2 - 0.025), 0, (z0 + z1) / 2), (0.05, d, h), "frame", "frame", 0.008)
        B.box((sx * (w / 2 - 0.025), fy - 0.004, (z0 + z1) / 2), (0.054, 0.012, h * 0.7), "accent", "frame", 0.0)


def core_shield(B, w, h, d, rng, spec):
    """Narrow armour shield: stacked chamfered plates front and sides with bolts, a recessed spine,
    an amber cap band, a short hazard band and a warning pip."""
    z0, z1 = -h / 2, h / 2
    B.box((0, 0, 0), (w * 0.7, d, h), "frame", "frame", 0.0)
    n = max(2, int(h / 0.26))
    for i in range(n):
        zc = z0 + (i + 0.5) * h / n
        for sx in (-1, 1):
            B.box((sx * (w * 0.35 + 0.012), 0, zc), (0.024, d * 0.92, h / n - 0.02), "panel", "cover", 0.006)
            Dt.bolts(B, [(-d * 0.4, zc + h / n * 0.35), (d * 0.4, zc - h / n * 0.35)], sx * (w * 0.35 + 0.024),
                     normal="+X" if sx > 0 else "-X")
        B.box((0, -d / 2 - 0.01, zc), (w * 0.9, 0.02, h / n - 0.02), "panel", "cover", 0.005)
    B.box((0, -d / 2 - 0.022, 0), (w * 0.26, 0.006, h * 0.82), "dark", "greeble", 0.0)
    B.box((0, 0, z1 - 0.025), (w, d, 0.05), "frame", "frame", 0.008)
    B.box((0, 0, z0 + 0.025), (w, d, 0.05), "dark", "frame", 0.008)
    B.box((0, -d / 2 - 0.004, z1 - 0.025), (w * 1.0, 0.012, 0.04), "accent", "frame", 0.0)
    B.hazard_band((0, -d / 2 - 0.02, z0 + 0.1), (w * 0.8, 0.006, 0.05), 2)
    B.light_strip((0, -d / 2 - 0.026, z1 - 0.09), (w * 0.3, 0.003, 0.03), "emit2")


def power_cell(B, w, h, d, rng, spec):
    """Energy cell in a caged frame: corner posts with amber caps, a glowing core cylinder banded
    with rings, terminal cap and hatch, a cable loom and a warning strip."""
    z0, z1 = -h / 2, h / 2
    r = min(w, d) * 0.34
    B.zprism(K.chamfer_rect(w, d, 0.03), z0, z0 + 0.05, "dark", "frame", 0.006)
    B.zprism(K.chamfer_rect(w, d * 0.92, 0.03), z1 - 0.04, z1, "frame", "frame", 0.006)
    Dt.corner_posts(B, w, d * 0.92, z0 + 0.05, z1 - 0.04, 0.032, "frame", accent=True)
    ch = h - 0.13
    B.lathe([(0.0, -ch / 2), (r * 0.8, -ch / 2), (r, -ch / 2 + 0.02), (r, ch / 2 - 0.02), (r * 0.8, ch / 2),
             (0.0, ch / 2)], (0, 0, 0.005), 16, "key", "cover")
    for zz in (-ch * 0.24, 0.0, ch * 0.24):
        B.ring((0, 0, zz), r * 1.04, r * 0.9, 0.014, "Z", 16, "emit", "emit", 0.0)
    for zz in (-ch * 0.12, ch * 0.12):
        B.ring((0, 0, zz), r * 1.07, r * 0.92, 0.03, "Z", 16, "trim", "frame", 0.0)
    B.cyl((0, 0, z1 - 0.045), r * 0.4, 0.03, "Z", 10, "trim", "greeble", 0.0)
    Dt.top_hatch(B, 0, 0, z1, w * 0.5, d * 0.4, "panel")
    Dt.loom(B, (-w / 2 + 0.03, -d * 0.2, z1 - 0.06), (-r * 0.9, -d * 0.1, -ch * 0.3), 2, 0.008, 0.04, 0.018,
            (0, 1, 0), seg=6)
    B.box((0, -d * 0.46 + 0.003, z0 + 0.025), (w * 0.4, 0.006, 0.02), "emit2", "emit", 0.0)
    B.hazard_band((0, -d * 0.46, z1 - 0.02), (w * 0.5, 0.006, 0.022), 3)


def blast_wall(B, w, h, d, rng, spec):
    """Armoured perimeter wall (SV-04): stacked armour plates with seams and bolts on the front,
    chamfered edge posts with amber caps, a top walkway with a hatch and louvre (the camera
    sees the top), a muted hazard band near the top and a thin compute line."""
    z0, z1 = -h / 2, h / 2
    fy = -d / 2
    post = min(0.07, w * 0.22)
    B.box((0, 0, 0), (w * 0.7, d * 0.92, h - 0.1), "frame", "frame", 0.012)
    B.zprism(K.chamfer_rect(w, d, 0.03), z0, z0 + 0.06, "dark", "frame", 0.006)
    B.zprism(K.chamfer_rect(w, d, 0.03), z1 - 0.05, z1, "frame", "frame", 0.008)
    # top walkway: seamed plates, a hatch, a louvre
    n_top = max(2, int(d / 0.4))
    for i in range(n_top):
        y = -d / 2 + (i + 0.5) * d / n_top
        B.box((0, y, z1 + 0.004), (w * 0.82, d / n_top - 0.014, 0.008), "panel", "cover", 0.002)
    Dt.louvre(B, 0, d * 0.25, w * 0.5, d * 0.16, z1 + 0.008, 4, normal="Z")
    # edge posts at the four corners, front ones capped amber
    Dt.corner_posts(B, w, d, z0 + 0.06, z1 - 0.05, post, "frame", accent=True)
    # front armour: plates in a stack with seams, bolts and a centre rib
    n = max(3, int(round(h / 0.36)))
    pw = w - 2 * post - 0.006
    Dt.seam_grid(B, -pw / 2, pw / 2, z0 + 0.07, z1 - 0.06, fy, 1, n, gap=0.012, thick=0.022, slot="panel")
    B.box((0, fy - 0.026, (z0 + z1) / 2), (0.016, 0.008, h * 0.78), "dark", "greeble", 0.0)
    B.light_strip((0, fy - 0.031, (z0 + z1) / 2 + h * 0.12), (0.005, 0.003, h * 0.3), "emit")
    # hazard band (restrained: one band, short, near the top)
    hz = z1 - 0.05 - 0.05
    B.hazard_band((0, fy - 0.022, hz), (pw * 0.86, 0.006, 0.034), 4)
    # sides (long, seen at the camera's -X side): cladding seams and a vent
    rows_s = max(2, int(round(h / 0.45)))
    for sx in (-1, 1):
        Dt.side_seams(B, -d / 2 + post, d / 2 - post, z0 + 0.07, z1 - 0.06, sx * (w * 0.35), sx, 2,
                      rows_s if sx < 0 else 1, thick=0.02)
    if h < 1.8:
        Dt.louvre(B, 0, z0 + 0.2, pw * 0.5, 0.08, fy - 0.022, 4)
    else:
        B.box((0, fy - 0.024, z0 + 0.2), (pw * 0.5, 0.006, 0.08), "dark", "greeble", 0.0)
    B.light_strip((pw * 0.3, fy - 0.026, z1 - 0.1), (0.02, 0.003, 0.012), "emit2")


def relay_mast(B, w, h, d, rng, spec):
    """Lattice relay mast: chamfered plinth with a louvred equipment box and amber blocks, twin
    trusses, a cable run, a muted warning band and an amber beacon at the head."""
    z0, z1 = -h / 2, h / 2
    t = max(0.012, w * 0.08)
    base_h = min(0.16, h * 0.08)
    B.zprism(K.chamfer_rect(w, d, w * 0.2), z0, z0 + base_h, "dark", "frame", 0.0)
    B.box((0, -d * 0.12, z0 + base_h * 0.55), (w * 0.8, d * 0.6, base_h * 0.7), "panel", "cover", 0.004)
    Dt.louvre(B, 0, z0 + base_h * 0.55, w * 0.5, base_h * 0.4, -d * 0.42 - 0.002, 3)
    for sx in (-1, 1):
        B.box((sx * (w / 2 - 0.014), -d / 2 + 0.014, z0 + base_h * 0.5), (0.026, 0.026, base_h * 0.9), "accent",
              "frame", 0.0)
    B.zprism(K.chamfer_rect(w * 0.7, d * 0.7, w * 0.12), z1 - 0.06, z1, "frame", "frame", 0.0)
    bays = max(3, int((h - base_h) / 0.28))
    for y in (-d * 0.32, d * 0.32):
        B.vtruss(z0 + base_h, z1 - 0.06, -w * 0.42, w * 0.42, y, t, bays, "frame", "frame", t * 1.5)
    for i in range(bays + 1):
        zz = z0 + base_h + i * (h - base_h - 0.06) / bays
        for sx in (-1, 1):
            B.box((sx * (w * 0.42 - t * 0.75), 0, zz + t / 2), (t, d * 0.64, t), "frame", "frame", 0.0)
    B.cable_run((w * 0.18, -d * 0.1, z1 - 0.1), (w * 0.18, -d * 0.1, z0 + base_h + 0.02), 0.0, 0.009, 3)
    B.hazard_band((0, -d * 0.36, z1 - 0.1), (w * 0.84, 0.006, 0.04), 3)
    B.light_strip((0, -d * 0.36, z1 - 0.03), (w * 0.3, 0.01, 0.02), "emit2")


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
    """Glazed control pod: chamfered sill with a louvre and roof with a hatch, corner posts with
    amber caps, glass front and side, and an operator console with two lit screens."""
    z0, z1 = -h / 2, h / 2
    fy = -d / 2
    B.zprism(K.chamfer_rect(w, d, 0.04), z0, z0 + 0.08, "dark", "frame", 0.006)
    Dt.louvre(B, 0, z0 + 0.04, w * 0.5, 0.04, fy - 0.001, 3)
    B.zprism(K.chamfer_rect(w, d, 0.06), z1 - 0.06, z1, "frame", "frame", 0.006)
    Dt.top_hatch(B, 0, 0.04, z1, w * 0.5, d * 0.4, "panel")
    post = 0.036
    Dt.corner_posts(B, w, d, z0 + 0.08, z1 - 0.06, post, "frame", accent=True)
    B.pane((0, fy + 0.012, 0.01), w - 2 * post, h - 0.16, 0.012)
    B.pane((-w / 2 + 0.012, 0, 0.01), d - 2 * post, h - 0.16, 0.012, "glass", "X")
    B.box((w / 2 - 0.012, 0, 0.0), (0.016, d - 2 * post, h - 0.16), "panel", "cover", 0.0)
    B.box((0, 0.05, z0 + 0.2), (w * 0.7, d * 0.4, 0.24), "panel", "internal", 0.006)
    B.xprism([(-d * 0.15, z0 + 0.32), (d * 0.25, z0 + 0.36), (d * 0.25, z0 + 0.32), (-d * 0.15, z0 + 0.3)],
             -w * 0.33, w * 0.33, "dark", "internal", 0.0)
    for k in range(3):
        B.light_strip((-w * 0.2 + k * w * 0.2, -d * 0.1, z0 + 0.336), (w * 0.12, 0.05, 0.004), "emit")
    B.box((0, d * 0.25, 0.1), (w * 0.6, 0.02, h * 0.35), "dark", "internal", 0.0)
    Dt.screen(B, -w * 0.14, 0.1, w * 0.22, h * 0.2, d * 0.24, "emit", "dark", 3, rng)
    Dt.screen(B, w * 0.16, 0.1, w * 0.22, h * 0.2, d * 0.24, "emit", "dark", 2, rng)
    B.light_strip((w * 0.3, fy + 0.002, z1 - 0.03), (0.02, 0.004, 0.012), "emit2")


def logistics_gantry(B, w, h, d, rng, spec):
    """Gantry frame: chamfered legs on bolted feet with amber blocks, truss beams with a muted
    hazard band, a hoist trolley with a louvre, a cable and an amber hook block."""
    z0, z1 = -h / 2, h / 2
    leg = 0.07
    for sx in (-1, 1):
        x = sx * (w / 2 - leg / 2)
        B.box((x, 0, z0 + 0.03), (leg * 1.6, d, 0.06), "dark", "frame", 0.008)
        Dt.bolts(B, [(x - leg * 0.5, z0 + 0.03), (x + leg * 0.5, z0 + 0.03)], -d / 2)
        for y in (-d * 0.35, d * 0.35):
            B.zprism(K.chamfer_rect(leg, leg, 0.018, x, y), z0 + 0.06, z1 - 0.12, "frame", "frame", 0.0)
        B.box((x, -d * 0.35 - 0.004, z0 + 0.1), (leg * 1.1, leg * 1.1, 0.05), "accent", "frame", 0.0)
        B.strut((x, -d * 0.35, z0 + 0.12), (x, d * 0.35, z1 - 0.2), 0.03, "frame", "frame")
    for y in (-d * 0.35, d * 0.35):
        B.truss(-w / 2, w / 2, z1 - 0.14, z1, y, 0.022, max(3, int(w / 0.3)), "frame", "frame", "/", 0.03)
    B.hazard_band((0, -d * 0.35 - 0.016, z1 - 0.015), (w * 0.6, 0.006, 0.024), 6)
    B.box((0, 0, z1 - 0.01), (w, d * 0.8, 0.02), "tread", "cover", 0.0)
    hx = rng.uniform(-w * 0.2, w * 0.2)
    B.box((hx, 0, z1 - 0.2), (0.18, d * 0.5, 0.1), "panel", "cover", 0.01)
    Dt.louvre(B, hx, z1 - 0.2, 0.1, 0.05, -d * 0.25 - 0.001, 3)
    B.light_strip((hx + 0.07, -d * 0.25 - 0.002, z1 - 0.17), (0.02, 0.004, 0.01), "emit2")
    B.strut((hx, 0, z1 - 0.25), (hx, 0, z0 + h * 0.4), 0.008, "cable", "cable", round_=True, verts=6)
    B.box((hx, 0, z0 + h * 0.38), (0.07, 0.05, 0.05), "accent", "greeble", 0.004)


def cooling_stack(B, w, h, d, rng, spec):
    """Stacked cooling modules: chamfered housings with fan grilles and hubs, side fins, a coolant
    pipe pair, a top louvre, bolts and a status light per module."""
    z0, z1 = -h / 2, h / 2
    B.box((0, 0, z0 + 0.03), (w, d, 0.06), "dark", "frame", 0.01)
    n = max(2, int((h - 0.1) / 0.36))
    mh = (h - 0.1) / n
    for i in range(n):
        zc = z0 + 0.06 + (i + 0.5) * mh
        B.zprism(K.chamfer_rect(w, d, 0.04), zc - mh / 2 + 0.006, zc + mh / 2 - 0.006, "panel", "cover", 0.0)
        rr = min(w, mh) * 0.4
        B.ring((0, -d / 2 - 0.004, zc), rr, rr * 0.86, 0.014, "Y", 16, "trim", "greeble", 0.0)
        B.cyl((0, -d / 2 + 0.004, zc), rr * 0.86, 0.01, "Y", 16, "internal", "greeble", 0.0)
        for k in range(4):
            a = k * 1.5708 + i * 0.4
            B.strut((0, -d / 2 - 0.002, zc), (math.cos(a) * rr * 0.84, -d / 2 - 0.002, zc + math.sin(a) * rr * 0.84),
                    0.016, "dark", "greeble")
        B.cyl((0, -d / 2 - 0.006, zc), rr * 0.22, 0.012, "Y", 8, "frame", "greeble", 0.0)
        Dt.bolts(B, [(-w * 0.42, zc + mh * 0.38), (w * 0.42, zc + mh * 0.38), (-w * 0.42, zc - mh * 0.38),
                     (w * 0.42, zc - mh * 0.38)], -d / 2)
        for f in range(3):
            for sx in (-1, 1):
                B.box((sx * (w / 2 - 0.004), d * (-0.25 + f * 0.25), zc), (0.012, 0.012, mh * 0.7), "trim", "greeble")
        B.light_strip((w * 0.36, -d / 2 - 0.002, zc - mh * 0.38), (0.02, 0.004, 0.008), "emit")
    B.box((0, 0, z1 - 0.02), (w * 0.9, d * 0.9, 0.04), "frame", "frame", 0.008)
    Dt.louvre(B, 0, 0, w * 0.6, d * 0.5, z1, 5, normal="Z")
    for k in (-1, 1):
        B.cyl((-w / 2 + 0.016, k * d * 0.12, 0), 0.014, h - 0.14, "Z", 8, "trim", "greeble", 0.0)


def data_crate(B, w, h, d, rng, spec):
    """Armoured data crate: chamfered shell with banded top and bottom frames, amber corner
    blocks, ribbed sides, a recessed handle, a label plate, status lights and a top hatch."""
    z0, z1 = -h / 2, h / 2
    B.zprism(K.chamfer_rect(w * 0.94, d * 0.94, 0.04), z0 + 0.02, z1 - 0.02, "panel", "frame", 0.0)
    for zz in (z0 + 0.03, z1 - 0.03):
        B.zprism(K.chamfer_rect(w, d, 0.05), zz - 0.03, zz + 0.03, "frame", "frame", 0.0)
        for sx in (-1, 1):
            B.box((sx * (w / 2 - 0.03), -d / 2 + 0.03, zz), (0.05, 0.05, 0.064), "accent", "frame", 0.004)
    for sx in (-1, 1):
        B.box((sx * w * 0.3, -d * 0.47 - 0.006, 0), (w * 0.08, 0.012, h - 0.14), "frame", "cover", 0.0)
        B.box((sx * w * 0.3, -d * 0.47 - 0.014, z1 - 0.11), (0.04, 0.008, 0.05), "trim", "greeble")
        for k in (-1, 1):
            B.box((-w * 0.47 - 0.006, k * d * 0.25, 0), (0.012, d * 0.08, h - 0.14), "frame", "cover", 0.0)
    B.box((0, -d * 0.47 - 0.004, 0.0), (w * 0.34, 0.008, h * 0.3), "dark", "cover", 0.0)
    B.light_strip((0, -d * 0.47 - 0.009, h * 0.08), (w * 0.24, 0.003, 0.012), "emit")
    B.box((0, -d * 0.47 - 0.009, -h * 0.06), (w * 0.24, 0.003, 0.006), "light", "greeble")
    Dt.status_leds(B, -w * 0.08, -h * 0.12, -d * 0.47 - 0.006, 3, 0.03, (0.014, 0.008), "emit", "emit2", rng)
    Dt.top_hatch(B, 0, 0, z1, w * 0.5, d * 0.5, "panel")


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
