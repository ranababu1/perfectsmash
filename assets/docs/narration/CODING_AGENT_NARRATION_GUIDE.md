# Coding agent guide — cinematic narration

The narration package is in place: 50 voice lines across 12 cinematics, one music bed per cinematic, duck envelopes and mixed references. **The game does not play any of it yet.** This guide covers the integration. Imran has approved changing `CinematicPlayer` so that **each slide holds until its voice line ends, plus a tail**.

**On `main`:** the full package lives under `assets/audio/voice/` and `assets/audio/music/cinematic/`, including the Kokoro review samples, every mix-reference ogg and mp3, and the Control showcase. Gameplay code and `data/cinematics.json` are unchanged; the player still ignores `slide.voice` until the wiring in this guide is done.


Source of truth for every number below: [`NARRATION_MANIFEST.json`](NARRATION_MANIFEST.json). It maps each file to its cinematic id and slide index, with duration, subtitle sync points, voice and text.

## 1. Paths and slide mapping

| Cinematic id (`data/cinematics.json`) | Voice folder | Voice files (slide N → `_NN`) | Music bed | Duck envelope |
|---|---|---|---|---|
| opening | `assets/audio/voice/opening/` | `gam_vo_opening_01..08.ogg` | `music/cinematic/gam_mus_cine_opening_bed.ogg` | `gam_mus_cine_opening_bed.duck_env.json` |
| ch01_intro / ch01_outro | `voice/helix/` | `hlx_vo_intro_01..03`, `hlx_vo_outro_01..03` | `hlx_mus_cine_intro_bed`, `hlx_mus_cine_outro_bed` | `<bed>.duck_env.json` |
| ch02_intro / ch02_outro | `voice/vita/` | `vta_vo_intro_01..05`, `vta_vo_outro_01..04` | `vta_mus_cine_intro_bed`, `vta_mus_cine_outro_bed` | 〃 |
| ch03_intro / ch03_outro | `voice/nova_grid/` | `nvg_vo_intro_01..03`, `nvg_vo_outro_01..03` | `nvg_mus_cine_intro_bed`, `nvg_mus_cine_outro_bed` | 〃 |
| ch04_intro / ch04_outro | `voice/civitas/` | `cvt_vo_intro_01..03`, `cvt_vo_outro_01..04` | `cvt_mus_cine_intro_bed`, `cvt_mus_cine_outro_bed` | 〃 |
| ch05_intro | `voice/meridian/` | `mrd_vo_intro_01..03` | `mrd_mus_cine_intro_bed` | 〃 |
| finale | `voice/finale/` | `gam_vo_finale_01..07` | `gam_mus_cine_finale_bed` | 〃 |
| teaser_2041 | `voice/teaser_2041/` | `gam_vo_teaser_2041_01..04` | `gam_mus_cine_teaser_2041_bed` | 〃 |

- Voice folders are under `assets/audio/voice/`; beds and envelopes are under `assets/audio/music/cinematic/`.
- `slide_index` in the manifest is 0-based, matching `sequence.slides[i]`. The file suffix is 1-based (`_01` is slide index 0).
- The simplest wiring is to set each slide's optional `voice` field in `data/cinematics.json` to `res://assets/audio/voice/<folder>/<file>.ogg`. Do the same for a per-sequence `music` path to the bed. `CinematicCatalog` already parses both fields.
- If assets get copied into `res://assets/`, keep the same names.
- Reference renders of the intended result: `music/cinematic/*_mix_ref.mp3` (and `.ogg`). These are for review only; never play them in game.

## 2. The player currently ignores `voice`

`scripts/ui/cinematic/cinematic_player.gd` states that "the player never plays voice audio (slide.voice is ignored on purpose)". Slides advance after `CinematicCatalog.Slide.reading_seconds()`, which is `max(3.5, words / 2.5 + 1.2)` unless `duration` is set. That is shorter than most voiced lines, so playing voice without changing the timing would cut lines off.

## 3. Slide timing (approved change)

- On `_show_stage(i)`, if the slide has a voice stream, play it on a dedicated `AudioStreamPlayer` on bus **Voice**.
- Set the stage time to **voice length + tail**:
  - tail **1.2 s** by default;
  - **2.0–3.0 s** where the manifest timeline shows a longer gap (dramatic beats). Use `timeline.gaps_s` per cinematic, or `recommended_slide_seconds` as a floor.
- Advance when both the stage time has elapsed and the voice has finished (`finished` signal). The voice must never be cut off by the auto-advance.
- Slides without a voice keep today's reading-time behaviour.
- **Tap or accept (advance) during a voiced slide:** stop the current line with a short fade (about 80 ms) and show the next slide. Keep the existing 0.35 s tap cooldown.
- The end card stays at `END_CARD_SECONDS` (4 s). Beds have a musical hit near the end card plus a tail of up to about 8 s, so fade the bed over the end card (or on `finished`).

## 4. Voice bus

- Add `Voice` to `default_bus_layout.tres`, sending to Master. Volume 0 dB: files are already at −18 LUFS integrated and −1.5 dBTP or lower.
- Optionally add a gentle limiter at −1 dBTP on Master.
- Expose a separate voice volume in settings if the settings screen has audio sliders.

