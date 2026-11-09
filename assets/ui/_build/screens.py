"""Screen layout mock-ups (1280x720 base) built from the kit generators and icon set.

All copy is placeholder text and each screen carries a visible MOCK tag. Text stays as live <text>
layers in the SVG source so it can be edited; in game every string is a Godot Label.
Run: python screens.py
"""
import os, sys, re, json, math
sys.path.insert(0, os.path.dirname(__file__))
import kit
from kit import chamfer
from svgkit import write, render, svg_doc
from tokens import UI, C, CHAPTERS, TIERS, ROOT
from icons import I as ICONS

OUT = os.path.join(UI, "screens")
BG = {"menu": "../../backgrounds/ui_bg_main_menu_1280x720.webp", "loading": "../../backgrounds/ui_bg_loading_1280x720.webp",
      "concept": "../../../environments/concepts/sv04_helix_gameplay_styleframe.webp",
      "greybox": "../../../docs/previews/baseline_harness_helix_01_greybox.webp"}

class S:
    def __init__(self, name, bg=None, tint=0.0, title=None):
        self.name = name; self.defs = []; self.body = []; self.n = 0
        if bg:
            self.body.append(f'<image href="{BG[bg]}" x="0" y="0" width="1280" height="720" preserveAspectRatio="xMidYMid slice"/>')
            if tint: self.body.append(f'<rect width="1280" height="720" fill="#05080B" fill-opacity="{tint}"/>')
        else:
            self.body.append('<rect width="1280" height="720" fill="url(#bgv)"/>')
            self.defs.append(f'<radialGradient id="bgv" cx="60%" cy="35%" r="85%"><stop offset="0" stop-color="#121C25"/><stop offset="1" stop-color="{C["void"]}"/></radialGradient>')
    def add(self, frag):
        if isinstance(frag, tuple):
            d, s = frag[0], frag[1]
            if d: self.defs.append(d)
            self.body.append(s)
        else:
            self.body.append(frag)
    def text(self, x, y, t, role="body", color=None, anchor="start", op=1.0, size=None, weight=None, track=None):
        R = {"display": ("Chakra Petch", 700, 44, 4), "title": ("Chakra Petch", 600, 32, 2), "heading": ("Chakra Petch", 600, 24, 1.5),
             "caps": ("Chakra Petch", 600, 16, 3), "caps_s": ("Chakra Petch", 600, 14, 2.5), "body": ("Barlow", 500, 20, 0), "body_s": ("Barlow", 500, 18, 0),
             "num_l": ("Chakra Petch", 700, 40, 1), "num": ("Chakra Petch", 600, 22, 0.5), "btn": ("Chakra Petch", 600, 20, 2.5)}[role]
        fam, wt, sz, tr = R
        sz = size or sz; wt = weight or wt; tr = tr if track is None else track
        color = color or C["text"]
        t = t.replace("&", "&amp;")
        self.body.append(f'<text x="{x}" y="{y}" font-family="{fam}" font-weight="{wt}" font-size="{sz}" letter-spacing="{tr}" fill="{color}" fill-opacity="{op}" text-anchor="{anchor}">{t}</text>')
    def icon(self, name, x, y, size=32, color=None, op=1.0):
        body = ICONS[name]
        ko = re.findall(r'<(?:path|circle|rect)[^>]*(?:fill|stroke)="#000"[^>]*/>', body)
        pos = body
        for k in ko: pos = pos.replace(k, "")
        col = color or C["text"]
        pos = pos.replace("#fff", col)
        s = size / 48
        if ko:
            self.n += 1; mid = f"ko_{self.name}_{self.n}"
            self.defs.append(f'<mask id="{mid}" maskUnits="userSpaceOnUse" x="0" y="0" width="48" height="48"><rect width="48" height="48" fill="#fff"/>{"".join(ko)}</mask>')
            self.body.append(f'<g transform="translate({x},{y}) scale({s:.4f})" opacity="{op}"><g mask="url(#{mid})">{pos}</g></g>')
        else:
            self.body.append(f'<g transform="translate({x},{y}) scale({s:.4f})" opacity="{op}">{pos}</g>')
    def button(self, x, y, w, h, label, kind="secondary", state="normal", icon=None):
        d, s, ink = kit.button(x, y, w, h, kind, state)
        self.add((d, s))
        tx = x + w / 2
        if icon:
            self.icon(icon, x + 18, y + h / 2 - 12, 24, ink)
            self.text(x + 54, y + h / 2 + 7, label, "btn", ink)
        else:
            self.text(tx, y + h / 2 + 7, label, "btn", ink, anchor="middle")
    def icon_btn(self, x, y, icon, state="normal", size=64):
        d, s, ink = kit.icon_button(x, y, size, state)
        self.add((d, s)); self.icon(icon, x + size / 2 - 16, y + size / 2 - 16, 32, ink)
    def chip(self, x, y, w, h, icon=None, label="", color=None):
        self.add(kit.chip(x, y, w, h))
        if icon: self.icon(icon, x + 10, y + h / 2 - 11, 22, color)
        self.text(x + (40 if icon else 14), y + h / 2 + 7, label, "num", C["text"], size=20)
    def mock_tag(self):
        self.body.append(f'<g id="mock_tag"><path d="{chamfer(12, 692, 200, 20, 5)}" fill="{C["amber"]}" fill-opacity="0.92"/>'
                         f'<text x="112" y="706" font-family="Chakra Petch" font-weight="700" font-size="12" letter-spacing="2" fill="#140C02" text-anchor="middle">MOCK · PLACEHOLDER</text></g>')
    def save(self):
        self.mock_tag()
        svg = svg_doc(1280, 720, "\n".join(self.body), defs="".join(self.defs))
        p = os.path.join(OUT, "source", f"gam_ui_screen_{self.name}_mock.svg"); write(p, svg)
        from PIL import Image
        for sub, w in (("png_1x", 1280), ("png_2x", 2560)):
            tmp = f"/tmp/_scr_{self.name}_{w}.png"; render(p, tmp, width=w)
            os.makedirs(os.path.join(OUT, sub.replace("png", "webp")), exist_ok=True)
            Image.open(tmp).convert("RGB").save(os.path.join(OUT, sub.replace("png", "webp"), f"gam_ui_screen_{self.name}_mock.webp"), quality=92, method=6)
        return p

