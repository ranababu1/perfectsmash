"""Breach Charge effects: flight trail, arming pulse, activation, explosion, shockwave, blast debris."""
import math, os, sys
import numpy as np
from vfxlib import *

OUT = os.path.join(VFX, "shared")
FIRE = [(0.0, "#1a0702"), (0.18, "#6a210a"), (0.38, "#c2501a"), (0.58, "#ec8a2c"), (0.75, "#f6b456"), (0.9, "#ffe2a6"), (1.1, "#ffffff")]


def contrast(v, k=2.2):
    return np.clip((v - 0.5) * k + 0.5, 0, 1)


def explosion(n=512, F=16, seed=11):
    x, y, r, a = grid(n)
    N1 = contrast(fbm3(F, n, n, base=4, tcells=2, octaves=5, seed=seed), 2.4)
    N2 = contrast(fbm3(F, n, n, base=9, tcells=3, octaves=4, seed=seed + 7), 2.0)
    rng = np.random.default_rng(seed)
    puffs = []
    for k in range(18):  # rim lobes, stratified around the circle
        ang = 2 * math.pi * (k + rng.uniform(-0.3, 0.3)) / 18
        puffs.append((ang, rng.uniform(0.75, 1.0), rng.uniform(0.75, 1.2), rng.uniform(0.7, 1.0)))
    for k in range(8):  # inner body
        puffs.append((rng.uniform(0, 2 * math.pi), rng.uniform(0.0, 0.45), rng.uniform(1.0, 1.4), rng.uniform(1.0, 1.2)))
    sparks = [(rng.uniform(0, 2 * math.pi), rng.uniform(0.6, 1.0), rng.uniform(0.004, 0.008)) for _ in range(54)]
    frames = []
    for i in range(F):
        t = i / (F - 1)
        grow = ease_out(t, 2.6)
        D = np.zeros((n, n), np.float32); Tw = np.zeros((n, n), np.float32)
        for ang, dist, rs, hs in puffs:
            d = dist * (0.06 + 0.60 * grow)
            px, py = math.cos(ang) * d, math.sin(ang) * d - 0.07 * t  # hot gas rises a touch
            rad = (0.08 + 0.17 * grow) * rs
            g = np.exp(-(((x - px) ** 2 + (y - py) ** 2) / (rad * rad)))
            D += g
            Tw += g * hs * (1 - 0.5 * dist)
        T = Tw / np.maximum(D, 1e-4)
        Dn = D * (0.5 + 1.0 * N1[i]) - 0.30 * t
        shape = smooth(0.22, 0.70, Dn)
        heat = T * (1.55 * (1 - t) ** 1.5) * (0.45 + 0.85 * N2[i]) * (1 + 0.5 * np.exp(-(r / (0.2 + 0.3 * t)) ** 2) * (1 - t))
        # rim cools first: darken edges of the body
        heat *= 0.55 + 0.45 * smooth(0.1, 0.9, Dn)
        flash = 2.8 * np.exp(-(r / (0.10 + 0.45 * t)) ** 2) * max(0.0, 1 - t / 0.2) ** 1.4
        I = shape * heat
        light = ramp(I + flash, FIRE) * (np.clip(I * 1.1 + flash, 0, 1.6) ** 1.1)[..., None]
        cv = Canvas(n, ss=1, channels=3)
        if t < 0.7:
            for ang, v, w in sparks:
                d0 = 0.10 + v * ease_out(t, 3.5) * 0.80; d1 = max(0.05, d0 - (0.22 * (1 - t) + 0.03) * v)
                fade = (1 - t / 0.7) ** 1.2
                cv.streak(math.cos(ang) * d1, math.sin(ang) * d1, math.cos(ang) * d0, math.sin(ang) * d0,
                          w * 0.6, w, hexc("#ffd79a") * 1.8 * fade, 0.25, 1.0)
        light = light + cv.result()[..., :3]
        frames.append(additive_from_light(light))
    return frames


