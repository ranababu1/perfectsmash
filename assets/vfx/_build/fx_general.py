"""General destruction effects: sparks, arcs, energy, smoke, fire, dust, debris atlases, critical asset, particle textures."""
import math, os, sys
import numpy as np
from vfxlib import *
from fx_kinetic import CYAN, WARM, ELEC, WHITE

RED = [(0.0, "#2a0408"), (0.35, "#9e1424"), (0.65, "#ff3b4e"), (1.0, "#ffc2c8"), (1.4, "#ffffff")]
FIRE = [(0.0, "#1a0702"), (0.2, "#6a210a"), (0.42, "#c2501a"), (0.62, "#ec8a2c"), (0.8, "#f6b456"), (1.0, "#ffe2a6"), (1.3, "#ffffff")]


def contrast(v, k=2.2):
    return np.clip((v - 0.5) * k + 0.5, 0, 1)


def shade(D, rgb_dark, rgb_light, light_dir=(-0.6, -0.8), amount=6.0):
    """Fake volumetric light: brighter where density falls off toward the light."""
    gy, gx = np.gradient(ndi.gaussian_filter(D, 2.0))
    l = np.clip(0.5 - amount * (gx * light_dir[0] + gy * light_dir[1]) * D.shape[0] / 64, 0, 1)
    l = l * 0.7 + 0.3 * (1 - np.clip(D, 0, 1))  # thin parts lighter
    return np.asarray(rgb_dark)[None, None] * (1 - l[..., None]) + np.asarray(rgb_light)[None, None] * l[..., None]


def volume(D, dark, light, absorb=2.2, shadow=1.6, offset=(-0.035, -0.05), ambient=0.25):
    """Beer-Lambert style alpha plus self-shadowing by sampling density toward the light (upper left)."""
    n = D.shape[0]
    D = np.clip(D, 0, None)
    alpha = 1 - np.exp(-absorb * D)
    sh = ndi.shift(ndi.gaussian_filter(D, n * 0.01), (-offset[1] * n * 0.5 * -1, -offset[0] * n * 0.5 * -1), order=1, mode="constant")
    lit = np.exp(-shadow * sh)
    l = ambient + (1 - ambient) * lit
    rgb = np.asarray(dark)[None, None] * (1 - l[..., None]) + np.asarray(light)[None, None] * l[..., None]
    return rgb, alpha


def flow_loop(F, n, base, octaves, seed, dist=0.5, axis_scale=(1.0, 1.0)):
    """Seamless looping noise that drifts upward: two scrolled copies crossfaded (classic flow-map loop)."""
    big = fbm2(int(n * (1 + dist) * axis_scale[0]) + 2, int(n * axis_scale[1]), base=base, octaves=octaves, seed=seed)
    big = ndi.zoom(big, (1 / axis_scale[0], 1 / axis_scale[1]), order=1) if axis_scale != (1.0, 1.0) else big
    H = big.shape[0]; D = int(n * dist)
    out = []
    for i in range(F):
        p = i / F
        o1 = int(round(D * p)); o2 = int(round(D * (p + 1))) if False else o1 + D  # second copy one period behind
        a1 = big[D - o1 + 0: D - o1 + n] if D - o1 + n <= H else big[-n:]
        a2 = big[max(0, D * 2 - o2 if D * 2 - o2 >= 0 else 0): max(0, D * 2 - o2) + n] if False else None
        out.append(a1)
    # proper crossfade version
    out = []
    for i in range(F):
        p = i / F
        y1 = int(round(D * (1 - p)))                # layer A scrolls up
        y2 = int(round(D * (1 - ((p + 0.5) % 1))))  # layer B half a cycle later
        w = abs(1 - 2 * p)                          # A visible at p=0, fades out at p=0.5
        A = big[y1:y1 + n, :n]; B = big[y2:y2 + n, :n]
        out.append(A * w + B * (1 - w))
    return np.stack(out)


