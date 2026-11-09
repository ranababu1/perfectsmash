"""tfjkit: shared scripted-Blender modelling library for Temporal: First Jump 3D kits.

Conventions (Blender side, Z up; glTF export converts to Godot Y up):
  * X = screen right (physics x), Z = up (physics -y), -Y = toward the camera (Godot +Z).
  * Front face (the face that matches the 2D physics rectangle) faces -Y.
  * Destructible pivot = centre of the physics rectangle, depth centred on the physics plane.
  * 1 Blender unit = 1 metre = 100 physics px.
Every part is its own object while building; parts carry a 'role' so damage passes can treat
covers, frames, glass, internals and emissive strips differently. Export joins parts into one
mesh per state (multi-surface, one material per slot name).
"""
import bpy, bmesh, math, random, os, json
import tfjtex as TX
from mathutils import Vector, Matrix, Euler, noise

# --------------------------------------------------------------------------------------------
# Materials (ASSET_CONTRACT v1 section 7 and 12)
#   main surface  : mat_<material_id>_<ch>   baseColorFactor = chapter key colour
#   emissive      : emit_<colour>_<ch>
#   transparent   : glass_<name>_<ch>
# Paint zones (frame / panel / trim / internals ...) and baked ambient occlusion are carried in
# COLOR_0 as a multiplier (<= 1) of the main colour, so one main slot still reads as several
# finishes, and a bound tileable texture keeps the zones and the AO.
# --------------------------------------------------------------------------------------------
CH_CODE = {"helix": "hlx", "vita": "vta", "nova_grid": "nvg", "civitas": "cvt", "meridian": "mrd",
           "shared": "shr", "arsenal": "opr", "operative": "opr"}

PALETTES = {
    # key: colour that COLOR_0 = 1 maps to; zones are absolute sRGB colours
    # Helix premium pass (SV-04): graphite and cold steel, light worn edges, amber accents kept small
    "helix": dict(hazard="b8902e", key="56606b", frame="3e4650", panel="4c5661", trim="8d98a3", internal="131619",
                  rubber="222529", cable="1c1f23", light="8f9aa5", dark="2d3239", scorch="0f1011",
                  concrete="6a7078", polymer="d4d9dd", accent="c0782f", edge="b4bec8", module="3a4048",
                  floor="2a3038", tread="3a414a", metal=0.16, rough=0.42,
                  emit={"cyan": "35d6f2", "orange": "ff8a24", "red": "ff3b4e", "white": "dff6ff"}),
    "vita": dict(hazard="e8c860", key="eef1f2", frame="9aa2aa", panel="dfe4e7", trim="eef1f2", internal="1b1f22",
                 rubber="2a2d30", cable="30353a", light="f4f6f7", dark="6b737a", scorch="141414",
                 concrete="a8adb1", polymer="e9ecee", accent="c3cbd1", edge="f8fafb", module="c9d0d5", floor="d4d9dc", tread="b9c0c5", metal=0.06, rough=0.34,
                 emit={"green": "62e3a4", "white": "e8fff4", "orange": "ffb347", "red": "ff3b4e"}),
    "nova_grid": dict(hazard="e0b53c", key="b0aaa0", frame="4a4c52", panel="65676d", trim="a39d93", internal="141416",
                      rubber="18181a", cable="202022", light="c4beb4", dark="383a3f", scorch="0c0c0c",
                      concrete="74767a", polymer="6a6c72", accent="7a756e", edge="c9c3b8", module="3a3c41", floor="3b3d42", tread="55575c", metal=0.3, rough=0.5,
                      emit={"amber": "ffae42", "blue": "4aa8ff", "red": "ff3b4e", "white": "fff1d8"}),
    "civitas": dict(hazard="c9b04a", key="c4c9ce", frame="5d636a", panel="848a91", trim="b8bdc3", internal="17191c",
                    rubber="1d1e20", cable="26292c", light="d6dade", dark="454a50", scorch="101011",
                    concrete="9a9ea2", polymer="aab0b6", accent="6f7a88", edge="dfe3e6", module="4a5058", floor="8a8f94", tread="6c7177", metal=0.16, rough=0.6,
                    emit={"blue": "8ab4ff", "red": "ff3b4e", "white": "e6eeff", "orange": "ffb347"}),
    "meridian": dict(hazard="c8b070", key="d4d7e0", frame="4c4e5a", panel="626576", trim="c4c8d4", internal="111117",
                     rubber="16161b", cable="1e1f26", light="e6e8ee", dark="3a3c47", scorch="0b0b0e",
                     concrete="6a6b74", polymer="dcdee6", accent="6c6a86", edge="e0e2ea", module="33343e", floor="3a3b45", tread="50525e", metal=0.28, rough=0.32,
                     emit={"violet": "8f7cff", "cyan": "7fe8ff", "white": "f0f0ff", "red": "ff3b4e"}),
}
PALETTES["arsenal"] = dict(hazard="8a7440", key="40464d", frame="2d3137", panel="474e56", trim="7d858d",
                           internal="15171a", rubber="202226", cable="23262a", light="b8c0c8", dark="282c31",
                           scorch="101011", concrete="70747a", polymer="d8dce0", accent="2f3338", edge="c2cad2",
                           metal=0.22,
                           rough=0.38, emit={"cyan": "35d6f2", "amber": "ffae42", "white": "e6f6ff", "red": "ff3b4e"})
PALETTES["operative"] = dict(hazard="d9a838", key="202329", frame="2a2f36", panel="383e47", trim="646b74",
                             internal="111216", rubber="1d1f23", cable="22252a", light="9aa2ac", dark="1c1f24",
                             scorch="0e0e0f", concrete="5a5e63", polymer="60656c", accent="33302c", edge="c0c8d2",
                             cloth="131417", visor="0b0c0e", metal=0.12,
                             rough=0.62, emit={"cyan": "35d6f2", "white": "e6f6ff", "amber": "ffae42", "red": "ff3b4e"})
