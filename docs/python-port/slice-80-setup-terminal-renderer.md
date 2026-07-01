# Slice 80 - Setup Terminal Renderer

Date: 2026-07-01

## Scope

Improve the user-facing `setup` and `uninstall` terminal output while keeping
the setup service UI-agnostic:

- add a Rich-backed setup renderer under the CLI edge
- show a branded banner, step-style status rows, and a polished next-step box
- keep `--json` output unchanged and machine-readable
- keep setup/uninstall non-interactive in this slice
- dogfood output under an isolated `HOME`

This slice does **not** add raw-mode target selection, default agent/model
selection, setup-owned automation choices, or scheduler uninstall integration.

## Why Now

Slice 79 restored the setup/uninstall instruction contract, but the terminal
surface is still plain text. The live agreement explicitly says the archived
setup terminal quality is part of the product. The next smallest aligned slice
is presentation quality, because the service seam already exists.

## Shape

```python
result = app.setup.run(request)
render_setup_result(result, json_output=args.json)
```

The renderer delegates to a setup-specific module:

```text
cli/render/setup.py
```

That module may import Rich. Services, workflows, integrations, and stores
must not import terminal UI libraries.

## Decisions

- Use Rich instead of hand-rolled ANSI and box drawing. Terminal UI polish is a
  solved problem, and the user explicitly asked not to hand-roll common library
  behavior.
- Keep JSON rendering through Pydantic `model_dump(mode="json")`.
- Text output should not expose hosted language, `almanac` aliases, or cloud
  setup.
- The next-step box should recommend `codealmanac init`, `codealmanac search`,
  and optional `codealmanac automation install ...`; it should not imply setup
  already installed automation.
- Interactive target selection remains deferred because the repo-level
  anti-pattern section says no interactive prompts while the live agreement
  calls for raw-mode selection. That conflict needs a deliberate later slice
  rather than a rushed prompt implementation.

## Cosmic Python Transfer

Chapter 4 says the service layer defines use cases. Setup output is not a use
case; it is an adapter concern.

Chapter 10 says command requests capture intent and fail noisily. This slice
does not change the `RunSetupRequest` / `RunUninstallRequest` command shape.

Chapter 13 says dependencies should be explicit at the composition boundary.
Rich stays in the CLI renderer and is not injected into the product service.

## Files

- `pyproject.toml`
- `uv.lock`
- `src/codealmanac/cli/render/admin.py`
- `src/codealmanac/cli/render/setup.py`
- `tests/test_cli.py`
- `tests/test_architecture.py`
- `tests/test_public_contract.py`

## Verification

Focused:

```bash
uv run pytest tests/test_cli.py tests/test_architecture.py tests/test_public_contract.py
uv run ruff check src/codealmanac/cli tests/test_cli.py tests/test_architecture.py tests/test_public_contract.py
```

Broad:

```bash
uv run pytest
uv run ruff check .
git diff --check
```

Dogfood:

```bash
HOME="$(mktemp -d)" uv run codealmanac setup --yes --target codex
HOME="$HOME" uv run codealmanac uninstall --yes --target codex
```
