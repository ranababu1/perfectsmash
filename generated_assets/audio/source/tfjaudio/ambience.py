"""Chapter ambience beds: 4 bands per chapter (asset contract section 19). Every bed is a seamless
stereo loop built from synthesis layers (no recordings). Continuous layers are rendered with a
circular cross-fade; discrete events wrap their tails across the loop point."""
import numpy as np
from .dsp import SR, rng, lp, hp, bp, softclip, bitcrush, reverb, widen
from .drums import tick, metal_hit, anvil, kick, reverse_swell, modal
from .song import circular
from . import sfx as S

st = S.st
onset = S.onset
T = S.T


def bed(fn, n, xf=3.0):
    return circular(fn, n, xf_sec=xf)


def wrap(n, events, room=None, wet=0.0):
    out = S._events_wrapped(n, events)
    if room:
        # periodic reverb: tile 3x, keep the middle
        x = np.concatenate([out, out, out], 0)
        y = reverb(x * wet, room)[: x.shape[0]]
        out = out + y[n: 2 * n]
    return out


def noise2(rr, m, fc, kind='lp', q=0.3, amp=1.0, decor=True):
    f = {'lp': lambda x: lp(x, fc), 'hp': lambda x: hp(x, fc), 'bp': lambda x: bp(x, fc, q)}[kind]
    a = f(rr.standard_normal(m))
    b = f(rr.standard_normal(m)) if decor else a
    return np.stack([a, b], 1) * amp


def tone(t, f, amp, detune=0.0006, phase=0.0):
    return np.stack([np.sin(2 * np.pi * f * (1 + detune) * t + phase), np.sin(2 * np.pi * f * (1 - detune) * t + phase + 1.0)], 1) * amp


# ------------------------------------------------------------------ event builders
def ev_ticks(r, sec, rate, f_lo, f_hi, amp):
    return [(r.uniform(0, sec), st(tick(int(r.integers(1e6)), f=r.uniform(f_lo, f_hi), decay=0.003) * r.uniform(0.3, 1) * amp, r.uniform(-0.9, 0.9))) for _ in range(int(sec * rate))]


def ev_relays(r, sec, every, amp):
    return [(r.uniform(0, sec), st(onset(metal_hit(int(r.integers(1e6)), f0=r.uniform(1400, 2600), decay=0.01, length=0.06)) * amp, r.uniform(-0.8, 0.8))) for _ in range(int(sec / every))]


def ev_beeps(r, sec, every, freqs, amp, dur=0.25):
    return [(r.uniform(0, sec), st(S._blip(r.choice(freqs), dur, r, fm=0.3, decay=dur / 3) * amp, r.uniform(-0.9, 0.9))) for _ in range(int(sec / every))]


def ev_bubbles(r, sec, rate, f_lo, f_hi, amp, spread=0.6):
    ev = []
    for _ in range(int(sec * rate)):
        L = int(r.uniform(0.02, 0.06) * SR)
        tb = np.arange(L) / SR
        f0 = r.uniform(f_lo, f_hi)
        b = np.sin(2 * np.pi * np.cumsum(f0 * (1 + 2.2 * tb / tb[-1])) / SR) * np.sin(np.pi * tb / tb[-1]) * amp * r.uniform(0.4, 1)
        ev.append((r.uniform(0, sec), st(b, r.uniform(-spread, spread))))
    return ev


def ev_drips(r, sec, every, f_lo, f_hi, amp):
    ev = []
    for _ in range(int(sec / every)):
        L = int(0.12 * SR)
        tb = np.arange(L) / SR
        f0 = r.uniform(f_lo, f_hi)
        d = np.sin(2 * np.pi * np.cumsum(f0 * (1 + 0.8 * np.exp(-tb / 0.01))) / SR) * np.exp(-tb / 0.025) * np.minimum(tb / 0.001, 1)
        ev.append((r.uniform(0, sec), st(d * amp * r.uniform(0.4, 1), r.uniform(-0.9, 0.9))))
    return ev


