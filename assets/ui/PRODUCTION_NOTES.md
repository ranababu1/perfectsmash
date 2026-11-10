# UI, branding and typography: production notes (stream ui-vfx)

Branch `assets` only. Everything here is new staging work under `assets/`; nothing is wired
into the game. `assets/icon/*` is untouched. Approval status of every file: `pending_review`.

## What is here

| Folder | Contents | Count |
|---|---|---|
| `branding/logo/` | Symbol mark and three lockups (horizontal, stacked, compact) in colour, light-on-dark, mono light, mono dark and colour-on-light; outlined SVG masters, PNG exports, editable live-text SVG sources | 21 SVG masters, 21 PNG, 3 editable sources |
| `branding/app_icon/` | Android adaptive foreground / background / monochrome at 432, flattened 512 / 256 / 192 / 48, SVG sources | 7 PNG + 5 SVG |
| `branding/splash/` | Boot splash 1280x720 and 2560x1440, transparent logo layer, SVG source | 3 PNG + 2 SVG |
| `branding/chapter_titles/` | Five chapter title treatments: editable SVG with live text, plus text-free decoration layers at 1x/2x for Godot | 5 editable SVG, 5 deco SVG, 10 PNG |
| `icons/` | 87 icons (weapons, upgrades, objectives, economy, state, navigation, settings, HUD, meta / Frontlines, chapter emblems); SVG + 64 px (1x) + 128 px (2x) + 256 px hero for weapons, upgrades and chapter emblems | 87 x (SVG, 1x, 2x) + 23 hero |
| `kit/` | 93 kit components: 9-slice panels (plus chapter-accent variants), chapter cards, primary / secondary / danger / icon buttons in normal, hover, pressed, disabled, focus ring, tabs, slider track / fill / grabbers, toggles, progress tracks and fills (cyan, amber, critical, success, segmented), cooldown ring layers, ammo pips, objective markers, off-screen indicators, critical-asset target marker (layered), aim reticle, trajectory dot, HUD weapon slots, chip, divider, upgrade tier badges | 93 x (SVG, 1x, 2x) |
| `screens/` | 23 mock layouts (WebP 1x and 2x, editable SVG): main menu, chapter select, chapter map x5, mission briefing, gameplay HUD (on the real greybox harness capture and on the SV-04 concept), pause, weapon selection, weapon tech / upgrades, results success and failure, settings, credits, loading; concept layouts for leaderboards, player profile, Temporal Frontlines hub, institution builder and attack report | 23 |
| `backgrounds/` | Main menu and loading / credits backdrops (1280x720 WebP) | 2 |
| `theme/tfj_theme_spec.json` | Godot Theme-ready spec | 1 |
| `previews/` | Contact sheets and key screens for review (WebP) | |
| `_build/` | The generators (Python) that produce all of the above; `build_all.sh` rebuilds everything | |

Fonts are in `assets/fonts/` (see its README): Chakra Petch (display) and Barlow (UI), SIL OFL 1.1, official Google Fonts files with OFL.txt.

## Design language

- **Shape:** chamfered corners (top-left and bottom-right cut at 45 degrees), 1 px hairline borders, a 2 px accent tick on the cut corners. Matches the SV-07 HUD concept and the Chakra Petch letterforms.
- **Colour:** charcoal / graphite surfaces (`#111A22` panels, `#080C10` base). Cyan `#3CC8E6` = interaction and temporal energy. Amber `#F2A23A` only for weapon energy (Breach Charge, cooldown) and danger. Red `#FF4D3D` only for critical assets, failure and alarms. Success `#6EDDA6`, Research Data `#8FE3F5`, stars `#F4C766`. Chapter accents (cyan, green, amber, cold blue, violet) only on chapter-specific frames, maps and titles.
- **Glow:** restrained. Hover = 1.5 px halo line; no bloom, no blurred glows in UI textures. Nothing relies on WorldEnvironment glow.
- **Text:** none baked into any game texture. Screen mock-ups contain placeholder copy (clearly tagged MOCK) and are references only.
- **Readability:** body text 18-20 px minimum at the 1280x720 base (about 32-36 physical px on a 1440p phone); touch targets 64 px (matches `UiKit.BUTTON_HEIGHT`); icons proofed at 32 px (`previews/ui_icons_32px_legibility_proof.webp`) and the app icon at 48 px.

