# Cinematic narration — phase 1 proposal

Temporal: First Jump. Prepared 2026-11-11 for Imran's approval. **Phase 1 only:** research, story inventory, voice direction, production options, naming and export settings, plus short samples. The full package is **not** generated until the voice direction and the production approach are approved.

Companion files (in `generated_assets/docs/narration/` on `assets`):
- `SCRIPT_EXTRACT.md`: every slide verbatim, with speaker, timing and estimated voiced length.
- `VOICE_DIRECTION.md`: the two voices, the pronunciation sheet and the technical voice spec.
- Samples: `generated_assets/audio/voice/samples/`.

Renderer and voice recipes: `generated_assets/audio/source/narration/` (`render_vo.py`, `voices.json`, `samples_render_log.json`).

## 1. Story inventory

Source: `data/cinematics.json` on `main` (c104c06). It matches the `.srt` subtitle files line for line. All lines also appear in `docs/narrative-bible.md` except the four teaser slides.

| | Count |
|---|---|
| Cinematics | **12**: opening, 5 chapter intros, 4 chapter endings (`ch01_outro` to `ch04_outro`), finale (also the chapter 5 ending), plus the extra `teaser_2041` |
| Slides | **50** (46 without the teaser) |
| Words | **902** (5,578 characters) |
| Narrator | 27 slides, 515 words, ≈ 258 s |
| Control | 23 slides, 387 words, ≈ 227 s |
| Estimated total narration | **≈ 486 s (≈ 8.1 min)** at the sample pace; ≈ 7.7 min without the teaser |

**Control lines exist.** The data already tags 23 slides as `speaker: "control"`. These are mission instructions and system messages; the player tints them `#bfe9ff`. No other speaking character exists. AURA is a system that is described but never speaks.

**Flagged, not changed** (details in `SCRIPT_EXTRACT.md`):
1. `opening_07` ("You cannot undo every decision...") is tagged narrator although it is phrased like an instruction. It stays narrator.
2. In finale slides 3, 5 and 7, Control loses its composure. These need a directed "uncertain" read (bible: "controlled at first, then increasingly uncertain").
3. `teaser_2041` is not in the narrative bible, and its last line is a promotional "Season two: The First Mistake." Is it in scope?
4. The bible gives the opening 7 slides and 70-85 s. The data has 8 slides, and voiced it runs ≈ 96 s.
5. Captions, end-card titles and taglines are on-screen text only, so they are not voiced. The 100 mission `briefing` texts are out of scope (bible §10: do not voice every level).
6. `docs/plan.md` revision 7 (2026-11-11) says "No AI-generated narration or voice recordings; voice settings stay hidden." The 2026-11-11 narration brief approves narration, so I treat revision 7 as superseded for voice. Imran should confirm whether AI voices are acceptable at all.

## 2. Godot audio pipeline (read, not modified)

- **Data:** `CinematicCatalog` already parses an optional per-slide `voice` (`res://` path) and an optional per-slide `duration` (seconds). Speakers are limited to `narrator` and `control`.
- **Player:** `CinematicPlayer` deliberately ignores `slide.voice` ("Subtitles are the narration"). It auto-advances each slide after `reading_seconds()` = `duration` if set, else `max(3.5, words / 2.5 + 1.2)`. It has a 0.8 s image cross-fade and a 0.5 s subtitle fade, tap or accept advances, and Skip ends the sequence.
- **Music:** `MusicDirector` plays the sequence's `music_cue` (cinematic cues are `-10.5 dB` on the `Music` bus). It already has `duck(amount_db, fade)` "e.g. under narration", but nothing calls it yet.
- **Buses:** `default_bus_layout.tres` has Master plus Music, Ambience, SFX and UI. There is **no Voice bus** (ASSET_CONTRACT proposed one).
- **Settings:** `ProgressData.voice_enabled` (default true) is saved, but the UI hides it.
- **Formats:** music and SFX are Ogg Vorbis at 44.1 kHz; music was re-encoded to Vorbis q1 on `main` for APK size. The project sets no custom mix rate, so Godot uses its 44.1 kHz default.
- **Consequence:** voiced lines are ≈ 15 % longer than today's auto-advance reading time (≈ 486 s against 421 s). By estimate, all 50 slides would advance before their line ends, most by 0.3-5 s. The coding agent must play `slide.voice` and hold each slide for `max(voice length + 0.5 s, reading time)`, either by setting `duration` in data or by waiting for the voice to finish. That is a change to the cinematic player, so it needs Imran's approval and the coding agent's work. I have not touched it.

