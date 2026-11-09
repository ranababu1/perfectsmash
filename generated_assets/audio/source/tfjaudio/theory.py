"""Harmony, motif and pattern helpers. The shared main-theme motif lives here."""
import numpy as np

NOTE = {'C': 0, 'C#': 1, 'Db': 1, 'D': 2, 'D#': 3, 'Eb': 3, 'E': 4, 'F': 5, 'F#': 6, 'Gb': 6,
        'G': 7, 'G#': 8, 'Ab': 8, 'A': 9, 'A#': 10, 'Bb': 10, 'B': 11}
MINOR = [0, 2, 3, 5, 7, 8, 10]
HARM_MINOR = [0, 2, 3, 5, 7, 8, 11]
PHRYGIAN = [0, 1, 3, 5, 7, 8, 10]
DORIAN = [0, 2, 3, 5, 7, 9, 10]
LYDIAN = [0, 2, 4, 6, 7, 9, 11]
MAJOR = [0, 2, 4, 5, 7, 9, 11]


def midi(name, octave):
    return 12 * (octave + 1) + NOTE[name]


# ---------------------------------------------------------------- the shared motif
# "The Temporal motif": 1 - b6 - 5 - b3 - 4 - 1 (semitones from tonic), a rising minor sixth
# (the jump back in time) that falls by step to an unresolved fourth before returning home.
# Rhythm in beats. Total 8 beats (two 4/4 bars).
MOTIF = [(0, 1.5), (8, 0.5), (7, 1.0), (3, 1.0), (5, 1.0), (0, 3.0)]
# Answer phrase: lifts to the minor seventh and stops on the second degree (the open question).
ANSWER = [(7, 1.0), (8, 0.5), (10, 0.5), (7, 2.0), (3, 1.0), (2, 3.0)]
# Hopeful major-mode inversion used for victory / ending (1 - 6 - 5 - 3 - 4 - 5 - 1').
HOPE = [(0, 1.5), (9, 0.5), (7, 1.0), (4, 1.0), (5, 1.0), (7, 1.0), (12, 2.0)]
# Clock cell: 3+3+2 sixteenth grouping, the rhythmic identity shared by all chapters.
CLOCK = [0.0, 0.75, 1.5]   # within each two-beat cell: onsets at 0, 3/16*4, 6/16*4 in beats


def motif_notes(tonic_midi, start, phrase=MOTIF, vel=0.8, stretch=1.0, legato=0.95, transpose=0, accent_first=0.1):
    out = []
    b = start
    for i, (iv, d) in enumerate(phrase):
        out.append((b, d * stretch * legato, tonic_midi + iv + transpose, min(1.0, vel + (accent_first if i == 0 else 0))))
        b += d * stretch
    return out


def phrase_len(phrase, stretch=1.0):
    return sum(d for _, d in phrase) * stretch


# ---------------------------------------------------------------- chords
QUAL = {
    'm': [0, 3, 7], 'M': [0, 4, 7], 'm7': [0, 3, 7, 10], 'M7': [0, 4, 7, 11], '7': [0, 4, 7, 10],
    'madd9': [0, 3, 7, 14], 'add9': [0, 4, 7, 14], 'sus2': [0, 2, 7], 'sus4': [0, 5, 7], 'm9': [0, 3, 7, 10, 14],
    'M7#11': [0, 4, 7, 11, 18], 'dim': [0, 3, 6], '5': [0, 7], 'm11': [0, 3, 7, 10, 14, 17], 'Mb5': [0, 4, 6],
}


def chord(root, qual):
    return [root + i for i in QUAL[qual]]


def voice(chord_pcs, prev=None, low=50, high=74):
    """Close voicing near the previous voicing (simple voice leading)."""
    pcs = sorted(set(p % 12 for p in chord_pcs))
    best = None
    best_cost = 1e9
    for base in range(low - 12, high):
        if base % 12 not in pcs:
            continue
        v = []
        cur = base
        for _ in range(len(pcs)):
            v.append(cur)
            # next chord tone above
            nxt = cur + 1
            while nxt % 12 not in pcs or nxt in v:
                nxt += 1
            cur = nxt
        if v[0] < low or v[-1] > high:
            continue
        cost = 0 if prev is None else sum(min(abs(a - b) for b in prev) for a in v) + abs(np.mean(v) - np.mean(prev))
        if prev is None:
            cost = abs(np.mean(v) - (low + high) / 2)
        if cost < best_cost:
            best, best_cost = v, cost
    return best


def progression(tonic, spec):
    """spec: list of (degree_semitones, quality, beats). Returns [(root_midi, chord_notes, beats)]."""
    return [(tonic + d, chord(tonic + d, q), b) for (d, q, b) in spec]


def pad_notes(prog, start=0.0, low=50, high=74, vel=0.6, overlap=0.15, bass_octave=None):
    out = []
    prev = None
    b = start
    for root, ch, beats in prog:
        v = voice(ch, prev, low, high)
        prev = v
        for m in v:
            out.append((b, beats + overlap, m, vel))
        b += beats
    return out


def bass_notes(prog, pattern, octave_midi=26, start=0.0, vel=0.85, beats_per_cycle=None):
    """pattern: list of (offset_beats, dur_beats, interval, vel_mul) repeated across each chord."""
    out = []
    b = start
    for root, ch, beats in prog:
        r = (root - octave_midi) % 12 + octave_midi
        cyc = beats_per_cycle or max(o + d for o, d, _, _ in pattern)
        t = 0.0
        while t < beats - 1e-6:
            for (o, d, iv, vm) in pattern:
                if t + o < beats - 1e-6:
                    out.append((b + t + o, min(d, beats - t - o), r + iv, vel * vm))
            t += cyc
        b += beats
    return out


def arp_notes(prog, step=0.25, order=(0, 1, 2, 1), octaves=(0, 12), low=62, vel=0.7, start=0.0, accent=None, gate=0.6, skip=()):
    out = []
    b = start
    for root, ch, beats in prog:
        pcs = sorted(set(c % 12 for c in ch))
        tones = []
        base = (root - low) % 12 + low
        tones = sorted([base + ((p - base) % 12) for p in pcs])
        tones = [t + o for o in octaves for t in tones]
        k = 0
        t = 0.0
        while t < beats - 1e-6:
            if k % 16 not in skip:
                idx = order[k % len(order)] % len(tones)
                v = vel * (accent[k % len(accent)] if accent else 1.0)
                out.append((b + t, step * gate, tones[idx], v))
            k += 1
            t += step
        b += beats
    return out


def grid(beats, pattern, start=0.0, cycle=4.0):
    """pattern: list of (offset, vel) within each cycle -> list of (beat, vel)."""
    out = []
    t = 0.0
    while t < beats - 1e-6:
        for o, v in pattern:
            if t + o < beats - 1e-6:
                out.append((start + t + o, v))
        t += cycle
    return out


def clock_pattern(vel=(1.0, 0.7, 0.8)):
    return [(CLOCK[0], vel[0]), (CLOCK[1], vel[1]), (CLOCK[2], vel[2]), (2 + CLOCK[0], vel[0] * 0.9), (2 + CLOCK[1], vel[1]), (2 + CLOCK[2], vel[2])]
