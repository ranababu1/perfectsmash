"""Builds generated_assets/manifest_parts/ui-vfx.json from the files actually on disk.
Run after any UI, branding, font or VFX rebuild: python manifest_fragment.py"""
import os, sys, json, glob, datetime
sys.path.insert(0, os.path.dirname(__file__))
from PIL import Image
from tokens import ROOT, CHAPTERS

REPO = os.path.dirname(ROOT)
def rel(p): return os.path.relpath(p, REPO)
def dims(p):
    with Image.open(p) as im: return f"{im.width}x{im.height}"

SRC_CODE = "hand-authored SVG written by the asset agent (Grok Bot) in generated_assets/ui/_build/*.py, rasterised with resvg 0.49.0"
RIGHTS_CODE = "original work authored by the asset agent for this project (code-generated vector art, AI-assisted authorship); ownership not legally settled for AI-assisted work; not marked commercially cleared; no third-party content except OFL fonts outlined in the logo"
RIGHTS_AI = "AI-generated image (GenerateImage tool, image model); provenance recorded; rights not verified; not commercially cleared"
RIGHTS_OFL = "SIL Open Font License 1.1 (OFL.txt beside the file); embedding in a commercial game permitted; font may not be sold on its own"
E = []
def add(**k):
    k.setdefault("approval_status", "pending_review")
    E.append(k)

def fonts():
    for fam, folder, designer, url in (("CHAKRA_PETCH", "chakra_petch", "Cadson Demak", "https://github.com/google/fonts/tree/main/ofl/chakrapetch"),
                                        ("BARLOW", "barlow", "Jeremy Tribby", "https://github.com/google/fonts/tree/main/ofl/barlow")):
        for f in sorted(glob.glob(os.path.join(ROOT, "fonts", folder, "*.ttf"))):
            w = os.path.basename(f).split("-")[1][:-4].upper()
            add(id=f"GAM-FNT-{fam}-{w}", path=rel(f), category="fonts", render_type="font", format="ttf",
                purpose=("display face: titles, headings, numerals" if fam == "CHAKRA_PETCH" else "UI and body text face"),
                source=f"{fam.replace('_', ' ').title()} by {designer}, official Google Fonts repository {url} (accessed 2026-11-09)",
                rights_status=RIGHTS_OFL, used_by="ui theme (generated_assets/ui/theme/tfj_theme_spec.json); logo wordmark outlines (Chakra Petch Bold)",
                chapter="shared", notes="licence: " + rel(os.path.join(ROOT, "fonts", folder, "OFL.txt")))

