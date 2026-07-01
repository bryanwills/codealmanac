# Slice 79 - Setup and Uninstall Instruction Foundation

Date: 2026-07-01

## Scope

Restore the first setup/uninstall layer in the Python product:

- add `codealmanac setup`
- add `codealmanac uninstall`
- install setup-owned Codex and Claude global agent instructions
- remove only setup-owned instruction artifacts on uninstall
- keep both commands idempotent and non-interactive with `--yes`
- expose JSON and text output through the existing admin CLI edge

This slice does **not** add raw-mode selection, provider auth/model selection,
local automation choices, auto-update scheduling, Cursor/Windsurf/OpenCode
instruction targets, or hosted setup wording.

## Why Now

The live agreement says setup and uninstall were not intentionally dropped.
The archived behavior made setup feel like a real product surface, while the
current Python CLI still lacks the command. The highest-value first slice is
the durable instruction contract because it is small, testable, and reverses
cleanly through uninstall.

## Shape

```python
result = app.setup.run(RunSetupRequest(targets=(SetupTarget.CODEX,)))
result = app.setup.uninstall(RunUninstallRequest(targets=(SetupTarget.CODEX,)))
```

The service owns the product command and result model. The filesystem adapter
owns agent-specific files:

```text
services/setup/
  models.py
  ports.py
  requests.py
  service.py

integrations/setup/
  instructions.py
```

`app.py` wires the adapter into `SetupService`; CLI dispatch builds Pydantic
requests and renders returned models.

## Decisions

- Public setup target values are `codex`, `claude`, and `all`.
- `all` installs Codex and Claude instructions. Future targets can extend the
  enum and adapter contract when they become concrete.
- Codex receives an inline managed block in `~/.codex/AGENTS.md` or
  `~/.codex/AGENTS.override.md` when the override file exists and is non-empty.
- Claude receives `~/.claude/codealmanac.md` plus an import line in
  `~/.claude/CLAUDE.md`.
- Managed markers use `<!-- codealmanac:start -->` and
  `<!-- codealmanac:end -->`.
- Uninstall removes only current `codealmanac` instruction artifacts. Old
  `almanac` artifacts may belong to a separate product install and are not
  Python v1 compatibility scope.
- `--skip-instructions` makes setup an honest no-op for this slice.
- `--keep-instructions` makes uninstall leave the instruction layer alone.
- Scheduler removal will be added when setup owns local automation choices.

## Cosmic Python Transfer

Chapter 4 says the service layer captures the use case. Setup/uninstall are
use cases, so they belong behind `SetupService`, not inside argparse handlers.

Chapter 10 says commands capture intent and fail loudly. `RunSetupRequest` and
`RunUninstallRequest` are command-shaped request models.

Chapter 13 recommends a composition root for explicit dependencies. `app.py`
wires the real filesystem installer, while tests can inject a fake installer.

## Files

- `src/codealmanac/services/setup/`
- `src/codealmanac/integrations/setup/`
- `src/codealmanac/app.py`
- `src/codealmanac/cli/parser/admin.py`
- `src/codealmanac/cli/dispatch/admin.py`
- `src/codealmanac/cli/render/admin.py`
- `tests/test_setup_service.py`
- `tests/test_cli.py`
- `tests/test_architecture.py`

## Verification

Focused:

```bash
uv run pytest tests/test_setup_service.py tests/test_cli.py tests/test_architecture.py tests/test_public_contract.py
uv run ruff check src/codealmanac/services/setup src/codealmanac/integrations/setup src/codealmanac/app.py src/codealmanac/cli tests/test_setup_service.py tests/test_cli.py tests/test_architecture.py
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
HOME="$HOME" uv run codealmanac setup --yes --target codex
HOME="$HOME" uv run codealmanac uninstall --yes --target codex
```
