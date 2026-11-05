#!/usr/bin/env bash
# Builds Android packages from export_presets.cfg and verifies them.
#
#   tools/build_android.sh debug        -> build/perfectsmash-debug.apk   (debug-signed, arm64 + x86_64)
#   tools/build_android.sh release-apk  -> build/perfectsmash-release.apk (release-signed, for testers)
#   tools/build_android.sh release-aab  -> build/perfectsmash-release.aab (Play upload; Gradle build)
#
# Requirements: Godot 4.7.2 with export templates, a JDK, and an Android SDK with build-tools
# (apksigner, zipalign) and platform-tools. Godot reads the SDK and JDK locations from its editor
# settings (export/android/android_sdk_path, java_sdk_path), not from ANDROID_HOME; this script
# uses ANDROID_HOME only to find apksigner for the final signature check. release-aab also needs
# the SDK platform Godot's Gradle template targets, plus network access for Gradle dependencies.
#
# Signing never reads secrets from the repository:
#   debug:   GODOT_ANDROID_KEYSTORE_DEBUG_{PATH,USER,PASSWORD}; if unset, a local debug keystore is
#            created at ~/.android/debug.keystore with Android's standard public debug credentials.
#   release: GODOT_ANDROID_KEYSTORE_RELEASE_{PATH,USER,PASSWORD} must be set (keystore kept outside Git).
set -euo pipefail

cd "$(dirname "$0")/.."
GODOT="${GODOT:-godot}"
MODE="${1:-}"
mkdir -p build

case "$MODE" in
	debug)       PRESET="Android Debug";       OUT="build/perfectsmash-debug.apk";   FLAG="--export-debug" ;;
	release-apk) PRESET="Android Release APK"; OUT="build/perfectsmash-release.apk"; FLAG="--export-release" ;;
	release-aab) PRESET="Android Release";     OUT="build/perfectsmash-release.aab"; FLAG="--export-release" ;;
	*) echo "usage: $0 debug|release-apk|release-aab" >&2; exit 2 ;;
esac

if [[ -z "${ANDROID_HOME:-}" || ! -d "$ANDROID_HOME" ]]; then
	echo "ANDROID_HOME must point at an Android SDK" >&2
	exit 1
fi

if [[ "$MODE" == debug ]]; then
	if [[ -z "${GODOT_ANDROID_KEYSTORE_DEBUG_PATH:-}" ]]; then
		export GODOT_ANDROID_KEYSTORE_DEBUG_PATH="$HOME/.android/debug.keystore"
		export GODOT_ANDROID_KEYSTORE_DEBUG_USER="androiddebugkey"
		export GODOT_ANDROID_KEYSTORE_DEBUG_PASSWORD="android"
		if [[ ! -f "$GODOT_ANDROID_KEYSTORE_DEBUG_PATH" ]]; then
			mkdir -p "$HOME/.android"
			keytool -genkeypair -v -keystore "$GODOT_ANDROID_KEYSTORE_DEBUG_PATH" -storepass android \
				-alias androiddebugkey -keypass android -keyalg RSA -keysize 2048 -validity 10000 \
				-dname "CN=Android Debug,O=Android,C=US" >/dev/null
		fi
	fi
else
	for v in GODOT_ANDROID_KEYSTORE_RELEASE_PATH GODOT_ANDROID_KEYSTORE_RELEASE_USER GODOT_ANDROID_KEYSTORE_RELEASE_PASSWORD; do
		if [[ -z "${!v:-}" ]]; then
			echo "$v is not set. Release builds need the upload keystore (see docs/release.md)." >&2
			exit 1
		fi
	done
fi

if [[ "$MODE" == release-aab && ! -d android/build ]]; then
	"$GODOT" --headless --install-android-build-template --quit
fi

rm -f "$OUT"
"$GODOT" --headless "$FLAG" "$PRESET" "$OUT"
if [[ ! -s "$OUT" ]]; then
	echo "Export produced no file: $OUT" >&2
	exit 1
fi

if [[ "$OUT" == *.apk ]]; then
	APKSIGNER="$(ls -d "$ANDROID_HOME"/build-tools/*/apksigner 2>/dev/null | sort -V | tail -1)"
	"${APKSIGNER:-apksigner}" verify --print-certs "$OUT" | grep -E "Signer #1 certificate (DN|SHA-256)"
fi
sha256sum "$OUT"
ls -l "$OUT"
