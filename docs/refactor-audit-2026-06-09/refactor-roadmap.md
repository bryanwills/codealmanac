# Refactor Roadmap For The .almanac Garden

Date: 2026-06-09

This roadmap describes wiki gardening work. It does not modify production code.

## Phase 0: Freeze The Meaning Of Current Terms

Goal:

Stop vocabulary drift before rewriting pages.

Changes:

- Decide whether `sync` is now the canonical product noun for automatic session memory.
- If yes, document capture as legacy vocabulary in a new `sync-hub`.
- List old slugs that need alias/redirect or archive treatment: `capture-automation`, `capture-flow`, `capture-ledger`.

Why first:

Every split or rewrite will otherwise preserve the old capture vocabulary.

Risk:

Renaming without redirect support can break existing wikilinks and user habits.

Verification:

- `almanac search "sync"` returns the hub and current pages.
- Old capture pages clearly point to current sync terminology.

## Phase 1: Add The Front Door And Hubs

Goal:

Create reading routes before rewriting dense pages.

Changes:

- Create `getting-started`.
- Create `wiki-design-hub`.
- Create `sync-hub`.
- Create `architecture-hub` for lifecycle, storage, process/jobs, provider harness, CLI, and viewer architecture.
- Create `product-strategy-hub`.
- Create `competitive-landscape`.

Why first:

Hubs let cleanup and page splits land into a known navigation structure. A front door prevents new agents from treating search result order as reading order.

Risk:

Weak hubs can become generic link dumps.

Verification:

- `getting-started` names the first page to read for major work areas.
- Each hub marks current versus historical/proposed pages.
- Each hub explains where future facts in that area should go.

## Phase 2: Repair Topic Retrieval

Goal:

Make topic searches less noisy.

Changes:

- Decide whether to add `architecture`, `lifecycle`, `provider-runtime`, `wiki-model`, `prior-art`, and `viewer` topics.
- Add `external-references` or `prior-art` if external idea pages keep crowding `agents`.
- Demote or delete `fundraising` unless it has more than one active implementation-shaping page.
- Review pages tagged `agents`; remove the topic from pure competitor/product pages unless they affect agent runtime or prompts.
- Review pages tagged `product-positioning`; require a product implication section.
- Treat `decisions`, `flows`, `constraints`, and `failure-modes` as overlays or page-shape conventions, not as reading routes.

Why first:

Retagging before source cleanup and splits reduces repeated metadata churn.

Risk:

Removing topics can make pages harder to find if hubs are weak.

Verification:

- `almanac search --topic agents` mostly returns agent/runtime/prompt pages.
- `almanac search --topic product-positioning` returns product pages with implementation or positioning consequences.
- External reference pages are findable without appearing as current architecture.

## Phase 3: Source Hygiene Before Page Expansion

Goal:

Make evidence trustworthy before adding more prose.

Changes:

- Run the safe source migration path if not already done.
- For high-gap pages, delete unused source entries or add citations near claims.
- Prioritize `capture-automation`, `almanac-serve`, `automation`, `provider-lifecycle-boundary`, `harness-providers`, `capture-flow`, `mem0`, `lifecycle-cli`, `sqlite-indexer`, and `process-manager-runs`.
- Replace "Migrated from legacy files" notes with relevance notes when sources remain.
- Update public guidance so new pages use `sources:` rather than legacy `files:` provenance.

Why after routing and topic cleanup:

Splitting pages with bloated source lists spreads provenance debt into more files. Routing and topics tell the cleanup pass which pages are canonical.

Risk:

Over-aggressive cleanup could remove useful historical evidence.

Verification:

- `almanac health` has sharply lower `unused_sources`, `legacy-frontmatter`, and `unfixable-sources` counts.
- High-importance pages cite non-obvious claims with source IDs.

## Phase 4: Split The Oversized Pages

Goal:

Separate maps, contracts, decisions, incidents, and product strategy.

Changes:

- Split `capture-automation` into sync contract, scheduler/migration, and incident/failure-mode material.
- Split `github-native-wiki-maintenance` into product anchor, PR loop, hosted runner, source tools, and deployment risks.
- Split `wiki-organization-primitives` only if hub guidance and source/link quality deserve separate operational pages.
- Split `almanac-product-family` only if generalized product material keeps competing with CodeAlmanac-specific strategy.
- Split `evidence-bundles` if source-connector contracts and product/source-access strategy keep competing.
- Split `almanac-serve` only if viewer work resumes; otherwise perform source cleanup and leave it as a dense anchor.

