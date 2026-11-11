"""Composes the store graphics from the captured screenshots (tools/release/capture_store.gd) and the
logo in assets/ui/branding/. Outputs: docs/store/feature-graphic.png (1024x500), docs/store/promo-still.png
(1920x1080) and docs/store/screenshots/phone/*.jpg (the chosen 8, 1920x1080 JPEG).
Run from the repo root:  python tools/release/make_store_graphics.py
"""
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
SHOTS = ROOT / "docs/store/screenshots"
LOGO = ROOT / "assets/ui/branding/logo/png/gam_logo_horizontal_a_colour_2048w.png"
OUT = ROOT / "docs/store"

PHONE_SET = [  # (output name, source png)
    ("01_nova_grid_overload", "09_nova_grid_20_b_destruction.png"),
    ("02_civitas_disruptor", "10_civitas_20_b_destruction.png"),
    ("03_meridian_temporal_lance", "11_meridian_20_b_destruction.png"),
    ("04_helix_collapse", "07_helix_20_b_destruction.png"),
    ("05_vita_breach", "08_vita_20_b_destruction.png"),
    ("06_story_cinematic", "06_cinematic.png"),
    ("07_upgrades", "04_upgrades.png"),
    ("08_mission_select", "03_mission_select.png"),
]


def gradient_h(size, left_alpha=235, right_alpha=0, hold=0.35):
    """Dark horizontal fade (opaque on the left) for text legibility."""
    w, h = size
    strip = Image.new("L", (w, 1))
    for x in range(w):
        t = x / (w - 1)
        a = left_alpha if t < hold else left_alpha + (right_alpha - left_alpha) * (t - hold) / (1 - hold)
        strip.putpixel((x, 0), int(max(0, a)))
    mask = strip.resize((w, h))
    layer = Image.new("RGBA", size, (6, 9, 14, 0))
    layer.putalpha(mask)
    return layer


def with_logo(base, logo_w, pos):
    logo = Image.open(LOGO).convert("RGBA")
    logo = logo.resize((logo_w, round(logo.height * logo_w / logo.width)), Image.LANCZOS)
    base.alpha_composite(logo, pos)
    return base


def feature_graphic():
    src = Image.open(SHOTS / "09_nova_grid_20_b_destruction.png").convert("RGBA")
    crop = src.crop((250, 225, 1520, 845)).resize((1024, 500), Image.LANCZOS)
    crop.alpha_composite(gradient_h(crop.size, 240, 0, 0.30))
    with_logo(crop, 520, (34, 190))
    crop.convert("RGB").save(OUT / "feature-graphic.png", optimize=True)


def promo_still():
    src = Image.open(SHOTS / "09_nova_grid_20_b_destruction.png").convert("RGBA")
    crop = src.crop((320, 200, 1520, 875)).resize((1920, 1080), Image.LANCZOS)
    crop.alpha_composite(gradient_h(crop.size, 240, 0, 0.30))
    with_logo(crop, 820, (80, 430))
    crop.convert("RGB").save(OUT / "promo-still.png", optimize=True)


def phone_set():
    d = SHOTS / "phone"
    d.mkdir(exist_ok=True)
    for name, png in PHONE_SET:
        Image.open(SHOTS / png).convert("RGB").save(d / (name + ".jpg"), quality=93, subsampling=0)


if __name__ == "__main__":
    feature_graphic()
    promo_still()
    phone_set()
    print("done")
