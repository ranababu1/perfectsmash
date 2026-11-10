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
    # strict reference: encode body, body, body back to back with the same encoder settings and measure
    # the codec error at the internal boundary (identical material, no file wrap)
    import subprocess
    tile = np.concatenate([g, g, g], 0)
    sf.write('/tmp/tfj_tile.wav', np.clip(tile, -1, 1), GAME_SR, subtype='FLOAT')
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', '/tmp/tfj_tile.wav', '-c:a', 'libvorbis', '-q:a', '6', '/tmp/tfj_tile.ogg'], check=True)
    dt, _ = sf.read('/tmp/tfj_tile.ogg', always_2d=True)
    nb = g.shape[0]
    err = dt[nb - k: nb + k] - ref
    s['tile_boundary_error_db'] = round(float(20 * np.log10(np.sqrt(np.mean(err ** 2)) / (np.sqrt(np.mean(ref ** 2)) + 1e-12))), 1)
    s['seamless'] = bool(s['wrap_hf_delta_db'] < 1.5 and s['wrap_error_db'] <= max(s['mid_error_db'], s['tile_boundary_error_db']) + 3)
    d['seam'] = s
    json.dump(d, open(f, 'w'), indent=1)
    out['seams'][d['id']] = s
    print('seam', d['id'], s, flush=True)
for code in ['HLX', 'VTA', 'NVG', 'CVT', 'MRD']:
    paths = {p.split('/')[-1]: p for p in glob.glob(f'{REPO}/assets/audio/music/*/{code.lower()}_mus_*.ogg')}
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
        r = {'samples_equal': bool(L.shape[0] == B.shape[0])}
        for duck in (0, 3, 4):
            m48 = resample_poly(L[:n] + B[:n] * 10 ** (-duck / 20), 160, 147, axis=0)
            r[f'bed_minus_{duck}dB'] = {'sum_true_peak_dbtp': round(true_peak_db(m48), 2), 'sum_lufs': round(lufs(m48), 2)}
        out['stems'][f'{code}-MUS-CRITICAL_LAYER-01 + {code}-MUS-{other.upper()}'] = r
        print('stem', code, other, r, flush=True)
json.dump(out, open('/workspace/tfj-scratch/qc_extra.json', 'w'), indent=1)
