# Next Agent Brief

Status: active.
Updated: 2026-07-02.

## Current Hypothesis

Build the launch in substantial slices. Each slice needs a plan, code, focused
verification, launch-folder updates, commit, and push.

## Last Completed Slice

Slice 21 restored prompt and manual resources for init-first-build.

Implemented:

- `PromptName.OPERATION_INIT`
- packaged prompt resource `src/codealmanac/prompts/operations/init.md`
- expanded base prompt resources from the archive doctrine
- expanded ingest and garden prompts
- bundled `manual/init.md`
- `ManualDocumentName.INIT`
- removal of bundled `manual/build.md`

Verified:

```text
uv run pytest tests/test_ingest_workflow.py::test_ingest_workflow_resolves_sources_runs_harness_and_refreshes_index tests/test_prompts.py tests/test_manual.py tests/test_build_workflow.py tests/test_architecture.py
uv run pytest
uv run ruff check .
git diff --check
```

## Next Pressure Test

Choose the next substantial slice from the launch plan. Good candidates:

- runtime half of init-first-build:
  remove public `build`, add full `init` flags, and route foreground init
  through the harness-backed page-run lifecycle
- local run storage bridge from repo-local job files to the control DB, if
  needed for compatibility
- cloud public API/auth slice in `codealmanac-hosted`

Before coding, write the next slice plan under `docs/plans/`, then implement
the full slice, update this brief, update `progress.md`, send a RelayForge
progress update, commit, and push.

## Known Repo State

The branch is `dev`. At the end of Slice 21 verification it was ready to
commit on top of `origin/dev`.

The local wiki command currently fails on this checkout with:

```text
almanac: table pages has no column named archived_at
```

Use source files and launch docs as the authority until the wiki index health is
repaired.