def header(s, title, sub=None, back=True, chips=True, accent=C["cyan"]):
    s.add(f'<rect width="1280" height="96" fill="url(#hdr)"/>')
    s.defs.append('<linearGradient id="hdr" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#05080B" stop-opacity="0.85"/><stop offset="1" stop-color="#05080B" stop-opacity="0"/></linearGradient>')
    x0 = 32
    if back:
        s.icon_btn(32, 24, "back"); x0 = 116
    s.text(x0, 58, title.upper(), "title", track=3)
    if sub: s.text(x0, 82, sub, "caps_s", accent)
    if chips:
        s.chip(1000, 32, 120, 44, "research_data", "1,240", C["research"])
        s.icon_btn(1140, 24, "settings") if False else None
        s.chip(1132, 32, 116, 44, "star_full", "38/300", C["star"])

def stars(s, x, y, n, size=22, gap=4):
    for i in range(3):
        s.icon("star_full" if i < n else "star_empty", x + i * (size + gap), y, size, C["star"] if i < n else C["star_empty"])

# ---------------------------------------------------------------- screens
def main_menu():
    s = S("main_menu", "menu")
    s.add('<rect width="1280" height="720" fill="url(#mmL)"/>')
    s.defs.append('<linearGradient id="mmL" x1="0" x2="1"><stop offset="0" stop-color="#05080B" stop-opacity="0.92"/><stop offset="0.45" stop-color="#05080B" stop-opacity="0.35"/><stop offset="0.7" stop-color="#05080B" stop-opacity="0"/></linearGradient>')
    import branding
    svg, (lw, lh) = branding.lockup("horizontal", "colour")
    inner = re.search(r"<defs>(.*?)</defs>\n(.*)\n</svg>", svg, re.S)
    s.defs.append(inner.group(1)); sc = 420 / lw
    s.add(f'<g transform="translate(40,44) scale({sc:.4f})">{inner.group(2)}</g>')
    y = 250
    s.button(64, y, 300, 60, "CONTINUE", "primary", "normal", icon="play")
    s.text(64, y + 84, "CHAPTER I  ·  MISSION 07  ·  REDUNDANCY", "caps_s", C["text_dim"])
    items = [("CAMPAIGN", "chapter_map", "normal"), ("FRONTLINES", "frontlines", "disabled"), ("SETTINGS", "settings", "normal"), ("CREDITS", "credits", "normal")]
    for i, (lab, ic, st) in enumerate(items):
        s.button(64, y + 110 + i * 72, 300, 56, lab, "secondary", "hover" if i == 0 else st, icon=ic)
    s.icon("lock", 330, y + 110 + 72 + 16, 22, C["text_disabled"])
    s.chip(1000, 32, 120, 44, "research_data", "1,240", C["research"])
    s.icon_btn(1184, 24, "profile")
    s.text(1216, 700, "v0.1.0  ·  BUILD MOCK", "caps_s", C["text_faint"], anchor="end")
    return s.save()

def chapter_select():
    s = S("chapter_select")
    header(s, "Campaign", "SELECT AN INTERVENTION")
    keys = list(CHAPTERS); w, h, gap = 224, 440, 16
    x0 = (1280 - (5 * w + 4 * gap)) / 2
    prog = {"helix": (20, 52), "vita": (7, 18), "nova_grid": (0, 0), "civitas": (0, 0), "meridian": (0, 0)}
    for i, k in enumerate(keys):
        ch = CHAPTERS[k]; a = ch["accent"]; x = x0 + i * (w + gap); y = 150
        state = "selected" if k == "vita" else ("locked" if i >= 2 else "normal")
        s.add(kit.chapter_card(x, y, w, h, k, state))
        # emblem plate
        s.add(f'<path d="M{x + w/2} {y + 40} L{x + w/2 + 58} {y + 98} L{x + w/2} {y + 156} L{x + w/2 - 58} {y + 98} Z" fill="{a}" fill-opacity="0.07" stroke="{a}" stroke-opacity="0.5" stroke-width="1.5"/>')
        s.icon(f"chapter_{k}", x + w / 2 - 36, y + 62, 72, a, op=0.45 if state == "locked" else 1)
        s.text(x + w / 2, y + 204, f"CHAPTER {['I','II','III','IV','V'][i]}", "caps", a, anchor="middle")
        title = ch["title"].upper().split(" ")
        lines = [" ".join(title[:2]), " ".join(title[2:])] if len(title) > 2 else [" ".join(title)]
        for j, ln in enumerate(lines):
            s.text(x + w / 2, y + 240 + j * 28, ln, "heading", C["text"] if state != "locked" else C["text_faint"], anchor="middle", size=22)
        s.text(x + w / 2, y + 310, f'{ch["org"]}  ·  {ch["year"]}', "body_s", C["text_dim"], anchor="middle", size=16)
        done, st = prog[k]
        if state == "locked":
            s.icon("lock", x + w / 2 - 14, y + 350, 28, C["text_faint"])
            s.text(x + w / 2, y + 406, "COMPLETE CHAPTER " + ["I", "II", "III", "IV"][i - 1], "caps_s", C["text_faint"], anchor="middle", size=12)
        else:
            s.add(kit.bar_track(x + 24, y + 350, w - 48, 8)); s.add(kit.bar_fill(x + 24, y + 350, (w - 48) * done / 20, 8, a))
            s.text(x + 24, y + 384, f"{done}/20", "num", C["text"], size=18)
            s.icon("star_full", x + w - 92, y + 366, 20, C["star"]); s.text(x + w - 24, y + 384, f"{st}/60", "num", C["text"], anchor="end", size=18)
    s.button(1280 - 64 - 260, 612, 260, 56, "OPEN CHAPTER", "primary", "normal", icon="chapter_map")
    return s.save()

LEVEL_NAMES = {"helix": ["Relay Node", "Cold Storage", "Traffic of One", "Load Balance", "The Safety Layer", "Mirror Site", "Redundancy", "Quiet Hours", "Backup Stacks", "Uplink",
                         "Priority One", "Logistics", "Override", "Root Access", "Containment", "Failsafe", "Hot Swap", "Blackout", "Central Logic", "The Machine That Decided"]}
