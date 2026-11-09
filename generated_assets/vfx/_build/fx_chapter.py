"""Chapter-specific effects (Helix, VITA, Nova Grid, Civitas, Meridian)."""
import math, os, sys
import numpy as np
from vfxlib import *
from fx_general import contrast, volume

HELIX = [(0.0, "#031c24"), (0.4, "#1f8fb0"), (0.75, "#3cc8e6"), (1.0, "#c8f5ff"), (1.4, "#ffffff")]
HELIX_AMB = [(0.0, "#2a1406"), (0.5, "#f2a23a"), (1.0, "#ffe0b0"), (1.4, "#ffffff")]
NOVA = [(0.0, "#04122e"), (0.35, "#1f5fc8"), (0.65, "#4aa8ff"), (0.9, "#cfe6ff"), (1.4, "#ffffff")]
NOVA_AMB = [(0.0, "#2a1406"), (0.5, "#f0a040"), (1.0, "#ffe0b0"), (1.4, "#ffffff")]
CIV = [(0.0, "#0b1622"), (0.45, "#5f88b0"), (0.8, "#8eb6da"), (1.1, "#e6f0fa"), (1.4, "#ffffff")]
CIV_RED = [(0.0, "#2a0608"), (0.5, "#e5484d"), (1.0, "#ffc4c6"), (1.4, "#ffffff")]
MRD = [(0.0, "#120a2e"), (0.4, "#6a52d6"), (0.75, "#a592ff"), (1.0, "#e4ddff"), (1.4, "#ffffff")]
MRD_CY = [(0.0, "#04202a"), (0.5, "#7fe6f2"), (1.0, "#e2fbff"), (1.4, "#ffffff")]


