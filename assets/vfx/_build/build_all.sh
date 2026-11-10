#!/usr/bin/env bash
# Rebuild the whole VFX library one module at a time (keeps memory low), then tiers, index and previews.
set -euo pipefail
cd "$(dirname "$0")"
PY=${PY:-python3}
rm -rf index_parts
for m in fx_breach fx_kinetic fx_general fx_chapter; do $PY $m.py; done
$PY tiers.py
$PY make_index.py
$PY previews.py
