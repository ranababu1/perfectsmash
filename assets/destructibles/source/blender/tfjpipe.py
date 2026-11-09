"""tfjpipe: zone colours, baked AO, progressive damage, debris and glb packaging."""
import bpy, bmesh, math, random, os, json
from mathutils import Vector, Matrix, noise
from mathutils.bvhtree import BVHTree
import tfjkit as K


# ------------------------------------------------------------------------------------------
# Part utilities
# ------------------------------------------------------------------------------------------
def clone(parts, suffix):
    out = []
    col = K.collection("work")
    for p in parts:
        c = p.copy()
        c.data = p.data.copy()
        c.name = p.name + suffix
        for k in p.keys():
            c[k] = p[k]
        col.objects.link(c)
        out.append(c)
    return out


def remove(obs):
    for o in obs:
        me = o.data
        bpy.data.objects.remove(o, do_unlink=True)
        if me and me.users == 0:
            bpy.data.meshes.remove(me)


def roles(parts, *names):
    return [p for p in parts if p.get("role") in names]


def _zone_attr(me, zid):
    a = me.attributes.get("zid") or me.attributes.new("zid", "INT", "FACE")
    for d in a.data:
        d.value = zid


def paint_parts(parts):
    """Write the zone multiplier of every part into a corner colour attribute 'Col' (preview and AO
    working data) and the zone id into a face attribute 'zid'. At export K.materialise turns the
    zones into material slots with the colour in baseColorFactor (ASSET_CONTRACT 7, v1.4)."""
    for p in parts:
        me = p.data
        zone = p.get("zone", "")
        col = (1.0, 1.0, 1.0, 1.0)  # colour lives in the zone slots; COLOR_0 carries occlusion only
        if p.get("scorched"):
            col = tuple(c * p["scorched"] for c in col[:3]) + (1.0,)
        a = me.color_attributes.get("Col") or me.color_attributes.new("Col", "FLOAT_COLOR", "CORNER")
        for d in a.data:
            d.color = col
        _zone_attr(me, K.zone_id("burnt" if p.get("scorched") and p["scorched"] < 0.72 else zone))


def cutter_paint(me, zone="scorch"):
    if not me.materials:
        me.materials.append(K.slot_material("frame")[0])
    a = me.color_attributes.get("Col") or me.color_attributes.new("Col", "FLOAT_COLOR", "CORNER")
    col = K.zone_ratio(zone)
    for d in a.data:
        d.color = col
    _zone_attr(me, K.zone_id(zone))


def bake_ao(ob, dist=0.12, samples=20, strength=0.85, seed=3):
    me = ob.data
    bm = bmesh.new()
    bm.from_mesh(me)
    bm.faces.ensure_lookup_table()
    tree = BVHTree.FromBMesh(bm)
    bm.free()
    rng = random.Random(seed)
    dirs = []
    for i in range(samples):  # cosine-weighted hemisphere around +Z, rotated per normal
        u, v = (i + 0.5) / samples, rng.random()
        r = math.sqrt(u)
        a = 2 * math.pi * v
        dirs.append(Vector((r * math.cos(a), r * math.sin(a), math.sqrt(max(0.0, 1 - u)))))
    attr = me.color_attributes.get("Col")
    if attr is None:
        return
    for poly in me.polygons:
        n = poly.normal
        q = n.to_track_quat("Z", "Y")
        for li in poly.loop_indices:
            co = me.vertices[me.loops[li].vertex_index].co
            # pull slightly toward the face centre to avoid self hits on the bevel
            o = co.lerp(poly.center, 0.04) + n * 0.002
            hits = 0.0
            for d in dirs:
                w = q @ d
                h = tree.ray_cast(o, w, dist)
                if h[0] is not None:
                    hits += 1.0 - (h[3] / dist) ** 0.5 * 0.6
            occ = hits / samples
            f = 1.0 - strength * occ
            c = attr.data[li].color
            attr.data[li].color = (c[0] * f, c[1] * f, c[2] * f, 1.0)


def decimate_to(ob, target):
    tris = K.tri_count(ob)
    if target is None or tris <= target:
        return
    m = ob.modifiers.new("dec", "DECIMATE")
    m.decimate_type = "COLLAPSE"
    m.ratio = max(0.25, target / tris * 0.97)
    m.use_collapse_triangulate = True
    bpy.context.view_layer.objects.active = ob
    bpy.ops.object.modifier_apply(modifier=m.name)


def pack(parts, name, ao=True, smooth_angle=35, budget=None):
    paint_parts(parts)
    ob = K.join(parts, name)
    if budget:
        bm = bmesh.new()
        bm.from_mesh(ob.data)
        bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-5)
        bm.to_mesh(ob.data)
        bm.free()
        decimate_to(ob, budget)
    K.finalize(ob, smooth_angle)
    if ao:
        bake_ao(ob)
    return ob


