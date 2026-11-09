# audio/

Music masters (when rights are clear), SFX, ambience and voice exports staged for review.

## Intended contents

- Gameplay bed candidates (do not replace `assets/audio/music/gameplay_bed.ogg` without owner approval and licence evidence).
- Chapter ambience layers.
- Weapon and material SFX variations.
- Narration / Control VO (external service; commercial-use plan required).

## Godot use

Compressed Ogg (or agreed format) referenced by audio directors. Masters may stay here or outside the repo until approved.

## render_type

`audio`.

## Licence rule

Never commit unlicensed or unverified commercial music. Record source, plan/terms and date for every clip in `../asset_manifest.json`.

## Current contents (audio stream, 2026-11-10)

Original music, SFX and ambience made as code; see `PRODUCTION_NOTES.md` for method, loudness targets and rights, and `CUE_SHEET.md` / `cue_sheet.json` for every file. Manifest fragment: `../manifest_parts/audio.json`.

- Loudness: music -16 LUFS integrated (cinematic -16.5), true peak at or below -1 dBTP; ambience -24 LUFS; SFX by family on momentary loudness (weapons -14 to -10, impacts -18 to -14, UI -22 to -18).
- Rights: original algorithmic composition produced for the owner; no third-party samples. Pending owner review.
