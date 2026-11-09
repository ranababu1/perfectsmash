"""Synthesised instruments (original sound design, no samples).

Each melodic instrument takes a list of notes (start_s, dur_s, midi, vel) and the total
buffer length in samples, and returns a stereo float64 buffer.
"""
import numpy as np
from .dsp import (SR, saw, square, sine, tri, svf, lp, hp, bp, lp4, adsr, perc_env, pan_stereo,
                  ensemble, softclip, rng, sos_filter, widen)


def mtof(m):
    return 440.0 * 2 ** ((np.asarray(m, dtype=np.float64) - 69) / 12.0)


def _place(buf, sig, start):
    i = int(round(start * SR))
    if i >= buf.shape[0]:
        return
    a = max(i, 0)
    b = min(buf.shape[0], i + sig.shape[0])
    if b <= a:
        return
    buf[a:b] += sig[a - i: b - i]


def _vib(n, rate, depth_cents, delay, r):
    t = np.arange(n) / SR
    ramp = np.clip((t - delay) / 0.6, 0, 1)
    ph = r.uniform(0, 6.28)
    drift = np.cumsum(r.standard_normal(n)) * 0
    return 2 ** ((depth_cents * ramp * np.sin(2 * np.pi * rate * t + ph)) / 1200.0)


# ------------------------------------------------------------------ pads/strings
def supersaw_pad(notes, n, seed=1, voices=7, detune=0.18, attack=1.2, release=2.5, cutoff=2200.0,
                 cutoff_env=0.0, res=0.1, lfo_rate=0.07, lfo_depth=0.35, sub=0.0, bright_vel=0.6, width=1.0):
    r = rng(seed)
    out = np.zeros((n, 2))
    for (st, du, m, v) in notes:
        L = int((du + release + 0.05) * SR)
        f0 = mtof(m)
        env = adsr(L, attack, 1.5, 0.85, release, du)
        sigL = np.zeros(L)
        sigR = np.zeros(L)
        for k in range(voices):
            off = (k - (voices - 1) / 2) / max(1, (voices - 1) / 2)
            cents = off * detune * 100 * 0.5 + r.normal(0, 2)
            f = np.full(L, f0 * 2 ** (cents / 1200))
            s = saw(f, SR, r.uniform(0, 1))
            p = (off * 0.9 * width + 1) * np.pi / 4
            sigL += s * np.cos(p)
            sigR += s * np.sin(p)
        if sub > 0:
            s = sine(np.full(L, f0 / 2)) * sub * voices * 0.3
            sigL += s
            sigR += s
        t = np.arange(L) / SR
        lfo = 1 + lfo_depth * np.sin(2 * np.pi * lfo_rate * (t + st) + seed)
        fc = cutoff * (0.4 + bright_vel * v) * lfo * (1 + cutoff_env * np.exp(-t / 0.8))
        fc = np.minimum(fc, 16000)
        sigL = lp(sigL, fc, res)
        sigR = lp(sigR, fc, res)
        g = v / voices * 0.9
        sig = np.stack([sigL * env * g, sigR * env * g], 1)
        _place(out, sig, st)
    return out


def strings(notes, n, seed=2, attack=0.45, release=1.4, bright=1.0, section=3, vibrato=5.0, legato_swell=True):
    """Hybrid string section: detuned saw voices, delayed vibrato, body formants, ensemble."""
    r = rng(seed)
    mono = np.zeros(n)
    for (st, du, m, v) in notes:
        L = int((du + release + 0.05) * SR)
        f0 = mtof(m)
        env = adsr(L, attack * (1.3 - 0.6 * v), 0.8, 0.9, release, du)
        if legato_swell:
            t = np.arange(L) / SR
            env *= 0.85 + 0.15 * np.sin(np.pi * np.clip(t / max(du, 0.1), 0, 1))
        sig = np.zeros(L)
        for k in range(section):
            vib = _vib(L, 5.2 + r.uniform(-0.4, 0.4), vibrato, 0.25, r)
            cents = r.normal(0, 6)
            f = f0 * 2 ** (cents / 1200) * vib
            sig += saw(f, SR, r.uniform(0, 1)) + 0.25 * square(f, 0.5, SR, r.uniform(0, 1))
        sig /= section
        fc = np.minimum((900 + 3800 * v * bright) * (1 + 0.6 * env), 14000) + f0 * 2
        sig = lp(sig, fc, 0.05)
        # body resonances
        body = bp(sig, 450, 0.45) * 0.5 + bp(sig, 1300, 0.5) * 0.35 + bp(sig, 2900, 0.55) * 0.2
        sig = hp(sig * 0.55 + body, 70 if m > 50 else 35)
        _place(mono, sig * env * v * 0.6, st)
    return ensemble(mono, voices=3, rate=0.27, depth=5.0, base=11.0, mix=0.7)


