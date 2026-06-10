# Feature Skeptic Report: `.almanac`

Date: 2026-06-09

Scope: `/Users/rohan/Desktop/Projects/codealmanac/.almanac`

Role: feature skeptic sidecar for a larger Garden/refactor audit.

Constraints followed: inspected the wiki, topics, dirty page state, and git-visible page names; did not edit implementation code; did not edit `.almanac` pages.

## Executive Summary

The `.almanac` wiki is structurally healthy but product-scope heavy. `almanac health` reports no orphans, stale pages, dead refs, broken links, broken cross-wiki links, missing sources, duplicate sources, empty topics, empty pages, or slug collisions. That is the good news.

The skeptic finding is that the wiki has started to contain a second product-strategy and market-research wiki inside the codebase wiki. The repo-specific notability bar explicitly allows product and market conclusions when they change how CodeAlmanac is built, positioned, priced, or trusted, so the issue is not that product memory exists. The issue is volume, granularity, topic placement, and retrieval cost. A future coding agent changing `src/sync/`, `src/jobs/`, or `src/wiki/indexer/` should not have to page through fundraising advice, broad company-brain strategy, personal Obsidian comparisons, private hosted deployment runbooks, and one-page-per-competitor notes unless that material directly constrains the code change.

The highest-value action is not a prose polish pass. It is a scope reset:

- Keep current implementation, invariant, decision, and failure-mode pages in `.almanac`.
- Reduce product/market memory to a few decision-changing synthesis anchors.
- Move fundraising, raw competitor research, private hosted deployment state, and personal inspiration pages to `docs/strategy/`, the owning repo, or archive status.
- Rename or bridge the `capture-*` pages whose current titles now say `Sync`, because the slug/name mismatch encodes migration history into everyday retrieval.
- Treat source-list bloat as a product problem: 347 unused sources and 135 unfixable legacy sources make pages look less curated even when claims are true.

## Evidence Inspected

I inspected:

- `.almanac/README.md`
- `.almanac/topics.yaml`
- the current `.almanac/pages/*.md` inventory
- `git ls-files .almanac/pages`
- `git status --short -- .almanac`
- staged and unstaged diff stats for `.almanac/pages`
- `almanac topics`
- `almanac topics show product-positioning --descendants`
- `almanac topics show agents --descendants`
- `almanac topics show wiki-design --descendants`
- `almanac health`
- representative pages across operational memory, product memory, competitor memory, compatibility stories, and proposed workflows

Inventory facts:

- 52 markdown pages exist under `.almanac/pages`.
- 51 are tracked by git.
- 1 page is untracked: `.almanac/pages/deep-refactor-audit.md`.
- Topic counts are high in the areas most likely to over-retrieve: `agents` has 24 pages, `product-positioning` has 18 pages, `cli` has 16 pages, `decisions` has 13 pages, `systems` has 13 pages, `flows` has 12 pages, `competitive-research` has 11 pages, and `wiki-design` has 10 pages.
- Product-positioning descendants currently include 19 pages: `agentmemory-competitor`, `almanac-business-model`, `almanac-product-family`, `codex-supermemory`, `company-brain`, `customer-segmentation`, `dosu`, `evidence-bundles`, `github-native-wiki-maintenance`, `hosted-deployment-environment`, `just-in-time-context-surfacing`, `mem0`, `moxie-docs`, `nessie`, `open-source-almanac`, `opendeepwiki`, `pitch-deck-fundraising`, `superpaper`, and `wiki-clarifications`.
- `almanac health` reports 347 unused sources, 29 legacy-frontmatter warnings, and 135 unfixable legacy sources.

Dirty-worktree facts:

