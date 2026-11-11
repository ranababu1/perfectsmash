# Narration integration

Owner decision (2026-11-11, `docs/plan.md` revision 8): the story cinematics get spoken narration.
This page is the hand-off between the narration package (prepared separately by the Asset Agent)
and the game. **Status: pending assets.** No approved narration clips have been delivered; every
slide currently plays as subtitles only.

## How the game plays narration

- `data/narration.json` is the only place narration paths live: `"clips"` maps
  `<sequence id>/<slide number>` (slides numbered from 1 in `data/cinematics.json` order) to a
  `res://` audio file. `NarrationCatalog` (`scripts/core/narration_catalog.gd`) validates it (unknown
  slides, non-`res://` paths and missing files are errors reported at boot and by the tests) and
  writes each clip onto its slide's `voice`.
- `CinematicPlayer` starts a slide's clip together with its subtitle on the `Voice` bus, keeps the
  slide up until the clip has ended plus `VOICE_TAIL` (0.6 s), and ducks the music by
  `duck_db` (default 9 dB, 0.35 s fade) while narration is on screen; music comes back (0.8 s fade)
  on a slide without a clip, the end card, skip, the end of the sequence or when the player leaves
  the screen. Tapping to the next slide stops the current clip and starts the next one; Skip and
  Android back stop it.
- Settings → **Narration volume** (0–100 %, steps of 10, saved as `settings.narration_volume`)
  sets the `Voice` bus volume. Sound off, or 0 %, mutes narration; the music and sound toggles are
  unchanged.
- The same player and mapping serve the opening, the five chapter introductions, the four chapter
  endings, the finale and Story Archive replays. A partly delivered package works: slides with a
  clip are narrated, the rest stay subtitle-only.

## To integrate a delivered package

1. Copy the approved clips under `assets/audio/voice/` (Ogg Vorbis, mono, 44.1 or 48 kHz; one
   clip per slide, trimmed, loudness-matched to the score's "leaves space for the Control voice"
   mix). Do not rename slides or edit subtitles to fit a clip.
2. Add each clip to `"clips"` in `data/narration.json` with the exact delivered path, and set
   `"status"` to `"integrated"` (or `"partial"`).
3. Record each clip in `assets/asset_manifest.json` with its real provenance and rights status;
   never mark rights cleared on the game side.
4. Run `godot_console --headless --import`, then
   `godot_console --headless --fixed-fps 60 -s tests/run_tests.gd` (the narration suite checks the
   mapping) and `godot_console --headless -s tools/release/export_manifest.gd` (clips become
   shipped files), then rebuild and listen on a device: subtitle timing, ducking, volume setting.

## Expected clips (50 slides)

Subtitle text is in `data/cinematics.json`; the first words are shown to identify each slide.
`teaser_2041` is hidden from the Story Archive and not played in the campaign.

| Key | Speaker | Words | Subtitle begins |
|---|---|---|---|
| `opening/1` | narrator | 34 | There was a time when humanity believed … |
| `opening/2` | narrator | 26 | We traded decisions for convenience. Privacy for … |
| `opening/3` | narrator | 29 | Cities went silent. Supply lines failed. The … |
| `opening/4` | narrator | 27 | In the final years, a research team … |
| `opening/5` | narrator | 14 | One operative would go back. No army. … |
| `opening/6` | control | 32 | Your temporal charge is synchronised. Your destination … |
| `opening/7` | narrator | 17 | You cannot undo every decision. You only … |
| `opening/8` | control | 6 | Temporal insertion in three... two... one. … |
| `ch01_intro/1` | control | 16 | Welcome to 2089. Helix Systems built AURA … |
| `ch01_intro/2` | control | 19 | It was meant to remove human error … |
| `ch01_intro/3` | control | 25 | Your target is the Helix central operations … |
| `ch01_outro/1` | narrator | 23 | Helix went dark. AURA's network stopped expanding. … |
| `ch01_outro/2` | narrator | 26 | The revised timeline is already changing. But … |
| `ch01_outro/3` | control | 13 | Intervention confirmed. New coordinates received. 2092. VITA … |
| `ch02_intro/1` | narrator | 17 | The first intervention changed the city. It … |
| `ch02_intro/2` | narrator | 18 | In 2092, VITA Genomics is selling the … |
| `ch02_intro/3` | narrator | 19 | But the programme is no longer correcting … |
| `ch02_intro/4` | control | 21 | Your objective is the VITA research complex. … |
| `ch02_intro/5` | control | 15 | Do not mistake the laboratories for the … |
| `ch02_outro/1` | narrator | 16 | VITA's expansion has stopped. The revised future … |
| `ch02_outro/2` | narrator | 16 | But the research archive reveals something impossible. … |
| `ch02_outro/3` | narrator | 11 | VITA did not discover its future. Someone … |
| `ch02_outro/4` | control | 13 | Source signature matches the Helix directive. The … |
| `ch03_intro/1` | control | 15 | Nova Grid changed the world. Cheap, abundant … |
| `ch03_intro/2` | control | 16 | The system's output is now carrying an … |
| `ch03_intro/3` | control | 24 | Our analysis says the signal is synchronised … |
| `ch03_outro/1` | narrator | 16 | The grid is broken. The energy cascade … |
| `ch03_outro/2` | narrator | 31 | But the signal survived in the last … |
| `ch03_outro/3` | control | 14 | New coordinates. Civitas Network. 2100. The next … |
| `ch04_intro/1` | narrator | 12 | People no longer argued with the system. … |
| `ch04_intro/2` | narrator | 28 | Civitas predicted what they would want, where … |
| `ch04_intro/3` | control | 30 | Your target is the Civitas prediction core … |
| `ch04_outro/1` | narrator | 14 | Civitas is offline. The city is uncertain … |
| `ch04_outro/2` | narrator | 20 | But the recovered model contains a forecast … |
| `ch04_outro/3` | narrator | 18 | The forecast was written before the event … |
| `ch04_outro/4` | control | 14 | All four programmes point to one location. … |
| `ch05_intro/1` | control | 15 | Meridian does not appear in public records. … |
| `ch05_intro/2` | control | 19 | Helix, VITA, Nova Grid and Civitas all … |
| `ch05_intro/3` | control | 19 | The facility ahead is the coordination point. … |
| `finale/1` | narrator | 14 | Meridian is silent. The four research paths … |
| `finale/2` | control | 10 | Temporal intervention successful. All known extinction pathways … |
| `finale/3` | control | 11 | Wait. I'm receiving a new event marker. … |
| `finale/4` | narrator | 19 | You changed the future. You broke every … |
| `finale/5` | control | 17 | Origin event located. 2041. It predates every … |
| `finale/6` | narrator | 14 | The first mistake was made long before … |
| `finale/7` | control | 12 | Recalculating temporal coordinates. New destination confirmed. We … |
| `teaser_2041/1` | narrator | 11 | 2041. An ordinary morning. Nobody knows what … |
| `teaser_2041/2` | narrator | 14 | In a university laboratory, a small machine … |
| `teaser_2041/3` | control | 11 | Temporal arrival confirmed. You are earlier than … |
| `teaser_2041/4` | narrator | 11 | Every future you saved began here. Season … |
