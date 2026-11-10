"""Chapter architecture (review pass 3): a distinct back wall pair and background massing silhouette per
chapter, so each chapter reads at a glance. Helix keeps the shared builders in env_common.
Blender axes: X right, -Y towards the camera, Z up. Back walls are 4 x 6 m with the front face at y -0.25;
everything stays bottom-centre so IDs, origins and placement rules are unchanged."""
import math
import tfjkit as K
import env_common as E


def _arc_pts(cx, cz, r, a0, a1, n):
    return [(cx + r * math.cos(math.radians(a0 + (a1 - a0) * i / n)), cz + r * math.sin(math.radians(a0 + (a1 - a0) * i / n)))
            for i in range(n + 1)]


def _rbar(B, c, length, thick, depth, angle, slot, role="frame"):
    """Thin bar in the XZ plane through c, rotated about Y (angle 0 = vertical)."""
    ob = B.box(c, (thick, depth, length), slot, role, 0.0)
    K.rotate(ob, angle, "Y", c)
    return ob


def _dome(B, c, r, slot, n=16, rings=5, cap=0.0):
    """Open hemisphere (lathe), optional flat crown of radius cap."""
    prof = [(r * math.cos(math.radians(90 * i / rings)), r * math.sin(math.radians(90 * i / rings))) for i in range(rings)]
    prof += [(cap, r)] if cap > 0 else []
    prof += [(0.0, r)]
    return B.lathe(prof, c, n, slot, "cover")


# ------------------------------------------------------------------------------------------------
# NOVA GRID: turbine halls, busbars, heavy transformers (warm amber heat, electric-blue arcs)
# ------------------------------------------------------------------------------------------------
def _nvg_shell(B, w, h, t):
    fy = -t / 2
    B.box((0, -0.03, 0.2), (w, t + 0.16, 0.4), "dark", "frame", 0.02)
    B.box((0, -0.02, h - 0.15), (w, t + 0.12, 0.3), "frame", "frame", 0.02)
    B.box((0, -0.05, h - 0.33), (w - 0.1, t + 0.12, 0.06), "trim", "frame", 0.0)
    for sx in (-1, 1):  # stepped buttresses: deep lower block, slimmer upper shaft, a capping slab between
        x = sx * (w / 2 - 0.25)
        B.box((x, -0.08, 1.3), (0.5, t + 0.26, 1.8), "frame", "frame", 0.02)
        B.box((x, -0.08, 2.23), (0.54, t + 0.3, 0.06), "trim", "frame", 0.0)
        B.box((x, -0.03, 3.93), (0.4, t + 0.12, 3.34), "frame", "frame", 0.015)
        B.bolts([(x - 0.14, 1.3), (x + 0.14, 1.3)], -t / 2 - 0.21, 0.024)
        B.box((x, -t / 2 - 0.095, 3.9), (0.08, 0.012, 2.6), "dark", "greeble", 0.0)
    B.hazard_band((0, -t / 2 - 0.105, 0.28), (w - 1.1, 0.012, 0.14), 8)
    return fy


def nvg_wall_busbar(B, w=4.0, h=6.0, t=0.5):
    """Busbar wall: board-marked concrete between stepped buttresses, three busbars on standoff
    insulators, a Jacob's ladder discharge gap with a blue arc, low heat vents glowing amber."""
    fy = _nvg_shell(B, w, h, t)
    iw = w - 1.0
    B.box((0, 0, 3.05), (iw, t, 5.3), "concrete", "frame", 0.0)
    for z in (1.6, 2.8, 4.6):  # formwork lift lines
        B.box((0, fy - 0.004, z), (iw, 0.01, 0.025), "internal", "greeble", 0.0)
    for x in (-1.0, 0.0, 1.0):
        B.cyl((x, fy - 0.004, 2.2), 0.022, 0.01, "Y", 6, "dark", "greeble", 0.0)
    # busbar run on two brackets, the top bar rising into the discharge gap
    B.box((0.93, fy - 0.29, 4.25), (0.06, 0.06, 0.2), "trim", "frame", 0.0)
    for x in (-1.1, 0.0):
        B.box((x, fy - 0.03, 3.85), (0.12, 0.06, 0.95), "dark", "frame", 0.0)
        for z in (3.55, 3.85, 4.15):
            B.lathe([(0.035, 0.0), (0.05, 0.05), (0.032, 0.1), (0.05, 0.15), (0.03, 0.2)],
                    (x, fy - 0.06, z), 6, "polymer", "greeble", "Y")
    for k, z in enumerate((3.55, 3.85, 4.15)):
        B.box((-0.25, fy - 0.29, z), (iw - 0.7, 0.06, 0.09), "trim", "frame", 0.004)
        for x in (-1.1, 0.0):  # clamp blocks, amber heat glow at the joints
            B.box((x, fy - 0.3, z), (0.1, 0.08, 0.12), "dark", "greeble", 0.0)
        B.light_strip((-0.55 + k * 0.4, fy - 0.322, z), (0.14, 0.004, 0.04), "emit_amber")
    # Jacob's ladder: two diverging horns with an electric-blue arc between them
    xc = 1.0
    for sx in (-1, 1):
        B.tube([(xc + sx * 0.06, fy - 0.3, 4.4), (xc + sx * 0.1, fy - 0.3, 4.75), (xc + sx * 0.22, fy - 0.3, 5.3)], 0.016, 6,
               "trim", "greeble")
    B.box((xc, fy - 0.3, 4.34), (0.26, 0.1, 0.1), "dark", "greeble", 0.0)
    pts = [(xc - 0.17, fy - 0.3, 5.05), (xc - 0.08, fy - 0.3, 5.13), (xc - 0.02, fy - 0.3, 5.0), (xc + 0.06, fy - 0.3, 5.12),
           (xc + 0.17, fy - 0.3, 5.06)]
    B.tube(pts, 0.018, 6, "emit_blue", "emit")
    B.tube([(xc - 0.12, fy - 0.3, 4.82), (xc - 0.03, fy - 0.3, 4.88), (xc + 0.04, fy - 0.3, 4.79), (xc + 0.12, fy - 0.3, 4.84)],
           0.013, 6, "emit_blue", "emit")
    B.light_strip((-1.0, fy - 0.004, 5.05), (0.5, 0.008, 0.05), "emit_blue")
    # heat vents, amber behind dark slats
    for cx in (-0.75, 0.75):
        B.box((cx, fy - 0.02, 1.1), (1.16, 0.04, 0.78), "frame", "frame", 0.006)
        B.vent(cx, 1.1, 1.04, 0.66, fy - 0.045, 6, "emit_amber", "dark")
    # overhead cable tray
    B.box((0, fy - 0.14, 5.45), (iw, 0.28, 0.04), "trim", "frame", 0.0)
    for yy in (-0.08, -0.18):
        B.cyl((0, fy + yy, 5.5), 0.035, iw, "X", 6, "cable", "cable", 0.0)


