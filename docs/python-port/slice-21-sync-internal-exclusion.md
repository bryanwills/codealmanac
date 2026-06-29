# Slice 21 - Sync Internal Transcript Exclusion

Date: 2026-06-29

## Scope

Make `codealmanac sync status` skip transcripts created by CodeAlmanac's own
lifecycle runs.

This slice does not add write-capable `codealmanac sync`. It proves the shared
eligibility gate that live sync must use before it can run Ingest.

## Architecture

`SyncWorkflow` now depends on `RunsService` as well as `SourcesService` and
`SyncLedgerStore`.

For each candidate repo, sync loads local run records once and checks any
stored `RunRecord.harness_transcript` refs before cursor evaluation.

A transcript is internal when:

- provider kind matches the discovered transcript app
- the provider session id matches, or the stored transcript path matches

Internal transcripts are skipped with:

```text
internal-lifecycle-transcript
```

## Why Status Owns The Filter

`sync status` is the read-only preview of the same gates that live sync will
use. If status reports a CodeAlmanac maintenance transcript as ready, a future
write-capable sync path would either duplicate the logic or spend model tokens
on its own maintenance exhaust.

## Next Boundary

The next slice can add live `codealmanac sync` by reusing this eligibility
path, then recording pending cursor state before invoking Ingest. It should
not bypass `SyncWorkflow.status(...)` semantics in CLI code.

## Verification

- focused sync workflow tests
- full pytest suite
- ruff
- `git diff --check`
- isolated sync-status dogfood where an internal transcript is skipped and an
  ordinary transcript remains ready
