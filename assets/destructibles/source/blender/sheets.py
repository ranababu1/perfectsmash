"""Compose labelled contact sheets from per-asset stats + tiles (system python, Pillow)."""
import json, sys, os, glob
from PIL import Image, ImageDraw, ImageFont

STATS = "/workspace/tfj-masters/3d-kits/stats"
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"


def sheet(ids, out, cell=300, title=None, states=("intact", "light", "heavy", "destroyed")):
    rows = []
    for i in ids:
        st = json.load(open(f"{STATS}/{i}.json"))
        tiles = [t for t in st.get("tiles", []) if any(t.endswith(f"_{s}.png") for s in states)]
        rows.append((st, tiles))
    lab = 22
    top = 34 if title else 0
    ncol = len(states)
    W = ncol * cell
    H = top + len(rows) * (cell + lab)
    im = Image.new("RGB", (W, H), (18, 21, 25))
    dr = ImageDraw.Draw(im)
    f = ImageFont.truetype(FONT, 13)
    fb = ImageFont.truetype(FONT, 17)
    if title:
        dr.text((10, 8), title, fill=(210, 220, 228), font=fb)
    for r, (st, tiles) in enumerate(rows):
        y = top + r * (cell + lab)
        t = st["tris"]
        dr.text((8, y + 4), f"{st['id']}   {st['reference_size_px'][0]}x{st['reference_size_px'][1]} px, depth {st['depth_m']} m   tris {t['intact']}/{t['light']}/{t['heavy']}/{t['debris']}",
                fill=(150, 162, 172), font=f)
        for c, tp in enumerate(tiles):
            tile = Image.open(tp).convert("RGB").resize((cell, cell), Image.LANCZOS)
            im.paste(tile, (c * cell, y + lab))
    os.makedirs(os.path.dirname(out), exist_ok=True)
    im.save(out, "WEBP", quality=88, method=6)
    return out


def grid(stats_files, out, title=None, ncol=4, cell=320):
    """Single-tile grid for environment, weapon and character pieces (tile /tmp/tfj_tiles/<stem>.png)."""
    items = []
    for p in stats_files:
        st = json.load(open(p))
        stem = os.path.basename(st["file"])[:-4]
        tiles = st.get("tiles") or [f"/tmp/tfj_tiles/{stem}.png"]
        for tp in tiles:
            if os.path.exists(tp):
                label = st["id"] if len(tiles) == 1 else os.path.basename(tp)[:-4].replace(stem + "_", st["id"] + "  ")
                items.append((label, f"{st['tris']['intact']} tris, {st['bytes'] / 1024:.0f} KB", tp))
    lab = 36
    top = 34 if title else 0
    nrow = (len(items) + ncol - 1) // ncol
    im = Image.new("RGB", (ncol * cell, top + nrow * (cell + lab)), (18, 21, 25))
    dr = ImageDraw.Draw(im)
    f = ImageFont.truetype(FONT, 12)
    fb = ImageFont.truetype(FONT, 17)
    if title:
        dr.text((10, 8), title, fill=(210, 220, 228), font=fb)
    for k, (label, info, tp) in enumerate(items):
        x, y = (k % ncol) * cell, top + (k // ncol) * (cell + lab)
        dr.text((x + 6, y + 3), label, fill=(170, 182, 192), font=f)
        dr.text((x + 6, y + 18), info, fill=(120, 132, 142), font=f)
        im.paste(Image.open(tp).convert("RGB").resize((cell, cell), Image.LANCZOS), (x, y + lab))
    os.makedirs(os.path.dirname(out), exist_ok=True)
    im.save(out, "WEBP", quality=88, method=6)
    return out, len(items)


if __name__ == "__main__" and sys.argv[1] == "grid":
    # sheets.py grid <out.webp> "<stats glob>" <title> [ncol]
    print(grid(sorted(glob.glob(sys.argv[3])), sys.argv[2], sys.argv[4], int(sys.argv[5]) if len(sys.argv) > 5 else 4))
elif __name__ == "__main__":
    out = sys.argv[1]
    pattern = sys.argv[2]
    title = sys.argv[3] if len(sys.argv) > 3 else None
    ids = sorted(os.path.basename(p)[:-5] for p in glob.glob(f"{STATS}/{pattern}.json"))
    print(sheet(ids, out, title=title))
