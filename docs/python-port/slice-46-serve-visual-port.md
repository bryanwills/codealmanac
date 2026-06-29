# Slice 46 - Serve Visual Port

Date: 2026-06-29

## Scope

Port UseAlmanac's visual language onto the local `codealmanac serve` viewer
without changing the product model.

## Decisions

- Keep CodeAlmanac's local wiki IA: overview, sidebar navigation, page,
  topic, search, and file-reference graph routes.
- Borrow UseAlmanac shell polish: alpine colors, dashboard rail, account-picker
  styling, page surface, row styling, search header, and side panel treatment.
- Do not copy UseAlmanac hosted wiki search/page flow, account routes,
  billing/settings surfaces, hosted wording, or hosted control-plane concepts.
- Keep the current static package-data viewer until a real maintainability
  problem justifies React or Next.js.
- Use Bulletproof React as a structure reference for future frontend growth:
  feature boundaries, shared UI primitives, colocated API helpers, and browser
  tests.

## Files

- `src/codealmanac/server/assets/index.html`
- `src/codealmanac/server/assets/app.css`
- `src/codealmanac/server/assets/app.js`
- `docs/reference/bulletproof-react/`

## Verification

- Focused viewer/server tests.
- Focused ruff over viewer/server files.
- Browser-harness desktop dogfood for overview, page, wikilink, search, and
  file-reference routes.
- Browser-harness mobile dogfood for page rendering, side-panel collapse, search
  width, and horizontal overflow.
