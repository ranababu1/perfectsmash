"""Arrangement, mixing and mastering engine."""
import numpy as np
import pyloudnorm as pyln
import pedalboard as pb
from .dsp import SR, reverb, delay_pp, tp_limit, true_peak_db, duck_curve, undb, pan_stereo, widen, fade, db

METER = pyln.Meter(SR)


def lufs(x):
    if x.shape[0] < int(0.5 * SR):
        x = np.concatenate([x, np.zeros((int(0.5 * SR) - x.shape[0], x.shape[1]))])
    v = METER.integrated_loudness(x)
    return float(v)


def circular(fn, n, xf_sec=2.0):
    """Render a texture of n samples that wraps seamlessly: fn(m) -> (m,2)."""
    xf = int(xf_sec * SR)
    x = fn(n + xf)
    out = x[:n].copy()
    w = np.sin(np.linspace(0, np.pi / 2, xf)) ** 2
    out[:xf] = x[:xf] * np.sqrt(w)[:, None] + x[n:n + xf] * np.sqrt(1 - w)[:, None]
    return out


class Track:
    def __init__(self, name, inst=None, gain_db=0.0, pan=0.0, width=1.0, sends=None, fx=None, duck=0.0, kw=None, level=None):
        self.name = name
        self.level = level
        self.auto = None
        self.inst = inst
        self.kw = kw or {}
        self.gain_db = gain_db
        self.pan = pan
        self.width = width
        self.sends = sends or {}
        self.fx = fx or []
        self.duck = duck
        self.notes = []   # (beat, dur_beats, midi, vel)
        self.hits = []    # (beat, array(mono or stereo), gain, pan)
        self.audio = []   # (beat, stereo array) not repeated per loop cycle specially


