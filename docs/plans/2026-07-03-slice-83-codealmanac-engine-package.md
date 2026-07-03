# Slice 83: CodeAlmanac engine package boundary

## Goal

Move CodeAlmanac's agent/wiki-update runtime into a first-class
`codealmanac.engine` package.

The open-source repository should make the reusable engine obvious. The hosted
worker should depend on the engine package, not on the human CLI and not on a
grab bag of `services/*` and `workflows/*` modules.

Target shape after this slice:

```text
codealmanac.cloud   # local client surface for CodeAlmanac Cloud
codealmanac.wiki    # repo wiki, registry, read model, viewer
codealmanac.engine  # sources, source bundles, harnesses, engine workspaces, page runs
```

## Scope

Move these packages:

```text
services/source_bundles    -> engine/source_bundles/
services/sources           -> engine/sources/
services/harnesses         -> engine/harnesses/
services/engine_workspaces -> engine/engine_workspaces/
workflows/page_run         -> engine/page_run/
workflows/lifecycle.py     -> engine/lifecycle/__init__.py
workflows/lifecycle_harness.py  -> engine/lifecycle/harness.py
workflows/lifecycle_mutation.py -> engine/lifecycle/mutation.py
```

Update imports in `src/`, `tests/`, and active launch/refactor docs.

Add architecture coverage so old source modules do not come back under
`services/` or `workflows/`.

## Out Of Scope

- Do not move `prompts/` or `manual/` package resources yet. They are packaged
  data and need their own distribution-aware slice.
- Do not move operation workflows (`init`, `ingest`, `garden`, `sync`,
  `local_update`, etc.) yet. Those compose wiki, local, and engine services.
- Do not change CLI command names or output.
- Do not rename classes yet. `HarnessesService`, `SourcesService`,
  `PageRunWorkflow`, etc. stay stable in this slice.
- Do not change local run DB/file formats.
- Do not change provider integrations.

## Design Decisions

- `engine/` owns model execution primitives and the source material fed to the
  model.
- `engine/page_run` owns the shared "run a model against a wiki and record the
  lifecycle" use case.
- `engine/lifecycle` owns mutation safety and harness result normalization.
- Operation workflows remain `workflows/*` for now because they are product
  workflows that call into `wiki`, `local`, and `engine`.
- Integrations may import `codealmanac.engine.*` contracts directly. That is
  the intended port boundary.

## Read Before Coding

- `MANUAL.md`
- `.almanac/README.md`
- `docs/refactor-audit-2026-07-03-hosted-local-architecture/target-architecture.md`
- `docs/reference/cosmic-python/chapter_04_service_layer.md`
- `docs/reference/cosmic-python/chapter_10_commands.md`
- `docs/reference/cosmic-python/chapter_13_dependency_injection.md`

Relevant Cosmic Python transfer:

- service-layer modules define the use cases and sit behind entrypoints;
- commands/request objects capture intent and fail noisily;
- the composition root wires concrete adapters in one place.

## Implementation Steps

1. Create `src/codealmanac/engine/` and subpackages.
2. `git mv` the scoped services/workflows into `engine/`.
3. Rewrite imports from old `services.*` and `workflows.lifecycle/page_run`
   paths to `codealmanac.engine.*`.
4. Update architecture tests and active docs.
5. Run focused tests for harnesses, sources, bundles, engine workspaces,
   page-run lifecycle, init/ingest/garden/sync/local update, and integrations.
6. Run full `uv run ruff check src tests`, `uv run pytest -q --tb=short`, and
   `git diff --check`.

## Verification

Focused:

```bash
uv run pytest \
  tests/test_harnesses_service.py \
  tests/test_sources_service.py \
  tests/test_source_bundles_service.py \
  tests/test_engine_workspaces_service.py \
  tests/test_init_workflow.py \
  tests/test_ingest_workflow.py \
  tests/test_garden_workflow.py \
  tests/test_sync_workflow.py \
  tests/test_run_queue_workflow.py \
  tests/test_local_engine_workflow.py \
  tests/test_local_update_workflow.py \
  tests/test_local_worker_workflow.py \
  tests/test_codex_adapter.py \
  tests/test_codex_app_server_adapter.py \
  tests/test_claude_adapter.py \
  tests/test_web_source_runtime.py \
  tests/test_filesystem_source_runtime.py \
  tests/test_github_source_runtime.py \
  tests/test_transcript_source_runtime.py \
  tests/test_architecture.py \
  -q --tb=short
```

Full:

```bash
uv run ruff check src tests
uv run pytest -q --tb=short
git diff --check
```

## Expected Risk

High import churn, medium behavior risk. The main risks are stale provider
contract imports and architecture tests that still assert old package paths.
