# Voice direction — Temporal: First Jump cinematics

Status: **phase 1 proposal, pending Imran's approval.** Based on the owner brief (2026-11-11), `docs/narrative-bible.md` §2 and §12, `docs/plan.md` (single narrator identity; Control "calm, precise and increasingly uncertain"; do not reveal who Control is) and `docs/visual-audio-production-guide.md` §7 (125-145 wpm, close-mic documentary, Control more clinical and processed but intelligible, music ducks under narration).

The existing story has exactly **two voices**: `narrator` (27 slides) and `control` (23 slides). No other character speaks (AURA, VITA, Nova Grid, Civitas and Meridian are systems or companies that are described, never voiced). The operative never speaks. No new voices are proposed.

## 1. Narrator

**Who:** the voice of the people who sent the operative, looking back from 2149. A witness, not a hero. Knows how it ends and is quietly carrying that weight.

- **Register:** mature (reads 40-60), baritone, close-mic, intimate. Documentary authority, sci-fi thriller undertow.
- **Delivery:** restrained, credible, never trailer-voice, never shouting. Emotion comes from timing and weight, not volume.
- **Pace:** 125-145 wpm inside sentences; full stops are real breaths (about 0.4 s), the last sentence of a slide lands after a longer beat (about 0.6 s).
- **Pitch and dynamics:** sentence ends fall and settle. Loudness range stays small (LRA under 6 LU) so lines sit evenly over music.
- **Emphasis pattern:** the short fragments carry the drama. "Privacy for protection. Limits for possibility." "No army. No second attempt. No guarantee of return." "It was not predicting the future. It was preparing it." Give each fragment its own space; do not run them together.
- **Arc across the campaign:** Opening (grave, elegiac), chapter endings (relief, then a cooler turn on the reveal line: "Someone called it Meridian.", "Someone gave it the answer."), finale (the quietest and heaviest read: "And still, the end is coming."). The teaser (if in scope) is lighter and curious: "An ordinary morning."
- **Accent:** to decide (open question). The script uses British spelling (programme, civilisation, synchronised). Candidate A is a neutral North-American baritone; candidate B is British.

## 2. Control

**Who:** the mission-control intelligence or operator guiding the jump. Identity unknown by design (bible §12). It believes it is in control and is right, until the finale.

- **Register:** calm, precise, even, slightly cool. Mid-low pitch with a narrow range (it does not emote). Every word intelligible.
- **Delivery:** declarative, unhurried, no warmth on instructions, no hesitation. Numbers and coordinates are crisp ("twenty eighty-nine", "Nova Grid. twenty ninety-six.").
- **Subtly unsettling:** come from evenness. It says "Destroy the structures" and "Do not mistake the laboratories for the people inside them" in the same unbothered tone. No robot effects, no pitch-shifting.
- **Arc:** steady through chapters 1-4. Finale slide 3 ("Wait. I'm receiving a new event marker. That is not possible.") is the first crack: a real pause after "Wait.", slightly faster and lower on "That is not possible." Slides 5 and 7 stay controlled but with urgency underneath ("We need to go further back."). The countdown ("three... two... one.") is metronomic, about 0.7 s between beats.
- **Treatment (subtle, intelligible):** high-pass about 150 Hz, gentle low-pass about 10.5 kHz, small presence lift around 2.8 kHz, a slight cut around 400 Hz, a very short synthetic room (about 17-29 ms reflections, low level) and light compression. It reads as "transmitted", not "robot". The same chain is applied to every Control line.
- **Gender:** not fixed by the story. The samples use a female Control so the two voices separate clearly from the male narrator. This is a creative choice to confirm.

## 3. Pronunciation sheet (model input only; subtitles never change)

| Text | Spoken as | Note |
|---|---|---|
| 2149 | twenty one forty-nine | |
| 2089 / 2092 / 2096 | twenty eighty-nine / twenty ninety-two / twenty ninety-six | |
| 2100 | twenty one hundred | |
| 2104 | twenty one oh four | |
| 2041 | twenty forty-one | |
| AURA | "AW-ruh" (spoken as a word, not spelled out) | |
| VITA | "VEE-tuh" (proposed) | open question: VEE-tuh or VY-tuh |
| Civitas | "SIV-ih-tahss" (proposed) | open question |
| Meridian, Helix, Nova Grid, New Avalon, Arclight, Kestrel | plain English | |

