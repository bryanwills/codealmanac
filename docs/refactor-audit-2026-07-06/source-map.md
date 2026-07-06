# Source Map

## Top Level

```text
src/codealmanac/
  app.py
  cli/
  core/
  database/
  integrations/
  manual/
  prompts/
  server/
  services/
  workflows/
```

This top-level shape matches `docs/python-port-live-agreement.md`.

## Dependency Direction

Target direction:

```text
cli/server -> app -> workflows -> services -> stores/ports -> integrations
```

The existing architecture tests already guard the biggest rule: `cli/`,
`workflows/`, and `services/` must not import `codealmanac.integrations`.

## Services

`services/` contains the product nouns. The largest package count is expected:
it holds most business rules and service-owned ports.

Important service boundaries already split well:

- `index`: store facade plus schema, source loading, projection, and query
  views.
- `runs`: store facade plus paths, IO, locks, transitions, factory, queries,
  and streaming.
- `sources`: address resolution and runtime/discovery ports.
- `topics`: service facade plus graph, read model, workspace, and mutation
  mechanics.
- `viewer`: service facade plus workspace scope, projections, renderer, and
  jobs.

## Workflows

`workflows/` contains multi-service verbs:

- `build`
- `ingest`
- `garden`
- `sync`
- `page_run`
- `run_queue`

`PageRunWorkflow` is the shared lifecycle execution seam. This is worth
preserving because it keeps harness execution and mutation safety out of
operation-specific workflows.

## Integrations

`integrations/` implements service-owned ports:

- harnesses: Codex and Claude;
- sources: filesystem, git, github, transcripts, web;
- automation scheduler;
- setup instruction files;
- package updates;
- workspace Git probe.

The provider integrations are split by responsibility and already show the
right general pattern.

## CLI

The CLI is split into:

```text
cli/parser/
cli/dispatch/
cli/render/
```

This split is intentional and documented. The main pressure is not the triad;
it is that some renderer files now own full terminal micro-frameworks.

## First Refactor Candidates

1. `cli/render/setup.py`
   - Reason: multiple output families and terminal-layout helpers in one file.
   - Risk: terminal output is behavior, so preserve byte shape or update tests
     only when tests describe file layout.

2. `app.py`
   - Reason: composition root is honest but hard to scan.
   - Risk: hiding wiring in vague helpers would make the root worse.

3. Architecture tests
   - Reason: valuable boundary tests mixed with exact-fragment tests.
   - Risk: weakening behavior or boundary protection.
