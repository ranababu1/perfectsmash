# ElevenLabs approval sample — opening cinematic + Control showcase

Status: **approval sample, `pending_review`**. This is not the full narration package. Nothing here is wired into the game. Gameplay code, the cinematic player and mission data are unchanged.

Rights for every file in this sample: **commercially usable per provider terms; not legally cleared.** See section 7.

## 1. Account and plan

- `GET /v1/user/subscription` returned **401 (`missing_permissions: user_read`)**. The key has no `user_read` scope (and no `models_read` scope), so the tier, quota and remaining characters **could not be read through the API**.
- The tier was inferred from the output formats the key accepts:
  - `mp3_44100_192` returned 200. This format needs Creator or above.
  - `pcm_44100` returned 403. This format needs Pro.
  - The plan is therefore **paid, Creator tier** (Creator includes a commercial licence).
- **44.1 kHz PCM output is not allowed on this plan.** Takes were generated as `pcm_48000`, which is allowed, and resampled to 44.1 kHz with soxr VHQ.
- Credits used by this sample, from the `character-cost` response header logged in `source/narration/elevenlabs/usage.jsonl`:

  | Item | Credits |
  |---|---|
  | TTS (auditions + 60 takes + probes, 67 calls) | 5,542 |
  | Sound effects (3 calls) | 308 |
  | **Logged total** | **5,850** |

  The 3 Voice Design preview calls sent 653 characters but returned no cost header. Creating the two voices from previews is free.
- Remaining quota: **unknown**. Check it on the dashboard, or grant the key `user_read`.

## 2. Voices

Both voices were made with ElevenLabs **Voice Design** (`POST /v1/text-to-voice/design`, model `eleven_ttv_v3`, guidance_scale 5, loudness 0.5, seed 11), then saved with `POST /v1/text-to-voice`.

- They are not library voices, so there is no notice-period risk.
- No cloning was used, and no real person's voice.
- Imran's own PVC voice in the account was not used.

| Role | Name | voice_id | Design prompt |
|---|---|---|---|
| Narrator | TFJ Narrator (Temporal First Jump) | `ekSI8bXMs4l0ajdl4bMT` | A mature British man in his fifties with a deep, warm, resonant baritone. Composed, authoritative and intimate, like the narrator of a prestige science-fiction documentary or thriller. Quiet gravity and controlled emotion, measured deliberate pacing, never theatrical. Clean, dry, close-microphone studio recording. |
| Control | TFJ Control (Temporal First Jump) | `RyGrFtWwuk4TeI35VwiE` | A calm, precise female artificial intelligence in her thirties with a neutral British accent. Even, cool and controlled, narrow pitch range, softly spoken and clinically polite, subtly unsettling, as if completely certain she is in control. Perfectly clear diction. Clean, dry studio recording. |

### Auditions

Each design prompt produced 3 previews. Premade and library voices were also auditioned. Metrics are UTMOS / Whisper word errors / median F0 / wpm.

- **Narrator.**
  - Chosen: designed British `nar_uk_2`, 4.26 / 0 / 87 Hz / 134. It has a deep baritone with the widest expressive range and suits the British spelling of the script.
  - Alternative: designed American `nar_us_2`, 4.41 / 0 / 88 Hz / 139. Its preview is kept on the box at `/workspace/tfj-narration-el/design/nar_us_2.mp3`, and it can be created on request.
  - Premade voices auditioned: George 4.18, Daniel 4.33, Bill 4.29, Brian 4.30. Library voice Adam Stone scored 4.34. Designed voices were preferred because they avoid library terms.
- **Control.**
  - Chosen: designed `ctl_f_2`, 4.38 / 0 / 181 Hz / 115. It has a narrow pitch range and a clean, cool read.
  - Premade voices auditioned: Lily 4.42 with 2 word errors, and Alice 4.37.

## 3. Direction and generation

