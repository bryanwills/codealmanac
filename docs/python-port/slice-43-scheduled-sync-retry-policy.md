# Slice 43 - Scheduled Sync Retry Policy

## Scope

Scheduled sync should have an explicit unattended policy without adding a local
queue, hosted worker, or new daemon.

Local automation still launches foreground `codealmanac sync`. The scheduled
command now supplies:

- stable claim owner: `codealmanac.automation.sync`
- pending timeout: `24h`
- failed-attempt budget: `3`

## Shape

```text
AutomationService
  -> ScheduledJob(program_arguments=(..., "sync", "--claim-owner", ...))
  -> CLI dispatch
  -> RunSyncRequest(claim_owner=..., max_failed_attempts=...)
  -> SyncWorkflow
  -> SyncLedgerEntry.failed_attempts
```

`SyncLedgerEntry.failed_attempts` is durable. It increments when an Ingest run
fails or when sync reconciles a linked failed pending run. Successful absorb
resets it to zero.

When a failed entry reaches `max_failed_attempts`, sync returns
`sync-retry-budget-exhausted` as needs-attention instead of retrying forever.

## Tests

- automation install includes stable sync owner, pending timeout, and
  failed-attempt budget in scheduled argv
- failed sync ingest records `failed_attempts = 1`
- exhausted failed entries report `sync-retry-budget-exhausted`
- focused sync, automation, and CLI tests cover the command path

## Cosmic Python Note

Chapter 11's async messaging section shaped this slice: scheduled sync is an
external command source. The adapter should translate that source into explicit
command data before workflow code runs. The workflow still owns the durable
state transition.
