"""Sound-effect synthesis for Temporal: First Jump. Every sound is generated from oscillators,
noise and resonator models (no recordings, no third-party samples)."""
import numpy as np
from .dsp import (SR, rng, lp, hp, bp, lp4, softclip, pan_stereo, widen, fade, reverb, sos_filter, saw, square, bitcrush)
from .drums import modal, tailfade, metal_hit, anvil, boom, kick, riser, downlifter, sub_drop, tick, reverse_swell
from .song import circular


def T(sec):
    return np.arange(int(sec * SR)) / SR


def place(buf, sig, t):
    i = int(t * SR)
    if i >= buf.shape[0]:
        return
    e = min(buf.shape[0], i + sig.shape[0])
    buf[i:e] += sig[: e - i]


def st(m, p=0.0):
    return pan_stereo(m, p)


def onset(x, ms=0.4):
    k = max(2, int(ms * SR / 1000))
    y = x.copy()
    if y.ndim == 2:
        y[:k] *= np.linspace(0, 1, k)[:, None]
    else:
        y[:k] *= np.linspace(0, 1, k)
    return y


def chirp(f0, f1, sec, tau=None, shape='exp'):
    t = T(sec)
    if shape == 'exp':
        f = f1 + (f0 - f1) * np.exp(-t / (tau or sec / 4))
    else:
        f = f0 * (f1 / f0) ** (t / sec)
    return np.sin(2 * np.pi * np.cumsum(f) / SR), f


def noise(n, r):
    return r.standard_normal(n)


def burst(r, sec, fc_lo, fc_hi, decay):
    t = T(sec)
    x = noise(t.shape[0], r)
    x = bp(x, np.sqrt(fc_lo * fc_hi), 0.1) if fc_hi < 18000 else hp(x, fc_lo)
    return x * np.exp(-t / decay)


def grains(r, sec, count, f_lo, f_hi, dec_lo, dec_hi, spread=1.0, dist=1.5, amp_decay=0.6, stereo=True, q=0.92):
    """Many tiny resonant impacts (shards, pebbles, sparks) scattered over time."""
    out = np.zeros((int(sec * SR), 2))
    for _ in range(count):
        tt = (r.random() ** dist) * sec * 0.85
        f = np.exp(r.uniform(np.log(f_lo), np.log(f_hi)))
        d = r.uniform(dec_lo, dec_hi)
        L = int(d * 6 * SR) + 16
        t = np.arange(L) / SR
        exc = r.standard_normal(L) * np.exp(-t / 0.0004)
        g = bp(exc, f, q) * np.exp(-t / d)
        g += 0.5 * bp(exc, f * r.uniform(1.4, 2.7), q) * np.exp(-t / (d * 0.6))
        a = np.exp(-tt / (sec * amp_decay)) * r.uniform(0.3, 1.0)
        place(out, st(onset(g) * a, r.uniform(-spread, spread) if stereo else 0), tt)
    return out


def crackle(r, sec, rate, fc, q=0.5, decay=None, amp_jitter=1.0):
    t = T(sec)
    n = t.shape[0]
    imp = (r.random(n) < rate / SR) * r.standard_normal(n) * (r.random(n) ** amp_jitter)
    y = bp(imp, fc, q) * 4
    if decay:
        y *= np.exp(-t / decay)
    return y


def norm(x, peak=0.9):
    return x / (np.abs(x).max() + 1e-12) * peak


# ===================================================================== kinetic accelerator
def kinetic_charge(seed, dur=0.9):
    r = rng(seed)
    t = T(dur + 0.25)
    n = t.shape[0]
    x = np.clip(t / dur, 0, 1)
    f = 140 * (8.5 ** (x ** 1.4)) * r.uniform(0.95, 1.05)
    ph = 2 * np.pi * np.cumsum(f) / SR
    tone = np.sin(ph) + 0.35 * np.sin(2 * ph) + 0.15 * np.sin(3 * ph + 0.3)
    whine = np.sin(2 * np.pi * np.cumsum(f * 6.02) / SR) * 0.12 * x ** 2
    cr = crackle(r, dur + 0.25, 300 + 1800 * 1, 5000, 0.4) * (x ** 2) * 0.25
    hum = np.sin(2 * np.pi * 55 * t) * 0.3 * x
    env = np.where(t < dur, (0.15 + 0.85 * x ** 1.2), np.exp(-(t - dur) / 0.05))
    m = (tone * 0.5 + whine + hum) * env + cr * env
    # lock click at full charge
    clk = tick(seed + 7, f=2600, decay=0.004) * 0.7
    place(m[:, None] if False else m, clk, dur) if False else None
    m[int(dur * SR): int(dur * SR) + clk.shape[0]] += clk[: n - int(dur * SR)]
    s = np.stack([m, m], 1)
    s[:, 0] += hp(r.standard_normal(n), 7000) * 0.03 * x
    s[:, 1] += hp(r.standard_normal(n), 7000) * 0.03 * x
    return tailfade(onset(s, 2), 0.15)


def kinetic_fire(seed, tier=0):
    r = rng(seed)
    dur = 0.7 + 0.15 * tier
    t = T(dur)
    n = t.shape[0]
    pv = r.uniform(0.93, 1.07)          # per-variation pitch
    snap = burst(r, dur, 2500 * pv, 9000, 0.004 * r.uniform(0.8, 1.2)) * 1.2
    thwip, _ = chirp(2200 * r.uniform(0.85, 1.15), 180 * pv, dur, tau=0.025 * r.uniform(0.8, 1.3))
    thwip *= np.exp(-t / 0.09) * 0.7
    body_lo = 48 * pv
    body = kick(seed, f_hi=160 * pv, f_lo=body_lo, sweep=0.03, decay=0.12 + 0.04 * tier, click=0.2, drive=1.8)[:n]
    body = np.pad(body, (0, n - body.shape[0]))
    zf = 900 * r.uniform(0.85, 1.15)
    zap = np.sin(2 * np.pi * zf * t + 6 * np.sin(2 * np.pi * zf * 2.55 * t)) * np.exp(-t / 0.035) * 0.35
    air = bp(r.standard_normal(n), 1800 * np.exp(-t / 0.15) + 300, 0.3) * np.exp(-t / 0.16) * 0.5
    rf = [f * pv * r.uniform(0.97, 1.03) for f in (1240, 1990, 3120, 4410)]
    ring = modal(rf, [0.18, 0.12, 0.08, 0.06], [1, 0.6, 0.4, 0.25], dur, seed) * 0.5
    m = snap + thwip + body * (0.8 + 0.15 * tier) + zap + air + ring
    if tier >= 1:
        # extra sub locked to the body pitch (no beating against the thump)
        f = body_lo + 80 * np.exp(-t / 0.05)
        m += np.sin(2 * np.pi * np.cumsum(f) / SR) * np.minimum(t / 0.002, 1) * np.exp(-t / (0.16 + 0.05 * tier)) * 0.45 * tier
    if tier >= 2:
        m += crackle(r, dur, 2500, 4500, 0.4, decay=0.12) * 0.4
        m += modal([2620 * pv, 3980 * pv, 5250 * pv], [0.3, 0.2, 0.15], [0.6, 0.4, 0.3], dur, seed + 1) * 0.4
    if tier >= 3:
        m += np.sin(2 * np.pi * np.cumsum(5200 * np.exp(-t / 0.08) + 600) / SR) * np.exp(-t / 0.12) * 0.25
    m = softclip(m * 0.9, 1.3)
    s = np.stack([m, m], 1)
    side = hp(r.standard_normal(n), 3000) * np.exp(-t / 0.05) * (0.08 + 0.05 * tier)
    s[:, 0] += side
    s[:, 1] -= side
    return tailfade(onset(s, 0.3), 0.3)


