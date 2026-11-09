# Renderer Evaluation — Compatibility vs Mobile (M3)

**Status:** In progress. Harness built and verified on desktop and the Android emulator. **Physical Android and iOS measurements: not yet done (blocked: no device attached, no Mac).**
**Production renderer:** unchanged, GL Compatibility. No production setting, export preset or minimum OS version has been changed.

## 1. Method

`tools/renderer_eval/` contains:
- `benchmark.gd` / `benchmark.tscn`: drives the real app root and records each scenario's frame-interval distribution (avg, p50, p95, p99, max, % frames over 18.3 ms, frames over 33.3 ms), viewport CPU and GPU render time (GPU timestamps, 0 where unsupported), draw calls, static and video memory, startup time (engine start → first frame) and per-level load time. Writes JSON to `user://renderer_eval/` and one `RENDER_EVAL_*` log line per scenario (readable via `adb logcat -s godot`).
- `make_eval_project.py`: copies the project into an **isolated folder outside the repo**, sets the renderer, makes the benchmark the main scene, and uses its own user dir and its own Android package `dev.imrn.temporal1.rendereval`, so it installs next to the real game. Optional `--soak-minutes N` adds N one-minute sustained stress segments for thermal drift.

Scenarios (identical for both renderers):

| Scenario | Content | Kind |
|---|---|---|
| `menu_idle` | Level-select menu, 6 s | Real |
| `level_ordinary_L01` | First level, solution shot, 8 s | Real |
| `destruction_L20_grand_collapse` | Chapter I finale, solution shot, 12 s | Real |
| `destruction_stress_synthetic` | 72 blocks + 3 targets, 3 max-power shots, 12 s | Synthetic level, real physics |
| `background_parallax_proxy` | Three translucent full-screen 1920×1080 layers drifting | Proxy for chapter art |
| `particles_shaders_proxy` | 4 × 96 GPU particles, full-screen ripple shader, screen-reading distortion | Proxy for VFX |
| `cinematic_proxy` | Two 1920×1080 slides, Ken Burns zoom, cross-fade, outlined subtitle | Proxy for cinematic player |

Proxies exist because chapter art, VFX and cinematics are not built yet. Re-run with real assets once the vertical slice exists.

### Commands

```
python tools/renderer_eval/make_eval_project.py --variant compatibility --out <dir>/eval-compatibility
python tools/renderer_eval/make_eval_project.py --variant mobile --out <dir>/eval-mobile [--soak-minutes 10]
godot_console --path <dir>/eval-<v> --headless --import
godot_console --path <dir>/eval-<v>                                          # desktop
godot_console --path <dir>/eval-<v> --headless --export-debug "Android Eval" <dir>/eval-<v>/build/eval.apk
adb install -r <dir>/eval-<v>/build/eval.apk
adb shell monkey -p dev.imrn.temporal1.rendereval -c android.intent.category.LAUNCHER 1
adb logcat -s godot | grep RENDER_EVAL
adb exec-out run-as dev.imrn.temporal1.rendereval cat files/renderer_eval/<file>.json > <file>.json
```

For each physical device also record before/after a 10-minute soak: `adb shell dumpsys battery` (level, temperature), `adb shell dumpsys thermalservice` (status), and screen brightness fixed at the same level for both runs. Keep the device unplugged for battery observations.

## 2. Results so far (2026-11-09, Godot 4.7.2)

### Windows desktop: functional smoke only (i7-14700K, RTX 5060 Ti, 144 Hz, vsync)

| Scenario | Compat p99 / max ms | Compat GPU ms | Mobile p99 / max ms | Mobile GPU ms |
|---|---|---|---|---|
| menu_idle | 7.14 / 9.08 | 0.12 | 7.79 / 30.47 | 0.05 |
| level_ordinary_L01 | 7.30 / 8.20 | 0.16 | 19.31 / **265.39** | 0.05 |
| destruction_L20 | 7.28 / 8.17 | 0.17 | 7.78 / 8.69 | 0.05 |
| destruction_stress | 7.67 / 8.27 | 0.14 | 8.08 / 30.48 | 0.07 |
| parallax_proxy | 7.13 / 7.31 | 0.21 | 7.78 / 9.42 | 0.09 |
| particles_shaders_proxy | 7.28 / 9.63 | 0.19 | 7.87 / **124.56** | 0.10 |
| cinematic_proxy | 15.29 / 82.95 | 0.20 | 16.00 / **137.40** | 0.09 |

Startup to first frame: Compatibility 699 ms, Mobile 1162 ms. Static memory peak: 46.2 MB vs 53.4 MB.

### Android emulator `Pixel10Pro` (x86_64, host-GPU translation): functional only

- Compatibility: OpenGL ES 3.1 via the emulator GLES translator. GPU timestamps unavailable (reported 0).
- Mobile: **Vulkan 1.3, Forward Mobile**, via Goldfish GFXStream. GPU timestamps available.
- Both complete every scenario without errors. Both show ~55 fps with p99 ≈ 35–40 ms, which is the emulator's own frame pacing. The stress scenario drops to ~46–48 fps on both, with Mobile spikes up to 109 ms.
- Eval APK size: Compatibility 57.8 MB, Mobile 62.3 MB (both arm64 + x86_64, debug).

**None of these numbers predict phone performance.** They show the harness works and that both renderers initialise on Android.

## 3. Preliminary observations (to confirm on devices)

1. **First-use hitches on Mobile.** Mobile shows one-off 120–265 ms frames the first time a new material, particle or shader is drawn (pipeline compilation), where Compatibility stays under 10 ms. On phones this would be a visible stutter at level start, on the first impact effect and at cinematic transitions. Mitigation if Mobile is adopted: pre-warm effects on a loading screen.
2. **Both renderers hitch at the first subtitle draw** (~80–140 ms in `cinematic_proxy`), consistent with font glyph rasterisation. The cinematic player should pre-render its fonts/glyphs before the first slide.
3. Current game content is very light (procedural 2D, under 300 draw calls, GPU under 0.3 ms on desktop). The renderer choice will matter mainly for chapter artwork, VFX and cinematics, and for battery and thermal behaviour, which only physical devices can show.
4. Mobile costs ~0.5 s more startup, ~7 MB more memory and ~4.5 MB more APK on desktop/emulator.

## 4. Device matrix required before a decision

| Class | Example | Why |
|---|---|---|
| Android low-end | Mali-G52/G57 or Adreno 610 class, Android 10–12 | Vulkan driver quality is weakest here; Compatibility may be required |
| Android mid | Adreno 6xx/7xx, Mali-G68/G710 | Main audience |
| Android high | Recent Pixel / Galaxy S | Thermal behaviour at high refresh rates |
| iPhone older supported | A13/A14 class | Metal baseline |
| iPhone recent | A16+ | ProMotion frame pacing |
| iPad | Any recent | Aspect ratio + Metal |

For each: device, OS, GPU, active renderer/driver (from `RENDER_EVAL_ENV`, never inferred), JSON report for both variants, 10-minute soak, battery % and temperature delta, and visual differences noted from screenshots.

## 5. Current recommendation

Keep **Compatibility** as production. Evidence so far gives no performance reason to switch for the current content, and Mobile shows first-use pipeline hitches. Revisit when (a) physical-device data exists and (b) the M5 vertical slice provides real chapter art, VFX and cinematic content to measure. Any change requires owner approval.
