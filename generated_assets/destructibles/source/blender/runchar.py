"""Operative character: stylised hooded faceless operative (SV-01, shorter cape), rigid node rig the code
can drive like OperativeRig (torso, arm_weapon pivot at the shoulder rotating about Godot +Z,
weapon_socket, head with emissive visor, legs), node-TRS animations exported as glTF animations.
Usage: blender -b --factory-startup --python runchar.py -- [--no-render]
Axes: Blender X = Godot X (the operative faces +X), Blender -Y = Godot +Z (towards the camera), Z up.
A rotation of +a about Godot +Z is a rotation of -a about Blender Y."""
import sys, os, math, json, random
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import bpy, bmesh
from mathutils import Vector, Matrix, Euler
import tfjkit as K
import tfjpipe as P
import tfjrender as R
import tfjbuild as TB

argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
RENDER = "--no-render" not in argv
SID = "opr_chr_operative_a"
OUT = f"{TB.GA}/characters/shared/{SID}.glb"
FPS = 30

K.reset_scene()
K.set_ctx("operative", "suit", "cyan", "white")
B = K.Builder(SID, 7)
G = {}  # group name -> parts


def grp(name):
    start = len(B.parts)
    def done():
        G.setdefault(name, []).extend(B.parts[start:])
    return done


def limb(a, b, r0, r1, slot, verts=8):
    a, b = Vector(a), Vector(b)
    L = (b - a).length
    bm = bmesh.new()
    K.bm_cyl(bm, Vector((0, 0, 0)), r0, L, "Z", verts, 0.0, 1, r1)
    q = (b - a).normalized().to_track_quat("Z", "Y")
    bmesh.ops.transform(bm, matrix=Matrix.Translation((a + b) / 2) @ q.to_matrix().to_4x4(), verts=bm.verts)
    return B._new_obj(bm, "frame", None, [slot])


# ---------------------------------------------------------------- premium pass 2 (SV-01): smooth layered stylised suit
# Rounded forms throughout: the torso is a superellipse loft, limbs are bulged 12-sided lathes with ball
# joints, and every armour plate is a curved shell sampled from the body surface it sits on (offset,
# solidified, rim bevelled in two segments) so the suit reads as layered panels, not boxes.
def _se(c, p):
    return math.copysign(abs(c) ** (2.0 / p), c)


def _finish(bm, slot, role="cover", bevel=0.0, segs=2, angle=40, outward=None):
    bm.normal_update()
    if outward is not None and bm.faces:
        f = bm.faces[0]
        if f.normal.dot(outward(f.calc_center_median())) < 0:
            bmesh.ops.reverse_faces(bm, faces=bm.faces[:])
    if bevel > 0:
        K.bm_bevel_sharp(bm, bevel, segs, angle=angle)
    return B._new_obj(bm, role, None, [slot])


def loft(rings, n=16, slot="key", p=2.6, caps=True, solid=0.0, role="frame"):
    """Superellipse loft. rings [(z, cx, rx, ry)]; angle 0 faces +X (the operative's front)."""
    bm = bmesh.new()
    vs = []
    for (z, cx, rx, ry) in rings:
        vs.append([bm.verts.new((cx + rx * _se(math.cos(2 * math.pi * i / n), p),
                                 ry * _se(math.sin(2 * math.pi * i / n), p), z)) for i in range(n)])
    for j in range(len(rings) - 1):
        for i in range(n):
            bm.faces.new((vs[j][i], vs[j][(i + 1) % n], vs[j + 1][(i + 1) % n], vs[j + 1][i]))
    if caps:
        bm.faces.new(vs[0][::-1])
        bm.faces.new(vs[-1])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    if solid:
        bmesh.ops.solidify(bm, geom=bm.faces[:], thickness=solid)
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    return _finish(bm, slot, role)


def loft_F(rings, p=2.6):
    zs = [r[0] for r in rings]

    def ring(z):
        z = max(zs[0], min(zs[-1], z))
        for k in range(len(rings) - 1):
            if zs[k] <= z <= zs[k + 1]:
                t = (z - zs[k]) / max(1e-6, zs[k + 1] - zs[k])
                return [rings[k][i] * (1 - t) + rings[k + 1][i] * t for i in (1, 2, 3)]
        return list(rings[-1][1:])

    def F(u, v, off=0.0):  # u angle (rad), v height z
        cx, rx, ry = ring(v)
        c, s = math.cos(u), math.sin(u)
        x, y = rx * _se(c, p), ry * _se(s, p)
        n = Vector((math.copysign(abs(x / rx) ** (p - 1), x) / rx, math.copysign(abs(y / ry) ** (p - 1), y) / ry,
                    0.0)).normalized()
        return Vector((cx + x, y, v)) + n * off, n
    return F


def limb_F(a, b, r0, r1, ref=(1, 0, 0), bulge=0.07):
    a, b = Vector(a), Vector(b)
    d = (b - a).normalized()
    L = (b - a).length
    e1 = Vector(ref) - d * Vector(ref).dot(d)
    e1.normalize()
    e2 = d.cross(e1)

    def rad(t):
        return (r0 * (1 - t) + r1 * t) * (1.0 + bulge * math.sin(math.pi * min(1.0, t * 1.25)))

    def F(u, t, off=0.0):
        n = e1 * math.cos(u) + e2 * math.sin(u)
        return a + d * (L * t) + n * (rad(t) + off), n
    return F, rad


def sphere_F(c, radii):
    c, R = Vector(c), Vector(radii)

    def F(u, v, off=0.0):
        q = Vector((math.cos(v) * math.cos(u), math.cos(v) * math.sin(u), math.sin(v)))
        p = Vector((q.x * R.x, q.y * R.y, q.z * R.z))
        n = Vector((p.x / R.x ** 2, p.y / R.y ** 2, p.z / R.z ** 2)).normalized()
        return c + p + n * off, n
    return F


