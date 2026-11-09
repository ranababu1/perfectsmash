#!/usr/bin/env bash
# One integration pass (integration stream): sync with origin/assets, merge manifest fragments,
# validate, Godot import/load check, render previews, rebuild the coverage matrix.
# Does not commit or push; review the output, then commit.
# Usage: generated_assets/tools/integration_cycle.sh
set -uo pipefail
REPO="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$REPO"
OUT=/tmp/tfj-godot-check
mkdir -p "$OUT"
echo "== validate + merge"
python3 generated_assets/tools/validate_asset_manifest.py --merge --quiet --report "$OUT/manifest_report.json"; V=$?
echo "== godot import + load"
generated_assets/tools/godot/run_import_check.sh "$OUT/load_report.json"; G=$?
echo "== previews"
rm -rf "$OUT/previews"
generated_assets/tools/godot/render_previews.sh "$OUT/previews" > "$OUT/previews.log" 2>&1; P=$?
grep -E "PREVIEW|ERROR" "$OUT/previews.log" | head -40
python3 - "$OUT/previews" "$REPO/generated_assets/docs/previews" <<'PY'
import sys, pathlib
from PIL import Image
src, dst = pathlib.Path(sys.argv[1]), pathlib.Path(sys.argv[2])
dst.mkdir(parents=True, exist_ok=True)
for p in sorted(src.glob("*.png")):
    out = dst / ("harness_" + p.stem + ".webp")
    Image.open(p).convert("RGB").save(out, quality=86, method=6)
    print("preview", out.relative_to(dst.parents[2]), out.stat().st_size)
PY
echo "== coverage"
python3 generated_assets/tools/build_coverage_matrix.py; C=$?
echo "== exit codes: validate=$V godot=$G previews=$P coverage=$C"