def spark_burst(n=256, F=16, seed=201):
    sp = spark_system(n, F, 46, seed, origin=(0, 0.05), dir_angle=-math.pi / 2, spread=2 * math.pi, speed=(1.8, 3.8),
                      gravity=2.4, life=(0.35, 0.9), drag=2.0, width=(0.007, 0.013), color_hot="#ffffff", color_cool="#ffc070",
                      trail=0.07, intensity=2.2, start=(0.0, 0.12))
    x, y, r, a = grid(n)
    frames = []
    for i in range(F):
        t = (i + 0.5) / F
        d = np.hypot(x, y - 0.05)
        I = 1.8 * np.exp(-(d / (0.05 + 0.08 * t)) ** 2) * max(0.0, 1 - t / 0.25)
        light = ramp(np.clip(I, 0, 1.6), WARM) * np.clip(I, 0, 1.6)[..., None] + sp[i]
        frames.append(additive_from_light(ndi.gaussian_filter(light, (0.5, 0.5, 0))))
    return frames


def arc_loop(n=256, F=16, seed=211):
    """Electrical arcing between left and right contact points (u = 0.12 and 0.88). Random flicker; loop with random start frame."""
    rng = np.random.default_rng(seed)
    x, y, r, a = grid(n)
    frames = []
    for i in range(F):
        lines = []
        for k in range(rng.integers(1, 3)):
            lines += lightning(rng, -0.76, rng.normal(0, 0.02), 0.76, rng.normal(0, 0.02), depth=7, rough=0.17, branch_p=0.22)
        keep = []
        for pts, lvl in lines:
            m = max(max(abs(px), abs(py)) for px, py in pts)
            if lvl == 0 and m > 0.8:
                pts = [(px, py * 0.8 / max(abs(py) for _, py in pts) if max(abs(py) for _, py in pts) > 0.8 else py) for px, py in pts]
                m = max(max(abs(px), abs(py)) for px, py in pts)
            if m <= 0.82:
                keep.append((pts, lvl))
        lines = keep
        core = draw_polylines(n, lines, core_w=0.007)
        glow = ndi.gaussian_filter(core, n * 0.012) * 4.5
        flick = 1.0 if i % 5 else 0.55
        contacts = 1.3 * (np.exp(-(((x + 0.76) ** 2 + y ** 2) / 0.05 ** 2)) + np.exp(-(((x - 0.76) ** 2 + y ** 2) / 0.05 ** 2)))
        I = (core * 1.6 + glow * 0.7) * flick + contacts
        frames.append(light_to_frame(I, ELEC))
    return frames


def energy_discharge(n=256, F=16, seed=221):
    """Cyan energy discharge: brief implosion, then plasma burst with curling tendrils and a ring."""
    rng = np.random.default_rng(seed)
    x, y, r, a = grid(n)
    N = contrast(fbm3(F, n, n, base=5, tcells=3, octaves=4, seed=seed), 2.6)
    tend = []
    for k in range(9):
        ang = 2 * math.pi * k / 9 + rng.uniform(-0.2, 0.2)
        tend += lightning(rng, 0, 0, math.cos(ang) * 0.7, math.sin(ang) * 0.7, depth=5, rough=0.22, branch_p=0.2)
    T = draw_polylines(n, tend, core_w=0.010)
    T = ndi.gaussian_filter(T, 1.0)
    frames = []
    for i in range(F):
        t = (i + 0.5) / F
        if t < 0.2:
            u = t / 0.2
            I = (0.6 + 1.4 * u) * np.exp(-(r / (0.32 * (1 - u) + 0.08)) ** 2) * (0.6 + 0.6 * N[i])
        else:
            u = (t - 0.2) / 0.8
            R = 0.12 + 0.6 * ease_out(u, 2.2)
            body = smooth(R, R * 0.3, r) * (0.4 + 0.9 * N[i]) * (1 - u) ** 1.4 * 1.3
            ring = np.exp(-((r - R) / (0.02 + 0.03 * u)) ** 2) * (1 - u) ** 1.6 * 1.2
            reach = smooth(R * 1.15, R * 0.8, r)
            I = body + ring + T * reach * 1.6 * (1 - u) ** 1.2 + 2.2 * np.exp(-(r / 0.1) ** 2) * max(0.0, 1 - u / 0.2)
        frames.append(light_to_frame(I, CYAN, blur=0.6))
    return frames


