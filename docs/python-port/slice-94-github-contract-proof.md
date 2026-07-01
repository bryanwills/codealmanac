# Slice 94 - GitHub Contract Proof

Date: 2026-07-01

## Purpose

Close the small verification gap left after slice 93 moved GitHub automation to
Python.

## Finding

The new workflow commands were correct, but two proof gaps remained:

- `uv sync --locked` had not been run locally after wiring it into CI.
- The bug-report template still said "Describe what you expected Almanac to
  do."
- The public-contract test searched GitHub text, but it did not parse workflow
  YAML to prove the files kept the expected top-level workflow shape.

## Design

Keep this as a contract slice:

```text
tests.test_public_contract
  -> parse .github/workflows/*.yml with ruamel-yaml
  -> assert each workflow has name, on, jobs
  -> assert CI/package workflows still expose the Python gate commands
  -> assert templates use CodeAlmanac wording where they mean the product
```

Do not add an actionlint dependency or a local GitHub Actions runner. The
current risk is stale project-surface drift, not full Actions emulation.

## Cosmic Python Note

Chapter 5 says service-layer tests reduce coupling because they check the API
that other entrypoints drive. Here, `.github/` is a public project entrypoint,
so the useful test is a high-level public-contract check over the files a
maintainer sees, not a narrow test for the implementation details of GitHub
Actions.

Reference: `docs/reference/cosmic-python/chapter_05_high_gear_low_gear.md`.

## Verification Plan

- `uv sync --locked`
- `uv run pytest tests/test_public_contract.py`
- `uv run ruff check tests/test_public_contract.py`
- `uv run pytest`
- `uv run ruff check .`
- `git diff --check`
