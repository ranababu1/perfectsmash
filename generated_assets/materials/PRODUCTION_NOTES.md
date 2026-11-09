# Materials: production notes (surfaces stream)

Status: all files `pending_review`. Nothing here is wired into the game; the coding agent binds these after owner approval.

## What is here

| Folder | Contents |
|---|---|
| `helix/`, `vita/`, `nova_grid/`, `civitas/`, `meridian/` | 8 tileable PBR sets per chapter at 512 x 512: the seven physics materials (`lightweight_alloy`, `reinforced_steel`, `composite`, `glass_polymer`, `concrete`, `electronic_module`, `energy_component`) plus a `FLOOR` set. Ids `<CH>-MAT-<MATERIAL_ID>-A`. |
| `shared/` | 13 shared sets (`SHR-MAT-*-A`, 1024 hero and tileable, 512 for small-detail sets), 12 decals (`SHR-DCL-*`), 14 damage overlays (`SHR-DMG-<MATERIAL_ID>-LIGHT` and `-HEAVY`), trim sheet and emissive strip sheet with UV guides. |
| `previews/tiles/` | One 3x3 tiling check per set (left half albedo, right half lit preview). |
| `previews/contact_*.webp` | Contact sheets per chapter, shared sets, decals and damage overlays. |
| `source_log.tsv` | Every generated source image used, unused or rejected, with its file name. |

Files per set: `_albedo.png` (sRGB; RGBA where the set is transparent), `_normal.png` (OpenGL +Y, the glTF and Godot convention), `_orm.png` (R occlusion, G roughness, B metallic), `_emission.png` where the set has lights. Import normal and ORM maps as linear (Godot: normal map import hint for `_normal`, and turn sRGB off for `_orm`).

## Scale and use

- Tile size is in each manifest entry `notes` and `purpose` (1 m per tile unless stated; concrete, floor and cladding sets are 2 m per tile; energy housings 0.5 m). Chapter sets reach 256-512 px/m, inside the contract range.
- AO is baked into the ORM red channel because the Compatibility renderer has no SSAO. It is deliberately subtle (cavities and grooves only), so it can sit under real shadows without doubling up.
- Glass sets (`*-GLASS_POLYMER-A`, `SHR-MAT-GLASS-A`, `SHR-MAT-FROSTED_POLYMER-A`) carry opacity in albedo alpha. Use `transparency = ALPHA` and keep roughness from the ORM.
- `ELECTRONIC_MODULE` sets are cut from rack images at unit gaps, so they tile vertically along a rack; their status lights are in `_emission`. Directional sets (rain streaks, soot runs, enamel drips) say "keep V up" in `notes`.
- Emission is restrained: chapter accents only (Helix cyan, VITA pale green, Nova Grid amber and electric blue, Civitas cold blue with single red security points, Meridian violet and cyan). Orange and amber appear only on energy components (danger) and the hazard strip. All emission reads without glow.

## Decals (`SHR-DCL-*`, straight alpha)

Scorch (radial 1024 and directional 512), soot plume, two crack decals with normals, glass fracture, kinetic impact on metal (with normal and ORM: bare steel is metallic), kinetic impact on concrete (with normal), spark burn (with an emission rim to fade over about 1.5 s), two procedural dents (normal-led, faint occlusion albedo) and a tileable scratch mask (`SHR-DCL-SCRATCHES-01`, 1024, 1 tile per metre). Use Godot `Decal` nodes or a `next_pass` quad.

## Damage overlays (`SHR-DMG-*`)

512 x 512 RGBA, tileable, one LIGHT and one HEAVY per physics material, shared by all chapters (tint through the overlay material albedo colour). Apply as ASSET_CONTRACT section 8: `material.next_pass` = transparent StandardMaterial3D, `uv1_triplanar = true`, `uv1_world_triplanar = false`, 1 tile per metre.

- LIGHT: scuffs and scratches, chipped paint flecks, small dents, hairline cracks on concrete and composite, a small chip fracture on glass, a small spark pit on electronics and energy.
- HEAVY: broad soft scorch, deep scratches, kinetic impacts (steel 3, alloy 2, others 1), dents, deep cracks and impact craters on concrete, large fractures on glass, spark burns and soot on electronics and energy.
- Built by wrap-stamping the decals (every stamp is placed in all nine neighbouring tiles, so the result is exactly periodic) over periodic noise. Alpha coverage is listed per entry in `notes`. The contact sheets show them over Helix, Civitas and Meridian sets.

## Trim and emissive strips

- `SHR-MAT-TRIM_SHEET-A` (1024): 11 horizontal strips that tile in U: bolted steel band, rubber gasket, vent louvres, restrained worn hazard stripes, perforated panel, conduit pipe, painted panel seams, brushed edge, tread strip, recessed light channel (neutral white emission to tint per chapter) and a painted rail with edge wear. V ranges in `shared/shr_mat_trim_sheet_a_uv_guide.json` (top-left UV origin, as glTF and Godot use).
- `SHR-MAT-EMISSIVE_STRIPS-A` (1024): eight light-strip rows in the chapter palette colours (odd rows segmented). V ranges in `shared/shr_mat_emissive_strips_a_uv_guide.json`.

## How it was made

1. Source photos-style textures were generated with the GenerateImage tool (every one in `source_log.tsv`; rejected ones are marked, for example a gunmetal that read as fabric and a composite with a visible seam).
2. Seamless conversion: low-frequency flattening, then two-band self-overlap quilting in both axes (minimum-error cut on the detail band, cosine cross-fade on the low band). Upscaling where needed with Real-ESRGAN (`realesr-general-x4v3`, ONNX, BSD-3 licence) on a wrap-padded image so the seam stays clean.
3. Periodic patterns (carbon twill, diamond tread, tie holes, cable bundles, panel grids, bolts, vents, inlays) are procedural and exactly periodic, because generated sources could not tile them cleanly.
4. Height is derived from albedo with a multi-scale band-pass; normals are calibrated to a target mean tilt per set (satin metals about 1 degree, plate and tread up to 9 degrees); AO from height.
5. Checks: a seam-crossing 2x2 crop of every set was inspected at full size (albedo and lit), plus the 3x3 previews. Weak sets were rebuilt: Helix, VITA and Civitas alloys (too saturated, cast-looking normals: now satin), VITA composite and floor (blotchy normals: now micro detail only), VITA bio-glass (green toned down), Nova Grid heat alloy (added brushed grain), Nova Grid composite (weave was blocky), Nova Grid and Civitas concrete streaks (read as dashes), Meridian glass (iridescence was blotchy), damage overlay scorch (star-shaped stamps replaced with soft procedural scorch).

## Validation

- `python3 generated_assets/tools/validate_asset_manifest.py` on the fragment: PASS (structure, ids, paths and deep image checks).
- Godot import check: see the stream report; not claimed here unless the report gives the command and output.

## Rights

Generated sources: AI-generated (GenerateImage tool), rights not verified, not commercially cleared. Procedural sets: original procedural work by the asset agent (AI-assisted authorship), ownership not legally settled, not marked commercially cleared. Real-ESRGAN models: BSD-3-Clause (xinntao/Real-ESRGAN), ONNX conversions from huggingface.co/jonathanst29/tinier-upscale-models.

## Known limits and what remains

- One variant (`-A`) per chapter material; a `-B` variant per heavy-use material (floor, reinforced steel) would reduce repetition on wide levels.
- Electronic module sets repeat their unit every metre vertically; on very tall racks mix with the trim sheet.
- Height maps (useful for parallax or Blender displacement) are kept outside the repo to save space; ask if needed.
