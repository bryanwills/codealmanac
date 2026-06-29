# Slice 56 - Public Release README

Date: 2026-06-29

## Scope

Replace the stale Node/npm public README with the Python local CodeAlmanac
contract and make that contract executable through public tests.

This slice also records a public-release readiness gate so future work stops
optimizing generic architecture once release proof is the higher-value work.

## Non-Goals

- No publish.
- No hosted CLI.
- No new command.
- No package-manager release automation.
- No viewer redesign.

## Design

`README.md` now documents:

- `codealmanac` as the only public command.
- Python 3.12+ as the runtime.
- `uv tool install codealmanac` and `python -m pip install codealmanac`.
- The default configured root `almanac/`.
- Core read commands, lifecycle commands, sync, automation, jobs, providers,
  configuration, and public-contract exclusions.

`pyproject.toml` now declares `readme = "README.md"` and the Apache-2.0 license
file so package metadata points at the current public contract.

`tests/test_public_contract.py` checks the README contains the Python local
surface and rejects old Node/npm, `almanac`, hosted-dashboard, and `absorb`
language.

## Cosmic Python Transfer

Chapter 5's high-gear testing advice applies here: this is release behavior, so
the test stays at the public contract level rather than pinning README sections
to implementation internals.

## Verification

Initial focused gate:

```bash
uv run pytest tests/test_public_contract.py
uv run ruff check tests/test_public_contract.py
```

Result: 15 tests passed; focused ruff passed.

Full gate:

```bash
uv run pytest
uv run ruff check .
git diff --check
uv build --wheel --no-build-logs --out-dir /tmp/codealmanac-build-slice56
```

Result: 238 tests passed; full ruff passed; diff hygiene passed; wheel built
as `codealmanac-0.1.0-py3-none-any.whl`.

Wheel inspection confirmed:

- README metadata exists as Markdown.
- `LICENSE.md` is recorded as a license file.
- server assets are packaged.
- bundled manual files are packaged.
- prompt files are packaged.

Clean install dogfood installed the wheel into a throwaway Python 3.12 venv,
set an isolated `HOME`, initialized a temp repo, and ran the installed
`codealmanac` binary:

```text
help_has_codealmanac=True
init_stdout=repo
search_stdout=getting-started
show_stdout=# Getting Started
health_keys=['broken_links', 'broken_xwiki', 'dead_refs', 'empty_pages', 'empty_topics', 'orphans']
jobs_stdout=
serve_workspace=repo
serve_page_count=1
```