def ev_hiss(r, sec, every, fc, amp, lo=0.6, hi=1.6):
    ev = []
    for _ in range(int(sec / every)):
        L = r.uniform(lo, hi)
        t = T(L)
        h = hp(r.standard_normal(t.shape[0]), fc) * np.sin(np.pi * t / L) ** 0.7 * amp
        ev.append((r.uniform(0, sec), st(h, r.uniform(-0.8, 0.8))))
    return ev


def ev_clunks(r, sec, every, amp, f_lo=150, f_hi=500):
    ev = []
    for _ in range(int(sec / every)):
        k = int(r.integers(1e6))
        p = r.uniform(-0.7, 0.7)
        c = _mix(st(onset(kick(k, f_hi=110, f_lo=50, decay=0.12, click=0.15, drive=1.3)) * 0.6, p),
                 st(onset(metal_hit(k, f0=r.uniform(f_lo, f_hi), decay=0.25, length=0.8)) * 0.4, p))
        ev.append((r.uniform(0, sec), c * amp))
    return ev


def ev_flybys(r, sec, every, amp, f0=180):
    ev = []
    for k in range(int(sec / every)):
        L = r.uniform(3, 5)
        t = T(L)
        f = f0 * r.uniform(0.8, 1.25) * (1 - 0.06 * np.tanh((t - L / 2) * 2))
        ph = 2 * np.pi * np.cumsum(f) / SR
        dr = (np.sin(ph) + 0.4 * np.sin(2 * ph)) * np.sin(np.pi * t / L) ** 2 * 0.6
        dr += bp(r.standard_normal(t.shape[0]), 1500, 0.3) * np.sin(np.pi * t / L) ** 2 * 0.35
        p = np.linspace(-0.9, 0.9, t.shape[0]) * (1 if k % 2 else -1)
        ev.append((r.uniform(0, sec), np.stack([dr * np.cos((p + 1) * np.pi / 4), dr * np.sin((p + 1) * np.pi / 4)], 1) * amp))
    return ev


def ev_scanners(r, sec, every, amp):
    ev = []
    for _ in range(int(sec / every)):
        t = T(0.6)
        sc, _ = S.chirp(r.uniform(1500, 2000), r.uniform(2800, 3400), 0.6, shape='lin')
        ev.append((r.uniform(0, sec), st(sc * np.sin(np.pi * t / 0.6) * amp, r.uniform(-0.8, 0.8))))
    return ev


def ev_pa(r, sec, every, amp, notes=(784, 988, 1175)):
    ev = []
    for _ in range(max(1, int(sec / every))):
        b = np.zeros((int(2.0 * SR), 2))
        for i, f in enumerate(notes):
            S.place(b, st(S._blip(f, 0.8, r, decay=0.35)), 0.28 * i)
        ev.append((r.uniform(0, sec), b * amp))
    return ev


def ev_glitches(r, sec, rate, amp):
    ev = []
    for _ in range(int(sec * rate)):
        g = bitcrush(r.standard_normal(int(r.uniform(0.02, 0.06) * SR)) * 1.0, 4, int(r.choice([6, 12, 24])))
        g = bp(g, r.uniform(1500, 5000), 0.4)
        ev.append((r.uniform(0, sec), st(onset(g) * amp, r.uniform(-1, 1))))
    return ev


def ev_creaks(r, sec, every, amp):
    ev = []
    for _ in range(int(sec / every)):
        x = S.metal_bend(int(r.integers(1e6)))
        x = x.mean(1) if x.ndim == 2 else x
        ev.append((r.uniform(0, sec), st(lp(x, 2500), r.uniform(-0.8, 0.8)) * amp))
    return ev


def ev_servos(r, sec, every, amp):
    ev = []
    for _ in range(int(sec / every)):
        x = S.servo(int(r.integers(1e6)))
        x = x if x.ndim == 2 else st(x)
        ev.append((r.uniform(0, sec), x * amp))
    return ev


