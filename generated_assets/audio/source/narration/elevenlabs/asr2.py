"""Robust re-transcription for take selection: two faster-whisper medium.en passes per take
(condition_on_previous_text=False, temperature fallback; pass A with a vocabulary prompt of proper nouns only,
pass B without). errs_min = fewer word errors of the two (a word dropped by one decode but present in the
other is a recogniser failure, not a missing word)."""
import sys, json, os, re
sys.argv += []
from faster_whisper import WhisperModel
exec(open('evalv2.py').read().split('def norm')[0].split('import torch')[0])  # imports
src = open('evalv2.py').read()
ns = {}; exec('import re\n' + src[src.index('NUM='):src.index('refs=json.load')], ns)
norm0, wer = ns['norm'], ns['wer']
FIX = [(r'\bnov[aoi] ?grid\b', 'nova grid'), (r'\bnovagrid\b', 'nova grid'), (r'\bvita\b', 'vita')]
def norm(s):
    s = s.lower()
    for a, b in FIX: s = re.sub(a, b, s)
    return norm0(s)
PROMPT = 'Helix Systems, AURA, VITA Genomics, Nova Grid, Civitas, Meridian.'
import numpy as np, soundfile as sf
def chunks(f):
    y, sr = sf.read(f, dtype='float32')
    if y.ndim > 1: y = y.mean(1)
    y16 = y[::3] if sr == 48000 else y; sr16 = 16000
    hop = 160; fr = len(y16) // hop
    e = np.sqrt(np.mean(y16[:fr * hop].reshape(fr, hop) ** 2, 1) + 1e-12); db = 20 * np.log10(e / e.max())
    quiet = db < -40; cuts = []; run = 0
    for i, q in enumerate(quiet):
        run = run + 1 if q else 0
        if run == 30: cuts.append(i - 15)
    bounds = [0] + [c * hop for c in cuts] + [len(y16)]
    out = []
    for a, b in zip(bounds, bounds[1:]):
        seg = y16[a:b]
        if len(seg) < 0.25 * sr16 or np.abs(seg).max() < 10 ** (-35 / 20) * np.abs(y16).max(): continue
        out.append(np.concatenate([np.zeros(3200, np.float32), seg, np.zeros(3200, np.float32)]))
    return out
m = WhisperModel('medium.en', device='cpu', compute_type='int8')
refs = json.load(open(sys.argv[1])); outp = sys.argv[2]
out = json.load(open(outp)) if os.path.exists(outp) else {}
for f, ref in refs.items():
    if f in out: continue
    r = {}
    # pass A: whole file; pass B: file split at pauses (>= 0.3 s below -40 dB re. peak), each chunk decoded alone
    segs, _ = m.transcribe(f, language='en', beam_size=5, condition_on_previous_text=False, vad_filter=False)
    r['hypA'] = ' '.join(s.text for s in segs).strip(); r['errsA'] = wer(norm(ref), norm(r['hypA']))
    parts = []
    for ch in chunks(f):
        segs, _ = m.transcribe(ch, language='en', beam_size=5, condition_on_previous_text=False, vad_filter=False, initial_prompt=PROMPT)
        parts.append(' '.join(s.text for s in segs).strip())
    r['hypB'] = ' '.join(parts); r['errsB'] = wer(norm(ref), norm(r['hypB']))
    r['errs_min'] = min(r['errsA'], r['errsB']); out[f] = r
    print(f, r['errsA'], r['errsB'], flush=True)
    json.dump(out, open(outp, 'w'), indent=1)
