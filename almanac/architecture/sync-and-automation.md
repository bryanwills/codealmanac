---
title: Sync And Automation
summary: Sync scans local transcripts and automation installs local scheduled jobs.
topics: [architecture, operations, cli]
sources:
  - id: sync-dispatch
    type: file
    path: src/codealmanac/cli/dispatch/sync.py
    note: CLI dispatch for sync and sync status.
  - id: sync-service
    type: file
    path: src/codealmanac/workflows/sync/service.py
    note: Sync workflow coordination.
  - id: automation-service
    type: file
    path: src/codealmanac/services/automation/service.py
    note: Automation install, uninstall, and status service.
  - id: automation-jobs
    type: file
    path: src/codealmanac/services/automation/jobs.py
    note: Scheduled job construction.
---

# Sync And Automation

`codealmanac sync` defaults to scanning Claude and Codex transcript sources unless `--from` restricts the app set [@sync-dispatch]. The dispatch layer resolves CLI config, quiet window, pending timeout, failed-attempt budget, harness, foreground/background execution, and claim owner before calling the sync workflow [@sync-dispatch].

`SyncWorkflow` evaluates eligible transcript candidates, creates a claim owner, and delegates execution to `SyncRunExecutor` [@sync-service]. `sync status` runs the same evaluation path without starting ingest work [@sync-service].

Automation installs scheduled jobs through `AutomationService`, which builds task jobs and passes them to the scheduler adapter [@automation-service]. The job factory writes logs under `~/.codealmanac/logs`, uses the Python executable with `-m codealmanac.cli.main`, schedules `sync` without a working directory, and schedules `garden` with the current wiki workspace [@automation-jobs].

Automation is local. It schedules local `sync` and `garden`; it does not install hosted capture, upload, login, or cloud polling.
