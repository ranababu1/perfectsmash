# Cinematics: narrated stills, sequences and subtitles (surfaces stream)

All entries are `pending_review`. Masters (1920 x 1080 PNG) and the source log are outside the repo in `/workspace/tfj-masters/surfaces/cin/`.

## What is here

| Path | Contents |
|---|---|
| `opening/` | `GAM-CIN-OPENING-01..08` and the end card plate `GAM-CIN-OPENING_ENDCARD-01` |
| `ch01_intro/` ... `ch05_intro/` | `<CH>-CIN-INTRO-*` and `<CH>-CIN-OUTRO-*`, one still per slide in `data/cinematics.json` |
| `finale/` | `GAM-CIN-FINALE-01..07` (level 100) and `GAM-CIN-FINALE_ENDCARD-01` |
| `teaser_2041/` | `GAM-CIN-TEASER_2041-01..04`, the season two hook |
| `cinematic_sequences.json` | All sequences in the `CinematicCatalog` format with `image` and `duration` filled in, plus `slide_id`, `vo_line` and `end_card.image` |
| `subtitles/` | One `.srt` per sequence and `subtitles.json` (cue start and end per slide) |
| `previews/` | Contact sheets; the yellow line on each frame marks the top of the subtitle band (lower 18%) |

Loading art (`<CH>-BG-LOADING-A`), the main menu backdrop (`GAM-BG-MAIN_MENU-A`) and the five chapter transition cards (`<CH>-BG-TRANSITION-A`) are in `../environments/screens/`. Sequences without their own end card plate use the chapter transition card behind the in-engine end title.

## Using the sequence file

`cinematic_sequences.json` is a superset of `data/cinematics.json`: same ids, speakers, subtitles, captions and motions, so `CinematicCatalog.from_json_text` loads it as it is (the extra keys are ignored). Image paths are `res://assets/...`. Durations follow the loader's own reading pace (2.5 words per second plus 1.2 s, at least 3.5 s), so they match what the player would compute; override them once VO is recorded. `vo_line` repeats the subtitle as the line to record. Captions such as `2096 / KESTREL ENERGY BASIN` stay in-engine; nothing is baked into any image.

The `teaser_2041` sequence is new and not in `data/cinematics.json`. Its four lines are drafts for the writer to approve or replace.

## How they were made

1. Each still was generated with the GenerateImage tool at 1280 x 720 from a prompt written for its slide (chapter palette, grounded near-future look, a calm dark lower band, no text). Shots with the operative used the SV-01 style frame as the reference image and asked for a short waist-length capelet that ends at the belt.
2. Every result was inspected at full size. Rejects (logged in the masters `genlog.tsv`) included long capes on the operative, invented subtitle-like text in the lower band (three cases, fixed by dropping the word "subtitles" from prompts), a dome that read as a real-world landmark, a convergence shot that looked like toy tubes, a saturated pink-violet sky, lit monitors with glyph-like marks, and a lightning-shaped rift that looked cheap.
3. Accepted stills were upscaled with Real-ESRGAN x4plus (ONNX, CPU, tiled) and resampled with Lanczos to 1920 x 1080, then saved as WebP quality 90.
4. Subtitle band check: for each still the script compares edge energy and bright-pixel share in the lower 18% with the rest of the frame. Stills over the threshold get a soft graded darkening across the lower 22% (listed in each manifest entry's notes and in the masters `band_report.json`).

## Delivery status

- Delivered and checked: `opening`, `ch01_intro` to `ch04_outro`, `ch05_intro` and `finale` (11 sequences, 48 stills including the opening and finale end cards). Godot 4.7.2 check (scratch project with a copy of `scripts/`, `godot --headless --script res://check.gd -- cinematic_sequences.json`): 11 sequences, errors 0, missing images 0. Civitas outro, Meridian intro and the finale are new in batch 8.
- In progress: `teaser_2041` (two of four stills upscaled; the sequence and its `.srt` are written once all four exist), loading art, main menu and transition cards.
- Subtitle timing fix: cue times are rounded to whole milliseconds first and then split into hours, minutes, seconds and milliseconds, so a start such as 20.9999 s is written `00:00:21,000` (pass 16 report). All `.srt` files were regenerated with it; every timestamp has three millisecond digits and seconds below 60.
- Band check: four stills with busy lower bands (`CVT-CIN-INTRO-03`, `MRD-CIN-INTRO-03`, `GAM-CIN-FINALE-05`, `-06`) were graded darker; their bands stay textured but dark (band mean 0.06 to 0.09, no bright pixels above the threshold except 1.8% on `FINALE-06`), so white subtitles stay readable. Values are in the masters `band_report.json`.

## Rights

AI-generated (GenerateImage tool), rights not verified, not commercially cleared. Real-ESRGAN: BSD-3-Clause (xinntao/Real-ESRGAN).
