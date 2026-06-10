# Boundary Critic Report: `.almanac`

Date: 2026-06-09

Scope: `/Users/rohan/Desktop/Projects/codealmanac/.almanac`

Constraint followed: this report did not edit implementation code or `.almanac` pages. The worktree was already dirty, including many `.almanac/pages` changes, and this audit treats that state as user-owned.

## Goal

Critically audit the `.almanac` wiki as a boundary critic to determine which page neighborhoods, topics, documentation dependencies, hidden policies, and product/business notes should be preserved, simplified, removed, or redesigned.

Core questions:

- Why does each documentation boundary exist?
- Is it still needed?
- Is this the simplest shape that supports engineering retrieval?
- Did this complexity come from real product constraints or accumulated capture output?
- Where do product, market, and fundraising notes distort codebase-wiki retrieval?
- What would this wiki look like if its boundaries were redesigned today?

## Sources Inspected

- `.almanac/README.md`
- `.almanac/topics.yaml`
- representative `.almanac/pages/*.md`, including `lifecycle-architecture`, `wiki-organization-primitives`, `almanac-product-family`, `github-native-wiki-maintenance`, `source-provenance`, `evidence-bundles`, `company-brain`, `customer-segmentation`, `hosted-deployment-environment`, `pitch-deck-fundraising`, `documenting-software-architectures`, `farzapedia`, `opendeepwiki`, `superpaper`, `wiki-clarifications`, and provider/lifecycle pages
- `MANUAL.md`
- `README.md`
- `/Users/rohan/Desktop/Projects/openalmanac/docs/ideas/codebase-wiki.md`
- `docs/manual/good-codebase-wikis.md`
- existing audit worklog at `docs/refactor-audit-2026-06-09/worklog.md`

## Executive Diagnosis

The `.almanac` wiki has a strong core model: repo-owned Markdown pages, flat slugs, a topic DAG, wikilinks, file/source-aware retrieval, and a local index. Keep that. The storage model is not the problem.

The problem is boundary pressure from three different knowledge products sharing one graph:

1. engineering memory for this TypeScript CLI,
2. product strategy for Almanac as a business,
3. external research about documentation systems, competitors, and future hosted products.

Those three products can coexist, but the current topics do not keep them cleanly separated. Product pages are now cross-tagged into engineering neighborhoods such as `agents`, `stack`, and `wiki-design`; external-reference pages are tagged as if they are part of current architecture; and the broad `agents` topic has become a junk drawer for provider runtimes, prompts, instructions, external writing systems, product direction, and competitor memory.

The best gardening move is not a complete rewrite of the storage format. It is a topic and hub redesign that makes the wiki expose four first-class neighborhoods:

- engineering architecture,
- wiki-system design,
- product strategy,
- external references.

Within that shape, product and business notes should stay only when they change engineering direction, trust boundaries, packaging, pricing, or roadmap. Pure investor or GTM notes should move out of engineering retrieval by default.

## Current Architecture Map

The README explicitly defines the wiki as more than code documentation. It says this repo wiki preserves "design decisions, subsystem contracts, agent prompt behavior, external runtime assumptions, product semantics, constraints, and failure modes" (`.almanac/README.md:3`). Its notability bar includes "a product or market conclusion that changes how Almanac should be built, positioned, priced, or trusted" (`.almanac/README.md:16`).

The topic graph has 14 topics:

- engineering roots: `stack`, `systems`, `flows`, `decisions`
- engineering children: `agents`, `cli`, `automation`, `storage`, `provider-harness`, `prompt-system`
- wiki/product crossover: `wiki-design`
- product roots: `product-positioning`, `fundraising`, `competitive-research`

The graph currently has 52 pages. The largest topic neighborhoods are:

- `agents`: 25 pages
- `product-positioning`: 18 pages
- `cli`: 17 pages
- `systems`: 13 pages
- `flows`: 13 pages
- `decisions`: 13 pages
- `competitive-research`: 11 pages
- `wiki-design`: 10 pages

