#!/usr/bin/env python3
"""Master ElevenLabs voice takes (48 kHz 16-bit PCM) into game voice stems.

trim (-45 dB re. peak, 10 ms pre-roll) -> 60 ms head / 180 ms tail -> soxr 44.1 kHz -> role chain
-> two-pass loudnorm (-18 LUFS, -2.0 dBTP (Vorbis headroom; delivered files <= -1.5), linear) -> 24-bit WAV master + mono Ogg Vorbis.
usage: master_vo.py ROLE IN.wav OUT_STEM [--q 4]
"""
import json, subprocess, sys
import numpy as np, soundfile as sf
FILTERS = {
    "narrator": "highpass=f=60,equalizer=f=250:t=q:w=1.2:g=-1.0,equalizer=f=4500:t=q:w=1.5:g=0.8,"
                "acompressor=threshold=-24dB:ratio=2:attack=15:release=200:makeup=1",
    "control": "highpass=f=150,lowpass=f=11000,equalizer=f=2800:t=q:w=1.0:g=1.5,"
               "equalizer=f=400:t=q:w=1.2:g=-2.0,aecho=0.9:0.7:17|29:0.10|0.06,"
               "acompressor=threshold=-24dB:ratio=3:attack=8:release=150:makeup=1",
}
HEAD, TAIL = 0.06, 0.18

def trim(path, tmp):
    y, sr = sf.read(path, dtype="float32")
    env = np.abs(y); th = env.max() * 10 ** (-45 / 20)
    idx = np.where(env > th)[0]
    s = max(0, idx[0] - int(0.01 * sr)); e = min(len(y), idx[-1] + int(0.04 * sr))
    seg = y[s:e].copy()
    n = int(0.005 * sr); seg[:n] *= np.linspace(0, 1, n); m = int(0.02 * sr); seg[-m:] *= np.linspace(1, 0, m)
    out = np.concatenate([np.zeros(int(HEAD * sr), np.float32), seg, np.zeros(int(TAIL * sr), np.float32)])
    sf.write(tmp, out, sr, subtype="FLOAT")
    return {"trim_start_s": round(s / sr, 3), "trim_end_s": round(e / sr, 3), "source_s": round(len(y) / sr, 3)}

def master(role, src, stem, q="4", tp="-2.0"):
    tmp = stem + ".trim.wav"; info = trim(src, tmp)
    chain = f"aresample=44100:resampler=soxr,{FILTERS[role]}"
    p = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", tmp, "-af", f"{chain},loudnorm=I=-18:TP={tp}:LRA=7:print_format=json", "-f", "null", "-"], capture_output=True, text=True).stderr
    m = json.loads(p[p.rindex("{"):p.rindex("}") + 1])
    ln = (f"loudnorm=I=-18:TP={tp}:LRA=7:measured_I={m['input_i']}:measured_TP={m['input_tp']}:measured_LRA={m['input_lra']}:"
          f"measured_thresh={m['input_thresh']}:offset={m['target_offset']}:linear=true")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", tmp, "-af", f"{chain},{ln}", "-ac", "1", "-ar", "44100", "-c:a", "pcm_s24le", stem + ".master.wav"], check=True)
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", stem + ".master.wav", "-c:a", "libvorbis", "-q:a", q, "-map_metadata", "-1", stem + ".ogg"], check=True)
    import os; os.remove(tmp)
    return {**info, "chain": chain, "loudnorm_first_pass": m, "vorbis_q": q, "true_peak_target": tp}

if __name__ == "__main__":
    q = sys.argv[sys.argv.index("--q") + 1] if "--q" in sys.argv else "4"
    tp = sys.argv[sys.argv.index("--tp") + 1] if "--tp" in sys.argv else "-2.0"
    print(json.dumps(master(sys.argv[1], sys.argv[2], sys.argv[3], q, tp)))
