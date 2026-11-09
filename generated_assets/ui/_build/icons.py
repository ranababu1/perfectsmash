"""Temporal: First Jump icon set. 48-unit grid, 4-unit keyline, 3-unit strokes, mitred joins.

Icons are authored white so Godot can tint them with modulate / theme colours. Each icon is
written as a standalone SVG source, then rasterised to 1x (48 px) and 2x (96 px) PNGs.
Run: python icons.py
"""
import math, os, sys, json
sys.path.insert(0, os.path.dirname(__file__))
from svgkit import write, render, svg_doc
from tokens import UI, C

SW = 3
def P(d, fill=False, w=SW, op=1.0, cap="butt"):
    o = f' opacity="{op}"' if op != 1.0 else ""
    if fill:
        return f'<path d="{d}" fill="#fff"{o}/>'
    return f'<path d="{d}" fill="none" stroke="#fff" stroke-width="{w}" stroke-linejoin="miter" stroke-miterlimit="10" stroke-linecap="{cap}"{o}/>'
def circ(cx, cy, r, fill=False, w=SW, op=1.0):
    o = f' opacity="{op}"' if op != 1.0 else ""
    if fill: return f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="#fff"{o}/>'
    return f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="#fff" stroke-width="{w}"{o}/>'
def pt(cx, cy, r, a):
    a = math.radians(a); return (cx + r * math.cos(a), cy + r * math.sin(a))
def arc(cx, cy, r, a0, a1):
    """Arc path from angle a0 to a1 degrees (clockwise in screen space when a1>a0)."""
    x0, y0 = pt(cx, cy, r, a0); x1, y1 = pt(cx, cy, r, a1)
    large = 1 if abs(a1 - a0) > 180 else 0
    sweep = 1 if a1 > a0 else 0
    return f"M{x0:.2f} {y0:.2f} A{r} {r} 0 {large} {sweep} {x1:.2f} {y1:.2f}"
def poly(pts, close=True):
    s = "M" + " L".join(f"{x:.2f} {y:.2f}" for x, y in pts)
    return s + (" Z" if close else "")
def star_pts(cx, cy, ro, ri, n=5, rot=-90):
    out = []
    for i in range(n * 2):
        r = ro if i % 2 == 0 else ri
        out.append(pt(cx, cy, r, rot + i * 180 / n))
    return out
def arrowhead(x, y, ang, size=6):
    a = math.radians(ang)
    l = (x - size * math.cos(a) + size * 0.75 * math.cos(a + math.pi / 2), y - size * math.sin(a) + size * 0.75 * math.sin(a + math.pi / 2))
    r = (x - size * math.cos(a) - size * 0.75 * math.cos(a + math.pi / 2), y - size * math.sin(a) - size * 0.75 * math.sin(a + math.pi / 2))
    return P(poly([(x + 2 * math.cos(a), y + 2 * math.sin(a)), l, r]), fill=True)
def gear(cx, cy, ro, ri, teeth=8):
    pts = []
    step = 360 / teeth
    for i in range(teeth):
        b = i * step - 90
        pts += [pt(cx, cy, ri, b - step * 0.5), pt(cx, cy, ri, b - step * 0.22), pt(cx, cy, ro, b - step * 0.16), pt(cx, cy, ro, b + step * 0.16), pt(cx, cy, ri, b + step * 0.22)]
    return poly(pts)
def hexagon(cx, cy, r, rot=-90):
    return poly([pt(cx, cy, r, rot + i * 60) for i in range(6)])
def diamond(cx, cy, r):
    return poly([(cx, cy - r), (cx + r, cy), (cx, cy + r), (cx - r, cy)])
def chamfer_rect(x, y, w, h, c):
    return poly([(x + c, y), (x + w, y), (x + w, y + h - c), (x + w - c, y + h), (x, y + h), (x, y + c)])