def kinetic_travel_loop(seed, sec=1.0):
    r = rng(seed)
    f0 = 820 * r.uniform(0.9, 1.15)
    def fn(n):
        t = np.arange(n) / SR
        rr = rng(seed + 1)
        flutter = 1 + 0.004 * np.sin(2 * np.pi * 31 * t) + 0.002 * np.sin(2 * np.pi * 7.3 * t)
        ph = 2 * np.pi * np.cumsum(f0 * flutter) / SR
        tone = (np.sin(ph) + 0.4 * np.sin(2 * ph) + 0.2 * np.sin(3.01 * ph)) * (0.8 + 0.2 * np.sin(2 * np.pi * 30 * t))
        rush = bp(rr.standard_normal(n), 3200, 0.2) * 0.6
        buzz = bp(saw(np.full(n, f0 / 4), SR, 0.0), 1500, 0.3) * 0.2
        m = tone * 0.4 + rush + buzz
        return np.stack([m, m], 1)
    x = circular(fn, int(sec * SR), xf_sec=0.25)
    return x[:, 0]


def kinetic_impact(seed):
    r = rng(seed)
    dur = 1.1
    t = T(dur)
    n = t.shape[0]
    crack = burst(r, dur, 1200, 18000, 0.006) * 1.3
    clank = metal_hit(seed, f0=r.uniform(260, 420), decay=0.35, length=dur, bright=1.2)[:n] * 1.6
    thump = kick(seed + 3, f_hi=120, f_lo=50, sweep=0.02, decay=0.1, click=0.1, drive=1.5)[:n]
    thump = np.pad(thump, (0, n - thump.shape[0]))
    # temporal ripple: fast descending comb-filtered shimmer
    rip = r.standard_normal(n) * np.exp(-t / 0.18)
    fc = 6000 * np.exp(-t / 0.12) + 400
    rip = bp(rip, fc, 0.85) * 0.5
    deb = grains(r, dur, 10, 1500, 6000, 0.01, 0.04, dist=1.8, amp_decay=0.3)
    m = crack + clank + thump * 0.9 + rip
    s = st(m) * 1.0 + deb * 0.5
    return tailfade(onset(s, 0.2), 0.35)


# ===================================================================== breach charge
def breach_prep(seed):
    r = rng(seed)
    dur = 0.9
    out = np.zeros((int(dur * SR), 2))
    c1 = metal_hit(seed, f0=r.uniform(380, 520), decay=0.05, length=0.25, bright=0.8) + tick(seed, f=1800, decay=0.006)[: int(0.25 * SR)].sum() * 0
    place(out, st(onset(c1) * 1.2, -0.2), 0.0)
    t = T(0.25)
    whirr = saw(220 + 500 * (t / 0.25), SR, 0.0)
    whirr = bp(whirr, 900, 0.4) * np.sin(np.pi * t / 0.25) * 0.25
    place(out, st(whirr, 0.1), 0.08)
    c2 = metal_hit(seed + 1, f0=r.uniform(600, 800), decay=0.03, length=0.2) * 1.0
    place(out, st(onset(c2), 0.2), 0.34)
    for k, f in enumerate([1600, 2200]):
        tb = T(0.09)
        b = np.sin(2 * np.pi * f * tb) * np.minimum(tb / 0.003, 1) * np.exp(-tb / 0.05) * 0.35
        place(out, st(b), 0.5 + 0.12 * k)
    return tailfade(out, 0.2)


def breach_launch(seed):
    r = rng(seed)
    dur = 0.8
    t = T(dur)
    n = t.shape[0]
    thump = kick(seed, f_hi=110, f_lo=55, sweep=0.03, decay=0.09, click=0.15, drive=1.4)[:n]
    thump = np.pad(thump, (0, n - thump.shape[0]))
    air = r.standard_normal(n)
    air = lp(air, 5000 * np.exp(-t / 0.05) + 300) * np.exp(-t / 0.12) * 0.7
    tube = bp(r.standard_normal(n), 420 * r.uniform(0.9, 1.1), 0.85) * np.exp(-t / 0.08) * 0.8
    clack = metal_hit(seed + 2, f0=700, decay=0.03, length=0.2)
    clack = np.pad(clack, (0, n - clack.shape[0]))
    whoosh = bp(r.standard_normal(n), 900 + 1500 * np.exp(-t / 0.2), 0.4) * np.sin(np.pi * np.clip(t / 0.5, 0, 1)) * 0.25
    m = thump * 1.0 + air + tube + clack * 0.6 + whoosh
    s = st(m)
    return tailfade(onset(s, 0.3), 0.3)


def breach_activate(seed):
    r = rng(seed)
    dur = 0.8
    out = np.zeros((int(dur * SR), 2))
    base = 1500 * r.uniform(0.95, 1.05)
    for k in range(3):
        tb = T(0.07)
        b = (np.sin(2 * np.pi * base * (1 + 0.25 * k) * tb) + 0.3 * np.sign(np.sin(2 * np.pi * base * (1 + 0.25 * k) * tb))) * np.minimum(tb / 0.002, 1) * np.exp(-tb / 0.04) * 0.3
        place(out, st(b), 0.1 * k)
    t = T(0.5)
    ch, _ = chirp(200, 1800, 0.5, shape='lin')
    ch = ch * (t / 0.5) ** 2 * 0.3
    cr = crackle(r, 0.5, 900, 4000, 0.5) * (t / 0.5) * 0.25
    place(out, st(ch + cr), 0.3)
    return tailfade(out, 0.15)


def breach_explosion(seed, tier=0):
    r = rng(seed)
    dur = 3.0 + 0.33 * tier
    t = T(dur)
    n = t.shape[0]
    crack = burst(r, dur, 800, 18000, 0.008) * 1.4
    body = boom(seed, f0=38 - 2 * tier, decay=0.9 + 0.25 * tier, length=dur, noise=0.5, drive=2.4)[:n]
    crunch = bp(r.standard_normal(n), 700, 0.1)
    crunch = softclip(crunch * 3, 1.0) * np.exp(-t / (0.25 + 0.05 * tier)) * 0.5
    mid = lp(r.standard_normal(n), 2500 * np.exp(-t / 0.3) + 200) * np.exp(-t / 0.5) * 0.6
    deb = grains(r, dur, 40 + 15 * tier, 400, 5000, 0.01, 0.06, dist=1.4, amp_decay=0.35)
    tail = lp(r.standard_normal(n), 300) * np.exp(-t / (1.0 + 0.3 * tier)) * np.minimum(t / 0.1, 1) * 0.6
    m = crack + body * 1.1 + crunch + mid + tail
    s = st(m)
    s = s + deb * 0.6
    s = widen(s + reverb(s * 0.25, 'chamber'), 1.3)
    if tier >= 2:
        s += st(sub_drop(min(dur, 2.5), f_hi=80, f_lo=26)[:n].copy() if sub_drop(min(dur, 2.5)).shape[0] >= n else np.pad(sub_drop(min(dur, 2.5), f_hi=80, f_lo=26), (0, n - sub_drop(min(dur, 2.5)).shape[0])) * 0.5)
    return tailfade(onset(softclip(s, 1.1), 0.3), 0.4)


def breach_shockwave(seed):
    r = rng(seed)
    dur = 2.2
    t = T(dur)
    n = t.shape[0]
    x = t / dur
    whoomp = np.sin(2 * np.pi * np.cumsum(30 + 60 * np.exp(-t / 0.25)) / SR) * np.minimum(t / 0.04, 1) * np.exp(-t / 0.6)
    rushL = bp(r.standard_normal(n), 4000 * np.exp(-t / 0.35) + 180, 0.35)
    rushR = bp(r.standard_normal(n), 4200 * np.exp(-t / 0.35) + 170, 0.35)
    env = np.minimum(t / 0.03, 1) * np.exp(-t / 0.55)
    s = np.stack([rushL, rushR], 1) * env[:, None] * 0.9 + st(whoomp) * 0.9
    # doppler-ish pan sweep
    pan = np.clip(-1 + 2 * x * 1.5, -1, 1) * 0.6
    s[:, 0] *= np.cos((pan + 1) * np.pi / 4) * np.sqrt(2)
    s[:, 1] *= np.sin((pan + 1) * np.pi / 4) * np.sqrt(2)
    return tailfade(onset(s, 1.0), 0.4)


