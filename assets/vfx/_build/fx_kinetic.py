"""Kinetic Accelerator effects, material impacts and weapon cooldown."""
import math, os, sys
import numpy as np
from vfxlib import *

CYAN = [(0.0, "#03222c"), (0.35, "#1f8fb0"), (0.7, "#3cc8e6"), (1.0, "#bff3ff"), (1.4, "#ffffff")]
WARM = [(0.0, "#2a1606"), (0.4, "#c98a3c"), (0.8, "#ffd9a0"), (1.2, "#fff6e6"), (1.5, "#ffffff")]
ICE = [(0.0, "#0a1e26"), (0.4, "#7fc7dc"), (0.8, "#d8f6ff"), (1.3, "#ffffff")]
ELEC = [(0.0, "#061436"), (0.35, "#2f6bff"), (0.7, "#6fc6ff"), (1.0, "#d6f2ff"), (1.4, "#ffffff")]
WHITE = [(0.0, "#202020"), (0.5, "#bdbdbd"), (1.0, "#ffffff"), (1.5, "#ffffff")]


def contrast2(v):
    return np.clip((v - 0.5) * 3.0 + 0.5, 0, 1)


def muzzle(n=256, F=8, seed=61):
    """Flash pointing to +x; pivot at the left-centre (barrel tip at u = 0.16)."""
    x, y, r, a = grid(n)
    ox = -0.68
    X = x - ox
    rng = np.random.default_rng(seed)
    N = fbm3(F, n, n, base=6, tcells=4, octaves=3, seed=seed)
    frames = []
    for i in range(F):
        t = i / (F - 1)
        L = 0.8 + 0.7 * ease_out(min(1.0, t * 2.5), 2)
        k = (1 - t) ** 1.3
        Xp = np.maximum(X, 0)
        cone = np.exp(-(Xp / L) ** 2 * 1.5) * np.exp(-(y / (0.05 + 0.17 * Xp)) ** 2) * smooth(-0.04, 0.02, X)
        core = np.exp(-((X) ** 2 + y ** 2) / (0.13 + 0.06 * t) ** 2) * 2.0
        petals = 0
        for ang in (math.radians(55), math.radians(-55)):
            ux, uy = math.cos(ang), math.sin(ang)
            along = X * ux + y * uy; perp = -X * uy + y * ux
            petals = petals + np.exp(-(np.maximum(along, 0) / (0.40 + 0.2 * t)) ** 2 * 2) * np.exp(-(perp / (0.025 + 0.07 * np.maximum(along, 0))) ** 2) * smooth(-0.02, 0.02, along) * 0.9
        I = (1.8 * cone * (0.55 + 0.9 * N[i]) + core + petals) * k
        f = light_to_frame(I, CYAN, blur=0.6)
        frames.append(f)
    return frames


def kinetic_impact(n=256, F=16, seed=71):
    """Direct hit: tight cyan-white flash, crisp ring, radial needles, lingering ion glow."""
    x, y, r, a = grid(n)
    N = fbm3(F, n, n, base=5, tcells=3, octaves=3, seed=seed)
    sp = spark_system(n, F, 40, seed, spread=2 * math.pi, speed=(1.6, 3.4), gravity=0.4, life=(0.3, 0.7), drag=2.6,
                      width=(0.008, 0.015), color_hot="#ffffff", color_cool="#3cc8e6", trail=0.07, intensity=2.4, start=(0.0, 0.08))
    frames = []
    for i in range(F):
        t = (i + 0.5) / F
        flash = 2.6 * np.exp(-(r / (0.07 + 0.16 * t)) ** 2) * max(0.0, 1 - t / 0.35) ** 1.5
        R = 0.06 + 0.62 * ease_out(t, 2.4)
        ring = 1.2 * np.exp(-((r - R) / (0.012 + 0.03 * t)) ** 2) * (1 - t) ** 3.2 * contrast2(N[i])
        glow = 0.45 * np.exp(-(r / 0.22) ** 2) * (1 - t) ** 1.6 * (0.6 + 0.8 * N[i])
        star = 0
        for k in range(4):
            ang = k * math.pi / 4 + 0.3
            perp = np.abs(-x * math.sin(ang) + y * math.cos(ang))
            star = star + np.exp(-(perp / 0.008) ** 2) * np.exp(-(r / (0.18 + 0.5 * t)) ** 2) * (k % 2 * 0.5 + 0.5)
        I = flash + ring + glow + star * 1.2 * max(0.0, 1 - t / 0.4)
        light = ramp(np.clip(I, 0, 1.6), CYAN) * np.clip(I, 0, 1.6)[..., None] + sp[i]
        frames.append(additive_from_light(ndi.gaussian_filter(light, (0.5, 0.5, 0))))
    return frames


