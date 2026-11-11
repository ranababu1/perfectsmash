# Narration package — licensing and provenance

**Status: commercially usable per provider terms; not legally cleared.** Every file has `approval_status: pending_review` in `generated_assets/manifest_parts/narration.json`. Nothing here is a legal opinion. Imran (or counsel) should confirm before release.

## 1. Voice (all 50 slide lines)

- **Provider and plan.** ElevenLabs, Imran's own paid plan, **Creator tier**.
  - The key has no `user_read` scope, so the tier was inferred from the API. `mp3_44100_192` was accepted, which needs Creator or above. `pcm_44100` was refused, which needs Pro.
  - Creator includes a commercial licence.
- **Terms checked 2026-11-12:**
  - Terms of Use: <https://elevenlabs.io/terms-of-use>. Paid subscribers may use output commercially, and you retain rights in your Output, subject to the terms.
  - Billing and plan rights: <https://elevenlabs.io/docs/overview/administration/billing>.
  - Prohibited Use Policy: <https://elevenlabs.io/use-policy>. Among other things, output must not be used to train AI models. Keep this in mind for any future dataset or tooling use.
- **Model.** `eleven_v4` text-to-speech with audio tags: <https://elevenlabs.io/docs/overview/capabilities/text-to-speech/eleven-v4>.
- **Voices.** Both voices were created for this project with **ElevenLabs Voice Design** (<https://elevenlabs.io/voice-design>, model `eleven_ttv_v3`) from text prompts only.
  - No voice cloning, no recording of a real person, and no Voice Library voice. There are therefore no library notice periods (<https://elevenlabs.io/vla>) and no third-party voice-owner terms.
  - Designed voices stay in Imran's account and cannot be shared. Losing the account or the paid plan stops new generation with these voices. Already generated files are unaffected under the terms.

| Role | Name | voice_id | Design prompt (abridged) |
|---|---|---|---|
| Narrator | TFJ Narrator (Temporal First Jump) | `ekSI8bXMs4l0ajdl4bMT` | mature British man, fifties, deep warm baritone, prestige sci-fi documentary narrator |
| Control | TFJ Control (Temporal First Jump) | `RyGrFtWwuk4TeI35VwiE` | calm, precise female AI, thirties, neutral British, subtly unsettling |

  The full prompts and design settings are in `audio/source/narration/elevenlabs/voice_design_meta.json` and `voices_created.json`.

- **Text.** The words are the game's own subtitle text from `data/cinematics.json` (main c104c06), unchanged. The only model-input changes are year numbers written as words and AURA/VITA written as Aura/Vita for pronunciation. The subtitles themselves are not changed.

## 2. Sound effects

- **Provider.** ElevenLabs Sound Effects (`POST /v1/sound-generation`) under the same paid plan. Commercially usable per the same Terms of Use: <https://elevenlabs.io/terms-of-use>.
  - Sound effects page: <https://elevenlabs.io/sound-effects>.
- **Files.** The 16 generated effects, with prompts, durations and costs, are in `audio/source/narration/elevenlabs/sfx_meta.json`. They are mixed into the cinematic beds, not shipped as separate files.

## 3. Music

- All music beds are **our own original algorithmic compositions**, rendered with the project's tfjaudio engine (`generated_assets/audio/source/tfjaudio`).
  - Each bed re-arranges and re-times the existing original cinematic cue for its sequence:
    - `opening_bed.py` for the opening;
    - `cine_beds.py` for the chapter intros and outros, the finale and the teaser.
  - No third-party samples and no AI music service were used.
  - The Control showcase uses an edit of our own `gam_mus_finale_01`.
- **Never used:** `assets/audio/music/gameplay_bed.ogg` and `assets/music/bg.mp3`. Their rights are unverified, so they were not touched.

## 4. Manifest wording

- Voice files: "ElevenLabs output generated under Imran's paid ElevenLabs plan (Creator tier, inferred from the API) … commercially usable per provider terms (https://elevenlabs.io/terms-of-use) … voice designed with ElevenLabs Voice Design for this project (no cloning, no library voice, no real person's voice). Not legally cleared."
- Beds and mixes: "Music: original algorithmic composition … Sound effects layered in: ElevenLabs Sound Effects output under the same paid plan, commercially usable per provider terms. Not legally cleared."

## 5. Keep in mind

- Keep generating on a paid plan. Output made on the free plan is non-commercial and needs attribution.
- Keep the generation logs (`usage.jsonl`, `eval_*.json`, `picks*.json`, `voices_created.json`). They show when and how each file was made, under which voice and model.
- Alternate takes are kept as FLAC masters on the box (`/workspace/tfj-masters/audio/voice/takes/`). They are not committed.