# ------------------------------------------------------------------------------------------
# Deformation primitives
# ------------------------------------------------------------------------------------------
def densify(ob, cuts=2, max_edge=None, normal=(0, -1, 0), min_area=0.0004):
    """Subdivide only the big faces that face `normal` (the side that will be dented)."""
    bm = bmesh.new()
    bm.from_mesh(ob.data)
    n = Vector(normal) if normal is not None else None
    faces = [f for f in bm.faces if f.calc_area() > min_area and (n is None or f.normal.dot(n) > 0.7)]
    edges = list({e for f in faces for e in f.edges})
    if max_edge:
        edges = [e for e in edges if e.calc_length() > max_edge]
    if edges:
        bmesh.ops.subdivide_edges(bm, edges=edges, cuts=cuts, use_grid_fill=True)
        bmesh.ops.triangulate(bm, faces=[f for f in bm.faces if len(f.verts) > 4])
    bm.to_mesh(ob.data)
    bm.free()


def dent(ob, point, radius, depth, direction, sharp=2.0):
    point, direction = Vector(point), Vector(direction).normalized()
    for v in ob.data.vertices:
        d = (v.co - point).length
        if d < radius:
            f = (1 - (d / radius) ** 2) ** sharp
            v.co += direction * depth * f
    ob.data.update()


def crumple(ob, amount, seed=0, scale=6.0):
    for v in ob.data.vertices:
        n = noise.noise_vector(v.co * scale + Vector((seed * 1.7, seed * 0.3, seed * 2.1)))
        v.co += n * amount
    ob.data.update()


def bend(ob, hinge_point, axis, angle_deg, falloff_axis=None, length=1.0):
    """Rotate vertices about a hinge line; with falloff_axis the angle grows with distance (curl)."""
    hp, ax = Vector(hinge_point), Vector(axis).normalized()
    for v in ob.data.vertices:
        a = angle_deg
        if falloff_axis is not None:
            t = abs((v.co - hp).dot(Vector(falloff_axis))) / max(length, 1e-4)
            a = angle_deg * min(1.0, t) ** 1.5
        R = Matrix.Rotation(math.radians(a), 3, ax)
        v.co = hp + R @ (v.co - hp)
    ob.data.update()


def rot_part(ob, deg, axis, pivot=None):
    c = Vector(pivot) if pivot is not None else K.center_of(ob)
    K.rotate(ob, deg, axis, c)


def jagged_cutter(center, size, seed, rough=0.05, subdiv=1, zone="scorch"):
    bm = bmesh.new()
    bmesh.ops.create_icosphere(bm, subdivisions=subdiv, radius=1.0)
    for v in bm.verts:
        n = noise.noise(v.co * 2.3 + Vector((seed, seed * 0.5, 0)))
        v.co = Vector((v.co.x * size[0], v.co.y * size[1], v.co.z * size[2])) * (1 + n * rough * 4)
        v.co += Vector(center)
    me = bpy.data.meshes.new("cutter")
    bm.to_mesh(me)
    bm.free()
    cutter_paint(me, zone)
    ob = bpy.data.objects.new("cutter", me)
    K.collection("work").objects.link(ob)
    return ob


