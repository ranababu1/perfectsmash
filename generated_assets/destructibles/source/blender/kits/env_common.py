"""Environment kit building blocks shared by all chapters, styled per chapter.
Blender axes: X right, -Y towards the camera (Godot +Z), Z up.
Origins: floor modules have their top at Z = 0 and left edge at X = 0, depth centred on Y = 0;
back pieces, props and landmarks are bottom-centre (X and Y centred, lowest point Z = 0);
statics are centred on their collision rectangle like components."""
import math
from mathutils import Vector
import tfjkit as K
import tfjdetail as Dt

STYLE = {
    "helix": dict(corner="chamfer", plate=1.0, rib=0.5, mat_floor="reinforced_steel", mat_wall="reinforced_steel"),
    "vita": dict(corner="round", plate=1.0, rib=1.0, mat_floor="composite", mat_wall="glass_polymer"),
    "nova_grid": dict(corner="heavy", plate=1.0, rib=1.0, mat_floor="reinforced_steel", mat_wall="concrete"),
    "civitas": dict(corner="angular", plate=0.5, rib=0.5, mat_floor="concrete", mat_wall="concrete"),
    "meridian": dict(corner="chamfer", plate=2.0, rib=1.0, mat_floor="concrete", mat_wall="concrete"),
}


def outline(ch, w, d, cx=0.0, cy=0.0, k=0.18):
    c = STYLE[ch]["corner"]
    if c == "round":
        return K.round_rect(w, d, min(w, d) * 0.3, 3, cx, cy)
    if c == "heavy":
        return K.chamfer_rect(w, d, min(w, d) * 0.08, cx, cy)
    return K.chamfer_rect(w, d, min(w, d) * k, cx, cy)


