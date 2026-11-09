# Environments: background layers, atmospherics and loops (surfaces stream)

All entries are `pending_review`. Masters, source logs and build scripts are kept outside the repo in `/workspace/tfj-masters/surfaces/` (`bg/`, `atmos/`, `tools/`).

## What is here

| Folder | Contents |
|---|---|
| `helix/`, `vita/`, `nova_grid/`, `civitas/`, `meridian/` | Per chapter: 4 band sets (far, mid, near), 2 variant far plates, a chapter-tinted haze overlay. Nova Grid also has a distant arc loop. |
| `shared/` | 7 static atmosphere overlays and 7 animated loops (contract section 13 flipbooks). |
| `screens/` | Loading art per chapter, the main menu backdrop and five chapter transition cards (1920 x 1080, no text). |
| `previews/` | Contact sheets and Godot renders under the game camera. |
| `level_schedule.json` | Level 1 to 100: which far, mid and near ids to load, with the variant far plate already substituted. `ready` is false where a layer is still being produced. |

## Ids and coverage

- Layers are `<CH>-BG-<FAR|MID|NEAR>_<band>_<ZONE>-A`; variants `<CH>-BG-FAR_V1_<ZONE>-A` and `_V2_`.
- The coverage matrix rotates the first four sorted `<CH>-BG-*` ids by band; those are `FAR_1` to `FAR_4`, which are the base far plates in band order. Overlay, loop, loading and transition ids all sort after them, so they do not disturb the rotation.
- Band zones follow contract section 19 (Helix server hall, logistics, cooling, core; VITA cleanroom, bioreactor, archive, growth; Nova Grid intake, cooling, transformer, reactor; Civitas street, plaza, control, spire; Meridian excavation, cavern, anchor, convergence).

## Placement under the MissionView camera (FOV 40, camera height about 3.9 m)

| Layer | Card size | z | Vertical placement | Notes |
|---|---|---|---|---|
| Far (opaque, 2048 x 1024 WebP) | 72 x 36 m | -30 | horizon row of the image at camera height | one card |
| Mid (RGBA, 2048 x 1024 WebP) | 28 x 14 m | -20 | card bottom at y -1 | repeat 3 across, alternate flips |
| Near (RGBA, 2048 x 1024 WebP) | 16 x 8 m | -12 | card bottom at y -0.4 | repeat 5 across, alternate flips, 5 m offset |

- Use unshaded `StandardMaterial3D` (albedo texture, alpha transparency for mid and near, linear filter with mipmaps, no shadow casting). Cards are graded for an unlit read, so scene lights should not touch them.
- Caveat: the current greybox back wall at z -6 (9 m tall) hides every card. The renders in `previews/` leave it out. The environment kit needs to open that wall up or lower it before these layers show in game.
- Overlays: lay `<CH>-BG-OVL_HAZE-A` (2048 x 512, mix) across the horizon row over the far and mid cards. Shared overlays: haze band, ground mist and smoke drift (mix), light shafts and dust motes (add), smoke column (mix), rain streaks (mix, scroll UV y).
- Loops (`animation` block in the manifest, straight alpha, 2 px margins, periodic so they loop cleanly): smoke plume, steam vent, haze drift and rain (mix), searchlight sweep, beacon pulse (red), warning beacon (amber) and the Nova Grid distant arc (add). Play with an `AnimatedSprite3D` or a flipbook shader on a quad; set the blend from the manifest.

## How they were made

1. Source plates came from the GenerateImage tool (every accepted and rejected source is logged in the masters `genlog.tsv`). Far plates were prompted as wide matte paintings. Mid and near plates were prompted as cut-out elements on a flat green screen (magenta where the subject has green light, such as the VITA growth band).
2. Far: crop to 2:1 around the requested horizon, Real-ESRGAN x4plus (ONNX, CPU, tiled), Lanczos to 2048 x 1024, light grade per chapter.
3. Mid and near: Real-ESRGAN general-x4v3, chroma key with spill subtraction, a small erode, content shifted down so it meets the card bottom, ground extension, soft edge fade, and a grade toward the matching far plate's haze colour so layers sit in the same air.
4. Atmospherics and loops are procedural (periodic spectral noise in numpy, `atmos.py`), no AI source.

Review rejects included a haze slab baked into a Nova Grid mid plate, monolith shapes that read as letters on a Meridian far plate, and stylised or CG-looking Meridian plates (re-prompted as photographic). Each set was checked as a composite at full size.

## Rights

AI-generated plates: rights not verified, not commercially cleared. Procedural overlays and loops: original procedural work (AI-assisted authorship), ownership not legally settled, not marked commercially cleared. Real-ESRGAN models: BSD-3-Clause (xinntao/Real-ESRGAN).

## Godot check

See the section below once renders are complete; nothing is claimed here until the command and its output are recorded.