def hood(cx, top, w, h):
    # anonymous operative hood: pointed crown, angled cowl, dark visor slot
    return poly([(cx, top), (cx + w * 0.42, top + h * 0.32), (cx + w * 0.5, top + h * 0.78), (cx + w * 0.22, top + h), (cx - w * 0.22, top + h), (cx - w * 0.5, top + h * 0.78), (cx - w * 0.42, top + h * 0.32)])

def circ_d(cx, cy, r):
    return f"M{cx-r} {cy} A{r} {r} 0 1 0 {cx+r} {cy} A{r} {r} 0 1 0 {cx-r} {cy} Z"

I = {}
cat = {}
def icon(name, group):
    def deco(fn):
        I[name] = fn(); cat[name] = group; return fn
    return deco

# ---------------- weapons ----------------
@icon("weapon_kinetic_accelerator", "weapons")
def _():
    # electromagnetic precision launcher: wedge receiver, twin accelerator rails, three coil rings,
    # short underslung fore-grip (no pistol grip, no scope)
    return (P("M4 22 L10 17 H28 V31 H16 L13 28 H4 Z", fill=True)
            + P("M28 18 H45 V21.5 H28 Z M28 26.5 H45 V30 H28 Z", fill=True)
            + P("M31 15 H34 V33 H31 Z M37 15 H40 V33 H37 Z M43 16.5 H45.5 V31.5 H43 Z", fill=True)
            + P("M17 31 H23 L21 37 H17 Z", fill=True)
            + P("M8 22.5 H20", w=2).replace('stroke="#fff"', 'stroke="#000"'))
@icon("weapon_breach_charge", "weapons")
def _():
    # launcher-fired canister: capsule body, hazard band, stabiliser fins
    return (P("M18 9 H30 L33 13 V35 L30 39 H18 L15 35 V13 Z")
            + P("M15 20 H33 V27 H15 Z", fill=True)
            + P("M21 20 L17 27 M27 20 L23 27 M33 20 L29 27", w=2.4).replace('stroke="#fff"', 'stroke="#000"')
            + P("M20 39 L17 44 H31 L28 39", w=2.5)
            + P("M21 4 H27 V9 H21 Z", fill=True))
@icon("weapon_precision_accelerator", "weapons")
def _():
    return (P("M4 23 L10 19 H26 V29 H14 L11 27 H4 Z", fill=True)
            + P("M26 20 H45 V23 H26 Z M26 25 H45 V28 H26 Z", fill=True)
            + P("M29 16 H31 V32 H29 Z M34 16 H36 V32 H34 Z M39 16 H41 V32 H39 Z", fill=True)
            + P("M12 13 H20 M12 13 V16 M44 37 H36 M44 37 V34", w=2)
            + P("M15 29 H20 L19 35 H15 Z", fill=True))
@icon("weapon_penetrator", "weapons")
def _():
    return (P("M4 24 L12 19 H30 L44 24 L30 29 H12 Z")
            + P("M30 19 L44 24 L30 29 Z", fill=True)
            + P("M16 24 H26", w=2.5) + P("M7 13 L12 19 M7 35 L12 29", w=2.5))
@icon("weapon_pulse_cannon", "weapons")
def _():
    return (P("M5 18 H22 L26 21 V27 L22 30 H5 Z", fill=True)
            + P(arc(30, 24, 7, -60, 60)) + P(arc(31, 24, 12, -50, 50)) + P(arc(32, 24, 17, -42, 42), op=0.6))
@icon("weapon_disruptor", "weapons")
def _():
    return (P("M5 20 H18 L22 17 V31 L18 28 H5 Z", fill=True)
            + P("M22 17 L32 12 M22 31 L32 36", w=3)
            + P("M28 24 L32 20 L36 27 L40 21 L44 24", w=2.5))
@icon("weapon_temporal_lance", "weapons")
def _():
    return (P("M4 24 H14", w=3) + P(diamond(20, 24, 6), fill=True)
            + P("M26 24 H44", w=3) + P("M36 18 L44 24 L36 30", w=3)
            + P(diamond(20, 24, 11), w=1.8, op=0.55))

