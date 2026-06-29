# Slice 26: Transcript Source Runtime

## Intent

Foreground `sync` passes ready transcript material to Ingest as
`transcript:<absolute path>`. Ingest should not rely on the harness being able
to read arbitrary provider transcript paths from outside the repo sandbox.

This slice adds a transcript source runtime adapter behind the existing
`SourceRuntimeAdapter` port.

## Scope

- Support `transcript:<path>` when the transcript resolves to a local JSONL
  file.
- Parse JSON Lines with the maintained `jsonlines` package.
- Validate known Codex and Claude transcript shapes with Pydantic models at the
  transcript integration edge.
- Render readable line-numbered transcript material for the Ingest prompt.
- Keep transcript runtime bounded by characters.
- Truncate transcript runtime from the tail, because sync transcript sources
  are append-only and recent lines are usually the new material.

## Out Of Scope

- Cursor-aware source-runtime requests.
- Provider-specific full transcript reconstruction.
- Hosted transcript storage.
- Raw transcript upload.
- Cursor transcript support.

## Design Decision

Use a local runtime adapter, not a sync-specific prompt branch.

`SyncWorkflow` remains responsible for transcript eligibility and cursor
updates. `IngestWorkflow` remains source-kind neutral. The transcript adapter
translates external provider JSONL into `SourceRuntime`, just as Git and GitHub
adapters translate their external shapes.

## Files

- `src/codealmanac/integrations/sources/transcripts/runtime.py`
- `src/codealmanac/integrations/sources/transcripts/__init__.py`
- `src/codealmanac/integrations/sources/__init__.py`
- `tests/test_transcript_source_runtime.py`
- `tests/test_sync_workflow.py`
- steering docs under `docs/python-port/`

## Verification

- Focused transcript runtime tests.
- Sync/Ingest prompt test proving transcript runtime reaches the harness.
- Full pytest.
- Full ruff.
- `git diff --check`.
- Isolated foreground sync dogfood with JSONL transcript runtime material.
