"""tfjbake: bakes a hero asset (weapons, operative) into one unique texture set (ASSET_CONTRACT 11:
weapons one 512 set, operative one 1024 set), so the textured zone slots collapse into a single
material and the detail of a high-poly copy lands in the normal map.

  high poly = the low poly with a 2-segment angle-limited bevel (soft rounded edges)
  low poly  = the game mesh with a unique smart-projected UV
Passes (Cycles, selected to active): DIFFUSE colour (library albedo x zone tint, times a softened
AO), tangent NORMAL, ROUGHNESS, metallic (through a temporary emission link), EMIT and AO.
Outputs <stem>_albedo / _normal / _orm (R occlusion, G roughness, B metallic) / _emission PNGs,
which the glb embeds (self-contained hero files)."""
import bpy, bmesh, math, os
import numpy as np
import tfjkit as K


def _new_image(name, size, colour=True, alpha=False):
    im = bpy.data.images.get(name)
    if im:
        bpy.data.images.remove(im)
    im = bpy.data.images.new(name, size, size, alpha=alpha, float_buffer=not colour)
    im.colorspace_settings.name = "sRGB" if colour else "Non-Color"
    return im


def _select(objs, active):
    for o in bpy.context.view_layer.objects:
        o.select_set(False)
    for o in objs:
        o.select_set(True)
    bpy.context.view_layer.objects.active = active


def _target(mats, im):
    for m in mats:
        nt = m.node_tree
        n = nt.nodes.get("__bake__") or nt.nodes.new("ShaderNodeTexImage")
        n.name = "__bake__"
        n.image = im
        nt.nodes.active = n


def _bake(kind, pairs, im, cage, margin=4, pass_filter=None):
    for i, (low, high) in enumerate(pairs):
        _target([m for m in low.data.materials if m], im)
        if high is None:  # self bake: the low's own material (library normal maps included), no ray misses
            _select([low], low)
            kw = dict(type=kind, use_selected_to_active=False, margin=margin, use_clear=(i == 0))
        else:
            _select([high, low], low)
            kw = dict(type=kind, use_selected_to_active=True, cage_extrusion=cage, max_ray_distance=cage * 4,
                      margin=margin, use_clear=(i == 0))
        if pass_filter:
            kw["pass_filter"] = pass_filter
        bpy.ops.object.bake(**kw)


def _route_bake(mats, socket, use_factor, pairs, im, cage):
    saved = []
    for m in mats:
        nt = m.node_tree
        p = nt.nodes.get("Principled BSDF")
        if p is None:
            continue
        st = dict(m=m, ec=tuple(p.inputs["Emission Color"].default_value), es=p.inputs["Emission Strength"].default_value,
                  links=[(l.from_socket, l.to_socket) for l in nt.links if l.to_node == p and l.to_socket.name == "Emission Color"])
        for l in list(nt.links):
            if l.to_node == p and l.to_socket.name == "Emission Color":
                nt.links.remove(l)
        fac = float(m.get("tfj_metal", 1.0)) if use_factor else 1.0
        src = p.inputs[socket]
        if src.links:
            mm = nt.nodes.new("ShaderNodeMix")
            mm.name = "__route__"
            mm.data_type = "RGBA"
            mm.blend_type = "MULTIPLY"
            mm.inputs["Factor"].default_value = 1.0
            nt.links.new(src.links[0].from_socket, mm.inputs[6])
            mm.inputs[7].default_value = (fac, fac, fac, 1.0)
            nt.links.new(mm.outputs[2], p.inputs["Emission Color"])
        else:
            v = src.default_value
            col = (v * fac, v * fac, v * fac, 1.0) if isinstance(v, float) else tuple(c * fac for c in v[:3]) + (1.0,)
            p.inputs["Emission Color"].default_value = col
        p.inputs["Emission Strength"].default_value = 1.0
        saved.append(st)
    _bake("EMIT", pairs, im, cage)
    for st in saved:
        m = st["m"]
        nt = m.node_tree
        p = nt.nodes.get("Principled BSDF")
        for l in list(nt.links):
            if l.to_node == p and l.to_socket.name == "Emission Color":
                nt.links.remove(l)
        n = nt.nodes.get("__route__")
        if n:
            nt.nodes.remove(n)
        for a, b in st["links"]:
            nt.links.new(a, b)
        p.inputs["Emission Color"].default_value = st["ec"]
        p.inputs["Emission Strength"].default_value = st["es"]


def _px(im):
    a = np.empty(len(im.pixels), dtype=np.float32)
    im.pixels.foreach_get(a)
    return a.reshape(im.size[1], im.size[0], 4)


