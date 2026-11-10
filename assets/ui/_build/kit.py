"""Temporal: First Jump UI kit: vector component generators + 9-slice / sprite exports.

Every component is a function returning an SVG fragment at any size, so screen layouts reuse the
exact same drawing code. `export()` writes per-component SVG sources and PNGs at 1x and 2x for the
1280x720 base, plus kit_index.json with 9-slice margins (file pixels) for Godot StyleBoxTexture.
Run: python kit.py
"""
import os, sys, json, math
sys.path.insert(0, os.path.dirname(__file__))
from svgkit import write, render, svg_doc
from tokens import UI, C, CHAPTERS, TIERS

_uid = [0]
def uid(p="g"):
    _uid[0] += 1; return f"{p}{_uid[0]}"

def chamfer(x, y, w, h, c, tl=True, tr=False, br=True, bl=False):
    pts = []
    pts += [(x + c, y)] if tl else [(x, y)]
    pts += [(x + w - c, y), (x + w, y + c)] if tr else [(x + w, y)]
    pts += [(x + w, y + h - c), (x + w - c, y + h)] if br else [(x + w, y + h)]
    pts += [(x + c, y + h), (x, y + h - c)] if bl else [(x, y + h)]
    if tl: pts += [(x, y + c)]
    return "M" + " L".join(f"{a:.2f} {b:.2f}" for a, b in pts) + " Z"

def vgrad(stops, x2=0, y2=1):
    i = uid("lg")
    s = "".join(f'<stop offset="{o}" stop-color="{c}" stop-opacity="{a}"/>' for o, c, a in stops)
    return i, f'<linearGradient id="{i}" x1="0" y1="0" x2="{x2}" y2="{y2}">{s}</linearGradient>'

# ------------------------------------------------------------------ panels
def panel(x, y, w, h, c=12, variant="main", accent=None):
    """variant: main | inset | modal | header"""
    accent = accent or C["cyan"]
    defs = ""
    if variant == "inset":
        gid, g = vgrad([(0, "#0A1117", 0.92), (1, "#0C141B", 0.92)]); defs += g
        border, bop = C["line"], 0.9
    elif variant == "modal":
        gid, g = vgrad([(0, "#18252F", 0.97), (1, "#101920", 0.97)]); defs += g
        border, bop = "#3A4E5E", 1.0
    else:
        gid, g = vgrad([(0, "#15202A", 0.94), (1, "#0F171E", 0.94)]); defs += g
        border, bop = "#2C3B48", 1.0
    d = chamfer(x, y, w, h, c)
    s = f'<path d="{d}" fill="url(#{gid})"/>'
    # inner top highlight
    s += f'<path d="M{x + c + 1} {y + 1.5} H{x + w - 1.5}" stroke="#FFFFFF" stroke-opacity="0.07" stroke-width="1"/>'
    s += f'<path d="{chamfer(x + 0.5, y + 0.5, w - 1, h - 1, c - 0.2)}" fill="none" stroke="{border}" stroke-opacity="{bop}" stroke-width="1"/>'
    if variant in ("main", "modal"):
        # accent ticks on the chamfered corners
        s += f'<path d="M{x + 0.5} {y + c + 8} V{y + c} L{x + c} {y + 0.5} H{x + c + 8}" fill="none" stroke="{accent}" stroke-width="2"/>'
        s += f'<path d="M{x + w - 0.5} {y + h - c - 8} V{y + h - c} L{x + w - c} {y + h - 0.5} H{x + w - c - 8}" fill="none" stroke="{accent}" stroke-opacity="0.6" stroke-width="2"/>'
    if variant == "modal":
        s += f'<rect x="{x + c + 14}" y="{y}" width="{min(96, w - 2 * c - 28)}" height="2" fill="{accent}"/>'
    if variant == "header":
        s += f'<rect x="{x}" y="{y + c}" width="3" height="{h - 2 * c}" fill="{accent}"/>'
    return defs, s

