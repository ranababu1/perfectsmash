#!/usr/bin/env python3
"""Temporal: First Jump narration renderer (phase 1 samples; same code renders the full package).

Reads slide text verbatim from data/cinematics.json (main), applies only a pronunciation map to
the text sent to the model (the subtitle text is never changed), synthesises sentence by sentence
with Kokoro-82M v1.0 (Apache-2.0) through kokoro-onnx, inserts directed pauses, then masters with
ffmpeg: voice EQ and gentle compression, Control treatment, two-pass EBU R128 loudnorm, 44.1 kHz
mono Ogg Vorbis for Godot plus an MP3 listening copy.

Deterministic: same text + voice recipe + settings = same audio, so single lines can be re-rendered.

usage: render_vo.py --cinematics data/cinematics.json --out DIR --voices voices.json \
           --job ID:SEQUENCE:SLIDE[,SLIDE...]:VOICE_KEY [--job ...] [--stitch NAME:ID,ID,...]
"""
import argparse, json, re, subprocess, sys, tempfile
from pathlib import Path
import numpy as np
import soundfile as sf
from kokoro_onnx import Kokoro

SR_MODEL = 24000
# Spoken form for the model only. Subtitles stay exactly as written.
PRONUNCIATION = {
    "2149": "twenty one forty-nine", "2104": "twenty one oh four", "2100": "twenty one hundred",
    "2096": "twenty ninety-six", "2092": "twenty ninety-two", "2089": "twenty eighty-nine",
    "2041": "twenty forty-one", "AURA": "Aura", "VITA": "Veeta",
}
# Pause design in seconds (documentary pacing). Ellipses are countdown beats.
GAP_SENTENCE = 0.42
GAP_BEFORE_LAST = 0.62
GAP_ELLIPSIS = 0.72
HEAD = 0.06
TAIL = 0.18
SLIDE_GAP_STITCH = 1.1

FILTERS = {
    # Clean documentary voice: rumble cut, slight warmth, light glue compression.
    "narrator": "highpass=f=70,equalizer=f=180:t=q:w=1.0:g=1.0,equalizer=f=3500:t=q:w=1.2:g=1.0,"
                "acompressor=threshold=-22dB:ratio=2.2:attack=12:release=180:makeup=1",
    # Control: thinner band, presence lift and a very short synthetic room, kept subtle.
    "control": "highpass=f=150,lowpass=f=10500,equalizer=f=2800:t=q:w=1.0:g=1.5,"
               "equalizer=f=400:t=q:w=1.2:g=-2.0,aecho=0.9:0.7:17|29:0.10|0.06,"
               "acompressor=threshold=-24dB:ratio=3:attack=8:release=150:makeup=1",
}
TARGET_LUFS = -18.0
TRUE_PEAK = -1.5


def spoken(text: str) -> str:
    for k, v in PRONUNCIATION.items():
        text = re.sub(rf"\b{re.escape(k)}\b", v, text)
    return text


def pieces(text: str):
    """Split a slide into sentences; ellipsis beats become their own pieces."""
    out = []
    for chunk in re.split(r"(?<=\.\.\.)\s+", text.strip()):
        parts = re.split(r"(?<=[.!?])\s+(?=[A-Z0-9])", chunk) if not chunk.endswith("...") else [chunk]
        for p in parts:
            p = p.strip()
            if p:
                out.append(p)
    return out


def trim(a: np.ndarray, thresh_db=-48.0) -> np.ndarray:
    env = np.abs(a)
    th = 10 ** (thresh_db / 20) * max(1e-9, env.max())
    idx = np.where(env > th)[0]
    if idx.size == 0:
        return a
    s = max(0, idx[0] - int(0.01 * SR_MODEL))
    e = min(len(a), idx[-1] + int(0.04 * SR_MODEL))
    return a[s:e]


def fade(a, sec_in=0.008, sec_out=0.03):
    n_in, n_out = int(sec_in * SR_MODEL), int(sec_out * SR_MODEL)
    a = a.copy()
    a[:n_in] *= np.linspace(0, 1, n_in)
    a[-n_out:] *= np.linspace(1, 0, n_out)
    return a


def voice_style(k: Kokoro, recipe: dict):
    style = None
    for name, w in recipe["mix"].items():
        s = k.get_voice_style(name) * float(w)
        style = s if style is None else style + s
    return style


