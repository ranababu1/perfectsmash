"""Temporal: First Jump branding: displacement mark, wordmark, lockups, app icons, splash and
chapter title treatments. Run: python branding.py

Design idea: a diamond (the tactical marker used throughout the UI) is split down its axis and
its right half has jumped upward, leaving a faint cyan afterimage where it was. The core is cut
with it. Time displacement, a precise fracture and a hidden centre, without clock imagery.
The wordmark carries the same idea: a single clean horizontal cut with the upper band shifted.
"""
import os, sys, json
sys.path.insert(0, os.path.dirname(__file__))
from svgkit import write, render, svg_doc, text_path, cap_height
from tokens import UI, C, CHAPTERS, DISPLAY

OUT = os.path.join(UI, "branding")
W = C["text"]; CY = C["cyan"]; DARK = C["bg0"]
BOLD = "chakra_petch/ChakraPetch-Bold.ttf"; SEMI = "chakra_petch/ChakraPetch-SemiBold.ttf"; MED = "chakra_petch/ChakraPetch-Medium.ttf"

# ---------------------------------------------------------------- mark
T = 16; R = 12; GAP = 3.0; OFF = 12
def _half(side, t=T, g=GAP / 2):
    k = t * 1.41421
    if side == "L":
        return f"M{50-g} 0 L{50-g} {k:.2f} L{k:.2f} 50 L{50-g} {100-k:.2f} L{50-g} 100 L0 50 Z"
    return f"M{50+g} 0 L100 50 L{50+g} 100 L{50+g} {100-k:.2f} L{100-k:.2f} 50 L{50+g} {k:.2f} Z"
def _core(side, r=R, g=GAP / 2):
    if side == "L":
        return f"M{50-g} {50-r+g} L{50-g} {50+r-g} L{50-r+g} 50 Z"
    return f"M{50+g} {50-r+g} L{50+r-g} 50 L{50+g} {50+r-g} Z"

def mark_body(frame=W, core=CY, echo=True, echo_color=CY, echo_op=0.5, echo_w=1.6):
    """Mark in a 100-unit box; visual bounds x 0..100, y -12..100."""
    s = ""
    if echo:
        s += f'<path id="echo" d="{_half("R")}" fill="none" stroke="{echo_color}" stroke-opacity="{echo_op}" stroke-width="{echo_w}"/>'
    s += f'<path id="frame_left" d="{_half("L")}" fill="{frame}"/><path id="core_left" d="{_core("L")}" fill="{core}"/>'
    s += f'<g id="displaced" transform="translate(0,{-OFF})"><path id="frame_right" d="{_half("R")}" fill="{frame}"/><path id="core_right" d="{_core("R")}" fill="{core}"/></g>'
    return s
MARK_BOUNDS = (0, -OFF, 100, 100 + OFF)  # x, y, w, h

