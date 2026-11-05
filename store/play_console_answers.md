# Play Console declarations: suggested answers

Prepared from the actual build (manifest of `build/perfectsmash-release.apk`, 2026-11-05: only
`android.permission.VIBRATE` is requested; no INTERNET permission; `allowBackup=false`; no SDKs beyond the Godot engine
and AndroidX libraries it bundles). The owner submits these, and should re-check them against the final AAB before
each release.

## Data safety

| Question | Answer |
|---|---|
| Does your app collect or share any of the required user data types? | **No** |
| Is all of the user data collected by your app encrypted in transit? | Not applicable (no data is collected or transmitted) |
| Do you provide a way for users to request that their data is deleted? | Not applicable; on-device progress can be erased in Settings → Reset progress, or by uninstalling |

Reasoning: Play's definition of "collect" means data transmitted off the device. The save file stays on the device and
the app has no network permission. The play report is only put on the clipboard when the user taps the button, and
the user decides whether to share it, so it is user-initiated sharing, not app collection.

Voice narration uses the device's own text-to-speech service through Android's standard API. The game passes it
only its own story text. The manifest declares a `<queries>` entry for `android.intent.action.TTS_SERVICE`
(package visibility, not a permission). No personal data is involved, so this doesn't change the answers above.

## Ads

- Contains ads: **No**

## App access

- All functionality is available without special access (no login, no account).

## Content rating (IARC questionnaire)

- Category: **Game** (Puzzle)
- Violence: **No.** Abstract wooden, stone and glass blocks, round "cores" and small drones break apart; orange
  crates explode with a cartoon flash. There are no people, creatures or blood, and the story never depicts harm
  to anyone. Re-check this answer against the IARC wording: "explosions of objects" may count as mild fantasy
  violence in some regions.
- Fear, sexuality, language, controlled substances, gambling: **No**
- User interaction / user-generated content / sharing location / digital purchases: **No**
- Expected result: the lowest age rating in most regions (for example PEGI 3 / ESRB Everyone). The actual rating
  is whatever IARC assigns.

## Target audience and content

- Suggested target age groups: **13–15, 16–17, 18+.** _Owner decision._ Including under-13 groups puts the app in
  Google Play's Families policy. The app would likely comply (no data collection, no ads), but that adds review
  requirements. Choosing 13+ keeps the first release simpler. The game's content is suitable for all ages either way.
- Appeals to children: the visuals are abstract and neutral; answer according to the target-age choice above.

## Government apps, financial features, health, news

- Not applicable (all **No**).

## Privacy policy

- Host `store/privacy_policy.md` at a public URL (for example GitHub Pages or the owner's site) and enter it in
  Play Console → App content → Privacy policy, and in the store listing.