def periodic_events(sec, period, make, offset=0.0):
    return [(offset + k * period, make(k)) for k in range(int(round(sec / period)))]


# ------------------------------------------------------------------ Helix Systems
def hlx_server_hall(seed, sec=48.0):
    return S.amb_server_room(seed, sec)


def hlx_logistics(seed, sec=48.0):
    r = rng(seed)
    n = int(sec * SR)
    def f(m):
        rr = rng(seed + 1)
        t = np.arange(m) / SR
        rum = noise2(rr, m, 160, amp=0.45)
        roll = noise2(rr, m, 900, 'bp', 0.25, amp=0.08) * (1 + 0.3 * np.sin(2 * np.pi * 2.0 * t))[:, None]
        motor = tone(t, 120, 0.02) + tone(t, 240, 0.01)
        return rum + roll + motor
    b = bed(f, n)
    ev = []
    # conveyor roller joints: a clack every 0.75 s, alternating sides, slight level drift
    ev += periodic_events(sec, 0.75, lambda k: st(onset(metal_hit(k % 7 + 3, f0=320 + 30 * (k % 3), decay=0.04, length=0.2)) * (0.07 + 0.02 * np.sin(k)), -0.4 + 0.15 * (k % 2)))
    ev += ev_clunks(r, sec, 6.0, 0.2)
    ev += ev_servos(r, sec, 5.0, 0.12)
    # distant reversing beeper (1 kHz, 0.5 s on / 0.5 s off) twice per loop
    for _ in range(2):
        t0 = r.uniform(0, sec)
        for k in range(6):
            tb = T(0.45)
            ev.append((t0 + k, st(lp(np.sin(2 * np.pi * 1030 * tb) * np.minimum(1, np.minimum(tb, 0.45 - tb) / 0.01), 2500) * 0.02, 0.6)))
    return b + wrap(n, ev, 'hall', 0.25)


def hlx_cooling(seed, sec=48.0):
    r = rng(seed)
    n = int(sec * SR)
    def f(m):
        rr = rng(seed + 1)
        t = np.arange(m) / SR
        fan = noise2(rr, m, 1600, amp=0.2) + noise2(rr, m, 110, 'bp', 0.35, amp=0.6)
        blade = (1 + 0.12 * np.sin(2 * np.pi * 14.5 * t))[:, None]
        water = noise2(rr, m, 3000, 'bp', 0.2, amp=0.07) * (1 + 0.2 * np.sin(2 * np.pi * 0.09 * t))[:, None]
        comp = tone(t, 40, 0.06) + tone(t, 80, 0.03)
        cyc = (0.6 + 0.4 * np.clip(np.sin(2 * np.pi * t / sec * 2), 0, 1))[:, None]
        return fan * blade + water + comp * cyc
    b = bed(f, n)
    ev = ev_drips(r, sec, 1.2, 900, 2200, 0.05) + ev_ticks(r, sec, 0.6, 1800, 3000, 0.05)
    return b + wrap(n, ev, 'chamber', 0.3)


def hlx_core(seed, sec=48.0):
    r = rng(seed)
    n = int(sec * SR)
    srv = S.amb_server_room(seed + 3, sec) * 0.55
    def f(m):
        t = np.arange(m) / SR
        drone = tone(t, 36.7, 0.12) + tone(t, 73.4, 0.05) + tone(t, 110.0, 0.02)
        breath = (0.65 + 0.35 * np.sin(2 * np.pi * t / 8.0) ** 2)[:, None]
        shimmer = tone(t, 1174.7, 0.004, 0.002) + tone(t, 1760, 0.003, 0.003)
        return drone * breath + shimmer * breath
    b = bed(f, n)
    ev = []
    # data chatter: short bit-crushed blips in bursts
    for _ in range(int(sec / 3)):
        t0 = r.uniform(0, sec)
        for k in range(int(r.integers(3, 9))):
            g = bitcrush(np.sin(2 * np.pi * r.choice([880, 1320, 1760, 2640]) * T(0.03)) * 0.5, 6, 8)
            ev.append((t0 + 0.04 * k, st(onset(g) * 0.05, r.uniform(-0.9, 0.9))))
    return srv + b + wrap(n, ev, 'hall', 0.3)


