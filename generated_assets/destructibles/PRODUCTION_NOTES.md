# Destructibles: production notes (3d-kits stream)

Scripted Blender kits for the MissionView components: the shared structural, electronic and energy kit plus one component set per chapter, each with four damage states. Every file is built from source in `source/blender/`; nothing is hand-edited.

## What is here

- `<chapter>/<ch>_cmp_<kind>_<var>.glb`: one component. Root node named after the file stem, child nodes `mesh_intact`, `mesh_light` (DAMAGED), `mesh_heavy` (CRITICAL), marker empties `fx_spark_NN`, `fx_smoke_NN` and, on some pieces, `fx_glow_NN`.
- `<chapter>/<ch>_deb_<kind>_<var>.glb`: the destroyed state. Nodes `husk` and `frag_01..`, each with its origin at its own centre, laid out in intact positions around the component centre. Total tris are at most 1.5 times the intact mesh.
- `previews/<ch>_components_sheet.webp`: intact, light, heavy and destroyed for every component, rendered in Cycles at the game camera angle.

## Conventions (ASSET_CONTRACT v1.5)

- 100 px = 1 m. The pivot is the centre of the collision rectangle, z = 0, front +Z. The front silhouette fits `reference_size_px`; depth is centred and at most the kind depth. A small auto-fit scale is applied at build time and logged as `FIT`.
- Budgets: intact at most 1,500 tris (critical cores 3,000). State meshes may be about 10% over intact. The build prints `BUDGET_WARNING` if a mesh goes over.
- **Materials.** Colour lives in the material (`baseColorFactor`); there is no `COLOR_0` (contract section 7, v1.4).
  - `mat_<material>_<ch>` is the main physics-material surface. `mat_<material>_<ch>_<zone>` (for example `_frame`, `_light`, `_accent`) are other finishes of the same physics material, so bind the same material set and damage overlay by prefix.
  - `trim_<zone>_<ch>` covers paint, dark plates, internals, cables, rubber, hazard paint and `trim_burnt_<ch>` (heat-darkened metal on damaged parts).
  - `emit_<colour>_<ch>` and `glass_<name>_<ch>` are as named.
  - Critical cores of HLX, VTA and CVT use `mat_ai_core_module_<ch>` (v1.5). NVG and MRD cores stay `energy_component`, as in the contract table.
- **UVs.** UV0 is a world-scale box projection, 1 UV unit = 1 m, so tileable sets and 1 tile/m overlays line up.
- **Emission.** Strength is 1.0 and the colours are the chapter palette, so lights read without glow. Red `#ff3b4e` is used on critical cores, plus sparingly for Civitas security pips and the Civitas heavy-state alarm.
- **Damage progression.**
  - Light: dents, chipped covers, a cracked pane, one flickering light.
  - Heavy: torn covers, a jagged bite out of the frame, shattered glass, exposed internals, and compute light switched to the warning colour or off.
  - Destroyed: a jagged boolean break, a slumped husk, and crumpled covers and chunks as fragments.
- glTF has no hidden flag, so `mesh_intact`, `mesh_light` and `mesh_heavy` all import visible. Show one at a time (contract section 8).
- When loaded at runtime with `GLTFDocument`, the root comes back as `<stem>2` because of a name clash with the scene root. The glTF itself has one root named after the stem.

## Ambient occlusion

The earlier builds carried paint zones multiplied by baked AO in `COLOR_0`. Contract v1.4 moves colour into the material, so the AO bake is no longer exported.

An AO texture on a second UV set was tested. Godot 4.7.2 imports `occlusionTexture` but does not set `ao_on_uv2`, so it would sample the box UVs. It was therefore not shipped. Depth is carried by bevels, panel gaps and the dark trim zones. If the loader ever sets `ao_on_uv2`, an AO atlas can be added without changing anything else.

## Commands