def impact_metal(n=256, F=16, seed=81):
    """Metal: hot white spark spray up and outward (frame up = surface normal), short white flash, ember fall."""
    x, y, r, a = grid(n)
    sp = spark_system(n, F, 70, seed, origin=(0.0, 0.30), dir_angle=-math.pi / 2, spread=math.radians(160), speed=(1.3, 3.2),
                      gravity=2.2, life=(0.35, 0.95), drag=1.9, width=(0.007, 0.014), color_hot="#ffffff", color_cool="#ffb860",
                      trail=0.07, intensity=2.4, start=(0.0, 0.10))
    frames = []
    for i in range(F):
        t = (i + 0.5) / F
        d = np.hypot(x, y - 0.30)
        flash = 2.2 * np.exp(-(d / (0.06 + 0.12 * t)) ** 2) * max(0.0, 1 - t / 0.3) ** 1.5
        glow = 0.5 * np.exp(-(d / 0.16) ** 2) * (1 - t) ** 2
        I = flash + glow
        light = ramp(np.clip(I, 0, 1.6), WARM) * np.clip(I, 0, 1.6)[..., None] + sp[i]
        frames.append(additive_from_light(ndi.gaussian_filter(light, (0.5, 0.5, 0))))
    return frames


def impact_glass(n=256, F=16, seed=91):
    """Glass: bright white crack flash, star crack lines, spinning shards with glints (additive, cold white)."""
    rng = np.random.default_rng(seed)
    x, y, r, a = grid(n)
    cracks = []
    for k in range(9):
        ang = 2 * math.pi * k / 9 + rng.uniform(-0.25, 0.25)
        L = rng.uniform(0.35, 0.62)
        cracks += lightning(rng, 0, 0, math.cos(ang) * L, math.sin(ang) * L, depth=4, rough=0.12, branch_p=0.35)
    crack_I = draw_polylines(n, cracks, core_w=0.006)
    shards = []
    for _ in range(26):
        ang = rng.uniform(0, 2 * math.pi); v = rng.uniform(0.35, 0.95); s = rng.uniform(0.035, 0.085)
        k = 3 if rng.random() < 0.7 else 4
        pts = [(math.cos(2 * math.pi * j / k + rng.uniform(-0.5, 0.5)) * rng.uniform(0.4, 1.0), math.sin(2 * math.pi * j / k + rng.uniform(-0.5, 0.5)) * rng.uniform(0.4, 1.0)) for j in range(k)]
        shards.append((ang, v, s, pts, rng.uniform(-9, 9), rng.uniform(0, 6)))
    frames = []
    for i in range(F):
        t = (i + 0.5) / F
        flash = 2.0 * np.exp(-(r / (0.05 + 0.18 * t)) ** 2) * max(0.0, 1 - t / 0.3) ** 1.4
        crack = crack_I * 1.6 * max(0.0, 1 - t / 0.55) ** 1.2 * smooth(0, 0.06, t)
        cv = Canvas(n, ss=2)
        for ang, v, s, pts, spin, rot0 in shards:
            d = 0.05 + v * ease_out(t, 2.2) * 0.85
            px, py = math.cos(ang) * d, math.sin(ang) * d + 0.5 * t * t
            if abs(px) > 0.88 or abs(py) > 0.88:
                continue
            rot = rot0 + spin * t
            P = [(px + (sx * math.cos(rot) - sy * math.sin(rot)) * s, py + (sx * math.sin(rot) + sy * math.cos(rot)) * s) for sx, sy in pts]
            glint = 0.5 + 0.5 * math.cos(rot * 2.0)
            fade = (1 - t) ** 0.8
            cv.polygon(P, np.array([1, 1, 1], np.float32) * (0.5 + 0.9 * glint), alpha=fade * (0.55 + 0.45 * glint))
        sh = cv.result()
        sh_light = sh[..., :3]
        I = flash + crack
        light = ramp(np.clip(I, 0, 1.5), ICE) * np.clip(I, 0, 1.5)[..., None] + sh_light * hexc("#e6f8ff")[None, None]
        frames.append(additive_from_light(ndi.gaussian_filter(light, (0.6, 0.6, 0))))
    return frames


