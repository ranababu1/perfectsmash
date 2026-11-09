"""Shared design tokens for Temporal: First Jump UI, branding and previews.

Single source of truth: ui/theme/tfj_theme_spec.json is generated from these values.
Palette rules (see ui/PRODUCTION_NOTES.md): charcoal/graphite base, cyan for interactive and
temporal elements, amber only for weapon energy and danger, red only for critical assets and
security alarms, violet only for Meridian temporal phenomena.
"""
import os

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))  # generated_assets/
UI = os.path.join(ROOT, "ui")
FONTS = os.path.join(ROOT, "fonts")
FONT_DIRS = [os.path.join(FONTS, "chakra_petch"), os.path.join(FONTS, "barlow")]
RESVG = os.environ.get("RESVG", "/workspace/tfj-ui-vfx-tools/resvg")

DISPLAY = "Chakra Petch"   # headings, numerals, logo-derived lettering
BODY = "Barlow"            # body copy, labels, long text

C = {
    # base
    "void": "#05080B",
    "bg0": "#080C10",
    "bg1": "#0D1319",
    "surface": "#111A22",
    "surface_raised": "#172330",
    "surface_hover": "#1D2C3A",
    "surface_pressed": "#0E161E",
    "line": "#2A3846",
    "line_bright": "#40546480",
    "line_solid": "#3D5061",
    "steel": "#7C8C99",
    # text
    "text": "#E7EDF2",
    "text_dim": "#97A7B4",
    "text_faint": "#5D6D7A",
    "text_disabled": "#46525C",
    "ink": "#061015",
    # interactive / temporal
    "cyan": "#3CC8E6",
    "cyan_bright": "#9BEBFA",
    "cyan_deep": "#127A92",
    "cyan_glow": "#3CC8E6",
    # semantic
    "amber": "#F2A23A",       # weapon energy, danger, warnings
    "amber_deep": "#9A5A12",
    "critical": "#FF4D3D",    # critical asset, failure, security alarm
    "critical_deep": "#8A1E16",
    "success": "#6EDDA6",
    "research": "#8FE3F5",    # Research Data currency
    "points": "#E7EDF2",      # Mission Points
    "star": "#F4C766",
    "star_empty": "#2C3946",
}

CHAPTERS = {
    "helix":     {"n": 1, "org": "Helix Systems", "year": 2089, "title": "The Machine That Decided",
                  "accent": "#3CC8E6", "accent2": "#F2A23A", "base": "#0F161C", "levels": [1, 20]},
    "vita":      {"n": 2, "org": "VITA Genomics", "year": 2092, "title": "The Price of Perfection",
                  "accent": "#7FD9A8", "accent2": "#DDEBEA", "base": "#0F1716", "levels": [21, 40]},
    "nova_grid": {"n": 3, "org": "Nova Grid", "year": 2096, "title": "The Energy Beneath",
                  "accent": "#F0A040", "accent2": "#4AA8FF", "base": "#15120F", "levels": [41, 60]},
    "civitas":   {"n": 4, "org": "Civitas", "year": 2100, "title": "The Quiet Cage",
                  "accent": "#8EB6DA", "accent2": "#E5484D", "base": "#11151A", "levels": [61, 80]},
    "meridian":  {"n": 5, "org": "Meridian", "year": 2104, "title": "The Convergence",
                  "accent": "#A592FF", "accent2": "#7FE6F2", "base": "#0B0E12", "levels": [81, 100]},
}

# Upgrade tier tints (base + 3 levels, matching data/weapons.json levels 1-3)
TIERS = {
    "tier0": {"name": "Base",    "color": "#9AA9B5"},
    "tier1": {"name": "Mk I",    "color": "#3CC8E6"},
    "tier2": {"name": "Mk II",   "color": "#5AA9FF"},
    "tier3": {"name": "Mk III",  "color": "#B9F2FF"},
}

# Typography scale for a 1280x720 base canvas (px at 1x). Mobile-first: body never below 18.
TYPE = {
    "display_xl": {"font": DISPLAY, "weight": 700, "size": 64, "tracking": 0.12},
    "display_l":  {"font": DISPLAY, "weight": 600, "size": 44, "tracking": 0.10},
    "title":      {"font": DISPLAY, "weight": 600, "size": 32, "tracking": 0.06},
    "heading":    {"font": DISPLAY, "weight": 600, "size": 26, "tracking": 0.06},
    "label_caps": {"font": DISPLAY, "weight": 600, "size": 18, "tracking": 0.16},
    "body_l":     {"font": BODY, "weight": 500, "size": 24, "tracking": 0.0},
    "body":       {"font": BODY, "weight": 500, "size": 20, "tracking": 0.0},
    "caption":    {"font": BODY, "weight": 500, "size": 18, "tracking": 0.02},
    "numeric_l":  {"font": DISPLAY, "weight": 700, "size": 40, "tracking": 0.02},
    "numeric":    {"font": DISPLAY, "weight": 600, "size": 24, "tracking": 0.02},
    "damage_number": {"font": DISPLAY, "weight": 700, "size": 30, "tracking": 0.0},
}

SPACING = {"xxs": 4, "xs": 8, "s": 12, "m": 16, "l": 24, "xl": 32, "xxl": 48}
SAFE_MARGIN = 32           # px from screen edge at 1x
TOUCH_MIN = 64             # matches UiKit.BUTTON_HEIGHT
CHAMFER = 12               # panel corner cut at 1x
CHAMFER_S = 8
