# Release 1.0.0-rc1 — build, verification and owner hand-off

> **1.0.0-rc2 (candidate, not tagged).** Fixes the three owner-reported issues (weapon fallback,
> Main Menu from pause with Android back, cinematic narration playback) — see `docs/changelog.md`.
> Debug APK: `build/temporal1-1.0.0-rc2-debug.apk` (~216 MB with narration, version name 1.0.0-rc2, code 3; rebuilt 2026-11-12 from `54262f7`), built with
> `python tools/release/make_export_presets.py --version-name 1.0.0-rc2 --version-code 3` then
> `godot_console --headless --export-debug "Android Debug" build/temporal1-1.0.0-rc2-debug.apk`.
> It contains all 50 voice lines and 12 music beds (mix references and review samples excluded).
> Emulator: fresh install plays the narrated opening on the manifest timeline. The release AAB was
> not rebuilt. The `v1.0.0-rc2` tag waits for the owner's listening check and approval.
> The rc1 record below is unchanged.

Release candidate of the complete game: 100 missions in five chapters, six weapons, story
cinematics with a Story Archive, weapon upgrades, offline single player. Tag `v1.0.0-rc1`.

## Artifacts (built locally, not committed: `build/` is gitignored)

| File | What | Signing |
|---|---|---|
| `build/temporal1-debug.apk` | Debug APK, arm64-v8a + x86_64 (emulators), ~198 MB | Godot editor debug key (not the owner's key) |
| `build/temporal1-1.0.0-rc1-release-unsigned.aab` | Release App Bundle, arm64-v8a, ~145 MB (game data in an install-time asset pack; base module ~27 MB) | **Unsigned** — the owner signs it |

Version: `config/version = 1.0.0-rc1`, Android `version/name = 1.0.0-rc1`, `version/code = 2`,
package `dev.imrn.temporal1`. Permissions in the merged manifest: `VIBRATE` only.

## How to rebuild

```
godot_console --headless -s tools/release/export_manifest.gd          # shipped vs excluded assets
python tools/release/make_export_presets.py --version-name 1.0.0-rc1 --version-code 2
python tools/release/rights_audit.py                                   # docs/release/rights-audit.md
godot_console --headless --export-debug "Android Debug" build/temporal1-debug.apk
godot_console --headless --install-android-build-template --export-release "Android Release AAB" build/temporal1-1.0.0-rc1-release-unsigned.aab
```
`export_presets.cfg` and `android/` are local (gitignored); the script regenerates the filters and
the release preset from the debug preset. The first Gradle build downloads dependencies (~10 min).
If Godot does not copy the bundle, it is at `android/build/build/outputs/bundle/standardRelease/build-standard-release.aab`.

**Signing (owner):** sign the AAB with your upload key (e.g. `jarsigner` or Play App Signing via the
Play Console); no keystore path or password is stored in this repository or in the presets.

## Size work done for this release
- 53 shipped music/ambience tracks re-encoded to Ogg Vorbis q1 (126 → 46 MB; same content and
  duration). **Needs a human listening check.**
- Cinematic stills imported lossy (WebP 0.82); 2048 px VFX flipbooks capped at 1024 px.
- Export filters exclude every asset the game does not reference (1,314 paths), including the
  unverified `gameplay_bed.ogg` and its source.

## Verification performed (2026-11-11)
- Headless test suite: 296 passed, 0 failed, 0 skipped.
- Design probe: every mission stands untouched; every recorded solution of all 100 missions wins
  3/3 within its recommended shots (381 replays).
- All 100 missions played through the real app in a window (`tools/levels/capture_campaign.gd`):
  100/100 won; opening and result frames reviewed as contact sheets.
- Desktop frame times (Windows, RTX 5060 Ti, GL Compatibility, 1280x720,
  `docs/benchmarks/campaign_frame_times_desktop.json`): median 6.9 ms, worst per-mission p99
  11.5 ms, one 48 ms hitch across all missions, mission loads median 37 ms (max 423 ms).
- Android **emulator** (Android 17, Pixel 10 Pro image, x86_64, 2856x1280): the debug APK installs
  and runs; opening cinematic → skip → main menu → Continue → chapter I introduction → helix_01
  played by touch (two touches on the controller destroy it) → decision prompt → results. Two bugs
  found there were fixed (touch aim ignored gravity drop; popups pinned to the top edge).

## Not verified (human tasks)
- **Physical Android devices** (performance, thermals, touch feel, aspect ratios, audio). Emulator
  and desktop numbers are not device numbers.
- **iOS**: no macOS environment; the iOS preset exists but no build was attempted.
- **Human play-testing** of the 100 missions (difficulty, clarity, target times are estimates).
- **Listening review** of music/ambience after re-encoding and of the new weapon sounds (built
  from existing library sounds; no dedicated recordings exist).
- **Rights:** every shipped asset is `pending_review` (`docs/release/rights-audit.md`). The game is
  technically complete; **commercial release clearance is not claimed** until the owner approves.
- Store submission, Data-safety form, content rating, privacy-policy hosting (`docs/store/`).
