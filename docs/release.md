# Release Guide

How to take Perfect Smash from this repository to Google Play. Steps marked **(owner)** need the project owner's
accounts, keys, devices or approval. Everything else is scripted and was verified in a Linux build container on
2026-11-05 (see `changelog.md`).

## 1. Versioning (one source each)

- **Version name:** `application/config/version` in `project.godot` (currently `0.3.0`). The export presets
  leave `version/name` empty so Godot uses it.
- **Version code:** `version/code` in `export_presets.cfg`. It appears once per preset; `tests/test_release_config.gd`
  fails if the presets disagree. Increase it by one for every upload to Play, including internal and closed testing.
- Record each upload's version name, code, commit hash, artifact SHA-256 and approval in `changelog.md`.

## 2. One-time setup on the build machine

1. Godot 4.7.2 with its export templates (Editor → Manage Export Templates).
2. A JDK (17 or newer) and the Android SDK with platform-tools, build-tools and the SDK platform Godot's Gradle
   template targets (API 36 for Godot 4.7.2). Set both paths in Editor Settings → Export → Android
   (`android_sdk_path`, `java_sdk_path`). Godot reads them there, not from `ANDROID_HOME`.
3. `export_presets.cfg` is now committed (it holds no secrets in Godot 4). If you still have an older local,
   untracked copy, move it aside before pulling, or Git will refuse to overwrite it.
4. **(owner) Upload key:** create it once, keep it **outside** the repository, and back it up somewhere safe.
   With Play App Signing, Google holds the app signing key and this upload key can be reset if lost.

   ```bash
   keytool -genkeypair -v -keystore ~/keys/perfectsmash-upload.jks -alias upload -keyalg RSA -keysize 2048 -validity 10000
   ```

## 3. Build

Signing details come only from environment variables (never from files in Git):

```bash
export GODOT_ANDROID_KEYSTORE_RELEASE_PATH=~/keys/perfectsmash-upload.jks
export GODOT_ANDROID_KEYSTORE_RELEASE_USER=upload
export GODOT_ANDROID_KEYSTORE_RELEASE_PASSWORD='…'
```

| Command | Output | Use |
|---|---|---|
| `tools/build_android.sh debug` | `build/perfectsmash-debug.apk` | Emulator/device checks (arm64 + x86_64, debug key) |
| `tools/build_android.sh release-apk` | `build/perfectsmash-release.apk` | Sideloading to testers outside Play (Gradle build) |
| `tools/build_android.sh release-aab` | `build/perfectsmash-release.aab` | **Play upload** (Gradle build; installs `android/build` on first run) |

The script prints the signing certificate and the SHA-256 of the output. Before every build, run the tests:

```bash
godot --headless --fixed-fps 60 -s tests/run_tests.gd
```

## 4. Manual device checklist (owner; plan M0/M4/M5)

Run on at least one physical phone (ideally a low-to-mid-range one) and note the model, Android version and results
in `changelog.md`:

- [ ] Clean install from the release APK/AAB: the app opens to the menu in landscape; the icon looks right in the launcher.
- [ ] Aim and launch with a finger on levels 1, 8 and 20: dragging feels precise, and a tap on a HUD button never fires.
- [ ] Physics stays smooth during the largest collapses (levels 12 and 20). Enable Developer options → Profile GPU rendering if unsure.
- [ ] Each stored solution still wins on the device (see `docs/currentstate.md`, "solutions" known issue).
- [ ] Vibration on hits and wins; turning vibration off in Settings stops it.
- [ ] Sound on/off; the setting persists after force-closing the app.
- [ ] Press Home during a collapse, then return: the game is paused and resumes correctly.
- [ ] Android back: closes Settings, opens/closes pause, and exits from the menu.
- [ ] Phones with a camera cutout or rounded corners: HUD and menu controls are clear of the cutout.
- [ ] Upgrade: install the previous build, play a few levels, install the new build over it, and confirm progress is kept.
- [ ] Settings → Copy play report pastes a readable report into a messaging app.
- [ ] Campaign: mission 1's briefing types out and is **spoken aloud** (release build; the debug APK has no TTS
      query). Each speaker sounds different. Narration off in Settings silences it, and text still shows.
- [ ] Briefings are readable at arm's length, and Skip / Begin mission respond on the first tap.
- [ ] Chapter tabs unlock as chapters are finished; "Continue" opens the next mission's briefing.
- [ ] Play a few missions from each chapter (for example 21, 41, 47, 61, 63, 100) and check the new mechanics:
      bounce pads, explosive chains, drop zones, drones and heavy/blast shots. Explosions and screen shake
      should feel punchy, not uncomfortable.
- [ ] Supply-drop missions (21, 27, 35, 66, 72, 78, 92) need precise aim; note if any feels unfair.

## 5. Play Console (owner)

1. Create the app (name "Perfect Smash", game, free). Enrol in Play App Signing.
2. Store listing: copy from `store/listing.md`; upload `assets/icon/play_store_512.png`, `store/feature_graphic.png`
   and `store/screenshot_*.png`.
3. App content: privacy policy URL (host `store/privacy_policy.md`), ads, data safety, content rating, target
   audience: use `store/play_console_answers.md`.
4. Upload the AAB to **internal testing** first, then **closed testing** (plan §13). Check the pre-launch report for
   crashes and ANRs.
5. Closed testers: ask them to send **Settings → Copy play report** after playing. It gives per-level attempts, wins,
   losses and timeouts without any analytics SDK. Plan §10 retention metrics (D1/D7) come from Play Console statistics.
6. **Production requires explicit owner approval**, recorded in `changelog.md` with the version, code, commit and artifact hash.
   Use a staged rollout if offered.

## 6. Before each release

- Confirm the AAB's merged manifest contains the `android.intent.action.TTS_SERVICE` query, added by
  `addons/android_tts` in Gradle builds; without it, voice narration is silently unavailable on Android 11+.

- Re-check Play's current target-API requirement against the built manifest (Godot 4.7.2 builds target API 36).
- Re-run the data safety review if any permission, SDK or network use changed.
- Re-render store art if the UI changed (`tools/render_store_art.gd`; pick collapse frames with `--probe`).