def patch(F, u0, u1, v0, v1, nu, nv, off=0.012, thick=0.01, slot="panel", bevel=0.004, vmap=None):
    """Curved armour shell over the surface F: outer face at `off`, a skirt dropping `thick` back towards
    the body (no hidden inner face, to save triangles) and one chamfer segment on the outer rim."""
    bm = bmesh.new()
    grid, nrm = [], []
    for j in range(nv + 1):
        row, nrow = [], []
        for i in range(nu + 1):
            u = u0 + (u1 - u0) * i / nu
            v = vmap(u, j / nv) if vmap else v0 + (v1 - v0) * j / nv
            pnt, n = F(u, v, off)
            row.append(bm.verts.new(pnt))
            nrow.append(n)
        grid.append(row)
        nrm.append(nrow)
    for j in range(nv):
        for i in range(nu):
            bm.faces.new((grid[j][i], grid[j][i + 1], grid[j + 1][i + 1], grid[j + 1][i]))
    bm.normal_update()
    um = (u0 + u1) / 2
    nc = F(um, vmap(um, 0.5) if vmap else (v0 + v1) / 2, off)[1]
    if sum((f.normal for f in bm.faces), Vector()).dot(nc) < 0:
        bmesh.ops.reverse_faces(bm, faces=bm.faces[:])
    nmap = {grid[j][i]: nrm[j][i] for j in range(nv + 1) for i in range(nu + 1)}
    rim = [e for e in bm.edges if e.is_boundary]
    res = bmesh.ops.extrude_edge_only(bm, edges=rim)
    for v in [g for g in res["geom"] if isinstance(g, bmesh.types.BMVert)]:
        src = next((e.other_vert(v) for e in v.link_edges if e.other_vert(v) in nmap), None)
        if src is not None:
            v.co = src.co - nmap[src] * thick
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    if bevel > 0:
        bmesh.ops.bevel(bm, geom=rim + list({v for e in rim for v in e.verts}), offset=bevel, segments=1,
                        profile=0.5, affect="EDGES", clamp_overlap=True)
    return B._new_obj(bm, "cover", None, [slot])


def limb(a, b, r0, r1, slot, verts=12, ref=(1, 0, 0), bulge=0.07, nt=5):
    F, rad = limb_F(a, b, r0, r1, ref, bulge)
    bm = bmesh.new()
    rows = []
    for j in range(nt + 1):
        t = j / nt
        rows.append([bm.verts.new(F(2 * math.pi * i / verts, t)[0]) for i in range(verts)])
    for j in range(nt):
        for i in range(verts):
            bm.faces.new((rows[j][i], rows[j][(i + 1) % verts], rows[j + 1][(i + 1) % verts], rows[j + 1][i]))
    bm.faces.new(rows[0][::-1])
    bm.faces.new(rows[-1])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    return _finish(bm, slot, "frame")


def joint(c, r, slot="key"):
    return B.uvsphere(tuple(c), r, 8, 5, slot, "frame")


def rbox(center, size, slot="accent", bevel=0.014):
    return B.box(center, size, slot, "cover", bevel, segs=1)


def strip_on(F, u, v, size, off=0.004):
    pnt, n = F(u, v, off)
    ob = B.light_strip(tuple(pnt), size, "emit")
    K.rotate(ob, math.degrees(math.atan2(n.y, n.x)), "Z", tuple(pnt))
    return ob


def strap(a, b, w=0.032, slot="rubber"):
    return B.strut(a, b, w, slot, "greeble")


def strap_path(pts, w=0.03, slot="rubber"):
    for p0, p1 in zip(pts, pts[1:]):
        strap(tuple(p0), tuple(p1), w, slot)


R_ = math.radians
HIP_Z, KNEE_Z, ANKLE_Z = 0.93, 0.5, 0.1
for side, sy in (("r", -1), ("l", 1)):
    y = sy * 0.1
    d = grp(f"leg_{side}")
    TH, _ = limb_F((0, y, HIP_Z), (0.012, y, KNEE_Z + 0.03), 0.094, 0.07)
    limb((0, y, HIP_Z), (0.012, y, KNEE_Z + 0.03), 0.094, 0.07, "key")                        # suit thigh
    patch(TH, R_(-55), R_(55), 0.14, 0.58, 4, 3, 0.014, 0.011, "panel")                       # thigh armour
    patch(TH, R_(-40), R_(40), 0.6, 0.78, 4, 1, 0.012, 0.009, "frame")                        # lower thigh layer
    strip_on(TH, R_(sy * 34), 0.36, (0.004, 0.008, 0.12), 0.026)
    rbox((0.0, y + sy * 0.1, HIP_Z - 0.15), (0.11, 0.05, 0.14), "accent")                     # thigh pouch
    strap((0.06, y + sy * 0.09, HIP_Z - 0.09), (-0.06, y + sy * 0.09, HIP_Z - 0.09), 0.018)
    strap((0.07, y + sy * 0.083, HIP_Z - 0.27), (-0.07, y + sy * 0.083, HIP_Z - 0.27), 0.016)
    d()
    d = grp(f"shin_{side}")
    SH_, _ = limb_F((0.012, y, KNEE_Z), (0.0, y, ANKLE_Z + 0.06), 0.072, 0.056, bulge=0.1)
    limb((0.012, y, KNEE_Z), (0.0, y, ANKLE_Z + 0.06), 0.072, 0.056, "key", bulge=0.1)
    KN = sphere_F((0.03, y, KNEE_Z + 0.01), (0.075, 0.08, 0.085))
    patch(KN, R_(-62), R_(62), R_(-45), R_(55), 4, 3, 0.004, 0.012, "panel")                   # knee guard
    B.light_strip((0.115, y, KNEE_Z - 0.015), (0.004, 0.045, 0.006), "emit")
    patch(SH_, R_(-58), R_(58), 0.2, 0.8, 4, 3, 0.012, 0.011, "panel")                        # shin guard
    strip_on(SH_, 0.0, 0.62, (0.004, 0.008, 0.07), 0.026)
    # boot: rounded tread sole, toe cap, ankle cuff and strap
    B.zprism(K.chamfer_rect(0.29, 0.135, 0.045, 0.05, y), 0.0, 0.035, "rubber", "frame", 0.0)
    B.zprism(K.chamfer_rect(0.26, 0.125, 0.05, 0.045, y), 0.035, 0.12, "dark", "frame", 0.006, top_scale=0.82)
    TOE = sphere_F((0.13, y, 0.04), (0.075, 0.068, 0.07))
    patch(TOE, R_(-70), R_(70), R_(0), R_(70), 4, 2, 0.002, 0.01, "panel")
    B.zprism(K.chamfer_rect(0.14, 0.135, 0.045, 0.0, y), 0.12, 0.2, "dark", "frame", 0.0)
    strap((0.07, y - 0.07, 0.15), (0.07, y + 0.07, 0.15), 0.02, "frame")
    d()