def shockwave(n=512, F=16, seed=21):
    x, y, r, a = grid(n)
    N = fbm3(F, n, n, base=8, tcells=2, octaves=3, seed=seed)
    frames = []
    for i in range(F):
        t = (i + 1) / F
        R = 0.08 + 0.80 * ease_out(t, 2.2)
        width = 0.018 + 0.07 * t
        ring = np.exp(-((r - R) / width) ** 2)
        inner = np.exp(-((r - R * 0.86) / (width * 2.2)) ** 2) * 0.35  # soft trailing wake
        mod = 0.65 + 0.7 * N[i]
        k = (1 - t) ** 1.3 * 1.05 * smooth(0.0, 0.25, t)
        I = (ring + inner) * mod * k
        light = ramp(np.clip(I, 0, 1.2), [(0, "#3a2208"), (0.45, "#f2a23a"), (0.9, "#ffd08a"), (1.2, "#ffe8c4")]) * np.clip(I, 0, 1.2)[..., None]
        frames.append(additive_from_light(light))
    return frames


def activation(n=256, F=8, seed=31):
    """Detonation trigger: hard white-amber pin flash with 4 cross glints, 8 frames."""
    x, y, r, a = grid(n)
    frames = []
    for i in range(F):
        t = i / (F - 1)
        core = 2.4 * np.exp(-(r / (0.06 + 0.22 * t)) ** 2) * (1 - t) ** 1.6
        glint = (np.exp(-(np.abs(y) / 0.012) ** 2) * np.exp(-(np.abs(x) / (0.25 + 0.6 * t)) ** 2) +
                 np.exp(-(np.abs(x) / 0.012) ** 2) * np.exp(-(np.abs(y) / (0.25 + 0.6 * t)) ** 2)) * 1.3 * (1 - t) ** 2
        ringR = 0.1 + 0.55 * ease_out(t, 2)
        ring = 0.9 * np.exp(-((r - ringR) / 0.02) ** 2) * (1 - t) ** 1.2
        I = core + glint + ring
        light = ramp(np.clip(I, 0, 1.5), [(0, "#5a2a06"), (0.5, "#f2a23a"), (1.0, "#ffe8c0"), (1.5, "#ffffff")]) * np.clip(I, 0, 1.5)[..., None]
        frames.append(additive_from_light(light))
    return frames


def arming(n=256, F=16):
    """Looping armed-charge pulse: amber core with two counter-rotating dashed rings (seamless loop)."""
    x, y, r, a = grid(n)
    frames = []
    for i in range(F):
        ph = i / F
        pulse = 0.5 + 0.5 * math.cos(2 * math.pi * ph)
        core = (1.1 + 0.6 * pulse) * np.exp(-(r / 0.10) ** 2)
        halo = 0.35 * (0.6 + 0.4 * pulse) * np.exp(-(r / 0.34) ** 2)
        d1 = (np.cos(6 * (a - 2 * math.pi * ph / 6)) > 0.2).astype(np.float32)
        ring1 = np.exp(-((r - 0.42) / 0.014) ** 2) * (0.25 + 0.75 * d1)
        d2 = (np.cos(10 * (a + 2 * math.pi * ph / 10)) > 0.5).astype(np.float32)
        ring2 = 0.6 * np.exp(-((r - 0.58) / 0.010) ** 2) * d2 * (0.5 + 0.5 * pulse)
        I = core + halo + ring1 + ring2
        light = ramp(np.clip(I, 0, 1.6), [(0, "#4a2004"), (0.4, "#e0781c"), (0.8, "#f2a23a"), (1.2, "#ffd890"), (1.6, "#ffffff")]) * np.clip(I, 0, 1.6)[..., None]
        light = ndi.gaussian_filter(light, (0.7, 0.7, 0))
        frames.append(additive_from_light(light))
    return frames