def nvg_wall_turbine(B, w=4.0, h=6.0, t=0.5):
    """Turbine hall bay: a ribbed turbine casing emerging from the bay with amber heat slits, an
    overhead crane rail with trolley and hook block, a blue arc indicator on the lintel."""
    fy = _nvg_shell(B, w, h, t)
    iw = w - 1.0
    B.box((0, 0, 0.8), (iw, t, 0.8), "concrete", "frame", 0.0)
    B.box((0, 0, 5.35), (iw, t, 0.6), "concrete", "frame", 0.0)
    B.box((0, 0.18, 3.1), (iw, 0.06, 3.9), "internal", "internal", 0.0)
    B.box((0, -0.04, 1.26), (iw, t + 0.1, 0.12), "trim", "frame", 0.006)
    B.box((0, -0.03, 4.95), (iw, t + 0.08, 0.2), "frame", "frame", 0.01)
    # casing: front shell segment, end flanges, ribs, heat slits
    cz, cy, R = 3.0, 0.66, 1.05
    B.ring((0, cy, cz), R, R - 0.07, iw - 0.1, "X", 28, "frame", "frame", 0.0, arc=(205, 335))
    for x in (-(iw / 2 - 0.1), iw / 2 - 0.1):
        B.ring((x, cy, cz), R + 0.08, R - 0.12, 0.1, "X", 22, "trim", "frame", 0.0, arc=(205, 335))
    for k in range(4):
        x = -0.9 + k * 0.6
        B.ring((x, cy, cz), R + 0.04, R - 0.02, 0.06, "X", 20, "dark", "frame", 0.0, arc=(208, 332))
    for k in range(3):
        x = -0.6 + k * 0.6
        B.ring((x, cy, cz), R + 0.012, R - 0.02, 0.05, "X", 28, "emit_amber", "emit", 0.0, arc=(250, 290))
    B.cyl((1.0, -0.25, cz + 0.55), 0.09, 0.06, "Y", 12, "dark", "greeble", 0.0)
    B.ring((1.0, -0.285, cz + 0.55), 0.08, 0.06, 0.012, "Y", 12, "emit_blue", "emit", 0.0)
    # crane rail with brackets, trolley, falls and hook block
    B.box((0, fy - 0.32, 4.72), (w - 0.2, 0.2, 0.05), "trim", "frame", 0.0)
    B.box((0, fy - 0.32, 4.6), (w - 0.2, 0.04, 0.2), "frame", "frame", 0.0)
    B.box((0, fy - 0.32, 4.48), (w - 0.2, 0.16, 0.04), "trim", "frame", 0.0)
    for sx in (-1, 1):
        B.box((sx * 1.5, fy - 0.17, 4.6), (0.1, 0.34, 0.3), "dark", "frame", 0.0)
    B.box((-0.7, fy - 0.32, 4.36), (0.36, 0.26, 0.18), "hazard", "greeble", 0.006)
    for dx in (-0.05, 0.05):
        B.cyl((-0.7 + dx, fy - 0.32, 3.95), 0.008, 0.66, "Z", 5, "cable", "cable", 0.0)
    B.box((-0.7, fy - 0.32, 3.55), (0.18, 0.12, 0.16), "dark", "greeble", 0.004)
    B.light_strip((0, fy - 0.045, 5.0), (iw * 0.6, 0.004, 0.03), "emit_blue")
    B.light_strip((-iw / 2 + 0.3, fy - 0.004, 1.0), (0.2, 0.008, 0.04), "emit_amber")


def nvg_massing_hall(B, w=6.0, h=10.0, d=4.0):
    """Turbine hall block: tall clerestory hall with a saw-tooth roof, two exhaust stacks with heat rings,
    a heavy transformer pair on the forecourt feeding busbars into the hall."""
    hh, fy, cy = 6.0, -d / 2 + 1.0, 0.5
    hd = d - 1.0
    B.zprism(E.outline("nova_grid", w, hd, 0, cy), 0.0, hh, "frame", "frame", 0.0)
    B.box((0, cy, hh + 0.08), (w + 0.1, hd + 0.1, 0.16), "trim", "frame", 0.0)
    for k in range(4):  # saw-tooth roof, glazed vertical faces
        x0 = -w / 2 + k * w / 4
        B.prism([(x0, hh + 0.16), (x0 + w / 4, hh + 0.16), (x0, hh + 1.1)], hd * 0.9, cy, "panel", "frame", 0.0)
        B.box((x0 + 0.04, cy, hh + 0.63), (0.06, hd * 0.9 + 0.02, 0.9), "trim", "frame", 0.0)
    for k in range(5):  # pilasters
        x = (k - 2) * w * 0.22
        B.box((x, fy - 0.08, hh / 2), (0.3, 0.16, hh), "dark", "frame", 0.0)
    for k in range(4):  # clerestory, warm interior light
        x = -w * 0.33 + k * w * 0.22
        B.box((x, fy - 0.012, hh - 1.0), (0.9, 0.02, 0.9), "glass_smoked", "pane", 0.0)
        B.light_strip((x, fy - 0.026, hh - 0.62), (0.84, 0.004, 0.06), "emit_amber")
    B.box((0, fy - 0.02, 1.7), (w * 0.36, 0.04, 3.4), "internal", "internal", 0.0)  # service door
    B.hazard_band((0, fy - 0.04, 3.5), (w * 0.38, 0.01, 0.16), 8)
    for xs, sh in ((0.3, 9.8), (0.13, 8.6)):  # exhaust stacks behind the roof line
        x = w * xs
        B.cyl((x, d * 0.3, sh / 2), 0.34, sh, "Z", 12, "concrete", "frame", 0.0, radius2=0.28)
        for z in (sh * 0.62, sh * 0.82):
            B.cyl((x, d * 0.3, z), 0.38, 0.12, "Z", 12, "trim", "frame", 0.0)
        B.cyl((x, d * 0.3, sh - 0.1), 0.29, 0.1, "Z", 12, "emit_amber", "emit", 0.0)
    for sx in (-1, 1):  # transformer pair on the forecourt, busbars up into the hall
        x = sx * w * 0.3
        B.box((x, -d / 2 + 0.5, 0.75), (1.3, 0.9, 1.5), "dark", "frame", 0.01)
        for k in range(6):
            B.box((x - 0.55 + k * 0.22, -d / 2 + 0.03, 0.75), (0.04, 0.06, 1.2), "trim", "greeble", 0.0)
        for k in range(3):
            xx = x - 0.35 + k * 0.35
            B.cyl((xx, -d / 2 + 0.55, 1.75), 0.06, 0.5, "Z", 8, "polymer", "greeble", 0.0)
            B.box((xx, fy - 0.25, 2.1), (0.05, 0.5, 0.05), "trim", "greeble", 0.0)
        B.light_strip((x, -d / 2 + 0.025, 1.35), (0.3, 0.004, 0.04), "emit_blue")


