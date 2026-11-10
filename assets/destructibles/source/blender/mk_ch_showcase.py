"""mk_ch_showcase.py <chapter> <CODE>: chapter showcase layout from the Helix scaffold (environment pieces swapped
to the chapter's kit) plus a gameplay band of the chapter's components, the operative with the Kinetic Accelerator."""
import json, sys, glob, os
ch, code = sys.argv[1], sys.argv[2]
c = code.lower()
GA = "/workspace/tfj-3d-kits/generated_assets"
H = json.load(open(f"{GA}/environments/showcase/helix_showcase_layout.json"))
ST = "/workspace/tfj-masters/3d-kits/stats"
items = []
for it in H["items"]:
    if it["f"].startswith("environments/helix/"):
        f = it["f"].replace("environments/helix/hlx_", f"environments/{ch}/{c}_")
        if os.path.exists(f"{GA}/{f}"):
            items.append(dict(it, f=f))
stats = {}
for p in sorted(glob.glob(f"{ST}/{code}-CMP-*.json")):
    s = json.load(open(p))
    stats[os.path.basename(p)[:-5]] = s
def dims(i):
    w, h = stats[i]["reference_size_px"]
    return w / 100.0, h / 100.0
def stem(i):
    return os.path.basename(stats[i]["file"])[:-4] if "file" in stats[i] else i.lower().replace("-", "_")
ids = list(stats)
crit = [i for i in ids if stats[i].get("critical")]
deck = next((i for i in ids if "DECK" in i and i.endswith("-C")), next((i for i in ids if "DECK" in i), None))
x = -0.8
row = [i for i in ids if i not in crit and i != deck]
def span(r):
    return sum(dims(i)[0] + 0.12 for i in r) + (dims(deck)[0] + 0.3 if deck else sum(dims(i)[0] + 0.42 for i in crit))
for suffix in ("-C", "-B"):
    while span(row) > 11.0 and any(i.endswith(suffix) for i in row):
        row.remove([i for i in row if i.endswith(suffix)][-1])
left, right = row[: len(row) // 2], row[len(row) // 2:]
def put(i, x, z=0.0, state=None):
    w, h = dims(i)
    d = dict(f=f"destructibles/{ch}/{stem(i)}.glb", p=[round(x + w / 2, 3), round(h / 2, 3), z])
    if state:
        d["state"] = state
    items.append(d)
    return x + w + 0.12
for k, i in enumerate(left):
    x = put(i, x, state="mesh_light" if k == len(left) - 1 else None)
if deck:
    dw, dh = dims(deck)
    dx = x + 0.1
    items.append(dict(f=f"destructibles/{ch}/{stem(deck)}.glb", p=[round(dx + dw / 2, 3), round(dh / 2, 3), 0.0]))
    for i in crit:
        w, h = dims(i)
        items.append(dict(f=f"destructibles/{ch}/{stem(i)}.glb", p=[round(dx + dw / 2, 3), round(dh + h / 2, 3), 0.0]))
    x = dx + dw + 0.2
else:
    for i in crit:
        x = put(i, x + 0.15) + 0.15
for k, i in enumerate(right):
    x = put(i, x, state="mesh_heavy" if k == 1 else None)
tall = sorted(row, key=lambda i: -dims(i)[1])[:3]
for k, xx in enumerate([-4.6, -3.9, 2.6, 3.3, 11.4, 12.1]):
    i = tall[k % len(tall)]
    w, h = dims(i)
    items.append(dict(f=f"destructibles/{ch}/{stem(i)}.glb", p=[xx, round(h / 2, 3), -2.6]))
op = next(it for it in H["items"] if "opr_chr_operative" in it["f"])
items.append(op)
L = {k: v for k, v in H.items() if k != "items"}
L["items"] = items
L.update(json.loads(sys.argv[3]) if len(sys.argv) > 3 else {})
L["focus"] = [round((x - 2.2) / 2, 2), 1.6, 0.0]
json.dump(L, open(f"{GA}/environments/showcase/{ch}_showcase_layout.json", "w"), indent=1)
print("LAYOUT", ch, len(items), "row end x", round(x, 2), "focus", L["focus"])
