# cinematics/

Narrated stills and optional short accent video for story sequences.

## Intended contents

- Opening sequence (~4-7 stills) and chapter intro/outro plates (~40-50 stills campaign-wide per production guide).
- 16:9 clean plates, quiet lower 15-18% for subtitles added in Godot.
- Short video accents only when stills are insufficient; not a campaign dependency.

## Godot use

Driven by `data/cinematics.json` and a rebuilt cinematic player (Phase 4). Subtle zoom/parallax in engine.

## render_type

Stills as 2D images; rare `video` accents. Audio beds and VO live under `../audio/`.