def branding():
    B = os.path.join(ROOT, "ui", "branding")
    for p in sorted(glob.glob(os.path.join(B, "logo", "png", "*.png"))):
        stem = os.path.basename(p)[:-4]
        parts = stem.split("_")  # gam logo <kind> a <scheme...> <size>
        kind = parts[2].upper(); scheme = "_".join(parts[4:-1]).upper()
        svg = os.path.join(B, "logo", "svg", "_".join(parts[:-1]) + ".svg")
        add(id=f"GAM-LOGO-{kind}-{scheme}", path=rel(p), category="ui", render_type="ui", format="png", dimensions=dims(p),
            purpose=f"Temporal: First Jump {kind.lower()} {'symbol mark' if kind == 'MARK' else 'logo lockup'}, {scheme.lower().replace('_', ' ')} variant",
            source=SRC_CODE, rights_status=RIGHTS_CODE, used_by="branding: menus, splash, store listing, credits (proposed)", chapter="shared",
            requires_alpha=True, notes=f"vector master {rel(svg)}; editable live-text source in ui/branding/logo/source/")
    for p in sorted(glob.glob(os.path.join(B, "logo", "source", "*.svg"))):
        kind = os.path.basename(p).split("_")[2].upper()
        add(id=f"GAM-LOGO-{kind}-EDITABLE_SOURCE", path=rel(p), category="ui", render_type="ui", format="svg",
            purpose=f"editable {kind.lower()} logo source with live text layers (Chakra Petch) for future edits", source=SRC_CODE, rights_status=RIGHTS_CODE,
            used_by="design source only; game uses the outlined PNG/SVG", chapter="shared")
    A = os.path.join(B, "app_icon")
    for role in ("foreground", "background", "monochrome"):
        p = os.path.join(A, "android_adaptive", f"gam_logo_app_icon_a_{role}_432.png")
        add(id=f"GAM-LOGO-APP_ICON-ADAPTIVE_{role.upper()}", path=rel(p), category="app_icon", render_type="ui", format="png", dimensions=dims(p),
            purpose=f"Android adaptive icon {role} layer (108 dp at xxxhdpi); mark fits the 66 dp (264 px) safe circle", source=SRC_CODE, rights_status=RIGHTS_CODE,
            used_by="Android export preset launcher_icons/adaptive_* (proposed; assets/icon/* untouched)", chapter="shared", requires_alpha=(role != "background"),
            notes="SVG source beside it; background PNG rebuilt with float gradients and dither to avoid banding")
    for n in (512, 256, 192, 48):
        p = os.path.join(A, f"gam_logo_app_icon_a_{n}.png")
        add(id=f"GAM-LOGO-APP_ICON-{n}", path=rel(p), category="app_icon", render_type="ui", format="png", dimensions=dims(p),
            purpose={512: "Play Store icon / main 512 icon", 256: "project icon (config/icon) replacement candidate", 192: "legacy launcher icon xxxhdpi", 48: "48 px legibility check / mdpi launcher"}[n],
            source=SRC_CODE, rights_status=RIGHTS_CODE, used_by="app icon replacement candidate (owner approval needed; assets/icon/* untouched)", chapter="shared",
            notes="flattened from the adaptive layers, showing the central 88 dp; source gam_logo_app_icon_a_legacy.svg")
    S = os.path.join(B, "splash")
    for p in sorted(glob.glob(os.path.join(S, "*.png"))):
        nm = os.path.basename(p)
        add(id="GAM-UI-SPLASH-" + ("LOGO_TRANSPARENT" if "transparent" in nm else nm.split("_")[-1][:-4].upper()), path=rel(p), category="ui", render_type="ui", format="png", dimensions=dims(p),
            purpose="boot splash" + (" logo layer (use with boot_splash/bg_color #080C10)" if "transparent" in nm else " full frame, logo centred on dark plate"),
            source=SRC_CODE, rights_status=RIGHTS_CODE, used_by="project boot_splash (proposed)", chapter="shared", requires_alpha="transparent" in nm)
    for key, ch in CHAPTERS.items():
        n = ch["n"]
        for sfx in ("1x", "2x"):
            p = os.path.join(B, "chapter_titles", "game", f"gam_ui_chapter_title_0{n}_{key}_deco_{sfx}.png")
            add(id=f"GAM-UI-CHAPTER_TITLE_DECO-0{n}_{sfx.upper()}", path=rel(p), category="ui", render_type="ui", format="png", dimensions=dims(p),
                purpose=f"chapter {n} ({ch['org']}) title treatment decoration layer: emblem plate, rules and ticks, no text; Godot draws CHAPTER n / title / institution and year as Labels",
                source=SRC_CODE, rights_status=RIGHTS_CODE, used_by="chapter intro title card (proposed)", chapter=key, requires_alpha=True,
                levels=list(range(ch["levels"][0], ch["levels"][1] + 1)),
                notes=f"text layout reference: ui/branding/chapter_titles/source/gam_ui_chapter_title_0{n}_{key}_editable.svg (text ids txt_chapter_number, txt_chapter_title, txt_institution_year at y 364 / 440 / 530, centred x 640)")
        p = os.path.join(B, "chapter_titles", "source", f"gam_ui_chapter_title_0{n}_{key}_editable.svg")
        add(id=f"GAM-UI-CHAPTER_TITLE-0{n}_EDITABLE_SOURCE", path=rel(p), category="ui", render_type="ui", format="svg", purpose=f"editable chapter {n} title treatment with live text layers",
            source=SRC_CODE, rights_status=RIGHTS_CODE, used_by="design source", chapter=key)

def icons():
    idx = json.load(open(os.path.join(ROOT, "ui", "icons", "icon_index.json")))["icons"]
    for e in idx:
        p = os.path.join(ROOT, "ui", "icons", "png_2x", e["file"] + ".png")
        ch = "shared"
        if e["group"] == "chapters": ch = e["name"].replace("chapter_", "")
        hero = f"; hero 256: ui/icons/png_hero_256/{e['file']}.png" if e["hero"] else ""
        add(id=e["id"], path=rel(p), category="ui", render_type="ui", format="png", dimensions=dims(p),
            purpose=f"icon ({e['group']}): {e['name'].replace('_', ' ')}", source=SRC_CODE + " (icons.py)", rights_status=RIGHTS_CODE,
            used_by="HUD, menus, upgrade and mission screens (proposed)", chapter=ch, requires_alpha=True,
            notes=f"white on transparent, tint with modulate; 64 base px; 1x: ui/icons/png_1x/{e['file']}.png; SVG: ui/icons/svg/{e['file']}.svg{hero}")

