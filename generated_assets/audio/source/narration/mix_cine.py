#!/usr/bin/env python3
"""Cinematic voice + music assembly for the narration approval sample.

  mix_cine.py opening  --el DIR --bed BED48.wav --out DIR
  mix_cine.py showcase --el DIR --score FINALE.flac --out DIR

Places mastered voice stems on the timeline, layers sound effects into the music bed, builds a
sidechain-style ducking envelope from voice activity (look-ahead 150 ms, attack 120 ms, hold 250 ms,
release 600 ms, depth 9 dB) and writes: bed (un-ducked) and mix reference (stereo, -16 LUFS,
true peak <= -1 dBTP) as 44.1 kHz float WAV, plus the duck envelope as JSON for the engine.
deps: numpy, scipy, soundfile, soxr, pyloudnorm
"""
import argparse, json, os
import numpy as np, soundfile as sf, soxr, pyloudnorm as pyln
from scipy.ndimage import maximum_filter1d

SR = 44100
DUCK_DB, LOOK, ATT, HOLD, REL = 9.0, 0.15, 0.12, 0.25, 0.6


def load(path, ch=2):
    y, sr = sf.read(path, dtype='float64', always_2d=True)
    if sr != SR:
        y = soxr.resample(y, sr, SR, quality='VHQ')
    if ch == 2 and y.shape[1] == 1:
        y = np.repeat(y, 2, 1)
    if ch == 1:
        y = y.mean(1, keepdims=True)
    return y


def place(buf, x, t, gain_db=0.0, fade_in=0.0, fade_out=0.0):
    x = x.copy() * 10 ** (gain_db / 20)
    n = len(x)
    if fade_in: k = min(n, int(fade_in * SR)); x[:k] *= np.linspace(0, 1, k)[:, None]
    if fade_out: k = min(n, int(fade_out * SR)); x[-k:] *= np.linspace(1, 0, k)[:, None]
    i = int(round(t * SR))
    if i + n > len(buf):
        buf = np.vstack([buf, np.zeros((i + n - len(buf), buf.shape[1]))])
    buf[i:i + n] += x
    return buf


def duck_env(voice_mono, n):
    """gain (linear) per sample: 1.0 when no voice, -DUCK_DB while voice is active."""
    hop = int(0.01 * SR)
    v = np.pad(voice_mono[:n], (0, max(0, n - len(voice_mono))))
    fr = len(v) // hop + 1
    v = np.pad(v, (0, fr * hop - len(v)))
    rms = np.sqrt(np.mean(v.reshape(fr, hop) ** 2, 1) + 1e-12)
    act = (20 * np.log10(rms) > -50).astype(float)                       # stems are -18 LUFS; -50 dBFS = silence
    act = maximum_filter1d(act, int((HOLD * 2) / 0.01) + 1)              # hold, bridges short pauses
    act = np.concatenate([act[int(LOOK / 0.01):], np.zeros(int(LOOK / 0.01))])  # look-ahead
    act = np.maximum(act, np.concatenate([np.zeros(int(LOOK / 0.01)), act[:-int(LOOK / 0.01)]]))
    tgt = 10 ** (-DUCK_DB * act / 20)
    g = np.empty_like(tgt); cur = 1.0
    a_att, a_rel = np.exp(-0.01 / ATT), np.exp(-0.01 / REL)
    for i, x in enumerate(tgt):
        a = a_att if x < cur else a_rel
        cur = a * cur + (1 - a) * x; g[i] = cur
    t_fr = np.arange(fr) * hop
    return np.interp(np.arange(n), t_fr, g), g


def norm(y, lufs, tp_max):
    m = pyln.Meter(SR)
    y = y * 10 ** ((lufs - m.integrated_loudness(y)) / 20)
    tp = 20 * np.log10(np.max(np.abs(soxr.resample(y, SR, SR * 4))) + 1e-12)
    if tp > tp_max:                                                       # gentle soft-knee peak control
        lim = 10 ** (tp_max / 20) * 0.98
        y = np.tanh(y / lim) * lim
        y = y * 10 ** ((lufs - m.integrated_loudness(y)) / 20)
        tp = 20 * np.log10(np.max(np.abs(soxr.resample(y, SR, SR * 4))) + 1e-12)
    return y, round(m.integrated_loudness(y), 2), round(tp, 2)