# ---------------------------------------------------------------- torso
TR = [(0.84, 0.0, 0.118, 0.162), (0.93, 0.0, 0.118, 0.158), (1.03, 0.0, 0.11, 0.148), (1.13, 0.005, 0.124, 0.172),
      (1.25, 0.01, 0.14, 0.2), (1.35, 0.005, 0.138, 0.212), (1.42, -0.005, 0.118, 0.2), (1.47, -0.01, 0.075, 0.11)]
T = loft_F(TR)
d = grp("torso")
loft(TR, 16, "key")                                                                          # suit torso
for sy in (-1, 1):
    u0, u1 = sorted((R_(sy * 6), R_(sy * 64)))
    patch(T, u0, u1, 1.23, 1.43, 4, 3, 0.016, 0.012, "panel")                                 # chest plates
    strip_on(T, R_(sy * 36), 1.36, (0.004, 0.07, 0.01), 0.03)
    if sy < 0:  # camera side only (the far side is hidden by the arm in every clip)
        patch(T, R_(-118), R_(-72), 1.17, 1.38, 2, 3, 0.014, 0.011, "panel")                  # side plate
        patch(T, R_(-75), R_(-40), 1.05, 1.18, 2, 2, 0.012, 0.009, "frame")                   # flank layer
strip_on(T, R_(-96), 1.33, (0.004, 0.08, 0.01), 0.028)
patch(T, R_(-12), R_(12), 1.15, 1.25, 2, 2, 0.02, 0.012, "frame")                            # sternum plate
for k in range(2):                                                                           # segmented abdomen
    patch(T, R_(-42), R_(42), 1.02 + k * 0.056, 1.034 + k * 0.052, 4, 1, 0.01, 0.008, "frame")
patch(T, R_(140), R_(220), 1.12, 1.41, 4, 3, 0.016, 0.012, "panel")                          # back plate
rbox((-0.165, 0, 1.1), (0.06, 0.17, 0.13), "accent", 0.016)                                   # back pack
B.light_strip((-0.196, 0, 1.12), (0.004, 0.08, 0.008), "emit")
for sy in (-1, 1):                                                                           # cross straps over the plates
    pts = [T(R_(sy * 58), 1.44, 0.03)[0], T(R_(sy * 24), 1.3, 0.034)[0], T(R_(-sy * 10), 1.19, 0.03)[0],
           T(R_(-sy * 38), 1.06, 0.022)[0]]
    strap_path(pts, 0.03)
B.box(tuple(T(0.0, 1.245, 0.038)[0]), (0.02, 0.05, 0.05), "trim", "greeble", 0.004)
# belt, buckle, pouches
loft([(0.915, 0.0, 0.132, 0.174), (0.99, 0.0, 0.13, 0.17)], 14, "rubber")
B.box(tuple(T(0.0, 0.952, 0.02)[0]), (0.02, 0.08, 0.055), "trim", "greeble", 0.004)
for sy, x in ((-1, 0.07), (-1, -0.05), (1, 0.07), (1, -0.05)):
    rbox((x, sy * 0.185, HIP_Z - 0.01), (0.08, 0.05, 0.1), "accent")
# cowl and scarf: a soft cloth loft around the neck and a V drape onto the chest
loft([(1.36, -0.005, 0.158, 0.218), (1.42, -0.012, 0.168, 0.226), (1.49, -0.012, 0.12, 0.14),
      (1.545, -0.006, 0.085, 0.095)], 14, "cloth", p=2.2, caps=False, solid=0.022)
CW = loft_F([(1.3, -0.005, 0.15, 0.215), (1.47, -0.012, 0.165, 0.222)], p=2.2)
patch(CW, R_(-50), R_(50), 0, 0, 5, 2, 0.012, 0.016, "cloth", 0.006,
      vmap=lambda u, t: 1.47 - t * (0.15 - 0.09 * abs(u) / R_(50)))
d()

# ---------------------------------------------------------------- head: faceless visor helmet inside a deep hood
NECK = Vector((0.0, 0.0, 1.48))
d = grp("head")
B.cyl((0.0, 0, 1.53), 0.052, 0.08, "Z", 10, "dark", "frame", 0.0)
B.uvsphere((0.015, 0, 1.645), 0.112, 12, 8, "dark", "frame", (1.0, 0.9, 1.12))               # helmet
B.uvsphere((0.075, 0, 1.635), 0.082, 12, 6, "visor", "frame", (0.72, 0.98, 0.98))               # glossy faceplate
for sy in (-1, 1):  # angled cyan eye slits
    ob = B.light_strip((0.13, sy * 0.034, 1.652), (0.008, 0.03, 0.006), "emit")
    K.rotate(ob, sy * 18, "X", (0.13, sy * 0.034, 1.652))
