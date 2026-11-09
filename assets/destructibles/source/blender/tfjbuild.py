"""Driver: build one destructible spec into <stem>.glb (mesh_intact, mesh_light, mesh_heavy, fx empties)
and <deb stem>.glb (husk + frag_NN), render preview tiles, return manifest stats."""
import bpy, os, json, math, random, time
from mathutils import Vector
import tfjkit as K
import tfjpipe as P
import tfjdamage as D
import tfjrender as R

REPO = "/workspace/tfj-3d-kits"
GA = REPO + "/assets"


def stem(asset_id):
    return asset_id.lower().replace("-", "_")


def _set_origin(ob):
    mn, mx = K.bounds([ob])
    c = (mn + mx) / 2
    K.translate(ob, -c)
    ob.location = c
    return c


def _empty(name, loc, parent):
    e = bpy.data.objects.new(name, None)
    e.empty_display_size = 0.05
    e.location = loc
    e.parent = parent
    bpy.context.scene.collection.objects.link(e)
    return e


def build(spec, out_dir=None, tiles_dir="/tmp/tfj_tiles", render=True, samples=40, tile=420):
    t0 = time.time()
    K.reset_scene()
    ch, mat = spec["chapter"], spec["material"]
    K.set_ctx(ch, mat, spec.get("emit"), spec.get("emit2"), spec.get("glass", "clear"))
    w, h, d = spec["w"], spec["h"], spec["d"]
    seed = spec.get("seed", hash(spec["id"]) & 0xffff)
    B = K.Builder(stem(spec["id"]), seed)
    spec["build"](B, w, h, d, random.Random(seed), spec)
    base = list(B.parts)
    fit_envelope(base, w, h, d, spec["id"])
    rt = {}
    for p in base:
        rt[p.get("role")] = rt.get(p.get("role"), 0) + sum(len(f.vertices) - 2 for f in p.data.polygons)
    print("ROLE_TRIS", spec["id"], rt)
    sid = stem(spec["id"])
    out_dir = out_dir or f"{GA}/{spec.get('category', 'destructibles')}/{ch}"
    stats = dict(id=spec["id"], file=f"{out_dir}/{sid}.glb")

    # ---- states ---------------------------------------------------------------------------
    rng = random.Random(seed + 1)
    light_parts = D.light(B, P.clone(base, "_l"), rng, (w, h, d))
    rng = random.Random(seed + 2)
    heavy_parts, sparks = D.heavy(B, P.clone(base, "_h"), rng, (w, h, d), spec.get("cover_loss", 0.45),
                                  spec.get("bites", 2))
    rng = random.Random(seed + 3)
    husk_parts, frag_groups = D.destroyed(B, P.clone(heavy_parts, "_d"), rng, (w, h, d),
                                          spec.get("cut_frac", (0.28, 0.5)), spec.get("lean", 8.0))

    budget = 3000 if spec.get("critical") or spec.get("hero") else 1500
    intact = P.pack(P.clone(base, "_i"), "mesh_intact")
    it = K.tri_count(intact)
    state_budget = max(budget, int(it * 1.1))
    light_ob = P.pack(light_parts, "mesh_light", budget=state_budget)
    heavy_ob = P.pack(heavy_parts, "mesh_heavy", budget=state_budget)
    # state geometry may leave the intact bounds by at most 0.10 m (contract section 8): pull outlying
    # flaps back inside a 0.08 m margin
    imn, imx = K.bounds([intact])
    for o in (light_ob, heavy_ob):
        moved = 0
        for v in o.data.vertices:
            for i in range(3):
                lo, hi = imn[i] - 0.08, imx[i] + 0.08
                if v.co[i] < lo or v.co[i] > hi:
                    v.co[i] = min(hi, max(lo, v.co[i]))
                    moved += 1
        if moved:
            o.data.update()
            print("STATE_CLAMP", spec["id"], o.name, moved)
    # debris set total <= 1.5 x intact (contract section 12)
    deb_total = 0
    for g in [husk_parts] + frag_groups:
        deb_total += sum(sum(len(f.vertices) - 2 for f in p.data.polygons) for p in g)
    deb_budget = int(it * 1.5)
    ratio = min(1.0, deb_budget / max(1, deb_total))
    husk = P.pack(husk_parts, "husk", budget=int(sum(sum(len(f.vertices) - 2 for f in p.data.polygons) for p in husk_parts) * ratio) if ratio < 1 else None)
    frags = []
    for i, g in enumerate(frag_groups):
        gt = sum(sum(len(f.vertices) - 2 for f in p.data.polygons) for p in g)
        f = P.pack(g, f"frag_{i + 1:02d}", ao=False, budget=int(gt * ratio) if ratio < 1 else None)
        frags.append(f)
    if intact and it > budget:
        print("BUDGET_WARNING", spec["id"], "intact", it, ">", budget)
    for o in [intact, light_ob, heavy_ob, husk] + frags:
        if o.name not in bpy.context.scene.collection.objects:
            pass

    # hide build collections
    for c in bpy.data.collections:
        c.hide_render = True
        c.hide_viewport = True

    root = bpy.data.objects.new(sid, None)
    bpy.context.scene.collection.objects.link(root)
    for o in (intact, light_ob, heavy_ob):
        o.parent = root
    empties = []
    for i, s in enumerate(sparks):
        empties.append(_empty(f"fx_spark_{i + 1:02d}", s, root))
    for i, g in enumerate(spec.get("glow", [])):
        empties.append(_empty(f"fx_glow_{i + 1:02d}", Vector(g), root))
    for i, g in enumerate(spec.get("smoke", [(0, 0, h * 0.3)])):
        empties.append(_empty(f"fx_smoke_{i + 1:02d}", Vector(g), root))
    size_c = K.export_glb([root, intact, light_ob, heavy_ob] + empties, stats["file"])

    did = spec["id"].replace("-CMP-", "-DEB-")
    dstem = stem(did)
    droot = bpy.data.objects.new(dstem, None)
    bpy.context.scene.collection.objects.link(droot)
    husk_c = _set_origin(husk)
    husk.parent = droot
    for f in frags:
        _set_origin(f)
        f.parent = droot
    stats["debris_file"] = f"{out_dir}/{dstem}.glb"
    size_d = K.export_glb([droot, husk] + frags, stats["debris_file"])
    stats.update(
        debris_id=did,
        tris=dict(intact=K.tri_count(intact), light=K.tri_count(light_ob), heavy=K.tri_count(heavy_ob),
                  debris=K.tri_count(husk) + sum(K.tri_count(f) for f in frags)),
        fragments=len(frags) + 1,
        bytes=size_c, debris_bytes=size_d,
        materials=sorted({m.name for o in (intact, light_ob, heavy_ob) for m in o.data.materials}),
        fx=[e.name for e in empties],
    )
    mn, mx = K.bounds([intact])
    stats["bounds_m"] = [[round(v, 4) for v in mn], [round(v, 4) for v in mx]]

    # ---- preview tiles ----------------------------------------------------------------------
    if render:
        tiles = []
        preview_materials()
        cam = R.setup((tile, tile), samples, floor=True, floor_z=-h / 2)
        # the floor sits at the bottom of the physics rectangle
        for o in bpy.context.scene.objects:
            if o.type == "MESH" and o.name != "floor":
                o.hide_render = True
        for name, obs in (("intact", [intact]), ("light", [light_ob]), ("heavy", [heavy_ob])):
            for o in obs:
                o.hide_render = False
            R.frame([intact], cam, 1.15)
            path = f"{tiles_dir}/{sid}_{name}.png"
            R.render(path)
            tiles.append(path)
            for o in obs:
                o.hide_render = True
        # destroyed: husk where it stood, fragments laid flat on the floor either side of it
        drng = random.Random(seed + 9)
        floor = -h / 2
        hmn, hmx = K.bounds([husk])
        ext = {("L", 0): hmn.x, ("R", 0): hmx.x, ("L", 1): hmn.x + 0.15 * w, ("R", 1): hmx.x - 0.15 * w}
        for i, f in enumerate(frags):
            sz = K.bounds([f])[1] - K.bounds([f])[0]
            dims = [sz.x, sz.y, sz.z]
            small = dims.index(min(dims))
            f.rotation_euler = (math.radians(90), 0, 0) if small == 1 else (0, math.radians(90), 0) if small == 0 else (0, 0, 0)
            f.rotation_euler.z = drng.uniform(-0.6, 0.6)
            bpy.context.view_layer.update()
            mn, mx = K.bounds([f])
            fw = mx.x - mn.x
            side = "R" if i % 2 == 0 else "L"
            row = (i // 2) % 2
            gap = 0.02 + drng.uniform(0, 0.04)
            if side == "R":
                f.location.x += (ext[(side, row)] + gap) - mn.x
                ext[(side, row)] += gap + fw
            else:
                f.location.x += (ext[(side, row)] - gap) - mx.x
                ext[(side, row)] -= gap + fw
            ty = (hmn.y - 0.05 - (mx.y - mn.y) / 2) if row == 1 else (hmx.y * 0.3)
            f.location.y += ty - (mn.y + mx.y) / 2
            f.location.z += floor - mn.z
        bpy.context.view_layer.update()
        for o in [husk] + frags:
            o.hide_render = False
        bpy.context.view_layer.update()
        R.frame([husk] + frags + [intact], cam, 1.05)
        path = f"{tiles_dir}/{sid}_destroyed.png"
        R.render(path)
        tiles.append(path)
        stats["tiles"] = tiles
    stats["seconds"] = round(time.time() - t0, 1)
    return stats


def fit_envelope(parts, w, h, d, sid, tol=0.004):
    """Scale parts about the origin so nothing leaves the collision rectangle (X, Z) or the depth (Y)."""
    mn, mx = K.bounds(parts)
    lim = (w / 2 + tol, d / 2 + tol, h / 2 + tol)
    s = []
    for i in range(3):
        ext = max(abs(mn[i]), abs(mx[i]))
        s.append(min(1.0, lim[i] / ext) if ext > 0 else 1.0)
    if any(v < 0.9999 for v in s):
        print("FIT", sid, [round(v, 4) for v in s])
        for p in parts:
            K.scale(p, s)
    mn, mx = K.bounds(parts)
    c = (mn + mx) / 2
    if abs(c.x) > 0.015 or abs(c.z) > 0.015:
        print("CENTRE_WARNING", sid, [round(v, 3) for v in c])


def preview_materials():
    """Preview-only shading: multiply base colour by COLOR_0 (as Godot does with vertex colours)."""
    for m in bpy.data.materials:
        if m.get("preview_done") or m.get("tfj_kind") == "baked":
            continue
        if m.get("tfj_textured"):  # textured slot: put COLOR_0 after the tint multiply
            nt = m.node_tree
            p = nt.nodes.get("Principled BSDF")
            src = p.inputs["Base Color"].links[0].from_socket
            attr = nt.nodes.new("ShaderNodeVertexColor")
            attr.layer_name = "Col"
            mix = nt.nodes.new("ShaderNodeMix")
            mix.data_type = "RGBA"
            mix.blend_type = "MULTIPLY"
            mix.inputs[0].default_value = 1.0
            nt.links.new(src, mix.inputs[6])
            nt.links.new(attr.outputs[0], mix.inputs[7])
            nt.links.new(mix.outputs[2], p.inputs["Base Color"])
            if p.inputs["Metallic"].links and m.get("tfj_metal") is not None:  # same metallicFactor as the glb
                msrc = p.inputs["Metallic"].links[0].from_socket
                mm = nt.nodes.new("ShaderNodeMath")
                mm.operation = "MULTIPLY"
                mm.inputs[1].default_value = float(m["tfj_metal"])
                nt.links.new(msrc, mm.inputs[0])
                nt.links.new(mm.outputs[0], p.inputs["Metallic"])
            m["preview_done"] = True
            continue
        if m.get("tfj_kind") != "main":
            continue
        nt = m.node_tree
        p = nt.nodes.get("Principled BSDF")
        attr = nt.nodes.new("ShaderNodeVertexColor")
        attr.layer_name = "Col"
        mix = nt.nodes.new("ShaderNodeMix")
        mix.data_type = "RGBA"
        mix.blend_type = "MULTIPLY"
        mix.inputs[0].default_value = 1.0
        mix.inputs[6].default_value = p.inputs["Base Color"].default_value
        nt.links.new(attr.outputs[0], mix.inputs[7])
        nt.links.new(mix.outputs[2], p.inputs["Base Color"])
        m["preview_done"] = True


def contact_sheet(rows, path, label=True, cell=None):
    """rows: list of (label, [tile paths]). Writes a WebP sheet."""
    from PIL import Image, ImageDraw, ImageFont
    ims = [[Image.open(t).convert("RGB") for t in r[1]] for r in rows]
    cw = cell or ims[0][0].size[0]
    ncol = max(len(r) for r in ims)
    lab_h = 26 if label else 0
    W, H = ncol * cw, len(ims) * (cw + lab_h)
    sheet = Image.new("RGB", (W, H), (21, 25, 30))
    dr = ImageDraw.Draw(sheet)
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 15)
    except Exception:
        font = ImageFont.load_default()
    for j, (r, row) in enumerate(zip(rows, ims)):
        y = j * (cw + lab_h)
        if label:
            dr.text((8, y + 5), r[0], fill=(170, 180, 190), font=font)
        for i, im in enumerate(row):
            sheet.paste(im.resize((cw, cw)), (i * cw, y + lab_h))
    os.makedirs(os.path.dirname(path), exist_ok=True)
    sheet.save(path, "WEBP", quality=86, method=6)
    return path
