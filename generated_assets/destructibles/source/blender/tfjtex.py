"""tfjtex: binds the surfaces stream's tileable texture library (generated_assets/materials/) to
kit material slots, and rewrites exported glb files so they reference the library PNGs by
relative URI instead of embedding copies (ASSET_CONTRACT 7: shared textures; no duplication).

Node layout per textured slot (what the Blender glTF exporter maps 1:1):
  albedo image -> Mix(MULTIPLY, tint) -> Base Color        => baseColorTexture * baseColorFactor
  orm image -> Separate Color: G -> Roughness, B -> Metallic, R -> glTF occlusion
  normal image -> Normal Map(strength) -> Normal           => normalTexture (scale)
  emission mask image -> Emission Color, strength          => emissiveTexture * emissiveFactor
"""
import os, json, struct
try:
    import bpy
except ImportError:  # the glb post-process also runs outside Blender
    bpy = None

GA = "/workspace/tfj-3d-kits/generated_assets"
LIB = GA + "/materials"
CODE = {"helix": "hlx", "vita": "vta", "nova_grid": "nvg", "civitas": "cvt", "meridian": "mrd"}


def set_paths(ch, mat):
    """Return dict(albedo, normal, orm, emission?) for a chapter set or a shared set ('shr:<name>')."""
    if ch == "shr" or mat.startswith("shr:"):
        name = mat.split(":", 1)[-1]
        base = f"{LIB}/shared/shr_mat_{name}_a"
    else:
        base = f"{LIB}/{ch}/{CODE[ch]}_mat_{mat}_a"
    out = {}
    for k in ("albedo", "normal", "orm", "emission"):
        p = f"{base}_{k}.png"
        if os.path.exists(p):
            out[k] = p
    if "albedo" not in out:
        raise FileNotFoundError(base)
    return out


def _img(path, colour=True):
    name = os.path.basename(path)
    im = bpy.data.images.get(name)
    if im is None:
        im = bpy.data.images.load(path, check_existing=True)
        im.name = name
    try:
        im.colorspace_settings.name = "sRGB" if colour else "Non-Color"
    except Exception:
        pass
    return im