def smoke_puff(n=256, F=16, seed=231, tint=("#23282c", "#9aa2a8"), rise=0.25, grow=(0.22, 0.72), density=1.0, puffs=16, fade_pow=1.2):
    x, y, r, a = grid(n)
    N1 = fbm3(F, n, n, base=4, tcells=2, octaves=5, seed=seed)
    rng = np.random.default_rng(seed)
    lobes = [(2 * math.pi * k / puffs + rng.uniform(-0.3, 0.3), rng.uniform(0.15, 0.75), rng.uniform(0.45, 0.8), rng.uniform(0.7, 1.1)) for k in range(puffs)]
    frames = []
    for i in range(F):
        t = (i + 0.5) / F
        R = grow[0] + (grow[1] - grow[0]) * ease_out(t, 2.0)
        cy = -rise * ease_out(t, 1.5)
        D = np.zeros_like(x)
        for ang, d, s_, w in lobes:
            px = math.cos(ang) * d * R * 0.75; py = cy + math.sin(ang) * d * R * 0.6
            D += w * np.exp(-(((x - px) ** 2 + (y - py) ** 2) / (R * s_ * 0.5) ** 2))
        erosion = contrast(N1[i], 2.0)
        Dn = np.clip(D * (0.25 + 1.15 * erosion) - 0.15 - 0.3 * t * (1 - erosion), 0, None) ** 1.4 * 0.8
        k = density * (1 - t) ** fade_pow * smooth(0, 0.1, t + 0.03)
        rgb, al = volume(Dn * k, hexc(tint[0]), hexc(tint[1]), absorb=1.7)
        frames.append(np.dstack([rgb, np.clip(al, 0, 1)]).astype(np.float32))
    return frames


def smoke_loop(n=256, F=16, seed=241):
    """Seamless rising smoke column from a source at the bottom centre (pivot bottom)."""
    x, y, r, a = grid(n)
    N = scroll_loop(F, n, period_mult=1, base=4, octaves=5, seed=seed)
    N2 = lattice_noise((F, n, n), (4, 3, 3), seed + 9, wrap_t=True)
    frames = []
    v = (1 - y) / 2  # 0 at bottom, 1 at top
    for i in range(F):
        width = 0.12 + 0.42 * v ** 0.8
        col = np.exp(-(x / width) ** 2)
        Dn = np.clip(col * (0.15 + 1.2 * contrast(N[i] * 0.75 + N2[i] * 0.25, 2.2)) - 0.3, 0, None) * 1.1
        Dn *= smooth(0.0, 0.10, v) * smooth(0.9, 0.45, v) * (1 - 0.5 * v) * smooth(0.9, 0.6, np.abs(x))
        rgb, alpha = volume(Dn, hexc("#22272b"), hexc("#8d969c"), absorb=1.8)
        frames.append(np.dstack([rgb, np.clip(alpha, 0, 1)]).astype(np.float32))
    return frames


def fire_loop(n=256, F=16, seed=251):
    """Seamless burning fire from a bottom source, for burning components (pivot bottom centre)."""
    x, y, r, a = grid(n)
    N = scroll_loop(F, n, period_mult=1, base=5, octaves=5, seed=seed)
    N2 = lattice_noise((F, n, n), (4, 4, 4), seed + 9, wrap_t=True)
    v = (1 - y) / 2
    frames = []
    for i in range(F):
        width = 0.34 * (1 - v) ** 0.6 + 0.03
        base = np.exp(-(x / width) ** 2) * smooth(0.0, 0.12, v)
        flame = base * (contrast(N[i] * 0.8 + N2[i] * 0.2, 2.6) * 1.3 + 0.15) - v * 1.05 - 0.05
        I = np.clip(flame, 0, None) * 1.25
        I = I * smooth(0.92, 0.6, v)
        frames.append(light_to_frame(I, FIRE, blur=0.8))
    return frames


