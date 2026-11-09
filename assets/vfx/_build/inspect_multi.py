import sys, numpy as np
from PIL import Image
from vfxlib import composite
out = sys.argv[1]; items = sys.argv[2:]
tiles = []
for it in items:
    p, b = it.rsplit(":", 1)
    im = np.asarray(Image.open(p).convert("RGBA"))
    c = Image.fromarray((composite(im, b) * 255).astype(np.uint8))
    w = 760; h = int(w * c.size[1] / c.size[0]); tiles.append(c.resize((w, h), Image.LANCZOS))
cols = 2; rows = (len(tiles) + 1) // 2
H = max(t.size[1] for t in tiles)
sheet = Image.new("RGB", (cols * 770, rows * (H + 10)), (60, 60, 60))
for i, t in enumerate(tiles):
    sheet.paste(t, ((i % cols) * 770, (i // cols) * (H + 10)))
sheet.save(out); print(out, sheet.size)