def build(m, paths, tint=(1, 1, 1, 1), normal_strength=1.0, emission=None, emission_strength=1.0,
          use_emission_map=True, alpha=None, uv="UVMap"):
    """(Re)build material m as a textured glTF-friendly node tree."""
    m.use_nodes = True
    nt = m.node_tree
    for n in list(nt.nodes):
        nt.nodes.remove(n)
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    out.location = (600, 0)
    p = nt.nodes.new("ShaderNodeBsdfPrincipled")
    p.location = (300, 0)
    nt.links.new(p.outputs[0], out.inputs[0])
    uvn = nt.nodes.new("ShaderNodeUVMap")
    uvn.uv_map = uv
    uvn.location = (-900, 0)
    a = nt.nodes.new("ShaderNodeTexImage")
    a.image = _img(paths["albedo"], True)
    a.location = (-600, 300)
    nt.links.new(uvn.outputs[0], a.inputs[0])
    mix = nt.nodes.new("ShaderNodeMix")
    mix.data_type = "RGBA"
    mix.blend_type = "MULTIPLY"
    mix.inputs[0].default_value = 1.0
    mix.location = (-250, 300)
    nt.links.new(a.outputs["Color"], mix.inputs[6])
    mix.inputs[7].default_value = tint
    nt.links.new(mix.outputs[2], p.inputs["Base Color"])
    if "orm" in paths:
        o = nt.nodes.new("ShaderNodeTexImage")
        o.image = _img(paths["orm"], False)
        o.location = (-600, 0)
        nt.links.new(uvn.outputs[0], o.inputs[0])
        sep = nt.nodes.new("ShaderNodeSeparateColor")
        sep.location = (-250, 0)
        nt.links.new(o.outputs["Color"], sep.inputs[0])
        nt.links.new(sep.outputs[1], p.inputs["Roughness"])
        nt.links.new(sep.outputs[2], p.inputs["Metallic"])
        # glTF occlusion via the exporter's settings group
        g = bpy.data.node_groups.get("glTF Material Output")
        if g is None:
            g = bpy.data.node_groups.new("glTF Material Output", "ShaderNodeTree")
            g.interface.new_socket("Occlusion", in_out="INPUT", socket_type="NodeSocketFloat")
            g.interface.new_socket("Thickness", in_out="INPUT", socket_type="NodeSocketFloat")
        gn = nt.nodes.new("ShaderNodeGroup")
        gn.node_tree = g
        gn.location = (300, -400)
        nt.links.new(sep.outputs[0], gn.inputs["Occlusion"])
    if "normal" in paths and normal_strength > 0:
        nimg = nt.nodes.new("ShaderNodeTexImage")
        nimg.image = _img(paths["normal"], False)
        nimg.location = (-600, -300)
        nt.links.new(uvn.outputs[0], nimg.inputs[0])
        nm = nt.nodes.new("ShaderNodeNormalMap")
        nm.inputs["Strength"].default_value = normal_strength
        nm.location = (-250, -300)
        nt.links.new(nimg.outputs["Color"], nm.inputs["Color"])
        nt.links.new(nm.outputs[0], p.inputs["Normal"])
    if emission is not None:
        p.inputs["Emission Strength"].default_value = emission_strength
        if use_emission_map and "emission" in paths:
            e = nt.nodes.new("ShaderNodeTexImage")
            e.image = _img(paths["emission"], True)
            e.location = (-600, -600)
            nt.links.new(uvn.outputs[0], e.inputs[0])
            em = nt.nodes.new("ShaderNodeMix")
            em.data_type = "RGBA"
            em.blend_type = "MULTIPLY"
            em.inputs[0].default_value = 1.0
            nt.links.new(e.outputs["Color"], em.inputs[6])
            em.inputs[7].default_value = emission
            nt.links.new(em.outputs[2], p.inputs["Emission Color"])
        else:
            p.inputs["Emission Color"].default_value = emission
    if alpha is not None:
        p.inputs["Alpha"].default_value = alpha
        for attr, val in (("surface_render_method", "BLENDED"), ("blend_method", "BLEND")):
            try:
                setattr(m, attr, val)
            except Exception:
                pass
    m["tfj_textured"] = os.path.basename(paths["albedo"])
    return m


# ------------------------------------------------------------------------------------------
# glb post-process: embedded library images -> relative URIs into generated_assets/materials
# ------------------------------------------------------------------------------------------
def _read_glb(path):
    raw = open(path, "rb").read()
    magic, ver, length = struct.unpack_from("<III", raw, 0)
    off = 12
    js, binc = None, b""
    while off < length:
        clen, ctype = struct.unpack_from("<II", raw, off)
        data = raw[off + 8: off + 8 + clen]
        if ctype == 0x4E4F534A:
            js = json.loads(data.decode("utf-8"))
        elif ctype == 0x004E4942:
            binc = data
        off += 8 + clen
    return js, binc


def _write_glb(path, js, binc):
    jb = json.dumps(js, separators=(",", ":")).encode("utf-8")
    jb += b" " * ((4 - len(jb) % 4) % 4)
    binc = binc + b"\0" * ((4 - len(binc) % 4) % 4)
    total = 12 + 8 + len(jb) + (8 + len(binc) if binc else 0)
    with open(path, "wb") as f:
        f.write(struct.pack("<III", 0x46546C67, 2, total))
        f.write(struct.pack("<II", len(jb), 0x4E4F534A))
        f.write(jb)
        if binc:
            f.write(struct.pack("<II", len(binc), 0x004E4942))
            f.write(binc)