def brass(notes, n, seed=3, attack=0.09, release=0.6, bright=1.0, growl=1.6):
    r = rng(seed)
    out = np.zeros(n)
    for (st, du, m, v) in notes:
        L = int((du + release + 0.05) * SR)
        f0 = mtof(m)
        t = np.arange(L) / SR
        scoop = 2 ** ((-35 * np.exp(-t / 0.05)) / 1200)
        vib = _vib(L, 4.6, 7, 0.5, r)
        f = f0 * scoop * vib
        s = saw(f, SR, 0.0) * 0.6 + saw(f * 1.003, SR, 0.3) * 0.6 + square(f * 0.5, 0.42, SR, 0.0) * 0.25
        env = adsr(L, attack, 0.5, 0.8, release, du)
        fenv = adsr(L, attack * 1.4, 0.7, 0.55, release, du)
        fc = f0 * (1.5 + 7 * v * bright * fenv) + 200
        s = lp4(s, np.minimum(fc, 12000), 0.15)
        s = softclip(s * growl * (0.5 + v), 1.2)
        s = hp(s, 60)
        out_sig = s * env * v * 0.5
        _place(out, out_sig, st)
    return ensemble(out, voices=2, rate=0.2, depth=2.0, base=7.0, mix=0.35)


# ------------------------------------------------------------------ keys / mallets
def piano(notes, n, seed=4, bright=1.0, stereo=0.5):
    """Additive stretched-partial piano-like instrument with hammer transient."""
    r = rng(seed)
    out = np.zeros((n, 2))
    for (st, du, m, v) in notes:
        f0 = float(mtof(m))
        dec_base = 7.0 * (0.985 ** (m - 40))
        L = int(min(dec_base * 1.2, du + 1.2) * SR) + int(0.3 * SR)
        t = np.arange(L) / SR
        B = 0.00035
        sig = np.zeros(L)
        nparts = int(min(28, 16000 / f0))
        for k in range(1, nparts + 1):
            fk = f0 * k * np.sqrt(1 + B * k * k)
            if fk > 18000:
                break
            amp = (1.0 / k ** (1.15 - 0.35 * v * bright)) * (1.0 if k == 1 else 0.85)
            dk = dec_base / (1 + 0.35 * (k - 1))
            det = 1 + r.normal(0, 0.0004)
            part = (np.sin(2 * np.pi * fk * t + r.uniform(0, 6.28)) + 0.6 * np.sin(2 * np.pi * fk * det * t)) * np.exp(-t / dk)
            # two-stage decay (prompt + aftersound)
            part *= 0.65 + 0.35 * np.exp(-t / (0.25 + 0.6 / k))
            sig += amp * part
        ham = r.standard_normal(int(0.02 * SR)) * np.exp(-np.arange(int(0.02 * SR)) / (0.003 * SR))
        ham = bp(ham, min(f0 * 4 + 1500, 9000), 0.3) * 0.25 * v
        sig[: ham.shape[0]] += ham
        rel = np.ones(L)
        gate = int(du * SR)
        if gate < L:
            rel[gate:] = np.exp(-np.arange(L - gate) / (0.18 * SR))
        sig *= rel * v * 0.18
        sig[: int(0.002 * SR)] *= np.linspace(0, 1, int(0.002 * SR))
        p = np.clip((m - 60) / 30.0, -1, 1) * stereo
        _place(out, pan_stereo(sig, p), st)
    return out