# ------------------------------------------------------------------ VITA Genomics
def vta_cleanroom(seed, sec=48.0):
    r = rng(seed)
    n = int(sec * SR)
    def f(m):
        rr = rng(seed + 1)
        t = np.arange(m) / SR
        vent = noise2(rr, m, 5000, amp=0.09) + noise2(rr, m, 300, 'bp', 0.3, amp=0.12)
        hepa = tone(t, 180, 0.01) + tone(t, 360, 0.005)
        return vent + hepa
    b = bed(f, n)
    ev = ev_hiss(r, sec, 9.0, 3500, 0.12, 1.5, 3.0) + ev_beeps(r, sec, 7.0, [1568, 2093, 2637], 0.05) + ev_ticks(r, sec, 0.3, 2500, 4000, 0.05)
    # pneumatic door seal: low thunk + short hiss
    for _ in range(2):
        t0 = r.uniform(0, sec)
        ev.append((t0, st(onset(kick(int(t0 * 10), f_hi=90, f_lo=45, decay=0.1, click=0.05)) * 0.15, -0.5)))
        ev += [(t0 + 0.05, x) for _, x in ev_hiss(r, 1.0, 1.0, 2000, 0.1, 0.5, 0.8)]
    return b + wrap(n, ev, 'room', 0.3)


def vta_bioreactor(seed, sec=48.0):
    r = rng(seed)
    n = int(sec * SR)
    def f(m):
        rr = rng(seed + 1)
        t = np.arange(m) / SR
        flow = noise2(rr, m, 600, 'bp', 0.2, amp=0.15) * (1 + 0.25 * np.sin(2 * np.pi * 0.2 * t))[:, None]
        hum = tone(t, 60, 0.04) + tone(t, 120, 0.02)
        return flow + hum + noise2(rr, m, 150, amp=0.2)
    b = bed(f, n)
    ev = ev_bubbles(r, sec, 6.0, 150, 600, 0.09) + ev_bubbles(r, sec, 2.0, 600, 1300, 0.05)
    # pump stroke every 2.4 s: soft thump plus liquid swish
    def stroke(k):
        tb = T(0.9)
        sw = bp(rng(k).standard_normal(tb.shape[0]), 500 + 600 * tb, 0.3) * np.sin(np.pi * tb / 0.9) * 0.15
        return _mix(st(onset(kick(k, f_hi=80, f_lo=40, decay=0.15, click=0.02)) * 0.2), st(sw, 0.2))
    ev += periodic_events(sec, 2.4, stroke)
    return b + wrap(n, ev, 'chamber', 0.3)


def _mix(a, b):
    m = max(a.shape[0], b.shape[0])
    out = np.zeros((m, 2))
    out[: a.shape[0]] += a
    out[: b.shape[0]] += b
    return out


def vta_archive(seed, sec=48.0):
    r = rng(seed)
    n = int(sec * SR)
    def f(m):
        rr = rng(seed + 1)
        t = np.arange(m) / SR
        cold = tone(t, 50, 0.05) + tone(t, 100, 0.03) + tone(t, 150, 0.012)
        comp_cycle = (0.5 + 0.5 * np.clip(np.sin(2 * np.pi * t / (sec / 2)) * 3, 0, 1))[:, None]
        room = noise2(rr, m, 1200, amp=0.05)
        return cold * comp_cycle + room
    b = bed(f, n)
    ev = ev_clunks(r, sec, 16.0, 0.1, 400, 900) + ev_hiss(r, sec, 14.0, 4000, 0.1, 2.0, 3.5) + ev_ticks(r, sec, 0.4, 3000, 5000, 0.04)
    return b + wrap(n, ev, 'hall', 0.35)