def impact_electric(n=256, F=16, seed=101):
    """Electrical: crackling blue-white arcs jumping from the hit point, flicker, small spark spray."""
    rng = np.random.default_rng(seed)
    x, y, r, a = grid(n)
    sp = spark_system(n, F, 22, seed, spread=2 * math.pi, speed=(0.6, 1.8), gravity=1.2, life=(0.25, 0.6), drag=2.5,
                      width=(0.004, 0.008), color_hot="#ffffff", color_cool="#6fc6ff", trail=0.04, intensity=1.4)
    frames = []
    for i in range(F):
        t = (i + 0.5) / F
        k = (1 - t) ** 1.1
        lines = []
        for _ in range(rng.integers(3, 6)):
            ang = rng.uniform(0, 2 * math.pi); L = rng.uniform(0.3, 0.72) * (0.6 + 0.4 * (1 - t))
            lines += lightning(rng, 0, 0, math.cos(ang) * L, math.sin(ang) * L, depth=6, rough=0.3, branch_p=0.3)
        core = draw_polylines(n, lines, core_w=0.007)
        flick = rng.uniform(0.55, 1.0) if i > 1 else 1.0
        glow = ndi.gaussian_filter(core, n * 0.012) * 6.0
        I = (core * 1.6 + glow * 0.8) * k * flick + 2.0 * np.exp(-(r / (0.06 + 0.1 * t)) ** 2) * max(0.0, 1 - t / 0.25)
        I += 0.35 * np.exp(-(r / 0.2) ** 2) * k
        light = ramp(np.clip(I, 0, 1.6), ELEC) * np.clip(I, 0, 1.6)[..., None] + sp[i]
        frames.append(additive_from_light(light))
    return frames


def cooldown_charge(n=256, F=16, seed=111):
    """Neutral white charging loop for a weapon icon or the projectile spawn: motes spiral in, ring breathes. Tint with modulate."""
    rng = np.random.default_rng(seed)
    x, y, r, a = grid(n)
    motes = [(rng.uniform(0, 2 * math.pi), rng.uniform(0, 1), rng.uniform(0.008, 0.016)) for _ in range(28)]
    frames = []
    for i in range(F):
        ph = i / F
        cv = Canvas(n, ss=2, channels=3)
        for ang0, off, w in motes:
            u = (ph + off) % 1.0  # 0 = far, 1 = arrived
            rr = 0.78 * (1 - u) ** 1.2 + 0.12
            ang = ang0 + 1.6 * u
            br = math.sin(math.pi * u) ** 0.8
            cv.splat(math.cos(ang) * rr, math.sin(ang) * rr, w * (0.6 + 0.6 * u), np.array([1, 1, 1]) * 1.3 * br)
        breathe = 0.5 + 0.5 * math.cos(2 * math.pi * ph)
        ring = (0.55 + 0.35 * breathe) * np.exp(-((r - 0.30) / 0.014) ** 2)
        core = (0.5 + 0.4 * breathe) * np.exp(-(r / 0.12) ** 2)
        I = ring + core
        light = ramp(np.clip(I, 0, 1.4), WHITE) * np.clip(I, 0, 1.4)[..., None] + cv.result()
        frames.append(additive_from_light(ndi.gaussian_filter(light, (0.5, 0.5, 0))))
    return frames


def cooldown_ready(n=256, F=8, seed=121):
    """Neutral white 'weapon ready' flash: ring snaps outward with four ticks. Tint with modulate."""
    x, y, r, a = grid(n)
    frames = []
    for i in range(F):
        t = (i + 0.5) / F
        R = 0.25 + 0.5 * ease_out(t, 2.5)
        ring = 1.3 * np.exp(-((r - R) / (0.016 + 0.02 * t)) ** 2) * (1 - t) ** 1.2
        ticks = 0
        for k in range(4):
            ang = k * math.pi / 2 + math.pi / 4
            along = x * math.cos(ang) + y * math.sin(ang); perp = np.abs(-x * math.sin(ang) + y * math.cos(ang))
            ticks = ticks + np.exp(-(perp / 0.012) ** 2) * smooth(R + 0.02, R + 0.05, along) * smooth(R + 0.16, R + 0.12, along)
        core = 1.6 * np.exp(-(r / 0.2) ** 2) * max(0.0, 1 - t / 0.4) ** 1.5
        I = ring + ticks * (1 - t) * 1.2 + core
        frames.append(light_to_frame(I, WHITE, blur=0.6))
    return frames