- Model: **`eleven_v4`**, the most expressive model, which supports audio tags.
  - It has no SSML `<break>`, so pauses use `[pause]` and ellipses.
  - Tags plus spoken text for every line are in `source/narration/elevenlabs/direction.json`. The **spoken words are exactly the slide text**. The only model-input change is that years are spelled out ("twenty eighty-nine"); subtitles are unchanged.
- Voice settings:
  - Narrator: stability 0.4, similarity_boost 0.8.
  - Control: stability 0.5, similarity_boost 0.8.
  - Each line also gets `previous_text` and `next_text` from the neighbouring slides, for continuity.
- **5 takes per line** (seeds 1–5) for 8 opening lines and 4 finale Control lines, 60 takes in total (`gen_takes.py`).
- Automatic selection (`evalv2.py`, `eval_takes.json`, `picks.json`):
  1. Whisper exact word match required (0 errors).
  2. No clipping.
  3. Highest UTMOS (predicted naturalness) wins, as long as pace and pauses look sensible. All picks fall within 85–156 wpm, and no pause is longer than 1.22 s.

| Line | Role | Take | UTMOS | wpm | Max gap | F0 |
|---|---|---|---|---|---|---|
| opening_01 | Narrator | s5 | 4.12 | 145 | 0.86 s | 108 Hz |
| opening_02 | Narrator | s1 | 4.16 | 112 | 0.88 | 89 |
| opening_03 | Narrator | s3 | 3.82 | 116 | 1.22 | 84 |
| opening_04 | Narrator | s5 | 3.86 | 142 | 0.94 | 99 |
| opening_05 | Narrator | s5 | 4.05 | 122 | 0.86 | 84 |
| opening_06 | Control | s2 | 4.46 | 132 | 0.90 | 183 |
| opening_07 | Narrator | s2 | 3.55 | 156 | 0.74 | 81 |
| opening_08 | Control | s5 | 4.44 | 85 | 0.84 | 178 |
| finale_02 | Control | s4 | 4.06 | 115 | 0.82 | 160 |
| finale_03 | Control | s2 | 3.74 | 125 | 0.62 | 242 |
| finale_05 | Control | s3 | 3.83 | 148 | 0.82 | 194 |
| finale_07 | Control | s3 | 4.36 | 116 | 0.86 | 211 |

**Caveat: these are machine checks, not a listening test.** UTMOS rewards clean, neutral speech and can score a quieter or more emotional take lower. opening_07 (whispered) and finale_03 (startled) have the lowest scores for that reason.
- For finale_03, take s2 was picked over s1 because s1 had more pitch movement and might sound more shaken, but scored worse on the artefact checks.
- If a line sounds wrong by ear, the other 4 takes for every line are on the box in `/workspace/tfj-narration-el/takes/`. Swapping a take needs no new credits.

The delivered oggs were re-checked with faster-whisper medium.en: two passes, `condition_on_previous_text=False` (`verify_delivered.json`). All 12 lines match the script. The only differences were transcription formatting ("2089", "2041", "synchronized").

## 4. Voice mastering

`source/narration/master_vo.py`:

1. Trim at -45 dB relative to peak, keeping 10 ms of pre-roll; add a 60 ms head and a 180 ms tail.
2. soxr resample to 44.1 kHz.
3. Role chain:
   - Narrator: HPF 60 Hz, -1 dB at 250 Hz, +0.8 dB at 4.5 kHz, 2:1 compression.
   - Control: band-limited 150 Hz–11 kHz, +1.5 dB at 2.8 kHz, -2 dB at 400 Hz, a faint 17/29 ms comb "system" sheen, 3:1 compression.
4. Two-pass linear loudnorm to -18 LUFS.
5. Encode as mono Ogg Vorbis q6.

