# Slice 110 - Viewer Service Boundaries

## Intent

Keep the local `serve` product behavior unchanged while making the viewer
service easier to extend. `serve` already has the agreed multi-wiki scope:
default viewer responses expose available registered local wikis, and
`serve --wiki` narrows the viewer to one wiki. The current pressure is that
`services/viewer/service.py` owns workspace fallback, registry filtering,
page/topic/source DTO conversion, related-page lookup, and route use-case
orchestration in one file.

Cosmic Python frames the adapter/service split as: "The Flask API now does only
two things: it initializes a unit of work, and it invokes a service." In this
repo, the server already invokes `ViewerService`; this slice keeps that edge
thin and makes `ViewerService` delegate its own non-use-case collaborators
instead of accumulating mapping and selection mechanics.

Read before coding:

- `MANUAL.md`
- `docs/python-port-live-agreement.md`
- `docs/reference/cosmic-python/chapter_06_uow.md`

## Scope

- Add a viewer workspace-scope collaborator for selected wiki fallback,
  registry availability filtering, and overview workspace ordering.
- Add viewer projection helpers for converting index/workspace models into
  browser payload models.
- Keep `ViewerService` as the service-facing use-case facade.
- Add an architecture test that prevents workspace-selection and DTO mapping
  from regrowing inside `service.py`.

## Out Of Scope

- No UI changes.
- No new server routes.
- No change to selected-wiki semantics.
- No React/Next/Vite build step.
- No source-code preview in the viewer.

## Verification

- Focused viewer and server tests.
- Focused architecture test.
- Focused lint over viewer/server/tests.
- Live serve API dogfood against two registered temp wikis.
- Full pytest, ruff, and diff check before commit.