# ---------------- upgrades ----------------
@icon("upgrade_impact_energy", "upgrades")
def _():
    return (P("M32 6 V42", w=3) + P(circ_d(18, 24, 6), fill=True) + P("M6 24 H10", w=3)
            + P("M27 14 L24 18 M27 34 L24 30 M27 24 H24", w=2.5) + P("M36 12 L40 8 M36 36 L40 40 M37 24 H42", w=2.5))
@icon("upgrade_penetration", "upgrades")
def _():
    return (P("M22 6 H28 V20 M28 28 V42 H22 V28 M22 20 V6", w=2.5)
            + P("M4 24 H34", w=3) + P("M32 17 L42 24 L32 31 Z", fill=True))
@icon("upgrade_blast_efficiency", "upgrades")
def _():
    return P(poly(star_pts(24, 24, 18, 8, n=8, rot=-90)), fill=False, w=2.5) + P(diamond(24, 24, 5), fill=True)
@icon("upgrade_energy_capacity", "upgrades")
def _():
    return (P(chamfer_rect(8, 14, 30, 20, 3)) + P("M38 20 H42 V28 H38", w=3)
            + P("M13 19 H18 V29 H13 Z M21 19 H26 V29 H21 Z", fill=True) + P("M29 19 H34 V29 H29 Z", w=1.6, op=0.7))
@icon("upgrade_targeting_assistance", "upgrades")
def _():
    return (circ(30, 18, 9) + P("M30 6 V11 M30 25 V30 M18 18 H23 M37 18 H42", w=2.5)
            + P("M6 42 Q10 30 18 26", w=2.5, cap="round").replace('stroke-width="2.5"', 'stroke-width="2.5" stroke-dasharray="3 3"'))
@icon("upgrade_energy_efficiency", "upgrades")
def _():
    x, y = pt(24, 24, 16, 20)
    return (P(arc(24, 24, 16, 110, 380)) + arrowhead(x, y, 20 + 90, 7)
            + P("M26 12 L18 26 H24 L22 36 L30 22 H24 Z", fill=True))

# ---------------- objectives ----------------
@icon("objective_primary", "objectives")
def _():
    return P(diamond(24, 24, 17)) + P(diamond(24, 24, 8), fill=True)
@icon("objective_optional", "objectives")
def _():
    return P(diamond(24, 24, 17), w=2.5).replace('stroke-width="2.5"', 'stroke-width="2.5" stroke-dasharray="5 3.5"') + P(diamond(24, 24, 6), fill=True, op=0.8)
@icon("objective_complete", "objectives")
def _():
    return P(diamond(24, 24, 18)) + P("M15 24 L21 30 L33 18", w=3.5)
@icon("objective_failed", "objectives")
def _():
    return P(diamond(24, 24, 18)) + P("M18 18 L30 30 M30 18 L18 30", w=3.5)
@icon("critical_asset", "objectives")
def _():
    b = "M6 15 V6 H15 M33 6 H42 V15 M42 33 V42 H33 M15 42 H6 V33"
    return P(b, w=3) + P(diamond(24, 24, 10), fill=True) + P(diamond(24, 24, 15), w=1.8, op=0.6)
@icon("destroy_components", "objectives")
def _():
    return (P("M8 18 H20 L18 26 L22 30 L20 40 H8 Z", fill=True) + P("M26 18 H40 V40 H28 L31 33 L26 28 L29 22 Z", fill=True)
            + P("M12 8 H36 V13 H12 Z", fill=True, op=0.55))
@icon("max_shots", "objectives")
def _():
    return (P(circ_d(14, 24, 6), fill=True) + P("M24 24 H30", w=2.5, op=0.7)
            + P("M33 14 V34 M38 14 V34 M43 14 V34", w=2.5))
