# Hand-Rolled Documentation Machinery Critic

Goal:
Critically audit `/Users/rohan/Desktop/Projects/codealmanac/.almanac` as documentation machinery to determine which taxonomy, page conventions, source provenance, link syntax, and gardening workflows should be preserved, simplified, removed, or redesigned.

Non-goals:
- Do not edit implementation code.
- Do not edit `.almanac` pages.
- Do not treat the current wiki shape as justified just because it exists.
- Do not recommend generic documentation patterns without explaining how they would move this wiki.

## Executive Summary

The `.almanac` documentation machinery should be kept. The core custom primitives are paying rent: flat markdown pages, stable slugs, a topic DAG, unified wikilinks, source frontmatter, file-aware retrieval, lineage metadata, and Build/Absorb/Garden as lifecycle operations. They are not accidental clones of a standard docs tree. They solve the product-specific problem of future coding agents needing grounded project memory before editing code.

The problem is that the custom system now has too many half-explicit conventions. Page jobs are intentionally not schema, but the wiki still relies on implicit anchors, informal hubs, optional `status` and `verified` fields, prompt-only page-shape doctrine, and docs that disagree about `files:` versus `sources:`. The result is a wiki with a healthy graph and a messy contract surface.

The strongest recommendation is not to replace Almanac's model with Diataxis, arc42, C4, ADRs, or a normal docs site. Those are good vocabularies, not the storage model. The right move is to wrap the custom wiki graph in a clearer organization doctrine: one front door, a few hub pages, canonical anchors, explicit merge/split/archive/redirect/no-op outcomes, and stricter source hygiene. That should happen in prompts and wiki conventions before it becomes TypeScript machinery.

The largest concrete quality issue is source provenance drift. I found 52 pages; all have `title`, `summary`, `topics`, and `sources`, but 30 pages still contain legacy string source entries inside `sources:` and one archived page still has legacy `files:`. There are 581 structured source objects and 136 legacy source strings. The migration is conceptually settled, but this wiki has not fully completed it.

The second concrete issue is navigation. `prompts/operations/build.md`, `build-operation.md`, `operation-prompts.md`, and `almanac-serve.md` all say `getting-started.md` is the canonical front door, but this wiki does not have `.almanac/pages/getting-started.md`. The graph has no broken page links in a direct parse, but a healthy graph is not the same thing as a readable first route.

## Evidence Snapshot

Inspected surfaces:
- `.almanac/README.md`
- `.almanac/topics.yaml`
- `.almanac/pages/*.md`
- `prompts/base/notability.md`
- `prompts/base/syntax.md`
- `prompts/operations/build.md`
- `prompts/operations/absorb.md`
- `prompts/operations/garden.md`
- `docs/concepts.md`
- `docs/manual/good-codebase-wikis.md`
- `README.md`
- `guides/mini.md`
- `guides/reference.md`
- `/Users/rohan/Desktop/Projects/openalmanac/docs/ideas/codebase-wiki.md`

Measured wiki state:
- 52 markdown pages under `.almanac/pages/`.
- 14 topics in `.almanac/topics.yaml`.
- Every page has `title`, `summary`, `topics`, and `sources`.
- 47 pages have `verified`; 5 do not.
- 32 pages have `status`; 20 do not.
- 2 pages have `external_version`.
- 1 page has legacy `files:`.
- 1 page is archived by `archived_at` and `superseded_by`.
- Direct wikilink parse found 362 page links, 135 file links, and 15 folder links.
- Direct wikilink parse found no broken page links.
- Four pages had no inbound page links: `hosted-deployment-environment`, `nessie`, `typescript-runtime-choice`, and `verification-workflow`.
- One page had no outbound page links: `global-agent-instructions`.
- Largest pages by line count: `github-native-wiki-maintenance` at 831 lines, `capture-automation` at 726, `wiki-organization-primitives` at 397, `almanac-serve` at 387, and `almanac-product-family` at 320.