B.box((0.124, 0, 1.6), (0.012, 0.03, 0.006), "frame", "greeble", 0.002)
d()
d = grp("hood")
hood = B.uvsphere((-0.02, 0, 1.672), 0.148, 14, 10, "cloth", "frame", (1.08, 1.0, 1.14))
bmh = bmesh.new()
bmh.from_mesh(hood.data)
bmesh.ops.delete(bmh, geom=[v for v in bmh.verts if v.co.x > 0.06 and 1.53 < v.co.z < 1.78], context="VERTS")
for v in bmh.verts:  # soft cloth: drape onto the shoulders, deepen the opening, soft peak and folds
    if v.co.z < 1.66:
        t = (1.66 - v.co.z) / 0.16
        v.co.z -= 0.1 * t
        v.co.y *= 1.0 + 0.3 * t
        if v.co.x < 0.02:
            v.co.x -= 0.035 * t
    if v.co.x < -0.05 and v.co.z > 1.72:
        v.co.x -= 0.04 * (v.co.z - 1.72) / 0.12
        v.co.z += 0.02 * (v.co.z - 1.72) / 0.12
    if v.co.z > 1.74 and v.co.x > -0.04:   # the brow comes forward into a soft point over the visor
        k = min(1.0, (v.co.z - 1.74) / 0.07) * min(1.0, (v.co.x + 0.04) / 0.1)
        v.co.x += 0.055 * k
        v.co.z -= 0.025 * k
    ang = math.atan2(v.co.y, v.co.x + 0.02)
    if v.co.z < 1.72:                       # loose vertical folds, stronger towards the shoulders
        f = 0.007 * math.sin(ang * 7.0) * min(1.0, (1.72 - v.co.z) / 0.12)
        v.co.x += f * math.cos(ang)
        v.co.y += f * math.sin(ang)
bmesh.ops.recalc_face_normals(bmh, faces=bmh.faces[:])
bmesh.ops.solidify(bmh, geom=bmh.faces[:], thickness=0.016)
bmesh.ops.recalc_face_normals(bmh, faces=bmh.faces[:])
K.bm_bevel_sharp(bmh, 0.005, 1, angle=60)                                                     # rolled rim
bmh.to_mesh(hood.data)
bmh.free()
d()

# ---------------------------------------------------------------- weapon arm (right, camera side), rest = aiming along +X
SH_R = Vector((0.0, -0.25, 1.4))
EL_R = SH_R + Vector((0.2, 0, -0.2))
HAND_R = EL_R + Vector((0.29, 0, -0.03))
SH_L = Vector((0.0, 0.25, 1.4))
EL_L = SH_L + Vector((0.2, -0.1, -0.2))


def arm(sh, el, sy, upper_name, fore_name, fore_vec, hand_off):
    d = grp(upper_name)
    joint(sh, 0.07)
    P1 = sphere_F(sh + Vector((0, sy * 0.005, 0.0)), (0.098, 0.095, 0.098))
    u0, u1 = sorted((R_(sy * 30), R_(sy * 150)))
    patch(P1, u0, u1, R_(-5), R_(80), 4, 3, 0.004, 0.014, "panel")                           # pauldron
    P2 = sphere_F(sh + Vector((0, sy * 0.01, -0.035)), (0.11, 0.105, 0.085))
    u0, u1 = sorted((R_(sy * 40), R_(sy * 140)))
    patch(P2, u0, u1, R_(-25), R_(20), 4, 1, 0.004, 0.012, "frame")                          # lower layer
    strip_on(P1, R_(sy * 62), R_(18), (0.004, 0.03, 0.03), 0.02)
    UA, _ = limb_F(sh, el, 0.066, 0.056, ref=(0, sy, 0))
    limb(sh, el, 0.066, 0.056, "key", ref=(0, sy, 0), nt=4)
    patch(UA, R_(-50), R_(50), 0.35, 0.82, 3, 2, 0.012, 0.01, "panel")                        # bicep plate
    d()
    d = grp(fore_name)
    joint(el, 0.058)
    fe = el + fore_vec
    FA, _ = limb_F(el, fe, 0.056, 0.046, ref=(0, sy, 0), bulge=0.12)
    limb(el, fe, 0.056, 0.046, "key", ref=(0, sy, 0), bulge=0.12, nt=4)
    patch(FA, R_(-80), R_(80), 0.12, 0.78, 5, 2, 0.012, 0.012, "panel")                       # bracer
    patch(FA, R_(-30), R_(30), 0.2, 0.62, 1, 2, 0.026, 0.006, "frame")                        # bracer inlay
    strip_on(FA, 0.0, 0.42, (0.09, 0.004, 0.008), 0.034) if False else None
    pnt, n = FA(0.0, 0.42, 0.034)
    B.light_strip(tuple(pnt), (0.1, 0.004, 0.008) if abs(fore_vec.x) > abs(fore_vec.y) else (0.008, 0.1, 0.008), "emit")
    hc = el + hand_off
    rbox(tuple(hc), (0.09, 0.08, 0.085), "rubber", 0.026)                                     # glove
    rbox(tuple(hc + Vector((0.025, sy * 0.036, 0.01))), (0.05, 0.016, 0.06), "frame", 0.006)  # knuckle plate
    d()


arm(SH_R, EL_R, -1, "arm_weapon", "forearm_weapon", Vector((0.25, 0, 0)), Vector((0.29, 0, -0.01)))
arm(SH_L, EL_L, 1, "arm_support", "forearm_support", Vector((0.25, -0.13, 0.0)), Vector((0.28, -0.15, 0.0)))


