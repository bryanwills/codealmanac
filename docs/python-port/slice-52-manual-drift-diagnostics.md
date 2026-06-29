# Slice 52 - Manual Drift Diagnostics

Date: 2026-06-29

## Scope

Report workspace manual files that differ from the bundled CodeAlmanac manual
without adding a public manual command or overwriting local edits.

This slice extends the existing manual support-package boundary:

- `ManualLibrary.workspace_status(...)` reports missing and changed manual files.
- `doctor` keeps missing files as a problem with the existing `build` fix.
- `doctor` reports changed manual files as informational drift that requires
  explicit review.

## Non-Goals

- No public `codealmanac manual` command.
- No automatic replacement of existing files under `<almanac-root>/manual/`.
- No hosted manual sync.
- No baseline database for distinguishing package drift from intentional local
  edits.

## Design

Manual files under the configured Almanac root are repo-owned text. The package
manual is the bundled default, but the local copy can contain user edits. Because
the tool cannot tell whether a difference is an intentional local override or an
older bundled copy, the right v1 behavior is diagnostic, not mutation.

`ManualLibrary` remains the support-package owner. It compares each present
workspace manual file with the bundled resource and returns typed status data.
`DiagnosticsService` decides how that status appears in `doctor`.

## Tests

- manual status reports changed files while preserving completeness semantics
- doctor reports changed manual files as informational drift
- CLI doctor renders the drift message through the existing generic doctor
  renderer

## Verification

Focused gate:

```bash
uv run pytest tests/test_manual.py tests/test_diagnostics.py tests/test_cli.py::test_cli_doctor_reports_manual_drift -q
uv run ruff check src/codealmanac/manual src/codealmanac/services/diagnostics tests/test_manual.py tests/test_diagnostics.py tests/test_cli.py
```

Result: 9 tests passed; focused ruff passed.

Full gate:

```bash
uv run pytest
uv run ruff check .
git diff --check
uv build --wheel --no-build-logs --out-dir /tmp/codealmanac-build-slice52
```

Result: 229 tests passed; full ruff passed; diff hygiene passed; wheel built
as `codealmanac-0.1.0-py3-none-any.whl`. Wheel inspection confirmed
`codealmanac/manual/library.py`, `codealmanac/manual/models.py`, and
`codealmanac/manual/README.md`.

Live dogfood used an isolated temp repo and temp `HOME`:

```bash
codealmanac build <repo> --name manual-drift-dogfood
printf 'local manual edit\n' > <repo>/almanac/manual/README.md
codealmanac doctor --wiki manual-drift-dogfood --json
```

Result: `wiki.manual` reported `status: "info"`,
`message: "manual differs: README.md"`, and
`fix: "review local manual files; codealmanac build preserves existing files"`.
