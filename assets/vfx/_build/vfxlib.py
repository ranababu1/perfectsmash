"""Procedural VFX toolkit (numpy / scipy / Pillow).

Conventions
- A frame is a float32 RGBA array (H, W, 4), straight alpha, values 0..1 (rgb may exceed 1 before export; clipped).
- Additive effects: rgb is the emitted colour, alpha is intensity (Godot blend add: dst += rgb * a).
- Mixed effects: rgb is the shaded albedo, alpha is coverage.
- Every frame keeps a 2 px (we use 3 px) fully empty border and a soft fade window so nothing clips.
"""
import json, math, os
import numpy as np
from PIL import Image
from scipy import ndimage as ndi

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))  # assets (library root)
VFX = os.path.join(ROOT, "vfx")
PREV = os.path.join(VFX, "previews")
BG = (0x15 / 255, 0x19 / 255, 0x1E / 255)
LAST_PREWIN = 0.0
INDEX = []  # manifest entries collected by build scripts


def hexc(h):
    h = h.lstrip("#"); return np.array([int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)], np.float32)


# ---------------------------------------------------------------- noise
def lattice_noise(shape, cells, seed, wrap_t=None):
    """Smooth value noise of output shape (T,H,W) or (H,W). cells = lattice cells per axis.
    wrap_t: if True the time axis loops seamlessly."""
    rng = np.random.default_rng(seed)
    if len(shape) == 2:
        lat = rng.random((cells[0] + 3, cells[1] + 3)).astype(np.float32)
        yy, xx = np.meshgrid(np.linspace(1, cells[0] + 1, shape[0], dtype=np.float32),
                             np.linspace(1, cells[1] + 1, shape[1], dtype=np.float32), indexing="ij")
        return ndi.map_coordinates(lat, [yy, xx], order=3, mode="nearest")
    T, H, W = shape
    ct, cy, cx = cells
    if wrap_t:
        lat = rng.random((ct, cy + 3, cx + 3)).astype(np.float32)
        tt = np.arange(T, dtype=np.float32) * ct / T
    else:
        lat = rng.random((ct + 3, cy + 3, cx + 3)).astype(np.float32)
        tt = 1 + np.linspace(0, ct, T, dtype=np.float32)
    out = np.empty(shape, np.float32)
    yy, xx = np.meshgrid(np.linspace(1, cy + 1, H, dtype=np.float32), np.linspace(1, cx + 1, W, dtype=np.float32), indexing="ij")
    for i, t in enumerate(tt):
        if wrap_t:
            # cubic in space, cosine-smoothed linear in time with wrap
            t0 = int(math.floor(t)) % ct; t1 = (t0 + 1) % ct; f = t - math.floor(t); f = f * f * (3 - 2 * f)
            a = ndi.map_coordinates(lat[t0], [yy, xx], order=3, mode="nearest")
            b = ndi.map_coordinates(lat[t1], [yy, xx], order=3, mode="nearest")
            out[i] = a * (1 - f) + b * f
        else:
            out[i] = ndi.map_coordinates(lat, [np.full_like(yy, t), yy, xx], order=3, mode="nearest")
    return out


def fbm2(h, w, base=4, octaves=5, seed=0, gain=0.5):
    acc = np.zeros((h, w), np.float32); amp = 1.0; norm = 0
    for o in range(octaves):
        c = base * 2 ** o
        acc += amp * lattice_noise((h, w), (c, c), seed + 101 * o); norm += amp; amp *= gain
    return acc / norm


def fbm3(T, h, w, base=4, tcells=4, octaves=4, seed=0, gain=0.5, wrap_t=False):
    acc = np.zeros((T, h, w), np.float32); amp = 1.0; norm = 0
    for o in range(octaves):
        c = base * 2 ** o
        acc += amp * lattice_noise((T, h, w), (max(1, tcells * (o + 1)), c, c), seed + 101 * o, wrap_t); norm += amp; amp *= gain
    return acc / norm


# ---------------------------------------------------------------- geometry helpers
def grid(n):
    """Pixel-centre coordinates in -1..1 for an n x n frame. Returns (x, y, r, a)."""
    c = (np.arange(n, dtype=np.float32) + 0.5) / n * 2 - 1
    y, x = np.meshgrid(c, c, indexing="ij")
    return x, y, np.hypot(x, y), np.arctan2(y, x)


def smooth(e0, e1, v):
    t = np.clip((v - e0) / (e1 - e0), 0, 1); return t * t * (3 - 2 * t)


