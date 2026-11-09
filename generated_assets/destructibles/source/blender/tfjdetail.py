"""tfjdetail: premium secondary-detail helpers shared by the component and environment kits
(premium uplift pass, 2026-11-10). Everything is real geometry sized for the MissionView camera
(about 60-200 px per piece): chamfered posts and caps that catch a worn edge highlight, panel
seams, bolts, vents, cable looms, rack units with emissive status lights, and chapter accents.
Builders stay within the contract budgets (standard <= 1,500 tris, hero <= 3,000)."""
import math
import bmesh
from mathutils import Vector
import tfjkit as K

UNITS_PER_TILE = 3  # electronic_module sets: three rack units per texture tile (materials notes)


def module_face(B, x0, x1, z0, z1, y_face, depth=0.02, unit=None, slot="module", role="cover"):
    """A rack unit plate facing -Y whose front face shows exactly one unit of the chapter
    electronic_module texture (status lights in its emission mask)."""
    cx, cz = (x0 + x1) / 2, (z0 + z1) / 2
    ob = B.box((cx, y_face + depth / 2, cz), (x1 - x0, depth, z1 - z0), slot, role, 0.0)
    k = B.rng.randrange(UNITS_PER_TILE) if unit is None else unit % UNITS_PER_TILE
    me = ob.data
    uvl = me.uv_layers.active.data
    for poly in me.polygons:
        if poly.normal.y < -0.7:
            for li in poly.loop_indices:
                co = me.vertices[me.loops[li].vertex_index].co
                u = (co.x - x0) / max(1e-6, x1 - x0)
                v = (k + 0.04 + 0.92 * (co.z - z0) / max(1e-6, z1 - z0)) / UNITS_PER_TILE
                uvl[li].uv = (u, v)
    return ob


def bolts(B, pts, y_face, s=0.014, slot="trim", normal="-Y"):
    """Square bolt heads (12 tris each). pts are (x, z) on a -Y face, or (y, z) on a +-X face."""
    out = []
    for p in pts:
        if normal == "-Y":
            out.append(B.box((p[0], y_face - 0.003, p[1]), (s, 0.006, s), slot, "greeble", 0.0))
        else:
            sx = -1 if normal == "-X" else 1
            out.append(B.box((y_face + sx * 0.003, p[0], p[1]), (0.006, s, s), slot, "greeble", 0.0))
    return out


def corner_posts(B, w, d, z0, z1, post, slot="frame", accent=True, accent_slot="accent", caps=True):
    """Four chamfered corner posts with optional amber corner caps (SV-04, SV-06)."""
    out = []
    for sx in (-1, 1):
        for sy in (-1, 1):
            cx, cy = sx * (w / 2 - post / 2), sy * (d / 2 - post / 2)
            out.append(B.zprism(K.chamfer_rect(post, post, post * 0.3, cx, cy), z0, z1, slot, "frame", 0.0))
            if caps and sy < 0:
                ch = min(0.05, (z1 - z0) * 0.06)
                for zz, top in ((z1 - ch / 2, True), (z0 + ch / 2, False)):
                    out.append(B.box((cx, cy - 0.004, zz), (post * 1.08, post * 1.08, ch),
                                     accent_slot if accent else slot, "frame", 0.004))
    return out


def seam_grid(B, x0, x1, z0, z1, y_face, cols, rows, gap=0.01, thick=0.016, slot="panel", bolt=True,
              skip=None):
    """Cladding plates with real seams and a bolt at alternate plate corners."""
    out = B.plate_grid(x0, x1, z0, z1, y_face, cols, rows, gap, thick, slot, "cover", 0.005, skip=skip)
    if bolt:
        w, h = (x1 - x0) / cols, (z1 - z0) / rows
        pts = []
        for i in range(cols):
            for j in range(rows):
                if skip and (i, j) in skip:
                    continue
                if (i + j) % 2 == 0:
                    pts.append((x0 + i * w + 0.03, z0 + (j + 1) * h - 0.03))
                    pts.append((x0 + (i + 1) * w - 0.03, z0 + j * h + 0.03))
        out += bolts(B, pts, y_face - thick, 0.012, "trim")
    return out