# ---------------------------------------------------------------- wordmark
WM_SIZE = 120; WM_TRACK = 0.10; CUT = 0.45; SHIFT = 10; SLIT = 2.6
def wordmark(color=W, accent=CY, sub_color=None, rule_color=None, editable=False, uid="wm", subtitle=True):
    """Returns (defs, body, width, height). Origin top-left of cap height. Height includes subtitle."""
    sub_color = sub_color or accent; rule_color = rule_color or color
    ch = cap_height(BOLD, WM_SIZE)
    d, w = text_path("TEMPORAL", BOLD, WM_SIZE, 0, ch, tracking=WM_TRACK)
    cut = ch * (1 - CUT)  # y of cut from top
    defs = (f'<clipPath id="{uid}_top"><rect x="-40" y="-40" width="{w+80}" height="{cut - SLIT/2 + 40}"/></clipPath>'
            f'<clipPath id="{uid}_bot"><rect x="-40" y="{cut + SLIT/2}" width="{w+80}" height="{ch}"/></clipPath>')
    if editable:
        ls = WM_TRACK * WM_SIZE
        glyphs = (f'<text x="0" y="{ch:.2f}" font-family="{DISPLAY}" font-weight="700" font-size="{WM_SIZE}" '
                  f'letter-spacing="{ls:.2f}" fill="{color}">TEMPORAL</text>')
    else:
        glyphs = f'<g fill="{color}">{d}</g>'
    body = (f'<g id="wordmark_lower" clip-path="url(#{uid}_bot)">{glyphs}</g>'
            f'<g id="wordmark_upper_displaced" clip-path="url(#{uid}_top)"><g transform="translate({SHIFT},0)">{glyphs}</g></g>'
            f'<rect id="jump_seam" x="{w*0.31:.2f}" y="{cut - 0.7:.2f}" width="{w*0.45:.2f}" height="1.4" fill="{accent}"/>')
    if not subtitle:
        return defs, body, w + SHIFT, ch
    sub_size = WM_SIZE * 0.30; sub_y = ch + WM_SIZE * 0.44
    sub_ch = cap_height(SEMI, sub_size)
    if editable:
        sub = (f'<text x="{w/2:.2f}" y="{sub_y:.2f}" text-anchor="middle" font-family="{DISPLAY}" font-weight="600" '
               f'font-size="{sub_size:.2f}" letter-spacing="{0.42*sub_size:.2f}" fill="{sub_color}">FIRST JUMP</text>')
        _, w2 = text_path("FIRST JUMP", SEMI, sub_size, w / 2, sub_y, tracking=0.42, anchor="middle")
    else:
        d2, w2 = text_path("FIRST JUMP", SEMI, sub_size, w / 2, sub_y, tracking=0.42, anchor="middle")
        sub = f'<g id="subtitle" fill="{sub_color}">{d2}</g>'
    ry = sub_y - sub_ch / 2 - 1
    lw = w / 2 - w2 / 2 - 26
    rules = (f'<rect x="0" y="{ry:.2f}" width="{lw:.2f}" height="2" fill="{rule_color}" fill-opacity="0.38"/>'
             f'<rect x="{w - lw:.2f}" y="{ry:.2f}" width="{lw:.2f}" height="2" fill="{rule_color}" fill-opacity="0.38"/>')
    return defs, body + sub + rules, w + SHIFT, sub_y + 2

# ---------------------------------------------------------------- lockups
SCHEMES = {
    "colour":        dict(frame=W, core=CY, text=W, accent=CY, bg=None),
    "light_on_dark": dict(frame=W, core=CY, text=W, accent=CY, bg=DARK),
    "mono_light":    dict(frame="#FFFFFF", core="#FFFFFF", text="#FFFFFF", accent="#FFFFFF", bg=None, echo=False),
    "mono_dark":     dict(frame=DARK, core=DARK, text=DARK, accent=DARK, bg=None, echo=False),
    "colour_on_light": dict(frame=DARK, core=C["cyan_deep"], text=DARK, accent=C["cyan_deep"], bg=None),
}

def bg_plate(w, h):
    return (f'<defs><radialGradient id="plate" cx="50%" cy="45%" r="75%"><stop offset="0" stop-color="#121C25"/>'
            f'<stop offset="1" stop-color="{C["void"]}"/></radialGradient></defs><rect width="{w}" height="{h}" fill="url(#plate)"/>')