def ease_out(t, p=2.0):
    return 1 - (1 - np.clip(t, 0, 1)) ** p


def ramp(v, stops):
    """Colour ramp: stops = [(pos, '#hex'), ...]. v any shape -> (...,3)."""
    pos = np.array([s[0] for s in stops], np.float32); cols = np.stack([hexc(s[1]) for s in stops])
    v = np.clip(v, pos[0], pos[-1])
    out = np.empty(v.shape + (3,), np.float32)
    for k in range(3):
        out[..., k] = np.interp(v, pos, cols[:, k])
    return out


class Canvas:
    """Supersampled accumulation buffer for particles (intensity or RGBA premultiplied)."""

    def __init__(self, n, ss=2, channels=4):
        self.n = n; self.ss = ss; self.N = n * ss
        self.buf = np.zeros((self.N, self.N, channels), np.float32)

    def _px(self, u):  # -1..1 -> supersampled px
        return (np.asarray(u, np.float32) + 1) * 0.5 * self.N

    def splat(self, x, y, radius, color, alpha=1.0, hard=0.0):
        """Gaussian-ish dot. x,y in -1..1, radius in frame units (-1..1 space). color (3,), premultiplied accumulate."""
        cx, cy = self._px(x), self._px(y); rp = max(radius * 0.5 * self.N, 0.6)
        R = int(math.ceil(rp * 3)) + 1
        x0, x1 = int(max(cx - R, 0)), int(min(cx + R + 1, self.N)); y0, y1 = int(max(cy - R, 0)), int(min(cy + R + 1, self.N))
        if x0 >= x1 or y0 >= y1:
            return
        yy, xx = np.mgrid[y0:y1, x0:x1].astype(np.float32)
        d2 = ((xx + 0.5 - cx) ** 2 + (yy + 0.5 - cy) ** 2) / (rp * rp)
        if hard > 0:
            w = np.clip((1 + hard - np.sqrt(d2)) / max(hard, 1e-3), 0, 1) ** 1.5
        else:
            w = np.exp(-d2 * 1.6)
        w *= alpha
        self.buf[y0:y1, x0:x1, :3] += w[..., None] * np.asarray(color, np.float32)
        if self.buf.shape[2] == 4:
            self.buf[y0:y1, x0:x1, 3] += w

    def streak(self, x0, y0, x1, y1, w0, w1, color, a0=1.0, a1=0.0, steps=None):
        L = math.hypot(x1 - x0, y1 - y0) * 0.5 * self.N
        steps = steps or max(2, int(L / max(0.35 * min(w0, w1) * 0.5 * self.N, 0.6)))
        for i in range(steps + 1):
            t = i / steps
            self.splat(x0 + (x1 - x0) * t, y0 + (y1 - y0) * t, w0 + (w1 - w0) * t, color, (a0 + (a1 - a0) * t) / max(steps, 1) * 4)

    def polygon(self, pts, color, alpha=1.0):
        """Hard-edged polygon (anti-aliased by supersampling). pts in -1..1."""
        from PIL import ImageDraw
        m = Image.new("L", (self.N, self.N), 0)
        ImageDraw.Draw(m).polygon([(float(self._px(px)), float(self._px(py))) for px, py in pts], fill=255)
        a = np.asarray(m, np.float32) / 255 * alpha
        # over-composite premultiplied
        self.buf[..., :3] = self.buf[..., :3] * (1 - a[..., None]) + a[..., None] * np.asarray(color, np.float32)
        self.buf[..., 3] = self.buf[..., 3] * (1 - a) + a

    def result(self):
        b = self.buf
        if self.ss > 1:
            b = b.reshape(self.n, self.ss, self.n, self.ss, -1).mean(axis=(1, 3))
        return b


def unpremultiply(buf):
    a = np.clip(buf[..., 3], 0, 1)
    rgb = np.where(a[..., None] > 1e-5, buf[..., :3] / np.maximum(buf[..., 3:4], 1e-5), 0)
    return np.dstack([rgb, a])


def additive_from_light(light):
    """light (H,W,3) linear-ish emitted light -> straight RGBA where rgb*a == light (as far as clip allows)."""
    a = np.clip(light.max(axis=-1), 0, 1)
    rgb = np.where(a[..., None] > 1e-5, light / np.maximum(light.max(axis=-1, keepdims=True), 1e-5), 0)
    # keep hot cores white: luminance above 1 pushes rgb towards white
    over = np.clip(light.max(axis=-1) - 1, 0, 1)[..., None]
    rgb = rgb * (1 - over) + over
    return np.dstack([np.clip(rgb, 0, 1), a]).astype(np.float32)