| File | Duration | LUFS | dBTP | kbps |
|---|---|---|---|---|
| voice/opening/gam_vo_opening_01.ogg | 14.45 s | -18.0 | -1.9 | 96 |
| voice/opening/gam_vo_opening_02.ogg | 14.18 | -18.0 | -2.0 | 93 |
| voice/opening/gam_vo_opening_03.ogg | 15.40 | -18.0 | -2.3 | 94 |
| voice/opening/gam_vo_opening_04.ogg | 11.83 | -18.1 | -1.9 | 89 |
| voice/opening/gam_vo_opening_05.ogg | 7.30 | -18.0 | -1.9 | 94 |
| voice/opening/gam_vo_opening_06.ogg | 15.81 | -18.1 | -2.0 | 88 |
| voice/opening/gam_vo_opening_07.ogg | 6.92 | -18.0 | -2.6 | 95 |
| voice/opening/gam_vo_opening_08.ogg | 4.69 | -18.0 | -2.0 | 85 |
| voice/finale/gam_vo_finale_02.ogg | 5.54 | -18.1 | -1.9 | 89 |
| voice/finale/gam_vo_finale_03.ogg | 6.02 | -17.5 | -3.0 | 82 |
| voice/finale/gam_vo_finale_05.ogg | 8.43 | -18.1 | -1.9 | 87 |
| voice/finale/gam_vo_finale_07.ogg | 6.63 | -17.7 | -2.0 | 87 |

All files are 44.1 kHz mono and true peak is at or below -1.9 dBTP. finale_03 and finale_07 sit slightly hot because short, dynamic lines limit linear loudnorm; both are within the ±1 LU tolerance. Masters (24-bit FLAC) are on the box at `/workspace/tfj-masters/audio/voice/{opening,finale}/`.

## 5. Music bed, sound effects and mix

**Bed: `music/cinematic/gam_mus_cine_opening_bed.ogg`** (128.0 s, stereo 44.1 kHz, -16.5 LUFS, -3.3 dBTP, un-ducked).

- It is a re-arrangement of our own opening score (tfjaudio cue `mus_cin_opening`, D minor, 60 BPM) by `source/narration/opening_bed.py`. At 60 BPM a beat is a second, so every event is placed from `elevenlabs/timeline.json`.
- Narrative layout:

  | Slide or gap | Music |
  |---|---|
  | Pre-roll (4 s) | Drone + noise bed + piano |
  | Slides 1–3 | Darkening pads, with piano answers and a string swell in the gaps |
  | Slide 3 ("Cities went silent") | Low boom |
  | Gap 3 into slide 4 | Glass shimmer and a riser into "a breakthrough" |
  | Gap 4 into slide 5 | The main motif in low strings |
  | Gap 5 | Braam swell |
  | From slide 6 (Control) | Clock ticks and a bass pulse that ramp up to the countdown |
  | Gap 6 | High-string lift |
  | Last 8 s | Riser |
  | Countdown ("three… two… one") | Taiko on each spoken word, at 106.77, 107.90 and 109.03 s |
  | Title hit (110.30 s) | Brass motif + high strings, then the tail |

- Neither `gameplay_bed.ogg` nor `bg.mp3` was used or touched.

**Sound effects** (ElevenLabs Sound Effects, `POST /v1/sound-generation`, prompt_influence 0.5; prompts in `elevenlabs/sfx_meta.json`):

| Effect | Length | Placement in bed | Gain | Cost |
|---|---|---|---|---|
| Ruined-city wind | 14 s | Under slide 3 | +14 dB | 154 credits |
| Temporal charge | 8 s | Slide 6 | -11 dB | 88 credits |
| Time-jump impact | 6 s | Impact on the title hit | -9 dB | 66 credits |

**Ducking.** `music/cinematic/gam_mus_cine_opening_bed.duck_env.json` holds the gain in dB every 10 ms. The engine can play it back, or reproduce the settings with `MusicDirector.duck()`:

- trigger: voice activity above -50 dBFS (10 ms RMS);
- look-ahead 150 ms, attack 120 ms, hold 250 ms, release 600 ms;
- depth **9 dB**.

In the mix, the voice sits about **10.7 LU above the ducked bed** while speaking.