Structured source inventory:
- `file`: 370
- `conversation`: 100
- `web`: 98
- `manual`: 8
- `commit`: 5

Legacy source inventory:
- 30 pages contain string source entries inside `sources:`.
- 136 total legacy string source entries remain.
- `sessionend-hook` contains legacy `files:`.
- `superpaper` has string sources only and no structured source objects.

## Current Architecture Map

The committed wiki source layer is:
- `.almanac/README.md`: local notability bar, topic taxonomy, page shapes, writing conventions, and source expectations.
- `.almanac/topics.yaml`: topic DAG metadata.
- `.almanac/pages/*.md`: page source of truth.

The derived local layer is:
- `.almanac/index.db`: SQLite projection over pages, topics, links, file refs, summaries, lineage, and page sources.
- `.almanac/runs/`, `.almanac/logs/`, old root `.capture-*` and `.bootstrap-*` logs: local run artifacts, ignored by git.

The prompt doctrine layer is:
- `prompts/base/purpose.md`: product purpose.
- `prompts/base/notability.md`: what deserves pages, topics, clusters, and hubs.
- `prompts/base/syntax.md`: frontmatter, sources, citations, wikilinks, writing conventions.
- `prompts/operations/build.md`: first wiki construction.
- `prompts/operations/absorb.md`: bounded source incorporation.
- `prompts/operations/garden.md`: graph maintenance.

The public documentation layer is:
- `README.md`
- `docs/concepts.md`
- `guides/mini.md`
- `guides/reference.md`
- `docs/manual/good-codebase-wikis.md`

The most important architectural fact: the source of truth is not one place. The wiki contract is spread across `.almanac/README.md`, prompts, guides, repo README, and implementation behavior. That spread is understandable for a fast-moving product, but it is now the main source of documentation machinery drift.

## Prior Art Used For Comparison

Diataxis is useful because it frames documentation around reader needs: tutorials, how-to guides, reference, and explanation. It should not become four top-level Almanac topics. Almanac's primary reader is an agent doing code work, so reader purpose should influence page leads and hubs rather than storage categories. Reference: https://diataxis.fr/

arc42 is useful because it names architecture communication sections: goals, constraints, context, solution strategy, building blocks, runtime, deployment, cross-cutting concepts, decisions, quality, risks, and glossary. Almanac already covers many of these as pages and topics. It should borrow this as a coverage checklist, not as a required folder or page template. Reference: https://arc42.org/overview

C4 is useful because it separates system context, containers, components, code, dynamic, and deployment views. Almanac should use that vocabulary when a page needs a view, but not add `type: container-view` frontmatter unless a query feature requires it. Reference: https://c4model.com/

Write the Docs' docs-as-code guidance supports Almanac's strongest choice: plain text, Git, code review, and docs integrated with product work. That argues for keeping repo-owned `.almanac` markdown rather than moving canonical memory into a hosted database. Reference: https://www.writethedocs.org/guide/docs-as-code/

Documenting Software Architectures is already represented by `.almanac/pages/documenting-software-architectures.md`. Its best contribution here is the "views and beyond" split: individual pages can answer different architecture questions, while shared beyond-view material gives rationale, glossary, review, currentness, and navigation.

## Inventory And Recommendations

### 1. Custom Topic DAG

What is hand-rolled:
`.almanac/topics.yaml` defines a multi-parent topic DAG. Pages assign topic slugs in frontmatter. Topics are reading neighborhoods rather than folders.

Evidence:
The current taxonomy has 14 topics. The densest topics are `agents` with 25 pages, `product-positioning` with 18, `cli` with 17, `systems` with 13, `flows` with 13, and `decisions` with 13. The DAG gives `agents` two parents (`flows`, `stack`) and narrower cross-cutting topics such as `provider-harness`, `prompt-system`, and `competitive-research`.

Why it exists:
The wiki needs multi-membership. A page like `source-provenance` is simultaneously `wiki-design`, `storage`, and `decisions`; a folder hierarchy would force one misleading primary home.

