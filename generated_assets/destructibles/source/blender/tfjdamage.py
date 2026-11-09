"""Progressive damage: light (dents, cracks, loosened plates), heavy (missing panels, bent plates,
bitten frame, shattered glass, exposed internals, malfunction emission), destroyed (collapsed husk
plus separate visual-only fragments). Every state is derived from the same intact parts."""
import bpy, bmesh, math, random
from mathutils import Vector, Matrix
import tfjkit as K
import tfjpipe as P

FRONT_IN = Vector((0, 1, 0))  # pushing into the front face (front faces -Y)


def _face_point(ob, rng, side="front"):
    mn, mx = K.bounds([ob])
    if side == "front":
        return Vector((rng.uniform(mn.x, mx.x), mn.y, rng.uniform(mn.z, mx.z))), FRONT_IN
    if side == "left":
        return Vector((mn.x, rng.uniform(mn.y, mx.y), rng.uniform(mn.z, mx.z))), Vector((1, 0, 0))
    return Vector((rng.uniform(mn.x, mx.x), rng.uniform(mn.y, mx.y), mx.z)), Vector((0, 0, -1))


def _size(ob):
    mn, mx = K.bounds([ob])
    return mx - mn


def _swap_material(ob, slot):
    m, zone = K.slot_material(slot)
    ob.data.materials.clear()
    ob.data.materials.append(m)
    ob["zone"] = zone or ""


def _shatter(B, pane_ob, rng, level):
    cx, cy, cz, w, h, t = pane_ob["pane"]
    slot = pane_ob.get("pane_slot", "glass")
    impact = (rng.uniform(-w * 0.25, w * 0.25), rng.uniform(-h * 0.2, h * 0.25))
    shards = P.glass_shards(B, (0, 0, 0), w, h, t, impact, rng, gap=0.003 if level == 1 else 0.006,
                            slot=slot, spokes=6 if level == 1 else 8)
    for s in shards:
        if pane_ob.get("pane_normal", "Y") == "X":
            K.rotate(s, 90, "Z")
        K.translate(s, (cx, cy, cz))
    B.parts = [p for p in B.parts if p not in shards]  # shards are tracked by caller
    keep = []
    for s in shards:
        ring = s["ring"]
        if level == 1:
            P.rot_part(s, rng.uniform(-0.6, 0.6), "Z")
            P.rot_part(s, rng.uniform(-0.6, 0.6), "X")
            keep.append(s)
        else:
            if ring <= 1 and rng.random() < 0.85 or rng.random() < 0.3:
                P.remove([s])
                continue
            P.rot_part(s, rng.uniform(-5, 5), "Z")
            P.rot_part(s, rng.uniform(-8, 8), "X")
            K.translate(s, (0, rng.uniform(-0.01, 0.006), rng.uniform(-0.01, 0.0)))
            keep.append(s)
    for s in keep:
        s["role"] = "glass"
    return keep


def light(B, parts, rng, size):
    w, h, d = size
    out = []
    for p in parts:
        role = p.get("role")
        if role == "pane":
            out += _shatter(B, p, rng, 1)
            P.remove([p])
            continue
        if role == "cover" and rng.random() < 0.4:
            P.densify(p, 2)
            pt, n = _face_point(p, rng)
            s = _size(p)
            P.dent(p, pt, max(s.x, s.z) * rng.uniform(0.4, 0.7), min(0.03, max(s.x, s.z) * 0.09), n)
            r = rng.random()
            if r < 0.3:
                P.rot_part(p, rng.choice([-1, 1]) * rng.uniform(2.5, 5.5), "Y")
            elif r < 0.45:
                mn, mx = K.bounds([p])
                P.bend(p, Vector(((mn.x + mx.x) / 2, mn.y, mx.z)), (1, 0, 0), rng.uniform(5, 10))
        elif role == "frame" and rng.random() < 0.25:
            P.densify(p, 1, max_edge=0.15, normal=None, min_area=0.004)
            pt, n = _face_point(p, rng, rng.choice(["front", "left", "top"]))
            P.dent(p, pt, 0.06, 0.008, n)
        elif role == "greeble" and rng.random() < 0.12:
            P.rot_part(p, rng.uniform(-9, 9), rng.choice("XYZ"))
        elif role == "emit":
            r = rng.random()
            if r < 0.14:
                _swap_material(p, "emit2")
            elif r < 0.3:
                _swap_material(p, "internal")
        out.append(p)
    return out