def nvg_massing_stack(B, w=3.0, h=14.0, d=3.0):
    """Exhaust stack tower: tapered stack on a plant block, gantry rings, amber heat crown, blue beacon."""
    B.zprism(E.outline("nova_grid", w, d), 0.0, 3.0, "frame", "frame", 0.0)
    B.box((0, 0, 3.06), (w + 0.1, d + 0.1, 0.12), "trim", "frame", 0.0)
    B.vent(0, 1.5, w * 0.6, 1.2, -d / 2 - 0.004, 6, "emit_amber", "dark")
    B.lathe([(0.0, 3.1), (1.15, 3.1), (1.0, 6.0), (0.82, 10.0), (0.74, 13.6), (0.82, 13.7), (0.82, 13.9), (0.0, 13.9)],
            (0, 0, 0), 14, "concrete", "frame")
    for z, r in ((5.5, 1.06), (9.0, 0.9)):
        B.cyl((0, 0, z), r + 0.2, 0.08, "Z", 14, "trim", "frame", 0.0)
        for k in range(6):
            a = k * math.pi / 3
            B.cyl((math.cos(a) * (r + 0.18), math.sin(a) * (r + 0.18), z + 0.5), 0.02, 1.0, "Z", 4, "trim", "frame", 0.0)
        B.cyl((0, 0, z + 1.0), r + 0.2, 0.03, "Z", 14, "trim", "frame", 0.0, radius2=r + 0.2)
    for z in (12.6, 13.2):
        B.cyl((0, 0, z), 0.79, 0.12, "Z", 14, "emit_amber", "emit", 0.0)
    B.cyl((0, -0.55, 13.95), 0.07, 0.12, "Z", 8, "emit_blue", "emit", 0.0)


# ------------------------------------------------------------------------------------------------
# CIVITAS: civic facade and surveillance glass (cold blue with red security lights)
# ------------------------------------------------------------------------------------------------
def _cvt_camera(B, x, y, z, s=1.0):
    B.box((x, y + 0.06 * s, z + 0.08 * s), (0.08 * s, 0.12 * s, 0.05 * s), "dark", "greeble", 0.0)
    B.lathe([(0.0, 0.0), (0.09 * s, 0.0), (0.085 * s, -0.04 * s), (0.06 * s, -0.075 * s), (0.0, -0.09 * s)], (x, y, z + 0.05 * s),
            8, "glass_smoked", "greeble")
    B.light_strip((x, y - 0.088 * s, z + 0.0), (0.022 * s, 0.008, 0.022 * s), "emit_red")


def cvt_wall_facade(B, w=4.0, h=6.0, t=0.5):
    """Civic facade: a stepped plinth, four tapered columns under a heavy entablature, slit windows
    with cold blue light, a surveillance eye in the frieze, dome cameras and red security lights."""
    fy = -t / 2
    B.box((0, -0.12, 0.08), (w, t + 0.34, 0.16), "dark", "frame", 0.01)
    B.box((0, -0.06, 0.25), (w - 0.1, t + 0.2, 0.18), "concrete", "frame", 0.01)
    B.box((0, 0.05, 2.75), (w, t - 0.1, 4.7), "concrete", "frame", 0.0)
    for x in (-1.0, 0.0, 1.0):  # slit windows between the columns
        B.box((x, fy + 0.09, 2.8), (0.4, 0.04, 3.7), "internal", "internal", 0.0)
        B.light_strip((x, fy + 0.07, 2.8), (0.03, 0.004, 3.4), "emit_blue")
        for z in (1.6, 2.8, 4.0):
            B.light_strip((x, fy + 0.07, z), (0.3, 0.004, 0.012), "emit_blue")
        B.box((x, fy + 0.04, 2.8), (0.38, 0.012, 3.66), "glass_smoked", "pane", 0.0)
    for x in (-1.5, -0.5, 0.5, 1.5):
        B.zprism(K.chamfer_rect(0.28, 0.3, 0.06, x, fy - 0.12), 0.34, 4.96, "frame", "frame", 0.0, top_scale=0.86)
        B.box((x, fy - 0.12, 5.02), (0.4, 0.4, 0.12), "trim", "frame", 0.006)
        B.box((x, fy - 0.12, 0.4), (0.38, 0.38, 0.1), "trim", "frame", 0.006)
        B.box((x, fy - 0.28, 2.6), (0.03, 0.012, 3.6), "dark", "greeble", 0.0)
    B.box((0, fy - 0.08, 5.36), (w, t * 0.5 + 0.5, 0.56), "frame", "frame", 0.01)
    B.box((0, fy - 0.1, 5.73), (w + 0.06, t * 0.5 + 0.6, 0.16), "trim", "frame", 0.01)
    B.box((0, fy - 0.33, 5.14), (w, 0.02, 0.06), "trim", "frame", 0.0)
    B.light_strip((0, fy - 0.334, 5.42), (w * 0.78, 0.004, 0.025), "emit_blue")
    # surveillance eye in the frieze
    B.ring((0, fy - 0.36, 5.38), 0.22, 0.15, 0.04, "Y", 20, "trim", "frame", 0.0)
    B.cyl((0, fy - 0.35, 5.38), 0.15, 0.02, "Y", 20, "glass_smoked", "greeble", 0.0)
    B.cyl((0, fy - 0.365, 5.38), 0.04, 0.01, "Y", 10, "emit_red", "emit", 0.0)
    for x in (-1.0, 1.0):
        _cvt_camera(B, x, fy - 0.3, 4.96, 1.0)
    for x in (-w / 2 + 0.12, w / 2 - 0.12):  # red security lights at the entablature ends
        B.light_strip((x, fy - 0.334, 5.42), (0.08, 0.006, 0.08), "emit_red")