def window(n, margin=3, feather=0.10):
    """Multiplicative fade so the outer border is empty; feather as fraction of frame."""
    x, y, r, _ = grid(n)
    edge = np.minimum(np.minimum(1 - np.abs(x), 1 - np.abs(y)), 1)  # 0 at frame edge (in -1..1 units)
    m_units = margin * 2 / n
    return smooth(m_units, m_units + feather * 2, edge)


# ---------------------------------------------------------------- export
def quantise(frame, rng):
    f = np.clip(frame, 0, 1)
    d = (rng.random(f.shape, dtype=np.float32) + rng.random(f.shape, dtype=np.float32) - 1) / 255
    q = np.clip(np.round((f + d) * 255), 0, 255).astype(np.uint8)
    q[..., :3][q[..., 3] == 0] = 0
    return q


def edge_report(frames, margin=2, ring=6):
    """max alpha (0..255) touching the outer `margin` px and within `ring` px of the frame edge."""
    worst_m = worst_r = 0
    for f in frames:
        a = f[..., 3]
        m = np.concatenate([a[:margin].ravel(), a[-margin:].ravel(), a[:, :margin].ravel(), a[:, -margin:].ravel()])
        r = np.concatenate([a[:ring].ravel(), a[-ring:].ravel(), a[:, :ring].ravel(), a[:, -ring:].ravel()])
        worst_m = max(worst_m, int(m.max())); worst_r = max(worst_r, int(r.max()))
    return worst_m, worst_r


