"""Core DSP kernels for the Temporal: First Jump audio pipeline.

Everything here is original code. No third-party samples are used anywhere in the
pipeline: every sound is synthesised from oscillators, noise and filters.
"""
import numpy as np
from numba import njit
from scipy.signal import resample_poly, oaconvolve, butter, sosfilt, sosfiltfilt

SR = 48000


def rng(seed):
    return np.random.default_rng(seed)


# ---------------------------------------------------------------- oscillators
@njit(cache=True)
def _polyblep(t, dt):
    if t < dt:
        x = t / dt
        return x + x - x * x - 1.0
    elif t > 1.0 - dt:
        x = (t - 1.0) / dt
        return x * x + x + x + 1.0
    return 0.0


@njit(cache=True)
def saw(freq, sr, phase0):
    n = freq.shape[0]
    out = np.empty(n)
    ph = phase0
    for i in range(n):
        dt = freq[i] / sr
        out[i] = 2.0 * ph - 1.0 - _polyblep(ph, dt)
        ph += dt
        if ph >= 1.0:
            ph -= 1.0
    return out


@njit(cache=True)
def square(freq, pw, sr, phase0):
    n = freq.shape[0]
    out = np.empty(n)
    ph = phase0
    for i in range(n):
        dt = freq[i] / sr
        v = 1.0 if ph < pw else -1.0
        v += _polyblep(ph, dt)
        p2 = ph + 1.0 - pw
        if p2 >= 1.0:
            p2 -= 1.0
        v -= _polyblep(p2, dt)
        out[i] = v
        ph += dt
        if ph >= 1.0:
            ph -= 1.0
    return out


def phase_of(freq, sr=SR, phase0=0.0):
    return phase0 + np.cumsum(freq) / sr


def sine(freq, sr=SR, phase0=0.0):
    return np.sin(2 * np.pi * phase_of(freq, sr, phase0))


def tri(freq, sr=SR, phase0=0.0):
    p = phase_of(freq, sr, phase0) % 1.0
    return 4 * np.abs(p - 0.5) - 1.0


# ---------------------------------------------------------------- filters
@njit(cache=True)
def svf(x, cutoff, res, mode, sr):
    """Zero-delay-feedback state variable filter (Simper). Time-varying cutoff.
    mode 0 lp, 1 bp, 2 hp, 3 notch. res in [0,1)."""
    n = x.shape[0]
    out = np.empty(n)
    ic1 = 0.0
    ic2 = 0.0
    k = 2.0 - 2.0 * res
    for i in range(n):
        fc = cutoff[i]
        if fc > sr * 0.45:
            fc = sr * 0.45
        if fc < 10.0:
            fc = 10.0
        g = np.tan(np.pi * fc / sr)
        a1 = 1.0 / (1.0 + g * (g + k))
        a2 = g * a1
        a3 = g * a2
        v3 = x[i] - ic2
        v1 = a1 * ic1 + a2 * v3
        v2 = ic2 + a2 * ic1 + a3 * v3
        ic1 = 2.0 * v1 - ic1
        ic2 = 2.0 * v2 - ic2
        if mode == 0:
            out[i] = v2
        elif mode == 1:
            out[i] = v1
        elif mode == 2:
            out[i] = x[i] - k * v1 - v2
        else:
            out[i] = x[i] - k * v1
    return out


def lp(x, fc, res=0.0, sr=SR):
    fc = np.broadcast_to(np.asarray(fc, dtype=np.float64), x.shape).copy()
    return svf(np.ascontiguousarray(x, dtype=np.float64), fc, res, 0, sr)


def hp(x, fc, res=0.0, sr=SR):
    fc = np.broadcast_to(np.asarray(fc, dtype=np.float64), x.shape).copy()
    return svf(np.ascontiguousarray(x, dtype=np.float64), fc, res, 2, sr)


def bp(x, fc, res=0.5, sr=SR):
    fc = np.broadcast_to(np.asarray(fc, dtype=np.float64), x.shape).copy()
    return svf(np.ascontiguousarray(x, dtype=np.float64), fc, res, 1, sr)


def lp4(x, fc, res=0.0, sr=SR):
    return lp(lp(x, fc, res * 0.5, sr), fc, res, sr)