def externalise(path, lib=None, factors=None):
    """Replace every embedded image whose name matches a library PNG by a relative uri, then
    repack the binary chunk without those bytes. factors: {material name: {"metallicFactor": x}}
    patched into pbrMetallicRoughness. Returns the list of referenced files."""
    js, binc = _read_glb(path)
    for mat in js.get("materials", []):
        f = (factors or {}).get(mat.get("name"))
        if f:
            mat.setdefault("pbrMetallicRoughness", {}).update(f)
    if not js.get("images") and factors:
        _write_glb(path, js, binc)
    imgs = js.get("images", [])
    if not imgs:
        return []
    index = {}
    for root, _d, files in os.walk(lib or LIB):
        for fn in files:
            if fn.endswith(".png"):
                index[os.path.splitext(fn)[0]] = os.path.join(root, fn)
    drop = set()
    refs = []
    for im in imgs:
        nm = os.path.splitext(im.get("name", ""))[0]
        if nm in index and "bufferView" in im:
            drop.add(im.pop("bufferView"))
            im.pop("mimeType", None)
            rel = os.path.relpath(index[nm], os.path.dirname(os.path.abspath(path)))
            im["uri"] = rel.replace(os.sep, "/")
            refs.append(im["uri"])
    if drop:
        views = js["bufferViews"]
        keep = [i for i in range(len(views)) if i not in drop]
        remap, newbin, nv = {}, bytearray(), []
        for i in keep:
            v = dict(views[i])
            s, l = v.get("byteOffset", 0), v["byteLength"]
            while len(newbin) % 4:
                newbin.append(0)
            v["byteOffset"] = len(newbin)
            newbin += binc[s:s + l]
            remap[i] = len(nv)
            nv.append(v)
        js["bufferViews"] = nv
        for acc in js.get("accessors", []):
            if "bufferView" in acc:
                acc["bufferView"] = remap[acc["bufferView"]]
            sp = acc.get("sparse")
            if sp:
                sp["indices"]["bufferView"] = remap[sp["indices"]["bufferView"]]
                sp["values"]["bufferView"] = remap[sp["values"]["bufferView"]]
        for im in imgs:
            if "bufferView" in im:
                im["bufferView"] = remap[im["bufferView"]]
        js["buffers"][0]["byteLength"] = len(newbin)
        binc = bytes(newbin)
    _write_glb(path, js, binc)
    return refs


# ------------------------------------------------------------------------------------------
# Zone -> texture set. Chapter sets where the library has one, shared sets otherwise. The
# palette colour of the zone is the target mean colour; the tint (baseColorFactor) is
# target / mean(albedo), so the library texture keeps its detail and the kit keeps its palette.
# ------------------------------------------------------------------------------------------
ZONE_SET = {
    "": "@main", "key": "@main", "frame": "reinforced_steel", "panel": "shr:painted_panel",
    "light": "shr:painted_panel", "accent": "shr:painted_panel", "polymer": "composite",
    "concrete": "concrete", "trim": "shr:brushed_steel", "dark": "shr:gunmetal",
    "internal": "shr:carbon_composite", "cable": "shr:cable_bundle", "rubber": "shr:rubber",
    "hazard": "shr:painted_panel", "scorch": "shr:gunmetal", "burnt": "shr:gunmetal",
    "edge": "shr:brushed_steel", "module": "electronic_module", "floor": "floor",
    "tread": "shr:floor_tread", "glassset": "glass_polymer", "cloth": "shr:rubber", "visor": "shr:glass",
}
MAIN_SET = {  # physics material -> set for the main ('key') zone
    "lightweight_alloy": "lightweight_alloy", "reinforced_steel": "reinforced_steel",
    "composite": "composite", "glass_polymer": "shr:painted_panel", "concrete": "concrete",
    "electronic_module": "shr:painted_panel", "energy_component": "energy_component",
    "ai_core_module": "shr:painted_panel", "suit": "shr:carbon_composite",
}
BRIGHT_FALLBACK = {True: "shr:brushed_steel", False: "shr:frosted_polymer"}
_MEAN = {}