That distribution is the main smell. Engineering retrieval is dominated by broad concepts that are doing too much.

## Findings

### 1. Keep: the flat graph model is correct

Classification: keep

Evidence:

- The README says pages live under `.almanac/pages/`, carry `title`, `topics`, and `sources`, and that `sources[type=file]` powers file-aware retrieval (`.almanac/README.md:76` to `.almanac/README.md:80`).
- `wiki-organization-primitives` says the committed primitives are page, link, topic, file reference, lineage, indexer-backed query surface, and operation prompts (`.almanac/pages/wiki-organization-primitives.md:148` to `.almanac/pages/wiki-organization-primitives.md:160`).
- `source-provenance` correctly separates evidence sources from navigation links and keeps `sources:` as the canonical evidence field while preserving `file_refs` for `search --mentions` (`.almanac/pages/source-provenance.md:103` to `.almanac/pages/source-provenance.md:109`).

Why it exists today:

This repo is the product's reference implementation. The wiki needs to demonstrate the artifact CodeAlmanac sells: durable, reviewable, source-linked project memory next to code.

Why the reason is still good enough:

The current storage model maps directly to the product thesis. It gives future agents a deterministic reading path and gives humans normal Git review.

Architectural cost:

Flat pages need stronger hubs and topic discipline because filesystem placement does not provide a default reading path.

Recommendation:

Keep flat pages, wikilinks, topics, sources, and file-aware retrieval. Do not replace them with folders as meaning. Add curated hub pages and stricter retopicing rules instead.

Confidence: high

### 2. Redesign: `agents` has become an overloaded topic

Classification: redesign

Evidence:

- `topics.yaml` defines `agents` as "AI agent integration - harness providers, operation prompts, Build, Absorb, Garden" and gives it parents `flows` and `stack` (`.almanac/topics.yaml:22` to `.almanac/topics.yaml:25`).
- The README repeats that broad definition (`.almanac/README.md:31`).
- The current `agents` topic contains 25 pages, including provider/runtime pages (`claude-agent-sdk`, `harness-providers`), operation pages (`build-operation`, `capture-flow`, `ingest-operation`), prompt pages (`operation-prompts`, `farzapedia`, `documenting-software-architectures`), product pages (`just-in-time-context-surfacing`, `evidence-bundles`, `superpaper`, `codex-supermemory`), and maintenance/workflow pages (`wiki-clarifications`, `deep-refactor-audit`).
- `wiki-organization-primitives` already admits the problem: "`agents` topic mixes provider runtimes, operation prompts, external references, product direction, and wiki-organization theory" (`.almanac/pages/wiki-organization-primitives.md:337` to `.almanac/pages/wiki-organization-primitives.md:343`).

Why it exists today:

The product is agent-centered, so many pages legitimately involve agents. Early capture likely used `agents` as the safe default for "AI-related".

Why that reason is no longer good enough:

`agents` now answers too many retrieval questions. A future agent changing `src/harness/providers/codex/` does not need competitor memory about Supermemory. A future agent editing prompts does not need hosted product packaging unless that page has a direct prompt invariant.

Architectural cost:

The topic weakens retrieval precision. It also hides which page owns which boundary: provider runtime, operation semantics, prompt doctrine, instruction installation, external prior art, or product direction.

Recommendation:

Split the topic neighborhood conceptually:

- `agent-runtime`: harness providers, provider capabilities, runtime execution, app-server/SDK boundaries.
- `agent-instructions`: AGENTS/CLAUDE/Codex instruction installation and setup behavior.
- `operation-prompts`: Build/Absorb/Garden prompt contracts and external writing references that directly shape prompts.
- `lifecycle-operations`: Build, Absorb, Garden, sync, ingest, jobs.
- `external-agent-memory`: competitor/reference systems such as Codex Supermemory, Mem0, Agentmemory.

The existing `agents` topic can remain as a parent if useful, but it should not be the topic future agents use for precise retrieval.

Confidence: high

### 3. Redesign: product strategy is allowed, but it leaks into engineering topics too freely

