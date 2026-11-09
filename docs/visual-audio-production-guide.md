# Visual & Audio Production Guide

**Project:** Temporal: First Jump (owner-approved 2026-11-09; application ID `dev.imrn.temporal1`)  
**Narrative:** The Wrong Future  
**Initial content:** 100 levels / five chapters  
**Purpose:** A handoff guide for the art, audio and coding agents. This document defines the asset language and production requirements. It does not imply that assets are integrated into Godot.

## 1. Visual identity

### Creative direction

Grounded cinematic science fiction. Think believable near-future industrial architecture, ominous scale, practical materials, atmospheric lighting and restrained temporal energy. The game should feel like a serious sci-fi thriller, not generic neon cyberpunk.

**Palette**
- Base: charcoal, graphite, cold steel, muted concrete.
- Temporal energy: controlled cyan / blue.
- Warning accents: restrained amber and occasional red.
- Chapter-specific secondary colours are allowed, but the temporal charge remains cyan/blue.

**Avoid**
- Purple/pink gradients and excessive bloom.
- Random holographic glyphs, unreadable fake text, floating UI debris.
- Cartoon proportions, fantasy weapons, generic space-opera armour.
- Logos, real company names, recognisable real-world brands.
- Text, subtitles, UI, watermarks or signatures baked into art.

### Composition
- Cinematic slides: 16:9 landscape, ideally 1920x1080 or higher.
- Gameplay backgrounds: separate from the foreground structure; keep low contrast behind destructible objects.
- Leave lower 15-18% visually quiet for subtitles in cinematics.
- Keep the main visual focal point away from the HUD and skip/continue controls.
- Use clean, uncluttered silhouette readability at phone scale.
- Generate clean plates. Add all typography, chapter labels, dates and interface elements in Godot.

## 2. Chapter art bible

| Chapter | Environment | Palette / lighting | Main props |
|---|---|---|---|
| I. The Machine That Decided | Helix corporate campus, server halls, logistics and civic automation | Steel, glass, cold cyan, small red warnings | Server racks, relay towers, security gates, autonomous logistics |
| II. The Price of Perfection | VITA biotech campus, clean rooms, bioreactor halls | Pale green, sterile white, cool teal | Bioreactors, lab platforms, sealed research equipment, storage |
| III. The Energy Beneath | Nova Grid power basin and containment plant | Dark steel, amber reactor glow, cyan signal | Reactor supports, cooling towers, cable bridges, containment rings |
| IV. The Quiet Cage | Civitas civic control district and prediction centre | Blue-grey, desaturated city light, cold white screens | Surveillance masts, data exchanges, control towers, civic infrastructure |
| V. The Convergence | Hidden underground Meridian megastructure | Charcoal, deep cyan, restrained red/amber alarms | Combined server/lab/reactor architecture, relay structures, central core |

## 3. Temporal Charge design

The existing projectile becomes a **Temporal Charge** through art and audio only.

Design:
- Compact, dense, engineered object; recognisable circular or capsule-like silhouette.
- Dark metal outer shell with a contained cyan temporal core.
- A few segmented rings or stabiliser fins, not a complicated missile.
- Strong silhouette at 48-64 px on a phone.
- One restrained cyan trail and a short temporal distortion at launch.
- Impact: brief compression ripple, sharp energy crack and debris response.
- Idle animation: slow core pulse, not continuous particle spray.

Deliverables *(Superseded 2026-11-09 — see “3D-ready production pipeline” at the end of this guide.)*
- Main projectile sprite, transparent PNG.
- Optional separate core/glow layer if the existing renderer can animate it cheaply.
- Small HUD icon.
- Launch trail / impact sprite sheets only if performance and integration justify them.

Do not alter the projectile's collision shape, mass, impulse, launch force or physics tuning as part of the reskin.

## 4. Cinematic inventory

First release target: 11 sequences:
1. Opening cinematic.
2. Chapter I intro and outro.
3. Chapter II intro and outro.
4. Chapter III intro and outro.
5. Chapter IV intro and outro.
6. Chapter V intro and level-100 finale.

Target stills: approximately 40-50 total. A sequence should usually use 4-6 images. Reframe, crop, add subtle parallax and camera movement rather than generating a new image for every sentence.