PALETTES["shared"] = dict(PALETTES["helix"])
PALETTES["shared"]["emit"] = {"cyan": "5fd4e8", "orange": "ff8a24", "red": "ff3b4e", "white": "e6f2ff"}

MATERIAL_FINISH = {  # physics material -> (metallic scale, roughness offset)
    "lightweight_alloy": (1.0, -0.04), "reinforced_steel": (1.0, 0.04), "composite": (0.55, 0.08),
    "glass_polymer": (0.8, -0.06), "concrete": (0.0, 0.45), "electronic_module": (0.9, 0.0),
    "energy_component": (0.85, 0.0), "ai_core_module": (0.6, 0.02),
}
EMIT_STRENGTH = 1.0

CTX = dict(chapter="helix", material="electronic_module", glass="clear", emit="cyan", emit2="orange")


def set_ctx(chapter, material, emit=None, emit2=None, glass="clear"):
    pal = PALETTES[chapter]
    names = list(pal["emit"].keys())
    CTX.update(chapter=chapter, material=material, emit=emit or names[0], emit2=emit2 or names[-1],
               glass=glass, value=1.0, main_zone=None, vcol=True, textures=True, floor_layer=False, matte=None,
               baking=False)


def hexcol(h, a=1.0):
    h = h.lstrip("#")
    c = [int(h[i:i + 2], 16) / 255.0 for i in (0, 2, 4)]
    c = [x / 12.92 if x <= 0.04045 else ((x + 0.055) / 1.055) ** 2.4 for x in c]
    return (c[0], c[1], c[2], a)


def zone_ratio(zone, chapter=None):
    pal = PALETTES[chapter or CTX["chapter"]]
    k = hexcol(pal["key"])
    z = hexcol(pal.get(zone, pal["key"]))
    return tuple(min(1.0, z[i] / max(k[i], 1e-4)) for i in range(3)) + (1.0,)


def _principled(m):
    try:
        m.use_nodes = True
    except Exception:
        pass
    return m.node_tree.nodes.get("Principled BSDF")


def slot_material(slot):
    """Resolve a builder slot ('panel', 'emit', 'emit2', 'glass', ...) to (material, zone)."""
    ch = CTX["chapter"]
    code = CH_CODE[ch]
    pal = PALETTES[ch]
    if slot in ("emit", "emit2") or slot.startswith("emit_"):
        colour = CTX["emit"] if slot == "emit" else CTX["emit2"] if slot == "emit2" else slot[5:]
        name = f"emit_{colour}_{code}"
        m = bpy.data.materials.get(name)
        if m is None:
            m = bpy.data.materials.new(name)
            p = _principled(m)
            col = hexcol(pal["emit"].get(colour, "ffffff"))
            p.inputs["Base Color"].default_value = tuple(x * 0.35 for x in col[:3]) + (1.0,)
            p.inputs["Emission Color"].default_value = col
            p.inputs["Emission Strength"].default_value = EMIT_STRENGTH
            p.inputs["Roughness"].default_value = 0.3
            p.inputs["Metallic"].default_value = 0.0
            m["tfj_kind"] = "emit"
        return m, None
    if slot.startswith("glass"):
        gname = CTX["glass"] if slot == "glass" else slot[6:]
        name = f"glass_{gname}_{code}"
        m = bpy.data.materials.get(name)
        if m is None:
            m = bpy.data.materials.new(name)
            p = _principled(m)
            tint = {"helix": "3d6573", "vita": "8fb3a8", "nova_grid": "6b5a3e", "civitas": "3e4b5c",
                    "meridian": "4f4a78", "shared": "4a6670", "arsenal": "3d6573", "operative": "20262b"}[ch]
            if gname == "smoked":
                tint = "4a5560"
            p.inputs["Base Color"].default_value = hexcol(tint)
            p.inputs["Metallic"].default_value = 0.0
            p.inputs["Roughness"].default_value = 0.35 if gname == "frost" else 0.05
            p.inputs["Alpha"].default_value = {"smoked": 0.6, "frost": 0.62}.get(gname, 0.4)
            if gname == "frost":
                p.inputs["Base Color"].default_value = hexcol("c8dde0")
            try:
                p.inputs["Specular IOR Level"].default_value = 0.7
            except Exception:
                pass
            for attr, val in (("surface_render_method", "BLENDED"), ("blend_method", "BLEND")):
                try:
                    setattr(m, attr, val)
                except Exception:
                    pass
            m["tfj_kind"] = "glass"
        return m, None
    mat_id = CTX["material"]
    name = f"src_{mat_id}_{code}"  # working material; materialise() maps its faces to the exported zone slots
    m = bpy.data.materials.get(name)
    if m is None:
        m = bpy.data.materials.new(name)
        p = _principled(m)
        p.inputs["Base Color"].default_value = hexcol(pal["key"])
        ms, ro = MATERIAL_FINISH.get(mat_id, (1.0, 0.0))
        p.inputs["Metallic"].default_value = pal["metal"] * ms
        p.inputs["Roughness"].default_value = min(0.95, max(0.08, pal["rough"] + ro))
        m["tfj_kind"] = "main"
    return m, slot


# --------------------------------------------------------------------------------------------
# Scene helpers
# --------------------------------------------------------------------------------------------
def reset_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)


def collection(name, parent=None):
    c = bpy.data.collections.get(name)
    if c is None:
        c = bpy.data.collections.new(name)
        (parent or bpy.context.scene.collection).children.link(c)
    return c