def lockup(kind, scheme, editable=False):
    sc = SCHEMES[scheme]
    echo = sc.get("echo", True)
    mono = scheme.startswith("mono")
    defs, wm, ww, wh = wordmark(sc["text"], sc["accent"], editable=editable, uid=f"wm")
    mk = mark_body(sc["frame"], sc["core"], echo=echo, echo_color=sc["accent"])
    pad = 48
    if kind == "horizontal":
        ms = wh / (100 + OFF) * 1.0          # mark height == wordmark block height
        mw = 100 * ms; gap = 44
        W_, H_ = pad * 2 + mw + gap + ww, pad * 2 + wh
        body = (f'<g id="mark" transform="translate({pad},{pad + OFF*ms:.2f}) scale({ms:.4f})">{mk}</g>'
                f'<g id="wordmark" transform="translate({pad + mw + gap:.2f},{pad})">{wm}</g>')
    elif kind == "stacked":
        ms = 2.6; mw = 100 * ms; mh = (100 + OFF) * ms; gap = 52
        W_ = pad * 2 + max(ww, mw); H_ = pad * 2 + mh + gap + wh
        body = (f'<g id="mark" transform="translate({(W_-mw)/2:.2f},{pad + OFF*ms:.2f}) scale({ms})">{mk}</g>'
                f'<g id="wordmark" transform="translate({(W_-ww)/2:.2f},{pad + mh + gap:.2f})">{wm}</g>')
    elif kind == "compact":
        # small-space lockup: mark + TEMPORAL only (FIRST JUMP omitted); use >= 160 px wide
        defs, g, w, ch = wordmark(sc["text"], sc["accent"], editable=editable, uid="wmc", subtitle=False)
        ms = ch * 1.5 / (100 + OFF); mw = 100 * ms; gap = 34
        W_, H_ = pad * 2 + mw + gap + w, pad * 2 + ch * 1.5
        body = (f'<g id="mark" transform="translate({pad},{pad + OFF*ms:.2f}) scale({ms:.4f})">{mk}</g>'
                f'<g id="wordmark" transform="translate({pad + mw + gap:.2f},{pad + ch*0.25:.2f})">{g}</g>')
    else:
        raise ValueError(kind)
    W_, H_ = round(W_), round(H_)
    pre = bg_plate(W_, H_) if sc["bg"] else ""
    return svg_doc(W_, H_, pre + body, defs=defs), (W_, H_)

def mark_svg(scheme, size=512, echo=None, pad=0.12):
    sc = SCHEMES[scheme]
    e = sc.get("echo", True) if echo is None else echo
    vb_w = 100 + 2 * 100 * pad; vb_h = 100 + OFF + 2 * 100 * pad
    vb = f"{-100*pad} {-OFF - 100*pad} {vb_w} {vb_h}"
    body = mark_body(sc["frame"], sc["core"], echo=e, echo_color=sc["accent"])
    pre = ""
    if sc["bg"]:
        pre = f'<rect x="{-100*pad}" y="{-OFF-100*pad}" width="{vb_w}" height="{vb_h}" fill="{sc["bg"]}"/>'
    h = round(size * vb_h / vb_w)
    return svg_doc(size, h, pre + body, vb=vb)

# ---------------------------------------------------------------- app icon (Android adaptive 108 dp -> 432 px)
def icon_background(n=432):
    lines = "".join(f'<path d="M{x} {n} L{x + n*0.6:.1f} 0" stroke="#FFFFFF" stroke-opacity="0.025" stroke-width="2"/>' for x in range(-300, n, 36))
    return svg_doc(n, n, (
        f'<rect width="{n}" height="{n}" fill="url(#g)"/>{lines}'
        f'<rect width="{n}" height="{n}" fill="url(#glow)"/>'
        f'<rect y="{n*0.62}" width="{n}" height="1.5" fill="{CY}" fill-opacity="0.10"/>'),
        defs=(f'<linearGradient id="g" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#16222D"/><stop offset="1" stop-color="#06090C"/></linearGradient>'
              f'<radialGradient id="glow" cx="50%" cy="50%" r="50%"><stop offset="0" stop-color="{CY}" stop-opacity="0.16"/>'
              f'<stop offset="0.55" stop-color="{CY}" stop-opacity="0.03"/><stop offset="1" stop-color="{CY}" stop-opacity="0"/></radialGradient>'))

def icon_foreground(n=432, mono=False, scale=2.05):
    # Adaptive safe zone: 66 dp circle = 264 px diameter centred in 432. Mark fits inside it.
    cx, cy = n / 2, n / 2
    mw = 100 * scale
    ox = cx - mw / 2; oy = cy - (100 - OFF) / 2 * scale - OFF * scale + OFF * scale * 0.5
    # centre the visual bounds (y -12..100) on the canvas centre
    oy = cy - ((100 + OFF) / 2 - OFF) * scale
    if mono:
        body = mark_body("#FFFFFF", "#FFFFFF", echo=False)
    else:
        body = mark_body(W, CY, echo=True, echo_op=0.55, echo_w=2.2)
    return svg_doc(n, n, f'<g transform="translate({ox:.2f},{oy:.2f}) scale({scale})">{body}</g>')

