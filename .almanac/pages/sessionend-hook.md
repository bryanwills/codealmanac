---
title: Legacy SessionEnd Hook
summary: Hook-based auto-capture is historical; scheduler-backed quiet-session sync supersedes it.
topics: [agents, flows, cli]
sources:
  - id: automation-command
    type: file
    path: src/cli/commands/automation.ts
    note: Defines the current scheduler-backed automation command surface that supersedes hook-based auto-capture.
  - id: migrate-command
    type: file
    path: src/cli/commands/migrate.ts
    note: Implements `almanac migrate automation` for legacy capture-sweep launchd migration.
  - id: setup-command
    type: file
    path: src/cli/commands/setup/index.ts
    note: Runs legacy hook cleanup during setup while installing scheduler-backed automation.
  - id: uninstall-command
    type: file
    path: src/cli/commands/uninstall.ts
    note: Runs legacy hook cleanup during uninstall.
  - id: legacy-hooks
    type: file
    path: src/platform/automation/legacy-hooks.ts
    note: Detects and removes CodeAlmanac-owned provider hook entries from Claude, Codex, and Cursor configs.
  - id: legacy-capture
    type: file
    path: src/platform/automation/legacy-capture.ts
    note: Detects removed capture-sweep launchd jobs that need migration.
  - id: hook-history-session
    type: conversation
    path: /Users/kushagrachitkara/.codex/sessions/2026/05/11/rollout-2026-05-11T14-32-08-019e18f4-5e73-7790-ba49-73cc02544a58.jsonl
    note: Records the original hook-based auto-capture design and the provider-specific hook names it used.
  - id: sync-refactor-commit
    type: commit
    rev: 6fc4124bec3da04242077dcd01b26482d6f1126d
    note: Renamed the scheduled transcript coordinator from capture sweep to sync and added legacy automation migration.
verified: 2026-06-08
archived_at: 2026-05-13
superseded_by: capture-automation
---

# Legacy SessionEnd Hook

Hook-based auto-capture is no longer the current product path. [[automation]] and [[capture-automation]] supersede it with scheduler-backed quiet-session sync: `almanac automation install` registers OS scheduler jobs, and the sync job periodically runs `almanac sync --quiet <duration>`. The current scheduler-owned automation surface itself is described in [[lifecycle-cli]] and [[install-time-node-launcher]]. [@automation-command] [@sync-refactor-commit]

This page remains only as historical context for cleanup and migration. Earlier versions installed a shared `almanac-capture.sh` command into provider hook configs: Claude used `SessionEnd`, Codex used `Stop`, and Cursor used `sessionEnd`. That shape was removed from onboarding and the public command surface because each provider exposes different lifecycle semantics, and Codex `Stop` is turn-scoped rather than a reliable session boundary. [@hook-history-session] [@sync-refactor-commit]

## Current invariant

Automatic session capture is scheduler-only. `almanac sync` is the only automatic path that decides transcript eligibility, quiet-window timing, cursor dedupe, and Absorb enqueueing. `almanac sync status` is the read-only verification path. No hook path should bypass [[capture-ledger]]. [@sync-refactor-commit]

Setup and uninstall still clean legacy hook entries privately. [[src/platform/automation/legacy-hooks.ts]] removes CodeAlmanac-owned commands whose `command` contains `almanac-capture.sh`, including wrapped and unwrapped hook shapes, while preserving unrelated user hooks. [@legacy-hooks] [@setup-command] [@uninstall-command]

## Legacy shapes to keep cleaning

Future migration code should keep recognizing these observed provider-era shapes:

- Claude: `~/.claude/settings.json` with `SessionEnd`
- Codex: `~/.codex/hooks.json` with `Stop`
- Cursor: `~/.cursor/hooks.json` with `sessionEnd`

The cleanup rule is content-based, not only key-based. It should remove the CodeAlmanac command object, then prune empty wrapper arrays and empty hook containers so setup and uninstall heal old machines in place.

## Debugging posture

When automatic capture does not run, inspect scheduler state first:

```bash
almanac doctor
almanac automation status
almanac sync status --json
almanac jobs
```

Hook config files under `~/.claude/`, `~/.codex/`, and `~/.cursor/` are now legacy cleanup targets, not active CodeAlmanac automation state. If a machine still has `almanac-capture.sh` entries, rerun `almanac setup` or `almanac automation install` to install scheduler-backed sync and clean the old entries. If a machine has `~/Library/LaunchAgents/com.codealmanac.capture-sweep.plist`, run `almanac migrate automation` to replace the removed `capture sweep` launchd job with sync automation. [@legacy-hooks] [@migrate-command] [@legacy-capture]
