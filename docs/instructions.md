# Development Instructions

## 1. Purpose and authority

This file defines the mandatory engineering workflow for this project. Follow it for every implementation task, whether the work is performed by a human developer or an AI coding agent.

- `plan.md` is the original product and engineering plan. Treat it as an immutable baseline. Do not silently rewrite, restructure, or replace it as the project evolves.
- If implementation requires a material departure from `plan.md`, document the rationale, alternatives, risks, and approval in `changelog.md` and `currentstate.md`. Change `plan.md` only when the project owner explicitly requests a revision. Preserve the original plan history if an approved revision is made.
- `changelog.md` and `currentstate.md` are required living documents. Create and maintain them from the beginning of development.
- Do not state or imply that a feature is implemented, tested, released, or measured until evidence supports that claim.

## 2. AI-agent operating protocol

Before editing:
1. Read `instructions.md`, `currentstate.md`, the relevant sections of `plan.md`, and the latest `changelog.md` entries.
2. Inspect the current branch, working tree, project structure, toolchain version, and available tests.
3. Identify user changes and preserve them. Never overwrite unrelated edits.
4. State the smallest coherent implementation plan, the files expected to change, and the validation commands.
5. Search for an existing implementation before creating a new one. Prefer a focused change over a broad refactor.

While editing:
- Implement only the requested scope. Do not introduce accounts, remote services, analytics SDKs, ads SDKs, dependency frameworks, or architectural layers without a documented need and approval.
- Follow the established architecture and naming conventions. Explain any new dependency or architectural decision in the changelog.
- Keep gameplay rules deterministic and separable from rendering, input, audio, and platform APIs.
- Treat the approved production target as Android + iOS, with mobile performance and battery efficiency as the primary quality goals.
- The current renderer is Compatibility. The proposed production renderer is Godot Mobile, subject to the renderer evaluation in `plan.md`. Do not switch the production renderer until the evaluation is complete and evidence is recorded.
- For renderer changes, preserve a reproducible Compatibility baseline and compare Mobile on representative physical Android and iOS devices. Validate actual GPU/backend support rather than assuming OS version or API level guarantees it.
- Do not change minimum supported Android/iOS versions, renderer defaults, rendering method, or export presets without recording the compatibility evidence and obtaining owner approval.
- Keep renderer-specific effects optional or provide a tested fallback where a feature is unsupported. Do not couple gameplay rules or physics behavior to a rendering backend.
- Use seeded random number generation whenever reproducibility is important for puzzle generation, challenge generation, or tests.
- Handle errors explicitly. Do not swallow exceptions or add empty catch blocks.
- Never fabricate test output, build results, performance numbers, store status, or feature completion.
- Do not add TODOs as a substitute for implementation. If work is intentionally deferred, record it in `currentstate.md`.

Before committing:
1. Run formatting, static analysis/lint, compilation/export checks, and relevant automated tests available for the changed scope.
2. Review `git diff` and `git diff --cached`; inspect every changed file for accidental edits, debug code, credentials, generated files, and unrelated changes.
3. Update `changelog.md` with meaningful implementation details, fixes, test evidence, and any user-visible changes.
4. Update `currentstate.md` with what is actually implemented, current architecture, known issues, test/build status, outstanding work, and next steps.
5. Ensure the working tree contains no unrelated changes staged by the agent.
6. Commit using a focused, descriptive message. Do not add AI co-author trailers.
7. Push according to the Git rules below and verify the push succeeded.

## 3. Buildability and Git workflow (mandatory)

