# ui/

HUD, icons, menus and branding artwork.

## Intended contents

- Weapon select icons (Kinetic Accelerator, Breach Charge).
- Objective / critical-asset markers readable at phone scale.
- Ammo and cooldown indicators (art only; numbers drawn in Godot).
- Later: logo variants, splash, chapter select frames, replacement app icons (delivered in `branding/app_icon/`; the Perfect Smash icons under `assets/icon/` were removed on 2026-11-10).

## Godot use

Imported as Texture2D / SVG. Do not bake dynamic scores, ammo counts or mission text into images.

## render_type

`ui`.
