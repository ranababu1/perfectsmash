"""Chapter palettes: keys, tempi, progressions and signature sound layers.

All five chapters share the Temporal motif (theory.MOTIF), the 3+3+2 clock cell and the
i - bVI family of progressions; each chapter adds its own colour (see
docs/visual-audio-production-guide.md section 8).
"""
import numpy as np
import pedalboard as pb
from . import instruments as I
from . import drums as D
from .theory import (midi, MOTIF, ANSWER, HOPE, progression, pad_notes, bass_notes, arp_notes, grid,
                     motif_notes, clock_pattern)
from .dsp import SR, rng, hp, lp, bp, pan_stereo

CH = {
    'helix': dict(
        title='Helix Systems 2089', tonic='D', bpm=112, levels='1-20',
        mood='precise, cold, clinical tension; electronic pulse',
        A=[(0, 'madd9', 8), (8, 'M7', 8), (3, 'add9', 8), (10, 'sus2', 8)],
        B=[(0, 'm', 8), (8, 'M', 8), (5, 'm7', 8), (7, 'sus4', 4), (7, 'M', 4)],
        C=[(8, 'M7', 8), (10, 'add9', 8), (0, 'madd9', 8), (7, 'm', 8)],
    ),
    'vita': dict(
        title='VITA Genomics 2092', tonic='E', bpm=92, levels='21-40',
        mood='sterile, glassy, quietly unsettling; organic undercurrent',
        A=[(0, 'm9', 8), (8, 'M7#11', 8), (3, 'M7', 8), (10, 'add9', 8)],
        B=[(0, 'm', 8), (5, 'm9', 8), (8, 'M7', 8), (7, 'sus4', 8)],
        C=[(8, 'M7#11', 8), (3, 'M7', 8), (5, 'm7', 8), (10, 'sus2', 8)],
    ),
    'nova': dict(
        title='Nova Grid 2096', tonic='C', bpm=120, levels='41-60',
        mood='heavy, industrial, pressurised heat; metallic rhythm',
        A=[(0, '5', 8), (1, 'M', 8), (0, '5', 8), (10, 'M', 8)],
        B=[(0, 'm', 8), (8, 'M', 8), (1, 'M', 8), (7, 'M', 8)],
        C=[(5, 'm', 8), (1, 'M7', 8), (0, 'm', 8), (10, 'sus2', 8)],
    ),
    'civitas': dict(
        title='Civitas Network 2100', tonic='B', bpm=100, levels='61-80',
        mood='sterile, watchful, controlled; ticking surveillance',
        A=[(0, 'sus2', 8), (0, 'madd9', 8), (8, 'M7', 8), (8, 'M7#11', 8)],
        B=[(0, 'm', 8), (10, 'M', 8), (8, 'M', 8), (7, 'M', 8)],
        C=[(5, 'm9', 8), (5, 'm9', 8), (0, 'madd9', 8), (1, 'M7', 8)],
    ),
    'meridian': dict(
        title='Meridian 2104', tonic='D', bpm=128, levels='81-100',
        mood='monumental, fractured, inevitable; the convergence of every system',
        A=[(0, 'm', 8), (8, 'M', 8), (1, 'M', 8), (7, 'M', 8)],
        B=[(0, 'madd9', 8), (8, 'M7', 8), (3, 'M', 8), (10, 'M', 8)],
        C=[(8, 'M', 8), (1, 'M', 8), (7, 'sus4', 8), (7, 'M', 8)],
    ),
}

PHRASES = ['A', 'A', 'B', 'B', 'C', 'C', 'B', 'A']   # 8 x 8 bars = 64 bars loop body


def tonic_pc(ch):
    from .theory import NOTE
    return NOTE[CH[ch]['tonic']]


def tmidi(ch, octave):
    return midi(CH[ch]['tonic'], octave)


def full_prog(ch, phrases=PHRASES, octave=3):
    t = tmidi(ch, octave)
    out = []
    for p in phrases:
        out += progression(t, CH[ch][p])
    return out