# ------------------------------------------------------------------ buttons
BTN = {
    "primary": {
        "normal":   dict(fill=[(0, "#4AD3EE", 1), (1, "#28AFCF", 1)], border="#8FE8F8", bop=0.9, ink=C["ink"]),
        "hover":    dict(fill=[(0, "#6FDDF2", 1), (1, "#36BEDD", 1)], border="#C9F5FD", bop=1.0, ink=C["ink"], halo=True),
        "pressed":  dict(fill=[(0, "#1F98B5", 1), (1, "#2AAECD", 1)], border="#5FD4EA", bop=0.8, ink=C["ink"], inset=True),
        "disabled": dict(fill=[(0, "#1A2530", 1), (1, "#16202A", 1)], border="#2A3846", bop=1.0, ink=C["text_disabled"]),
    },
    "secondary": {
        "normal":   dict(fill=[(0, "#18242F", 0.92), (1, "#121C25", 0.92)], border=C["cyan"], bop=0.55, ink=C["text"]),
        "hover":    dict(fill=[(0, "#1E2F3D", 0.95), (1, "#172531", 0.95)], border=C["cyan_bright"], bop=0.95, ink=C["text"], halo=True),
        "pressed":  dict(fill=[(0, "#0D151C", 0.95), (1, "#121C25", 0.95)], border=C["cyan"], bop=0.8, ink=C["text"], inset=True),
        "disabled": dict(fill=[(0, "#121A21", 0.7), (1, "#10171D", 0.7)], border="#2A3846", bop=0.8, ink=C["text_disabled"]),
    },
    "danger": {
        "normal":   dict(fill=[(0, "#2A1615", 0.94), (1, "#1E1111", 0.94)], border=C["critical"], bop=0.65, ink=C["text"]),
        "hover":    dict(fill=[(0, "#3A1B19", 0.96), (1, "#291514", 0.96)], border="#FF8A7E", bop=1.0, ink=C["text"], halo=True),
        "pressed":  dict(fill=[(0, "#170C0C", 0.96), (1, "#211110", 0.96)], border=C["critical"], bop=0.85, ink=C["text"], inset=True),
        "disabled": dict(fill=[(0, "#121A21", 0.7), (1, "#10171D", 0.7)], border="#2A3846", bop=0.8, ink=C["text_disabled"]),
    },
}
def button(x, y, w, h, kind="primary", state="normal", c=10):
    st = BTN[kind][state]
    gid, g = vgrad(st["fill"]); defs = g
    s = ""
    if st.get("halo"):
        s += f'<path d="{chamfer(x - 3, y - 3, w + 6, h + 6, c + 1.5)}" fill="none" stroke="{st["border"]}" stroke-opacity="0.28" stroke-width="1.5"/>'
    s += f'<path d="{chamfer(x, y, w, h, c)}" fill="url(#{gid})"/>'
    if st.get("inset"):
        s += f'<path d="M{x + c} {y + 1.5} H{x + w - 1}" stroke="#000" stroke-opacity="0.35" stroke-width="2"/>'
    elif kind == "primary" and state != "disabled":
        s += f'<path d="M{x + c} {y + 1.5} H{x + w - 1.5}" stroke="#FFFFFF" stroke-opacity="0.45" stroke-width="1"/>'
    s += f'<path d="{chamfer(x + 0.5, y + 0.5, w - 1, h - 1, c - 0.2)}" fill="none" stroke="{st["border"]}" stroke-opacity="{st["bop"]}" stroke-width="1"/>'
    if kind != "primary" and state not in ("disabled",):
        s += f'<path d="M{x + w - c - 22} {y + h - 3.5} H{x + w - c - 3}" stroke="{st["border"]}" stroke-width="2" stroke-opacity="{st["bop"]}"/>'
    return defs, s, st["ink"]

def icon_button(x, y, size, state="normal", c=10):
    m = {"normal": ("secondary", "normal"), "hover": ("secondary", "hover"), "pressed": ("secondary", "pressed"), "disabled": ("secondary", "disabled")}
    return button(x, y, size, size, *m[state], c=c)

def focus_ring(x, y, w, h, c=10):
    return "", f'<path d="{chamfer(x - 4, y - 4, w + 8, h + 8, c + 2)}" fill="none" stroke="{C["cyan_bright"]}" stroke-width="2"/>'