def blast_debris(n=512, F=16, seed=41):
    """Mixed-blend chunks and grit flung out from the blast centre, with a little dark dust."""
    rng = np.random.default_rng(seed)
    chunks = []
    for _ in range(70):
        ang = rng.uniform(0, 2 * math.pi); v = rng.uniform(0.45, 1.0)
        size = rng.uniform(0.012, 0.048) * (1.25 - v * 0.5)
        k = rng.integers(4, 7)
        shape = [(math.cos(2 * math.pi * j / k + rng.uniform(-0.4, 0.4)) * rng.uniform(0.6, 1.0),
                  math.sin(2 * math.pi * j / k + rng.uniform(-0.4, 0.4)) * rng.uniform(0.6, 1.0)) for j in range(k)]
        chunks.append(dict(ang=ang, v=v, size=size, shape=shape, spin=rng.uniform(-6, 6), rot=rng.uniform(0, 6.3),
                           shade=rng.uniform(0.38, 0.72), hot=rng.random() < 0.35))
    x, y, r, a = grid(n)
    D = fbm3(F, n, n, base=4, tcells=2, octaves=4, seed=seed)
    frames = []
    for i in range(F):
        t = (i + 1) / F
        cv = Canvas(n, ss=2)
        # dust ring under the chunks
        R = 0.15 + 0.55 * ease_out(t, 2.0)
        dust = smooth(1.0, 0.5, r / R * (1 + 0.5 * (D[i] - 0.5))) * (0.55 + 0.45 * smooth(0.0, 0.5, r / R)) * (0.55 * (1 - t) ** 1.2)
        for c in chunks:
            d = 0.05 + c["v"] * ease_out(t, 2.6) * 0.78
            px = math.cos(c["ang"]) * d; py = math.sin(c["ang"]) * d + 0.25 * t * t  # slight gravity (screen down = +y)
            if abs(px) > 0.9 or abs(py) > 0.9:
                continue
            rot = c["rot"] + c["spin"] * t
            pts = [(px + (sx * math.cos(rot) - sy * math.sin(rot)) * c["size"], py + (sx * math.sin(rot) + sy * math.cos(rot)) * c["size"]) for sx, sy in c["shape"]]
            g = c["shade"]
            col = np.array([g, g * 0.97, g * 0.93], np.float32)
            if c["hot"] and t < 0.6:
                col = col * (1 - (1 - t / 0.6)) + hexc("#f2a23a") * (1 - t / 0.6)
            fade = 1.0 if t < 0.8 else max(0.0, 1 - (t - 0.8) / 0.2)
            cv.polygon(pts, col, alpha=fade)
            # lit top edge: a smaller, brighter copy offset up-left reads as a bevel highlight
            hl = [(px + (qx - px) * 0.55 - c["size"] * 0.18, py + (qy - py) * 0.55 - c["size"] * 0.22) for qx, qy in pts]
            cv.polygon(hl, np.minimum(col * 1.35 + 0.06, 1), alpha=fade * 0.8)
        res = unpremultiply(cv.result())
        dust_rgb = np.array([0.36, 0.34, 0.32], np.float32) * (0.8 + 0.4 * D[i][..., None])
        a_c = res[..., 3:4]; a_d = dust[..., None]
        out_a = a_c + a_d * (1 - a_c)
        out_rgb = (res[..., :3] * a_c + dust_rgb * a_d * (1 - a_c)) / np.maximum(out_a, 1e-5)
        frames.append(np.dstack([out_rgb, out_a]).astype(np.float32))
    return frames


