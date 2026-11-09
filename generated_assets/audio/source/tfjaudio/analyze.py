"""Technical QC: loudness, true peak, DC, clipping, silence padding, loop seams, spectrograms."""
import json
import subprocess
import numpy as np
import soundfile as sf
from scipy.signal import stft
from .dsp import SR, true_peak_db, db, hp
from .song import lufs


_KB1 = ([1.53512485958697, -2.69169618940638, 1.19839281085285], [1.0, -1.69065929318241, 0.73248077421585])
_KB2 = ([1.0, -2.0, 1.0], [1.0, -1.99004745483398, 0.99007225036621])


def momentary_curve(x):
    """BS.1770 momentary loudness (400 ms window, 10 ms hop) in LUFS."""
    from scipy.signal import lfilter
    if x.ndim == 1:
        x = x[:, None]
    w = int(0.4 * SR)
    if x.shape[0] < w:
        x = np.concatenate([x, np.zeros((w - x.shape[0], x.shape[1]))])
    y = lfilter(*_KB2, lfilter(*_KB1, x, axis=0), axis=0)
    p = np.sum(y ** 2, 1)
    c = np.concatenate([[0], np.cumsum(p)])
    hop = int(0.01 * SR)
    idx = np.arange(0, x.shape[0] - w + 1, hop)
    ms = (c[idx + w] - c[idx]) / w
    return -0.691 + 10 * np.log10(ms + 1e-20)


def momentary_max(x):
    return float(momentary_curve(x).max())


def _hf_peak_db(seg, centre, sr=SR):
    h = hp(seg.mean(1), 6000, sr=sr)
    w = int(0.004 * sr)
    e = np.convolve(h ** 2, np.ones(w) / w, mode='same')
    return 10 * np.log10(e[centre - w: centre + w].max() + 1e-14)


def seam_metrics(x, ref=None, mid_ref=None, sr=SR):
    """Loop-wrap checks. x: the loop file (decoded). ref: the continuous signal across the
    wrap from the master render (end of cycle -> start of next cycle), same length 2k.
    mid_ref: (start, continuous_segment) to measure codec error away from the wrap."""
    k = int(0.15 * sr)
    joined = np.concatenate([x[-k:], x[:k]], 0)
    out = {}
    s = int(0.2 * sr)
    def spec(seg):
        mag = np.abs(np.fft.rfft(seg.mean(1) * np.hanning(seg.shape[0])))
        bands = np.array_split(mag, 48)
        return 20 * np.log10(np.array([b.mean() for b in bands]) + 1e-9)
    out['spectral_delta_db'] = round(float(np.mean(np.abs(spec(x[-s:]) - spec(x[:s])))), 2)
    if ref is not None:
        err = joined - ref
        rms = np.sqrt(np.mean(ref ** 2)) + 1e-12
        out['wrap_error_db'] = round(float(20 * np.log10(np.sqrt(np.mean(err ** 2)) / rms + 1e-12)), 1)
        out['wrap_hf_delta_db'] = round(float(_hf_peak_db(joined, k, sr) - _hf_peak_db(ref, k, sr)), 2)
        if mid_ref is not None:
            st, seg = mid_ref
            e2 = x[st:st + seg.shape[0]] - seg
            out['mid_error_db'] = round(float(20 * np.log10(np.sqrt(np.mean(e2 ** 2)) / (np.sqrt(np.mean(seg ** 2)) + 1e-12) + 1e-12)), 1)
        out['seamless'] = bool(out['wrap_hf_delta_db'] < 1.5 and (mid_ref is None or out['wrap_error_db'] <= out['mid_error_db'] + 3))
    return out


def periodicity_error(full, nb, seconds=3.0):
    """In a 2-cycle render, compare cycle start (at nb) with the next cycle start (at 2nb)."""
    k = int(seconds * SR)
    a = full[nb:nb + k]
    b = full[2 * nb:2 * nb + k]
    if b.shape[0] < k:
        k = b.shape[0]
        a = a[:k]
    err = np.sqrt(np.mean((a - b) ** 2))
    ref = np.sqrt(np.mean(a ** 2)) + 1e-12
    return float(20 * np.log10(err / ref + 1e-12))


