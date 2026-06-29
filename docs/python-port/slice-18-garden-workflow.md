# Slice 18: Garden Workflow

## Scope

Add public local Garden execution:

```text
codealmanac garden --using claude
codealmanac garden --using codex --guidance "tighten one topic cluster"
```

Garden maintains the existing repo-owned `.almanac/` graph. It does not start
from selected source inputs. It inspects the current wiki, health report, topic
shape, and page index, then lets a harness make bounded wiki edits.

## Architecture

Garden is a workflow beside Ingest:

```text
cli garden
  -> RunGardenRequest
  -> GardenWorkflow
     -> RunsService
     -> IndexService
     -> HealthService
     -> HarnessesService
     -> LifecycleMutationPolicy
```

The CLI only adapts flags and renders the result. It does not build prompts,
inspect Git, invoke providers, or refresh the index directly.

Prompt text now lives under `src/codealmanac/prompts/` as package resources.
`PromptRenderer` composes base doctrine with an operation prompt and a Pydantic
runtime JSON payload. Ingest and Garden both use that renderer, so operation
doctrine is editable Markdown rather than inline Python strings.

## Mutation Safety

The old ingest-only mutation guard became `LifecycleMutationPolicy`.

The policy still requires:

- Git change tracking
- clean `.almanac/` before the lifecycle run
- no non-wiki mutation during the harness run
- reported harness changes staying under `.almanac/`

The policy is operation-labeled. Ingest failures say `ingest`; Garden failures
say `garden`.

## Cosmic Python Translation

This slice follows the same service-layer shape as Ingest. `GardenWorkflow` is
the use case handler. `PromptRenderer`, `RunsService`, `IndexService`,
`HealthService`, and `HarnessesService` are dependencies supplied by the
composition root.

The important boundary is operation input. Ingest receives selected source
briefs. Garden receives wiki state. Those prompts share doctrine, but the
workflows remain separate command handlers.

## Tests And Dogfood

- `tests/test_prompts.py` covers packaged prompt composition and prompt request
  validation.
- `tests/test_garden_workflow.py` covers run creation, prompt payload contents,
  mutation safety, index refresh, run log events, and operation-labeled Garden
  safety failures.
- `tests/test_cli.py` covers public `codealmanac garden` dispatch and help.
- Full `pytest`, full `ruff`, `git diff --check`, CLI help, and package build
  passed.
- Wheel inspection confirmed prompt Markdown is packaged:
  `base/notability.md`, `base/purpose.md`, `base/syntax.md`,
  `operations/garden.md`, and `operations/ingest.md`.
- Real temp-repo `codealmanac garden --using codex` updated only
  `.almanac/pages/thin-dogfood-note.md` by adding the existing `concepts`
  topic. Search found `thin-dogfood-note`, and the run log recorded queued,
  prepared context, clean preflight, `codex succeeded`, and done.