def dust_burst(n=256, F=16, seed=261, tint=("#5d564d", "#b3aa9c")):
    """Concrete dust: low outward puff of pale grit from an impact (mix)."""
    fr = smoke_puff(n=n, F=F, seed=seed, tint=tint, rise=0.12, grow=(0.18, 0.80), density=0.95)
    # add grit specks
    sp = spark_system(n, F, 50, seed, origin=(0, 0.1), dir_angle=-math.pi / 2, spread=math.radians(200), speed=(0.6, 2.0),
                      gravity=2.6, life=(0.4, 1.0), drag=2.4, width=(0.008, 0.014), trail=0.02, intensity=1.0, start=(0.0, 0.1))
    out = []
    for f, s in zip(fr, sp):
        g = np.clip(s.max(axis=-1), 0, 1) * 0.9
        rgb = f[..., :3] * (1 - g[..., None]) + hexc("#8d8476") * g[..., None]
        out.append(np.dstack([rgb, np.maximum(f[..., 3], g)]))
    return out


def collapse_dust(n=512, F=16, seed=271):
    """Component collapse: heavy ground-hugging billow rolling outward left and right (pivot bottom centre)."""
    x, y, r, a = grid(n)
    N1 = fbm3(F, n, n, base=4, tcells=2, octaves=5, seed=seed)
    N2 = fbm3(F, n, n, base=10, tcells=3, octaves=3, seed=seed + 3)
    rng = np.random.default_rng(seed)
    rolls = [(rng.uniform(-1, 1), rng.uniform(0.4, 1.0), rng.uniform(0.45, 1.6), rng.uniform(0.0, 0.3)) for _ in range(34)]
    frames = []
    for i in range(F):
        t = (i + 0.5) / F
        spread = 0.15 + 0.72 * ease_out(t, 2.2)
        D = np.zeros_like(x)
        for side, sp, s, t0 in rolls:
            tl = max(0.0, (t - t0) / (1 - t0))
            if tl <= 0:
                continue
            px = side * (0.12 + 0.60 * ease_out(tl, 2.2)) * sp; rad = (0.06 + 0.24 * ease_out(tl, 1.8)) * s * (1 - 0.3 * abs(side))
            py = 0.74 - rad * 0.9 - 0.30 * ease_out(tl, 1.3) * (1 - abs(side)) ** 2 * s
            D += np.exp(-(((x - px) ** 2) / (rad * 1.3) ** 2 + ((y - py) ** 2) / rad ** 2))
        Dn = np.clip(D * (0.25 + 1.2 * contrast(N1[i], 2.2)) * (0.7 + 0.6 * N2[i]) - 0.15, 0, None) ** 1.4 * 0.8
        Dn *= (1 - t) ** 0.9 * smooth(0, 0.1, t) * smooth(0.95, 0.80, y)
        rgb, alpha = volume(Dn, hexc("#34332f"), hexc("#b2ab9f"), absorb=1.8)
        frames.append(np.dstack([rgb, np.clip(alpha, 0, 1)]).astype(np.float32))
    return frames


def _poly(rng, k, jitter=0.35, elong=1.0):
    pts = []
    for j in range(k):
        th = 2 * math.pi * j / k + rng.uniform(-jitter, jitter)
        rr = rng.uniform(0.55, 1.0)
        pts.append((math.cos(th) * rr * elong, math.sin(th) * rr))
    return pts


