# Bulletproof React Notes For CodeAlmanac

Source: https://github.com/alan2207/bulletproof-react, cloned 2026-06-29.
License: MIT; see `LICENSE.md` in this folder.

## What Applies

- Treat the frontend as a set of features, not a flat script pile, once `serve`
  grows beyond a small static viewer.
- Keep API declarations close to the feature that consumes them, with typed
  request/response contracts on the Python side.
- Keep shared visual primitives separate from wiki-specific components.
- Prefer integration and browser tests for viewer behavior because the value is
  whether the user can browse the wiki, search, follow links, and inspect page
  context.
- Use battle-tested libraries for real UI machinery if the viewer becomes a
  React app. Do not hand-roll complex dropdowns, routing, focus traps, or data
  caching once those concerns exist.

## What Does Not Automatically Apply

- Bulletproof React is not a mandate to create a React or Next.js build step for
  `codealmanac serve` today.
- The current viewer ships as Python package data and is read-only. A static
  HTML/CSS/JS surface is acceptable while the UI is small and has no complex
  client state.
- If a React/Next.js rewrite becomes justified, it must preserve the local-only
  serve contract: no hosted routes, no account/billing semantics, no SDK/MCP,
  and no CLI shell-out.

## Current Serve Guidance

Use UseAlmanac as the source for visual language: alpine colors, dashboard
chrome, account-picker styling, readable wiki typography, and polished shell
spacing.

Do not copy UseAlmanac's hosted wiki information architecture wholesale. The
CodeAlmanac local viewer remains wiki-first: sidebar navigation, page/topic/search
views, backlinks, related pages, and file-reference graph navigation.