@icon("time_limit", "objectives")
def _():
    # hourglass, chamfered; deliberately not a clock face
    return (P("M12 6 H36 M12 42 H36", w=3) + P("M15 6 L15 12 L24 24 L15 36 L15 42 M33 6 L33 12 L24 24 L33 36 L33 42", w=2.5)
            + P("M18 40 L24 32 L30 40 Z", fill=True) + P("M19 13 H29 L24 19 Z", fill=True, op=0.7))
@icon("intel_briefing", "objectives")
def _():
    return P(chamfer_rect(10, 6, 28, 36, 6)) + P("M16 16 H32 M16 22 H32 M16 28 H26", w=2.5) + P(diamond(31, 34, 3.5), fill=True)
@icon("mission", "objectives")
def _():
    return circ(24, 24, 16) + circ(24, 24, 8, w=2.5) + circ(24, 24, 2.5, fill=True) + P("M24 2 V10 M24 38 V46 M2 24 H10 M38 24 H46", w=2.5)

# ---------------- economy / rating ----------------
@icon("research_data", "economy")
def _():
    # Research Data: faceted data shard
    return (P("M24 4 L38 16 L24 44 L10 16 Z", fill=True)
            + P("M10 16 H38 M18 16 L24 4 L30 16 M18 16 L24 44 M30 16 L24 44", w=1.6).replace('stroke="#fff"', 'stroke="#000"'))
@icon("mission_points", "economy")
def _():
    return P("M10 30 L24 20 L38 30", w=3.5) + P("M10 40 L24 30 L38 40", w=3.5) + P(diamond(24, 10, 5), fill=True)
@icon("star_full", "economy")
def _():
    return P(poly(star_pts(24, 25, 20, 8.6)), fill=True)
@icon("star_empty", "economy")
def _():
    return P(poly(star_pts(24, 25, 19, 8.2)), w=2.5)
@icon("star_half", "economy")
def _():
    pts = star_pts(24, 25, 20, 8.6)
    left = [p for p in pts if p[0] <= 24.01]
    return (P(poly(star_pts(24, 25, 19, 8.2)), w=2.5)
            + f'<clipPath id="h"><rect x="0" y="0" width="24" height="48"/></clipPath><g clip-path="url(#h)">' + P(poly(pts), fill=True) + "</g>")
@icon("trophy", "economy")
def _():
    return (P("M14 6 H34 V18 L30 26 H18 L14 18 Z", fill=True) + P("M14 10 H7 V15 L13 21 M34 10 H41 V15 L35 21", w=2.5)
            + P("M22 26 V34 H26 V26 Z M15 36 H33 V42 H15 Z", fill=True))

# ---------------- state ----------------
@icon("lock", "state")
def _():
    return P("M16 22 V15 A8 8 0 0 1 32 15 V22", w=3.5) + P(chamfer_rect(10, 21, 28, 21, 4), fill=True) + P("M22.5 28 H25.5 V35 H22.5 Z", fill=True).replace('fill="#fff"', 'fill="#000"')
@icon("unlock", "state")
def _():
    return P("M16 21 V15 A8 8 0 0 1 31.6 12.6", w=3.5) + P(chamfer_rect(10, 21, 28, 21, 4), fill=True)
@icon("check", "state")
def _():
    return P("M9 25 L19 35 L39 13", w=4.5)
@icon("cross", "state")
def _():
    return P("M12 12 L36 36 M36 12 L12 36", w=4.5)
@icon("warning", "state")
def _():
    return P("M24 5 L44 41 H4 Z", w=3) + P("M22.2 16 H25.8 L25 30 H23 Z", fill=True) + P("M22.2 33 H25.8 V36.6 H22.2 Z", fill=True)
@icon("info", "state")
def _():
    return P(diamond(24, 24, 19), w=3) + P("M22.2 21 H25.8 V34 H22.2 Z M22.2 14 H25.8 V17.6 H22.2 Z", fill=True)
@icon("shield", "state")
def _():
    return P("M24 4 L40 10 V24 C40 33 33 40 24 44 C15 40 8 33 8 24 V10 Z", w=3) + P("M24 12 L33 16 V24 C33 29 29 33 24 36 Z", fill=True)