def dither_icons():
    """Rebuild the PNG exports of the icon background (and flattened icons) with dithered gradients."""
    from dither import radial, linear_v, to_image
    from PIL import Image
    import numpy as np
    def bg_png(n):
        rgb = linear_v(n, n, [(0, "#16222D"), (1, "#06090C")])
        y, x = np.mgrid[0:n, 0:n] + 0.5
        d = np.sqrt((x - n / 2) ** 2 + (y - n / 2) ** 2) / (n / 2)
        g = np.interp(d, [0, 0.55, 1.0], [0.16, 0.03, 0.0])[..., None]
        rgb = rgb * (1 - g) + np.array([0x3C, 0xC8, 0xE6]) * g
        img = to_image(rgb)
        # vector detail (diagonal structure lines + horizon) without the gradient fills
        det = svg_doc(432, 432, "".join(f'<path d="M{x} 432 L{x + 432*0.6:.1f} 0" stroke="#FFFFFF" stroke-opacity="0.025" stroke-width="2"/>' for x in range(-300, 432, 36))
                      + f'<rect y="{432*0.62}" width="432" height="1.5" fill="{CY}" fill-opacity="0.10"/>')
        write("/tmp/_icon_det.svg", det); render("/tmp/_icon_det.svg", "/tmp/_icon_det.png", width=n)
        img.alpha_composite(Image.open("/tmp/_icon_det.png").convert("RGBA"))
        return img
    b = bg_png(432); b.convert("RGB").save(os.path.join(OUT, "app_icon/android_adaptive/gam_logo_app_icon_a_background_432.png"))
    for n in (512, 256, 192, 48):
        full = int(round(n * 432 / 352))
        bb = bg_png(full)
        render(os.path.join(OUT, "app_icon/android_adaptive/gam_logo_app_icon_a_foreground_432.svg"), "/tmp/_fg.png", width=full)
        bb.alpha_composite(Image.open("/tmp/_fg.png").convert("RGBA"))
        off = (full - n) // 2
        bb.crop((off, off, off + n, off + n)).convert("RGB").save(os.path.join(OUT, f"app_icon/gam_logo_app_icon_a_{n}.png"))

# ---------------------------------------------------------------- chapter title treatments
ROMAN = {1: "I", 2: "II", 3: "III", 4: "IV", 5: "V"}
def chapter_title(key, with_text=True):
    ch = CHAPTERS[key]; a = ch["accent"]; a2 = ch["accent2"]
    Wd, Hd = 1280, 720
    from icons import I as ICONS
    emb = ICONS[f"chapter_{key}"].replace('#fff', a)
    import re
    emb = re.sub(r'<(?:path|circle)[^>]*fill="#000"[^>]*/>', '', emb)
    cx = 640
    # emblem plate: chamfered diamond frame with a soft inner fill, emblem at 2x icon scale
    deco = (
        f'<g id="emblem_plate"><path d="M{cx} 150 L{cx+78} 228 L{cx} 306 L{cx-78} 228 Z" fill="{a}" fill-opacity="0.06" stroke="{a}" stroke-opacity="0.55" stroke-width="1.5"/>'
        f'<path d="M{cx} 138 L{cx+90} 228 L{cx} 318 L{cx-90} 228 Z" fill="none" stroke="{a}" stroke-opacity="0.18" stroke-width="1"/></g>'
        f'<g id="emblem" transform="translate({cx-48},180) scale(2)">{emb}</g>'
        f'<rect id="rule_left" x="{cx-470}" y="355.25" width="320" height="1.5" fill="url(#fadeL)"/>'
        f'<rect id="rule_right" x="{cx+150}" y="355.25" width="320" height="1.5" fill="url(#fadeR)"/>'
        f'<path id="tick_left" d="M{cx-146} 350 L{cx-138} 356 L{cx-146} 362 Z" fill="{a}"/>'
        f'<path id="tick_right" d="M{cx+146} 350 L{cx+138} 356 L{cx+146} 362 Z" fill="{a}"/>'
        f'<rect id="underline_accent" x="{cx-32}" y="482" width="64" height="3" fill="{a2}"/>'
    )
    defs = (f'<linearGradient id="fadeL" x1="0" x2="1"><stop offset="0" stop-color="{a}" stop-opacity="0"/><stop offset="1" stop-color="{a}" stop-opacity="0.9"/></linearGradient>'
            f'<linearGradient id="fadeR" x1="0" x2="1"><stop offset="0" stop-color="{a}" stop-opacity="0.9"/><stop offset="1" stop-color="{a}" stop-opacity="0"/></linearGradient>')
    text = ""
    if with_text:
        text = (
            f'<text id="txt_chapter_number" x="{cx + 3.5}" y="364" text-anchor="middle" font-family="{DISPLAY}" font-weight="600" font-size="22" letter-spacing="7" fill="{a}">CHAPTER {ROMAN[ch["n"]]}</text>'
            f'<text id="txt_chapter_title" x="{cx + 2.5}" y="440" text-anchor="middle" font-family="{DISPLAY}" font-weight="700" font-size="62" letter-spacing="5" fill="{W}">{ch["title"].upper()}</text>'
            f'<text id="txt_institution_year" x="{cx + 3}" y="530" text-anchor="middle" font-family="Barlow" font-weight="500" font-size="24" letter-spacing="6" fill="{C["text_dim"]}">{ch["org"].upper()}  /  {ch["year"]}</text>'
        )
    return svg_doc(Wd, Hd, deco + text, defs=defs)