def save_sheet(frames, path, columns, rows, apply_window=True, seed=7):
    n = frames[0].shape[0]
    rng = np.random.default_rng(seed)
    win = window(n)
    q = []
    global LAST_PREWIN
    LAST_PREWIN = 0.0
    ring = max(4, n // 32)
    for f in frames:
        a_ = f[..., 3]
        LAST_PREWIN = max(LAST_PREWIN, float(max(a_[:ring].max(), a_[-ring:].max(), a_[:, :ring].max(), a_[:, -ring:].max())))
        f = f.copy()
        if apply_window:
            f[..., 3] *= win
        qf = quantise(f, rng)
        qf[:3] = 0; qf[-3:] = 0; qf[:, :3] = 0; qf[:, -3:] = 0
        q.append(qf)
    sheet = np.zeros((rows * n, columns * n, 4), np.uint8)
    for i, f in enumerate(q):
        r, c = divmod(i, columns)
        sheet[r * n:(r + 1) * n, c * n:(c + 1) * n] = f
    os.makedirs(os.path.dirname(path), exist_ok=True)
    Image.fromarray(sheet, "RGBA").save(path, optimize=True)
    return q


def composite(frame_u8, blend, bg=None):
    f = frame_u8.astype(np.float32) / 255
    if bg is None:
        bg = np.broadcast_to(np.array(BG, np.float32), f.shape[:2] + (3,))
    a = f[..., 3:4]
    if blend == "add":
        out = bg + f[..., :3] * a
    else:
        out = bg * (1 - a) + f[..., :3] * a
    return np.clip(out, 0, 1)


def save_preview(frames_u8, blend, path, fps, size=256, bg=None, loops=0):
    ims = []
    for f in frames_u8:
        c = composite(f, blend, bg)
        im = Image.fromarray((c * 255 + 0.5).astype(np.uint8), "RGB")
        if im.size[0] != size:
            im = im.resize((size, size), Image.LANCZOS)
        ims.append(im)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    ims[0].save(path, save_all=True, append_images=ims[1:], duration=int(1000 / fps), loop=loops, quality=88, method=4)
    return path


def register(eid, path, chapter, blend, purpose, frames, columns, rows, fps, loop, frame_px, pivot="center",
             used_by=None, notes="", render_type="sprite", extra=None):
    rel = os.path.relpath(path, os.path.dirname(ROOT)).replace(os.sep, "/")  # assets/...
    w, h = Image.open(path).size
    e = {
        "id": eid, "path": rel, "category": "vfx", "render_type": render_type, "format": "png",
        "dimensions": [w, h], "purpose": purpose,
        "source": "procedural, assets/vfx/_build (Python numpy/scipy/Pillow), authored by the ui-vfx asset stream",
        "rights_status": "original procedural work generated by code written with AI assistance; ownership of AI-assisted output not legally settled; not commercially cleared",
        "approval_status": "pending_review", "used_by": used_by or ["MissionView VFX (proposed)"], "chapter": chapter,
        "blend": blend, "pivot": pivot, "requires_alpha": True,
    }
    if render_type == "sprite":
        e["animation"] = {"frames": frames, "columns": columns, "rows": rows, "fps": fps, "loop": loop}
        e["loop"] = loop
        e["notes"] = (f"Frame {frame_px}x{frame_px} px, {frames} frames ({columns}x{rows}), {fps} fps, "
                      f"{'looping' if loop else 'one-shot'} ({frames / fps:.2f} s). Straight alpha, 3 px empty frame border. " + notes).strip()
    else:
        e["notes"] = notes
    if extra:
        e.update(extra)
    INDEX.append(e)
    return e


def write_index(name):
    os.makedirs(os.path.join(VFX, "_build", "index_parts"), exist_ok=True)
    with open(os.path.join(VFX, "_build", "index_parts", name + ".json"), "w") as fh:
        json.dump(INDEX, fh, indent=1)


# ---------------------------------------------------------------- shared effect helpers
def light_to_frame(I, stops, cap=1.6, blur=0.0):
    I = np.clip(I, 0, cap)
    light = ramp(I, stops) * I[..., None]
    if blur:
        light = ndi.gaussian_filter(light, (blur, blur, 0))
    return additive_from_light(light)


def spark_system(n, F, count, seed, origin=(0.0, 0.0), dir_angle=-math.pi / 2, spread=math.pi, speed=(0.5, 1.4),
                 gravity=0.9, life=(0.4, 1.0), width=(0.006, 0.012), drag=1.6, color_hot="#ffffff", color_cool="#ffd59a",
                 trail=0.06, intensity=1.6, start=(0.0, 0.15), ss=2):
    """Ballistic spark streaks. Times are normalised to the clip (0..1). Returns list of (n,n,3) light arrays."""
    rng = np.random.default_rng(seed)
    P = []
    for _ in range(count):
        ang = dir_angle + rng.uniform(-spread / 2, spread / 2) * (rng.random() ** 0.6 if spread < 2 * math.pi else 1)
        v = rng.uniform(*speed)
        P.append(dict(a=ang, v=v, t0=rng.uniform(*start), life=rng.uniform(*life), w=rng.uniform(*width),
                      ox=origin[0] + rng.normal(0, 0.01), oy=origin[1] + rng.normal(0, 0.01)))
    hot, cool = hexc(color_hot), hexc(color_cool)

    def pos(p, tt):
        # exponential drag on velocity, constant gravity (+y is down on screen)
        k = drag
        s = (1 - math.exp(-k * tt)) / k
        return (p["ox"] + math.cos(p["a"]) * p["v"] * s,
                p["oy"] + math.sin(p["a"]) * p["v"] * s + 0.5 * gravity * tt * tt)
    out = []
    for i in range(F):
        t = (i + 0.5) / F
        cv = Canvas(n, ss=ss, channels=3)
        for p in P:
            age = t - p["t0"]
            if age <= 0 or age > p["life"]:
                continue
            u = age / p["life"]
            x1, y1 = pos(p, age); x0, y0 = pos(p, max(0.0, age - trail))
            col = hot * (1 - u) + cool * u
            br = intensity * (1 - u) ** 0.9
            cv.streak(x0, y0, x1, y1, p["w"] * 0.5, p["w"] * (1.2 - 0.5 * u), col * br, 0.15, 1.0)
        out.append(cv.result())
    return out


def lightning(rng, x0, y0, x1, y1, depth=6, rough=0.35, branch_p=0.25, branches=None, level=0):
    """Midpoint displacement polyline. Returns list of polylines [(pts, level)]."""
    pts = [(x0, y0), (x1, y1)]
    disp = rough * math.hypot(x1 - x0, y1 - y0)
    for _ in range(depth):
        new = [pts[0]]
        for (ax, ay), (bx, by) in zip(pts[:-1], pts[1:]):
            mx, my = (ax + bx) / 2, (ay + by) / 2
            nx, ny = -(by - ay), (bx - ax); L = math.hypot(nx, ny) or 1
            o = rng.normal(0, disp)
            new += [(mx + nx / L * o, my + ny / L * o), (bx, by)]
        pts = new; disp *= 0.55
    res = [(pts, level)]
    if level < 2:
        for j in range(2, len(pts) - 2, 3):
            if rng.random() < branch_p / (level + 1):
                ax, ay = pts[j]
                bx, by = pts[min(len(pts) - 1, j + 1)]
                ang = math.atan2(by - ay, bx - ax) + rng.choice([-1, 1]) * rng.uniform(0.4, 1.0)
                L = math.hypot(x1 - x0, y1 - y0) * rng.uniform(0.15, 0.4)
                res += lightning(rng, ax, ay, ax + math.cos(ang) * L, ay + math.sin(ang) * L, max(3, depth - 2), rough, branch_p, level=level + 1)
    return res


def draw_polylines(n, lines, core_w=0.006, ss=2):
    """Thin bright core lines; returns (n,n) intensity. Glow added by the caller with gaussian blur."""
    from PIL import ImageDraw
    N = n * ss
    m = Image.new("F", (N, N), 0.0)
    d = ImageDraw.Draw(m)
    for pts, level in lines:
        w = max(1, int(round(core_w * N * 0.5 * (0.6 ** level))))
        val = 1.0 * (0.75 ** level)
        d.line([((px + 1) * 0.5 * N, (py + 1) * 0.5 * N) for px, py in pts], fill=val, width=w, joint="curve")
    a = np.asarray(m, np.float32)
    return a.reshape(n, ss, n, ss).mean(axis=(1, 3))


CHAPTER_DIR = {"shared": "shared", "helix": "helix", "vita": "vita", "nova_grid": "nova_grid", "civitas": "civitas", "meridian": "meridian"}


def save_texture(frame, path, margin=2):
    rng = np.random.default_rng(3)
    q = quantise(frame, rng); q[:margin] = 0; q[-margin:] = 0; q[:, :margin] = 0; q[:, -margin:] = 0
    os.makedirs(os.path.dirname(path), exist_ok=True)
    Image.fromarray(q, "RGBA").save(path, optimize=True)
    return q


def run_jobs(jobs, index_name, only=None):
    """jobs: dicts with id, fn, n, C, R, fps, loop, blend, purpose, [notes, chapter, pivot, used_by, kwargs]."""
    for j in jobs:
        if only and only not in j["id"]:
            continue
        ch = j.get("chapter", "shared")
        frames = j["fn"](n=j["n"], **j.get("kwargs", {}))
        name = j["id"].lower().replace("-", "_")
        path = os.path.join(VFX, CHAPTER_DIR[ch], name + ".png")
        q = save_sheet(frames, path, j["C"], j["R"])
        em, er = edge_report(q)
        print(j["id"], len(frames), "frames; edge max alpha 2px/6px:", em, er, "| pre-window outer-ring alpha: %.3f" % LAST_PREWIN, flush=True)
        save_preview(q, j["blend"], os.path.join(PREV, "anim", name + ".webp"), j["fps"], size=256)
        register(j["id"], path, ch, j["blend"], j["purpose"], len(frames), j["C"], j["R"], j["fps"], j["loop"], j["n"],
                 pivot=j.get("pivot", "center"), notes=j.get("notes", ""), used_by=j.get("used_by"))
    write_index(index_name + (("_" + only) if only else ""))


def fbm2_tile_y(h, w, base=4, octaves=5, seed=0, gain=0.5):
    """fbm that tiles vertically with period h (scroll by h loops seamlessly)."""
    acc = np.zeros((h, w), np.float32); amp = 1.0; norm = 0
    for o in range(octaves):
        c = base * 2 ** o
        rng = np.random.default_rng(seed + 101 * o)
        lat = rng.random((c, c * max(1, w // h) + 3)).astype(np.float32)
        yy, xx = np.meshgrid(np.arange(h, dtype=np.float32) * c / h, np.linspace(1, c * max(1, w // h) + 1, w, dtype=np.float32), indexing="ij")
        # wrap in y: pad lattice by repeating rows
        latp = np.concatenate([lat[-2:], lat, lat[:3]], axis=0)
        acc += amp * ndi.map_coordinates(latp, [yy + 2, xx], order=3, mode="nearest"); norm += amp; amp *= gain
    return acc / norm


def scroll_loop(F, n, period_mult=2, base=4, octaves=5, seed=0, xscale=1.0):
    """Seamless upward-scrolling noise frames (F, n, n): tileable strip of height period_mult*n scrolled once per loop."""
    P = n * period_mult
    big = fbm2_tile_y(P, n, base=base * period_mult, octaves=octaves, seed=seed)
    out = []
    for i in range(F):
        off = int(round(P * i / F))
        idx = (np.arange(n) + off) % P
        out.append(big[idx])
    return np.stack(out)
