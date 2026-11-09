"""Usage: blender -b --factory-startup --python runkit.py -- <kit module> [id substrings...] [--no-render]"""
import sys, os, json, traceback
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "kits"))
import importlib
import tfjbuild as TB

argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
mod = importlib.import_module(argv[0])
filters = [a for a in argv[1:] if not a.startswith("--")]
render = "--no-render" not in argv
outdir = os.environ.get("TFJ_OUT")
STATS = "/workspace/tfj-masters/3d-kits/stats"
os.makedirs(STATS, exist_ok=True)
for spec in mod.SPECS:
    if filters and not any(f in spec["id"] for f in filters):
        continue
    try:
        st = TB.build(spec, out_dir=outdir, render=render, samples=int(os.environ.get("TFJ_SAMPLES", "40")))
        st.update(kind=spec["kind"], chapter=spec["chapter"], material=spec["material"], depth_m=spec["d"],
                  reference_size_px=spec["ref_px"], scale_range=spec.get("scale", [0.8, 1.25]),
                  critical=spec.get("critical", False))
        json.dump(st, open(f"{STATS}/{spec['id']}.json", "w"), indent=1)
        print("BUILT", spec["id"], st["tris"], st["bytes"], st["debris_bytes"], st["seconds"], "s")
    except Exception:
        traceback.print_exc()
        print("FAILED", spec["id"])
