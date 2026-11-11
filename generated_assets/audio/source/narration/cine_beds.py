#!/usr/bin/env python3
"""Narration music beds for the chapter intros, chapter outros, finale and 2041 teaser.

Each bed is a re-arrangement of our own original cinematic cue for that sequence (tfjaudio cues2:
cin_intro / cin_outro / cin_finale / cin_teaser, chapter keys, tempos, progressions, signature layers and
the MOTIF / ANSWER / HOPE themes), re-timed so that every musical event lands on the voiced timeline:
swells in the gaps between lines, the turn on the line that turns the story, hits on the end card.
Timeline JSON comes from cine_build.py (slide starts/ends in seconds, word times, end card).
The opening bed is opening_bed.py.

usage (tfjaudio deps): cine_beds.py KIND CHAPTER timeline.json out_master48.wav
  KIND in intro | outro | finale | teaser ; CHAPTER in helix vita nova civitas meridian
"""
import json, os, sys
import numpy as np, soundfile as sf
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from tfjaudio import instruments as I, drums as D
from tfjaudio.cues2 import base_song, end_hit, chapter_layers, put_prog
from tfjaudio.chapters import CH, full_prog, tmidi
from tfjaudio.theory import MOTIF, ANSWER, HOPE, progression, pad_notes, arp_notes, motif_notes, midi
from tfjaudio.song import trim_tail
from tfjaudio.dsp import SR, rng


class Cue:
    def __init__(self, sid, ch, bpm, end_s, tail):
        self.bpm = bpm
        self.s = base_song(sid, bpm, int(np.ceil(end_s * bpm / 60)) + 1, ch, tail=tail)
        self.s.master_target = -16.5

    def b(self, t):           # seconds -> beats
        return t * self.bpm / 60.0

    def notes(self, tr, items):   # items in seconds: (t, dur_s, midi, vel)
        self.s.notes(tr, [(self.b(t), self.b(d), m, v) for t, d, m, v in items])

    def hit(self, tr, t, arr, gain=1.0, pan=0.0):
        self.s.hit(tr, self.b(t), arr, gain=gain, pan=pan)

    def cut_after(self, t, keep=()):
        bt = self.b(t)
        for name, tr in self.s.tracks.items():
            if name in keep: continue
            tr.notes = [x for x in tr.notes if x[0] < bt]
            tr.hits = [x for x in tr.hits if x[0] < bt]

    def layers(self, ch, t0, t1, intensity=1, gain_db=-3.0):
        n = max(1, int(np.ceil(self.b(t1 - t0) / 32)))
        chapter_layers(self.s, ch, self.b(t0), ['A'] * n, intensity, gain_db=gain_db)

    def swells(self, tl, chord, inst='strings', vel=0.45):
        for g0, g1 in tl['gaps']:
            self.notes(inst, [(g0 - 0.6, g1 - g0 + 1.8, m, vel) for m in chord])


def intro(ch, tl):
    d = CH[ch]; c = Cue(f'mus_cine_{ch}_intro_vo', ch, d['bpm'], tl['end_s'], 8.0)
    t1, t3, t4, t5 = tmidi(ch, 1), tmidi(ch, 3), tmidi(ch, 4), tmidi(ch, 5)
    hit = tl['end_card_s']
    c.notes('drone', [(0, hit, t3 - 12, 0.7), (0, hit, t3 - 5, 0.45)])
    prog = full_prog(ch, ['A'] * 8, 3)
    c.s.notes('pad', [(b, du, m, 0.42) for (b, du, m, v) in pad_notes(prog, low=53, high=72) if b < c.b(hit - 1)])
    c.layers(ch, 0, hit, 1, gain_db=-4)
    c.cut_after(hit - 0.3, keep=('pad', 'drone', 'fx', 'tex'))
    c.s.notes('glass_lead', motif_notes(t5, 0.5, MOTIF, vel=0.38, stretch=2.0, legato=0.8))
    c.swells(tl, (t3 + 7, t4 + 3))
    for g0, g1 in tl['gaps']:
        c.notes('piano', [(g0 + 0.1, 2.5, t4 + 7, 0.36), (g0 + 0.7, 2.5, t4 + 3, 0.32)])
    c.hit('fx', hit - 4.0, D.riser(4.0, seed=3, tonal_m=t4), gain=0.6)
    end_hit(c.s, c.b(hit), t1, big=True, seed=31)
    c.s.notes('brass', motif_notes(t3, c.b(hit), MOTIF[:3], vel=0.85) + [(c.b(hit) + 3, 5, t3, 0.6)])
    c.notes('strings_hi', [(hit, 6, t4 + 12, 0.5), (hit, 6, t4 + 19, 0.4)])
    return c