def cvt_wall_glass(B, w=4.0, h=6.0, t=0.5):
    """Surveillance glass: angular pilasters framing a three-storey curtain wall, cold blue office light
    behind smoked glass, camera pods on the mullions, a scanning band and red security lights."""
    fy = -t / 2
    pil = 0.3
    B.box((0, 0, 0.15), (w, t + 0.1, 0.3), "dark", "frame", 0.01)
    for sx in (-1, 1):
        B.zprism(K.chamfer_rect(pil, t + 0.1, 0.1, sx * (w / 2 - pil / 2), -0.02), 0.3, h - 0.3, "frame", "frame", 0.0,
                 top_scale=0.9)
        B.light_strip((sx * (w / 2 - pil / 2), fy - 0.08, 2.5), (0.02, 0.004, 3.6), "emit_blue")
    iw = w - 2 * pil
    B.box((0, 0.2, 3.0), (iw, 0.05, 5.4), "internal", "internal", 0.0)
    floors = (0.3, 2.0, 3.7, 5.4)
    for z in floors:
        B.box((0, -0.02, z), (iw, t + 0.04, 0.18), "frame", "frame", 0.006)
    for a, b in zip(floors[:-1], floors[1:]):
        B.light_strip((0, 0.1, b - 0.18), (iw * 0.96, 0.02, 0.03), "emit_blue")
        for k in range(3):  # desks and screens seen through the glass
            x = -iw / 3 + k * iw / 3
            B.box((x, 0.12, a + 0.6), (0.6, 0.06, 0.6), "dark", "internal", 0.0)
            B.light_strip((x, 0.085, a + 0.85), (0.34, 0.004, 0.2), "emit_blue")
        B.box((0, fy + 0.02, (a + b) / 2), (iw - 0.02, 0.012, b - a - 0.18), "glass_smoked", "pane", 0.0)
        for k in range(1, 4):
            x = -iw / 2 + k * iw / 4
            B.box((x, fy - 0.02, (a + b) / 2), (0.05, 0.08, b - a - 0.18), "trim", "frame", 0.0)
    for x, z in ((-iw / 4, 3.7), (iw / 4, 2.0)):
        _cvt_camera(B, x, fy - 0.12, z - 0.12, 0.8)
    B.box((0, -0.04, h - 0.2), (w, t + 0.12, 0.4), "frame", "frame", 0.01)
    B.light_strip((0, fy - 0.1, h - 0.2), (w * 0.8, 0.004, 0.04), "emit_blue")
    for x in (-w / 2 + 0.15, w / 2 - 0.15):
        B.light_strip((x, fy - 0.1, h - 0.2), (0.08, 0.006, 0.08), "emit_red")


def cvt_massing_slab(B, w=6.0, h=10.0, d=4.0):
    """Civic administration slab: a raised podium, a glazed slab with cold blue floor bands, a cantilevered
    crown carrying a surveillance ring, red aviation lights at the corners."""
    B.zprism(K.chamfer_rect(w, d, 0.4), 0.0, 1.6, "concrete", "frame", 0.0)
    B.box((0, 0, 1.66), (w + 0.1, d + 0.1, 0.12), "trim", "frame", 0.0)
    sw, sd = w * 0.78, d * 0.7
    B.zprism(K.chamfer_rect(sw, sd, 0.3), 1.72, 8.2, "frame", "frame", 0.0)
    B.box((0, -sd / 2 - 0.01, 4.96), (sw * 0.9, 0.02, 6.2), "glass_smoked", "pane", 0.0)
    for k in range(8):
        z = 2.2 + k * 0.8
        B.light_strip((0, -sd / 2 - 0.024, z), (sw * 0.86, 0.004, 0.04), "emit_blue")
    for k in range(7):
        x = -sw * 0.45 + k * sw * 0.15
        B.box((x, -sd / 2 - 0.04, 4.96), (0.08, 0.06, 6.3), "trim", "frame", 0.0)
    B.zprism(K.chamfer_rect(w * 0.92, d * 0.86, 0.4), 8.2, 8.8, "frame", "frame", 0.0, top_scale=1.04)
    B.light_strip((0, -d * 0.43 - 0.03, 8.5), (w * 0.8, 0.004, 0.06), "emit_blue")
    B.ring((0, 0, 9.3), 1.5, 1.38, 0.12, "Z", 24, "trim", "frame", 0.0)
    B.cyl((0, 0, 9.05), 0.2, 0.5, "Z", 8, "dark", "frame", 0.0)
    for k in range(6):
        a = k * math.pi / 3 + math.pi / 6
        _cvt_camera(B, math.cos(a) * 1.44, math.sin(a) * 1.44, 9.12, 1.6)
    for sx in (-1, 1):
        for sy in (-1, 1):
            B.cyl((sx * w * 0.44, sy * d * 0.4, 8.86), 0.08, 0.12, "Z", 8, "emit_red", "emit", 0.0)
    B.box((0, -d / 2 - 0.02, 0.9), (w * 0.3, 0.04, 1.4), "internal", "internal", 0.0)
    B.light_strip((0, -d / 2 - 0.044, 1.5), (w * 0.3, 0.004, 0.04), "emit_blue")