Classification: redesign

Evidence:

- The README intentionally admits product and market conclusions into the notability bar (`.almanac/README.md:16`).
- `topics.yaml` defines `product-positioning` as product, market, user, pricing, and positioning synthesis (`.almanac/topics.yaml:42` to `.almanac/topics.yaml:45`).
- Pages with `product-positioning` are cross-tagged into engineering topics:
  - `just-in-time-context-surfacing`: `product-positioning`, `agents` (`.almanac/pages/just-in-time-context-surfacing.md:1` to `.almanac/pages/just-in-time-context-surfacing.md:5`)
  - `evidence-bundles`: `wiki-design`, `product-positioning`, `agents` (`.almanac/pages/evidence-bundles.md:1` to `.almanac/pages/evidence-bundles.md:5`)
  - `hosted-deployment-environment`: `product-positioning`, `stack` (`.almanac/pages/hosted-deployment-environment.md:1` to `.almanac/pages/hosted-deployment-environment.md:5`)
  - `superpaper`: `wiki-design`, `product-positioning`, `agents`, `competitive-research` (`.almanac/pages/superpaper.md:1` to `.almanac/pages/superpaper.md:5`)
  - `wiki-clarifications`: `agents`, `flows`, `product-positioning` (`.almanac/pages/wiki-clarifications.md:1` to `.almanac/pages/wiki-clarifications.md:5`)

Why it exists today:

Product strategy is shaping architecture. For this repo, business model and trust strategy legitimately affect local/hosted boundaries, GitHub App behavior, source provenance, and review surfaces.

Why that reason is not enough:

The current tagging does not distinguish product strategy that imposes a code invariant from product strategy that merely explains positioning. That makes engineering queries retrieve broad GTM, segmentation, fundraising, and competitor pages.

Architectural cost:

Agents asked to change implementation code may over-read business notes and under-read current code-contract pages. Product strategy becomes ambient context instead of a named dependency.

Recommendation:

Use stricter tagging:

- Product-only pages stay under `product-positioning`, `fundraising`, `competitive-research`, or a new `hosted-product` topic.
- A product page gets an engineering topic only when it contains a present-tense implementation invariant, command contract, source schema, or file-specific rule.
- Product pages that influence architecture should link to the engineering anchor instead of joining the engineering topic. Example: `almanac-business-model` can link to `github-native-wiki-maintenance` and `source-provenance`, but it does not need `decisions` unless it records a concrete architecture choice future code must preserve.
- Add an explicit bridge topic such as `product-architecture` only for pages whose primary job is translating product direction into engineering boundaries.

Confidence: high

### 4. Redesign: `wiki-design` is carrying product, architecture, prompt, and external-reference work at once

Classification: redesign

Evidence:

- `wiki-design` is defined as "Product and architecture decisions about what a codebase wiki should contain and how pages, hubs, topics, and links should fit together" (`.almanac/topics.yaml:47` to `.almanac/topics.yaml:50`).
- Current pages under `wiki-design` include product-family generalization, external competitors, prompt contracts, source provenance, OpenDeepWiki, Superpaper, GitHub-native product strategy, and organization primitives.
- `wiki-organization-primitives` says topics are an index, not a map, and cannot express reading order or canonical architecture versus supporting context (`.almanac/pages/wiki-organization-primitives.md:235` to `.almanac/pages/wiki-organization-primitives.md:255`).

Why it exists today:

The wiki itself is the product, so every question about docs structure, prompt behavior, product scope, and hosted presentation can plausibly be called "wiki design".

Why that reason is no longer good enough:

The topic now hides four distinct reasons to read:

- current mechanics of CodeAlmanac wiki storage,
- editorial doctrine for agents,
- generalized Almanac product model,
- external reference or competitor lessons.

Architectural cost:

`wiki-design` cannot tell a coding agent whether a page is current contract, future product sketch, borrowed pattern, or competitor comparison.

Recommendation:

Split the neighborhood:

