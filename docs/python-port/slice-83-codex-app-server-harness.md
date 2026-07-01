# Slice 83 - Codex App-Server Harness

Date: 2026-07-01

## Scope

Make the default Python Codex harness use `codex app-server --listen stdio://`
instead of `codex exec`.

This slice ports the archived app-server behavior that fits the current Python
`RunHarnessRequest` contract:

- three-step JSON-RPC startup: `initialize`, `thread/start`, `turn/start`
- `mcp_servers={}` isolation
- noninteractive approval, permission, elicitation, and user-input responses
- ephemeral provider threads
- workspace-write sandbox policy with network disabled
- root-turn completion handling
- startup RPC timeout and accepted-turn timeout
- normalized `HarnessEvent` mapping for text, tools, warnings, errors, usage,
  provider sessions, and done
- changed-file detection through the existing Git status snapshots

## Non-Goals

- No model/effort/config CLI surface.
- No structured output schema surface yet; Python lifecycle prompts do not
  expose it.
- No skills/MCP/subagent request construction beyond mapping provider-reported
  agent trace events.
- No hosted/cloud behavior.
- No Claude SDK/event harness in this slice.

## Shape

```python
CodexAppServerHarnessAdapter.run(request)
    before = git_status_snapshot(...)
    app_server = CodexAppServerClient(command="codex")
    outcome = app_server.run(request)
    after = git_status_snapshot(...)
    return outcome.with_changed_files(...)
```

The process client stays provider-specific:

```python
client.request("initialize", ...)
thread = client.request("thread/start", ...)
client.request("turn/start", ...)

while not root_done:
    message = client.read_message(timeout)
    if server_request(message):
        client.respond(noninteractive_response(message))
    elif notification(message):
        events += map_codex_notification(message, state)
```

## Cosmic Python Transfer

Chapter 11 frames an external listener as translating outside messages into
application-owned messages. Here, Codex app-server JSON-RPC messages are the
outside shape; `HarnessEvent` is the application-owned message.

Chapter 13 argues for explicit dependencies and a composition root. The default
adapter wiring changes in `integrations/harnesses/__init__.py`, while tests can
still inject fake harness adapters through `create_app(...)`.

## Files

- `src/codealmanac/integrations/harnesses/__init__.py`
- `src/codealmanac/integrations/harnesses/codex/adapter.py`
- `src/codealmanac/integrations/harnesses/codex/app_server.py`
- `src/codealmanac/integrations/harnesses/codex/display.py`
- `src/codealmanac/integrations/harnesses/codex/errors.py`
- `src/codealmanac/integrations/harnesses/codex/events.py`
- `src/codealmanac/integrations/harnesses/codex/failures.py`
- `src/codealmanac/integrations/harnesses/codex/fields.py`
- `src/codealmanac/integrations/harnesses/codex/rpc.py`
- `src/codealmanac/integrations/harnesses/codex/usage.py`
- `tests/test_codex_app_server_adapter.py`
- `tests/test_codex_adapter.py`
- steering docs under `docs/python-port/`

## Verification

Focused:

```bash
uv run pytest tests/test_codex_app_server_adapter.py tests/test_codex_adapter.py tests/test_ingest_workflow.py::test_ingest_workflow_records_normalized_harness_events
uv run ruff check src/codealmanac/integrations/harnesses/codex tests/test_codex_app_server_adapter.py tests/test_codex_adapter.py
```

Broad:

```bash
uv run pytest
uv run ruff check .
git diff --check
```
