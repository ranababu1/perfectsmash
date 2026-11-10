"""Upgrade-tier variants of the weapon effects (gradient remap of the base sheets) plus upgrade_tiers.json."""
import json, os
import numpy as np
from PIL import Image
from vfxlib import *

TIERS = {
    # tier: (label, colour token from ui/_build/tokens.py TIERS, kinetic ramp, breach ramp, scale, emission note)
    "T2": ("Mk II", "#5AA9FF",
           [(0.0, "#04122e"), (0.35, "#1f5fc8"), (0.7, "#5aa9ff"), (1.0, "#d6e9ff"), (1.4, "#ffffff")],
           [(0.0, "#2a1004"), (0.35, "#c45a14"), (0.65, "#f29a3a"), (0.9, "#ffd6a0"), (1.3, "#ffffff")], 1.12),
    "T3": ("Mk III", "#B9F2FF",
           [(0.0, "#0a2430"), (0.35, "#4fb8d8"), (0.65, "#b9f2ff"), (0.9, "#f2fdff"), (1.3, "#ffffff")],
           [(0.0, "#2a1606"), (0.35, "#d27a26"), (0.6, "#f6c060"), (0.85, "#fff0c8"), (1.2, "#ffffff")], 1.25),
}
SOURCES = [("OPR-VFX-KINETIC_TRAIL-A", "k", "texture"), ("OPR-VFX-KINETIC_MUZZLE-A", "k", "sprite"), ("OPR-VFX-KINETIC_IMPACT-A", "k", "sprite"),
           ("OPR-VFX-BREACH_TRAIL-A", "b", "texture"), ("OPR-VFX-BREACH_EXPLOSION-A", "b", "sprite"), ("OPR-VFX-BREACH_SHOCKWAVE-A", "b", "sprite")]


def remap(path_in, stops, boost):
    im = np.asarray(Image.open(path_in).convert("RGBA")).astype(np.float32) / 255
    L = (im[..., :3] * im[..., 3:4]).max(axis=-1) * boost
    col = ramp(np.clip(L, 0, 1.4), stops)
    col = col / np.maximum(col.max(axis=-1, keepdims=True), 1e-4)  # hue from the tier ramp, intensity preserved
    light = col * np.clip(L, 0, 1.4)[..., None]
    return additive_from_light(light)


def load_index():
    ents = {}
    d = os.path.join(VFX, "_build", "index_parts")
    for f in sorted(os.listdir(d), key=lambda f: os.path.getmtime(os.path.join(d, f))):
        for e in json.load(open(os.path.join(d, f))):
            ents[e["id"]] = e
    return ents


def build():
    base = load_index()
    out_entries = []
    for tid, (label, col, kr, br, boost) in TIERS.items():
        for sid, kind, rt in SOURCES:
            src = base[sid]
            pin = os.path.join(os.path.dirname(ROOT), src["path"])
            f = remap(pin, kr if kind == "k" else br, boost)
            eid = sid[:-2] + "-" + tid
            pout = os.path.join(VFX, "shared", "tiers", eid.lower().replace("-", "_") + ".png")
            rng = np.random.default_rng(5)
            q = quantise(f, rng)
            os.makedirs(os.path.dirname(pout), exist_ok=True)
            Image.fromarray(q, "RGBA").save(pout, optimize=True)
            e = dict(src); e["id"] = eid; e["path"] = os.path.relpath(pout, os.path.dirname(ROOT))
            e["purpose"] = f"{label} upgrade-tier variant of {sid}: " + src["purpose"]
            e["notes"] = (src.get("notes", "") + f" Tier variant: gradient remap of the base sheet to the {label} colour ({col}) with {int((boost - 1) * 100)}% brighter emission; same frames, timing and pivot as the base.").strip()
            out_entries.append(e)
            print(eid)
    with open(os.path.join(VFX, "_build", "index_parts", "zz_tiers.json"), "w") as fh:
        json.dump(out_entries, fh, indent=1)
    spec = {
        "_note": "Weapon upgrade tiers for VFX. Base and Mk I use the base sheets (Mk I adds scale only); Mk II and Mk III use the -T2 / -T3 remapped sheets. Tier is the highest upgrade level owned for that weapon (data/weapons.json levels 1-3). Colours match ui/_build/tokens.py TIERS and the HUD tier badges.",
        "tiers": {
            "tier0": {"label": "Base", "sheets": "-A", "scale": 1.0, "modulate": "#FFFFFF", "badge_colour": "#9AA9B5"},
            "tier1": {"label": "Mk I", "sheets": "-A", "scale": 1.08, "modulate": "#FFFFFF", "badge_colour": "#3CC8E6"},
            "tier2": {"label": "Mk II", "sheets": "-T2", "scale": 1.12, "modulate": "#FFFFFF", "badge_colour": "#5AA9FF"},
            "tier3": {"label": "Mk III", "sheets": "-T3", "scale": 1.22, "modulate": "#FFFFFF", "badge_colour": "#B9F2FF", "extra": "add one SHR-VFX-PARTICLE_GLOW-A ember trail (amount 6, lifetime 0.25 s) behind the slug"},
        },
        "weapons": {
            "kinetic_accelerator": ["OPR-VFX-KINETIC_TRAIL", "OPR-VFX-KINETIC_MUZZLE", "OPR-VFX-KINETIC_IMPACT"],
            "breach_charge": ["OPR-VFX-BREACH_TRAIL", "OPR-VFX-BREACH_EXPLOSION", "OPR-VFX-BREACH_SHOCKWAVE"],
        },
        "cooldown_modulate": {"kinetic_accelerator": "#3CC8E6", "breach_charge": "#F2A23A"},
        "chapter_tints": {
            "_note": "Optional modulate for shared neutral sheets (PARTICLE_GLOW, PARTICLE_RING, COOLDOWN) when used as chapter accents. Do not tint fire, smoke or critical-asset red.",
            "helix": "#3CC8E6", "vita": "#7FD9A8", "nova_grid": "#4AA8FF", "civitas": "#8EB6DA", "meridian": "#A592FF",
        },
    }
    with open(os.path.join(VFX, "upgrade_tiers.json"), "w") as fh:
        json.dump(spec, fh, indent=2)


if __name__ == "__main__":
    build()