# ------------------------------------------------------------------ tabs
def tab(x, y, w, h, state="normal"):
    s = ""
    if state == "selected":
        gid, g = vgrad([(0, "#1C2B38", 0.0), (1, "#1C2B38", 0.95)])
        s += f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="url(#{gid})"/>'
        s += f'<rect x="{x}" y="{y + h - 3}" width="{w}" height="3" fill="{C["cyan"]}"/>'
        s += f'<path d="M{x + w/2 - 6} {y + h - 3} L{x + w/2} {y + h - 9} L{x + w/2 + 6} {y + h - 3} Z" fill="{C["cyan"]}"/>'
        return g, s
    if state == "hover":
        s += f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="#FFFFFF" fill-opacity="0.04"/>'
        s += f'<rect x="{x}" y="{y + h - 2}" width="{w}" height="2" fill="{C["cyan"]}" fill-opacity="0.45"/>'
        return "", s
    if state == "disabled":
        s += f'<rect x="{x}" y="{y + h - 1}" width="{w}" height="1" fill="{C["line"]}" fill-opacity="0.6"/>'
        return "", s
    s += f'<rect x="{x}" y="{y + h - 1}" width="{w}" height="1" fill="{C["line_solid"]}"/>'
    return "", s

# ------------------------------------------------------------------ bars
def bar_track(x, y, w, h):
    return "", (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="#070C10" fill-opacity="0.9"/>'
                f'<rect x="{x + 0.5}" y="{y + 0.5}" width="{w - 1}" height="{h - 1}" fill="none" stroke="{C["line"]}" stroke-width="1"/>')
def bar_fill(x, y, w, h, color=C["cyan"], segments=False):
    gid, g = vgrad([(0, color, 1), (1, color, 0.78)])
    s = f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="url(#{gid})"/>'
    s += f'<rect x="{x}" y="{y}" width="{w}" height="1" fill="#FFFFFF" fill-opacity="0.35"/>'
    if segments:
        for sx in range(int(x) + 8, int(x + w), 8):
            s += f'<rect x="{sx}" y="{y}" width="1" height="{h}" fill="#000" fill-opacity="0.35"/>'
    return g, s

def slider_grabber(cx, cy, state="normal"):
    col = {"normal": C["text"], "hover": C["cyan_bright"], "pressed": C["cyan"], "disabled": C["text_disabled"]}[state]
    s = ""
    if state in ("hover", "pressed"):
        s += f'<path d="M{cx} {cy - 17} L{cx + 17} {cy} L{cx} {cy + 17} L{cx - 17} {cy} Z" fill="{C["cyan"]}" fill-opacity="0.16"/>'
    s += f'<path d="M{cx} {cy - 12} L{cx + 12} {cy} L{cx} {cy + 12} L{cx - 12} {cy} Z" fill="{C["bg1"]}" stroke="{col}" stroke-width="2"/>'
    s += f'<path d="M{cx} {cy - 5} L{cx + 5} {cy} L{cx} {cy + 5} L{cx - 5} {cy} Z" fill="{col}"/>'
    return "", s

def toggle(x, y, state="off"):
    """64x32 switch. state: off | on | off_disabled | on_disabled"""
    on = state.startswith("on"); dis = state.endswith("disabled")
    w, h = 64, 32
    track_fill = (C["cyan_deep"] if on else "#0A1117"); border = (C["cyan"] if on else C["line_solid"])
    if dis: track_fill, border = ("#14202A" if on else "#0B1116"), C["line"]
    s = f'<path d="{chamfer(x, y, w, h, 8, tl=True, br=True)}" fill="{track_fill}" fill-opacity="{0.9 if on else 0.95}"/>'
    s += f'<path d="{chamfer(x + 0.5, y + 0.5, w - 1, h - 1, 7.8)}" fill="none" stroke="{border}" stroke-width="1"/>'
    kx = x + (w - 4 - 26) if on else x + 4
    kc = (C["text"] if on else C["steel"]) if not dis else C["text_disabled"]
    s += f'<path d="{chamfer(kx, y + 4, 26, h - 8, 5)}" fill="{kc}"/>'
    if on and not dis:
        s += f'<rect x="{x + 10}" y="{y + 14}" width="12" height="4" fill="{C["cyan_bright"]}" fill-opacity="0.8"/>'
    return "", s