def vta_growth(seed, sec=48.0):
    r = rng(seed)
    n = int(sec * SR)
    def f(m):
        rr = rng(seed + 1)
        t = np.arange(m) / SR
        breath = noise2(rr, m, 700, 'bp', 0.25, amp=0.18) * (0.3 + 0.7 * np.sin(np.pi * t / 6.0) ** 4)[:, None]
        glass = sum(tone(t, fq, 0.006, 0.001) * (0.5 + 0.5 * np.sin(2 * np.pi * (0.021 + 0.013 * i) * t + i))[:, None] for i, fq in enumerate([329.6, 493.9, 587.3, 740.0]))
        return breath + glass + noise2(rr, m, 200, amp=0.12)
    b = bed(f, n)
    ev = ev_bubbles(r, sec, 2.5, 300, 900, 0.05) + ev_drips(r, sec, 2.5, 1200, 2600, 0.04)
    return b + wrap(n, ev, 'hall', 0.35)


# ------------------------------------------------------------------ Nova Grid
def nvg_intake(seed, sec=48.0):
    r = rng(seed)
    n = int(sec * SR)
    def f(m):
        rr = rng(seed + 1)
        t = np.arange(m) / SR
        roar = noise2(rr, m, 700, amp=0.45) + noise2(rr, m, 2500, 'bp', 0.3, amp=0.08)
        gust = (1 + 0.2 * np.sin(2 * np.pi * 0.07 * t) + 0.1 * np.sin(2 * np.pi * 0.19 * t + 1))[:, None]
        turb = tone(t, 2210, 0.006) + tone(t, 4420, 0.002) + tone(t, 1105, 0.004)
        return roar * gust + turb
    b = bed(f, n)
    ev = []
    for _ in range(int(sec / 5)):
        t0 = r.uniform(0, sec)
        for k in range(int(r.integers(4, 10))):
            ev.append((t0 + 0.03 * k + r.uniform(0, 0.01), st(onset(metal_hit(int(r.integers(1e6)), f0=r.uniform(700, 1100), decay=0.02, length=0.1)) * 0.04, 0.5)))
    return b + wrap(n, ev, 'chamber', 0.2)


def nvg_cooling(seed, sec=48.0):
    r = rng(seed)
    n = int(sec * SR)
    def f(m):
        rr = rng(seed + 1)
        t = np.arange(m) / SR
        cascade = noise2(rr, m, 4000, amp=0.2) + noise2(rr, m, 1200, 'bp', 0.15, amp=0.25)
        fans = noise2(rr, m, 95, 'bp', 0.4, amp=0.5) * (1 + 0.1 * np.sin(2 * np.pi * 9.0 * t))[:, None]
        return cascade + fans
    b = bed(f, n)
    ev = ev_hiss(r, sec, 7.0, 2500, 0.15, 0.8, 1.8) + ev_drips(r, sec, 0.8, 700, 1800, 0.04)
    return b + wrap(n, ev, 'hall', 0.2)


def nvg_transformer(seed, sec=48.0):
    r = rng(seed)
    n = int(sec * SR)
    b = S.amb_electrical_hum(seed, sec)
    ev = []
    for _ in range(int(sec / 8)):
        x = S.electrical_short(int(r.integers(1e6)))
        x = x if x.ndim == 2 else st(x, r.uniform(-0.7, 0.7))
        ev.append((r.uniform(0, sec), x * 0.12))
    return b + wrap(n, ev, 'hall', 0.2)


