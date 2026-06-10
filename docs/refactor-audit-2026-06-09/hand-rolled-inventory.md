# Hand-Rolled Documentation Machinery Inventory

Date: 2026-06-09

This audit targets `.almanac` as a custom documentation system. Not every custom primitive is bad. The useful question is whether the custom shape earns its cost.

## Flat Markdown Page Corpus

What is hand-rolled:

One markdown file per slug in `.almanac/pages/`, with repo-specific frontmatter and wikilinks.

Existing alternatives:

- GitHub Wiki
- MkDocs, Docusaurus, Mintlify
- ADR directories
- Obsidian-style vaults
- hosted knowledge bases

Justification:

Keep custom. The product is a repo-owned, agent-maintained wiki with file-aware search and lifecycle operations. A conventional docs site would optimize human publishing, not agent retrieval and maintenance.

Recommendation: Keep.

## Topic DAG

What is hand-rolled:

`.almanac/topics.yaml` stores topics with multiple parents. Pages can belong to multiple topics.

Existing alternatives:

- folder hierarchy
- tags only
- docs-site nav
- graph database categories

Justification:

Keep custom. Codebase knowledge is cross-cutting: a page can be a flow, a decision, an agent prompt concern, and a CLI concern at once. Folders would either duplicate pages or hide relationships.

Recommendation: Keep, but stop expecting topics to act as hubs.

## Unified Wikilink Syntax

What is hand-rolled:

`[[...]]` classifies page, file, folder, and cross-wiki references by content.

Existing alternatives:

- standard Markdown links
- Obsidian-style wikilinks
- explicit typed syntax such as `[[file:...]]`

Justification:

Keep custom. The syntax is terse and works for agent writing. It is load-bearing for path-aware retrieval and page graph traversal.

Cost:

Classification rules must remain simple and well documented. Ambiguous syntax could cause false links.

Recommendation: Keep.

## `sources:` Provenance Model

What is hand-rolled:

Page-local source IDs with source type, target fields, notes, and inline citation markers like `[@source-id]`.

Existing alternatives:

- Pandoc citations
- Markdown footnotes
- BibTeX/CSL
- plain "Sources" section
- ADR links only

Justification:

Keep custom. The sources need to represent code files, folders, commits, PRs, conversations, web docs, wiki pages, manual notes, and later source connectors. Academic citation systems do not fit repo-local evidence.

Cost:

The current corpus shows the cost clearly: unused sources and ambiguous legacy entries. The model is only valuable if pages cite claims, not if frontmatter hoards inspected files.

Recommendation: Keep, but enforce through Garden and health. Treat source cleanup as a release-blocking quality pass for major garden rewrites.

## Citation Markers

What is hand-rolled:

Inline `[@id]` markers connect claims to frontmatter source IDs.

Existing alternatives:

- Markdown reference links
- footnotes
- numbered citations
- embedded links in prose

Justification:

Keep custom for now. The marker is compact and maps directly to source rows.

Cost:

Markdown viewers render it as plain text unless special rendering is added. Page authors may forget markers.

Recommendation: Keep. Add viewer rendering later only if it improves trust inspection.

## Anchor Pages And Hubs

What is hand-rolled:

The wiki has informal anchor and hub concepts in prose and prompts, but no metadata.

Existing alternatives:

- docs-site navigation sidebars
- folders
- `type: hub` frontmatter
- `subject:` frontmatter
- ADR-style index pages

Justification:

The concept is necessary. The current implementation is too implicit.

Recommendation:

Use normal pages first. Create hub pages and strengthen `.almanac/README.md` guidance. Do not add `type:` or `subject:` frontmatter until there is a concrete query feature that needs it.

## Getting-Started Front Door

What is hand-rolled:

A single first-entry page for agents, separate from README rules and separate from topic listings.

Existing alternatives:

- docs-site landing page
- generated topic index
- README-only onboarding
- CLI search as the only entry point

Justification:

Add. The wiki is now dense enough that first-entry routing is a real requirement. A front door is cheaper than a generated navigation system and clearer than expecting every agent to infer reading order from topics.

Recommendation:

Create `getting-started` as a normal page. It should link to hubs and explain how to navigate the wiki. It should not replace `.almanac/README.md`, which should remain contributor guidance and notability policy.

## Redirects And Aliases

What is hand-rolled:

The wiki has archival lineage fields but no lightweight alias or redirect primitive.

Existing alternatives:

- filesystem symlinks
- web-server redirects
- frontmatter aliases
- Obsidian aliases
- duplicate stub pages

Justification:

Needed soon. Capture-to-sync rename makes the gap concrete.

Recommendation:

Research a minimal alias/redirect design. Avoid full page-type schema. A page-level `redirect_to:` or `aliases:` field may be justified if the indexer and `show/search` can use it cleanly.

## Garden Operation

What is hand-rolled:

An AI lifecycle operation maintains wiki shape through prompts rather than deterministic pipelines.

Existing alternatives:

- docs linting
- scheduled static-site checks
- schema validation
- proposal/review/apply workflows
- human docs ownership

Justification:

Keep. Garden is the right place for judgment: merge/split/archive/no-op decisions, currentness, source relevance, page neighborhoods, and link quality.

Cost:

If Garden only appends and creates pages, it fails its purpose. It must be explicitly authorized to delete, merge, split, archive, and no-op.

Recommendation:

Keep and strengthen prompts around structural operations. Do not convert Garden into a TypeScript state machine.

## Health Checks

What is hand-rolled:

`almanac health` checks graph integrity and source hygiene over the wiki corpus.

Existing alternatives:

- markdownlint
- link checkers
- static-site build failures
- custom CI scripts

Justification:

Keep. Standard link checkers do not know page slugs, file refs, topics, source IDs, archives, or wiki-specific semantics.

Recommendation:

Keep, and make source-hygiene categories easier to prioritize. A summary by page would help Garden choose cleanup order.

## Casual Metadata: `status` And `verified`

What is hand-rolled:

Several pages carry fields that look like workflow state or quality markers, but the README does not define them as queryable wiki semantics.

Existing alternatives:

- no metadata; rely on citations and archive lineage
- documented frontmatter schema
- health/query behavior that enforces state semantics
- review labels in git or issue trackers

Justification:

Not justified in its current casual form. A quality marker that does not have a precise meaning can create false confidence.

Recommendation:

Define or delete. If `verified` means "claims are source-cited and checked against current code," then make that explicit and let Garden/health reason about it. If `status` means active/proposed/archived, use existing archival lineage where possible and document the rest. Otherwise remove these fields during cleanup.

## Public Guidance Drift

What is hand-rolled:

The project has repo-local wiki guidance, imported AGENTS guidance, and user-facing/public guidance that can describe different provenance models.

Existing alternatives:

- a single generated guide
- docs only in the package
- wiki README as source of truth

Justification:

Some duplication is unavoidable because agents need instructions in different contexts. It becomes harmful when old guidance tells agents to create legacy metadata.

Recommendation:

After the garden rewrite settles source semantics, update exported guidance to match. In particular, stop teaching `files:` as the primary provenance mechanism if `sources:` is the current contract.

## Browse Projection

What is hand-rolled:

Currently mostly absent. `almanac serve` and README provide human entry points, but flat pages remain the GitHub file view.

Existing alternatives:

- docs folder tree
- static-site nav
- GitHub Wiki sidebar
- generated index pages

Justification:

Needed, but as presentation rather than meaning.

Recommendation:

Start with hub pages and README navigation. Add a generated or configured browse projection only when teams need GitHub-readable navigation. Do not move pages into topic folders.
