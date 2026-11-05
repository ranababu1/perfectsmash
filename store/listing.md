# Google Play listing: Perfect Smash

Draft copy for the Play Console. Character limits are Play's (checked 2026-11-05; re-check at upload).
Everything here describes only what the build actually does.

## App details

| Field | Value | Limit |
|---|---|---|
| App name | Perfect Smash | 30 (13 used) |
| Short description | Aim one shot, topple the tower, and watch the chain reaction unfold. | 80 (68 used) |
| Category | Game → Puzzle | |
| Tags (suggested) | Puzzle, Physics, Casual, Offline | |
| Contains ads | No | |
| In-app purchases | No | |
| Contact email | _owner to fill in_ | |
| Privacy policy URL | _owner to host `store/privacy_policy.md` and paste its URL_ | |

## Full description

> Up to 4000 characters; 1,007 used.

```
One smart hit. A spectacular chain reaction.

Perfect Smash is a short, satisfying physics puzzle. Each level is a small structure of wood, stone and glass with one or more red cores hidden in it. You get a few shots. Pull back, aim, and let go: the ball flies, beams tip, glass shatters, and the whole thing comes down — if you picked the right spot.

The fun is in reading the structure. Which beam holds everything up? Will that tower fall forward or back? Can one well-placed shot knock out three cores at once?

• 20 handcrafted levels that teach one idea at a time, then combine them
• Real physics: weight, momentum and balance decide every outcome
• Three stars for solving a level in as few shots as possible
• Simple drag-to-aim controls with an optional short aim guide
• Calm, clean visuals that keep every collapse easy to follow
• Plays fully offline. No account, no ads, no data collection

Short levels make it easy to play a few in a spare minute, and every failure is one tap from a retry.
```

## Graphics (in this folder)

| Asset | File | Play requirement |
|---|---|---|
| App icon 512×512 | `../assets/icon/play_store_512.png` | 32-bit PNG, 512×512 |
| Feature graphic | `feature_graphic.png` | 1024×500, JPEG or 24-bit PNG (no alpha) |
| Phone screenshots | `screenshot_1_menu.png` … `screenshot_5_clear.png` | 2–8 images, 16:9, 24-bit PNG |

Screenshots are 1920×1080 landscape, rendered from the real game by `tools/render_store_art.gd`. Check Play's
current tablet screenshot rules before reusing them in the 7-inch and 10-inch tablet slots.

Suggested captions (if a store experiment uses captions later):
1. Twenty handcrafted structures
2. Pull back, aim, release
3. Watch it all come down
4. Set up the chain reaction
5. Three stars for the cleanest solve

## Release notes (first closed test, 0.2.0)

```
First test build. 20 levels, drag-to-aim, sound and vibration settings, an optional aim guide,
and a play report you can copy from Settings and send to us. Thanks for testing!
```