Standard comparison:
Diataxis and arc42 are hierarchical presentation aids, not good storage models for cross-cutting codebase memory. C4 is a view vocabulary, not a taxonomy. A DAG is justified for agent retrieval.

Recommendation:
Keep the topic DAG. Do not replace it with folders, Diataxis buckets, arc42 sections, or C4 levels.

Simplify:
Narrow the overloaded `agents` topic. It currently mixes provider runtimes, operation prompts, source provenance, competitive products, product strategy, and wiki-design theory. The existing `prompt-system`, `provider-harness`, `wiki-design`, and `competitive-research` topics should absorb more of that meaning.

Wrap:
Add a browse projection through hubs or a nav/front-door page. Topics should answer "what belongs together"; hubs should answer "what should I read first and why."

Confidence:
High.

### 2. Page Type Conventions

What is hand-rolled:
The wiki uses page-shape vocabulary: Entity, Decision, Flow, Constraint, Failure Mode, Hub, Anchor, Subject Neighborhood, and similar terms. These are conventions, not enforced schema.

Evidence:
`.almanac/README.md` says page shapes are suggestions. `prompts/base/notability.md` says genres are vocabulary, not enforcement. `wiki-organization-primitives.md` explicitly rejects `subject:` and `type:` frontmatter. `operation-prompts.md` calls the stray `## **type: runtime-view**` heading in `prompts/base/notability.md` prompt debt.

Why it exists:
The product wants agents to make editorial judgments instead of filling a rigid template.

Standard comparison:
arc42 and C4 would be harmful if copied as page types. Their value is asking "which view does this reader need?" Diataxis has the same role. The page should be named for the subject and job, not for the template.

Recommendation:
Keep page types as vocabulary. Do not add `type:` or `subject:` frontmatter unless a concrete query feature needs it.

Simplify:
Remove the `## **type: runtime-view**` prompt debt from `prompts/base/notability.md` in a future implementation pass. It conflicts with the settled "page naming before schema" rule.

Redesign:
Make "page job" visible in leads and hubs. For example, `capture-flow` should read as the runtime flow anchor; `capture-automation` should read as the scheduler/product-contract anchor. The wiki should not require a hidden schema to tell those apart.

Confidence:
High.

### 3. Source Provenance Model

What is hand-rolled:
`sources:` frontmatter stores page-local source IDs, types, targets, and notes. Citations use `[@source-id]`. The indexer derives `page_sources` and file refs. Legacy `files:` and string source entries remain supported.

Evidence:
The current wiki has 581 structured source objects and 136 legacy source strings. Source types are mostly `file`, `conversation`, and `web`. There are no missing citation IDs in the direct parse, but 30 pages still have legacy string source entries. The source notes often say "Migrated from legacy files" or "Migrated from legacy sources," which is mechanically honest but weak as evidence.

Why it exists:
Plain `files:` could only answer "what code does this page mention?" It could not answer "why should the reader believe this claim?" Structured sources also support web docs, conversations, commits, PRs, manual notes, and future issue/discussion sources.

Standard comparison:
Docs-as-code does not solve provenance by itself; it gives versioned source files. Architecture docs need rationale and evidence, but standard templates do not provide CodeAlmanac's file-aware retrieval behavior. This custom model is justified.

Recommendation:
Keep structured `sources:`. This is one of the strongest product primitives.

Simplify:
Finish the legacy migration. The current wiki should not continue teaching future agents that string sources are normal. Run the deterministic migration in a future maintenance pass, then let Garden improve source notes and citations.

Redesign:
Separate "sources inspected" from "sources that support claims." The largest pages have source lists that look like audit trails of everything an agent touched. A source list should contain evidence a future reader may need to inspect, not every input from the session.

Wrap:
Add a source-quality gardening rule:
- delete source entries not cited by any non-obvious claim unless they support general page context
- replace "Migrated from legacy files" with a claim-specific note when the page is edited
- prefer current code, tests, config, prompts, and public docs for present-tense claims
- use conversations for rationale and history, not current behavior unless backed by current repo evidence