- 41 `.almanac/pages` files have unstaged changes, totaling 2,741 insertions and 1,094 deletions.
- 17 `.almanac/pages` files have staged changes, totaling 445 insertions and 37 deletions.
- Staged additions include `dosu.md`, `opendeepwiki.md`, and `typescript-runtime-choice.md`; `typescript-runtime-choice.md` also has unstaged changes.
- `deep-refactor-audit.md` is untracked.
- The largest unstaged changes are `github-native-wiki-maintenance.md` (+368/-123), `capture-automation.md` (+248/-106), `almanac-serve.md` (+133/-54), `harness-providers.md` (+132/-45), `automation.md` (+127/-43), `wiki-organization-primitives.md` (+124/-52), `capture-flow.md` (+114/-85), `process-manager-runs.md` (+114/-52), and `capture-ledger.md` (+107/-66).

Graph facts:

- `hosted-deployment-environment`, `nessie`, `typescript-runtime-choice`, and `verification-workflow` currently have zero same-wiki backlinks by a direct wikilink scan.
- `github-native-wiki-maintenance.md` is 831 lines with 65 structured source ids.
- `capture-automation.md` is 726 lines with 37 structured source ids.
- `wiki-organization-primitives.md` is 397 lines with 21 structured source ids.
- `almanac-product-family.md` is 320 lines with 9 structured source ids.
- `superpaper.md` is sourced from a personal vault under `/Users/rohan/Documents/life` and local Codex transcripts, and is tagged into `wiki-design`, `product-positioning`, `agents`, and `competitive-research`.

## What Should Stay

These page classes are paying rent in a codebase wiki:

- Current implementation maps: `sqlite-indexer`, `topic-dag`, `wikilink-syntax`, `global-registry`, `almanac-serve`, `almanac-doctor`, `process-manager-runs`, `harness-providers`, `provider-lifecycle-boundary`, `lifecycle-cli`, `lifecycle-architecture`, `wiki-lifecycle-operations`, `build-operation`, `ingest-operation`, `automation`, `capture-flow`, `capture-ledger`, `self-update`, `install-time-node-launcher`.
- Current invariants and design decisions: `source-provenance`, `operation-prompts`, `global-agent-instructions`, `accidental-special-case-architecture`, `typescript-runtime-choice` if it remains short and decision-shaped.
- Small operational gotchas: `verification-workflow` has zero backlinks today, but the content is directly useful to future coding agents because it records that `npm test` does not run typechecking and that CI runs build, typecheck, and tests.
- Close product constraints that change code shape: `github-native-wiki-maintenance`, `open-source-almanac`, `just-in-time-context-surfacing`, and `almanac-product-family` are legitimate only after they are compressed or split so the code-relevant decisions are separate from market notes.

## Major Findings

### 1. Product and market memory has become a parallel wiki

Evidence:

- `product-positioning` has 18 direct pages and 19 pages including descendants.
- `competitive-research` has 11 pages.
- Pages include individual competitors (`dosu`, `moxie-docs`, `nessie`, `mem0`, `agentmemory-competitor`, `codex-supermemory`, `opendeepwiki`), broad category pages (`company-brain`), product architecture pages (`almanac-product-family`, `github-native-wiki-maintenance`, `open-source-almanac`), and fundraising material (`pitch-deck-fundraising`).
- Several competitor pages are heavily linked into implementation-adjacent topics. For example, `superpaper` is tagged `agents`, `wiki-design`, `product-positioning`, and `competitive-research`; `opendeepwiki` is tagged `competitive-research`, `wiki-design`, and `prompt-system`.

Why it exists:

The repo notability bar allows durable product and market conclusions. That is correct for CodeAlmanac because product choices change architecture: GitHub-native maintenance, repo-owned memory, source provenance, just-in-time context surfacing, and hosted coordination all affect implementation priorities.

Why that reason is not enough:

The current granularity confuses "decision-changing synthesis" with "all useful product research." A coding-agent wiki should store the conclusion a future implementation agent needs, not every market note that helped a founder reason about strategy.

User/product value:

High for a founder, product strategist, or agent designing hosted workflows. Medium to low for a coding agent editing local CLI, indexer, automation, or provider code.

Retrieval cost:

