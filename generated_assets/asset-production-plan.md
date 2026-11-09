# Temporal: First Jump - Asset production plan

**Role:** Art / asset lead (images, modular meshes + textures, VFX, UI, cinematics stills; audio via external services).  
**Repository:** `ranababu1/temporal-chapter1`  
**Branch for this work:** `assets`  
**Staging root:** `generated_assets/`  
**Date:** 2026-11-09 (Asia/Calcutta); full-scale production section added 2026-11-10  
**Brief:** Master Art, Animation, Video and Audio Production Brief §26 first response.  
**Rendering decision (owner):** Option B - Godot 3D rendering with a tilted three-quarter camera over retained Godot 2D physics. No 3D physics.

## Full-scale production (owner authorised 2026-11-09, supersedes the Helix-only gate)

The owner authorised production of the complete library for all five chapters and 100 levels across every workstream in parallel, with these standing rules: quality over speed, `main` untouched, all work on `assets`, AI output never marked commercially cleared, the existing music file preserved with rights unverified, and no change to the 2.5D presentation over 2D physics. The "no bulk production before greybox validation" gate in sections 4, 15 and the Helix milestone below is superseded: the Batch 3 greybox now exists on `main` (merged into `assets` at `84a34fd`), and the asset contract is derived from it.

### Streams

| Stream | Owns (under `generated_assets/`) | Manifest fragment |
|---|---|---|
| integration | `asset_manifest.json`, `tools/`, `docs/` (contract, coverage matrix, previews), this plan, `docs/changelog.md` and `docs/currentstate.md` on `assets` | merges all fragments |
| 3d-kits | destructible component kits and debris for five chapters, environment kits, props and landmarks, operative and weapons | `manifest_parts/3d-kits.json` |
| surfaces | material texture sets, damage overlays, decals | `manifest_parts/surfaces.json` |
| ui-vfx | VFX sprite sheets, HUD, menus, progression and mission screens, icons, logo, app icon, splash, fonts, cinematic stills | `manifest_parts/ui-vfx.json` |
| audio | soundtrack (chapter, menu, gameplay, combat, boss, transitions, ending), SFX, ambience | `manifest_parts/audio.json` |

### Shared contract and validation

- Contract: `docs/ASSET_CONTRACT.md` (v1.1). Units, axes, pivots, depth band, kind catalogue for all chapters, naming, materials, damage states, camera and light, texture, VFX, UI, audio and loading rules, and the ids the coverage matrix resolves.
- Tools: Godot 4.7.2 stable and Blender 5.2.3 LTS in `/opt/tfj-tools` on the asset box (official builds, checksums verified).
- Validation per batch: `tools/validate_asset_manifest.py --merge` (structure and deep file checks), `tools/godot/run_import_check.sh` (Godot import and load of every asset), `tools/godot/render_previews.sh` (game-camera previews into `docs/previews/`), `tools/build_coverage_matrix.py` (100-level matrix).

### Coverage targets

