# Slice 85 Review Fixes

## Findings

### Must-fix: remove the `events.py` compatibility facade

`events.py` was split into a thin SDK message dispatcher, but `ClaudeSdkClient`
still imported run-state and result helpers through `events.py`. That kept the
old grab-bag import surface alive after the owning modules existed.

Fix shape:

- `client.py` imports `ClaudeRunState` from `state.py`.
- `client.py` imports `ClaudeMessage` and `session_id_for_message` from
  `sdk_messages.py`.
- `client.py` imports result helpers from `result.py`.
- `events.py` only dispatches one SDK message into normalized events.
- The architecture test rejects result helper exports in `events.py`.

## Verification

- `uv run pytest tests/test_claude_adapter.py tests/test_architecture.py`
- `uv run ruff check src/codealmanac/integrations/harnesses/claude tests/test_claude_adapter.py tests/test_architecture.py`
- `uv run pytest`
- `uv run ruff check .`
- `git diff --check`
