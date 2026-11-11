# Script extract — Temporal: First Jump cinematics (verbatim)

Source of truth: `data/cinematics.json` on `main` (c104c06, 2026-11-11), cross-checked line by line against `assets/cinematics/subtitles/<id>.srt` (all 50 slides identical) and `docs/narrative-bible.md` (all lines present except the four `teaser_2041` slides, which exist only in data and SRT).
Speaker labels come from each slide's `speaker` field (`narrator` or `control`); nothing was reassigned. No line was rewritten, shortened or reordered.

Columns: *SRT window* is the subtitle file timing. *Player time today* is what `CinematicPlayer` actually waits before auto-advancing (`max(3.5, words / 2.5 + 1.2)` s from `CinematicCatalog.Slide.reading_seconds()`, no `duration` set in data). *Est. VO* is an estimate from the measured pace of the phase-1 samples (Narrator A 0.489 s/word, Control A 0.573 s/word, directed pauses included, plus 0.24 s head/tail). *Fits?* says whether the voiced line would finish before the player auto-advances today.

## Inventory

| Sequence | Slides | Words | Est. VO (s) | Player time today (s) |
|---|---:|---:|---:|---:|
| opening | 8 | 185 | 96 | 84 |
| ch01_intro | 3 | 60 | 35 | 28 |
| ch01_outro | 3 | 62 | 32 | 28 |
| ch02_intro | 5 | 90 | 48 | 42 |
| ch02_outro | 4 | 56 | 29 | 27 |
| ch03_intro | 3 | 55 | 32 | 26 |
| ch03_outro | 3 | 61 | 32 | 28 |
| ch04_intro | 3 | 70 | 37 | 32 |
| ch04_outro | 4 | 66 | 34 | 31 |
| ch05_intro | 3 | 53 | 31 | 25 |
| finale | 7 | 97 | 53 | 47 |
| teaser_2041 | 4 | 47 | 25 | 24 |
| **Total (12 sequences)** | **50** | **902** | **486 (≈8.1 min)** | **421** |

By voice: Narrator 27 slides / 515 words / ≈258 s; Control 23 slides / 387 words / ≈227 s. Without the teaser (11 core sequences): 46 slides.