### Opening cinematic shot list

| Slide | Visual | Camera / motion | Voiceover focus |
|---:|---|---|---|
| 1 | Ruined future megacity at dusk | Very slow push-in, smoke movement | Humanity believed every problem had a solution |
| 2 | Montage-like wide view of data centre, biotech lab and reactor silhouettes | Slow lateral pan / dissolves | Convenience, privacy and limits were traded away |
| 3 | Abandoned city and distant survivor shelter | Slow pull-back | Systems failed; almost nothing remained |
| 4 | Hidden temporal experiment chamber, unstable ring | Slow push-in, low-frequency pulse | Matter can be sent backwards |
| 5 | Anonymous operative silhouette facing the device | Subtle parallax, no visible face | One operative, no second attempt |
| 6 | Temporal Charge close-up on a technical platform | Slow orbit / light pulse | Charge synchronisation and target instructions |
| 7 | Helix facility at dawn, insertion distortion in foreground | Gentle forward movement | Mission begins |

### Chapter intro/outro shot guidance

- **Chapter I intro:** pristine Helix campus, server interior, AURA city map abstraction, target campus.
- **Chapter I outro:** Helix lights going dark, ordinary city lights returning, unknown Meridian signature.
- **Chapter II intro:** VITA campus, clean-room silhouette, bioreactor, sealed trial wing.
- **Chapter II outro:** abandoned sterile lab, stopped production, matching signature on two data records.
- **Chapter III intro:** enormous reactor basin, containment rings, energy output.
- **Chapter III outro:** grid going dark, signal waveform still pulsing, timestamp anomaly.
- **Chapter IV intro:** city under surveillance, civic control room, prediction screens.
- **Chapter IV outro:** city regaining independent activity, future-event file, Meridian coordinates.
- **Chapter V intro:** hidden underground complex, four industrial systems converging, central Meridian core.
- **Chapter V outro:** ruined city transforms into a living city, false success readout, timeline fracture, 2041 timestamp, new coordinates.

## 5. Image-generation prompt templates

Use these templates as a base. Replace bracketed fields and retain the style anchors. Each prompt should describe one scene, not a collage.

### Cinematic environment plate
"Wide 16:9 cinematic science-fiction environment concept art for a grounded near-future thriller. [CHAPTER LOCATION AND SCENE]. Believable industrial architecture, physically plausible materials, immense scale, atmospheric haze, carefully controlled practical lighting, charcoal and cold-steel palette with restrained cyan temporal energy and small amber warning lights. Strong depth layers, clear focal point, visually quiet lower 18 percent for subtitles. No characters unless specified. No text, letters, numbers, logos, interface, watermark or signature. High-detail production concept art, realistic matte-painting finish."

### Gameplay background plate *(Superseded 2026-11-09 — see “3D-ready production pipeline” at the end of this guide.)*
"Landscape 16:9 background environment for a 2D physics destruction puzzle. [CHAPTER ENVIRONMENT]. Simplified readable architecture, low-contrast distant scenery, soft atmospheric depth, large open negative space behind the playable structure. Keep foreground gameplay area visually uncluttered. Dark grounded sci-fi industrial art, charcoal/steel palette and restrained chapter accent. No destructible objects, no text, no UI, no logo, no watermark."

### Destructible object sprite *(Superseded 2026-11-09 — see “3D-ready production pipeline” at the end of this guide.)*
"Single isolated [OBJECT] designed as a destructible object in a polished 2D physics puzzle game. Side-on orthographic view, clean silhouette, consistent scale, believable near-future industrial construction, clear material identity, restrained highlights, transparent background, centred with padding. No cast shadow beyond a subtle contact shadow if requested. No text, logo, watermark or extra objects."

### Temporal Charge sprite *(Superseded 2026-11-09 — see “3D-ready production pipeline” at the end of this guide.)*
"Single compact futuristic temporal impact charge, dark engineered metal shell, contained cyan-blue energy core, segmented stabiliser ring, strong circular silhouette, readable at small mobile-game scale, side-on 2D game sprite, transparent background, centred, consistent studio lighting. No text, no logo, no smoke cloud, no watermark."