- Work on the intended existing branch unless the project owner explicitly authorizes a branch change. Do not create or switch branches without checking the repository's existing workflow and obtaining authorization where required.
- Preserve all pre-existing user changes. Do not discard, reset, stash, or overwrite them without explicit permission.
- Keep the project buildable at all times. Prefer small, coherent, compilable increments.
- **Push after every file change that leaves the solution buildable, or when approximately 50 lines of production code have changed since the previous push, whichever comes first.** Do not wait for the 50-line threshold when a completed file change leaves the project buildable. For documentation-only changes, use a focused commit and push after the requested documentation update is complete.
- After each push, verify success using the Git command output and, where available, the remote branch status. Report the commit hash and verification result accurately.
- Review diffs before committing. Use focused, descriptive commit messages such as `feat: add seeded puzzle generator` or `fix: prevent duplicate score submission`.
- Do not use AI co-author trailers in commit messages.
- Never run destructive operations such as `git reset --hard`, `git clean -fd`, force-push, history rewriting, or branch deletion without explicit authorization.
- Do not amend or rewrite shared commits unless explicitly authorized.
- Push only to the configured remote and intended branch. If no remote is configured, credentials are unavailable, or the push is rejected, do not invent success; explain the blocker and the exact next step.

## 4. Repository hygiene and security

- Never commit secrets, API keys, access tokens, signing keys, passwords, private certificates, production credentials, personal data, or databases containing user data.
- Never commit build outputs, exported APKs/AABs, caches, editor state, temporary files, crash dumps, or generated artifacts that should be excluded. Store release binaries in the release process or approved artifact storage, not as ordinary source files.
- Ensure `.gitignore` covers the selected Godot or Flutter toolchain, IDE/editor files, OS files, caches, build/export output, local secrets, and local test artifacts.
- Use environment variables or local, ignored configuration for any future credentials. No secrets should be embedded in the client app.
- Request only permissions required for an explicitly approved feature. Explain why each permission is necessary.
- Minimize collection and retention of user data. Do not introduce a backend merely to store data that can safely remain on-device.
- Review dependencies for maintenance status, licensing, permissions, size, platform compatibility, and security before adoption. Pin or constrain versions appropriately and document them.
- Do not collect advertising IDs, contact lists, location, or other sensitive data unless the owner approves a clearly justified use case and the store disclosures are updated.

## 5. Coding standards and architecture

- Keep gameplay/domain logic independent from scene nodes, widgets, platform APIs, networking, analytics, and presentation code where practical.
- Use descriptive names, small cohesive functions, explicit types where supported, and constants for tuning values. Avoid unexplained magic numbers.
- Separate content/configuration from logic when this improves balancing or testing; avoid overengineering a data-driven framework before there is a concrete need.
- Prefer deterministic, reproducible logic for scoring, challenge generation, puzzle validation, and save migrations.
- Handle pause/resume, app backgrounding, screen rotation where relevant, low-memory recovery, and interrupted sessions deliberately.
- Make touch targets comfortable for phones, respect system insets, support common aspect ratios, and ensure essential text remains legible.
- Do not block the main thread with expensive work. Profile before adding concurrency or optimization complexity.
- Add comments for non-obvious constraints and algorithms, not comments that merely restate the code.
- No hard-coded user-facing strings if localization is planned for the current milestone. Keep initial localization scope explicit.

## 6. Testing requirements

Every meaningful change must have tests proportionate to risk. At minimum, add or maintain automated tests for:
- Core gameplay rules and state transitions.
- Scoring, combo, move/attempt limits, failure and success conditions.
- Puzzle validity, solvability, and generator edge cases where applicable.
- Progression and difficulty/configuration boundaries.
- Save-state persistence, loading, invalid/corrupt data handling, and schema migration where applicable.
- Daily challenge determinism and date/time boundary behavior where applicable.
- Reproducible bug regressions.

Also perform practical device/manual checks for touch input, pause/resume, audio settings, screen sizes, accessibility/contrast, and performance. Test on physical Android and iOS devices before a production release. For the renderer evaluation, compare Compatibility and Mobile using the same representative scenes and repeatable test conditions. Record device model, OS version, GPU, renderer/backend, frame pacing, thermal behavior, memory observations, visual differences and limitations. A skipped test must be labeled skipped with a reason, not passed.

## 7. Versioning and release management