def atlas(n=128, kind="chip", seed=281, count=16):
    """Static variant atlas (one variant per cell)."""
    rng = np.random.default_rng(seed)
    frames = []
    for v in range(count):
        cv = Canvas(n, ss=4)
        rot = rng.uniform(0, math.pi)
        if kind == "chip":
            pts = _poly(rng, int(rng.integers(5, 8)), 0.4, rng.uniform(0.8, 1.4)); sc = 0.62; base = rng.uniform(0.42, 0.62)
            col = np.array([base, base * 0.97, base * 0.92])
        elif kind == "fragment":
            k = int(rng.integers(4, 6)); pts = _poly(rng, k, 0.25, rng.uniform(1.0, 1.8)); sc = 0.6; base = rng.uniform(0.22, 0.36)
            col = np.array([base * 0.95, base, base * 1.06])
        else:  # glass
            pts = _poly(rng, 3 if rng.random() < 0.6 else 4, 0.6, rng.uniform(1.2, 2.2)); sc = 0.66
            col = np.array([0.78, 0.90, 0.96])
        P = [((px * math.cos(rot) - py * math.sin(rot)) * sc, (px * math.sin(rot) + py * math.cos(rot)) * sc) for px, py in pts]
        cx_ = sum(p_[0] for p_ in P) / len(P); cy_ = sum(p_[1] for p_ in P) / len(P)
        P = [(px - cx_, py - cy_) for px, py in P]
        ext = max(max(abs(px), abs(py)) for px, py in P)
        if ext > 0.8:
            P = [(px * 0.8 / ext, py * 0.8 / ext) for px, py in P]
        if kind == "glass":
            cv.polygon(P, col, alpha=0.38)
            inner = [(px * 0.86, py * 0.86) for px, py in P]
            # edge highlight = full poly bright minus inner
            buf_before = cv.buf.copy()
            cv.polygon(P, np.array([1, 1, 1]), alpha=0.95)
            edge = cv.buf.copy(); cv.buf = buf_before; cv.polygon(inner, col, alpha=0.38)
            cv2 = Canvas(n, ss=4); cv2.polygon(P, np.array([1, 1, 1]), 1.0); cv3 = Canvas(n, ss=4); cv3.polygon(inner, np.array([1, 1, 1]), 1.0)
            rim = np.clip(cv2.buf[..., 3] - cv3.buf[..., 3], 0, 1) * 0.9
            cv.buf[..., :3] = cv.buf[..., :3] * (1 - rim[..., None]) + rim[..., None]
            cv.buf[..., 3] = np.maximum(cv.buf[..., 3], rim)
        else:
            cv.polygon(P, col * 0.7)
            # facets: light top-left half, dark lower-right, plus edge highlight
            hl = [(px * 0.78 - 0.05, py * 0.78 - 0.06) for px, py in P]
            cv.polygon(hl, np.minimum(col * 1.18 + 0.03, 1))
            if kind == "fragment":
                # painted panel stripe and a bright cut edge
                ex0, ey0 = P[0]; ex1, ey1 = P[1]
                cv.streak(ex0, ey0, ex1, ey1, 0.02, 0.02, np.array([0.85, 0.88, 0.9]), 1.0, 1.0)
        res = unpremultiply(cv.result())
        if kind != "glass":
            # surface grain and a crisp lit rim on the upper-left edges
            g = fbm2(n, n, base=6, octaves=4, seed=int(rng.integers(1e6)))
            res[..., :3] *= (0.82 + 0.36 * g)[..., None]
            a_ = res[..., 3]
            gy, gx = np.gradient(ndi.gaussian_filter(a_, 0.8))
            rim = np.clip((gx * 0.7 + gy * 0.7) * n * 0.08, 0, 1) * a_  # alpha rising toward lower-right = upper-left edge
            res[..., :3] = res[..., :3] * (1 - rim[..., None]) + rim[..., None] * 0.92
        frames.append(res)
    return frames