### Chapter key art
"Premium cinematic key art for [CHAPTER TITLE], grounded science-fiction thriller. Show [CHAPTER'S CENTRAL ENVIRONMENT / THREAT] with a small anonymous human silhouette for scale. Strong focal hierarchy, atmospheric depth, realistic industrial design, restrained cyan temporal energy, chapter-specific accent colour. Leave clean negative space for title typography to be added later. No text or typography generated in image, no logos, no watermark."

## 6. Asset inventory and naming

Suggested directory layout for the coding agent to adapt after inspecting the repository:

```
assets/
  story/
    opening/
      slide_01_ruined_future.webp
      slide_02_the_bargain.webp
      ...
    chapter_01/
      intro/
      outro/
    chapter_02/
      intro/
      outro/
    chapter_03/
      intro/
      outro/
    chapter_04/
      intro/
      outro/
    chapter_05/
      intro/
      finale/
  environments/
    chapter_01_helix/
    chapter_02_vita/
    chapter_03_nova_grid/
    chapter_04_civitas/
    chapter_05_meridian/
  objects/
    temporal_charge/
    helix/
    vita/
    nova_grid/
    civitas/
    meridian/
  audio/
    music/
    narration/
    sfx/
```

Naming rules:
- lowercase snake_case.
- Stable sequence and slide IDs. Never use display titles as save keys.
- Keep source prompt and rights metadata in a manifest.
- Prefer WebP for opaque cinematic stills if quality is adequate; PNG for transparency (decals, VFX, UI). 3D models as glTF 2.0 (`.glb`); see the 3D-ready pipeline section.
- Do not commit source video, enormous uncompressed masters or unused generation variants into the game repository.

## 7. Narration production

Narrator delivery:
- Mature, calm, close-mic documentary tone.
- Moderate pace, roughly 125-145 words per minute.
- Slightly restrained urgency, not theatrical shouting.
- Control voice is more clinical and processed, but words remain intelligible.
- Record/generate each slide or sequence as a separate audio file for timing flexibility.
- Export WAV masters; create compressed Ogg Vorbis or AAC assets for the game after approval.
- Keep subtitle text exactly aligned with the approved narration.
- Music ducking under narration is mandatory in cinematics.

Suggested filenames:
- `opening_slide_01.wav` ... `opening_slide_07.wav`
- `ch01_intro.wav`, `ch01_outro.wav`, etc.
- Keep a JSON/CSV manifest with sequence ID, slide ID, transcript, duration, audio path and image path.

## 8. Music direction and licensing

### Main gameplay music brief
Original instrumental dark sci-fi ambient bed for long puzzle sessions:
- Slow evolving analogue synth drones.
- Restrained pulsing bass and sparse mechanical ticks.
- Distant metallic textures and subtle electrical hum.
- Faint hopeful motif that can surface between tension passages.
- No vocals, lyrics, choir, aggressive drums or sudden trailer hits.
- No large dynamic swings; it must remain comfortable over 10-20 minute sessions.
- 2-4 minutes preferred, with an edit-friendly ending and a tested seamless loop or cross-fade.

### Chapter variations
Use the same harmonic and rhythmic identity, then add a subtle layer:
- Helix: precise electronic pulse.
- VITA: soft glassy tones and organic low textures.
- Nova Grid: industrial low pulse and restrained metallic rhythm.
- Civitas: sterile sustained tones and ticking patterns.
- Meridian: deeper sub-bass and fractured signal textures.

Do not generate five completely unrelated tracks. A shared musical motif makes the world feel coherent.

### Cinematic score
Separate 60-90 second opening cue and shorter chapter transition cues. Use slow tension, controlled low-frequency impact and space for narration. Do not let the score overpower dialogue.

### Free music candidates
These are discovery sources, not selected or integrated tracks. Verify the exact track-level licence and archive a copy of the licence page at download time.