## Logo and symbol mark

"Displacement mark": the diamond marker used throughout the UI is split down its axis; the right half has jumped upward and left a faint cyan afterimage outline where it was; the core is cut with it. It reads as time displacement (the jump), a precise fracture (tactical destruction) and a hidden centre (mystery). No clock imagery. The wordmark carries the same idea: TEMPORAL in Chakra Petch Bold with a single clean horizontal cut, the upper band shifted right, and a thin cyan seam in the cut. FIRST JUMP sits below in tracked Chakra Petch SemiBold between hairline rules.

- Minimum sizes: horizontal lockup 240 px wide, compact 160 px, mark 24 px (use `gam_logo_mark_a_colour_simple` without the echo outline below 64 px).
- Clear space: at least the width of the mark's frame stroke x 2 around any lockup.
- The outlined SVGs are the masters for production; the `logo/source/*_editable.svg` files keep live text (needs Chakra Petch installed) and render identically (`previews/branding_editable_render_check_*.webp`).

## App icon (Android adaptive)

- Foreground / monochrome 432x432 with the mark inside the 66 dp (264 px) safe circle, so circle, squircle and teardrop masks never clip it. Background: graphite gradient with faint diagonal structure lines and a soft cyan centre, rebuilt with float gradients plus 1 LSB dither so it does not band.
- Godot 4.7 Android export preset fields: `launcher_icons/adaptive_foreground_432x432`, `launcher_icons/adaptive_background_432x432`, `launcher_icons/adaptive_monochrome_432x432`, `launcher_icons/main_192x192` -> the files in `branding/app_icon/`. Project `config/icon` candidate: `gam_logo_app_icon_a_256.png`. All of this needs owner approval before it touches `assets/icon/` or `project.godot`.
- Note: ASSET_CONTRACT 14 suggests `assets/ui/app_icon/`; this stream's brief put branding under `ui/branding/`, so the icons are in `ui/branding/app_icon/`.

## Splash and loading

- `branding/splash/gam_ui_splash_a_1280x720.png` (and 2560x1440): full-frame boot splash. Alternatively use `gam_ui_splash_a_logo_transparent_1024w.png` with `application/boot_splash/bg_color = #080C10`, `show_image = true`, `fullsize = false`.
- Loading screen: `backgrounds/ui_bg_loading_1280x720.webp` + `progress_track` / `progress_fill_cyan` + Labels (see `screens/webp_1x/gam_ui_screen_loading_mock.webp`).

## Chapter title treatments

Text stays dynamic. Use `chapter_titles/game/gam_ui_chapter_title_0N_<key>_deco_2x.png` as a full-screen TextureRect (1280x720 base) and place three Labels centred on x 640: `CHAPTER N` (Chakra Petch SemiBold 22, spacing 7, chapter accent) baseline y 364; title (Chakra Petch Bold 62, spacing 5, `#E7EDF2`) baseline y 440; institution and year (Barlow Medium 24, spacing 6, `#97A7B4`) baseline y 530. The editable SVGs show the exact layout with live text layers `txt_chapter_number`, `txt_chapter_title`, `txt_institution_year`.

## Godot integration