def cooldown(seed):
    r = rng(seed)
    dur = 1.4
    out = np.zeros((int(dur * SR), 2))
    t = T(0.8)
    hiss = hp(r.standard_normal(t.shape[0]), 3000) * np.minimum(t / 0.01, 1) * np.exp(-t / 0.25) * 0.5
    place(out, np.stack([hiss, hp(r.standard_normal(t.shape[0]), 3000) * np.minimum(t / 0.01, 1) * np.exp(-t / 0.25) * 0.5], 1), 0.0)
    for k in range(6):
        place(out, st(tick(seed + k, f=r.uniform(3000, 5500), decay=0.004) * r.uniform(0.15, 0.35), r.uniform(-0.6, 0.6)), 0.1 + r.random() * 0.6)
    for k, f in enumerate([1320, 1980]):
        tb = T(0.35)
        b = np.sin(2 * np.pi * f * tb + 1.2 * np.sin(2 * np.pi * f * 2 * tb) * np.exp(-tb / 0.05)) * np.minimum(tb / 0.003, 1) * np.exp(-tb / 0.12) * 0.35
        place(out, st(b), 0.85 + 0.09 * k)
    return tailfade(out, 0.2)


def weapon_switch(seed):
    r = rng(seed)
    dur = 0.6
    out = np.zeros((int(dur * SR), 2))
    t = T(0.14)
    slide = bp(r.standard_normal(t.shape[0]), 1500 + 3000 * (t / 0.14), 0.4) * np.sin(np.pi * t / 0.14) * 0.4
    place(out, st(slide, -0.2), 0.0)
    place(out, st(onset(metal_hit(seed, f0=r.uniform(900, 1200), decay=0.02, length=0.12)) * 1.2, -0.1), 0.13)
    place(out, st(onset(metal_hit(seed + 1, f0=r.uniform(500, 700), decay=0.03, length=0.15)) * 1.2, 0.1), 0.22)
    tb = T(0.18)
    sv = bp(saw(380 + 700 * tb / 0.18, SR, 0.0), 1200, 0.4) * np.sin(np.pi * tb / 0.18) * 0.18
    place(out, st(sv, 0.2), 0.25)
    tb = T(0.08)
    place(out, st(np.sin(2 * np.pi * 2400 * tb) * np.minimum(tb / 0.002, 1) * np.exp(-tb / 0.03) * 0.25), 0.42)
    return tailfade(out, 0.15)


# ===================================================================== destruction by material
def metal_bend(seed):
    """Stick-slip creak: irregular friction impulses exciting high-Q plate modes, slow pitch drift."""
    from .dsp import svf
    r = rng(seed)
    dur = 1.6
    t = T(dur)
    n = t.shape[0]
    rate = 35 + 60 * (0.5 + 0.5 * np.sin(2 * np.pi * r.uniform(0.4, 1.0) * t + r.uniform(0, 6))) * (0.6 + 0.4 * t / dur)
    ph = np.cumsum(rate / SR)
    imp = np.diff(np.floor(ph), prepend=0) * r.uniform(0.4, 1.0, n)
    exc = lp(imp, 3000)
    f0 = r.uniform(150, 280)
    body = np.zeros(n)
    for k, (fr, a) in enumerate([(1, 1.0), (2.32, 0.7), (3.91, 0.5), (5.43, 0.35), (7.2, 0.2)]):
        fc = f0 * fr * (1 + 0.05 * np.sin(2 * np.pi * 0.6 * t + k) + 0.04 * t / dur)
        body += svf(np.ascontiguousarray(exc), np.ascontiguousarray(fc), 0.985, 1, SR) * a
    env = np.sin(np.pi * np.clip(t / dur, 0, 1)) ** 0.6
    groan = bp(saw(f0 * 0.5 * (1 + 0.08 * t), SR, 0.0), f0 * 2, 0.7) * 0.06
    m = (body + groan) * env
    m = m / (np.abs(m).max() + 1e-9)
    s = st(m)
    return tailfade(onset(s + reverb(s * 0.15, 'metal'), 2), 0.25)


def metal_break(seed):
    r = rng(seed)
    dur = 1.5
    t = T(dur)
    n = t.shape[0]
    snap = burst(r, dur, 1500, 18000, 0.003) * 1.5
    ring = metal_hit(seed, f0=r.uniform(300, 650), decay=0.45, length=dur, bright=1.3)[:n] * 1.8
    ring2 = metal_hit(seed + 5, f0=r.uniform(900, 1500), decay=0.25, length=dur, bright=1.4)[:n] * 0.9
    thud = kick(seed, f_hi=140, f_lo=60, sweep=0.02, decay=0.08, click=0.1)[:n]
    thud = np.pad(thud, (0, n - thud.shape[0]))
    tink = grains(r, dur, 8, 2500, 8000, 0.02, 0.08, dist=1.2, amp_decay=0.4)
    m = snap + ring + ring2 + thud * 0.7
    s = st(m) + tink * 0.6
    s = s + reverb(s * 0.15, 'metal')
    return tailfade(onset(s, 0.2), 0.35)


def glass_break(seed):
    r = rng(seed)
    dur = 1.7
    t = T(dur)
    n = t.shape[0]
    crack = hp(burst(r, dur, 3000, 18000, 0.005), 2500) * 1.4
    shards = grains(r, dur, int(r.uniform(55, 85)), 2200, 11000, 0.015, 0.12, dist=1.7, amp_decay=0.45, q=0.95)
    tinkle = grains(r, dur, 25, 4000, 12000, 0.03, 0.2, dist=1.0, amp_decay=0.7, q=0.97) * 0.5
    thud = kick(seed, f_hi=200, f_lo=90, sweep=0.01, decay=0.05, click=0.1)[:n]
    thud = np.pad(thud, (0, n - thud.shape[0]))
    s = st(crack + thud * 0.4) + shards * 1.1 + tinkle
    # tame isolated shard spikes so the break reads as dense, not as single clicks
    pk = np.percentile(np.abs(s), 99.7) * 1.5 + 1e-9
    s = np.tanh(s / pk) * pk
    return tailfade(onset(s, 0.2), 0.3)


def concrete_crack(seed):
    r = rng(seed)
    dur = 1.4
    t = T(dur)
    n = t.shape[0]
    density = 2500 * np.exp(-t / 0.2) + 200
    imp = (r.random(n) < density / SR) * r.standard_normal(n)
    cr = lp(bp(imp, 1200, 0.2), 4000) * 3
    thump = kick(seed, f_hi=100, f_lo=45, sweep=0.03, decay=0.12, click=0.2, drive=1.4)[:n]
    thump = np.pad(thump, (0, n - thump.shape[0]))
    crunch = softclip(bp(r.standard_normal(n), 500, 0.15) * 3, 1.0) * np.exp(-t / 0.15) * 0.5
    dust = bp(r.standard_normal(n), 2500, 0.1) * np.exp(-t / 0.6) * np.minimum(t / 0.05, 1) * 0.12
    deb = grains(r, dur, 15, 600, 3500, 0.01, 0.05, dist=1.3, amp_decay=0.5, q=0.8)
    s = st(cr * np.exp(-t / 0.4) + thump + crunch + dust) + deb * 0.6
    return tailfade(onset(s, 0.2), 0.35)