- **Pixabay Music:** <https://pixabay.com/music/>. Pixabay's content licence permits free use and adaptation subject to prohibited uses; check the full licence and track page before shipping. See <https://pixabay.com/service/license-summary/>.
- **Free Music Archive:** <https://freemusicarchive.org/>. Filter for CC0 or CC BY. Avoid NC for a commercial game; avoid ND if editing, looping or adapting. FMA explains that the licence is selected by each rights holder and varies by track: <https://freemusicarchive.org/License_Guide>.
- **Incompetech / Kevin MacLeod:** <https://incompetech.com/music/royalty-free/>. Free Creative Commons option requires attribution; standard licence is available if attribution is not desired. Confirm the chosen track and generated credit: <https://incompetech.com/music/royalty-free/licenses/>.
- **FreeGameMusic / Purrple Cat:** <https://www.freegamemusic.com/>. The site states its tracks are CC BY 4.0 and usable in paid games with credit. The style is often lofi, so it may suit menus or calm interludes better than the main tense gameplay bed.

License rules:
- "Royalty-free" does not automatically mean unrestricted or free.
- Avoid CC BY-NC and CC BY-NC-SA for a commercial game unless separate written commercial permission is obtained.
- Avoid CC BY-ND if the track will be edited, looped, remixed or synchronised in a way the licence disallows.
- For CC BY, preserve exact attribution in an in-game credits screen and a project `THIRD_PARTY_ASSETS.md`.
- Save the original download, source URL, artist, track title, licence version, date accessed and any permission email.
- Check whether the asset may be embedded in a game and distributed as part of the game. Do not redistribute a standalone music pack.

### AI-generated music

**Update 2026-11-09:** The owner placed a candidate at `assets/music/bg.mp3`. Its metadata reads "made with suno" (id `142466df-1693-4ac7-b0ca-3972206ef363`, created 2026-11-09T08:24:39Z), so its provenance differs from the Topview task below. Record which service and plan produced the approved track. For Suno, commercial use depends on the subscription tier active when the track was generated: save that evidence with the asset. Technical check: 198.4 s, −14.8 LUFS, silent head 0.7 s / tail 0.4 s, so trim to a seamless loop or cross-fade in engine, and ship as Ogg Vorbis.
An original instrumental gameplay background track was generated successfully through the connected music-generation service (task ID: `0456971a021d4760a1e4771f3f3901a9`). A temporary download URL was returned. The track is a first-pass candidate, not yet listened to, approved, loop-tested or integrated. Before shipping:
1. Download and listen for loop seams, artefacts, sudden transitions and fatigue.
2. Confirm the generation service's current commercial-use and redistribution terms for the account and generated asset.
3. Save the terms/evidence with the asset.
4. Trim and test a seamless loop or implement a cross-fade in Godot.
5. Keep the source master outside the game until approved.

## 9. Sound effects

Create a restrained consistent set:
- Temporal charge idle hum.
- Aim charge-up / tension tick.
- Launch whoosh.
- Impact crack / temporal ripple.
- Wood, stone and glass destruction layers.
- Facility alarm / relay shutdown.
- Cinematic transition whoosh.
- Time insertion / extraction.
- UI confirm and chapter reveal stinger.

Avoid overloading every collision with a loud sound. Layer by material and use sensible voice/music ducking.

## 10. Reference images currently prepared

The initial concept-art pack contains six environment reference plates:
1. Ruined future city.
2. Helix corporate AI campus.
3. VITA biotech facility.
4. Nova Grid reactor complex.
5. Civitas surveillance / civic control district.
6. Meridian underground convergence facility.

These are art-direction references, not final production sprites or approved in-game backgrounds. The coding agent must not assume that they are already imported into Godot or correctly sized for the current scene.

## 11. Approval checklist before bulk production

- [ ] Final title and logo direction approved.
- [ ] Temporal Charge design approved.
- [ ] One representative 3D environment kit per chapter approved (after the Batch 3 greybox is validated).
- [ ] One modular destructible component kit (concepts, textures, specs) per chapter approved.
- [ ] Opening cinematic storyboard approved.
- [ ] Narrator and Control voice tests approved.
- [ ] Gameplay music master and commercial-use rights approved.
- [ ] Chapter intro/outro scripts locked.
- [ ] Subtitle safe area and skip UI checked on physical Android devices.
- [ ] All source prompts, outputs and licences entered in asset manifest.


---

