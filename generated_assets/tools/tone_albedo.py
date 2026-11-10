#!/usr/bin/env python3
"""Tone albedo textures in linear light (integration stream, 2026-11-10; used for VITA revision 4).

    out = k * tint * (mean + c * (x - mean))      per pixel, in linear light, alpha kept

k darkens, c > 1 lifts panel detail around the texture mean, tint (optional RGB) offsets a colour cast.
Usage:
    python3 generated_assets/tools/tone_albedo.py SRC_DIR DST_DIR PREFIX PARAMS_JSON
VITA revision 4 (sources are the revision 3 files at commit 191dc77):
    mkdir -p /tmp/vita_r3 && for n in floor composite reinforced_steel lightweight_alloy concrete \
      electronic_module ai_core_module energy_component; do f=vta_mat_${n}_a_albedo.png; \
      git show 191dc77:generated_assets/materials/vita/$f > /tmp/vita_r3/$f; done
    python3 generated_assets/tools/tone_albedo.py /tmp/vita_r3 generated_assets/materials/vita vta_mat_ \
      "$(cat generated_assets/tools/vita_tone_rev4.json)"
"""
import json, sys
import numpy as np
from PIL import Image


def to_lin(v):
    v = v / 255.0
    return np.where(v <= 0.04045, v / 12.92, ((v + 0.055) / 1.055) ** 2.4)


def to_srgb(lin):
    lin = np.clip(lin, 0, 1)
    return np.where(lin <= 0.0031308, lin * 12.92, 1.055 * lin ** (1 / 2.4) - 0.055) * 255.0


def main() -> None:
    src, dst, prefix, params = sys.argv[1], sys.argv[2], sys.argv[3], json.loads(sys.argv[4])
    for name, spec in params.items():
        k, c = spec[0], spec[1]
        tint = np.array(spec[2] if len(spec) > 2 else [1.0, 1.0, 1.0])
        f = f"{prefix}{name}_a_albedo.png"
        im = Image.open(f"{src}/{f}")
        mode = im.mode
        a = np.asarray(im.convert("RGBA")).astype(float)
        lin = to_lin(a[..., :3])
        mean = lin.reshape(-1, 3).mean(0)
        out = k * tint * (mean + c * (lin - mean))
        rgb = np.round(to_srgb(out)).astype(np.uint8)
        res = np.dstack([rgb, a[..., 3].astype(np.uint8)])
        Image.fromarray(res, "RGBA").convert(mode).save(f"{dst}/{f}", optimize=True)
        print(f, "mean sRGB", [round(x) for x in rgb.reshape(-1, 3).mean(0)])


if __name__ == "__main__":
    main()