Research:
Whether web sources need snapshots under `.almanac/sources/` is still open. Do not add that machinery until shared-team verification requires it.

Confidence:
High.

### 4. Legacy `files:` Compatibility

What is hand-rolled:
The wiki historically used `files:` frontmatter to power `search --mentions`. The newer source model derives file refs from `sources[type=file]`, inline file wikilinks, and legacy `files:`.

Evidence:
`.almanac/README.md` and `prompts/base/syntax.md` say `sources:` is canonical and `files:` is legacy. `docs/concepts.md`, `guides/mini.md`, and chunks of `guides/reference.md` still teach `files:` as central. The current wiki has one page with legacy `files:`: `sessionend-hook`.

Why it exists:
Backward compatibility for existing wikis.

Recommendation:
Keep read compatibility. Delete or rewrite instructional emphasis on `files:` everywhere current docs are meant to teach new behavior.

Delete candidate:
Once migration has run across sample and real wikis, stop presenting `files:` in examples except in a compatibility section.

Risk:
Removing read support too early would break existing wikis and `search --mentions` expectations. Do not remove parser support yet.

Confidence:
High.

### 5. Wikilink Syntax

What is hand-rolled:
One `[[...]]` syntax classifies page, file, folder, and cross-wiki links by content.

Evidence:
The current page graph parse found 362 page links, 135 file links, 15 folder links, and no broken page links. `.almanac/README.md`, `prompts/base/syntax.md`, and the spec all document the same classifier.

Why it exists:
The syntax gives agents one lightweight form that can express graph navigation and code references in ordinary prose.

Standard comparison:
Markdown links cannot distinguish page slugs from repo file refs as a first-class index contract. Wiki engines usually support page links, but not CodeAlmanac's file/folder/source retrieval requirement.

Recommendation:
Keep. This is a small, justified custom syntax.

Simplify:
Prefer display text in prose where raw slugs interrupt reading. The syntax supports this, but some guide material still normalizes raw slugs too much.

Research:
Do not add aliases or redirects through a second link syntax. If aliases become necessary, model them as lineage or redirect metadata resolved by the existing link form.

Confidence:
High.

### 6. Gardening Workflow

What is hand-rolled:
Build creates the initial graph, Absorb incorporates bounded new context, and Garden improves the existing graph. Garden may merge, split, archive, retopic, relink, create hubs, or no-op.

Evidence:
`prompts/operations/garden.md` gives a soft algorithm and explicitly allows broad graph edits. `wiki-organization-primitives.md` names create/update/merge/split/redirect/archive/no-op as structural outcomes. `wiki-lifecycle-operations.md` says operations are prompt-owned algorithms rather than proposal/apply pipelines.

Why it exists:
The wiki drifts through content accumulation, not only through broken links. A deterministic `health` command can find graph integrity problems, but it cannot decide page scope, canonicality, or currentness of semantic claims.

Standard comparison:
Docs-as-code expects ongoing maintenance and code review. Almanac's Garden is the agentic form of that maintenance loop. This is custom, but justified.

Recommendation:
Keep Garden as an AI operation. Do not replace it with a TypeScript state machine.

Redesign:
Make the Garden doctrine more operational. It should first inspect front door, hubs, oversized pages, orphan-ish pages, source-health warnings, stale source notes, and pages whose job is unclear. Today the prompt names those outcomes, but this wiki shows the front door and source migration can still drift.

Wrap:
Use `almanac health` as deterministic preflight and postflight input for Garden, but do not make `health` mutate page prose.

Confidence:
High.

### 7. Front Door And Hubs

What is hand-rolled:
`getting-started.md` is a prompt-level convention for the canonical wiki front door. Hubs are normal pages, not special storage objects.

Evidence:
`prompts/operations/build.md` requires `.almanac/pages/getting-started.md`. `build-operation.md`, `operation-prompts.md`, and `almanac-serve.md` document the same convention. This wiki does not have `.almanac/pages/getting-started.md`.

