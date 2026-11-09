"""Through-composed cues: themes, cinematic score, stingers, results, credits, critical layers, climaxes."""
import copy
import numpy as np
import pedalboard as pb
from . import instruments as I
from . import drums as D
from .theory import (MOTIF, ANSWER, HOPE, MAJOR, progression, pad_notes, bass_notes, arp_notes, grid, motif_notes,
                     clock_pattern, midi)
from .chapters import CH, LAYERS, full_prog, std_tracks, tmidi
from .cues import _common_lead_tracks, drums_for, LEAD, add_motif
from .song import Song
from .dsp import SR, rng, fade

ORDER = ['helix', 'vita', 'nova', 'civitas', 'meridian']


def graft(dst, src, offset, window=None, gain_db=0.0):
    """Copy src tracks/events into dst shifted by offset beats (window limits src beats)."""
    w0, w1 = window or (0, src.beats)
    for name, tr in src.tracks.items():
        if name not in dst.tracks:
            t2 = copy.copy(tr)
            t2.notes, t2.hits, t2.auto = [], [], None
            dst.tracks[name] = t2
        d = dst.tracks[name]
        for (b, du, m, v) in tr.notes:
            if w0 <= b < w1:
                d.notes.append((b - w0 + offset, min(du, w1 - b + 2), m, v * (10 ** (gain_db / 20))))
        for (b, arr, g, p) in tr.hits:
            if w0 <= b < w1:
                d.hits.append((b - w0 + offset, arr, g * (10 ** (gain_db / 20)), p))
    for (name, fn) in src.textures:
        n = int(src.s(w1 - w0) * SR)
        x = fade(fn(n), 1.5, 2.0) * (10 ** (gain_db / 20))
        if name not in dst.tracks:
            dst.track(name, None, level=src.tracks[name].level if name in src.tracks else -32)
        dst.tracks[name].hits.append((offset, x, 1.0, 0.0))
    dst.duck_hits += [b - w0 + offset for b in src.duck_hits if w0 <= b < w1]


def chapter_layers(dst, ch, offset, phrases, intensity, gain_db=0.0, drums=False):
    tmp = Song('tmp', dst.bpm, 32 * len(phrases))
    std_tracks(tmp, ch)
    prog = full_prog(ch, phrases, octave=3)
    LAYERS[ch](tmp, prog, intensity, tmp.beats)
    if drums:
        drums_for(tmp, ch, intensity, tmp.beats)
    graft(dst, tmp, offset, gain_db=gain_db)
    return prog


def put_prog(dst, prog, offset, pad_vel=0.6, bass=True, sub=True, low=53, high=74, bass_oct=None, track='pad'):
    pn = pad_notes(prog, low=low, high=high, vel=pad_vel)
    dst.notes(track, [(b + offset, d, m, v) for (b, d, m, v) in pn])
    if sub:
        bo = bass_oct if bass_oct is not None else 26
        dst.notes('sub', [(b + offset, d, m, v) for (b, d, m, v) in bass_notes(prog, [(0, 7.6, 0, 0.8)], octave_midi=bo)])


def base_song(sid, bpm, beats, ch=None, tail=7.0):
    s = Song(sid, bpm, beats, loop=False, tail=tail)
    std_tracks(s, ch or 'helix')
    _common_lead_tracks(s, ch or 'helix')
    s.track('piano', I.piano, level=-24, sends={'hall': -4}, kw=dict(seed=34))
    s.track('glass', I.bell, level=-26, sends={'bighall': -3, 'delay': -12}, kw=dict(seed=31, ratio=3.5, index=1.8, decay=2.6, shimmer=0.7))
    s.track('hit', None, level=-20, sends={'bighall': -5})
    s.track('low', None, level=-22, sends={'hall': -10})
    s.tracks['sub'].kw['release'] = 1.2
    s.tracks['pad'].kw['release'] = 3.5
    return s


def end_hit(s, beat, tonic_low, big=True, seed=0):
    s.hit('hit', beat, D.braam(tonic_low, length=s.s(8) if big else s.s(4), seed=seed, bright=0.9), gain=1.0 if big else 0.6)
    s.hit('low', beat, D.boom(seed, f0=40, decay=2.0 if big else 1.2), gain=1.0)


def riser_into(s, beat, beats=4, seed=0, gain=0.7, tonal=None):
    L = s.s(beats)
    s.hit('fx', beat - beats, D.riser(L, seed=seed, tonal_m=tonal), gain=gain)