def critical_destruction(n=512, F=16, seed=291):
    """Critical asset (core) destroyed: red-white implosion, white flash, red shockwave and white shards."""
    rng = np.random.default_rng(seed)
    x, y, r, a = grid(n)
    N = contrast(fbm3(F, n, n, base=5, tcells=3, octaves=4, seed=seed), 2.4)
    shards = [(rng.uniform(0, 2 * math.pi), rng.uniform(0.5, 1.0), rng.uniform(0.006, 0.012)) for _ in range(40)]
    frames = []
    for i in range(F):
        t = (i + 0.5) / F
        cv = Canvas(n, ss=1, channels=3)
        if t < 0.18:
            u = t / 0.18
            I = (0.8 + 1.6 * u) * np.exp(-(r / (0.25 * (1 - u) + 0.05)) ** 2)
            I += np.exp(-((r - 0.45 * (1 - u)) / 0.02) ** 2) * u * 1.2
            light = ramp(np.clip(I, 0, 1.6), RED) * np.clip(I, 0, 1.6)[..., None]
        else:
            u = (t - 0.18) / 0.82
            flash = 3.0 * np.exp(-(r / (0.12 + 0.4 * u)) ** 2) * max(0.0, 1 - u / 0.3) ** 1.5
            R = 0.1 + 0.75 * ease_out(u, 2.2)
            ring = 1.4 * np.exp(-((r - R) / (0.015 + 0.03 * u)) ** 2) * (1 - u) ** 1.5 * (0.6 + 0.6 * N[i])
            body = 0.8 * smooth(R * 0.9, R * 0.2, r) * N[i] * (1 - u) ** 2
            I = flash + ring + body
            light = ramp(np.clip(I, 0, 1.6), RED) * np.clip(I, 0, 1.6)[..., None]
            for ang, v, w in shards:
                d0 = 0.08 + v * ease_out(u, 2.6) * 0.8; d1 = max(0.04, d0 - 0.25 * (1 - u) * v)
                cv.streak(math.cos(ang) * d1, math.sin(ang) * d1, math.cos(ang) * d0, math.sin(ang) * d0, w * 0.5, w,
                          np.array([1.0, 0.9, 0.92]) * 2.0 * (1 - u) ** 1.2, 0.2, 1.0)
            light = light + cv.result()
        frames.append(additive_from_light(ndi.gaussian_filter(light, (0.6, 0.6, 0))))
    return frames


def critical_idle(n=256, F=16):
    """Critical asset idle loop: red core pulse with a slow rotating bracket ring (seamless)."""
    x, y, r, a = grid(n)
    frames = []
    for i in range(F):
        ph = i / F
        p = 0.5 + 0.5 * math.cos(2 * math.pi * ph)
        core = (0.6 + 0.6 * p) * np.exp(-(r / 0.16) ** 2)
        halo = 0.25 * (0.7 + 0.3 * p) * np.exp(-(r / 0.45) ** 2)
        seg = (np.cos(4 * (a - 2 * math.pi * ph / 4)) > 0.55).astype(np.float32)
        ring = np.exp(-((r - 0.62) / 0.012) ** 2) * seg * 0.9
        I = core + halo + ring
        frames.append(light_to_frame(I, RED, blur=0.6))
    return frames