Why it exists:
Search and topics are not enough for first-read ergonomics. A future agent needs a ranked route through dense clusters.

Standard comparison:
arc42 has a table of contents; C4 starts broad and zooms in; Diataxis is organized around reader tasks. Almanac should borrow that as a navigation habit while keeping graph storage.

Recommendation:
Redesign the wiki's navigation surface, not the storage model.

Target shape:
- Add `getting-started.md` as the front door in a future Garden run.
- Add or strengthen hubs for `wiki-design`, lifecycle operations, provider harness, product positioning, and competitive research.
- Keep hubs as normal pages with prose, sources, and links.
- Do not add a parallel folder hierarchy as the canonical meaning model.

Confidence:
High.

### 8. Page Size And Subject Boundaries

What is hand-rolled:
Subject neighborhoods are an editorial convention. There is no hard page size limit or page-splitting rule.

Evidence:
`github-native-wiki-maintenance` has 831 lines. `capture-automation` has 726. `wiki-organization-primitives` has 397. These are not automatically wrong, but they are large enough that their sections now mix architecture, product contracts, incident lessons, backlog items, and open questions.

Why it exists:
Absorb and Garden have favored append/update over split. That is often correct, but it can produce anchor pages that become hidden bundles of several page jobs.

Standard comparison:
arc42 would split these across constraints, runtime, decisions, risks, and glossary. C4 would split static structure, dynamic flow, and deployment. Diataxis would split explanation from reference and task guidance.

Recommendation:
Simplify through subject neighborhoods.

Candidate splits:
- `capture-automation`: keep scheduler-backed quiet-session sync as anchor; split legacy hook cleanup, sync activation/backlog policy, cost-control incident, and manual smoke ladder if each remains useful.
- `github-native-wiki-maintenance`: split remote product loop, GitHub App event model, hosted worker/sandbox substrate, OSS route, and buyer/payment thesis.
- `wiki-organization-primitives`: keep as doctrine anchor; split repo browse projection or source/hub doctrine only if those topics continue to grow.

Risk:
Splitting too eagerly creates thin pages. Split only when the subtopic has an independent reader question and enough links/sources.

Confidence:
Medium-high.

### 9. `status`, `verified`, And Other Editorial-Only Metadata

What is hand-rolled:
Many pages use fields such as `status`, `verified`, and `external_version`. Current parser/query surfaces understand `title`, `summary`, `topics`, `sources`, `archived_at`, `superseded_by`, and `supersedes`; `status`, `verified`, and `external_version` appear to be editorial conventions rather than core indexed contracts.

Evidence:
32 pages have `status`, 20 do not. 47 have `verified`, 5 do not. 2 have `external_version`. `prompts/base/syntax.md` shows these fields in the example, but its next paragraph says the current tooling understands `title`, `summary`, `topics`, `sources`, `archived_at`, `supersedes`, and `superseded_by`.

Why it exists:
The wiki wants currentness and lifecycle state to be inspectable.

Recommendation:
Research and decide. Do not keep these as casual pseudo-schema forever.

Options:
- Keep `verified` as an editorial date and teach Garden to update it only after checking sources.
- Drop `status` except for proposed/implemented product-thesis pages where it is meaningful.
- Add tooling only if queries like `search --stale-verified` or `health --unverified-web-sources` become necessary.

Risk:
If `verified` is not maintained, it creates false confidence. A missing field is safer than a stale date that looks authoritative.

Confidence:
Medium.

### 10. Public Docs Drift

What is hand-rolled:
There are multiple instruction surfaces for agents and humans: `.almanac/README.md`, `guides/mini.md`, `guides/reference.md`, `docs/concepts.md`, `prompts/base/syntax.md`, and root `README.md`.

