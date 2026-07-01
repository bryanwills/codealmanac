# Slice 104: GitHub Source Runtime Boundaries

## Scope

Split `integrations/sources/github/adapter.py` into focused GitHub runtime
modules without changing public behavior:

- `adapter.py` stays the `SourceRuntimeAdapter` implementation and dispatches
  pull-request versus issue inspection.
- `client.py` owns `gh` command execution, timeout/error conversion, JSON
  parsing, and typed payload retrieval.
- `models.py` owns Pydantic models for `gh --json` payloads.
- `rendering.py` owns prompt-facing source-runtime text and titles.
- `targets.py` owns `SourceRef` to `gh` target argument policy.
- `errors.py` owns unavailable-runtime diagnostics.

## Out Of Scope

- No GitHub API feature changes.
- No new GitHub source kinds.
- No move from `gh` CLI to native GitHub API or MCP.
- No source-address parser changes.

## Design Notes

The GitHub adapter reached 413 lines and mixes payload models, process
execution, target argument policy, error shaping, source inspection flow, and
prompt rendering. This is the same integration-boundary pressure that slice 96
fixed for filesystem runtime.

Cosmic Python's service-layer chapter frames ports and adapters as explicit
runtime dependencies: services depend on the port and the real app swaps in the
adapter (`docs/reference/cosmic-python/chapter_04_service_layer.md`). Here the
service-owned port remains `SourceRuntimeAdapter`; the split is inside the
concrete GitHub adapter.

## Files

- `src/codealmanac/integrations/sources/github/adapter.py`
- `src/codealmanac/integrations/sources/github/client.py`
- `src/codealmanac/integrations/sources/github/models.py`
- `src/codealmanac/integrations/sources/github/rendering.py`
- `src/codealmanac/integrations/sources/github/targets.py`
- `src/codealmanac/integrations/sources/github/errors.py`
- `tests/test_architecture.py`
- `docs/python-port-live-agreement.md`
- `docs/python-port/ownership-map.md`
- `docs/python-port/idea-evolution.md`
- `docs/python-port/next-agent-brief.md`
- `docs/python-port/verification-matrix.md`
- `docs/python-port/worklog.md`

## Tests

- Focused GitHub runtime tests.
- Focused ingest GitHub-source test.
- Architecture guard preventing payload models, process execution, and
  rendering helpers from returning to `adapter.py`.
- Fake-runner dogfood through `GitHubSourceRuntimeAdapter`.
- Full `uv run pytest`.
- Full `uv run ruff check .`.