def chapter_map(key):
    ch = CHAPTERS[key]; a = ch["accent"]; n = ch["n"]
    s = S(f"chapter_map_0{n}_{key}")
    # chapter-tinted backdrop: faint grid + accent haze
    s.defs.append(f'<radialGradient id="haze" cx="42%" cy="55%" r="60%"><stop offset="0" stop-color="{a}" stop-opacity="0.10"/><stop offset="1" stop-color="{a}" stop-opacity="0"/></radialGradient>'
                  f'<pattern id="grid" width="40" height="40" patternUnits="userSpaceOnUse"><path d="M40 0 H0 V40" fill="none" stroke="#FFFFFF" stroke-opacity="0.035" stroke-width="1"/></pattern>')
    s.add('<rect width="1280" height="720" fill="url(#grid)"/><rect width="1280" height="720" fill="url(#haze)"/>')
    header(s, ch["title"], f'CHAPTER {["I","II","III","IV","V"][n-1]}  ·  {ch["org"].upper()}  ·  {ch["year"]}', accent=a)
    s.icon(f"chapter_{key}", 1280 - 32 - 40 - 268, 30, 40, a) if False else None
    # route: 20 nodes on a serpentine path within x 60..860, y 140..660
    pts = []
    for i in range(20):
        row = i // 5; col = i % 5
        if row % 2: col = 4 - col
        x = 110 + col * 175 + (20 if row % 2 else 0); y = 170 + row * 125 + (12 if col % 2 else 0)
        pts.append((x, y))
    cur = {"helix": 7, "vita": 4, "nova_grid": 0, "civitas": 0, "meridian": 0}[key]
    path = "M" + " L".join(f"{x} {y}" for x, y in pts)
    done_path = "M" + " L".join(f"{x} {y}" for x, y in pts[:cur + 1])
    s.add(f'<path d="{path}" fill="none" stroke="{C["line_solid"]}" stroke-width="2" stroke-dasharray="6 6"/>')
    if cur: s.add(f'<path d="{done_path}" fill="none" stroke="{a}" stroke-opacity="0.8" stroke-width="2.5"/>')
    for i, (x, y) in enumerate(pts):
        lv = (n - 1) * 20 + i + 1
        boss = i == 19
        r = 30 if boss else 24
        if i < cur:
            s.add(f'<path d="M{x} {y - r} L{x + r} {y} L{x} {y + r} L{x - r} {y} Z" fill="{C["bg1"]}" stroke="{a}" stroke-width="2"/>')
            s.text(x, y + 7, f"{lv:02d}", "num", C["text"], anchor="middle", size=18)
            stars(s, x - 31, y + r + 6, 3 - (i % 3 == 2), 18, 4)
        elif i == cur:
            s.add(f'<path d="M{x} {y - r - 9} L{x + r + 9} {y} L{x} {y + r + 9} L{x - r - 9} {y} Z" fill="none" stroke="{a}" stroke-opacity="0.35" stroke-width="1.5"/>')
            s.add(f'<path d="M{x} {y - r} L{x + r} {y} L{x} {y + r} L{x - r} {y} Z" fill="{a}"/>')
            s.text(x, y + 7, f"{lv:02d}", "num", C["ink"], anchor="middle", size=18, weight=700)
        else:
            s.add(f'<path d="M{x} {y - r} L{x + r} {y} L{x} {y + r} L{x - r} {y} Z" fill="#0A1015" stroke="{C["line_solid"]}" stroke-width="1.5"/>')
            if boss:
                s.icon("critical_asset", x - 14, y - 14, 28, C["critical"], op=0.8)
            else:
                s.icon("lock", x - 10, y - 10, 20, C["text_faint"])
    # mission card
    px, py, pw, ph = 900, 132, 348, 556
    s.add(kit.panel(px, py, pw, ph, 14, "main", accent=a))
    lvl = (n - 1) * 20 + cur + 1
    name = LEVEL_NAMES.get(key, ["Mission"] * 20)[cur] if key == "helix" else "Mission title"
    s.text(px + 28, py + 48, f"MISSION {lvl:02d}", "caps", a)
    s.text(px + 28, py + 86, name.upper(), "title", size=28)
    s.add(kit.divider(px + 28, py + 108, pw - 56))
    s.text(px + 28, py + 144, "Placeholder briefing line one for", "body_s", C["text_dim"])
    s.text(px + 28, py + 168, "the selected mission, two lines.", "body_s", C["text_dim"])
    rows = [("critical_asset", "Primary", "Destroy the critical asset", C["critical"]), ("objective_optional", "Optional", "Optional objective text", C["text_dim"]), ("max_shots", "Optional", "Finish within 8 shots", C["text_dim"])]
    for j, (ic, k2, t, col) in enumerate(rows):
        yy = py + 214 + j * 52
        s.icon(ic, px + 28, yy - 4, 28, col); s.text(px + 68, yy + 6, k2.upper(), "caps_s", col, size=12); s.text(px + 68, yy + 28, t, "body_s", C["text"], size=17)
    s.add(kit.divider(px + 28, py + 380, pw - 56))
    s.icon("shots_fired", px + 28, py + 400, 24, C["text_dim"]); s.text(px + 60, py + 420, "REC. SHOTS  4", "caps_s", C["text_dim"])
    s.icon("time_limit", px + 190, py + 400, 24, C["text_dim"]); s.text(px + 222, py + 420, "TARGET  1:15", "caps_s", C["text_dim"])
    stars(s, px + 28, py + 448, 0, 26, 6); s.text(px + pw - 28, py + 470, "BEST  --", "caps_s", C["text_faint"], anchor="end")
    s.button(px + 28, py + ph - 84, pw - 56, 60, "BRIEFING", "primary", "normal", icon="intel_briefing")
    return s.save()

def mission_select():
    s = S("mission_briefing", "concept", tint=0.72)
    header(s, "Relay Node", "MISSION 01  ·  HELIX SYSTEMS  ·  2089")
    s.add(kit.panel(32, 120, 560, 568, 14, "main"))
    s.text(64, 168, "BRIEFING", "caps", C["cyan"])
    for j, ln in enumerate(["Placeholder briefing copy. The coding agent fills", "this from the mission data at runtime. Two to four", "lines at body size stay readable on a phone."]):
        s.text(64, 206 + j * 30, ln, "body", C["text"])
    s.add(kit.divider(64, 310, 496))
    s.text(64, 350, "OBJECTIVES", "caps", C["cyan"])
    rows = [("critical_asset", "PRIMARY", "Destroy the critical asset", C["critical"]), ("destroy_components", "OPTIONAL", "Optional objective one", C["text_dim"]), ("objective_optional", "OPTIONAL", "Optional objective two", C["text_dim"]), ("max_shots", "OPTIONAL", "Finish within 8 shots", C["text_dim"])]
    for j, (ic, k2, t, col) in enumerate(rows):
        yy = 384 + j * 60
        s.icon(ic, 64, yy, 32, col); s.text(112, yy + 12, k2, "caps_s", col, size=12); s.text(112, yy + 34, t, "body", C["text"])
    s.text(64, 652, "REWARD", "caps_s", C["text_dim"]); s.icon("research_data", 150, 634, 24, C["research"]); s.text(182, 653, "+20", "num", C["research"])
    s.icon("mission_points", 260, 634, 24, C["text"]); s.text(292, 653, "1,000", "num", C["text"])
    # loadout
    s.add(kit.panel(624, 120, 624, 420, 14, "inset"))
    s.text(656, 168, "LOADOUT", "caps", C["cyan"])
    for j, (wid, nm, ammo, col) in enumerate([("weapon_kinetic_accelerator", "Kinetic Accelerator", "14", C["cyan"]), ("weapon_breach_charge", "Breach Charge", "3", C["amber"])]):
        x = 656 + j * 284
        s.add(kit.weapon_slot(x, 196, 268, 300, "selected" if j == 0 else "normal", col))
        s.icon(wid, x + 70, 222, 128, C["text"])
        s.text(x + 24, 390, nm.upper(), "heading", size=20)
        s.text(x + 24, 418, "DIRECT" if j == 0 else "LOBBED  ·  AREA", "caps_s", C["text_dim"], size=12)
        for k in range(min(int(ammo), 14)):
            s.add(kit.pip(x + 24 + k * (16 if j == 0 else 24), 440, "kinetic" if j == 0 else "breach", "full"))
        s.text(x + 244, 460, f"×{ammo}", "num", C["text"], anchor="end", size=20)
    s.button(624, 568, 300, 60, "WEAPON TECH", "secondary", "normal", icon="upgrade_impact_energy")
    s.button(948, 568, 300, 60, "DEPLOY", "primary", "normal", icon="play")
    return s.save()