def heavy(B, parts, rng, size, cover_loss=0.45, bites=2):
    w, h, d = size
    out = []
    sparks = []
    covers = [p for p in parts if p.get("role") == "cover"]
    lose = set(rng.sample(range(len(covers)), int(len(covers) * cover_loss))) if covers else set()
    for p in parts:
        role = p.get("role")
        if role == "pane":
            out += _shatter(B, p, rng, 2)
            P.remove([p])
            continue
        if role == "cover":
            idx = covers.index(p)
            if idx in lose:
                sparks.append(K.center_of(p))
                P.remove([p])
                continue
            P.densify(p, 2)
            pt, n = _face_point(p, rng)
            s = _size(p)
            P.dent(p, pt, max(s.x, s.z) * 0.6, min(0.04, max(s.x, s.z) * 0.1), n)
            if rng.random() < 0.35:
                mn, mx = K.bounds([p])
                top = rng.random() < 0.6
                hinge = Vector(((mn.x + mx.x) / 2, mn.y, mx.z if top else mn.z))
                P.bend(p, hinge, (1, 0, 0), rng.uniform(14, 32) * (1 if top else -1))
            elif rng.random() < 0.4:
                P.rot_part(p, rng.uniform(-8, 8), "Y")
            p["scorched"] = rng.uniform(0.55, 0.85)
        elif role == "frame":
            p["scorched"] = rng.uniform(0.65, 0.9)
        elif role == "internal":
            p["scorched"] = rng.uniform(0.5, 0.8)
            if rng.random() < 0.25:
                P.rot_part(p, rng.uniform(-10, 10), rng.choice("XY"))
        elif role == "greeble":
            if rng.random() < 0.3:
                P.remove([p])
                continue
            if rng.random() < 0.3:
                P.rot_part(p, rng.uniform(-20, 20), rng.choice("XYZ"))
        elif role == "vessel":
            # glass vessel: a jagged hole punched through the front, upper half
            mn, mx = K.bounds([p])
            sz = mx - mn
            cz = rng.uniform(mn.z + sz.z * 0.45, mx.z - sz.z * 0.2)
            cut = P.jagged_cutter((rng.uniform(-sz.x, sz.x) * 0.15 + (mn.x + mx.x) / 2, mn.y, cz),
                                  (sz.x * 0.32, sz.y * 0.45, sz.z * 0.22), rng.random() * 50, 0.05)
            P.boolean(p, cut)
            P.remove([cut])
            sparks.append(Vector(((mn.x + mx.x) / 2, mn.y, cz)))
        elif role == "medium":
            mn, mx = K.bounds([p])
            K.scale(p, (1.0, 1.0, rng.uniform(0.3, 0.5)), (0, 0, mn.z))
        elif role == "emit":
            r = rng.random()
            if r < 0.55:
                _swap_material(p, "internal")
            elif r < 0.85:
                _swap_material(p, "emit2")
        out.append(p)
    # frame bites: jagged chunks out of the silhouette edges
    frames = [p for p in out if p.get("role") == "frame"]
    for k in range(bites):
        cx = rng.choice([-1, 1]) * w * rng.uniform(0.3, 0.5)
        cz = rng.uniform(-h * 0.1, h * 0.5)
        r = min(w, h) * rng.uniform(0.18, 0.28)
        cut = P.jagged_cutter((cx, -d * rng.uniform(0.1, 0.5), cz), (r, d * 0.45, r * 1.2), rng.random() * 50, 0.06)
        for f in frames:
            if P.intersects(f, cut):
                P.boolean(f, cut)
        sparks.append(Vector((cx, -d / 2, cz)))
        P.remove([cut])
    # loose cables hanging from exposed areas
    for k in range(min(2, len(sparks))):
        a = sparks[k] + Vector((0, rng.uniform(0.02, 0.1), 0))
        b = a + Vector((rng.uniform(-0.12, 0.12), -rng.uniform(0.02, 0.06), -rng.uniform(0.12, 0.3)))
        b.z = max(b.z, -h / 2 + 0.03)
        out.append(B.cable_run(a, b, sag=0.03, radius=0.008, n=8))
        out[-1]["role"] = "cable"
    return out, sparks[:6]


