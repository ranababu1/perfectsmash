# Audio QC report (2026-11-10)

All checks run on the box against the delivered files on `assets`.

## Per-file QC (source/produce_music.py, source/produce_sfx.py)

Every file is decoded after encoding and measured: integrated loudness, true peak (4x oversampled), sample peak, clipped samples, DC offset, lead and tail silence, phone-band energy share, and for loops the seam test. Results per file are in `cue_sheet.json`.

- Music, 55 cues: integrated loudness -16.25 to -15.97 LUFS (cinematic scores -16.60 to -16.49, critical layers -18.98 to -18.97 by design), true peak -7.81 to -1.20 dBTP, 0 clipped samples, DC under 0.0003.
- Music loops, 26 files: wrap error equals the codec error at an internal boundary of the same material within 1 dB in every file (for example HLX-MUS-GAMEPLAY-TENSION -30.0 dB at the wrap, -30.3 dB at the internal boundary); high-frequency delta at the join -0.56 to +0.06 dB, so no click. Render periodicity before encoding about -127 dB.
- SFX and ambience, 190 files: 0 clipped, true peak at or below -1.06 dBTP, DC under 0.0005, durations 0.09 to 4.0 s (ambience 48 to 56 s), at most 1 ms lead-in, momentary loudness within about 0.7 dB of each family target. 26 loops (20 ambience, 3 travel, 3 alarm) all pass the seam test.
- Stem sums (source/qc_extra.py): critical layer plus tension or combat loop with the bed lowered 3 dB: -16.0 LUFS, -1.68 to -4.31 dBTP.

## Manifest validator

`python3 assets/tools/validate_asset_manifest.py --quiet --loudness`

```
entries: 849 checked, 849 present, 280.0 MB
warnings: 3
PASS: structure, ids, paths and deep file checks valid
```

The 3 warnings: SHR-SFX-IMPACT_COMPOSITE-02, -03, -04 measure 1.2 dB louder in ffmpeg ebur128 than the recorded value (short 1 s clips with silence gating; the in-house BS.1770 meter and ffmpeg gate the final block differently). Music and ambience match exactly.

Update (integration stream, 2026-11-10): the recorded `loudness_lufs` of SHR-SFX-IMPACT_COMPOSITE-02, -03 and -04 is now the ffmpeg ebur128 value (-22.0, -22.3 and -21.7 LUFS; was -23.17, -23.54 and -22.87), so the validator no longer warns. The audio files are unchanged.

## Godot 4.7.2 import and load (temp copy of the clone, /tmp/tfj-audio-godot/project)

```
== 4.7.2.stable.official.ed1daf0bf
== /opt/tfj-tools/bin/godot --headless --path /tmp/tfj-audio-godot/project --import
import rc=0
== load_check.gd
LOADCHECK loaded 857 entries (11 unlisted scenes/resources), 0 failed, by type {"AudioStreamOggVorbis":233,"AudioStreamWAV":13,"CompressedTexture2D":592,"FontFile":8,"PackedScene":11}
== audio_check.gd
AUDIOCHECK 245 ok, 0 failed, 52 loop entries set loop=true with loop_offset
```

The import printed `Failed decoding WebP image` errors for animated WebP previews of another stream (assets/vfx/previews/); none concern audio files. `audio_check.gd` loads every entry of `manifest_parts/audio.json`, compares Godot's stream length with `duration_seconds` (all within 0.02 s) and sets `loop` and `loop_offset` on every loop entry. It cannot judge the seam by ear; the seam evidence is the decoded-file test above.
