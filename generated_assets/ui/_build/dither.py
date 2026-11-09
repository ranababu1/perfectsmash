"""Float gradient rendering with triangular dither, so large dark gradients ship without banding.
resvg renders 8-bit, which bands on slow dark gradients; PNG exports of gradient plates are therefore
rebuilt here and the vector layers are composited on top."""
import numpy as np
from PIL import Image

def hex2f(h):
    h = h.lstrip("#"); return np.array([int(h[i:i+2], 16) for i in (0, 2, 4)], dtype=np.float64)

def ramp(t, stops):
    t = np.clip(t, 0, 1); out = np.zeros(t.shape + (3,))
    for (o0, c0), (o1, c1) in zip(stops[:-1], stops[1:]):
        m = (t >= o0) & (t <= o1)
        k = ((t - o0) / max(o1 - o0, 1e-9))[..., None]
        out[m] = (hex2f(c0) * (1 - k) + hex2f(c1) * k)[m]
    out[t < stops[0][0]] = hex2f(stops[0][1]); out[t > stops[-1][0]] = hex2f(stops[-1][1])
    return out

def radial(w, h, cx, cy, rx, ry, stops):
    y, x = np.mgrid[0:h, 0:w] + 0.5
    d = np.sqrt(((x - cx * w) / (rx * w)) ** 2 + ((y - cy * h) / (ry * h)) ** 2)
    return ramp(d, stops)

def linear_v(w, h, stops):
    y = (np.mgrid[0:h, 0:w][0] + 0.5) / h
    return ramp(y, stops)

def to_image(rgb, seed=7):
    rng = np.random.default_rng(seed)
    n = rng.random(rgb.shape) - rng.random(rgb.shape)  # triangular, +-1 LSB
    a = np.clip(np.round(rgb + n), 0, 255).astype(np.uint8)
    return Image.fromarray(a, "RGB").convert("RGBA")
