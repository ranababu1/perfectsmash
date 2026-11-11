# Current State

_Last updated: 2026-11-11 · Version **1.0.0-rc1** (release candidate) · Branch `release/1.0` → `main` · Remote `origin` (github.com/ranababu1/temporal-chapter1)_

Concise handoff. Earlier detailed versions are in Git history (`99f5ee3`, `639b0ec`). Release
procedure, artifacts and the verification record: `docs/release/README.md`. Contracts:
`docs/interfaces.md`. Owner decisions: `docs/plan.md` revision 7.

## Purpose and phase

Temporal: First Jump — angled 2.5D tactical destruction puzzle (Godot 4.7.2, 3D presentation over
2D physics, GL Compatibility, Android first, iOS later). **Phase:** release candidate of the
complete game. Technically complete; awaiting the owner's device testing, signing, rights approval
and store submission.

## Feature status

| Feature | Status | Evidence / notes |
|---|---|---|
| Campaign: 100 missions, 5 chapters × 20 | **Complete** | `data/missions/`, set dressing `data/environments/`, recorded solutions `tools/levels/solutions/`, design tables `docs/levels/<chapter>.md`; probe 381/381 wins; 100/100 won through the app |
| Weapons: Kinetic, Breach (I), Penetrator (II), Pulse Cannon (III), Disruptor (IV), Temporal Lance (V) | Complete | rules, physics, presentation, sounds, upgrades; `tests/weapons/` |
| Rules: piercing, material bonuses, EMP, shield emitters, temporal crystal, reactor housing, collapse leaves cores at 1 hp | Complete | `scripts/core/`, `data/materials.json`, `data/weapons.json` |
| Objectives, scoring, Research Data, decision prompt | Complete | `MissionEngine`, `MissionScoring` |
| Upgrades screen | Complete | Main menu → Upgrades; ~85% of all upgrades affordable in a completionist run |
| Story: opening, 5 intros, 4 endings, finale; Story Archive | Complete | stills + pan/zoom + subtitles + music + skip; no voice |
| Chapter worlds (lighting/atmosphere per chapter) | Complete | `data/atmospheres.json` |
| Main menu, chapter/mission select (names), settings (sound, music, vibration), results | Complete | haptics on fire / blasts / core |
| Save schema v4 (local JSON) | Complete | migrates v1-v3 |
| Retired slingshot game | Removed from the game | engine-level tests kept |
| Android debug APK / unsigned release AAB | Built 2026-11-11 | ~198 MB / ~145 MB; `docs/release/README.md` |
| iOS | Not built | no macOS environment |
| Store materials, privacy policy, Data safety | Drafted | `docs/store/` (owner submits) |
| Rights audit | Generated | `docs/release/rights-audit.md`: every shipped asset `pending_review` |

## Build / test status (2026-11-11)

- Headless suite `godot_console --headless --fixed-fps 60 -s tests/run_tests.gd` → **296 passed, 0 failed, 0 skipped**.
- `tools/levels/probe_missions.gd -- solve all 3` → exit 0 (100 stand checks OK, 381 replays won).
- Windowed campaign capture (`tools/levels/capture_campaign.gd`, 1280x720, fixed 60 fps) → 100/100 WIN.
- Desktop frame-time sweep (`tools/perf/campaign_frame_times.gd`, RTX 5060 Ti) → median 6.9 ms, max p99 11.5 ms.
- Android emulator (Android 17, x86_64): APK runs; opening → menu → chapter intro → helix_01 won by touch → results.
- Asset validator → PASS. Boot smoke → no errors.

## Known issues and risks

- **No physical-device or human play-test** yet: difficulty, aiming feel, target times and performance on phones are unverified.
- **Rights:** AI-assisted art and audio are `pending_review`; commercial clearance not claimed. `gameplay_bed.ogg` (unverified licence) is never shipped.
- **Audio:** music/ambience re-encoded to Vorbis q1 for size; new weapon sounds reuse library files — needs a listening review.
- **Curves:** shot curves rise within each chapter but some mid-chapter levels sit at the low end of their bands; many levels have a single recorded line (see `docs/levels/*.md` notes).
- Physics is repeatable on one platform, not bit-identical across platforms.
- `export_presets.cfg` and `android/` are local files (gitignored); regenerate with `tools/release/make_export_presets.py`.
- Stale git worktree registrations from the paused multi-agent setup remain (`git worktree prune` not run).

## Next actions (owner)

1. Install the APK on physical Android phones; play a few missions per chapter; report feel and performance.
2. Listen to music, ambience and weapon sounds.
3. Review rights (`docs/release/rights-audit.md`) and approve or replace assets.
4. Sign the AAB, complete the store listing / Data safety / content rating (`docs/store/`), upload to an internal or closed testing track.
5. iOS build on macOS when available.
