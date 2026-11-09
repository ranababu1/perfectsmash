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


# ---------------------------------------------------------------- legs (thigh + shin + boot per side)
HIP_Z, KNEE_Z, ANKLE_Z = 0.93, 0.5, 0.1
for side, sy in (("r", -1), ("l", 1)):
    y = sy * 0.1
    d = grp(f"leg_{side}")
    limb((0, y, HIP_Z), (0.01, y, KNEE_Z + 0.03), 0.092, 0.068, "frame")
    B.box((0.05, y, HIP_Z - 0.2), (0.06, 0.13, 0.2), "panel", "cover", 0.012)  # thigh plate
    B.box((0.0, y + sy * 0.09, HIP_Z - 0.12), (0.11, 0.04, 0.13), "accent", "cover", 0.008)  # holster pouch
    d()
    d = grp(f"shin_{side}")
    limb((0.01, y, KNEE_Z), (0.0, y, ANKLE_Z + 0.04), 0.07, 0.055, "frame")
    B.box((0.065, y, KNEE_Z - 0.0), (0.07, 0.13, 0.12), "panel", "cover", 0.014)  # knee pad
    B.light_strip((0.102, y - 0.03, KNEE_Z - 0.01), (0.004, 0.012, 0.05), "emit")
    B.box((0.055, y, KNEE_Z - 0.2), (0.05, 0.12, 0.22), "panel", "cover", 0.01)  # shin guard
    B.zprism(K.chamfer_rect(0.27, 0.13, 0.03, 0.05, y), 0.0, 0.04, "rubber", "frame", 0.0)  # sole
    B.zprism(K.chamfer_rect(0.24, 0.12, 0.035, 0.04, y), 0.04, 0.13, "dark", "frame", 0.006, top_scale=0.85)
    B.box((0.0, y, 0.16), (0.13, 0.13, 0.09), "panel", "cover", 0.01)
    d()

# ---------------------------------------------------------------- torso
d = grp("torso")
B.zprism(K.chamfer_rect(0.23, 0.33, 0.05), HIP_Z - 0.06, 1.12, "frame", "frame", 0.0, top_scale=1.04)  # abdomen
B.zprism(K.chamfer_rect(0.27, 0.44, 0.08), 1.12, 1.46, "frame", "frame", 0.0, top_scale=0.84)  # chest
B.zprism(K.chamfer_rect(0.22, 0.32, 0.05), HIP_Z - 0.08, HIP_Z + 0.06, "dark", "frame", 0.0)  # pelvis
# chest armour: angled plates facing the camera side and the front
for sy in (-1, 1):
    ob = B.box((0.085, sy * 0.1, 1.33), (0.08, 0.17, 0.19), "panel", "cover", 0.012)
    K.rotate(ob, sy * 12, "X", (0.085, sy * 0.1, 1.33))
B.light_strip((0.126, -0.12, 1.33), (0.004, 0.07, 0.012), "emit")
B.light_strip((0.126, 0.12, 1.33), (0.004, 0.07, 0.012), "emit")
B.box((0.0, -0.215, 1.3), (0.18, 0.03, 0.22), "panel", "cover", 0.01)  # side plate (camera side)
B.light_strip((0.0, -0.232, 1.33), (0.1, 0.004, 0.012), "emit")
# cross straps
for sy in (-1, 1):
    B.strut((0.125, sy * 0.15, 1.44), (0.12, -sy * 0.12, 1.05), 0.03, "rubber", "greeble")
B.box((0.118, 0, 1.25), (0.02, 0.05, 0.05), "trim", "greeble", 0.0)
# belt, buckle, pouches
B.zprism(K.chamfer_rect(0.25, 0.34, 0.06), HIP_Z + 0.02, HIP_Z + 0.08, "rubber", "frame", 0.0)
B.box((0.128, 0, HIP_Z + 0.05), (0.016, 0.07, 0.05), "trim", "greeble", 0.0)
for sy, x in ((-1, 0.06), (-1, -0.06), (1, 0.06)):
    B.box((x, sy * 0.18, HIP_Z - 0.02), (0.08, 0.05, 0.1), "accent", "cover", 0.008)
B.box((-0.12, 0, 1.1), (0.06, 0.2, 0.22), "panel", "cover", 0.01)  # back pack plate
# short cape: curved sheet hanging from the shoulders at the back, ragged hem at mid-thigh
bm = bmesh.new()
rows, cols = 5, 7
vs = []
for j in range(rows + 1):
    t = j / rows
    z = 1.44 - t * 0.78
    row = []
    for i in range(cols + 1):
        u = i / cols
        yy = (u - 0.5) * (0.4 + 0.18 * t)
        xx = -0.15 - 0.06 * t - 0.05 * math.cos((u - 0.5) * math.pi) * (0.4 + t)
        hem = (0.05 * math.sin(i * 2.1 + 0.4)) if j == rows else 0.0
        row.append(bm.verts.new((xx, yy, z + hem)))
    vs.append(row)
for j in range(rows):
    for i in range(cols):
        bm.faces.new((vs[j][i], vs[j][i + 1], vs[j + 1][i + 1], vs[j + 1][i]))
res = bmesh.ops.solidify(bm, geom=bm.faces[:], thickness=0.012)
bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
cape = B._new_obj(bm, "frame", "cape_mesh", ["dark"])
d()