def phrase_starts(phrases=PHRASES):
    return [i * 32 for i in range(len(phrases))]


# ---------------------------------------------------------------- shared track setup
def std_tracks(s, ch):
    d = CH[ch]
    s.track('pad', I.supersaw_pad, level=-24, sends={'hall': -6}, kw=dict(seed=3, cutoff=1800 if ch != 'vita' else 2600, detune=0.16, attack=1.4, release=3.0))
    s.track('drone', I.drone, level=-28, sends={'bighall': -8}, kw=dict(seed=4))
    s.track('sub', I.sub_bass, level=-22, duck=4.0, fx=[pb.LowpassFilter(180)], kw=dict(harm=0.3, release=0.35))
    s.track('bass', I.pulse_bass, level=-22, duck=5.0, fx=[pb.HighpassFilter(38)], kw=dict(seed=5))
    s.track('strings', I.strings, level=-24, sends={'hall': -4}, kw=dict(seed=6))
    s.track('ostinato', I.strings, level=-26, sends={'hall': -8}, kw=dict(seed=7, attack=0.02, release=0.18, vibrato=0.0, legato_swell=False, bright=1.2))
    s.track('brass', I.brass, level=-23, sends={'hall': -3}, kw=dict(seed=8))
    s.track('lead', I.fm_pluck, level=-23, sends={'delay': -10, 'hall': -8}, kw=dict(seed=9, ratio=1.0, index=1.6, decay=0.9, idx_decay=0.25))
    s.track('kick', None, level=-21, fx=[pb.HighpassFilter(30)])
    s.track('snare', None, level=-25, sends={'plate': -10})
    s.track('hats', None, level=-31, sends={'room': -12}, width=1.3)
    s.track('perc', None, level=-28, sends={'hall': -12, 'delay': -16})
    s.track('toms', None, level=-25, sends={'hall': -8})
    s.track('fx', None, level=-25, sends={'bighall': -6})
    s.track('tex', None, level=-32, sends={'hall': -12})


# ---------------------------------------------------------------- signature layers
def helix_layers(s, prog, intensity, beats):
    t = tmidi('helix', 4)
    s.track('arp', I.fm_pluck, level=-25 if intensity < 3 else -24, sends={'delay': -7, 'hall': -12}, kw=dict(seed=21, ratio=2.0, index=2.6, decay=0.16, idx_decay=0.05))
    acc = [1.0, 0.55, 0.6, 0.9, 0.55, 0.6, 0.85, 0.6]
    if intensity == 1:
        # sparse 8th arp, top register, only from bar 9
        s.notes('arp', [n for n in arp_notes(prog, step=0.5, order=(0, 2, 1, 3), octaves=(12, 24), low=62, vel=0.5, gate=0.5) if n[0] >= 32])
    else:
        s.notes('arp', arp_notes(prog, step=0.25, order=(0, 1, 2, 3, 2, 1, 4, 3), octaves=(0, 12), low=62, vel=0.75, accent=acc, gate=0.45))
    # cyan shimmer: high glass bell on phrase starts
    s.track('shimmer', I.bell, level=-31, sends={'bighall': -2}, kw=dict(seed=22, ratio=4.0, index=1.2, decay=3.0))
    for p in range(0, int(beats), 32):
        s.notes('shimmer', [(p, 4, t + 24, 0.5), (p + 0.75, 4, t + 31, 0.4)])
    # precise digital ticks (3+3+2)
    tk = [D.tick(i, f=4200, decay=0.006) for i in range(3)]
    for b, v in grid(beats, clock_pattern(), cycle=4.0):
        if intensity >= 2 or (b % 8) < 4:
            s.hit('perc', b, tk[int(b * 4) % 3], gain=v * (0.6 if intensity == 1 else 1.0), pan=0.35 if int(b * 4) % 2 else -0.35)


