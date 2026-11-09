"""Usage: blender -b --factory-startup --python runenv.py -- <kit module> [id substrings...] [--no-render]"""
import sys, os, json, traceback
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "kits"))
import importlib
import tfjenv as TE

argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
mod = importlib.import_module(argv[0])
filters = [a for a in argv[1:] if not a.startswith("--")]
render = "--no-render" not in argv
STATS = "/workspace/tfj-masters/3d-kits/stats_env"
os.makedirs(STATS, exist_ok=True)
for spec in mod.SPECS:
    if filters and not any(f in spec["id"] for f in filters):
        continue
    try:
        st = TE.build(spec, render=render, samples=int(os.environ.get("TFJ_SAMPLES", "32")))
        for k in ("chapter", "material", "category", "layer", "origin", "purpose", "kind", "dims_m",
                  "reference_size_px", "depth_m", "landmark"):
            if k in spec:
                st[k] = spec[k]
        json.dump(st, open(f"{STATS}/{spec['id']}.json", "w"), indent=1)
        print("BUILT", spec["id"], st["tris"], st["bytes"], st["seconds"], "s")
    except Exception:
        traceback.print_exc()
        print("FAILED", spec["id"])
