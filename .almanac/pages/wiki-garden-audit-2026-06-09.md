---
title: Wiki Garden Audit 2026-06-09
summary: The 2026-06-09 garden audit concluded that the wiki's storage graph should stay, while retrieval quality needs hubs, source hygiene, topic repair, and split/merge work.
topics: [wiki-design, decisions, prompt-system]
sources:
  - id: audit-session
    type: conversation
    path: /Users/rohan/.codex/sessions/2026/06/08/rollout-2026-06-08T21-39-05-019eaaad-518e-7d12-ac50-aa63bcc255b2.jsonl
    note: Records the deep-refactor audit of `.almanac`, the sidecar report synthesis, the final audit verdict, and the follow-up explanation through examples.
  - id: wiki-readme
    type: file
    path: .almanac/README.md
    note: Defines the repo wiki's notability bar, topic taxonomy, and rule that product or market memory belongs when it shapes how CodeAlmanac is built, positioned, priced, or trusted.
status: active
---

# Wiki Garden Audit 2026-06-09

The 2026-06-09 garden audit treated `.almanac` as an information architecture rather than a markdown file pile. Its durable conclusion is that CodeAlmanac should keep the flat committed corpus, page slugs, double-bracket links, topic DAG, source provenance, lineage metadata, and `almanac health` checks, while adding stronger editorial structure over those primitives. The problem was retrieval quality and page shape, not the underlying graph model. [@audit-session]

The audit is a temporal page because the measured wiki state mattered. At the snapshot, the wiki had 52 pages, one archived page, mechanically clean graph health, and major source-provenance debt: 347 unused source IDs, 29 pages with legacy source metadata, and 135 ambiguous legacy source targets. Those counts are evidence of a specific garden state, not a standing invariant. [@audit-session]

## What It Settled

The audit rejected replacing Almanac with a schema-heavy docs framework. Hubs, anchors, source cleanup, split/merge decisions, and product-shelf boundaries should be normal wiki pages and prompt doctrine before they become new frontmatter fields or deterministic orchestration. This extends the existing [[wiki-organization-primitives]] rule that pages, links, topics, and lineage are storage primitives, while hubs and anchors remain editorial primitives until a query need proves otherwise. [@audit-session]

`almanac health` is necessary but not sufficient. A graph can have no broken links, dead refs, or orphan pages while still being hard to read because agents cannot tell which page is canonical, which page is historical, and which page is the entry route for a dense subject. Future Garden work should treat health output as graph integrity evidence, not as proof that the wiki is well organized. [@audit-session]

The missing front door became a concrete finding. The audit found no active `.almanac/pages/getting-started.md` page, even though the corpus had grown into dense neighborhoods for lifecycle operations, sync/capture, wiki design, provider runtime, source provenance, product strategy, and competitive research. `getting-started` should be a normal page that routes agents to hubs and explains that topics are browse neighborhoods, not reading order. [@audit-session]

## Garden Roadmap

The audit's dependency order is important. First freeze current vocabulary, especially the capture-to-sync transition. Then add `getting-started` and hubs such as `wiki-design-hub`, `sync-hub`, `architecture-hub`, `product-strategy-hub`, and `competitive-landscape`. After those routes exist, repair noisy topic retrieval, clean source provenance, split oversized pages, move or archive scope mismatches, handle aliases or renames, define or delete casual metadata such as `status` and `verified`, and then update `.almanac/README.md` and exported agent guidance. [@audit-session]

Source hygiene should happen before page expansion. The audit found many pages whose source lists looked like inspection logs rather than evidence for cited claims. That supports the [[source-provenance]] contract: a source entry should support a claim, citations should appear near non-obvious claims, and legacy `files:` or ambiguous source strings should be treated as migration debt rather than current authoring style. [@audit-session]

Topic repair should make reading neighborhoods narrower. The audit singled out `agents` as overloaded because it mixed provider/runtime pages, prompt pages, competitors, external inspiration, product strategy, and wiki theory. [[topic-dag|The topic DAG]] should stay, but broad topics should not substitute for hubs that tell agents what to read before changing code. [@audit-session]

Product and competitive pages remain legitimate only when they change CodeAlmanac decisions. The repo wiki README allows product and market conclusions that shape how CodeAlmanac is built, positioned, priced, or trusted; the audit turned that into a stricter gate for future garden work. Product pages should state the implementation, command, packaging, pricing, trust, review, or positioning decision they affect, or they should move to strategy docs or a separate product wiki. [@wiki-readme] [@audit-session]

## Examples From The Audit

`[[source-provenance]]` was treated as a strong dense page because it states a product contract, a citation contract, transition boundaries, implementation surfaces, prompt guidance, and open questions. It is long, but its sections answer separate reader tasks under one clear subject.

`[[capture-automation]]` and `[[github-native-wiki-maintenance]]` were treated as split candidates because each combines hub duties, current contracts, migration history, incidents, implementation details, and product strategy in one page. Those pages should not be split until hubs and source cleanup exist, because splitting a bloated source list across several new pages would preserve the trust problem in more places. [@audit-session]

The follow-up explanation framed the issue as editorial boundaries rather than storage design. The pages and topics are like good data structures with drifted module boundaries: useful primitives remain, but future work needs clearer front doors, canonical anchors, and rules for where facts belong. [@audit-session]

## Related Pages

[[wiki-organization-primitives]] owns the general page, hub, anchor, and graph-shape doctrine. [[source-provenance]] owns the evidence model that the audit identified as the highest-risk quality problem. [[topic-dag]] owns the topic storage model that the audit said to keep but narrow. [[operation-prompts]] owns the prompt-layer changes that should carry new Garden and Absorb judgment before TypeScript orchestration is added.
