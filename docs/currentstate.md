# Current State

_Last updated: 2026-11-11 · Version **1.0.0-rc2** (candidate, untagged; `v1.0.0-rc1` is the last tag) · Branch `fix/rc2-owner-issues` → PR into `main` · Remote `origin` (github.com/ranababu1/temporal-chapter1)_

Concise handoff. Earlier detailed versions are in Git history (`99f5ee3`, `639b0ec`). Release
procedure, artifacts and the verification record: `docs/release/README.md`. Contracts:
`docs/interfaces.md`. Owner decisions: `docs/plan.md` revision 8 (narration approved; supersedes the
revision 7 narration restriction) and revision 7.

## Purpose and phase

Temporal: First Jump — angled 2.5D tactical destruction puzzle (Godot 4.7.2, 3D presentation over
2D physics, GL Compatibility, Android first, iOS later). **Phase:** release candidate 2: the three
owner-reported issues are fixed (weapon fallback, Main Menu from pause, narration playback), but
**narration is not complete** until the separately prepared narration clips are delivered,
integrated and listened to. Then: owner device testing, signing, rights approval, store submission.

## Feature status

| Feature | Status | Evidence / notes |
|---|---|---|
| Campaign: 100 missions, 5 chapters × 20 | **Complete** | `data/missions/`, set dressing `data/environments/`, recorded solutions `tools/levels/solutions/`, design tables `docs/levels/<chapter>.md`; probe 381/381 wins; 100/100 won through the app |
| Weapons: Kinetic, Breach (I), Penetrator (II), Pulse Cannon (III), Disruptor (IV), Temporal Lance (V) | Complete | rules, physics, presentation, sounds, upgrades; `tests/weapons/` |
| Rules: piercing, material bonuses, EMP, shield emitters, temporal crystal, reactor housing, collapse leaves cores at 1 hp | Complete | `scripts/core/`, `data/materials.json`, `data/weapons.json` |
| Objectives, scoring, Research Data, decision prompt | Complete | `MissionEngine`, `MissionScoring` |
| Upgrades screen | Complete | Main menu → Upgrades; ~85% of all upgrades affordable in a completionist run |
| Story: opening, 5 intros, 4 endings, finale; Story Archive | Complete (subtitles) | stills + pan/zoom + subtitles + music + skip |
| Narration (plan rev. 8) | **Partial: playback integrated, assets pending** | `data/narration.json` (empty, `pending_assets`), `NarrationCatalog`, `CinematicPlayer` voice + music ducking, Settings → Narration volume; 50 expected clips listed in `docs/audio/narration-integration.md` |
| Weapon fallback (empty weapon never stays selected) | Complete | `MissionEngine.select_weapon` / `apply_pending_auto_select`; `tests/weapons/test_weapon_fallback.gd` |
| Pause: Resume / Restart Mission / Main Menu, Android back | Complete | confirmations; leaving records nothing; `tests/campaign/test_pause_navigation.gd` |
| Chapter worlds (lighting/atmosphere per chapter) | Complete | `data/atmospheres.json` |
| Main menu, chapter/mission select (names), settings (sound, music, vibration, narration volume), results | Complete | haptics on fire / blasts / core |
| Save schema v4 (local JSON) | Complete | migrates v1-v3; rc2 adds the optional `settings.narration_volume` |
| Retired slingshot game | Removed from the game | engine-level tests kept |
| Android debug APK | rc2 built 2026-11-11 | `build/temporal1-1.0.0-rc2-debug.apk`, ~198 MB, version code 3 |
| Unsigned release AAB | rc1 only | not rebuilt for rc2 (owner approval of the rc2 scope first) |
| iOS | Not built | no macOS environment |
| Store materials, privacy policy, Data safety | Drafted | `docs/store/` (owner submits) |
| Rights audit | Generated | `docs/release/rights-audit.md`: every shipped asset `pending_review` |

## Build / test status (2026-11-11, rc2 branch)

- Headless suite `godot_console --headless --fixed-fps 60 -s tests/run_tests.gd` → **320 passed, 0 failed, 0 skipped** (296 at rc1 + 24 new).
- `tools/levels/probe_missions.gd -- solve all 3` on the final branch code → exit 0 (100 stand checks OK, 381/381 replays won).
- Android emulator (Android 17, Pixel 10 Pro image, x86_64), rc2 APK installed over rc1: opening skipped with back; Narration volume 50 % saved; helix_01 won by touch; back on results → mission list; helix_02: last Breach charge → automatic switch to Kinetic, empty Breach press keeps Kinetic; back → pause → Main Menu → confirm → back → pause → Main Menu confirmed (save byte-identical); Restart Mission → fresh attempt.
- rc1 evidence still current for unchanged areas: windowed campaign capture 100/100 WIN; desktop frame-time sweep median 6.9 ms, max p99 11.5 ms.
- Asset validator → PASS. Boot smoke → no errors.

## Known issues and risks

- **No physical-device or human play-test** yet: difficulty, aiming feel, target times and performance on phones are unverified.
- **Rights:** AI-assisted art and audio are `pending_review`; commercial clearance not claimed. `gameplay_bed.ogg` (unverified licence) is never shipped.
- **Narration not delivered:** no approved clips exist in the repository; every slide plays subtitles only and the Narration volume slider has no audible effect until clips are mapped. Playback, ducking and sync are tested with stand-in library sounds, not with narration.
- **Audio:** music/ambience re-encoded to Vorbis q1 for size; new weapon sounds reuse library files — needs a listening review.
- Emulator screenshots can lag behind the app (stale frames); device checks used paired captures and the mission clock to confirm state.
- **Curves:** shot curves rise within each chapter but some mid-chapter levels sit at the low end of their bands; many levels have a single recorded line (see `docs/levels/*.md` notes).
- Physics is repeatable on one platform, not bit-identical across platforms.
- `export_presets.cfg` and `android/` are local files (gitignored); regenerate with `tools/release/make_export_presets.py`.
- Stale git worktree registrations from the paused multi-agent setup remain (`git worktree prune` not run).

## Next actions (owner)

0. Deliver the approved narration package; integrate per `docs/audio/narration-integration.md`; listen to sync and ducking; then approve the rc2 scope and the `v1.0.0-rc2` tag.
1. Install the APK on physical Android phones; play a few missions per chapter; report feel and performance.
2. Listen to music, ambience and weapon sounds.
3. Review rights (`docs/release/rights-audit.md`) and approve or replace assets.
4. Sign the AAB, complete the store listing / Data safety / content rating (`docs/store/`), upload to an internal or closed testing track.
5. iOS build on macOS when available.