class Builder:
    """Accumulates parts (objects) for one asset."""

    def __init__(self, name, seed=0):
        self.name = name
        self.parts = []
        self.rng = random.Random(seed)
        self.col = collection("build_" + name)

    # ---- raw part creation -----------------------------------------------------------------
    def _new_obj(self, bm, role, name=None, mats=()):
        bm.loops.layers.uv.verify()  # every part carries UVMap so authored (fit) UVs survive join()
        me = bpy.data.meshes.new(name or f"{self.name}_{role}_{len(self.parts)}")
        bm.to_mesh(me)
        bm.free()
        ob = bpy.data.objects.new(me.name, me)
        for s in mats:
            m, zone = slot_material(s)
            me.materials.append(m)
            ob["zone"] = zone or ""
        ob["role"] = role
        self.col.objects.link(ob)
        self.parts.append(ob)
        return ob

    def box(self, center, size, slot="frame", role="frame", bevel=0.012, segs=1, name=None,
            taper=None, chamfer_front=0.0):
        bm = bmesh.new()
        bm_box(bm, Vector(center), Vector(size), bevel, segs, 0, taper=taper)
        return self._new_obj(bm, role, name, [slot])

    def prism(self, outline, depth, center_y=0.0, slot="frame", role="frame", bevel=0.01, segs=1,
              axis="Y", name=None):
        """Extrude a 2D outline (list of (u,v)) along axis. For axis Y: u->X, v->Z."""
        bm = bmesh.new()
        bm_prism(bm, outline, depth, center_y, axis, bevel, segs)
        return self._new_obj(bm, role, name, [slot])

    def cyl(self, center, radius, length, axis="Z", verts=16, slot="trim", role="greeble", bevel=0.006,
            segs=1, radius2=None, name=None):
        bm = bmesh.new()
        bm_cyl(bm, Vector(center), radius, length, axis, verts, bevel, segs, radius2)
        return self._new_obj(bm, role, name, [slot])

    def ring(self, center, r_outer, r_inner, length, axis="Y", verts=32, slot="trim", role="frame",
             bevel=0.006, segs=1, name=None, arc=(0.0, 360.0)):
        bm = bmesh.new()
        bm_ring(bm, Vector(center), r_outer, r_inner, length, axis, verts, arc)
        if bevel > 0:
            bm_bevel_all(bm, bevel, segs)
        return self._new_obj(bm, role, name, [slot])

    def tube(self, points, radius, verts=8, slot="cable", role="cable", name=None, cap=True):
        bm = bmesh.new()
        bm_tube(bm, [Vector(p) for p in points], radius, verts, cap)
        return self._new_obj(bm, role, name, [slot])

    def sphere(self, center, radius, subdiv=2, slot="glass", role="glass", scale=(1, 1, 1), name=None):
        bm = bmesh.new()
        bmesh.ops.create_icosphere(bm, subdivisions=subdiv, radius=radius)
        for v in bm.verts:
            v.co = Vector((v.co.x * scale[0], v.co.y * scale[1], v.co.z * scale[2])) + Vector(center)
        return self._new_obj(bm, role, name, [slot])

    def uvsphere(self, center, radius, segs=24, rings=12, slot="glass", role="glass", scale=(1, 1, 1),
                 name=None):
        bm = bmesh.new()
        bmesh.ops.create_uvsphere(bm, u_segments=segs, v_segments=rings, radius=radius)
        for v in bm.verts:
            v.co = Vector((v.co.x * scale[0], v.co.y * scale[1], v.co.z * scale[2])) + Vector(center)
        return self._new_obj(bm, role, name, [slot])

    def lathe(self, profile, center, verts=24, slot="frame", role="frame", axis="Z", name=None,
              bevel=0.0):
        """Revolve a profile [(r, h), ...] around axis through center."""
        bm = bmesh.new()
        bm_lathe(bm, profile, verts)
        orient(bm, axis)
        for v in bm.verts:
            v.co += Vector(center)
        if bevel > 0:
            bm_bevel_sharp(bm, bevel, 1, angle=40)
        return self._new_obj(bm, role, name, [slot])

    # ---- composite detail helpers ----------------------------------------------------------
    def plate_grid(self, x0, x1, z0, z1, y_face, cols, rows, gap=0.008, thick=0.02, slot="panel",
                   role="cover", bevel=0.006, inset_jitter=0.0, skip=None):
        """Cladding plates on a front face (normal -Y) at y_face, leaving real panel-line gaps."""
        out = []
        w = (x1 - x0) / cols
        h = (z1 - z0) / rows
        for i in range(cols):
            for j in range(rows):
                if skip and (i, j) in skip:
                    continue
                cx = x0 + (i + 0.5) * w
                cz = z0 + (j + 0.5) * h
                dy = self.rng.uniform(0, inset_jitter)
                out.append(self.box((cx, y_face - thick / 2 + dy, cz), (w - gap, thick, h - gap), slot,
                                    role, bevel))
        return out

    def side_plate_grid(self, y0, y1, z0, z1, x_face, sign, cols, rows, gap=0.008, thick=0.02,
                        slot="panel", role="cover", bevel=0.006):
        out = []
        w = (y1 - y0) / cols
        h = (z1 - z0) / rows
        for i in range(cols):
            for j in range(rows):
                cy = y0 + (i + 0.5) * w
                cz = z0 + (j + 0.5) * h
                out.append(self.box((x_face + sign * thick / 2, cy, cz), (thick, w - gap, h - gap), slot,
                                    role, bevel))
        return out

    def bolts(self, pts, y_face, r=0.012, slot="trim", normal="-Y"):
        out = []
        for (x, z) in pts:
            if normal == "-Y":
                out.append(self.cyl((x, y_face - 0.004, z), r, 0.01, "Y", 6, slot, "greeble", 0.002))
        return out

    def vent(self, cx, cz, w, h, y_face, slats=5, slot="internal", slat_slot="trim"):
        """Recessed vent: dark backing plus angled slats."""
        out = [self.box((cx, y_face + 0.004, cz), (w, 0.012, h), slot, "greeble", 0.002)]
        for k in range(slats):
            z = cz - h / 2 + (k + 0.5) * h / slats
            ob = self.box((cx, y_face - 0.006, z), (w * 0.94, 0.006, h / slats * 0.55), slat_slot,
                          "greeble", 0.001)
            out.append(ob)
        return out

    def light_strip(self, center, size, slot="emit", role="emit", bevel=0.0):
        return self.box(center, size, slot, role, bevel, 1)

    def cable_run(self, a, b, sag=0.08, radius=0.012, n=10, slot="cable"):
        a, b = Vector(a), Vector(b)
        pts = []
        for i in range(n + 1):
            t = i / n
            p = a.lerp(b, t)
            p.z -= sag * math.sin(math.pi * t)
            pts.append(p)
        return self.tube(pts, radius, 6, slot)

    def hazard_band(self, center, size, stripes=6, slot_a="hazard", slot_b="rubber", angle=45):
        """Physical hazard chevrons as alternating raised strips (no texture needed)."""
        out = []
        cx, cy, cz = center
        w, d, h = size
        base = self.box(center, size, slot_b, "cover", 0.003)
        out.append(base)
        sw = w / (stripes * 2)
        for k in range(stripes):
            x = cx - w / 2 + (2 * k + 0.5) * sw * 2 / 2 + sw / 2
            ob = self.prism([(-sw / 2 - h * 0.5, -h / 2), (sw / 2 - h * 0.5, -h / 2), (sw / 2 + h * 0.5, h / 2),
                             (-sw / 2 + h * 0.5, h / 2)], 0.004, 0, slot_a, "cover", 0.0)
            translate(ob, (x, cy - d / 2 - 0.002, cz))
            out.append(ob)
        return out

    def finish(self):
        return self.parts