# ------------------------------------------------------------------ cooldown ring (TextureProgressBar radial)
def ring(cx, cy, r, w, part="under", color=C["cyan"]):
    if part == "under":
        return "", (f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="#070C10" stroke-opacity="0.85" stroke-width="{w + 2}"/>'
                    f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="{C["line_solid"]}" stroke-width="{w}" stroke-opacity="0.5"/>')
    if part == "progress":
        return "", f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="{color}" stroke-width="{w}"/>'
    # over: segment ticks + inner hairline
    s = ""
    for i in range(24):
        a = math.radians(i * 15 - 90)
        x0, y0 = cx + (r - w / 2 - 1) * math.cos(a), cy + (r - w / 2 - 1) * math.sin(a)
        x1, y1 = cx + (r + w / 2 + 1) * math.cos(a), cy + (r + w / 2 + 1) * math.sin(a)
        s += f'<path d="M{x0:.2f} {y0:.2f} L{x1:.2f} {y1:.2f}" stroke="#070C10" stroke-width="1.6"/>'
    s += f'<circle cx="{cx}" cy="{cy}" r="{r - w/2 - 4}" fill="none" stroke="#FFFFFF" stroke-opacity="0.10" stroke-width="1"/>'
    s += f'<path d="M{cx} {cy - r - w/2 - 5} L{cx + 4} {cy - r - w/2 - 10} H{cx - 4} Z" fill="{C["text"]}"/>'
    return "", s

# ------------------------------------------------------------------ ammo pips
def pip(x, y, kind="kinetic", state="full"):
    """kinetic pip 10x24 (slim slug), breach pip 16x24 (canister)."""
    if kind == "kinetic":
        w, h = 10, 24
        if state == "full":
            return "", (f'<path d="{chamfer(x, y, w, h, 3, tl=True, tr=True, br=False, bl=False)}" fill="{C["cyan"]}"/>'
                        f'<rect x="{x}" y="{y + h - 5}" width="{w}" height="2" fill="#000" fill-opacity="0.35"/>')
        return "", f'<path d="{chamfer(x + 0.75, y + 0.75, w - 1.5, h - 1.5, 2.5, tl=True, tr=True, br=False, bl=False)}" fill="#070C10" fill-opacity="0.6" stroke="{C["line_solid"]}" stroke-width="1.5"/>'
    w, h = 16, 24
    if state == "full":
        return "", (f'<path d="M{x + 3} {y} H{x + w - 3} L{x + w} {y + 3} V{y + h - 3} L{x + w - 3} {y + h} H{x + 3} L{x} {y + h - 3} V{y + 3} Z" fill="{C["amber"]}"/>'
                    f'<rect x="{x}" y="{y + 9}" width="{w}" height="6" fill="#1A1006" fill-opacity="0.75"/>'
                    f'<path d="M{x + 3} {y + 15} L{x + 7} {y + 9} M{x + 9} {y + 15} L{x + 13} {y + 9}" stroke="{C["amber"]}" stroke-width="2"/>')
    return "", f'<path d="M{x + 3.75} {y + 0.75} H{x + w - 3.75} L{x + w - 0.75} {y + 3.75} V{y + h - 3.75} L{x + w - 3.75} {y + h - 0.75} H{x + 3.75} L{x + 0.75} {y + h - 3.75} V{y + 3.75} Z" fill="#070C10" fill-opacity="0.6" stroke="{C["line_solid"]}" stroke-width="1.5"/>'

# ------------------------------------------------------------------ markers
def objective_marker(cx, cy, state="primary", s=1.0):
    col = {"primary": C["cyan"], "optional": C["text_dim"], "complete": C["success"], "failed": C["critical"]}[state]
    r = 14 * s
    out = f'<path d="M{cx} {cy - r} L{cx + r} {cy} L{cx} {cy + r} L{cx - r} {cy} Z" fill="{C["bg0"]}" fill-opacity="0.75" stroke="{col}" stroke-width="{2.5*s}"/>'
    if state == "primary":
        out += f'<path d="M{cx} {cy - r*0.45} L{cx + r*0.45} {cy} L{cx} {cy + r*0.45} L{cx - r*0.45} {cy} Z" fill="{col}"/>'
    elif state == "optional":
        out += f'<path d="M{cx} {cy - r*0.35} L{cx + r*0.35} {cy} L{cx} {cy + r*0.35} L{cx - r*0.35} {cy} Z" fill="{col}" fill-opacity="0.8"/>'
    elif state == "complete":
        out += f'<path d="M{cx - 6*s} {cy} L{cx - 1.5*s} {cy + 4.5*s} L{cx + 6.5*s} {cy - 4*s}" fill="none" stroke="{col}" stroke-width="{2.5*s}"/>'
    else:
        out += f'<path d="M{cx - 4.5*s} {cy - 4.5*s} L{cx + 4.5*s} {cy + 4.5*s} M{cx + 4.5*s} {cy - 4.5*s} L{cx - 4.5*s} {cy + 4.5*s}" stroke="{col}" stroke-width="{2.5*s}"/>'
    # stem pointing down to the world position
    out += f'<path d="M{cx} {cy + r + 3*s} V{cy + r + 12*s}" stroke="{col}" stroke-width="{2*s}" stroke-opacity="0.8"/>'
    return "", out

def offscreen_arrow(cx, cy, color=C["cyan"]):
    return "", (f'<path d="M{cx - 12} {cy - 14} L{cx + 14} {cy} L{cx - 12} {cy + 14} L{cx - 6} {cy} Z" fill="{color}"/>'
                f'<path d="M{cx - 22} {cy - 14} L{cx + 4} {cy} L{cx - 22} {cy + 14}" fill="none" stroke="{color}" stroke-opacity="0.4" stroke-width="2"/>')

def critical_marker(cx, cy, size=96, layer="all", color=C["critical"]):
    """Critical-asset target marker. Layers: brackets (static), diamond (pulse scale), ring (rotate)."""
    h = size / 2; k = size * 0.18; t = max(2.0, size * 0.035)
    out = ""
    if layer in ("all", "ring"):
        r = size * 0.40
        for i in range(4):
            a0 = i * 90 + 12; a1 = a0 + 66
            x0, y0 = cx + r * math.cos(math.radians(a0)), cy + r * math.sin(math.radians(a0))
            x1, y1 = cx + r * math.cos(math.radians(a1)), cy + r * math.sin(math.radians(a1))
            out += f'<path d="M{x0:.2f} {y0:.2f} A{r} {r} 0 0 1 {x1:.2f} {y1:.2f}" fill="none" stroke="{color}" stroke-opacity="0.55" stroke-width="{t*0.6:.2f}"/>'
    if layer in ("all", "brackets"):
        o = h - t
        out += (f'<path d="M{cx - o} {cy - o + k} V{cy - o} H{cx - o + k} M{cx + o - k} {cy - o} H{cx + o} V{cy - o + k} '
                f'M{cx + o} {cy + o - k} V{cy + o} H{cx + o - k} M{cx - o + k} {cy + o} H{cx - o} V{cy + o - k}" fill="none" stroke="{color}" stroke-width="{t:.2f}"/>')
    if layer in ("all", "diamond"):
        r = size * 0.13
        out += f'<path d="M{cx} {cy - r} L{cx + r} {cy} L{cx} {cy + r} L{cx - r} {cy} Z" fill="{color}"/>'
        out += f'<path d="M{cx} {cy - r - 6} L{cx + r + 6} {cy} L{cx} {cy + r + 6} L{cx - r - 6} {cy} Z" fill="none" stroke="#FFFFFF" stroke-opacity="0.75" stroke-width="1.5"/>'
    return "", out

# ------------------------------------------------------------------ HUD pieces
def weapon_slot(x, y, w, h, state="normal", accent=C["cyan"]):
    """HUD weapon card: normal | selected | empty | cooldown (overlay drawn by code)."""
    d1, s = panel(x, y, w, h, c=10, variant="inset")
    if state == "selected":
        s += f'<path d="{chamfer(x + 0.75, y + 0.75, w - 1.5, h - 1.5, 9.8)}" fill="none" stroke="{accent}" stroke-width="1.5"/>'
        s += f'<rect x="{x + 10}" y="{y + h - 3}" width="{w - 20}" height="3" fill="{accent}"/>'
        s += f'<path d="{chamfer(x, y, w, h, 10)}" fill="{accent}" fill-opacity="0.07"/>'
    elif state == "empty":
        s += f'<path d="{chamfer(x, y, w, h, 10)}" fill="#000" fill-opacity="0.35"/>'
        s += f'<path d="M{x + 10} {y + h - 10} L{x + w - 10} {y + 10}" stroke="{C["critical"]}" stroke-opacity="0.5" stroke-width="1.5"/>'
    return d1, s

def chip(x, y, w, h):
    return "", (f'<path d="{chamfer(x, y, w, h, 6)}" fill="#0A1117" fill-opacity="0.82"/>'
                f'<path d="{chamfer(x + 0.5, y + 0.5, w - 1, h - 1, 5.8)}" fill="none" stroke="{C["line_solid"]}" stroke-width="1"/>')

def chapter_card(x, y, w, h, key, state="normal"):
    a = CHAPTERS[key]["accent"]
    d1, s = panel(x, y, w, h, c=14, variant="main", accent=a)
    if state == "selected":
        s += f'<path d="{chamfer(x - 3, y - 3, w + 6, h + 6, 16)}" fill="none" stroke="{a}" stroke-width="2"/>'
    if state == "locked":
        s += f'<path d="{chamfer(x, y, w, h, 14)}" fill="#05080B" fill-opacity="0.6"/>'
    return d1, s

def trajectory_dot(cx, cy, r=5, color=C["text"]):
    return "", f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{color}"/><circle cx="{cx}" cy="{cy}" r="{r + 1.5}" fill="none" stroke="#000" stroke-opacity="0.45" stroke-width="1.5"/>'

def aim_reticle(cx, cy, size=64, color=C["text"]):
    h = size / 2
    return "", (f'<circle cx="{cx}" cy="{cy}" r="{h*0.55}" fill="none" stroke="{color}" stroke-width="2"/>'
                f'<path d="M{cx} {cy - h + 2} V{cy - h*0.7} M{cx} {cy + h - 2} V{cy + h*0.7} M{cx - h + 2} {cy} H{cx - h*0.7} M{cx + h - 2} {cy} H{cx + h*0.7}" stroke="{color}" stroke-width="2.5"/>'
                f'<circle cx="{cx}" cy="{cy}" r="2.5" fill="{color}"/>')

def divider(x, y, w, color=C["line_solid"]):
    gid, g = vgrad([(0, color, 0), (0.15, color, 1), (0.85, color, 1), (1, color, 0)], x2=1, y2=0)
    return g, f'<rect x="{x}" y="{y}" width="{w}" height="1" fill="url(#{gid})"/>'

def scrim(w, h):
    gid, g = vgrad([(0, "#05080B", 0.55), (1, "#05080B", 0.85)])
    return g, f'<rect width="{w}" height="{h}" fill="url(#{gid})"/>'

def tier_badge(cx, cy, tier="tier1", s=1.0):
    col = TIERS[tier]["color"]; n = int(tier[-1])
    out = f'<path d="M{cx} {cy - 14*s} L{cx + 14*s} {cy} L{cx} {cy + 14*s} L{cx - 14*s} {cy} Z" fill="{C["bg0"]}" stroke="{col}" stroke-width="{2*s}"/>'
    for i in range(3):
        on = i < n
        yy = cy + (4 - i * 5) * s
        out += f'<path d="M{cx - 6*s} {yy + 2*s} L{cx} {yy - 2*s} L{cx + 6*s} {yy + 2*s}" fill="none" stroke="{col}" stroke-opacity="{1 if on else 0.25}" stroke-width="{2*s}"/>'
    return "", out

# ------------------------------------------------------------------ export
ENTRIES = []
def _emit(name, w, h, frag, nine=None, notes="", group="kit", pad=0):
    defs, body = frag[0], frag[1]
    W_, H_ = w + 2 * pad, h + 2 * pad
    svg = svg_doc(W_, H_, f'<g id="{name}">{body}</g>', defs=defs)
    stem = f"gam_ui_{name}"
    src = os.path.join(UI, "kit", "svg", f"{stem}.svg"); write(src, svg)
    p1 = os.path.join(UI, "kit", "png_1x", f"{stem}.png"); p2 = os.path.join(UI, "kit", "png_2x", f"{stem}.png")
    render(src, p1, width=W_); render(src, p2, width=W_ * 2)
    ENTRIES.append({"name": name, "file": stem, "group": group, "size_1x": [W_, H_], "size_2x": [W_ * 2, H_ * 2],
                    "nine_slice_1x": nine, "nine_slice_2x": ({k: v * 2 for k, v in nine.items()} if nine else None), "notes": notes})

def export():
    # panels (9-slice)
    for v in ("main", "inset", "modal", "header"):
        _emit(f"panel_{v}", 96, 96, panel(0, 0, 96, 96, 12, v), nine=dict(left=28, top=28, right=28, bottom=28),
              notes="StyleBoxTexture; axis_stretch stretch; content margins 24 at 1x", group="panels")
    for key in CHAPTERS:
        _emit(f"panel_main_{key}", 96, 96, panel(0, 0, 96, 96, 12, "main", accent=CHAPTERS[key]["accent"]), nine=dict(left=28, top=28, right=28, bottom=28),
              notes=f"chapter-accent variant ({key})", group="panels")
    for key in CHAPTERS:
        for st in ("normal", "selected", "locked"):
            _emit(f"card_chapter_{key}_{st}", 112, 112, chapter_card(4, 4, 104, 104, key, st), nine=dict(left=34, top=34, right=34, bottom=34),
                  notes="chapter tile frame; emblem and text added in Godot", group="cards")
    # buttons (9-slice)
    for kind in BTN:
        for st in BTN[kind]:
            d, s, ink = button(4, 4, 96, 56, kind, st)
            _emit(f"button_{kind}_{st}", 104, 64, (d, s), nine=dict(left=22, top=22, right=22, bottom=22),
                  notes=f"label colour {ink}; 4 px transparent pad on each side holds the hover halo; set StyleBox expand margins 4 (1x)", group="buttons")
    for st in ("normal", "hover", "pressed", "disabled"):
        d, s, ink = icon_button(4, 4, 64, st)
        _emit(f"button_icon_{st}", 72, 72, (d, s), nine=dict(left=22, top=22, right=22, bottom=22), notes="64 px square icon button (touch minimum) with 4 px halo pad", group="buttons")
    _emit("focus_ring", 104, 64, focus_ring(4, 4, 96, 56), nine=dict(left=22, top=22, right=22, bottom=22), notes="keyboard/gamepad focus StyleBox; drawn over buttons", group="buttons")
    # tabs
    for st in ("normal", "hover", "selected", "disabled"):
        _emit(f"tab_{st}", 96, 48, tab(0, 0, 96, 48, st), nine=dict(left=16, top=8, right=16, bottom=10), notes="TabBar tab StyleBox", group="tabs")
    # slider
    _emit("slider_track", 64, 8, bar_track(0, 0, 64, 8), nine=dict(left=3, top=3, right=3, bottom=3), notes="HSlider slider StyleBox", group="slider")
    _emit("slider_fill", 64, 8, bar_fill(0, 0, 64, 8), nine=dict(left=3, top=3, right=3, bottom=3), notes="HSlider grabber_area StyleBox", group="slider")
    for st in ("normal", "hover", "pressed", "disabled"):
        _emit(f"slider_grabber_{st}", 40, 40, slider_grabber(20, 20, st), notes="HSlider grabber icon", group="slider")
    # toggles
    for st in ("off", "on", "off_disabled", "on_disabled"):
        _emit(f"toggle_{st}", 64, 32, toggle(0, 0, st), notes="CheckButton checked/unchecked icons", group="toggle")
    # progress bars
    _emit("progress_track", 64, 12, bar_track(0, 0, 64, 12), nine=dict(left=3, top=3, right=3, bottom=3), notes="ProgressBar background", group="progress")
    for nm, col in (("cyan", C["cyan"]), ("amber", C["amber"]), ("critical", C["critical"]), ("success", C["success"])):
        _emit(f"progress_fill_{nm}", 64, 12, bar_fill(0, 0, 64, 12, col), nine=dict(left=3, top=3, right=3, bottom=3), notes="ProgressBar fill", group="progress")
        _emit(f"progress_fill_{nm}_segmented", 64, 12, bar_fill(0, 0, 64, 12, col, segments=True), nine=dict(left=0, top=3, right=0, bottom=3), notes="segmented fill; axis_stretch tile horizontally", group="progress")
    # cooldown rings (TextureProgressBar, fill_mode clockwise)
    for part in ("under", "progress", "over"):
        _emit(f"cooldown_ring_{part}", 96, 96, ring(48, 48, 36, 6, part), notes="TextureProgressBar radial, fill_mode FILL_CLOCKWISE, radial_initial_angle 0", group="cooldown")
    _emit("cooldown_ring_progress_amber", 96, 96, ring(48, 48, 36, 6, "progress", C["amber"]), notes="Breach Charge cooldown", group="cooldown")
    # ammo pips
    for k in ("kinetic", "breach"):
        for st in ("full", "empty"):
            w = 10 if k == "kinetic" else 16
            _emit(f"ammo_pip_{k}_{st}", w + 4, 28, pip(2, 2, k, st), notes="HBox of TextureRects; one pip per round", group="ammo")
    # markers
    for st in ("primary", "optional", "complete", "failed"):
        _emit(f"objective_marker_{st}", 48, 64, objective_marker(24, 22, st), notes="world-space objective marker, pivot bottom-centre (24, 60 at 1x)", group="markers")
    _emit("offscreen_indicator", 48, 48, offscreen_arrow(26, 24), notes="edge-of-screen pointer; rotate toward target; pivot centre", group="markers")
    _emit("offscreen_indicator_critical", 48, 48, offscreen_arrow(26, 24, C["critical"]), notes="critical-asset edge pointer", group="markers")
    for layer in ("all", "brackets", "diamond", "ring"):
        _emit(f"critical_marker_{layer}", 128, 128, critical_marker(64, 64, 120, layer), notes="critical-asset marker; animate layers in code: ring rotates 30 deg/s, diamond pulses scale 0.9-1.1 at 1.2 Hz; pivot centre", group="markers")
    _emit("aim_reticle", 64, 64, aim_reticle(32, 32, 60), notes="aim end-point reticle; tint white", group="hud")
    _emit("trajectory_dot", 16, 16, trajectory_dot(8, 8, 5), notes="trajectory preview dot; fade alpha along the arc", group="hud")
    for st in ("normal", "selected", "empty"):
        _emit(f"weapon_slot_{st}", 112, 112, weapon_slot(4, 4, 104, 104, st), nine=dict(left=30, top=30, right=30, bottom=30), notes="HUD weapon card", group="hud")
    _emit("chip", 64, 40, chip(0, 0, 64, 40), nine=dict(left=12, top=12, right=12, bottom=12), notes="small info chip (currency, timers)", group="hud")
    _emit("divider", 256, 4, divider(0, 1.5, 256), notes="horizontal divider; stretch X", group="panels")
    for t in TIERS:
        _emit(f"tier_badge_{t}", 40, 40, tier_badge(20, 20, t), notes=f"upgrade tier badge {TIERS[t]['name']}", group="upgrades")
    with open(os.path.join(UI, "kit", "kit_index.json"), "w") as f:
        json.dump({"base_viewport": [1280, 720], "files": {"svg": "svg/<file>.svg", "1x": "png_1x/<file>.png", "2x": "png_2x/<file>.png"},
                   "nine_slice_note": "margins in file pixels; use nine_slice_2x with the 2x PNG (contract: author at 2x, display at base size)", "components": ENTRIES}, f, indent=1)
    print(len(ENTRIES), "kit components")

if __name__ == "__main__":
    export()
