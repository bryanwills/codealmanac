# Target Architecture For The .almanac Garden

Date: 2026-06-09

## Target Mental Model

The wiki should read as a curated graph of project memory, not as a transcript archive and not as a generated docs tree.

```text
repo-owned markdown corpus
  -> pages with strong leads, source citations, links, and topics
  -> a getting-started front door for first-entry routing
  -> hubs that route dense subjects
  -> anchors that own current truth for major subjects
  -> supporting pages for runtime, structure, rationale, constraints, workflows, and failures
  -> lineage for archived or superseded knowledge
  -> health and Garden to keep the graph current
```

## Boundaries To Preserve

### Flat Graph Storage

Keep `.almanac/pages/*.md` as the canonical page corpus for now. Do not move pages into topic folders. Multi-topic pages are a feature, not an accident.

### Topic DAG

Keep topics as browse neighborhoods. Topics are not reading order, page type, or currentness state.

### Wikilinks

Keep one double-bracket syntax. The page/file/folder/cross-wiki classifier is simple enough for agents and powerful enough for retrieval.

### Structured Sources

Keep `sources:` as the evidence model. Retire legacy source strings through migration and Garden cleanup. Do not return to `files:` as the primary provenance field.

### Garden As Judgment

Keep Garden as an AI lifecycle operation. Do not create a deterministic propose/review/apply state machine for editorial judgment. The prompt should name allowed structural outcomes: create, update, merge, split, redirect, archive, and no-op.

## Boundaries To Add

### Front Door

Add `getting-started` as a normal page. It should be the first page for a new agent that knows only that this repo has an Almanac wiki.

It should:

- name the main hubs and the first page to read in each area
- explain that topics are browse neighborhoods, not reading order
- state current vocabulary such as sync versus capture
- describe the product and external-reference shelves without putting them on the default engineering path
- point to `.almanac/README.md` for contribution rules

This page should not duplicate every hub. It should route.

### Hubs

A hub is a normal page whose job is navigation for a dense subject area. It should:

- name the canonical anchor pages
- give reading order
- separate current architecture from historical pages
- point to related decisions and failure modes
- explain where future facts should go

Initial hubs:

- `architecture-hub`
- `lifecycle-hub`
- `sync-hub`
- `wiki-design-hub`
- `product-strategy-hub`
- `competitive-landscape`
- `provider-harness-hub` only if provider work grows beyond three pages

### Anchors

An anchor is the canonical current-truth page for a named subject. Anchors do not need metadata yet. They need clear leads and inbound links from hubs.

Examples:

- `sqlite-indexer`
- `source-provenance`
- `lifecycle-architecture`
- `wiki-organization-primitives`
- future `sync-automation`
- future `github-native-wiki-maintenance` after split

### Redirects / Aliases

Capture-to-sync rename shows the need for lightweight redirect behavior. The target can be:

```yaml
---
title: Capture Automation
redirect_to: sync-automation
archived_at: 2026-06-09
superseded_by: sync-automation
---
```

That should be researched before implementation. Until then, use hub prose and lineage.

### Source Hygiene Tiering

Each page should fall into one of these evidence tiers:

- **Current contract**: current code, tests, prompts, config, docs, commits, or current external docs cite active claims.
- **Rationale/history**: sessions, PRs, issues, and old plans cite why decisions happened.
- **External reference**: web docs, competitor material, or books cite ideas and market/architecture lessons.
- **Speculative/proposed**: page lead says the content is proposed, and claims do not read as implemented behavior.

This can stay prose and prompt guidance at first. No source-status schema until a query or health need proves it.

## Page Neighborhood Model

For each major subject, use this shape:

```text
<subject>-hub or <subject> anchor
  current contract / overview
  runtime flow
  source or allocation placement
  decisions and rejected alternatives
  constraints / invariants
  failure modes / incidents
  workflow pages
  external references that shaped the subject
```

Small subjects can be one page. Major subjects should split when one page starts mixing maps, contracts, incidents, and strategy.

## Page Shape Contracts

Do not add `type:` frontmatter yet. Use these as README and Garden conventions:

- **Hub**: routes a dense subject, names canonical anchors, and separates current from historical/proposed pages.
- **Anchor**: states current truth for a stable concept or subsystem.
- **Contract**: records a behavior surface, interface, command, prompt contract, storage contract, or invariant.
- **Flow**: explains an end-to-end operation in time order.
- **Decision**: states context, options considered, outcome, consequences, and how to confirm whether the decision still holds.
- **Failure mode / incident**: records what broke, trigger conditions, fix, and future prevention.
- **External reference**: captures outside prior art, competitor behavior, or inspiration, and names the CodeAlmanac decision it shaped.

## Proposed Topic Adjustments

Keep the DAG, but make topic meanings narrower. A target root set can look like this:

- `architecture`: current implementation architecture and cross-subsystem design. Add this only with a hub so it does not become a catch-all.
- `lifecycle`: Build, Ingest, Garden, Sync, jobs, and lifecycle operation semantics.
- `storage`: page corpus, indexer, registry, topic DAG, source provenance, and path semantics.
- `cli`: command surface and local-machine UX.
- `provider-runtime`: Claude, Codex, provider harness, auth/readiness, and runtime boundaries.
- `prompt-system`: bundled lifecycle prompts and agent contracts.
- `wiki-model`: page/link/source/topic/Garden doctrine.
- `product-strategy`: product decisions that affect implementation, packaging, trust, pricing, or command design.
- `prior-art`: external references that are not direct competitors and are not current implementation.
- `competitive-research`: competitors and market alternatives.
- `automation`: scheduler and background job integration, if it remains distinct from lifecycle.
- `viewer`: `almanac serve` and future browse/UI surfaces, if viewer work resumes.

Use these as overlays or page-shape tags only if needed, not as substitutes for hubs:

- `decisions`
- `flows`
- `constraints`
- `failure-modes`
- `reference`

Remove or demote `fundraising` unless fundraising materially changes product, pricing, or trust architecture. Move pitch-only material to `docs/strategy/` or a separate product Almanac.

Retag `agents` aggressively. It should mean agent runtime, prompts, provider behavior, or agent-facing workflow. It should not be a default home for competitors, product strategy, or outside inspiration.

## Page Split Targets

### Sync

Target pages:

- `sync-hub`
- `sync-automation`
- `sync-flow`
- `sync-ledger`
- `sync-legacy-hooks`
- `sync-recursion-incident` or equivalent failure-mode page if the issue remains important

Old capture slugs should become aliases or archived lineage pages after redirect support exists.

### GitHub-Native Product

Target pages:

- `github-native-wiki-maintenance` as short anchor
- `github-pr-almanac-loop`
- `hosted-github-runner`
- `github-source-tools`
- `github-almanac-update-risks`
- `github-check-run-actions` only if implementation touches check-run button limits or action transport

### Product Strategy

Target pages:

- `product-strategy-hub`
- `almanac-product-family` as generalized product anchor
- `codealmanac-product-loop` or keep as section if not enough substance
- `almanac-business-model`
- `customer-segmentation`
- `competitive-landscape`

Move or demote pure fundraising/pitch material unless it changes a product decision.

### Viewer

Target pages only if viewer work resumes:

- `almanac-serve` as anchor
- `viewer-api-contract`
- `viewer-jobs-ui`
- `viewer-source-rail`

Otherwise do source cleanup first.

## What Becomes Easier

- A future agent can start at a hub and know what to read first.
- Garden can decide merge/split/archive/no-op with a named target shape.
- Source cleanup has a clear standard: source entries must support claims.
- Product research remains available without polluting engineering change workflows.
- Renames such as capture to sync stop leaking old vocabulary into new code.

## What Is Intentionally Unsupported For Now

- No frontmatter `type:` or `subject:` fields.
- No topic-folder storage.
- No numbered ADR-only decision log.
- No docs-site framework as the canonical wiki.
- No generic product notebook inside `.almanac`.
- No automatic web-source snapshotting until portability or trust demands it.
- No casual `status` or `verified` pseudo-schema unless the fields get documented semantics and query/health support.