High. Product pages appear in `agents`, `wiki-design`, and `prompt-system` neighborhoods, so implementation searches can surface broad market pages. Large pages such as `github-native-wiki-maintenance` and `almanac-product-family` also mix current product contract, hosted implementation notes, future generalized product ideas, and raw source-backed research.

Recommendation:

Keep product memory in `.almanac` only when it directly changes codebase behavior or future code review. Create or preserve a small set of strategy anchors:

- `almanac-product-strategy` or a trimmed `almanac-product-family`
- `github-native-wiki-maintenance`, split into current CodeAlmanac-facing contract and hosted implementation details
- `competitive-landscape`, replacing most one-page-per-competitor notes
- `open-source-almanac`, trimmed to product constraints that change GitHub workflow behavior

Move raw market research and investor narrative to `docs/strategy/` or a separate product/company Almanac.

### 2. Competitor pages should be merged unless they change an implementation decision

Evidence:

- `dosu.md` and `moxie-docs.md` are close competitors and both directly constrain positioning around GitHub App workflows, PR-time docs drift, MCP context, and reviewable update PRs.
- `opendeepwiki.md` directly shapes `wiki-organization-primitives` through the catalog-first/hubs-versus-leaves lesson.
- `nessie.md` has zero backlinks and frames a conversation-memory product rather than a codebase-memory implementation constraint.
- `mem0.md`, `agentmemory-competitor.md`, and `codex-supermemory.md` overlap around runtime memory products, hooks, recall, and context injection.
- `superpaper.md` is a personal Obsidian-first knowledge system from `/Users/rohan/Documents/life`, not a codealmanac subsystem.

User/product value:

High for close competitors that shape decisions: `dosu`, `moxie-docs`, and `opendeepwiki`.

Medium for memory-daemon comparisons: they clarify "runtime recall" versus "repo-governed project memory," but they do not all need separate pages.

Low inside this repo for `nessie` and `superpaper` as standalone pages. Their lessons can be carried by synthesis pages.

Retrieval cost:

High. One page per competitor multiplies backlinks, topics, and source lists. It also encourages future Garden runs to preserve competitor-specific pages because they exist, even when their actual lesson is one paragraph in a landscape page.

Recommendation:

- Keep close competitor material as sections in `competitive-landscape` unless a competitor directly changes an active implementation decision.
- Merge `mem0`, `agentmemory-competitor`, and `codex-supermemory` into one "runtime memory products" comparison.
- Merge `nessie` into the same memory-products section or move it to `docs/strategy/research`.
- Merge `superpaper` lessons into `wiki-organization-primitives` and archive or move the standalone page.
- Keep `opendeepwiki` only if its catalog-first lesson remains a direct input to Build/Garden prompt design; otherwise fold it into `wiki-organization-primitives`.

### 3. Fundraising material does not belong in the codebase wiki

Evidence:

- `pitch-deck-fundraising.md` is 125 lines.
- It is tagged `fundraising` and `product-positioning`.
- It cites Guy Kawasaki, Sequoia, YC, Crunchbase, DocSend, and `/tmp/pitch-deck-research.md`.
- It has only one same-wiki backlink, from `company-brain`.
- Its content is about investor deck structure, seed versus Series A emphasis, market slides, competition slides, and pitch failure modes.

User/product value:

High for fundraising preparation.

Retrieval cost:

High for codebase work. A future agent editing implementation code should almost never retrieve slide-deck advice. The page also encourages the wiki to become a company operating notebook rather than repo memory.

Recommendation:

Move this to `docs/strategy/fundraising/` or a company/product Almanac. Keep at most one sentence in a product-strategy page if fundraising constraints materially change near-term implementation priorities.

### 4. Hosted deployment environment belongs in the owning hosted repo or a runbook, not this codebase wiki

Evidence:

- `hosted-deployment-environment.md` has zero same-wiki backlinks.
- It is tagged `product-positioning` and `stack`, not a codealmanac implementation topic.
- It records `usealmanac` repository deployment state, Render service ids, Supabase project refs, Doppler config names, Modal secret names, GitHub App IDs, webhook delivery behavior, and production smoke details.
- Its own related pages point back to `github-native-wiki-maintenance`, `evidence-bundles`, and `process-manager-runs`.

