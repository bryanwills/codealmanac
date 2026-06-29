# Slice 47 - Viewer Frontend Modules

Date: 2026-06-29

## Scope

Split the packaged `serve` frontend JavaScript into small static modules while
keeping the viewer as Python package data.

## Decisions

- Keep the local viewer static for now. Do not add React, Next.js, Vite, or a
  frontend build step until complex client state or component-library pressure
  appears.
- Apply Bulletproof React's structure lesson without copying its machinery:
  API calls, routing helpers, shared DOM components, and screen renderers get
  separate modules.
- Keep module imports direct. Do not add barrel files.
- Make nested static assets an explicit server concern instead of relying on
  the catchall HTML fallback.
- Use Pydantic validation for requested package asset paths.

## Shape

```text
src/codealmanac/server/assets/
  index.html
  app.css
  app.js
  viewer/
    api.js
    components.js
    main.js
    renderers.js
    routes.js
```

## Verification

- Focused server/viewer tests.
- Focused ruff over the server package.
- Browser-harness smoke over page, search, file-reference, wikilink, and
  mobile no-overflow behavior.
- Wheel inspection proves nested viewer modules are packaged.