- Keep application version name and version code/build number in one authoritative place per toolchain; avoid conflicting duplicate values.
- Use semantic versioning for product-facing versions where suitable: `MAJOR.MINOR.PATCH`. Increment Android version code monotonically for every uploaded release.
- Keep debug, internal testing, closed testing, and production configuration distinct.
- Never publish directly to production without explicit release approval.
- Before Android release, verify package/application ID, app name, icon, orientation, target SDK and current Google Play requirements, privacy policy and Data safety answers, content rating, ads declaration, permissions, signing, crash-free startup, save migration, and release notes.
- Before iOS release, verify the exported Xcode project, supported iOS deployment target, Metal renderer/backend, bundle identifier, signing team, provisioning, entitlements, privacy declarations, App Store requirements and TestFlight upgrade behavior. Final iOS builds/signing/submission require macOS with Xcode; do not claim iOS release validation from a Windows-only export.
- Keep signing credentials outside Git and use a secure local or CI secret store. Never send signing secrets to an AI agent.
- Build and test a release candidate, install it on a clean device/profile, verify upgrade behavior from the previous version, and retain reproducible build instructions.
- Document the exact artifact filename, version name, version code, commit hash, test evidence, and release approval. Never claim a Play listing or release exists before it does.

## 8. Documentation maintenance

### `changelog.md`
Record meaningful changes in reverse chronological order. Each entry should include:
- Date and version/commit when known.
- Summary of changes and implementation details.
- User-visible impact and relevant fixes.
- Tests/build/export commands actually run and their outcomes.
- Known regressions, migration notes, dependency changes, and release notes where relevant.

Do not log every trivial keystroke. Do log changes that alter behavior, architecture, dependencies, release readiness, or known issues.

### `currentstate.md`
Keep this concise, accurate, and useful as a handoff document. It must include:
- Project purpose and current phase.
- Actual implementation status by feature (implemented, partial, planned, blocked).
- Architecture and important files/modules.
- Toolchain and dependency versions if verified.
- Current build/test/export status, including the last verified date and exact commands.
- Known issues, risks, and unimplemented items.
- Next recommended actions in priority order.
- Current version/branch/commit when known.
- Decisions or deviations requiring owner approval.

Update both files in the same implementation increment as the code change whenever feasible, before committing. Do not mark a feature implemented merely because it is described in `plan.md`.

## 9. Definition of done

A task is done only when:
- Scope and acceptance criteria are met.
- Code is buildable and relevant tests pass, or any blocked/skipped validation is clearly explained.
- `changelog.md` and `currentstate.md` accurately reflect the change.
- `plan.md` remains unchanged unless the owner explicitly approved a revision.
- Diff and staged diff have been reviewed.
- No secrets or excluded artifacts are included.
- A focused commit has been created and the configured push has been verified, or the exact reason pushing could not be completed is reported.


## 10. Owner-approved gameplay direction (2026-11-09)

The owner has explicitly approved a major gameplay revision. This section and the latest owner-approved revision in `docs/plan.md` supersede older instructions that describe a slingshot/one-projectile game, prohibit new weapon classes, or exclude multiplayer from the product roadmap.

### Product direction
- Product: Temporal: First Jump.
- Repository: `https://github.com/ranababu1/temporal-chapter1`.
- Canonical branch: `main`.
- Application ID / bundle ID: `dev.imrn.temporal1`.
- Engine: Godot 4.7.2; Android + iOS.
- Gameplay: angled 2.5D tactical destruction puzzle, visible anonymous operative, multiple weapons, story-specific structures, hybrid upgrades.
- Preserve the existing 2D physics architecture for the initial prototype. Do not convert to full 3D physics without a validated technical case and explicit owner approval.

### Approved implementation priorities
1. Greybox an angled 2.5D Helix facility with a visible operative, one Kinetic Accelerator, one Breach Charge, distinct structural objects and a critical AI core.
2. Validate readability, aiming, physics and mobile performance before bulk asset production.
3. Build a reusable data-driven weapon framework. New weapon classes are approved in principle, but implement incrementally and validate each tactical role.
4. Replace generic block presentation with reusable story-specific institutional components and a small material vocabulary. Calibrate actual physics values; do not infer them from visual labels.
5. Support complex multi-stage facilities that may require 15, 25 or more shots where justified. Recommended shot budgets are scoring benchmarks, not universal hard caps.
6. Separate regular Mission Points from bonus Research Data. Research Data funds weapon upgrades. Reward speed and shot efficiency relative to level-specific targets without making speed the only scoring factor.
7. Use automatic chapter technology unlocks plus player-controlled weapon upgrades. Keep base campaign content reasonably completable without upgrades and do not require multiplayer for campaign progression.