def composite_crack(seed):
    r = rng(seed)
    dur = 1.0
    t = T(dur)
    n = t.shape[0]
    imp = (r.random(n) < (1800 * np.exp(-t / 0.12) + 100) / SR) * r.standard_normal(n)
    fib = bp(imp, r.uniform(800, 1400), 0.6) * 3 + bp(imp, r.uniform(1800, 2600), 0.6) * 2
    snap = burst(r, dur, 1000, 8000, 0.004)
    thud = kick(seed, f_hi=150, f_lo=70, sweep=0.02, decay=0.06, click=0.1)[:n]
    thud = np.pad(thud, (0, n - thud.shape[0]))
    m = fib * np.exp(-t / 0.3) + snap + thud * 0.5
    return tailfade(onset(st(m) + grains(r, dur, 8, 900, 3000, 0.01, 0.04) * 0.4, 0.2), 0.3)


def structural_collapse(seed):
    r = rng(seed)
    dur = 4.0
    t = T(dur)
    n = t.shape[0]
    x = t / dur
    rumbleL = lp(r.standard_normal(n), 140) * 2.5
    rumbleR = lp(r.standard_normal(n), 150) * 2.5
    env = np.minimum(t / 0.3, 1) * np.exp(-t / 1.4)
    s = np.stack([rumbleL, rumbleR], 1) * env[:, None]
    times = np.sort(np.concatenate([[0.0], r.uniform(0.1, 2.3, 6)]))
    for k, tt in enumerate(times):
        b = boom(seed + k, f0=r.uniform(40, 60), decay=0.4, length=1.5, noise=0.6, drive=2.0)
        place(s, st(onset(b) * (1.0 if k == 0 else r.uniform(0.4, 0.8)), r.uniform(-0.5, 0.5)), tt)
        c = concrete_crack(seed + 20 + k)
        place(s, c * r.uniform(0.4, 0.8), tt + 0.02)
    place(s, metal_bend(seed + 40) * 0.5, 0.4)
    place(s, metal_break(seed + 41) * 0.5, 1.2)
    s += grains(r, dur, 90, 300, 5000, 0.01, 0.06, dist=1.2, amp_decay=0.5) * 0.5
    s = s + reverb(s * 0.2, 'hall')
    return tailfade(onset(softclip(s * 0.8, 1.1), 0.5), 0.35)


def debris_heavy(seed):
    r = rng(seed)
    dur = 1.6
    out = np.zeros((int(dur * SR), 2))
    tt = 0.0
    gap = r.uniform(0.12, 0.2)
    k = 0
    while tt < dur * 0.85 and k < 12:
        f0 = r.uniform(90, 300)
        hit = modal([f0, f0 * 1.7, f0 * 2.6, f0 * 4.1], [0.08, 0.05, 0.04, 0.02], [1, 0.6, 0.4, 0.2], 0.4, seed + k, strike=0.002, strike_bright=3000)
        kk = kick(seed + k, f_hi=110, f_lo=55, sweep=0.015, decay=0.05, click=0.3)[: hit.shape[0]]
        hit[: kk.shape[0]] += kk * 0.6
        a = np.exp(-tt / 0.6) * r.uniform(0.6, 1.0)
        place(out, st(onset(hit) * a, r.uniform(-0.5, 0.5)), tt)
        tt += gap * r.uniform(0.6, 1.2)
        gap *= 0.8
        k += 1
    return tailfade(out, 0.3)


def debris_small(seed):
    r = rng(seed)
    dur = 0.9
    out = grains(r, dur, int(r.uniform(14, 26)), 900, 5000, 0.006, 0.03, dist=1.6, amp_decay=0.35, q=0.85)
    return tailfade(out, 0.3)


def electrical_short(seed):
    r = rng(seed)
    dur = 1.1
    t = T(dur)
    n = t.shape[0]
    gate = (sos_filter(r.standard_normal(n), 'lowpass', 25, 2) > r.uniform(-0.1, 0.2)).astype(float)
    gate = lp(gate, 200)
    buzz = saw(np.full(n, r.choice([100, 120]) * r.uniform(0.98, 1.02)), SR, 0.0)
    buzz = hp(softclip(buzz * 3 + r.standard_normal(n) * 1.5, 1.0), 300) * 0.4
    zap = crackle(r, dur, 1500, 3500, 0.3) * 0.8 + crackle(r, dur, 700, 7500, 0.4) * 0.5
    pop = burst(r, dur, 1000, 12000, 0.005) * 1.2
    env = np.exp(-t / 0.5)
    m = (buzz + zap) * gate * env + pop
    return tailfade(onset(st(m) + reverb(st(m) * 0.1, 'room'), 0.2), 0.25)


def energy_discharge(seed):
    r = rng(seed)
    dur = 1.7
    t = T(dur)
    n = t.shape[0]
    f = 2400 * np.exp(-t / 0.18) + 90 * r.uniform(0.9, 1.1)
    ph = 2 * np.pi * np.cumsum(f) / SR
    fm = np.sin(ph + 4 * np.exp(-t / 0.3) * np.sin(ph * 2.01))
    plasma = bp(r.standard_normal(n), 1500 * np.exp(-t / 0.3) + 200, 0.5) * 0.6
    cr = crackle(r, dur, 1200, 5000, 0.4, decay=0.3) * 0.5
    env = np.minimum(t / 0.004, 1) * np.exp(-t / 0.45)
    m = (fm * 0.6 + plasma + cr) * env
    s = st(m)
    s = s + reverb(s * 0.3, 'plate')
    return tailfade(onset(s, 0.3), 0.35)


def machinery_failure(seed):
    r = rng(seed)
    dur = 2.8
    t = T(dur)
    n = t.shape[0]
    x = t / dur
    f = 120 * (1 - x) ** 1.5 + 18
    ph = 2 * np.pi * np.cumsum(f) / SR
    motor = (np.sin(ph) + 0.5 * np.sin(2 * ph) + 0.4 * np.sin(3 * ph) + 0.3 * square(f * 4, 0.5, SR, 0.0) * 0.3)
    whine = np.sin(2 * np.pi * np.cumsum(f * 10.3) / SR) * 0.2
    grind = bp(r.standard_normal(n), 1200, 0.3) * (0.5 + 0.5 * np.sign(np.sin(ph * 0.5))) * 0.35
    env = np.minimum(t / 0.05, 1) * (1 - x) ** 0.6
    m = (motor * 0.5 + whine + grind) * env
    out = st(m)
    place(out, st(onset(metal_hit(seed, f0=180, decay=0.3, length=1.0)) * 1.4), dur * 0.78)
    place(out, st(onset(kick(seed, f_hi=90, f_lo=45, decay=0.15)) * 0.9), dur * 0.78)
    sp = crackle(r, dur, 300, 5000, 0.4) * np.exp(-t / 1.0) * 0.4
    out += st(sp, 0.3)
    return tailfade(onset(out, 0.3), 0.2)


# ===================================================================== critical assets
def _crit_common(r, dur, seed):
    s = st(boom(seed, f0=34, decay=1.25, length=dur, noise=0.6, drive=2.5)[: int(dur * SR)]) * 1.2
    s += st(burst(r, dur, 600, 18000, 0.01)) * 1.2
    return s


def crit_helix(seed):
    r = rng(seed)
    dur = 4.0
    t = T(dur)
    n = t.shape[0]
    s = np.zeros((n, 2))
    # power-down sweep of the AI core
    f = 1800 * np.exp(-t / 0.9) + 30
    ph = 2 * np.pi * np.cumsum(f) / SR
    pd = (np.sin(ph) + 0.4 * np.sign(np.sin(ph)) * 0.3) * np.exp(-t / 1.6) * 0.5
    s += st(pd)
    # data stutter glitches before the blast
    for k in range(10):
        g = bitcrush(np.sin(2 * np.pi * r.choice([880, 1320, 1760]) * T(0.05)) * 0.6, 6, 8)
        place(s, st(onset(g), r.uniform(-0.8, 0.8)), 0.02 + 0.045 * k)
    blast = _crit_common(r, dur - 0.45, seed)
    place(s, blast, 0.45)
    place(s, energy_discharge(seed + 1) * 0.8, 0.5)
    place(s, electrical_short(seed + 2) * 0.6, 0.9)
    fans = bp(r.standard_normal(n), 800 * np.exp(-t / 1.5) + 100, 0.2) * np.exp(-t / 2.0) * 0.3
    s += st(fans)
    s = s + reverb(s * 0.25, 'hall')
    return tailfade(onset(softclip(s * 0.7, 1.1), 0.3), 0.4)


