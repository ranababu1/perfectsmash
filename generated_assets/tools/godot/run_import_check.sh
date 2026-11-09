#!/usr/bin/env bash
# Godot 4.7.2 import and load check for every manifest asset.
# 1. Copies the repo working tree (without .git and .godot) into a persistent temp project.
# 2. Runs `godot --headless --import` there (incremental: the temp .godot cache is kept).
# 3. Runs load_check.gd, which loads every manifest glb/png/webp/ogg/wav/font and reports failures.
# Usage: generated_assets/tools/godot/run_import_check.sh [report.json]
set -euo pipefail
REPO="$(cd "$(dirname "$0")/../../.." && pwd)"
GODOT="${GODOT:-/opt/tfj-tools/bin/godot}"
WORK="${TFJ_GODOT_WORK:-/tmp/tfj-godot-check/project}"
REPORT="${1:-/tmp/tfj-godot-check/load_report.json}"
mkdir -p "$WORK" "$(dirname "$REPORT")"
# Fresh copy of the working tree, keeping only the temp project's .godot import cache.
find "$WORK" -mindepth 1 -maxdepth 1 ! -name .godot -exec rm -rf {} +
tar -C "$REPO" --exclude=./.git --exclude=./.godot --exclude=./tests/output -cf - . | tar -C "$WORK" -xpf -
echo "== $("$GODOT" --headless --version)"
echo "== import: $GODOT --headless --path $WORK --import"
set +e
"$GODOT" --headless --path "$WORK" --import > /tmp/tfj-godot-check/import.log 2>&1
IMPORT_RC=$?
# Godot 4.7.2 headless import has been seen to segfault (139) once on a large first
# reimport and then pass cleanly on the next, incremental run. Retry once, and say so.
if [ "$IMPORT_RC" -eq 139 ]; then
  echo "== import crashed with exit code 139 (segfault); retrying once"
  "$GODOT" --headless --path "$WORK" --import > /tmp/tfj-godot-check/import.log 2>&1
  IMPORT_RC=$?
fi
set -e
sed "s/\x1b\[[0-9;]*m//g" /tmp/tfj-godot-check/import.log | grep -E "^(ERROR|SCRIPT ERROR|WARNING)" | sort | uniq -c | sort -rn | head -40 || true
echo "== import exit code $IMPORT_RC"
echo "== load: $GODOT --headless --path $WORK --script res://generated_assets/tools/godot/load_check.gd -- --report=$REPORT"
set +e
"$GODOT" --headless --path "$WORK" --script res://generated_assets/tools/godot/load_check.gd -- --report="$REPORT" 2>&1 | grep -E "LOADCHECK|ERROR" | head -80
LOAD_RC=${PIPESTATUS[0]}
set -e
echo "== load exit code $LOAD_RC, report $REPORT"
[ "$IMPORT_RC" -eq 0 ] && [ "$LOAD_RC" -eq 0 ]