User/product value:

High for operating the hosted product.

Retrieval cost:

High in this repo. The details are private, cross-repo, time-sensitive, and likely to drift. They are operational state for `usealmanac`, not durable understanding of this TypeScript CLI repo.

Recommendation:

Move the page to the `usealmanac` repo's docs or a deployment runbook. In this wiki, keep only the architectural fact that hosted infrastructure coordinates GitHub events while repo-owned Almanac pages remain canonical.

### 5. Proposed/future workflow pages are written too much like settled product architecture

Evidence:

- `evidence-bundles.md` is 216 lines and has status `proposed`.
- It mixes implemented local `almanac ingest github:pr:123` behavior, historical Notion/Composio branch details, hosted GitHub source-tool design, future connector manifests, `SourceCatalog`, `Publisher`, `ReviewNote`, and operation-output shapes.
- `wiki-clarifications.md` mixes a future clarification concept with the shipped `.almanac/review.yaml` editorial review queue.
- `github-native-wiki-maintenance.md` is 831 lines and includes product thesis, GitHub check-run transport, hosted runner design, old backend placement, Modal callback security, production smoke notes, and extensibility rules.

User/product value:

High for architecture planning.

Retrieval cost:

High for current implementation tasks. Present-tense code claims, planned connector abstractions, hosted product notes, and future operation outputs are interleaved. That raises the risk that a future agent treats a proposal as an implemented invariant.

Recommendation:

- Split proposed architecture from implemented contract.
- Move unimplemented connector and hosted-product plans to `docs/plans/` or `docs/strategy/`.
- Keep `.almanac` pages focused on current behavior, settled invariants, and explicit implementation-facing decisions.
- Rename `wiki-clarifications` toward the shipped concept, likely `review-escalations`, if the primary durable feature is `almanac review` over `.almanac/review.yaml`.

### 6. `capture-*` pages carry a stale naming story after the product moved to `sync`

Evidence:

- The files are `capture-flow.md`, `capture-automation.md`, and `capture-ledger.md`.
- Their current titles are `Sync Flow`, `Sync Automation`, and `Sync Ledger`.
- `sessionend-hook.md` is archived and superseded by `capture-automation`.
- `capture-automation.md` explicitly says the coordinator was renamed from `capture sweep` to `almanac sync`, and that the current scheduler surface is `almanac sync` plus automation commands.
- `capture-ledger.md` says the current file is `.almanac/jobs/sync-ledger.json` and that legacy capture ledger paths remain fallback reads.

User/product value:

High. The sync/capture pages preserve important dedupe, quiet-window, transcript, and automation invariants.

Retrieval cost:

Medium to high. The slug/title mismatch forces agents to carry migration history in their head. Searching for `sync` and searching for `capture` may produce different mental models even though the current product path is sync.

Recommendation:

Use one current vocabulary for active pages. Preferred shape:

- `sync-flow`
- `sync-automation`
- `sync-ledger`
- `legacy-sessionend-hook`

If slug migration is too risky right now, create redirects or alias pages later, but do not keep adding active knowledge to `capture-*` slugs whose titles say `Sync`.

### 7. Source frontmatter has become a retrieval-cost multiplier

Evidence:

- `almanac health` reports 347 unused sources.
- `almanac health` reports 135 unfixable legacy sources.
- `almanac health` reports 29 legacy-frontmatter entries.
- `github-native-wiki-maintenance.md` lists 65 source ids.
- `capture-automation.md` lists 37 source ids.
- `almanac-serve.md` lists 27 source ids.
- `harness-providers.md` lists 26 source ids.
- Many migrated entries have notes such as "Migrated from legacy files" or "Migrated from legacy sources."

User/product value:

High when sources support specific claims and power file-aware retrieval.

Retrieval cost:

High when source lists become inventories of everything an agent inspected. They increase page length, health noise, and false confidence. They also make Garden look successful because every page has provenance, even if the prose does not cite most of it.

