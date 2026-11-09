"""Merge index_parts/*.json (latest wins per id) into vfx/vfx_index.json with manifest-ready entries."""
import json, os, datetime
from vfxlib import VFX, ROOT

PIVOTS = {  # normalised [u, v] in the frame (v down), keyed by id
    "OPR-VFX-KINETIC_MUZZLE": [0.16, 0.5], "OPR-VFX-KINETIC_TRAIL": [1.0, 0.5], "OPR-VFX-BREACH_TRAIL": [1.0, 0.5],
    "SHR-VFX-IMPACT_METAL": [0.5, 0.65], "SHR-VFX-SMOKE_LOOP": [0.5, 0.95], "SHR-VFX-FIRE_LOOP": [0.5, 0.94],
    "SHR-VFX-DUST_COLLAPSE": [0.5, 0.86], "VTA-VFX-CONTAINMENT_LEAK": [0.1, 0.5],
}


def main():
    d = os.path.join(VFX, "_build", "index_parts")
    ents = {}
    for f in sorted(os.listdir(d), key=lambda f: os.path.getmtime(os.path.join(d, f))):
        for e in json.load(open(os.path.join(d, f))):
            ents[e["id"]] = e
    out = []
    for eid in sorted(ents):
        e = dict(ents[eid])
        if not os.path.exists(os.path.join(os.path.dirname(ROOT), e["path"])):
            continue
        key = eid.rsplit("-", 1)[0]
        e["pivot"] = PIVOTS.get(key, [0.5, 0.5])
        if isinstance(e.get("used_by"), list):
            e["used_by"] = "; ".join(e["used_by"])
        out.append(e)
    with open(os.path.join(VFX, "vfx_index.json"), "w") as fh:
        json.dump({"updated": datetime.date.today().isoformat(), "pivot_convention": "[u, v] normalised in the frame, origin top-left, v down", "entries": out}, fh, indent=1)
    print(len(out), "vfx entries")


if __name__ == "__main__":
    main()
