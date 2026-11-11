#!/usr/bin/env python3
"""Opening cinematic music bed, re-arranged from the original GAM-MUS-OPENING-01 cue (tfjaudio cues2.cin_opening)
to the voiced timeline. 60 BPM, so beats = seconds; every musical event is placed from timeline.json
(slide starts, gaps, countdown words, title hit). Same instruments, key (D minor), motif and gestures as
the original cue; swells sit in the gaps between lines. Renders a 48 kHz master with the tfjaudio engine.

usage (tfjaudio deps: numpy, scipy, pedalboard): opening_bed.py timeline.json out_master.wav
"""
import json, os, sys
import numpy as np
import soundfile as sf
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from tfjaudio import instruments as I, drums as D
from tfjaudio.cues2 import base_song, end_hit
from tfjaudio.theory import MOTIF, motif_notes, midi
from tfjaudio.song import trim_tail
from tfjaudio.dsp import SR


def build(tl):
    t = tl['slide_starts_s']; dur = tl['slide_durations_s']; title = tl['title_hit_s']; cd = tl['countdown_hits_s']
    end = [a + b for a, b in zip(t, dur)]
    s = base_song('mus_cine_opening_bed', 60, int(np.ceil(title + 3)), 'helix', tail=9.0)
    s.master_target = -16.5
    D1, D2, D3, D4 = midi('D', 1), midi('D', 2), midi('D', 3), midi('D', 4)
    # pre-roll + slides 1-3: drone, noise bed, sparse piano, darkening pads
    s.notes('drone', [(0, t[3], D2, 0.7), (0, t[3], D2 + 7, 0.45), (t[2] - 1, t[3] - t[2] + 1, D2 + 1 + 12, 0.25)])
    s.track('tex', None, level=-33)
    s.texture('tex', lambda n: I.noise_bed(n, seed=92, lo=150, hi=1800, level=0.04, motion=0.02))
    s.notes('pad', [(0.5, t[1] - 0.5, m, 0.33) for m in (D3 + 3, D3 + 7, D3 + 14)])
    s.notes('pad', [(t[1] - 1.0, t[2] - t[1] + 1, m, 0.4) for m in (D3 - 2, D3 + 3, D3 + 10)])
    s.notes('pad', [(t[2] - 1.0, t[3] - t[2] + 1, m, 0.42) for m in (D3 - 4, D3, D3 + 3, D3 + 8)])
    # piano: one note at each slide start, answer phrases in the gaps (swells)
    s.notes('piano', [(1.0, 3, D4 + 14, 0.38), (2.6, 3, D4 + 10, 0.3),
                      (end[0] + 0.2, 3, D4 + 8, 0.42), (end[0] + 1.0, 3, D4 + 7, 0.36),
                      (end[1] + 0.3, 4, D4 + 3, 0.4), (end[1] + 1.3, 4, D4 + 2, 0.34)])
    s.notes('strings', [(end[1] - 0.5, 4.0, D3 - 4, 0.5), (end[1] - 0.5, 4.0, D3 + 3, 0.45)])   # gap 2 swell
    s.hit('low', t[2], D.boom(21, f0=36, decay=3.0), gain=0.55)                                  # "Cities went silent."
    # gap 3 -> slide 4: discovery shimmer rises out of the dark
    g = [D4 + 12, D4 + 19, D4 + 24, D4 + 15, D4 + 26, D4 + 19, D4 + 31, D4 + 24, D4 + 27]
    s.notes('glass', [(end[2] + 0.3 + i * 1.3, 3, m, 0.34 + 0.035 * i) for i, m in enumerate(g)])
    s.notes('pad', [(end[2] + 0.5, t[4] - end[2] - 0.5, m, 0.45) for m in (D3 - 2, D3 + 5, D3 + 10, D3 + 14)])
    s.notes('drone', [(t[3], t[5] - t[3], D2, 0.62), (t[3], t[5] - t[3], D2 + 7, 0.38)])
    s.hit('fx', end[2] - 0.2, D.riser(3.4, seed=17, tonal_m=D4), gain=0.45)
    # gap 4 -> slide 5: the operative, motif in low strings
    st = (t[5] - end[3] + 0.5) / 8.0
    s.notes('strings', motif_notes(D3, end[3] + 0.2, MOTIF, vel=0.6, stretch=max(1.0, st)))
    s.notes('pad', [(end[3], t[5] - end[3], m, 0.45) for m in (D3, D3 + 3, D3 + 7, D3 + 14)])
    s.hit('hit', end[4] + 0.3, D.braam(D1 + 12, length=s.s(4), seed=9, bright=0.7), gain=0.45)  # gap 5 swell
    # slide 6 onward: Control - pulse and clock, ramping to the countdown
    tk = D.tick(5, f=4000, decay=0.005)
    p0, p1 = t[5] - 0.5, cd[0]
    for b in np.arange(p0, p1, 0.5):
        r = (b - p0) / (p1 - p0)
        s.hit('perc', float(b), tk, gain=0.3 + 0.45 * r, pan=0.3 if int(b * 2) % 2 else -0.3)
    s.notes('bass', [(float(b), 0.3, D2 + 12, 0.45 + 0.35 * (b - p0) / (p1 - p0)) for b in np.arange(p0, p1, 0.5)])
    s.notes('pad', [(t[5] - 0.5, t[6] - t[5] + 0.5, m, 0.5) for m in (D3 - 4, D3, D3 + 3, D3 + 7)])
    s.notes('pad', [(t[6] - 0.5, title - t[6] + 0.5, m, 0.55) for m in (D3 - 5, D3 + 2, D3 + 7, D3 + 10)])
    s.notes('strings_hi', [(end[5], t[6] - end[5] + 2, D4 + 7, 0.35)])                            # gap 6 lift
    s.hit('fx', title - 8.0, D.riser(8, seed=23, tonal_m=D3), gain=0.8)
    for b, v in zip(cd, (0.7, 0.8, 0.9)):                                                         # "three... two... one."
        s.hit('low', b, D.taiko(int(24 + v * 10), f0=70), gain=v * 0.7)
    end_hit(s, title, D1, big=True, seed=25)
    s.notes('brass', motif_notes(D3, title, MOTIF[:3], vel=0.9) + [(title + 2.5, 5, D3, 0.7)])
    s.notes('strings_hi', [(title, 8, D4 + 12, 0.6), (title, 8, D4 + 19, 0.5)])
    s.meta.update({'timeline': tl})
    return s


if __name__ == '__main__':
    tl = json.load(open(sys.argv[1]))
    s = build(tl)
    mix, n = s.render()
    m = s.master(mix)
    y, _ = s.finish(m, n)
    y = trim_tail(y)
    sf.write(sys.argv[2], y, SR, subtype='FLOAT')
    print(json.dumps({'seconds': round(len(y) / SR, 3), 'sr': SR}))