def nvg_reactor(seed, sec=48.0):
    r = rng(seed)
    n = int(sec * SR)
    b = S.amb_reactor(seed, sec)
    ind = S.amb_industrial(seed + 7, sec)
    ind = np.stack([lp(ind[:, 0], 900), lp(ind[:, 1], 900)], 1) * 0.35   # distant presses
    ev = ev_ticks(r, sec, 0.5, 1500, 2500, 0.05)
    return b + ind + wrap(n, ev, 'hall', 0.3)


# ------------------------------------------------------------------ Civitas Network
def cvt_street(seed, sec=56.0):
    return S.amb_surveillance_city(seed, sec)


def cvt_plaza(seed, sec=56.0):
    r = rng(seed)
    n = int(sec * SR)
    def f(m):
        rr = rng(seed + 1)
        t = np.arange(m) / SR
        city = noise2(rr, m, 220, amp=0.35)
        wind = noise2(rr, m, 900, 'bp', 0.15, amp=0.06) * (1 + 0.3 * np.sin(2 * np.pi * 0.04 * t))[:, None]
        fountain = noise2(rr, m, 3500, 'bp', 0.3, amp=0.05)
        screens = tone(t, 900, 0.002) + tone(t, 1250, 0.0015)
        return city + wind + fountain + screens
    b = bed(f, n)
    ev = ev_flybys(r, sec, 9.0, 0.05, 220) + ev_scanners(r, sec, 5.0, 0.03) + ev_pa(r, sec, 18.0, 0.04)
    return b + wrap(n, ev, 'bighall', 0.25)


def cvt_control(seed, sec=48.0):
    r = rng(seed)
    n = int(sec * SR)
    def f(m):
        rr = rng(seed + 1)
        t = np.arange(m) / SR
        room = noise2(rr, m, 2200, amp=0.08) + noise2(rr, m, 400, 'bp', 0.25, amp=0.12)
        hum = tone(t, 60, 0.03) + tone(t, 180, 0.01)
        crt = tone(t, 10500, 0.0015, 0.0001)
        return room + hum + crt
    b = bed(f, n)
    ev = ev_relays(r, sec, 3.0, 0.1) + ev_beeps(r, sec, 4.0, [1318.5, 1760, 1975.5], 0.04, 0.15) + ev_ticks(r, sec, 2.0, 3000, 5500, 0.05)
    for _ in range(int(sec / 6)):
        t0 = r.uniform(0, sec)
        for k in range(int(r.integers(5, 12))):
            g = bitcrush(np.sin(2 * np.pi * r.choice([660, 990, 1320]) * T(0.025)) * 0.5, 6, 8)
            ev.append((t0 + 0.05 * k, st(onset(g) * 0.04, r.uniform(-0.9, 0.9))))
    return b + wrap(n, ev, 'room', 0.3)


def cvt_spire(seed, sec=56.0):
    r = rng(seed)
    n = int(sec * SR)
    def f(m):
        rr = rng(seed + 1)
        t = np.arange(m) / SR
        g = (1 + 0.45 * np.sin(2 * np.pi * 0.05 * t) + 0.25 * np.sin(2 * np.pi * 0.13 * t + 2))[:, None]
        wind = noise2(rr, m, 500, 'bp', 0.2, amp=0.2) * g + noise2(rr, m, 1800, 'bp', 0.5, amp=0.04) * g ** 2
        whistle = tone(t, 1450, 0.003) * (g - 0.7).clip(0)
        hum = tone(t, 60, 0.02)
        return wind + whistle + hum + noise2(rr, m, 120, amp=0.15)
    b = bed(f, n)
    ev = periodic_events(sec, 2.0, lambda k: st(S._blip(880, 0.4, rng(k), decay=0.12) * 0.025, 0.7))
    ev += ev_creaks(r, sec, 14.0, 0.15)
    return b + wrap(n, ev, 'bighall', 0.3)


