"""Owner-review previews (small WebP) for the UI stream: icons, kit, branding, screens, damage numbers."""
import os, sys, json, glob
sys.path.insert(0, os.path.dirname(__file__))
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from tokens import UI, FONTS, C
PV = os.path.join(UI, "previews")
def webp(img, name, q=88):
    p = os.path.join(PV, name); img.convert("RGB").save(p, quality=q, method=6); return p
def font(f, s): return ImageFont.truetype(os.path.join(FONTS, f), s)

def damage_numbers():
    th = json.load(open(os.path.join(UI, "theme", "tfj_theme_spec.json")))["damage_numbers"]["label_settings"]
    im = Image.open(os.path.join(UI, "..", "docs", "previews", "baseline_harness_helix_01_greybox.webp")).convert("RGBA").crop((420, 100, 1180, 480))
    im = Image.alpha_composite(im, Image.new("RGBA", im.size, (5, 8, 11, 110)))
    d = ImageDraw.Draw(im)
    demo = [("standard", "-90", (60, 60)), ("resisted", "-12", (250, 70)), ("blast", "-160", (420, 50)), ("critical_asset", "-135", (330, 170)), ("destroyed", "+120", (80, 250)), ("research", "+5", (560, 250))]
    for key, txt, (x, y) in demo:
        st = th[key]; scale = 2
        f = font("chakra_petch/ChakraPetch-Bold.ttf", st["font_size"] * scale // 2 * 2 // 2 * 1)
        f = font("chakra_petch/ChakraPetch-Bold.ttf", int(st["font_size"] * 1.0))
        oc = st["outline_color"]; o = tuple(int(oc[i:i+2], 16) for i in (1, 3, 5)) + (int(oc[7:9], 16),)
        d.text((x, y), txt, font=f, fill=st["font_color"], stroke_width=st["outline_size"] // 2, stroke_fill=o)
        if key == "critical_asset":
            d.text((x + 4, y + st["font_size"] + 6), "CRITICAL", font=font("chakra_petch/ChakraPetch-SemiBold.ttf", 12), fill=C["critical"])
        d.text((x, y - 18), key, font=font("barlow/Barlow-Medium.ttf", 12), fill=C["text_faint"])
    return webp(im, "ui_damage_number_styles.webp")

def icons_sheet():
    im = Image.open(os.path.join(PV, "ui_icons_contact_sheet.png"))
    p = webp(im, "ui_icons_contact_sheet.webp"); os.remove(os.path.join(PV, "ui_icons_contact_sheet.png")); return p

def icons_small_proof():
    idx = json.load(open(os.path.join(UI, "icons", "icon_index.json")))["icons"]
    cols = 30; cell = 40
    rows = (len(idx) + cols - 1) // cols
    im = Image.new("RGBA", (cols * cell + 16, rows * cell + 16), C["surface"])
    for i, e in enumerate(idx):
        ic = Image.open(os.path.join(UI, "icons", "png_2x", e["file"] + ".png")).convert("RGBA").resize((32, 32), Image.LANCZOS)
        col = Image.new("RGBA", ic.size, C["text"]); col.putalpha(ic.getchannel("A"))
        im.alpha_composite(col, (8 + (i % cols) * cell + 4, 8 + (i // cols) * cell + 4))
    return webp(im, "ui_icons_32px_legibility_proof.webp", 92)

def kit_sheet():
    im = Image.open(os.path.join(PV, "ui_kit_contact_sheet.png"))
    p = webp(im, "ui_kit_contact_sheet.webp"); os.remove(os.path.join(PV, "ui_kit_contact_sheet.png")); return p

def screens_sheet():
    fs = sorted(glob.glob(os.path.join(UI, "screens", "webp_1x", "*.webp")))
    cols, w, h = 4, 480, 270
    rows = (len(fs) + cols - 1) // cols
    S = Image.new("RGB", (cols * w + (cols + 1) * 8, rows * (h + 26) + 8), C["bg0"]); d = ImageDraw.Draw(S)
    f = font("barlow/Barlow-Medium.ttf", 14)
    for i, p in enumerate(fs):
        x = 8 + (i % cols) * (w + 8); y = 8 + (i // cols) * (h + 26)
        S.paste(Image.open(p).convert("RGB").resize((w, h), Image.LANCZOS), (x, y))
        d.text((x, y + h + 4), os.path.basename(p).replace("gam_ui_screen_", "").replace("_mock.webp", ""), font=f, fill=C["text_dim"])
    out = [webp(S, "ui_screens_contact_sheet.webp")]
    for key in ("main_menu", "gameplay_hud_concept", "chapter_select", "results_success", "weapon_tech_upgrades", "chapter_map_01_helix"):
        out.append(webp(Image.open(os.path.join(UI, "screens", "webp_1x", f"gam_ui_screen_{key}_mock.webp")), f"ui_screen_{key}.webp", 90))
    return out

def branding_sheet():
    B = os.path.join(UI, "branding")
    S = Image.new("RGBA", (1600, 1300), C["bg0"])
    def put(p, box, bg=None):
        im = Image.open(p).convert("RGBA"); x, y, w, h = box
        r = min(w / im.width, h / im.height); im = im.resize((int(im.width * r), int(im.height * r)), Image.LANCZOS)
        if bg: S.paste(Image.new("RGBA", (w, h), bg), (x, y))
        S.alpha_composite(im, (x + (w - im.width) // 2, y + (h - im.height) // 2))
    put(f"{B}/logo/png/gam_logo_horizontal_a_colour_2048w.png", (40, 30, 1000, 240))
    put(f"{B}/logo/png/gam_logo_stacked_a_colour_1200w.png", (1080, 30, 480, 420))
    put(f"{B}/logo/png/gam_logo_horizontal_a_colour_on_light_2048w.png", (40, 290, 1000, 200), "#DCE2E6")
    put(f"{B}/logo/png/gam_logo_compact_a_mono_light_1600w.png", (40, 520, 480, 120))
    put(f"{B}/logo/png/gam_logo_compact_a_mono_dark_1600w.png", (560, 520, 480, 120), "#DCE2E6")
    put(f"{B}/app_icon/gam_logo_app_icon_a_512.png", (40, 680, 300, 300))
    put(f"{B}/app_icon/android_adaptive/gam_logo_app_icon_a_monochrome_432.png", (370, 680, 300, 300), "#2A3540")
    for i, n in enumerate((192, 48)):
        put(f"{B}/app_icon/gam_logo_app_icon_a_{n}.png", (700 + i * 210, 680 + (300 - n) // 2, n, n))
    put(f"{B}/splash/gam_ui_splash_a_1280x720.png", (1080, 470, 480, 270))
    put(os.path.join(PV, "branding_chapter_title_01_helix_preview.png"), (1080, 760, 480, 270), "#0A0F14")
    put(os.path.join(PV, "branding_chapter_title_05_meridian_preview.png"), (40, 1010, 480, 270), "#0A0F14")
    put(os.path.join(PV, "branding_chapter_title_03_nova_grid_preview.png"), (560, 1010, 480, 270), "#0A0F14")
    put(os.path.join(PV, "branding_chapter_title_04_civitas_preview.png"), (1080, 1030, 480, 270), "#0A0F14")
    out = webp(S, "branding_contact_sheet.webp")
    for p in glob.glob(os.path.join(PV, "branding_*.png")):
        im = Image.open(p).convert("RGBA"); bg = Image.new("RGBA", im.size, "#0A0F14"); bg.alpha_composite(im)
        webp(bg.resize((im.width // 2, im.height // 2), Image.LANCZOS), os.path.basename(p).replace(".png", ".webp")); os.remove(p)
    return out

if __name__ == "__main__":
    for fn in (damage_numbers, icons_sheet, icons_small_proof, kit_sheet, screens_sheet, branding_sheet):
        try:
            print(fn())
        except FileNotFoundError as exc:
            print("skip", fn.__name__, "(source contact sheet not rebuilt:", exc.filename, ")")