def vita_layers(s, prog, intensity, beats):
    t = tmidi('vita', 4)
    s.track('glass', I.bell, level=-26, sends={'bighall': -3, 'delay': -12}, kw=dict(seed=31, ratio=3.5, index=1.8, decay=2.6, shimmer=0.7))
    # triplet-feel glass arpeggio (organic, breathing against the 4/4 pulse)
    step = 2 / 3 if intensity < 3 else 1 / 3
    notes = arp_notes(prog, step=step, order=(0, 2, 1, 3, 2, 4), octaves=(12, 24), low=64, vel=0.55, gate=0.9)
    if intensity == 1:
        notes = [n for i, n in enumerate(notes) if i % 2 == 0]
    s.notes('glass', notes)
    s.track('breath', None, level=-31 if intensity > 1 else -29, sends={'hall': -10})
    s.texture('breath', lambda n: I.breath_texture(n, seed=33, rate=s.bpm / 60 / 8, level=0.08, fc=700))
    # heartbeat-like low double pulse every bar (organic low texture)
    hb = D.kick(5, f_hi=90, f_lo=42, sweep=0.03, decay=0.25, click=0.05, drive=1.1)
    for b in np.arange(0, beats, 4):
        s.hit('perc', b, hb, gain=0.8)
        s.hit('perc', b + 0.5, hb, gain=0.5)
    s.track('piano', I.piano, level=-27 if intensity < 3 else -26, sends={'hall': -4}, kw=dict(seed=34))
    if intensity >= 2:
        pn = []
        for i, (root, ch, bt) in enumerate(prog):
            b0 = sum(x[2] for x in prog[:i])
            if i % 2 == 0:
                pn += [(b0 + 2, 3, max(ch) + 12, 0.45), (b0 + 5.5, 2, ch[1] + 12, 0.35)]
        s.notes('piano', pn)