# --------------------------------------------------------------------------------------------
# bmesh primitives
# --------------------------------------------------------------------------------------------
def bm_box(bm, c, s, bevel=0.0, segs=1, mat=0, taper=None):
    res = bmesh.ops.create_cube(bm, size=1.0)
    vs = res["verts"]
    for v in vs:
        x, y, z = v.co.x * s.x, v.co.y * s.y, v.co.z * s.z
        if taper and v.co.z > 0:
            x *= taper[0]
            y *= taper[1]
        v.co = Vector((x, y, z)) + c
    if bevel > 0:
        b = min(bevel, min(s) * 0.45)
        edges = list({e for v in vs for e in v.link_edges})
        bmesh.ops.bevel(bm, geom=list(vs) + edges, offset=b, segments=segs, profile=0.5,
                        affect="EDGES", clamp_overlap=True)
    return vs


def bm_bevel_all(bm, amount, segs=1):
    bmesh.ops.bevel(bm, geom=list(bm.verts) + list(bm.edges), offset=amount, segments=segs,
                    profile=0.5, affect="EDGES", clamp_overlap=True)


def bm_bevel_sharp(bm, amount, segs=1, angle=30):
    bm.normal_update()
    edges = [e for e in bm.edges if len(e.link_faces) == 2 and
             e.calc_face_angle(0) > math.radians(angle)]
    verts = list({v for e in edges for v in e.verts})
    if edges:
        bmesh.ops.bevel(bm, geom=verts + edges, offset=amount, segments=segs, profile=0.5,
                        affect="EDGES", clamp_overlap=True)


def orient(bm, axis):
    """Geometry built along Z; rotate to requested axis."""
    if axis == "Z":
        return
    if axis == "Y":
        R = Matrix.Rotation(math.radians(90), 4, "X")
    elif axis == "X":
        R = Matrix.Rotation(math.radians(90), 4, "Y")
    bmesh.ops.transform(bm, matrix=R, verts=bm.verts)


def bm_prism(bm, outline, depth, center_y, axis, bevel, segs):
    vs_f = [bm.verts.new((u, -depth / 2, v)) for (u, v) in outline]
    f = bm.faces.new(vs_f)
    f.normal_update()
    if f.normal.y > 0:
        f.normal_flip()
    ext = bmesh.ops.extrude_face_region(bm, geom=[f])
    nv = [g for g in ext["geom"] if isinstance(g, bmesh.types.BMVert)]
    for v in nv:
        v.co.y += depth
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    if bevel > 0:
        bm_bevel_all(bm, bevel, segs)
    if axis == "X":
        R = Matrix.Rotation(math.radians(90), 4, "Z")
        bmesh.ops.transform(bm, matrix=R, verts=bm.verts)
    if center_y:
        for v in bm.verts:
            v.co.y += center_y


def bm_cyl(bm, c, r, length, axis, verts, bevel, segs, r2=None):
    res = bmesh.ops.create_cone(bm, cap_ends=True, cap_tris=False, segments=verts, radius1=r,
                                radius2=r if r2 is None else r2, depth=length)
    vs = res["verts"]
    if bevel > 0:
        bm.normal_update()
        edges = [e for e in bm.edges if len(e.link_faces) == 2 and e.calc_face_angle(0) > math.radians(50)]
        bmesh.ops.bevel(bm, geom=list({v for e in edges for v in e.verts}) + edges,
                        offset=min(bevel, r * 0.3, length * 0.3), segments=segs, profile=0.5,
                        affect="EDGES", clamp_overlap=True)
    orient(bm, axis)
    for v in bm.verts:
        v.co += c


def bm_ring(bm, c, ro, ri, length, axis, verts, arc=(0.0, 360.0)):
    a0, a1 = math.radians(arc[0]), math.radians(arc[1])
    full = abs(arc[1] - arc[0]) >= 359.9
    n = verts if full else max(2, int(verts * (arc[1] - arc[0]) / 360.0))
    rings = []
    for i in range(n + (0 if full else 1)):
        a = a0 + (a1 - a0) * i / (n if not full else n)
        ca, sa = math.cos(a), math.sin(a)
        rings.append([bm.verts.new((ro * ca, ro * sa, -length / 2)), bm.verts.new((ro * ca, ro * sa, length / 2)),
                      bm.verts.new((ri * ca, ri * sa, length / 2)), bm.verts.new((ri * ca, ri * sa, -length / 2))])
    m = len(rings)
    for i in range(m if full else m - 1):
        A, B = rings[i], rings[(i + 1) % m]
        for k in range(4):
            bm.faces.new((A[k], B[k], B[(k + 1) % 4], A[(k + 1) % 4]))
    if not full:
        bm.faces.new(rings[0][::-1])
        bm.faces.new(rings[-1])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    orient(bm, axis)
    for v in bm.verts:
        v.co += c