@icon("repair", "state")
def _():
    return (P("M30 6 A10 10 0 0 0 23 20 L8 35 L13 40 L28 25 A10 10 0 0 0 42 18 L36 20 L31 17 L30 11 Z", fill=True))

# ---------------- navigation ----------------
@icon("play", "navigation")
def _():
    return P("M15 9 L39 24 L15 39 Z", fill=True)
@icon("pause", "navigation")
def _():
    return P("M13 9 H20 V39 H13 Z M28 9 H35 V39 H28 Z", fill=True)
@icon("retry", "navigation")
def _():
    x, y = pt(24, 24, 15, 20)
    return P(arc(24, 24, 15, 120, 380)) + arrowhead(x, y, 20 + 90, 7)
@icon("next", "navigation")
def _():
    return P("M18 10 L32 24 L18 38", w=4)
@icon("back", "navigation")
def _():
    return P("M30 10 L16 24 L30 38", w=4)
@icon("skip", "navigation")
def _():
    return P("M8 11 L22 24 L8 37 Z M22 11 L36 24 L22 37 Z", fill=True) + P("M37 11 H41 V37 H37 Z", fill=True)
@icon("fast_forward", "navigation")
def _():
    return P("M6 12 L22 24 L6 36 Z M24 12 L40 24 L24 36 Z", fill=True)
@icon("home", "navigation")
def _():
    return P("M6 22 L24 7 L42 22", w=3.5) + P("M11 22 V41 H20 V30 H28 V41 H37 V22", w=3)
@icon("close", "navigation")
def _():
    return P("M13 13 L35 35 M35 13 L13 35", w=4)
@icon("menu", "navigation")
def _():
    return P("M8 13 H40 M8 24 H40 M8 35 H32", w=3.5)
@icon("settings", "navigation")
def _():
    return P(gear(24, 24, 19, 14.5, 8), fill=True) + '<circle cx="24" cy="24" r="6.5" fill="#000"/>'
@icon("chapter_map", "navigation")
def _():
    return (P("M5 10 L17 6 L31 10 L43 6 V38 L31 42 L17 38 L5 42 Z", w=2.5)
            + P("M11 33 L19 24 L27 28 L36 16", w=2).replace('stroke-width="2"', 'stroke-width="2" stroke-dasharray="3 2.5"')
            + P(diamond(36, 16, 4), fill=True) + circ(11, 33, 2.5, fill=True))
@icon("replay", "navigation")
def _():
    x, y = pt(24, 24, 17, 10)
    return P(arc(24, 24, 17, 100, 370)) + arrowhead(x, y, 10 + 90, 7) + P("M20 16 L32 24 L20 32 Z", fill=True)
@icon("credits", "navigation")
def _():
    return P(chamfer_rect(8, 6, 32, 36, 6)) + P(diamond(24, 18, 5), fill=True) + P("M15 29 H33 M18 35 H30", w=2.5)

# ---------------- settings ----------------
def speaker():
    return P("M6 18 H13 L23 9 V39 L13 30 H6 Z", fill=True)
@icon("sound_on", "settings")
def _():
    return speaker() + P(arc(24, 24, 8, -50, 50)) + P(arc(24, 24, 15, -50, 50))
@icon("sound_off", "settings")
def _():
    return speaker() + P("M29 18 L41 30 M41 18 L29 30", w=3.5)
@icon("music_on", "settings")
def _():
    return P("M18 34 V9 L40 5 V30", w=3.5) + P(circ_d(13, 34, 6), fill=True) + P(circ_d(35, 30, 6), fill=True) + P("M18 15 L40 11", w=3.5)
@icon("music_off", "settings")
def _():
    return I["music_on"] + P("M6 6 L42 42", w=3.5) if "music_on" in I else ""