def cvt_massing_spire(B, w=3.0, h=14.0, d=3.0):
    """Surveillance spire: angular tapering shaft with scanning bands, a camera halo near the top, a mast
    with red beacons."""
    B.zprism(K.chamfer_rect(w, d, 0.5), 0.0, 1.2, "concrete", "frame", 0.0)
    B.zprism(K.chamfer_rect(w * 0.7, d * 0.7, 0.35), 1.2, 11.0, "frame", "frame", 0.0, top_scale=0.6)
    for z, s in ((3.5, 0.92), (6.5, 0.8), (9.2, 0.68)):
        B.zprism(K.chamfer_rect(w * 0.7 * s + 0.12, d * 0.7 * s + 0.12, 0.3), z, z + 0.16, "trim", "frame", 0.0)
        B.light_strip((0, -d * 0.35 * s - 0.065, z + 0.08), (w * 0.5 * s, 0.004, 0.04), "emit_blue")
    B.light_strip((0, -d * 0.3 - 0.01, 5.0), (0.06, 0.004, 6.0), "emit_blue")
    B.ring((0, 0, 11.2), 1.1, 0.95, 0.1, "Z", 20, "trim", "frame", 0.0)
    for k in range(5):
        a = -math.pi / 2 + (k - 2) * 0.7
        _cvt_camera(B, math.cos(a) * 1.02, math.sin(a) * 1.02, 11.08, 1.4)
    B.cyl((0, 0, 12.4), 0.06, 2.6, "Z", 6, "trim", "frame", 0.0, radius2=0.03)
    for z in (12.2, 13.6):
        B.cyl((0, 0, z), 0.09, 0.1, "Z", 8, "emit_red", "emit", 0.0)


# ------------------------------------------------------------------------------------------------
# MERIDIAN: monumental temporal arches and rings (violet and cyan temporal glow)
# ------------------------------------------------------------------------------------------------
def _mrd_body(B, w, h, t, top=5.5):
    fy = -t / 2
    for k, (z0, z1, dd) in enumerate(((0.0, 0.15, 0.36), (0.15, 0.3, 0.24), (0.3, 0.45, 0.12))):
        B.box((0, -dd / 2, (z0 + z1) / 2), (w, t + dd, z1 - z0), "dark" if k == 0 else "concrete", "frame", 0.01)
    B.box((0, 0, (0.45 + top) / 2), (w, t, top - 0.45), "concrete", "frame", 0.0)
    for k in range(1, 9):  # ashlar courses
        z = 0.45 + k * (top - 0.45) / 9
        B.box((0, fy - 0.003, z), (w, 0.008, 0.018), "internal", "greeble", 0.0)
    B.box((0, -0.06, top + 0.12), (w, t + 0.14, 0.24), "frame", "frame", 0.01)
    B.box((0, -0.1, top + 0.3), (w + 0.04, t + 0.22, 0.12), "trim", "frame", 0.006)
    B.light_strip((0, -t / 2 - 0.124, 0.375), (w * 0.9, 0.004, 0.014), "emit_violet")
    return fy


def mrd_wall_arch(B, w=4.0, h=6.0, t=0.5):
    """Monumental temporal arch: stepped plinth, ashlar body, a deep round-headed arch with voussoirs and
    keystone, broken violet rings and a cyan core ring hanging in the arch."""
    fy = _mrd_body(B, w, h, t, top=5.55)
    cz, ro, ri = 3.1, 1.5, 1.12
    B.box((0, fy - 0.012, 1.78), (2.24, 0.02, 2.66), "internal", "internal", 0.0)
    B.prism(_arc_pts(0, cz, ri, 0, 180, 16), 0.02, fy - 0.012, "internal", "internal", 0.0)
    for sx in (-1, 1):
        B.box((sx * (ri + 0.19), fy - 0.09, 1.78), (0.38, 0.18, 2.66), "frame", "frame", 0.01)
        B.box((sx * (ri + 0.19), fy - 0.12, cz - 0.05), (0.46, 0.24, 0.1), "trim", "frame", 0.0)
    B.ring((0, fy - 0.09, cz), ro, ri, 0.18, "Y", 24, "frame", "frame", 0.0, arc=(0, 180))
    for k in range(1, 9):  # voussoir joints
        a = math.radians(k * 20)
        c = (math.cos(a) * (ro + ri) / 2, fy - 0.185, cz + math.sin(a) * (ro + ri) / 2)
        _rbar(B, c, ro - ri, 0.015, 0.008, 90 - k * 20, "internal", "greeble")
    B.zprism([(-0.16, fy - 0.24), (0.16, fy - 0.24), (0.12, fy + 0.02), (-0.12, fy + 0.02)], cz + ri - 0.05, cz + ro + 0.08,
             "trim", "frame", 0.0, top_scale=1.2)
    rc = 2.45
    B.ring((0, fy - 0.05, rc), 0.92, 0.86, 0.04, "Y", 32, "trim", "frame", 0.0)
    for a0 in (12, 132, 252):
        B.ring((0, fy - 0.07, rc), 0.82, 0.77, 0.03, "Y", 32, "emit_violet", "emit", 0.0, arc=(a0, a0 + 96))
    B.ring((0, fy - 0.08, rc), 0.5, 0.46, 0.025, "Y", 24, "emit_cyan", "emit", 0.0)
    B.cyl((0, fy - 0.08, rc), 0.09, 0.04, "Y", 12, "emit_cyan", "emit", 0.0)
    for k in range(4):
        a = math.radians(45 + k * 90)
        _rbar(B, (math.cos(a) * 0.66, fy - 0.05, rc + math.sin(a) * 0.66), 0.22, 0.03, 0.02, 90 - 45 - k * 90, "trim")
    for sx in (-1, 1):  # flanking pilasters with violet capitals
        x = sx * (w / 2 - 0.16)
        B.box((x, fy - 0.08, 3.0), (0.32, 0.16, 5.1), "frame", "frame", 0.006)
        B.light_strip((x, fy - 0.162, 5.2), (0.2, 0.004, 0.05), "emit_violet")


