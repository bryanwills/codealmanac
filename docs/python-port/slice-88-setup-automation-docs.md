# Slice 88: Setup Automation Docs

## Scope

Update user-facing documentation after slice 87 made setup capable of
installing scheduled local automation.

This slice changes:

- `README.md` setup docs
- `docs/concepts.md` command group summary
- public contract tests that guard those docs
- steering docs for the Python port

## Why

The code now supports:

```bash
codealmanac setup --yes --install-automation
codealmanac setup --yes --sync-every 5h --sync-quiet 45m
codealmanac uninstall --yes --keep-automation
```

`README.md` still says setup does not install scheduled automation. That is now
false user-facing guidance.

Cosmic Python chapter 4 frames the service layer as the main way into the app.
For this project, public docs are part of that entrypoint contract: they should
describe the service behavior the CLI exposes, not stale implementation history.

## Out Of Scope

- No new CLI behavior.
- No hosted setup wording.
- No raw interactive setup prompts.
- No scheduled update automation docs.

## Verification

- Focused public-contract tests.
- README examples parse where relevant.
- Full `uv run pytest`, `uv run ruff check .`, and `git diff --check`.
