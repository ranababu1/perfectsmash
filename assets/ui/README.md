# ui/

HUD, icons, menus and branding artwork.

## Intended contents

- Weapon select icons (Kinetic Accelerator, Breach Charge).
- Objective / critical-asset markers readable at phone scale.
- Ammo and cooldown indicators (art only; numbers drawn in Godot).
- Later: logo variants, splash, chapter select frames, replacement app icons (current Perfect Smash icons remain under `assets/icon/` until replaced).

## Godot use

Imported as Texture2D / SVG. Do not bake dynamic scores, ammo counts or mission text into images.

## render_type

`ui`.