def bm_tube(bm, pts, r, verts, cap):
    rings = []
    for i, p in enumerate(pts):
        if i == 0:
            t = (pts[1] - pts[0]).normalized()
        elif i == len(pts) - 1:
            t = (pts[-1] - pts[-2]).normalized()
        else:
            t = (pts[i + 1] - pts[i - 1]).normalized()
        up = Vector((0, 0, 1)) if abs(t.z) < 0.9 else Vector((1, 0, 0))
        n1 = t.cross(up).normalized()
        n2 = t.cross(n1).normalized()
        ring = []
        for k in range(verts):
            a = 2 * math.pi * k / verts
            ring.append(bm.verts.new(p + r * (math.cos(a) * n1 + math.sin(a) * n2)))
        rings.append(ring)
    for i in range(len(rings) - 1):
        A, B = rings[i], rings[i + 1]
        for k in range(verts):
            bm.faces.new((A[k], A[(k + 1) % verts], B[(k + 1) % verts], B[k]))
    if cap:
        bm.faces.new(rings[0][::-1])
        bm.faces.new(rings[-1])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)


def bm_lathe(bm, profile, verts):
    rings = []
    for k in range(verts):
        a = 2 * math.pi * k / verts
        rings.append([bm.verts.new((r * math.cos(a), r * math.sin(a), h)) for (r, h) in profile])
    n = len(profile)
    for k in range(verts):
        A, B = rings[k], rings[(k + 1) % verts]
        for i in range(n - 1):
            q = (A[i], B[i], B[i + 1], A[i + 1])
            if len({v.co.to_tuple(5) for v in q}) >= 3:
                try:
                    bm.faces.new(q)
                except ValueError:
                    pass
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-5)
    # caps
    for idx in (0, n - 1):
        if profile[idx][0] > 1e-4:
            ring = [rings[k][idx] for k in range(verts)]
            try:
                bm.faces.new(ring if idx == n - 1 else ring[::-1])
            except ValueError:
                pass
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)


# --------------------------------------------------------------------------------------------
# Object transform helpers
# --------------------------------------------------------------------------------------------
def translate(ob, d):
    ob.data.transform(Matrix.Translation(Vector(d)))


def rotate(ob, angle_deg, axis="Z", pivot=(0, 0, 0)):
    p = Vector(pivot)
    M = Matrix.Translation(p) @ Matrix.Rotation(math.radians(angle_deg), 4, axis) @ Matrix.Translation(-p)
    ob.data.transform(M)


def scale(ob, s, pivot=(0, 0, 0)):
    p = Vector(pivot)
    S = Matrix.Diagonal(Vector((s[0], s[1], s[2], 1.0)))
    ob.data.transform(Matrix.Translation(p) @ S @ Matrix.Translation(-p))


def bounds(obs):
    mn = Vector((1e9, 1e9, 1e9))
    mx = Vector((-1e9, -1e9, -1e9))
    for ob in obs:
        for v in ob.data.vertices:
            co = ob.matrix_world @ v.co
            mn = Vector(map(min, mn, co))
            mx = Vector(map(max, mx, co))
    return mn, mx


def center_of(ob):
    mn, mx = bounds([ob])
    return (mn + mx) / 2


# --------------------------------------------------------------------------------------------
# UVs, normals, joining, export
# --------------------------------------------------------------------------------------------
TILE_M = 1.0  # 1 UV unit = 1 metre; tileable surfaces textures repeat every metre


ZONE_TILE = {"concrete": 2.0, "floor": 2.0, "tread": 1.0, "cable": 0.5, "rubber": 0.5}
FIT_ZONES = {"module"}  # parts author their own UVs (one rack unit per blade face)


def box_uv(me, tile=TILE_M):
    if not me.uv_layers:
        me.uv_layers.new(name="UVMap")
    uv = me.uv_layers.active.data
    za = me.attributes.get("zid")
    for poly in me.polygons:
        z = ZONES[za.data[poly.index].value] if za and za.data[poly.index].value < len(ZONES) else ""
        if z in FIT_ZONES and abs(poly.normal.y) > 0.7:
            continue
        t = ZONE_TILE.get(z, tile)
        n = poly.normal
        ax = max(range(3), key=lambda i: abs(n[i]))
        for li in poly.loop_indices:
            co = me.vertices[me.loops[li].vertex_index].co
            if ax == 0:
                u, v = co.y * (1 if n.x > 0 else -1), co.z
            elif ax == 1:
                u, v = co.x * (-1 if n.y > 0 else 1), co.z
            else:
                u, v = co.x, co.y * (1 if n.z > 0 else -1)
            uv[li].uv = (u / t, v / t)


def join(parts, name):
    """Merge parts (meshes in world space) into one new object. Originals are left untouched."""
    mats = []
    bm = bmesh.new()
    for p in parts:
        if p.type != "MESH" or len(p.data.polygons) == 0:
            continue
        me = p.data.copy()
        me.transform(p.matrix_world)
        local = []
        for m in me.materials:
            if m is None:
                m = slot_material("frame")[0]
            if m not in mats:
                mats.append(m)
            local.append(mats.index(m))
        nf = len(bm.faces)
        bm.from_mesh(me)
        bm.faces.ensure_lookup_table()
        for f in bm.faces[nf:]:
            f.material_index = local[f.material_index] if local else 0
        bpy.data.meshes.remove(me)
    out = bpy.data.meshes.new(name)
    bm.to_mesh(out)
    bm.free()
    for m in mats:
        out.materials.append(m)
    ob = bpy.data.objects.new(name, out)
    bpy.context.scene.collection.objects.link(ob)
    ca = out.color_attributes.get("Col")
    if ca is not None:
        out.color_attributes.active_color = ca
        try:
            out.color_attributes.render_color_index = out.color_attributes.active_color_index
        except Exception:
            pass
    return ob


