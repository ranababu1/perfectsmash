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

## Godot check (run 2026-11-10)

`tools/bg_godot.py` copies the layers into a scratch project, writes one scene spec per set (base far, mid and near; variants use the variant far over the base band mid and near), imports, then renders each set under the MissionView camera (FOV 40, offset (-2.2, 2.3, 10.5)) and sun copied from `scripts/mission/view/mission_view.gd`, with a helix_01-like greybox band in front and no back wall:

```
/opt/tfj-tools/bin/godot --headless --path /tmp/tfj-surf-godot --import
import rc 0
xvfb-run -a -s "-screen 0 1280x720x24" /opt/tfj-tools/bin/godot --path /tmp/tfj-surf-godot --rendering-driver opengl3 --resolution 1280x720 --script res://bg_render.gd -- --spec=/tmp/tfj-surf-godot/spec.json --out=/tmp/tfj-surf-godot/out
BGRENDER game_cvt_1 ... BGRENDER game_vta_v2   (30 sets, no ERROR lines)
render rc 0
```

Renders: `previews/godot_<chapter>_sets.webp` (bands 1 to 4, then V1 and V2). Composites of the full cards: `previews/contact_<chapter>_sets.webp`.

What the renders show, for review:

- At this camera the play band covers the lower half of the screen, so mostly the lower half of each far plate and the mid and near cards read. Skies matter less than the skyline and ground line.
- Repeats of mid and near cards are visible on wide shots (for example the Civitas spire mid card). Alternate flips help; a `-B` card per band would remove it if needed.
- Meridian excavation (band 1 and V1) is the brightest set and competes most with the greybox blocks. If it is too strong once real components are in, lower the card `albedo_color` to about 0.8.
- The Meridian convergence mid and near cards were regenerated after review (the first pair read as clay renders and did not sit in the night light).

## Helix review (batch 9)

Every Helix set was checked against the chapter brief (Helix Systems AI infrastructure: server halls, data-centre architecture, cooling, cold steel and cyan with orange warnings) and the SV-04 style frame. Changes, same ids and paths:

- Band 2 logistics: the first far, mid and near plates read as a cargo port (container cranes over water, grab claws, shipping containers). All three were regenerated as data-centre logistics: a server-hall campus with an enclosed rack conveyor and lit dock doors on the far plate, a rack storage tower and a conveyor bridge into a dock on the mid card, and an overhead rack carrier, sealed server crates on a pallet mover and a cable column on the near card.
- Band 3 cooling: the far plate showed round power-station cooling towers and solar fields, and the near card had a smokestack, so the set read as a power plant (and too close to Nova Grid). Regenerated: the far plate is a server-hall cooling yard with rooftop dry coolers and square evaporative towers; the near card is an insulated coolant manifold and a dry-cooler unit. The mid card (chillers and pipe bridge) was kept. A second far attempt was rejected because its high camera put the ground edge well below the horizon.
- Band 4 core: contract 10 asks for a quiet band behind the critical asset. The near card was regenerated with an empty low middle third (the earlier card had a tall tower in the centre and a red beacon mast). The mid card, the band 4 far and the V2 far now get a quiet-centre pass in `bg.py`: across the middle 30 % of the card (8 % feather) local contrast is reduced, red light is desaturated and bright emission is pulled down. The far plates keep their detail (a lighter pass); the cyan core tower on the far plate is dimmed, not removed.
- Bands 1, V1 and V2 were in brief and were kept.
- `bg_godot.py HLX_1 HLX_2 HLX_3 HLX_4 HLX_V1 HLX_V2` was rerun: import rc 0, six `BGRENDER game_hlx_*` lines, render rc 0, no ERROR lines. `previews/godot_helix_sets.webp` and `previews/contact_helix_sets.webp` were regenerated.


## Environment modules, statics, props and landmarks (3d-kits stream)

These are the modular environment kits per chapter, built in scripted Blender (`destructibles/source/blender/kits/env_*.py`, pipeline `tfjenv.py`, runner `runenv.py`). Each chapter has 21 pieces, with ids from contract section 19:

| Group | Ids |
|---|---|
| Floor | `<CH>-ENV-FLOOR_TILE-A` (1 x 1 m), `-FLOOR_TILE-B` (4 x 4 m), `-FLOOR_TRENCH-A` (4 x 4 m with a service trench) |
| Mid-back walls | `-BACK_WALL-A` (solid), `-BACK_WALL-B` (window), `-LOW_WALL-A`, `-PILLAR-A` |
| Overhead | `-CATWALK-A`, `-CEILING_TRUSS-A` |
| Massing | `-MASSING_BLOCK-A`, `-MASSING_TOWER-B` |
| Statics | `-LEDGE_STATIC-A` (200 x 30 px), `-PLINTH_STATIC-A` (100 x 60 px), depth 1.6 m, centred like components |
| Near-back props | `<CH>-PRP-CRATE_STACK-A`, `-PIPE_RUN-A`, `-CONSOLE-A`, `-TANK-A` |
| Band landmarks | Four `<CH>-PRP-<KEY>-A` per chapter (one per five levels, mid-back), at most 3,000 tris |