## 5. Music under voice (ducking)

- **Preferred:** play the cinematic's bed (not the chapter theme) when a voiced sequence starts. Then either:
  - apply its `.duck_env.json`: `gain_db` every `hop_s` = 0.01 s, timed from the start of the bed, built for the default timeline in the manifest; or
  - when the real timing differs (taps, device latency), duck live: `MusicDirector.duck(9.0, 0.12)` when a line starts and `duck(0.0, 0.6)` 0.25 s after it ends. This matches the envelope (attack 120 ms, hold 250 ms, release 600 ms, depth 9 dB).
- `MusicDirector.duck()` exists but nothing calls it yet. It is the narration duck. The separate 3 dB critical-layer offset in CODING_AGENT_HANDOFF.md is unrelated.
- Beds are mastered at −16.5 LUFS un-ducked, so they sit with the other cinematic scores. With the 9 dB duck, the voice lands about 10–11 LU above the music, as measured on the mix references.
- **Bed timing is built around the default timeline.** Each bed's hits (end-card hit, the outro "timeline shift", finale 2041 hit, teaser "Season two" hit) are placed at the timeline times in the manifest.
  - If the player holds each slide for `voice + gap` as listed, starting the bed with the first slide minus `pre_roll_s`, the music lines up.
  - If the user taps ahead, the bed simply runs ahead; this is acceptable.
  - For exact sync, start voice line N at `timeline.voice_start_s` relative to bed start.

## 6. Subtitle sync

- Show the subtitle when the slide appears (as now). The whole slide text stays on screen while its line plays.
- `subtitle_sync.start_s` and `end_s` are the first and last word times inside each voice file.
- `subtitle_sync.sentences[]` gives per-sentence start and end times, from forced word timestamps (faster-whisper word timing, about ±0.1 s), for a future karaoke or sentence-by-sentence reveal.
- Subtitles must stay verbatim. Do not change `data/cinematics.json` text to match the audio; the audio already matches the text.

## 7. Skip and stop

- **Skip button / `ui_cancel` (Android back):**
  - stop the voice immediately (about 50 ms fade);
  - restore any duck: `duck(0)`;
  - let the app root restore its own music as today;
  - emit `finished(id, true)`.
- **App pause / backgrounding** (`NOTIFICATION_APPLICATION_PAUSED`): pause the voice and bed and resume together. If the player is freed, stop both.
- Never let a voice line outlive the cinematic, for example by an exit to the menu while a line is playing.

## 8. Preloading

- Voice files are small, 80–96 kbps mono, about 50–200 KB each.
- On `play(sequence)`, preload all slide voices and the bed with `ResourceLoader.load_threaded_request` before showing slide 1, or `load()` them in `play()`. Each sequence is under about 2.5 MB including the bed.
- Do not stream from disk mid-slide on low-end Android.
- Keep Vorbis (`.ogg`). Godot imports these as AudioStreamOggVorbis with loop off. Make sure loop stays **off** for voice and beds.

## 9. Expected durations

Per-line durations are in the manifest; the per-cinematic summary table is appended below by the build. Tests should assert that each voiced slide's stage time is at least the voice length, not a hard-coded number.

## 10. Tests to add or update

- `tests/test_cinematics.gd`: every `voice` path exists and loads, and slide count matches voice count per voiced sequence.
- Player tick test: a voiced slide does not advance before the voice ends, tap advances and stops the voice, and skip stops everything.
- Bus test: `Voice` exists.

## 11. Measured durations (this package)

| Cinematic | Voice lines | Voice runtime | Mix reference | Recommended total (voices + tails + end card) |
|---|---|---|---|---|
| `opening` | 8 | 90.6 s | 128.0 s | 104.2 s |
| `ch01_intro` | 3 | 31.8 s | 51.7 s | 39.4 s |
| `ch01_outro` | 3 | 33.5 s | 55.0 s | 41.1 s |
| `ch02_intro` | 5 | 40.2 s | 65.8 s | 50.2 s |
| `ch02_outro` | 4 | 31.9 s | 55.0 s | 40.7 s |
| `ch03_intro` | 3 | 26.7 s | 49.9 s | 34.3 s |
| `ch03_outro` | 3 | 28.4 s | 50.5 s | 36.0 s |
| `ch04_intro` | 3 | 29.8 s | 55.4 s | 37.4 s |
| `ch04_outro` | 4 | 33.3 s | 56.2 s | 42.1 s |
| `ch05_intro` | 3 | 27.3 s | 47.1 s | 34.9 s |
| `finale` | 7 | 48.8 s | 85.1 s | 61.2 s |
| `teaser_2041` | 4 | 25.2 s | 43.4 s | 34.0 s |
| **Total** | **50** | **7.5 min** | | |

Recommended total uses 1.2 s tail per slide plus a 4 s end card. Use the longer gaps in `timeline.gaps_s` (2.0–3.2 s) where listed, so the real hold matches the mix-reference length.

