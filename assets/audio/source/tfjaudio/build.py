"""Render -> master (48 kHz) -> game file (44.1 kHz Ogg) -> decode -> QC -> preview, for one music cue."""
import os
import json
import time
import subprocess
import numpy as np
import soundfile as sf
from scipy.signal import resample_poly
from .dsp import SR, tp_limit, undb
from .song import trim_tail, lufs
from .analyze import qc, seam_metrics, spectrogram_png, periodicity_error
from .export import write_master, to_game_rate, GAME_SR

REPO = '/workspace/tfj-audio'
QC_DIR = '/workspace/tfj-scratch/qc'


def _ogg(y44, path, quality=6):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = path + '.tmp.wav'
    sf.write(tmp, np.clip(y44, -1, 1), GAME_SR, subtype='FLOAT')
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', tmp, '-c:a', 'libvorbis', '-q:a', str(quality), '-ar', str(GAME_SR),
                    '-map_metadata', '-1', '-fflags', '+bitexact', '-flags:a', '+bitexact', path], check=True)
    os.remove(tmp)


def produce_music(cue, song, intro=None, quality=6):
    t0 = time.time()
    cid = cue['id']
    rel = cue['path']
    out = os.path.join(REPO, rel)
    extra = {}
    k44 = int(0.15 * GAME_SR)
    if song.loop:
        mix, n = song.render()
        m = song.master(mix)
        y, (a, b) = song.finish(m, n)
        nb = b - a
        body = y[a:b]
        extra['periodicity_error_db'] = round(periodicity_error(y, nb), 1)
        gbody = to_game_rate(body, loop=True)
        if intro is not None:
            imix, _ = intro.render()
            im = intro.master(imix) * undb(song.master_gain_db)
            im = tp_limit(im, song.master_ceiling)
            ni = int(round(intro.s(intro.beats) * SR))
            xf = int(0.04 * SR)
            head = im[:ni].copy()
            w = np.linspace(0, 1, xf)[:, None]
            head[ni - xf:] = head[ni - xf:] * (1 - w) + body[nb - xf:] * w
            full = np.concatenate([head, body], 0)
            ni44 = int(round(ni * GAME_SR / SR))
            h44 = resample_poly(np.concatenate([head, body[: SR]], 0), 147, 160, axis=0)[:ni44]
            game = np.concatenate([h44, gbody], 0)
            ls48, le48 = ni, ni + nb
            ls44, le44 = ni44, ni44 + gbody.shape[0]
        else:
            full = body
            game = gbody
            ls48, le48 = 0, nb
            ls44, le44 = 0, gbody.shape[0]
        ref44 = np.concatenate([gbody[-k44:], gbody[:k44]], 0)
        # codec reference: the same-length window centred on the body midpoint (a phrase downbeat for
        # every loop here), so the wrap and the reference contain comparable material
        mid44 = gbody.shape[0] // 2 - k44
        midseg44 = gbody[mid44: mid44 + 2 * k44]
    else:
        mix, n = song.render()
        m = song.master(mix)
        y, _ = song.finish(m, n)
        full = trim_tail(y)
        mx = song.meta.get('max_seconds')
        if mx and full.shape[0] > mx * SR:
            # stingers and results must stay within the contract length: let the ring-out decay
            # faster over the last seconds (equal-power curve) instead of cutting it
            n = int(mx * SR)
            fl = int(min(3.0, mx / 3) * SR)
            full = full[:n].copy()
            full[n - fl:] *= (np.cos(np.linspace(0, np.pi / 2, fl)) ** 2)[:, None]
            # the shorter tail raises integrated loudness: normalise again to the cue target
            for _ in range(3):
                full = tp_limit(full * undb(song.master_target - lufs(full)), song.master_ceiling)
                if abs(lufs(full) - song.master_target) < 0.1:
                    break
        game = to_game_rate(full, loop=False)
    master = write_master(full, f"music/{os.path.basename(rel).replace('.ogg', '.flac')}")
    _ogg(game, out, quality)
    dec44, sr = sf.read(out, always_2d=True)
    dec48 = resample_poly(dec44, 160, 147, axis=0)
    info = qc(dec48, loop=False)
    info['samples'] = int(dec44.shape[0])
    info['sample_rate'] = int(sr)
    info['seconds'] = round(dec44.shape[0] / sr, 3)
    info['samples_match_master'] = bool(dec44.shape[0] == game.shape[0])
    info['lufs_master'] = round(lufs(full), 2)
    info['master_sample_rate'] = SR
    info['master_samples'] = int(full.shape[0])
    if song.loop:
        body_dec = dec44[ls44:le44]
        info['seam'] = seam_metrics(body_dec, ref44, (mid44, midseg44), sr=GAME_SR)
        info['loop_start_samples'] = int(ls44)
        info['loop_end_samples'] = int(le44)
        info['loop_offset_seconds'] = round(ls44 / GAME_SR, 6)
        info['master_loop_start_samples'] = int(ls48)
        info['master_loop_end_samples'] = int(le48)
    info['track_levels_lufs'] = getattr(song, 'track_report', {})
    pdir = os.path.join(REPO, 'assets/audio/previews/music')
    os.makedirs(pdir, exist_ok=True)
    title = f"{cid}  {info['seconds']} s  {info['lufs_i']} LUFS  {info['true_peak_dbtp']} dBTP" + (f"  loop {info['loop_start_samples']}-{info['loop_end_samples']} @44.1k" if song.loop else '')
    png = os.path.join(pdir, os.path.basename(rel).replace('.ogg', '.png'))
    spectrogram_png(dec48, png, title)
    from PIL import Image
    Image.open(png).convert('RGB').save(png.replace('.png', '.webp'), 'WEBP', quality=82, method=6)
    os.remove(png)
    rec = dict(cue)
    rec.update(info)
    rec.update(extra)
    rec['master'] = master
    rec['bytes'] = os.path.getsize(out)
    rec['render_seconds'] = round(time.time() - t0, 1)
    os.makedirs(QC_DIR, exist_ok=True)
    json.dump(rec, open(f'{QC_DIR}/{cid}.json', 'w'), indent=1)
    return rec
