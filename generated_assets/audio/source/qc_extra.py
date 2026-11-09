"""Independent checks on the delivered files (run after rendering):
1. loop seams of every music loop re-measured from the delivered Ogg against the 48 kHz master
   (symmetric reference window centred on the loop midpoint);
2. stem sync: critical layer + tension loop and critical layer + combat loop summed sample-aligned,
   true peak and loudness of the sum (the layer must not push the pair into clipping);
3. summary table. Writes /workspace/tfj-scratch/qc_extra.json and updates the per-cue QC JSON seams."""
import sys, os, json, glob
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np, soundfile as sf
from tfjaudio.export import to_game_rate, GAME_SR
from tfjaudio.analyze import seam_metrics
from tfjaudio.dsp import true_peak_db
from tfjaudio.song import lufs
from scipy.signal import resample_poly
REPO = '/workspace/tfj-audio'
QC = '/workspace/tfj-scratch/qc'
out = {'seams': {}, 'stems': {}}
for f in sorted(glob.glob(f'{QC}/*.json')):
    d = json.load(open(f))
    if not d.get('loop'):
        continue
    m, _ = sf.read(d['master'], always_2d=True)
    body = m[d['master_loop_start_samples']:d['master_loop_end_samples']]
    g = to_game_rate(body, True)
    dec, _ = sf.read(f"{REPO}/{d['path']}", always_2d=True)
    bd = dec[d['loop_start_samples']:d['loop_end_samples']]
    k = int(0.15 * GAME_SR)
    ref = np.concatenate([g[-k:], g[:k]])
    mid = g.shape[0] // 2 - k
    s = seam_metrics(bd, ref, (mid, g[mid:mid + 2 * k]), sr=GAME_SR)
    d['seam'] = s
    json.dump(d, open(f, 'w'), indent=1)
    out['seams'][d['id']] = s
    print('seam', d['id'], s, flush=True)
for code in ['HLX', 'VTA', 'NVG', 'CVT', 'MRD']:
    paths = {p.split('/')[-1]: p for p in glob.glob(f'{REPO}/generated_assets/audio/music/*/{code.lower()}_mus_*.ogg')}
    lay = paths.get(f'{code.lower()}_mus_critical_layer_01.ogg')
    if not lay:
        continue
    L, _ = sf.read(lay, always_2d=True)
    for other in ('gameplay_tension', 'combat_01'):
        p = paths.get(f'{code.lower()}_mus_{other}.ogg')
        if not p:
            continue
        B, _ = sf.read(p, always_2d=True)
        n = min(L.shape[0], B.shape[0])
        mix = L[:n] + B[:n]
        m48 = resample_poly(mix, 160, 147, axis=0)
        r = {'samples_equal': bool(L.shape[0] == B.shape[0]), 'sum_true_peak_dbtp': round(true_peak_db(m48), 2), 'sum_lufs': round(lufs(m48), 2)}
        out['stems'][f'{code}-MUS-CRITICAL_LAYER-01 + {code}-MUS-{other.upper()}'] = r
        print('stem', code, other, r, flush=True)
json.dump(out, open('/workspace/tfj-scratch/qc_extra.json', 'w'), indent=1)
