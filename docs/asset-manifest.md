# Asset Manifest

Every shipped non-code asset: source, rights status and how it is used. An asset whose rights are not verified is a **release blocker** even if it is integrated.

| Asset | Source / provenance | Processing | Used by | Rights status |
|---|---|---|---|---|
| `assets/audio/music/gameplay_bed.ogg` | Owner-supplied `bg.mp3` (2026-11-09). Embedded metadata: "made with suno", id `142466df-1693-4ac7-b0ca-3972206ef363`, created 2026-11-09T08:24:39Z. The master stays untracked in `assets/music/` (gitignored, `.gdignore`). | ffmpeg: trimmed near-silent head/tail (−50 dB), Ogg Vorbis q4 (~101 kbps), 197.9 s. Fade-in ≈3 s, fade-out ≈5 s; looped in engine by a 4.5 s self-overlap (`MusicDirector.loop_overlap`). | `main.gd` (gameplay/menu music bed at −12 dB) | **Unverified.** Integrated on the owner's instruction. Commercial use depends on the Suno plan active at generation time; save plan/terms evidence here before release. Listening review for artefacts and fatigue also pending. |
| `assets/ui/branding/app_icon/*` (replaces the legacy `assets/icon/*`, removed 2026-11-10) | ui-vfx stream, code-generated vector art (`assets/ui/_build`) | Rendered PNGs: 256 project icon, 192 launcher, 512 store, Android adaptive foreground, background and monochrome 432 | `project.godot` `config/icon`; Android export preset `launcher_icons/*` (local `export_presets.cfg`) | Original work, AI-assisted authorship; ownership of AI-assisted output not legally settled; not marked commercially cleared. `pending_review`. |
