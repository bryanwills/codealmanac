# Slice 107 - CLI Render Facade Split

## Scope

Split `cli/render/root.py` into domain render modules while preserving the
existing render function names imported by dispatchers.

## Why Now

After slice 106, `cli/render/root.py` became the largest production file. It
mixes lifecycle output, sync summaries, workspace registry rows, page display,
topic mutations, health reports, tagging, and shared formatting helpers.

The CLI edge already has parser/dispatch/render packages. This slice makes the
render package match that shape internally: root is a facade, domains own their
presentation functions.

## In Scope

- Move shared formatting helpers to `cli/render/common.py`.
- Move lifecycle renderers to `cli/render/lifecycle.py`.
- Move workspace list/drop renderers to `cli/render/workspaces.py`.
- Move page/search/topic/health/tagging renderers to `cli/render/wiki.py`.
- Keep `cli/render/root.py` as a small re-export facade so dispatch imports do
  not churn.
- Add an architecture guard that prevents `root.py` from regrowing rendering
  logic or service model imports.

## Out of Scope

- Rich terminal redesign.
- Output text changes.
- Dispatch or parser command changes.
- JSON output format changes.

## Verification

- Focused CLI tests for read/lifecycle/admin surfaces.
- Architecture guard for render package shape.
- Ruff over CLI render and dispatch.
- Public CLI smoke.
- Full pytest, Ruff, and diff hygiene.