def crit_vita(seed):
    r = rng(seed)
    dur = 4.0
    t = T(dur)
    n = t.shape[0]
    s = np.zeros((n, 2))
    place(s, glass_break(seed) * 1.3, 0.0)
    place(s, glass_break(seed + 1) * 0.9, 0.08)
    place(s, _crit_common(r, dur - 0.1, seed), 0.1)
    # liquid gush and bubbling
    gush = lp(r.standard_normal(n), 1200 * np.exp(-t / 1.0) + 200) * np.minimum(t / 0.05, 1) * np.exp(-t / 1.2) * 0.8
    s += np.stack([gush, lp(r.standard_normal(n), 1100) * np.minimum(t / 0.05, 1) * np.exp(-t / 1.2) * 0.8], 1)
    for k in range(70):
        tt = 0.3 + r.random() ** 1.5 * 2.8
        L = int(r.uniform(0.02, 0.06) * SR)
        tb = np.arange(L) / SR
        f0 = r.uniform(300, 1400)
        bub = np.sin(2 * np.pi * np.cumsum(f0 * (1 + 3 * tb / tb[-1])) / SR) * np.sin(np.pi * tb / tb[-1]) * 0.2 * np.exp(-tt / 2)
        place(s, st(bub, r.uniform(-0.7, 0.7)), tt)
    hiss = hp(r.standard_normal(n), 2500) * np.exp(-t / 1.2) * 0.25
    s += st(hiss, 0.2)
    s = s + reverb(s * 0.2, 'hall')
    return tailfade(onset(softclip(s * 0.7, 1.1), 0.3), 0.3)


def crit_nova(seed):
    r = rng(seed)
    dur = 4.0
    t = T(dur)
    n = t.shape[0]
    s = np.zeros((n, 2))
    # pressure build (0.4 s) then breach
    pre = bp(r.standard_normal(int(0.4 * SR)), 600 + 3000 * T(0.4) / 0.4, 0.4) * (T(0.4) / 0.4) ** 2 * 0.6
    place(s, st(pre), 0.0)
    place(s, _crit_common(r, dur - 0.4, seed) * 1.15, 0.4)
    place(s, breach_explosion(seed + 3, tier=3) * 0.7, 0.4)
    for k in range(4):
        place(s, electrical_short(seed + 10 + k) * 0.5, 0.6 + 0.4 * k)
    place(s, metal_bend(seed + 20) * 0.6, 1.2)
    hum = np.zeros(n)
    for h, a in [(1, 1), (2, 0.6), (3, 0.4), (5, 0.2)]:
        hum += a * np.sin(2 * np.pi * 50 * h * t * (1 - 0.35 * t / dur))
    s += st(hum * np.exp(-t / 1.6) * 0.2)
    s = s + reverb(s * 0.25, 'hall')
    return tailfade(onset(softclip(s * 0.7, 1.1), 0.3), 0.4)


def crit_civitas(seed):
    r = rng(seed)
    dur = 4.0
    t = T(dur)
    n = t.shape[0]
    s = np.zeros((n, 2))
    # alarm dyad cut off
    ta = T(0.35)
    al = (np.sin(2 * np.pi * 988 * ta) + np.sin(2 * np.pi * 1047 * ta)) * 0.25 * np.minimum(ta / 0.005, 1)
    place(s, st(al), 0.0)
    # data cascade
    for k in range(24):
        g = bitcrush(np.sin(2 * np.pi * r.choice([440, 660, 990, 1480, 2220]) * T(0.04)) * 0.5, 5, int(r.choice([4, 8, 16])))
        place(s, st(onset(g) * (1 - k / 30), r.uniform(-0.9, 0.9)), 0.3 + 0.035 * k)
    place(s, _crit_common(r, dur - 0.35, seed), 0.35)
    place(s, glass_break(seed + 5) * 0.7, 0.4)
    place(s, metal_break(seed + 6) * 0.6, 0.45)
    # screens shutting off: CRT-like whine drops and clicks
    for k in range(6):
        tt = 0.8 + 0.3 * k
        L = int(0.3 * SR)
        tb = np.arange(L) / SR
        w = np.sin(2 * np.pi * np.cumsum(15000 * np.exp(-tb / 0.05) + 200) / SR) * np.exp(-tb / 0.1) * 0.08
        place(s, st(onset(w) + 0, r.uniform(-0.8, 0.8)), tt)
        place(s, st(tick(seed + k, f=1800, decay=0.004) * 0.3, r.uniform(-0.8, 0.8)), tt)
    s = s + reverb(s * 0.2, 'hall')
    return tailfade(onset(softclip(s * 0.7, 1.1), 0.3), 0.3)


def crit_meridian(seed):
    r = rng(seed)
    dur = 4.0
    t = T(dur)
    n = t.shape[0]
    s = np.zeros((n, 2))
    # temporal implosion: reverse swell sucks in, then the blast
    sw = reverse_swell(38, length=0.7, seed=seed) * 1.2
    place(s, st(sw), 0.0)
    rv = riser(0.7, seed=seed, f_lo=8000, f_hi=300, curve=0.7) * 0.8
    place(s, rv, 0.0)
    place(s, _crit_common(r, dur - 0.7, seed) * 1.2, 0.7)
    # shimmering pitch-falling cloud
    tt = T(dur - 0.7)
    cloud = np.zeros(tt.shape[0])
    for k in range(6):
        f0 = r.uniform(400, 2400)
        cloud += np.sin(2 * np.pi * np.cumsum(f0 * (1 - 0.5 * tt / tt[-1]) * (1 + 0.003 * k)) / SR) * 0.08
    cloud *= np.exp(-tt / 1.6)
    place(s, np.stack([cloud, np.roll(cloud, 300)], 1), 0.7)
    place(s, st(sub_drop(3.0, f_hi=70, f_lo=22)) * 0.9, 0.7)
    for k in range(14):
        g = bitcrush(r.standard_normal(int(0.03 * SR)) * 0.4, 4, 12)
        place(s, st(onset(g), r.uniform(-1, 1)), 0.8 + r.random() * 2.0)
    s = s + reverb(s * 0.3, 'bighall')
    return tailfade(onset(softclip(s * 0.7, 1.1), 0.3), 0.3)


# ===================================================================== UI
def _blip(f, sec, r, fm=0.0, shape=0.0, decay=None):
    t = T(sec)
    ph = 2 * np.pi * f * t
    x = np.sin(ph + fm * np.sin(2 * ph) * np.exp(-t / 0.02))
    if shape:
        x = x * (1 - shape) + np.tanh(3 * x) * shape
    env = np.minimum(t / 0.002, 1) * np.exp(-t / (decay or sec / 3))
    return x * env


def ui_select(seed):
    r = rng(seed)
    f = [1760, 1976, 2093, 1865][seed % 4]
    x = _blip(f, 0.09, r, fm=0.8, decay=0.025) * 0.6 + tick(seed, f=4500, decay=0.003)[: int(0.09 * SR)].shape[0] * 0
    k = tick(seed, f=5200, decay=0.002) * 0.25
    x[: k.shape[0]] += k[: x.shape[0]]
    return tailfade(x, 0.3)