def main():
    made = []
    def put(rel, svg, png=None, pw=None, ph=None):
        p = os.path.join(OUT, rel); write(p, svg); made.append(p)
        if png:
            q = os.path.join(OUT, png); render(p, q, width=pw, height=ph); made.append(q)
    # mark
    for sch in ("colour", "light_on_dark", "mono_light", "mono_dark", "colour_on_light"):
        put(f"logo/svg/gam_logo_mark_a_{sch}.svg", mark_svg(sch), f"logo/png/gam_logo_mark_a_{sch}_1024.png", 1024)
    put("logo/svg/gam_logo_mark_a_colour_simple.svg", mark_svg("colour", echo=False), "logo/png/gam_logo_mark_a_colour_simple_256.png", 256)
    # lockups: production (outlined) + editable source (live text)
    for kind in ("horizontal", "stacked", "compact"):
        for sch in ("colour", "light_on_dark", "mono_light", "mono_dark", "colour_on_light"):
            svg, (w, h) = lockup(kind, sch)
            tw = {"horizontal": 2048, "stacked": 1200, "compact": 1600}[kind]
            put(f"logo/svg/gam_logo_{kind}_a_{sch}.svg", svg, f"logo/png/gam_logo_{kind}_a_{sch}_{tw}w.png", tw)
        src, _ = lockup(kind, "colour", editable=True)
        put(f"logo/source/gam_logo_{kind}_a_editable.svg", src, f"../previews/branding_editable_render_check_{kind}.png", 1024)
    # app icon
    put("app_icon/android_adaptive/gam_logo_app_icon_a_background_432.svg", icon_background(), "app_icon/android_adaptive/gam_logo_app_icon_a_background_432.png", 432)
    put("app_icon/android_adaptive/gam_logo_app_icon_a_foreground_432.svg", icon_foreground(), "app_icon/android_adaptive/gam_logo_app_icon_a_foreground_432.png", 432)
    put("app_icon/android_adaptive/gam_logo_app_icon_a_monochrome_432.svg", icon_foreground(mono=True), "app_icon/android_adaptive/gam_logo_app_icon_a_monochrome_432.png", 432)
    # flattened legacy / store icons
    bg = icon_background(); fg = icon_foreground()
    import re
    inner_bg = re.search(r"<defs>(.*?)</defs>\n(.*)\n</svg>", bg, re.S); inner_fg = re.search(r"<defs>(.*?)</defs>\n(.*)\n</svg>", fg, re.S)
    full = svg_doc(432, 432, inner_bg.group(2) + inner_fg.group(2), defs=inner_bg.group(1))
    # legacy square icons crop to the central 72 dp (288 px) like a launcher mask would show more fully
    put("app_icon/gam_logo_app_icon_a_full_432.svg", full)
    for n in (512, 256, 192, 48):
        p = os.path.join(OUT, f"app_icon/gam_logo_app_icon_a_{n}.png"); made.append(p)
    # crop: legacy icons show the 88 dp inner area (352 px) so the mark is larger than in adaptive form
    legacy = svg_doc(352, 352, inner_bg.group(2) + inner_fg.group(2), defs=inner_bg.group(1), vb="40 40 352 352")
    put("app_icon/gam_logo_app_icon_a_legacy.svg", legacy)
    for n in (512, 256, 192, 48):
        render(os.path.join(OUT, "app_icon/gam_logo_app_icon_a_legacy.svg"), os.path.join(OUT, f"app_icon/gam_logo_app_icon_a_{n}.png"), width=n)
    dither_icons()
    # chapter titles
    for key in CHAPTERS:
        n = CHAPTERS[key]["n"]
        put(f"chapter_titles/source/gam_ui_chapter_title_0{n}_{key}_editable.svg", chapter_title(key, True), f"../previews/branding_chapter_title_0{n}_{key}_preview.png", 1280)
        put(f"chapter_titles/game/gam_ui_chapter_title_0{n}_{key}_deco.svg", chapter_title(key, False), f"chapter_titles/game/gam_ui_chapter_title_0{n}_{key}_deco_1x.png", 1280)
        render(os.path.join(OUT, f"chapter_titles/game/gam_ui_chapter_title_0{n}_{key}_deco.svg"), os.path.join(OUT, f"chapter_titles/game/gam_ui_chapter_title_0{n}_{key}_deco_2x.png"), width=2560)
        made.append(os.path.join(OUT, f"chapter_titles/game/gam_ui_chapter_title_0{n}_{key}_deco_2x.png"))
    print(len(made), "files")