## 3. Production approaches compared

Licence facts were checked on 2026-11-11. This is not legal advice.

| Approach | Consistency | Commercial and redistribution rights | Revise one line | Emotional delivery | Cost (this script) | Quality and size |
|---|---|---|---|---|---|---|
| **A. Professional human VO**, non-union full buyout (cast on Voices.com, Voice123, Backstage or direct) | High within a session. Pickups weeks later can drift (room, mic, voice). | **Strongest and clearest**: a written contract assigns perpetual, worldwide, all-media rights; add no-AI-cloning and pickup clauses. | Needs a pickup session with the same actor. Slow, extra fee. | **Best**: real performance and direction. | GVAA rates for video games are **$200-350/hr, 2-4 h minimum, full buyout** per actor ([GVAA via VoiceCrafters](https://www.voicecrafters.com/industry-standard-voice-over-rates/), [GVAA](https://globalvoiceacademy.com/rates-negotiation/)). Two actors at ≈ 2 h each ≈ **$800-2,800**, plus a 4-6 % platform fee ([Voices.com](https://www.voices.com/rates)). Union (SAG-AFTRA) scale is reported at ≈ $825/4-h session ([source](https://getcleveraboutvo.com/voice-over-rate-calculator/)) and needs signatory status. | 48 kHz/24-bit studio masters. Game files are the same size as any option (≈ 4-6 MB total as Vorbis). |
| **B. ElevenLabs** (paid plan) | Good with one fixed voice, model and settings. v3 is more expressive but less stable than Multilingual v2. | **Paid plans give commercial rights**; free plans are non-commercial only ([billing docs](https://elevenlabs.io/docs/overview/administration/billing), [ToS](https://elevenlabs.io/terms-of-use): "you retain all rights in and to your Output"). Subject to the [Prohibited Use Policy](https://elevenlabs.io/use-policy) (no training other models on the output, etc.). Voice Library voices carry their owner's sharing terms ([VLA](https://elevenlabs.io/vla)); Voice Design voices are synthetic (no real person). Copyright in AI output is unsettled in law. | **Instant**: regenerate any line, with a seed. | **Strong**: v3 audio tags, stability and style controls. | 5,578 characters ≈ 5,600 credits per full pass; 4-5 takes ≈ 25-30k. **Starter $6/mo (30k credits, commercial licence)**, **Creator $22/mo (121k)**, **Pro $99/mo (600k, 44.1 kHz PCM via API, 192 kbps)** ([pricing](https://elevenlabs.io/pricing)). One month of Creator or Pro covers the package plus revisions. | 44.1 kHz PCM on Pro. Lower tiers give MP3 (lossy before Vorbis). |
| **C. Kokoro-82M v1.0, local** (used for these samples) | **Perfect**: deterministic, the same input gives the same audio. | Weights and voices **Apache-2.0** ([model card](https://huggingface.co/hexgrad/Kokoro-82M)). **Caveat:** the card says training data includes "synthetic audio generated by closed TTS models from large providers". Voice-level commercial questions are open and unanswered ([#385](https://github.com/hexgrad/kokoro/issues/385), [#388](https://github.com/hexgrad/kokoro/issues/388), [#219](https://github.com/hexgrad/kokoro/issues/219)). So: **not commercially cleared**. | Instant, offline, free. | **Limited**: no emotion or emphasis control. Pacing comes only from speed and inserted pauses, so it reads rather than performs. | $0 | 24 kHz native (no content above 12 kHz), delivered at 44.1 kHz. |
| D. Chatterbox (Resemble AI), local; tested | Medium: sampling drifts per line. In tests a cloned timbre drifted from 88 Hz to 110-127 Hz median pitch. | **MIT** ([licence](https://raw.githubusercontent.com/resemble-ai/chatterbox/master/LICENSE)). **Retired and unmaintained since Aug 2026** ([repo](https://github.com/resemble-ai/chatterbox)). A PerTh watermark is on by default. Cloning needs a reference voice we hold rights to; the built-in voice's provenance is undocumented. | Yes, but takes vary. | Better than Kokoro (exaggeration control). | $0, about 3× slower than real time on this box | 24 kHz |
| E. Piper | High | Engine MIT/GPL, but **licences vary per voice**: en_US-ryan is CC BY-NC-SA ([card](https://huggingface.co/rhasspy/piper-voices/blob/main/en/en_US/ryan/high/MODEL_CARD)); en_GB-alan's dataset is "All Rights Reserved" ([card](https://huggingface.co/rhasspy/piper-voices/blob/main/en/en_GB/alan/medium/MODEL_CARD), [licence](https://github.com/MycroftAI/mimic3-voices/blob/master/voices/en_UK/apope_low/LICENSE)). | Instant | Flat, assistant-like | $0 | Lower than Kokoro |
| F. XTTS-v2 | — | **Coqui Public Model License: non-commercial** ([licence](https://huggingface.co/coqui/XTTS-v2/blob/main/LICENSE.txt)); Coqui has shut down, so no commercial licence can be bought. **Excluded.** | | | | |
| G. F5-TTS | — | Code MIT, **weights CC-BY-NC-4.0** ([repo](https://github.com/SWivid/F5-TTS/)). **Excluded.** | | | | |
| H. StyleTTS2 pretrained | — | Code MIT. The LibriTTS checkpoints require telling listeners the speech is synthetic unless you have permission for the voice, and the voices are real LibriTTS readers. **Not suitable.** | | | | |

## 4. Samples (phase 1)

All sample text is verbatim from `data/cinematics.json`. Samples were rendered with Kokoro-82M v1.0 (ONNX, `kokoro-onnx` 0.6.1, onnxruntime 1.31.1, CPU), sentence by sentence with directed pauses, and mastered with ffmpeg 7.1.5.

| File (`generated_assets/audio/voice/samples/`) | Content | Voice recipe | Length | Loudness / true peak (ogg) | Size ogg / mp3 |
|---|---|---|---|---|---|
| `gam_vo_sample_narrator_a_01.ogg` (+ `.mp3`) | Opening slides 1, 2, 5 (narrator) | **Recommended narrator candidate.** Kokoro style blend 70 % `am_michael` + 30 % `bm_lewis`, speed 0.88, en-us | 38.4 s | -18.0 LUFS / -1.2 dBTP | 292 KB / 616 KB |
| `gam_vo_sample_narrator_b_01.ogg` (+ `.mp3`) | Same text | Alternate: `bm_george`, speed 0.90, en-gb | 42.0 s | -18.0 LUFS / -1.5 dBTP | 290 KB / 673 KB |
| `gam_vo_sample_control_a_01.ogg` (+ `.mp3`) | Opening slides 6 and 8, then finale slide 3 (all real Control lines) | **Recommended Control candidate.** `bf_emma`, speed 0.86, en-gb, plus the Control treatment | 30.3 s | -18.1 LUFS / -1.6 dBTP | 217 KB / 485 KB |
| `gam_vo_sample_control_b_01.ogg` (+ `.mp3`) | Same text | Alternate: 70 % `bf_emma` + 30 % `af_heart`, plus the Control treatment | 29.6 s | -18.1 LUFS / -1.5 dBTP | 211 KB / 475 KB |

Format: Ogg Vorbis q5 (≈ 96 kbps), mono, 44.1 kHz; MP3 128 kbps listening copies. Slides inside a sample are joined with 1.1 s gaps. About 70 ms of silence before the first word. FLAC masters are kept on the box at `/workspace/tfj-masters/audio/voice/samples/`.

**Objective checks** (I cannot listen to audio myself, so these are measurements, not a listening test):

| Sample | Whisper transcript vs script | UTMOS (predicted naturalness, 1-5) | Median pitch | Pace inside slides |
|---|---|---|---|---|
| Narrator A | matches (medium.en, verbatim) | 4.40 | 110 Hz | ≈ 123 wpm |
| Narrator B | matches | 4.25 | 150 Hz | ≈ 112 wpm |
| Control A | matches | 3.98 treated (4.46 dry) | 186 Hz, narrow range (2.3 semitone SD) | ≈ 105 wpm (countdown beats included) |
| Control B | matches | 3.88 treated | 189 Hz | ≈ 106 wpm |

**Candidates tried:** 11 Kokoro male and 8 female stock voices, 4 male and 2 female style blends, and Chatterbox (default voice, plus 10 Chatterbox renders using Kokoro voices as the reference timbre). Selection used UTMOS, transcription accuracy, pitch and pace, and Kokoro's own voice-quality grades (am_michael C+ was the best male; bm_george C; bm_lewis D+; bf_emma B-).

**Honest quality assessment:** the samples are clean, intelligible, even in loudness and correctly paced, and fine as an **animatic or placeholder** and as a timing reference. They are **not premium cinematic narration.** Kokoro reads rather than performs. Sentence endings tend to share the same falling cadence, there is no real emphasis or dramatic intent, and the finale's "uncertain" Control cannot be directed beyond pacing. The 24 kHz model also lacks top-end air. Chatterbox was more expressive but less stable, unmaintained and watermarked, so it was not used. **No local, commercially usable option I can run here reaches the bar Imran set.**

## 5. Recommendation

1. **Preferred for a commercial release: professional human VO**, one narrator and one Control actor, on a non-union full-buyout contract with explicit perpetual worldwide game and marketing use, a no-AI-training or cloning clause and a pickup clause. It has the best performance and the cleanest rights evidence. Budget ≈ $0.8-2.8k; about 1-2 weeks including casting. I would produce the casting brief from `VOICE_DIRECTION.md` and these samples, direct from the script, and then edit, master, slice and document.
2. **Faster or cheaper alternative: ElevenLabs on a paid plan.** Use one Voice Design narrator and one Voice Design Control voice (synthetic, no real person's likeness), Multilingual v2 for consistency and v3 only for the finale's emotional Control lines if it matches. Use one month of **Pro ($99)** for 44.1 kHz PCM masters, or **Creator ($22)** at minimum. Rights evidence would be the paid-plan receipt plus a dated copy of the ToS. It would still be recorded as "AI-generated, commercial use permitted under the ElevenLabs paid-plan terms; owner review pending", never "cleared" without Imran's sign-off.
3. **Kokoro** stays only as the placeholder and timing reference (and a free fallback if Imran accepts its quality and rights caveat). It is recorded as not commercially cleared.

## 6. Proposed file naming

The contract (§6) id is `<CH>-VO-<NAME>-<NN>`, with the file name as the id in lower snake case. It mirrors the existing still names one to one (`hlx_cin_intro_01.webp` → `hlx_vo_intro_01.ogg`), with one file per slide.

| Imran's suggestion | Contract id | File (game path on `assets`: `generated_assets/audio/voice/<chapter folder>/`) |
|---|---|---|
| `opening_narration_01` … `_08` | `GAM-VO-OPENING-01` … `-08` | `shared/gam_vo_opening_01.ogg` |
| `chapter_01_intro_01` … | `HLX-VO-INTRO-01` … | `helix/hlx_vo_intro_01.ogg` |
| `chapter_01_ending_01` … | `HLX-VO-OUTRO-01` … | `helix/hlx_vo_outro_01.ogg` |
| `chapter_02_intro_01` / ending | `VTA-VO-INTRO-01` / `VTA-VO-OUTRO-01` | `vita/vta_vo_intro_01.ogg` |
| chapter 3 / 4 | `NVG-VO-…`, `CVT-VO-…` | `nova_grid/…`, `civitas/…` |
| chapter 5 intro | `MRD-VO-INTRO-01` … | `meridian/mrd_vo_intro_01.ogg` |
| finale | `GAM-VO-FINALE-01` … `-07` | `shared/gam_vo_finale_01.ogg` |
| teaser (if in scope) | `GAM-VO-TEASER_2041-01` … | `shared/gam_vo_teaser_2041_01.ogg` |

`outro` matches the existing sequence ids (`ch01_outro`) and still names. The manifest records `sequence`, `slide`, `speaker`, transcript, duration and image path for each clip, so the speaker is not in the file name. On `main`, the files would sit under `assets/audio/voice/…`, mirroring the integration layout. The production guide's older suggestion of `audio/narration/` is noted; I would use `voice` to match the contract type `VO`.

## 7. Export settings (proposed for the full package)

- **Game files:** Ogg Vorbis, **mono, 44.1 kHz** (Godot's mix rate; same as music and SFX), **q4 (≈ 80 kbps)**. That is about 4.9 MB for ≈ 8 min. q5 (≈ 96 kbps, ≈ 5.8 MB) is the alternative. Godot import: loop off.
- **Masters:** 44.1 or 48 kHz 24-bit FLAC, kept on the box (`/workspace/tfj-masters/audio/voice/`), not committed.
- **Loudness:** -18 LUFS integrated per clip (contract voice target), true peak at -1.5 dBTP or lower before encoding (at -1.0 or lower measured on the delivered file), LRA under 6 LU. Every clip is measured and recorded in the manifest.
- **Edits:** 60 ms head, 180 ms tail, no clipped breaths, no noise floor above -60 dBFS, no fades over words.
- **Playback (for the coding agent, after approval):** add a `Voice` bus. Play `slide.voice` about 0.3 s after the slide's cross-fade begins. Duck music 8-10 dB with `MusicDirector.duck()` while a voice plays. Hold each slide for `max(voice length + 0.5 s, reading time)`. Stop the voice on Skip or advance. Respect `voice_enabled`. Re-time the `.srt` files from the delivered clip lengths.

## 8. Open questions for Imran

1. **Approach:** human VO (budget ≈ $0.8-2.8k), ElevenLabs (paid plan: Pro $99 or Creator $22 for a month), or accept Kokoro despite its quality and rights caveats?
2. **AI voices:** is AI narration acceptable at all, given plan revision 7's "No AI-generated narration"?
3. **Voices:** narrator accent (neutral American or British, given the script's British spelling) and Control gender (the samples use a female Control).
4. **Pronunciation:** VITA (VEE-tuh or VY-tuh), Civitas (SIV-ih-tahss or KIV-ih-tahss), and years as "twenty eighty-nine".
5. **Scope:** voice `teaser_2041` (including "Season two: The First Mistake.")? Voice any end-card taglines (I recommend not)?
6. **Player change:** do you approve the coding agent changing `CinematicPlayer` and `cinematics.json` timing so the voice plays and slides wait for it? Without this, the narration cannot be heard.
7. **Length:** the voiced opening runs ≈ 96 s, against the bible's 70-85 s target. Is that acceptable, or do you want to approve cuts? (I will not cut text without approval.)