Evidence:
`.almanac/README.md` says structured `sources:` is canonical and legacy `files:` is only compatibility. `docs/concepts.md` still introduces `files:` as the frontmatter field. `guides/mini.md` still says frontmatter carries `topics:` and `files:` and tells writers to include `files:`. `guides/reference.md` contains both the new migration command and old `files:` examples.

Why it exists:
The source-provenance model was added after the first public docs and guides.

Recommendation:
Simplify the teaching surface. Make `sources:` the only first-class field in examples. Keep `files:` in a migration/legacy section.

Risk:
Leaving this drift means future agents will continue creating legacy pages while the indexer and source-health system try to migrate away from them.

Confidence:
High.

## Legitimate Complexity Worth Preserving

Keep these even though they are custom:
- Flat `.almanac/pages/` slug identity.
- Topic DAG instead of folders.
- Unified `[[...]]` syntax.
- Source-derived file refs.
- Structured `sources:` with page-local citation IDs.
- Lineage fields for archival reversals.
- Git as history.
- `index.db` as derived local query cache.
- Build/Absorb/Garden as prompt-owned lifecycle operations.
- Health as deterministic report, not a mutating semantic fixer.

These are not solved by a standard docs site, ADR directory, C4 diagram set, or architecture template.

## Accidental Complexity To Remove Or Contain

Remove or contain these:
- Legacy string sources in `sources:`.
- Legacy `files:` examples in current teaching docs.
- "Migrated from legacy files/sources" source notes when a page is next gardened.
- The stray `## **type: runtime-view**` heading in the notability prompt.
- Oversized source lists that act as session audit trails rather than claim evidence.
- Inconsistent `status` and `verified` fields unless they receive a clear maintenance contract.
- Missing `getting-started.md` despite the prompt and viewer convention.
- Topic overload where `agents` becomes a catchall for runtime, prompts, product research, and wiki theory.

## Target Architecture For The Wiki

The clean target is still a graph, not a tree:

```text
.almanac/
  README.md             repo-local wiki constitution
  topics.yaml           topic DAG metadata
  pages/
    getting-started.md  canonical front door
    wiki-design.md      hub or anchor for wiki doctrine
    lifecycle.md        hub or anchor for Build/Absorb/Garden/sync/jobs
    provider-harness.md hub or anchor for runtime providers
    product-positioning.md hub for market/product pages
    <subject>.md        natural subject anchors
```

The page model:

```yaml
---
title: Natural Subject Name
description: One factual sentence that explains why an agent opens this page.
topics: [stable-topic, another-topic]
sources:
  - id: current-code
    type: file
    path: src/current/file.ts
    note: Supports the present-tense implementation claim.
  - id: rationale-session
    type: conversation
    path: /path/to/session.jsonl
    note: Records the rationale for the decision, not current code behavior.
verified: 2026-06-09
---
```

The editorial model:
- Strong slugs and leads carry page identity.
- Topics carry reading-neighborhood membership.
- Hubs carry reading order and interpretation.
- Sources carry evidence.
- Wikilinks carry navigation.
- Lineage carries conceptual reversals.
- Git carries raw history.
- Garden carries ongoing shape repair.

The anti-target:
- Do not add rigid `type:` or `subject:` fields now.
- Do not create a folder hierarchy that becomes the real taxonomy.
- Do not make Diataxis, arc42, or C4 the storage model.
- Do not create proposal/apply workflows for wiki edits.
- Do not move canonical wiki memory into a hosted database.

## Refactor And Gardening Roadmap

### Phase 0: Stop Teaching The Old Contract

Goal:
Make all current docs teach `sources:` as canonical.

Changes:
- Update `docs/concepts.md`, `guides/mini.md`, and old examples in `guides/reference.md` to use structured `sources:`.
- Keep `files:` only in a legacy compatibility section.

Why first:
New writes should not create new legacy debt.

Risk:
Low. This is documentation and prompt hygiene.

Verification:
Search docs for `files:` and confirm only compatibility sections remain.

### Phase 1: Complete Source Migration

Goal:
Remove legacy source shapes from this wiki.