Far background cards (`-BG-`) are textures from the surfaces stream; they are not in this kit.

### Conventions

- **Origins.**
  - Floor tiles have their top face at y = 0 and their left edge at x = 0, with depth centred on z = 0, so they tile along +x and in z.
  - Walls, pillars, props, massing and landmarks have their origin at the bottom centre.
  - Statics have their origin at the centre of the collision rectangle.
  - Catwalks and trusses sit at the bottom centre of the piece.
- **Layer darkening.** Darkening is baked into `baseColorFactor`, giving value relative to gameplay pieces of: floor 0.5, near-back 0.72, mid-back 0.52, landmark 0.62 and statics 1.0. VITA floor, mid-back and landmark pieces get a further 0.72 because the chapter is white. This keeps backgrounds 30-50% below the gameplay band, as section 10 asks.
- **Materials.** Slots are the same as the destructibles: `mat_<material>_<ch>[_<zone>]`, `trim_<zone>_<ch>`, `emit_<colour>_<ch>` and `glass_<name>_<ch>`. Colour is in the material, with no `COLOR_0`. UV0 is a box projection at 1 UV = 1 m.
- **Emission.** Emission is restrained: thin strips in the chapter light colour. Landmark cores use white, not red, because red marks critical targets. The Meridian floor inlays are non-emissive rings with one short violet arc. The Nova Grid hazard marking is on the tile corner only, so tiled floors do not read as lane lines.
- **With the surfaces stream's cards.** The kit walls are 6 m tall, not the greybox's 9 m, so at z -6 under the game camera the near, mid and far cards show above them. Leave wall runs open where a landmark stands (the test frames do), and use `BACK_WALL-B` windows to break up long runs. The massing pieces (10 and 14 m) belong at the frame edges, not in front of a card's focal area.
- **Budget.** At most 2,000 tris per module and 3,000 per landmark; `tfjenv.py` decimates down to the budget if needed.
- **Physics.** There is no collision geometry; MissionView keeps its 2D physics.

### Commands

    cd generated_assets/destructibles/source/blender
    TFJ_SAMPLES=32 blender -b --factory-startup --python runenv.py -- kits.env_kits [ID filters] [--no-render]
    python3 sheets.py grid ../../../environments/previews/<ch>_environment_sheet.webp "/workspace/tfj-masters/3d-kits/stats_env/<CH>-*.json" "<title>" 6

Godot test frame (a full chapter set at the exact MissionView camera, sun and environment):

    TFJ_LANDMARK=<landmark key, lower case> TFJ_COMPONENTS="<stem>:<h m>:<w m>,..." xvfb-run -a -s "-screen 0 1280x720x24" \
      godot --path <any project> --rendering-driver opengl3 --script generated_assets/destructibles/source/godot/kit_scene.gd \
      -- out.png generated_assets <chapter> <code>

The test frames are in `previews/<ch>_godot_test_frame.webp`.

### Rights

This is original procedural work. The scripted Blender code was written by the 3d-kits asset agent (AI-assisted authorship). No third-party meshes or textures are used. Ownership is not legally settled for AI-assisted work, and nothing is marked commercially cleared.

## Premium uplift pass, batch 1: Helix environment (3d-kits stream, 2026-11-10)

The 21 Helix environment pieces were rebuilt in place with the same ids.

- **Materials.** Textured slots use the same scheme as the components, with relative URIs to `generated_assets/materials/`. Floor pieces use the chapter floor set with its emission inlays, at a low metallic value.
- **Secondary detail** (shared builders, so the other chapters gain it as they are rebuilt):
  - floor: plate bolts and short amber seam inlays;
  - walls: pilaster bolts, a conduit pair with brackets, a status screen and LEDs;
  - low wall: bolts, a screen and a kick plate;
  - pillar: base bolts and a conduit;
  - catwalk: deck grating and kick plates;
  - massing: ribs and roof louvres.
- **Showcase.** `showcase/helix_showcase_layout.json` is a Helix scene for `destructibles/source/godot/showcase.gd`. It holds floor, walls, background rack rows and the gameplay band of every Helix component, plus the operative with a weapon on `weapon_socket`. Frames:
  - `previews/hlx_showcase_missionview.webp` is the MissionView camera and lighting exactly as the game sets them today. `hlx_godot_test_frame.webp` is the same frame.
  - `previews/hlx_showcase_graded.webp` adds what GL Compatibility allows: reflection sky, ACES tonemap, glow, depth fog, a cool rim light and local amber and cyan omni lights.
  - `previews/hlx_showcase_close.webp` is a closer graded view of the core deck.
  - These are honest engine frames. They do not reach the SV-04 painting: SV-04 uses a much higher camera, painted bounce light and AO, and GL Compatibility has no SSAO, SDFGI or volumetric fog.
- **Checks.** Godot lineup: 21 of 21 files load.

## Helix showcase lift (2026-11-10, 3d-kits, after owner review)

