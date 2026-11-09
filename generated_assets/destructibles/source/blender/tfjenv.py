"""Driver for single-state pieces (environment modules, statics, props, landmarks, weapons):
build parts -> one packed mesh (paint zones become material slots, layer value scales baseColorFactor) -> glb with
root node = file stem, child mesh_intact, optional marker empties -> preview tile."""
import bpy, os, math, random, time
from mathutils import Vector
import tfjkit as K
import tfjpipe as P
import tfjrender as R
import tfjbuild as TB

GA = TB.GA


def scale_value(ob, v):
    if v >= 0.999:
        return
    attr = ob.data.color_attributes.get("Col")
    if attr is None:
        return
    for d in attr.data:
        c = d.color
        d.color = (c[0] * v, c[1] * v, c[2] * v, 1.0)


def build(spec, out_dir=None, tiles_dir="/tmp/tfj_tiles", render=True, samples=40, tile=420):
    t0 = time.time()
    K.reset_scene()
    ch = spec["chapter"]
    K.set_ctx(ch, spec["material"], spec.get("emit"), spec.get("emit2"), spec.get("glass", "clear"))
    K.CTX["value"] = spec.get("value", 1.0)  # layer darkening goes into baseColorFactor
    K.CTX["matte"] = 0.78 if spec.get("layer") in ("floor", "near", "mid", "landmark") else None
    K.CTX["floor_layer"] = spec.get("layer") == "floor" and spec.get("kind", "").startswith("floor")
    seed = spec.get("seed", hash(spec["id"]) & 0xffff)
    sid = TB.stem(spec["id"])
    B = K.Builder(sid, seed)
    markers = spec["build"](B, random.Random(seed), spec) or {}
    parts = list(B.parts)
    if spec.get("fit"):
        w, h, d = spec["fit"]
        TB.fit_envelope(parts, w, h, d, spec["id"])
    budget = spec.get("budget", 2000)
    pre = sum(sum(len(f.vertices) - 2 for f in p.data.polygons) for p in parts)
    print("PRE_TRIS", spec["id"], pre)
    ob = P.pack(parts, "mesh_intact", ao=False, budget=budget if pre > budget else None)
    P.bake_ao(ob, dist=spec.get("ao_dist", 0.12), samples=16)
    scale_value(ob, spec.get("value", 1.0))
    if spec.get("bake"):  # hero assets: one unique baked set (contract 11), no COLOR_0
        import tfjbake
        for c in bpy.data.collections:  # the builder parts overlap the packed mesh: hide them from the bake rays
            c.hide_render = True
            c.hide_viewport = True
        K.CTX["baking"] = True
        K.materialise([ob])
        tfjbake.bake(ob, sid, spec["bake"], emit_strength=spec.get("emit_strength", 1.6),
                     high_bevel=spec.get("high_bevel", 0.0025), cage=spec.get("cage", 0.006),
                     use_high=spec.get("bake_high", False), ao_mix=spec.get("ao_mix", 0.4))
        K.CTX["vcol"] = False
    for c in bpy.data.collections:
        c.hide_render = True
        c.hide_viewport = True
    root = bpy.data.objects.new(sid, None)
    bpy.context.scene.collection.objects.link(root)
    ob.parent = root
    empties = []
    for name, loc in markers.items():
        empties.append(TB._empty(name, Vector(loc), root))
    out_dir = out_dir or f"{GA}/{spec['category']}/{spec.get('folder', ch)}"
    path = f"{out_dir}/{sid}.glb"
    size = K.export_glb([root, ob] + empties, path)
    mn, mx = K.bounds([ob])
    st = dict(id=spec["id"], file=path, tris=dict(intact=K.tri_count(ob)), bytes=size,
              materials=sorted({m.name for m in ob.data.materials}), fx=[e.name for e in empties],
              bounds_m=[[round(v, 4) for v in mn], [round(v, 4) for v in mx]])
    if K.tri_count(ob) > budget:
        print("BUDGET_WARNING", spec["id"], K.tri_count(ob), ">", budget)
    if render:
        TB.preview_materials()
        cam = R.setup((tile, tile), samples, floor=spec.get("floor", True), floor_z=mn.z if spec.get("floor_at_min", True) else 0.0)
        R.frame([ob], cam, spec.get("frame", 1.12))
        tp = f"{tiles_dir}/{sid}.png"
        R.render(tp)
        st["tiles"] = [tp]
    st["seconds"] = round(time.time() - t0, 1)
    return st