def hud(bgkey):
    s = S(f"gameplay_hud_{'greybox' if bgkey == 'greybox' else 'concept'}", bgkey)
    # top-left objectives (matches current code placement)
    s.add(kit.panel(24, 24, 330, 150, 12, "inset"))
    s.icon("critical_asset", 40, 40, 26, C["critical"]); s.text(76, 59, "Destroy the critical asset", "body", C["text"], size=19)
    for j, (t, done) in enumerate([("Optional objective one", True), ("Optional objective two", False), ("Finish within 8 shots", False)]):
        yy = 84 + j * 28
        s.icon("objective_complete" if done else "objective_optional", 42, yy, 22, C["success"] if done else C["text_dim"])
        s.text(76, yy + 17, t, "body_s", C["text_dim"] if not done else C["success"], size=17)
    # top-centre shots / time
    s.add(kit.chip(486, 24, 308, 48))
    s.icon("shots_fired", 502, 36, 24, C["text_dim"]); s.text(534, 56, "SHOTS 2 / 4", "num", size=20)
    s.add('<rect x="650" y="36" width="1" height="24" fill="#3D5061"/>')
    s.icon("time_limit", 664, 36, 24, C["text_dim"]); s.text(696, 56, "0:41 / 1:15", "num", size=20)
    # top-right
    s.icon_btn(1112, 24, "retry"); s.icon_btn(1192, 24, "pause")
    # critical marker over the AI core
    cx, cy = (805, 246) if bgkey == "greybox" else (772, 262)
    s.add(kit.critical_marker(cx, cy, 104))
    # trajectory + reticle
    if bgkey == "greybox":
        ox, oy, tx, ty = 196, 432, 792, 250
    else:
        ox, oy, tx, ty = 270, 338, 742, 268
    for i in range(1, 12):
        t = i / 12
        x = ox + (tx - ox) * t; y = oy + (ty - oy) * t - 60 * math.sin(math.pi * t) * 0.6
        s.add(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{4.5 - t*1.5:.2f}" fill="#FFFFFF" fill-opacity="{0.9 - t*0.5:.2f}"/>')
    s.add(kit.aim_reticle(tx, ty, 44))
    # damage numbers (style demo)
    s.text(cx + 66, cy - 26, "-135", "num", C["text"], size=30, weight=700)
    s.text(cx + 70, cy - 4, "CRITICAL", "caps_s", C["critical"], size=12)
    # bottom-right weapon selector + cooldown
    for j, (wid, nm, ammo, mx, col, st) in enumerate([("weapon_kinetic_accelerator", "KINETIC", 9, 14, C["cyan"], "selected"), ("weapon_breach_charge", "BREACH", 2, 3, C["amber"], "normal")]):
        x = 900 + j * 188
        s.add(kit.weapon_slot(x, 586, 176, 110, st, col))
        s.icon(wid, x + 14, 600, 56, C["text"] if st == "selected" else C["text_dim"])
        s.text(x + 162, 624, nm, "caps_s", C["text"], anchor="end", size=13)
        s.text(x + 162, 652, f"{ammo}", "num_l", C["text"], anchor="end", size=30)
        for k in range(mx if mx <= 3 else 0):
            s.add(kit.pip(x + 16 + k * 22, 664, "breach", "full" if k < ammo else "empty"))
        if mx > 3:
            s.add(kit.bar_track(x + 16, 670, 100, 8)); s.add(kit.bar_fill(x + 16, 670, 100 * ammo / mx, 8, col, segments=True))
    # cooldown ring on selected weapon
    d, ringu = kit.ring(1042, 548, 22, 5, "under"); s.add(ringu)
    s.add(f'<path d="M1042 526 A22 22 0 1 1 1020.1 550.3" fill="none" stroke="{C["cyan"]}" stroke-width="5"/>')
    s.text(1042, 555, "0.4", "num", C["text"], anchor="middle", size=15)
    # hint line
    s.text(640, 690, "Hint line placeholder: touch the structure, release to fire", "body_s", C["text_dim"], anchor="middle", size=17)
    return s.save()

def pause():
    s = S("pause", "greybox", tint=0.0)
    s.add(kit.scrim(1280, 720))
    s.add(kit.panel(440, 150, 400, 420, 14, "modal"))
    s.text(640, 214, "PAUSED", "title", anchor="middle", track=6)
    s.text(640, 244, "MISSION 01  ·  RELAY NODE", "caps_s", C["text_dim"], anchor="middle")
    for j, (lab, ic, kind) in enumerate([("RESUME", "play", "primary"), ("RESTART", "retry", "secondary"), ("SETTINGS", "settings", "secondary"), ("ABORT MISSION", "close", "danger")]):
        s.button(480, 276 + j * 70, 320, 56, lab, kind, "normal", icon=ic)
    s.icon_btn(500, 600, "sound_on"); s.icon_btn(608, 600, "music_on"); s.icon_btn(716, 600, "vibration")
    return s.save()

def weapon_select():
    s = S("weapon_selection", "concept", tint=0.78)
    header(s, "Loadout", "CHOOSE WEAPONS FOR THIS MISSION  ·  2 SLOTS")
    weapons = [("weapon_kinetic_accelerator", "Kinetic Accelerator", "I", C["cyan"], "equipped"), ("weapon_breach_charge", "Breach Charge", "I", C["amber"], "equipped"),
               ("weapon_penetrator", "Penetrator", "II", C["cyan"], "locked"), ("weapon_pulse_cannon", "Pulse Cannon", "III", C["cyan"], "locked"),
               ("weapon_disruptor", "Disruptor", "IV", C["cyan"], "locked"), ("weapon_temporal_lance", "Temporal Lance", "V", C["cyan"], "locked")]
    for i, (wid, nm, ch, col, st) in enumerate(weapons):
        x = 32 + (i % 3) * 196; y = 124 + (i // 3) * 276
        s.add(kit.weapon_slot(x, y, 180, 260, "selected" if i == 0 else "normal", col))
        s.icon(wid, x + 26, y + 26, 128, C["text"] if st != "locked" else C["text_faint"])
        s.text(x + 20, y + 186, nm.upper(), "heading", C["text"] if st != "locked" else C["text_faint"], size=14 if len(nm) > 14 else 16, track=1)
        if st == "locked":
            s.icon("lock", x + 20, y + 206, 20, C["text_faint"]); s.text(x + 48, y + 222, f"CHAPTER {ch}", "caps_s", C["text_faint"], size=12)
        else:
            s.icon("check", x + 20, y + 206, 20, C["success"]); s.text(x + 48, y + 222, "EQUIPPED", "caps_s", C["success"], size=12)
    # detail panel
    s.add(kit.panel(632, 124, 616, 536, 14, "main"))
    s.icon("weapon_kinetic_accelerator", 664, 140, 200, C["text"])
    s.text(880, 196, "KINETIC ACCELERATOR", "title", size=26)
    s.text(880, 226, "DIRECT FIRE  ·  ELECTROMAGNETIC", "caps_s", C["cyan"], size=13)
    for j, ln in enumerate(["Placeholder weapon description. High-velocity", "slug for precise strikes on supports and cores."]):
        s.text(880, 262 + j * 26, ln, "body_s", C["text_dim"], size=17)
    stats = [("IMPACT", 0.55), ("PENETRATION", 0.1), ("BLAST", 0.0), ("COOLDOWN", 0.7), ("AMMUNITION", 0.8)]
    for j, (lab, v) in enumerate(stats):
        yy = 372 + j * 44
        s.text(664, yy + 6, lab, "caps_s", C["text_dim"], size=13)
        s.add(kit.bar_track(820, yy - 6, 300, 10)); 
        if v: s.add(kit.bar_fill(820, yy - 6, 300 * v, 10, C["cyan"], segments=True))
        s.text(1216, yy + 6, f"{int(v*100)}", "num", C["text"], anchor="end", size=18)
    s.button(664, 600 - 8, 260, 56, "WEAPON TECH", "secondary", "normal", icon="upgrade_impact_energy")
    s.button(956, 600 - 8, 260, 56, "CONFIRM", "primary", "normal", icon="check")
    return s.save()

def upgrades():
    s = S("weapon_tech_upgrades")
    header(s, "Weapon Tech", "SPEND RESEARCH DATA ON UPGRADES")
    # weapon tabs
    for j, (lab, st) in enumerate([("KINETIC ACCELERATOR", "selected"), ("BREACH CHARGE", "normal"), ("PENETRATOR", "disabled")]):
        x = 32 + j * 248
        s.add(kit.tab(x, 108, 240, 48, st)); s.text(x + 120, 139, lab, "caps", C["text"] if st != "disabled" else C["text_disabled"], anchor="middle", size=15)
    s.add(kit.panel(32, 176, 380, 512, 14, "inset"))
    s.icon("weapon_kinetic_accelerator", 70, 214, 300, C["text"])
    s.text(64, 560, "CURRENT TIER", "caps_s", C["text_dim"]); s.add(kit.tier_badge(240, 554, "tier2", 1.0)); s.text(266, 561, "MK II", "num", TIERS["tier2"]["color"], size=18)
    s.text(64, 610, "Placeholder: upgrades make shots", "body_s", C["text_dim"], size=17); s.text(64, 634, "more efficient, never mandatory.", "body_s", C["text_dim"], size=17)
    ups = [("upgrade_impact_energy", "IMPACT ENERGY", "+15% / +30% / +50% impact damage", 2), ("upgrade_penetration", "PENETRATION", "+0.1 / +0.2 / +0.3 structural penetration", 1),
           ("upgrade_targeting_assistance", "TARGETING ASSISTANCE", "Longer trajectory preview", 0), ("upgrade_energy_efficiency", "ENERGY EFFICIENCY", "-10% / -20% / -30% cooldown", 3)]
    for j, (ic, nm, desc, lvl) in enumerate(ups):
        y = 176 + j * 128
        s.add(kit.panel(436, y, 812, 112, 12, "main" if j == 0 else "inset"))
        s.icon(ic, 460, y + 28, 56, C["cyan"] if lvl else C["text_dim"])
        s.text(536, y + 44, nm, "heading", size=20); s.text(536, y + 74, desc, "body_s", C["text_dim"], size=17)
        for t in range(3):
            tx = 896 + t * 44
            s.add(kit.tier_badge(tx, y + 56, f"tier{t+1}", 1.1) if t < lvl else (f'<path d="M{tx} {y + 41} L{tx + 15} {y + 56} L{tx} {y + 71} L{tx - 15} {y + 56} Z" fill="#0A1117" stroke="{C["line_solid"]}" stroke-width="1.5"/>'))
        if lvl < 3:
            s.button(1048, y + 30, 176, 52, f"{[30, 60, 100][lvl]}", "primary" if j == 0 else "secondary", "normal" if j != 2 else "normal", icon="research_data")
        else:
            s.text(1136, y + 64, "MAXED", "caps", C["success"], anchor="middle")
    return s.save()

def results(success=True):
    s = S("results_success" if success else "results_failure", "greybox")
    s.add(kit.scrim(1280, 720))
    col = C["success"] if success else C["critical"]
    s.add(kit.panel(300, 70, 680, 600, 16, "modal", accent=col))
    s.icon("objective_complete" if success else "objective_failed", 610, 96, 60, col)
    s.text(640, 196, "MISSION COMPLETE" if success else "MISSION FAILED", "display", anchor="middle", size=40, track=6)
    s.text(640, 228, "CRITICAL ASSET DESTROYED" if success else "CRITICAL ASSET INTACT  ·  AMMUNITION SPENT", "caps_s", col, anchor="middle")
    if success:
        for i in range(3):
            on = i < 2
            x = 640 + (i - 1) * 84 - 30; y = 252 - (8 if i == 1 else 0)
            s.icon("star_full" if on else "star_empty", x, y, 60, C["star"] if on else C["star_empty"])
    rows = [("Critical asset", "500"), ("Destruction", "742"), ("Optional objectives", "300"), ("Shot efficiency", "600"), ("Time", "210")] if success else [("Critical asset", "0"), ("Destruction", "318"), ("Optional objectives", "0")]
    y0 = 350 if success else 290
    for j, (k, v) in enumerate(rows):
        yy = y0 + j * 32
        s.text(360, yy, k, "body", C["text_dim"], size=19); s.text(920, yy, v, "num", C["text"], anchor="end", size=20)
    yy = y0 + len(rows) * 32 + 4
    s.add(kit.divider(360, yy - 18, 560))
    s.icon("mission_points", 360, yy - 6, 28, C["text"]); s.text(400, yy + 16, "MISSION POINTS", "caps", C["text"]); s.text(920, yy + 18, "2,352" if success else "318", "num_l", C["text"], anchor="end", size=32)
    if success:
        s.icon("research_data", 360, yy + 30, 28, C["research"]); s.text(400, yy + 52, "RESEARCH DATA", "caps", C["research"]); s.text(920, yy + 54, "+31", "num_l", C["research"], anchor="end", size=32)
    else:
        s.icon("info", 360, yy + 34, 24, C["text_dim"]); s.text(396, yy + 52, "Placeholder tip: supports carry the deck. Break them first.", "body_s", C["text_dim"], size=17)
    if success:
        s.button(340, 586, 190, 58, "RETRY", "secondary", "normal", icon="retry"); s.button(546, 586, 190, 58, "UPGRADES", "secondary", "normal", icon="upgrade_energy_capacity")
        s.button(752, 586, 190, 58, "NEXT", "primary", "normal", icon="next")
    else:
        s.button(340, 586, 290, 58, "MISSION MAP", "secondary", "normal", icon="chapter_map"); s.button(650, 586, 290, 58, "RETRY", "primary", "normal", icon="retry")
    return s.save()

def settings():
    s = S("settings")
    header(s, "Settings", None, chips=False)
    for j, (lab, st) in enumerate([("AUDIO", "selected"), ("DISPLAY", "normal"), ("CONTROLS", "normal"), ("ACCESSIBILITY", "hover"), ("LANGUAGE", "normal")]):
        x = 116 + j * 200
        s.add(kit.tab(x, 100, 192, 48, st)); s.text(x + 96, 131, lab, "caps", C["text"] if st != "normal" else C["text_dim"], anchor="middle", size=15)
    s.add(kit.panel(116, 172, 1048, 500, 14, "inset"))
    rows = [("music_on", "Music", 0.7), ("sound_on", "Effects", 0.85), ("subtitles", "Narration", 0.6), ("controls_touch", "Interface", 0.5)]
    for j, (ic, lab, v) in enumerate(rows):
        y = 220 + j * 72
        s.icon(ic, 156, y - 16, 32, C["text_dim"]); s.text(204, y + 7, lab, "body", C["text"])
        s.add(kit.bar_track(420, y - 4, 560, 8)); s.add(kit.bar_fill(420, y - 4, 560 * v, 8))
        s.add(kit.slider_grabber(420 + 560 * v, y, "hover" if j == 1 else "normal"))
        s.text(1124, y + 7, f"{int(v*100)}", "num", C["text"], anchor="end")
    trows = [("vibration", "Haptics", "on"), ("subtitles", "Subtitles", "on"), ("accessibility", "Reduce screen shake", "off"), ("brightness", "Reduce flashes", "off_disabled")]
    for j, (ic, lab, st) in enumerate(trows):
        y = 520 + (j // 2) * 64; x = 156 + (j % 2) * 500
        s.icon(ic, x, y - 16, 32, C["text_dim"]); s.text(x + 48, y + 7, lab, "body", C["text"] if "disabled" not in st else C["text_disabled"])
        s.add(kit.toggle(x + 380, y - 16, st))
    return s.save()

def credits():
    s = S("credits", "loading", tint=0.55)
    s.add(kit.panel(340, 60, 600, 600, 16, "modal"))
    import branding
    svg, (lw, lh) = branding.lockup("stacked", "colour")
    inner = re.search(r"<defs>(.*?)</defs>\n(.*)\n</svg>", svg, re.S); s.defs.append(inner.group(1)); sc = 200 / lw
    s.add(f'<g transform="translate({640 - 100},{86}) scale({sc:.4f})">{inner.group(2)}</g>')
    y = 330
    for role, names in [("GAME DESIGN AND DIRECTION", ["Name placeholder"]), ("PROGRAMMING", ["Name placeholder"]), ("ART, UI AND VFX", ["Name placeholder"]), ("MUSIC AND SOUND", ["Name placeholder"]),
                        ("TYPEFACES", ["Chakra Petch by Cadson Demak (SIL OFL 1.1)", "Barlow by Jeremy Tribby (SIL OFL 1.1)"])]:
        s.text(640, y, role, "caps_s", C["cyan"], anchor="middle"); y += 26
        for nm in names:
            s.text(640, y, nm, "body_s", C["text"], anchor="middle", size=17); y += 24
        y += 14
    s.icon_btn(32, 24, "back")
    return s.save()

def loading():
    s = S("loading", "loading")
    s.add('<rect y="520" width="1280" height="200" fill="url(#lf)"/>')
    s.defs.append('<linearGradient id="lf" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#05080B" stop-opacity="0"/><stop offset="1" stop-color="#05080B" stop-opacity="0.9"/></linearGradient>')
    s.text(64, 600, "CHAPTER I  ·  MISSION 02", "caps", C["cyan"])
    s.text(64, 640, "COLD STORAGE", "title")
    s.add(kit.bar_track(64, 664, 520, 6)); s.add(kit.bar_fill(64, 664, 520 * 0.62, 6))
    s.text(1216, 640, "Placeholder tip: energy cells detonate when destroyed.", "body_s", C["text_dim"], anchor="end", size=18)
    s.icon("intel_briefing", 1216 - 520 - 34, 620, 26, C["text_dim"])
    return s.save()

# ---------------- concept-level online / Frontlines layouts
def leaderboards():
    s = S("concept_leaderboards")
    header(s, "Leaderboards", "CONCEPT LAYOUT  ·  ONLINE FEATURE, LATER PHASE")
    for j, (lab, st) in enumerate([("GLOBAL", "selected"), ("FRIENDS", "normal"), ("CHAPTER", "normal"), ("LEVEL", "normal"), ("WEEKLY", "normal"), ("FRONTLINES", "normal")]):
        s.add(kit.tab(32 + j * 168, 104, 160, 44, st)); s.text(32 + j * 168 + 80, 133, lab, "caps", C["text"] if st == "selected" else C["text_dim"], anchor="middle", size=14)
    for j, (lab, st) in enumerate([("STANDARD", "selected"), ("COMPETITIVE", "normal")]):
        s.add(kit.tab(1048 + j * 104, 104, 100, 44, st)); s.text(1048 + j * 104 + 50, 133, lab, "caps_s", C["text"] if st == "selected" else C["text_dim"], anchor="middle", size=11)
    s.add(kit.panel(32, 168, 1216, 520, 14, "inset"))
    s.text(72, 206, "RANK", "caps_s", C["text_faint"]); s.text(180, 206, "OPERATIVE", "caps_s", C["text_faint"]); s.text(860, 206, "SHOTS", "caps_s", C["text_faint"], anchor="end"); s.text(1000, 206, "TIME", "caps_s", C["text_faint"], anchor="end"); s.text(1208, 206, "MISSION POINTS", "caps_s", C["text_faint"], anchor="end")
    for j in range(8):
        y = 226 + j * 54; me = j == 5
        if me: s.add(f'<path d="{chamfer(44, y, 1192, 46, 6)}" fill="{C["cyan"]}" fill-opacity="0.10" stroke="{C["cyan"]}" stroke-opacity="0.6"/>')
        elif j % 2 == 0: s.add(f'<rect x="44" y="{y}" width="1192" height="46" fill="#FFFFFF" fill-opacity="0.02"/>')
        rk = [1, 2, 3, 4, 5, 214, 215, 216][j]
        if rk <= 3: s.icon("trophy", 66, y + 10, 26, [C["star"], "#C9D3DC", "#C98B5A"][rk - 1])
        else: s.text(80, y + 30, f"{rk}", "num", C["text_dim"], anchor="middle", size=18)
        s.icon("operative", 180, y + 8, 30, C["cyan"] if me else C["text_dim"]); s.text(224, y + 30, "You (mock)" if me else f"Operative_{rk:04d}", "body", C["text"] if me else C["text_dim"], size=18)
        s.text(860, y + 30, f"{3 + j % 3}", "num", C["text"], anchor="end", size=18); s.text(1000, y + 30, f"0:{40 + j * 3:02d}", "num", C["text"], anchor="end", size=18)
        s.text(1208, y + 30, f"{4120 - j * 160:,}", "num", C["text"], anchor="end", size=18)
    return s.save()

def profile():
    s = S("concept_player_profile")
    header(s, "Operative Profile", "CONCEPT LAYOUT  ·  ONLINE FEATURE, LATER PHASE")
    s.add(kit.panel(32, 120, 400, 568, 14, "main"))
    s.add(f'<path d="M232 156 L332 256 L232 356 L132 256 Z" fill="{C["cyan"]}" fill-opacity="0.06" stroke="{C["cyan"]}" stroke-opacity="0.5" stroke-width="1.5"/>')
    s.icon("operative", 172, 196, 120, C["text"])
    s.text(232, 400, "OPERATIVE_0001", "heading", anchor="middle"); s.text(232, 428, "Display name placeholder", "body_s", C["text_dim"], anchor="middle", size=17)
    for j, (ic, k, v, col) in enumerate([("mission_points", "MISSION POINTS", "48,210", C["text"]), ("research_data", "RESEARCH DATA", "1,240", C["research"]), ("star_full", "STARS", "38 / 300", C["star"])]):
        y = 476 + j * 58
        s.icon(ic, 64, y - 4, 28, col); s.text(104, y + 16, k, "caps_s", C["text_dim"]); s.text(400, y + 18, v, "num", C["text"], anchor="end")
    s.add(kit.panel(456, 120, 792, 260, 14, "inset")); s.text(488, 164, "CAMPAIGN PROGRESS", "caps", C["cyan"])
    for i, k in enumerate(CHAPTERS):
        x = 488 + i * 150; a = CHAPTERS[k]["accent"]; v = [1, 0.35, 0, 0, 0][i]
        s.icon(f"chapter_{k}", x + 40, 190, 56, a if v else C["text_faint"])
        s.add(kit.bar_track(x, 272, 136, 6)); s.add(kit.bar_fill(x, 272, 136 * v, 6, a)) if v else None
        s.text(x + 68, 312, f"{int(v*20)}/20", "num", C["text"] if v else C["text_faint"], anchor="middle", size=18)
    s.add(kit.panel(456, 404, 792, 284, 14, "inset")); s.text(488, 448, "ACHIEVEMENTS", "caps", C["cyan"])
    for i in range(10):
        x = 488 + (i % 5) * 150; y = 472 + (i // 5) * 104
        on = i < 4
        s.icon("achievement", x + 44, y, 56, C["star"] if on else C["text_faint"], op=1 if on else 0.6)
        s.add(f'<rect x="{x + 24}" y="{y + 70}" width="96" height="8" fill="#FFFFFF" fill-opacity="0.08"/>')
    return s.save()

def frontlines():
    s = S("concept_frontlines_hub", "concept", tint=0.8)
    header(s, "Temporal Frontlines", "CONCEPT LAYOUT  ·  ASYNCHRONOUS MODE, LATER PHASE")
    for j, (ic, title, sub, kind) in enumerate([("institution_builder", "BUILD AND DEFEND", "Design your institution", "secondary"), ("frontlines", "ATTACK", "Find an institution", "primary"), ("attack_report", "REPORTS", "2 new attack reports", "secondary")]):
        x = 32 + j * 412
        s.add(kit.panel(x, 124, 392, 380, 14, "main" if j == 1 else "inset"))
        s.add(f'<path d="M{x + 196} 160 L{x + 276} 240 L{x + 196} 320 L{x + 116} 240 Z" fill="{C["cyan"]}" fill-opacity="0.06" stroke="{C["cyan"]}" stroke-opacity="0.4"/>')
        s.icon(ic, x + 148, 192, 96, C["text"])
        s.text(x + 196, 372, title, "heading", anchor="middle"); s.text(x + 196, 402, sub, "body_s", C["text_dim"], anchor="middle", size=17)
        s.button(x + 40, 428, 312, 56, "OPEN", kind, "normal")
    s.add(kit.panel(32, 528, 1216, 160, 14, "inset"))
    s.icon("shield", 64, 560, 40, C["success"]); s.text(120, 580, "INSTITUTION STATUS", "caps", C["text_dim"]); s.text(120, 612, "Recovery shield active  ·  placeholder 6 h", "body", C["text"])
    s.icon("leaderboard", 760, 560, 40, C["text_dim"]); s.text(816, 580, "SEASON RANK", "caps", C["text_dim"]); s.text(816, 612, "Placeholder rank 1,204", "body", C["text"])
    s.text(64, 664, "Budget, snapshot and validation rules follow docs/plan.md revision 5 section 8.", "body_s", C["text_faint"], size=15)
    return s.save()

def builder():
    s = S("concept_institution_builder")
    header(s, "Institution Builder", "CONCEPT LAYOUT  ·  GRID PLACEMENT ON THE 2D PHYSICS PLANE", chips=False)
    # grid area
    s.add(kit.panel(32, 116, 900, 572, 14, "inset"))
    s.defs.append('<pattern id="bg_grid" width="25" height="25" patternUnits="userSpaceOnUse"><path d="M25 0 H0 V25" fill="none" stroke="#3CC8E6" stroke-opacity="0.10" stroke-width="1"/></pattern>')
    s.add('<rect x="48" y="132" width="868" height="500" fill="url(#bg_grid)"/>')
    s.add('<rect x="48" y="620" width="868" height="12" fill="#2A3846"/>')
    # placed components as flat front-face silhouettes
    blocks = [(300, 520, 30, 100, C["steel"]), (360, 540, 40, 80, "#4A6272"), (410, 540, 40, 80, "#4A6272"), (500, 460, 26, 160, C["steel"]), (640, 460, 26, 160, C["steel"]),
              (480, 436, 200, 24, "#5C6E7A"), (560, 376, 60, 60, "#E7EDF2"), (630, 396, 36, 40, C["amber"]), (740, 420, 22, 200, C["steel"]), (716, 396, 70, 24, "#9BC7D8")]
    for x, y, w, h, col in blocks:
        s.add(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{col}" fill-opacity="0.85" stroke="#05080B" stroke-width="1.5"/>')
    s.add(kit.critical_marker(590, 406, 84))
    # ghost placement
    s.add(f'<rect x="800" y="520" width="40" height="100" fill="{C["cyan"]}" fill-opacity="0.18" stroke="{C["cyan"]}" stroke-width="2" stroke-dasharray="6 4"/>')
    s.icon_btn(48, 640 - 8, "replay", size=48) if False else None
    for j, ic in enumerate(["weapon_swap", "repair", "close"]):
        s.icon_btn(64 + j * 76, 112 + 520 - 68 + 0, ic, size=56) if False else None
    # palette
    s.add(kit.panel(956, 116, 292, 572, 14, "main"))
    s.text(980, 156, "COMPONENTS", "caps", C["cyan"]); s.text(1224, 156, "BUDGET 640 / 1000", "caps_s", C["text_dim"], anchor="end", size=11)
    for j, (nm, cost, ic) in enumerate([("Support column", 40, "structure_integrity"), ("Service deck", 60, "structure_integrity"), ("Server rack", 50, "chapter_helix"), ("Power cell", 80, "upgrade_energy_capacity"), ("Blast wall", 90, "shield"), ("Critical core", 0, "critical_asset")]):
        y = 176 + j * 72
        s.add(kit.weapon_slot(980, y, 244, 60, "selected" if j == 2 else "normal"))
        s.icon(ic, 996, y + 14, 32, C["critical"] if "Critical" in nm else C["text"])
        s.text(1040, y + 37, nm, "body_s", C["text"], size=17); s.text(1208, y + 37, f"{cost}", "num", C["text_dim"], anchor="end", size=17)
    s.button(980, 612, 244, 56, "PUBLISH", "primary", "normal", icon="share")
    return s.save()

def attack_report():
    s = S("concept_attack_report")
    header(s, "Attack Report", "CONCEPT LAYOUT  ·  DEFENDER VIEW", chips=False)
    s.add(kit.panel(32, 116, 760, 572, 14, "inset"))
    s.defs.append(f'<linearGradient id="rp" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#16222D"/><stop offset="1" stop-color="#0B1117"/></linearGradient>')
    s.add('<rect x="52" y="136" width="720" height="420" fill="url(#rp)"/>')
    s.text(412, 350, "REPLAY RECONSTRUCTION VIEWPORT", "caps", C["text_faint"], anchor="middle")
    s.add(kit.bar_track(52, 584, 720, 6)); s.add(kit.bar_fill(52, 584, 720 * 0.42, 6))
    for j, t in enumerate([0.12, 0.3, 0.42, 0.7]):
        s.add(f'<path d="M{52 + 720*t} 576 L{58 + 720*t} 570 L{46 + 720*t} 570 Z" fill="{C["amber"]}"/>')
    s.icon_btn(52, 608, "replay", size=56); s.icon_btn(120, 608, "pause", size=56); s.icon_btn(188, 608, "fast_forward", size=56)
    s.add(kit.panel(816, 116, 432, 572, 14, "main", accent=C["critical"]))
    s.text(848, 160, "RESULT", "caps", C["critical"]); s.text(848, 200, "CORE DESTROYED", "title", size=28)
    s.text(848, 230, "Attacker placeholder  ·  2 h ago", "body_s", C["text_dim"], size=17)
    for j, (k, v) in enumerate([("Shots used", "6"), ("Components lost", "11 / 18"), ("Weapons", "Kinetic, Breach"), ("Points lost", "-120")]):
        y = 282 + j * 40
        s.text(848, y, k, "body", C["text_dim"], size=18); s.text(1216, y, v, "num", C["text"], anchor="end", size=18)
    s.add(kit.divider(848, 444, 368)); s.icon("shield", 848, 464, 28, C["success"]); s.text(888, 485, "Recovery shield placeholder", "body_s", C["text"], size=17)
    s.button(848, 540, 368, 56, "REPAIR INSTITUTION", "primary", "normal", icon="repair"); s.button(848, 612, 368, 56, "REVENGE ATTACK", "secondary", "normal", icon="frontlines")
    return s.save()

def all_screens():
    out = [main_menu(), chapter_select()]
    for k in CHAPTERS: out.append(chapter_map(k))
    out += [mission_select(), hud("greybox"), hud("concept"), pause(), weapon_select(), upgrades(), results(True), results(False), settings(), credits(), loading(),
            leaderboards(), profile(), frontlines(), builder(), attack_report()]
    print(len(out), "screens")
    return out

if __name__ == "__main__":
    only = sys.argv[1:] 
    if only:
        for n in only: globals()[n]()
    else:
        all_screens()