Build a kit (Blender 5.2.3; one Blender job at a time on this box):

    cd generated_assets/destructibles/source/blender
    TFJ_SAMPLES=32 blender -b --factory-startup --python runkit.py -- kits.<helix|vita|nova_grid|civitas|meridian|shared> [ID filters] [--no-render]
    python3 sheets.py ../../previews/<ch>_components_sheet.webp "<CH>-CMP-*" "<title>"
    python3 mkfrag.py [chapters or category:chapter ...]   # writes manifest_parts/3d-kits.json

Godot check (4.7.2, GL Compatibility, runtime glTF load, MissionView camera, sun and environment):

    xvfb-run -a -s "-screen 0 1280x720x24" godot --path <any project> --rendering-driver opengl3 \
      --script generated_assets/destructibles/source/godot/kit_lineup.gd -- out.png lineup <glb files...>
    ... kit_lineup.gd -- out.png states <component.glb> <debris.glb>

`kit_lineup.gd` prints one `CHECK OK` line per file, listing nodes, surfaces, materials, `colour0` and the marker count.

## Source files

- `tfjkit.py`: palettes, material slots, the zone-to-slot step (`materialise`), primitives and export.
- `tfjpipe.py`: packing, decimation, deformation, booleans and glass shards.
- `tfjdamage.py`: the light, heavy and destroyed states.
- `tfjbuild.py`: the per-component pipeline and the preview tiles.
- `tfjrender.py`: the Cycles preview camera and light, matched to MissionView.
- `kits/*.py`: the per-chapter builders.

## Rights

This is original procedural work. The scripted Blender code was written by the 3d-kits asset agent (AI-assisted authorship). No third-party meshes, textures or concept pixels are used. Form language follows the project concept frames. Ownership is not legally settled for AI-assisted work, and nothing is marked commercially cleared.

## Premium uplift pass, batch 1: Helix (2026-11-10)

Revision of the 22 Helix components and their debris sets in place. File names and manifest ids are unchanged.

- **Materials.** Every zone slot is now textured from the surfaces stream library (`generated_assets/materials/helix/` and `materials/shared/`). The glb files reference the PNGs by relative URI and do not embed them. Godot resolves the URIs to the `res://` library textures on editor import and through runtime GLTFDocument (both tested on the box). `baseColorFactor` is a palette tint over the library albedo, `metallicFactor` is set per zone, and emission textures are masks.
- **Vertex colour.** COLOR_0 now carries baked ambient occlusion only (valid since contract v1.7).
- **New slots.** `trim_edge_hlx` is a worn edge highlight on the bevel faces. `trim_module_hlx` maps one rack unit of the electronic_module set per blade (fitted UVs), with status lights in its emission mask.
- **Geometry.** Racks, columns, decks, shields, power cell, blast walls, mast, pod, gantry, cooling stack and crate were rebuilt with real secondary detail: chamfered corner posts with amber caps, panel seams, bolts, louvres, cable looms, status LEDs, top hatches and small screens. Every piece stays within budget (standard 1,500 tris; the AI core is critical at 3,000).
- **Sizes.** Contract v1.9 makes 40 x 100 the shipped Helix rack size: that is `HLX-CMP-SERVER_RACK-B`. `-A` (40 x 40) stays as the probe size and `-C` (50 x 160) as the tall variant.
- **Emission.** Per v1.9, loader-built materials should keep emission enabled on every surface (black when unlit) and change state by value.
- **Checks.**
  - Godot 4.7.2 GL Compatibility lineup: 44 of 44 files load, with COLOR_0 present.
  - Validator: PASS.
  - Previews: `previews/hlx_components_sheet.webp` (Cycles) and `environments/previews/hlx_showcase_*.webp` (Godot).

## Premium uplift, VITA batch (2026-11-10)

- VITA components (17) rebuilt with the premium pass: textured zone slots from the surfaces library (relative URIs), COLOR_0 AO, `trim_edge_vta` and `trim_module_vta` slots with fit UVs, and secondary detail from `kits/vita.py` (premium block: column caps and seams, deck edge trims, cleanroom panel frames and status LEDs, specimen rack bays, reactor and cryo bands, gene vault core cap and pips). VITA keeps the clean white lab look: no bolts on floors, soft white edges.
- Tris: 256 to 2,104 intact (the gene vault core is critical, under 3,000). Debris sets stay within 1.5x. IDs unchanged.
- Godot 4.7.2 `kit_lineup.gd`: 34/34 component and debris files load, COLOR_0 present on all 34.
- Previews (after): `previews/vta_components_sheet.webp` (Cycles). Before: the same path at commit `9091af3`.

