# Slice 51 - Serve Shell Polish

Date: 2026-06-29

## Scope

Polish the local `serve` shell so it follows the agreed sidebar-first
CodeAlmanac reader shape. This slice does not add React, Next.js, hosted wiki
routes, source-code preview, or a new viewer service.

## Product Decision

The viewer should feel like a local repo wiki browser. UseAlmanac remains a
visual reference for colors, rail polish, and account-picker feel, but the
current hosted UseAlmanac wiki page-list/search interaction is not the target.

## Changes

- The rail account area labels the current wiki as a repo-owned local wiki.
- The sidebar names the graph scope as `Local knowledge graph`.
- Page and topic rail links carry route metadata and receive active state when
  their route is open.
- CSS gives the rail account trigger a clearer picker treatment and highlights
  active page/topic links.
- Mobile hides dense topic/page rail lists and keeps the compact top nav.
- Viewer CSS no longer uses viewport-scaled font sizes.

## Verification

- Focused tests: `uv run pytest tests/test_server.py tests/test_architecture.py -q`
  passed with 16 tests.
- Live pinned-project static/API dogfood: temp repo, isolated `HOME`,
  `uv --project /Users/rohan/Desktop/Projects/codealmanac run codealmanac serve`,
  `curl /`, `/assets/viewer/main.js`, `/api/overview`, and `/api/page/auth-flow`
  returned the expected CodeAlmanac viewer assets and wiki payloads.
- Browser-harness could not complete the visual pass because Chrome remote
  debugging failed with `CDP WS handshake failed` and requested the user to
  click Allow in Chrome. Keep the server/browser dogfood as an open gate until
  Chrome allows the connection again.
