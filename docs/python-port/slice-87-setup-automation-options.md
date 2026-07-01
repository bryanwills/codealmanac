# Slice 87: Setup Automation Options

## Scope

Restore the self-managed automation branch of setup in Python form.

This slice adds explicit non-interactive setup flags that install scheduled
sync/Garden automation through the Python automation service:

- `codealmanac setup --yes --install-automation`
- `codealmanac setup --yes --sync-every 2h --sync-quiet 30m`
- `codealmanac setup --yes --install-automation --garden-off`

It also makes uninstall remove scheduler entries by default, with
`codealmanac uninstall --keep-automation` as the escape hatch.

## Out Of Scope

- No hosted setup.
- No scheduled self-update.
- No raw-mode interactive prompts.
- No auto-commit.
- No CLI shell-out from setup to `codealmanac automation install`.

## Why

The live agreement says setup should cover local automation choices. Slice 86
made setup show typed automation recommendations, but users still had to copy a
second command to actually install local sync/Garden automation.

Cosmic Python chapter 10 says, "Commands capture intent." In this slice,
`RunSetupRequest` carries the user's intent to install local automation, and
`SetupService` handles it by calling an automation service port directly.

## Shape

```python
result = app.setup.run(
    RunSetupRequest(
        cwd=repo,
        install_automation=True,
        sync_every=timedelta(hours=5),
        sync_quiet=timedelta(minutes=45),
        garden_every=timedelta(hours=4),
    )
)

result.automation_install  # scheduled jobs installed by AutomationService

removed = app.setup.uninstall(
    RunUninstallRequest(keep_automation=False)
)

removed.automation_uninstall  # scheduler entries removed by AutomationService
```

## Design Decisions

- Explicit setup automation flags install automation now; plain setup still
  recommends commands only.
- Any sync/Garden timing flag implies `install_automation=True`.
- Setup depends on an automation service port, not on the CLI.
- Uninstall removes automation by default because setup can now create it.

## Verification

- Focused setup service and CLI tests.
- Focused automation tests where shared defaults are touched.
- Architecture tests for CLI/service boundaries.
- Isolated live setup smoke with `--install-automation`.
- Full `uv run pytest`, `uv run ruff check .`, and `git diff --check`.