def finish(bed, voice, out, base, lufs=-16.0, tp=-1.0, bed_lufs=None):
    n = max(len(bed), len(voice))
    bed = np.pad(bed, ((0, n - len(bed)), (0, 0))); voice = np.pad(voice, ((0, n - len(voice)), (0, 0)))
    g, g_fr = duck_env(voice[:, 0], n)
    if bed_lufs is not None:
        bed, bi, bt = norm(bed, bed_lufs, -1.5)
        sf.write(os.path.join(out, base + '_bed.wav'), bed.astype(np.float32), SR, subtype='FLOAT')
    mix = bed * g[:, None] + voice
    mix, mi, mt = norm(mix, lufs, tp)
    sf.write(os.path.join(out, base + '_mix.wav'), mix.astype(np.float32), SR, subtype='FLOAT')
    env = {'hop_s': 0.01, 'duck_db': DUCK_DB, 'look_ahead_s': LOOK, 'attack_s': ATT, 'hold_s': HOLD, 'release_s': REL,
           'gain_db': [round(float(20 * np.log10(x)), 2) for x in g_fr]}
    json.dump(env, open(os.path.join(out, base + '_duck_env.json'), 'w'))
    # voice-vs-ducked-bed check
    m = pyln.Meter(SR); act = g < 10 ** (-DUCK_DB * 0.9 / 20)
    vb = m.integrated_loudness(voice[act]) - m.integrated_loudness((bed * g[:, None])[act]) if act.sum() > SR else None
    return {'mix_lufs': mi, 'mix_tp': mt, 'voice_over_ducked_bed_lu': round(vb, 1) if vb else None, 'seconds': round(n / SR, 3)}


def opening(a):
    tl = json.load(open(os.path.join(a.el, 'timeline.json')))
    t = tl['slide_starts_s']; title = tl['title_hit_s']
    bed = load(a.bed)
    sfx = os.path.join(a.el, 'sfx')
    bed = place(bed, load(os.path.join(sfx, 'amb_ruins.wav')), t[2] - 0.5, gain_db=+14, fade_in=2.0, fade_out=3.0)
    bed = place(bed, load(os.path.join(sfx, 'charge_powerup.wav')), t[5] - 0.8, gain_db=-11, fade_in=1.5, fade_out=2.0)
    bed = place(bed, load(os.path.join(sfx, 'time_jump.wav')), title - 1.397, gain_db=-9, fade_out=1.5)
    voice = np.zeros_like(bed)
    for i, s in enumerate(t, 1):
        voice = place(voice, load(os.path.join(a.el, 'stems', f'gam_vo_opening_{i:02d}.master.wav')), s)
    r = finish(bed, voice, a.out, 'opening', bed_lufs=-16.5)
    r['sfx'] = {'amb_ruins': [t[2] - 0.5, 14], 'charge_powerup': [t[5] - 0.8, -11], 'time_jump_impact_s': title}
    return r


def showcase(a):
    sc = load(a.score); b = 60 / 66 * 4                                     # finale cue: 66 BPM, 4/4
    A = sc[int(5 * b * SR):int(11 * b * SR)]; B = sc[int(13 * b * SR):]
    xf = int(1.5 * SR); fo = np.linspace(1, 0, xf)[:, None]
    bed = np.vstack([A[:-xf], A[-xf:] * fo + B[:xf] * fo[::-1], B[xf:]])
    cut = int(52 * SR); bed = bed[:cut + int(4 * SR)]; bed[cut:] *= np.linspace(1, 0, len(bed) - cut)[:, None] ** 2
    voice = np.zeros_like(bed)
    for name, t in (('02', 2.5), ('03', 12.3), ('05', 26.7), ('07', 36.8)):
        voice = place(voice, load(os.path.join(a.el, 'stems', f'gam_vo_finale_{name}.master.wav')), t)
    r = finish(bed, voice, a.out, 'showcase')
    r['edit'] = {'source': os.path.basename(a.score), 'segments_s': [[5 * b, 11 * b], [13 * b, 'end']], 'crossfade_s': 1.5,
                 'fade_out_s': [52, 56], 'voice_starts_s': {'finale_02': 2.5, 'finale_03': 12.3, 'finale_05': 26.7, 'finale_07': 36.8}}
    return r


if __name__ == '__main__':
    p = argparse.ArgumentParser(); p.add_argument('mode'); p.add_argument('--el'); p.add_argument('--bed'); p.add_argument('--score'); p.add_argument('--out')
    a = p.parse_args(); os.makedirs(a.out, exist_ok=True)
    r = opening(a) if a.mode == 'opening' else showcase(a)
    print(json.dumps(r, indent=1))
