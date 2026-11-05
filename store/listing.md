# Google Play listing: Perfect Smash

Draft copy for the Play Console. Character limits are Play's (checked 2026-11-05; re-check at upload).
Everything here describes only what the build actually does.

## App details

| Field | Value | Limit |
|---|---|---|
| App name | Perfect Smash | 30 (13 used) |
| Short description | 100 story missions of physics demolition. Topple a rogue AI one smash at a time. | 80 (80 used) |
| Category | Game → Puzzle | |
| Tags (suggested) | Puzzle, Physics, Casual, Offline | |
| Contains ads | No | |
| In-app purchases | No | |
| Contact email | _owner to fill in_ | |
| Privacy policy URL | _owner to host `store/privacy_policy.md` and paste its URL_ | |

## Full description

> Up to 4000 characters; 1,249 used.

```
One smart hit. A spectacular chain reaction.

Port Halden is drowning in towers. ARCHITECT, the machine built to rebuild the city after the Flood, never stopped building, and its glowing red cores are draining the grid. You are Wrecker, the demolition specialist of Ground Unit Seven. Your job: bring ARCHITECT's structures down, one well-placed shot at a time.

Perfect Smash is a physics puzzle campaign of 100 missions across five chapters. Every mission opens with a radio briefing from your crew and ends with a debrief, so the story moves forward with every structure you topple.

• 100 handcrafted missions, unlocked one after another
• A full storyline with briefings and debriefs, read aloud by your device's voice if you like
• More than knocking out cores: deliver supply crates, bank shots off bounce pads, set off chains of explosive crates, and rescue friendly drones without breaking them
• Three kinds of ammo: standard, heavy and blast
• Real physics: weight, momentum and balance decide every outcome
• Three stars for solving a mission in as few shots as possible
• Plays fully offline. No account, no ads, no data collection

Short missions make it easy to play a few in a spare minute, and every failure is one tap from a retry.
```
## Graphics (in this folder)

| Asset | File | Play requirement |
|---|---|---|
| App icon 512×512 | `../assets/icon/play_store_512.png` | 32-bit PNG, 512×512 |
| Feature graphic | `feature_graphic.png` | 1024×500, JPEG or 24-bit PNG (no alpha) |
| Phone screenshots | `screenshot_1_menu.png` … `screenshot_6_debrief.png` | 2–8 images, 16:9, 24-bit PNG |

Screenshots are 1920×1080 landscape, rendered from the real game by `tools/render_store_art.gd`. Check Play's
current tablet screenshot rules before reusing them in the 7-inch and 10-inch tablet slots.

Suggested captions (if a store experiment uses captions later):
1. 100 missions, five chapters
2. Every mission starts with a briefing
3. Bring down the Spire
4. Explosive chain reactions
5. Watch it all come down
6. The story moves with every win

## Release notes (first closed test, 0.3.0)

```
First test build: the full Operation Rebuild campaign. 100 missions in five chapters, briefings and
debriefs (with optional voice narration), supply drops, bounce pads, explosive crates, drone rescues and
three ammo types. Settings → Copy play report lets you send us your results. Thanks for testing!
```
