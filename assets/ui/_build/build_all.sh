#!/usr/bin/env bash
# Rebuild every UI, branding and preview output in dependency order.
# Needs: Python 3 with Pillow, numpy, fontTools; resvg (RESVG env var, default /workspace/tfj-ui-vfx-tools/resvg).
set -euo pipefail
cd "$(dirname "$0")"
PY=${PY:-python3}
$PY icons.py
$PY sheet.py
$PY branding.py
$PY branding.py --splash
$PY kit.py
$PY kitsheet.py
$PY theme.py
$PY screens.py
$PY previews.py
$PY manifest_fragment.py
