"""Kit contact sheet (preview): every component at 2x on the game background tone, plus stretched 9-slice demos."""
import os, sys, json
sys.path.insert(0, os.path.dirname(__file__))
from PIL import Image, ImageDraw, ImageFont
from tokens import UI, FONTS, C
idx = json.load(open(os.path.join(UI, "kit", "kit_index.json")))["components"]
f = ImageFont.truetype(os.path.join(FONTS, "barlow", "Barlow-Medium.ttf"), 13)
W = 2000; x = y = 20; rowh = 0
im = Image.new("RGBA", (W, 2400), C["bg1"]); d = ImageDraw.Draw(im)
def nine(img, m, w, h):
    L, T, R, B = m["left"], m["top"], m["right"], m["bottom"]
    sw, sh = img.size; out = Image.new("RGBA", (w, h))
    xs = [(0, L, 0, L), (L, sw - R, L, w - R), (sw - R, sw, w - R, w)]
    ys = [(0, T, 0, T), (T, sh - B, T, h - B), (sh - B, sh, h - B, h)]
    for sx0, sx1, dx0, dx1 in xs:
        for sy0, sy1, dy0, dy1 in ys:
            if sx1 > sx0 and sy1 > sy0 and dx1 > dx0 and dy1 > dy0:
                out.alpha_composite(img.crop((sx0, sy0, sx1, sy1)).resize((dx1 - dx0, dy1 - dy0), Image.LANCZOS), (dx0, dy0))
    return out
for e in idx:
    img = Image.open(os.path.join(UI, "kit", "png_2x", e["file"] + ".png")).convert("RGBA")
    if e["nine_slice_2x"] and e["group"] in ("buttons", "panels") and e["name"].startswith(("button_primary", "button_secondary", "button_danger", "panel_main", "panel_modal", "panel_inset", "panel_header")) and "_" not in e["name"].replace("panel_main", "").replace("button_", "x").strip("_x").replace("primary", "").replace("secondary", "").replace("danger", "").replace("normal", "").replace("hover", "").replace("pressed", "").replace("disabled", "").replace("inset", "").replace("modal", "").replace("header", ""):
        tw, th = (480, 128) if e["name"].startswith("button") else (420, 260)
        img = nine(img, e["nine_slice_2x"], tw, th)
    w, h = img.size
    if x + w + 20 > W:
        x = 20; y += rowh + 34; rowh = 0
    im.alpha_composite(img, (x, y)); d.text((x, y + h + 4), e["name"], font=f, fill=C["text_dim"])
    x += max(w, 120) + 20; rowh = max(rowh, h)
im = im.crop((0, 0, W, y + rowh + 40))
out = os.path.join(UI, "previews", "ui_kit_contact_sheet.png"); im.save(out); print(out, im.size)