- `wiki-model`: page/link/topic/source/lineage/indexer primitives and current `.almanac` mechanics.
- `wiki-editorial-system`: page naming, hubs, anchors, Garden, source hygiene, writing doctrine.
- `prompt-system`: operation prompts and external writing references that directly change prompt behavior.
- `external-references`: Documenting Software Architectures, Farzapedia, OpenDeepWiki, Superpaper, Diataxis-style lessons.
- `hosted-product`: GitHub App, hosted workflow, dashboard/deployment strategy.

The existing `wiki-design` can become a parent topic or a hub page, but it should stop being the retrieval neighborhood for everything.

Confidence: high

### 5. Simplify: subject neighborhoods are described but not consistently materialized

Classification: simplify

Evidence:

- The README says major entities may need a "subject neighborhood" and that the anchor page should route readers (`.almanac/README.md:54`).
- `wiki-organization-primitives` defines anchor pages and subject neighborhoods (`.almanac/pages/wiki-organization-primitives.md:210` to `.almanac/pages/wiki-organization-primitives.md:233`).
- `lifecycle-architecture` is a good hub: it tells readers which page to start with for semantic operations, CLI commands, job history, and provider runtime (`.almanac/pages/lifecycle-architecture.md:48` to `.almanac/pages/lifecycle-architecture.md:63`).
- `company-brain` is the opposite pattern: its related-pages paragraph routes to customer segmentation, GitHub-native wiki maintenance, product family, pitch deck, Agentmemory, Codex Supermemory, Mem0, Moxie, Dosu, just-in-time context surfacing, lifecycle operations, and Farzapedia in one paragraph (`.almanac/pages/company-brain.md:192` to `.almanac/pages/company-brain.md:194`).

Why it exists today:

The wiki learned through capture. Links accreted as new related pages appeared, while hub pages did not always get promoted into explicit maps.

Why the reason is not good enough:

The graph has enough pages that related-page dumps are now a weak substitute for real routing.

Architectural cost:

Agents have to infer which page is anchor, which page is supporting rationale, which page is historical, and which page is merely external comparison.

Recommendation:

Create or strengthen four hub pages as normal wiki pages:

- engineering architecture hub, with `lifecycle-architecture` as the current starting point;
- wiki-system hub, owning `wiki-organization-primitives`, `source-provenance`, `wikilink-syntax`, `topic-dag`, and Garden/prompt doctrine;
- product strategy hub, owning market, customer, pricing, and hosted-product pages;
- external references hub, owning competitors and borrowed documentation systems.

Then shorten related-pages sections so they point to the relevant hub and a small number of direct dependencies.

Confidence: high

### 6. Delete candidate from engineering retrieval: fundraising material

Classification: delete candidate from `.almanac` engineering retrieval; keep only if treated as product-strategy memory

Evidence:

- `fundraising` is defined as investor-facing narrative, pitch deck, and financing assumptions (`.almanac/topics.yaml:52` to `.almanac/topics.yaml:55`).
- `pitch-deck-fundraising` says the deck should earn an investor meeting and compress the product into a fundraising story (`.almanac/pages/pitch-deck-fundraising.md:44` to `.almanac/pages/pitch-deck-fundraising.md:48`).
- The page links implementation pages such as `ingest-operation`, `capture-flow`, `wiki-lifecycle-operations`, and `almanac-serve` only to explain how product story compresses them (`.almanac/pages/pitch-deck-fundraising.md:122` to `.almanac/pages/pitch-deck-fundraising.md:124`).

Why it exists today:

The README notability bar explicitly allows product/market conclusions that affect how the product is positioned, priced, or trusted.

Why that reason may no longer be good enough:

Fundraising story rarely helps a coding agent modify code safely. It may help a founder or GTM agent, but it is a different retrieval job from engineering memory.

Architectural cost:

Fundraising pages make `.almanac` less obviously a codebase wiki. They also invite future Absorb/Garden runs to preserve investor narrative inside a graph whose primary runtime consumer is a coding agent.

Recommendation:

Either move fundraising pages to `docs/strategy/` or keep them under a product-only topic that is never a descendant of engineering topics. Do not link fundraising pages from engineering hubs except as optional product context.

Confidence: medium-high

### 7. Redesign: hosted deployment state belongs to a hosted-product neighborhood, not `stack`

Classification: redesign

Evidence:

- `stack` means "Third-party technologies and libraries the CLI depends on" (`.almanac/topics.yaml:2` to `.almanac/topics.yaml:5`).
- `hosted-deployment-environment` is tagged `product-positioning` and `stack`, but its summary says it records the `usealmanac` repository and hosted resource namespace across Vercel, Render, Supabase, Modal, and Doppler (`.almanac/pages/hosted-deployment-environment.md:1` to `.almanac/pages/hosted-deployment-environment.md:5`).
- The page states that `usealmanac` is the code home for hosted frontend, FastAPI backend, Modal worker scaffold, provider docs, and deployment configuration, while `codealmanac` is the shared resource name (`.almanac/pages/hosted-deployment-environment.md:31` to `.almanac/pages/hosted-deployment-environment.md:37`).

Why it exists today:

Hosted GitHub App direction is product-critical and shares the CodeAlmanac name, so hosted environment state got captured into this repo's wiki.

Why that reason is not enough:

The page is about another repo and hosted deployment operations, not dependencies of the local TypeScript CLI. `stack` retrieval for this repo should not return Render, Supabase, Modal, Doppler, and Vercel unless the local CLI depends on those systems.

Architectural cost:

The `stack` topic loses meaning. A future agent auditing CLI dependencies could read hosted deployment state and assume the CLI has cloud runtime obligations it does not have.

Recommendation:

Move this page into a `hosted-product` or `almanac-for-github` neighborhood, or into the `usealmanac` wiki if that repo owns the implementation. Keep only the cross-repo boundary summary in `github-native-wiki-maintenance`: hosted service can compute/propose/publish, durable project memory remains repo-owned Markdown.

Confidence: high

### 8. Keep but rename around: source provenance and evidence bundles separate the right concepts

Classification: keep, with naming simplification

Evidence:

- `source-provenance` says page `sources:` are evidence after a page has been written and are separate from connector ingestion (`.almanac/pages/source-provenance.md:137` to `.almanac/pages/source-provenance.md:147`).
- `evidence-bundles` says the bundle is pre-page operation input and separate from `sources:` frontmatter (`.almanac/pages/evidence-bundles.md:64` to `.almanac/pages/evidence-bundles.md:67`).
- `evidence-bundles` also states that "source" now names page evidence, operation input, and future connector runtime concepts at the same time (`.almanac/pages/evidence-bundles.md:70` to `.almanac/pages/evidence-bundles.md:77`).

Why it exists today:

The product genuinely has two different source concepts: evidence that supports a written claim and source material that triggers/runs an operation.

Why the reason remains good:

Collapsing those concepts would make pages carry transient webhook/run state or make operations pretend page citations exist before any durable claim is written.

Architectural cost:

The word "source" is overloaded enough that page titles and topics need to be sharper than they are today.

Recommendation:

Keep the conceptual split. In future gardening, consider renaming the page or neighborhood around `operation-input-boundary`, `source-event-boundary`, or `connector-run-input` if "evidence bundle" keeps attracting product pages into `agents` and `wiki-design`.

Confidence: high

### 9. Redesign: external-reference pages are tagged as current architecture too often

Classification: redesign

Evidence:

- `documenting-software-architectures` is an external reference page, but it has `decisions`, `agents`, `wiki-design`, and `prompt-system` topics (`.almanac/pages/documenting-software-architectures.md:1` to `.almanac/pages/documenting-software-architectures.md:11`).
- `farzapedia` is an external wiki-system reference, but it has `agents`, `decisions`, and `prompt-system` topics (`.almanac/pages/farzapedia.md:1` to `.almanac/pages/farzapedia.md:5`).
- `opendeepwiki` is a generated codebase-documentation reference with `competitive-research`, `wiki-design`, and `prompt-system` topics (`.almanac/pages/opendeepwiki.md:1` to `.almanac/pages/opendeepwiki.md:5`).
- `superpaper` is an Obsidian-first personal knowledge system with `wiki-design`, `product-positioning`, `agents`, and `competitive-research` topics (`.almanac/pages/superpaper.md:1` to `.almanac/pages/superpaper.md:5`).