def outro(ch, tl):
    d = CH[ch]; c = Cue(f'mus_cine_{ch}_outro_vo', ch, 72, tl['end_s'], 8.0)
    t1, t3, t4 = tmidi(ch, 1), tmidi(ch, 3), tmidi(ch, 4)
    rel = t3 + 3
    turn, shift, end = tl['turn_s'], tl['shift_s'], tl['end_card_s']
    # hope (relative major), as in cin_outro, until the turn
    H = progression(rel, [(0, 'add9', 8), (7, 'sus2', 8), (5, 'M7', 8), (0, 'add9', 8)])
    put_prog(c.s, H, 0, pad_vel=0.42, bass_oct=rel - 24)
    c.cut_after(turn - 0.2, keep=())
    c.s.notes('piano', motif_notes(rel + 12, 0.5, HOPE, vel=0.5))
    c.notes('strings', [(2.0, turn - 1.5, rel + 16, 0.42), (2.0, turn - 1.5, rel + 7, 0.38)])
    c.notes('glass', [(1.0 + 3.3 * i, 3, rel + 24 + (0, 2, 4, 7)[i % 4], 0.3) for i in range(int(max(1, (turn - 2) / 3.3)))])
    # the turn: minor drone, ANSWER low, glitch fractures
    c.notes('drone', [(turn - 0.5, end - turn + 6, t3 - 12, 0.7), (turn - 0.5, end - turn + 6, t3 - 11, 0.22)])
    c.notes('pad', [(turn - 0.5, shift - turn + 0.5, m, 0.45) for m in (t3, t3 + 3, t3 + 8)])
    c.s.notes('strings', motif_notes(t3, c.b(turn + 0.3), ANSWER, vel=0.55, stretch=1.2))
    c.s.track('glitch', None, level=-28, sends={'delay': -8, 'plate': -12})
    r = rng(40 + ord(ch[0]))
    hits = sorted([turn + (shift - turn) * (r.random() ** 0.6) for _ in range(22)])
    c.hit('glitch', 0, I.glitch_layer(int((end + 2) * SR), hits, seed=41, level=0.28))
    c.swells(tl, (t3 - 2, t3 + 7), vel=0.4)
    # timeline shift on the Control line, then cold pulse
    c.hit('fx', shift - 3.0, D.riser(3.0, seed=50, f_hi=10000), gain=0.55)
    c.hit('hit', shift - 0.15, D.braam(t1, length=5.0, seed=60, bright=0.7), gain=0.6)
    c.hit('low', shift - 0.15, D.sub_drop(3.0), gain=0.75)
    c.notes('pad', [(shift, end - shift + 4, m, 0.45) for m in (t3 - 2, t3 + 2, t3 + 7)])
    tk = D.tick(5, f=3800, decay=0.006)
    for i, t in enumerate(np.arange(shift + 0.5, end, 0.5)):
        c.hit('perc', float(t), tk, gain=0.35 + 0.01 * i, pan=0.3 if i % 2 else -0.3)
    c.hit('low', end, D.boom(12, f0=38, decay=2.4), gain=0.6)
    return c