# ---------------------------------------------------------------- head and hood
NECK = Vector((0.0, 0.0, 1.48))
d = grp("head")
B.cyl((0.0, 0, 1.52), 0.05, 0.08, "Z", 8, "frame", "frame", 0.0)
B.uvsphere((0.02, 0, 1.64), 0.112, 12, 8, "internal", "frame", (1.0, 0.92, 1.15))  # faceless helmet
B.uvsphere((0.065, 0, 1.635), 0.075, 12, 6, "dark", "frame", (0.65, 1.0, 0.9))  # visor shell
B.light_strip((0.112, -0.03, 1.645), (0.006, 0.026, 0.006), "emit")
B.light_strip((0.112, 0.03, 1.645), (0.006, 0.026, 0.006), "emit")
ob = B.light_strip((0.105, 0, 1.6), (0.006, 0.02, 0.004), "emit")
d()
d = grp("hood")
hood = B.uvsphere((-0.015, 0, 1.665), 0.15, 14, 9, "dark", "frame", (1.08, 1.0, 1.1))
bmh = bmesh.new()
bmh.from_mesh(hood.data)
bmesh.ops.delete(bmh, geom=[v for v in bmh.verts if v.co.x > 0.075 and v.co.z < 1.75 and v.co.z > 1.55], context="VERTS")
for v in bmh.verts:  # drape the back and sides of the hood down onto the shoulders
    if v.co.z < 1.64:
        t = (1.64 - v.co.z) / 0.16
        v.co.z -= 0.09 * t
        v.co.x -= 0.03 * t * (1.0 if v.co.x < 0.03 else 0.0)
        v.co.y *= 1.0 + 0.25 * t
    if v.co.x < -0.05 and v.co.z > 1.7:
        v.co.x -= 0.03 * (v.co.z - 1.7) / 0.13
bmesh.ops.recalc_face_normals(bmh, faces=bmh.faces[:])
bmesh.ops.solidify(bmh, geom=bmh.faces[:], thickness=0.012)
bmesh.ops.recalc_face_normals(bmh, faces=bmh.faces[:])
bmh.to_mesh(hood.data)
bmh.free()
B.prism([(0.05, 1.82), (0.16, 1.74), (0.13, 1.7), (0.02, 1.78)], 0.2, 0.0, "dark", "frame", 0.0)  # hood peak
# cowl around the neck
B.ring((0.0, 0, 1.49), 0.16, 0.06, 0.08, "Z", 12, "dark", "frame", 0.0)
K.scale(B.parts[-1], (0.95, 1.05, 1.0), (0, 0, 1.49))
d()

# ---------------------------------------------------------------- weapon arm (right, camera side), rest = aiming along +X
SH_R = Vector((0.0, -0.25, 1.4))
d = grp("arm_weapon")
B.uvsphere(SH_R + Vector((0.0, -0.01, 0.025)), 0.1, 12, 6, "panel", "cover", (1.05, 1.0, 0.85))  # shoulder pad
limb(SH_R, SH_R + Vector((0.2, 0, -0.2)), 0.065, 0.056, "frame", 10)
ob = B.box(SH_R + Vector((0.1, -0.055, -0.1)), (0.15, 0.025, 0.075), "panel", "cover", 0.006)
K.rotate(ob, 45, "Y", SH_R + Vector((0.1, -0.055, -0.1)))
ob = B.light_strip(SH_R + Vector((0.1, -0.069, -0.1)), (0.09, 0.004, 0.01), "emit")
K.rotate(ob, 45, "Y", SH_R + Vector((0.1, -0.069, -0.1)))
d()
EL_R = SH_R + Vector((0.2, 0, -0.2))
d = grp("forearm_weapon")
limb(EL_R, EL_R + Vector((0.25, 0, 0)), 0.056, 0.047, "frame", 10)
B.box(EL_R + Vector((0.13, -0.035, 0.0)), (0.17, 0.04, 0.085), "panel", "cover", 0.008)  # bracer
B.light_strip(EL_R + Vector((0.13, -0.057, 0.01)), (0.08, 0.004, 0.01), "emit")
B.box(EL_R + Vector((0.29, 0, -0.01)), (0.09, 0.075, 0.085), "rubber", "frame", 0.01)  # glove
d()
HAND_R = EL_R + Vector((0.29, 0, -0.03))

# support arm (left, far side): reaches toward the fore-grip in the rest (aim) pose
SH_L = Vector((0.0, 0.25, 1.4))
d = grp("arm_support")
B.uvsphere(SH_L + Vector((0.0, 0.01, 0.025)), 0.1, 12, 6, "panel", "cover", (1.05, 1.0, 0.85))
limb(SH_L, SH_L + Vector((0.2, -0.1, -0.2)), 0.062, 0.054, "frame")
d()
EL_L = SH_L + Vector((0.2, -0.1, -0.2))
d = grp("forearm_support")
limb(EL_L, EL_L + Vector((0.25, -0.13, 0.0)), 0.054, 0.046, "frame")
B.box(EL_L + Vector((0.28, -0.15, 0.0)), (0.08, 0.07, 0.08), "rubber", "frame", 0.01)
d()

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
    ob = P.pack(G[name], name, ao=(name != "hood"))
    total += K.tri_count(ob)
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
print("TRIS", total)

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


def anim(name, frames, loop, fn):
    for ob in NODES.values():
        if ob.animation_data:
            ob.animation_data.action = None
    fn()
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
NODES["hips"].location = REST["hips"]
sc.frame_start, sc.frame_end = 1, 61

objs = [root] + list(NODES.values())
K.materialise(objs)  # zone colours into material slots, no COLOR_0 (ASSET_CONTRACT 7, v1.4)
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
                          export_anim_slide_to_zero=True, export_optimize_animation_size=False,
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
    meshes = [o for o in NODES.values() if o.type == "MESH"]
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