Why it exists today:

These references shaped prompt design and wiki doctrine. They are useful because they preserve imported vocabulary and rejected alternatives.

Why that reason is not enough:

The current tags make references appear in the same neighborhoods as current implementation contracts. A page can influence an architecture without belonging in the current architecture topic.

Architectural cost:

Agents can mistake prior art for current contract. The more external pages accumulate, the harder it becomes to ask "what do I need to preserve in this repo today?"

Recommendation:

Create `external-references` as a parent topic, with child topics such as `competitive-research`, `documentation-prior-art`, and `memory-products`. Put adopted lessons into current architecture pages. The external page should be evidence and comparison; the current page should own the rule.

Confidence: high

### 10. Unknown: status and verification semantics are not consistently meaningful

Classification: unknown

Evidence:

- Some pages have `status: active`, some have `status: implemented`, some have `status: proposed`, and many have no status.
- `evidence-bundles` is `status: proposed` but contains implemented local GitHub source-aware ingest behavior and future hosted architecture in the same page (`.almanac/pages/evidence-bundles.md:58`, `.almanac/pages/evidence-bundles.md:113` to `.almanac/pages/evidence-bundles.md:133`).
- `source-provenance` has a detailed truth/currentness model and warns that source ordering is not a currentness model (`.almanac/pages/source-provenance.md:161` to `.almanac/pages/source-provenance.md:171`).

Why it exists today:

Status likely accumulated from capture and manual edits rather than one enforced schema.

Why this is not yet a definite bug:

The README treats page shapes as suggestions, not schema (`.almanac/README.md:44` to `.almanac/README.md:54`). A flexible wiki should not overfit status fields before there is a query or health feature that consumes them.

Architectural cost:

If status is visible but semantically weak, agents may trust it incorrectly.

Recommendation:

Either remove casual status use from pages where it is not mechanically meaningful, or define a small status convention in `.almanac/README.md`: `active`, `proposed`, `historical`, `superseded`, `external-reference`. Do not use status as a substitute for explicit prose about what is current.

Confidence: medium

## Page And Topic Actions

| Page/topic | Current boundary issue | Classification | Recommended action |
|---|---|---:|---|
| `agents` topic | Mixes runtime, prompts, operations, product, competitors, and external references | Redesign | Split into narrower child topics or stop using it for precise retrieval |
| `wiki-design` topic | Mixes current wiki mechanics, product generalization, prompt doctrine, and external references | Redesign | Split into `wiki-model`, `wiki-editorial-system`, `external-references`, and `hosted-product` |
| `product-positioning` topic | Legitimate but too often cross-tagged into engineering topics | Redesign | Keep product pages isolated unless they contain a current engineering invariant |
| `pitch-deck-fundraising` | Investor narrative has low value for coding-agent retrieval | Delete candidate from engineering wiki | Move to `docs/strategy/` or keep product-only |
| `hosted-deployment-environment` | Describes `usealmanac` hosted resources but is tagged `stack` | Redesign | Move to hosted-product or `usealmanac` wiki; remove `stack` |
| `evidence-bundles` | Correct concept, but too broad and cross-tagged | Simplify | Keep split from `source-provenance`; consider renaming around operation input |
| `source-provenance` | Strong boundary page | Keep | Use it as the canonical page-evidence contract |
| `lifecycle-architecture` | Good hub behavior | Keep | Use as model for other hubs |
| `company-brain` | Useful market anchor, but related-pages section is a graph dump | Simplify | Route through a product hub and reduce direct links |
| external-reference pages | Prior art tagged as if current architecture | Redesign | Put under `external-references`; copy adopted rules into current contract pages |