def sos_filter(x, kind, fc, order=2, sr=SR, zero_phase=False):
    sos = butter(order, fc, btype=kind, fs=sr, output='sos')
    if x.ndim == 2:
        return np.stack([sos_filter(x[:, c], kind, fc, order, sr, zero_phase) for c in range(x.shape[1])], 1)
    return sosfiltfilt(sos, x) if zero_phase else sosfilt(sos, x)


# ---------------------------------------------------------------- envelopes
def adsr(n, a, d, s, r, gate, sr=SR, curve=3.0):
    """n samples total. gate = seconds the key is held. Exponential-ish segments."""
    t = np.arange(n) / sr
    env = np.zeros(n)
    a = max(a, 1e-4)
    d = max(d, 1e-4)
    r = max(r, 1e-4)
    att = t < a
    env[att] = (t[att] / a) ** 1.0
    dec = (t >= a) & (t < gate)
    td = t[dec] - a
    env[dec] = s + (1 - s) * np.exp(-curve * td / d)
    # level at release start
    if gate <= a:
        lvl = gate / a
    else:
        lvl = s + (1 - s) * np.exp(-curve * (gate - a) / d)
    rel = t >= gate
    env[rel] = lvl * np.exp(-curve * 2.0 * (t[rel] - gate) / r)
    return env


def perc_env(n, attack, decay, sr=SR, curve=1.0):
    t = np.arange(n) / sr
    a = max(attack, 1e-4)
    env = np.where(t < a, t / a, np.exp(-(t - a) / max(decay, 1e-4)) ** curve)
    return env


def fade(x, fin=0.0, fout=0.0, sr=SR):
    y = x.copy()
    n = y.shape[0]
    if fin > 0:
        k = min(n, int(fin * sr))
        w = np.sin(np.linspace(0, np.pi / 2, k)) ** 2
        y[:k] *= w[:, None] if y.ndim == 2 else w
    if fout > 0:
        k = min(n, int(fout * sr))
        w = np.cos(np.linspace(0, np.pi / 2, k)) ** 2
        y[n - k:] *= w[:, None] if y.ndim == 2 else w
    return y


# ---------------------------------------------------------------- utilities
def db(x):
    return 20 * np.log10(np.maximum(np.abs(x), 1e-12))


def undb(d):
    return 10 ** (d / 20.0)


def pan_stereo(mono, pan):
    """pan -1..1 constant power"""
    p = (np.clip(pan, -1, 1) + 1) * np.pi / 4
    return np.stack([mono * np.cos(p), mono * np.sin(p)], 1)


def widen(st, amount):
    m = (st[:, 0] + st[:, 1]) * 0.5
    s = (st[:, 0] - st[:, 1]) * 0.5 * amount
    return np.stack([m + s, m - s], 1)


def softclip(x, drive=1.0):
    return np.tanh(x * drive) / np.tanh(drive)


@njit(cache=True)
def sample_hold(x, step):
    n = x.shape[0]
    out = np.empty(n)
    v = 0.0
    for i in range(n):
        if i % step == 0:
            v = x[i]
        out[i] = v
    return out


def bitcrush(x, bits, step):
    q = 2 ** (bits - 1)
    y = sample_hold(np.ascontiguousarray(x, dtype=np.float64), int(step))
    return np.round(y * q) / q


@njit(cache=True)
def comb_delay(x, dsamp, fb, damp):
    n = x.shape[0]
    buf = np.zeros(dsamp + 1)
    out = np.empty(n)
    idx = 0
    lpst = 0.0
    for i in range(n):
        d = buf[idx]
        lpst = d * (1 - damp) + lpst * damp
        out[i] = d
        buf[idx] = x[i] + lpst * fb
        idx += 1
        if idx >= dsamp:
            idx = 0
    return out


@njit(cache=True)
def pingpong(xl, xr, dsamp, fb, damp):
    n = xl.shape[0]
    bl = np.zeros(dsamp)
    br = np.zeros(dsamp)
    ol = np.empty(n)
    orr = np.empty(n)
    idx = 0
    sl = 0.0
    sr_ = 0.0
    for i in range(n):
        dl = bl[idx]
        dr = br[idx]
        sl = dl * (1 - damp) + sl * damp
        sr_ = dr * (1 - damp) + sr_ * damp
        ol[i] = dl
        orr[i] = dr
        bl[idx] = 0.5 * (xl[i] + xr[i]) + sr_ * fb
        br[idx] = sl * fb
        idx += 1
        if idx >= dsamp:
            idx = 0
    return ol, orr