def fm_pluck(notes, n, seed=5, ratio=2.0, index=3.0, decay=0.35, idx_decay=0.12, bright=1.0, pan_spread=0.4, attack=0.002):
    r = rng(seed)
    out = np.zeros((n, 2))
    for j, (st, du, m, v) in enumerate(notes):
        f0 = float(mtof(m))
        L = int((min(du, 2.0) + decay * 5) * SR)
        t = np.arange(L) / SR
        I = index * bright * v * np.exp(-t / idx_decay)
        mod = np.sin(2 * np.pi * f0 * ratio * t)
        car = np.sin(2 * np.pi * f0 * t + I * mod)
        env = np.minimum(t / attack, 1) * np.exp(-t / decay)
        gate = int(du * SR)
        if gate < L:
            env[gate:] *= np.exp(-np.arange(L - gate) / (0.05 * SR))
        sig = car * env * v * 0.35
        p = pan_spread * (1 if j % 2 else -1) * r.uniform(0.3, 1)
        _place(out, pan_stereo(sig, p), st)
    return out


def bell(notes, n, seed=6, ratio=3.5, index=2.2, decay=2.2, shimmer=0.5, pan_spread=0.6):
    """Glassy inharmonic FM bell."""
    r = rng(seed)
    out = np.zeros((n, 2))
    for j, (st, du, m, v) in enumerate(notes):
        f0 = float(mtof(m))
        L = int(decay * 4 * SR)
        t = np.arange(L) / SR
        I = index * v * np.exp(-t / (decay * 0.35))
        car = np.sin(2 * np.pi * f0 * t + I * np.sin(2 * np.pi * f0 * ratio * t))
        car += shimmer * 0.35 * np.sin(2 * np.pi * f0 * 2.756 * t) * np.exp(-t / (decay * 0.4))
        car += 0.2 * np.sin(2 * np.pi * f0 * 1.0015 * t)
        env = np.minimum(t / 0.003, 1) * np.exp(-t / decay)
        sig = car * env * v * 0.22
        p = r.uniform(-pan_spread, pan_spread)
        _place(out, pan_stereo(sig, p), st)
    return out


# ------------------------------------------------------------------ bass
def sub_bass(notes, n, seed=7, harm=0.25, attack=0.01, release=0.15, glide=0.0):
    out = np.zeros(n)
    for (st, du, m, v) in notes:
        L = int((du + release + 0.02) * SR)
        f0 = float(mtof(m))
        ph = 2 * np.pi * f0 * np.arange(L) / SR
        s = np.sin(ph) + harm * np.sin(2 * ph) + harm * 0.4 * np.sin(3 * ph)
        s = softclip(s, 1.3)
        env = adsr(L, attack, 0.3, 0.9, release, du)
        _place(out, s * env * v * 0.5, st)
    return np.stack([out, out], 1)


def pulse_bass(notes, n, seed=8, cutoff=500, env_amt=2500, decay=0.18, res=0.35, drive=1.5, sub=0.6, release=0.06):
    r = rng(seed)
    out = np.zeros(n)
    for (st, du, m, v) in notes:
        L = int((du + release + 0.02) * SR)
        f0 = float(mtof(m))
        f = np.full(L, f0)
        s = saw(f, SR, 0.0) * 0.7 + square(f * 1.004, 0.5, SR, 0.25) * 0.4
        t = np.arange(L) / SR
        fc = cutoff + env_amt * v * np.exp(-t / decay)
        s = lp4(s, fc, res)
        s = softclip(s * drive, 1.0)
        s += sub * np.sin(2 * np.pi * f0 * t)
        env = adsr(L, 0.003, decay * 2, 0.6, release, du)
        _place(out, s * env * v * 0.45, st)
    return np.stack([out, out], 1)


def reese(notes, n, seed=9, cutoff=700, lfo=0.15, drive=2.2, release=0.3):
    r = rng(seed)
    L0 = n
    out = np.zeros((n, 2))
    for (st, du, m, v) in notes:
        L = int((du + release) * SR)
        f0 = float(mtof(m))
        t = np.arange(L) / SR
        a = saw(np.full(L, f0 * 0.995), SR, 0.0)
        b = saw(np.full(L, f0 * 1.007), SR, 0.5)
        c = saw(np.full(L, f0 * 2.002), SR, 0.2) * 0.3
        s = a + b + c
        fc = cutoff * (1 + 0.7 * np.sin(2 * np.pi * lfo * (t + st)))
        s = lp4(s, fc, 0.25)
        s = softclip(s * drive, 1.0)
        subs = np.sin(2 * np.pi * f0 * t) * 0.8
        env = adsr(L, 0.02, 0.5, 0.9, release, du)
        side = hp(a - b, 200) * 0.25
        mono = (s * 0.5 + subs) * env * v * 0.35
        _place(out, np.stack([mono + side * env * v * 0.35, mono - side * env * v * 0.35], 1), st)
    return out


