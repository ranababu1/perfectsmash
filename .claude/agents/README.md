# Temporal: First Jump — specialist agent files

Five Claude Code subagent definitions, one per workstream in the Master Orchestrator directive.

| File | Agent name | Branch | Model / effort |
|---|---|---|---|
| `levels.md` | `levels` | `agent/levels-100` | sonnet / medium |
| `operative-weapons.md` | `operative-weapons` | `agent/operative-weapons` | sonnet / medium |
| `ui-ux.md` | `ui-ux` | `agent/ui-ux` | sonnet / medium |
| `audio-atmosphere.md` | `audio-atmosphere` | `agent/audio-atmosphere` | sonnet / medium |
| `performance-qa.md` | `performance-qa` | `agent/performance-qa` | sonnet / medium |

## Install

Copy the five `.md` files into the repository at `.claude/agents/` and commit them to `main`. They are picked up automatically; no restart needed. The orchestrator can then delegate with the agent name (for example "use the `levels` agent to author VITA 21–40").

Each agent has `isolation: worktree`, so it runs in its own git worktree and switches to (or creates) its own branch on start. Nothing it does touches your checkout or another agent's files.

## Decisions baked into these files

- **Specialists commit, the orchestrator pushes.** The directive says "push after ~50 lines"; the agent files say commit at that cadence and leave pushing/PRs to the orchestrator. Background subagents can't answer permission prompts, so unattended pushes would stall or fail silently anyway. If you do want specialists pushing, delete the "Do not push" sentence in each file and add `Bash(git push:*)` and `Bash(gh pr create:*)` to the allow list below.
- **Destructive git is blocked** by the deny list in `.claude/settings.json`, not just by instruction. (A `disallowedTools` list of `Bash(...)` patterns in the agent frontmatter removed the Bash tool entirely and was dropped on 2026-11-11.)
- **Asset integration is not a specialist job.** The directive's Section 5 "asset agent" isn't one of the five; treat it as an orchestrator Stage 0 task (see edits below).
- **File paths are deliberately generic.** The agents name the shared files from your directive (`project.godot`, `mission_screen.gd`, `mission_view.gd`, `data/integrated_assets.json`, `assets/asset_manifest.json`) but defer to the orchestrator's ownership map for everything else. Once Stage 0 produces that map, paste the concrete owned/forbidden paths into each file's "You own" / "You must not modify" sections.

## Settings to add

In `.claude/settings.json` (project) or `~/.claude/settings.json`:

```json
{
  "permissions": {
    "allow": [
      "Bash(git status:*)",
      "Bash(git branch:*)",
      "Bash(git switch:*)",
      "Bash(git add:*)",
      "Bash(git commit:*)",
      "Bash(git diff:*)",
      "Bash(git log:*)",
      "Bash(godot:*)"
    ],
    "deny": [
      "Bash(git push --force:*)",
      "Bash(git reset --hard:*)",
      "Bash(git rebase:*)",
      "Bash(git filter-branch:*)"
    ]
  }
}
```

Adjust `Bash(godot:*)` to however the headless binary is invoked on your machine (for example `Bash(godot4:*)` or a script in `tools/`).

## Edits to make to the orchestrator directive before pasting it

1. Select **Opus 5.5 at medium effort** for the session yourself (`/model`). The "You: Opus 5.5" line in the prompt doesn't change the model.
2. Replace the opening "Continue from the entire existing conversation" with a pointer to where the decisions live: "Read `CLAUDE.md`, `plan.md` and `currentstate.md` first; they are the record of prior decisions. Do not re-plan what they already settle." Make sure those files actually contain the chapter list, interface decisions and anything else you don't want reopened.
3. In Section 1, add: "The five specialists are defined in `.claude/agents/` as `levels`, `operative-weapons`, `ui-ux`, `audio-atmosphere` and `performance-qa`. Delegate to them by name. Do not implement specialist-scoped work yourself."
4. In Section 4, change the push rule to: "Specialists commit at that cadence on their branch. You pull each worktree, review the diff, push the branch and open the PR."
5. In Section 5, replace "The asset agent" with "You, in Stage 0" so the 1,473-asset integration has an owner.
6. In Section 10, add: "Physical-device validation cannot be performed by any agent. Report it as a human task with exact steps."

## Launching

Paste the amended directive. Stage 0 should produce the baseline report and ownership map before any specialist is invoked. Check that map, paste the concrete paths into the agent files, commit, and then let the orchestrator launch the five workstreams.