# ------------------------------------------------------------------ Meridian
def mrd_excavation(seed, sec=48.0):
    r = rng(seed)
    n = int(sec * SR)
    def f(m):
        rr = rng(seed + 1)
        t = np.arange(m) / SR
        rum = noise2(rr, m, 90, amp=0.6) * (1 + 0.2 * np.sin(2 * np.pi * 0.06 * t))[:, None]
        return rum + noise2(rr, m, 1500, amp=0.03)
    b = bed(f, n)
    ev = ev_drips(r, sec, 2.0, 700, 1600, 0.04) + ev_clunks(r, sec, 9.0, 0.12)
    # distant drill runs
    for _ in range(3):
        L = r.uniform(2.5, 5.0)
        t = T(L)
        d = bp(r.standard_normal(t.shape[0]), 900, 0.3) * (0.6 + 0.4 * np.sign(np.sin(2 * np.pi * 26 * t))) * np.minimum(1, np.minimum(t, L - t) / 0.3) * 0.12
        ev.append((r.uniform(0, sec), st(lp(d, 2000), r.uniform(-0.6, 0.6))))
    # rubble trickles
    for _ in range(int(sec / 7)):
        g = S.grains(r, 1.5, 25, 600, 4000, 0.004, 0.02, dist=1.5, amp_decay=0.5)
        ev.append((r.uniform(0, sec), g * 0.06))
    return b + wrap(n, ev, 'bighall', 0.3)


def mrd_cavern(seed, sec=56.0):
    r = rng(seed)
    n = int(sec * SR)
    def f(m):
        rr = rng(seed + 1)
        t = np.arange(m) / SR
        drone = tone(t, 41.2, 0.08) + tone(t, 61.7, 0.03)
        air = noise2(rr, m, 400, 'bp', 0.2, amp=0.08) * (1 + 0.4 * np.sin(2 * np.pi * 0.03 * t))[:, None]
        return drone + air
    b = bed(f, n, 4.0)
    ev = ev_drips(r, sec, 1.6, 900, 2400, 0.06)
    for _ in range(3):
        x = S.boom(int(r.integers(1e6)), f0=r.uniform(32, 45), decay=1.5, length=3.0, noise=0.6, drive=1.4)
        ev.append((r.uniform(0, sec), st(lp(x, 300) * 0.08, r.uniform(-0.5, 0.5))))
    return b + wrap(n, ev, 'bighall', 0.5)


def mrd_anchor(seed, sec=48.0):
    r = rng(seed)
    n = int(sec * SR)
    tem = S.amb_temporal(seed, sec)
    def f(m):
        t = np.arange(m) / SR
        sub = tone(t, 29.1, 0.12) * (0.5 + 0.5 * np.sin(2 * np.pi * t / 4.0) ** 2)[:, None]
        bowed = sum(tone(t, fq, 0.008) * (0.5 + 0.5 * np.sin(2 * np.pi * (0.02 + 0.011 * i) * t + i))[:, None] for i, fq in enumerate([233.1, 349.2, 466.2, 587.3 * 1.003]))
        return sub + bowed
    b = bed(f, n)
    ev = [(r.uniform(0, sec), st(onset(metal_hit(int(r.integers(1e6)), f0=r.uniform(80, 160), decay=2.5, length=4.0)) * 0.06, r.uniform(-0.6, 0.6))) for _ in range(4)]
    return tem * 0.8 + b + wrap(n, ev, 'bighall', 0.4)