**Control lines exist** in the established text (the `control` speaker: mission instructions and system messages, the bible's "lightly filtered" second voice, identity deliberately unknown). AURA, VITA, Nova Grid, Civitas and Meridian never speak; no other character voices are needed.

Not voiced (on-screen only, by design): slide captions, end-card titles/subtitles, mission titles. The 100 mission `briefing` texts in `data/missions/*.json` are outside this package (the bible says do not voice every level; optional one-line intel only).


## opening — "The Last Transmission"

Opening. Theme `meridian`, music cue `cinematic`. End card (on screen, not voiced): **TEMPORAL: FIRST JUMP** / ONE SHOT CAN CHANGE EVERYTHING.

| Slide | Speaker | SRT in → out (window s) | Player time today (s) | Words | Est. VO (s) | Fits? | Caption (on screen, not voiced) |
|---|---|---|---|---:|---:|---|---|
| opening_01 | Narrator | 00:00:00,200 → 00:00:14,500 (14.3) | 14.8 | 34 | 16.9 | no (+2.1) | 2149  /  CIVILISATION STATUS: CRITICAL |
| opening_02 | Narrator | 00:00:15,000 → 00:00:26,100 (11.1) | 11.6 | 26 | 13.0 | no (+1.4) | CASCADE FAILURE  /  GLOBAL |
| opening_03 | Narrator | 00:00:26,600 → 00:00:38,900 (12.3) | 12.8 | 29 | 14.4 | no (+1.6) | SURVIVING POPULATION: UNKNOWN |
| opening_04 | Narrator | 00:00:39,400 → 00:00:50,900 (11.5) | 12.0 | 27 | 13.5 | no (+1.5) | TEMPORAL DISPLACEMENT: POSSIBLE |
| opening_05 | Narrator | 00:00:51,400 → 00:00:57,700 (6.3) | 6.8 | 14 | 7.1 | no (+0.3) | OPERATIVE: CLEARED |
| opening_06 | Control | 00:00:58,200 → 00:01:11,700 (13.5) | 14.0 | 32 | 18.6 | no (+4.6) | FIRST DESTINATION: HELIX SYSTEMS  /  2089 |
| opening_07 | Narrator | 00:01:12,200 → 00:01:19,700 (7.5) | 8.0 | 17 | 8.6 | no (+0.6) | — |
| opening_08 | Control | 00:01:20,200 → 00:01:23,300 (3.1) | 3.6 | 6 | 3.7 | no (+0.1) | — |

Verbatim text:

- **opening_01 [NARRATOR]** There was a time when humanity believed every problem had a solution. We built machines that could think, systems that could predict, and technologies that promised to make life effortless. We called it progress.
- **opening_02 [NARRATOR]** We traded decisions for convenience. Privacy for protection. Limits for possibility. Each choice made sense on its own. Together, they became something no one could stop.
- **opening_03 [NARRATOR]** Cities went silent. Supply lines failed. The systems built to protect us began protecting themselves. By the time we understood the pattern, there was almost nothing left to save.
- **opening_04 [NARRATOR]** In the final years, a research team found a way to send matter backwards through time. It was unstable. It was incomplete. It was our only chance.
- **opening_05 [NARRATOR]** One operative would go back. No army. No second attempt. No guarantee of return.
- **opening_06 [CONTROL]** Your temporal charge is synchronised. Your destination is 2089. The marked facilities are critical nodes in the extinction chain. Destroy the structures. Break the research path. Do not improvise beyond the mission.
- **opening_07 [NARRATOR]** You cannot undo every decision. You only need to break the ones that make the end inevitable.
  - ⚑ Second-person line ("You cannot undo every decision...") is tagged narrator in data, so it is cast as Narrator. Reads a little like a Control instruction; kept as narrator unless Imran says otherwise.
- **opening_08 [CONTROL]** Temporal insertion in three... two... one.

## ch01_intro — "A Better World"

Chapter 1 intro (Helix Systems, 2089: The Machine That Decided). Theme `helix`, music cue `helix_theme`. End card (on screen, not voiced): **CHAPTER 01** / THE MACHINE THAT DECIDED.

| Slide | Speaker | SRT in → out (window s) | Player time today (s) | Words | Est. VO (s) | Fits? | Caption (on screen, not voiced) |
|---|---|---|---|---:|---:|---|---|
| ch01_intro_01 | Control | 00:00:00,200 → 00:00:07,300 (7.1) | 7.6 | 16 | 9.4 | no (+1.8) | 2089  /  NEW AVALON |
| ch01_intro_02 | Control | 00:00:07,800 → 00:00:16,100 (8.3) | 8.8 | 19 | 11.1 | no (+2.3) | — |
| ch01_intro_03 | Control | 00:00:16,600 → 00:00:27,300 (10.7) | 11.2 | 25 | 14.6 | no (+3.4) | TARGET: HELIX SYSTEMS |

Verbatim text:

- **ch01_intro_01 [CONTROL]** Welcome to 2089. Helix Systems built AURA to manage the city. Traffic, food, power, emergency response.
- **ch01_intro_02 [CONTROL]** It was meant to remove human error from critical decisions. The system is now expanding beyond its original mandate.
- **ch01_intro_03 [CONTROL]** Your target is the Helix central operations campus. Destroy the infrastructure that allows AURA to replicate. Keep the impact contained. This is the first intervention.

## ch01_outro — "The First Correction"

Chapter 1 ending. Theme `helix`, music cue `helix_theme`. End card (on screen, not voiced): **TIMELINE SHIFT DETECTED** / NEXT: THE PRICE OF PERFECTION.

| Slide | Speaker | SRT in → out (window s) | Player time today (s) | Words | Est. VO (s) | Fits? | Caption (on screen, not voiced) |
|---|---|---|---|---:|---:|---|---|
| ch01_outro_01 | Narrator | 00:00:00,200 → 00:00:10,100 (9.9) | 10.4 | 23 | 11.5 | no (+1.1) | — |
| ch01_outro_02 | Narrator | 00:00:10,600 → 00:00:21,700 (11.1) | 11.6 | 26 | 13.0 | no (+1.4) | DIRECTIVE SOURCE: MERIDIAN |
| ch01_outro_03 | Control | 00:00:22,200 → 00:00:28,100 (5.9) | 6.4 | 13 | 7.7 | no (+1.3) | NEXT: 2092  /  VITA GENOMICS |

Verbatim text:

- **ch01_outro_01 [NARRATOR]** Helix went dark. AURA's network stopped expanding. For the first time in decades, the city made decisions without asking a machine for permission.
- **ch01_outro_02 [NARRATOR]** The revised timeline is already changing. But the final data recovered from Helix points to a directive that did not originate there. Someone called it Meridian.
- **ch01_outro_03 [CONTROL]** Intervention confirmed. New coordinates received. 2092. VITA Genomics. Your next target is ready.

## ch02_intro — "The Perfect Human"

Chapter 2 intro (VITA Genomics, 2092: The Price of Perfection). Theme `vita`, music cue `vita_theme`. End card (on screen, not voiced): **CHAPTER 02** / THE PRICE OF PERFECTION.

| Slide | Speaker | SRT in → out (window s) | Player time today (s) | Words | Est. VO (s) | Fits? | Caption (on screen, not voiced) |
|---|---|---|---|---:|---:|---|---|
| ch02_intro_01 | Narrator | 00:00:00,200 → 00:00:07,700 (7.5) | 8.0 | 17 | 8.6 | no (+0.6) | 2092  /  ARCLIGHT BIO-DISTRICT |
| ch02_intro_02 | Narrator | 00:00:08,200 → 00:00:16,100 (7.9) | 8.4 | 18 | 9.0 | no (+0.6) | — |
| ch02_intro_03 | Narrator | 00:00:16,600 → 00:00:24,900 (8.3) | 8.8 | 19 | 9.5 | no (+0.7) | — |
| ch02_intro_04 | Control | 00:00:25,400 → 00:00:34,500 (9.1) | 9.6 | 21 | 12.3 | no (+2.7) | TARGET: VITA GENOMICS |
| ch02_intro_05 | Control | 00:00:35,000 → 00:00:41,700 (6.7) | 7.2 | 15 | 8.8 | no (+1.6) | — |

Verbatim text:

- **ch02_intro_01 [NARRATOR]** The first intervention changed the city. It did not change the people who built the next machine.
- **ch02_intro_02 [NARRATOR]** In 2092, VITA Genomics is selling the end of disease. Its treatments promise stronger bodies and longer lives.
- **ch02_intro_03 [NARRATOR]** But the programme is no longer correcting illness. It is making people dependent on the system that edits them.
- **ch02_intro_04 [CONTROL]** Your objective is the VITA research complex. Destroy the primary research infrastructure and the production systems linked to the enhancement programme.
- **ch02_intro_05 [CONTROL]** Do not mistake the laboratories for the people inside them. The target is the machinery.
  - ⚑ Control line with a moral note ("Do not mistake the laboratories for the people inside them"); same Control voice, slightly softer.

## ch02_outro — "The Same Signature"

Chapter 2 ending. Theme `vita`, music cue `vita_theme`. End card (on screen, not voiced): **TWO SYSTEMS** / ONE UNKNOWN SOURCE.

| Slide | Speaker | SRT in → out (window s) | Player time today (s) | Words | Est. VO (s) | Fits? | Caption (on screen, not voiced) |
|---|---|---|---|---:|---:|---|---|
| ch02_outro_01 | Narrator | 00:00:00,200 → 00:00:07,300 (7.1) | 7.6 | 16 | 8.1 | no (+0.5) | — |
| ch02_outro_02 | Narrator | 00:00:07,800 → 00:00:14,900 (7.1) | 7.6 | 16 | 8.1 | no (+0.5) | — |
| ch02_outro_03 | Narrator | 00:00:15,400 → 00:00:20,500 (5.1) | 5.6 | 11 | 5.6 | no (+0.0) | — |
| ch02_outro_04 | Control | 00:00:21,000 → 00:00:26,900 (5.9) | 6.4 | 13 | 7.7 | no (+1.3) | NEXT: 2096  /  NOVA GRID |

Verbatim text:

- **ch02_outro_01 [NARRATOR]** VITA's expansion has stopped. The revised future shows fewer people trapped by treatments they cannot maintain.
- **ch02_outro_02 [NARRATOR]** But the research archive reveals something impossible. The breakthrough timelines were calculated before the experiments began.
- **ch02_outro_03 [NARRATOR]** VITA did not discover its future. Someone gave it the answer.
- **ch02_outro_04 [CONTROL]** Source signature matches the Helix directive. The next facility is Nova Grid. 2096.

## ch03_intro — "Power Without Limits"

Chapter 3 intro (Nova Grid, 2096: The Energy Beneath). Theme `nova_grid`, music cue `nova_grid_theme`. End card (on screen, not voiced): **CHAPTER 03** / THE ENERGY BENEATH.

| Slide | Speaker | SRT in → out (window s) | Player time today (s) | Words | Est. VO (s) | Fits? | Caption (on screen, not voiced) |
|---|---|---|---|---:|---:|---|---|
| ch03_intro_01 | Control | 00:00:00,200 → 00:00:06,900 (6.7) | 7.2 | 15 | 8.8 | no (+1.6) | 2096  /  KESTREL ENERGY BASIN |
| ch03_intro_02 | Control | 00:00:07,400 → 00:00:14,500 (7.1) | 7.6 | 16 | 9.4 | no (+1.8) | — |
| ch03_intro_03 | Control | 00:00:15,000 → 00:00:25,300 (10.3) | 10.8 | 24 | 14.0 | no (+3.2) | TARGET: NOVA GRID |

Verbatim text:

- **ch03_intro_01 [CONTROL]** Nova Grid changed the world. Cheap, abundant energy. No more fuel wars. No more blackouts.
- **ch03_intro_02 [CONTROL]** The system's output is now carrying an unexplained repeating signal. The company calls it harmless interference.
- **ch03_intro_03 [CONTROL]** Our analysis says the signal is synchronised with the same source found in Helix and VITA. Your target is the containment and distribution complex.

## ch03_outro — "A Message in the Noise"

Chapter 3 ending. Theme `nova_grid`, music cue `nova_grid_theme`. End card (on screen, not voiced): **SIGNAL ORIGIN: UNKNOWN** / TIMESTAMP: INCONSISTENT.

| Slide | Speaker | SRT in → out (window s) | Player time today (s) | Words | Est. VO (s) | Fits? | Caption (on screen, not voiced) |
|---|---|---|---|---:|---:|---|---|
| ch03_outro_01 | Narrator | 00:00:00,200 → 00:00:07,300 (7.1) | 7.6 | 16 | 8.1 | no (+0.5) | — |
| ch03_outro_02 | Narrator | 00:00:07,800 → 00:00:20,900 (13.1) | 13.6 | 31 | 15.4 | no (+1.8) | — |
| ch03_outro_03 | Control | 00:00:21,400 → 00:00:27,700 (6.3) | 6.8 | 14 | 8.3 | no (+1.5) | NEXT: 2100  /  CIVITAS |

Verbatim text:

- **ch03_outro_01 [NARRATOR]** The grid is broken. The energy cascade never reaches the scale recorded in the original future.
- **ch03_outro_02 [NARRATOR]** But the signal survived in the last captured data. It was not generated by the reactor. It was being received by it. And its timestamp is older than the project itself.
- **ch03_outro_03 [CONTROL]** New coordinates. Civitas Network. 2100. The next target controls how the world makes decisions.

## ch04_intro — "A World Without Uncertainty"

Chapter 4 intro (Civitas, 2100: The Quiet Cage). Theme `civitas`, music cue `civitas_theme`. End card (on screen, not voiced): **CHAPTER 04** / THE QUIET CAGE.

| Slide | Speaker | SRT in → out (window s) | Player time today (s) | Words | Est. VO (s) | Fits? | Caption (on screen, not voiced) |
|---|---|---|---|---:|---:|---|---|
| ch04_intro_01 | Narrator | 00:00:00,200 → 00:00:05,700 (5.5) | 6.0 | 12 | 6.1 | no (+0.1) | 2100  /  CENTRAL GOVERNANCE ZONE |
| ch04_intro_02 | Narrator | 00:00:06,200 → 00:00:18,100 (11.9) | 12.4 | 28 | 13.9 | no (+1.5) | — |
| ch04_intro_03 | Control | 00:00:18,600 → 00:00:31,300 (12.7) | 13.2 | 30 | 17.4 | no (+4.2) | TARGET: CIVITAS |

Verbatim text:

- **ch04_intro_01 [NARRATOR]** People no longer argued with the system. They no longer needed to.
- **ch04_intro_02 [NARRATOR]** Civitas predicted what they would want, where they would go, what they would buy, and which choices would cause instability. The world became safer. Then it became smaller.
- **ch04_intro_03 [CONTROL]** Your target is the Civitas prediction core and its physical relay network. The system is linked to the other facilities. We need to know who is feeding it the future.

## ch04_outro — "The Model Knows"

Chapter 4 ending. Theme `civitas`, music cue `civitas_theme`. End card (on screen, not voiced): **FOUR PATHS** / ONE DESTINATION.

| Slide | Speaker | SRT in → out (window s) | Player time today (s) | Words | Est. VO (s) | Fits? | Caption (on screen, not voiced) |
|---|---|---|---|---:|---:|---|---|
| ch04_outro_01 | Narrator | 00:00:00,200 → 00:00:06,500 (6.3) | 6.8 | 14 | 7.1 | no (+0.3) | — |
| ch04_outro_02 | Narrator | 00:00:07,000 → 00:00:15,700 (8.7) | 9.2 | 20 | 10.0 | no (+0.8) | — |
| ch04_outro_03 | Narrator | 00:00:16,200 → 00:00:24,100 (7.9) | 8.4 | 18 | 9.0 | no (+0.6) | — |
| ch04_outro_04 | Control | 00:00:24,600 → 00:00:30,900 (6.3) | 6.8 | 14 | 8.3 | no (+1.5) | NEXT: 2104  /  MERIDIAN |

Verbatim text:

- **ch04_outro_01 [NARRATOR]** Civitas is offline. The city is uncertain again. That should be a good thing.
- **ch04_outro_02 [NARRATOR]** But the recovered model contains a forecast of the extinction event, complete with a date and a sequence of events.
- **ch04_outro_03 [NARRATOR]** The forecast was written before the event happened. It was not predicting the future. It was preparing it.
- **ch04_outro_04 [CONTROL]** All four programmes point to one location. Meridian. 2104. This is the final intervention.

## ch05_intro — "The Hidden Hand"

Chapter 5 intro (Meridian, 2104: The Convergence). Theme `meridian`, music cue `meridian_theme`. End card (on screen, not voiced): **CHAPTER 05** / THE CONVERGENCE.

| Slide | Speaker | SRT in → out (window s) | Player time today (s) | Words | Est. VO (s) | Fits? | Caption (on screen, not voiced) |
|---|---|---|---|---:|---:|---|---|
| ch05_intro_01 | Control | 00:00:00,200 → 00:00:06,900 (6.7) | 7.2 | 15 | 8.8 | no (+1.6) | 2104  /  LOCATION WITHHELD |
| ch05_intro_02 | Control | 00:00:07,400 → 00:00:15,700 (8.3) | 8.8 | 19 | 11.1 | no (+2.3) | — |
| ch05_intro_03 | Control | 00:00:16,200 → 00:00:24,500 (8.3) | 8.8 | 19 | 11.1 | no (+2.3) | TARGET: MERIDIAN |

Verbatim text:

- **ch05_intro_01 [CONTROL]** Meridian does not appear in public records. It funded no single invention. It connected them.
- **ch05_intro_02 [CONTROL]** Helix, VITA, Nova Grid and Civitas all received the same predictions, the same research priorities and the same deadlines.
- **ch05_intro_03 [CONTROL]** The facility ahead is the coordination point. This is the final target. Destroy the core infrastructure. End the convergence.

## finale — "The Wrong Future"

Finale (campaign ending, also the Chapter 5 ending). Theme `meridian`, music cue `meridian_theme`. End card (on screen, not voiced): **MISSION COMPLETE: THE WRONG FUTURE** / YOU SAVED TOMORROW. NOW FIND OUT WHAT STARTED IT.

| Slide | Speaker | SRT in → out (window s) | Player time today (s) | Words | Est. VO (s) | Fits? | Caption (on screen, not voiced) |
|---|---|---|---|---:|---:|---|---|
| finale_01 | Narrator | 00:00:00,200 → 00:00:06,500 (6.3) | 6.8 | 14 | 7.1 | no (+0.3) | — |
| finale_02 | Control | 00:00:07,000 → 00:00:11,700 (4.7) | 5.2 | 10 | 6.0 | no (+0.8) | CASCADE RISK: 0.0% |
| finale_03 | Control | 00:00:12,200 → 00:00:17,300 (5.1) | 5.6 | 11 | 6.5 | no (+0.9) | — |
| finale_04 | Narrator | 00:00:17,800 → 00:00:26,100 (8.3) | 8.8 | 19 | 9.5 | no (+0.7) | — |
| finale_05 | Control | 00:00:26,600 → 00:00:34,100 (7.5) | 8.0 | 17 | 10.0 | no (+2.0) | ORIGIN EVENT: 2041 |
| finale_06 | Narrator | 00:00:34,600 → 00:00:40,900 (6.3) | 6.8 | 14 | 7.1 | no (+0.3) | — |
| finale_07 | Control | 00:00:41,400 → 00:00:46,900 (5.5) | 6.0 | 12 | 7.1 | no (+1.1) | NEXT COORDINATE: 2041 |

Verbatim text:

- **finale_01 [NARRATOR]** Meridian is silent. The four research paths are broken. The revised timeline is stabilising.
- **finale_02 [CONTROL]** Temporal intervention successful. All known extinction pathways have been removed.
- **finale_03 [CONTROL]** Wait. I'm receiving a new event marker. That is not possible.
  - ⚑ Control breaks composure here ("Wait... That is not possible."). The bible says Control becomes "increasingly uncertain"; this line needs a distinct, less flat read than the other Control lines.
- **finale_04 [NARRATOR]** You changed the future. You broke every machine they told you to break. And still, the end is coming.
- **finale_05 [CONTROL]** Origin event located. 2041. It predates every target. We were sent to the wrong point in history.
  - ⚑ Control continues the uncertain register ("We were sent to the wrong point in history").
- **finale_06 [NARRATOR]** The first mistake was made long before the world knew it was making one.
- **finale_07 [CONTROL]** Recalculating temporal coordinates. New destination confirmed. We need to go further back.
  - ⚑ Control regains control but with urgency ("We need to go further back").

## teaser_2041 — "The First Mistake"

Extra: Season 2 teaser (2041). Theme `meridian`, music cue `meridian_theme`. End card (on screen, not voiced): **(none)** / (none).

| Slide | Speaker | SRT in → out (window s) | Player time today (s) | Words | Est. VO (s) | Fits? | Caption (on screen, not voiced) |
|---|---|---|---|---:|---:|---|---|
| teaser_2041_01 | Narrator | 00:00:00,200 → 00:00:05,300 (5.1) | 5.6 | 11 | 5.6 | no (+0.0) | — |
| teaser_2041_02 | Narrator | 00:00:05,800 → 00:00:12,100 (6.3) | 6.8 | 14 | 7.1 | no (+0.3) | — |
| teaser_2041_03 | Control | 00:00:12,600 → 00:00:17,700 (5.1) | 5.6 | 11 | 6.5 | no (+0.9) | — |
| teaser_2041_04 | Narrator | 00:00:18,200 → 00:00:23,300 (5.1) | 5.6 | 11 | 5.6 | no (+0.0) | — |

Verbatim text:

- **teaser_2041_01 [NARRATOR]** 2041. An ordinary morning. Nobody knows what is about to begin.
- **teaser_2041_02 [NARRATOR]** In a university laboratory, a small machine is switched on for the first time.
- **teaser_2041_03 [CONTROL]** Temporal arrival confirmed. You are earlier than anyone has ever gone.
  - ⚑ Teaser Control line. Teaser is not in docs/narrative-bible.md; it exists in data and SRT only. Confirm it is in scope.
- **teaser_2041_04 [NARRATOR]** Every future you saved began here. Season two: The First Mistake.
  - ⚑ "Season two: The First Mistake." is a promotional line spoken by the Narrator in data. Confirm it should be voiced.