def destroyed(B, parts, rng, size, cut_frac=(0.38, 0.6), lean=5.0, n_frags=7):
    """Returns (husk_parts, fragment_groups). The husk is the lower part of the same object, cut along a
    jagged break and slumped; fragments are the broken-off upper sections, crumpled covers and shards."""
    w, h, d = size
    z0 = -h / 2
    keep, frags = [], []
    for p in parts:
        role = p.get("role")
        if role in ("emit", "medium"):
            _swap_material(p, "internal")
            p["scorched"] = 0.6
        if role == "medium":
            mn, mx = K.bounds([p])
            K.scale(p, (1.0, 1.0, 0.15), (0, 0, mn.z))
        if role == "vessel":
            P.remove([p])
            continue
        if role == "pane":
            sh = _shatter(B, p, rng, 2)
            frags += [[s] for s in sh[:2]]
            P.remove(sh[2:])
            P.remove([p])
            continue
        keep.append(p)
    covers = [p for p in keep if p.get("role") == "cover"]
    rng.shuffle(covers)
    for c in covers[:3]:
        keep.remove(c)
        P.densify(c, 1, normal=None)
        P.crumple(c, 0.01, rng.random() * 10)
        sz = _size(c)
        P.bend(c, K.center_of(c), (1, 0, 0) if sz.x >= sz.y else (0, 1, 0), rng.uniform(-30, 30), (0, 0, 1),
               max(sz.z, 0.05))
        c["scorched"] = 0.6
        frags.append([c])
    for p in keep:
        p["scorched"] = min(p.get("scorched", 1.0), rng.uniform(0.55, 0.8))
    zc = z0 + h * rng.uniform(*cut_frac)
    tilt = (rng.uniform(-0.3, 0.3) * min(1.0, h / max(w, 0.1)) * 0.4, rng.uniform(-0.1, 0.1))
    slab = P.slab_cutter(zc, max(w, 0.3) / 2 + 0.2, d / 2 + 0.2, rng.random() * 100, amp=min(0.07, h * 0.1),
                         tilt=tilt)
    upper, husk = [], []
    for p in keep:
        mn, mx = K.bounds([p])
        if mn.z > zc + 0.1:
            upper.append(p)
            continue
        if mx.z > zc - 0.1:
            top = P.clone([p], "_up")[0]
            P.boolean(top, slab, "INTERSECT")
            if len(top.data.polygons) > 0 and top.get("role") in ("frame", "cover", "internal"):
                upper.append(top)
            else:
                P.remove([top])
            P.boolean(p, slab, "DIFFERENCE")
            if len(p.data.polygons) == 0:
                P.remove([p])
                continue
        husk.append(p)
    P.remove([slab])
    # broken-off upper section: split into 2-3 spatial chunks (by the longer axis)
    upper = [u for u in upper if u.get("role") not in ("emit", "cable")] + \
            [u for u in upper if u.get("role") in ("emit", "cable") and P.remove([u])]
    nchunk = 2 if len(upper) < 8 else 3
    axis = 0 if w >= h else 2
    if upper:
        cs = sorted(upper, key=lambda u: K.center_of(u)[axis])
        lo_v = K.center_of(cs[0])[axis]
        hi_v = K.center_of(cs[-1])[axis] + 1e-6
        groups = [[] for _ in range(nchunk)]
        for u in cs:
            k = min(nchunk - 1, int((K.center_of(u)[axis] - lo_v) / (hi_v - lo_v) * nchunk))
            groups[k].append(u)
        for g in groups:
            if not g:
                continue
            if len(g) > 14:
                P.remove(g[14:])
                g = g[:14]
            c = Vector((0, 0, 0))
            for u in g:
                c += K.center_of(u)
            c /= len(g)
            ang = rng.uniform(-14, 14)
            for u in g:
                P.crumple(u, 0.004, rng.random() * 10)
                K.rotate(u, ang, "Y", c)
            frags.append(g)
    sign = rng.choice([-1, 1])
    for p in husk:
        K.scale(p, (1.0, 1.0, 0.96), (0, 0, z0))
        K.rotate(p, sign * rng.uniform(lean * 0.4, lean), "Y", (sign * w / 2, 0, z0))
    # lift so the slumped husk still rests on the floor line
    mn, _ = K.bounds(husk) if husk else (Vector((0, 0, z0)), None)
    for p in husk:
        K.translate(p, (0, 0, z0 - mn.z))
    for k in range(rng.randint(3, 5)):
        r = min(w, h, 0.25) * rng.uniform(0.12, 0.22)
        x = rng.uniform(-w * 0.55, w * 0.55)
        rub = B.sphere((x, rng.uniform(-d * 0.4, d * 0.2), z0 + r * 0.45), r, 0, "frame", "rubble",
                       (1.0, 0.8, 0.55))
        P.crumple(rub, r * 0.25, rng.random() * 10, 9.0)
        rub["scorched"] = 0.55
        husk.append(rub)
    return husk, [f for f in frags if f][:10]