# ------------------------------------------------------------------------------------------------
# Floors
# ------------------------------------------------------------------------------------------------
def floor_tile(B, ch, sx, sz, variant="plain"):
    """sx along X (width), sz along Y (depth). Top at Z = 0."""
    B.box((sx / 2, 0, -0.16), (sx, sz, 0.28), "dark", "frame", 0.0)
    trench = variant == "trench"
    if ch == "nova_grid":
        # steel grating cells with heavy frames
        n = max(1, int(round(sx))), max(1, int(round(sz)))
        for i in range(n[0]):
            for j in range(n[1]):
                x0, y0 = i * sx / n[0], -sz / 2 + j * sz / n[1]
                cw, cd = sx / n[0], sz / n[1]
                if trench and abs(y0 + cd / 2) < cd * 0.6:
                    continue
                B.box((x0 + cw / 2, y0 + cd / 2, -0.03), (cw - 0.02, cd - 0.02, 0.05), "frame", "frame", 0.006)
                for k in range(5):
                    B.box((x0 + cw / 2, y0 + 0.08 + k * (cd - 0.16) / 4, -0.004), (cw - 0.1, 0.03, 0.012), "panel", "cover", 0.0)
        if sx >= 2:
            for k in range(4):  # corner hazard marking only (1 m), so tiled floors do not read as lane lines
                B.box(((k + 0.5) * 0.25, -sz / 2 + 0.08, -0.001), (0.24, 0.12, 0.006),
                      "hazard" if k % 2 == 0 else "rubber", "greeble", 0.0)
    elif ch == "civitas":
        rows = max(1, int(round(sz / 0.5)))
        for j in range(rows):
            y = -sz / 2 + (j + 0.5) * sz / rows
            if trench and abs(y) < 0.4:
                continue
            off = 0.5 if j % 2 else 0.0
            nx = int(round(sx / 1.0))
            for i in range(nx + (1 if off else 0)):
                xa = max(0.0, (i - off) * 1.0)
                xb = min(sx, (i - off + 1) * 1.0)
                if xb - xa < 0.1:
                    continue
                B.box(((xa + xb) / 2, y, -0.02), (xb - xa - 0.012, sz / rows - 0.012, 0.04), "concrete", "frame", 0.004)
        if sx >= 2:
            B.light_strip((sx / 2, -sz * 0.3, -0.001), (sx, 0.02, 0.004), "emit")
    else:
        p = STYLE[ch]["plate"]
        nx, ny = max(1, int(round(sx / p))), max(1, int(round(sz / p)))
        gap = 0.014 if ch != "vita" else 0.008
        for i in range(nx):
            for j in range(ny):
                x = (i + 0.5) * sx / nx
                y = -sz / 2 + (j + 0.5) * sz / ny
                if trench and abs(y) < sz / ny * 0.6:
                    continue
                slot = "panel" if (i * 3 + j * 5) % 7 == 0 else "frame"
                if ch == "vita":
                    B.zprism(K.round_rect(sx / nx - gap, sz / ny - gap, 0.04, 2, x, y), -0.04, 0.0, "light", "cover", 0.0)
                else:
                    B.box((x, y, -0.02), (sx / nx - gap, sz / ny - gap, 0.04), slot, "cover", 0.006)
        if ch != "vita":  # premium pass: bolt heads at alternate plate corners
            for i in range(nx):
                for j in range(ny):
                    x = (i + 0.5) * sx / nx
                    y = -sz / 2 + (j + 0.5) * sz / ny
                    if trench and abs(y) < sz / ny * 0.6:
                        continue
                    hx, hy = sx / nx / 2 - 0.06, sz / ny / 2 - 0.06
                    for bx, by in ((-hx, -hy), (hx, hy)) if (i + j) % 2 == 0 else ((hx, -hy), (-hx, hy)):
                        B.box((x + bx, y + by, 0.002), (0.026, 0.026, 0.006), "trim", "greeble", 0.0)
        if ch == "helix" and sx >= 2:
            for i in range(nx):  # short amber seam inlays (SV-04 floor read), warning colour only as accents
                if i % 2 == 0:
                    B.light_strip(((i + 0.5) * sx / nx, -sz * 0.05, -0.001), (sx / nx * 0.5, 0.018, 0.004), "emit2")
            B.light_strip((sx / 2, -sz * 0.3, -0.001), (sx, 0.025, 0.004), "emit")
            for i in range(nx):
                B.box(((i + 0.5) * sx / nx, sz * 0.3, -0.001), (0.3, 0.06, 0.006), "trim", "greeble", 0.0)
        if ch == "vita":
            for i in range(nx + 1):
                B.cyl((i * sx / nx, -sz * 0.25, -0.002), 0.012, 0.006, "Z", 6, "emit", "emit", 0.0)
        if ch == "meridian":
            r = min(sx, sz) * 0.36
            if sx >= 2:
                # restrained inlay: non-emissive trim ring with one short violet arc
                B.ring((sx / 2, 0, -0.002), r, r - 0.03, 0.006, "Z", 32, "panel", "greeble", 0.0)
                B.ring((sx / 2, 0, -0.001), r, r - 0.03, 0.006, "Z", 8, "emit", "emit", 0.0, arc=(255, 285))
    if trench:
        B.box((sx / 2, 0, -0.12), (sx, 0.7, 0.04), "internal", "internal", 0.0)
        B.cyl((sx / 2, -0.15, -0.09), 0.06, sx, "X", 10, "cable", "cable", 0.0)
        B.cyl((sx / 2, 0.12, -0.08), 0.05, sx, "X", 10, "trim", "greeble", 0.0)
        for k in range(int(sx / 0.25)):
            B.box(((k + 0.5) * 0.25, 0, -0.006), (0.03, 0.7, 0.012), "frame", "cover", 0.0)
        B.light_strip((sx / 2, 0.3, -0.1), (sx, 0.02, 0.01), "emit")


