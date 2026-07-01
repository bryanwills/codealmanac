# Slice 86: Codex Default And Setup Plan

## Scope

Make the default lifecycle harness match the live agreement and expose setup's
current defaults as typed service facts.

This slice changes:

- default config harness from Claude to Codex
- setup result model to include a `SetupPlan`
- setup terminal/JSON output to render the plan instead of hardcoded next-step
  strings

It does not install automation from setup and does not add interactive raw-mode
selection.

## Why now

The live agreement says the default lifecycle harness is Codex. Current code
still sets `DEFAULT_HARNESS = HarnessKind.CLAUDE`, which means no-flag
`ingest`, `garden`, and `sync` can select the wrong provider unless config
overrides it.

Setup also still hardcodes next-step strings in the renderer. That makes future
target selection, default agent/model selection, and local automation choices
harder to implement cleanly.

Cosmic Python chapter 4 says the service layer captures the use case. Cosmic
Python chapter 10 says commands capture intent. Setup should therefore return
the defaults and recommended follow-up commands as request/result facts, not as
renderer-only text.

## Shape

```python
result = app.setup.run(RunSetupRequest(...))

result.plan.default_harness      # codex
result.plan.instruction_targets  # selected setup targets
result.plan.automation           # sync/garden recommendations
result.plan.next_commands        # renderer + JSON share this
```

## Design decisions

- Keep setup non-interactive in this slice.
- Keep automation installation explicit. Setup recommends commands; it does not
  call `AutomationService.install(...)`.
- Keep update automation out of setup until the update-notification policy is
  reopened.
- Use Pydantic setup models for the shaped plan.

## Verification

- `uv run pytest tests/test_config_service.py tests/test_setup_service.py tests/test_cli.py::test_cli_setup_and_uninstall_codex_instructions tests/test_cli.py::test_cli_setup_skip_instructions_json tests/test_automation_service.py tests/test_public_contract.py`
- `uv run ruff check src/codealmanac/services/config src/codealmanac/services/setup src/codealmanac/services/automation src/codealmanac/cli/render/setup.py tests/test_config_service.py tests/test_setup_service.py tests/test_cli.py tests/test_automation_service.py tests/test_public_contract.py`
- `uv run pytest`
- `uv run ruff check .`
- `git diff --check`