@icon("vibration", "settings")
def _():
    return P(chamfer_rect(16, 6, 16, 36, 3), w=3) + P("M10 14 L6 18 L10 22 L6 26 L10 30 L6 34 M38 14 L42 18 L38 22 L42 26 L38 30 L42 34", w=2.2)
@icon("graphics", "settings")
def _():
    return (P(diamond(24, 28, 15), fill=False, w=2.5, op=0.6) + P(diamond(24, 22, 15), fill=True))
@icon("language", "settings")
def _():
    return circ(24, 24, 18) + P("M6 24 H42 M24 6 C14 14 14 34 24 42 C34 34 34 14 24 6", w=2.5)
@icon("controls_touch", "settings")
def _():
    return circ(24, 24, 18, w=2, op=0.55) + circ(24, 24, 11, w=2.8) + circ(24, 24, 4, fill=True)
@icon("accessibility", "settings")
def _():
    return circ(24, 9, 4, fill=True) + P("M8 16 H40 M24 16 V30 M24 30 L16 43 M24 30 L32 43", w=3.5)
@icon("brightness", "settings")
def _():
    return P(diamond(24, 24, 9), fill=True) + "".join(P(f"M{pt(24,24,13,a)[0]:.2f} {pt(24,24,13,a)[1]:.2f} L{pt(24,24,19,a)[0]:.2f} {pt(24,24,19,a)[1]:.2f}", w=3) for a in range(0, 360, 45))
@icon("subtitles", "settings")
def _():
    return P(chamfer_rect(5, 10, 38, 28, 5), w=3) + P("M11 26 H20 M24 26 H37 M11 32 H30", w=3)

# ---------------- gameplay HUD ----------------
@icon("ammo", "gameplay")
def _():
    out = ""
    for x in (10, 21, 32):
        out += P(f"M{x} 14 L{x+3} 9 L{x+6} 14 V39 H{x} Z", fill=True)
    return out
@icon("cooldown", "gameplay")
def _():
    out = ""
    for i in range(8):
        a0 = -90 + i * 45 + 4; a1 = a0 + 37
        out += P(arc(24, 24, 17, a0, a1), w=5, op=1.0 if i < 5 else 0.3)
    return out + P("M26 14 L19 25 H24 L22 34 L29 23 H24 Z", fill=True)
@icon("reticle", "gameplay")
def _():
    return circ(24, 24, 14) + P("M24 3 V14 M24 34 V45 M3 24 H14 M34 24 H45", w=3) + circ(24, 24, 2.5, fill=True)
@icon("trajectory", "gameplay")
def _():
    d = []
    for i, t in enumerate([0.0, 0.17, 0.34, 0.51, 0.68]):
        x = 6 + t * 40; y = 40 - 52 * t + 44 * t * t
        d.append(circ(round(x, 2), round(y, 2), 2.6 - i * 0.2, fill=True, op=1 - i * 0.12))
    return "".join(d) + P(diamond(39, 30, 5), w=2.5)
@icon("shots_fired", "gameplay")
def _():
    return P(circ_d(32, 24, 7), fill=True) + P("M5 18 H20 M9 24 H22 M5 30 H20", w=3)
@icon("structure_integrity", "gameplay")
def _():
    return (P("M8 34 H40 V42 H8 Z", fill=True) + P("M12 20 H22 V32 H12 Z M26 20 H36 V32 H26 Z", fill=True)
            + P("M10 8 H38 V18 H10 Z", w=2.5) + P("M24 8 L21 13 L26 15 L23 18", w=2))
@icon("blast_radius", "gameplay")
def _():
    return circ(24, 24, 18, w=2, op=0.5) + circ(24, 24, 11, w=2.5) + P(poly(star_pts(24, 24, 7, 3, n=6)), fill=True)
@icon("weapon_swap", "gameplay")
def _():
    return P("M8 16 H36", w=3) + P("M32 9 L40 16 L32 23 Z", fill=True) + P("M40 32 H12", w=3) + P("M16 25 L8 32 L16 39 Z", fill=True)
