"""Cue builders: chapter mission loops, critical layers and climax tracks."""
import numpy as np
import pedalboard as pb
from . import instruments as I
from . import drums as D
from .theory import (MOTIF, ANSWER, HOPE, progression, pad_notes, bass_notes, arp_notes, grid, motif_notes,
                     clock_pattern)
from .chapters import CH, PHRASES, LAYERS, full_prog, std_tracks, tmidi
from .song import Song
from .dsp import SR, rng

LEAD = {'helix': 'lead', 'vita': 'glass_lead', 'nova': 'brass', 'civitas': 'strings_hi', 'meridian': 'brass'}


def _common_lead_tracks(s, ch):
    s.track('glass_lead', I.bell, level=-23, sends={'bighall': -4, 'delay': -10}, kw=dict(seed=81, ratio=2.0, index=1.4, decay=2.0, shimmer=0.4, pan_spread=0.15))
    s.track('strings_hi', I.strings, level=-23, sends={'hall': -3}, kw=dict(seed=82, attack=0.35, bright=1.1))


def add_motif(s, ch, start, inst, octave, vel=0.8, answer=True, stretch=1.0):
    t = tmidi(ch, octave)
    n = motif_notes(t, start, MOTIF, vel=vel, stretch=stretch)
    if answer:
        n += motif_notes(t, start + 8 * stretch, ANSWER, vel=vel * 0.95, stretch=stretch)
    s.notes(inst, n)


def drums_for(s, ch, intensity, beats, fills=True):
    r = rng(hash(ch) % 1000)
    k = [D.kick(i, f_hi=150 if ch != 'nova' else 130, f_lo=46 if ch != 'meridian' else 40, decay=0.3, drive=1.6 if ch != 'nova' else 2.4) for i in range(2)]
    sn = [D.snare(i, tone=190 if ch != 'civitas' else 230, bright=1.0) for i in range(3)]
    hh = [D.hat(i, decay=0.03 + 0.01 * i) for i in range(3)]
    tom = [D.taiko(i, f0=f) for i, f in enumerate([80, 105, 140])]
    if intensity == 2:
        pat = {'helix': [(0, 0.9), (2, 0.7)], 'vita': [(0, 0.8)], 'nova': [(0, 1.0), (1.5, 0.6), (2, 0.8)],
               'civitas': [(0, 0.8), (2.5, 0.5)], 'meridian': [(0, 1.0), (2.5, 0.7)]}[ch]
        for b, v in grid(beats, pat, cycle=4):
            if b >= 32:  # pulse drums enter after the first phrase
                s.hit('kick', b, k[0], gain=v)
                s.duck_hits.append(b)
        for b, v in grid(beats, [(0.5, 0.5), (1.5, 0.7), (2.5, 0.5), (3.5, 0.7)], cycle=4):
            if b >= 64:
                s.hit('hats', b, hh[int(b) % 3], gain=v, pan=0.25)
    elif intensity >= 3:
        if ch in ('helix', 'meridian'):
            kp = [(0, 1.0), (0.75, 0.6), (1.5, 0.8), (2, 0.9), (2.75, 0.6), (3.5, 0.7)]
        elif ch == 'nova':
            kp = [(0, 1.0), (0.75, 0.8), (1.5, 0.9), (2.5, 0.8), (3, 0.9)]
        elif ch == 'vita':
            kp = [(0, 1.0), (1.5, 0.6), (2.5, 0.8)]
        else:
            kp = [(0, 1.0), (1, 0.7), (2, 0.9), (3, 0.7)]
        for b, v in grid(beats, kp, cycle=4):
            s.hit('kick', b, k[int(b * 4) % 2], gain=v)
            s.duck_hits.append(b)
        for b, v in grid(beats, [(1, 0.9), (3, 1.0)], cycle=4):
            s.hit('snare', b, sn[int(b) % 3], gain=v)
        hp_ = [(i * 0.25, 0.9 if i % 4 == 2 else (0.6 if i % 2 == 0 else 0.4)) for i in range(16)]
        for b, v in grid(beats, hp_, cycle=4):
            s.hit('hats', b, hh[int(b * 4) % 3], gain=v * (0.9 + 0.1 * r.random()), pan=0.2 * np.sin(b))
        if fills:
            for p in range(32, int(beats) + 1, 32):
                for j, o in enumerate([-2, -1.5, -1, -0.75, -0.5, -0.25]):
                    s.hit('toms', p + o, tom[j % 3], gain=0.6 + 0.07 * j, pan=-0.4 + 0.16 * j)
        # big taiko on phrase downbeats
        for p in range(0, int(beats), 32):
            s.hit('toms', p, tom[0], gain=1.0)
            s.hit('toms', p + 16, tom[1], gain=0.8)