| Mix | File | Duration | Loudness | Peak |
|---|---|---|---|---|
| Opening mix reference | `music/cinematic/gam_cine_opening_mix_ref.ogg` | 128.0 s | -16.1 LUFS | -1.7 dBTP |
| Opening mix reference | `music/cinematic/gam_cine_opening_mix_ref.mp3` | 128.0 s | -16.2 LUFS | -1.7 dBTP |
| Control showcase | `music/cinematic/gam_cine_finale_control_showcase.ogg` | 56.0 s | -16.0 LUFS | -1.3 dBTP |
| Control showcase | `music/cinematic/gam_cine_finale_control_showcase.mp3` | 56.0 s | -16.2 LUFS | -1.3 dBTP |

- **Opening mix reference.** All 8 lines on the timeline over the ducked bed with the sound effects.
- **Control showcase.**
  - Score: an edit of `gam_mus_finale_01` (bars 5–11 + 13–end, 1.5 s crossfade, fade 52–56 s).
  - Lines and start times: finale_02 at 2.5 s, finale_03 ("Wait…") at 12.3 s right after the signal returns, finale_05 ("…Twenty forty-one…") at 26.7 s after the 2041 reveal, finale_07 at 36.8 s.
  - Same ducking as the opening mix.

## 6. Engine notes for later (not done; needs approval)

- `CinematicPlayer` currently ignores the `voice` field and auto-advances after `max(3.5, words/2.5 + 1.2)` s. Voiced slides need to advance on the voice length plus the gaps in `timeline.json` (2.0–3.0 s).
- There is no Voice bus yet. `MusicDirector.duck()` exists but nothing calls it.

## 7. Terms (checked 2026-11-12)

- ElevenLabs Terms of Use: <https://elevenlabs.io/terms-of-use>. Paid plans include a commercial licence, and you retain the rights in your Output. See also <https://elevenlabs.io/docs/overview/administration/billing>.
- Prohibited Use Policy: <https://elevenlabs.io/use-policy>. It forbids, among other things, using output to train AI models.
- Voice Design: <https://elevenlabs.io/voice-design>. Designed voices can be used commercially on paid plans.
- Library voices carry notice periods (<https://elevenlabs.io/docs/help-center/product/voices/voice-library/what-is-a-notice-period>, <https://elevenlabs.io/vla>). This is why designed voices were used.
- v4 and audio tags: <https://elevenlabs.io/docs/overview/capabilities/text-to-speech/eleven-v4>.
- Manifest wording: "commercially usable per provider terms; not legally cleared". Approval status is `pending_review`. **Keep the plan paid** while generating release assets: output made on a free plan is non-commercial and needs attribution.

## 8. Estimate for the full package

- The script has 50 slides across 12 cinematics, about 5,578 characters of spoken text. With tags at about +25%, that is about 7,000 characters per pass.
- eleven_v4 is billed at about 0.44 credits per character, as measured from `character-cost` on this account. That is about **3,100 credits per pass**.
  - 5 takes per line: about **15,500 credits**.
  - 3 takes per line: about **9,300 credits**.
- Sound effects for the other cinematics add about 1,000–2,000 credits.
- **Total: about 17,000 credits** at 5 takes, roughly 14% of a Creator month (121k credits). Opening and finale lines already approved could be reused.

## 9. Files

- Source in `assets/audio/source/narration/`: `master_vo.py`, `opening_bed.py`, `mix_cine.py`.
- `assets/audio/source/narration/elevenlabs/`:
  - helper scripts `el.py` (reads the key from the environment, never stores it), `gen_takes.py`, `evalv2.py`, `verify_delivered.py`;
  - `direction.json`, `timeline.json`, `voices_created.json`, `voice_design_meta.json`, `sfx_meta.json`;
  - `eval_takes.json`, `picks.json`, `master_log.json`, `verify_delivered.json`, `usage.jsonl`.
  - Note: `master_log.json` records the q4 encode. The delivered oggs are q6 re-encodes of the same masters, measured in section 4.