def trail_texture(w=512, h=128, core="#ffd790", edge="#f2a23a", seed=51):
    """Static trail ribbon texture, head at the right edge, fading to the left (stretch along the flight path)."""
    xs = (np.arange(w, dtype=np.float32) + 0.5) / w
    ys = ((np.arange(h, dtype=np.float32) + 0.5) / h) * 2 - 1
    Y, X = np.meshgrid(ys, xs, indexing="ij")
    taper = 0.15 + 0.85 * X
    noise = fbm2(h, w, base=3, octaves=4, seed=seed)
    prof_core = np.exp(-(Y / (0.10 * taper)) ** 2)
    prof_glow = np.exp(-(Y / (0.42 * taper)) ** 2) * (0.75 + 0.5 * noise)
    along = smooth(0.0, 0.9, X) ** 1.6 * smooth(1.0, 0.94, X)
    I = (1.25 * prof_core + 0.45 * prof_glow) * along
    light = ramp(np.clip(I, 0, 1.3), [(0, "#2a1004"), (0.4, edge), (0.9, core), (1.3, "#ffffff")]) * np.clip(I, 0, 1.3)[..., None]
    f = additive_from_light(light)
    win = smooth(0, 3 / h * 2 + 0.06, 1 - np.abs(Y)) * smooth(0, 0.01, X) * smooth(0, 0.01, 1 - X)
    f[..., 3] *= win
    return f


JOBS = [
    dict(id="OPR-VFX-BREACH_EXPLOSION-A", fn=explosion, n=512, C=4, R=4, fps=24, loop=False, blend="add",
         purpose="Breach Charge detonation fireball: white flash, turbulent amber fireball, radial hot streaks; follow with SHR-VFX-SMOKE_PUFF-A and the shockwave.",
         notes="Scale so the frame width = 2.2 x blast_radius (Breach base 140 px = 1.4 m -> billboard about 3.1 m). Pivot centre at the blast point.",
         used_by=["MissionView._on_blast (proposed)"]),
    dict(id="OPR-VFX-BREACH_SHOCKWAVE-A", fn=shockwave, n=512, C=4, R=4, fps=30, loop=False, blend="add",
         purpose="Breach Charge shockwave ring, expands to 0.88 of the frame half-width.",
         notes="Camera-facing quad (the camera looks down -Z, so billboard on or off both work). Frame width = 2 x blast_radius / 0.88.",
         used_by=["MissionView._on_blast (proposed)"]),
    dict(id="OPR-VFX-BREACH_ACTIVATION-A", fn=activation, n=256, C=4, R=2, fps=30, loop=False, blend="add",
         purpose="Breach Charge activation flash at detonation (first 0.27 s), plays on top of the explosion.",
         used_by=["MissionView._on_blast (proposed)"]),
    dict(id="OPR-VFX-BREACH_ARMING-A", fn=arming, n=256, C=4, R=4, fps=16, loop=True, blend="add",
         purpose="Armed Breach Charge pulse; seamless loop while the charge is in flight or attached.",
         notes="Size about 0.6 m, parented to the projectile.", used_by=["MissionView._on_projectile_spawned (proposed)"]),
    dict(id="OPR-VFX-BREACH_DEBRIS-A", fn=blast_debris, n=512, C=4, R=4, fps=24, loop=False, blend="mix",
         purpose="Blast debris burst: rubble chunks (some still glowing amber) and grit flung radially, slight downward drift.",
         notes="Draw behind the explosion (sorting offset -0.1). Supplements mesh debris from the destructibles stream.",
         used_by=["MissionView._on_blast (proposed)"]),
]


def build(only=None):
    run_jobs(JOBS, "breach", only)
    if not only or "TRAIL" in only:
        eid = "OPR-VFX-BREACH_TRAIL-A"
        path = os.path.join(OUT, eid.lower().replace("-", "_") + ".png")
        save_texture(trail_texture(), path)
        register(eid, path, "shared", "add", "Breach Charge flight trail ribbon; head at the right edge (u = 1), fades to the tail.", 1, 1, 1, 0, False, 0,
                 pivot="right_center", render_type="texture",
                 notes="512x128 static texture. Use on a camera-facing quad stretched from the projectile back along its velocity (about 0.12 s of travel), or as a ribbon trail texture.")
        write_index("breach_trail")


if __name__ == "__main__":
    build(sys.argv[1] if len(sys.argv) > 1 else None)