def dedupe_materials(ob):
    me = ob.data
    names = [m.name if m else None for m in me.materials]
    uniq = []
    remap = {}
    for i, n in enumerate(names):
        if n not in uniq:
            uniq.append(n)
        remap[i] = uniq.index(n)
    if len(uniq) == len(names):
        return
    for poly in me.polygons:
        poly.material_index = remap[poly.material_index]
    mats = [bpy.data.materials.get(n) for n in uniq]
    me.materials.clear()
    for m in mats:
        me.materials.append(m)


def finalize(ob, smooth_angle=35):
    me = ob.data
    bm = bmesh.new()
    bm.from_mesh(me)
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-5)
    bmesh.ops.dissolve_degenerate(bm, dist=1e-6, edges=bm.edges)
    bm.to_mesh(me)
    bm.free()
    box_uv(me)
    for p in me.polygons:
        p.use_smooth = True
    try:
        me.set_sharp_from_angle(angle=math.radians(smooth_angle))
    except Exception:
        pass
    mod = ob.modifiers.new("wn", "WEIGHTED_NORMAL")
    mod.keep_sharp = True
    mod.weight = 50
    ctx = bpy.context
    ctx.view_layer.objects.active = ob
    bpy.ops.object.modifier_apply(modifier=mod.name)
    return ob


# --------------------------------------------------------------------------------------------
# Zones -> material slots (ASSET_CONTRACT 7, v1.4: colour lives in the material, not COLOR_0)
# --------------------------------------------------------------------------------------------
ZONES = ["", "frame", "panel", "light", "key", "polymer", "concrete", "accent",
         "trim", "dark", "internal", "cable", "rubber", "hazard", "scorch", "burnt", "edge", "module", "floor",
         "tread", "cloth", "visor"]
STRUCTURAL = {"", "frame", "panel", "light", "key", "polymer", "concrete", "accent", "module", "floor", "tread",
              "cloth", "visor"}
EDGE_ZONES = {"", "key", "frame", "panel", "light", "accent", "polymer"}  # bevels on these catch a worn edge
EDGE_WIDTH = 0.024  # m: narrow diagonal faces (bevel chamfers) below this width become the edge slot
ZONE_FINISH = {  # zone -> (metallic scale, roughness override or None)
    "trim": (1.0, None), "dark": (0.7, 0.55), "internal": (0.5, 0.6), "cable": (0.0, 0.7),
    "rubber": (0.0, 0.85), "hazard": (0.0, 0.5), "scorch": (0.0, 0.92), "burnt": (0.3, 0.8),
    "edge": (1.0, 0.3),
}


def _is_edge_face(me, poly):
    n = poly.normal
    if max(abs(n.x), abs(n.y), abs(n.z)) > 0.985:
        return False  # axis-aligned: a main face, not a chamfer
    per = 0.0
    vs = [me.vertices[i].co for i in poly.vertices]
    for i in range(len(vs)):
        per += (vs[i] - vs[i - 1]).length
    return per > 0 and 2.0 * poly.area / per < EDGE_WIDTH * 0.5 and per > 0.08


def zone_id(zone):
    if zone not in ZONES:
        ZONES.append(zone)
    return ZONES.index(zone)


def _zone_material(main, zone, name, value):
    m = bpy.data.materials.get(name)
    if m is not None and m.get("tfj_value") == value:
        return m
    if m is None:
        m = bpy.data.materials.new(name)
    pal = PALETTES[CTX["chapter"]]
    pm, pz = _principled(main), _principled(m)
    col = hexcol(pal.get(zone or "key", pal["key"]))
    if zone == "burnt":  # heat-darkened structure on damaged parts
        col = tuple(c * 0.42 for c in hexcol(pal["frame"])[:3]) + (1.0,)
    pz.inputs["Base Color"].default_value = tuple(c * value for c in col[:3]) + (1.0,)
    ms, rough = ZONE_FINISH.get(zone, (1.0, None))
    pz.inputs["Metallic"].default_value = pm.inputs["Metallic"].default_value * ms
    pz.inputs["Roughness"].default_value = rough if rough is not None else pm.inputs["Roughness"].default_value
    if CTX.get("matte"):  # background layers: matte, so the ambient-colour specular does not lift them (no sky in MissionView)
        pz.inputs["Roughness"].default_value = max(pz.inputs["Roughness"].default_value, CTX["matte"])
        pz.inputs["Metallic"].default_value *= 0.4
    m["tfj_kind"] = "zone"
    m["tfj_zone"] = zone or "key"
    m["tfj_value"] = value
    m.use_backface_culling = True
    if CTX.get("matte"):
        m["tfj_matte_layer"] = True
    if CTX.get("textures", True):
        if CTX.get("baking"):
            m["tfj_allow_bright"] = True
        if zone == "module":
            m["tfj_emit_col"] = hexcol(pal["emit"][CTX["emit"]])
            m["tfj_emit_strength"] = CTX.get("module_emit", 1.0)
        fl = None
        if CTX.get("floor_layer"):
            fl = dict(value=min(1.0, CTX.get("value", 1.0) * 2.6), emit=hexcol(pal["emit"][CTX["emit"]]),
                      emit_strength=0.8)
        TX.texture_zone(m, CTX["chapter"], zone or "key", CTX["material"], pz.inputs["Base Color"].default_value,
                        CTX.get("normal_strength", 1.0), floor=fl)
        if CTX.get("matte"):
            m["tfj_matte"] = True
    return m


