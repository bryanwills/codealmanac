# Slice 92: Local API Edge Naming

## Scope

Rename the local viewer HTTP edge from `codealmanac.api` to
`codealmanac.api`.

This is not a behavior change. It removes stale language from the active Python
package so local CodeAlmanac and codealmanac-hosted use the same top-level noun
for HTTP edges.

## Why

`server` is now too vague. It can mean the hosted backend, the local viewer, a
GitHub app server, or an agent app-server transport. `api` is the current
product noun for HTTP routes and edge concerns.

Cosmic Python chapter 4 says the service layer is the main way into the app;
routes should talk to that layer. Chapter 13 says dependency wiring should stay
in the composition root. For this slice, that means:

- `codealmanac.api` owns FastAPI route registration, error mapping, and static
  viewer asset serving.
- `codealmanac.app.CodeAlmanac` remains the composition root.
- `codealmanac.wiki.viewer` remains the product service behind the routes.

## Shape

```text
src/codealmanac/
  api/
    app.py             # FastAPI composition for local viewer HTTP edge
    routes.py          # viewer API routes
    errors.py          # product/validation error mapping
    static_assets.py   # packaged viewer asset loading
    static_routes.py   # static viewer routes
    assets/
```

Public call shape:

```python
from codealmanac.api.app import create_api_app

viewer_api = create_api_app(app, cwd, wiki)
```

## Out Of Scope

- Do not rename the user-facing command from `codealmanac serve`.
- Do not rewrite the viewer UI.
- Do not change local/cloud delivery behavior.
- Do not edit archived or generated research references that mention `server`.

## Verification

- Focused viewer/API tests.
- Architecture test that active code no longer imports `codealmanac.api`.
- Full Python test suite, lint, format check, compileall, and diff hygiene.
