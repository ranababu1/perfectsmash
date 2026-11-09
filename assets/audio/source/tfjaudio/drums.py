"""Synthesised percussion and cinematic one-shots (original sound design)."""
import numpy as np
from .dsp import SR, sine, lp, hp, bp, lp4, perc_env, softclip, rng, pan_stereo, sos_filter, saw, square
from .instruments import mtof


def _t(sec):
    return np.arange(int(sec * SR)) / SR


def tailfade(s, frac=0.3):
    """Smooth the end of a one-shot so it never truncates (no end click)."""
    n = s.shape[0]
    k = max(16, int(n * frac))
    w = np.cos(np.linspace(0, np.pi / 2, k)) ** 2
    s = s.copy()
    if s.ndim == 2:
        s[n - k:] *= w[:, None]
    else:
        s[n - k:] *= w
    return s


def kick(seed=0, f_hi=150, f_lo=46, sweep=0.045, decay=0.3, click=0.6, drive=1.6, length=None):
    r = rng(seed)
    t = _t(length or decay * 5.5)
    f = f_lo + (f_hi - f_lo) * np.exp(-t / sweep)
    ph = 2 * np.pi * np.cumsum(f) / SR
    body = np.sin(ph) * np.exp(-t / decay)
    cl = r.standard_normal(t.shape[0]) * np.exp(-t / 0.0025)
    cl = bp(cl, 3500, 0.2) * click
    s = softclip(body * drive + cl, 1.0)
    s[:48] *= np.linspace(0, 1, 48)
    return tailfade(s * 0.9)


def boom(seed=0, f0=42, decay=2.2, length=None, noise=0.35, drive=2.0):
    """Cinematic low hit: swept sine body plus filtered noise thump and distorted mids for phones."""
    r = rng(seed)
    t = _t(length or decay * 5)
    f = f0 + 90 * np.exp(-t / 0.07)
    body = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / decay)
    nz = r.standard_normal(t.shape[0])
    nz = lp(nz, 180 + 2500 * np.exp(-t / 0.05)) * np.exp(-t / 0.35) * noise
    s = body + nz
    mids = softclip(bp(s, 180, 0.2) * drive * 3, 1.0) * 0.18 * np.exp(-t / 0.6)
    out = softclip(s * 1.2, 1.0) + mids
    out[:48] *= np.linspace(0, 1, 48)
    return tailfade(out)


def taiko(seed=0, f0=95, decay=0.32, length=None):
    r = rng(seed)
    t = _t(length or decay * 6)
    f = f0 * (1 + 0.6 * np.exp(-t / 0.02))
    body = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / decay)
    body += 0.4 * np.sin(2 * np.pi * np.cumsum(f * 1.58) / SR) * np.exp(-t / (decay * 0.5))
    skin = bp(r.standard_normal(t.shape[0]), 700, 0.25) * np.exp(-t / 0.04) * 0.6
    return tailfade(softclip((body + skin) * 1.3, 1.0) * 0.8)


def snare(seed=0, tone=190, decay=0.09, noise_decay=0.2, length=None, bright=1.0):
    r = rng(seed)
    t = _t(length or max(decay, noise_decay) * 6)
    tonal = np.sin(2 * np.pi * np.cumsum(tone * (1 + 0.4 * np.exp(-t / 0.01))) / SR) * np.exp(-t / decay)
    nz = r.standard_normal(t.shape[0])
    nz = hp(bp(nz, 4200 * bright, 0.05), 900) * np.exp(-t / noise_decay)
    return tailfade(softclip(tonal * 0.6 + nz * 0.9, 1.2) * 0.7)


def hat(seed=0, decay=0.04, length=None, bright=1.0, metal=0.6):
    r = rng(seed)
    t = _t(length or decay * 7)
    s = np.zeros(t.shape[0])
    for f in [317, 421, 553, 709, 871, 1061]:
        s += square(np.full(t.shape[0], f * 7.3 * bright), 0.5, SR, r.uniform(0, 1))
    nz = r.standard_normal(t.shape[0])
    x = s * metal * 0.15 + nz * (1 - metal * 0.5)
    x = hp(bp(x, 9000 * bright, 0.1), 6500)
    return tailfade(x * np.exp(-t / decay) * 0.6)


def tick(seed=0, f=3200, decay=0.008, length=None, q=0.85):
    """Mechanical clock tick / precise digital tick (soft-onset noise strike into resonators)."""
    r = rng(seed)
    t = _t(length or max(0.03, decay * 8))
    exc = r.standard_normal(t.shape[0]) * np.exp(-t / 0.0006)
    s = bp(exc, f, q) + 0.5 * bp(exc, f * 2.31, q) + 0.3 * bp(exc, f * 0.37, 0.5)
    s *= np.exp(-t / decay)
    k = int(0.0004 * SR)
    s[:k] *= np.sin(np.linspace(0, np.pi / 2, k)) ** 2
    s = s / (np.abs(s).max() + 1e-9) * 0.8
    return tailfade(s)