# ===================================================================== main theme
def main_theme():
    bpm = 84
    s = base_song('mus_main_theme', bpm, 200, 'helix', tail=8.0)
    D4 = midi('D', 4)
    D3 = midi('D', 3)
    A = progression(D3, [(0, 'madd9', 8), (8, 'M7', 8), (3, 'add9', 8), (10, 'sus2', 8)])
    B = progression(D3, [(0, 'm', 8), (8, 'M', 8), (5, 'm7', 8), (7, 'sus4', 4), (7, 'M', 4)])
    F3 = midi('F', 3)
    BR = progression(F3, [(0, 'add9', 8), (7, 'sus2', 8), (5, 'M7', 8), (7, 'M', 8)])   # bridge in F major
    s.notes('drone', [(0, 48, D3 - 12, 0.7), (0, 48, D3 - 5, 0.45)])
    # 1-4 piano motif
    s.notes('piano', motif_notes(D4, 0, MOTIF, vel=0.7) + motif_notes(D4, 8, ANSWER, vel=0.65))
    s.notes('pad', [(b, d, m, 0.35) for (b, d, m, v) in pad_notes(A[:2], low=53, high=70)])
    # 5-12 strings + piano arps
    put_prog(s, A + A, 16, pad_vel=0.5)
    s.notes('strings', motif_notes(D4, 16, MOTIF, vel=0.7) + motif_notes(D4, 24, ANSWER, vel=0.65))
    s.notes('piano', [n for n in arp_notes(A + A, step=0.5, order=(0, 1, 2, 3, 2, 1), octaves=(0, 12), low=57, vel=0.4, start=16, gate=1.6)])
    s.notes('brass', motif_notes(D3, 32, MOTIF, vel=0.7) + motif_notes(D3, 40, ANSWER, vel=0.65))
    # 13-20 pulse enters (Helix colour)
    put_prog(s, B + B, 48, pad_vel=0.55)
    chapter_layers(s, 'helix', 48, ['B'], 2, gain_db=-1)
    s.notes('lead', motif_notes(D4 + 12, 48, MOTIF, vel=0.7) + motif_notes(D4 + 12, 56, ANSWER, vel=0.65))
    s.notes('strings_hi', [(64 + 8 * i, 8, m, 0.5) for i, m in enumerate([D4 + 12, D4 + 10, D4 + 9, D4 + 7])])
    for b in range(48, 80, 4):
        s.hit('kick', b, D.kick(1), gain=0.8)
        s.duck_hits.append(b)
    s.notes('bass', [(b + 48, d, m, v) for (b, d, m, v) in bass_notes(B + B, [(o * 0.5, 0.3, 0, 1.0 if o % 2 == 0 else 0.7) for o in range(8)], octave_midi=38)])
    riser_into(s, 80, 4, seed=3)
    # 21-28 full statement
    put_prog(s, A + A, 80, pad_vel=0.7)
    end_hit(s, 80, midi('D', 1), big=True, seed=1)
    s.notes('brass', motif_notes(D3, 80, MOTIF, vel=0.9) + motif_notes(D3, 88, ANSWER, vel=0.85))
    s.notes('strings', motif_notes(D4, 80, MOTIF, vel=0.85) + motif_notes(D4, 88, ANSWER, vel=0.8))
    s.notes('strings_hi', motif_notes(D4 + 12, 96, MOTIF, vel=0.8) + motif_notes(D4 + 12, 104, ANSWER, vel=0.8))
    s.notes('brass', [(96 + 8 * i, 7.5, m, 0.7) for i, m in enumerate([D3 + 7, D3 + 5, D3 + 3, D3 + 2])])
    chapter_layers(s, 'helix', 80, ['A'], 3, gain_db=-2, drums=True)
    # 29-36 bridge (hope)
    put_prog(s, BR, 112, pad_vel=0.5, bass_oct=29)
    s.notes('piano', motif_notes(midi('F', 4), 112, HOPE, vel=0.65))
    s.notes('glass', motif_notes(midi('F', 5), 120, HOPE, vel=0.5))
    s.notes('strings', [(112 + 8 * i, 8, m, 0.5) for i, m in enumerate([midi('A', 4), midi('G', 4), midi('A', 4), midi('B', 4) - 1])])
    s.notes('strings', [(136, 8, midi('A', 4), 0.6), (136, 8, midi('C#', 5), 0.55)])
    riser_into(s, 144, 8, seed=5, gain=0.8, tonal=midi('D', 3))
    # 37-44 climax tutti
    put_prog(s, B + A, 144, pad_vel=0.75)
    end_hit(s, 144, midi('D', 1), big=True, seed=2)
    for inst, base, v in [('brass', D3, 0.95), ('strings', D4, 0.9), ('strings_hi', D4 + 12, 0.85), ('lead', D4 + 12, 0.6)]:
        s.notes(inst, motif_notes(base, 144, MOTIF, vel=v) + motif_notes(base, 152, ANSWER, vel=v) + motif_notes(base, 160, MOTIF, vel=v) + motif_notes(base, 168, ANSWER, vel=v))
    chapter_layers(s, 'meridian', 144, ['B'], 3, gain_db=-3, drums=True)
    # 45-50 outro: piano alone, unresolved second degree over the drone
    s.notes('drone', [(176, 24, D3 - 12, 0.7), (176, 24, D3 - 5, 0.4)])
    s.notes('piano', motif_notes(D4, 176, MOTIF, vel=0.55, stretch=1.25))
    s.notes('piano', [(188, 6, D4 + 7, 0.45), (191, 6, D4 + 3, 0.4), (194, 8, D4 + 2, 0.4)])
    s.notes('strings_hi', [(186, 14, D4 + 14, 0.35)])
    s.hit('low', 196, D.boom(9, f0=38, decay=2.5), gain=0.7)
    s.mask('kick', [(0, 176)])
    return s