Recommendation:

Treat source trimming as part of gardening. A good page should list sources that support claims a future reader may audit, not every file or transcript seen during a run. For pages with huge source lists, either cite the sources close to claims or remove/move them. The long-term source rule should be: sources are evidence, not worklogs.

### 8. Topic placement is making product memory look implementation-relevant

Evidence:

- `agents --descendants` includes `codex-supermemory`, `evidence-bundles`, `opendeepwiki`, `superpaper`, `farzapedia`, `just-in-time-context-surfacing`, and `documenting-software-architectures`.
- `wiki-design --descendants` includes `superpaper`, `opendeepwiki`, `github-native-wiki-maintenance`, `open-source-almanac`, `evidence-bundles`, `farzapedia`, and `documenting-software-architectures`.
- `product-positioning` is a top-level topic with no parent, and `competitive-research` is its child.

User/product value:

Topics are useful for retrieval neighborhoods, and CodeAlmanac does need product memory.

Retrieval cost:

High when product pages are also tagged as `agents`, `prompt-system`, or `wiki-design` because they influenced a prompt or idea once. Those tags make inspiration pages compete with implementation pages.

Recommendation:

Use implementation topics only when the page changes implementation work. A competitor or inspiration page should not be tagged `agents` merely because it discusses agents. If product memory stays in `.almanac`, isolate it under product topics and use synthesis pages to link implementation implications back into code topics.

## Page-Level Recommendations

| Page or group | Current value | Retrieval cost | Recommendation |
|---|---:|---:|---|
| `pitch-deck-fundraising` | Fundraising prep | High | Move to `docs/strategy/fundraising` or a company/product Almanac. |
| `hosted-deployment-environment` | Hosted ops runbook | High | Move to `usealmanac` docs/runbook; keep only architectural summary here. |
| `superpaper` | Personal knowledge-system contrast | High | Merge lessons into `wiki-organization-primitives`; archive or move page. |
| `farzapedia` | Prompt-writing reference | Medium | Merge durable prompt lessons into `operation-prompts`; archive source page. |
| `nessie` | Adjacent conversation-memory competitor | Medium | Merge into memory-products landscape or move to strategy research. |
| `mem0`, `agentmemory-competitor`, `codex-supermemory` | Runtime memory contrast | Medium | Merge into one memory-products comparison. |
| `dosu`, `moxie-docs` | Close hosted docs/workflow competitors | Medium | Keep only as close-competitor sections or concise pages tied to decisions. |
| `opendeepwiki` | Catalog-first organization lesson | Low to medium | Keep only if directly tied to Build/Garden organization; otherwise merge. |
| `github-native-wiki-maintenance` | Core hosted direction | Very high | Split current contract from hosted implementation/runbook/history. |
| `almanac-product-family` | Product vocabulary and scope | High | Trim to codebase-relevant product contract; move generalized product loop to strategy docs. |
| `evidence-bundles` | Proposed source/connector architecture | High | Keep implemented source-ingest contract; move future connector design to plans. |
| `wiki-clarifications` | Shipped review queue plus future clarification idea | Medium | Rename/reframe around `almanac review`; move speculative clarification flow out. |
| `deep-refactor-audit` | Skill documentation | Medium | Do not add as a wiki page unless repo-owned skill behavior must be discovered by future implementation agents. The skill file itself is the source of truth. |
| `typescript-runtime-choice` | Durable runtime decision | Low | Keep if short; link from `install-time-node-launcher` or merge if it remains a one-off. |
| `verification-workflow` | Direct agent workflow gotcha | Low | Keep and add backlinks from AGENTS/manual-oriented pages later. |

## Product/Market Memory Rule

The wiki should keep product memory only when it answers at least one of these questions for a future coding agent:

- Should this feature exist in this repo?
- Which implementation path was chosen because of a product constraint?
- Which competitor or prior-art lesson changes a CodeAlmanac design boundary?
- Which market or trust constraint changes the default behavior, config surface, storage location, or review workflow?
- Which current product promise would this code change violate?