def mrd_wall_ring(B, w=4.0, h=6.0, t=0.5):
    """Ring gate: an ashlar block carrying a great stepped ring with segmented violet light, radial struts
    to a cyan core and twelve glyph ticks, set over a dark recessed disc."""
    fy = _mrd_body(B, w, h, t, top=5.55)
    cz = 3.0
    B.cyl((0, fy - 0.02, cz), 1.42, 0.02, "Y", 32, "internal", "internal", 0.0)
    B.ring((0, fy - 0.12, cz), 1.78, 1.46, 0.24, "Y", 32, "trim", "frame", 0.0)
    B.ring((0, fy - 0.06, cz), 1.46, 1.38, 0.14, "Y", 32, "frame", "frame", 0.0)
    for k in range(6):
        a0 = k * 60 + 6
        B.ring((0, fy - 0.03, cz), 1.36, 1.3, 0.03, "Y", 36, "emit_violet", "emit", 0.0, arc=(a0, a0 + 48))
    for k in range(12):
        a = math.radians(k * 30)
        r = 1.62
        _rbar(B, (math.cos(a) * r, fy - 0.245, cz + math.sin(a) * r), 0.16 if k % 3 == 0 else 0.08, 0.03, 0.01,
              90 - k * 30, "dark", "greeble")
    for k in range(4):
        a = math.radians(k * 90 + 45)
        _rbar(B, (math.cos(a) * 0.86, fy - 0.03, cz + math.sin(a) * 0.86), 0.88, 0.05, 0.04, 90 - k * 90 - 45, "frame")
    B.ring((0, fy - 0.04, cz), 0.44, 0.36, 0.05, "Y", 24, "trim", "frame", 0.0)
    B.ring((0, fy - 0.06, cz), 0.34, 0.3, 0.02, "Y", 24, "emit_cyan", "emit", 0.0)
    B.cyl((0, fy - 0.05, cz), 0.12, 0.04, "Y", 12, "emit_cyan", "emit", 0.0)
    for sx in (-1, 1):
        B.box((sx * (w / 2 - 0.12), fy - 0.06, 3.0), (0.24, 0.12, 5.1), "frame", "frame", 0.004)


def mrd_massing_monument(B, w=6.0, h=10.0, d=4.0):
    """Temporal monument: a three-tier stepped mass with an arch relief, crowned by a great standing ring
    with violet segments and a cyan core."""
    z = 0.0
    for k, (th, s) in enumerate(((2.6, 1.0), (2.0, 0.8), (1.4, 0.62))):
        B.zprism(K.chamfer_rect(w * s, d * s, 0.2), z, z + th, "concrete", "frame", 0.0)
        B.box((0, 0, z + th + 0.05), (w * s + 0.1, d * s + 0.1, 0.1), "trim", "frame", 0.0)
        B.light_strip((0, -d * s / 2 - 0.054, z + th + 0.05), (w * s * 0.8, 0.004, 0.02), "emit_violet")
        z += th + 0.1
    B.box((0, -d / 2 - 0.01, 1.2), (1.4, 0.02, 2.4), "internal", "internal", 0.0)
    B.ring((0, -d / 2 - 0.03, 2.4), 0.9, 0.7, 0.06, "Y", 16, "frame", "frame", 0.0, arc=(0, 180))
    for sx in (-1, 1):
        B.box((sx * 0.8, -d / 2 - 0.03, 1.2), (0.2, 0.06, 2.4), "frame", "frame", 0.0)
    rc, R = z + 2.0, 1.9
    B.box((0, 0, z + 0.1), (1.6, 0.8, 0.2), "frame", "frame", 0.0)
    B.ring((0, 0, rc), R, R - 0.22, 0.3, "Y", 32, "trim", "frame", 0.0)
    for k in range(4):
        a0 = k * 90 + 10
        B.ring((0, -0.16, rc), R - 0.24, R - 0.32, 0.03, "Y", 32, "emit_violet", "emit", 0.0, arc=(a0, a0 + 70))
    B.ring((0, -0.02, rc), 0.6, 0.52, 0.06, "Y", 20, "emit_cyan", "emit", 0.0)
    for k in range(2):
        a = math.radians(k * 180 + 90)
        _rbar(B, (math.cos(a) * 1.1, 0, rc + math.sin(a) * 1.1), 1.0, 0.08, 0.06, 90 - k * 180 - 90, "frame")


def mrd_massing_obelisk(B, w=3.0, h=14.0, d=3.0):
    """Temporal obelisk: tapered shaft with a pyramidion and three floating orbit rings in violet and cyan."""
    B.zprism(K.chamfer_rect(w, d, 0.3), 0.0, 0.8, "concrete", "frame", 0.0)
    B.zprism(K.chamfer_rect(w * 0.82, d * 0.82, 0.2), 0.8, 1.3, "frame", "frame", 0.0)
    B.zprism(K.chamfer_rect(w * 0.5, d * 0.5, 0.12), 1.3, 12.0, "concrete", "frame", 0.0, top_scale=0.58)
    B.zprism(K.chamfer_rect(w * 0.29, d * 0.29, 0.07), 12.0, 13.8, "trim", "frame", 0.0, top_scale=0.04)
    B.light_strip((0, -d * 0.2 - 0.01, 6.5), (0.05, 0.004, 9.0), "emit_violet")
    for z, r, slot in ((4.0, 1.25, "emit_violet"), (7.6, 1.05, "emit_cyan"), (10.6, 0.85, "emit_violet")):
        B.ring((0, 0, z), r, r - 0.06, 0.05, "Z", 28, slot, "emit", 0.0)
        B.ring((0, 0, z - 0.08), r + 0.06, r - 0.12, 0.04, "Z", 28, "trim", "frame", 0.0)


# ------------------------------------------------------------------------------------------------
# VITA: lab glazing and clean domes (soft green, clean whites)
# ------------------------------------------------------------------------------------------------
def _vta_body(B, w, h, t):
    fy = -t / 2
    B.zprism(K.round_rect(w, t + 0.08, 0.04, 2), 0.0, 0.3, "frame", "frame", 0.0)
    B.box((0, 0, (0.3 + h - 0.3) / 2), (w - 0.5, t, h - 0.6), "light", "frame", 0.0)
    for sx in (-1, 1):
        B.zprism(K.round_rect(0.26, t + 0.06, 0.1, 3, sx * (w / 2 - 0.13), 0), 0.3, h - 0.3, "light", "frame", 0.0)
        B.light_strip((sx * (w / 2 - 0.13), fy - 0.032, 2.8), (0.016, 0.004, 3.8), "emit")
    B.zprism(K.round_rect(w, t + 0.12, 0.06, 2), h - 0.3, h, "frame", "frame", 0.0)
    B.light_strip((0, fy - 0.062, h - 0.15), (w * 0.7, 0.004, 0.02), "emit")
    return fy