def materialise(objs, value=None):
    """Replace the single main slot by one slot per paint zone, colour in baseColorFactor.
    The largest structural zone of the first mesh keeps the bare mat_<material>_<ch> name; other
    structural zones are mat_<material>_<ch>_<zone>; trims, rubber, cables, hazard paint and scorch
    are trim_<zone>_<ch>. Idempotent: only faces still on a 'main' material are remapped."""
    value = CTX.get("value", 1.0) if value is None else value
    code = CH_CODE[CTX["chapter"]]
    mat_id = CTX["material"]
    meshes = [o for o in objs if o.type == "MESH"]
    if CTX.get("main_zone") is None:
        area = {}
        for o in meshes:
            za = o.data.attributes.get("zid")
            for poly in o.data.polygons:
                m = o.data.materials[poly.material_index] if o.data.materials else None
                if m is None or m.get("tfj_kind") != "main":
                    continue
                z = ZONES[za.data[poly.index].value] if za else ""
                if z in STRUCTURAL:
                    area[z] = area.get(z, 0.0) + poly.area
            if area:
                break
        CTX["main_zone"] = max(area, key=area.get) if area else "frame"
    for o in meshes:
        me = o.data
        za = me.attributes.get("zid")
        slots = list(me.materials)
        new_index = {}
        for poly in me.polygons:
            m = slots[poly.material_index] if slots else None
            if m is None or m.get("tfj_kind") != "main":
                continue
            z = ZONES[za.data[poly.index].value] if za else ""
            if CTX.get("edges", True) and z in EDGE_ZONES and _is_edge_face(me, poly):
                z = "edge"
            if z in ("", "key"):
                z = "key"
            if z == CTX["main_zone"] or (z == "key" and CTX["main_zone"] in ("", "key")):
                name = f"mat_{mat_id}_{code}"
            elif z in STRUCTURAL:
                name = f"mat_{mat_id}_{code}_{z}"
            else:
                name = f"trim_{z}_{code}"
            key = (poly.material_index, name)
            if key not in new_index:
                zm = _zone_material(m, z, name, value)
                if zm.name not in [x.name for x in me.materials if x]:
                    me.materials.append(zm)
                new_index[key] = [x.name if x else None for x in me.materials].index(zm.name)
            poly.material_index = new_index[key]
        # drop slots no face uses any more
        used = {p.material_index for p in me.polygons}
        keep = [i for i in range(len(me.materials)) if i in used]
        if len(keep) != len(me.materials):
            remap = {old: new for new, old in enumerate(keep)}
            mats = [me.materials[i] for i in keep]
            idx = [remap[p.material_index] for p in me.polygons]
            me.materials.clear()
            for mm in mats:
                me.materials.append(mm)
            for p, i in zip(me.polygons, idx):
                p.material_index = i


def tri_count(ob):
    return sum(len(p.vertices) - 2 for p in ob.data.polygons)


def export_glb(objs, path, animations=False):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    ctx = bpy.context
    for o in ctx.view_layer.objects:
        o.select_set(False)
    for o in objs:
        o.select_set(True)
    ctx.view_layer.objects.active = objs[0]
    materialise(objs)
    # rename materials to bare slot names for export
    renamed = {}
    for o in objs:
        for m in (o.data.materials if o.type == "MESH" else []):
            if m and "@" in m.name and m.name not in renamed:
                renamed[m.name] = m
    kw = dict(filepath=path, export_format="GLB", use_selection=True, export_apply=True,
              export_yup=True, export_texcoords=True, export_normals=True, export_materials="EXPORT",
              export_animations=animations, export_vertex_color="ACTIVE" if CTX.get("vcol", True) else "NONE",
              export_all_vertex_colors=False, export_active_vertex_color_when_no_material=False,
              export_extras=False, export_cameras=False, export_lights=False)
    for o in objs:  # COLOR_0 = baked occlusion (grey, <= 1): contract v1.7 lets the loader honour it
        if o.type == "MESH" and o.data.color_attributes.get("Col") is not None:
            o.data.color_attributes.active_color = o.data.color_attributes.get("Col")
    with slot_names(renamed.values()):
        bpy.ops.export_scene.gltf(**kw)
    factors = {}
    for o in objs:
        for m in (o.data.materials if o.type == "MESH" else []):
            if m and m.get("tfj_metal") is not None:
                factors[m.name.split("@")[0]] = {"metallicFactor": round(float(m["tfj_metal"]), 3)}
    TX.externalise(path, factors=factors)
    return os.path.getsize(path)


class slot_names:
    """Temporarily rename 'slot@chapter' materials to 'slot' so the glb carries bare slot names."""

    def __init__(self, mats):
        self.mats = list(mats)

    def __enter__(self):
        self.old = [m.name for m in self.mats]
        # avoid collisions: two chapters' slots never coexist in one export
        for m in self.mats:
            m.name = "__tmp__" + m.name
        for m, n in zip(self.mats, self.old):
            m.name = n.split("@")[0]

    def __exit__(self, *a):
        for m, n in zip(self.mats, self.old):
            m.name = n


def _pane(self, center, w, h, thick=0.012, slot="glass", normal="Y"):
    """Glass pane facing -Y (normal 'Y') or a side pane facing -X (normal 'X', w runs along depth).
    Damage passes replace it with shards."""
    size = (w, thick, h) if normal == "Y" else (thick, w, h)
    ob = self.box(center, size, slot, "pane", 0.0)
    ob["pane"] = [center[0], center[1], center[2], w, h, thick]
    ob["pane_slot"] = slot
    ob["pane_normal"] = normal
    return ob


Builder.pane = _pane


# --------------------------------------------------------------------------------------------
# Extra builders
# --------------------------------------------------------------------------------------------
SMALL_BEVEL_MIN = 0.04  # parts thinner than this get no bevel (sub-pixel at game scale)


def chamfer_rect(w, d, c, cx=0.0, cy=0.0):
    c = min(c, w * 0.45, d * 0.45)
    hw, hd = w / 2, d / 2
    pts = [(-hw + c, -hd), (hw - c, -hd), (hw, -hd + c), (hw, hd - c), (hw - c, hd), (-hw + c, hd),
           (-hw, hd - c), (-hw, -hd + c)]
    return [(x + cx, y + cy) for x, y in pts]


