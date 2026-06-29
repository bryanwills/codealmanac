# Slice 57 - Real Codex Ingest Dogfood

Date: 2026-06-29

## Purpose

Move the public-release gate from fake harness confidence to a real Codex
provider run against an isolated repo.

## Scope

- Run `IngestWorkflow` with the real `CodexCliHarnessAdapter`.
- Keep the workspace registry isolated in a temp home.
- Let Codex use the real local login state.
- Verify generated wiki pages through CodeAlmanac read services and CLI
  behavior.
- Patch only issues exposed by dogfood.

## Dogfood Shape

The dogfood created a temp Git repo with:

- `almanac/` initialized by the Python build workflow.
- `notes/auth-boundary.md` as selected source material.
- a committed clean baseline before Ingest.
- a temp registry path at `<temp-home>/.almanac/registry.json`.

The service call shape matched the production boundary:

```python
app = create_app(
    AppConfig(registry_path=temp_home / ".almanac" / "registry.json"),
    harness_adapters=(CodexCliHarnessAdapter(),),
)
app.workflows.build.initialize(InitializeWorkspaceRequest(path=repo))
app.workflows.ingest.run(
    RunIngestRequest(
        cwd=repo,
        inputs=("notes/auth-boundary.md",),
        harness=HarnessKind.CODEX,
    )
)
```

This follows the Cosmic Python service-layer shape: the CLI is not involved,
the composition root wires the real adapter, and the workflow owns the product
use case.

## First Run Finding

The first real Codex run completed and wrote one page under `almanac/pages/`.
The run log recorded lifecycle status plus provider output:

```text
1 status queued ingest
2 status running
3 message verified clean almanac preflight
4 message resolved 1 source
5 message loaded 1 source runtime snapshot
6 output codex succeeded: Added one wiki page:
7 status done
```

The generated page used `[[workos]]` and `[[autumn]]` page links even though
those pages did not exist. `codealmanac health --json` reported both as broken
links. The failure was prompt/manual quality, not workflow architecture.

## Fix

- `src/codealmanac/prompts/base/syntax.md` now says page wikilinks must
  resolve.
- `src/codealmanac/manual/pages.md` now says page links are real wiki nodes,
  not automatic entity markup.
- `src/codealmanac/manual/garden.md` now tells Garden how to repair broken page
  links.
- Prompt/manual tests pin those instructions.

The run also showed starter scaffold health noise from predefined empty topics.
`starter_topics_yaml()` now includes only the `concepts` topic used by the
starter page. A fresh-init health test guards against empty-topic, broken-link,
and dead-reference noise.

## Second Run Evidence

After the prompt/manual fix, a second real Codex run completed with:

- run id `ingest-20260629225644-1b61b756`
- created page `almanac/pages/auth-membership-boundary.md`
- `codealmanac search auth` returned `auth-membership-boundary`
- `health` reported no broken links, no dead refs, and no empty pages
- provider names stayed as plain text instead of dangling page links

The only health item in the second run was the starter scaffold's old
`operations` empty topic, which this slice removes for new initialized repos.

## Verification

- `uv run pytest tests/test_prompts.py tests/test_manual.py
  tests/test_ingest_workflow.py::test_ingest_workflow_resolves_sources_runs_harness_and_refreshes_index`
  passed before the scaffold change.
- `uv run pytest
  tests/test_build_workflow.py::test_initialize_starter_wiki_has_no_health_noise
  tests/test_build_workflow.py::test_initialize_creates_almanac_wiki_and_registry
  tests/test_prompts.py tests/test_manual.py
  tests/test_ingest_workflow.py::test_ingest_workflow_resolves_sources_runs_harness_and_refreshes_index`
  passed after the scaffold change.
- `uv run pytest` passed with 239 tests.
- `uv run ruff check .` passed.
- `git diff --check` passed.