def kit():
    idx = json.load(open(os.path.join(ROOT, "ui", "kit", "kit_index.json")))["components"]
    for e in idx:
        p = os.path.join(ROOT, "ui", "kit", "png_2x", e["file"] + ".png")
        ch = "shared"
        for k in CHAPTERS:
            if f"_{k}" in e["name"]: ch = k
        item = dict(id=f"GAM-UI-{e['name'].upper()}-A", path=rel(p), category="ui", render_type="ui", format="png", dimensions=dims(p),
                    purpose=f"UI kit {e['group']}: {e['name'].replace('_', ' ')}", source=SRC_CODE + " (kit.py)", rights_status=RIGHTS_CODE,
                    used_by="Godot Theme (ui/theme/tfj_theme_spec.json)", chapter=ch, requires_alpha=True,
                    notes=f"{e['notes']}; 1x: ui/kit/png_1x/{e['file']}.png" + (f" (1x 9-slice {e['nine_slice_1x']})" if e["nine_slice_1x"] else "") + f"; SVG: ui/kit/svg/{e['file']}.svg")
        if e["nine_slice_2x"]: item["nine_slice"] = e["nine_slice_2x"]
        add(**item)

def screens():
    for p in sorted(glob.glob(os.path.join(ROOT, "ui", "screens", "webp_1x", "*.webp"))):
        nm = os.path.basename(p)[len("gam_ui_screen_"):-len("_mock.webp")]
        concept = nm.startswith("concept_")
        add(id=f"GAM-UI-SCREEN_{nm.upper()}-MOCK", path=rel(p), category="ui", render_type="reference", format="webp", dimensions=dims(p),
            purpose=("concept-level " if concept else "") + f"screen layout mock-up: {nm.replace('concept_', '').replace('_', ' ')} (placeholder text, labelled MOCK)",
            source=SRC_CODE + " (screens.py); backgrounds from ui/backgrounds, SV-04 concept or the integration greybox harness capture", rights_status=RIGHTS_CODE + "; any embedded background keeps its own rights status",
            used_by="layout reference for the coding agent; not a game texture", chapter="shared",
            notes=f"2x: ui/screens/webp_2x/{os.path.basename(p)}; editable SVG: ui/screens/source/{os.path.basename(p)[:-4]}.svg")

def backgrounds():
    for p, what in ((os.path.join(ROOT, "ui", "backgrounds", "ui_bg_main_menu_1280x720.webp"), "MAIN_MENU"), (os.path.join(ROOT, "ui", "backgrounds", "ui_bg_loading_1280x720.webp"), "LOADING")):
        add(id=f"GAM-BG-{what}-A", path=rel(p), category="ui", render_type="ui", format="webp", dimensions=dims(p),
            purpose={"MAIN_MENU": "main menu backdrop: temporal chamber ring, operative silhouette, dark left third for the menu column",
                     "LOADING": "loading screen / credits backdrop: sealed facility corridor with temporal distortion, quiet lower band"}[what],
            source="GenerateImage (cursor image tool), 2026-11-09, prompt content restated in ui/PRODUCTION_NOTES.md (exact strings not logged); graded (vignette, shadow tint, dither) by the asset agent; raw master /workspace/tfj-masters/ui-vfx/ (box only)",
            rights_status=RIGHTS_AI, used_by="main menu / loading / credits screens (proposed)", chapter="shared",
            notes="1280x720 is the generator's maximum; no upscale applied. No text, logos or watermarks (inspected)")

def theme():
    p = os.path.join(ROOT, "ui", "theme", "tfj_theme_spec.json")
    add(id="GAM-UI-THEME_SPEC-A", path=rel(p), category="ui", render_type="ui", format="json", purpose="Godot Theme-ready spec: colours, fonts, type roles, margins, StyleBox textures + 9-slice, StyleBoxFlat equivalents, HUD layout, damage numbers",
        source="asset agent (theme.py)", rights_status=RIGHTS_CODE, used_by="coding agent: build Theme / LabelSettings resources", chapter="shared")

def vfx():
    idx_p = os.path.join(ROOT, "vfx", "vfx_index.json")
    if not os.path.exists(idx_p): return
    for e in json.load(open(idx_p))["entries"]:
        add(**e)

if __name__ == "__main__":
    fonts(); branding(); icons(); kit(); screens(); backgrounds(); theme(); vfx()
    for e in E:
        assert os.path.isfile(os.path.join(REPO, e["path"])), e["path"]
    out = {"stream": "ui-vfx", "updated": datetime.date.today().isoformat(), "entries": E}
    p = os.path.join(ROOT, "manifest_parts", "ui-vfx.json")
    json.dump(out, open(p, "w"), indent=1, ensure_ascii=False)
    from collections import Counter
    print(len(E), "entries", Counter(e["category"] for e in E))