def modal(freqs, decays, amps, length, seed=0, strike=0.004, strike_bright=6000):
    """Modal synthesis: bank of decaying sinusoids excited by a short strike."""
    r = rng(seed)
    t = _t(length)
    s = np.zeros(t.shape[0])
    for f, d, a in zip(freqs, decays, amps):
        if f > SR * 0.45:
            continue
        s += a * np.sin(2 * np.pi * f * t + r.uniform(0, 6.28)) * np.exp(-t / d)
    exc = r.standard_normal(t.shape[0]) * np.exp(-t / strike)
    exc = lp(exc, strike_bright)
    exc[: int(0.0003 * SR)] *= np.linspace(0, 1, int(0.0003 * SR))
    s = s * np.minimum(t / 0.0008, 1) + exc * 0.3
    return tailfade(s, 0.35)


def metal_hit(seed=0, f0=220, decay=1.2, length=None, inharm=None, bright=1.0):
    r = rng(seed)
    ratios = inharm or [1.0, 2.76, 5.40, 8.93, 13.34, 18.64, 1.51, 3.98]
    freqs = [f0 * k * r.uniform(0.985, 1.015) for k in ratios]
    decs = [decay / (1 + 0.35 * i) for i in range(len(ratios))]
    amps = [1 / (1 + 0.5 * i) * (bright if i > 2 else 1) for i in range(len(ratios))]
    return modal(freqs, decs, amps, length or decay * 5, seed) * 0.35


def anvil(seed=0, f0=520):
    return metal_hit(seed, f0, decay=0.6, length=3.0, inharm=[1, 1.47, 2.09, 2.56, 3.39, 4.17, 5.43], bright=1.2)


def riser(length=4.0, seed=0, f_lo=300, f_hi=9000, tonal_m=None, curve=2.0):
    r = rng(seed)
    t = _t(length)
    x = (t / length) ** curve
    fc = f_lo * (f_hi / f_lo) ** x
    nzL = bp(r.standard_normal(t.shape[0]), fc, 0.45)
    nzR = bp(r.standard_normal(t.shape[0]), fc * 1.05, 0.45)
    env = x ** 1.5
    st = np.stack([nzL, nzR], 1) * env[:, None] * 0.5
    if tonal_m is not None:
        f = mtof(tonal_m) * 2 ** (x * 1.0)
        ton = saw(f, SR, 0.0) * 0.3 + saw(f * 1.01, SR, 0.5) * 0.3
        ton = lp(ton, 400 + 6000 * x) * env * 0.5
        st += np.stack([ton, ton], 1)
    fin = int(0.005 * SR)
    st[-fin:] *= np.linspace(1, 0, fin)[:, None]
    return st


def downlifter(length=3.0, seed=0, f_hi=6000, f_lo=120):
    r = rng(seed)
    t = _t(length)
    x = t / length
    fc = f_hi * (f_lo / f_hi) ** (x ** 0.6)
    nz = np.stack([bp(r.standard_normal(t.shape[0]), fc, 0.4), bp(r.standard_normal(t.shape[0]), fc * 0.95, 0.4)], 1)
    env = np.exp(-x * 3.5) * np.minimum(t / 0.01, 1)
    return nz * env[:, None] * 0.5


def braam(m=26, length=4.5, seed=0, bright=1.0, drive=2.4):
    """Huge low brass-like cluster with distortion: cinematic hit."""
    r = rng(seed)
    t = _t(length)
    env = np.minimum(t / 0.06, 1) * np.exp(-t / (length * 0.38)) * np.cos(np.linspace(0, np.pi / 2, t.shape[0])) ** 0.5
    s = np.zeros(t.shape[0])
    for k, iv in enumerate([0, 12, 19, 24, 7, 0]):
        f = mtof(m + iv) * (1 + r.normal(0, 0.003))
        s += saw(np.full(t.shape[0], f), SR, r.uniform(0, 1)) * (0.8 if iv == 0 else 0.5)
    fc = 120 + 2600 * bright * np.exp(-t / 0.5) + 300 * env
    s = lp4(s, fc, 0.25)
    s = softclip(s * drive, 1.0)
    side = hp(r.standard_normal(t.shape[0]), 3000) * np.exp(-t / 0.2) * 0.05
    return np.stack([s * env * 0.5 + side, s * env * 0.5 - side], 1)


def sub_drop(length=2.5, f_hi=110, f_lo=28):
    t = _t(length)
    f = f_lo + (f_hi - f_lo) * np.exp(-t / (length * 0.3))
    s = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / (length * 0.45))
    s += 0.2 * np.sin(4 * np.pi * np.cumsum(f) / SR) * np.exp(-t / (length * 0.3))
    s[:48] *= np.linspace(0, 1, 48)
    return tailfade(s * 0.8)


def reverse_swell(m=50, length=2.0, seed=0):
    r = rng(seed)
    t = _t(length)
    x = t / length
    s = np.zeros(t.shape[0])
    for iv in [0, 7, 12, 15, 19]:
        f = mtof(m + iv)
        s += saw(np.full(t.shape[0], f * (1 + r.normal(0, 0.002))), SR, r.uniform(0, 1))
    s = lp(s, 200 + 5000 * x ** 2) * x ** 2.5 * 0.2
    fin = int(0.004 * SR)
    s[-fin:] *= np.linspace(1, 0, fin)
    return s
