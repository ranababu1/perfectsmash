# Temporal: First Jump

An angled 2.5D tactical destruction puzzle game for Android (iOS later), built with Godot 4.7.2.
A lone operative is sent back through time to bring down five institutions before their systems end
the world: 100 missions in five chapters, six weapons, real 2D physics under a 3D presentation, story
cinematics, upgrades. Offline, single player.

- **Status:** release candidate `1.0.0-rc1` — see `docs/currentstate.md` and `docs/release/README.md`.
- **Plan and decisions:** `docs/plan.md` (revision 7 is the current owner direction), `docs/narrative-bible.md`, `docs/level-design-spec.md`.
- **Changes:** `docs/changelog.md`. **Contracts:** `docs/interfaces.md`. **Working rules:** `docs/instructions.md`.
- **Levels:** `data/missions/`, authoring guide `docs/levels/authoring-guide.md`, per-chapter tables `docs/levels/`.

## Run and test

```
godot_console --path .                                                   # play (desktop)
godot_console --headless --fixed-fps 60 -s tests/run_tests.gd            # full test suite
godot_console --headless --fixed-fps 60 -s tools/levels/probe_missions.gd -- solve all 3   # every mission's solutions
```

Asset rights: generated assets are AI-assisted and pending the owner's review
(`assets/asset_manifest.json`, `docs/release/rights-audit.md`); no commercial clearance is claimed.