# ------------------------------------------------------------------------------------------------
# Walls (bottom-centre, front face towards -Y)
# ------------------------------------------------------------------------------------------------
def wall(B, ch, w=4.0, h=6.0, t=0.5, kind="solid"):
    fy = -t / 2
    # skeleton: base plinth, cornice, edge pilasters
    B.box((0, 0, 0.15), (w, t + 0.1, 0.3), "dark", "frame", 0.02)
    B.box((0, 0, h - 0.12), (w, t + 0.06, 0.24), "frame", "frame", 0.02)
    pil = 0.32 if ch != "vita" else 0.24
    for sx in (-1, 1):
        B.zprism(outline(ch, pil, t + 0.08, sx * (w / 2 - pil / 2), 0), 0.3, h - 0.24, "frame", "frame", 0.0)
    z0, z1 = 0.3, h - 0.24
    iw = w - 2 * pil
    if kind == "window":
        wz0, wz1 = h * 0.35, h * 0.8
        B.box((0, 0, (z0 + wz0) / 2), (iw, t, wz0 - z0), "panel", "cover", 0.0)
        B.box((0, 0, (wz1 + z1) / 2), (iw, t, z1 - wz1), "panel", "cover", 0.0)
        B.box((0, t * 0.3, (wz0 + wz1) / 2), (iw, 0.04, wz1 - wz0), "internal", "internal", 0.0)
        B.pane((0, -t * 0.05, (wz0 + wz1) / 2), iw, wz1 - wz0, 0.02, "glass_smoked")
        nm = 3 if ch != "civitas" else 5
        for k in range(1, nm):
            x = -iw / 2 + k * iw / nm
            B.box((x, -t * 0.1, (wz0 + wz1) / 2), (0.06, 0.1, wz1 - wz0), "trim", "frame", 0.0)
        B.box((0, -t * 0.1, wz0 + 0.03), (iw, t * 0.6, 0.06), "trim", "frame", 0.0)
        B.light_strip((0, -t * 0.1 - 0.051, wz1 - 0.04), (iw * 0.9, 0.004, 0.02), "emit")
        # silhouettes of equipment behind the glass for depth
        for k in range(3):
            x = -iw / 3 + k * iw / 3
            B.box((x, t * 0.15, wz0 + (wz1 - wz0) * 0.3), (iw / 4, 0.1, (wz1 - wz0) * 0.6), "dark", "internal", 0.0)
        return
    B.box((0, 0, (z0 + z1) / 2), (iw, t, z1 - z0), "frame", "frame", 0.0)
    _wall_detail(B, ch, w, h, t, pil, z0, z1)
    if ch == "helix":
        nx, nz = 2, 4
        for i in range(nx):
            for j in range(nz):
                x = -iw / 2 + (i + 0.5) * iw / nx
                z = z0 + (j + 0.5) * (z1 - z0) / nz
                B.box((x, fy - 0.025, z), (iw / nx - 0.05, 0.05, (z1 - z0) / nz - 0.05), "panel", "cover", 0.008)
        B.box((0, fy - 0.052, (z0 + z1) / 2), (0.06, 0.01, (z1 - z0) * 0.9), "internal", "greeble", 0.0)
        B.light_strip((0, fy - 0.058, (z0 + z1) / 2 + 0.6), (0.016, 0.004, (z1 - z0) * 0.4), "emit")
        B.vent(-iw / 4, z0 + 0.6, iw * 0.3, 0.5, fy - 0.05, 5)
        B.light_strip((iw * 0.3, fy - 0.054, z1 - 0.4), (0.06, 0.004, 0.04), "emit2")
    elif ch == "vita":
        for j in range(3):
            z = z0 + (j + 0.5) * (z1 - z0) / 3
            for i in range(2):
                x = -iw / 2 + (i + 0.5) * iw / 2
                ob = B.prism(K.round_rect(iw / 2 - 0.04, (z1 - z0) / 3 - 0.04, 0.12, 3), 0.04, fy - 0.02, "light", "cover", 0.0)
                K.translate(ob, (x, 0, z))
        B.light_strip((0, fy - 0.045, z0 + (z1 - z0) / 3), (iw * 0.94, 0.004, 0.012), "emit")
        B.box((0, fy - 0.03, z0 + 0.15), (iw, 0.06, 0.3), "frame", "frame", 0.0)
    elif ch == "nova_grid":
        n = int(iw / 1.0)
        for i in range(n + 1):
            x = -iw / 2 + i * iw / n
            B.box((x, fy - 0.06, (z0 + z1) / 2), (0.14, 0.12, z1 - z0), "dark", "frame", 0.01)
            B.box((x, fy - 0.125, (z0 + z1) / 2), (0.24, 0.02, z1 - z0), "frame", "frame", 0.0)
        for zz in (z0 + 1.4, z0 + 1.7):
            B.cyl((0, fy - 0.2, zz), 0.08, iw, "X", 10, "trim", "greeble", 0.0)
        for i in range(n):
            x = -iw / 2 + (i + 0.5) * iw / n
            B.box((x, fy - 0.12, 0.9), (0.16, 0.08, 0.1), "frame", "greeble", 0.0)
        B.hazard_band((0, fy - 0.01, z0 + 0.25), (iw, 0.02, 0.24), 10)
        B.light_strip((0, fy - 0.004, z1 - 0.5), (iw * 0.5, 0.008, 0.05), "emit")
    elif ch == "civitas":
        n = int(iw / 0.5)
        for i in range(n):
            x = -iw / 2 + (i + 0.5) * iw / n
            ob = B.box((x, fy - 0.08, (z0 + z1) / 2), (0.05, 0.16, z1 - z0 - 0.4), "trim", "cover", 0.0)
            K.rotate(ob, 25, "Z", (x, fy - 0.08, 0))
        B.box((0, fy - 0.02, z1 - 0.2), (iw, 0.04, 0.4), "panel", "frame", 0.0)
        B.light_strip((0, fy - 0.045, z1 - 0.2), (iw * 0.9, 0.004, 0.02), "emit")
        B.light_strip((iw * 0.4, fy - 0.045, z0 + 0.8), (0.04, 0.004, 0.04), "emit2")
    elif ch == "meridian":
        rows = 5
        for j in range(rows):
            z = z0 + (j + 0.5) * (z1 - z0) / rows
            off = 0.5 if j % 2 else 0.0
            for i in range(3):
                xa = max(-iw / 2, -iw / 2 + (i - off) * iw / 2.5)
                xb = min(iw / 2, -iw / 2 + (i - off + 1) * iw / 2.5)
                if xb - xa < 0.2:
                    continue
                B.box(((xa + xb) / 2, fy - 0.03, z), (xb - xa - 0.03, 0.06, (z1 - z0) / rows - 0.03), "panel", "cover", 0.01)
        B.ring((0, fy - 0.07, h * 0.55), 0.9, 0.82, 0.03, "Y", 32, "trim", "frame", 0.0)
        B.ring((0, fy - 0.075, h * 0.55), 0.78, 0.76, 0.02, "Y", 32, "emit", "emit", 0.0, arc=(20, 160))


