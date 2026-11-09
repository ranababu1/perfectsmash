"""Preview rendering with the game camera direction (from scripts/mission/view/mission_view.gd).

Godot camera offset (-2.2, 2.3, 10.5) looking at focus - (0, 0.4, 0), FOV 40 (vertical).
Godot -> Blender axis map: (x, y, z) -> (x, -z, y).
Sun: Godot rotation_degrees (-52, -38, 0) -> travel direction (0.379, 0.485, -0.788) in Blender.
"""
import bpy, math, os
from mathutils import Vector

GAME_DIR = Vector((-2.2, -10.5, 2.7)).normalized()   # from look target toward camera (Blender)
SUN_DIR = Vector((0.379, 0.485, -0.788)).normalized()  # light travel direction (Blender)
FOV_V = 40.0


def srgb(h):
    h = h.lstrip("#")
    c = [int(h[i:i + 2], 16) / 255.0 for i in (0, 2, 4)]
    return tuple(x / 12.92 if x <= 0.04045 else ((x + 0.055) / 1.055) ** 2.4 for x in c)


def setup(res=(640, 640), samples=48, engine="CYCLES", bg="15191e", ambient=("8090a0", 0.55),
          floor=True, floor_z=0.0, rim=False, exposure=0.0):
    sc = bpy.context.scene
    sc.render.engine = engine
    sc.render.resolution_x, sc.render.resolution_y = res
    sc.render.resolution_percentage = 100
    sc.render.film_transparent = False
    if engine == "CYCLES":
        sc.cycles.device = "CPU"
        sc.cycles.samples = samples
        sc.cycles.use_denoising = True
        try:
            sc.cycles.denoiser = "OPENIMAGEDENOISE"
        except Exception:
            pass
        sc.cycles.max_bounces = 6
        sc.cycles.transparent_max_bounces = 8
        sc.cycles.use_adaptive_sampling = True
    try:
        sc.view_settings.view_transform = "AgX"
        sc.view_settings.look = "AgX - Base Contrast"
    except Exception:
        try:
            sc.view_settings.view_transform = "Filmic"
        except Exception:
            pass
    sc.view_settings.exposure = exposure
    w = bpy.data.worlds.new("preview_world")
    sc.world = w
    try:
        w.use_nodes = True
    except Exception:
        pass
    nt = w.node_tree
    bgn = nt.nodes.get("Background")
    amb = srgb(ambient[0])
    bgn.inputs[0].default_value = (*amb, 1.0)
    bgn.inputs[1].default_value = ambient[1]
    # visible backdrop colour separate from lighting: use light path trick
    lp = nt.nodes.new("ShaderNodeLightPath")
    bg2 = nt.nodes.new("ShaderNodeBackground")
    bg2.inputs[0].default_value = (*srgb(bg), 1.0)
    bg2.inputs[1].default_value = 1.0
    mix = nt.nodes.new("ShaderNodeMixShader")
    out = nt.nodes.get("World Output")
    # camera and glossy rays see the background colour (Godot: no sky, reflections come from the
    # background), diffuse rays get the ambient colour, as in MissionView
    mx = nt.nodes.new("ShaderNodeMath")
    mx.operation = "MAXIMUM"
    nt.links.new(lp.outputs["Is Camera Ray"], mx.inputs[0])
    nt.links.new(lp.outputs["Is Glossy Ray"], mx.inputs[1])
    nt.links.new(mx.outputs[0], mix.inputs[0])
    nt.links.new(bgn.outputs[0], mix.inputs[1])
    nt.links.new(bg2.outputs[0], mix.inputs[2])
    nt.links.new(mix.outputs[0], out.inputs[0])

    sun_d = bpy.data.lights.new("sun", "SUN")
    sun_d.energy = 1.15 * 3.14159
    sun_d.color = srgb("dfe8f0")
    sun_d.angle = math.radians(2.5)
    sun = bpy.data.objects.new("sun", sun_d)
    sc.collection.objects.link(sun)
    sun.rotation_euler = SUN_DIR.to_track_quat("-Z", "Y").to_euler()
    if rim:
        rim_d = bpy.data.lights.new("rim", "AREA")
        rim_d.energy = 220
        rim_d.size = 3.0
        rim_d.color = srgb("9fc8ff")
        rim = bpy.data.objects.new("rim", rim_d)
        sc.collection.objects.link(rim)
        rim["preview_rim"] = True
    if floor:
        me = bpy.data.meshes.new("floor")
        s = 40
        me.from_pydata([(-s, -s, 0), (s, -s, 0), (s, s, 0), (-s, s, 0)], [], [(0, 1, 2, 3)])
        fl = bpy.data.objects.new("floor", me)
        fl.location.z = floor_z
        m = bpy.data.materials.new("floor_mat")
        m.use_nodes = True if hasattr(m, "use_nodes") else None
        p = m.node_tree.nodes.get("Principled BSDF")
        p.inputs["Base Color"].default_value = (*srgb("1c2026"), 1)
        p.inputs["Roughness"].default_value = 0.55
        p.inputs["Metallic"].default_value = 0.2
        me.materials.append(m)
        sc.collection.objects.link(fl)
    cam_d = bpy.data.cameras.new("cam")
    cam_d.sensor_fit = "VERTICAL"
    cam_d.angle_y = math.radians(FOV_V)
    cam = bpy.data.objects.new("cam", cam_d)
    sc.collection.objects.link(cam)
    sc.camera = cam
    return cam


def frame(objs, cam, margin=1.12, direction=None, look_offset=(0, 0, 0)):
    """Place camera along the game direction so objs fill the frame."""
    direction = (direction or GAME_DIR).normalized()
    pts = []
    for ob in objs:
        if ob.type != "MESH":
            continue
        for v in ob.data.vertices:
            pts.append(ob.matrix_world @ v.co)
    mn = Vector((min(p.x for p in pts), min(p.y for p in pts), min(p.z for p in pts)))
    mx = Vector((max(p.x for p in pts), max(p.y for p in pts), max(p.z for p in pts)))
    c = (mn + mx) / 2 + Vector(look_offset)
    r = max((p - c).length for p in pts)
    sc = bpy.context.scene
    aspect = sc.render.resolution_x / sc.render.resolution_y
    fov = math.radians(FOV_V)
    fov_h = 2 * math.atan(math.tan(fov / 2) * aspect)
    d = r * margin / math.sin(min(fov, fov_h) / 2)
    cam.location = c + direction * d
    cam.rotation_euler = (-direction).to_track_quat("-Z", "Y").to_euler()
    cam.data.clip_start = 0.01
    cam.data.clip_end = d * 4 + 50
    for ob in sc.objects:
        if ob.get("preview_rim"):
            ob.location = c + Vector((3.0, 4.0, 2.5)) * max(1.0, r)
            ob.rotation_euler = (c - ob.location).to_track_quat("-Z", "Y").to_euler()
            ob.data.energy = 220 * max(1.0, r) ** 2
    return c, r


def render(path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    bpy.context.scene.render.image_settings.file_format = "PNG"
    bpy.context.scene.render.filepath = path
    bpy.ops.render.render(write_still=True)
    return path