def bake(lows, stem, size=512, out_dir="/tmp/tfj_bake", high_bevel=0.0025, cage=0.006, emit_strength=1.0,
         samples=16, ao_mix=0.55, slot=None, use_high=True, ao_dist=None, keep=None):
    """lows: one object or a list sharing one atlas (the operative's rigid nodes)."""
    if not isinstance(lows, (list, tuple)):
        lows = [lows]
    os.makedirs(out_dir, exist_ok=True)
    sc = bpy.context.scene
    sc.render.engine = "CYCLES"
    sc.cycles.device = "CPU"
    sc.cycles.samples = samples
    sc.render.bake.use_selected_to_active = use_high
    # world needed for AO / diffuse
    if sc.world is None:
        sc.world = bpy.data.worlds.new("bake_world")
    # AO reach scaled to the asset (default 1 m darkened small hero assets almost to black)
    if ao_dist is None:
        ext = max(max(o.dimensions) for o in lows)
        ao_dist = max(0.02, min(0.25, ext * 0.06))
    sc.world.light_settings.distance = ao_dist
    pairs = []
    for low in lows:
        if not use_high:
            me = low.data
            uv_bake = me.uv_layers.get("bake") or me.uv_layers.new(name="bake")
            me.uv_layers.active = uv_bake
            pairs.append((low, None))
            continue
        high = low.copy()
        high.data = low.data.copy()
        high.name = low.name + "_high"
        high.parent = None
        high.matrix_world = low.matrix_world.copy()
        bpy.context.scene.collection.objects.link(high)
        bm_ = high.modifiers.new("hb", "BEVEL")
        bm_.width = high_bevel
        bm_.segments = 2
        bm_.limit_method = "ANGLE"
        bm_.angle_limit = math.radians(35)
        _select([high], high)
        bpy.ops.object.modifier_apply(modifier=bm_.name)
        for p in high.data.polygons:
            p.use_smooth = True
        try:
            high.data.set_sharp_from_angle(angle=math.radians(60))
        except Exception:
            pass
        me = low.data
        uv_bake = me.uv_layers.get("bake") or me.uv_layers.new(name="bake")
        me.uv_layers.active = uv_bake
        pairs.append((low, high))
    # ---- one shared unique UV layout for every low object (multi-object edit mode)
    _select(lows, lows[0])
    bpy.ops.object.mode_set(mode="EDIT")
    bpy.ops.mesh.select_all(action="SELECT")
    bpy.ops.uv.smart_project(angle_limit=math.radians(60), island_margin=0.01, area_weight=0.0,
                             correct_aspect=True, scale_to_bounds=False)
    try:
        bpy.ops.uv.pack_islands(margin=0.006, rotate=True)
    except Exception:
        pass
    bpy.ops.object.mode_set(mode="OBJECT")
    mats = []
    for low in lows:
        for m in low.data.materials:
            if m and m not in mats:
                mats.append(m)
    ims = {}
    # ---- passes
    ims["nrm"] = _new_image(stem + "_nrm", size, colour=False)
    _bake("NORMAL", pairs, ims["nrm"], cage)
    ims["rgh"] = _new_image(stem + "_rgh", size, colour=False)
    _bake("ROUGHNESS", pairs, ims["rgh"], cage)
    ims["ao"] = _new_image(stem + "_ao", size, colour=False)
    sc.cycles.samples = max(samples, 32)
    _bake("AO", pairs, ims["ao"], cage)
    sc.cycles.samples = samples
    ims["emi"] = _new_image(stem + "_emi", size)
    _bake("EMIT", pairs, ims["emi"], cage)
    # metallic and base colour: route the signal into emission for an EMIT bake each (Cycles' DIFFUSE COLOR
    # pass is base colour x (1 - metallic), which darkened every metal surface)
    ims["met"] = _new_image(stem + "_met", size, colour=False)
    _route_bake(mats, "Metallic", True, pairs, ims["met"], cage)
    ims["col"] = _new_image(stem + "_col2", size)
    _route_bake(mats, "Base Color", False, pairs, ims["col"], cage)
    # ---- compose the output set
    col, ao = _px(ims["col"]), _px(ims["ao"])[..., 0]
    print("BAKE_STATS", stem, "ao_dist", round(ao_dist, 3), "col_mean", float(col[..., :3].mean()), "ao_mean", float(ao.mean()))
    rgh, met = _px(ims["rgh"])[..., 0], _px(ims["met"])[..., 0]
    emi = _px(ims["emi"])
    albedo = col.copy()
    albedo[..., :3] *= (1.0 - ao_mix + ao_mix * ao)[..., None]  # soft occlusion in the albedo (contract 9)
    orm = np.stack([ao, rgh, np.clip(met, 0, 1), np.ones_like(ao)], -1)
    out = {}
    for key, arr, colour in (("albedo", albedo, True), ("normal", _px(ims["nrm"]), False), ("orm", orm, False),
                             ("emission", emi, True)):
        im = _new_image(f"{stem}_{key}", size, colour=colour)
        a = np.clip(arr, 0, 1).astype(np.float32)
        a[..., 3] = 1.0
        im.pixels.foreach_set(a.ravel())
        path = f"{out_dir}/{stem}_{key}.png"
        im.filepath_raw = path
        im.file_format = "PNG"
        im.save()
        out[key] = path
    has_emit = float(emi[..., :3].max()) > 0.02
    # ---- swap the low polys to the baked set
    import tfjtex as TX
    name = slot or f"wpn_{stem}"
    bm = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    paths = dict(albedo=out["albedo"], normal=out["normal"], orm=out["orm"])
    if has_emit:
        paths["emission"] = out["emission"]
    TX.build(bm, paths, tint=(1, 1, 1, 1), emission=(1, 1, 1, 1) if has_emit else None,
             emission_strength=emit_strength)
    bm.use_backface_culling = True
    bm["tfj_kind"] = "baked"
    for low, high in pairs:
        me = low.data
        for u in list(me.uv_layers):
            if u.name != "bake":
                me.uv_layers.remove(u)
        me.uv_layers["bake"].name = "UVMap"
        me.uv_layers.active = me.uv_layers["UVMap"]
        me.materials.clear()
        me.materials.append(bm)
        for p in me.polygons:
            p.material_index = 0
        if high is not None:
            hm = high.data
            bpy.data.objects.remove(high, do_unlink=True)
            bpy.data.meshes.remove(hm)
    return out