def delay_pp(st, seconds, fb=0.4, damp=0.3, sr=SR):
    d = max(1, int(seconds * sr))
    l, r = pingpong(np.ascontiguousarray(st[:, 0], dtype=np.float64), np.ascontiguousarray(st[:, 1], dtype=np.float64), d, fb, damp)
    return np.stack([l, r], 1)


@njit(cache=True)
def chorus_mono(x, sr, rate, depth_ms, base_ms, phase):
    n = x.shape[0]
    maxd = int((base_ms + depth_ms) * sr / 1000.0) + 4
    buf = np.zeros(maxd)
    out = np.empty(n)
    w = 0
    for i in range(n):
        buf[w] = x[i]
        d = (base_ms + depth_ms * 0.5 * (1 + np.sin(2 * np.pi * rate * i / sr + phase))) * sr / 1000.0
        rpos = w - d
        while rpos < 0:
            rpos += maxd
        i0 = int(rpos)
        fr = rpos - i0
        i1 = i0 + 1
        if i1 >= maxd:
            i1 = 0
        out[i] = buf[i0] * (1 - fr) + buf[i1] * fr
        w += 1
        if w >= maxd:
            w = 0
    return out


def ensemble(mono, voices=3, rate=0.35, depth=6.0, base=9.0, mix=0.6):
    """String-machine style ensemble: stereo from mono."""
    L = np.zeros_like(mono)
    R = np.zeros_like(mono)
    for v in range(voices):
        ph = 2 * np.pi * v / voices
        c = chorus_mono(mono, SR, rate * (1 + 0.37 * v), depth, base, ph)
        p = -0.8 + 1.6 * v / max(1, voices - 1)
        L += c * np.cos((p + 1) * np.pi / 4)
        R += c * np.sin((p + 1) * np.pi / 4)
    L /= voices * 0.7
    R /= voices * 0.7
    return np.stack([mono * (1 - mix) + L * mix, mono * (1 - mix) + R * mix], 1)


# ---------------------------------------------------------------- reverb
def make_ir(seconds=4.0, predelay=0.02, damp_hi=0.35, width=1.0, early=True, seed=7, bright=1.0, sr=SR):
    """Synthetic stereo hall IR: early reflections + band-split exponential late tail."""
    r = rng(seed)
    n = int((seconds * 1.3 + predelay) * sr)
    ir = np.zeros((n, 2))
    pd = int(predelay * sr)
    bands = [(20, 250, 1.15), (250, 1200, 1.0), (1200, 4500, 0.75 * (1 - damp_hi) + 0.25), (4500, 20000, 0.45 * (1 - damp_hi) + 0.12)]
    t = np.arange(n - pd) / sr
    for ch in range(2):
        late = np.zeros(n - pd)
        for lo, hi, k in bands:
            nz = r.standard_normal(n - pd)
            hi_ = min(hi, sr * 0.45)
            nz = sos_filter(nz, 'bandpass', [lo, hi_], 2)
            rt = seconds * k
            late += nz * np.exp(-6.9 * t / rt) * (bright if lo >= 4500 else 1.0)
        # smooth onset of late field
        onset = 1 - np.exp(-t / 0.025)
        ir[pd:, ch] = late * onset
    if early:
        for _ in range(18):
            tt = predelay + r.uniform(0.004, 0.085)
            g = r.uniform(0.15, 0.55) * np.exp(-tt * 12)
            idx = int(tt * sr)
            ch = r.integers(0, 2)
            ir[idx, ch] += g * r.choice([-1, 1])
            ir[idx + int(r.uniform(1, 7) * sr / 1000), 1 - ch] += g * 0.6
    ir = widen(ir, width)
    ir /= np.sqrt(np.sum(ir ** 2) / 2)
    return ir


_IR_CACHE = {}


