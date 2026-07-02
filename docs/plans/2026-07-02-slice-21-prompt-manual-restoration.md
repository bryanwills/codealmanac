# Slice 21 Plan: Prompt And Manual Restoration

Status: implemented.
Date: 2026-07-02.

## Intent

Restore the richer first-build prompt doctrine and manual resource surface that
the Python port compressed, without changing public command behavior yet.

This is the resource prerequisite for making `codealmanac init` the real
agent-backed first-build command in the next runtime slice.

## Product Contract

- Add an `init` operation prompt resource for first-build wiki construction.
- Expand base prompts from the archive doctrine while adapting them to current
  CodeAlmanac names and configured Almanac roots.
- Expand `ingest` and `garden` operation prompts without restoring removed
  public names such as `absorb`.
- Replace the public manual's `build.md` teaching surface with `init.md`.
- Do not yet remove the parser-level `build` command or change runtime behavior
  in this slice.

## Source Material

Read and adapt:

- `archive/code/prompts/base/purpose.md`
- `archive/code/prompts/base/notability.md`
- `archive/code/prompts/base/syntax.md`
- `archive/code/prompts/operations/build.md`
- `archive/code/prompts/operations/absorb.md`
- `archive/code/prompts/operations/garden.md`
- current files under `src/codealmanac/prompts/`
- current files under `src/codealmanac/manual/`

## Implementation Scope

Add or modify:

- `src/codealmanac/prompts/models.py`
  - add `PromptName.OPERATION_INIT`
- `src/codealmanac/prompts/operations/init.md`
- `src/codealmanac/prompts/base/*.md`
- `src/codealmanac/prompts/operations/ingest.md`
- `src/codealmanac/prompts/operations/garden.md`
- `src/codealmanac/manual/models.py`
  - replace `BUILD` with `INIT`
- `src/codealmanac/manual/init.md`
- `src/codealmanac/manual/README.md`
- remove `src/codealmanac/manual/build.md`
- prompt/manual tests

Out of scope:

- removing public `codealmanac build`.
- making `codealmanac init` run the harness.
- queueing `RunOperation.INIT`.
- live foreground/background init execution.
- hosted worker API changes.

## Verification

Focused:

```bash
uv run pytest tests/test_prompts.py tests/test_manual.py tests/test_architecture.py
```

Actual focused gate:

```bash
uv run pytest tests/test_ingest_workflow.py::test_ingest_workflow_resolves_sources_runs_harness_and_refreshes_index tests/test_prompts.py tests/test_manual.py tests/test_build_workflow.py tests/test_architecture.py
```

Result: `87 passed`.

Full gate:

```bash
uv run pytest
uv run ruff check .
git diff --check
```

Result: `458 passed`; ruff and diff-check passed.