def mission_loop(ch, intensity, sid=None):
    sid = sid or f"mus_{ch}_{[None, 'prep', 'tension', 'combat'][intensity]}_loop"
    d = CH[ch]
    beats = 4 * 8 * len(PHRASES)
    s = Song(sid, d['bpm'], beats, loop=True)
    std_tracks(s, ch)
    _common_lead_tracks(s, ch)
    prog = full_prog(ch, octave=3)
    t3 = tmidi(ch, 3)
    padv = {1: 0.45, 2: 0.6, 3: 0.75}[intensity]
    s.notes('pad', [(b, du, m, padv) for (b, du, m, v) in pad_notes(prog, low=53, high=74)])
    # drone: tonic + fifth across every phrase
    for p in range(0, beats, 32):
        s.notes('drone', [(p, 32, t3 - 12, 0.7), (p, 32, t3 - 5, 0.5)])
    # bass
    if intensity == 1:
        s.notes('sub', bass_notes(prog, [(0, 7.5, 0, 0.7)], octave_midi=tmidi(ch, 1) + 2))
    else:
        s.notes('sub', bass_notes(prog, [(0, 3.8, 0, 0.8), (4, 3.8, 0, 0.75)], octave_midi=tmidi(ch, 1) + 2))
        if ch != 'nova':
            if intensity == 2:
                pat = [(o * 0.5, 0.3, 0, 1.0 if o % 2 == 0 else 0.7) for o in range(8)]
            else:
                pat = [(0, 0.2, 0, 1.0), (0.75, 0.2, 0, 0.8), (1.5, 0.2, 12, 0.9), (2, 0.2, 0, 1.0), (2.75, 0.2, 0, 0.8), (3.5, 0.2, 7, 0.9)]
            s.notes('bass', bass_notes(prog, pat, octave_midi=tmidi(ch, 2)))
    # chapter signature
    LAYERS[ch](s, prog, intensity, beats)
    # motif plan over 8 phrases: P3 lead, P4 second voice, P6 soft answer, P7 restatement
    lead = LEAD[ch]
    if intensity == 1:
        add_motif(s, ch, 64, 'glass_lead' if ch != 'vita' else 'glass', 5, vel=0.45, answer=False, stretch=2.0)
        add_motif(s, ch, 192, 'glass_lead' if ch != 'vita' else 'glass', 5, vel=0.4, answer=False, stretch=2.0, )
    else:
        lo = 4 if lead != 'brass' else 3
        add_motif(s, ch, 64, lead, lo, vel=0.75 if intensity == 2 else 0.85)
        add_motif(s, ch, 96, 'strings' if intensity == 2 else 'brass', 4 if intensity == 2 else 3, vel=0.7)
        s.notes('glass_lead', motif_notes(tmidi(ch, 5), 168, ANSWER, vel=0.45, stretch=1.5))
        add_motif(s, ch, 192, 'strings_hi', 4, vel=0.7 if intensity == 2 else 0.85)
        if intensity >= 3:
            add_motif(s, ch, 192, 'brass', 3, vel=0.85)
        # counter line across the C phrases: long top voice
        top = []
        for i, (root, chd, bt) in enumerate(prog[16:24]):
            top.append((128 + 8 * i, 8, max(chd) + 12, 0.55))
        s.notes('strings_hi', top)
    if intensity >= 3:
        # staccato string ostinato on the clock cell
        on = []
        for i, (root, chd, bt) in enumerate(prog):
            b0 = sum(x[2] for x in prog[:i])
            r0 = (root - tmidi(ch, 3)) % 12 + tmidi(ch, 3)
            for k in range(int(bt // 2)):
                for o, iv in [(0, 0), (0.75, 7), (1.5, 12)]:
                    on.append((b0 + 2 * k + o, 0.3, r0 + iv, 0.8 if o == 0 else 0.65))
        s.notes('ostinato', on)
        for p in range(0, beats, 32):
            s.hit('fx', p, D.braam(tmidi(ch, 1), length=s.s(6), seed=p, bright=0.8), gain=0.9 if p % 64 == 0 else 0.6)
            s.hit('fx', p + 28, D.riser(s.s(4), seed=p + 1), gain=0.7)
    elif intensity == 2:
        for p in (64, 192):
            s.hit('fx', p - 4, D.riser(s.s(4), seed=p, f_hi=6000), gain=0.5)
    drums_for(s, ch, intensity, beats)
    arrange_mission(s, ch, intensity, beats)
    s.meta.update(dict(chapter=ch, intensity=intensity))
    return s


def arrange_mission(s, ch, intensity, beats):
    """Phrase-level arrangement so a 64-bar loop breathes.
    P1 A intro, P2 A' pulse, P3 B motif, P4 B' second voice, P5 C breakdown-lift, P6 C' development,
    P7 B'' restatement, P8 A'' wind-down into the loop point."""
    have = set(s.tracks)
    def m(name, ranges):
        if name in have:
            s.mask(name, ranges)
    def a(name, pts):
        if name in have:
            s.automate(name, pts)
    if intensity == 1:
        a('pad', [(0, -2), (64, 0), (128, 1), (192, 0), (240, -1.5)])
        a('arp', [(0, -4), (96, 0), (160, -2), (224, -4)])
        m('perc', [(0, 128), (160, 240)])
        a('drone', [(0, 0), (128, -2), (192, 0)])
    elif intensity == 2:
        m('bass', [(32, 128), (144, 240)])
        m('kick', [(32, 128), (144, 240)])
        m('hats', [(64, 128), (160, 224)])
        m('strings', [(96, 128)])
        a('arp', [(0, -5), (32, 0), (128, -3), (160, 0), (224, -2), (255, -5)])
        a('pad', [(0, -1), (96, 0.5), (128, 1.5), (192, 1), (224, 0), (255, -1)])
        a('perc', [(0, -2), (64, 0), (224, -1)])
        for name in ('reese', 'metal', 'glitch', 'alarm', 'glass', 'deepsub'):
            a(name, [(0, -3), (32, 0), (224, 0), (255, -3)])
    else:
        m('kick', [(0, 128), (144, 248)])
        m('hats', [(0, 128), (136, 248)])
        m('snare', [(0, 128), (144, 248)])
        a('pad', [(0, 0), (128, 2), (160, 0), (192, 1), (224, 0)])
        a('ostinato', [(0, -2), (64, 0), (128, -4), (144, 0), (224, -1), (255, -2)])
