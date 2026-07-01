# Slice 136: Real Codex App-Server Dogfood

## Goal

Prove the default Codex lifecycle path against the installed real Codex
`app-server`, or fix the first concrete mismatch it exposes.

## Why This Slice

Slices 83, 100, and 101 restored the Codex app-server harness and split the
transport/event boundaries, but their dogfood used a fake app-server executable.
`docs/python-port/next-agent-brief.md` still lists real-provider dogfood for
the richer Codex app-server transport as a likely next pressure point. Local
`codex login status` currently reports `Logged in using ChatGPT`, and
`codex app-server --help` exposes `--listen stdio://`, so the real provider path
can be tested now.

Cosmic Python chapter 13 supports the test shape: use the composition root with
explicit dependencies rather than wiring through the CLI when the goal is to
test an application path with controlled state. This slice uses
`create_app(AppConfig(registry_path=<tmp>))` so the CodeAlmanac registry is
isolated while the real `HOME` remains available for Codex authentication.

## Architecture

Use the real application composition and real Codex provider:

```python
app = create_app(AppConfig(registry_path=temp_registry))
app.workflows.build.initialize(InitializeWorkspaceRequest(path=temp_repo))
result = app.workflows.ingest.run(
    RunIngestRequest(
        cwd=temp_repo,
        inputs=("notes/design.md",),
        harness=HarnessKind.CODEX,
        guidance="...",
    )
)
```

Responsibility split:

- `app.py` composes the real Codex harness.
- `IngestWorkflow` drives the lifecycle.
- `CodexAppServerClient` owns app-server JSON-RPC transport.
- Run logs and health/readback prove the normalized event surface.

## Scope

In scope:

- Run a temp-repo real Codex app-server ingest with a tiny source note.
- Inspect `jobs logs`, `search`, `show`, and `health`.
- Update the verification matrix, next-agent brief, and worklog with exact
  evidence.
- Patch code only for a concrete provider mismatch.

Out of scope:

- Paid broad prompt-quality evaluation.
- Real Claude SDK dogfood.
- Hosted/cloud behavior.
- CLI registry override design.

## Verification

Focused if code changes:

```bash
uv run pytest tests/test_codex_app_server_adapter.py tests/test_codex_adapter.py
```

Dogfood:

```bash
uv run python <temp real-codex-ingest script>
```

Full gate before commit:

```bash
uv run pytest
uv run ruff check .
git diff --check
```

## Outcome

The first real provider run failed after app-server startup and model output
because the installed Codex app-server emitted `item/agentMessage/delta` with
`delta: "\n"`. `HarnessEvent.message` rejects empty text, which is correct for
the normalized event contract. The fix is to drop blank text and plan deltas at
the Codex provider edge.

The rerun passed with real HOME/Codex auth and a temp CodeAlmanac registry. Run
`ingest-20260701163042-e849c0e6` finished `done`, wrote
`webhook-idempotency-invariant.md`, `search webhook` found the page, and every
health category count was zero.
