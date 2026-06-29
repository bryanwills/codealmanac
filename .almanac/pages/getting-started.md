---
title: Getting Started
summary: Getting Started is the wiki front door that routes future agents from task intent to the core CodeAlmanac pages and clusters.
topics: [wiki-design, systems, flows, agents]
sources:
  - id: wiki-readme
    type: file
    path: .almanac/README.md
    note: Defines this repo wiki's purpose, topic taxonomy, page shapes, and agent-facing writing conventions.
  - id: build-prompt
    type: file
    path: prompts/operations/build.md
    note: Requires `.almanac/pages/getting-started.md` as the canonical front door and rejects a second `project-overview.md` front-door page.
  - id: repo-manual
    type: file
    path: MANUAL.md
    note: Defines the repo's engineering and architecture-building doctrine, which is distinct from wiki-writing doctrine.
  - id: human-manual-seed
    type: file
    path: docs/manual/good-codebase-wikis.md
    note: Provides the short human-facing manual seed for codebase wiki quality, sources, links, names, and subject neighborhoods.
  - id: notability-prompt
    type: file
    path: prompts/base/notability.md
    note: Defines the agent-facing rules for what deserves a page, topic, hub, or no-op.
  - id: syntax-prompt
    type: file
    path: prompts/base/syntax.md
    note: Defines the agent-facing page syntax, frontmatter, citations, wikilinks, grounding, page shape, and source-control rules.
  - id: lifecycle-architecture
    type: wiki
    slug: lifecycle-architecture
    note: Provides the reading map for lifecycle operations, CLI commands, jobs, providers, and automation.
  - id: wiki-lifecycle-operations
    type: wiki
    slug: wiki-lifecycle-operations
    note: Explains Build, Absorb, and Garden as semantic AI write operations.
  - id: source-provenance
    type: wiki
    slug: source-provenance
    note: Defines the page evidence model, citation contract, and legacy source migration boundary.
  - id: wiki-organization-primitives
    type: wiki
    slug: wiki-organization-primitives
    note: Explains pages, links, topics, lineage, hubs, anchors, and graph-shape doctrine.
  - id: sqlite-indexer
    type: wiki
    slug: sqlite-indexer
    note: Explains the SQLite projection that powers search, show, health, topics, links, and file-aware retrieval.
  - id: harness-providers
    type: wiki
    slug: harness-providers
    note: Explains the provider-neutral harness boundary and provider adapters.
  - id: product-family
    type: wiki
    slug: almanac-product-family
    note: Places CodeAlmanac inside the broader Almanac product family and object model.
status: active
verified: 2026-06-09
---

# Getting Started

This page is the front door for the CodeAlmanac wiki. It exists because Build treats `.almanac/pages/getting-started.md` as the canonical orientation page and rejects a second front-door page such as `project-overview.md`. [@build-prompt]

Use this page to choose a reading path before changing code. The wiki's job is to preserve project understanding that is not obvious from source files alone, and topics are browse neighborhoods rather than a reliable read order. [@wiki-readme]

## Where guidance lives

CodeAlmanac guidance is intentionally split by audience and job. `[[.almanac/README.md]]` is the repo wiki charter for notability, topic taxonomy, page shapes, linking, and the flat `.almanac/pages/` layout. [@wiki-readme]

`[[docs/manual/good-codebase-wikis.md]]` is the short human-facing manual seed for codebase wiki quality. It defines sources as trust evidence, links as navigation, readable page names, and subject neighborhoods for large areas. [@human-manual-seed]

`[[prompts/base/notability.md]]` and `[[prompts/base/syntax.md]]` are the agent-facing wiki-writing doctrine loaded by lifecycle operations. They define page existence, topic and hub judgment, structured `sources:`, citation markers, wikilink syntax, grounding, page shape, and source-control hygiene. [@notability-prompt] [@syntax-prompt]

`[[./MANUAL.md]]` is the repo engineering manual. Read it before implementing features because it defines how this project evolves architecture, but do not treat it as the wiki-writing manual. [@repo-manual]

## Start by task