def qc(x, loop=False, kind='music', ref=None, mid_ref=None):
    peak = float(db(np.abs(x).max()))
    out = {
        'samples': int(x.shape[0]), 'seconds': round(x.shape[0] / SR, 3), 'channels': int(x.shape[1]),
        'lufs_i': round(lufs(x), 2), 'true_peak_dbtp': round(true_peak_db(x), 2), 'sample_peak_dbfs': round(peak, 2),
        'dc_offset': [round(float(x[:, c].mean()), 6) for c in range(x.shape[1])],
        'clipped_samples': int(np.sum(np.abs(x) >= 0.999)),
    }
    a = np.abs(x).max(1)
    thr = 10 ** (-60 / 20)
    nz = np.where(a > thr)[0]
    out['lead_silence_ms'] = round(float(nz[0] / SR * 1000), 1) if nz.size else None
    out['tail_silence_ms'] = round(float((x.shape[0] - 1 - nz[-1]) / SR * 1000), 1) if nz.size else None
    if kind == 'sfx':
        out['momentary_max_lufs'] = round(momentary_max(x), 2)
    if loop:
        out['seam'] = seam_metrics(x, ref, mid_ref)
    # phone-speaker relevance: share of energy 300 Hz - 8 kHz
    mono = x.mean(1)
    spec = np.abs(np.fft.rfft(mono[: min(len(mono), SR * 30)])) ** 2
    f = np.fft.rfftfreq(min(len(mono), SR * 30), 1 / SR)
    tot = spec.sum() + 1e-12
    out['phone_band_energy_pct'] = round(float(spec[(f >= 300) & (f <= 8000)].sum() / tot * 100), 1)
    return out


def decode(path, loop=False):
    """Read a game file and return it at 48 kHz for analysis (plus native rate and length)."""
    x, sr = sf.read(path, always_2d=True)
    n_native = x.shape[0]
    if sr != SR:
        from scipy.signal import resample, resample_poly
        if loop:
            x = resample(x, int(round(n_native * SR / sr)), axis=0)
        else:
            x = resample_poly(x, 160, 147, axis=0)
    return x, sr, n_native


def spectrogram_png(x, path, title, width=10, height=3.2):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    mono = x.mean(1)
    fig = plt.figure(figsize=(width, height), dpi=80)
    ax1 = fig.add_axes([0.06, 0.70, 0.92, 0.2])
    ax2 = fig.add_axes([0.06, 0.12, 0.92, 0.55])
    step = max(1, len(mono) // 4000)
    env = np.abs(mono[: len(mono) // step * step]).reshape(-1, step).max(1)
    tt = np.arange(env.shape[0]) * step / SR
    ax1.fill_between(tt, -env, env, color='#2bb8c9', lw=0)
    ax1.set_xlim(0, len(mono) / SR)
    ax1.set_ylim(-1, 1)
    ax1.axis('off')
    nper = 2048 if len(mono) > SR * 3 else 512
    f, t, Z = stft(mono, SR, nperseg=nper, noverlap=nper * 3 // 4)
    S = 20 * np.log10(np.abs(Z) + 1e-9)
    ax2.pcolormesh(t, f, S, vmin=S.max() - 90, vmax=S.max(), shading='auto', cmap='magma')
    ax2.set_yscale('symlog', linthresh=200)
    ax2.set_ylim(30, 20000)
    ax2.set_xlabel('s', fontsize=7)
    ax2.tick_params(labelsize=6)
    fig.suptitle(title, fontsize=8, x=0.06, ha='left', y=0.98)
    fig.savefig(path, facecolor='#111418')
    plt.close(fig)
    # quantise to keep file small
    from PIL import Image
    im = Image.open(path).convert('RGB').quantize(colors=96)
    im.save(path, optimize=True)
