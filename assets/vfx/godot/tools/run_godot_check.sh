#!/usr/bin/env bash
# Builds and validates the VFX preset scenes in a temp copy of the project with Godot 4.7.2, then renders them.
# Usage: assets/vfx/godot/tools/run_godot_check.sh [work_dir]
set -uo pipefail
GODOT="${GODOT:-/opt/tfj-tools/bin/godot}"
REPO="$(cd "$(dirname "$0")/../../../.." && pwd)"
WORK="${1:-/tmp/tfj-vfx-godot}"
P="$WORK/project"; OUT="$WORK/render"
rm -rf "$WORK"; mkdir -p "$P/assets/vfx" "$OUT"
cp "$REPO/project.godot" "$P/"
sed -i '/run\/main_scene/d;/config\/icon/d' "$P/project.godot"
for d in shared helix vita nova_grid civitas meridian godot; do cp -r "$REPO/assets/vfx/$d" "$P/assets/vfx/"; done
rm -rf "$P/assets/vfx/godot/presets"
echo "== $GODOT --headless --path $P --import"
"$GODOT" --headless --path "$P" --import > "$WORK/import.log" 2>&1; echo "import exit $? errors $(grep -c 'ERROR' "$WORK/import.log")"
echo "== $GODOT --headless --path $P --script res://assets/vfx/godot/tools/build_presets.gd"
"$GODOT" --headless --path "$P" --script res://assets/vfx/godot/tools/build_presets.gd > "$WORK/build.log" 2>&1; echo "build exit $?"
grep -E "PRESET|ERROR" "$WORK/build.log"
"$GODOT" --headless --path "$P" --import > "$WORK/import2.log" 2>&1
echo "== $GODOT --headless --path $P --script res://assets/vfx/godot/tools/load_presets.gd"
"$GODOT" --headless --path "$P" --script res://assets/vfx/godot/tools/load_presets.gd > "$WORK/load.log" 2>&1; echo "load exit $?"
grep -E "LOAD|ERROR" "$WORK/load.log"
echo "== xvfb-run -a -s '-screen 0 1280x720x24' $GODOT --path $P --rendering-driver opengl3 --resolution 1280x720 --fixed-fps 30 --script res://assets/vfx/godot/tools/render_presets.gd -- --out=$OUT"
xvfb-run -a -s "-screen 0 1280x720x24" "$GODOT" --path "$P" --rendering-driver opengl3 --resolution 1280x720 --fixed-fps 30 \
  --script res://assets/vfx/godot/tools/render_presets.gd -- --out="$OUT" > "$WORK/render.log" 2>&1; echo "render exit $?"
grep -E "RENDER|ERROR|OpenGL API" "$WORK/render.log"
echo "frames: $(ls "$OUT" | wc -l)"
