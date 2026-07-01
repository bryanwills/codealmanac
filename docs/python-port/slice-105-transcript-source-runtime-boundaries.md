# Slice 105 - Transcript Source Runtime Boundaries

## Scope

Split the transcript source runtime by responsibility without changing the
public `TranscriptSourceRuntimeAdapter` behavior.

## Why Now

After slice 104, `integrations/sources/transcripts/runtime.py` is the largest
production module. It mixes the adapter port, transcript path resolution,
JSONL reading, Pydantic edge models, known-provider entry normalization,
prompt rendering, and truncation. That shape works today, but it makes the
next transcript-source change feel like editing a grab bag.

Cosmic Python chapter 04 describes the service layer as the main way into an
app and separates orchestration logic from interfacing code. Chapter 10 says
commands capture intent and should fail noisily. Applied here: the source
runtime adapter is the command-facing integration edge; the mechanics behind it
should be named by reason to change.

## In Scope

- Keep `TranscriptSourceRuntimeAdapter` as the package export.
- Move Pydantic transcript JSON and runtime entry models to `models.py`.
- Move path resolution to `paths.py`.
- Move unavailable diagnostics to `errors.py`.
- Move JSONL file reading to `reader.py`.
- Move line-to-entry normalization to `entries.py`.
- Move prompt-facing text rendering and tail truncation to `rendering.py`.
- Add an architecture guard so the adapter does not regrow parsing/rendering
  mechanics.

## Out of Scope

- New transcript providers.
- Cursor transcript support.
- A different normalized transcript event schema.
- Sync ledger behavior changes.
- Raw provider transcript browsing in the viewer.

## Verification

- Focused transcript runtime tests.
- Focused sync/ingest prompt test proving transcript runtime still reaches
  lifecycle prompts.
- Architecture test for transcript runtime module boundaries.
- Full pytest and ruff after docs updates.