def ui_confirm(seed):
    r = rng(seed)
    base = [1175, 1319, 1245][seed % 3]
    out = np.zeros(int(0.32 * SR))
    place(out, _blip(base, 0.12, r, fm=0.6, decay=0.05) * 0.55, 0.0)
    place(out, _blip(base * 1.5, 0.2, r, fm=0.6, decay=0.08) * 0.6, 0.06)
    return tailfade(out, 0.3)


def ui_back(seed):
    r = rng(seed)
    base = [1568, 1480, 1661][seed % 3]
    out = np.zeros(int(0.3 * SR))
    place(out, _blip(base, 0.1, r, fm=0.5, decay=0.04) * 0.55, 0.0)
    place(out, _blip(base / 1.335, 0.18, r, fm=0.5, decay=0.06) * 0.55, 0.06)
    return tailfade(out, 0.3)


def ui_error(seed):
    r = rng(seed)
    out = np.zeros(int(0.4 * SR))
    f = [311, 330, 294][seed % 3]
    for k in range(2):
        t = T(0.11)
        x = (square(np.full(t.shape[0], f), 0.5, SR, 0.0) + square(np.full(t.shape[0], f * 1.06), 0.5, SR, 0.3)) * 0.5
        x = lp(x, 2200) * np.minimum(t / 0.003, 1) * np.exp(-t / 0.08)
        place(out, x * 0.5, 0.13 * k)
    return tailfade(out, 0.3)


def ui_unlock(seed):
    r = rng(seed)
    out = np.zeros((int(1.5 * SR), 2))
    for k, m in enumerate([1047, 1319, 1568, 2093]):
        place(out, st(_blip(m, 0.6, r, fm=1.0, decay=0.25) * 0.4, -0.3 + 0.2 * k), 0.07 * k)
    sh = grains(r, 1.2, 20, 5000, 11000, 0.05, 0.2, dist=0.8, amp_decay=0.6, q=0.97) * 0.25
    place(out, sh, 0.2)
    return tailfade(out, 0.3)


def ui_upgrade(seed, tier=1):
    r = rng(seed)
    dur = 0.9 + 0.3 * tier
    out = np.zeros((int(dur * SR), 2))
    t = T(0.5)
    sw, _ = chirp(300, 1800 + 600 * tier, 0.5, shape='lin')
    sw = sw * (t / 0.5) ** 1.5 * 0.25
    place(out, st(sw), 0.0)
    notes = [880, 1109, 1319, 1760, 2217, 2637][: 2 + tier]
    for k, f in enumerate(notes):
        place(out, st(_blip(f, 0.5, r, fm=0.8, decay=0.18) * 0.38, -0.4 + 0.8 * k / max(1, len(notes) - 1)), 0.4 + 0.07 * k)
    hum = np.sin(2 * np.pi * 110 * T(0.6)) * np.exp(-T(0.6) / 0.2) * 0.3
    place(out, st(hum), 0.4)
    return tailfade(out, 0.3)


def ui_achievement(seed):
    r = rng(seed)
    out = np.zeros((int(2.2 * SR), 2))
    for k, f in enumerate([1175, 1480, 1760, 2349]):
        place(out, st(_blip(f, 1.6, r, fm=1.2, decay=0.6) * 0.3, -0.5 + 0.33 * k), 0.03 * k)
    sh = grains(r, 1.8, 35, 4000, 12000, 0.05, 0.3, dist=0.7, amp_decay=0.7, q=0.97) * 0.3
    place(out, sh, 0.05)
    place(out, st(np.sin(2 * np.pi * 147 * T(1.0)) * np.exp(-T(1.0) / 0.3) * 0.4), 0.0)
    return tailfade(out + reverb(out * 0.2, 'plate'), 0.3)


def ui_mission_complete(seed):
    r = rng(seed)
    out = np.zeros((int(1.8 * SR), 2))
    for k, f in enumerate([587, 880, 1175]):
        place(out, st(_blip(f, 1.2, r, fm=0.9, decay=0.45) * 0.4, -0.3 + 0.3 * k), 0.09 * k)
    place(out, st(_blip(1480, 1.2, r, fm=0.9, decay=0.5) * 0.35), 0.3)
    place(out, st(onset(kick(seed, f_hi=120, f_lo=55, decay=0.15, click=0.1)) * 0.5), 0.3)
    return tailfade(out + reverb(out * 0.2, 'plate'), 0.3)


def ui_mission_fail(seed):
    r = rng(seed)
    out = np.zeros((int(1.8 * SR), 2))
    for k, f in enumerate([622, 523, 466]):
        place(out, st(_blip(f, 0.9, r, fm=0.4, shape=0.3, decay=0.35) * 0.4), 0.16 * k)
    t = T(1.2)
    dn = np.sin(2 * np.pi * np.cumsum(220 * (1 - 0.5 * t / 1.2)) / SR) * np.exp(-t / 0.5) * 0.3
    place(out, st(dn), 0.45)
    return tailfade(out + reverb(out * 0.15, 'plate'), 0.3)


# ===================================================================== character foley
def suit_move(seed):
    r = rng(seed)
    dur = r.uniform(0.4, 0.7)
    t = T(dur)
    n = t.shape[0]
    am = np.abs(sos_filter(r.standard_normal(n), 'lowpass', 30, 2)) * 8
    am = np.clip(am, 0, 1.5)
    x = bp(r.standard_normal(n), r.uniform(1800, 3200), 0.15) * am
    x += bp(r.standard_normal(n), 600, 0.2) * am * 0.4
    env = np.sin(np.pi * t / dur) ** 0.8
    return tailfade(onset(x * env * 0.5, 2), 0.3)


def equipment(seed):
    r = rng(seed)
    dur = 0.6
    out = np.zeros(int(dur * SR))
    for k in range(int(r.uniform(3, 7))):
        h = metal_hit(seed + k, f0=r.uniform(1200, 3200), decay=0.015, length=0.08, bright=1.0)
        place(out, onset(h) * r.uniform(0.3, 0.9), r.uniform(0.0, 0.4))
    out += suit_move(seed + 100)[: out.shape[0]].copy() * 0.4 if suit_move(seed + 100).shape[0] >= out.shape[0] else np.pad(suit_move(seed + 100), (0, out.shape[0] - suit_move(seed + 100).shape[0])) * 0.4
    return tailfade(out, 0.2)


def weapon_handle(seed):
    r = rng(seed)
    dur = 0.7
    out = np.zeros(int(dur * SR))
    sm = suit_move(seed + 3)
    place(out, sm * 0.6, 0.0)
    place(out, onset(metal_hit(seed, f0=r.uniform(700, 1100), decay=0.025, length=0.12)) * 1.0, r.uniform(0.15, 0.3))
    place(out, onset(kick(seed, f_hi=180, f_lo=90, sweep=0.01, decay=0.03, click=0.3)) * 0.35, 0.3)
    place(out, onset(tick(seed, f=2800, decay=0.003)) * 0.5, 0.42)
    return tailfade(out, 0.2)


def servo(seed):
    r = rng(seed)
    dur = r.uniform(0.3, 0.55)
    t = T(dur)
    x = t / dur
    up = seed % 2 == 0
    f = 220 + 380 * (x if up else 1 - x) + 30 * np.sin(2 * np.pi * 9 * t)
    s = saw(f, SR, 0.0) * 0.5 + square(f * 2, 0.3, SR, 0.0) * 0.2
    s = bp(s, 1400, 0.3)
    gear = bp(r.standard_normal(t.shape[0]), 3500, 0.5) * (0.5 + 0.5 * np.sign(np.sin(2 * np.pi * f * 0.25 * t))) * 0.15
    env = np.minimum(t / 0.02, 1) * np.minimum((dur - t) / 0.04, 1)
    m = (s + gear) * env
    place(m, onset(tick(seed, f=2400, decay=0.004)) * 0.3, dur - 0.03) if False else None
    return tailfade(onset(m, 1), 0.15)


