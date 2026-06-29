# Slice 19 - Sync Status

Date: 2026-06-29

## Scope

Add read-only local transcript sync inspection:

```text
codealmanac sync status
codealmanac sync status --from claude,codex --quiet 45m --wiki <name> --json
```

This slice does not run ingest, queue jobs, update the sync ledger, install
automation, or write wiki prose.

## Product Boundary

`sync` means local transcript sweep. It is not hosted upload or cloud sync.

The status command answers:

- which supported transcript stores were scanned
- which quiet transcripts map to repos with `.almanac/`
- which transcript line ranges are ready for a future ingest run
- which transcripts are skipped because they are still quiet, unchanged,
  already pending, unreadable, or cursor-conflicted

## Architecture

```python
# CLI adapts flags only.
summary = app.workflows.sync.status(
    RunSyncStatusRequest(
        cwd=Path.cwd(),
        wiki=args.wiki,
        apps=parse_sync_apps(args.source_apps),
        quiet=parse_quiet(args.quiet),
    )
)
```

`SyncWorkflow` coordinates the product status calculation. It calls
`SourcesService.discover_transcripts(...)`, reads the per-repo sync ledger, and
evaluates cursor state.

`SourcesService` owns the `TranscriptDiscoveryAdapter` port. Concrete Codex and
Claude scanners live under `integrations/sources/transcripts/` and translate
provider JSONL files into typed `TranscriptCandidate` models.

`app.py` is the composition root. It wires transcript discovery adapters into
`SourcesService`, matching Cosmic Python chapter 13's composition-root
guidance. The CLI does not import concrete Codex or Claude transcript scanners.

## Data Shape

`TranscriptCandidate` is a source observation:

- app: `claude` or `codex`
- session id
- transcript path
- transcript cwd
- mapped repo root
- modified time
- size

`SyncLedgerEntry` records the last absorbed cursor for a transcript:

- app and session id
- transcript path
- status
- last absorbed byte size
- last absorbed line
- last absorbed prefix hash

For a new transcript, sync status uses the empty transcript hash as the cursor.
For a known transcript, status validates that the stored prefix still matches
the current transcript bytes before reporting a ready range.

## Duration Parsing

`--quiet` uses `humanfriendly.parse_timespan(...)` instead of hand-rolled
duration parsing. The CLI converts it to `datetime.timedelta` before building
`RunSyncStatusRequest`.

## Why Status Before Execution

Full sync execution needs to avoid ingesting CodeAlmanac's own lifecycle
transcripts. Ingest and Garden now create provider transcripts through Claude
and Codex harness runs, but `HarnessRunResult` and `RunRecord` do not yet carry
the provider session id or transcript path that sync can mark as internal.

Until that feedback loop exists, `sync status` is safe because it is read-only.
`sync` execution remains gated.

## Verification

- focused transcript discovery, sync workflow, CLI, and architecture tests
- full pytest suite
- ruff
- `git diff --check`
- CLI help and JSON status smoke
- package build
- isolated dogfood with a synthetic Codex transcript mapped to a temp repo