## Premium uplift, Nova Grid batch (2026-11-10)

- Nova Grid components (13) rebuilt with the premium pass: textured zone slots from the surfaces library (relative URIs), COLOR_0 AO, `trim_edge_nvg` and `trim_module_nvg` slots with fit UVs, and heavy-industrial secondary detail from the new premium block in `kits/nova_grid.py`: flange bolts and a cable run on the pylons, a cable loom along the bridge tops, bolts and amber status pips on the transformers, roof louvres on the cooling towers, ring bolts, capacitor top hatches and pips, wall hatches and looms, and base bolts on the reactor core.
- The cable bridge loom first hung below the collision rectangle (validator: origin not centred); it now runs along the top and both bridges pass.
- Tris: 532 to 1,612 intact (reactor core critical, under 3,000). Debris within 1.5x. IDs unchanged.
- Godot `kit_lineup.gd`: 26/26 component and debris files load, COLOR_0 on all 26.
- Previews (after): `previews/nvg_components_sheet.webp` (Cycles). Before: the same path at commit `023939a`.

## Premium uplift, Civitas batch (2026-11-10)

- Civitas components (16) rebuilt with the premium pass: textured zone slots from the surfaces library (relative URIs), COLOR_0 AO, `trim_edge_cvt` and `trim_module_cvt` slots with fit UVs, and civic secondary detail from the premium block in `kits/civitas.py`: column capitals, seams and bolts, relay bridge deck trims and LEDs, sensor mast collars and pips, array frames, civic screen bezels, data exchange rack bays and status lights, security wall panels, and the surveillance core's ring and eye detail.
- Tris: 320 to 1,592 intact (surveillance core critical, under 3,000). Debris within 1.5x. IDs unchanged.
- Godot `kit_lineup.gd`: 32/32 component and debris files load, COLOR_0 on all 32.
- Previews (after): `previews/cvt_components_sheet.webp` (Cycles). Before: the same path at commit `0b4feb7`.

## Premium uplift, Meridian batch (2026-11-10)

- Meridian components (12) rebuilt with the premium pass: textured zone slots from the surfaces library (relative URIs), COLOR_0 AO, `trim_edge_mrd` and `trim_module_mrd` slots with fit UVs, and secondary detail from the premium block in `kits/meridian.py`: temporal glyph inlays, anchor column collars, convergence deck edge rings, phase shield frames, stabilizer rings, temporal cell bands, monolith slab seams, timeline relay pips and the convergence core cage.
- The quantum stabilizer first came out at 1,568 tris (over the 1,500 standard budget); a cable loom was removed and it is now 1,432.
- Tris: 208 to 1,972 intact (convergence core critical, under 3,000). Debris within 1.5x. IDs unchanged.
- Godot `kit_lineup.gd`: 24/24 component and debris files load, COLOR_0 on all 24.
- Previews (after): `previews/mrd_components_sheet.webp` (Cycles). Before: the same path at commit `6864c26`.

## Shared kit re-render (premium pass, 2026-11-10)
- All 94 SHR files rebuilt with the current pipeline (library textures, COLOR_0 AO no longer scaled by the layer value). IDs unchanged.
- SHR-CMP-ENERGY_CELL-B reuses the Helix power cell, which gained secondary detail in the uplift and reached 1,544 intact tris. The tall shared variant now drops the cable loom (1,384 intact tris, inside the 1,500 component budget). Variant A keeps the loom.
- Verification: Godot 4.7.2 lineup of destructibles/shared, 94 of 94 load, COLOR_0 present on all 94. Sheet: destructibles/previews/shr_components_sheet.webp.
