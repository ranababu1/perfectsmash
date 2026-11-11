"""Pace and pause metrics from the waveform (independent of ASR): speech span, longest pause (< -40 dB re. peak, 10 ms frames), words per minute over the span."""
import json, re, sys, numpy as np, soundfile as sf
refs = json.load(open(sys.argv[1])); out = {}
for f, ref in refs.items():
    y, sr = sf.read(f); hop = sr // 100; n = len(y) // hop
    e = np.sqrt(np.mean(y[:n * hop].reshape(n, hop) ** 2, 1) + 1e-12); db = 20 * np.log10(e / e.max())
    act = np.where(db > -40)[0]; a, b = act[0], act[-1]
    q = db[a:b + 1] < -40; run = best = 0
    for x in q:
        run = run + 1 if x else 0; best = max(best, run)
    words = len(re.findall(r"[A-Za-z0-9']+", re.sub(r'\b(20\d\d|21\d\d)\b', 'x x x', ref.replace('-', ' '))))
    out[f] = {'span_s': round((b - a) / 100, 2), 'max_pause_s': round(best / 100, 2), 'wpm_e': round(words / ((b - a) / 100) * 60)}
json.dump(out, open(sys.argv[2], 'w'), indent=1); print(len(out))