def _wall_detail(B, ch, w, h, t, pil, z0, z1):
    """Premium pass: pilaster bolt rows, a cable loom down the right pilaster, a status screen and LEDs."""
    fy = -t / 2 - 0.04
    for sx in (-1, 1):
        xp = sx * (w / 2 - pil / 2)
        Dt.bolts(B, [(xp + dx, z) for z in (z0 + 0.25, z1 - 0.25, (z0 + z1) / 2) for dx in (-pil * 0.3, pil * 0.3)], fy, 0.02)
        B.box((xp, fy - 0.004, z0 + 0.6), (pil * 0.8, 0.012, 0.06), "dark", "greeble", 0.0)
    xr = w / 2 - pil - 0.06
    for zz in (z0 + 0.5, (z0 + z1) / 2, z1 - 0.5):
        B.box((xr, -t / 2 - 0.05, zz), (0.1, 0.1, 0.05), "trim", "greeble", 0.0)
    B.cyl((xr - 0.02, -t / 2 - 0.07, (z0 + z1) / 2), 0.03, z1 - z0 - 0.2, "Z", 6, "cable", "cable", 0.0)
    B.cyl((xr + 0.03, -t / 2 - 0.065, (z0 + z1) / 2), 0.022, z1 - z0 - 0.2, "Z", 6, "cable", "cable", 0.0)
    if ch not in ("meridian",):
        Dt.screen(B, -w / 2 + pil + 0.45, z0 + 1.55, 0.42, 0.26, -t / 2 - 0.05, "emit", lines=3, rng=B.rng)
        Dt.status_leds(B, -w / 2 + pil + 0.3, z0 + 1.3, -t / 2 - 0.05, 4, 0.04, (0.022, 0.01), "emit", "emit2", B.rng)


def low_wall(B, ch, w=4.0, h=1.1, t=0.4):
    """Near-back low wall with railing and a console face (props layer, no collision)."""
    fy = -t / 2
    B.zprism(outline(ch, w, t, 0, 0, 0.1), 0.0, h * 0.75, "frame", "frame", 0.0)
    B.box((0, 0, h * 0.75 + 0.03), (w, t + 0.06, 0.06), "trim", "frame", 0.006)
    for k in range(5):
        x = -w / 2 + 0.2 + k * (w - 0.4) / 4
        B.cyl((x, 0, h * 0.75 + (h * 0.25) / 2 + 0.03), 0.025, h * 0.25, "Z", 8, "trim", "frame", 0.0)
    B.cyl((0, 0, h - 0.02), 0.03, w - 0.3, "X", 8, "trim", "frame", 0.0)
    for k in range(2):
        x = -w / 4 + k * w / 2
        B.box((x, fy - 0.015, h * 0.45), (w * 0.3, 0.03, h * 0.4), "panel", "cover", 0.004)
        B.light_strip((x - w * 0.08, fy - 0.032, h * 0.55), (w * 0.08, 0.004, 0.02), "emit")
        B.light_strip((x + w * 0.1, fy - 0.032, h * 0.4), (0.03, 0.004, 0.03), "emit2")
        Dt.bolts(B, [(x - w * 0.14, h * 0.27), (x + w * 0.14, h * 0.27), (x - w * 0.14, h * 0.63), (x + w * 0.14, h * 0.63)],
                 fy - 0.03, 0.016)
    Dt.screen(B, w * 0.42, h * 0.45, 0.3, 0.2, fy, "emit", lines=2, rng=B.rng)
    B.box((0, fy - 0.01, 0.06), (w, 0.03, 0.12), "dark", "frame", 0.0)  # kick plate