| Task | Open first | Then read |
| --- | --- | --- |
| Change AI wiki write operations, job execution, or lifecycle boundaries | [[lifecycle-architecture]] | [[wiki-lifecycle-operations]], [[operation-prompts]], [[process-manager-runs]], [[lifecycle-cli]] |
| Change transcript sync, scheduled capture, or automation | [[capture-flow]] | [[capture-automation]], [[capture-ledger]], [[automation]], [[sessionend-hook]] |
| Change search, file mentions, health, sources, links, or topics | [[sqlite-indexer]] | [[source-provenance]], [[wikilink-syntax]], [[topic-dag]], [[global-registry]] |
| Change Claude, Codex, Cursor, or future provider execution | [[harness-providers]] | [[provider-lifecycle-boundary]], [[claude-agent-sdk]], [[agents-md]], [[global-agent-instructions]] |
| Change operation prompts or wiki-writing doctrine | [[wiki-organization-primitives]] | [[operation-prompts]], [[documenting-software-architectures]], [[farzapedia]], [[source-provenance]] |
| Change product shape, hosted GitHub workflows, or positioning | [[almanac-product-family]] | [[just-in-time-context-surfacing]], [[github-native-wiki-maintenance]], [[company-brain]], [[customer-segmentation]] |

[[lifecycle-architecture]] is the current hub for the write-capable runtime: operations, CLI routing, provider execution, job records, and scheduled maintenance. [@lifecycle-architecture]

[[wiki-lifecycle-operations]] is the semantic overview for Build, Absorb, and Garden. It matters when a change affects what kind of wiki work an operation performs rather than how a provider process runs. [@wiki-lifecycle-operations]

[[source-provenance]] is the evidence contract. It explains why `sources:` is canonical, why `files:` remains legacy compatibility, how citations work, and why deterministic source-frontmatter migration is not Garden-owned prose editing. [@source-provenance]

[[wiki-organization-primitives]] is the graph-shape doctrine. It explains why pages, links, topics, and lineage are storage primitives while hubs, anchors, redirects, and gardening remain editorial conventions until a query need proves otherwise. [@wiki-organization-primitives]

[[sqlite-indexer]] is the storage projection to read before changing query behavior. It owns the local SQLite index that backs `search`, `show`, `health`, topic queries, wikilinks, and file-aware retrieval. [@sqlite-indexer]

[[harness-providers]] is the provider execution boundary. It explains how provider-neutral operation specs become Claude, Codex, Cursor, or future runtime executions without leaking SDK details into lifecycle code. [@harness-providers]

[[almanac-product-family]] is the product-shape entry point. It separates the local repo-owned wiki, hosted workflow products, source objects, operations, pages, and topics so product work does not collapse every idea into the CLI. [@product-family]

## Core model

The committed wiki source is `.almanac/README.md`, `.almanac/pages/`, and `.almanac/topics.yaml`. The derived local layer is `.almanac/index.db`, job records, logs, and viewer state. Future agents should trust current code for present-tense behavior, but the wiki usually explains why the code has its current shape. [@wiki-readme]

The main runtime split is operations, jobs, and providers. Operations define wiki semantics, jobs record and observe one run, and providers translate a neutral spec into Claude, Codex, Cursor, or another runtime. Start with [[lifecycle-architecture]] when a change crosses those boundaries. [@lifecycle-architecture]

The main wiki-quality split is evidence versus navigation. `sources:` and citation markers explain why a claim is believable; wikilinks and topics explain where to read next. When a page has many source entries but few citations, treat that as source hygiene debt rather than proof that the underlying source list is useless. [@source-provenance]

## Current cautions

Do not use this page as a replacement for file-aware search. For a concrete code change, still run `almanac search --mentions <path>` and open the pages it returns before editing the related subsystem. [@wiki-readme]

Do not create another overview page for orientation. If the front door needs to change, update this page and the links that depend on it. [@build-prompt]

Do not treat broad topics as ownership. `agents`, `flows`, `systems`, and `product-positioning` are reading neighborhoods; the owning page for a fact should be the page whose lead names that subject. [@wiki-organization-primitives]
