# Source Map: Current .almanac Information Architecture

Date: 2026-06-09

## Portable Corpus

The committed wiki surface is small and understandable:

- `.almanac/README.md`: notability bar, topic taxonomy, page shape guidance, writing conventions, linking rules
- `.almanac/topics.yaml`: topic DAG
- `.almanac/pages/*.md`: 52 markdown pages

The committed file list includes only README, topics, and page files under `.almanac`. Local artifacts such as `.almanac/index.db` and `.almanac/runs/` exist on disk but are not tracked in git.

There is no active `.almanac/pages/getting-started.md` page. That is a notable absence because the wiki already has enough neighborhoods that first-entry routing matters, and because adjacent viewer/prompt concepts refer to a getting-started style entry point.

## Local Derived State

The working tree contains local generated or ignored state:

- `.almanac/index.db`
- `.almanac/runs/`
- capture logs and worker lock files

These are not the shared wiki. They matter only because their presence can mislead a human browsing the filesystem. The shared artifact is markdown plus topics.

## Topic DAG

Current topics and page counts from `almanac topics`:

| Topic | Pages | Judgment |
| --- | ---: | --- |
| `agents` | 24 to 25 | Too broad. It mixes runtime providers, prompts, product mechanisms, external references, and wiki theory. |
| `product-positioning` | 18 | Legitimate but needs a hub and stricter admission rules. |
| `cli` | 16 to 17 | Useful as a technical browse neighborhood. |
| `decisions` | 13 | Useful, but many decision pages do not follow a decision-record shape. |
| `systems` | 13 | Useful for implementation architecture. |
| `flows` | 12 to 13 | Useful, but capture/sync vocabulary drift makes the neighborhood confusing. |
| `competitive-research` | 11 | Legitimate as a product shelf, not as default engineering context. |
| `wiki-design` | 10 | Strong and important. Should get a hub. |
| `storage` | 6 | Coherent. |
| `prompt-system` | 6 | Coherent but overlaps heavily with `agents` and `wiki-design`. |
| `automation` | 5 | Coherent but should be under sync/runtime hub. |
| `stack` | 5 | Coherent. |
| `provider-harness` | 3 | Coherent and should remain narrow. |
| `fundraising` | 1 | Questionable as a first-class topic inside the codebase wiki. |

The indexer sees no orphan pages. That is good. The problem is not missing topic assignments.

The topic DAG currently carries at least five meanings:

- browse neighborhood, such as `storage` or `provider-harness`
- page role, such as `decisions` or `flows`
- implementation area, such as `cli` or `automation`
- product shelf, such as `product-positioning` and `competitive-research`
- external influence, currently folded into `agents`, `wiki-design`, or `prompt-system`

That overload is why the graph is healthy while retrieval can still feel noisy.

## Page Inventory Shape

The page corpus currently has:

- 52 pages
- 1 archived page: `sessionend-hook`, superseded by `capture-automation`
- 12 pages above roughly 180 lines
- 1 active page with no page-to-page links: `global-agent-instructions` has only file links
- Several pages with many sources and few citations
- 30 pages with legacy source strings or legacy `files:` style provenance in the sidecar inventory
- casual frontmatter fields such as `status` and `verified` that look intentional but are not documented as queryable schema

The largest pages:

| Page | Lines | Current job |
| --- | ---: | --- |
| `github-native-wiki-maintenance` | 831 | Remote product thesis, GitHub App runtime, PR UX, hosted worker architecture, product strategy, source tooling |
| `capture-automation` | 726 | Sync contract, scheduler behavior, hook removal, migration cleanup, incident history, source list |
| `wiki-organization-primitives` | 397 | Organization doctrine, prior art, source/link rules, hubs, structural operations, open gaps |
| `almanac-serve` | 387 | Local viewer design, implementation, packaging, API, source rail, jobs UI |
| `almanac-product-family` | 320 | Product vocabulary, generalized Almanac model, CLI/GUI loops, directory shape, product packaging |
| `capture-ledger` | 237 | Sync ledger state model and reconciliation |
| `source-provenance` | 232 | Evidence model, transition contract, implementation surfaces, open questions |
| `automation` | 223 | Scheduled task public surface, launchd, migration, config, install behavior |
| `capture-flow` | 216 | Sync flow but under old capture slug |
| `evidence-bundles` | 216 | Source connector operation input model |
| `company-brain` | 195 | Market-category analysis and product positioning |
| `process-manager-runs` | 192 | Durable job/run storage and status model |

## Current Page Neighborhoods

### Wiki Design

Core pages:

- `wiki-organization-primitives`
- `source-provenance`
- `wikilink-syntax`
- `topic-dag`
- `documenting-software-architectures`
- `operation-prompts`
- `evidence-bundles`

This is the strongest neighborhood. It has a coherent conceptual center, but it needs a hub because agents need to know which page answers which question.

### Sync / Capture / Automation

Core pages:

- `capture-automation` with title "Sync Automation"
- `capture-flow` with title "Sync Flow"
- `capture-ledger` with title "Sync Ledger"
- `automation`
- `verification-workflow`
- `sessionend-hook` archived

This is the most urgent naming problem. The current product language is sync, while stable slugs still say capture. Without redirects or a rename plan, new agents will search both terms and may reintroduce old vocabulary.

### Lifecycle / Operations / Jobs

Core pages:

- `lifecycle-architecture`
- `wiki-lifecycle-operations`
- `build-operation`
- `ingest-operation`
- `process-manager-runs`
- `operation-prompts`

The neighborhood is useful. It needs a hub that says which pages are current operation semantics, which are job infrastructure, and which are prompt contracts.

### Provider Harness

Core pages:

- `harness-providers`
- `provider-lifecycle-boundary`
- `claude-agent-sdk`

This is narrow and healthy. Keep it separate from broad `agents` pages.

### Product Strategy And Competitive Research

Core pages:

- `almanac-product-family`
- `company-brain`
- `github-native-wiki-maintenance`
- `open-source-almanac`
- `almanac-business-model`
- `customer-segmentation`
- `pitch-deck-fundraising`
- `mem0`
- `codex-supermemory`
- `agentmemory-competitor`
- `dosu`
- `moxie-docs`
- `opendeepwiki`
- `nessie`

This is legitimate under the repo README's current notability bar, but it has become a product wiki inside the codebase wiki. The fix is a product strategy hub plus a rule: product pages must state the implementation or positioning decision they affect.

### External References And Inspirations

Core pages:

- `documenting-software-architectures`
- `farzapedia`
- `superpaper`
- `mem0`
- `codex-supermemory`
- `agentmemory-competitor`
- `opendeepwiki`
- `nessie`

Some of these are competitors, some are prior-art references, and some are product inspirations. They should not all sit in the same path as current agent runtime architecture. The wiki needs either an `external-references` topic or a hub convention that says which pages are current implementation, which are market references, and which are conceptual inputs.

## Working Tree Note

The audit ran against a dirty tree. `git status --short` showed broad in-progress `.almanac/pages/*` edits, two added competitor pages, a new `deep-refactor-audit` page, and many unrelated source changes. This report treats the current tree as the garden state the user asked to audit. It does not assume the checked-in baseline is identical.