@icon("zoom", "gameplay")
def _():
    return circ(20, 20, 12) + P("M29 29 L42 42", w=4.5) + P("M14 20 H26 M20 14 V26", w=2.5)
@icon("camera_pan", "gameplay")
def _():
    return P("M24 4 L30 11 H18 Z M24 44 L18 37 H30 Z M4 24 L11 18 V30 Z M44 24 L37 30 V18 Z", fill=True) + P(diamond(24, 24, 5), fill=True)
@icon("operative", "gameplay")
def _():
    return P(hood(24, 4, 30, 30), fill=True) + P("M17 24 H31 L29 28 H19 Z", fill=True).replace('fill="#fff"', 'fill="#000"') + P("M8 44 C10 36 16 33 24 33 C32 33 38 36 40 44 Z", fill=True)

# ---------------- meta / social / Frontlines ----------------
@icon("leaderboard", "meta")
def _():
    return P("M18 16 H30 V42 H18 Z", fill=True) + P("M5 26 H16 V42 H5 Z M32 22 H43 V42 H32 Z", fill=True, op=0.75) + P(diamond(24, 8, 4), fill=True)
@icon("profile", "meta")
def _():
    return I["operative"]
@icon("friends", "meta")
def _():
    return (P(hood(15, 8, 20, 20), fill=True, op=0.6) + P("M2 42 C3 35 8 32 15 32 C18 32 20 33 21 34 C17 36 14 39 13 42 Z", fill=True, op=0.6)
            + P(hood(31, 6, 24, 24), fill=True) + P("M24 21 H38 L36.5 24 H25.5 Z", fill=True).replace('fill="#fff"', 'fill="#000"')
            + P("M16 44 C18 37 24 34 31 34 C38 34 44 37 46 44 Z", fill=True))
@icon("frontlines", "meta")
def _():
    # defended institution (left block) versus incoming attack chevrons: asymmetric build-and-demolish
    return (P("M5 14 H19 V42 H5 Z", fill=True) + P("M9 8 H15 V14 H9 Z", fill=True)
            + P("M25 15 L33 24 L25 33", w=3.5) + P("M34 15 L42 24 L34 33", w=3.5, op=0.6))
@icon("institution_builder", "meta")
def _():
    return (P("M6 42 H42", w=3) + P("M9 26 H21 V39 H9 Z M27 30 H39 V39 H27 Z", fill=True)
            + P("M12 12 H22 V23 H12 Z", w=2.5).replace('stroke-width="2.5"', 'stroke-width="2.5" stroke-dasharray="3 2"')
            + P("M33 9 V23 M26 16 H40", w=3))
@icon("attack_report", "meta")
def _():
    return (P(chamfer_rect(8, 5, 26, 38, 6), w=2.5) + P("M14 14 H28 M14 20 H24", w=2.5)
            + P(poly(star_pts(34, 33, 11, 4.5, n=7)), fill=True))
@icon("achievement", "meta")
def _():
    return P("M16 28 L12 44 L20 40 L24 46 L26 30 M32 28 L36 44 L28 40", w=2.5) + P(diamond(24, 17, 14), fill=True) + P(diamond(24, 17, 6), fill=True).replace('fill="#fff"', 'fill="#000"')
@icon("share", "meta")
def _():
    return circ(36, 11, 5, fill=True) + circ(12, 24, 5, fill=True) + circ(36, 37, 5, fill=True) + P("M16 22 L32 13 M16 26 L32 35", w=3)
@icon("weekly_challenge", "meta")
def _():
    return P(chamfer_rect(6, 9, 36, 33, 5), w=3) + P("M14 4 V13 M34 4 V13", w=3) + P(diamond(24, 28, 7), fill=True)