# Owner-approved visual direction update: angled tactical destruction (2026-11-09)

This update supersedes visual guidance that assumes a slingshot, a single ball-like projectile as the player's only weapon, or generic block towers as the primary target identity.

## 1. Overall gameplay composition

The gameplay identity is an angled 2.5D / three-quarter tactical destruction game. Use a consistent camera angle and readable front/side faces, layered industrial structures, restrained perspective, clear ground plane and depth cues. The first prototype retains 2D physics, so artwork and composition must not imply unsupported depth-axis collision.

The visible operative stands at a clear firing position. Keep the character anonymous, with a concealed face and a distinctive silhouette. The operative should read clearly at phone scale. Chapter-specific suit changes should be subtle and reusable.

## 2. Weapon visual family

The arsenal contains multiple distinct weapon silhouettes and projectile/effect families. The initial prototype needs only:
- Kinetic Accelerator: compact electromagnetic launcher, engineered metal, restrained cyan energy detail, direct kinetic projectile.
- Breach Charge: clearly distinguishable limited-use area-effect weapon/projectile, with readable safety/arming cues and restrained blast visuals.

Later proposed designs include a precision penetrator, Pulse Cannon, Disruptor and Temporal Lance. Do not produce final art for all weapons before their mechanics and visual roles are validated. Each weapon needs a recognizable silhouette and distinct muzzle, projectile, impact and HUD treatment without excessive glow.

The existing Temporal Charge artwork may remain a visual reference for the energy language, but it is no longer the only projectile/weapon identity. Do not assume all weapons share the same physics profile.

## 3. Story-specific target environments

- Helix: AI server halls, data cores, autonomous manufacturing, relay towers and control infrastructure.
- VITA: clean rooms, bioreactors, containment chambers and genetic storage.
- Nova Grid: transformers, power cells, reactor housings, cooling and distribution infrastructure.
- Civitas: surveillance masts, sensor arrays, civic control rooms and automated security systems.
- Meridian: temporal reactors, quantum stabilizers, timeline anchors and convergence machinery.

Objects should have distinct shapes, silhouettes and visual material identities. Build reusable modular object families rather than one-off decorative towers. Keep destructible foreground structures higher contrast than backgrounds.

## 4. Destruction readability

Use restrained material-specific feedback: metal deformation/impact sparks, glass/polymer fracture, electrical discharge, energy containment failure and controlled debris. Avoid effects that hide remaining structural supports, projectile paths or critical objectives. Visual effects must be profiled on mobile devices.

## 5. Multiplayer art is later-phase work

Temporal Frontlines may eventually need a construction grid, component placement/rotation states, defensive modules, institution status, attack report and replay/reconstruction screens. Do not generate or integrate a large Frontlines asset pack before the single-player greybox and component catalogue are validated.

---

# 3D-ready production pipeline (owner-aligned, 2026-11-09)

**Authority:** This section supersedes earlier guidance in this guide that assumes transparent PNG sprites for gameplay objects, side-on 2D object art or 2D gameplay background plates. It matches the planned architecture: **Godot 3D rendering with a tilted three-quarter camera over the existing 2D physics** (Option B; implemented in Batch 3).

## 1. What gets made in 3D vs 2D

| Asset family | Form | Notes |
|---|---|---|
| Buildings and destructible components (racks, columns, decks, cores, cells, masts, walls...) | **3D modular geometry** with textures | Never a PNG sprite per object |
| Environment set (floor, back walls, distant structures) | 3D modular pieces + textured cards for far background | Low contrast behind gameplay |
| Operative and weapons | **Placeholder primitives** for now | No detailed models until the greybox is validated |
| Projectiles and impact/blast VFX | Simple meshes + particle/sprite VFX | 2D VFX textures (flipbooks, glows, sparks) are fine here |
| Material textures, decals, damage variants | **2D generated/painted art** | Tileable texture sets, scorch/crack/impact decals, damage overlays |
| UI, icons, HUD | 2D | |
| Cinematics | **Narrated stills** (2D frames, subtle zoom/parallax, subtitles, music) | Video production is not a dependency |

## 2. Geometry rules (match the physics)