def synth_slide(k, text, recipe):
    style = voice_style(k, recipe)
    sents = pieces(text)
    buf = [np.zeros(int(HEAD * SR_MODEL), np.float32)]
    for i, s in enumerate(sents):
        a, sr = k.create(spoken(s), voice=style, speed=recipe["speed"], lang=recipe["lang"])
        assert sr == SR_MODEL
        buf.append(fade(trim(a.astype(np.float32))))
        if i < len(sents) - 1:
            gap = GAP_ELLIPSIS if s.endswith("...") else (GAP_BEFORE_LAST if i == len(sents) - 2 and len(sents) > 2 else GAP_SENTENCE)
            buf.append(np.zeros(int(gap * SR_MODEL), np.float32))
    buf.append(np.zeros(int(TAIL * SR_MODEL), np.float32))
    return np.concatenate(buf), sents


def master(raw: Path, out_stem: Path, role: str) -> dict:
    chain = FILTERS[role]
    probe = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", str(raw), "-af",
                            f"aresample=44100:resampler=soxr,{chain},loudnorm=I={TARGET_LUFS}:TP={TRUE_PEAK}:LRA=9:print_format=json",
                            "-f", "null", "-"], capture_output=True, text=True).stderr
    m = json.loads(probe[probe.rindex("{"):probe.rindex("}") + 1])
    ln = (f"loudnorm=I={TARGET_LUFS}:TP={TRUE_PEAK}:LRA=9:measured_I={m['input_i']}:measured_TP={m['input_tp']}:"
          f"measured_LRA={m['input_lra']}:measured_thresh={m['input_thresh']}:offset={m['target_offset']}:linear=true")
    wav = out_stem.with_suffix(".master.wav")
    subprocess.run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-i", str(raw), "-af",
                    f"aresample=44100:resampler=soxr,{chain},{ln}", "-ac", "1", "-ar", "44100",
                    "-c:a", "pcm_s24le", str(wav)], check=True)
    subprocess.run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-i", str(wav), "-c:a", "libvorbis",
                    "-q:a", "5", str(out_stem.with_suffix(".ogg"))], check=True)
    subprocess.run(["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-i", str(wav), "-c:a", "libmp3lame",
                    "-b:a", "128k", str(out_stem.with_suffix(".mp3"))], check=True)
    return {"ffmpeg_chain": chain, "loudnorm_first_pass": m}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cinematics", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--voices", required=True)
    ap.add_argument("--model", default="models/kokoro-v1.0.onnx")
    ap.add_argument("--voicepack", default="models/voices-v1.0.bin")
    ap.add_argument("--job", action="append", default=[])
    ap.add_argument("--stitch", action="append", default=[])
    args = ap.parse_args()
    seqs = {s["id"]: s for s in json.load(open(args.cinematics))["sequences"]}
    voices = json.load(open(args.voices))
    k = Kokoro(args.model, args.voicepack)
    out = Path(args.out); out.mkdir(parents=True, exist_ok=True)
    tmp = Path(tempfile.mkdtemp())
    log, raws = {}, {}
    for job in args.job:
        jid, seq, slides, vkey = job.split(":")
        recipe = voices[vkey]
        parts, texts = [], []
        for n in [int(x) for x in slides.split(",")]:
            slide = seqs[seq]["slides"][n - 1]
            a, sents = synth_slide(k, slide["subtitle"], recipe)
            parts.append(a); texts.append({"sequence": seq, "slide": n, "speaker": slide["speaker"], "subtitle": slide["subtitle"],
                                           "spoken_input": [spoken(s) for s in sents]})
            parts.append(np.zeros(int(SLIDE_GAP_STITCH * SR_MODEL), np.float32))
        audio = np.concatenate(parts[:-1])
        raw = tmp / f"{jid}.wav"; sf.write(raw, audio, SR_MODEL, subtype="FLOAT")
        raws[jid] = (audio, recipe["role"])
        info = master(raw, out / jid, recipe["role"])
        log[jid] = {"voice_key": vkey, "recipe": recipe, "lines": texts, **info}
    for st in args.stitch:
        name, ids = st.split(":")
        segs = []
        for jid in ids.split(","):
            segs += [raws[jid][0], np.zeros(int(SLIDE_GAP_STITCH * SR_MODEL), np.float32)]
        raw = tmp / f"{name}.wav"; sf.write(raw, np.concatenate(segs[:-1]), SR_MODEL, subtype="FLOAT")
        log[name] = {"stitched_from": ids.split(","), **master(raw, out / name, raws[ids.split(",")[0]][1])}
    json.dump(log, open(out / "render_log.json", "w"), indent=1)


if __name__ == "__main__":
    sys.exit(main())
