"""Contact sheet for the icon set (preview only)."""
import os, sys, json
sys.path.insert(0, os.path.dirname(__file__))
from PIL import Image, ImageDraw, ImageFont
from tokens import UI, FONTS, C
idx = json.load(open(os.path.join(UI, "icons", "icon_index.json")))["icons"]
cols = 10; cell = 128
rows = (len(idx) + cols - 1) // cols
im = Image.new("RGBA", (cols * cell, rows * cell + 40), C["bg0"])
d = ImageDraw.Draw(im)
f = ImageFont.truetype(os.path.join(FONTS, "barlow", "Barlow-Medium.ttf"), 12)
for i, e in enumerate(idx):
    x, y = (i % cols) * cell, (i // cols) * cell
    d.rectangle([x + 4, y + 4, x + cell - 4, y + cell - 4], fill=C["surface"])
    ic0 = Image.open(os.path.join(UI, "icons", "png_2x", e["file"] + ".png")).convert("RGBA")
    ic = ic0.resize((96, 96), Image.LANCZOS)
    g = e["group"]
    tint = {"weapons": C["text"], "objectives": C["cyan"], "economy": C["star"], "chapters": C["cyan_bright"]}.get(g, C["text"])
    if e["name"] in ("critical_asset", "objective_failed"): tint = C["critical"]
    if e["name"] == "research_data": tint = C["research"]
    if e["name"] == "warning": tint = C["amber"]
    col = Image.new("RGBA", ic.size, tint); col.putalpha(ic.getchannel("A"))
    im.alpha_composite(col, (x + 16, y + 10))
    sm = ic.resize((24, 24), Image.LANCZOS); col2 = Image.new("RGBA", sm.size, tint); col2.putalpha(sm.getchannel("A"))
    im.alpha_composite(col2, (x + 96, y + 10))
    d.text((x + 10, y + 108), e["name"][:22], font=f, fill=C["text_dim"])
out = os.path.join(UI, "previews", "ui_icons_contact_sheet.png")
os.makedirs(os.path.dirname(out), exist_ok=True)
im.save(out)
print(out)
