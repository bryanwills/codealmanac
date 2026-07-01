# Slice 82 - Rich Harness Event Logs

Date: 2026-07-01

## Scope

Finish the Python harness event contract so job logs can preserve the archived
provider event model:

- structured tool display details
- actor/root/helper attribution
- usage and context-window counts
- provider session ids
- provider failure metadata
- agent trace events
- raw provider payloads when an adapter needs lossless debug material

This slice keeps the existing text `jobs logs` output stable. JSON logs gain an
optional `harness_event` object beside the readable `kind` and `message`.

## Non-Goals

- No Codex app-server transport in this slice.
- No Claude SDK event-stream port in this slice.
- No viewer transcript redesign.
- No hosted/cloud job history.

## Why Now

The live agreement says CodeAlmanac's inspectable transcript surface is the
normalized harness event stream, not raw provider transcript files. Current
Python only records `kind`, `message`, and terminal status, so an app-server or
Claude SDK adapter would still lose tool details, usage, actor ids, and provider
session ids after the run returns.

## Shape

Adapters return service-owned events:

```python
HarnessEvent(
    kind=HarnessEventKind.TOOL_USE,
    message="Reading file",
    actor=HarnessRunActor(...),
    tool_display=HarnessToolDisplay(kind=HarnessToolDisplayKind.READ, ...),
)
```

The run log stores both display and structured data:

```json
{
  "kind": "tool",
  "message": "Reading file",
  "harness_event": {
    "kind": "tool_use",
    "message": "Reading file",
    "tool_display": {"kind": "read", "path": "almanac/pages/auth.md"}
  }
}
```

## Cosmic Python Transfer

Chapter 11 says an outside listener translates from the outside world to our
events (`docs/reference/cosmic-python/chapter_11_external_events.md`). That is
the adapter job for Codex/Claude provider notifications.

Chapter 8 says events help "isolate concerns"
(`docs/reference/cosmic-python/chapter_08_events_and_message_bus.md`). This
slice isolates provider detail in `HarnessEvent` while keeping run storage and
CLI display provider-neutral.

Chapter 10 separates commands from events. Lifecycle run execution remains the
command; individual provider notifications are facts recorded as events
(`docs/reference/cosmic-python/chapter_10_commands.md`).

## Files

- `src/codealmanac/services/harnesses/models.py`
- `src/codealmanac/services/runs/models.py`
- `src/codealmanac/services/runs/requests.py`
- `src/codealmanac/services/runs/service.py`
- `src/codealmanac/services/runs/store.py`
- `src/codealmanac/cli/render/admin.py`
- `src/codealmanac/workflows/page_run/service.py`
- `src/codealmanac/workflows/lifecycle.py`
- `tests/test_ingest_workflow.py`
- `tests/test_runs_service.py`
- `tests/test_cli.py`
- `docs/python-port/next-agent-brief.md`

## Verification

Focused:

```bash
uv run pytest tests/test_ingest_workflow.py tests/test_runs_service.py tests/test_codex_adapter.py tests/test_claude_adapter.py tests/test_cli.py::test_cli_jobs_inspects_local_run_records
uv run ruff check src/codealmanac/services/harnesses src/codealmanac/services/runs src/codealmanac/workflows src/codealmanac/cli/render/admin.py tests/test_ingest_workflow.py tests/test_runs_service.py tests/test_cli.py
```

Broad:

```bash
uv run pytest
uv run ruff check .
git diff --check
```
