# Slice 20 - Harness Transcript Feedback

Date: 2026-06-29

## Scope

Add the feedback path that lets lifecycle runs remember the provider transcript
they created.

This slice does not execute sync or skip internal transcripts yet. It creates
the typed evidence future sync execution needs.

## Architecture

`HarnessRunResult` now carries:

```python
transcript: HarnessTranscriptRef | None
```

`HarnessTranscriptRef` contains:

- harness kind
- provider session id
- optional transcript path

`RunRecord` now carries:

```python
harness_transcript: HarnessTranscriptRef | None
```

`RunsService.record_harness_transcript(...)` persists the provider transcript
identity independently of terminal run status. Ingest and Garden call it as
soon as a harness returns, before mutation validation or provider-status
validation. Failed lifecycle runs can therefore still be excluded by future
sync execution.

## Provider Behavior

Claude has a structured `session_id` in the JSON result from
`claude -p --output-format json`, so the Claude adapter attaches that session
id directly.

Codex does not expose the run session id in the final-message output. The Codex
adapter therefore performs a best-effort lookup after `codex exec` starts:

- scan Codex `.jsonl` sessions modified after the run started
- parse structured session metadata
- require matching `cwd`
- skip subagent sessions
- return the newest matching transcript

If Codex cannot identify a transcript, the result remains valid with
`transcript=None`.

## CLI Surface

`codealmanac jobs show <run-id>` now prints the stored harness transcript id and
path when present. JSON output includes the same nested Pydantic model.

## Why This Is Separate From Sync Execution

Full sync still needs a skip policy that compares discovered
`TranscriptCandidate` values against recorded internal lifecycle transcript
refs. That policy should be implemented and tested inside `workflows/sync`
before public `codealmanac sync` runs ingest.

## Verification

- focused runs, workflow, adapter, and jobs CLI tests
- full pytest suite
- ruff
- `git diff --check`
- live CLI jobs show smoke with a persisted transcript ref