def mrd_convergence(seed, sec=56.0):
    r = rng(seed)
    n = int(sec * SR)
    def f(m):
        rr = rng(seed + 1)
        t = np.arange(m) / SR
        out = np.zeros((m, 2))
        for k, fq in enumerate([146.8, 155.6, 220.0, 293.7, 311.1, 440.0]):   # D minor with the Neapolitan Eb clashing in
            am = (0.5 + 0.5 * np.sin(2 * np.pi * (0.025 + 0.014 * k) * t + k))[:, None]
            out += tone(t, fq, 0.025 / (1 + 0.3 * k), 0.0009) * am
        out += tone(t, 36.7, 0.12) * (0.6 + 0.4 * np.sin(2 * np.pi * t / 7.0))[:, None]
        out += noise2(rr, m, 6000, 'bp', 0.6, amp=0.02)
        return out
    b = bed(f, n, 4.0)
    ev = ev_glitches(r, sec, 1.2, 0.05)
    ev += [(k * 7.0, st(reverse_swell(45, length=2.5, seed=k) * 0.15)) for k in range(int(sec / 7))]
    # echoes of earlier chapters: server ticks, bubbles, transformer buzz, PA chime
    ev += ev_ticks(r, sec, 0.8, 2500, 5000, 0.05) + ev_bubbles(r, sec, 0.5, 400, 1000, 0.04) + ev_pa(r, sec, 28.0, 0.02, (587, 740, 880))
    return b + wrap(n, ev, 'bighall', 0.4)


BANDS = {
    'helix': [('SERVER_HALL', hlx_server_hall, 48, 'Server hall: dense fan wash, 60 Hz hum, drive ticks and relay clicks'),
              ('LOGISTICS', hlx_logistics, 48, 'Automated logistics floor: conveyor roller clacks, motor hum, servo arms, clunks, distant reversing beeper'),
              ('COOLING', hlx_cooling, 48, 'Cooling plant: big fan rumble with blade flutter, chilled-water flow, compressor cycle, drips'),
              ('CORE', hlx_core, 48, 'AI core chamber: muted servers under a breathing low drone and bursts of data chatter')],
    'vita': [('CLEANROOM', vta_cleanroom, 48, 'Cleanroom: bright HEPA ventilation, air-shower bursts, door seals, soft instrument beeps'),
             ('BIOREACTOR', vta_bioreactor, 48, 'Bioreactor hall: heavy bubbling, pump strokes every 2.4 s, liquid flow and mains hum'),
             ('ARCHIVE', vta_archive, 48, 'Cold-storage archive: compressor hum cycling, freezer clunks, cryogenic venting hiss'),
             ('GROWTH', vta_growth, 48, 'Growth chambers: slow organic breathing swells, glassy tones, soft bubbles and drips')],
    'nova_grid': [('INTAKE', nvg_intake, 48, 'Air intake: turbine whine and gusting airflow roar with grille rattles'),
                  ('COOLING', nvg_cooling, 48, 'Cooling towers: water cascade, low fan drone, steam vents and drips'),
                  ('TRANSFORMER', nvg_transformer, 48, 'Transformer yard: 50 Hz hum and harmonics, buzz, crackle and occasional arcs'),
                  ('REACTOR', nvg_reactor, 48, 'Reactor hall: deep throb, coolant flow, pulsing whine, distant presses')],
    'civitas': [('STREET', cvt_street, 56, 'Surveillance street: distant city, wind, drone fly-bys, scanner sweeps, PA tones'),
                ('PLAZA', cvt_plaza, 56, 'Empty plaza: open city wash, fountain, wide drone passes, scanners, public-address chime'),
                ('CONTROL', cvt_control, 48, 'Surveillance control room: room tone, screen whine, relays, data blips and beeps'),
                ('SPIRE', cvt_spire, 56, 'Spire summit: gusting high wind, whistle, aviation beacon every 2 s, structural creaks')],
    'meridian': [('EXCAVATION', mrd_excavation, 48, 'Excavation tunnels: deep rumble, distant drilling, rubble trickles, clunks, drips'),
                 ('CAVERN', mrd_cavern, 56, 'Cavern: low drone, cave air, long-reverb drips, distant rock booms'),
                 ('ANCHOR', mrd_anchor, 48, 'Temporal anchor: shimmering detuned tones over a pulsing sub, bowed metal resonance'),
                 ('CONVERGENCE', mrd_convergence, 56, 'Convergence: clashing temporal chord, reverse swells, glitches and faint echoes of earlier chapters')],
}