Changes:
- Run the deterministic legacy source migration in a future maintenance task.
- Garden pages whose source notes still say "Migrated from legacy files/sources."
- Keep conversations as rationale/history sources unless current code or docs support present-tense claims.

Why first:
Source provenance is the trust model. It should be clean before major page rewrites.

Risk:
Medium. Mechanical migration preserves body text, but source-note quality requires editorial judgment.

Verification:
No `legacy-frontmatter` or `unfixable-sources` findings. No string entries in page `sources:`.

### Phase 2: Add The Front Door

Goal:
Make the wiki readable from a first page.

Changes:
- Add `.almanac/pages/getting-started.md` in a future Garden run.
- Link to core hubs and anchors.
- Explain read paths for common work: indexer/query, lifecycle operations, provider harness, sync/jobs, wiki design, product strategy.

Why first:
This repo's own prompt contract already requires the page.

Risk:
Low if it stays a map, not a duplicate architecture manual.

Verification:
`almanac serve` home route has a page-backed front door. New agents can identify first reads without topic spelunking.

### Phase 3: Split Or Hub The Largest Clusters

Goal:
Reduce bloated anchors without creating thin fragments.

Changes:
- Treat `capture-automation`, `github-native-wiki-maintenance`, and `wiki-organization-primitives` as split candidates.
- Create hubs only where clusters have multiple stable reader questions.

Why first:
The longest pages are where architecture, history, incident, product, and open questions blur.

Risk:
Medium. Bad splits create more navigation work.

Verification:
Each split page has an independent reason to exist, sources, links, and a clear lead.

### Phase 4: Define Or Delete Editorial Metadata

Goal:
Stop pseudo-schema from accumulating.

Changes:
- Decide whether `verified` has a real maintenance policy.
- Decide whether `status` is meaningful outside product/proposal pages.
- Keep `external_version` only for external dependencies or references where version changes affect claims.

Why first:
Metadata without semantics is worse than no metadata.

Risk:
Medium. Some pages may use the fields as useful human signals even if tooling ignores them.

Verification:
Every retained field has a documented meaning in `.almanac/README.md` or `prompts/base/syntax.md`.

### Phase 5: Strengthen Garden Doctrine

Goal:
Make Garden a real graph editor, not a style cleanup pass.

Changes:
- Add or strengthen organization doctrine in prompts.
- Require Garden to check front door, hubs, canonical anchors, source hygiene, page size, topic overload, and pages without inbound or outbound links.
- Keep no-op as a first-class successful outcome.

Why first:
The current primitives are strong enough; the editor needs sharper priorities.

Risk:
Low if it remains prompt guidance and does not become a deterministic state machine.

Verification:
Future Garden runs produce fewer bloated pages, fewer weak source notes, and clearer hubs without adding schema.

## Final Classification

Keep:
- Flat page graph
- Topic DAG
- Unified wikilinks
- Structured sources and citations
- File-aware retrieval
- Lineage metadata
- Build/Absorb/Garden operation split
- Git-reviewed markdown source

Simplify:
- Docs that still teach `files:`
- Overloaded `agents` topic
- Large pages that now contain several page jobs
- Source lists that preserve raw session inventory rather than claim evidence

Delete candidate:
- Legacy string source entries after migration
- Stray `type: runtime-view` prompt heading
- Casual `status` field if no maintenance/query contract appears

Replace with library:
- None at the `.almanac` convention layer. This is not a solved-by-library problem. The existing use of standard YAML/markdown tooling in implementation is enough; the remaining issue is editorial structure.

Wrap:
- Wrap the graph with hubs and `getting-started.md`.
- Wrap prior-art vocabularies as guidance in prompts, not schema.
- Wrap source hygiene with deterministic health plus Garden judgement.

Research further:
- Whether web sources need snapshots.
- Whether issue/discussion source types should become first-class in all docs.
- Whether redirects/aliases need explicit metadata.
- Whether `verified` should become a queryable currentness field.
