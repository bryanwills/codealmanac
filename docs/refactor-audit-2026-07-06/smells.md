# Smells

## Setup Rendering Is A Whole Terminal Toolkit In One Module

Classification: redesign.

Evidence:

- `src/codealmanac/cli/render/setup.py` is 612 lines.
- It owns setup result rendering, uninstall rendering, interactive selection
  screens, card layout, visible-length calculation, ANSI constants, banner art,
  text wrapping, and Rich panels.

Why it exists:

Terminal setup polish is a first-class product behavior, and this file grew as
that behavior was restored.

Cost:

The module name says "setup render", but the file also owns generic terminal
layout primitives. Future terminal screens would either copy those helpers or
grow this file further.

Recommendation:

Split by reason to change:

```text
cli/render/setup.py          setup and uninstall result rendering
cli/render/setup_screens.py  interactive setup choice screens
cli/render/terminal.py       ANSI width, wrapping, box/card primitives
cli/render/brand.py          banner, colors, product labels
```

Keep Rich inside `cli/render/`.

## Composition Root Is Honest But Dense

Classification: simplify.

Evidence:

- `src/codealmanac/app.py` is 255 lines.
- `create_app()` wires services, integrations, runtime paths, page-run
  workflows, operation workflows, queue, and sync in one linear function.

Why it exists:

Cosmic Python recommends a composition root so entrypoints do not construct
their own adapters.

Cost:

The function is still readable, but the dependency graph is harder to inspect
than it needs to be. Adding a new workflow now requires finding the right place
inside one long function.

Recommendation:

Keep `app.py` as the public composition root, but introduce small private
factory helpers or a narrow `wiring.py` module only if the helper names match
real groups: `services`, `lifecycle`, `workflows`. Do not create a generic
container framework.

## Architecture Tests Are Both Guardrail And Fossil Layer

Classification: simplify.

Evidence:

- `tests/test_architecture.py` is 1845 lines.
- Many tests assert exact module names, exact imports, exact snippets, and file
  length caps.

Why it exists:

This repo was refactored slice-by-slice, and architecture tests prevented old
mixed modules from regrowing.

Cost:

Exact-fragment assertions make deliberate renames feel like breakage. The tests
sometimes preserve a slice's implementation path instead of only preserving the
boundary.

Recommendation:

Keep architecture tests, but make new or edited tests guard ownership rules:
allowed imports, max file sizes by family, no SQL in services, no Rich outside
render, no integrations above `app.py`, no provider JSON in service models.
Avoid asserting incidental exact strings unless that string is the behavior.

## Facades Need A Higher Bar Now

Classification: keep or delete case-by-case.

Evidence:

- The live agreement intentionally names many facades:
  `services/index/store.py`, `services/index/views.py`,
  `services/harnesses/models.py`, `services/wiki/topics.py`,
  `workflows/lifecycle.py`, and command-family CLI facades.

Why it exists:

Facades preserved stable import surfaces while internals were split.

Cost:

Import-compatible facades can become a polite name for stale compatibility if
callers no longer need them.

Recommendation:

Audit facades one by one. Keep service-facing facades where they are the public
boundary. Delete or inline facades that only preserve old imports and have no
service-facing job.