def side_seams(B, y0, y1, z0, z1, x_face, sign, cols, rows, slot="panel", thick=0.014):
    return B.side_plate_grid(y0, y1, z0, z1, x_face, sign, cols, rows, gap=0.01, thick=thick, slot=slot,
                             role="cover", bevel=0.004)


def louvre(B, cx, cz, w, h, y_face, slats=6, slot="dark", back="internal", normal="-Y"):
    """Recessed vent with angled slats (reads as depth at game scale)."""
    out = []
    if normal == "-Y":
        out.append(B.box((cx, y_face + 0.006, cz), (w, 0.012, h), back, "greeble", 0.0))
        out.append(B.box((cx, y_face - 0.002, cz + h / 2 + 0.006), (w + 0.02, 0.012, 0.012), "trim", "greeble", 0.0))
        out.append(B.box((cx, y_face - 0.002, cz - h / 2 - 0.006), (w + 0.02, 0.012, 0.012), "trim", "greeble", 0.0))
        for k in range(slats):
            z = cz - h / 2 + (k + 0.5) * h / slats
            ob = B.box((cx, y_face - 0.002, z), (w * 0.96, 0.004, h / slats * 0.62), slot, "greeble", 0.0)
            K.rotate(ob, 35, "X", (cx, y_face, z))
            out.append(ob)
    else:  # on a top face (+Z), slats along X
        out.append(B.box((cx, cz, y_face - 0.004), (w, h, 0.008), back, "greeble", 0.0))
        for k in range(slats):
            y = cz - h / 2 + (k + 0.5) * h / slats
            out.append(B.box((cx, y, y_face + 0.003), (w * 0.94, h / slats * 0.5, 0.006), slot, "greeble", 0.0))
    return out


def loom(B, a, b, n=3, r=0.01, sag=0.06, spread=0.022, axis=(1, 0, 0), slot="cable", seg=8):
    """Bundle of n sagging cables between a and b, offset along axis."""
    out = []
    ax = Vector(axis).normalized()
    for i in range(n):
        o = ax * (i - (n - 1) / 2) * spread
        out.append(B.cable_run(Vector(a) + o, Vector(b) + o, sag * (1 + 0.15 * i), r * (1 - 0.12 * i), seg, slot))
    return out


def status_leds(B, x0, z, y_face, n=4, pitch=0.022, size=(0.012, 0.006), slot="emit", alt=None, rng=None):
    """Row of small emissive status lights; alt slot on a random one (warning pip)."""
    out = []
    pick = rng.randrange(n) if (rng and alt) else -1
    for i in range(n):
        out.append(B.light_strip((x0 + i * pitch, y_face - 0.002, z), (size[0], 0.004, size[1]),
                                 alt if i == pick else slot))
    return out


def top_hatch(B, cx, cy, z, w, d, slot="panel"):
    """Raised service hatch on a top face with a seam frame and two bolts (seen from the 14 degree camera)."""
    out = [B.box((cx, cy, z + 0.006), (w, d, 0.012), slot, "cover", 0.003)]
    out.append(B.box((cx, cy, z + 0.0125), (w * 0.8, d * 0.08, 0.002), "dark", "greeble", 0.0))
    for sx in (-1, 1):
        out.append(B.box((cx + sx * w * 0.4, cy, z + 0.015), (0.012, 0.012, 0.006), "trim", "greeble", 0.0))
    return out


def screen(B, cx, cz, w, h, y_face, slot="emit", bezel="dark", lines=3, rng=None):
    """Small display: dark bezel, emissive glass with a few brighter text lines (no text pixels)."""
    out = [B.box((cx, y_face - 0.004, cz), (w + 0.02, 0.008, h + 0.02), bezel, "greeble", 0.002)]
    out.append(B.light_strip((cx, y_face - 0.0085, cz), (w, 0.002, h), "glass_smoked"))
    for i in range(lines):
        lw = w * (0.4 + 0.5 * ((rng.random() if rng else 0.5)))
        z = cz + h / 2 - (i + 0.8) * h / (lines + 0.6)
        out.append(B.light_strip((cx - w / 2 + lw / 2 + 0.01, y_face - 0.0105, z), (lw, 0.002, h * 0.07), slot))
    return out