def nova_layers(s, prog, intensity, beats):
    t = tmidi('nova', 2)
    s.track('reese', I.reese, level=-23 if intensity > 1 else -26, duck=4.0, kw=dict(seed=41, cutoff=500 if intensity < 3 else 900))
    rn = []
    for i, (root, ch, bt) in enumerate(prog):
        b0 = sum(x[2] for x in prog[:i])
        r = (root - t) % 12 + t
        if intensity == 1:
            rn.append((b0, bt, r, 0.6))
        else:
            # industrial 3+3+2 low pulse
            for k in range(int(bt // 2)):
                for o, d in [(0, 0.6), (0.75, 0.6), (1.5, 0.4)]:
                    rn.append((b0 + 2 * k + o, d, r, 0.85 if o == 0 else 0.65))
    s.notes('reese', rn)
    s.track('metal', None, level=-27, sends={'metal': -4, 'hall': -10})
    an = [D.anvil(i, f0=f) for i, f in enumerate([520, 780, 610, 450])]
    pat = [(0, 1.0), (1.5, 0.6), (2.75, 0.8), (3.5, 0.5)] if intensity > 1 else [(0, 0.7), (2.75, 0.5)]
    for b, v in grid(beats, pat, cycle=4):
        s.hit('metal', b, an[int(b * 4) % 4], gain=v, pan=((int(b * 4) % 5) - 2) / 3)
    s.track('hum', None, level=-33, sends={'hall': -14})
    s.texture('hum', lambda n: I.electric_hum(n, seed=43, f=50.0, level=0.04, crackle=0.6))
    # steam/pressure noise swells every 8 bars
    s.track('steam', None, level=-31, sends={'hall': -8})
    for p in range(0, int(beats), 32):
        s.hit('steam', p + 24, D.riser(s.s(8), seed=p, f_lo=200, f_hi=4000, curve=1.5), gain=0.8)


def civitas_layers(s, prog, intensity, beats):
    t = tmidi('civitas', 5)
    # sterile sustained sine tones (cold high cluster)
    s.track('sterile', I.drone, level=-29, sends={'bighall': -4}, kw=dict(seed=51, partials=(1, 2, 3), attack=4.0, release=5.0, bright=0.25))
    for p in range(0, int(beats), 32):
        s.notes('sterile', [(p, 30, t + 7, 0.6), (p + 8, 22, t + 10 if (p // 32) % 2 else t + 8, 0.45)])
    # ticking surveillance: 3-against-4 polymeter of clock ticks
    tk = [D.tick(60 + i, f=2400 + 300 * i, decay=0.01, q=0.9) for i in range(4)]
    for b in np.arange(0, beats, 0.5):
        s.hit('perc', b, tk[0], gain=0.75 if b % 1 == 0 else 0.45, pan=-0.3)
    if intensity >= 2:
        for b in np.arange(0, beats, 2 / 3):
            s.hit('perc', b, tk[2], gain=0.5, pan=0.4)
    # red security pulse: minor-second dyad, soft, every 2 bars in tension+
    s.track('alarm', I.fm_pluck, level=-29 if intensity < 3 else -27, sends={'delay': -8, 'hall': -10}, kw=dict(seed=52, ratio=1.0, index=0.6, decay=0.5, idx_decay=0.2))
    if intensity >= 2:
        an = []
        for b in np.arange(4, beats, 8):
            an += [(b, 0.9, t + 12, 0.6), (b, 0.9, t + 13, 0.45), (b + 1.5, 0.9, t + 12, 0.45), (b + 1.5, 0.9, t + 13, 0.35)]
        s.notes('alarm', an)


def meridian_layers(s, prog, intensity, beats):
    t = tmidi('meridian', 1)
    # deep sub-bass: an octave below the usual bass, long notes
    s.track('deepsub', I.sub_bass, level=-21, duck=3.0, fx=[pb.LowpassFilter(120)], kw=dict(harm=0.35, attack=0.08, release=0.5))
    dn = []
    for i, (root, ch, bt) in enumerate(prog):
        b0 = sum(x[2] for x in prog[:i])
        dn.append((b0, bt, (root - t) % 12 + t, 0.9))
    s.notes('deepsub', dn)
    # fractured signal textures
    r = rng(71)
    density = {1: 0.6, 2: 1.4, 3: 2.4}[intensity]
    hits = []
    for b in np.arange(0, beats, 1):
        if r.random() < density / 4:
            hits.append(s.s(b + r.choice([0, 0.25, 0.5, 0.75])))
    s.track('glitch', None, level=-29, sends={'delay': -8, 'plate': -12})
    gl = I.glitch_layer(int(s.s(beats) * SR) + SR, hits, seed=72, level=0.3)
    s.hit('glitch', 0, gl)
    # convergence: echoes of the other four chapters at low level
    s.track('echo_helix', I.fm_pluck, level=-30, sends={'delay': -6, 'hall': -10}, kw=dict(seed=73, ratio=2.0, index=2.4, decay=0.14, idx_decay=0.05))
    if intensity >= 2:
        s.notes('echo_helix', [n for n in arp_notes(prog, step=0.25, order=(0, 1, 2, 3, 2, 1, 4, 3), octaves=(0, 12), low=62, vel=0.6, gate=0.4) if (n[0] % 32) >= 16])
    s.track('echo_vita', I.bell, level=-31, sends={'bighall': -3}, kw=dict(seed=74, ratio=3.5, index=1.8, decay=2.6))
    s.notes('echo_vita', [(p + 0.0, 4, tmidi('meridian', 6) + 7, 0.5) for p in range(0, int(beats), 16)])
    s.track('echo_nova', None, level=-30, sends={'metal': -4})
    an = D.anvil(75, f0=587)
    for b in np.arange(0, beats, 8):
        s.hit('echo_nova', b + 2.75, an, gain=0.7, pan=0.5)
    tk = D.tick(76, f=2600, decay=0.01)
    s.track('echo_civitas', None, level=-33)
    for b in np.arange(0, beats, 0.5):
        s.hit('echo_civitas', b, tk, gain=0.6 if b % 1 == 0 else 0.35, pan=-0.4)


LAYERS = {'helix': helix_layers, 'vita': vita_layers, 'nova': nova_layers, 'civitas': civitas_layers, 'meridian': meridian_layers}