JOBS = [
    dict(id="SHR-VFX-SPARK_BURST-A", fn=spark_burst, n=256, C=4, R=4, fps=30, loop=False, blend="add",
         purpose="Omnidirectional spark burst with gravity; damage state 'sparking', machinery breaking, cut cables.",
         notes="Re-trigger every 0.6-1.4 s with random rotation and scale 0.7-1.2 for the sparking state."),
    dict(id="SHR-VFX-ARC_ELECTRIC_LOOP-A", fn=arc_loop, n=256, C=4, R=4, fps=24, loop=True, blend="add", pivot="center",
         purpose="Electrical arc crackling between two contacts at u = 0.12 and u = 0.88 (stretch the quad between the two points).",
         notes="Frames are independent flicker states; loop and start on a random frame. Chapter tints: none needed (electric blue reads everywhere)."),
    dict(id="SHR-VFX-ENERGY_DISCHARGE-A", fn=energy_discharge, n=256, C=4, R=4, fps=24, loop=False, blend="add",
         purpose="Energy discharge (cells, capacitors, power cores): implosion then cyan plasma burst with tendrils.",
         notes="Tintable: Nova Grid uses the dedicated overload sheet; for VITA multiply by #7FD9A8."),
    dict(id="SHR-VFX-SMOKE_PUFF-A", fn=smoke_puff, n=256, C=4, R=4, fps=16, loop=False, blend="mix",
         purpose="Grey smoke puff that billows, rises and fades; follow-up after blasts and component destruction.",
         notes="1 s at 16 fps. Spawn 3-6 as CPUParticles3D with random rotation and scale 1-2.5 m; lit from upper left."),
    dict(id="SHR-VFX-SMOKE_LOOP-A", fn=smoke_loop, n=256, C=4, R=4, fps=12, loop=True, blend="mix", pivot="bottom_center",
         purpose="Seamless rising smoke column for damaged / burning components (pivot bottom centre).",
         notes="Seamless loop (crossfaded scrolling noise). Stack two at different scales and fps for depth."),
    dict(id="SHR-VFX-FIRE_LOOP-A", fn=fire_loop, n=256, C=4, R=4, fps=20, loop=True, blend="add", pivot="bottom_center",
         purpose="Seamless fire loop for burning components (pivot bottom centre). Amber is reserved for blasts and danger, which burning is.",
         notes="Pair with SHR-VFX-SMOKE_LOOP-A above it."),
    dict(id="SHR-VFX-DUST_CONCRETE-A", fn=dust_burst, n=256, C=4, R=4, fps=20, loop=False, blend="mix",
         purpose="Concrete / composite impact dust: pale grit puff and falling specks."),
    dict(id="SHR-VFX-DUST_COLLAPSE-A", fn=collapse_dust, n=512, C=4, R=4, fps=16, loop=False, blend="mix", pivot="bottom_center",
         purpose="Component collapse dust: heavy ground-hugging billow rolling outward (pivot bottom centre, ground at v = 0.86).",
         notes="Frame width = 2.5 x the collapsed component width. Play when a component topples or is removed at ground level."),
    dict(id="SHR-VFX-DEBRIS_CHIP_SMALL-A", fn=atlas, n=128, C=4, R=4, fps=1, loop=False, blend="mix", kwargs=dict(kind="chip", seed=281),
         purpose="Small concrete / stone debris chips, 16 variants (not an animation: pick one cell per particle).",
         notes="Variant atlas. Godot: particles_anim_h_frames = 4, v_frames = 4, anim_speed 0, anim_offset_min 0, max 1 for a random variant. Tint per material."),
    dict(id="SHR-VFX-DEBRIS_FRAGMENT_LARGE-A", fn=atlas, n=256, C=4, R=4, fps=1, loop=False, blend="mix", kwargs=dict(kind="fragment", seed=291),
         purpose="Large metal / panel fragments with a bright cut edge, 16 variants (pick one cell per particle).",
         notes="Variant atlas, as above. Use with angular velocity 90-360 deg/s."),
    dict(id="SHR-VFX-GLASS_SHARD-A", fn=atlas, n=128, C=4, R=4, fps=1, loop=False, blend="mix", kwargs=dict(kind="glass", seed=301),
         purpose="Glass fragment variants: translucent cold-white shards with bright rims, 16 variants.",
         notes="Variant atlas. Add a little emission (or a second additive pass) for glints."),
    dict(id="SHR-VFX-CRITICAL_CORE_DESTRUCTION-A", fn=critical_destruction, n=512, C=4, R=4, fps=24, loop=False, blend="add",
         purpose="Critical asset destroyed: red implosion, white flash, red shockwave and white shards (mission-winning moment).",
         notes="Red #FF3B4E family matches the critical-asset marker. Layer with SHR-VFX-ENERGY_DISCHARGE-A and the Breach explosion for big cores."),
    dict(id="SHR-VFX-CRITICAL_CORE_IDLE-A", fn=critical_idle, n=256, C=4, R=4, fps=16, loop=True, blend="add",
         purpose="Critical asset idle glow loop (red pulse with rotating bracket ring) on the core until it is destroyed."),
]