# ===================================================================== ambience loops (stereo, seamless)
def _amb(fn, sec, xf=3.0):
    return circular(fn, int(sec * SR), xf_sec=xf)


def _events_wrapped(n, events):
    """events: list of (t_sec, stereo array). Wrap tails around the loop end."""
    buf = np.zeros((n + int(6 * SR), 2))
    for tt, a in events:
        place(buf, a, tt)
    out = buf[:n].copy()
    out[: buf.shape[0] - n] += buf[n:]
    return out


def amb_server_room(seed, sec=48.0):
    r = rng(seed)
    n = int(sec * SR)
    def bed(m):
        rr = rng(seed + 1)
        t = np.arange(m) / SR
        fanL = lp(rr.standard_normal(m), 3500) * 0.25 + bp(rr.standard_normal(m), 450, 0.2) * 0.3
        fanR = lp(rr.standard_normal(m), 3300) * 0.25 + bp(rr.standard_normal(m), 470, 0.2) * 0.3
        hum = sum(a * np.sin(2 * np.pi * 60 * k * t + k) for k, a in [(1, 0.05), (2, 0.03), (3, 0.02), (6, 0.01)])
        whine = np.sin(2 * np.pi * 7480 * t) * 0.004 + np.sin(2 * np.pi * 11200 * t) * 0.002
        swell = 1 + 0.15 * np.sin(2 * np.pi * t / 12.0)
        return np.stack([(fanL + hum + whine) * swell, (fanR + hum + whine) * swell], 1)
    base = _amb(bed, sec)
    ev = []
    for _ in range(int(sec * 2.5)):
        ev.append((r.uniform(0, sec), st(tick(r.integers(1e6), f=r.uniform(2500, 5000), decay=0.003) * r.uniform(0.03, 0.1), r.uniform(-0.9, 0.9))))
    for _ in range(int(sec / 6)):
        ev.append((r.uniform(0, sec), st(onset(metal_hit(r.integers(1e6), f0=r.uniform(1500, 2500), decay=0.01, length=0.06)) * 0.12, r.uniform(-0.8, 0.8))))
    return base + _events_wrapped(n, ev)


def amb_industrial(seed, sec=48.0):
    r = rng(seed)
    n = int(sec * SR)
    def bed(m):
        rr = rng(seed + 1)
        t = np.arange(m) / SR
        rum = lp(rr.standard_normal((m, 2)).T, 120).T * 0.5 if False else np.stack([lp(rr.standard_normal(m), 120), lp(rr.standard_normal(m), 130)], 1) * 0.5
        whine = np.sin(2 * np.pi * 1180 * t + 0.4 * np.sin(2 * np.pi * 0.2 * t)) * 0.01
        return rum + st(whine)
    base = _amb(bed, sec)
    ev = []
    period = 1.6
    for k in range(int(sec / period)):
        tt = k * period
        ev.append((tt, st(onset(kick(int(k), f_hi=90, f_lo=40, decay=0.2, click=0.05, drive=1.2)) * 0.35, -0.3)))
        ev.append((tt + 0.05, st(onset(metal_hit(int(k) + 50, f0=180, decay=0.15, length=0.8)) * 0.15, -0.3)))
    for _ in range(int(sec / 5)):
        L = r.uniform(0.6, 1.5)
        t = T(L)
        h = hp(r.standard_normal(t.shape[0]), 2500) * np.sin(np.pi * t / L) * 0.12
        ev.append((r.uniform(0, sec), st(h, r.uniform(-0.8, 0.8))))
    for _ in range(int(sec / 4)):
        ev.append((r.uniform(0, sec), st(onset(anvil(int(r.integers(1e6)), f0=r.uniform(300, 900))) * 0.08, r.uniform(-1, 1))))
    out = base + _events_wrapped(n, ev)
    return out + 0 * out


def amb_electrical_hum(seed, sec=40.0):
    def bed(m):
        rr = rng(seed)
        t = np.arange(m) / SR
        h = np.zeros(m)
        for k, a in [(1, 1.0), (2, 0.8), (3, 0.5), (4, 0.4), (5, 0.25), (6, 0.2), (8, 0.1), (10, 0.06)]:
            h += a * np.sin(2 * np.pi * 50 * k * t + k * 0.7)
        h *= 1 + 0.08 * np.sin(2 * np.pi * 0.11 * t)
        buzz = hp(softclip(np.sin(2 * np.pi * 100 * t) * 4, 1.0), 800) * 0.05
        cr = crackle(rr, m / SR, 30, 6000, 0.4) * 0.15
        L = h * 0.08 + buzz + cr
        R = h * 0.078 + buzz * 0.9 + np.roll(cr, 977)
        return np.stack([L, R], 1)
    return _amb(bed, sec)


def amb_reactor(seed, sec=48.0):
    def bed(m):
        rr = rng(seed)
        t = np.arange(m) / SR
        throb = np.sin(2 * np.pi * 31 * t) * (0.6 + 0.4 * np.sin(2 * np.pi * 0.5 * t)) * 0.35
        throb += np.sin(2 * np.pi * 62 * t) * 0.12 * (0.6 + 0.4 * np.sin(2 * np.pi * 0.5 * t + 0.5))
        flowL = bp(rr.standard_normal(m), 700, 0.15) * 0.25
        flowR = bp(rr.standard_normal(m), 760, 0.15) * 0.25
        whine = np.sin(2 * np.pi * (880 + 20 * np.sin(2 * np.pi * 0.25 * t)) * t) * 0.012 * (0.5 + 0.5 * np.sin(2 * np.pi * 0.25 * t))
        return np.stack([throb + flowL + whine, throb + flowR + whine], 1)
    return _amb(bed, sec)


def amb_laboratory(seed, sec=48.0):
    r = rng(seed)
    n = int(sec * SR)
    def bed(m):
        rr = rng(seed + 1)
        t = np.arange(m) / SR
        vent = np.stack([lp(rr.standard_normal(m), 2500), lp(rr.standard_normal(m), 2400)], 1) * 0.12
        cent = np.sin(2 * np.pi * 240 * t) * 0.015 + np.sin(2 * np.pi * 480 * t) * 0.008
        return vent + st(cent, 0.4)
    base = _amb(bed, sec)
    ev = []
    for _ in range(int(sec * 1.5)):
        L = int(r.uniform(0.02, 0.05) * SR)
        tb = np.arange(L) / SR
        f0 = r.uniform(400, 1200)
        bub = np.sin(2 * np.pi * np.cumsum(f0 * (1 + 2 * tb / tb[-1])) / SR) * np.sin(np.pi * tb / tb[-1]) * 0.05
        ev.append((r.uniform(0, sec), st(bub, r.uniform(-0.5, 0.5))))
    for k in range(int(sec / 8)):
        b = _blip(r.choice([1568, 2093, 2637]), 0.25, r, fm=0.3, decay=0.08) * 0.06
        ev.append((r.uniform(0, sec), st(b, r.uniform(-0.9, 0.9))))
    return base + _events_wrapped(n, ev)