- Each damageable component is one physics rectangle in the 2D plane. Its 3D model is that rectangle extruded in depth: **front face = physics shape**. Visual overhangs may not extend the collision silhouette in the plane.
- **Scale:** 100 physics px = 1 Godot 3D unit (1 m). A 40 × 100 px server rack is 0.4 m × 1.0 m on its front face; depth per component kind (e.g. rack 0.8 m).
- **Pivot** at the geometric centre, so the mesh follows the body's position and rotation directly.
- All gameplay components share one depth band. Do not model or place pieces that look like they sit in front of or behind each other in a way the 2D simulation cannot represent.
- Modular kit, not unique buildings: a small set of reusable pieces per chapter (column, beam/deck, panel/wall, rack/cabinet, core/housing, cell/canister, mast/dish) recombined by level data.
- **Formats and budgets (initial, revisit after renderer evaluation):** glTF 2.0 (`.glb`); ~200-1,500 triangles per component, ≤ 3,000 for hero pieces such as the AI core; one material per component where practical; textures 512² (standard) to 1024² (hero), mobile-compressed on import (ETC2/ASTC).
- **Damage states:** intact → damaged → critical → destroyed are shown first with material/decal swaps, emissive changes and VFX; pre-fractured mesh variants only where gameplay benefits and performance allows.
- Lighting: real-time directional light + simple shadows tuned for mobile; no dependency on baked lightmaps for gameplay pieces.

## 3. 2D art inside the 3D pipeline

- **Material texture sets** (tileable, flat-lit, no perspective, no baked shadows): albedo, normal, roughness/metallic (or ORM). One set per gameplay material category (lightweight alloy, reinforced steel, composite, glass/polymer, concrete, electronic module, energy component) plus chapter variants via tint/trim.
- **Decals:** scorch marks, impact cracks, warning stripes, panel seams, chapter insignia without real-world logos.
- **Damage variations:** crack/char overlays per material at damaged and critical levels.
- **VFX textures:** sparks, debris chips, blast flash, electrical arcs, temporal-energy accents (restrained; no excessive glow).
- **UI and cinematic stills** as before (16:9 frames, clean plates, subtitles added in Godot).

## 4. First asset milestone (before and during Batch 3)

Deliverables are **concepts, references, textures and specifications**, not finished models:
1. Helix component concept sheet: orthographic front/side views of each Helix kit piece (column, deck, server rack, AI core, power cell, blast wall, relay mast/dish), with dimensions taken from `data/missions/helix_01.json`.
2. Material reference boards for the seven gameplay materials (what each reads as in-game, and how damage looks).
3. Tileable texture sets for those seven materials (mobile resolutions).
4. Decal and damage-overlay set for Helix.
5. A written spec per kit piece: dimensions, depth, pivot, triangle budget, material, damage-state treatment.
6. Operative silhouette concept (anonymous, readable at phone scale) for later modelling; **the prototype uses a placeholder**.

**Gate:** No bulk model or texture production for other chapters until the coding agent's Batch 3 greybox has been played and visually validated (camera angle, readability at phone size, depth honesty, performance).

## 5. Prompt templates for the 3D pipeline

### Component concept sheet
"Orthographic concept sheet of a [COMPONENT] for a grounded near-future [CHAPTER INSTITUTION] facility. Front view and side view on a neutral grey background, consistent scale, believable industrial construction, clear material identity ([MATERIAL]), simple readable silhouette suitable for a low-poly mobile 3D game, restrained cyan accent lights only where functional. No perspective, no dramatic lighting, no text, labels, logos or watermark."

### Tileable material texture
"Seamless tileable texture of [MATERIAL DESCRIPTION] for a mobile 3D game, viewed perfectly flat and head-on, even diffuse lighting, no shadows, no perspective, no vignette, subtle wear appropriate to a near-future industrial facility, no text or logos."

### Damage decal / overlay
"[DAMAGE TYPE: impact crack / scorch mark / torn metal edge] decal on a transparent background, flat head-on view, even lighting, designed to overlay [MATERIAL] surfaces in a mobile 3D game, restrained and readable, no text or logos."

Transparent PNG output is appropriate for **decals, VFX and UI only**, not for gameplay objects.
