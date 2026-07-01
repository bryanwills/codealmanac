# Slice 130: Setup Instruction Boundaries

## Scope

Keep `codealmanac setup` and `codealmanac uninstall` behavior unchanged while
splitting setup-owned agent instruction mechanics by responsibility.

## Out of scope

- No interactive setup prompts.
- No setup output redesign.
- No automation behavior changes.
- No hosted setup, login, upload, or compatibility aliases.

## Design

Cosmic Python chapter 4 describes the service layer as the place for
"orchestrating our workflows and defining the use cases of our system." Setup's
use case belongs in `SetupService`, while filesystem instruction mechanics
belong in the setup integration adapter.

The split is:

```python
integrations.setup.instructions      # service-facing FileInstructionInstaller
  -> guide.py                        # packaged guide resource read
  -> codex.py                        # Codex AGENTS target install/uninstall
  -> claude.py                       # Claude guide/import install/uninstall
  -> managed_blocks.py               # marker block text transforms
  -> text_files.py                   # narrow UTF-8 file helpers
```

This follows chapter 13's dependency-injection pressure: entrypoints and
services should depend on an explicit abstraction, while concrete filesystem
details stay in the adapter.

## Verification

- Existing setup service behavior tests.
- Existing setup CLI behavior tests.
- Architecture guard that prevents `instructions.py` from regrowing provider
  marker and file-edit mechanics.
- Isolated CLI dogfood for setup/uninstall with `HOME="$(mktemp -d)"`.
- Full pytest, Ruff, and diff checks.