### Leaderboards and Temporal Frontlines
- Leaderboards are approved for a later online phase, after scoring and upgrades are stable. Include global, friends, chapter, level, weekly challenge and multiplayer categories as appropriate.
- Provide Standard and Competitive conditions so progression upgrades do not make every ranking incomparable.
- Temporal Frontlines is the approved working name for asynchronous asymmetric multiplayer.
- Builders create persistent institutions using predefined modular components on a validated grid, construction budgets and defensive modules.
- Attackers attack a versioned saved snapshot while the builder is offline. No simultaneous online session is required.
- Persist structured, versioned institution data, not a live Godot scene.
- Backend authority is required for accounts, structure validation, match state, results, rankings and rewards. Do not trust client-reported scores.
- Plan attack reports/replay reconstruction, repair/recovery windows and limits against repeated raids.
- Real-time synchronized multiplayer physics is not part of the approved initial scope.
- Multiplayer must not block the first single-player campaign release. Do not add backend SDKs, accounts or networking to the greybox prototype without the appropriate implementation milestone and owner approval.

### Documentation and status discipline
Update `plan.md`, `currentstate.md` and `changelog.md` when these decisions affect implementation. Update `level-design-spec.md` for weapon, shot-budget, target and scoring constraints. Update visual/art guidance for the angled operative/weapon/institution identity. Describing an approved feature does not mean it is implemented; mark it planned until code and tests prove otherwise.

## 11. Batch 5 working rules (2026-11-10)

### Physics tolerances
- Pure scoring maths is deterministic: exact-value tests (`test_scoring.gd` golden breakdown).
- Godot 2D physics is repeatable for identical input on one platform but not bit-identical across platforms (Windows vs Android emulator: 0.4516 vs 0.4519 structural damage, +1 physics frame). Physics tests assert damage-state categories, exact equality only within one run, and the scripted replay within ±0.01 structural damage and ±15 Mission Points of the Windows reference (`tests/test_mission_world.gd`).
- Do not force bit-identical physics at the cost of gameplay. Future leaderboard validation uses plausibility bounds per score term, not server re-simulation.
- Re-measure the replay reference (`tools/regression/score_replay.tscn`) whenever physics, materials or the Helix layout change, and record the commit in the test comment.

### Balance evidence
- Gameplay tuning must be backed by the probes: `tools/regression/tactics_probe.gd` (Breach/Kinetic sweeps), `collapse_probe.gd` (core damage by cause), `rack_comparison.gd --sweep` (layout variants, kinetic-only finish aimed with the arc preview). Layout variants live in `probe_layouts.gd`; the shipped data is never edited by a probe.
- Report what the probe measured, including results that contradict a proposal.

### Renderer and device benchmarks
- Build eval copies with `tools/renderer_eval/make_eval_project.py --main res://tools/renderer_eval/mission_benchmark.tscn`. Record the source commit, check that `adb install` printed `Success`, and record the package `lastUpdateTime`. A run on a stale install is not evidence.
- Keep logs and JSON reports under `docs/benchmarks/<date>-<topic>/`. Emulator results are smoke tests; never report them as physical-device validation.

### Assets from the `assets` branch
- `assets` is owned by the asset stream. Never merge it into `main`, never modify or delete it.
- Integrate only owner-approved files, selected individually (`git checkout origin/assets -- <path>`), at their delivered `assets/...` paths, keeping their manifest ids. Carry the manifest entries (rights, approval status, source) with them.
- Development integration is not commercial clearance: never change `rights_status` or `approval_status` to cleared.
- The asset contract (`assets/docs/ASSET_CONTRACT.md`) is binding for scale, axes, pivots, depth, material slots and damage-state nodes.
