# Data safety answers — Temporal: First Jump

Source: the code audit of version 1.0.0-rc1 on 2026-11-11 (see `privacy-policy.md`). Re-check against the final signed build before submitting. The owner submits the forms; this file only prepares the answers.

## Google Play — Data safety form

| Question | Answer |
|---|---|
| Does your app collect or share any of the required user data types? | **No** |
| Data collected | None |
| Data shared with third parties | None |
| Is all of the user data collected by your app encrypted in transit? | Not applicable — no data is transmitted (the app has no network code and requests no INTERNET permission). If the form insists on an answer: "No data collected". |
| Do you provide a way for users to request that their data be deleted? | Not applicable — nothing is collected. Data stored locally (progress, settings) is deleted by uninstalling the app or clearing app data. |
| Does the app use advertising ID / ads? | No ads; no advertising ID read |
| Independent security review / committed to Families policy | Not claimed |

Notes for the form:
- Local-only data: one file in the app's private storage (`user://progress.json`) with mission results/scores, Research Data, upgrade levels, settings (sound, music, vibration) and seen story sequences. It never leaves the device, so it is not "collected" under Google's definition.
- Permissions: VIBRATE only. (The orchestrator verifies the final manifest separately; confirm before submitting.)
- Privacy policy URL: the owner must host `privacy-policy.md` (after inserting the contact address) at a public URL and enter it in Play Console.

## Apple — App Privacy ("nutrition label")

| Question | Answer |
|---|---|
| Do you or your third-party partners collect data from this app? | **No** |
| Resulting label | **Data Not Collected** |
| Tracking | None (no tracking, no ATT prompt needed) |

Notes: the iOS build is not part of this release; the same facts apply (no SDKs, no network code, local file only), but re-audit the iOS build before submitting. A privacy policy URL is required by App Store Connect as well.
