# Slice 29 - Update Command

Date: 2026-06-29

## Scope

Add the local-only update surface:

```text
codealmanac update
codealmanac update --check
codealmanac update --json
```

This slice closes the CLI-contract gap without adding a background notifier,
scheduled update automation, hosted update checks, dismiss state, or npm-era
behavior.

## Read Before Coding

- `MANUAL.md`
- `.almanac/README.md`
- `docs/python-port-live-agreement.md`
- `docs/reference/cosmic-python/CODEALMANAC.md`
- `docs/reference/cosmic-python/chapter_04_service_layer.md`
- `docs/reference/cosmic-python/chapter_11_external_events.md`
- `docs/reference/cosmic-python/chapter_13_dependency_injection.md`
- uv tool docs: `https://docs.astral.sh/uv/concepts/tools/`
- pip install docs: `https://pip.pypa.io/en/stable/cli/pip_install/`

## Design

`update` is product policy plus external package-manager execution. It should
not live inside CLI rendering, and it should not assume the old npm installer.

```python
request = CheckUpdateRequest()
plan = app.updates.check(request)

request = RunUpdateRequest()
result = app.updates.run(request)
```

`services/updates` owns:

- install metadata models
- update strategy selection
- request/result contracts
- unsupported-install decisions

`integrations/updates` owns:

- reading package metadata from `importlib.metadata`
- running foreground package-manager commands

Supported v1 strategies:

- uv tool install: `uv tool upgrade codealmanac`
- pip install: `python -m pip install --upgrade codealmanac`

Editable/source installs are intentionally unsupported for mutation. In that
case, `update --check` reports the current editable source and `update` exits
without running a command, with a fix message such as `git pull && uv sync`.

Unknown installers are also unsupported. The result should show the detected
installer and the manual commands a user can run.

Update run status reports whether the foreground package-manager command
completed, not whether package files definitely changed. Dogfood showed
`uv tool upgrade codealmanac` can exit 0 with `Nothing to upgrade`; the service
must not scrape package-manager prose to infer a stronger state.

## Tests

- service tests:
  - uv non-editable install plans `uv tool upgrade codealmanac`
  - pip non-editable install plans `python -m pip install --upgrade codealmanac`
  - editable install is unsupported and does not invoke the executor
  - failed executor returns failed result with captured output
- CLI tests:
  - help includes `update`
  - `update --check --json` renders the plan
  - editable default `update` exits non-zero with a clear message
- architecture test remains green: CLI/services do not import integrations.

## Verification Plan

Focused:

```bash
uv run pytest tests/test_update_service.py tests/test_cli.py::test_cli_update_check_json_reports_plan tests/test_cli.py::test_cli_update_refuses_editable_install tests/test_cli.py::test_cli_help_includes_update tests/test_architecture.py
uv run ruff check src/codealmanac/services/updates src/codealmanac/integrations/updates src/codealmanac/app.py src/codealmanac/cli/main.py tests/test_update_service.py tests/test_cli.py
```

Live:

```bash
uv run codealmanac update --check
uv run codealmanac update --check --json
uv run codealmanac update
```

In this repo, the live install is editable, so the default update command
should refuse mutation and exit non-zero.