def amb_surveillance_city(seed, sec=56.0):
    r = rng(seed)
    n = int(sec * SR)
    def bed(m):
        rr = rng(seed + 1)
        t = np.arange(m) / SR
        city = np.stack([lp(rr.standard_normal(m), 250), lp(rr.standard_normal(m), 260)], 1) * 0.5
        wind = np.stack([bp(rr.standard_normal(m), 600 + 300 * np.sin(2 * np.pi * 0.05 * t), 0.2), bp(rr.standard_normal(m), 650 + 300 * np.sin(2 * np.pi * 0.05 * t + 1), 0.2)], 1) * 0.08
        return city + wind
    base = _amb(bed, sec)
    ev = []
    for k in range(int(sec / 10)):
        L = r.uniform(3, 5)
        t = T(L)
        f = 180 * (1 + 0.06 * np.tanh((t - L / 2) * 2) * -1)
        dr = (np.sin(2 * np.pi * np.cumsum(f) / SR) + 0.4 * np.sin(4 * np.pi * np.cumsum(f) / SR)) * np.sin(np.pi * t / L) ** 2 * 0.05
        dr += bp(r.standard_normal(t.shape[0]), 1500, 0.3) * np.sin(np.pi * t / L) ** 2 * 0.03
        p = np.linspace(-0.9, 0.9, t.shape[0]) * (1 if k % 2 else -1)
        s2 = np.stack([dr * np.cos((p + 1) * np.pi / 4), dr * np.sin((p + 1) * np.pi / 4)], 1)
        ev.append((r.uniform(0, sec), s2))
    for k in range(int(sec / 7)):
        t = T(0.6)
        sc, _ = chirp(1800, 3200, 0.6, shape='lin')
        ev.append((r.uniform(0, sec), st(sc * np.sin(np.pi * t / 0.6) * 0.03, r.uniform(-0.8, 0.8))))
    for k in range(int(sec / 14)):
        b = (_blip(784, 0.6, r, decay=0.3) + _blip(988, 0.6, r, decay=0.3)) * 0.03
        ev.append((r.uniform(0, sec), st(b, r.uniform(-0.3, 0.3)) + reverb(st(b) * 0.5, 'hall')[: b.shape[0]] * 0))
    return base + _events_wrapped(n, ev)


def amb_temporal(seed, sec=48.0):
    r = rng(seed)
    n = int(sec * SR)
    def bed(m):
        rr = rng(seed + 1)
        t = np.arange(m) / SR
        L = np.zeros(m)
        R = np.zeros(m)
        for k, f in enumerate([146.8, 220.0, 293.7, 349.2, 440.0, 587.3]):
            am = 0.5 + 0.5 * np.sin(2 * np.pi * (0.03 + 0.017 * k) * t + k)
            L += np.sin(2 * np.pi * f * 1.0007 * t) * am * 0.03 / (1 + 0.3 * k)
            R += np.sin(2 * np.pi * f * 0.9993 * t + 1) * am * 0.03 / (1 + 0.3 * k)
        sub = np.sin(2 * np.pi * 36.7 * t) * 0.12 * (0.7 + 0.3 * np.sin(2 * np.pi * 0.125 * t))
        sh = np.stack([bp(rr.standard_normal(m), 6000, 0.6), bp(rr.standard_normal(m), 6400, 0.6)], 1) * 0.02
        return np.stack([L + sub, R + sub], 1) + sh
    base = _amb(bed, sec)
    ev = []
    for _ in range(int(sec * 0.8)):
        g = bitcrush(r.standard_normal(int(r.uniform(0.02, 0.06) * SR)) * 0.05, 4, int(r.choice([6, 12, 24])))
        g = bp(g, r.uniform(1500, 5000), 0.4)
        ev.append((r.uniform(0, sec), st(onset(g), r.uniform(-1, 1))))
    for k in range(int(sec / 8)):
        ev.append((k * 8.0, st(reverse_swell(50, length=2.0, seed=k) * 0.15)))
    return base + _events_wrapped(n, ev)


# ===================================================================== additions for the asset contract
def secondary_blast(seed):
    """Chain-reaction blast: a component detonating near the main destruction (smaller than the Breach Charge)."""
    r = rng(seed)
    dur = 2.2
    t = T(dur)
    n = t.shape[0]
    crack = burst(r, dur, 1200, 16000, 0.006) * 1.2
    body = boom(seed, f0=r.uniform(48, 60), decay=0.45, length=dur, noise=0.6, drive=2.2)[:n]
    crunch = softclip(bp(r.standard_normal(n), r.uniform(800, 1300), 0.12) * 3, 1.0) * np.exp(-t / 0.15) * 0.5
    fire = lp(r.standard_normal(n), 1800 * np.exp(-t / 0.4) + 250) * np.minimum(t / 0.02, 1) * np.exp(-t / 0.5) * 0.4
    s = st(crack + body + crunch + fire, r.uniform(-0.3, 0.3))
    s += grains(r, dur, 30, 600, 6000, 0.008, 0.04, dist=1.3, amp_decay=0.3) * 0.5
    s = widen(s + reverb(s * 0.2, 'chamber'), 1.2)
    return tailfade(onset(softclip(s, 1.1), 0.3), 0.4)


def _periodic(cycle_fn, n_cycle, room='room', wet=0.25):
    """Render a periodic one-cycle loop: 3 cycles through reverb, keep the middle one."""
    x = np.concatenate([cycle_fn(), cycle_fn(), cycle_fn()], 0)
    y = x + reverb(x * wet, room)[: x.shape[0]]
    return y[n_cycle: 2 * n_cycle]


def _int_phase(f):
    """Scale an instantaneous-frequency curve so it holds a whole number of cycles (phase-continuous at the wrap)."""
    tot = f.sum() / SR
    return 2 * np.pi * np.cumsum(f * (max(1, round(tot)) / tot)) / SR


def alarm(seed, style=1):
    """Facility alarm, seamless loop. style 1: two-tone klaxon, 2: rising siren, 3: digital triple pulse."""
    r = rng(seed)
    L = {1: 2.0, 2: 1.6, 3: 1.2}[style]
    n = int(L * SR)
    t = np.arange(n) / SR
    def cyc():
        if style == 1:
            f = np.where(t < L / 2, 740.0, 587.3)
            ph = _int_phase(f)
            w = np.tanh(2.5 * np.sin(ph)) + 0.3 * np.sin(3 * ph)
            g = np.minimum(1, np.minimum(np.abs(t - L / 2), np.minimum(t, L - t)) / 0.006)
            x = bp(np.tile(w * g, 3), 1400, 0.4)[n: 2 * n] * 0.7 + w * g * 0.3
        elif style == 2:
            f = 480 + 640 * (t / L) ** 0.7
            ph = _int_phase(f)
            w = np.sin(ph) + 0.35 * np.sin(2 * ph) + 0.2 * np.sin(3 * ph)
            env = np.minimum(1, t / 0.05) * np.minimum(1, (L - t) / 0.12)
            x = w * (0.35 + 0.65 * env)
        else:
            x = np.zeros(n)
            for k in range(3):
                t0 = 0.2 * k
                m = (t >= t0) & (t < t0 + 0.09)
                tb = t[m] - t0
                e = np.minimum(1, tb / 0.004) * np.minimum(1, (0.09 - tb) / 0.006)
                x[m] = (np.sin(2 * np.pi * 1200 * tb) + 0.3 * np.sign(np.sin(2 * np.pi * 1200 * tb)) * 0.5) * e
        return np.stack([x, x], 1)
    y = _periodic(cyc, n, 'room', 0.3)
    return y


def objective_complete(seed):
    """Objective cleared: quick rising triad with a soft low thump and shimmer (stereo, about 1.3 s)."""
    r = rng(seed)
    out = np.zeros((int(1.4 * SR), 2))
    for k, (f, p) in enumerate([(587.3, -0.3), (880.0, 0.0), (1174.7, 0.3)]):
        b = _blip(f, 0.9, r, fm=0.25, decay=0.22) * (0.5 - 0.06 * k)
        place(out, st(b, p), 0.07 * k)
    place(out, st(np.sin(2 * np.pi * 98 * T(0.5)) * np.exp(-T(0.5) / 0.12) * 0.35), 0.0)
    sh = hp(r.standard_normal(out.shape[0]), 7000) * np.exp(-T(1.4) / 0.35) * np.minimum(T(1.4) / 0.1, 1) * 0.04
    out += np.stack([sh, np.roll(sh, 331)], 1)
    out = out + reverb(out * 0.25, 'plate')[: out.shape[0]]
    return tailfade(onset(out, 0.5), 0.35)
