---
title: OpenDeepWiki
summary: OpenDeepWiki is a generated codebase-documentation reference whose catalog-first pipeline shows why planned navigation can make AI-written repo docs easier to read.
topics: [competitive-research, wiki-design, prompt-system]
sources:
  - id: comparison-session
    type: conversation
    path: /Users/rohan/.codex/sessions/2026/06/07/rollout-2026-06-07T12-52-48-019ea3a5-20e5-7d90-9b55-31a2dacc1048.jsonl
    note: Records the CodeAlmanac comparison against a local clone of AIDotNet/OpenDeepWiki at commit a32b3c7a8e0a53dfc9971191466d6ea17dc597a5.
  - id: catalog-model
    type: web
    url: https://github.com/AIDotNet/OpenDeepWiki/blob/a32b3c7a8e0a53dfc9971191466d6ea17dc597a5/src/OpenDeepWiki.Entities/Repositories/DocCatalog.cs
    retrieved_at: 2026-06-07
    note: Defines the catalog tree model with parent IDs, child catalogs, order, path, and optional document-file association.
  - id: doc-model
    type: web
    url: https://github.com/AIDotNet/OpenDeepWiki/blob/a32b3c7a8e0a53dfc9971191466d6ea17dc597a5/src/OpenDeepWiki.Entities/Repositories/DocFile.cs
    retrieved_at: 2026-06-07
    note: Defines generated document content and source-file tracking for catalog leaf documents.
  - id: catalog-prompt
    type: web
    url: https://github.com/AIDotNet/OpenDeepWiki/blob/a32b3c7a8e0a53dfc9971191466d6ea17dc597a5/src/OpenDeepWiki/prompts/catalog-generator.md
    retrieved_at: 2026-06-07
    note: Documents OpenDeepWiki's catalog-generation rules, including parent nodes as navigation domains and leaf nodes as document pages.
  - id: doc-tool
    type: web
    url: https://github.com/AIDotNet/OpenDeepWiki/blob/a32b3c7a8e0a53dfc9971191466d6ea17dc597a5/src/OpenDeepWiki/Agents/Tools/DocTool.cs
    retrieved_at: 2026-06-07
    note: Implements the rule that document writes and appends are rejected for catalog items that have child catalog items.
verified: 2026-06-07
external_version: a32b3c7a8e0a53dfc9971191466d6ea17dc597a5
---

# OpenDeepWiki

OpenDeepWiki is an open-source generated codebase-documentation system. It matters to CodeAlmanac because its strongest readability move is structural rather than stylistic: it generates a catalog tree before it generates page prose, and the catalog separates navigation nodes from content pages.

## What It Does

OpenDeepWiki's documentation model has `DocCatalog` rows for the tree and `DocFile` rows for generated Markdown. A catalog item carries `ParentId`, `Title`, `Path`, `Order`, optional `DocFileId`, and child catalog navigation; a document file carries the generated content and the source files read for that document. [@catalog-model] [@doc-model]

The catalog prompt asks the agent to design topic domains and independently readable deep-dive leaves from actual source code. It explicitly rejects file/class pages, fixed page counts, over-compressed catalogs, and generic template sections. It also states that parent nodes with children are navigation or grouping domains and that generated document content belongs on leaf nodes. [@catalog-prompt]

`DocTool` enforces the prompt rule at write time. `WriteAsync` and `AppendAsync` both check whether the target catalog item has children; if it does, the tool clears the catalog item's `DocFileId`, saves that state, and returns an error saying documents can only be written or appended to leaf catalog items. [@doc-tool]

## Product Lesson For CodeAlmanac

OpenDeepWiki is not the product model CodeAlmanac should copy. It stores generated docs and catalogs in an application database, while CodeAlmanac's durable artifact is repo-owned Markdown under `.almanac/` plus topics, links, sources, lineage, and Git review. [@comparison-session]

The part CodeAlmanac should copy is the catalog-first discipline. Before Build writes a first wiki, and before Garden restructures a dense graph, the agent should decide the package shape: front door, hubs, navigation shelves, leaf pages, page purpose, source expectations, and scope exclusions. That planning can stay inside the prompt-driven operation; it does not require proposal files, a TypeScript state machine, or replacing topics with folders. [@comparison-session]

The transferable invariant is: hubs route, leaves explain. A dense subject should not force a single page to be both the map and the deep dive. In Almanac, a hub page or browse projection can route readers through architecture, workflows, decisions, constraints, failure modes, reference, and product-internal areas while stable slugs, topics, backlinks, sources, and lineage remain the real graph model. [@comparison-session]

## Related Pages

[[competitive-landscape]] is the hub for the full competitive research and external-influence cluster. [[wiki-organization-primitives]] explains how this lesson fits CodeAlmanac's page, link, topic, source, hub, and browse-projection model. [[operation-prompts]] explains why better organization behavior should live in prompts before it becomes CLI machinery. [[moxie-docs]] explains the closest hosted codebase-docs competitor found before this OpenDeepWiki comparison.