def particle_textures():
    x, y, r, a = grid(128)
    out = []
    # soft glow dot
    I = np.exp(-(r / 0.42) ** 2) * 1.0 + 0.6 * np.exp(-(r / 0.12) ** 2)
    out.append(("SHR-VFX-PARTICLE_GLOW-A", light_to_frame(I, WHITE), "add", "Soft round glow for generic additive particles (embers, motes, energy). Tint with color."))
    # ring
    I = np.exp(-((r - 0.6) / 0.05) ** 2)
    out.append(("SHR-VFX-PARTICLE_RING-A", light_to_frame(I, WHITE), "add", "Thin soft ring for pulses and scaled shockwaves. Tint with color."))
    # spark streak (128x32)
    xs = (np.arange(128) + 0.5) / 128 * 2 - 1; ys = (np.arange(32) + 0.5) / 32 * 2 - 1
    Y, X = np.meshgrid(ys, xs, indexing="ij")
    I = np.exp(-(Y / 0.22) ** 2) * smooth(-1, 0.6, X) * smooth(1.0, 0.75, X) * 1.2
    out.append(("SHR-VFX-PARTICLE_SPARK-A", light_to_frame(I, WHITE), "add", "Spark streak 128x32, head at the right. Use with billboard mode 'particles' and velocity-aligned (particle_flag_align_y) or as a stretched quad."))
    # dust mote / soft puff
    n = fbm2(128, 128, base=4, octaves=4, seed=9)
    D = np.exp(-(r / 0.6) ** 2) * (0.5 + 0.9 * contrast(n, 1.6)) - 0.15
    al = smooth(0, 0.8, D)
    rgb = shade(D, hexc("#5a5a5a"), hexc("#d0d0d0"))
    out.append(("SHR-VFX-PARTICLE_SMOKE-A", np.dstack([rgb, al]), "mix", "Single soft smoke / dust puff, neutral grey; tint per material (concrete #B3AA9C, VITA vapour #7FD9A8)."))
    return out


def threshold_line():
    """Topple threshold marker: dashed red line with soft glow, 512x64 (tile along u)."""
    w, h = 512, 64
    xs = (np.arange(w) + 0.5) / w; ys = (np.arange(h) + 0.5) / h * 2 - 1
    Y, X = np.meshgrid(ys, xs, indexing="ij")
    dash = smooth(0.0, 0.02, (X * 8) % 1) * smooth(0.62, 0.6, (X * 8) % 1)
    I = (np.exp(-(Y / 0.06) ** 2) * dash * 1.2 + np.exp(-(Y / 0.35) ** 2) * 0.25 * (0.4 + 0.6 * dash))
    return light_to_frame(I, RED)


def build(only=None):
    run_jobs(JOBS, "general", only)
    if not only or "PARTICLE" in only or "THRESHOLD" in only:
        for eid, f, blend, purpose in particle_textures():
            path = os.path.join(VFX, "shared", "particles", eid.lower().replace("-", "_") + ".png")
            save_texture(f, path)
            register(eid, path, "shared", blend, purpose, 1, 1, 1, 0, False, 0, render_type="texture",
                     notes="Particle texture (not animated). Power-of-two, straight alpha, 2 px empty border.")
        eid = "SHR-VFX-THRESHOLD_LINE-A"
        path = os.path.join(VFX, "shared", eid.lower().replace("-", "_") + ".png")
        save_texture(threshold_line(), path)
        register(eid, path, "shared", "add", "Topple threshold marker line (dashed red with soft glow); tiles along u.", 1, 1, 1, 0, False, 0,
                 render_type="texture", pivot="center",
                 notes="512x64, tiles horizontally (8 dashes per tile). Use on a quad or Line2D/MeshInstance3D strip with texture repeat on.")
        write_index("general_textures")


if __name__ == "__main__":
    build(sys.argv[1] if len(sys.argv) > 1 else None)