def trail_tex(w=512, h=64, stops=CYAN, seed=131):
    xs = (np.arange(w, dtype=np.float32) + 0.5) / w
    ys = ((np.arange(h, dtype=np.float32) + 0.5) / h) * 2 - 1
    Y, X = np.meshgrid(ys, xs, indexing="ij")
    taper = 0.2 + 0.8 * X ** 0.7
    core = np.exp(-(Y / (0.09 * taper)) ** 2)
    glow = np.exp(-(Y / (0.40 * taper)) ** 2) * 0.45
    along = smooth(0.0, 1.0, X) ** 2.2 * smooth(1.0, 0.97, X)
    I = (1.35 * core + glow) * along
    f = light_to_frame(I, stops)
    win = smooth(0, 0.14, 1 - np.abs(Y)) * smooth(0, 0.01, X) * smooth(0, 0.01, 1 - X)
    f[..., 3] *= win
    return f


JOBS = [
    dict(id="OPR-VFX-KINETIC_MUZZLE-A", fn=muzzle, n=256, C=4, R=2, fps=30, loop=False, blend="add", pivot="left_center",
         purpose="Kinetic Accelerator muzzle flash, cyan-white, fires toward +u (right).",
         notes="Pivot: barrel tip at u = 0.16, v = 0.5. Rotate the quad to the aim angle. About 0.5 m wide in game. Play once per shot (0.27 s)."),
    dict(id="OPR-VFX-KINETIC_IMPACT-A", fn=kinetic_impact, n=256, C=4, R=4, fps=30, loop=False, blend="add",
         purpose="Kinetic slug direct hit: cyan-white flash, ring, radial needles and sparks (any material, layered under the material impact).",
         notes="About 0.8 m at impact strength 1; scale with impact strength 0.6-1.4."),
    dict(id="SHR-VFX-IMPACT_METAL-A", fn=impact_metal, n=256, C=4, R=4, fps=30, loop=False, blend="add", pivot="center_bottom_quarter",
         purpose="Metal impact: hot white sparks sprayed off the surface, falling embers, short flash. Doubles as SPARK_BURST for the sparking damage state.",
         notes="Origin at u = 0.5, v = 0.65 (frame up = surface normal); rotate to the hit normal. Contains SPARK keyword use: sparking state may loop it with random rotation every 0.6-1.2 s."),
    dict(id="SHR-VFX-IMPACT_GLASS-A", fn=impact_glass, n=256, C=4, R=4, fps=30, loop=False, blend="add",
         purpose="Glass impact: crack star flash and glinting shards thrown out (cold white).",
         notes="Pair with mesh glass shards from destructibles where present; this sheet carries the read at phone scale."),
    dict(id="SHR-VFX-IMPACT_ELECTRIC-A", fn=impact_electric, n=256, C=4, R=4, fps=30, loop=False, blend="add",
         purpose="Electronic / electrical impact: blue-white arcs jumping from the hit point, flicker, small sparks."),
    dict(id="OPR-VFX-WEAPON_COOLDOWN_CHARGE-A", fn=cooldown_charge, n=256, C=4, R=4, fps=20, loop=True, blend="add",
         purpose="Weapon cooldown charging loop (neutral white; modulate cyan #3CC8E6 for Kinetic, amber #F2A23A for Breach).",
         notes="Seamless loop. Use behind the HUD weapon slot icon (CanvasItem with CanvasItemMaterial blend add, AnimatedTexture or shader frame index) or at the launch point in 3D."),
    dict(id="OPR-VFX-WEAPON_COOLDOWN_READY-A", fn=cooldown_ready, n=256, C=4, R=2, fps=24, loop=False, blend="add",
         purpose="Weapon ready flash when cooldown completes (neutral white; tint per weapon)."),
]


def build(only=None):
    run_jobs(JOBS, "kinetic", only)
    if not only or "TRAIL" in only:
        eid = "OPR-VFX-KINETIC_TRAIL-A"
        path = os.path.join(VFX, "shared", eid.lower().replace("-", "_") + ".png")
        save_texture(trail_tex(), path)
        register(eid, path, "shared", "add", "Kinetic Accelerator slug trail streak, cyan-white; head at the right edge (u = 1).", 1, 1, 1, 0, False, 0,
                 pivot="right_center", render_type="texture",
                 notes="512x64 static texture. Stretch along the velocity behind the slug (about 0.06 s of travel, 1 m at 1700 px/s). Tier tints: modulate per vfx/upgrade_tiers.json.")
        write_index("kinetic_trail")


if __name__ == "__main__":
    build(sys.argv[1] if len(sys.argv) > 1 else None)