## Target Wiki Boundary

A cleaner `.almanac` would have four visible neighborhoods.

### Engineering Memory

Purpose: help future coding agents modify this repo safely.

Topics:

- `systems`
- `flows`
- `cli`
- `storage`
- `automation`
- `provider-harness`
- `lifecycle-operations`
- `agent-runtime`
- `agent-instructions`

Pages:

- `lifecycle-architecture`
- `wiki-lifecycle-operations`
- `harness-providers`
- `process-manager-runs`
- `capture-flow`
- `capture-ledger`
- `sqlite-indexer`
- `topic-dag`
- `global-registry`
- `almanac-doctor`
- `almanac-serve`

Rule: product pages do not enter this neighborhood unless they define a current implementation boundary.

### Wiki System Model

Purpose: explain how Almanac pages, topics, links, sources, prompts, hubs, and Garden should behave.

Topics:

- `wiki-model`
- `wiki-editorial-system`
- `source-provenance`
- `prompt-system`
- `garden-maintenance`

Pages:

- `wiki-organization-primitives`
- `source-provenance`
- `wikilink-syntax`
- `operation-prompts`
- `documenting-software-architectures` only if retagged as external reference plus adopted lesson

Rule: this neighborhood owns reusable wiki architecture, not GTM or hosted deployment resources.

### Product Strategy

Purpose: preserve product, market, packaging, trust, and business decisions that shape what should be built.

Topics:

- `product-positioning`
- `customer-segments`
- `business-model`
- `hosted-product`
- `fundraising`

Pages:

- `almanac-product-family`
- `almanac-business-model`
- `customer-segmentation`
- `github-native-wiki-maintenance`
- `just-in-time-context-surfacing`
- `hosted-deployment-environment`, if it remains in this repo
- `pitch-deck-fundraising`, if it remains in `.almanac`

Rule: product strategy links to engineering anchors when it constrains architecture; it does not join engineering topics by default.

### External References

Purpose: preserve prior art, competitors, and borrowed vocabulary without making them current project contract.

Topics:

- `external-references`
- `competitive-research`
- `documentation-prior-art`
- `memory-products`

Pages:

- `company-brain`
- `agentmemory-competitor`
- `codex-supermemory`
- `mem0`
- `moxie-docs`
- `dosu`
- `opendeepwiki`
- `farzapedia`
- `superpaper`
- `documenting-software-architectures`

Rule: external pages should end with "adopted lesson" and link to the current page that owns the rule. They should not be the place a coding agent must read to know current implementation behavior.

## Gardening Roadmap

### Phase 0: Freeze noisy cross-tagging

Goal: stop new graph drift before retopicing.

Changes:

- No new product-only pages under `agents`, `stack`, `systems`, `cli`, `flows`, or `storage`.
- No new external-reference pages under `agents` unless they document a current agent runtime contract.
- No new hosted deployment runbooks under `stack` for this CLI repo.

Why first:

New capture output will otherwise keep reinforcing the current broad neighborhoods.

Risk:

Low. This is editorial policy, not storage change.

Verification:

Run topic page inventory and inspect pages with both `product-positioning` and engineering topics.

### Phase 1: Retopic the most misleading pages

Goal: restore retrieval precision without rewriting prose.

Changes:

- Remove `stack` from `hosted-deployment-environment`.
- Remove engineering topics from product-only and external-reference pages unless a current implementation contract justifies them.
- Move Farzapedia, OpenDeepWiki, Superpaper, Documenting Software Architectures, and competitor pages under `external-references` or its children.
- Keep `source-provenance`, `operation-prompts`, and `harness-providers` in engineering/wiki-system neighborhoods because they are current contracts.

Why first:

Retopicing is cheaper and safer than page rewrites, and it immediately improves topic retrieval.

Risk:

Medium. Some pages carry both product and engineering value. Use direct links from engineering hubs to preserve important bridge pages.

Verification:

Topic inventory should show fewer product pages under `agents`, `stack`, and `wiki-design`.