class Song:
    def __init__(self, sid, bpm, beats, loop=False, intro_beats=0.0, meta=None, tail=6.0):
        self.id = sid
        self.bpm = bpm
        self.beats = beats            # total beats (non-loop) or loop body length (loop)
        self.loop = loop
        self.intro_beats = intro_beats
        self.tracks = {}
        self.textures = []            # (track_name, fn(n)->stereo) for continuous circular beds (loop body)
        self.duck_hits = []           # beats of sidechain trigger
        self.meta = meta or {}
        self.tail = tail
        self.master_target = -16.0
        self.master_ceiling = -1.5
        self.master_comp = True
        self.delay_beats = 0.75

    def s(self, beats):
        return beats * 60.0 / self.bpm

    def track(self, name, inst=None, **kw):
        if name not in self.tracks:
            ik = kw.pop('kw', None)
            self.tracks[name] = Track(name, inst, kw=ik, **kw)
        return self.tracks[name]

    def notes(self, name, notes):
        self.tracks[name].notes.extend(notes)

    def hit(self, name, beat, arr, gain=1.0, pan=0.0):
        self.tracks[name].hits.append((beat, arr, gain, pan))

    def automate(self, name, points):
        """points: [(beat, dB)], linear in dB, periodic in loop mode."""
        self.tracks[name].auto = sorted(points)

    def mask(self, name, ranges):
        """Keep only notes/hits whose start beat lies inside one of the [a, b) ranges."""
        tr = self.tracks[name]
        ok = lambda b: any(a <= b < e for a, e in ranges)
        tr.notes = [x for x in tr.notes if ok(x[0])]
        tr.hits = [x for x in tr.hits if ok(x[0])]

    def _auto_curve(self, pts, n, nb=None):
        if self.loop:
            L = self.beats
            bx = [p[0] for p in pts]
            by = [p[1] for p in pts]
            bx = [bx[-1] - L] + bx + [bx[0] + L]
            by = [by[-1]] + by + [by[0]]
            t = (np.arange(nb) / SR) * self.bpm / 60.0
            c = np.interp(t, bx, by)
            c = np.concatenate([c, c, c[: n - 2 * nb]])
        else:
            t = (np.arange(n) / SR) * self.bpm / 60.0
            c = np.interp(t, [p[0] for p in pts], [p[1] for p in pts])
        return undb(c)

    def texture(self, name, fn):
        self.textures.append((name, fn))

    # ----------------------------------------------------------------- render
    def _render_raw(self, tr, n, tex=None):
        buf = np.zeros((n, 2))
        if tr.inst is not None and tr.notes:
            ev = [(self.s(b), self.s(d), m, v) for (b, d, m, v) in tr.notes if self.s(b) < n / SR]
            if ev:
                buf += tr.inst(ev, n, **tr.kw)
        for (b, arr, g, p) in tr.hits:
            i = int(round(self.s(b) * SR))
            if i >= n:
                continue
            a = arr if arr.ndim == 2 else pan_stereo(arr, p)
            e = min(n, i + a.shape[0])
            buf[i:e] += a[: e - i] * g
        if tex is not None:
            buf += tex[:n]
        return buf

    def _post(self, tr, buf):
        if tr.width != 1.0:
            buf = widen(buf, tr.width)
        if tr.pan:
            buf = buf * np.array([np.cos((tr.pan + 1) * np.pi / 4), np.sin((tr.pan + 1) * np.pi / 4)]) * np.sqrt(2)
        if tr.fx:
            board = pb.Pedalboard(tr.fx)
            buf = board(buf.T.astype(np.float32), SR, reset=True).T.astype(np.float64)
        return buf

    @staticmethod
    def fold(buf, nb):
        out = np.zeros((nb, buf.shape[1]))
        for s0 in range(0, buf.shape[0], nb):
            seg = buf[s0:s0 + nb]
            out[: seg.shape[0]] += seg
        return out

    def render(self):
        """Loop mode: every track is rendered once, folded onto the loop length (so release
        tails wrap into the loop start exactly) and tiled 2x + 4 s for the bus/master
        processing, so the extracted middle cycle is periodic by construction."""
        if self.loop:
            nb = int(round(self.s(self.beats) * SR))
            n_raw = nb + int(self.tail * SR) + int(4 * SR)
            n = 2 * nb + int(4 * SR)
        else:
            n = int((self.s(self.beats) + max(self.tail, 14.0)) * SR)
            n_raw = n
        tex_map = {}
        for (name, fn) in self.textures:
            t = circular(fn, nb) if self.loop else fn(n)
            tex_map[name] = tex_map.get(name, 0) + t

        def tile(x):
            return np.concatenate([x, x, x[: n - 2 * nb]], 0)

        dry = np.zeros((n, 2))
        buses = {}
        if self.loop:
            dh = [self.s(b) for b in self.duck_hits] + [self.s(b) + nb / SR for b in self.duck_hits]
            dh += [h - nb / SR for h in dh] + [h + 2 * nb / SR for h in dh]
        else:
            dh = [self.s(b) for b in self.duck_hits]
        self.track_report = {}
        for name, tr in self.tracks.items():
            tex = tex_map.get(name)
            if self.loop:
                raw = self._render_raw(tr, n_raw, None)
                raw = self.fold(raw, nb)
                if tex is not None:
                    raw = raw + tex
                if np.abs(raw).max() < 1e-7:
                    continue
                buf = tile(raw)
            else:
                buf = self._render_raw(tr, n_raw, tex)
                if np.abs(buf).max() < 1e-7:
                    continue
            buf = self._post(tr, buf)
            if tr.level is not None:
                seg = buf[nb:2 * nb] if self.loop else buf
                cur = lufs(seg)
                if cur > -100:
                    buf *= undb(tr.level - cur)
            buf *= undb(tr.gain_db)
            if tr.auto:
                buf *= self._auto_curve(tr.auto, n, nb if self.loop else None)[:, None]
            if tr.duck:
                buf *= duck_curve(n, dh, -abs(tr.duck), release=min(0.22, self.s(0.45)))[:, None]
            self.track_report[name] = round(lufs(buf[nb:2 * nb] if self.loop else buf), 1)
            dry += buf
            for bus, lvl in tr.sends.items():
                buses.setdefault(bus, np.zeros((n, 2)))
                buses[bus] += buf * undb(lvl)
        for name in tex_map:
            if name not in self.tracks:
                dry += tile(tex_map[name]) if self.loop else tex_map[name]
        wet = np.zeros((n, 2))
        for bus, x in buses.items():
            if bus == 'delay':
                y = delay_pp(x, self.s(self.delay_beats), fb=0.42, damp=0.35)
                y = reverb(y, 'chamber') * 0.35 + y
            else:
                y = reverb(x, bus)
            wet += y
        self.wet_db = round(lufs(wet[nb:2 * nb] if self.loop else wet), 1) if np.abs(wet).max() > 0 else None
        return dry + wet, n

    def master(self, mix):
        x = mix
        chain = [pb.HighpassFilter(26.0)]
        if self.master_comp:
            chain += [pb.Compressor(threshold_db=-20, ratio=1.7, attack_ms=30, release_ms=260)]
        x = pb.Pedalboard(chain)(x.T.astype(np.float32), SR).T.astype(np.float64)
        return x

    def finish(self, x, n):
        """Loudness normalise + true-peak limit. Returns final buffer and loop info."""
        if self.loop:
            nb = int(round(self.s(self.beats) * SR))
            region = (nb, 2 * nb)
        else:
            region = (0, x.shape[0])
        g = 0.0
        y = x
        for _ in range(4):
            seg = y[region[0]:region[1]]
            cur = lufs(seg)
            g += self.master_target - cur
            y = tp_limit(x * undb(g), self.master_ceiling)
            if abs(lufs(y[region[0]:region[1]]) - self.master_target) < 0.15:
                break
        self.master_gain_db = g
        return y, region


def trim_tail(x, thresh_db=-72.0, keep=0.05):
    a = np.abs(x).max(1)
    idx = np.where(a > undb(thresh_db))[0]
    if idx.size == 0:
        return x
    end = min(x.shape[0], idx[-1] + int(keep * SR))
    y = x[:end].copy()
    k = int(0.03 * SR)
    y[-k:] *= np.linspace(1, 0, k)[:, None]
    return y
