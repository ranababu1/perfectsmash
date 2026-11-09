# fonts/

Two SIL Open Font License 1.1 families, downloaded from the official Google Fonts repository and
committed with their licence files. They are embedded in the game build as Godot FontFile
resources; do not rely on OS fonts.

| Role | Family | Weights committed | Folder | Licence |
|---|---|---|---|---|
| Display: titles, headings, numerals, logo lettering | Chakra Petch (Cadson Demak) | Regular 400, Medium 500, SemiBold 600, Bold 700 | `chakra_petch/` | `chakra_petch/OFL.txt` (SIL OFL 1.1) |
| UI and body: labels, objectives, long text | Barlow (Jeremy Tribby) | Regular 400, Medium 500, SemiBold 600, Bold 700 | `barlow/` | `barlow/OFL.txt` (SIL OFL 1.1) |

Why these: Chakra Petch has chamfered corners that match the chamfered panel language of the UI kit
and the logo, and its numerals stay legible at HUD sizes. Barlow is a grotesk derived from road and
rail signage: calm, grounded and very readable on phone screens at 18-24 px.

## Sources (accessed 2026-11-09)

- https://github.com/google/fonts/tree/main/ofl/chakrapetch (last upstream commit touching the folder: a4c8c2a0f77efa06765d596d64d077af1d7f0dae)
  - Raw files: https://raw.githubusercontent.com/google/fonts/main/ofl/chakrapetch/ChakraPetch-{Regular,Medium,SemiBold,Bold}.ttf and OFL.txt
  - Upstream project: https://github.com/m4rc1e/Chakra-Petch
- https://github.com/google/fonts/tree/main/ofl/barlow (last upstream commit touching the folder: 6cdf01867df0813c2390f90dff7dc66c87f14cf7)
  - Raw files: https://raw.githubusercontent.com/google/fonts/main/ofl/barlow/Barlow-{Regular,Medium,SemiBold,Bold}.ttf and OFL.txt
  - Upstream project: https://github.com/jpt/barlow

## SHA-256

```
98fcd638baa5c81ff0316b7538ce330ee3b23b1302726de3526d5933a8ecf986  chakra_petch/ChakraPetch-Regular.ttf
d480f4f97405fac3600652e2e14fd0b14339031c0af4da11582994878f04d919  chakra_petch/ChakraPetch-Medium.ttf
45264de3204ddbd5fb3e14a2402acd5c630d16650ae5fc221d2c52da46a6734b  chakra_petch/ChakraPetch-SemiBold.ttf
65fbf76d95651697275e19db4d717c0e95a789ddd3476478b05292104db278a0  chakra_petch/ChakraPetch-Bold.ttf
95aa02c7c43096e0dd44d787ba6216864a67157e402adab59b35572e0c1577ea  barlow/Barlow-Regular.ttf
f8906f762cb73dca441da034bc363b2d8e2e68bc10d5c05e58717646c20cc4b4  barlow/Barlow-Medium.ttf
86577cb32f8abe3673db53ca0f4221e6856751a4f6730c867e00f720f8bb1fc5  barlow/Barlow-SemiBold.ttf
84e6a4d61e7c3e21f3c50ea6a4f7e5303a3467864c038be6ea3759bab8d547f9  barlow/Barlow-Bold.ttf
```

## Licence notes

- OFL 1.1 allows bundling, embedding and selling the fonts as part of a game. The fonts may not be
  sold on their own. Keep `OFL.txt` beside the files and list both families in the in-game credits
  and THIRD_PARTY_ASSETS notes.
- Reserved Font Names: if a font is ever modified (subset tools that rename are fine for build
  output, but a modified source font), it must be renamed per the OFL.
- The logo wordmark is outlined from Chakra Petch Bold. OFL permits using the font to make artwork;
  the outlined logo is not a font and carries no OFL obligation, but the source is recorded here.

## Godot use

- Import the .ttf files directly (FontFile). Recommended import: antialiasing LCD off, hinting Light,
  generate mipmaps off, MSDF off for UI text (on only if text is scaled in 3D).
- See `assets/ui/theme/tfj_theme_spec.json` for sizes and weights per text role.
