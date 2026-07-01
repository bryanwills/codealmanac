# Slice 101: Codex App-Server Client Boundaries

## Scope

Keep `CodexAppServerClient` focused on process orchestration and JSON-RPC
turn flow by moving policy and result helpers out of
`integrations/harnesses/codex/app_server.py`.

This slice changes internal Codex integration structure only. It must not change
the public `HarnessAdapter` contract, app-server startup arguments, sandbox
payload, noninteractive server responses, timeout behavior, normalized event
stream, changed-file reporting, or public CLI behavior.

## Why Now

Slice 100 split Codex app-server notification mapping, but `app_server.py` still
mixes transport orchestration with server-request response policy, sandbox
policy, timeout environment parsing, root-turn completion detection, and
`HarnessRunResult` projection. The repo wiki page
`.almanac/pages/codex-app-server-harness-adapter.md` describes those as separate
responsibilities in the Codex provider boundary.

Cosmic Python chapter 13 frames explicit dependencies as a way to avoid hidden
entrypoint responsibilities. Here, the app-server client remains the explicit
transport dependency while policy helpers become named provider-edge modules.

## Shape

```text
integrations/harnesses/codex/
  app_server.py       # process orchestration and JSON-RPC turn flow
  responses.py        # noninteractive server-request responses
  sandbox.py          # sandbox mode, env parsing, and sandbox policy payload
  turn_completion.py  # root turn completion detection
  run_result.py       # CodexRunState / failure -> HarnessRunResult
```

## Design Decisions

- Keep `noninteractive_response` importable from `codex.app_server` for current
  tests and internal callers by re-exporting it.
- Keep timeout constants with the app-server transport because they bound the
  transport read loop.
- Keep the low-level JSON-RPC process in `rpc.py`; this slice does not change
  subprocess framing.
- Add an architecture guard that prevents `app_server.py` from regrowing
  response policy, sandbox policy, result projection, or env parsing helpers.

## Verification

- `uv run pytest tests/test_codex_app_server_adapter.py tests/test_codex_adapter.py tests/test_architecture.py`
- `uv run ruff check src/codealmanac/integrations/harnesses/codex tests/test_codex_app_server_adapter.py tests/test_codex_adapter.py tests/test_architecture.py`
- Fake app-server client dogfood through `CodexAppServerClient`
- `uv run pytest`
- `uv run ruff check .`
- `git diff --check`