Why after hubs, topics, and source cleanup:

Splits need hubs, topic routes, and source standards to be discoverable and trustworthy.

Risk:

Over-splitting creates thin pages and weak canonicality.

Verification:

- No split page is just a paragraph.
- Each new page has a lead that states its job.
- The old page either remains a hub/anchor or points clearly to the new pages.

## Phase 5: Move, Merge, Or Archive Scope Mismatches

Goal:

Keep `.almanac` focused on repo memory that helps agents build CodeAlmanac.

Changes:

- Move or demote `pitch-deck-fundraising` unless it directly constrains product language, pricing, trust architecture, or packaging.
- Move or reframe `hosted-deployment-environment` if it is deployment planning rather than current codebase architecture.
- Merge `superpaper` lessons into `wiki-organization-primitives` or a prior-art page if the standalone page does not shape current work.
- Merge `farzapedia` into `operation-prompts` if it is mainly an inspiration note.
- Consolidate weak memory-product competitor pages where their only durable value is a comparison table or landscape note.
- Keep close competitor pages such as `dosu` and `moxie-docs` only if each names a CodeAlmanac product or implementation consequence.

Why after splits:

Splits clarify whether a page is current architecture, product strategy, prior art, or transcript residue.

Risk:

Moving too aggressively can lose product rationale that explains current architectural choices.

Verification:

- Product pages have explicit implementation or positioning consequences.
- External references state the decision or design they shaped.
- Moved material remains discoverable from `docs/strategy/` or a product wiki if it is still useful.

## Phase 6: Rename Or Alias

Goal:

Resolve capture/sync and other stale naming.

Changes:

- If redirect support exists, rename active pages to sync slugs and archive old capture slugs as redirects.
- If redirect support does not exist, keep old slugs but add explicit lineage and hub warnings.
- Identify other misleading slugs such as pages whose subject is hidden behind a genre suffix.

Why after hubs, topic cleanup, and scope cleanup:

Readers need stable routes during renames.

Risk:

Broken wikilinks or external bookmarks.

Verification:

- `almanac health` has no broken links.
- Searches for old and new terms both route to current pages.

## Phase 7: Define Or Delete Editorial Metadata

Goal:

Prevent optional frontmatter from becoming accidental schema.

Changes:

- Decide whether `status` has durable meanings and query/health behavior.
- Decide whether `verified` means source-verified, current-code-verified, reviewer-verified, or nothing.
- If the fields are meaningful, document them in `.almanac/README.md` and make Garden use them consistently.
- If they are not meaningful, remove them from pages during garden cleanup.

Why after source cleanup:

Source cleanup reveals whether `verified` can mean anything objective.

Risk:

Keeping weak metadata creates false confidence; deleting useful metadata may remove a future quality signal.

Verification:

- A future agent can read README and know whether to trust `status` and `verified`.
- No page carries these fields merely because another page did.

## Phase 8: Update The Wiki README And Exported Guidance

Goal:

Turn audit decisions into durable conventions.

Changes:

- Add hub/anchor guidance.
- Add decision-page shape guidance borrowed from MADR.
- Add source hygiene guidance: sources support claims; sources are not an inspection log.
- Add product-page admission rule.
- Add external-reference convention.
- Replace legacy `files:` provenance guidance with the current `sources:` contract.

Why late:

The README should capture settled practice after the first rewrite proves the model.

Risk:

Putting too much doctrine in README can make it harder for agents to start.

Verification:

- README remains short enough to read before work.
- Rules map to actual page examples in the wiki.

## Phase 9: Health And Review

Goal:

Finish with graph integrity and retrieval quality.

Changes:

- Run `almanac health`.
- Run representative searches: `sync`, `source provenance`, `provider harness`, `GitHub App`, `sqlite`, `product positioning`.
- Check backlinks for renamed/split pages.
- Review `git diff -- .almanac` for source churn and accidental prose loss.

Why last:

The final quality bar is retrieval, not file count.

Verification:

- Health graph categories stay clean.
- Source warnings are reduced and intentional.
- Hubs make top subjects readable without knowing page names.
