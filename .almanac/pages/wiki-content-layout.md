---
title: Wiki Content Layout
summary: Wiki content layout is the active design direction that separates visible wiki content from local Almanac runtime state.
topics: [wiki-design, storage, systems, decisions]
sources:
  - id: syntax-prompt
    type: file
    path: prompts/base/syntax.md
    note: Shows the prompt text that still teaches the old `.almanac/pages` authoring path in this checkout.
  - id: organization-page
    type: wiki
    slug: wiki-organization-primitives
    note: Defines the graph-versus-browse-projection distinction that makes a visible wiki root useful without replacing links, topics, and hubs.
  - id: product-family-page
    type: wiki
    slug: almanac-product-family
    note: Records the product direction that `docs/almanac/` is the preferred public/team profile while `.almanac/` remains the quiet local/private profile.
  - id: github-native-page
    type: wiki
    slug: github-native-wiki-maintenance
    note: Records the GitHub and hosted-product root choice discussion for `docs/almanac/`, `.almanac/`, and top-level `almanac/`.
  - id: layout-session
    type: conversation
    path: /Users/rohan/.codex/sessions/2026/06/13/rollout-2026-06-13T12-41-50-019ec281-3f93-7a20-a1d1-7154582ac2b1.jsonl
    note: Records the wiki-quality audit, General Almanac comparison, and separate worktree implementation that pushed the layout transition further.
status: active
verified: 2026-06-19
---

# Wiki Content Layout

Wiki content layout is the boundary between reviewable project memory and local Almanac machinery. The active design direction points durable, human-readable wiki content toward `docs/almanac/`, keeps `.almanac/` as the quiet local/runtime profile, and treats a top-level `almanac/` directory as higher-clutter opt-in surface. [@product-family-page] [@github-native-page]

The change exists because a hidden flat `.almanac/pages/` corpus is strong for local agent retrieval but weak as the default human browsing surface. The 2026-06-13 quality audit found that the old shape let good pages become buried under long page lists, source-list sprawl, and stale prompt guidance. The durable product direction is visible docs-style project memory with graph semantics underneath, not a raw generated-docs tree. [@layout-session] [@organization-page]

## Design Contract

The browse root and the graph identity layer are separate. `docs/almanac/` can make the first repo-open experience readable, but links, topics, backlinks, sources, hubs, and stable page identities still carry the wiki's meaning. A folder path should not become the only way a page belongs to a subject. [@organization-page]

`docs/almanac/` is the preferred team/public profile because it reads as project documentation without adding a branded root directory. `.almanac/` remains the quiet local/private profile and the place users expect generated state, local indexes, job records, and agent-specific machinery to live. [@product-family-page] [@github-native-page]

The 2026-06-13 worktree branch tested a stronger version of this boundary: `docs/almanac/` as the only durable source root and `.almanac/` as runtime-only. That branch result is evidence for the migration direction, not proof that every checkout already has the new behavior. [@layout-session]

## Verification Boundary

Do not describe `docs/almanac/` as landed on a target branch without checking that branch's code, prompts, and guides. In this checkout, `prompts/base/syntax.md` still instructs lifecycle agents to write pages directly under `.almanac/pages/`, so the prompt layer has not fully caught up to the design direction. [@syntax-prompt]

This boundary matters because Absorb can otherwise turn branch work into false current memory. Code is current truth for implementation claims, while branch transcripts are evidence for direction, rationale, and tested alternatives until their commits land on the branch whose wiki is being edited.

## Migration Checklist

A real layout migration needs one central path boundary and matching updates to all readers and writers of wiki content. The 2026-06-13 branch showed that the affected surfaces include page discovery, index freshness, topic-file reads and writes, lifecycle page snapshots, viewer front-door selection, global viewer repository discovery, prompts, guides, repo agent instructions, tests, and source-control hygiene. [@layout-session]

## Related Pages

[[wiki-organization-primitives]] explains why visible browse projection and graph identity are separate concerns. [[almanac-product-family]] explains the root-choice product profiles. [[sqlite-indexer]] explains how content roots become query rows. [[source-provenance]] explains why `sources:` remains the evidence model while `file_refs` preserve file-aware search.