def data_corruption(n=256, F=16, seed=401):
    """Helix: digital corruption loop: tearing scan blocks, pixel shards, cyan with rare amber faults."""
    rng = np.random.default_rng(seed)
    x, y, r, a = grid(n)
    env = smooth(0.95, 0.45, r)
    frames = []
    for i in range(F):
        I = np.zeros((n, n), np.float32); J = np.zeros((n, n), np.float32)
        # horizontal tear bands
        for _ in range(rng.integers(3, 7)):
            y0 = rng.uniform(-0.7, 0.7); h = rng.uniform(0.01, 0.06); x0 = rng.uniform(-0.8, 0.2); w = rng.uniform(0.2, 0.9)
            band = ((y > y0) & (y < y0 + h) & (x > x0) & (x < x0 + w)).astype(np.float32)
            stripes = 0.55 + 0.45 * (np.sin((x + rng.uniform()) * n * rng.uniform(0.3, 0.9)) > 0)
            I += band * stripes * rng.uniform(0.5, 1.1)
        # blocks (quantised to an 8 px grid so it reads as data)
        g = 16
        cells = (rng.random((g, g)) < 0.10).astype(np.float32) * rng.uniform(0.4, 1.2, (g, g))
        blocks = np.kron(cells, np.ones((n // g, n // g), np.float32))
        I += blocks * (0.6 + 0.4 * (np.indices((n, n))[0] % 4 < 2))
        if rng.random() < 0.35:
            fc = (rng.random((g, g)) < 0.04).astype(np.float32)
            J += np.kron(fc, np.ones((n // g, n // g), np.float32)) * 1.1
        # scanlines and centre glow
        I *= 0.85 + 0.15 * (np.indices((n, n))[0] % 3 == 0)
        I = I * env + 0.25 * np.exp(-(r / 0.35) ** 2) * rng.uniform(0.6, 1.0)
        L = ramp(np.clip(I, 0, 1.4), HELIX) * np.clip(I, 0, 1.4)[..., None] + ramp(np.clip(J * env, 0, 1.4), HELIX_AMB) * np.clip(J * env, 0, 1.4)[..., None]
        # chromatic offset: shift red slightly for an RGB-split feel
        L[..., 0] = np.roll(L[..., 0], 2, axis=1)
        frames.append(additive_from_light(ndi.gaussian_filter(L, (0.4, 0.4, 0))))
    return frames


def electrical_overload(n=256, F=16, seed=411):
    """Helix: server / relay overload: arcs build around a core, then a sharp pop with sparks."""
    rng = np.random.default_rng(seed)
    x, y, r, a = grid(n)
    sp = spark_system(n, F, 40, seed, spread=2 * math.pi, speed=(1.2, 2.9), gravity=1.8, life=(0.3, 0.7), drag=2.2,
                      width=(0.006, 0.012), color_hot="#ffffff", color_cool="#f2a23a", trail=0.06, intensity=2.0, start=(0.55, 0.62))
    frames = []
    for i in range(F):
        t = (i + 0.5) / F
        if t < 0.55:
            u = t / 0.55
            lines = []
            for _ in range(int(2 + 6 * u)):
                ang = rng.uniform(0, 2 * math.pi); L = rng.uniform(0.25, 0.45) + 0.2 * u
                lines += lightning(rng, math.cos(ang) * 0.08, math.sin(ang) * 0.08, math.cos(ang) * L, math.sin(ang) * L, depth=5, rough=0.3, branch_p=0.25)
            core = draw_polylines(n, lines, core_w=0.006)
            I = core * 1.5 + ndi.gaussian_filter(core, n * 0.012) * 4 * (0.4 + 0.6 * u) + (0.5 + 1.2 * u) * np.exp(-(r / (0.10 + 0.05 * u)) ** 2)
            I *= rng.uniform(0.75, 1.0)
            light = ramp(np.clip(I, 0, 1.5), HELIX) * np.clip(I, 0, 1.5)[..., None]
        else:
            u = (t - 0.55) / 0.45
            flash = 2.8 * np.exp(-(r / (0.10 + 0.4 * u)) ** 2) * max(0.0, 1 - u / 0.35) ** 1.4
            R = 0.12 + 0.6 * ease_out(u, 2.4)
            ring = 1.2 * np.exp(-((r - R) / (0.015 + 0.02 * u)) ** 2) * (1 - u) ** 1.6
            I = flash + ring
            light = ramp(np.clip(I, 0, 1.5), HELIX) * np.clip(I, 0, 1.5)[..., None]
        light = light + sp[i]
        frames.append(additive_from_light(light))
    return frames


def containment_leak(n=256, F=16, seed=421):
    """VITA: pressurised containment leak: pale green vapour jet venting to the right from a nozzle at u = 0.1 (seamless loop)."""
    x, y, r, a = grid(n)
    N = scroll_loop(F, n, period_mult=1, base=4, octaves=5, seed=seed)  # scrolls along rows; transpose to scroll along x
    N2 = lattice_noise((F, n, n), (4, 3, 3), seed + 3, wrap_t=True)
    u = (x + 0.8) / 1.6  # 0 at nozzle, 1 at far end
    frames = []
    for i in range(F):
        Nx = N[i].T[:, ::-1]  # drift toward +x
        width = 0.05 + 0.42 * np.clip(u, 0, 1) ** 0.85
        jet = np.exp(-(y / width) ** 2) * smooth(-0.02, 0.06, u) * smooth(1.05, 0.55, u)
        Dn = np.clip(jet * (0.25 + 1.2 * contrast(Nx * 0.8 + N2[i] * 0.2, 2.2)) - 0.18, 0, None) ** 1.2 * 1.1
        Dn *= (1 - 0.55 * np.clip(u, 0, 1))
        rgb, al = volume(Dn, hexc("#1f3a30"), hexc("#bff0d6"), absorb=1.6)
        # hot-white nozzle core so the source reads
        core = np.exp(-(((x + 0.78) / 0.06) ** 2 + (y / 0.05) ** 2)) * 0.9
        rgb = rgb * (1 - core[..., None]) + hexc("#e8fff2") * core[..., None]
        al = np.maximum(al, core)
        frames.append(np.dstack([rgb, np.clip(al * 0.9, 0, 1)]).astype(np.float32))
    return frames


def nova_overload(n=512, F=16, seed=431):
    """Nova Grid: energy overload: unstable blue plasma ball with amber arcs, swelling, then bursting."""
    rng = np.random.default_rng(seed)
    x, y, r, a = grid(n)
    N = contrast(fbm3(F, n, n, base=4, tcells=4, octaves=5, seed=seed), 2.6)
    frames = []
    for i in range(F):
        t = (i + 0.5) / F
        if t < 0.6:
            u = t / 0.6
            R = 0.14 + 0.12 * u + 0.02 * math.sin(i * 2.3)
            body = smooth(R * 1.15, R * 0.4, r * (1 + 0.25 * (N[i] - 0.5))) * (0.7 + 0.8 * N[i]) * (0.8 + 0.6 * u)
            lines = []
            for _ in range(int(2 + 5 * u)):
                ang = rng.uniform(0, 2 * math.pi)
                lines += lightning(rng, math.cos(ang) * R * 0.8, math.sin(ang) * R * 0.8, math.cos(ang) * (R + 0.25 + 0.2 * u), math.sin(ang) * (R + 0.25 + 0.2 * u), depth=5, rough=0.3, branch_p=0.3)
            arcs = draw_polylines(n, lines, core_w=0.005)
            arcs = arcs * 1.4 + ndi.gaussian_filter(arcs, n * 0.01) * 3.5
            light = ramp(np.clip(body, 0, 1.5), NOVA) * np.clip(body, 0, 1.5)[..., None] + ramp(np.clip(arcs, 0, 1.4), NOVA_AMB) * np.clip(arcs, 0, 1.4)[..., None]
        else:
            u = (t - 0.6) / 0.4
            flash = 3.0 * np.exp(-(r / (0.15 + 0.5 * u)) ** 2) * max(0.0, 1 - u / 0.4) ** 1.3
            R = 0.2 + 0.65 * ease_out(u, 2.3)
            ring = 1.3 * np.exp(-((r - R) / (0.02 + 0.03 * u)) ** 2) * (1 - u) ** 1.4 * (0.6 + 0.6 * N[i])
            body = 0.8 * smooth(R, R * 0.3, r) * N[i] * (1 - u) ** 1.8
            I = flash + ring + body
            light = ramp(np.clip(I, 0, 1.6), NOVA) * np.clip(I, 0, 1.6)[..., None]
        frames.append(additive_from_light(ndi.gaussian_filter(light, (0.6, 0.6, 0))))
    return frames


def sensor_disruption(n=256, F=16, seed=441):
    """Civitas: sensor / surveillance disruption loop: scanning sweep jammed by interference rings, static and red fault pings."""
    rng = np.random.default_rng(seed)
    x, y, r, a = grid(n)
    env = smooth(0.92, 0.6, r)
    frames = []
    for i in range(F):
        ph = i / F
        sweep_ang = 2 * math.pi * ph
        da = np.angle(np.exp(1j * (a - sweep_ang)))
        sweep = np.exp(-(np.clip(-da, 0, None) / 0.6)) * (da <= 0) * smooth(0.85, 0.2, r) * 0.6
        rings = 0
        for k in range(3):
            R = ((ph + k / 3) % 1.0) * 0.85
            rings = rings + np.exp(-((r - R) / 0.012) ** 2) * (1 - R / 0.85) * 0.9
        static = (rng.random((n // 4, n // 4)) ** 6)
        static = np.kron(static, np.ones((4, 1)))[:, :].repeat(4, axis=1)[:n, :n] * 0.6
        bands = np.zeros((n, n), np.float32)
        for _ in range(2):
            y0 = rng.uniform(-0.6, 0.6); bands += ((y > y0) & (y < y0 + rng.uniform(0.02, 0.05))) * rng.uniform(0.3, 0.7)
        I = (sweep + rings + static * 0.5 + bands * 0.6) * env
        J = np.zeros((n, n), np.float32)
        if i % 4 in (1, 2):
            px, py = rng.uniform(-0.4, 0.4, 2)
            J += np.exp(-(((x - px) ** 2 + (y - py) ** 2) / 0.03 ** 2)) * 1.4
            J += np.exp(-((np.hypot(x - px, y - py) - 0.08) / 0.008) ** 2) * 0.8
        L = ramp(np.clip(I, 0, 1.4), CIV) * np.clip(I, 0, 1.4)[..., None] + ramp(np.clip(J, 0, 1.4), CIV_RED) * np.clip(J, 0, 1.4)[..., None]
        frames.append(additive_from_light(ndi.gaussian_filter(L, (0.5, 0.5, 0))))
    return frames


def temporal_distortion(n=512, F=16, seed=451):
    """Meridian: temporal distortion loop: seamless violet ripple rings with cyan echo offsets around a dark eye."""
    x, y, r, a = grid(n)
    N = lattice_noise((F, n, n), (4, 5, 5), seed, wrap_t=True)
    frames = []
    for i in range(F):
        ph = i / F
        I = np.zeros((n, n), np.float32); J = np.zeros((n, n), np.float32)
        wob = 0.03 * (N[i] - 0.5)
        for k in range(4):
            u = (ph + k / 4) % 1.0
            R = 0.12 + 0.72 * u
            fade = math.sin(math.pi * u) ** 1.5
            I += np.exp(-((r + wob - R) / (0.012 + 0.02 * u)) ** 2) * fade * 0.95
            J += np.exp(-((r + wob - R * 0.94) / (0.008 + 0.01 * u)) ** 2) * fade * 0.55  # echo ring just inside
        # angular shimmer bands and dark eye
        shimmer = 0.6 + 0.4 * np.cos(6 * a + 2 * math.pi * ph + 8 * N[i])
        I *= shimmer
        I += 0.25 * np.exp(-((r - 0.1) / 0.06) ** 2) * (0.7 + 0.3 * math.cos(2 * math.pi * ph))
        L = ramp(np.clip(I, 0, 1.4), MRD) * np.clip(I, 0, 1.4)[..., None] + ramp(np.clip(J, 0, 1.4), MRD_CY) * np.clip(J, 0, 1.4)[..., None]
        frames.append(additive_from_light(ndi.gaussian_filter(L, (0.6, 0.6, 0))))
    return frames


def quantum_instability(n=256, F=16, seed=461):
    """Meridian: quantum instability loop: points blink in and out in displaced pairs, small cube shards flicker between positions."""
    rng = np.random.default_rng(seed)
    pts = [(rng.uniform(-0.6, 0.6), rng.uniform(-0.6, 0.6), rng.uniform(0, 1), rng.uniform(0.015, 0.035)) for _ in range(26)]
    x, y, r, a = grid(n)
    frames = []
    for i in range(F):
        ph = i / F
        cv = Canvas(n, ss=2, channels=3)
        cv2 = Canvas(n, ss=2, channels=3)
        for px, py, off, s in pts:
            u = (ph + off) % 1.0
            on = max(0.0, math.sin(2 * math.pi * u)) ** 3
            # displaced echo (the 'other' timeline position)
            ex, ey = px + 0.12 * math.cos(off * 12), py + 0.12 * math.sin(off * 12)
            cv.splat(px, py, s, np.array([1, 1, 1]) * 1.4 * on)
            cv2.splat(ex, ey, s * 0.8, np.array([1, 1, 1]) * 1.1 * (1 - on) * (u > 0.5))
            if on > 0.6:
                cv.streak(px, py, ex, ey, 0.004, 0.004, np.array([1, 1, 1]) * 0.6, 1.0, 0.2)
        A = cv.result()[..., 0]; B = cv2.result()[..., 0]
        core = 0.4 * np.exp(-(r / 0.3) ** 2) * (0.8 + 0.2 * math.cos(4 * math.pi * ph))
        L = ramp(np.clip(A + core, 0, 1.4), MRD) * np.clip(A + core, 0, 1.4)[..., None] + ramp(np.clip(B, 0, 1.4), MRD_CY) * np.clip(B, 0, 1.4)[..., None]
        frames.append(additive_from_light(ndi.gaussian_filter(L, (0.6, 0.6, 0))))
    return frames


JOBS = [
    dict(id="HLX-VFX-DATA_CORRUPTION-A", fn=data_corruption, n=256, C=4, R=4, fps=15, loop=True, blend="add", chapter="helix",
         purpose="Helix: data corruption loop on damaged servers / relays (tearing scan blocks, pixel shards, cyan with amber faults).",
         notes="Independent flicker frames; start on a random frame. Place on the component face (fixed quad, not billboard) at 60-90% of its size."),
    dict(id="HLX-VFX-ELECTRICAL_OVERLOAD-A", fn=electrical_overload, n=256, C=4, R=4, fps=20, loop=False, blend="add", chapter="helix",
         purpose="Helix: electrical overload of a server or relay: arcs build around a core for 0.45 s, then pop with sparks.",
         notes="0.8 s. Trigger on component destroyed for Helix electronics; layer SHR-VFX-SMOKE_PUFF-A after."),
    dict(id="VTA-VFX-CONTAINMENT_LEAK-A", fn=containment_leak, n=256, C=4, R=4, fps=16, loop=True, blend="mix", chapter="vita", pivot="left_center",
         purpose="VITA: containment leak loop: pale green pressurised vapour jet venting to +u from a nozzle at u = 0.1.",
         notes="Seamless loop. Rotate the quad to the vent direction; scale 1-2 m long. Reads on both dark and clean white VITA rooms (dark-to-pale shading)."),
    dict(id="NVG-VFX-ENERGY_OVERLOAD-A", fn=nova_overload, n=512, C=4, R=4, fps=20, loop=False, blend="add", chapter="nova_grid",
         purpose="Nova Grid: energy overload: unstable blue plasma ball with amber arcs swelling for 0.5 s, then bursting.",
         notes="0.8 s. For transformers, capacitor banks and the reactor ring. Frame width about 3 m for large components."),
    dict(id="CVT-VFX-SENSOR_DISRUPTION-A", fn=sensor_disruption, n=256, C=4, R=4, fps=16, loop=True, blend="add", chapter="civitas",
         purpose="Civitas: sensor disruption loop: jammed scanning sweep, interference rings, static and red fault pings.",
         notes="Loop on damaged sensor towers, cameras and screen walls (fixed quad on the device face)."),
    dict(id="MRD-VFX-TEMPORAL_DISTORTION-A", fn=temporal_distortion, n=512, C=4, R=4, fps=16, loop=True, blend="add", chapter="meridian",
         purpose="Meridian: temporal distortion loop: seamless violet ripple rings with cyan echoes around a dark eye (temporal anchors, convergence).",
         notes="Seamless loop. Billboard or fixed quad 2-4 m. Purple is Meridian only (chapter palette)."),
    dict(id="MRD-VFX-QUANTUM_INSTABILITY-A", fn=quantum_instability, n=256, C=4, R=4, fps=16, loop=True, blend="add", chapter="meridian",
         purpose="Meridian: quantum instability loop: points blink between displaced positions with faint links.",
         notes="Seamless loop. Overlay on unstable Meridian components or as an ambient accent near anchors."),
]


def build(only=None):
    run_jobs(JOBS, "chapter", only)


if __name__ == "__main__":
    build(sys.argv[1] if len(sys.argv) > 1 else None)
