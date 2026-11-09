"""VFX review previews: contact sheet (peak frame per effect), tier comparison, in-engine Godot renders (animated WebP)."""
import glob, json, os, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from vfxlib import VFX, PREV, ROOT, composite

FONT = os.path.join(ROOT, "fonts", "barlow", "Barlow-Medium.ttf")


def frames_of(e):
    im = np.asarray(Image.open(os.path.join(os.path.dirname(ROOT), e["path"])).convert("RGBA"))
    if e["render_type"] != "sprite":
        return [im]
    a = e["animation"]; fw = im.shape[1] // a["columns"]; fh = im.shape[0] // a["rows"]
    return [im[(i // a["columns"]) * fh:(i // a["columns"] + 1) * fh, (i % a["columns"]) * fw:(i % a["columns"] + 1) * fw] for i in range(a["frames"])]


def peak(fr, blend):
    if len(fr) == 1:
        return fr[0]
    score = [float((f[..., 3].astype(np.float32) * (f[..., :3].max(-1) if blend == "add" else 255)).sum()) for f in fr]
    return fr[int(np.argmax(score)) if blend == "mix" else min(int(np.argmax(score)) + 1, len(fr) - 1)]


def contact(entries, out, cols=6, cell=230, title=None):
    font = ImageFont.truetype(FONT, 12)
    rows = (len(entries) + cols - 1) // cols
    S = Image.new("RGB", (cols * cell, rows * (cell + 22)), (21, 25, 30))
    d = ImageDraw.Draw(S)
    for i, e in enumerate(entries):
        f = peak(frames_of(e), e["blend"])
        c = Image.fromarray((composite(f, e["blend"]) * 255).astype(np.uint8))
        c.thumbnail((cell - 8, cell - 8), Image.LANCZOS)
        x, y = (i % cols) * cell, (i // cols) * (cell + 22)
        S.paste(c, (x + (cell - c.size[0]) // 2, y + (cell - c.size[1]) // 2))
        label = e["id"].replace("-VFX-", " ")
        while d.textlength(label, font=font) > cell - 10:
            label = label[:-2]
        d.text((x + 5, y + cell + 2), label if label == e["id"].replace("-VFX-", " ") else label[:-1] + "...", font=font, fill=(151, 167, 180))
    S.save(out, quality=88, method=6)
    print(out)


def godot_anims(render_dir):
    bg_p = os.path.join(render_dir, "vfx_kinetic_impact_35.png")
    if not os.path.exists(bg_p):
        print("no Godot renders in", render_dir); return
    bg = np.asarray(Image.open(bg_p).convert("RGB")).astype(int)
    names = sorted(set(os.path.basename(f).rsplit("_", 1)[0] for f in glob.glob(os.path.join(render_dir, "*.png"))))
    strip = []
    for n in names:
        fs = sorted(glob.glob(os.path.join(render_dir, n + "_*.png")))
        acc = np.zeros(bg.shape[:2], bool)
        for f in fs:
            acc |= np.abs(np.asarray(Image.open(f).convert("RGB")).astype(int) - bg).max(-1) > 6
        ys, xs = np.nonzero(acc)
        if len(xs) == 0:
            print("empty render", n); continue
        cx, cy = (xs.min() + xs.max()) // 2, (ys.min() + ys.max()) // 2
        w = max(xs.max() - xs.min() + 60, (ys.max() - ys.min() + 60) * 16 // 9, 320); h = w * 9 // 16
        x0 = int(np.clip(cx - w // 2, 0, 1280 - w)); y0 = int(np.clip(cy - h // 2, 0, 720 - h))
        box = (x0, y0, x0 + w, y0 + h)
        ims = [Image.open(f).convert("RGB").crop(box).resize((480, 270), Image.LANCZOS) for f in fs]
        p = os.path.join(PREV, "godot", n + "_godot.webp")
        os.makedirs(os.path.dirname(p), exist_ok=True)
        ims[0].save(p, save_all=True, append_images=ims[1:], duration=33, loop=0, quality=85, method=4)
        strip.append((n, [ims[i] for i in (1, 4, 8, 14, 24) if i < len(ims)]))
        print(p, "crop", box)
    font = ImageFont.truetype(FONT, 15)
    S = Image.new("RGB", (5 * 320, len(strip) * 200), (21, 25, 30)); d = ImageDraw.Draw(S)
    for r, (n, ims) in enumerate(strip):
        for c, im in enumerate(ims):
            S.paste(im.resize((320, 180), Image.LANCZOS), (c * 320, r * 200))
        d.text((6, r * 200 + 181), n + "  (Godot 4.7.2 GL Compatibility, MissionView camera; frames 0.07 / 0.17 / 0.30 / 0.50 / 0.83 s)", font=font, fill=(151, 167, 180))
    out = os.path.join(PREV, "vfx_godot_render_contact_sheet.webp"); S.save(out, quality=88, method=6); print(out)


def main():
    idx = json.load(open(os.path.join(VFX, "vfx_index.json")))["entries"]
    base = [e for e in idx if not e["id"].endswith(("-T2", "-T3"))]
    order = lambda e: ({"shared": 0}.get(e["chapter"], 1), "PARTICLE" in e["id"] or "THRESHOLD" in e["id"], e["id"])
    base.sort(key=order)
    contact(base, os.path.join(PREV, "vfx_contact_sheet.webp"))
    tiers = []
    for k in ("KINETIC_TRAIL", "KINETIC_MUZZLE", "KINETIC_IMPACT", "BREACH_TRAIL", "BREACH_EXPLOSION", "BREACH_SHOCKWAVE"):
        tiers += [e for e in idx if f"-{k}-" in e["id"]]
    tiers.sort(key=lambda e: (e["id"].rsplit("-", 1)[0], e["id"][-2:] != "-A", e["id"]))
    contact(tiers, os.path.join(PREV, "vfx_upgrade_tiers_contact_sheet.webp"), cols=3, cell=240)
    godot_anims(sys.argv[1] if len(sys.argv) > 1 else "/tmp/tfj-vfx-godot/render")


if __name__ == "__main__":
    main()