if __name__ == "__main__":
    main()

# ---------------------------------------------------------------- splash
def splash(w=1280, h=720, logo_w=520, with_bg=True):
    import re
    svg, (lw, lh) = lockup("stacked", "colour")
    inner = re.search(r"<defs>(.*?)</defs>\n(.*)\n</svg>", svg, re.S)
    s = logo_w / lw
    x = (w - logo_w) / 2; y = (h - lh * s) / 2 - 10
    defs = (inner.group(1) + f'<radialGradient id="sp" cx="50%" cy="46%" r="70%"><stop offset="0" stop-color="#132029"/><stop offset="0.6" stop-color="#090E13"/><stop offset="1" stop-color="{C["void"]}"/></radialGradient>'
            f'<linearGradient id="hz" x1="0" x2="1"><stop offset="0" stop-color="{CY}" stop-opacity="0"/><stop offset="0.5" stop-color="{CY}" stop-opacity="0.35"/><stop offset="1" stop-color="{CY}" stop-opacity="0"/></linearGradient>')
    body = ((f'<rect width="{w}" height="{h}" fill="url(#sp)"/>' if with_bg else "")
            + f'<rect x="0" y="{h*0.5:.1f}" width="{w}" height="1" fill="url(#hz)" opacity="0.35"/>'
            f'<g transform="translate({x:.2f},{y:.2f}) scale({s:.4f})">{inner.group(2)}</g>')
    return svg_doc(w, h, body, defs=defs)

def splash_main():
    from dither import radial, to_image
    from PIL import Image
    p = os.path.join(OUT, "splash/gam_ui_splash_a.svg"); write(p, splash())
    fg = "/tmp/_splash_fg.svg"; write(fg, splash(with_bg=False))
    for (w, h) in ((1280, 720), (2560, 1440)):
        base = to_image(radial(w, h, 0.5, 0.46, 0.7, 0.7, [(0, "#132029"), (0.6, "#090E13"), (1, C["void"])]))
        render(fg, "/tmp/_splash_fg.png", width=w)
        base.alpha_composite(Image.open("/tmp/_splash_fg.png").convert("RGBA"))
        base.convert("RGB").save(os.path.join(OUT, f"splash/gam_ui_splash_a_{w}x{h}.png"), optimize=True)
    p2 = os.path.join(OUT, "splash/gam_ui_splash_a_logo_transparent.svg")
    svg, _ = lockup("stacked", "colour"); write(p2, svg)
    render(p2, os.path.join(OUT, "splash/gam_ui_splash_a_logo_transparent_1024w.png"), width=1024)

if __name__ == "__main__" and "--splash" in sys.argv:
    splash_main()