def slab_cutter(z_cut, half_w, half_d, seed, amp=0.06, top=50.0, res=5, tilt=(0.0, 0.0), zone="scorch"):
    """Big box whose underside is a jagged break surface at about z_cut (everything above is cut)."""
    bm = bmesh.new()
    verts = {}
    W, D = half_w * 1.6, half_d * 1.6
    for i in range(res + 1):
        for j in range(res + 1):
            x = -W + 2 * W * i / res
            y = -D + 2 * D * j / res
            n = noise.noise(Vector((x * 4.1 + seed, y * 4.1, seed * 0.37)))
            z = z_cut + n * amp + x * tilt[0] + y * tilt[1]
            verts[(i, j)] = bm.verts.new((x, y, z))
    topv = {}
    for i in range(res + 1):
        for j in range(res + 1):
            x, y, _ = verts[(i, j)].co
            topv[(i, j)] = bm.verts.new((x, y, z_cut + top))
    for i in range(res):
        for j in range(res):
            bm.faces.new((verts[(i, j)], verts[(i, j + 1)], verts[(i + 1, j + 1)], verts[(i + 1, j)]))
            bm.faces.new((topv[(i, j)], topv[(i + 1, j)], topv[(i + 1, j + 1)], topv[(i, j + 1)]))
    for k in range(res):
        for (a, b) in (((k, 0), (k + 1, 0)), ((res, k), (res, k + 1)), ((k + 1, res), (k, res)), ((0, k + 1), (0, k))):
            bm.faces.new((verts[a], verts[b], topv[b], topv[a]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    me = bpy.data.meshes.new("slab")
    bm.to_mesh(me)
    bm.free()
    cutter_paint(me, zone)
    ob = bpy.data.objects.new("slab", me)
    K.collection("work").objects.link(ob)
    return ob


def boolean(ob, cutter, op="DIFFERENCE"):
    m = ob.modifiers.new("b", "BOOLEAN")
    m.object = cutter
    m.operation = op
    m.solver = "EXACT"
    try:
        m.material_mode = "TRANSFER"
    except Exception:
        pass
    ctx = bpy.context
    ctx.view_layer.objects.active = ob
    try:
        bpy.ops.object.modifier_apply(modifier=m.name)
    except RuntimeError:
        ob.modifiers.remove(m)
    return ob


def intersects(ob, cutter):
    a0, a1 = K.bounds([ob])
    b0, b1 = K.bounds([cutter])
    return all(a0[i] <= b1[i] and b0[i] <= a1[i] for i in range(3))


# ------------------------------------------------------------------------------------------
# Glass shards (radial crack cells clipped to the pane)
# ------------------------------------------------------------------------------------------
def _clip(poly, a, b, c):
    """Keep the side a*x + b*y <= c of a convex polygon."""
    out = []
    n = len(poly)
    for i in range(n):
        P, Q = poly[i], poly[(i + 1) % n]
        fp, fq = a * P[0] + b * P[1] - c, a * Q[0] + b * Q[1] - c
        if fp <= 0:
            out.append(P)
        if (fp <= 0) != (fq <= 0):
            t = fp / (fp - fq)
            out.append((P[0] + (Q[0] - P[0]) * t, P[1] + (Q[1] - P[1]) * t))
    return out


def shard_cells(w, h, impact, rng, spokes=7, rings=(0.12, 0.3, 0.7)):
    rect = [(-w / 2, -h / 2), (w / 2, -h / 2), (w / 2, h / 2), (-w / 2, h / 2)]
    ix, iy = impact
    angles = sorted(rng.uniform(0, 2 * math.pi) for _ in range(spokes))
    cells = []
    radii = [0.0] + [r * max(w, h) for r in rings] + [10.0]
    for k in range(spokes):
        a0, a1 = angles[k], angles[(k + 1) % spokes] + (2 * math.pi if k == spokes - 1 else 0)
        if a1 - a0 > math.pi * 0.95:
            mid = (a0 + a1) / 2
            parts_a = [(a0, mid), (mid, a1)]
        else:
            parts_a = [(a0, a1)]
        for (b0, b1) in parts_a:
            wedge = rect
            # half-planes bounding the wedge
            n0 = (-math.sin(b0), math.cos(b0))   # left of ray b0 -> keep side where cross >= 0
            wedge = _clip(wedge, -n0[0], -n0[1], -(n0[0] * ix + n0[1] * iy))
            n1 = (math.sin(b1), -math.cos(b1))
            wedge = _clip(wedge, -n1[0], -n1[1], -(n1[0] * ix + n1[1] * iy))
            if len(wedge) < 3:
                continue
            for j in range(len(radii) - 1):
                r0, r1 = radii[j], radii[j + 1]
                cell = wedge
                bm_ = (b0 + b1) / 2
                ca, sa = math.cos(bm_), math.sin(bm_)
                jitter0 = r0 * rng.uniform(0.85, 1.15)
                jitter1 = r1 * rng.uniform(0.85, 1.15)
                if r0 > 0:
                    cell = _clip(cell, -ca, -sa, -(ca * ix + sa * iy + jitter0))
                cell = _clip(cell, ca, sa, ca * ix + sa * iy + jitter1)
                if len(cell) >= 3:
                    area = 0.5 * abs(sum(cell[i][0] * cell[(i + 1) % len(cell)][1] -
                                         cell[(i + 1) % len(cell)][0] * cell[i][1] for i in range(len(cell))))
                    if area > 1e-4:
                        cells.append((cell, j))
    return cells


def glass_shards(B, center, w, h, thick, impact, rng, gap=0.004, slot="glass", spokes=7):
    """Build shards of a pane in the XZ plane (normal -Y) at center. Returns list of (obj, ring)."""
    out = []
    cx, cy, cz = center
    for cell, ring in shard_cells(w, h, impact, rng, spokes):
        mx = sum(p[0] for p in cell) / len(cell)
        mz = sum(p[1] for p in cell) / len(cell)
        shrunk = []
        for (x, z) in cell:
            d = Vector((x - mx, z - mz))
            L = d.length
            s = max(0.0, L - gap) / L if L > 0 else 0
            shrunk.append((mx + d.x * s, mz + d.y * s))
        ob = B.prism(shrunk, thick, 0.0, slot, "glass", 0.0)
        K.translate(ob, (cx, cy, cz))
        ob["ring"] = ring
        out.append(ob)
    return out