# ===================================================================== menu loop
def menu_loop():
    s = Song('mus_menu_loop', 76, 128, loop=True)
    std_tracks(s, 'helix')
    _common_lead_tracks(s, 'helix')
    s.track('piano', I.piano, level=-25, sends={'hall': -3}, kw=dict(seed=35))
    D3 = midi('D', 3)
    A = progression(D3, [(0, 'madd9', 8), (8, 'M7', 8), (3, 'add9', 8), (10, 'sus2', 8)])
    C = progression(D3, [(8, 'M7', 8), (5, 'm9', 8), (0, 'madd9', 8), (7, 'sus4', 8)])
    prog = A + A + C + A
    s.notes('pad', [(b, d, m, 0.5) for (b, d, m, v) in pad_notes(prog, low=53, high=72)])
    s.notes('sub', bass_notes(prog, [(0, 7.6, 0, 0.7)], octave_midi=26))
    for p in range(0, 128, 32):
        s.notes('drone', [(p, 32, D3 - 12, 0.6), (p, 32, D3 - 5, 0.4)])
    s.notes('piano', motif_notes(midi('D', 4), 32, MOTIF, vel=0.5, stretch=1.0) + motif_notes(midi('D', 4), 40, ANSWER, vel=0.45))
    s.notes('glass_lead', motif_notes(midi('D', 5), 96, MOTIF, vel=0.4, stretch=2.0, legato=0.7))
    s.notes('piano', [n for n in arp_notes(C, step=1.0, order=(0, 2, 1, 3), octaves=(12,), low=57, vel=0.3, start=64, gate=2.5)])
    s.track('arp', I.fm_pluck, level=-30, sends={'delay': -6, 'hall': -10}, kw=dict(seed=21, ratio=2.0, index=1.8, decay=0.25, idx_decay=0.06))
    s.notes('arp', [n for n in arp_notes(prog, step=0.5, order=(0, 2, 1, 3), octaves=(12, 24), low=62, vel=0.45, gate=0.5) if 16 <= (n[0] % 64) < 56])
    tk = D.tick(3, f=4000, decay=0.005)
    for b, v in grid(128, clock_pattern((0.8, 0.5, 0.6)), cycle=4):
        s.hit('perc', b, tk, gain=v * 0.6, pan=0.3 if int(b * 4) % 2 else -0.3)
    s.automate('perc', [(0, -6), (32, 0), (96, -2), (127, -6)])
    s.track('shimmer', I.bell, level=-31, sends={'bighall': -2}, kw=dict(seed=22, ratio=4.0, index=1.2, decay=3.0))
    s.notes('shimmer', [(p, 4, midi('D', 6), 0.4) for p in range(0, 128, 16)])
    s.track('tex', None, level=-34)
    s.texture('tex', lambda n: I.noise_bed(n, seed=91, lo=300, hi=2500, level=0.03, motion=0.03))
    return s


# ===================================================================== chapter themes
def chapter_theme(ch):
    d = CH[ch]
    s = base_song(f'mus_{ch}_theme', d['bpm'], 192, ch, tail=8.0)
    t3, t4 = tmidi(ch, 3), tmidi(ch, 4)
    lead = LEAD[ch]
    lead_oct = t3 if lead == 'brass' else t4
    pA = full_prog(ch, ['A'], 3)
    pB = full_prog(ch, ['B'], 3)
    pC = full_prog(ch, ['C'], 3)
    s.notes('drone', [(0, 64, t3 - 12, 0.7), (0, 64, t3 - 5, 0.45)])
    # 1-8 intro
    chapter_layers(s, ch, 0, ['A'], 1)
    s.notes('pad', [(b, du, m, 0.4) for (b, du, m, v) in pad_notes(pA, low=53, high=72)])
    s.notes('glass_lead', motif_notes(tmidi(ch, 5), 8, MOTIF, vel=0.4, stretch=2.0, legato=0.8))
    # 9-16 statement
    put_prog(s, pA, 32, pad_vel=0.55, bass_oct=tmidi(ch, 1) + 2)
    chapter_layers(s, ch, 32, ['A'], 2, gain_db=-2)
    s.notes(lead, motif_notes(lead_oct, 32, MOTIF, vel=0.75) + motif_notes(lead_oct, 40, ANSWER, vel=0.7))
    s.notes('piano', motif_notes(t4, 48, MOTIF, vel=0.5) + motif_notes(t4, 56, ANSWER, vel=0.45))
    # 17-32 development
    put_prog(s, pB + pB, 64, pad_vel=0.6, bass_oct=tmidi(ch, 1) + 2)
    chapter_layers(s, ch, 64, ['B', 'B'], 2, drums=True)
    s.notes('strings', motif_notes(t4, 64, MOTIF, vel=0.75) + motif_notes(t4, 72, ANSWER, vel=0.7))
    s.notes('brass', motif_notes(t3, 96, MOTIF, vel=0.8) + motif_notes(t3, 104, ANSWER, vel=0.75))
    s.notes('strings_hi', [(80 + 8 * i, 8, m, 0.5) for i, m in enumerate([t4 + 12, t4 + 10, t4 + 8, t4 + 7])])
    riser_into(s, 128, 4, seed=7)
    # 33-40 peak
    put_prog(s, pC, 128, pad_vel=0.75, bass_oct=tmidi(ch, 1) + 2)
    end_hit(s, 128, tmidi(ch, 1), big=True, seed=4)
    chapter_layers(s, ch, 128, ['C'], 3, drums=True)
    for inst, base, v in [('brass', t3, 0.9), ('strings', t4, 0.85), ('strings_hi', t4 + 12, 0.75)]:
        s.notes(inst, motif_notes(base, 128, MOTIF, vel=v) + motif_notes(base, 136, ANSWER, vel=v * 0.95) + motif_notes(base, 144, MOTIF, vel=v))
    # 41-48 outro
    s.notes('drone', [(160, 32, t3 - 12, 0.65), (160, 32, t3 - 5, 0.4)])
    chapter_layers(s, ch, 160, ['A'], 1, gain_db=-2)
    s.notes('pad', [(b + 160, du, m, 0.4) for (b, du, m, v) in pad_notes(pA[:3], low=53, high=72)] + [(184, 10, t3 + 3, 0.3), (184, 10, t3 + 7, 0.3), (184, 10, t3 + 12, 0.3)])
    s.notes('piano', motif_notes(t4, 168, MOTIF, vel=0.5, stretch=1.25))
    s.hit('low', 184, D.boom(11, f0=38, decay=2.2), gain=0.6)
    return s