# ---------------------------------------------------------------- short flowing cloth cape (skinned to a 3 x 3 bone grid)
def cape_mesh():
    bm = bmesh.new()
    rows, cols = 10, 12
    vs = []
    for j in range(rows + 1):
        t = j / rows
        z = 1.45 - t * 0.82                                  # shoulders to just above the knee
        row = []
        for i in range(cols + 1):
            u = i / cols
            yy = (u - 0.5) * (0.42 + 0.26 * t)
            xx = -0.16 - 0.13 * t ** 1.3 - 0.06 * math.cos((u - 0.5) * math.pi) * (0.3 + t)   # flares back
            xx -= 0.022 * (0.5 + 0.5 * math.sin(u * math.pi * 6.0 + 0.6)) * t ** 1.2   # soft vertical folds
            hem = 0.0
            if j == rows:   # pointed, uneven hem: lower at the centre, lifted at the corners
                hem = -0.07 * (1.0 - abs(u - 0.5) * 2.0) + 0.012 * math.sin(i * 2.3 + 0.5) + 0.02
            row.append(bm.verts.new((xx, yy, z + hem * t)))
        vs.append(row)
    for j in range(rows):
        for i in range(cols):
            bm.faces.new((vs[j][i], vs[j][i + 1], vs[j + 1][i + 1], vs[j + 1][i]))
    bmesh.ops.solidify(bm, geom=bm.faces[:], thickness=0.012)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    return B._new_obj(bm, "frame", "cape_mesh", ["cloth"])


CAPE_PART = cape_mesh()

# ---------------------------------------------------------------- pack groups into nodes
PIVOTS = {
    "hips": Vector((0, 0, HIP_Z)),
    "torso": Vector((0, 0, HIP_Z + 0.05)),
    "head": NECK, "hood": NECK,
    "arm_weapon": SH_R, "forearm_weapon": EL_R,
    "arm_support": SH_L, "forearm_support": EL_L,
    "leg_r": Vector((0, -0.1, HIP_Z)), "shin_r": Vector((0.01, -0.1, KNEE_Z)),
    "leg_l": Vector((0, 0.1, HIP_Z)), "shin_l": Vector((0.01, 0.1, KNEE_Z)),
}
PARENT = {"torso": "hips", "head": "torso", "hood": "head", "arm_weapon": "torso", "forearm_weapon": "arm_weapon",
          "arm_support": "torso", "forearm_support": "arm_support", "leg_r": "hips", "shin_r": "leg_r",
          "leg_l": "hips", "shin_l": "shin_l" if False else "leg_l"}

NODES = {}
root = bpy.data.objects.new(SID, None)
bpy.context.scene.collection.objects.link(root)
hips = bpy.data.objects.new("hips", None)
bpy.context.scene.collection.objects.link(hips)
hips.parent = root
hips.location = PIVOTS["hips"]
NODES["hips"] = hips
total = 0
for name in ("torso", "head", "hood", "arm_weapon", "forearm_weapon", "arm_support", "forearm_support",
             "leg_r", "shin_r", "leg_l", "shin_l"):
    ob = P.pack(G[name], name, ao=(name != "hood"), smooth_angle=(70 if name == "hood" else 42))
    total += K.tri_count(ob)
    print("GROUP_TRIS", name, K.tri_count(ob))
    ob.data.transform(Matrix.Translation(-PIVOTS[name]))
    par = PARENT[name]
    ob.parent = NODES[par]
    ob.location = PIVOTS[name] - PIVOTS[par]
    NODES[name] = ob
for c in bpy.data.collections:
    c.hide_render = True
    c.hide_viewport = True
sock = bpy.data.objects.new("weapon_socket", None)
bpy.context.scene.collection.objects.link(sock)
sock.parent = NODES["forearm_weapon"]
sock.location = HAND_R - EL_R
NODES["weapon_socket"] = sock

# cape: skinned cloth on a 3 x 3 bone grid under cape_root, the rig parented to the torso node
cape = P.pack([CAPE_PART], "cape", smooth_angle=75)
arm_d = bpy.data.armatures.new("cape_rig")
rig = bpy.data.objects.new("cape_rig", arm_d)
bpy.context.scene.collection.objects.link(rig)
bpy.context.view_layer.objects.active = rig
bpy.ops.object.mode_set(mode="EDIT")
eb = arm_d.edit_bones
rootb = eb.new("cape_root")
rootb.head, rootb.tail = Vector((-0.17, 0, 1.47)), Vector((-0.17, 0, 1.42))
CHAIN_Y = (-0.2, 0.0, 0.2)
CHAIN_Z = (1.42, 1.15, 0.9, 0.62)
for ci, cy in enumerate(CHAIN_Y):
    par = rootb
    for k in range(3):
        b = eb.new(f"cape_{ci}_{k}")
        t0, t1 = k / 3, (k + 1) / 3
        b.head = Vector((-0.17 - 0.08 * t0 - 0.04 * abs(cy), cy * (1 + 0.6 * t0), CHAIN_Z[k]))
        b.tail = Vector((-0.17 - 0.08 * t1 - 0.04 * abs(cy), cy * (1 + 0.6 * t1), CHAIN_Z[k + 1]))
        b.parent = par
        b.use_connect = k > 0
        par = b
