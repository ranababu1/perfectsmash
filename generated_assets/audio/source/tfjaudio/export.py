"""Writers for masters (FLAC/WAV 24-bit 48 kHz) and game files (Ogg Vorbis / 16-bit WAV)."""
import os
import subprocess
import numpy as np
import soundfile as sf
from .dsp import SR

MASTERS = '/workspace/tfj-masters/audio'


def write_master(x, rel, fmt='FLAC'):
    path = os.path.join(MASTERS, rel)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    sf.write(path, np.clip(x, -1, 1), SR, subtype='PCM_24', format=fmt)
    return path


def write_ogg(x, path, quality=5):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = path + '.tmp.wav'
    sf.write(tmp, np.clip(x, -1, 1), SR, subtype='PCM_24')
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', tmp, '-c:a', 'libvorbis', '-q:a', str(quality),
                    '-map_metadata', '-1', '-fflags', '+bitexact', '-flags:a', '+bitexact', path], check=True)
    os.remove(tmp)
    return path


def write_wav16(x, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    # TPDF dither to 16 bit
    r = np.random.default_rng(1)
    d = (r.random(x.shape) - r.random(x.shape)) / 32768.0
    sf.write(path, np.clip(x + d, -1, 1), SR, subtype='PCM_16')
    return path


GAME_SR = 44100


def to_game_rate(x, loop=False):
    """48 kHz master -> 44.1 kHz game file. Loops use FFT resampling, which treats the
    signal as periodic, so the loop stays seamless at the new rate."""
    from scipy.signal import resample, resample_poly
    if loop:
        n2 = int(round(x.shape[0] * GAME_SR / SR))
        return resample(x, n2, axis=0)
    return resample_poly(x, 147, 160, axis=0)


def write_game_ogg(x, path, loop=False, quality=6):
    """Write a 44.1 kHz Ogg Vorbis game file from a 48 kHz master buffer."""
    from .dsp import true_peak_db, undb
    y = to_game_rate(x, loop)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = path + '.tmp.wav'
    sf.write(tmp, np.clip(y, -1, 1), GAME_SR, subtype='FLOAT')
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', tmp, '-c:a', 'libvorbis', '-q:a', str(quality), '-ar', str(GAME_SR),
                    '-map_metadata', '-1', '-fflags', '+bitexact', '-flags:a', '+bitexact', path], check=True)
    os.remove(tmp)
    return path, y.shape[0]


def write_game_wav16(x, path):
    y = to_game_rate(x, False)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    r = np.random.default_rng(1)
    d = (r.random(y.shape) - r.random(y.shape)) / 32768.0
    sf.write(path, np.clip(y + d, -1, 1), GAME_SR, subtype='PCM_16')
    return path, y.shape[0]
