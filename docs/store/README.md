# Store materials — Temporal: First Jump (1.0.0-rc1)

Prepared materials only. The owner submits and publishes.

## Contents

| File | What it is |
|---|---|
| `store-listing.md` | Title, short/full description (with character counts), category, tags, content-rating guidance, release notes, fact box, the chosen phone screenshot set with captions |
| `privacy-policy.md` | Publishable privacy policy (needs the contact address filled in) |
| `data-safety.md` | Answers for Google Play Data safety and Apple App Privacy |
| `screenshots/` | Full-resolution 1920x1080 PNGs (all captures) and `phone/` — the chosen eight as high-quality JPEG |
| `feature-graphic.png` | 1024x500 Google Play feature graphic |
| `promo-still.png` | 1920x1080 promo still |

## Regenerating

From the repo root (needs a desktop GPU window; not `--headless`):

```
godot_console --resolution 1920x1080 --fixed-fps 60 -s tools/release/capture_store.gd -- docs/store/screenshots
python tools/release/make_store_graphics.py
```

`capture_store.gd` boots the real app borderless at 1920x1080 with a throwaway save (`user://capture_store_progress.json`, deleted afterwards) holding some completed missions and Research Data. Pass `scout` as a second argument to dump 960x540 candidates of every shot of the five finales; the moments used are the `MOMENTS` constant. Screenshots are deterministic with `--fixed-fps 60`. Re-view every frame after regenerating — content changes (art, UI) change the frames.

`make_store_graphics.py` (Pillow) composes the feature graphic, promo still and the phone JPEG set from the screenshots and `assets/ui/branding/`.

## Still to do by the owner

1. **Rights approval.** All game art and audio is AI-assisted and every shipped manifest entry is still `pending_review` in `assets/asset_manifest.json`; `docs/release/rights-audit.md` lists them. Nothing here claims the assets are cleared. Screenshots and graphics contain that art, so they are also not cleared until the owner approves it.
2. **Contact address and policy URL.** Replace `<owner contact email>` in `privacy-policy.md`, host it publicly, and enter the URL in the store consoles.
3. **Signing and upload.** Create/own the upload keystore, build the signed release AAB, upload to Play Console (internal testing first).
4. **Data safety / App Privacy / content-rating forms.** Submit using `data-safety.md` and the guidance in `store-listing.md`; verify against the final manifest (VIBRATE only, no INTERNET).
5. **Store listing entry.** Paste text from `store-listing.md`, upload graphics and screenshots, set price/countries.
6. **Human review.** No human play-test exists yet; check the screenshots represent the build you ship.
