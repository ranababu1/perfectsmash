# Narration integration

Owner decision (2026-11-11, `docs/plan.md` revision 8): the story cinematics have spoken narration.
**Status: integrated (2026-11-12).** The delivered package (`assets/audio/voice/`,
`assets/audio/music/cinematic/`, manifest `assets/docs/narration/NARRATION_MANIFEST.json`, guide
`assets/docs/narration/CODING_AGENT_NARRATION_GUIDE.md`) plays in game: 50 lines across 12 cinematics,
each cinematic with its own music bed. Rights: commercially usable per provider terms, **not legally
cleared**, pending the owner's review (`assets/docs/narration/LICENSING_PROVENANCE.md`,
`docs/release/rights-audit.md`).

## Data

- `data/narration.json` is generated, never hand-edited:
  `python tools/audio/build_narration_map.py`. It reads the manifest and checks that every manifest
  line matches its subtitle in `data/cinematics.json` verbatim, that every voice file and bed exists,
  and that no slide hold cuts its line. Per cinematic it stores the bed and its level (the
  "cinematic" cue's −10.5 dB). Per slide it stores the voice clip, `voice_at` (seconds after the
  slide appears; the bed pre-roll on slide 1), `subtitle_at` (`voice_at` + the manifest's
  `subtitle_sync.start_s`) and `hold`.
- Holds follow the manifest timeline, so the beds' hits land where they were written. A slide lasts
  until the next line's `voice_start_s`, including the manifest's dramatic gaps. The last slide lasts
  until the timeline end card, never less than its line + 1 s.
- `NarrationCatalog.apply_to()` writes `voice`, `voice_delay`, `subtitle_delay`, `duration` (the
  hold) and the sequence's `music` and `music_volume_db` onto `CinematicCatalog`. Story text, captions
  and images are untouched (tested).

## Playback (`CinematicPlayer`)

- **Bed:** a narrated cinematic plays its own bed from the first slide
  (`MusicDirector.play_track`). Without narration data it falls back to the chapter music cue.
- **Clock:** while the bed plays and nobody has tapped ahead, slide time is the bed's playback
  position, so every line starts on the bed timeline. Measured within 0.02 s (below). After a tap,
  timing falls back to the frame clock and the bed runs ahead, as the guide accepts.
- **Line timing:** each line starts at `voice_delay` on the `Voice` bus, and its subtitle fades in
  at `subtitle_delay`. A slide never changes while its line is still sounding; a 3 s overrun cap
  guards against a stalled device.
- **Duck:** the bed drops 9 dB with a 0.12 s attack when a line starts, holds 0.25 s after the line
  ends, then releases over 0.6 s. These are the package's duck-envelope parameters.
- **Tap or accept:** the line fades over 80 ms on one of two voice players, and the next slide's
  line starts on the other.
- **Skip and Android back:** the voice fades over 50 ms, the duck is released and the bed fades over
  0.8 s; the next screen then brings in its own music. Leaving the tree stops everything.
- **Loading:** all lines of a cinematic are preloaded at its start. The next still loads in the
  background. While the app is backgrounded, voice, bed and slide clock pause together.
- **Settings:** Narration volume (0–100 %) sets the `Voice` bus. At 0 %, with Sound off or with
  narration disabled, no line plays and nothing ducks; slides keep the narrated timing over the bed.
  The Story Archive replays use the same path.

## Verification

- Headless suite: `tests/ui/test_cinematic_narration.gd` covers data integrity, verbatim text, bus,
  timing, duck, tap, skip, leave, volume, app and archive.
- Real playback: run
  `godot_console --resolution 1280x720 -s tools/audio/narration_sync_check.gd -- <out> opening ch01_intro finale`
  (Master at −80 dB; Voice and Music buses recorded), then
  `python tools/audio/narration_sync_report.py <out> opening ch01_intro finale`.
- Results on 2026-11-12, desktop Windows:
  - all 18 lines started within 0.02 s of their manifest bed time;
  - each subtitle appeared 0.05–0.09 s before its speech was heard;
  - each line ended 1.3–3.5 s before its slide changed;
  - the bed sat 6–14 dB lower under speech than in the gaps, consistent with the 9 dB duck over a
    bed whose own level moves.
- A human listening check on a phone is still needed.

## To update the package

Replace files at the same paths, update the manifest, then run `python tools/audio/build_narration_map.py`,
`godot_console --headless --import`, the test suite,
`godot_console --headless -s tools/release/export_manifest.gd`, `python tools/release/rights_audit.py`
and the sync check above.

## Clip keys (50 slides)

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