# ===================================================================== critical-asset layer
def critical_layer(ch):
    d = CH[ch]
    beats = 256
    s = Song(f'mus_{ch}_critical_layer', d['bpm'], beats, loop=True)
    s.master_target = -19.0
    std_tracks(s, ch)
    prog = full_prog(ch, octave=3)
    t4 = tmidi(ch, 4)
    # high spiccato 16ths on chord tones (urgency)
    on = []
    for i, (root, chd, bt) in enumerate(prog):
        b0 = sum(x[2] for x in prog[:i])
        tones = sorted(set(c % 12 for c in chd))
        top = [t4 + 12 + ((p - t4) % 12) for p in tones]
        for k in range(int(bt * 4)):
            on.append((b0 + k * 0.25, 0.12, top[k % len(top)] if k % 4 else top[0], 0.85 if k % 8 in (0, 3, 6) else 0.55))
    s.notes('ostinato', on)
    s.tracks['ostinato'].level = -24
    # toms on the clock cell
    tom = [D.taiko(i + 20, f0=f) for i, f in enumerate([90, 120, 160])]
    for b, v in grid(beats, [(0, 1.0), (0.75, 0.6), (1.5, 0.8), (2, 0.9), (2.75, 0.6), (3.5, 0.7)], cycle=4):
        s.hit('toms', b, tom[int(b * 4) % 3], gain=v)
    # risers into every phrase, hits on phrase downbeats
    for p in range(0, beats, 32):
        s.hit('fx', p + 24, D.riser(s.s(8), seed=p, f_hi=8000), gain=0.6)
    # chapter-coloured warning figure
    s.track('warn', I.fm_pluck, level=-25, sends={'delay': -8, 'hall': -10}, kw=dict(seed=99, ratio=1.0 if ch != 'vita' else 3.5, index=1.2, decay=0.35, idx_decay=0.1))
    wn = []
    fig = {'helix': [(0, 7), (0.5, 7), (1, 8)], 'vita': [(0, 19), (0.333, 18), (0.667, 19)], 'nova': [(0, 0), (0.75, 1), (1.5, 0)],
           'civitas': [(0, 12), (0, 13), (1.5, 12), (1.5, 13)], 'meridian': [(0, 8), (0.5, 7), (1, 1)]}[ch]
    for b in np.arange(0, beats, 4):
        for o, iv in fig:
            wn.append((b + o, 0.4, t4 + iv, 0.7))
    s.notes('warn', wn)
    # sub pulses on phrase downbeats and a high string sustain in the second half of each phrase
    s.notes('strings', [(p + 16, 16, max(chd) + 24, 0.55) for p, (root, chd, bt) in zip(range(0, beats, 32), prog[::4])])
    s.automate('ostinato', [(0, -3), (16, 0), (31, 1)] + [(p, -3) for p in range(32, beats, 32)])
    return s