# ------------------------------------------------------------------ drones & textures
def drone(notes, n, seed=10, partials=(1, 2, 3, 4.01, 5, 6.02, 8), drift=0.25, attack=3.0, release=4.0, bright=0.5):
    r = rng(seed)
    out = np.zeros((n, 2))
    for (st, du, m, v) in notes:
        L = int((du + release) * SR)
        f0 = float(mtof(m))
        t = np.arange(L) / SR
        env = adsr(L, attack, 2.0, 0.95, release, du)
        sl = np.zeros(L)
        sr_ = np.zeros(L)
        for k, p in enumerate(partials):
            if f0 * p > 12000:
                continue
            rate = r.uniform(0.02, 0.09)
            am = 0.5 + 0.5 * np.sin(2 * np.pi * rate * t + r.uniform(0, 6.28))
            amp = (bright ** k) * am
            det = r.normal(0, 0.7) / 1200
            sl += amp * np.sin(2 * np.pi * f0 * p * (1 + det) * t + r.uniform(0, 6.28))
            sr_ += amp * np.sin(2 * np.pi * f0 * p * (1 - det) * t + r.uniform(0, 6.28))
        g = v * 0.18
        _place(out, np.stack([sl * env * g, sr_ * env * g], 1), st)
    return out


def noise_bed(n, seed=11, lo=200, hi=3000, level=0.05, motion=0.1, stereo=True):
    r = rng(seed)
    t = np.arange(n) / SR
    chans = []
    for c in range(2 if stereo else 1):
        x = r.standard_normal(n)
        fc = np.exp(np.log(lo) + (np.log(hi) - np.log(lo)) * (0.5 + 0.5 * np.sin(2 * np.pi * motion * t + c * 1.7 + seed)))
        y = bp(x, fc, 0.3)
        chans.append(y * level)
    if not stereo:
        chans = chans * 2
    return np.stack(chans, 1)


def breath_texture(n, seed=12, rate=0.18, level=0.06, fc=900):
    """Organic slow 'breathing' filtered noise (VITA)."""
    r = rng(seed)
    t = np.arange(n) / SR
    env = (0.5 - 0.5 * np.cos(2 * np.pi * rate * t)) ** 2
    x = r.standard_normal((n, 2))
    y = np.stack([bp(x[:, c], fc * (0.7 + 0.6 * env), 0.2) for c in range(2)], 1)
    return y * env[:, None] * level


def electric_hum(n, seed=13, f=50.0, level=0.03, crackle=0.2):
    r = rng(seed)
    t = np.arange(n) / SR
    s = np.zeros(n)
    for k, a in [(1, 1.0), (2, 0.6), (3, 0.5), (4, 0.25), (5, 0.3), (7, 0.15), (9, 0.08)]:
        s += a * np.sin(2 * np.pi * f * k * t + k)
    s *= 1 + 0.1 * np.sin(2 * np.pi * 0.13 * t)
    cr = (r.random(n) < 0.0006 * crackle) * r.standard_normal(n)
    cr = hp(cr, 2000) * 2
    mono = s * level + cr * level
    return np.stack([mono, mono * 0.95], 1)


def glitch_layer(n, hits, seed=14, level=0.25):
    """Fractured signal textures: short bit-crushed tonal fragments at given times."""
    r = rng(seed)
    out = np.zeros((n, 2))
    for h in hits:
        L = int(r.uniform(0.03, 0.14) * SR)
        t = np.arange(L) / SR
        f = r.choice([880, 1320, 1760, 2640, 3520]) * r.choice([0.5, 1, 2])
        s = np.sign(np.sin(2 * np.pi * f * t)) * 0.5 + r.standard_normal(L) * 0.3
        step = int(r.choice([4, 8, 16]))
        s = np.repeat(s[::step], step)[:L]
        s *= np.exp(-t / (L / SR / 2.5))
        s = bp(s, r.uniform(1500, 6000), 0.4)
        _place(out, pan_stereo(s * level, r.uniform(-0.9, 0.9)), h)
    return out