def finale(ch, tl):
    c = Cue('mus_cine_finale_vo', 'meridian', 66, tl['end_s'], 10.0)
    D1, D2, D3, D4 = midi('D', 1), midi('D', 2), midi('D', 3), midi('D', 4)
    st, en = tl['slide_starts_s'], tl['slide_ends_s']
    sig, rev, last = st[2] - 0.6, st[4] - 0.25, tl['end_card_s']
    Dmaj = progression(D3, [(0, 'add9', 8), (9, 'm', 8), (7, 'M7', 8), (7, 'sus4', 4), (7, 'M', 4)] * 2)
    put_prog(c.s, Dmaj, 0, pad_vel=0.5)
    c.cut_after(sig, keep=())
    c.s.notes('strings', motif_notes(D4, c.b(1.0), HOPE, vel=0.55))
    c.s.notes('piano', [n for n in arp_notes(Dmaj, step=1.0, order=(0, 1, 2, 3), octaves=(12,), low=57, vel=0.28, gate=2.5) if n[0] < c.b(sig - 0.5)])
    # signal returns on "Wait."
    c.notes('pad', [(sig, rev - sig, m, 0.5) for m in (D3, D3 + 3, D3 + 7)])
    c.notes('drone', [(sig, last - sig + 6, D2, 0.7), (sig + 4, rev - sig - 4, D2 + 1, 0.3)])
    tk = D.tick(7, f=3800, decay=0.006); n = 0
    for t in np.arange(sig + 1.0, rev, 0.9 if True else 0.5):
        c.hit('perc', float(t), tk, gain=0.35 + 0.012 * n, pan=0.3 if n % 2 else -0.3); n += 1
    c.s.track('glitch', None, level=-26, sends={'delay': -8, 'plate': -12})
    r = rng(70); hits = sorted([sig + (rev - sig) * (r.random() ** 0.5) for _ in range(36)])
    c.hit('glitch', 0, I.glitch_layer(int((last + 4) * SR), hits, seed=71, level=0.33))
    c.notes('strings', [(en[2] + 0.2, st[4] - en[2], D3 + 1, 0.45), (en[2] + 0.2, st[4] - en[2], D3 + 8, 0.4)])
    c.hit('fx', rev - 3.5, D.riser(3.5, seed=72, tonal_m=D3), gain=0.65)
    # 2041
    end_hit(c.s, c.b(rev), D1, big=True, seed=73)
    c.hit('low', rev, D.sub_drop(4.0, f_hi=90, f_lo=24), gain=0.85)
    c.s.notes('brass', motif_notes(D2 + 12, c.b(en[4] + 0.2), MOTIF, vel=0.8, stretch=1.25))
    # unresolved second degree over the drone
    c.notes('strings_hi', [(st[5] - 0.5, last - st[5] + 5, D4 + 14, 0.38)])
    c.notes('piano', [(en[5] + 0.1, 3, D4, 0.42), (en[5] + 0.9, 3, D4 + 8, 0.38), (st[6] + 2, 5, D4 + 7, 0.35)])
    c.hit('low', last, D.boom(74, f0=34, decay=3.0), gain=0.65)
    return c


def teaser(ch, tl):
    c = Cue('mus_cine_teaser_2041_vo', 'helix', 92, tl['end_s'], 7.0)
    G1, G2, G3, G4 = midi('G', 1), midi('G', 2), midi('G', 3), midi('G', 4)
    st, en = tl['slide_starts_s'], tl['slide_ends_s']
    hit = tl['hit_s']
    prog = progression(G3, [(0, 'm', 8), (8, 'M', 8), (3, 'M', 8), (10, 'M', 8)] * 3)
    c.s.notes('pad', [(b, du, m, 0.45) for (b, du, m, v) in pad_notes(prog, low=53, high=72) if b < c.b(hit - 0.3)])
    c.notes('drone', [(0, hit, G2, 0.55)])
    c.notes('piano', [(1.0, 3, G4 + 7, 0.35), (2.2, 3, G4 + 3, 0.3), (en[0] + 0.2, 3, G4 + 10, 0.32)])
    c.notes('glass', [(en[1] + 0.2 + 0.6 * i, 2.5, G4 + 12 + m, 0.3) for i, m in enumerate((0, 7, 12, 15))])
    c.s.track('warm', I.supersaw_pad, level=-24, sends={'hall': -4, 'delay': -10}, kw=dict(seed=93, voices=3, detune=0.08, attack=0.02, release=0.4, cutoff=2400))
    c.s.notes('warm', motif_notes(G4, c.b(st[2]), MOTIF, vel=0.6) + motif_notes(G4, c.b(st[3]), ANSWER, vel=0.6))
    p0 = st[2] - 0.5
    c.s.notes('bass', [(b, 0.3, G2, 0.55 + 0.25 * (b - c.b(p0)) / max(1, c.b(hit - p0))) for b in np.arange(c.b(p0), c.b(hit), 0.5)])
    for b in np.arange(np.ceil(c.b(st[3] - 0.3)), c.b(hit)):
        c.s.hit('kick', b, D.kick(3), gain=0.7)
    c.hit('fx', hit - 5.0, D.riser(5.0, seed=94, tonal_m=G3), gain=0.75)
    end_hit(c.s, c.b(hit), G1, big=True, seed=95)
    c.s.notes('brass', motif_notes(G3, c.b(hit), MOTIF[:3], vel=0.85))
    c.notes('piano', [(hit + 2.5, 3, G4 + 8, 0.4)])
    return c


if __name__ == '__main__':
    kind, ch, tlp, out = sys.argv[1:5]
    tl = json.load(open(tlp))
    c = {'intro': intro, 'outro': outro, 'finale': finale, 'teaser': teaser}[kind](ch, tl)
    c.s.meta.update({'timeline': tl})
    mix, n = c.s.render(); m = c.s.master(mix); y, _ = c.s.finish(m, n); y = trim_tail(y)
    sf.write(out, y, SR, subtype='FLOAT')
    print(json.dumps({'seconds': round(len(y) / SR, 3), 'bpm': c.bpm}))