def pillar(B, ch, w=0.8, h=6.0):
    B.zprism(outline(ch, w * 1.2, w * 1.2), 0.0, 0.35, "dark", "frame", 0.01)
    B.zprism(outline(ch, w * 1.15, w * 1.15), h - 0.3, h, "dark", "frame", 0.01)
    ts = 0.82 if ch == "civitas" else 1.0
    B.zprism(outline(ch, w, w), 0.35, h - 0.3, "frame", "frame", 0.0, top_scale=ts)
    n = int((h - 0.65) / 1.2)
    for k in range(n):
        z = 0.35 + (k + 0.5) * (h - 0.65) / n
        B.box((0, -w / 2 - 0.015, z), (w * 0.7, 0.03, (h - 0.65) / n - 0.1), "panel", "cover", 0.006)
    B.box((0, -w / 2 - 0.032, h / 2), (0.04, 0.006, h * 0.7), "internal", "greeble", 0.0)
    B.light_strip((0, -w / 2 - 0.036, h / 2 + 0.5), (0.012, 0.004, h * 0.3), "emit")
    Dt.bolts(B, [(x, 0.18) for x in (-w * 0.45, -w * 0.15, w * 0.15, w * 0.45)], -w * 0.6, 0.026)
    xc = w / 2 + 0.03
    B.cyl((xc, -w * 0.25, h / 2), 0.035, h - 0.8, "Z", 6, "trim", "greeble", 0.0)
    for zz in (0.8, h / 2, h - 0.8):
        B.box((xc - 0.02, -w * 0.25, zz), (0.07, 0.09, 0.06), "dark", "greeble", 0.0)


def catwalk(B, ch, w=4.0, d=1.2):
    """Raised walkway module: truss underside 0..0.5 m, deck 0.5..0.6 m, railing to 1.6 m."""
    for y in (-d / 2 + 0.05, d / 2 - 0.05):
        B.truss(-w / 2, w / 2, 0.0, 0.5, y, 0.04, 4, "frame", "frame")
    n = int(w / 0.5)
    for i in range(n):
        B.box((-w / 2 + (i + 0.5) * w / n, 0, 0.55), (w / n - 0.02, d, 0.05), "panel", "cover", 0.0)
    for y in (-d / 2 + 0.03, d / 2 - 0.03):
        for k in range(5):
            x = -w / 2 + 0.1 + k * (w - 0.2) / 4
            B.box((x, y, 1.1), (0.04, 0.04, 1.0), "trim", "frame", 0.0)
        B.box((0, y, 1.58), (w, 0.05, 0.05), "trim", "frame", 0.0)
        B.box((0, y, 1.1), (w, 0.03, 0.03), "trim", "frame", 0.0)
    B.light_strip((0, -d / 2 - 0.002, 0.55), (w * 0.96, 0.004, 0.015), "emit")
    B.cyl((0, 0.2, 0.32), 0.05, w, "X", 8, "cable", "cable", 0.0)
    for k in range(int(w / 0.12)):  # grating bars on the deck
        B.box((-w / 2 + (k + 0.5) * 0.12, 0, 0.578), (0.03, d - 0.12, 0.006), "dark", "greeble", 0.0)
    for y in (-d / 2 + 0.03, d / 2 - 0.03):
        B.box((0, y, 0.64), (w, 0.012, 0.08), "frame", "frame", 0.0)


