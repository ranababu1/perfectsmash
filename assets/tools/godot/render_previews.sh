#!/usr/bin/env bash
# Renders previews with the game camera and light (Godot 4.7.2, GL Compatibility, software GL via Xvfb).
# Usage: assets/tools/godot/render_previews.sh [out_dir] [--only=helix,vita]
# Uses the temp project prepared by run_import_check.sh (run that first so imports are current).
set -euo pipefail
GODOT="${GODOT:-/opt/tfj-tools/bin/godot}"
WORK="${TFJ_GODOT_WORK:-/tmp/tfj-godot-check/project}"
OUT="${1:-/tmp/tfj-godot-check/previews}"
shift || true
mkdir -p "$OUT"
echo "== xvfb-run -a -s '-screen 0 1280x720x24' $GODOT --path $WORK --rendering-driver opengl3 --resolution 1280x720 --script res://assets/tools/godot/render_previews.gd -- --out=$OUT $*"
xvfb-run -a -s "-screen 0 1280x720x24" "$GODOT" --path "$WORK" --rendering-driver opengl3 --resolution 1280x720 \
  --script res://assets/tools/godot/render_previews.gd -- --out="$OUT" "$@" 2>&1 | grep -E "PREVIEW|ERROR|OpenGL API" || true
ls -la "$OUT"