bpy.ops.object.mode_set(mode="OBJECT")
groups = {n: cape.vertex_groups.new(name=n) for n in [b.name for b in arm_d.bones]}
for v in cape.data.vertices:
    co = v.co
    span = (co.y / (0.21 + 0.13 * max(0.0, (1.45 - co.z) / 0.82)))  # -1 .. 1 across the cape
    fy = (max(-1.0, min(1.0, span)) + 1.0)  # 0 .. 2
    c0 = min(1, int(fy))
    wy1 = fy - c0
    tz = max(0.0, min(2.999, (1.42 - co.z) / (1.42 - 0.62) * 3.0))
    k0 = int(tz)
    wz1 = tz - k0
    k1 = min(2, k0 + 1)
    top = max(0.0, 1.0 - (1.45 - co.z) / 0.08)
    if top > 0:
        groups["cape_root"].add([v.index], top, "ADD")
    for ci, wy in ((c0, 1.0 - wy1), (c0 + 1, wy1)):
        for kk, wz in ((k0, 1.0 - wz1), (k1, wz1)):
            w = wy * wz * (1.0 - top)
            if w > 0.001:
                groups[f"cape_{ci}_{kk}"].add([v.index], w, "ADD")
cape.parent = rig
mod = cape.modifiers.new("skin", "ARMATURE")
mod.object = rig
rig.parent = NODES["torso"]
rig.matrix_parent_inverse = NODES["torso"].matrix_world.inverted()
NODES["cape_rig"] = rig
CAPE_BONES = [b.name for b in arm_d.bones if b.name != "cape_root"]
total += K.tri_count(cape)
print("TRIS", total)
if os.environ.get("TFJ_COUNT_ONLY"):
    sys.stdout.flush()
    os._exit(0)

# ---------------------------------------------------------------- animation
sc = bpy.context.scene
sc.render.fps = FPS
GZ = lambda deg: (0.0, math.radians(-deg), 0.0)  # rotation about Godot +Z (aim in the screen plane)


def key(node, frame, rot=None, loc=None, scl=None):
    ob = NODES[node]
    if rot is not None:
        ob.rotation_euler = Euler(rot)
        ob.keyframe_insert("rotation_euler", frame=frame)
    if loc is not None:
        ob.location = loc
        ob.keyframe_insert("location", frame=frame)
    if scl is not None:
        ob.scale = scl
        ob.keyframe_insert("scale", frame=frame)


def rot(gz=0.0, gx=0.0, gy=0.0):
    """Euler in Blender terms from Godot-axis degrees: gz = about Godot Z (Blender -Y), gx = Godot X
    (Blender X), gy = Godot Y (Blender Z)."""
    return (math.radians(gx), math.radians(-gz), math.radians(gy))


REST = {n: (NODES[n].location.copy()) for n in NODES}
POSES = {
    # node: (gz rotation) relative to rest; arm rest = aiming straight along +X
    "relaxed": {"arm_weapon": -50, "forearm_weapon": -10, "arm_support": -45, "forearm_support": -25, "torso": 0, "head": 0},
    "ready": {"arm_weapon": -24, "forearm_weapon": -4, "arm_support": -20, "forearm_support": -6, "torso": -2, "head": -4},
    "aim": {"arm_weapon": 0, "forearm_weapon": 0, "arm_support": 0, "forearm_support": 0, "torso": -4, "head": 2},
}


def pose(frame, p, extra=None, hips_dz=0.0, leg=(0, 0), shin=(0, 0)):
    q = dict(POSES[p]) if isinstance(p, str) else dict(p)
    if extra:
        q.update(extra)
    for n in ("arm_weapon", "forearm_weapon", "arm_support", "forearm_support", "torso", "head"):
        key(n, frame, rot=rot(q.get(n, 0.0)))
    key("hips", frame, loc=REST["hips"] + Vector((0, 0, hips_dz)), rot=(0.0, 0.0, 0.0))
    key("torso", frame, scl=(1.0, 1.0, 1.0))
    key("leg_r", frame, rot=rot(leg[0]))
    key("leg_l", frame, rot=rot(leg[1]))
    key("shin_r", frame, rot=rot(shin[0]))
    key("shin_l", frame, rot=rot(shin[1]))


ANIMS = {}


CAPE_MOTION = {  # clip -> (amplitude deg, cycles over the clip, back-lift deg)
    "idle": (2.0, 1, 0.0), "ready": (2.5, 1, 2.0), "aim_pose": (2.0, 1, 3.0), "fire_recoil": (6.0, 1, 4.0),
    "reload": (3.0, 1, 2.0), "weapon_switch": (4.0, 1, 2.0), "victory": (3.0, 2, 0.0), "defeat": (5.0, 1, -6.0),
    "reposition": (8.0, 2, 12.0),
}


def cape_keys(name, frames, loop):
    amp, cyc, lift = CAPE_MOTION.get(name, (2.0, 1, 0.0))
    step = 3 if frames <= 25 else 5
    fr = list(range(1, frames + 1, step))
    if fr[-1] != frames:
        fr.append(frames)
    for pb in rig.pose.bones:
        pb.rotation_mode = "XYZ"
    for f in fr:
        t = (f - 1) / max(1, frames - 1)
        for bn in CAPE_BONES:
            ci, k = int(bn.split("_")[1]), int(bn.split("_")[2])
            ph = 2 * math.pi * cyc * t - k * 0.9 - ci * 0.5
            env = 1.0 if loop else math.sin(math.pi * t) ** 0.7
            a = math.radians(amp * (0.5 + 0.5 * k) * math.sin(ph) * env + lift * (k + 1) / 3 * (env if not loop else 1.0))
            tw = math.radians(amp * 0.4 * math.sin(ph + 1.3) * env)
            pb = rig.pose.bones[bn]
            pb.rotation_euler = (a, 0.0, tw)
            pb.keyframe_insert("rotation_euler", frame=f)


def anim(name, frames, loop, fn):
    for ob in NODES.values():
        if ob.animation_data:
            ob.animation_data.action = None
    fn()
    cape_keys(name, frames, loop)
    actions = []
    for n, ob in NODES.items():
        ad = ob.animation_data
        if ad and ad.action:
            act = ad.action
            act.name = f"{name}__{n}"
            tr = ad.nla_tracks.new()
            tr.name = name
            st = tr.strips.new(name, 1, act)
            ad.action = None
            actions.append(act)
    ANIMS[name] = dict(frames=frames, loop=loop, seconds=round((frames - 1) / FPS, 3))