def truss(B, ch, w=8.0, h=0.8, d=0.8):
    for y in (-d / 2 + 0.04, d / 2 - 0.04):
        B.truss(-w / 2, w / 2, 0.0, h, y, 0.05, 8, "frame", "frame")
    for k in range(9):
        x = -w / 2 + 0.05 + k * (w - 0.1) / 8
        B.box((x, 0, 0.03), (0.05, d, 0.05), "frame", "frame", 0.0)
        B.box((x, 0, h - 0.03), (0.05, d, 0.05), "frame", "frame", 0.0)
    for k in range(4):
        x = -w / 2 + (k + 0.5) * w / 4
        B.box((x, 0, -0.04), (0.6, 0.3, 0.06), "dark", "greeble", 0.0)
        B.light_strip((x, 0, -0.072), (0.5, 0.2, 0.004), "emit_white" if ch != "meridian" else "emit")
    B.cyl((0, 0.15, h * 0.5), 0.05, w, "X", 8, "cable", "cable", 0.0)


def massing(B, ch, w=6.0, h=8.0, d=4.0, tiers=3):
    """Mid-back facility block: stepped tiers, window bands, roof plant."""
    z = 0.0
    for t in range(tiers):
        th = h / tiers * (1.15 if t == 0 else 0.92)
        sc = 1.0 - 0.14 * t
        B.zprism(outline(ch, w * sc, d * sc, 0, 0, 0.08), z, z + th, "frame", "frame", 0.0)
        nb = max(1, int(th / 1.2))
        for k in range(nb):
            zz = z + (k + 0.6) * th / nb
            B.box((0, -d * sc / 2 - 0.01, zz), (w * sc * 0.86, 0.02, 0.3), "internal", "greeble", 0.0)
            if (k + t) % 2 == 0:
                B.light_strip((rng_off(t, k) * w * sc * 0.2, -d * sc / 2 - 0.022, zz), (w * sc * 0.5, 0.004, 0.08), "emit")
        B.box((0, 0, z + th + 0.06), (w * sc + 0.1, d * sc + 0.1, 0.12), "trim", "frame", 0.0)
        z += th + 0.12
    for k in range(3):
        x = (k - 1) * w * 0.22
        B.box((x, 0, z + 0.3), (w * 0.15, d * 0.3, 0.6), "dark", "greeble", 0.0)
        Dt.louvre(B, x, 0, w * 0.12, d * 0.24, z + 0.6, 4, "trim", "internal", normal="+Z")
    for k in range(5):  # vertical structural ribs on the front of the lowest tier
        x = (k - 2) * w * 0.2
        B.box((x, -d / 2 - 0.03, h * 0.19), (0.12, 0.06, h * 0.38), "dark", "frame", 0.0)
    B.cyl((w * 0.3, 0, z + 1.0), 0.05, 2.0, "Z", 6, "trim", "greeble", 0.0)


def rng_off(a, b):
    return math.sin(a * 2.3 + b * 1.7)


# ------------------------------------------------------------------------------------------------
# Statics (centred on the collision rectangle, depth 1.6)
# ------------------------------------------------------------------------------------------------
def static_ledge(B, ch, w, h, d=1.6):
    z0, z1 = -h / 2, h / 2
    B.xprism(outline(ch, d, h, 0, 0, 0.12), -w / 2, w / 2, "frame", "frame", 0.0)
    n = max(2, int(w / 0.5))
    for i in range(n):
        x = -w / 2 + (i + 0.5) * w / n
        B.box((x, 0, z1 + 0.0), (w / n - 0.02, d * 0.9, 0.012), "panel", "cover", 0.0)
    B.box((0, -d / 2 + 0.01, z1 - h * 0.25), (w * 0.98, 0.02, h * 0.18), "trim", "cover", 0.0)
    B.light_strip((0, -d / 2 - 0.002, z1 - h * 0.25), (w * 0.9, 0.004, 0.012), "emit")
    if ch == "nova_grid":
        B.hazard_band((0, -d / 2 + 0.004, z0 + h * 0.28), (w * 0.98, 0.008, h * 0.22), int(w * 5))


