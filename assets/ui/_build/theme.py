"""Writes ui/theme/tfj_theme_spec.json: a Godot Theme-ready specification (colours, fonts, type
roles, margins, StyleBoxTexture paths and 9-slice margins, per-state font colours, HUD layout,
damage-number LabelSettings and motion). Values are for the 1280x720 base viewport."""
import os, sys, json
sys.path.insert(0, os.path.dirname(__file__))
from tokens import UI, C, CHAPTERS, TIERS, TYPE, SPACING, SAFE_MARGIN, TOUCH_MIN
RES = "res://assets"
kit = {e["name"]: e for e in json.load(open(os.path.join(UI, "kit", "kit_index.json")))["components"]}

def sb(name, content=None, expand=0):
    e = kit[name]
    d = {"type": "StyleBoxTexture", "texture": f"{RES}/ui/kit/png_1x/{e['file']}.png", "texture_margin": e["nine_slice_1x"],
         "texture_2x": f"{RES}/ui/kit/png_2x/{e['file']}.png", "texture_margin_2x": e["nine_slice_2x"],
         "axis_stretch_horizontal": "stretch", "axis_stretch_vertical": "stretch"}
    if content: d["content_margin"] = content
    if expand: d["expand_margin"] = {"left": expand, "top": expand, "right": expand, "bottom": expand}
    return d

FONTS = {
    "display_regular": f"{RES}/fonts/chakra_petch/ChakraPetch-Regular.ttf", "display_medium": f"{RES}/fonts/chakra_petch/ChakraPetch-Medium.ttf",
    "display_semibold": f"{RES}/fonts/chakra_petch/ChakraPetch-SemiBold.ttf", "display_bold": f"{RES}/fonts/chakra_petch/ChakraPetch-Bold.ttf",
    "body_regular": f"{RES}/fonts/barlow/Barlow-Regular.ttf", "body_medium": f"{RES}/fonts/barlow/Barlow-Medium.ttf",
    "body_semibold": f"{RES}/fonts/barlow/Barlow-SemiBold.ttf", "body_bold": f"{RES}/fonts/barlow/Barlow-Bold.ttf",
}
WEIGHT_KEY = {400: "regular", 500: "medium", 600: "semibold", 700: "bold"}

def roles():
    out = {}
    for k, v in TYPE.items():
        fam = "display" if v["font"] == "Chakra Petch" else "body"
        out[k] = {"font": FONTS[f"{fam}_{WEIGHT_KEY[v['weight']]}"], "size": v["size"],
                  "spacing_glyph": round(v["tracking"] * v["size"], 1), "uppercase": fam == "display" and k not in ("numeric", "numeric_l", "damage_number")}
    return out

btn_colours = {
    "primary": {"font_color": C["ink"], "font_hover_color": C["ink"], "font_pressed_color": C["ink"], "font_focus_color": C["ink"], "font_disabled_color": C["text_disabled"], "icon_normal_color": C["ink"]},
    "secondary": {"font_color": C["text"], "font_hover_color": "#FFFFFF", "font_pressed_color": C["cyan_bright"], "font_focus_color": C["text"], "font_disabled_color": C["text_disabled"]},
    "danger": {"font_color": C["text"], "font_hover_color": "#FFFFFF", "font_pressed_color": "#FFB3AA", "font_focus_color": C["text"], "font_disabled_color": C["text_disabled"]},
}

