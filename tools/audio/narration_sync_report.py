"""Checks a narration_sync_check.gd run against the narration manifest.

    python tools/audio/narration_sync_report.py <out dir> <id> [<id> ...]

Per voiced slide it reports:
  * line start: the bed's playback position when the line started vs the manifest timeline
    (voice_start_s; the beds' hits are written around it);
  * subtitle: when the subtitle appeared vs when speech is actually heard on the Voice bus
    (first 10 ms window above the speech threshold after the line started);
  * speech end vs the slide change (the slide must outlast the line);
  * duck: Music-bus level while the line speaks vs in the gap before the next line.
Exits 1 when a line starts more than START_TOLERANCE off the bed timeline, a subtitle is more than
SUBTITLE_TOLERANCE away from its speech, or a slide changes before its speech has ended.
"""
import array
import json
import math
import os
import sys
import wave

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
MANIFEST = os.path.join(ROOT, "assets", "docs", "narration", "NARRATION_MANIFEST.json")
WINDOW = 0.01
SPEECH_DB = -45.0
START_TOLERANCE = 0.25
SUBTITLE_TOLERANCE = 0.30


def levels(path):
    """dBFS per WINDOW for a 16-bit PCM WAV (channels averaged)."""
    with wave.open(path, "rb") as w:
        rate, channels, width = w.getframerate(), w.getnchannels(), w.getsampwidth()
        if width != 2:
            raise SystemExit(f"{path}: expected 16-bit PCM")
        data = array.array("h", w.readframes(w.getnframes()))
    if sys.byteorder == "big":
        data.byteswap()
    step = int(rate * WINDOW) * channels
    out = []
    for i in range(0, len(data) - step + 1, step):
        chunk = data[i:i + step]
        rms = math.sqrt(sum(s * s for s in chunk) / len(chunk)) / 32768.0
        out.append(20 * math.log10(rms) if rms > 1e-6 else -120.0)
    return out


def mean_db(values):
    values = [v for v in values if v > -100]
    if not values:
        return -120.0
    return 20 * math.log10(sum(10 ** (v / 20) for v in values) / len(values))


def report(out_dir, sid, cinematic):
    with open(os.path.join(out_dir, f"{sid}_events.json"), encoding="utf-8") as f:
        run = json.load(f)
    voice = levels(os.path.join(out_dir, f"{sid}_voice.wav"))
    music = levels(os.path.join(out_dir, f"{sid}_music.wav"))
    events = run["events"]
    lines = [e for e in events if e["event"] == "voice"]
    subtitles = {e["index"]: e["t"] for e in events if e["event"] == "subtitle"}
    stages = {e["index"]: e["t"] for e in events if e["event"] == "stage"}
    # The recording starts a frame or so before play(); align it on the first heard speech.
    problems = []
    print(f"\n{sid} ({run['seconds']:.1f} s)")
    print(" slide  bed@start  manifest  diff   subtitle-vs-speech  speech-end->next-slide  duck(dB)")
    slides = sorted(cinematic["slides"], key=lambda s: s["slide_index"])
    for n, line in enumerate(lines):
        i = line["index"]
        expected = slides[i]["timeline"]["voice_start_s"]
        diff = line["bed_position"] - expected
        start_w = int(line["t"] / WINDOW)
        onset_w = next((w for w in range(start_w, min(start_w + 300, len(voice))) if voice[w] > SPEECH_DB), None)
        end_t = (stages.get(i + 1, run["seconds"]))
        end_w = int(end_t / WINDOW)
        heard = [w for w in range(start_w, min(end_w, len(voice))) if voice[w] > SPEECH_DB]
        speech_end = heard[-1] * WINDOW if heard else None
        onset = onset_w * WINDOW if onset_w is not None else None
        sub_diff = subtitles.get(i, float("nan")) - onset if onset is not None else float("nan")
        tail = end_t - speech_end if speech_end is not None else float("nan")
        speaking = music[start_w + 50:(heard[-1] if heard else start_w) - 10] if heard else []
        gap_from = (heard[-1] if heard else start_w) + int(0.25 / WINDOW) + int(0.6 / WINDOW)
        gap = music[gap_from:end_w] if end_w - gap_from > 30 else []
        duck = mean_db(gap) - mean_db(speaking) if speaking and gap else float("nan")
        print(f" {i + 1:>5}  {line['bed_position']:>8.2f}  {expected:>8.2f}  {diff:+.2f}   {sub_diff:+.2f}               {tail:+.2f}                  {duck:5.1f}")
        if abs(diff) > START_TOLERANCE:
            problems.append(f"{sid}/{i + 1}: line starts {diff:+.2f} s off the bed timeline")
        if not math.isnan(sub_diff) and abs(sub_diff) > SUBTITLE_TOLERANCE:
            problems.append(f"{sid}/{i + 1}: subtitle {sub_diff:+.2f} s from its speech")
        if onset is None:
            problems.append(f"{sid}/{i + 1}: no speech heard on the Voice bus")
        if not math.isnan(tail) and tail < 0.2:
            problems.append(f"{sid}/{i + 1}: slide changed {tail:.2f} s after the speech ended")
    if len(lines) != len(slides):
        problems.append(f"{sid}: {len(lines)} lines played for {len(slides)} slides")
    return problems


def main():
    if len(sys.argv) < 3:
        raise SystemExit(__doc__)
    out_dir = sys.argv[1]
    with open(MANIFEST, encoding="utf-8") as f:
        manifest = {c["cinematic_id"]: c for c in json.load(f)["cinematics"]}
    problems = []
    for sid in sys.argv[2:]:
        problems += report(out_dir, sid, manifest[sid])
    print()
    print("\n".join(problems) if problems else "OK: every line on the bed timeline, subtitles with their speech, no line cut")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