def a_idle():
    for f, b in ((1, 0.0), (31, 1.0), (61, 0.0)):
        pose(f, "relaxed", {"torso": -1.0 * b, "head": 1.5 * b, "arm_weapon": -50 + 2 * b}, hips_dz=-0.006 * b)
        key("torso", f, scl=(1.0, 1.0 + 0.012 * b, 1.0 + 0.006 * b))


def a_ready():
    for f, b in ((1, 0.0), (21, 1.0), (41, 0.0)):
        pose(f, "ready", {"arm_weapon": -24 + 1.5 * b, "torso": -2 - 0.8 * b}, hips_dz=-0.03 - 0.008 * b, leg=(6, -6), shin=(-6, -4))


def a_aim():
    for f, b in ((1, 0.0), (16, 1.0), (31, 0.0)):
        pose(f, "aim", {"arm_weapon": 0.4 * b, "torso": -4 - 0.5 * b}, hips_dz=-0.04, leg=(8, -8), shin=(-8, -5))


def a_fire():
    pose(1, "aim", hips_dz=-0.04, leg=(8, -8), shin=(-8, -5))
    pose(3, "aim", {"arm_weapon": 6, "forearm_weapon": 3, "torso": -1, "head": 3}, hips_dz=-0.035, leg=(8, -8), shin=(-8, -5))
    pose(7, "aim", {"arm_weapon": 3, "forearm_weapon": 1, "torso": -3}, hips_dz=-0.04, leg=(8, -8), shin=(-8, -5))
    pose(13, "aim", hips_dz=-0.04, leg=(8, -8), shin=(-8, -5))


def a_reload():
    pose(1, "aim", hips_dz=-0.04, leg=(8, -8), shin=(-8, -5))
    pose(8, "ready", {"arm_weapon": -40, "forearm_weapon": 20, "arm_support": -50, "forearm_support": 30}, hips_dz=-0.04, leg=(8, -8), shin=(-8, -5))
    pose(18, "ready", {"arm_weapon": -42, "forearm_weapon": 24, "arm_support": -38, "forearm_support": 45, "head": -10}, hips_dz=-0.04, leg=(8, -8), shin=(-8, -5))
    pose(26, "ready", {"arm_weapon": -36, "forearm_weapon": 18, "arm_support": -48, "forearm_support": 25, "head": -6}, hips_dz=-0.04, leg=(8, -8), shin=(-8, -5))
    pose(37, "aim", hips_dz=-0.04, leg=(8, -8), shin=(-8, -5))


def a_switch():
    pose(1, "aim", hips_dz=-0.04, leg=(8, -8), shin=(-8, -5))
    pose(9, "relaxed", {"arm_weapon": -80, "forearm_weapon": -5, "torso": -3}, hips_dz=-0.04, leg=(8, -8), shin=(-8, -5))
    pose(15, "relaxed", {"arm_weapon": -82, "forearm_weapon": -8, "torso": -3}, hips_dz=-0.04, leg=(8, -8), shin=(-8, -5))
    pose(25, "aim", hips_dz=-0.04, leg=(8, -8), shin=(-8, -5))


def a_victory():
    pose(1, "ready", hips_dz=-0.03, leg=(6, -6), shin=(-6, -4))
    pose(14, "relaxed", {"arm_weapon": -70, "torso": 3, "head": 8}, hips_dz=0.0)
    pose(30, "relaxed", {"arm_weapon": -72, "torso": 4, "head": 10, "arm_support": -70}, hips_dz=0.005)
    pose(61, "relaxed", {"arm_weapon": -70, "torso": 3, "head": 6, "arm_support": -66}, hips_dz=0.0)


def a_defeat():
    pose(1, "ready", hips_dz=-0.03, leg=(6, -6), shin=(-6, -4))
    pose(14, "relaxed", {"arm_weapon": -80, "torso": -14, "head": -18}, hips_dz=-0.18, leg=(30, -10), shin=(-60, -30))
    pose(30, "relaxed", {"arm_weapon": -86, "forearm_weapon": -4, "torso": -24, "head": -28, "arm_support": -80},
         hips_dz=-0.36, leg=(62, -5), shin=(-118, -80))
    pose(49, "relaxed", {"arm_weapon": -86, "forearm_weapon": -4, "torso": -26, "head": -30, "arm_support": -82},
         hips_dz=-0.37, leg=(62, -5), shin=(-118, -80))


def a_reposition():
    for f, s in ((1, 1), (7, 0), (13, -1), (19, 0), (25, 1)):
        pose(f, "ready", {"torso": -4}, hips_dz=-0.03 - 0.02 * abs(s) + 0.01, leg=(18 * s, -18 * s),
             shin=(-12 if s < 0 else -28 * abs(s), -12 if s > 0 else -28 * abs(s)))


anim("idle", 61, True, a_idle)
anim("ready", 41, True, a_ready)
anim("aim_pose", 31, True, a_aim)
anim("fire_recoil", 13, False, a_fire)
anim("reload", 37, False, a_reload)
anim("weapon_switch", 25, False, a_switch)
anim("victory", 61, False, a_victory)
anim("defeat", 49, False, a_defeat)
anim("reposition", 25, True, a_reposition)
for ob in NODES.values():
    ob.rotation_euler = (0, 0, 0)
for pb in rig.pose.bones:
    pb.rotation_euler = (0, 0, 0)
NODES["hips"].location = REST["hips"]
sc.frame_start, sc.frame_end = 1, 61
sc.frame_set(1)

objs = [root] + list(NODES.values()) + [cape]
K.CTX["baking"] = True
K.materialise(objs)  # textured zone slots (Blender side only), then one baked 1024 set (contract 11)
import tfjbake