If the page only answers "how should we pitch this?", "what did we learn about the market?", "what did this adjacent product do?", or "what might a generalized Almanac become?", it belongs in `docs/strategy/`, a product/company Almanac, or an archive page outside the implementation retrieval path.

## Recommended Target Shape

The `.almanac` wiki should read like this:

- A small implementation core: indexer, registry, topics, links, source provenance, lifecycle operations, jobs, harness providers, automation, sync, viewer, setup/update.
- A small decision core: runtime choice, source provenance, provider boundary, no interactive prompts, Git-owned memory, scheduler-backed sync, structured sources.
- A small product-constraint core: repo-owned memory, GitHub-native maintenance, OSS maintainer context, just-in-time context surfacing.
- A small competitive synthesis: close competitors and the specific product constraints they impose.
- No standalone fundraising advice.
- No private hosted deployment runbook for another repo.
- No personal knowledge-system pages except as folded lessons inside wiki organization guidance.
- No one-page-per-adjacent-competitor unless the page owns a live design decision.

## Refactor Roadmap For Garden

Phase 0: Freeze scope

- Stop adding new product/competitive pages until the page taxonomy is reset.
- Treat the current dirty `.almanac` surface as one large Garden rewrite that needs cluster review, not as ordinary page touch-up.

Verification:

- `git status --short -- .almanac/pages`
- page inventory count before and after

Phase 1: Move or archive clear non-codebase memory

- Move/archive `pitch-deck-fundraising`.
- Move/archive `hosted-deployment-environment`.
- Move/archive or merge `superpaper`.
- Do not add `deep-refactor-audit.md` unless the team explicitly wants skill docs in repo wiki.

Verification:

- Product-positioning page count drops.
- No implementation topic loses a current code invariant.

Phase 2: Merge competitor sprawl

- Create one concise competitive synthesis from `dosu`, `moxie-docs`, `opendeepwiki`, `nessie`, `mem0`, `agentmemory-competitor`, and `codex-supermemory`.
- Keep individual close competitor pages only when they own a direct decision.

Verification:

- `competitive-research` page count drops.
- `company-brain` becomes a short category/positioning anchor rather than a market notebook.

Phase 3: Normalize sync naming

- Rename or bridge `capture-flow`, `capture-automation`, and `capture-ledger` to sync vocabulary.
- Keep `sessionend-hook` archived as the legacy cleanup page.

Verification:

- Searching for `sync` returns the current active pages.
- Searching for `capture` returns legacy context or redirect/alias pages.

Phase 4: Split proposed architecture from implemented contracts

- Trim `evidence-bundles` to current source-aware ingest or move future connector architecture to plans.
- Split `github-native-wiki-maintenance` into current contract, hosted implementation notes, and strategy material.
- Reframe `wiki-clarifications` around the shipped review escalation queue.

Verification:

- Current implementation pages do not describe proposed features as settled behavior.
- Future design pages are clearly marked or moved out of `.almanac`.

Phase 5: Source hygiene

- For the largest source lists, remove unused source entries or cite them next to claims.
- Replace "Migrated from legacy files/sources" source notes with claim-specific notes only where the source still matters.
- Treat `almanac health` source warnings as wiki quality debt, not harmless noise.

Verification:

- `unused_sources` and `unfixable_sources` counts materially decrease.
- Page leads and source lists become shorter and more auditable.

## Open Questions For The Main Auditor

- Should product/market memory stay in this repo's `.almanac` at all, or should CodeAlmanac have a separate product/company Almanac?
- Is `docs/strategy/` the right destination for moved market and fundraising material, or should archived `.almanac` pages preserve historical context in place?
- Should Garden support redirect/alias pages before renaming the `capture-*` slugs to `sync-*`?
- Is `company-brain` still a useful category anchor, or should it be replaced by a narrower `codebase-memory-positioning` page?
- Should source-health warnings become a release gate for Garden output, or remain advisory until the source model stabilizes?