# ===================================================================== climax / boss track (intro + loop)
def climax(ch):
    d = CH[ch]
    # intro: 8 bars build
    intro = base_song(f'mus_{ch}_climax_intro', d['bpm'], 32, ch, tail=4.0)
    t1, t3, t4 = tmidi(ch, 1), tmidi(ch, 3), tmidi(ch, 4)
    pA = full_prog(ch, ['A'], 3)
    intro.notes('drone', [(0, 32, t3 - 12, 0.8), (0, 32, t3 - 5, 0.6)])
    intro.notes('pad', [(b, du, m, 0.5) for (b, du, m, v) in pad_notes(pA, low=53, high=72)])
    end_hit(intro, 0, t1, big=True, seed=10)
    chapter_layers(intro, ch, 0, ['A'], 2)
    on = []
    for k in range(32 * 2):
        on.append((16 + k * 0.25, 0.12, t4 + (0 if k % 2 == 0 else 7), 0.4 + 0.5 * k / 64))
    intro.notes('ostinato', on)
    intro.notes('brass', motif_notes(t3, 8, MOTIF[:3], vel=0.8))
    intro.hit('fx', 24, D.riser(intro.s(8), seed=11, tonal_m=t3), gain=0.8)
    tom = [D.taiko(i, f0=f) for i, f in enumerate([80, 105, 140])]
    for j, b in enumerate(np.arange(28, 32, 0.25)):
        intro.hit('toms', b, tom[j % 3], gain=0.5 + 0.5 * j / 16)
    # body: 64 bars, loops
    s = Song(f'mus_{ch}_climax', d['bpm'], 256, loop=True)
    std_tracks(s, ch)
    _common_lead_tracks(s, ch)
    phrases = ['B', 'B', 'C', 'A', 'B', 'B', 'C', 'A']
    prog = full_prog(ch, phrases, 3)
    s.notes('pad', [(b, du, m, 0.75) for (b, du, m, v) in pad_notes(prog, low=53, high=74)])
    s.notes('sub', bass_notes(prog, [(0, 3.8, 0, 0.85), (4, 3.8, 0, 0.8)], octave_midi=t1 + 2))
    if ch != 'nova':
        s.notes('bass', bass_notes(prog, [(0, 0.2, 0, 1.0), (0.75, 0.2, 0, 0.8), (1.5, 0.2, 12, 0.9), (2, 0.2, 0, 1.0), (2.75, 0.2, 0, 0.8), (3.5, 0.2, 7, 0.9)], octave_midi=tmidi(ch, 2)))
    LAYERS[ch](s, prog, 3, 256)
    drums_for(s, ch, 3, 256)
    lead = LEAD[ch] if LEAD[ch] != 'brass' else 'lead'
    plan = [(0, 'brass', t3, 0.95), (0, 'strings', t4, 0.85), (32, 'strings_hi', t4 + 12, 0.8), (96, lead, t4 + 12, 0.7),
            (128, 'brass', t3, 0.95), (128, 'strings', t4, 0.9), (160, 'strings_hi', t4 + 12, 0.85), (160, 'brass', t3, 0.9)]
    for b0, inst, base, v in plan:
        s.notes(inst, motif_notes(base, b0, MOTIF, vel=v) + motif_notes(base, b0 + 8, ANSWER, vel=v))
    for off in (64, 192):
        s.notes('brass', [(off + 8 * i, 7.5, m, 0.8) for i, m in enumerate([t3 + 7, t3 + 8, t3 + 7, t3 + 5])])
        s.notes('strings_hi', [(off + 8 * i, 8, m, 0.6) for i, m in enumerate([t4 + 15, t4 + 14, t4 + 12, t4 + 10])])
    on = []
    for i, (root, chd, bt) in enumerate(prog):
        b0 = sum(x[2] for x in prog[:i])
        r0 = (root - t3) % 12 + t3
        for k in range(int(bt // 2)):
            for o, iv in [(0, 0), (0.75, 7), (1.5, 12)]:
                on.append((b0 + 2 * k + o, 0.3, r0 + iv + 12, 0.85 if o == 0 else 0.7))
    s.notes('ostinato', on)
    for p in range(0, 256, 32):
        s.hit('fx', p, D.braam(t1, length=s.s(6), seed=p + 3, bright=0.9), gain=0.9 if p % 64 == 0 else 0.65)
        s.hit('fx', p + 28, D.riser(s.s(4), seed=p + 5), gain=0.7)
    # breathing room: half-time drums for 4 bars in the second C phrase
    s.mask('snare', [(0, 192), (208, 256)])
    s.mask('hats', [(0, 192), (200, 256)])
    return intro, s


# ===================================================================== cinematic: opening
OPENING_SLIDES = [0, 12, 24, 36, 47, 58, 70]   # seconds (60 BPM, so beats = seconds)


def cin_opening():
    s = base_song('mus_cin_opening', 60, 80, 'helix', tail=9.0)
    s.master_target = -16.5   # contract -16 +-1; sits slightly low under narration, MusicDirector ducks further
    D2, D3, D4 = midi('D', 2), midi('D', 3), midi('D', 4)
    # slides 1-3: the world that remained / the bargain / the end
    s.notes('drone', [(0, 36, D2, 0.7), (0, 36, D2 + 7, 0.45), (24, 12, D2 + 1 + 12, 0.25)])
    s.notes('pad', [(0, 12, m, 0.35) for m in (D3 + 3, D3 + 7, D3 + 14)] + [(12, 12, m, 0.4) for m in (D3 - 2 + 0, D3 + 3, D3 + 10)] + [(24, 12, m, 0.4) for m in (D3 - 4, D3, D3 + 3, D3 + 8)])
    s.notes('piano', [(2, 3, D4 + 14, 0.35), (6, 3, D4 + 10, 0.3), (14, 3, D4 + 8, 0.35), (18, 4, D4 + 7, 0.3), (26, 4, D4 + 3, 0.3), (31, 4, D4 + 2, 0.3)])
    s.track('tex', None, level=-33)
    s.texture('tex', lambda n: I.noise_bed(n, seed=92, lo=150, hi=1800, level=0.04, motion=0.02))
    s.hit('low', 24, D.boom(21, f0=36, decay=3.0), gain=0.5)
    # slide 4: discovery (shimmer rises)
    s.notes('glass', [(36 + i * 1.5, 3, m, 0.35 + 0.03 * i) for i, m in enumerate([D4 + 12, D4 + 19, D4 + 24, D4 + 15, D4 + 26, D4 + 19, D4 + 31])])
    s.notes('pad', [(36, 11, m, 0.45) for m in (D3 - 2, D3 + 5, D3 + 10, D3 + 14)])
    s.notes('drone', [(36, 22, D2, 0.65), (36, 22, D2 + 7, 0.4)])
    # slide 5: the operative (motif in low strings)
    s.notes('strings', motif_notes(D3, 47, MOTIF, vel=0.6, stretch=1.2))
    s.notes('pad', [(47, 11, m, 0.45) for m in (D3, D3 + 3, D3 + 7, D3 + 14)])
    # slide 6: the charge (pulse and clock begin, Control voice)
    tk = D.tick(5, f=4000, decay=0.005)
    for b in np.arange(58, 78, 0.5):
        s.hit('perc', b, tk, gain=0.35 + 0.4 * (b - 58) / 20, pan=0.3 if (b * 2) % 2 else -0.3)
    s.notes('bass', [(b, 0.3, D2 + 12, 0.5 + 0.3 * (b - 58) / 20) for b in np.arange(58, 78, 0.5)])
    s.notes('pad', [(58, 12, m, 0.5) for m in (D3 - 4, D3, D3 + 3, D3 + 7)])
    # slide 7: countdown, riser, title hit at 78
    s.notes('pad', [(70, 8, m, 0.55) for m in (D3 - 5, D3 + 2, D3 + 7, D3 + 10)])
    s.hit('fx', 70, D.riser(8, seed=23, tonal_m=D3), gain=0.8)
    for b, v in [(74, 0.7), (75, 0.8), (76, 0.9)]:   # "three... two... one"
        s.hit('low', b, D.taiko(24 + b, f0=70), gain=v * 0.7)
    end_hit(s, 78, midi('D', 1), big=True, seed=25)
    s.notes('brass', motif_notes(D3, 78, MOTIF[:3], vel=0.9) + [(80.5, 5, D3, 0.7)])
    s.notes('strings_hi', [(78, 8, D4 + 12, 0.6), (78, 8, D4 + 19, 0.5)])
    s.meta['slide_starts_s'] = OPENING_SLIDES
    s.meta['title_hit_s'] = 78
    return s


# ===================================================================== cinematic: chapter intro / outro
def cin_intro(ch, idx):
    d = CH[ch]
    beats = 64 if d['bpm'] >= 110 else 56 if d['bpm'] >= 96 else 48
    s = base_song(f'mus_cin_{ch}_intro', d['bpm'], beats, ch, tail=8.0)
    s.master_target = -16.5
    t1, t3, t4 = tmidi(ch, 1), tmidi(ch, 3), tmidi(ch, 4)
    phrases = ['A', 'A'] if beats == 64 else ['A', 'A']
    prog = full_prog(ch, ['A', 'A'], 3)[: int(beats / 8)]
    s.notes('drone', [(0, beats, t3 - 12, 0.7), (0, beats, t3 - 5, 0.45)])
    s.notes('pad', [(b, du, m, 0.45) for (b, du, m, v) in pad_notes(prog, low=53, high=72) if b < beats - 8])
    chapter_layers(s, ch, 0, ['A', 'A'], 1, gain_db=-1)
    for name in list(s.tracks):
        tr = s.tracks[name]
        tr.notes = [x for x in tr.notes if x[0] < beats - 8 or name in ('brass', 'strings_hi', 'pad', 'drone')]
        tr.hits = [x for x in tr.hits if x[0] < beats - 8 or name in ('hit', 'low', 'fx')]
    s.notes('glass_lead', motif_notes(tmidi(ch, 5), 16, MOTIF, vel=0.4, stretch=2.0, legato=0.8))
    riser_into(s, beats - 8, 4, seed=idx, gain=0.6)
    end_hit(s, beats - 8, t1, big=True, seed=30 + idx)
    s.notes('brass', motif_notes(t3, beats - 8, MOTIF[:3], vel=0.85) + [(beats - 5, 5, t3, 0.6)])
    s.notes('strings_hi', [(beats - 8, 8, t4 + 12, 0.5), (beats - 8, 8, t4 + 19, 0.4)])
    s.meta['end_card_beat'] = beats - 8
    s.meta['end_card_s'] = round(s.s(beats - 8), 3)
    return s


def cin_outro(ch, idx):
    bpm = 72
    s = base_song(f'mus_cin_{ch}_outro', bpm, 48, ch, tail=8.0)
    s.master_target = -16.5
    t1, t3, t4 = tmidi(ch, 1), tmidi(ch, 3), tmidi(ch, 4)
    rel = t3 + 3   # relative major tonic
    H = progression(rel, [(0, 'add9', 8), (7, 'sus2', 8), (5, 'M7', 8)])
    put_prog(s, H, 0, pad_vel=0.45, bass_oct=(rel - 24))
    s.notes('piano', motif_notes(rel + 12, 0, HOPE, vel=0.55) + motif_notes(rel + 12, 9, HOPE[:4], vel=0.45))
    s.notes('strings', [(8, 16, rel + 16, 0.45), (8, 16, rel + 7, 0.4)])
    s.notes('glass', [(4, 3, rel + 24, 0.35), (12, 3, rel + 26, 0.3), (20, 3, rel + 28, 0.3)])
    # the turn: signal fractures, minor drone, low motif answer
    s.notes('drone', [(24, 24, t3 - 12, 0.7), (24, 24, t3 - 11, 0.25)])
    s.notes('pad', [(24, 12, m, 0.45) for m in (t3, t3 + 3, t3 + 8)] + [(36, 6, m, 0.45) for m in (t3 - 2, t3 + 2, t3 + 7)])
    s.notes('strings', motif_notes(t3, 26, ANSWER, vel=0.55, stretch=1.2))
    s.track('glitch', None, level=-27, sends={'delay': -8, 'plate': -12})
    r = rng(40 + idx)
    hits = sorted([s.s(24 + 18 * (r.random() ** 0.6)) for _ in range(26)])
    s.hit('glitch', 0, I.glitch_layer(int(s.s(48) * SR), hits, seed=41 + idx, level=0.3))
    s.hit('fx', 38, D.riser(s.s(4), seed=idx + 50, f_hi=10000), gain=0.6)
    s.hit('hit', 42, D.braam(t1, length=s.s(6), seed=idx + 60, bright=0.7), gain=0.7)
    s.hit('low', 42, D.sub_drop(3.0), gain=0.8)
    s.meta['turn_beat'] = 24
    s.meta['timeline_shift_hit_s'] = round(s.s(42), 3)
    return s


# ===================================================================== finale and teaser
def cin_finale():
    s = base_song('mus_cin_finale', 66, 96, 'meridian', tail=10.0)
    s.master_target = -16.5
    D2, D3, D4 = midi('D', 2), midi('D', 3), midi('D', 4)
    Dmaj = progression(D3, [(0, 'add9', 8), (9, 'm', 8), (7, 'M7', 8), (7 - 0, 'sus4', 4), (7, 'M', 4)])
    Dmaj = [(r, c, b) if i != 3 else (r, c, b) for i, (r, c, b) in enumerate(Dmaj)]
    put_prog(s, Dmaj, 0, pad_vel=0.5)
    s.notes('strings', motif_notes(D4, 0, HOPE, vel=0.6) + motif_notes(D4, 12, HOPE[:5], vel=0.6))
    s.notes('piano', [n for n in arp_notes(Dmaj, step=1.0, order=(0, 1, 2, 3), octaves=(12,), low=57, vel=0.3, gate=2.5)])
    # 32-56: the signal returns
    s.notes('pad', [(32, 12, m, 0.5) for m in (D3, D3 + 4, D3 + 7)] + [(44, 12, m, 0.5) for m in (D3, D3 + 3, D3 + 7)])
    s.notes('drone', [(32, 40, D2, 0.7), (40, 32, D2 + 1, 0.3)])
    tk = D.tick(7, f=3800, decay=0.006)
    for i, b in enumerate(np.concatenate([np.arange(36, 48, 1.0), np.arange(48, 56, 0.5)])):
        s.hit('perc', b, tk, gain=0.4 + 0.02 * i, pan=0.3 if i % 2 else -0.3)
    s.track('glitch', None, level=-26, sends={'delay': -8, 'plate': -12})
    r = rng(70)
    hits = sorted([s.s(34 + 22 * (r.random() ** 0.5)) for _ in range(40)])
    s.hit('glitch', 0, I.glitch_layer(int(s.s(96) * SR), hits, seed=71, level=0.35))
    s.hit('fx', 52, D.riser(s.s(4), seed=72, tonal_m=D3), gain=0.7)
    # 56: 2041
    end_hit(s, 56, midi('D', 1), big=True, seed=73)
    s.hit('low', 56, D.sub_drop(4.0, f_hi=90, f_lo=24), gain=0.9)
    s.notes('brass', motif_notes(D2 + 12, 57, MOTIF, vel=0.85, stretch=1.25))
    s.notes('strings', [(56, 16, D3 + 1, 0.5), (56, 16, D3 + 8, 0.45)])
    # 72-96: unresolved second degree over the drone
    s.notes('drone', [(72, 24, D2, 0.6)])
    s.notes('strings_hi', [(72, 22, D4 + 14, 0.4)])
    s.notes('piano', [(76, 4, D4 + 0, 0.45), (78, 4, D4 + 8, 0.4), (80, 8, D4 + 7, 0.4)])
    s.hit('low', 92, D.boom(74, f0=34, decay=3.0), gain=0.6)
    s.meta.update(dict(signal_returns_s=round(s.s(32), 2), reveal_2041_s=round(s.s(56), 2), final_hit_s=round(s.s(92), 2)))
    return s


def cin_teaser():
    s = base_song('mus_cin_expansion_teaser', 92, 52, 'helix', tail=7.0)
    s.master_target = -16.5
    G2, G3, G4 = midi('G', 2), midi('G', 3), midi('G', 4)
    prog = progression(G3, [(0, 'm', 8), (8, 'M', 8), (3, 'M', 8), (10, 'M', 8), (0, 'm', 8), (1, 'M', 8)])
    put_prog(s, prog, 0, pad_vel=0.5, bass_oct=31)
    s.track('warm', I.supersaw_pad, level=-23, sends={'hall': -4, 'delay': -10}, kw=dict(seed=93, voices=3, detune=0.08, attack=0.02, release=0.4, cutoff=2400))
    s.notes('warm', motif_notes(G4, 16, MOTIF, vel=0.8) + motif_notes(G4, 24, ANSWER, vel=0.75))
    s.notes('bass', [(b, 0.3, G2, 0.8) for b in np.arange(8, 48, 0.5)])
    for b in range(16, 48):
        s.hit('kick', b, D.kick(3), gain=0.85)
        s.duck_hits.append(b)
    for b in range(17, 48, 2):
        s.hit('snare', b, D.snare(3), gain=0.7)
    s.hit('fx', 40, D.riser(s.s(8), seed=94, tonal_m=G3), gain=0.8)
    end_hit(s, 48, midi('G', 1), big=True, seed=95)
    s.notes('piano', [(50, 3, G4 + 8, 0.4)])
    s.mask('pad', [(0, 48)])
    s.mask('sub', [(0, 48)])
    return s


# ===================================================================== stingers & results
def stinger(ch):
    d = CH[ch]
    s = base_song(f'mus_stinger_chapter_{ch}', d['bpm'], 8, ch, tail=4.5)
    s.master_target = -16.0
    t1, t3, t4 = tmidi(ch, 1), tmidi(ch, 3), tmidi(ch, 4)
    lead = LEAD[ch]
    base = t3 if lead == 'brass' else t4
    s.notes(lead, [(0, 0.45, base, 0.9), (0.5, 0.45, base + 8, 0.85), (1.0, 2.8, base + 7, 0.85)])
    s.notes('strings', [(1, 6, t4, 0.6), (1, 6, t4 + 7, 0.5), (1, 6, t4 + 3, 0.5)])
    end_hit(s, 1, t1, big=False, seed=80)
    chapter_layers(s, ch, 1, ['A'], 2, gain_db=-4)
    for name in list(s.tracks):
        s.tracks[name].notes = [x for x in s.tracks[name].notes if x[0] < 5]
        s.tracks[name].hits = [x for x in s.tracks[name].hits if x[0] < 5 or name in ('hit', 'low')]
    s.textures = []
    s.mask('drone', [])
    s.meta['max_seconds'] = 11.8
    return s


def stinger_timeline_shift():
    s = base_song('mus_stinger_timeline_shift', 90, 6, 'meridian', tail=4.0)
    s.hit('fx', 0, D.riser(s.s(2), seed=3, f_lo=600, f_hi=12000, curve=1.2), gain=0.7)
    s.track('glitch', None, level=-24, sends={'delay': -8})
    s.hit('glitch', 0, I.glitch_layer(int(s.s(4) * SR), [s.s(x) for x in (0.5, 1.0, 1.25, 1.5, 1.75, 1.875, 2.0, 2.5, 3.0)], seed=5, level=0.4))
    end_hit(s, 2, midi('D', 1), big=False, seed=6)
    s.notes('strings_hi', [(2, 3, midi('D', 5), 0.5), (2, 3, midi('Eb', 5), 0.35)])
    s.meta['max_seconds'] = 11.8
    return s


def result_success():
    s = base_song('mus_result_mission_success', 96, 10, 'helix', tail=4.0)
    D4, D3 = midi('D', 4), midi('D', 3)
    s.notes('glass_lead', [(0, 0.5, D4 + 12, 0.8), (0.5, 0.5, D4 + 21, 0.75), (1, 0.5, D4 + 19, 0.75), (1.5, 3, D4 + 16, 0.8)])
    s.notes('strings', [(1.5, 6, m, 0.6) for m in (D4, D4 + 4, D4 + 7, D4 + 14)])
    s.notes('pad', [(1.5, 6, m, 0.5) for m in (D3, D3 + 7, D3 + 16)])
    s.notes('sub', [(1.5, 6, midi('D', 1) + 12, 0.7)])
    s.notes('piano', [(1.5, 4, D4 + 12, 0.5), (1.5, 4, D4 + 16, 0.45), (1.5, 4, D4 + 19, 0.45)])
    s.hit('low', 1.5, D.boom(81, f0=44, decay=1.0), gain=0.6)
    s.meta['max_seconds'] = 11.8
    return s


def result_fail():
    s = base_song('mus_result_mission_fail', 72, 8, 'helix', tail=4.0)
    D3, D4 = midi('D', 3), midi('D', 4)
    s.notes('strings', [(0, 1, D4 + 7, 0.65), (1, 1, D4 + 3, 0.6), (2, 1, D4 + 2, 0.55), (3, 4, D4 + 1, 0.5)])
    s.notes('pad', [(0, 7, m, 0.45) for m in (D3, D3 + 3, D3 + 8)])
    s.notes('drone', [(0, 7, midi('D', 2), 0.7), (0, 7, midi('D', 2) + 1, 0.3)])
    s.hit('low', 0, D.sub_drop(3.0, f_hi=80, f_lo=26), gain=0.8)
    s.hit('fx', 0, D.downlifter(3.0, seed=4), gain=0.6)
    s.meta['max_seconds'] = 11.8
    return s


def result_chapter_complete():
    s = base_song('mus_result_chapter_complete', 96, 16, 'helix', tail=5.0)
    D3, D4 = midi('D', 3), midi('D', 4)
    F3 = midi('F', 3)
    prog = progression(D3, [(8, 'M', 4), (10, 'M', 4), (0, 'M', 8)])
    put_prog(s, prog, 2, pad_vel=0.6)
    s.notes('brass', motif_notes(D3, 2, HOPE, vel=0.85))
    s.notes('strings', motif_notes(D4, 2, HOPE, vel=0.8))
    s.notes('glass_lead', [(10, 6, D4 + 24, 0.5), (11, 6, D4 + 28, 0.4)])
    tom = [D.taiko(i + 40, f0=f) for i, f in enumerate([80, 105, 140])]
    for j, b in enumerate(np.arange(0, 2, 0.25)):
        s.hit('toms', b, tom[j % 3], gain=0.45 + 0.07 * j)
    end_hit(s, 2, midi('D', 1), big=False, seed=82)
    s.hit('low', 10, D.boom(83, f0=40, decay=2.0), gain=0.7)
    s.meta['max_seconds'] = 11.8
    return s


# ===================================================================== credits
def credits():
    bpm = 72
    s = base_song('mus_credits', bpm, 216, 'meridian', tail=10.0)
    D2, D3, D4 = midi('D', 2), midi('D', 3), midi('D', 4)
    A = progression(D3, [(0, 'madd9', 8), (8, 'M7', 8), (3, 'add9', 8), (10, 'sus2', 8)])
    F3 = midi('F', 3)
    H = progression(F3, [(0, 'add9', 8), (7, 'sus2', 8), (5, 'M7', 8), (7, 'M', 8)])
    # 1-8 piano solo
    s.notes('drone', [(0, 32, D2, 0.6)])
    s.notes('piano', motif_notes(D4, 0, MOTIF, vel=0.55, stretch=1.0) + motif_notes(D4, 8, ANSWER, vel=0.5) + motif_notes(D4, 16, MOTIF, vel=0.55) + [(24, 8, D4 + 2, 0.45), (24, 8, D4 - 3, 0.35)])
    s.notes('pad', [(b, d, m, 0.35) for (b, d, m, v) in pad_notes(A, low=53, high=70)])
    # 9-16 strings + hope
    put_prog(s, H, 32, pad_vel=0.5, bass_oct=29)
    s.notes('strings', motif_notes(midi('F', 4), 32, HOPE, vel=0.65) + motif_notes(midi('F', 4), 44, HOPE[:5], vel=0.6))
    s.notes('piano', [n for n in arp_notes(H, step=0.5, order=(0, 1, 2, 3, 2, 1), octaves=(0, 12), low=57, vel=0.35, start=32, gate=1.5)])
    # cameos: each chapter colour for 8 bars, the motif passing between instruments
    for i, ch in enumerate(ORDER[:4]):
        off = 64 + 32 * i
        prog = chapter_layers(s, ch, off, ['A'], 2 if i % 2 == 0 else 1, gain_db=-3)
        # keep the credits in D minor-ish: graft gives chapter keys, which is the point (journey)
        put_prog(s, prog, off, pad_vel=0.5, bass_oct=tmidi(ch, 1) + 2)
        lead = {'helix': 'lead', 'vita': 'glass_lead', 'nova': 'brass', 'civitas': 'strings_hi'}[ch]
        base = tmidi(ch, 3 if lead == 'brass' else 4)
        s.notes(lead, motif_notes(base, off + 8, MOTIF, vel=0.6) + motif_notes(base, off + 16, ANSWER, vel=0.55))
    # 41-46 convergence tutti in D
    off = 192
    put_prog(s, A[:3], off, pad_vel=0.65)
    s.notes('brass', motif_notes(D3, off, MOTIF, vel=0.8))
    s.notes('strings', motif_notes(D4, off, MOTIF, vel=0.75) + [(off + 8, 12, D4 + 2, 0.5)])
    s.notes('strings_hi', [(off, 12, D4 + 12, 0.5), (off + 12, 10, D4 + 14, 0.45)])
    end_hit(s, off, midi('D', 1), big=False, seed=90)
    s.notes('piano', [(off + 16, 3, D4 + 7, 0.4), (off + 19, 3, D4 + 3, 0.35), (off + 22, 6, D4 + 2, 0.35)])
    s.notes('drone', [(off, 24, D2, 0.6)])
    s.mask('kick', [])
    return s