## 4. Technical voice spec (both voices)

- One file per slide, mono, 44.1 kHz, Ogg Vorbis for the game; FLAC/WAV masters kept off-repo.
- Integrated loudness -18 LUFS per clip (ASSET_CONTRACT §"Voice -18 LUFS"), true peak at -1.5 dBTP or lower before encoding (at -1 dBTP or lower after encoding), LRA under 6 LU.
- About 60 ms of silence before the first word and about 180 ms after the last; no long pads, no breaths clipped, no fades over words.
- Identical recipe (same voice, settings and chain) for every line of a role, so any line can be re-rendered or picked up alone without a noticeable change.

## 5. ElevenLabs realisation (approval sample, 2026-11-12)

| Role | Voice | voice_id | Model | Settings |
|---|---|---|---|---|
| Narrator | TFJ Narrator (Voice Design, British baritone) | `ekSI8bXMs4l0ajdl4bMT` | `eleven_v4` | stability 0.4, similarity 0.8 |
| Control | TFJ Control (Voice Design, cool British female AI) | `RyGrFtWwuk4TeI35VwiE` | `eleven_v4` | stability 0.5, similarity 0.8 |

- Direction uses v4 audio tags, for example:
  - `[thoughtful, quietly reflective]`, `[ominous]`, `[intimate, close, almost a whisper]`;
  - for Control: `[calm, precise, clinical]`, `[calm, precise, metronomic]`;
  - for the finale: `[startled, losing composure]`, `[shaken, anxious]`.
- Pauses use `[pause]` and ellipses. Per-line tagged text is in `audio/source/narration/elevenlabs/direction.json`, and the spoken words are verbatim.
- Control keeps a light processing chain (band-limit, presence lift, faint 17/29 ms comb) so it reads as a system voice without sounding robotic.

Details are in [ELEVENLABS_APPROVAL_SAMPLE.md](ELEVENLABS_APPROVAL_SAMPLE.md).

## 6. Full package realisation (2026-11-12)

Every slide of all 12 cinematics is now voiced with the same voices, model and settings as the approval sample (section 5). The tagged input for every line is in `audio/source/narration/elevenlabs/direction.json`; the spoken words are verbatim. The beats were directed as follows:

- **Opening.** As the approval sample: reflective, then regret, then dread, then resolve, then Control's clinical brief and countdown.
- **Chapter intros.** Control (Helix, Nova Grid, Meridian) or the narrator (VITA, Civitas) arriving in a new year: calm, precise, a hint of warning as the mandate expands.
- **Chapter outros.** Relief that the intervention worked, then unease as the evidence points elsewhere, then Control's clinical handoff to the next coordinates. The music turns from the relative major to the minor drone on the unease line, and the timeline-shift hit lands on Control's new coordinates.
- **Finale.** Exhausted relief, Control's satisfaction, then Control shaken ("Wait…", "That is not possible.", "We were sent to the wrong point in history"), the narrator's heavy "And still, the end is coming.", and the resolve to go further back.
- **Teaser 2041.** Quiet ordinary morning, the first machine switching on, Control's arrival ("You are earlier than anyone has ever gone"), and a cinematic close: "Season two: The First Mistake."

Selection, measurements, rights and engine notes: [ELEVENLABS_APPROVAL_SAMPLE.md](ELEVENLABS_APPROVAL_SAMPLE.md), [LICENSING_PROVENANCE.md](LICENSING_PROVENANCE.md), [CODING_AGENT_NARRATION_GUIDE.md](CODING_AGENT_NARRATION_GUIDE.md), [NARRATION_MANIFEST.json](NARRATION_MANIFEST.json), [FINAL_SCRIPT.md](FINAL_SCRIPT.md).