- `theme/tfj_theme_spec.json` lists colours, fonts, type roles, spacing, StyleBoxTexture paths with 9-slice margins (1x and 2x), StyleBoxFlat equivalents, per-state font colours, HUD layout anchors (matching the current `MissionHud` placement), damage-number LabelSettings and motion.
- **9-slice and scale:** `StyleBoxTexture` draws its margins at texel size, so a 2x texture with 2x margins draws corners twice as large. Use the 1x textures + 1x margins in StyleBoxes, or (preferred for crisp phones) the `flat_equivalents` StyleBoxFlat values: `corner_radius_top_left` and `corner_radius_bottom_right` = 12 (10 for buttons) with `corner_detail = 1` reproduce the chamfer exactly and stay sharp at any scale. 2x PNGs are for TextureRect / icon use (expand + keep aspect) and for NinePatchRect drawn at half scale.
- Icons: TextureRect, `expand_mode = ignore size`, `stretch_mode = keep aspect centred`, tint with `self_modulate`. Use the 2x (128 px) file; import with mipmaps on and filter linear.
- Cooldown: `TextureProgressBar` with `fill_mode = FILL_CLOCKWISE`, textures `cooldown_ring_under / progress / over`; value = remaining cooldown fraction.
- Critical-asset marker: three layered TextureRects (`critical_marker_ring`, `_brackets`, `_diamond`) in a CanvasLayer at `Camera3D.unproject_position()` of the marker point the code already uses (0.75 m above the core). Ring rotates 30 deg/s, diamond pulses 0.9-1.1 at 1.2 Hz. `critical_marker_all` is a single-texture fallback.
- Damage numbers: Labels with the `damage_numbers.label_settings` from the spec (Chakra Petch Bold, 6 px dark outline), rise 36 px over 0.7 s, pop 1.25 to 1.0, fade the last 0.25 s; preview `previews/ui_damage_number_styles.webp`.
- Weapon art in UI: the weapon icons are silhouettes. When the weapons stream delivers meshes, hero renders of the actual glb models can replace the 256 px icons on the loadout and weapon-tech screens.

## Not validated in Godot yet

PNG/SVG/JSON files were checked with the integration validator (`python3 assets/tools/validate_asset_manifest.py`, PASS) and visually inspected here. They have not been imported into Godot by this stream; the integration stream's `tools/godot/run_import_check.sh` covers that. No Theme `.tres` has been written, because it would need the coding agent's control structure to be useful.

## Rights

- Vector art (logo, icons, kit, layouts, chapter titles, app icon, splash): authored by the asset agent as code (Python generating SVG), AI-assisted authorship. Recorded as original project work; not marked commercially cleared because ownership of AI-assisted output is not legally settled.
- The wordmark is outlined from Chakra Petch Bold (OFL 1.1 permits artwork made with the font).
- Backgrounds: GenerateImage output, graded; rights not verified, not commercially cleared. Prompts below.
- Screen mock-ups embed the SV-04 concept (AI-generated, pending review) or the integration stream's greybox harness capture; they are references, not shipping art.

### Background prompts (GenerateImage, 2026-11-09, 16:9, graded to 1280x720)

The exact prompt strings were not logged at generation time; the text below is a faithful restatement of their content, not a verbatim copy. Raw outputs are kept off-repo in the box masters folder.

- Main menu: "Wide 16:9 cinematic science-fiction environment concept art for a grounded near-future thriller game main menu background. A hidden underground temporal experiment chamber: a colossal circular machine ring of dark graphite steel standing upright on the right two-thirds of the frame, segmented heavy industrial housings, cable bundles, restrained cyan temporal energy contained in a thin luminous seam inside the ring, faint distortion of the air in its centre. A tiny anonymous hooded operative silhouette stands on a metal platform far below the ring, seen from behind, for scale. Charcoal, graphite and cold steel palette, deep blue-grey shadows, very subtle amber warning lights on far walls. Atmospheric haze, volumetric light, strong depth layers. The left third of the image is dark, quiet and low-detail (negative space for menu buttons). Realistic matte-painting finish, premium AAA production concept art. No text, letters, numbers, logos, interface, watermark or signature. No purple or pink."
- Loading: "Wide 16:9 dark cinematic science-fiction loading screen background for a grounded near-future thriller game. Close, low-angle view along a long industrial transit corridor inside a sealed facility, graphite steel wall panels and structural ribs receding to a vanishing point at the centre, a faint cyan temporal distortion ripple hanging in the air at the far end like a heat shimmer, thin cyan light strips along the floor edges, cold steel and charcoal palette, very restrained small amber warning lamps. Heavy atmospheric haze, soft volumetric light, subtle film grain. The lower 25 percent of the frame is dark and calm (space for a loading bar), and the image is low contrast overall so overlaid text remains readable. Realistic matte painting, premium AAA concept art. No people, no text, no letters, numbers, logos, interface, watermark or signature. No purple or pink."

## Rebuild

`assets/ui/_build/build_all.sh` (Python 3 with Pillow, numpy, fontTools; resvg 0.49 from https://github.com/linebender/resvg/releases, path in `RESVG`).