def albedo_mean(path):
    if path in _MEAN:
        return _MEAN[path]
    import numpy as np
    im = _img(path, True)
    px = np.empty(len(im.pixels), dtype=np.float32)
    im.pixels.foreach_get(px)  # Blender stores float pixels in scene-linear for sRGB images
    px = px.reshape(-1, 4)[:, :3]
    if not im.is_float:  # byte image: pixels are sRGB-encoded
        px = np.where(px <= 0.04045, px / 12.92, ((px + 0.055) / 1.055) ** 2.4)
    _MEAN[path] = tuple(float(x) for x in px.mean(0))
    return _MEAN[path]


def zone_paths(ch, zone, physics):
    key = ZONE_SET.get(zone, "@main")
    if key == "@main":
        key = MAIN_SET.get(physics, "shr:painted_panel")
    if ch not in CODE:
        ch = "helix"
    try:
        return key, set_paths(ch, key)
    except FileNotFoundError:
        return "shr:painted_panel", set_paths("shr", "shr:painted_panel")


def texture_zone(m, ch, zone, physics, target, normal_strength=1.0, floor=None):
    """Turn zone material m (flat colour target, linear RGBA) into a textured slot. floor: for floor
    layer pieces the main zone takes the chapter FLOOR set as authored (tint = layer value only)
    with its inlay emission mask lit in the chapter colour."""
    if floor is not None and zone in ("", "key") and ch in CODE:
        paths = set_paths(ch, "floor")
        v = floor["value"]
        build(m, paths, tint=(v, v, v, 1.0), normal_strength=normal_strength,
              emission=floor.get("emit"), emission_strength=floor.get("emit_strength", 0.8))
        m["tfj_set"] = "floor"
        m["tfj_metal"] = METAL_FACTOR["floor"]
        return m
    key, paths = zone_paths(ch, zone, physics)
    mean = albedo_mean(paths["albedo"])
    tint = [target[i] / max(mean[i], 1e-4) for i in range(3)]
    bright_ok = bool(m.get("tfj_allow_bright"))  # baked assets: the tint never reaches the glb
    if not bright_ok and zone != "module" and max(tint) > 1.6:  # library set darker than the palette asks for: use a bright neutral set
        metal = key.endswith(("steel", "alloy", "gunmetal"))
        key = BRIGHT_FALLBACK[metal]
        paths = set_paths("shr", key)
        mean = albedo_mean(paths["albedo"])
        tint = [target[i] / max(mean[i], 1e-4) for i in range(3)]
    s = max(tint)
    if s > (4.0 if bright_ok else 1.0):
        tint = [t / s * (4.0 if bright_ok else 1.0) for t in tint]
    emission = None
    if zone == "module":
        emission = m.get("tfj_emit_col")
    build(m, paths, tint=tuple(tint) + (1.0,), normal_strength=normal_strength,
          emission=emission, emission_strength=m.get("tfj_emit_strength", 1.0))
    m["tfj_set"] = key
    m["tfj_metal"] = METAL_FACTOR.get(zone, 0.5)
    if m.get("tfj_matte_layer"):  # background layers: near-dielectric so the sky does not light them up
        m["tfj_metal"] = round(m["tfj_metal"] * 0.25, 3)
    return m


METAL_FACTOR = {  # glTF metallicFactor per zone (multiplies the library ORM blue channel). MissionView has
    # no sky today, so fully metallic surfaces would mirror the #15191e background and read black.
    "key": 0.5, "": 0.5, "frame": 0.55, "panel": 0.5, "trim": 0.75, "edge": 0.85, "dark": 0.5,
    "internal": 0.4, "burnt": 0.3, "scorch": 0.1, "module": 0.6, "floor": 0.08, "tread": 0.3,
}
