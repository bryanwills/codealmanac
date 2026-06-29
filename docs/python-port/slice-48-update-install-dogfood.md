# Slice 48 - Update Install Dogfood

Date: 2026-06-29

## Scope

Dogfood `codealmanac update` from non-editable package installs and tighten the
status contract exposed by the update service.

This slice does not add scheduled update checks, a background notifier,
dismissal state, hosted update policy, or a release-channel mechanism.

## Read Before Coding

- `MANUAL.md`
- `.almanac/README.md`
- `docs/python-port-live-agreement.md`
- `docs/reference/cosmic-python/CODEALMANAC.md`
- `docs/reference/cosmic-python/chapter_04_service_layer.md`
- `docs/reference/cosmic-python/chapter_11_external_events.md`
- `docs/reference/cosmic-python/chapter_13_dependency_injection.md`
- `docs/python-port/slice-29-update-command.md`

## Design

`update` remains a service-layer use case with explicit dependencies:

```python
plan = app.updates.check(CheckUpdateRequest())
result = app.updates.run(RunUpdateRequest())
```

The metadata provider reads package install facts. The command runner executes
the package-manager command. The CLI renders typed plans and results only.

The dogfood changed the result status vocabulary. A package-manager command can
exit 0 without changing installed files: `uv tool upgrade codealmanac` reported
`Nothing to upgrade`. CodeAlmanac should not scrape package-manager prose to
infer whether files changed. A successful foreground package-manager command is
therefore `completed`, not `updated`.

## Dogfood

Pip branch:

- build a wheel into `/tmp`
- create a throwaway Python 3.12 venv
- install the wheel with `python -m pip install ...`
- run `codealmanac update --check --json`
- run `codealmanac update --json` with `PIP_NO_INDEX=1` and
  `PIP_FIND_LINKS=<wheel-dir>`

Expected evidence:

- metadata reports `installer: "pip"`
- plan method is `pip`
- command uses the throwaway venv Python
- actual update command exits 0 with status `completed`

Uv-tool branch:

- set throwaway `UV_TOOL_DIR` and `UV_TOOL_BIN_DIR`
- install the wheel with `uv tool install <wheel>`
- run the installed `codealmanac update --check --json`
- run `codealmanac update --json` with `UV_FIND_LINKS=<wheel-dir>`

Expected evidence:

- metadata reports `installer: "uv"`
- plan method is `uv-tool`
- command is `uv tool upgrade codealmanac`
- actual update command exits 0 with status `completed`

## Verification Plan

Focused:

```bash
uv run pytest tests/test_update_service.py \
  tests/test_cli.py::test_cli_update_check_json_reports_plan \
  tests/test_cli.py::test_cli_update_refuses_editable_install \
  tests/test_cli.py::test_cli_help_includes_update
uv run ruff check src/codealmanac/services/updates \
  src/codealmanac/integrations/updates \
  src/codealmanac/cli/dispatch/root.py \
  tests/test_update_service.py tests/test_cli.py
```

Full gates:

```bash
uv run pytest
uv run ruff check .
git diff --check
uv build --wheel --out-dir /tmp/codealmanac-build-slice48
```