# ---------------- chapter emblems ----------------
@icon("chapter_helix", "chapters")
def _():
    # AI server lattice: hexagonal housing with three compute bars and a core node
    return P(hexagon(24, 24, 20), w=3) + P("M14 15 H34 V19 H14 Z M14 22 H34 V26 H14 Z M14 29 H34 V33 H14 Z", fill=True, op=0.9) + P("M30 14.5 H34 V19.5 H30 Z", fill=True).replace('fill="#fff"', 'fill="#000"')
@icon("chapter_vita", "chapters")
def _():
    # sealed containment vessel: capsule within a chamfered ring, a single suspended cell
    return P(chamfer_rect(6, 6, 36, 36, 9), w=2.5) + P("M18 11 H30 V33 A6 6 0 0 1 18 33 Z", w=3) + circ(24, 30, 3.5, fill=True) + P("M16 11 H32", w=3)
@icon("chapter_nova_grid", "chapters")
def _():
    # containment ring with three conductors and an energy bolt
    return circ(24, 24, 19, w=3) + P("M24 5 V12 M7.5 33.5 L13.6 30 M40.5 33.5 L34.4 30", w=3) + P("M27 13 L18 26 H24 L21 36 L31 22 H25 Z", fill=True)
@icon("chapter_civitas", "chapters")
def _():
    # surveillance aperture: lens ring with iris blades
    out = P("M3 24 C10 12 38 12 45 24 C38 36 10 36 3 24 Z", w=3) + circ(24, 24, 8.5, fill=True)
    return out + circ(24, 24, 3.2, fill=True).replace('fill="#fff"', 'fill="#000"')
@icon("chapter_meridian", "chapters")
def _():
    # convergence: displaced diamond (brand) inside an orbit with a vertical meridian
    return (circ(24, 24, 20, w=2, op=0.6) + P("M24 2 V46", w=2)
            + P("M22.5 10 L22.5 38 L8.5 24 Z", fill=True) + P("M25.5 6 L39.5 20 L25.5 34 Z", fill=True))

import re
def knockout(name, body):
    """Elements authored with fill="#000" become true transparent cut-outs via a mask."""
    ko = re.findall(r'<(?:path|circle|rect)[^>]*(?:fill|stroke)="#000"[^>]*/>', body)
    if not ko:
        return (f'<g id="{name}">{body}</g>',)
    pos = body
    for k in ko:
        pos = pos.replace(k, "")
    m = "".join(ko)
    defs = f'<mask id="ko" maskUnits="userSpaceOnUse" x="0" y="0" width="48" height="48"><rect width="48" height="48" fill="#fff"/>{m}</mask>'
    return (f'<g id="{name}" mask="url(#ko)">{pos}</g>', defs)

if __name__ == "__main__":
    out_svg = os.path.join(UI, "icons", "svg")
    HERO = {"weapons", "chapters", "upgrades"}
    index = []
    for name, body in I.items():
        if not body:
            raise SystemExit(f"empty icon {name}")
        stem = f"gam_icn_{name}_a"
        svg = svg_doc(48, 48, *knockout(name, body))
        p = os.path.join(out_svg, f"{stem}.svg"); write(p, svg)
        render(p, os.path.join(UI, "icons", "png_1x", f"{stem}.png"), width=64)
        render(p, os.path.join(UI, "icons", "png_2x", f"{stem}.png"), width=128)
        if cat[name] in HERO:
            render(p, os.path.join(UI, "icons", "png_hero_256", f"{stem}.png"), width=256)
        index.append({"id": f"GAM-ICN-{name.upper()}-A", "name": name, "file": stem, "group": cat[name], "hero": cat[name] in HERO})
    with open(os.path.join(UI, "icons", "icon_index.json"), "w") as f:
        json.dump({"grid_units": 48, "stroke_units": SW, "base_px": 64, "files": {"svg": "svg/<file>.svg", "1x": "png_1x/<file>.png (64)", "2x": "png_2x/<file>.png (128)", "hero": "png_hero_256/<file>.png (256, hero groups only)"},
                   "tint": "white source; tint in Godot with modulate or theme colours", "icons": index}, f, indent=1)
    print(len(I), "icons")
