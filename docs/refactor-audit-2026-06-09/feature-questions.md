# Feature And Scope Questions

Date: 2026-06-09

This file questions wiki surface area. "Feature" here means a page, topic, workflow, or documentation convention that carries maintenance cost.

## Product-Positioning Pages

Question: Should product strategy live inside the codebase wiki?

Current evidence:

- `.almanac/README.md` says product and market conclusions belong when they shape how CodeAlmanac is built, positioned, priced, or trusted.
- Product pages currently influence real architecture: hosted GitHub App, source connectors, repo-owned markdown, review wedge, trust boundary, and local versus hosted packaging.

Recommendation: Keep, but gate.

Keep product strategy pages only when they name a current or near-future product decision that affects code, prompts, command surface, packaging, trust, pricing, or review. Pages that are only pitch material should move to `docs/strategy/` or a separate product Almanac.

## `fundraising` Topic

Question: Does `fundraising` deserve to be a codebase wiki topic?

Current evidence:

- It has one page: `pitch-deck-fundraising`.
- Fundraising advice can shape product narrative, but it rarely helps a future coding agent change code safely.

Recommendation: Delete candidate or move.

Either move `pitch-deck-fundraising` to `docs/strategy/` or keep it under product-positioning without a first-class `fundraising` topic. It should remain in `.almanac` only if it directly constrains product language or pricing decisions in code/docs.

## `getting-started`

Question: Does the wiki need a canonical first page?

Current evidence:

- The active corpus has no `.almanac/pages/getting-started.md`.
- Multiple dense neighborhoods now compete for first attention: sync, lifecycle, storage, wiki model, provider runtime, product strategy, and competitive research.
- A future agent should not have to infer reading order from topic counts or search result order.

Recommendation: Add.

Create a normal page called `getting-started`. It should route to hubs, define the main reading paths, explain current vocabulary, and point to `.almanac/README.md` for contribution conventions. Do not make it a schema special case.

## Competitive Research

Question: Should competitors be first-class wiki pages?

Current evidence:

- Competitor pages such as `dosu`, `moxie-docs`, `opendeepwiki`, `mem0`, `codex-supermemory`, and `agentmemory-competitor` clarify product boundaries.
- They can also crowd engineering searches if mixed into broad topics like `agents`.

Recommendation: Keep with a shelf.

Competitor pages belong when each has a "Product lesson" or "Implementation consequence" section. Add a `competitive-landscape` hub. Remove competitor pages from broad engineering topics unless they directly shape a technical boundary.

## Generalized Almanac Pages

Question: Should CodeAlmanac's repo wiki store general Personal/Company/Research Almanac product model pages?

Current evidence:

- `almanac-product-family` is useful because generalized product thinking affects command semantics, directory shape, source portability, and local/hosted split.
- The page is now large enough to be a generalized product architecture doc.

Recommendation: Split.

Keep a CodeAlmanac product anchor in `.almanac`. Move or split generalized product material into dedicated pages only when it drives implementation. If generalized product research grows independently, create a product Almanac or keep it in `docs/strategy/`.

## `github-native-wiki-maintenance`

Question: Is this one page or a product area?

Current evidence:

- 831 lines.
- Covers hosted GitHub App product, PR UX, check-run actions, sandbox runtime, GitHub source tools, product loop, deployment risks, and source access.

Recommendation: Split immediately.

Proposed split:

- `github-native-wiki-maintenance`: short anchor and current product thesis
- `github-pr-almanac-loop`: PR UX, sticky comments, checks, same-PR updates
- `hosted-github-runner`: Modal/sandbox/runtime/source-tool execution
- `github-source-tools`: source access boundary for PRs, issues, diffs, reviews
- `github-almanac-update-risks`: CI, deploy, branch protection, fork risk

## Sync/Capture Pages

Question: Should old capture slugs remain?

Current evidence:

- Current titles say Sync.
- Slugs say capture.
- One archived `sessionend-hook` page points to `capture-automation`.

Recommendation: Rename once redirects exist.

Until redirect or alias behavior is implemented, create a `sync-hub` that explicitly says old capture slugs are historical names for sync pages. After redirect support, rename the active pages and archive old capture pages.

## `almanac-serve`

Question: Is the local viewer one page?

Current evidence:

- 387 lines.
- 36 sources, 2 cited source IDs.
- Headings include rationale, invocation, routes, viewer capabilities, packaging, module structure, API types, source rail, jobs UI, and design details.

Recommendation: Split if viewer work continues.

Keep an anchor page for "Local Viewer" and split API/reference or jobs UI pages only when future work touches those areas. Provenance cleanup is more urgent than splitting unless viewer development resumes.

## `hosted-deployment-environment`

Question: Is this current CodeAlmanac architecture or hosted product planning?

Current evidence:

- The sidecar reports flagged hosted deployment material as prone to mixing infrastructure planning with the codebase wiki's current implementation memory.
- Hosted GitHub work is product-relevant, but not every deployment-environment note helps a future agent modify this repo safely.

Recommendation: Reframe or move.

Keep hosted deployment material in `.almanac` only when it records current code constraints, provider/runtime boundaries, deployment blockers, or product decisions that shape implementation. Move broad planning notes to `docs/strategy/` or a product Almanac.

## `wiki-organization-primitives`

Question: Is this a page or the hidden manual?

Current evidence:

- 397 lines.
- It already states the target model: anchors, hubs, redirects, structural operations, source/link separation, Garden discipline, and browse projection.

Recommendation: Keep as the doctrine anchor, but create smaller operational pages.

This page is valuable and coherent. Do not delete it. Add a `wiki-design-hub` that routes to it, and consider splitting "hubs", "anchors", and "source/link quality" into focused pages if the page keeps growing.

## Standalone Inspiration Pages

Question: Should pages such as `farzapedia`, `superpaper`, `nessie`, or weak memory-product references stand alone?

Current evidence:

- External references can shape CodeAlmanac's model.
- Several inspiration or competitor pages are tagged into broad engineering paths where they can look like current architecture.
- The sidecar reports converged on keeping outside ideas only when they name the CodeAlmanac decision they affected.

Recommendation: Merge or mark as external.

Keep standalone external-reference pages only if the lead states the design, prompt, product, trust, or workflow decision they shaped. Otherwise merge their durable lesson into the relevant anchor or landscape page.

## `deep-refactor-audit`

Question: Should the deep-refactor-audit skill have its own wiki page?

Current evidence:

- The skill is relevant to this session's gardening workflow.
- A page belongs in the codebase wiki only if the skill changes recurring repo behavior, architecture-review practice, or Garden/review prompts.

Recommendation: Gate.

Do not add or keep a standalone `.almanac` page merely because this audit used the skill. Keep it only if the repo adopts the skill as part of a repeatable architecture-review workflow.