def reverb(st, kind='hall'):
    presets = {
        'hall': dict(seconds=4.2, predelay=0.03, damp_hi=0.4, seed=11),
        'bighall': dict(seconds=6.5, predelay=0.045, damp_hi=0.45, seed=12),
        'chamber': dict(seconds=1.8, predelay=0.012, damp_hi=0.3, seed=13),
        'plate': dict(seconds=2.6, predelay=0.005, damp_hi=0.15, seed=14, early=False, bright=1.4),
        'room': dict(seconds=0.7, predelay=0.004, damp_hi=0.4, seed=15),
        'metal': dict(seconds=2.2, predelay=0.008, damp_hi=0.05, seed=16, bright=1.6),
    }
    if kind not in _IR_CACHE:
        _IR_CACHE[kind] = make_ir(**presets[kind]).astype(np.float32)
    ir = _IR_CACHE[kind]
    st = st.astype(np.float32)
    outL = oaconvolve(st[:, 0], ir[:, 0])[: st.shape[0]] + oaconvolve(st[:, 1], ir[:, 1] * 0.25)[: st.shape[0]]
    outR = oaconvolve(st[:, 1], ir[:, 1])[: st.shape[0]] + oaconvolve(st[:, 0], ir[:, 0] * 0.25)[: st.shape[0]]
    return np.stack([outL, outR], 1).astype(np.float64)


# ---------------------------------------------------------------- dynamics
@njit(cache=True)
def _limiter_gain(peak, ceiling, look, rel_coef):
    n = peak.shape[0]
    g = np.empty(n)
    for i in range(n):
        p = peak[i]
        g[i] = ceiling / p if p > ceiling else 1.0
    # backward sliding min over window look+1 (simple, O(n*look) but look small)
    gm = np.empty(n)
    for i in range(n):
        m = 1.0
        j0 = i - look
        if j0 < 0:
            j0 = 0
        for j in range(j0, i + 1):
            if g[j] < m:
                m = g[j]
        gm[i] = m
    # release smoothing (instant attack)
    y = np.empty(n)
    prev = 1.0
    for i in range(n):
        v = gm[i]
        if v < prev:
            prev = v
        else:
            prev = prev + (v - prev) * rel_coef
        y[i] = prev
    # box average over look samples
    out = np.empty(n)
    acc = 0.0
    for i in range(n):
        acc += y[i]
        if i >= look:
            acc -= y[i - look]
            out[i] = acc / look
        else:
            out[i] = acc / (i + 1) if i + 1 < look else acc / look
            # conservative at start
            if y[i] < out[i]:
                out[i] = y[i]
    return out


def true_peak_envelope(x, os=4):
    """Per-sample true-peak estimate (max over channels of 4x oversampled abs)."""
    if x.ndim == 1:
        x = x[:, None]
    n = x.shape[0]
    pk = np.zeros(n)
    chunk = SR * 8
    pad = 64
    for s in range(0, n, chunk):
        a = max(0, s - pad)
        b = min(n, s + chunk + pad)
        for c in range(x.shape[1]):
            u = resample_poly(x[a:b, c].astype(np.float64), os, 1)
            u = np.abs(u).reshape(-1, os).max(1)
            seg = u[s - a: s - a + min(chunk, n - s)]
            pk[s: s + seg.shape[0]] = np.maximum(pk[s: s + seg.shape[0]], seg)
    return pk


def true_peak_db(x):
    return float(db(true_peak_envelope(x).max()))


def tp_limit(x, ceiling_db=-1.4, lookahead_ms=1.5, release_ms=90.0):
    """Lookahead true-peak limiter. Returns same length (latency compensated)."""
    st = x if x.ndim == 2 else x[:, None]
    look = max(2, int(lookahead_ms * SR / 1000))
    pk = true_peak_envelope(st)
    rel = 1 - np.exp(-1.0 / (release_ms * SR / 1000))
    g = _limiter_gain(pk, undb(ceiling_db), look, rel)
    # gain computed for original indices; it was built causally (window behind) so shift it
    # back by `look` so the dip arrives before the peak.
    g2 = np.concatenate([g[look:], np.ones(look)])
    g2 = np.minimum(g2, 1.0)
    y = st * g2[:, None]
    return y if x.ndim == 2 else y[:, 0]


def duck_curve(n, hits, depth_db=-6.0, attack=0.004, release=0.18, sr=SR):
    """Sidechain-style gain curve from hit times (seconds)."""
    g = np.zeros(n)
    t = np.arange(int(release * 5 * sr)) / sr
    shape = np.where(t < attack, t / attack, np.exp(-(t - attack) / release))
    for h in hits:
        i = int(h * sr)
        if i >= n or i < -shape.shape[0]:
            continue
        a = max(i, 0)
        b = min(n, i + shape.shape[0])
        g[a:b] = np.maximum(g[a:b], shape[a - i: b - i])
    return undb(depth_db * g)