def vta_wall_glazing(B, w=4.0, h=6.0, t=0.5):
    """Lab glazing: clean white body with a projecting rounded bay window (deep white reveal, slim
    transom), a lit lab bench with sample columns and a monitor inside, a rounded sill, service panels."""
    fy = _vta_body(B, w, h, t)
    cz, ww, wh, r, dp = 3.55, 3.1, 3.0, 0.3, 0.27
    hw, hh = ww / 2, wh / 2
    B.prism(K.round_rect(ww, wh, r, 4, 0, cz), 0.02, fy - 0.01, "internal", "internal", 0.0)
    B.box((0, fy - 0.03, cz + hh - 0.16), (ww - 0.6, 0.01, 0.04), "emit_white", "emit", 0.0)
    B.box((0, fy - 0.08, cz - hh + 0.62), (ww - 0.4, 0.14, 0.05), "light", "frame", 0.0)
    B.box((0, fy - 0.04, cz - hh + 0.33), (ww - 0.5, 0.04, 0.52), "frame", "frame", 0.0)
    for k in range(4):
        x = -0.9 + k * 0.6
        B.cyl((x, fy - 0.1, cz - hh + 0.95), 0.075, 0.6, "Z", 10, "glass", "greeble", 0.0)
        B.cyl((x, fy - 0.1, cz - hh + 0.85), 0.06, 0.38, "Z", 8, "emit", "emit", 0.0)
        B.cyl((x, fy - 0.1, cz - hh + 1.28), 0.085, 0.06, "Z", 10, "light", "greeble", 0.0)
    B.box((0.9, fy - 0.05, cz + 0.45), (0.7, 0.03, 0.45), "dark", "greeble", 0.0)
    B.light_strip((0.9, fy - 0.068, cz + 0.45), (0.62, 0.004, 0.37), "emit")
    yc = fy - 0.02 - dp / 2
    for sx in (-1, 1):  # deep reveal: straight runs plus quarter rings at the corners
        B.box((sx * (hw + 0.04), yc, cz), (0.08, dp, wh - 2 * r), "light", "frame", 0.0)
    for sz in (-1, 1):
        B.box((0, yc, cz + sz * (hh + 0.04)), (ww - 2 * r, dp, 0.08), "light", "frame", 0.0)
    for (sx, sz, a0) in ((1, 1, 0), (-1, 1, 90), (-1, -1, 180), (1, -1, 270)):
        B.ring((sx * (hw - r), yc, cz + sz * (hh - r)), r + 0.08, r, dp, "Y", 16, "light", "frame", 0.0, arc=(a0, a0 + 90))
    yg = fy - 0.02 - dp + 0.03
    B.box((0, yg - 0.02, cz + 0.2), (ww, 0.03, 0.04), "frame", "frame", 0.0)
    B.box((-0.45, yg - 0.02, cz), (0.04, 0.03, wh), "frame", "frame", 0.0)
    B.prism(K.round_rect(ww, wh, r, 4, 0, cz), 0.012, yg, "glass", "pane", 0.0)
    B.zprism(K.round_rect(ww + 0.3, dp + 0.12, 0.06, 2, 0, yc - 0.04), cz - hh - 0.16, cz - hh - 0.04, "frame", "frame", 0.0)
    B.light_strip((0, yc - dp / 2 - 0.1, cz - hh - 0.1), (ww * 0.6, 0.004, 0.012), "emit")
    for x in (-0.85, 0.85):
        B.prism(K.round_rect(1.4, 1.1, 0.14, 3, x, 1.1), 0.03, fy - 0.015, "panel", "cover", 0.0)
    B.light_strip((-0.85, fy - 0.035, 1.45), (0.4, 0.004, 0.016), "emit")


def vta_wall_dome(B, w=4.0, h=6.0, t=0.5):
    """Dome bay: a projecting round-arched glazed bay with radial mullions and a deep white reveal, a
    clean growth dome on a lit plinth inside, white sill."""
    fy = _vta_body(B, w, h, t)
    sz, R, dp = 3.0, 1.4, 0.34
    shape = [(-R, 0.8), (R, 0.8)] + _arc_pts(0, sz, R, 0, 180, 16)
    B.prism(shape, 0.02, fy - 0.01, "internal", "internal", 0.0)
    B.light_strip((0, fy - 0.025, sz + 0.6), (1.0, 0.004, 0.03), "emit_white")
    B.box((0, fy - 0.12, 1.05), (2.2, 0.18, 0.5), "light", "frame", 0.0)
    B.box((0, fy - 0.212, 1.12), (1.6, 0.004, 0.025), "emit", "emit", 0.0)
    dome = _dome(B, (0, fy - 0.14, 1.3), 0.95, "glass", 18, 5, 0.08)
    K.scale(dome, (1.0, 0.16, 1.0), (0, fy - 0.14, 1.3))
    for k in range(3):
        a = 50 + k * 40
        _rbar(B, (math.cos(math.radians(a)) * 0.48, fy - 0.19, 1.3 + math.sin(math.radians(a)) * 0.48), 0.97, 0.02, 0.012,
              90 - a, "light", "greeble")
    B.lathe([(0.0, 0.0), (0.24, 0.0), (0.2, 0.22), (0.09, 0.36), (0.0, 0.38)], (0, fy - 0.1, 1.3), 10, "emit", "emit")
    B.cyl((0, fy - 0.14, 1.32), 0.97, 0.04, "Z", 18, "emit", "emit", 0.0)
    yc = fy - 0.02 - dp / 2
    for sx in (-1, 1):
        B.box((sx * (R + 0.04), yc, (0.8 + sz) / 2), (0.08, dp, sz - 0.8), "light", "frame", 0.0)
    B.ring((0, yc, sz), R + 0.08, R, dp, "Y", 20, "light", "frame", 0.0, arc=(0, 180))
    yg = fy - 0.02 - dp + 0.03
    B.box((0, yg - 0.02, sz), (2 * R, 0.03, 0.04), "frame", "frame", 0.0)
    B.box((0, yg - 0.02, (0.8 + sz) / 2), (0.04, 0.03, sz - 0.8), "frame", "frame", 0.0)
    for k in range(1, 4):
        a = k * 45
        _rbar(B, (math.cos(math.radians(a)) * R / 2, yg - 0.02, sz + math.sin(math.radians(a)) * R / 2), R, 0.035, 0.03,
              90 - a, "frame")
    B.prism(shape, 0.012, yg, "glass", "pane", 0.0)
    B.zprism(K.round_rect(2 * R + 0.36, dp + 0.12, 0.06, 2, 0, yc - 0.04), 0.66, 0.8, "frame", "frame", 0.0)
    B.light_strip((0, yc - dp / 2 - 0.1, 0.73), (R, 0.004, 0.012), "emit")


