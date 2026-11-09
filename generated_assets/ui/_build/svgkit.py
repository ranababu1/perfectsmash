"""SVG helpers: rendering with resvg, glyph outlines with fontTools."""
import os, subprocess, tempfile
from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.boundsPen import BoundsPen
from tokens import RESVG, FONT_DIRS, FONTS

def write(path, svg):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        f.write(svg)

def render(svg_path, png_path, width=None, height=None, zoom=None):
    os.makedirs(os.path.dirname(png_path), exist_ok=True)
    cmd = [RESVG, "--skip-system-fonts"]
    for d in FONT_DIRS:
        cmd += ["--use-fonts-dir", d]
    if width: cmd += ["-w", str(width)]
    if height: cmd += ["-h", str(height)]
    if zoom: cmd += ["-z", str(zoom)]
    cmd += [svg_path, png_path]
    subprocess.run(cmd, check=True)

def svg_doc(w, h, body, defs="", vb=None, extra=""):
    vb = vb or f"0 0 {w} {h}"
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="{vb}" {extra}>\n'
            f'<defs>{defs}</defs>\n{body}\n</svg>\n')

_font_cache = {}
def font(name):
    if name not in _font_cache:
        _font_cache[name] = TTFont(os.path.join(FONTS, name))
    return _font_cache[name]

def text_path(text, fontfile, size, x=0, y=0, tracking=0.0, anchor="start"):
    """Return (path_d, width) for text as outlines. y = baseline. tracking in em."""
    f = font(fontfile)
    gs = f.getGlyphSet(); cmap = f.getBestCmap(); upm = f["head"].unitsPerEm
    hmtx = f["hmtx"]
    s = size / upm
    names = [cmap[ord(ch)] for ch in text]
    adv = [hmtx[n][0] for n in names]
    total = sum(adv) * s + tracking * size * (len(text) - 1)
    if anchor == "middle": x -= total / 2
    elif anchor == "end": x -= total
    ds = []
    cx = x
    for n, a in zip(names, adv):
        pen = SVGPathPen(gs)
        gs[n].draw(pen)
        d = pen.getCommands()
        if d:
            ds.append(f'<path transform="translate({cx:.2f},{y:.2f}) scale({s:.5f},{-s:.5f})" d="{d}"/>')
        cx += a * s + tracking * size
    return "\n".join(ds), total

def cap_height(fontfile, size):
    f = font(fontfile)
    os2 = f["OS/2"]
    return os2.sCapHeight * size / f["head"].unitsPerEm