### Phase 2: Promote hubs as maps

Goal: make first-read paths explicit.

Changes:

- Keep `lifecycle-architecture` as the engineering lifecycle hub.
- Add or strengthen a wiki-system hub that routes through organization primitives, source provenance, wikilinks, topics, prompts, and Garden.
- Add a product strategy hub that routes through business model, customer segmentation, hosted product, and fundraising.
- Add an external references hub that separates competitor pages from documentation-prior-art pages.

Why first:

Hubs solve what topics cannot: reading order, canonical current pages, historical/supporting pages, and "read this first" guidance.

Risk:

Medium. Hubs can become stale if they restate too much content. Keep them as maps, not duplicate summaries.

Verification:

A new agent should be able to answer "where do I start for provider runtime?", "where do I start for wiki design?", and "where do I start for product positioning?" without scanning a topic with 20 pages.

### Phase 3: Split or move low-engineering pages

Goal: reduce wiki retrieval noise.

Changes:

- Move `pitch-deck-fundraising` to `docs/strategy/` unless `.almanac` intentionally serves founder strategy agents as a first-class consumer.
- Move `hosted-deployment-environment` to the `usealmanac` wiki if that repo owns the hosted implementation.
- Consider moving pure competitor pages to an external-references neighborhood that is opt-in from engineering hubs.

Why first:

Some pages are useful, but useful for a different reader. Moving or isolating them clarifies the primary `.almanac` contract.

Risk:

Medium-high. Product memory may be intentionally colocated because CodeAlmanac is the product repo. The safer move is isolation before deletion.

Verification:

Engineering file/topic searches should stop surfacing fundraising, market, and hosted-resource pages unless the query explicitly asks for product strategy.

### Phase 4: Clarify status/currentness conventions

Goal: make page metadata trustworthy.

Changes:

- Define status values if they remain in frontmatter.
- Prefer explicit prose for "current implementation", "proposal", "external reference", "historical", and "superseded".
- Avoid using `verified` as a substitute for source-backed currentness.

Why first:

Currentness is already a product requirement in `source-provenance`, but metadata is inconsistent.

Risk:

Low to medium. Over-schema can make wiki writing stiff; keep it light.

Verification:

Garden or health should not need to infer truth from source order, `verified`, or casual `status`.

## Strongest Objections To The Current Shape

1. `agents` is no longer a meaningful boundary. It is an umbrella over almost every interesting thing in this product.
2. `wiki-design` is a false friend. It sounds precise, but it currently means storage primitives, editorial doctrine, prompt behavior, product generalization, and competitor lessons.
3. `stack` is being diluted by hosted deployment state from another repo.
4. Product strategy is useful but needs opt-in retrieval. It should constrain engineering through links and bridge pages, not by living in every engineering topic.
5. External prior art should not be tagged as current architecture. Borrowed lessons belong in the current architecture page that owns the rule.

## Legitimate Complexity Worth Preserving

- Product strategy inside the repo wiki is legitimate when it changes code direction, trust architecture, packaging, or roadmap.
- External references are legitimate when they explain why Almanac adopted or rejected a pattern.
- The flat page layout is legitimate because pages can belong to multiple conceptual neighborhoods.
- The source/provenance model is legitimate because it separates trust evidence from graph navigation.
- Hubs are legitimate editorial machinery because topics cannot express reading order.

## Open Questions For The Main Audit

- Should `.almanac` be the memory layer for both coding agents and founder/product agents, or should product/fundraising strategy move to `docs/strategy/`?
- Should `hosted-deployment-environment` live in this repo, or should the `usealmanac` repo own hosted operational truth with this wiki retaining only product/architecture boundaries?
- Should `external-references` become a real topic now, or should external pages be moved under more specific existing topics with clearer hub routing?
- Should page status/currentness become a documented convention, or should it stay prose-only until a query feature needs it?
- Should `agents` remain as a broad parent topic, or should it disappear in favor of precise topics such as `agent-runtime`, `agent-instructions`, and `operation-prompts`?