spec = {
    "name": "Temporal: First Jump UI theme",
    "version": 1,
    "base_viewport": [1280, 720],
    "stretch": "canvas_items / expand (project.godot)",
    "notes": [
        "All numbers are 1x base pixels unless a key ends in _2x.",
        "StyleBoxTexture draws texture margins at texel size, so a 2x texture with 2x margins would draw corners twice as large. Use the 1x texture + 1x margins in a StyleBox (default below), or use the resolution-independent StyleBoxFlat equivalents in flat_equivalents (preferred for crisp panels on phones: corner_detail 1 gives the chamfer). The 2x files are for NinePatchRect/TextureRect use where the node is drawn at half scale, and for icons/sprites (TextureRect expand + stretch keep aspect, so 2x stays crisp).",
        "No dynamic text is baked into any texture. Every string is a Label / Button text using these fonts.",
        "Orange/amber is reserved for weapon energy and danger; red for critical assets and failure; cyan for interaction and temporal energy.",
        "Restrained glow: hover states use a 1.5 px halo line, not bloom. Nothing depends on WorldEnvironment glow.",
    ],
    "colors": C,
    "chapter_accents": {k: {"accent": v["accent"], "accent2": v["accent2"], "base": v["base"], "levels": v["levels"]} for k, v in CHAPTERS.items()},
    "upgrade_tiers": TIERS,
    "fonts": FONTS,
    "font_import": {"antialiasing": "grayscale", "hinting": "light", "subpixel_positioning": "auto", "generate_mipmaps": False, "multichannel_signed_distance_field": False},
    "default_font": FONTS["body_medium"], "default_font_size": 20,
    "type_roles": roles(),
    "spacing": SPACING, "safe_margin": SAFE_MARGIN, "touch_target_min": TOUCH_MIN,
    "minimum_readable_size": {"body": 18, "caps_label": 12, "numerals_hud": 20, "note": "never smaller on a 1280x720 base; phones scale up about 1.8x"},
    "theme": {
        "Button": {"styles": {"normal": sb("button_secondary_normal", {"left": 20, "top": 12, "right": 20, "bottom": 12}, 4), "hover": sb("button_secondary_hover", None, 4),
                              "pressed": sb("button_secondary_pressed", None, 4), "disabled": sb("button_secondary_disabled", None, 4), "focus": sb("focus_ring", None, 4)},
                   "colors": btn_colours["secondary"], "font": FONTS["display_semibold"], "font_size": 20, "spacing_glyph": 2.5, "min_height": 56, "icon_max_width": 24, "h_separation": 12},
        "PrimaryButton": {"base_type": "Button", "styles": {s: sb(f"button_primary_{s}", None, 4) for s in ("normal", "hover", "pressed", "disabled")}, "colors": btn_colours["primary"]},
        "DangerButton": {"base_type": "Button", "styles": {s: sb(f"button_danger_{s}", None, 4) for s in ("normal", "hover", "pressed", "disabled")}, "colors": btn_colours["danger"]},
        "IconButton": {"base_type": "Button", "styles": {s: sb(f"button_icon_{s}", None, 4) for s in ("normal", "hover", "pressed", "disabled")}, "min_size": [64, 64], "icon_size": 32},
        "PanelContainer": {"styles": {"panel": sb("panel_main", {"left": 24, "top": 24, "right": 24, "bottom": 24})}},
        "PanelInset": {"base_type": "PanelContainer", "styles": {"panel": sb("panel_inset", {"left": 20, "top": 20, "right": 20, "bottom": 20})}},
        "PanelModal": {"base_type": "PanelContainer", "styles": {"panel": sb("panel_modal", {"left": 32, "top": 32, "right": 32, "bottom": 32})}},
        "PanelHeader": {"base_type": "PanelContainer", "styles": {"panel": sb("panel_header", {"left": 24, "top": 12, "right": 24, "bottom": 12})}},
        "Chip": {"base_type": "PanelContainer", "styles": {"panel": sb("chip", {"left": 14, "top": 8, "right": 14, "bottom": 8})}},
        "TabBar": {"styles": {"tab_unselected": sb("tab_normal"), "tab_hovered": sb("tab_hover"), "tab_selected": sb("tab_selected"), "tab_disabled": sb("tab_disabled")},
                   "colors": {"font_unselected_color": C["text_dim"], "font_hovered_color": C["text"], "font_selected_color": C["text"], "font_disabled_color": C["text_disabled"]},
                   "font": FONTS["display_semibold"], "font_size": 15, "spacing_glyph": 3, "min_tab_height": 48},
        "HSlider": {"styles": {"slider": sb("slider_track"), "grabber_area": sb("slider_fill"), "grabber_area_highlight": sb("slider_fill")},
                    "icons": {"grabber": f"{RES}/ui/kit/png_2x/gam_ui_slider_grabber_normal.png", "grabber_highlight": f"{RES}/ui/kit/png_2x/gam_ui_slider_grabber_hover.png",
                              "grabber_disabled": f"{RES}/ui/kit/png_2x/gam_ui_slider_grabber_disabled.png"}, "icon_display_size_1x": [40, 40], "min_height": 40},
        "CheckButton": {"icons": {"checked": f"{RES}/ui/kit/png_2x/gam_ui_toggle_on.png", "unchecked": f"{RES}/ui/kit/png_2x/gam_ui_toggle_off.png",
                                  "checked_disabled": f"{RES}/ui/kit/png_2x/gam_ui_toggle_on_disabled.png", "unchecked_disabled": f"{RES}/ui/kit/png_2x/gam_ui_toggle_off_disabled.png"},
                        "icon_display_size_1x": [64, 32], "min_height": 56},
        "ProgressBar": {"styles": {"background": sb("progress_track"), "fill": sb("progress_fill_cyan")}, "variants": {"energy": "progress_fill_amber", "integrity": "progress_fill_critical", "success": "progress_fill_success"}, "show_percentage": False, "min_height": 12},
        "TextureProgressBar_Cooldown": {"under": f"{RES}/ui/kit/png_2x/gam_ui_cooldown_ring_under.png", "progress": f"{RES}/ui/kit/png_2x/gam_ui_cooldown_ring_progress.png",
                                         "over": f"{RES}/ui/kit/png_2x/gam_ui_cooldown_ring_over.png", "progress_amber": f"{RES}/ui/kit/png_2x/gam_ui_cooldown_ring_progress_amber.png",
                                         "fill_mode": "FILL_CLOCKWISE (TextureProgressBar.FILL_CLOCKWISE = 4)", "display_size_1x": [96, 96], "value_semantics": "value = remaining cooldown fraction, 1 -> 0"},
        "Label": {"colors": {"font_color": C["text"], "font_shadow_color": "#00000000", "font_outline_color": "#05080BCC"}, "font": FONTS["body_medium"], "font_size": 20},
        "Tooltip": {"styles": {"panel": sb("chip", {"left": 12, "top": 8, "right": 12, "bottom": 8})}, "font_size": 18},
        "ScrimColor": "#05080BB3",
    },
    "flat_equivalents": {
        "note": "StyleBoxFlat values that reproduce the kit shapes without textures. corner radius is applied to top-left and bottom-right only; corner_detail = 1 makes it a straight chamfer.",
        "panel_main": {"bg_color": "#131D26F0", "border_color": "#2C3B48", "border_width": 1, "corner_radius_top_left": 12, "corner_radius_bottom_right": 12, "corner_detail": 1, "anti_aliasing": True, "content_margin": 24, "accent_tick": "draw the 2 px cyan corner tick with a small TextureRect (gam_ui_panel_main 1x corner) or omit"},
        "panel_inset": {"bg_color": "#0B1218EB", "border_color": "#2A3846", "border_width": 1, "corner_radius_top_left": 12, "corner_radius_bottom_right": 12, "corner_detail": 1, "content_margin": 20},
        "panel_modal": {"bg_color": "#141F28F7", "border_color": "#3A4E5E", "border_width": 1, "corner_radius_top_left": 12, "corner_radius_bottom_right": 12, "corner_detail": 1, "content_margin": 32},
        "button_primary": {"normal": {"bg_color": "#3AC1DE", "border_color": "#8FE8F8"}, "hover": {"bg_color": "#52CDE7", "border_color": "#C9F5FD"}, "pressed": {"bg_color": "#2393B0", "border_color": "#5FD4EA"}, "disabled": {"bg_color": "#18232D", "border_color": "#2A3846"},
                           "common": {"border_width": 1, "corner_radius_top_left": 10, "corner_radius_bottom_right": 10, "corner_detail": 1, "content_margin_h": 20, "content_margin_v": 12}},
        "button_secondary": {"normal": {"bg_color": "#15202AEB", "border_color": "#3CC8E68C"}, "hover": {"bg_color": "#1B2A37F2", "border_color": "#9BEBFAF2"}, "pressed": {"bg_color": "#0F1820F2", "border_color": "#3CC8E6CC"}, "disabled": {"bg_color": "#11181FB3", "border_color": "#2A3846CC"},
                             "common": {"border_width": 1, "corner_radius_top_left": 10, "corner_radius_bottom_right": 10, "corner_detail": 1}},
        "button_danger": {"normal": {"bg_color": "#241413F0", "border_color": "#FF4D3DA6"}, "hover": {"bg_color": "#321816F5", "border_color": "#FF8A7E"}, "pressed": {"bg_color": "#1C0F0EF5", "border_color": "#FF4D3DD9"}, "disabled": {"bg_color": "#11181FB3", "border_color": "#2A3846CC"},
                          "common": {"border_width": 1, "corner_radius_top_left": 10, "corner_radius_bottom_right": 10, "corner_detail": 1}},
        "chip": {"bg_color": "#0A1117D1", "border_color": "#3D5061", "border_width": 1, "corner_radius_top_left": 6, "corner_radius_bottom_right": 6, "corner_detail": 1},
        "focus": {"draw_center": False, "border_color": "#9BEBFA", "border_width": 2, "expand_margin": 4, "corner_radius_top_left": 12, "corner_radius_bottom_right": 12, "corner_detail": 1},
    },
    "hud_layout": {
        "note": "matches the current MissionHud placement in code (objectives top-left, shots and time top-centre, retry and pause top-right, weapon cards bottom-right, hint bottom-centre)",
        "objectives_panel": {"anchor": "top_left", "offset": [24, 24], "width": 330, "row_height": 28, "icon_size": 22, "primary_font": "body 19", "optional_font": "body 17"},
        "stats_chip": {"anchor": "top_center", "offset": [0, 24], "size": [308, 48]},
        "buttons_top_right": {"anchor": "top_right", "offset": [-24, 24], "size": [64, 64], "gap": 16, "order": ["retry", "pause"]},
        "weapon_cards": {"anchor": "bottom_right", "offset": [-24, -24], "card_size": [176, 110], "gap": 12, "states": ["normal", "selected", "empty"]},
        "cooldown_ring": {"anchor": "above the selected weapon card", "size": [48, 48], "note": "TextureProgressBar_Cooldown drawn at 48 base px in the HUD"},
        "hint": {"anchor": "bottom_center", "offset": [0, -30], "font": "body 17", "color": C["text_dim"]},
        "critical_marker": {"world_anchor": "0.75 m above the critical asset top (code)", "size": [104, 104], "layers": ["ring", "brackets", "diamond"],
                            "motion": {"ring_rotation_deg_per_s": 30, "diamond_pulse_scale": [0.9, 1.1], "diamond_pulse_hz": 1.2}},
        "objective_marker": {"size": [48, 64], "pivot": [24, 60]},
        "trajectory": {"dot_texture": f"{RES}/ui/kit/png_2x/gam_ui_trajectory_dot.png", "dot_size_start": 9, "dot_size_end": 6, "alpha_start": 0.9, "alpha_end": 0.35, "spacing_px": 28},
    },
    "damage_numbers": {
        "font": FONTS["display_bold"],
        "label_settings": {
            "standard":  {"font_size": 30, "font_color": C["text"], "outline_size": 6, "outline_color": "#05080BD9"},
            "resisted":  {"font_size": 22, "font_color": C["text_dim"], "outline_size": 5, "outline_color": "#05080BD9", "note": "hit absorbed by resistance or below min_damage"},
            "blast":     {"font_size": 32, "font_color": C["amber"], "outline_size": 6, "outline_color": "#05080BD9"},
            "critical_asset": {"font_size": 34, "font_color": C["critical"], "outline_size": 6, "outline_color": "#05080BD9", "caption": {"text_key": "ui.damage.critical", "font": FONTS["display_semibold"], "font_size": 12, "spacing_glyph": 2.5, "color": C["critical"]}},
            "destroyed": {"font_size": 26, "font_color": C["success"], "outline_size": 5, "outline_color": "#05080BD9", "note": "component destroyed, shows +Mission Points"},
            "research":  {"font_size": 24, "font_color": C["research"], "outline_size": 5, "outline_color": "#05080BD9"},
        },
        "format": {"damage": "-{value}", "points": "+{value}", "thousands_separator": ","},
        "motion": {"spawn_offset_px": [0, -24], "rise_px": 36, "duration_s": 0.7, "ease": "cubic out", "pop_scale": [1.25, 1.0], "pop_s": 0.12, "fade_out_last_s": 0.25,
                   "stack_offset_px": 18, "max_on_screen": 6, "merge_window_s": 0.15, "note": "draw in a CanvasLayer above the 3D view; position from Camera3D.unproject_position"},
    },
    "motion": {"panel_in_s": 0.28, "panel_rise_px": 16, "button_press_scale": 0.96, "button_press_s": 0.06, "button_release_s": 0.12, "screen_fade_s": 0.25, "chapter_title_hold_s": 2.4,
               "reduce_motion": "honour the Reduce screen shake / Reduce flashes settings: no pop scale, no flicker, fades only"},
}

if __name__ == "__main__":
    p = os.path.join(UI, "theme", "tfj_theme_spec.json")
    os.makedirs(os.path.dirname(p), exist_ok=True)
    json.dump(spec, open(p, "w"), indent=1)
    print(p)