The coverage matrix (`docs/coverage_matrix.md`) lists for each level its environment kit, background layer, structural components (from the level's layout archetypes), critical asset and debris, material sets and damage overlays, VFX, music, ambience, cinematics and its band landmark. Variety comes from 23 layout archetypes across the campaign, one landmark per band of five levels (20 landmarks), four far-background variants per chapter and a rotating dressing-prop pool.

### Production log

| Date | Batch | Result |
|---|---|---|
| 2026-11-10 | Integration set-up | `main` merged into `assets` (`84a34fd`); contract v1 (`8eaebdf`), validator v2 (`c089817`), Godot harness (`9ce5a6b`), coverage matrix (`f264d81`). Coverage before stream deliveries: 0 / 100 levels |
| 2026-11-10 | Integration pass 1 | ui-vfx merged (263 entries); Godot load 279 / 279; contract v1.3 (`be7a157`) |
| 2026-11-10 | Integration pass 2 | surfaces batch 1 merged (273 entries); Godot import and load 550 / 550; contract v1.4; textured greybox and material-board previews in `docs/previews/harness_*`; coverage 1074 / 3176 requirement slots, 0 / 100 levels complete (`ecddb76`) |
| 2026-11-10 | Integration pass 3 | audio batch 1 merged (190 entries); Godot load 740 / 740; loudness measured (ambience about -24 LUFS, SFX peaks at most -1.1 dBTP); coverage 1174 / 3176, game-wide 26 / 36, 0 / 100 levels complete (`77b86ae`) |
| 2026-11-10 | Integration pass 4 | VFX library merged (51 entries, 11 particle presets); Godot load 802 / 802; coverage 2014 / 3176, game-wide 27 / 36, 0 / 100 levels complete (`9776f35`) |
| 2026-11-10 | Main sync | `main` `abf69fc` merged (`41eec2e`, `462f4ae`, `425dd6a`); contract v1.5 (`ai_core_module`, new `helix_01` sizes); coverage 1903 / 3236, 0 / 100 levels complete |
| 2026-11-10 | Main sync | `main` `fa9da67` merged (`be095a8`); audio hook map added (13 code sound ids: 12 delivered, 1 stand-in; music cues `menu`, `cinematic` missing); contract v1.6 |
| 2026-11-10 | Integration pass 5 | audio batches 2 and 3 (55 music cues) and surfaces batch 2 merged; Godot load 857 / 857; music -16.1 LUFS median; coverage 2009 / 3236, game-wide 29 / 36, 0 / 100 levels complete |
| 2026-11-10 | Integration pass 6 | surfaces batch 3 (backgrounds for Helix, VITA, Nova Grid) merged; Godot load 923 / 923; contract v1.7; coverage 2109 / 3236, game-wide 29 / 36, 0 / 100 levels complete |

## Review status (2026-11-09)

- Staging structure: approved by reviewer.
- Visual direction (SV-01 to SV-07): pending owner review. These are concepts and references, not production meshes, textures or animations.
- Production meshes and textures: none yet; all remain in `planned[]` until the Batch 3 Helix greybox is validated.
- Gameplay music (`gameplay_bed.ogg`): preserved, rights unverified, not commercially cleared.
- Merge: do not merge `assets` yet. It is behind `main`; reconcile with the latest mainline before integration.

This first-response plan (below) did not start bulk production; see the full-scale section above for the current state. It records understanding, audit findings, Helix prototype scope, coding-agent dependencies and open owner decisions. Proposed notes for `docs/changelog.md` and `docs/currentstate.md` are at the end so mainline docs stay untouched until the owner merges.

---

## 1. Understanding of the approved visual identity

Temporal: First Jump is a tactical, story-driven destruction game. The player is an anonymous operative sent back through time to dismantle institutions that led to humanity's extinction. It is not an Angry Birds clone, slingshot puzzle, medieval fantasy or conventional military shooter.

Locked look:

- Angled three-quarter / 2.5D presentation (3D meshes + lighting) with gameplay collision on a single 2D physics plane.
- Premium dystopian science fiction: cinematic industrial architecture, strong silhouettes, sophisticated but readable detail on mobile.
- Palette base: charcoal, graphite, gunmetal, cool steel, deep blue-grey.
- Accents: cyan/blue for computing and controlled tech; orange/amber reserved for weapon energy and danger; green for biotech; violet sparingly for temporal phenomena.
- Visible anonymous operative (hooded / face obscured, no fixed gender).
- Five chapter identities (Helix, VITA, Nova Grid, Civitas, Meridian) that share one language but read as different institutions.
- Critical targets (especially the Helix AI core) must remain obvious at phone scale.

Owner reference pack (external, unverified AI provenance) reinforces the hooded operative, charcoal/orange language, intact-to-destroyed component rows and chapter moodboards. Adjustments applied in this plan: Kinetic Accelerator pushed toward a distinctive electromagnetic precision design (pack currently reads too much like a conventional assault rifle); orange glow dialled back so it is not on every surface; Breach Charge treated as a launcher that fires lobbed canisters to match `data/weapons.json`.

---

## 2. Repository asset audit

Inspected on `main` at `19b0de2` (work committed on the existing `assets` branch).

| Area | Finding |
|---|---|
| Shipped art | `assets/icon/*` only - Perfect Smash era vectors/PNGs; marked for replacement |
| Shipped audio | `assets/audio/music/gameplay_bed.ogg` - owner-supplied Suno track, integrated on instruction; **rights unverified** (release blocker) |
| Gitignored masters | `assets/music/` (owner masters; do not commit) |
| Mission data | `data/missions/helix_01.json` - Relay Node greybox layout, 8 component kinds, AURA core critical |
| Materials / weapons | `data/materials.json` (7), `data/weapons.json` (Kinetic Accelerator direct, Breach Charge lobbed) |
| Docs | Production guide includes a “3D-ready production pipeline” section aligned with Option B; sprite templates marked superseded |
| Batches | Batch 1 (materials/damage/structure) and Batch 2 (mission engine) implemented; **Batch 3 Helix playable greybox not built yet** |
| Engine on this box | Godot binary not available in the asset agent environment; Blender package not installed (may be installable later for scripted primitives) |
| Tests | Not run here (no Godot). Do not claim test status from this branch |

No gameplay meshes, textures, VFX packs, UI kit, cinematic stills library or SFX library exist in-repo yet.

---

## 3. Existing assets that can be reused

- App icon set under `assets/icon/` as temporary store/launcher art until Temporal branding replaces it.
- `gameplay_bed.ogg` as the current music bed (do not replace or delete; licence evidence still required).
- Chapter theme colour keys already used by `ChapterTheme` / scenery code - keep new art compatible with those palettes.
- Mission component `kind` list and dimensions in `helix_01.json` - authoritative for Helix mesh front-face sizes.
- Narrative and cinematic shot lists in `docs/visual-audio-production-guide.md` and `data/cinematics.json` structure.
- Owner reference pack (external) as art-direction only.

---

## 4. Missing asset categories

Relative to brief deliverables and Helix needs:

1. Art bible / styleframes as approved production docs (this plan + later bible pass).
2. Modular 3D component kit for Helix kinds (meshes).
3. Material texture sets and damage decals for seven materials.
4. Operative placeholder mesh and later character pack.
5. Weapon placeholder meshes and projectile/VFX art (Kinetic + Breach).
6. Helix environment / backdrop kit.
7. Destruction and weapon VFX textures.
8. HUD / icon library and Temporal logo / app icon replacement.
9. Cinematic stills (~40-50 campaign; none produced).
10. Music with verified commercial rights; SFX; VO.
11. Fonts with redistributable licences.
12. Machine-readable manifest with path existence checks (added here under `generated_assets/`).

---

## 5. Proposed Asset Bible structure

To be written as `generated_assets/docs/art-bible.md` after style validation (not in this first commit):

1. Overall art direction  
2. Visual references and style rules  
3. Colour palettes (master + five chapters)  
4. Lighting and atmosphere  
5. Environment design language  
6. Character design (operative)  
7. Weapon design  
8. Destructible component design (mesh kit rules)  
9. Materials and textures  
10. Animation direction  
11. VFX direction  
12. UI design  
13. Cinematic direction (narrated stills first)  
14. Music direction  
15. Sound-effect direction  
16. Technical asset specifications (scale, pivots, budgets)  
17. Naming conventions  
18. Asset inventory (links to `asset_manifest.json`)  
19. Asset dependencies  
20. Production priorities and gates  

---

## 6. Proposed asset folder structure

```
generated_assets/
  characters/
  weapons/
  environments/
  destructibles/
  materials/
  vfx/
  ui/
  cinematics/
  audio/
  fonts/
  tools/
  docs/references/
  asset-production-plan.md
  asset_manifest.json
  README.md

assets/                    # existing shipped paths (do not reorganise from this branch)
  icon/
  audio/music/gameplay_bed.ogg
```

Naming: lowercase `snake_case`. Stable ids separate from display names. Prefer `.glb` for meshes; PNG/WebP for 2D; Ogg for game audio. Source masters and huge variants stay out of git or behind LFS if the owner enables it later.

---

## 7. Visual style recommendations for all five chapters

| Chapter | Institution | Look | Accent |
|---|---|---|---|
| I | Helix Systems (2089) | AI server halls, relays, robotic logistics; cold steel and glass | Cyan/blue compute light; small amber warnings |
| II | VITA Genomics (2092) | Sterile labs, bioreactors, containment | Restrained green biological light; clinical white/cool metal |
| III | Nova Grid (2096) | Heavy power infrastructure, cooling, containment rings | Amber heat, electrical blue |
| IV | Civitas (2100) | Surveillance masts, civic control, prediction rooms | Desaturated city tones, cold monitoring cyan, rare red security |
| V | Meridian (2104) | Monumental temporal machinery, convergence core | Graphite foundations; restrained violet, cyan, white |

Shared rules: no purple/pink cyberpunk gradients, no baked UI text, no real brands, readable silhouettes at phone scale, low-contrast backgrounds behind gameplay pieces.

---

## 8. Character design direction

- Anonymous specialist; hooded or otherwise face-obscured; distinctive silhouette; practical near-future gear.
- Support idle, ready, aim, fire/recoil, reload/cooldown and mission reaction later.
- **Now:** concept refinement + greybox placeholder only. No expensive character modelling until the Helix greybox visual test is approved (owner constraint).

---

## 9. Weapon visual direction

- **Kinetic Accelerator:** compact electromagnetic precision launcher; linear barrel / accelerator language; controlled cyan energy; sharp muzzle and impact. Avoid conventional assault-rifle scope-and-grip clichés from the reference pack.
- **Breach Charge:** clearly different silhouette; launcher that fires lobbed canisters (assumed; matches lobbed delivery in data). Hazard striping, arming cue, radial blast and debris. Pending owner confirmation if throwable-only is preferred instead.
- Orange/amber reserved for energy and danger, not every panel trim.

---

## 10. Destructible component strategy

Mesh kit, not per-level illustrations.

- Each gameplay component = one 2D physics rectangle; 3D mesh extruded so **front face = physics shape**.
- Scale: 100 px = 1 m. Centre pivot. Shared depth band (visual depth only).
- Helix kinds: blast wall, server rack, support column, service deck, AI core, power cell, relay mast, relay dish (~8 types).
- Damage states intact → damaged → critical → destroyed: prefer material/emissive/decal swaps and VFX first; pre-fractured mesh variants only where performance allows.
- Budgets (initial): ~200-1,500 tris per component, ≤ ~3,000 for the AI core; one material where practical; 512²-1024² textures.
- Formats: glTF 2.0 (`.glb`).

---

## 11. Cinematic production strategy

Follow the repo production guide: **narrated stills with subtle parallax/zoom**, about 40-50 stills across opening + chapter intros/outros. Rebuild player from `data/cinematics.json` (coding agent, Phase 4). Short video only as accents. No bulk video dependency.

---

## 12. Music and sound production strategy

Honest capability limits:

- This agent can generate images and video. It has **no native music or voice synthesis**.
- Music / VO require an external service (e.g. Suno, ElevenLabs) under a **commercial-use** plan, with terms saved beside the asset.
- SFX: procedural synthesis and/or CC0 libraries with per-file licence records.
- Leave `gameplay_bed.ogg` in place; collecting Suno plan evidence remains a release blocker.
- Do not add unreviewed music into shipping paths.

---

## 13. Technical formats and specifications

| Family | Form | Notes |
|---|---|---|
| Destructibles, near architecture | `mesh` (.glb) | Front face matches physics rect |
| Operative / weapons (prototype) | `mesh` placeholders | Primitives OK |
| Material maps, decals, damage overlays | 2D textures | Flat-lit, tileable, no baked shadow |
| VFX | `sprite` / particles | Flipbooks, glows, sparks |
| UI / icons | `ui` | No baked dynamic text |
| Cinematics | stills (+ rare `video`) | 16:9, quiet lower band |
| Audio | `audio` | Ogg in-game; masters reviewed first |

Lighting: real-time directional + simple shadows; no baked lightmap dependency for gameplay pieces. Mobile triangle and texture budgets as in the production guide's 3D pipeline section.

**3D authoring on the asset box:** plan to build placeholder/modular meshes as Godot primitives (coding agent) and/or scripted Blender meshes if Blender is installed later. Do not claim production character models.

---

## 14. Estimated inventory (gameplay-driven, not decorative)

**Helix prototype milestone (this phase):**

- 8 destructible component kinds × (1 base mesh + damage treatment)  
- 1 AI core hero treatment  
- 2 weapon placeholders + 2 projectile presentations  
- 1 operative placeholder  
- ~7 material texture sets (shared) + small decal sheet  
- ~8-12 VFX textures (muzzle, impact, blast, sparks, arc, shockwave, debris, smoke)  
- ~6-10 HUD icons  
- Optional: 1 Helix backdrop card set  

**Later (gated):** full chapter kits, ~40-50 cinematic stills, music stems, SFX library, VO, logo/app icon replacement, fonts.

Do not generate 100 unique level illustrations.

---

## 15. Production sequence

1. **This commit:** plan, folder scaffold, manifest schema, validation script, reference notes.  
2. **Style-validation package (small):** Helix component concept sheet (ortho front/side from `helix_01` sizes), material boards, operative silhouette concept, Kinetic + Breach concept revisions (electromagnetic KA; canister launcher BC). Owner review.  
3. **Coding-agent Batch 3 greybox** with placeholders (see §16). Joint visual validation: camera, perspective, depth honesty, lighting, destruction readability, mobile performance.  
4. **Helix prototype art pack** only after greybox approval: textures, decals, refined placeholder or simple meshes, VFX, basic HUD.  
5. Bulk chapter production only after Helix playable review.  
6. Cinematics / audio campaigns in parallel once style is locked and licences are clear.

---

## 16. Dependencies and requests for the coding agent

Please treat these as explicit asks for Batch 3:

1. Build a representative Helix Systems greybox scene from `data/missions/helix_01.json` with 3D presentation over 2D physics.  
2. Tilted three-quarter camera, directional light and simple shadows; confirm readability at phone resolution.  
3. Map each component `kind` to a placeholder mesh (box/cylinder extruded to front-face size and agreed depth).  
4. Wire damage states to material/emissive or mesh-swap hooks the art pack can target.  
5. Operative and both weapons as greybox placeholders at the mission operative position.  
6. Expose import path conventions for `.glb` and textures under or alongside `generated_assets/` (or a future `assets/` subpath you prefer).  
7. Re-run renderer evaluation with 3D content before any Compatibility vs Mobile production switch.  
8. Do not require per-object PNG sprites for gameplay pieces.  
9. Confirm Breach Charge presentation as launcher + lobbed canister (or request throwable-only).  
10. Keep music bed path stable; art agent will not move `gameplay_bed.ogg`.

Art agent will not modify `scripts/` or `scenes/` on this branch.

---

## Helix prototype milestone scope (summary)

Small and representative only:

- ~8 component types listed above + ground static presentation  
- AI core as critical visual anchor  
- Kinetic Accelerator + Breach Charge placeholders and basic VFX  
- Operative placeholder (no final character model)  
- Shared material textures / decals as available  
- Basic HUD icons for weapons and objectives  
- Manifest entries only for files that exist; planned rows stay in `planned`

Gate: no bulk production until Batch 3 greybox is played and visually validated.

---

## Open owner decisions

1. Confirm Breach Charge as **launcher firing lobbed canisters** (assumed) vs throwable canister only.  
2. Provide Suno plan / terms evidence for `gameplay_bed.ogg` (release blocker).  
3. Approve style-validation package before Helix art pack production.  
4. Confirm whether Git LFS should be enabled before large texture/mesh commits.  
5. Confirm merge path: keep production on `assets` until review, then PR into `main`.

---

## Risks

- Greybox not yet built: camera/lighting assumptions may change mesh depth and texture contrast.  
- AI art ownership unsettled: never mark commercially cleared; keep provenance in the manifest.  
- Music/VO blocked on external paid commercial plans.  
- Repo/APK size growth (APK already ~60 MB): watch texture resolution and consider LFS.  
- Reference pack over-uses orange glow and military rifle language; following it literally would hurt mobile readability and brief compliance.  
- No Godot on the asset agent box: cannot run the game test suite or import `.glb` here; validation is path/manifest based until a Godot environment is available.

---

## Proposed changelog entry (for `docs/changelog.md` when merging)

```
## 2026-11-09 - Asset branch: production plan and generated_assets scaffold

- Branch `assets`: added `generated_assets/` with category folders, asset production plan (brief §26, Option B), machine-readable `asset_manifest.json` (existing paths only + planned inventory), and `tools/validate_asset_manifest.py`.
- No gameplay code or shipped `assets/` files changed. Owner reference pack kept external (unverified AI provenance).
- Helix prototype scoped to a small mesh+texture kit gated on Batch 3 greybox validation.
```

## Proposed currentstate note (for `docs/currentstate.md` when merging)

```
## Asset production (branch `assets`, 2026-11-09)

- Staging tree: `generated_assets/` (plan, manifest, category READMEs). See `generated_assets/asset-production-plan.md`.
- Rendering alignment: Option B (3D presentation over 2D physics); first milestone = small Helix prototype after greybox validation.
- Existing shipped assets unchanged: `assets/icon/*`, `assets/audio/music/gameplay_bed.ogg` (rights still unverified).
- Coding agent ask: Batch 3 Helix greybox with placeholder meshes for joint visual sign-off before bulk art.
```