def _detail_bump(m, kind):
    """Bake-time normal detail (self bake): suit panel seams on the key suit, soft creases on cloth.
    A Bump node in object space chained after the library normal map, so it lands in the baked normal."""
    nt = m.node_tree
    bsdf = next((n for n in nt.nodes if n.type == "BSDF_PRINCIPLED"), None)
    if bsdf is None:
        return
    tc = nt.nodes.new("ShaderNodeTexCoord")
    bump = nt.nodes.new("ShaderNodeBump")
    prev = bsdf.inputs["Normal"].links[0].from_socket if bsdf.inputs["Normal"].links else None
    if prev is not None:
        nt.links.new(prev, bump.inputs["Normal"])
    if kind == "suit":
        tex = nt.nodes.new("ShaderNodeTexBrick")
        tex.inputs["Scale"].default_value = 7.0
        tex.inputs["Mortar Size"].default_value = 0.012
        tex.inputs["Mortar Smooth"].default_value = 0.4
        tex.offset = 0.5
        tex.squash = 1.6
        nt.links.new(tc.outputs["Object"], tex.inputs["Vector"])
        nt.links.new(tex.outputs["Fac"], bump.inputs["Height"])
        bump.inputs["Strength"].default_value = 0.55
        bump.inputs["Distance"].default_value = 0.004
    else:
        tex = nt.nodes.new("ShaderNodeTexNoise")   # soft irregular creases, no banding
        tex.inputs["Scale"].default_value = 5.0
        tex.inputs["Detail"].default_value = 3.0
        tex.inputs["Roughness"].default_value = 0.45
        nt.links.new(tc.outputs["Object"], tex.inputs["Vector"])
        nt.links.new(tex.outputs["Fac"], bump.inputs["Height"])
        bump.inputs["Strength"].default_value = 0.22
        bump.inputs["Distance"].default_value = 0.006
    nt.links.new(bump.outputs["Normal"], bsdf.inputs["Normal"])
    print("DETAIL_BUMP", m.name, kind)


for m in bpy.data.materials:
    if m.get("tfj_kind") == "zone" and m.use_nodes:
        if m.get("tfj_zone") == "key":
            _detail_bump(m, "suit")
        elif m.get("tfj_zone") == "cloth":
            _detail_bump(m, "cloth")
mesh_nodes = [o for o in objs if o.type == "MESH"]
for pb in rig.pose.bones:
    pb.rotation_euler = (0, 0, 0)
cape.modifiers["skin"].show_viewport = False
cape.modifiers["skin"].show_render = False
tfjbake.bake(mesh_nodes, SID, 1024, high_bevel=0.003, cage=0.008, emit_strength=1.6, slot="chr_operative_a",
             samples=16, ao_mix=0.5, use_high=False)
cape.modifiers["skin"].show_viewport = True
cape.modifiers["skin"].show_render = True
for o in bpy.context.view_layer.objects:
    o.select_set(False)
for o in objs:
    o.select_set(True)
bpy.context.view_layer.objects.active = root
os.makedirs(os.path.dirname(OUT), exist_ok=True)
bpy.ops.export_scene.gltf(filepath=OUT, export_format="GLB", use_selection=True, export_apply=True, export_yup=True,
                          export_texcoords=True, export_normals=True, export_materials="EXPORT",
                          export_vertex_color="NONE", export_all_vertex_colors=False,
                          export_active_vertex_color_when_no_material=False, export_animations=True,
                          export_animation_mode="NLA_TRACKS", export_force_sampling=True, export_frame_step=1,
                          export_anim_slide_to_zero=True, export_optimize_animation_size=False, export_skins=True,
                          export_optimize_animation_keep_anim_object=True,
                          export_extras=False, export_cameras=False, export_lights=False)
size = os.path.getsize(OUT)
stats = dict(id="OPR-CHR-OPERATIVE-A", file=OUT, tris=dict(intact=total), bytes=size, animations=ANIMS,
             nodes=sorted(NODES.keys()), materials=sorted({m.name for o in NODES.values() if o.type == "MESH" for m in o.data.materials}))
json.dump(stats, open("/workspace/tfj-masters/3d-kits/stats_char.json", "w"), indent=1)
print("EXPORTED", OUT, size, total)

if RENDER:
    TB.preview_materials()
    tiles = []
    poses = [("rest_aim", None), ("idle", ("idle", 31)), ("ready", ("ready", 1)), ("fire_recoil", ("fire_recoil", 3)),
             ("reload", ("reload", 18)), ("victory", ("victory", 30)), ("defeat", ("defeat", 30)), ("reposition", ("reposition", 7))]
    cam = R.setup((420, 420), int(os.environ.get("TFJ_SAMPLES", "32")), floor=True, floor_z=0.0)
    meshes = [o for o in NODES.values() if o.type == "MESH"] + [cape]
    for label, pa in poses:
        for o in NODES.values():
            if o.animation_data:
                for t in o.animation_data.nla_tracks:
                    t.mute = True
                    t.is_solo = False
        if pa:
            for o in NODES.values():
                if o.animation_data:
                    for t in o.animation_data.nla_tracks:
                        t.mute = t.name != pa[0]
            sc.frame_set(pa[1])
        else:
            for o in NODES.values():
                o.rotation_euler = (0, 0, 0)
            NODES["hips"].location = REST["hips"]
            sc.frame_set(1) if False else None
        bpy.context.view_layer.update()
        R.frame(meshes, cam, 1.12)
        p = f"/tmp/tfj_tiles/{SID}_{label}.png"
        R.render(p)
        tiles.append(p)
    stats["tiles"] = tiles
    json.dump(stats, open("/workspace/tfj-masters/3d-kits/stats_char.json", "w"), indent=1)