def static_plinth(B, ch, w, h, d=1.6):
    z0, z1 = -h / 2, h / 2
    B.zprism(outline(ch, w, d), z0, z0 + h * 0.2, "dark", "frame", 0.01)
    B.zprism(outline(ch, w * 0.9, d * 0.9), z0 + h * 0.2, z1 - h * 0.12, "frame", "frame", 0.0)
    B.zprism(outline(ch, w * 0.97, d * 0.97), z1 - h * 0.12, z1, "trim", "frame", 0.006)
    B.box((0, -d * 0.45 - 0.01, 0), (w * 0.7, 0.02, h * 0.4), "panel", "cover", 0.004)
    B.light_strip((0, -d * 0.45 - 0.022, -h * 0.05), (w * 0.5, 0.004, 0.012), "emit")


# ------------------------------------------------------------------------------------------------
# Props (bottom-centre)
# ------------------------------------------------------------------------------------------------
def prop_crates(B, ch, rng):
    sizes = [(1.2, 0.9, 0.8), (0.9, 0.8, 0.7), (0.7, 0.7, 0.55)]
    x = -0.9
    for i, (w, d, h) in enumerate(sizes[:2]):
        B.zprism(outline(ch, w, d, x + w / 2, 0, 0.08), 0.0, h, "panel", "frame", 0.01)
        B.box((x + w / 2, -d / 2 - 0.01, h * 0.5), (w * 0.8, 0.02, h * 0.12), "trim", "cover", 0.0)
        B.light_strip((x + w * 0.8, -d / 2 - 0.022, h * 0.8), (0.06, 0.004, 0.03), "emit" if i else "emit2")
        x += w + 0.06
    w, d, h = sizes[2]
    ob = B.zprism(outline(ch, w, d, -0.9 + 0.6, 0, 0.08), 0.8, 0.8 + h, "frame", "frame", 0.01)
    K.rotate(ob, 8, "Z", (-0.3, 0, 0))


def prop_pipes(B, ch, w=3.0):
    for k, (z, r) in enumerate(((0.45, 0.14), (0.8, 0.1), (1.05, 0.08))):
        B.cyl((0, -0.1 + 0.08 * k, z), r, w, "X", 12, "trim" if k != 1 else "panel", "frame", 0.0)
        for x in (-w / 2 + 0.2, w / 2 - 0.2):
            B.cyl((x, -0.1 + 0.08 * k, z), r * 1.18, 0.08, "X", 12, "dark", "greeble", 0.0)
    for x in (-w / 2 + 0.4, w / 2 - 0.4):
        B.box((x, 0, 0.6), (0.08, 0.4, 1.2), "frame", "frame", 0.0)
        B.box((x, 0, 0.03), (0.3, 0.5, 0.06), "dark", "frame", 0.0)
    B.box((0.3, -0.25, 0.8), (0.16, 0.06, 0.2), "frame", "greeble", 0.0)
    B.light_strip((0.3, -0.282, 0.84), (0.05, 0.004, 0.03), "emit2")


def prop_console(B, ch):
    B.zprism(outline(ch, 1.6, 0.7, 0, 0.05, 0.1), 0.0, 0.8, "frame", "frame", 0.0)
    ob = B.box((0, -0.15, 0.85), (1.5, 0.5, 0.06), "panel", "cover", 0.0)
    K.rotate(ob, -18, "X", (0, -0.15, 0.85))
    for k in range(3):
        x = (k - 1) * 0.52
        ob = B.box((x, 0.2, 1.15), (0.46, 0.04, 0.32), "dark", "frame", 0.0)
        ob2 = B.box((x, 0.175, 1.15), (0.4, 0.006, 0.26), "emit", "emit", 0.0)
        for o in (ob, ob2):
            K.rotate(o, -8, "X", (x, 0.2, 1.0))
    B.light_strip((0.6, -0.28, 0.4), (0.1, 0.004, 0.03), "emit2")


def prop_tank(B, ch, r=0.55, h=2.2):
    B.zprism(outline(ch, r * 2.4, r * 2.4), 0.0, 0.12, "dark", "frame", 0.01)
    B.lathe([(0, 0.12), (r, 0.12), (r, h - r * 0.4), (r * 0.6, h - 0.05), (0, h)], (0, 0, 0), 20, "panel", "frame")
    for z in (0.5, h * 0.55):
        B.ring((0, 0, z), r * 1.04, r * 0.98, 0.06, "Z", 20, "trim", "frame", 0.0)
    B.cyl((r * 0.7, -r * 0.7, h * 0.4), 0.04, h * 0.6, "Z", 8, "trim", "greeble", 0.0)
    B.light_strip((0, -r - 0.002, h * 0.35), (0.12, 0.004, 0.04), "emit")