- Review note: the Helix MissionView showcase frame was too dark for a phone screen. `showcase.gd` gains two layout opt-ins: `asis_exposure` / `asis_ambient` (presentation lift for the MissionView-camera frame) and `fill` (a soft camera-side fill light, no shadow). Helix uses exposure 1.3, ambient 0.72 and fill 0.42 for that frame, and exposure 1.12, ambient 0.55 for the graded frame. The background stays dark, so the mood holds.
- `previews/hlx_godot_test_frame.webp` is not regenerated and stays the strict MissionView lighting reference.
- Re-rendered with the pass-2 operative and Kinetic Accelerator: `previews/hlx_showcase_missionview.webp`, `previews/hlx_showcase_graded.webp`, `previews/hlx_showcase_close.webp`.

## VITA environment premium pass and showcase (2026-11-10, 3d-kits)

- 21 VITA environment pieces rebuilt with the shared premium detail in `env_common.py` (wall pilasters, conduits, screens and LEDs, low wall kick plates, pillar conduits, catwalk grating, massing louvres and ribs; no floor bolts in VITA). Tris 96 to 1,500. Godot `kit_lineup.gd`: 21/21 load.
- Showcase: `showcase/vita_showcase_layout.json` (generated from the Helix scaffold by `destructibles/source/blender/mk_ch_showcase.py`: VITA kit pieces, a gameplay band of VITA components on a lab deck with the gene vault core, background rows, the operative with the Kinetic Accelerator B). The white lab surfaces clip under the Helix lift, so VITA uses a lower lift: MissionView-camera frame exposure 1.0, ambient 0.55, fill 0.22; graded exposure 0.8.
- Previews (after): `previews/vta_environment_sheet.webp` (Cycles), `previews/vta_showcase_missionview.webp`, `previews/vta_showcase_graded.webp`, `previews/vta_showcase_close.webp`, and `previews/vta_godot_test_frame.webp` (strict MissionView lighting, `kit_scene.gd`, regenerated with the new pieces). Before: the same paths at commit `9091af3` (the showcase frames are new).
- There is no VITA concept frame; the check was against the chapter style (white clinical lab, mint glass, red helix accents) and the Helix premium level.

## Fix: environment pieces were darkened twice (2026-11-10, 3d-kits)

- Found while checking Nova Grid, Civitas and Meridian against their earlier Godot test frames: `tfjenv.build` still multiplied COLOR_0 (the baked AO) by the layer value, which the premium pass already puts in baseColorFactor. Textured environment pieces therefore read about 2.5 to 6 times too dark in Godot (floor COLOR_0 mean about 0.2 instead of about 0.65). This was also the main reason the Helix showcase looked very dark.
- Fixed in `tfjenv.py`: the layer value lives in baseColorFactor only. All 105 environment pieces (5 x 21) were rebuilt. IDs, tris and slots are unchanged; only COLOR_0 changed.
- Helix and VITA were re-rendered with the fix. The presentation lift is smaller now, so Helix keeps its low-key mood: MissionView-camera frame exposure 1.0, ambient 0.55, fill 0.22; graded exposure 0.92. VITA: 0.95 and graded 0.72. `hlx_godot_test_frame.webp` and `vta_godot_test_frame.webp` were regenerated with `kit_scene.gd` (strict MissionView lighting, no lift).
- Godot `kit_lineup.gd`: Helix 21/21 and VITA 21/21 environment files load, COLOR_0 on all.
- Previews (after): `previews/hlx_showcase_missionview.webp`, `hlx_showcase_graded.webp`, `hlx_showcase_close.webp`, `hlx_godot_test_frame.webp`, `hlx_environment_sheet.webp`, and the same five for `vta_`. Before: the same paths at commit `c830eaa`.

## Nova Grid environment premium pass and showcase (2026-11-10, 3d-kits)

- 21 Nova Grid environment pieces rebuilt with the shared premium detail (`env_common.py`: floor plate bolts, wall pilasters, conduits, screens and LEDs, kick plates, pillar conduits, catwalk grating, massing louvres) and the COLOR_0 fix above. Tris 116 to 2,476 (the transformer yard landmark is the largest). Godot `kit_lineup.gd`: 21/21 load.
- Showcase: `showcase/nova_grid_showcase_layout.json` (from `destructibles/source/blender/mk_ch_showcase.py`): Nova Grid kit pieces, a gameplay band of Nova Grid components with the reactor core, background rows, the operative with the Kinetic Accelerator B. MissionView-camera frame exposure 1.0, ambient 0.55, fill 0.22; graded exposure 0.9.
- Previews (after): `previews/nvg_showcase_missionview.webp`, `nvg_showcase_graded.webp`, `nvg_showcase_close.webp`, `nvg_godot_test_frame.webp` (strict MissionView lighting), `nvg_environment_sheet.webp`. Before: the same paths at commit `023939a` (the showcase frames are new). There is no Nova Grid concept frame; the check was against the chapter style (heavy industrial power plant, gunmetal, hazard yellow, amber pips) and the Helix premium level.
