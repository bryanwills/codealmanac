# .almanac Garden Refactor Audit

Date: 2026-06-09

Scope: `/Users/rohan/Desktop/Projects/codealmanac/.almanac`

This audit treats the repo wiki as an information architecture, not as a pile of markdown files. The question is whether future coding agents can find the right project memory before changing code, trust the claims they read, and update the graph without turning it into transcript sediment.

## Executive Summary

The wiki's storage model is good. Keep the flat committed corpus, page slugs, double-bracket links, topic DAG, file-aware retrieval, lineage metadata, `sources:` provenance, and `almanac health` checks. These are the right primitives for an agent-first codebase wiki.

The garden problem is editorial, not mechanical. `almanac health` reports no orphans, stale pages, dead refs, broken links, broken cross-wiki links, empty topics, empty pages, or slug collisions. The graph is intact. The weak point is that dense areas now need an explicit front door, hubs, canonical anchors, split/merge rules, and evidence cleanup.

The missing front door is concrete. Several viewer and prompt assumptions expect a `getting-started` entry point, but the active corpus does not have `.almanac/pages/getting-started.md`. Today an agent must infer the first page from search results or the README. That is fine for power users and weak for a shared agent memory system.

The topic graph is doing too many jobs. The topic DAG is a good retrieval primitive, but current topic use mixes browse neighborhoods, page type, currentness, product strategy, external references, and runtime architecture. The `agents` topic is the clearest example: it contains provider/runtime pages, prompt-system pages, competitor pages, external inspiration, and product pages.

The provenance model needs immediate cleanup. The health report found 347 unused source IDs, 29 pages with legacy source metadata, and 135 ambiguous legacy source targets. That means many pages list source material that no claim cites. For a wiki whose value proposition is trustable project memory, this is a first-order quality problem.

The biggest pages should be split before they attract more facts. `github-native-wiki-maintenance` is 831 lines, `capture-automation` is 726 lines, `wiki-organization-primitives` is 397 lines, `almanac-serve` is 387 lines, and `almanac-product-family` is 320 lines. Some of those are coherent reference pages, but several are doing hub, history, decision, current contract, and product roadmap jobs at once.

Product and competitive memory can stay, but only as a disciplined shelf. The repo README explicitly allows product and market conclusions that shape how CodeAlmanac is built, positioned, priced, or trusted. That is legitimate. It should not blur current engineering architecture with investor narrative, broad company-brain strategy, or competitor notes in the same reading path.

## Main Recommendations

1. Add hub pages before adding schema. The next garden pass should create normal pages such as `architecture-hub`, `sync-hub`, `wiki-design-hub`, `product-strategy-hub`, and `competitive-landscape`. Hubs should route readers, name canonical pages, mark historical pages, and describe reading order.

2. Add `getting-started` as the first page before splitting dense clusters. It should name the wiki's main neighborhoods, explain how to search, point to the highest-value hubs, and say that topics are retrieval neighborhoods rather than reading order.

3. Make the capture-to-sync rename explicit. Several pages now have `Sync` titles under `capture-*` slugs. Keep old slugs only if alias or redirect behavior exists; otherwise rename or archive with lineage so future agents do not treat old vocabulary as current architecture.

4. Split oversized pages along reader tasks. Use anchor pages for current truth, decision pages for rationale, failure-mode pages for incidents, reference pages for contracts, and product pages for strategy. Do not let one page be both the map and the deep dive.

5. Run provenance gardening as its own pass. Remove irrelevant source entries, cite non-obvious claims close to the claim, migrate ambiguous legacy sources where possible, and prefer current code/test/prompt/web sources over local transcripts for team-verifiable claims.

6. Keep product-positioning in the wiki, but tighten the notability bar. A product page belongs when it changes implementation, command naming, packaging, pricing, trust boundaries, hosted/local split, or review behavior. Otherwise it belongs in `docs/strategy/` or a separate product Almanac, not the codebase wiki.

7. Define or delete casual metadata. `status` and `verified` appear often enough to look like schema, but not consistently enough to be trustworthy. Either document their semantics and query behavior, or remove them from pages where they only add false precision.

8. Borrow prior art as lenses, not folder structures. Use Diataxis for reader purpose, SEI Views and Beyond / ISO 42010 for stakeholder concerns and viewpoints, C4 for zoom levels, arc42 for architecture-documentation coverage, and MADR for decision shape. Do not turn `.almanac/pages/` into `tutorials/`, `reference/`, `context/`, or numbered ADR folders.

## Audit Files

- `worklog.md`: running evidence and decisions
- `source-map.md`: current wiki architecture map
- `smells.md`: strongest findings and classifications
- `feature-questions.md`: pages, topics, and workflows that may not deserve current shape
- `hand-rolled-inventory.md`: custom wiki machinery and recommendations
- `research-notes.md`: outside patterns and how they apply here
- `target-architecture.md`: proposed garden target
- `refactor-roadmap.md`: staged rewrite and cleanup plan
- `subagent-briefs.md`: independent sidecar reports and synthesis
- `reports/`: raw sidecar reports

## Current Verdict

Do a major garden rewrite, but do not replace the wiki model. The correct move is not a new schema-heavy documentation framework. The correct move is to install editorial structure over the existing graph: hubs, anchors, split pages, source hygiene, and product-shelf boundaries.