def _zprism(self, outline, z0, z1, slot="frame", role="frame", bevel=0.008, segs=1, name=None, top_scale=1.0):
    """Extrude an XY outline (list of (x, y)) from z0 to z1 (vertical members)."""
    bm = bmesh.new()
    lo = [bm.verts.new((x, y, z0)) for x, y in outline]
    cx = sum(p[0] for p in outline) / len(outline)
    cy = sum(p[1] for p in outline) / len(outline)
    hi = [bm.verts.new((cx + (x - cx) * top_scale, cy + (y - cy) * top_scale, z1)) for x, y in outline]
    n = len(outline)
    bm.faces.new(lo[::-1])
    bm.faces.new(hi)
    for i in range(n):
        bm.faces.new((lo[i], lo[(i + 1) % n], hi[(i + 1) % n], hi[i]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    if bevel > 0:
        bm_bevel_sharp(bm, bevel, segs, 30)
    return self._new_obj(bm, role, name, [slot])


def _xprism(self, outline, x0, x1, slot="frame", role="frame", bevel=0.008, segs=1, name=None):
    """Extrude a YZ outline (list of (y, z)) from x0 to x1 (horizontal members along X)."""
    bm = bmesh.new()
    lo = [bm.verts.new((x0, y, z)) for y, z in outline]
    hi = [bm.verts.new((x1, y, z)) for y, z in outline]
    n = len(outline)
    bm.faces.new(lo[::-1])
    bm.faces.new(hi)
    for i in range(n):
        bm.faces.new((lo[i], lo[(i + 1) % n], hi[(i + 1) % n], hi[i]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    if bevel > 0:
        bm_bevel_sharp(bm, bevel, segs, 30)
    return self._new_obj(bm, role, name, [slot])


def _strut(self, a, b, t, slot="frame", role="frame", bevel=0.0, round_=False, verts=8):
    """Square (or round) member from point a to point b with thickness t."""
    a, b = Vector(a), Vector(b)
    L = (b - a).length
    if round_:
        bm = bmesh.new()
        bm_cyl(bm, Vector((0, 0, 0)), t / 2, L, "Z", verts, 0.0, 1)
    else:
        bm = bmesh.new()
        bm_box(bm, Vector((0, 0, 0)), Vector((t, t, L)), bevel if t > SMALL_BEVEL_MIN else 0.0, 1)
    q = (b - a).normalized().to_track_quat("Z", "Y")
    M = Matrix.Translation((a + b) / 2) @ q.to_matrix().to_4x4()
    bmesh.ops.transform(bm, matrix=M, verts=bm.verts)
    return self._new_obj(bm, role, None, [slot])


def _truss(self, x0, x1, z0, z1, y, t, bays, slot="frame", role="frame", diag="X", chord=None):
    """Planar truss in the XZ plane at depth y: top/bottom chords, verticals, diagonals."""
    out = []
    chord = chord or t * 1.4
    out.append(self.box(((x0 + x1) / 2, y, z1 - chord / 2), (x1 - x0, chord, chord), slot, role, 0.006))
    out.append(self.box(((x0 + x1) / 2, y, z0 + chord / 2), (x1 - x0, chord, chord), slot, role, 0.006))
    bw = (x1 - x0) / bays
    for i in range(bays + 1):
        x = x0 + i * bw
        x = min(max(x, x0 + t / 2), x1 - t / 2)
        out.append(self.box((x, y, (z0 + z1) / 2), (t, t, z1 - z0 - 2 * chord), slot, role, 0.0))
    for i in range(bays):
        xa, xb = x0 + i * bw + t / 2, x0 + (i + 1) * bw - t / 2
        za, zb = z0 + chord, z1 - chord
        if diag in ("X", "/"):
            out.append(self.strut((xa, y, za), (xb, y, zb), t * 0.8, slot, role))
        if diag in ("X", "\\"):
            out.append(self.strut((xa, y, zb), (xb, y, za), t * 0.8, slot, role))
    return out


def _vtruss(self, z0, z1, x0, x1, y, t, bays, slot="frame", role="frame", chord=None):
    """Vertical truss (mast face) in the XZ plane: two vertical chords and zig-zag bracing."""
    out = []
    chord = chord or t * 1.4
    for x in (x0 + chord / 2, x1 - chord / 2):
        out.append(self.box((x, y, (z0 + z1) / 2), (chord, chord, z1 - z0), slot, role, 0.0))
    bh = (z1 - z0) / bays
    for i in range(bays):
        za, zb = z0 + i * bh, z0 + (i + 1) * bh
        out.append(self.box(((x0 + x1) / 2, y, za + t / 2), (x1 - x0 - 2 * chord, t, t), slot, role, 0.0))
        xa, xb = (x0 + chord, x1 - chord) if i % 2 == 0 else (x1 - chord, x0 + chord)
        out.append(self.strut((xa, y, za + t), (xb, y, zb), t * 0.8, slot, role))
    return out


Builder.zprism = _zprism
Builder.xprism = _xprism
Builder.strut = _strut
Builder.truss = _truss
Builder.vtruss = _vtruss

_orig_box = Builder.box


def _box_auto(self, center, size, slot="frame", role="frame", bevel=0.012, segs=1, name=None, taper=None,
              chamfer_front=0.0):
    if min(size) < SMALL_BEVEL_MIN:
        bevel = min(bevel, min(size) * 0.2) if min(size) >= 0.02 else 0.0
    return _orig_box(self, center, size, slot, role, bevel, segs, name, taper, chamfer_front)


Builder.box = _box_auto


def round_rect(w, d, r, n=3, cx=0.0, cy=0.0):
    """Rounded-rectangle outline (n segments per corner) for the softer VITA / Meridian forms."""
    r = min(r, w * 0.49, d * 0.49)
    hw, hd = w / 2 - r, d / 2 - r
    pts = []
    for (ox, oy, a0) in ((hw, -hd, -90), (hw, hd, 0), (-hw, hd, 90), (-hw, -hd, 180)):
        for i in range(n + 1):
            a = math.radians(a0 + 90 * i / n)
            pts.append((cx + ox + r * math.cos(a), cy + oy + r * math.sin(a)))
    return pts


def regular(n, r, cx=0.0, cy=0.0, rot=0.0, sy=1.0):
    return [(cx + r * math.cos(rot + 2 * math.pi * i / n), cy + sy * r * math.sin(rot + 2 * math.pi * i / n)) for i in range(n)]