def vta_massing_pavilion(B, w=6.0, h=10.0, d=4.0):
    """Lab pavilion: rounded two-storey block with a glazing band, a roof terrace carrying a large and a
    small clean dome with ribs and green base rings."""
    B.zprism(K.round_rect(w, d, 0.9, 4), 0.0, 4.6, "light", "frame", 0.0)
    B.zprism(K.round_rect(w + 0.1, d + 0.1, 0.92, 4), 4.6, 4.78, "frame", "frame", 0.0)
    B.box((0, -d / 2 - 0.01, 2.6), (w * 0.7, 0.02, 1.1), "glass", "pane", 0.0)
    B.light_strip((0, -d / 2 - 0.024, 2.2), (w * 0.66, 0.004, 0.03), "emit")
    for k in range(6):
        B.box((-w * 0.33 + k * w * 0.132, -d / 2 - 0.03, 2.6), (0.05, 0.04, 1.1), "frame", "frame", 0.0)
    B.box((0, -d / 2 - 0.02, 0.9), (1.2, 0.04, 1.8), "internal", "internal", 0.0)
    for (x, y, r) in ((-0.8, 0.0, 1.7), (1.85, 0.2, 0.85)):
        B.cyl((x, y, 4.9), r + 0.12, 0.24, "Z", 20, "light", "frame", 0.0)
        B.cyl((x, y, 5.04), r + 0.02, 0.05, "Z", 20, "emit", "emit", 0.0)
        _dome(B, (x, y, 5.02), r, "glass", 20, 6, 0.1)
        for k in range(4):
            a = k * math.pi / 4
            B.ring((x, y, 5.02), r + 0.02, r - 0.03, 0.04, "Y", 20, "light", "frame", 0.0, arc=(0, 180))
            # ribs share the meridian; rotate each about Z
            K.rotate(B.parts[-1], math.degrees(a), "Z", (x, y, 5.02))


def vta_massing_tower(B, w=3.0, h=14.0, d=3.0):
    """Clean research tower: rounded shaft with soft green floor lines, a glazed observation drum and dome cap."""
    B.zprism(K.round_rect(w, d, 0.8, 4), 0.0, 1.0, "frame", "frame", 0.0)
    B.zprism(K.round_rect(w * 0.76, d * 0.76, 0.6, 4), 1.0, 10.2, "light", "frame", 0.0)
    for k in range(6):
        B.light_strip((0, -d * 0.38 - 0.01, 2.0 + k * 1.4), (w * 0.5, 0.004, 0.03), "emit")
    B.cyl((0, 0, 10.6), 1.25, 0.8, "Z", 20, "glass", "pane", 0.0)
    B.cyl((0, 0, 10.24), 1.3, 0.12, "Z", 20, "frame", "frame", 0.0)
    B.cyl((0, 0, 11.03), 1.32, 0.1, "Z", 20, "light", "frame", 0.0)
    B.cyl((0, 0, 10.5), 1.2, 0.04, "Z", 20, "emit", "emit", 0.0)
    _dome(B, (0, 0, 11.08), 1.2, "light", 20, 6, 0.08)
    B.cyl((0, 0, 12.6), 0.04, 1.2, "Z", 6, "trim", "frame", 0.0)
    B.cyl((0, 0, 13.2), 0.07, 0.08, "Z", 8, "emit", "emit", 0.0)


WALLS = {"nova_grid": (nvg_wall_busbar, nvg_wall_turbine), "civitas": (cvt_wall_facade, cvt_wall_glass),
         "meridian": (mrd_wall_arch, mrd_wall_ring), "vita": (vta_wall_glazing, vta_wall_dome)}
MASSING = {"nova_grid": (nvg_massing_hall, nvg_massing_stack), "civitas": (cvt_massing_slab, cvt_massing_spire),
           "meridian": (mrd_massing_monument, mrd_massing_obelisk), "vita": (vta_massing_pavilion, vta_massing_tower)}
PURPOSE = {
    "nova_grid": ("Mid-back busbar wall: buttressed concrete, busbars on insulators, blue discharge arc, amber heat vents",
                  "Mid-back turbine hall bay: ribbed turbine casing with amber heat slits, crane rail and hook block",
                  "Background turbine hall: saw-tooth roof, exhaust stacks with heat rings, transformer pair",
                  "Background exhaust stack tower with gantry rings and an amber heat crown"),
    "civitas": ("Mid-back civic facade: columns under an entablature, slit windows, surveillance eye, red security lights",
                "Mid-back surveillance glass: three-storey curtain wall, cold blue light, camera pods, red security lights",
                "Background civic slab: podium, glazed slab with blue floor bands, crown with a surveillance ring",
                "Background surveillance spire with scanning bands, camera halo and red beacons"),
    "meridian": ("Mid-back temporal arch: ashlar body, round-headed arch, violet rings and a cyan core",
                 "Mid-back ring gate: great stepped ring with violet segments, radial struts, cyan core",
                 "Background temporal monument: three stepped tiers crowned by a standing ring",
                 "Background temporal obelisk with three floating orbit rings"),
    "vita": ("Mid-back lab glazing: rounded window, lit lab bench and sample columns behind clean glass",
             "Mid-back dome alcove: round-arched glazed bay with a clean growth dome inside",
             "Background lab pavilion with a large and a small clean dome on the roof",
             "Background research tower with an observation drum and dome cap"),
}
